#!/usr/bin/env python3
"""Ekole OpsConsole — localhost only; no network writes or Moodle/Git writes.

Runs a fixed allowlist of Ekole CLI actions. Deployment can only copy the
static site to an external local directory, after dry run + explicit consent.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import os
import pathlib
import re
import secrets
import shutil
import subprocess
import sys
import threading
import time
import urllib.parse
import webbrowser
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, SimpleHTTPRequestHandler, ThreadingHTTPServer

ROOT = pathlib.Path(__file__).resolve().parents[1]
HERE = pathlib.Path(__file__).resolve().parent
WEB = HERE / "web"
LOGDIR = HERE / "logs"
REPORTDIR = HERE / "reports"
ID_RE = re.compile(r"^qc-pri-[a-z]+-\d{3}$")
MAIN_TOOL = ROOT / "tools" / "ekole.py"
FIXED_ACTIONS = {"verify", "build", "moodle-plan", "pages-zip"}
LOCAL_CONFIRMATION = "COPIER EN LOCAL"
MAX_POST = 16_384

def read_json(path: pathlib.Path) -> object:
    return json.loads(path.read_text(encoding="utf-8-sig"))

def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")

def static_fingerprint() -> str:
    h = hashlib.sha256()
    for path in sorted((ROOT / "site").rglob("*")):
        if path.is_file():
            rel = path.relative_to(ROOT / "site").as_posix()
            h.update(rel.encode("utf-8"))
            h.update(hashlib.sha256(path.read_bytes()).digest())
    return h.hexdigest()

def check_target(target: str) -> pathlib.Path:
    if not isinstance(target, str) or not target.strip() or len(target) > 800:
        raise ValueError("Un dossier local de destination est requis.")
    path = pathlib.Path(target).expanduser().resolve()
    site = (ROOT / "site").resolve()
    if path == ROOT or ROOT in path.parents or path == site:
        raise ValueError("La destination ne peut pas être située dans Ekole.")
    if path == path.parent:
        raise ValueError("Impossible de copier vers la racine d'un disque.")
    for ancestor in [path, *path.parents]:
        if (ancestor / ".git").exists():
            raise ValueError("La destination appartient à un dépôt Git; utiliser un dossier statique distinct.")
    return path

def verify_public_files() -> None:
    site = ROOT / "site"
    allowed = {".html", ".css", ".js", ".json", ".svg", ".png", ".jpg", ".jpeg", ".webp", ".ico", ".txt", ".xml", ".woff", ".woff2"}
    for path in site.rglob("*"):
        if path.is_symlink():
            raise ValueError(f"Lien symbolique interdit dans le site public : {path.name}")
        if not path.is_file():
            continue
        relative = path.relative_to(site).as_posix().lower()
        if path.suffix.lower() not in allowed or any(part in relative for part in [".env", "secret", "token", "/evaluation/", "/authoring/", "/livraison/", "/vendor/"]):
            raise ValueError(f"Fichier non autorisé pour export public : {relative}")

def catalog() -> list[dict]:
    obj = read_json(ROOT / "catalogue/202_kristals.json")
    if not isinstance(obj, dict) or not isinstance(obj.get("kristals"), list):
        raise ValueError("Catalogue absent ou invalide.")
    return obj["kristals"]

def overview() -> dict:
    records = catalog()
    graph = read_json(ROOT / "catalogue/graphe_pedagogique.json")
    portal = read_json(ROOT / "organisation/kristal-portail-ekole.candidat.json")
    codes = sorted(set(x.get("discipline", "") for x in records))
    status = {"declared": len(records), "folders": sum((ROOT / "kristals" / r["id"] / "livraison/MANIFEST.json").is_file() for r in records)}
    return {
        "project": "Ekole", "updated": utcnow(), "root": str(ROOT),
        "catalog": status, "items": sum(int(x.get("nombre_items", 0)) for x in records),
        "disciplines": len(codes), "waves": {str(w): sum(r.get("vague") == w for r in records) for w in range(5)},
        "relations": len(graph.get("relations", [])), "portal": {"profile": portal.get("profile"), "status": portal.get("status"), "pages": len(portal.get("pages", []))},
        "site": {"html": (ROOT / "site/index.html").is_file(), "logo": (ROOT / "site/assets/ekole-logo.svg").is_file(), "data": (ROOT / "site/data/index.json").is_file()},
        "status_note": "Livraisons pédagogiques à revoir; portail candidat. Aucun État v9 ni nœud v10 publié n'est attesté par cette console.",
        "features": {"local_preview": True, "moodle_write": False, "github_write": False, "server_write": False, "semantik_call": False, "konstellation_call": False},
    }

def courses(search: str = "", discipline: str = "", wave: str = "") -> dict:
    records = catalog()
    query = search.casefold().strip()
    matched = []
    for r in records:
        if discipline and r.get("discipline") != discipline:
            continue
        if wave and str(r.get("vague")) != wave:
            continue
        if query and query not in " ".join(str(r.get(k,"")) for k in ("id", "titre", "discipline", "objectif")).casefold():
            continue
        matched.append({k: r.get(k) for k in ("id", "titre", "discipline", "vague", "nombre_items", "statut")})
    return {"total": len(matched), "courses": matched[:202], "disciplines": sorted({r.get("discipline", "") for r in records})}

def inspect_kristal(kid: str) -> dict:
    if not ID_RE.fullmatch(kid):
        raise ValueError("Identifiant de Kristal invalide.")
    record = next((r for r in catalog() if r["id"] == kid), None)
    if record is None:
        raise ValueError("Kristal introuvable dans le registre.")
    base = ROOT / "kristals" / kid
    expected = ["authoring/PARCOURS.md", "authoring/CONTRAT_PEDAGOGIQUE.json", "contenu/01_NOTIONS_ET_EXEMPLES.md", "contenu/02_DIAGNOSTIC.md", "contenu/03_ENSEIGNEMENT_GUIDE.md", "contenu/04_PRATIQUE_ACCOMPAGNEE.md", "contenu/05_PRATIQUE_AUTONOME.md", "contenu/06_REMEDIATION_ET_TRANSFERT.md", "evaluation/PLAN_EVALUATION.md", "evaluation/BANQUE_ITEMS.json", "evaluation/GRILLE_MAITRISE.md", "sources/REFERENCES_CONTENU.md", "livraison/MANIFEST.json", "livraison/VALIDATION.md"]
    present = [rel for rel in expected if (base / rel).is_file() and (base / rel).stat().st_size > 0]
    faults = []
    try:
        bank = read_json(base / "evaluation/BANQUE_ITEMS.json")
        items = bank.get("items", [])
        item_ids = [q.get("item_id") for q in items]
        if len(item_ids) != len(set(item_ids)):
            faults.append("Doublons dans les identifiants des items")
        if bank.get("family_id") != record["family_id"]:
            faults.append("La famille d'évaluation diffère du registre")
        modes = sorted({q.get("mode", "") for q in items})
        review = sum(q.get("validation_status") == "a_revoir" for q in items)
    except Exception as e:
        items, modes, review = [], [], 0
        faults.append("Impossible d'analyser la banque : " + str(e))
    relations = read_json(ROOT / "catalogue/graphe_pedagogique.json").get("relations", [])
    related = [{"type": r.get("type"), "to": r.get("to")} for r in relations if r.get("from") == kid]
    return {"record": record, "files": {"count": len(present), "expected": len(expected), "missing": sorted(set(expected) - set(present))}, "evaluation": {"items": len(items), "to_review": review, "modes": modes}, "relations": related, "issues": faults, "course_url": "/?cours=" + kid}

def integrations() -> dict:
    # Informational only. Never attempt to connect or publish automatically.
    parent = ROOT.parent
    neighbors = {
        "uckk-moodle": parent / "uckk-moodle",
        "UCKK_ops_console": parent / "UCKK_ops_console",
        "Mediatheque": parent / "Mediatheque",
        "SemantiK_Architect": parent / "SemantiK_Architect",
        "Konstellation": parent / "Konstellation",
    }
    return {"neighbors": [{"name": n, "present": p.is_dir(), "path": str(p)} for n,p in neighbors.items()],
            "references": {"framework_v10": (ROOT / "vendor/reference-only/kristal-framework-v10-source.zip").exists(), "moodle_plan": (ROOT / "plans/moodle_projection_dry_run.json").exists()},
            "connections": {"moodle": "read_only_plan", "github": "read_only_git", "semantik": "adapter_non_branche", "konstellation": "adapter_non_branche", "mediatheque": "references_seulement"}}

def git_status() -> dict:
    if not shutil.which("git"):
        return {"available": False, "reason": "Git absent du PATH"}
    def call(args):
        return subprocess.run(["git", "-C", str(ROOT), *args], text=True, capture_output=True, timeout=8, encoding="utf-8", errors="replace")
    r = call(["rev-parse", "--is-inside-work-tree"])
    if r.returncode != 0 or r.stdout.strip() != "true":
        return {"available": True, "repository": False, "reason": "Dossier Ekole non initialisé comme dépôt Git"}
    branch = call(["branch", "--show-current"])
    status = call(["status", "--porcelain", "--untracked-files=no"])
    return {"available": True, "repository": True, "branch": branch.stdout.strip() or "(détachée)", "changed_tracked_files": len(status.stdout.splitlines()) if status.returncode == 0 else None, "writes_enabled": False}

def check_install() -> dict:
    paths = ["README.md", "tools/ekole.py", "catalogue/202_kristals.json", "catalogue/graphe_pedagogique.json", "organisation/kristal-portail-ekole.candidat.json", "site/index.html", "site/app.js", "site/style.css", "opsconsole/web/index.html"]
    return {"success": all((ROOT / p).is_file() for p in paths), "files": {p: (ROOT / p).is_file() for p in paths}}

class Service:
    def __init__(self):
        self.token = secrets.token_urlsafe(32)
        self.lock = threading.Lock()
        self.preview = None
        self.preview_thread = None
        self.records = []
        self.last_plan = None

    def record(self, action: str, result: dict):
        entry = {"at": utcnow(), "action": action, "ok": bool(result.get("ok")), "detail": result.get("message", "")[:160], "seconds": result.get("seconds", 0)}
        self.records.insert(0, entry)
        self.records[:] = self.records[:80]
        try:
            LOGDIR.mkdir(exist_ok=True)
            with (LOGDIR / "operations.jsonl").open("a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        except OSError:
            pass

    def run_cli(self, cmd: str, target: str | None = None, apply=False) -> dict:
        args = [sys.executable, str(MAIN_TOOL), cmd]
        if cmd == "deploy":
            if not target:
                raise ValueError("Destination manquante")
            args += ["--target", target]
            if apply:
                args.append("--apply")
        started = time.monotonic()
        r = subprocess.run(args, cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=120)
        output = (r.stdout + ("\n" + r.stderr if r.stderr else ""))[-30000:]
        return {"ok": r.returncode == 0, "message": ("Opération réussie" if r.returncode == 0 else "Opération échouée"), "returncode": r.returncode, "output": output, "seconds": round(time.monotonic() - started, 2)}

    def start_preview(self) -> dict:
        if self.preview is not None:
            return {"ok": True, "message": "Prévisualisation déjà en service", "url": "http://127.0.0.1:8765/"}
        site = ROOT / "site"
        class SiteHandler(SimpleHTTPRequestHandler):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, directory=str(site), **kwargs)
            def log_message(self, *_):
                return
        try:
            server = ThreadingHTTPServer(("127.0.0.1", 8765), SiteHandler)
        except OSError:
            return {"ok": False, "message": "Port 8765 occupé : le portail est peut-être déjà lancé séparément.", "url": "http://127.0.0.1:8765/"}
        self.preview = server
        self.preview_thread = threading.Thread(target=server.serve_forever, daemon=True)
        self.preview_thread.start()
        return {"ok": True, "message": "Portail local démarré", "url": "http://127.0.0.1:8765/"}

    def stop_preview(self) -> dict:
        if self.preview is None:
            return {"ok": True, "message": "Aucun portail démarré par cette console"}
        self.preview.shutdown()
        self.preview.server_close()
        self.preview = None
        return {"ok": True, "message": "Prévisualisation de la console arrêtée"}

    def action(self, req: dict) -> dict:
        action = req.get("action")
        started = time.monotonic()
        if not isinstance(action, str):
            raise ValueError("Action invalide")
        if action not in FIXED_ACTIONS | {"preview-start", "preview-stop", "deploy-dry-run", "deploy-local-apply"}:
            raise ValueError("Action refusée : non autorisée")
        with self.lock:
            if action in FIXED_ACTIONS:
                if action == "pages-zip":
                    verify_public_files()
                result = self.run_cli(action)
            elif action == "preview-start":
                result = self.start_preview()
            elif action == "preview-stop":
                result = self.stop_preview()
            elif action == "deploy-dry-run":
                target = str(check_target(req.get("target", "")))
                verify_public_files()
                result = self.run_cli("deploy", target)
                if result["ok"]:
                    self.last_plan = {"target": target, "fingerprint": static_fingerprint(), "time": time.monotonic(), "nonce": secrets.token_urlsafe(18)}
                    result["plan_id"] = self.last_plan["nonce"]
                    result["message"] = "Simulation terminée, aucune copie effectuée"
            else:
                target = str(check_target(req.get("target", "")))
                p = self.last_plan
                if not p or p["target"] != target or p["nonce"] != req.get("plan_id"):
                    raise ValueError("Simulation préalable correspondante requise")
                if time.monotonic() - p["time"] > 600 or static_fingerprint() != p["fingerprint"]:
                    raise ValueError("Simulation périmée ou site modifié : recommencer la simulation")
                if req.get("confirmation") != LOCAL_CONFIRMATION:
                    raise ValueError("Confirmation exacte requise : " + LOCAL_CONFIRMATION)
                verify_public_files()
                self.last_plan = None
                result = self.run_cli("deploy", target, apply=True)
                result["message"] = "Copie locale terminée" if result["ok"] else "Copie locale échouée"
            result["seconds"] = round(time.monotonic() - started, 2)
            self.record(action, result)
            return result

service = Service()

class Handler(BaseHTTPRequestHandler):
    server_version = "EkoleOps/0.1"

    def log_message(self, *_):
        return

    def common_headers(self, mime: str = "application/json; charset=utf-8"):
        self.send_header("Content-Type", mime)
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Security-Policy", "default-src 'self'; img-src 'self'; style-src 'self'; script-src 'self'; connect-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'")

    def send_body(self, payload: bytes, code=200, mime="application/json; charset=utf-8"):
        self.send_response(code)
        self.common_headers(mime)
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def send_json(self, payload: dict, code=200):
        self.send_body(json.dumps(payload, ensure_ascii=False).encode("utf-8"), code)

    def do_GET(self):
        try:
            url = urllib.parse.urlsplit(self.path)
            path = url.path
            query = urllib.parse.parse_qs(url.query)
            if path == "/":
                page = (WEB / "index.html").read_text(encoding="utf-8")
                page = page.replace("__CSRF_TOKEN__", html.escape(service.token, quote=True))
                self.send_body(page.encode("utf-8"), mime="text/html; charset=utf-8")
            elif path in ("/app.js", "/style.css", "/logo.svg"):
                mime = ("text/javascript; charset=utf-8" if path.endswith(".js") else "image/svg+xml" if path.endswith(".svg") else "text/css; charset=utf-8")
                self.send_body((WEB / path.lstrip("/")).read_bytes(), mime=mime)
            elif path == "/api/overview":
                self.send_json({"overview": overview(), "git": git_status(), "preview": bool(service.preview)})
            elif path == "/api/courses":
                self.send_json(courses((query.get("q") or [""])[0], (query.get("discipline") or [""])[0], (query.get("wave") or [""])[0]))
            elif path == "/api/course":
                self.send_json(inspect_kristal((query.get("id") or [""])[0]))
            elif path == "/api/integrations":
                self.send_json(integrations())
            elif path == "/api/records":
                self.send_json({"records": service.records[:60], "preview": bool(service.preview)})
            elif path == "/api/health":
                self.send_json(check_install())
            else:
                self.send_json({"error": "Ressource introuvable"}, 404)
        except (ValueError, KeyError, OSError, json.JSONDecodeError) as e:
            self.send_json({"error": str(e)}, 400)

    def do_POST(self):
        try:
            if self.path != "/api/action":
                self.send_json({"error": "Action non trouvée"}, 404)
                return
            origin = self.headers.get("Origin")
            if origin and origin != f"http://127.0.0.1:{self.server.server_port}":
                self.send_json({"error": "Origine interdite"}, 403)
                return
            if self.headers.get("X-Ekole-Token") != service.token or not self.headers.get("Content-Type", "").startswith("application/json"):
                self.send_json({"error": "Action refusée (jeton local ou type de requête incorrect)"}, 403)
                return
            n = int(self.headers.get("Content-Length", "0"))
            if n < 2 or n > MAX_POST:
                self.send_json({"error": "Corps de requête invalide"}, 413)
                return
            data = json.loads(self.rfile.read(n).decode("utf-8"))
            if not isinstance(data, dict):
                raise ValueError("Corps JSON objet requis")
            self.send_json(service.action(data))
        except (ValueError, KeyError, OSError, json.JSONDecodeError, subprocess.TimeoutExpired) as e:
            self.send_json({"ok": False, "error": str(e)}, 400)

def main():
    parser = argparse.ArgumentParser(description="Ekole OpsConsole : local only")
    parser.add_argument("--check", action="store_true", help="Vérifier que le dépôt contient les fichiers attendus")
    parser.add_argument("--no-browser", action="store_true")
    parser.add_argument("--port", type=int, default=8766)
    args = parser.parse_args()
    if args.check:
        result = check_install()
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result["success"] else 1
    if not check_install()["success"]:
        print("Ekole incomplet. Extraire l'overlay dans la racine du dépôt avant de lancer la console.", file=sys.stderr)
        return 2
    if args.port < 1024 or args.port > 65535:
        parser.error("Port autorisé : 1024-65535")
    try:
        server = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    except OSError as exc:
        print("Impossible d'ouvrir le port local : " + str(exc), file=sys.stderr)
        return 3
    print(f"Ekole OpsConsole : http://127.0.0.1:{args.port}/\nFermer cette fenêtre ou Ctrl+C pour arrêter.")
    if not args.no_browser:
        threading.Timer(0.5, lambda: webbrowser.open(f"http://127.0.0.1:{args.port}/")).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        service.stop_preview()
        server.server_close()
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
