"""Vérifier la frontière public/enseignant et les tentatives avec un catalogue Ekole v7."""
import http.cookiejar
from http.server import ThreadingHTTPServer
import json
import os
from pathlib import Path
from tempfile import TemporaryDirectory
from threading import Thread
import unittest
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import HTTPCookieProcessor, Request, build_opener, urlopen

from activite_locale import Catalogue
from launcher import Environment, create_handler


@unittest.skipUnless(os.environ.get('EKOLE_CATALOGUE_TEST'), 'Catalogue Ekole v7 requis')
class RolePathsTests(unittest.TestCase):
    def test_role_practice_and_reviewed_bank(self):
        folder = Path(__file__).resolve().parents[2]
        env = Environment(folder / 'ekole-quebec', True)
        with TemporaryDirectory() as work:
            env.activity_catalogue = Catalogue(Path(os.environ['EKOLE_CATALOGUE_TEST']), env.by_id,
                folder / 'Inkuisite', database=Path(work) / 'roles.sqlite3', content=env.content, pack=env.pack)
            with (ThreadingHTTPServer(('127.0.0.1', 0), create_handler(env)) as pupil,
                  ThreadingHTTPServer(('127.0.0.1', 0), create_handler(env, True)) as teacher):
                threads = [Thread(target=server.serve_forever) for server in (pupil, teacher)]
                for thread in threads:
                    thread.start()
                try:
                    self.exercise(env, pupil.server_port, teacher.server_port)
                finally:
                    pupil.shutdown()
                    teacher.shutdown()
                    for thread in threads:
                        thread.join()

    def exercise(self, env, pupil_port, teacher_port):
        pupil = f'http://127.0.0.1:{pupil_port}'
        teacher = f'http://127.0.0.1:{teacher_port}'
        browser = build_opener(HTTPCookieProcessor(http.cookiejar.CookieJar()))
        prefix = '/api/parcours-roles'
        catalogue = env.activity_catalogue
        cid = 'qc-pri-fr-021'

        def call(host, path, data=None, teacher=False):
            request = Request(host + path, None if data is None else json.dumps(data).encode(), {
                'Content-Type': 'application/json', 'Origin': host, 'X-Ekole-CSRF': env.csrf,
            })
            with (browser.open if teacher else urlopen)(request, timeout=5) as response:
                return json.load(response)

        with self.assertRaises(HTTPError) as denied:
            call(teacher, prefix + '.json')
        self.assertEqual(denied.exception.code, 401)
        with browser.open(teacher + '/open?' + urlencode({'key': env.key}), timeout=5):
            pass
        admin = call(teacher, prefix + '.json', teacher=True)['themes']
        self.assertEqual(len(admin), 10)
        self.assertEqual(sum(len(theme['roles']) for theme in admin), 38)
        self.assertEqual(sum(len(row['questions']) for theme in admin for row in theme['roles']), 76)
        self.assertEqual(call(pupil, prefix + '.json')['themes'], [])
        data = {'univers': 'jazz', 'role': 'photographe'}
        with self.assertRaises(HTTPError) as denied:
            call(pupil, prefix + '/pratique', data)
        self.assertEqual(denied.exception.code, 404)
        catalogue.univers.publish({'choices': ['jazz', 'jardinage'], 'default': 'jazz', 'style': 'pastel'})
        visible = call(pupil, prefix + '.json')
        self.assertEqual([theme['id'] for theme in visible['themes']], ['jazz', 'jardinage'])
        self.assertNotIn('questions', json.dumps(visible))
        photo = call(pupil, prefix + '/jazz/photographe.json')
        music = call(pupil, prefix + '/jazz/musicien.json')
        self.assertEqual(photo['course'], cid)
        self.assertEqual(music['course'], 'qc-pri-mu-002')
        self.assertNotEqual(photo['scene'], music['scene'])
        self.assertNotIn('answer', photo)
        practice = call(pupil, prefix + '/pratique', data)
        exam = practice['exam']
        self.assertNotIn('scoring', exam['items'][0])

        def submit(attempt, answer):
            exam = attempt['exam']
            return call(pupil, '/api/activite-locale/submit', {
                'attempt_id': attempt['attempt_id'], 'attempt': {
                    'format': 'inkui.attempt/1.0', 'exam_id': exam['exam_id'],
                    'exam_digest': exam['exam_digest'], 'answers': {exam['items'][0]['id']: answer}}})

        self.assertEqual(submit(practice, 'b')['score'], 1)
        with self.assertRaises(HTTPError) as denied:
            call(pupil, prefix + '/banque', data)
        self.assertEqual(denied.exception.code, 422)
        version = catalogue.banks.refs[cid]['source']
        template = {'cours': cid, 'source': version, 'revision': None, 'reviewer': 'Essai local',
            'reason': 'Tester la sélection', 'confirmed': True, 'prompt': 'Écris la légende du reportage.',
            'criterion': 'L’idée principale correspond à la scène.', 'feedback': 'Vérifie ta première phrase.'}
        catalogue.banks.change({**template, 'item': cid + '-q-002'})
        with self.assertRaises(HTTPError) as denied:
            call(pupil, prefix + '/banque', data)
        self.assertEqual(denied.exception.code, 422)
        linked = cid + '-q-001'
        receipt = catalogue.banks.change({**template, 'item': linked})
        attempt = call(pupil, prefix + '/banque', data)
        self.assertEqual([item['id'] for item in attempt['exam']['items']], [linked])
        catalogue.banks.change({**template, 'item': linked, 'revision': receipt['revision']}, withdraw=True)
        with self.assertRaises(HTTPError) as denied:
            call(pupil, prefix + '/banque', data)
        self.assertEqual(denied.exception.code, 422)
        self.assertEqual(submit(attempt, 'Les musiciens préparent le concert.')['status'], 'awaiting_release')
        token = {'attempt_id': attempt['attempt_id']}
        review_api = '/api/activites-locales/tentatives/'
        detail = call(teacher, review_api + 'inspect', token, teacher=True)
        self.assertEqual(detail['items'][0]['id'], linked)
        result = detail['result']
        reviewed = call(teacher, review_api + 'review', {**token, 'result_digest': result['result_digest'],
            'reviews': {'format': 'inkui.reviews/1.0', 'attempt_digest': result['attempt_digest'],
                        'items': {linked: {'reviewer': 'Essai local', 'reason': 'L’idée centrale est claire.',
                            'evidence': 'Les musiciens préparent le concert.',
                            'feedback': 'Ta phrase annonce bien la préparation.',
                            'next_step': 'Ajoute un détail de la répétition.',
                            'criteria_scores': {'reviewed-criterion': '1'}}}}}, teacher=True)
        call(teacher, review_api + 'release', {**token, 'reviewer': 'Essai local',
            'result_digest': reviewed['result']['result_digest']}, teacher=True)
        result = call(pupil, '/api/activite-locale/result', token)
        self.assertEqual(result['items'][0]['feedback'], 'Ta phrase annonce bien la préparation.')
