"""La publication Kolor doit filtrer l’export et respecter la session enseignant."""
from hashlib import sha256
from http.cookiejar import CookieJar
from http.server import ThreadingHTTPServer
import json
import os
from pathlib import Path
from tempfile import TemporaryDirectory
from threading import Thread
import unittest
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import HTTPCookieProcessor, Request, build_opener, urlopen

from activite_locale import Catalogue
from launcher import Environment, create_handler

try:
    from PIL import Image
except ImportError:
    Image = None


@unittest.skipUnless(os.environ.get('EKOLE_CATALOGUE_TEST') and Image, 'Catalogue compilé et Pillow requis')
class KolorRoleTests(unittest.TestCase):
    def test_review_publish_and_withdraw(self):
        repos = Path(__file__).resolve().parents[2]
        env = Environment(repos / 'ekole-quebec', True)
        with TemporaryDirectory() as work, patch.dict(os.environ, {'EKOLE_KOLOR_EXPORTS': work}):
            root = Path(work)
            env.activity_catalogue = Catalogue(Path(os.environ['EKOLE_CATALOGUE_TEST']), env.by_id,
                repos / 'Inkuisite', database=root / 'isolated.sqlite3', content=env.content, pack=env.pack)
            folder = root / 'images/roles'
            folder.mkdir(parents=True)
            roles = {'fermier': 'pret', 'photographe': 'a_verifier', 'extraterrestre': 'pret'}
            rows = []
            hashes = {}
            for role, state in roles.items():
                path = folder / (role + '.png')
                Image.new('RGB', (512, 512), 'blue').save(path)
                hashes[role] = sha256(path.read_bytes()).hexdigest()
                rows.append({'visual_id': 'role-' + role, 'statut': state, 'chemin': path.relative_to(root).as_posix()})
            (root / 'manifest.json').write_text(json.dumps({'format': 'kolor.studio.export/1', 'roles': rows}), encoding='utf-8')
            with (ThreadingHTTPServer(('127.0.0.1', 0), create_handler(env)) as pupil,
                  ThreadingHTTPServer(('127.0.0.1', 0), create_handler(env, True)) as teacher):
                threads = [Thread(target=server.serve_forever) for server in (pupil, teacher)]
                for thread in threads:
                    thread.start()
                try:
                    self.exercise(env, pupil.server_port, teacher.server_port, hashes, folder)
                finally:
                    pupil.shutdown()
                    teacher.shutdown()
                    for thread in threads:
                        thread.join()

    def exercise(self, env, pupil_port, teacher_port, hashes, folder):
        pupil = f'http://127.0.0.1:{pupil_port}'
        teacher = f'http://127.0.0.1:{teacher_port}'
        browser = build_opener(HTTPCookieProcessor(CookieJar()))

        def call(host, path, data=None, key=None, admin=False):
            headers = {'Content-Type': 'application/json', 'Origin': host}
            if key:
                headers['X-Ekole-CSRF'] = key
            request = Request(host + path, None if data is None else json.dumps(data).encode(), headers)
            with (browser.open if admin else urlopen)(request, timeout=5) as response:
                return response.read()

        def expect_error(code, *args, **kwargs):
            with self.assertRaises(HTTPError) as result:
                call(*args, **kwargs)
            self.assertEqual(result.exception.code, code)
            result.exception.close()

        base = '/api/kolor'
        img = '/api/personnages/image/role-fermier'
        candidate = base + '/candidat/role-fermier/' + hashes['fermier']
        selection = {'portraits': {'role-fermier': hashes['fermier']}}
        expect_error(404, pupil, base + '/portraits.json')
        expect_error(404, pupil, candidate)
        expect_error(404, pupil, img)
        expect_error(401, pupil, base + '/publier', selection, key=env.csrf)
        with browser.open(teacher + '/open?' + urlencode({'key': env.key}), timeout=5):
            pass
        listing = json.loads(call(teacher, base + '/portraits.json', admin=True))
        rows = {row['id']: row for row in listing['roles']}
        self.assertEqual(rows['role-photographe']['state'], 'a_verifier')
        self.assertNotIn('candidate', rows['role-photographe'])
        self.assertEqual(sha256(call(teacher, candidate, admin=True)).hexdigest(), hashes['fermier'])
        expect_error(403, teacher, base + '/publier', selection, admin=True)
        Image.new('RGB', (512, 512), 'red').save(folder / 'extraterrestre.png')
        expect_error(422, teacher, base + '/publier', {
            'portraits': {**selection['portraits'], 'role-extraterrestre': hashes['extraterrestre']}},
            key=env.csrf, admin=True)
        expect_error(404, pupil, img)
        result = json.loads(call(teacher, base + '/publier', selection, key=env.csrf, admin=True))
        self.assertEqual(result['published'], 1)
        self.assertEqual(sha256(call(pupil, img)).hexdigest(), hashes['fermier'])
        inventory = json.loads(call(pupil, '/api/personnages/catalogue.json'))
        entry = next(row for row in inventory['assets'] if row['id'] == 'role-fermier')
        self.assertTrue(entry['disponible'])
        self.assertNotIn('sha256', entry)
        (folder / 'fermier.png').unlink()
        self.assertEqual(sha256(call(pupil, img)).hexdigest(), hashes['fermier'])
        call(teacher, base + '/retirer', {'role': 'role-fermier', 'sha256': hashes['fermier']},
             key=env.csrf, admin=True)
        expect_error(404, pupil, img)
