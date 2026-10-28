#!/usr/bin/env python3
"""Ekole: serveur local indépendant des curriculums (stdlib Python 3.10+).
Dépôts frères : ./ekole (moteur), ./ekole-quebec et ./ecole-pastorale (contenus).
Le contenu n'est jamais copié ni importé dans le dépôt moteur.
"""
from __future__ import annotations
import argparse
import hashlib
import http.server
import json
import os
import pathlib
import re
import secrets
import socket
import sys
import threading
import time
import urllib.parse
import webbrowser
import visuals
import publications
from tandem import load_synthetic_preview, PreviewError

ENGINE = pathlib.Path(__file__).resolve().parent
SAFE_ID = re.compile(r"[A-Za-z0-9_-]{1,80}\Z")
EMPTY_PACK = {
    'format': 'ekole.content-pack/0.1', 'id': 'sans-contenu',
    'nom': 'Moteur Ekole sans corpus',
    'description': 'Déposez un dépôt de contenu à côté du moteur ou fournissez --contenu.',
    'langue': 'fr-CA', 'statut': 'aucun_contenu', 'cours': [], 'parcours': []
}


def load_pack(root: pathlib.Path | None) -> dict:
    if root is None:
        return EMPTY_PACK.copy()
    p = root / 'pack.json'
    if not p.is_file() or p.is_symlink():
        raise ValueError(f'Manifeste absent ou lien symbolique interdit : {p}')
    pack = json.loads(p.read_text(encoding='utf-8-sig'))
    if pack.get('format') != 'ekole.content-pack/0.1':
        raise ValueError('Format de manifeste non reconnu')
    if not isinstance(pack.get('cours'), list) or not isinstance(pack.get('parcours'), list):
        raise ValueError('Cours/parcours doivent être des listes')
    if not isinstance(pack.get('id'), str) or not SAFE_ID.fullmatch(pack['id']):
        raise ValueError('Identifiant de paquet invalide')
    if not isinstance(pack.get('nom'), str):
        raise ValueError('Nom du paquet manquant')
    ids = set()
    for c in pack['cours']:
        cid = c.get('id')
        if not isinstance(cid, str) or not SAFE_ID.fullmatch(cid) or cid in ids:
            raise ValueError(f'Identifiant de cours invalide ou dupliqué : {cid}')
        if c.get('fichier') != f'cours/{cid}.json':
            raise ValueError(f'Chemin de cours non autorisé : {cid}')
        if not isinstance(c.get('titre'), str) or not isinstance(c.get('prerequis', []), list):
            raise ValueError(f'Champs de cours invalides : {cid}')
        cp = root / 'cours' / (cid + '.json')
        if cp.is_symlink() or not cp.is_file() or not cp.resolve().is_relative_to(root.resolve()):
            raise ValueError(f'Fichier de cours manquant ou dangereux : {cid}')
        ids.add(cid)
    for c in pack['cours']:
        if not set(c.get('prerequis', [])).issubset(ids):
            raise ValueError(f'Prérequis inconnus : {c["id"]}')
    paths = set()
    for p in pack['parcours']:
        pid = p.get('id')
        if not isinstance(pid, str) or not SAFE_ID.fullmatch(pid) or pid in paths:
            raise ValueError(f'Parcours invalide : {pid}')
        if not isinstance(p.get('cours_ids'), list) or not set(p['cours_ids']).issubset(ids):
            raise ValueError(f'Références de parcours invalides : {pid}')
        paths.add(pid)
    return pack


