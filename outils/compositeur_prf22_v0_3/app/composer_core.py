"""Compositeur de situations Ékole — brouillons locaux, sans admission runtime.

Sources: Kontexte (trames/missions/exercices/micro-situations/Kristals/rôles).
Do not publish, authorize, or send real student data from this module.
"""
from __future__ import annotations

import hashlib
import json
import math
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

FORMAT = "ekole.situation-composition-draft/0.1"
PREFERRED_KONTEXTE = Path(r"C:\mycode\Ekole\Kontexte")
VALID_REALITY = ("fictif", "réel", "mixte")
MAX_PARTICIPANTS = 30


def _read(path: Path) -> dict:
    with path.open("r", encoding="utf-8-sig") as stream:
        data = json.load(stream)
    if not isinstance(data, dict):
        raise ValueError(f"Document non objet: {path}")
    return data


def _stable_id(prefix: str, obj: Any) -> str:
    content = json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return prefix + hashlib.sha256(content.encode("utf-8")).hexdigest()[:16]


def _title(obj: Any) -> str:
    if isinstance(obj, str):
        return obj
    if isinstance(obj, dict):
        return obj.get("fr-CA") or obj.get("fr") or next((v for v in obj.values() if isinstance(v, str)), "")
    return str(obj or "")


@dataclass
class Catalogue:
    root: Path
    templates: list[dict]
    activities: list[dict]
    objectives: list[dict]
    roles: list[dict]
    trames_count: int
    missions_count: int

    def template(self, source_id: str) -> dict:
        for item in self.templates:
            if item["ref"] == source_id:
                return item
        raise ValueError(f"Situation inconnue : {source_id}")

    def activity(self, ref: str) -> dict:
        for item in self.activities:
            if item["ref"] == ref:
                return item
        raise ValueError(f"Exercice inconnu : {ref}")

    def objective(self, ref: str) -> dict:
        for item in self.objectives:
            if item["ref"] == ref:
                return item
        raise ValueError(f"Objectif inconnu : {ref}")


