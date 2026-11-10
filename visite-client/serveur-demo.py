"""Servir Ekole sur deux ports locaux avec une base de démonstration temporaire."""
import json
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
from threading import Thread
from urllib.parse import urlsplit
from http.server import ThreadingHTTPServer


ALLOWED_POSTS = {
    '/api/lecons-locales/prepare', '/api/lecons-locales/review', '/api/lecons-locales/publish',
    '/api/activite-locale/start', '/api/activite-locale/submit', '/api/activite-locale/result',
    '/api/activites-locales/tentatives/inspect', '/api/activites-locales/tentatives/review',
    '/api/activites-locales/tentatives/release',
}


def demo_handler(handler):
    class DemoHandler(handler):
        def do_POST(self):
            if urlsplit(self.path).path not in ALLOWED_POSTS:
                return self.json(403, {'error': 'Action désactivée dans la visite de démonstration.'})
            return super().do_POST()

        def log_message(self, *_args):
            pass

    return DemoHandler


def require_files(folder, files, instruction):
    missing = [file for file in files if not (folder / file).is_file()]
    if missing:
        names = ', '.join(missing)
        raise SystemExit(f'[Ekole] Fichiers manquants dans {folder} ({names}). {instruction}')


def catalogue_for_visit(content, work, engine, inkui):
    index = content / 'dist/ecole-locale/catalogue.json'
    try:
        data = json.loads(index.read_bytes())
        if (data.get('lessons') and data.get('explorer')
                and any('/invitations-mila/' in row['bundle'] for row in data['entries'])):
            return index
    except (OSError, ValueError, KeyError, AttributeError, TypeError):
        pass

    require_files(content, ('outils/construire_ecole.py',),
                  'Applique les fichiers ekole-quebec du ZIP v6.')
    print(json.dumps({'status': 'Compilation du catalogue de démonstration. Cela peut prendre un moment.'}),
          flush=True)
    output = work / 'catalogue'
    env = {**os.environ, 'EKOLE_MOTEUR': str(engine), 'EKOLE_INKUISITE': str(inkui)}
    result = subprocess.run(
        [sys.executable, '-B', str(content / 'outils/construire_ecole.py'), '--out', str(output)],
        env=env, stdout=sys.stderr, check=False,
    )
    if result.returncode:
        raise SystemExit('[Ekole] Compilation interrompue. Vérifie les dépôts et leurs chemins.')
    index = output / 'catalogue.json'
    if not json.loads(index.read_bytes()).get('explorer'):
        raise SystemExit('[Ekole] Carte absente. Place Konstellation-Light à côté d’ekole-quebec '
                         'ou définis EKOLE_KONSTELLATION_LIGHT.')
    return index


def serve(engine, content):
    require_files(engine, ('launcher.py', 'activite_locale.py', 'lecons_locales.py'),
                  'Copie le contenu du dossier ekole du ZIP v6 à la racine du moteur, '
                  'ou définis EKOLE_MOTEUR si cette racine se trouve ailleurs.')
    require_files(content, ('pack.json',),
                  'Place le dépôt complet ekole-quebec à côté du moteur ou définis EKOLE_CONTENU.')
    inkui = Path(os.environ.get('EKOLE_INKUISITE', engine.parent / 'Inkuisite')).resolve()
    require_files(inkui, ('inkui/__init__.py',),
                  'Place Inkuisite à côté du moteur ou définis EKOLE_INKUISITE.')

    sys.path.insert(0, str(engine))
    from activite_locale import Catalogue
    from launcher import Environment, create_handler

    with TemporaryDirectory(prefix='ekole-visite-') as work:
        index = catalogue_for_visit(content, Path(work), engine, inkui)
        env = Environment(content, True)
        env.activity_catalogue = Catalogue(index, env.by_id, inkui,
                                          database=Path(work) / 'demo.sqlite3',
                                          content=content, pack=env.pack)
        if not env.activity_catalogue.editorial:
            raise SystemExit('Atelier des leçons absent du catalogue. Applique puis compile l’overlay v6.')
        with (ThreadingHTTPServer(('127.0.0.1', 0), demo_handler(create_handler(env))) as public,
              ThreadingHTTPServer(('127.0.0.1', 0), demo_handler(create_handler(env, True))) as teacher):
            env.port_public = public.server_port
            for server in (public, teacher):
                Thread(target=server.serve_forever, daemon=True).start()
            print(json.dumps({
                'public': f'http://127.0.0.1:{public.server_port}',
                'teacher': f'http://127.0.0.1:{teacher.server_port}',
                'open': f'http://127.0.0.1:{teacher.server_port}/open?key={env.key}',
            }), flush=True)
            try:
                sys.stdin.readline()
            finally:
                public.shutdown()
                teacher.shutdown()


if __name__ == '__main__':
    serve(Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve())