def jsonify(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode('utf-8')


class Environment:
    def __init__(self, content: pathlib.Path | None, edition: bool, port_public: int = 8765, tandem_preview: dict | None = None):
        self.content = content
        self.pack = load_pack(content)
        self.by_id = {c['id']: c for c in self.pack['cours']}
        self.edition = edition
        self.port_public = port_public
        self.key = secrets.token_urlsafe(32)
        self.csrf = secrets.token_urlsafe(32)
        self.student_course_cache = {}
        # Projeté seulement dans l'éditeur local; aucune identité/mission distribuée aux enfants.
        self.tandem_preview = tandem_preview

    def student_course(self, cid):
        if cid not in self.by_id: return None
        # Le dossier expert et ses corrigés ne sont jamais lus par le portail public.
        source = self.content / 'publications' / 'eleve' / (cid + '.json') if self.content else None
        if source and source.is_file() and not source.is_symlink() and source.resolve().is_relative_to(self.content.resolve()):
            data = json.loads(source.read_text(encoding='utf-8-sig'))
            if data.get('id') != cid or not isinstance(data.get('modules'),list): raise ValueError('Publication élève invalide')
            return data
        # Ancien format de paquet sans vues distinctes: compatibilité pour les écoles
        # qui publient déjà leurs textes comme du contenu public.
        if self.pack.get('politique_publication') != 'vues_separees':
            return json.loads(self.course_path(cid).read_text(encoding='utf-8'))
        return {'id':cid,'titre':self.by_id[cid]['titre'],'statut_publication':'en_preparation',
                'modules':[], 'message':'Cette leçon est en préparation pour les élèves. Demande une autre activité à ton enseignant.'}

    def course_path(self, cid):
        if cid not in self.by_id or not SAFE_ID.fullmatch(cid) or self.content is None:
            return None
        p = self.content / 'cours' / (cid + '.json')
        if p.is_symlink() or not p.is_file() or not p.resolve().is_relative_to(self.content.resolve()):
            return None
        return p


def create_handler(env: Environment, teacher: bool = False):
    directory = ENGINE / ('enseignant-app' if teacher else 'site')

    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(directory), **kwargs)

        def end_headers(self):
            self.send_header('Cache-Control', 'no-store')
            self.send_header('X-Content-Type-Options', 'nosniff')
            self.send_header('Referrer-Policy', 'no-referrer')
            self.send_header('X-Frame-Options', 'DENY')
            self.send_header('Content-Security-Policy', "default-src 'self'; connect-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; object-src 'none'; base-uri 'none'; frame-ancestors 'none'")
            super().end_headers()

        def respond(self, status, body=b'', typ='text/plain; charset=utf-8'):
            self.send_response(status)
            self.send_header('Content-Type', typ)
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def json(self, status, value):
            return self.respond(status, jsonify(value), 'application/json; charset=utf-8')

        def authed(self):
            cookies = self.headers.get('Cookie', '')
            return any(secrets.compare_digest(chunk.strip().split('=', 1)[1], env.key)
                       for chunk in cookies.split(';') if chunk.strip().startswith('EkoleTeacher='))

        def do_GET(self):
            u = urllib.parse.urlsplit(self.path)
            route = u.path
            if teacher and route == '/open':
                candidate = urllib.parse.parse_qs(u.query).get('key', [''])[0]
                if not secrets.compare_digest(candidate, env.key):
                    return self.respond(403, b'Lien de session invalide')
                self.send_response(303)
                self.send_header('Location', '/')
                self.send_header('Set-Cookie', f'EkoleTeacher={env.key}; HttpOnly; SameSite=Strict; Path=/')
                self.end_headers()
                return
            if teacher and not self.authed():
                return self.respond(401, b'Espace local protege. Relancer le lanceur et utiliser son lien de session.')
            # Inventaire visuel : prompts et images brutes sont réservés à l'enseignant.
            visual = re.fullmatch(r'/api/visuels/([A-Za-z0-9_-]{1,80})\.json', route)
            if visual:
                cid=visual[1]
                if cid not in env.by_id or env.content is None: return self.respond(404,b'Visuels indisponibles')
                result=visuals.teacher_inventory(env.content,cid) if teacher else visuals.public_inventory(env.content,cid)
                return self.json(200,result)
            media = re.fullmatch(r'/api/media/([A-Za-z0-9_-]{1,80})/([A-Za-z0-9_-]{1,40})', route)
            if media:
                cid,slot=media.groups()
                if cid not in env.by_id or env.content is None or slot not in visuals.entries(env.content,cid):
                    return self.respond(404,b'Image introuvable')
                f=visuals.locate(env.content,cid,slot) if teacher else visuals.published_file(env.content,cid,slot)
                if not f:return self.respond(404,b'Image non publiee')
                try:
                    raw=f.read_bytes();fmt,w,h=visuals.image_info(raw)
                    return self.respond(200,raw,visuals.MIMES[fmt])
                except (OSError,ValueError):return self.respond(404,b'Image invalide')
            # Adaptateurs de ressources, en lecture seule, définis par le dépôt de contenu.
            # Aucun chemin de fichier arbitraire ni répertoire historique n'est exposé.
            if route in ('/api/integrations/spek.json', '/api/integrations/graphe.json', '/api/integrations/activites.json'):
                if env.content is None:
                    return self.respond(404, b'Integration indisponible')
                filename = route.rsplit('/', 1)[-1]
                # Les neuf fiches Spek historiques sont des scénarios enseignants,
                # jamais publiées telles quelles aux enfants.
                if not teacher and filename == 'spek.json':
                    filename = 'spek-eleve.json'
                candidate = env.content / 'integrations' / filename
                if candidate.is_symlink() or not candidate.is_file() or not candidate.resolve().is_relative_to(env.content.resolve()):
                    return self.respond(404, b'Integration indisponible')
                if candidate.stat().st_size > 2_000_000:
                    return self.respond(413, b'Ressource trop grande')
                return self.respond(200, candidate.read_bytes(), 'application/json; charset=utf-8')
            if route == '/api/tandem/preview.json':
                # La session de l'enseignant est vérifiée au début de do_GET.
                # Aucune route publique n'expose les fragments ou les tâches.
                if not teacher or env.tandem_preview is None:
                    return self.respond(404, b'Projection non disponible')
                return self.json(200, env.tandem_preview)
            if route == '/api/pack.json':
                if teacher: return self.json(200,env.pack)
                public=dict(env.pack)
                public['cours']=[{**{k:v for k,v in c.items() if k in ('id','titre','discipline','objectif','statut','fichier','prerequis')},
                                   'publication_eleve': bool(env.pack.get('politique_publication') != 'vues_separees' or
                                     (env.content and (env.content/'publications'/'eleve'/(c['id']+'.json')).is_file()))}
                                  for c in env.pack['cours']]
                return self.json(200, public)
            if route == '/api/health':
                return self.json(200, {'service': 'ekole', 'espace': 'editeur' if teacher else 'public',
                                       'contenu_charge': env.content is not None, 'cours': len(env.by_id)})
            student_draft=re.fullmatch(r'/api/brouillon-eleve/([A-Za-z0-9_-]{1,80})\.json',route)
            if teacher and student_draft:
                cid=student_draft[1];p=env.course_path(cid)
                if p is None:return self.respond(404,b'Cours inconnu')
                try:return self.json(200,publications.draft_read(env.content,cid,json.loads(p.read_text(encoding='utf8'))))
                except (ValueError,OSError,json.JSONDecodeError):return self.respond(500,b'Brouillon invalide')
            student_preview=re.fullmatch(r'/api/publication-eleve/([A-Za-z0-9_-]{1,80})\.json',route)
            if teacher and student_preview:
                cid=student_preview[1]
                if cid not in env.by_id:return self.respond(404,b'Cours inconnu')
                try:return self.json(200,env.student_course(cid))
                except (ValueError,OSError,json.JSONDecodeError):return self.respond(500,b'Publication invalide')
            if route == '/api/editor-config' and teacher:
                return self.json(200, {'csrf': env.csrf, 'edition': env.edition, 'port_public': env.port_public})
            match = re.fullmatch(r'/api/cours/([A-Za-z0-9_-]{1,80})\.json', route)
            if match:
                file = env.course_path(match[1])
                if not file:
                    return self.respond(404, b'Cours indisponible')
                try:
                    # Même URL pour les deux vues mais une provenance différente.
                    return self.respond(200,file.read_bytes(),'application/json; charset=utf-8') if teacher else self.json(200,env.student_course(match[1]))
                except (OSError,ValueError,json.JSONDecodeError):
                    return self.respond(500,b'Erreur de lecture')
            if route.startswith('/api/'):
                return self.respond(404, b'API inconnue')
            return super().do_GET()

        def do_POST(self):
            if not teacher or not env.edition:
                return self.respond(403, b'Edition desactivee')
            if not self.authed():
                return self.respond(401, b'Session requise')
            if self.headers.get('Origin') != f'http://127.0.0.1:{self.server.server_port}':
                return self.respond(403, b'Origine non autorisee')
            if not secrets.compare_digest(self.headers.get('X-Ekole-CSRF', ''), env.csrf):
                return self.respond(403, b'Protection CSRF')
            route=urllib.parse.urlsplit(self.path).path
            draft_post=re.fullmatch(r'/api/brouillon-eleve/([A-Za-z0-9_-]{1,80})\.json',route)
            draft_publish=re.fullmatch(r'/api/brouillon-eleve/([A-Za-z0-9_-]{1,80})/publier',route)
            if draft_post or draft_publish:
                cid=(draft_post or draft_publish)[1]
                p=env.course_path(cid)
                if p is None:return self.respond(404,b'Cours inconnu')
                n=self.headers.get('Content-Length','')
                if not n.isascii() or not n.isdigit() or int(n)>500000:return self.respond(413,b'Taille de fichier invalide')
                if self.headers.get('Content-Type','').split(';')[0]!='application/json':return self.respond(415,b'JSON attendu')
                try:
                    raw=self.rfile.read(int(n));expert=json.loads(p.read_text(encoding='utf8'))
                    if draft_post:
                        result=publications.draft_save(env.content,cid,json.loads(raw),expert)
                    else:
                        if self.headers.get('X-Ekole-Reviewed')!='yes':return self.respond(422,b'Confirmation de revue requise')
                        result=publications.publish(env.content,cid,expert)
                    return self.json(200,result)
                except FileExistsError as e:return self.respond(409,str(e).encode('utf8'))
                except (ValueError,OSError,json.JSONDecodeError) as e:return self.respond(422,str(e).encode('utf8'))
            upload=re.fullmatch(r'/api/visuels/([A-Za-z0-9_-]{1,80})/([A-Za-z0-9_-]{1,40})',route)
            publication=re.fullmatch(r'/api/visuels/([A-Za-z0-9_-]{1,80})/([A-Za-z0-9_-]{1,40})/(publier|retirer)',route)
            if upload or publication:
                cid,slot=(upload or publication).group(1,2)
                if cid not in env.by_id or env.content is None or slot not in visuals.entries(env.content,cid):
                    return self.respond(404,b'Emplacement inconnu')
                size=self.headers.get('Content-Length','')
                if not size.isascii() or not size.isdigit() or not 0<=int(size)<=visuals.MAX_BYTES:
                    return self.respond(413,b'Taille invalide')
                try:
                    if publication:
                        if self.headers.get('X-Ekole-Reviewed')!='yes':return self.respond(422,b'Validation manuelle requise')
                        if int(size):self.rfile.read(int(size))
                        result=visuals.set_publication(env.content,cid,slot,publication[3]=='publier')
                    else:
                        if self.headers.get('Content-Type','').split(';')[0]!='application/octet-stream':
                            return self.respond(415,b'Image binaire attendue')
                        raw=self.rfile.read(int(size))
                        result=visuals.save_image(env.content,cid,slot,raw,self.headers.get('X-Ekole-Replace')=='yes')
                    return self.json(200,result)
                except FileExistsError as err:return self.respond(409,str(err).encode('utf8'))
                except (ValueError,OSError) as err:return self.respond(422,str(err).encode('utf8'))
            m = re.fullmatch(r'/api/cours/([A-Za-z0-9_-]{1,80})\.json', urllib.parse.urlsplit(self.path).path)
            if not m:
                return self.respond(404, b'Ressource inconnue')
            path = env.course_path(m[1])
            if not path:
                return self.respond(404, b'Cours indisponible')
            n = self.headers.get('Content-Length', '')
            if not n.isascii() or not n.isdigit() or not (1 <= int(n) <= 2_000_000):
                return self.respond(413, b'Taille invalide')
            if self.headers.get('Content-Type', '').split(';')[0].strip() != 'application/json':
                return self.respond(415, b'JSON attendu')
            try:
                incoming = json.loads(self.rfile.read(int(n)))
                old_bytes = path.read_bytes()
                old = json.loads(old_bytes)
                if incoming.get('id') != m[1] or incoming.get('id') != old.get('id'):
                    return self.respond(422, b'Identite du cours refusee')
                # Simple text edition: metadata / provenance / invariant IDs remain untouched.
                previous = old.get('modules', [])
                updated = incoming.get('modules')
                if not isinstance(updated, list) or len(updated) != len(previous):
                    return self.respond(422, b'Structure des modules inchangeable')
                for i, (before, after) in enumerate(zip(previous, updated)):
                    if not isinstance(after, dict) or after.get('id') != before.get('id') or after.get('titre') != before.get('titre') or not isinstance(after.get('texte'), str):
                        return self.respond(422, f'Module {i} invalide'.encode())
                    if len(after['texte']) > 150_000:
                        return self.respond(422, b'Texte trop long')
                old_digest = hashlib.sha256(old_bytes).hexdigest()
                if incoming.get('_revision') != old_digest:
                    return self.respond(409, b'Fichier modifie depuis le chargement')
                for i, after in enumerate(updated):
                    previous[i]['texte'] = after['texte']
                # Atomic replacement and an adjacent, uniquely named backup.
                data = jsonify(old)
                backup = path.with_suffix(path.suffix + '.backup-' + secrets.token_hex(4))
                backup.write_bytes(old_bytes)
                staged = path.with_suffix('.tmp-' + secrets.token_hex(4))
                try:
                    staged.write_bytes(data)
                    os.replace(staged, path)
                finally:
                    staged.unlink(missing_ok=True)
                return self.json(200, {'resultat': 'enregistre', '_revision': hashlib.sha256(data).hexdigest(),
                                       'copie': backup.name})
            except (OSError, ValueError, TypeError, KeyError, json.JSONDecodeError) as exc:
                return self.respond(422, ('Modification invalide: ' + str(exc)).encode('utf-8'))

        def log_message(self, format, *args):
            sys.stderr.write(('[EDITEUR] ' if teacher else '[PUBLIC] ') + format % args + '\n')

    return Handler