def load_catalogue(root: Path | str) -> Catalogue:
    """Read and normalize existing Kontexte sources without mutating them."""
    root = Path(root)
    required = [
        "data/trames/catalogue-neutral-v0.2.json",
        "data/locales/qc/fr-CA/grade3/exercices-deterministes.json",
        "data/locales/qc/fr-CA/grade3/micro-situations-34.json",
        "data/catalogue/202_kristals.json",
    ]
    absent = [p for p in required if not (root / p).is_file()]
    if absent:
        raise FileNotFoundError("Sources Kontexte absentes : " + ", ".join(absent) + " (racine " + str(root) + ")")
    trames_data = _read(root / required[0])
    micro_data = _read(root / required[2])
    ex_data = _read(root / required[1])
    kristal_data = _read(root / required[3])

    templates = []
    for trame in trames_data.get("scenarios", []):
        templates.append({
            "ref": "trame:" + trame["id"], "source_type": "trame", "source_id": trame["id"],
            "titre": trame.get("titre", trame["id"]), "probleme": trame.get("tension", ""),
            "declencheur": trame.get("declencheur", ""),
            "roles": trame.get("roles", []), "domaines_potentiels": trame.get("domaines_potentiels", []),
            "family": trame.get("famille", ""), "source_format": trames_data.get("format"),
            "source_relpath": required[0],
        })
    missions_count = 0
    for path in sorted((root / "data" / "missions").glob("*.json")):
        mission = _read(path)
        if mission.get("format") != "kontexte.mission/1":
            continue
        missions_count += 1
        templates.append({
            "ref": "mission:" + mission["id"], "source_type": "mission", "source_id": mission["id"],
            "titre": _title(mission.get("title")), "probleme": _title(mission.get("fiction")),
            "declencheur": _title(mission.get("fiction")),
            "roles": mission.get("roles", []), "domaines_potentiels": [],
            "family": "mission existante", "source_format": mission.get("format"),
            "source_relpath": path.relative_to(root).as_posix(),
            "step_refs": [x["id"] for x in mission.get("steps", [])],
        })

    activities = []
    for micro in micro_data.get("modules", []):
        activities.append({
            "ref": "micro:" + micro["id"], "source_type": "micro_situation",
            "titre": micro.get("titre", micro["id"]), "consigne": micro.get("tache_concrete", ""),
            "preuve_attendue": micro.get("preuve_attendue", ""),
            "domaine": micro.get("discipline", ""),
            "objective_candidate": micro.get("objet_pedagogique"),
            "qualification": "activité proposée à relire et instancier",
            "source_relpath": required[2],
        })
    for ex in ex_data.get("exercices", []):
        activities.append({
            "ref": _stable_id("det:", ex), "source_type": "exercice_deterministe",
            "titre": ex.get("question", ""), "consigne": ex.get("question", ""),
            "preuve_attendue": "Réponse et vérification selon fixture locale (non décision de maîtrise)",
            "domaine": "mathématiques (fixture)", "objective_candidate": None,
            "qualification": "pratique arithmétique locale, non évaluation réelle",
            "scenario_id": ex.get("scenario_id"),
            "source_relpath": required[1],
        })
    objectives = []
    for kr in kristal_data.get("kristals", []):
        objectives.append({
            "ref": kr["id"], "titre": kr.get("titre", ""), "objectif": kr.get("objectif", ""),
            "preuve_attendue": kr.get("preuve", ""), "discipline": kr.get("discipline", ""),
            "source_status": kr.get("statut", ""),
            "source_relpath": required[3],
        })
    role_dir = root / "data" / "roles"
    roles = []
    if role_dir.is_dir():
        for path in sorted(role_dir.glob("*.json")):
            role = _read(path)
            if role.get("format") == "kontexte.role/1":
                roles.append({"id": role["id"], "name": _title(role.get("name")), "visual_id": role.get("visual_id"), "source_relpath": path.relative_to(root).as_posix()})

    def unique(items: list[dict], kind: str) -> None:
        refs = [x["ref"] for x in items]
        if len(refs) != len(set(refs)):
            raise ValueError(f"Références {kind} en double")

    unique(templates, "situation"); unique(activities, "activité"); unique(objectives, "objectif")
    return Catalogue(root=root, templates=templates, activities=activities, objectives=objectives,
                     roles=roles, trames_count=len(trames_data.get("scenarios", [])), missions_count=missions_count)


def group_sizes(participants: int, maximum: int) -> list[int]:
    if not isinstance(participants, int) or not 1 <= participants <= MAX_PARTICIPANTS:
        raise ValueError("Nombre de participants : 1 à 30")
    if not isinstance(maximum, int) or not 1 <= maximum <= 6:
        raise ValueError("Taille maximale d'équipe : 1 à 6")
    teams = math.ceil(participants / maximum)
    base, extra = divmod(participants, teams)
    return [base + (1 if i < extra else 0) for i in range(teams)]


