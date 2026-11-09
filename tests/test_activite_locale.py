"""Regression coverage for the new public/private assessment boundary."""
import http.server
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from threading import Thread
import unittest
from urllib.error import HTTPError
from urllib.request import Request, urlopen
import subprocess
import sys

from activite_locale import Activity
from launcher import Environment, create_handler


class LocalActivityTests(unittest.TestCase):
    def test_practice_bilan_and_release(self):
        repos = Path(__file__).resolve().parents[2]
        quebec = repos / 'ekole-quebec'
        with TemporaryDirectory() as folder:
            work = Path(folder)
            subprocess.run([sys.executable, str(quebec / 'outils/compiler_activite.py'),
                            '--out', folder], check=True, capture_output=True)
            env = Environment(quebec, False)
            with http.server.ThreadingHTTPServer(('127.0.0.1', 0), create_handler(env)) as server:
                thread = Thread(target=server.serve_forever)
                thread.start()
                try:
                    base = f'http://127.0.0.1:{server.server_port}'
                    with self.assertRaises(HTTPError) as rejected:
                        urlopen(base + '/api/activite-locale.json')
                    self.assertEqual(rejected.exception.code, 404)
                    env.activity = Activity(work / 'activite-privee.json', work / 'tests.sqlite',
                                            env.by_id, repos / 'Inkuisite')
                    self.exercise(base, env.activity)
                finally:
                    server.shutdown()
                    thread.join()

    def exercise(self, base, activity):
        def post(action, data, origin=base):
            request = Request(base + '/api/activite-locale/' + action, json.dumps(data).encode(),
                              {'Content-Type': 'application/json', 'Origin': origin})
            with urlopen(request, timeout=5) as response:
                return json.load(response)

        def submit(session, answers):
            exam = session['exam']
            attempt = {'format': 'inkui.attempt/1.0', 'exam_id': exam['exam_id'],
                       'exam_digest': exam['exam_digest'], 'answers': answers}
            return post('submit', {'attempt_id': session['attempt_id'], 'attempt': attempt})

        with urlopen(base + '/api/activite-locale.json?locale=en') as response:
            view = json.load(response)
        self.assertEqual(view['title'], 'Mila’s invitations')
        self.assertNotIn('exams', view)
        with self.assertRaises(HTTPError) as rejected:
            post('start', {'locale': 'fr-CA', 'mode': 'pratique'}, 'http://example.test')
        self.assertEqual(rejected.exception.code, 403)
        practice = post('start', {'locale': 'fr-CA', 'mode': 'pratique'})
        self.assertNotIn('scoring', practice['exam']['items'][0])
        answers = {'pratique-needed': '3', 'pratique-missing': '1'}
        result = submit(practice, answers)
        self.assertEqual(result['score'], 2)
        self.assertEqual(submit(practice, answers), result)
        with self.assertRaises(HTTPError) as rejected:
            submit(practice, {**answers, 'pratique-needed': '4'})
        self.assertEqual(rejected.exception.code, 422)

        bilan = post('start', {'locale': 'en', 'mode': 'bilan'})
        answers = {'bilan-needed': '5', 'bilan-missing': '2',
                   'bilan-explain': 'The last invitation also needs a sheet.'}
        outcome = submit(bilan, answers)
        self.assertEqual(outcome['status'], 'awaiting_release')
        self.assertNotIn('score', outcome)
        token = bilan['attempt_id']
        private = activity.store.inspect(token)
        self.assertEqual(private['result']['pending_count'], 1)
        self.assertIsNone(private['result']['score'])
        activity.store.review(token, {'format': 'inkui.reviews/1.0',
                                     'attempt_digest': private['result']['attempt_digest'],
                                     'items': {'bilan-explain': {
                                         'reviewer': 'Fixture technique', 'reason': 'Groupe incomplet identifié',
                                         'evidence': answers['bilan-explain'], 'feedback': 'Clear explanation',
                                         'next_step': 'Check with counters',
                                         'criteria_scores': {'incomplete-group': 1}}}})
        self.assertEqual(post('result', {'attempt_id': token})['status'], 'awaiting_release')
        activity.store.release(token, 'Fixture technique')
        outcome = post('result', {'attempt_id': token})
        self.assertEqual(outcome['score'], 3)
        self.assertNotIn('review', outcome['items'][-1])
        self.assertNotIn('source_refs', outcome['items'][-1])