def run():
    args = argparse.ArgumentParser(description='Ekole neutre — moteur partagé entre plusieurs dépôts de contenus')
    args.add_argument('--contenu', default='auto', help='Dossier de contenu, "auto" (frère), ou "none"')
    args.add_argument('--port', type=int, default=8765)
    args.add_argument('--port-editeur', type=int, default=8766)
    args.add_argument('--sans-editeur', action='store_true')
    args.add_argument('--edition', action='store_true', help='Active la modification locale des textes; sauvegardes adjacentes')
    args.add_argument('--ouvrir', action='store_true', help='Ouvrir les pages dans le navigateur')
    args.add_argument('--verifier', action='store_true', help='Valider le corpus, sans démarrer le serveur')
    args.add_argument('--tandem-preview', metavar='FICHIER', help='Aperçu enseignant local de missions synthétiques; aucune connexion Orgo')
    a = args.parse_args()
    if a.contenu.lower() == 'none':
        content = None
    elif a.contenu == 'auto':
        candidates = [(ENGINE.parent / name).resolve() for name in ('ekole-quebec', 'ecole-pastorale')]
        available = [p for p in candidates if p.is_dir()]
        if len(available) > 1:
            args.error('Plusieurs contenus disponibles : utilisez le lanceur du dépôt souhaité ou --contenu CHEMIN')
        content = available[0] if available else None
    else:
        content = pathlib.Path(a.contenu).expanduser().resolve()
        if not content.is_dir():
            args.error(f'Dépôt de contenu absent : {content}')
    try:
        projection = load_synthetic_preview(a.tandem_preview) if a.tandem_preview else None
        env = Environment(content, a.edition, a.port, tandem_preview=projection)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        args.error('Corpus / projection invalide : ' + str(exc))
    print(f'[EKOLE] Moteur    : {ENGINE}')
    print(f'[EKOLE] Contenu   : {content if content else "aucun (moteur autonome)"}')
    print(f'[EKOLE] Cours     : {len(env.by_id)} ; parcours : {len(env.pack["parcours"])}')
    print('[TANDEM]   : aperçu synthetique enseignant UNIQUEMENT (lecture seule, pas de reseau Orgo)' if projection else '[TANDEM]   : desactive par defaut')
    if a.verifier:
        print('[EKOLE] Validation du manifeste OK.')
        return
    if not (1 <= a.port <= 65535 and 1 <= a.port_editeur <= 65535 and a.port != a.port_editeur):
        args.error('Ports incorrects ou identiques')
    servers = []
    try:
        servers.append(http.server.ThreadingHTTPServer(('127.0.0.1', a.port), create_handler(env)))
        if not a.sans_editeur:
            servers.append(http.server.ThreadingHTTPServer(('127.0.0.1', a.port_editeur), create_handler(env, True)))
        for srv in servers:
            th = threading.Thread(target=srv.serve_forever, daemon=True)
            th.start()
        public_url = f'http://127.0.0.1:{a.port}/'
        print('[EKOLE] Accueil   : ' + public_url)
        print('[EKOLE] Apprenant: ' + public_url + 'eleve/')
        if len(servers) > 1:
            teacher_url = f'http://127.0.0.1:{a.port_editeur}/open?key={env.key}'
            print('[EKOLE] Éditeur  : ' + teacher_url)
            print('[EKOLE] Modifications : ' + ('ACTIVÉES avec sauvegarde' if env.edition else 'lecture seule (--edition pour activer)'))
        print('[EKOLE] Local seulement (127.0.0.1). Arrêt : Ctrl+C.', flush=True)
        if a.ouvrir:
            webbrowser.open(public_url)
            if len(servers) > 1:
                webbrowser.open(teacher_url)
        while True:
            time.sleep(0.2)
    except KeyboardInterrupt:
        print('\n[EKOLE] Arrêt demandé.')
    except OSError as exc:
        print('[EKOLE] Port indisponible : ' + str(exc), file=sys.stderr)
        sys.exit(1)
    finally:
        for srv in servers:
            srv.shutdown()
            srv.server_close()


if __name__ == '__main__':
    run()