def rotation_plan(team_ids: list[str], station_ids: list[str], parallel_posts: int = 1) -> list[dict]:
    """Capacity-aware rounds: every team sees each activity once, no overlaps.

    R=max(number of activities, ceil(number of teams / copies)). For station s,
    team t attends at round r=(floor(t/copies)+s) mod R. Distinct stations
    never conflict for a team; at most copies teams at a station per round.
    """
    if not team_ids or not station_ids or len(set(team_ids)) != len(team_ids) or len(set(station_ids)) != len(station_ids):
        raise ValueError("Équipes et stations doivent être non vides et uniques")
    if not isinstance(parallel_posts, int) or not 1 <= parallel_posts <= 10:
        raise ValueError("Nombre de postes parallèles : 1 à 10")
    tcount, scount = len(team_ids), len(station_ids)
    rounds = max(scount, math.ceil(tcount / parallel_posts))
    output = []
    for r in range(rounds):
        assignments = []
        for ti, team in enumerate(team_ids):
            station = next((station_ids[si] for si in range(scount)
                            if (ti // parallel_posts + si) % rounds == r), None)
            assignments.append({
                "team_id": team, "station_id": station,
                "post_id": (f"{station}-poste-{ti % parallel_posts + 1:02d}" if station else None),
                "status": "visit" if station else "independent_or_break",
            })
        output.append({"round": r + 1, "assignments": assignments})
    return output


def _required_text(s: str, field: str, max_length: int = 200) -> str:
    if not isinstance(s, str) or not s.strip() or len(s) > max_length:
        raise ValueError(f"{field} : texte obligatoire de 1 à {max_length} caractères")
    return s.strip()


def compose_draft(
    catalog: Catalogue, source_ref: str, activities: list[str], participants: int,
    maximum_per_team: int, *, epoch: str, cultural_frame: str, setting: str,
    reality: str, language: str = "fr-CA", objectives: list[str] | None = None,
    notes: str = "", distribution: str = "rotation", parallel_posts: int = 1,
) -> dict:
    """Compose a versioned *planning draft*. No runtime effects or grants."""
    if reality not in VALID_REALITY:
        raise ValueError("Réalité : fictif, réel ou mixte")
    epoch = _required_text(epoch, "Époque")
    cultural_frame = _required_text(cultural_frame, "Contexte culturel")
    setting = _required_text(setting, "Lieu / cadre")
    if language not in ("fr-CA", "en-CA"):
        raise ValueError("Langue non prise en charge par ce prototype")
    if distribution != "rotation":
        raise ValueError("Distribution inconnue")
    if len(set(activities)) != len(activities) or not 1 <= len(activities) <= 12:
        raise ValueError("Sélectionne de 1 à 12 activités distinctes")
    objectives = objectives or []
    if len(set(objectives)) != len(objectives) or len(objectives) > 20:
        raise ValueError("Maximum 20 objectifs distincts")
    source = catalog.template(source_ref)
    selected = [catalog.activity(ref) for ref in activities]
    selected_objectives = [catalog.objective(ref) for ref in objectives]
    sizes = group_sizes(participants, maximum_per_team)
    teams = []
    cursor = 1
    suggested_roles = source.get("roles", [])
    for i, size in enumerate(sizes):
        members = [f"P{x:02d}" for x in range(cursor, cursor + size)]
        cursor += size
        teams.append({
            "id": f"equipe-{i+1:02d}", "participant_placeholders": members,
            "size": size, "suggested_role": suggested_roles[i % len(suggested_roles)] if suggested_roles else None,
            "assignment_status": "teacher_to_approve",
        })
    stations = []
    for i, ex in enumerate(selected):
        stations.append({
            "id": f"station-{i+1:02d}", "activity_ref": ex["ref"],
            "title": ex["titre"], "source_type": ex["source_type"],
            "qualification": ex["qualification"],
            "evidence_expected": ex["preuve_attendue"],
            "adaptation_status": "to_review",
        })
    cycles = rotation_plan([x["id"] for x in teams], [s["id"] for s in stations], parallel_posts)
    world_slug = re.sub(r"[^a-z0-9-]", "-", source["source_id"].lower().replace("_", "-"))
    return {
        "format": FORMAT,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "status": "draft_not_admitted",
        "authorities": {
            "scenario_source": "Kontexte", "exercise_catalogue": "Kontexte / Inkuisite selon le contenu",
            "objectives_and_evidence": "Ékole", "role_proposals": "Kompose",
            "operational_tasks": "Orgo", "world_ownership": "Orgo_Worlds",
            "social_collaboration": "Konnaxion", "channels": ["Web", "Kor", "Kamel"],
        },
        "source": {
            "reference": source["ref"], "source_format": source["source_format"],
            "source_relpath": source["source_relpath"], "title": source["titre"],
            "problem": source["probleme"], "narrative_role_codes": suggested_roles,
            "source_step_refs_unchanged": source.get("step_refs", []),
        },
        "world_context": {
            "epoch": epoch, "cultural_frame": cultural_frame, "place": setting,
            "reality": reality, "language": language,
            "notes": notes[:2000], "cultural_validation": "pending_human_review",
        },
        "activity_bindings": [
            {
                "activity_ref": ex["ref"], "source_type": ex["source_type"],
                "source_relpath": ex["source_relpath"], "title": ex["titre"],
                "activity_status": "candidate_not_authorized",
                "objective_candidate": ex.get("objective_candidate"),
            } for ex in selected
        ],
        "learning_objective_links": [
            {"objective_ref": o["ref"], "source_relpath": o["source_relpath"],
             "title": o["titre"], "status": "candidate_teacher_review_required"}
            for o in selected_objectives
        ],
        "participation": {
            "participant_count": participants, "anonymized_placeholder_only": True,
            "mode": "solo" if participants == 1 else ("petit_groupe" if participants <= 4 else "groupes_rotatifs"),
            "maximum_per_team": maximum_per_team,
            "teams": teams,
            "role_use": "rôles narratifs réutilisables par équipe, pas des permissions",
            "solo_substitution": "Un indice ou un personnage manquant est fourni par le matériel/enseignant, jamais bloquant" if participants == 1 else None,
            "stations": stations, "rotation": cycles,
            "parallel_posts_per_activity": parallel_posts,
            "additional_equipment_required": parallel_posts > 1,
            "when_team_idle": "lecture, exercice autonome, pause ou aide supervisée",
            "station_capacity": f"jusqu’à {parallel_posts} équipe(s) par activité et par ronde, chacune à son poste distinct",
            "role_validation": "teacher_required",
        },
        "collaboration": {
            "kontexte_hints": "utiliser les joins/fragments de la source, sans libération automatique",
            "communication": "Konnaxion / Kids, sous permissions serveur",
            "progress_from_messages": False,
        },
        "export_hints": {
            "orgo_world_slug_suggested": world_slug,
            "world_creation_performed": False,
            "tasks_dispatched": False, "qr_created": False,
            "runtime_admitted": False, "teacher_authorized": False,
            "real_learner_profiles_loaded": False,
        },
        "required_reviews": [
            "adéquation au niveau scolaire", "exactitude historique et culturelle",
            "sécurité et consentements", "objectifs pédagogiques et critères de preuve",
            "rôles et disponibilité", "matériel et encadrement des postes parallèles", "autorisations serveur et isolement de classe",
        ],
    }


def validate_draft(draft: dict) -> None:
    if draft.get("format") != FORMAT or draft.get("status") != "draft_not_admitted":
        raise ValueError("Format de brouillon invalide")
    hints = draft.get("export_hints", {})
    for critical in ("world_creation_performed", "tasks_dispatched", "qr_created", "runtime_admitted", "teacher_authorized", "real_learner_profiles_loaded"):
        if hints.get(critical) is not False:
            raise ValueError(f"Le brouillon ne peut pas autoriser : {critical}")
    p = draft["participation"]
    n = p["participant_count"]
    if not isinstance(n, int) or n not in range(1, 31):
        raise ValueError("Participants hors limites")
    teams = p["teams"]; stations = p["stations"]; rotations = p["rotation"]
    if sum(t["size"] for t in teams) != n:
        raise ValueError("Nombre de participants incohérent")
    all_members = [m for team in teams for m in team["participant_placeholders"]]
    if len(all_members) != len(set(all_members)) or len(all_members) != n:
        raise ValueError("Participants fictifs dupliqués")
    team_ids = {t["id"] for t in teams}; station_ids = {s["id"] for s in stations}
    visited = {tid: [] for tid in team_ids}
    parallel_posts = p.get("parallel_posts_per_activity", 1)
    if not isinstance(parallel_posts, int) or not 1 <= parallel_posts <= 10:
        raise ValueError("Nombre de postes invalide")
    for rd in rotations:
        used = set()
        counts = {sid: 0 for sid in station_ids}
        if len(rd["assignments"]) != len(teams):
            raise ValueError("Ronde incomplète")
        for a in rd["assignments"]:
            if a["team_id"] not in team_ids:
                raise ValueError("Équipe inconnue")
            sid = a["station_id"]
            if sid is not None:
                if sid not in station_ids or a.get("post_id") in used:
                    raise ValueError("Conflit de capacité de station")
                used.add(a["post_id"])
                counts[sid] += 1
                if counts[sid] > parallel_posts:
                    raise ValueError("Station surchargée")
                visited[a["team_id"]].append(sid)
    if any(set(v) != station_ids or len(v) != len(station_ids) for v in visited.values()):
        raise ValueError("Toutes les équipes ne visitent pas toutes les stations exactement une fois")


def format_preview(draft: dict) -> str:
    validate_draft(draft)
    src = draft["source"]; c = draft["world_context"]; p = draft["participation"]
    lines = [
        f"COMPOSITION — {src['title']}", "=" * 68,
        f"Source : {src['reference']} (contenu d'origine inchangé)",
        f"Problème : {src['problem']}",
        f"Cadre : {c['reality']} · {c['epoch']} · {c['place']}",
        f"Contexte culturel : {c['cultural_frame']} (à faire relire)",
        f"Langue : {c['language']}", "",
        f"Participants : {p['participant_count']} · équipes : {len(p['teams'])} · stations : {len(p['stations'])}",
        f"Mode : {p['mode']} · postes simultanés par exercice : {p['parallel_posts_per_activity']}",
    ]
    for t in p["teams"]:
        lines.append(f"  {t['id']} ({t['size']}) — rôle proposé : {t['suggested_role'] or 'à définir'} — {', '.join(t['participant_placeholders'])}")
    lines.extend(["", "STATIONS — exercices indépendants du scénario"])
    for s in p["stations"]:
        lines.append(f"  {s['id']} · {s['source_type']} · {s['title']}")
    lines.extend(["", "ROTATION — une équipe maximum par station et par ronde"])
    for rd in p["rotation"]:
        lines.append("  Ronde " + str(rd["round"]) + " : " + "; ".join(
            a["team_id"] + "→" + (a.get("post_id") or "activité autonome") for a in rd["assignments"]))
    lines.extend(["", "OBJECTIFS CANDIDATS (non approuvés)"])
    links = draft["learning_objective_links"]
    lines.extend(["  " + x["objective_ref"] + " — " + x["title"] for x in links] or ["  Aucun objectif explicitement choisi"])
    lines.extend(["", "IMPORTANT : BROUILLON DE PLANIFICATION SEULEMENT.",
                  "Aucun World réel créé, aucune tâche distribuée, aucun accès élève autorisé.",
                  "Toute attribution et toute preuve d'apprentissage doivent être validées par l'enseignant."])
    return "\n".join(lines) + "\n"


def export_draft(draft: dict, folder: Path | str) -> tuple[Path, Path]:
    validate_draft(draft)
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    stem = re.sub(r"[^a-z0-9-]", "-", draft["source"]["reference"].lower().replace(":", "-"))
    # Distinct filename per export, with no collision or overwrite.
    nonce = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    json_path = folder / f"situation-{stem}-{nonce}.json"
    txt_path = json_path.with_suffix(".txt")
    with json_path.open("x", encoding="utf-8", newline="\n") as f:
        json.dump(draft, f, ensure_ascii=False, indent=2)
        f.write("\n")
    with txt_path.open("x", encoding="utf-8", newline="\n") as f:
        f.write(format_preview(draft))
    return json_path, txt_path


def export_activity_index(catalog: Catalogue, folder: Path | str) -> Path:
    """Generate a clear, read-only index of source activities (not answer keys)."""
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    index = {
        "format": "ekole.activity-index/0.1",
        "status": "references_only_teacher_review_required",
        "source": "Kontexte",
        "activities": [
            {key: x.get(key) for key in (
                "ref", "source_type", "titre", "domaine", "consigne", "preuve_attendue",
                "source_relpath", "qualification", "objective_candidate", "scenario_id") if key in x}
            for x in catalog.activities
        ],
        "notice": "Répertoire d'activités, pas un registre de compétences évaluées. Aucune clé de réponse publiée.",
    }
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    target = folder / f"repertoire-activites-{stamp}.json"
    with target.open("x", encoding="utf-8", newline="\n") as f:
        json.dump(index, f, ensure_ascii=False, indent=2)
        f.write("\n")
    return target
