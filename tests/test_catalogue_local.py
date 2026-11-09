"""Integration check for the cumulative overlay (set EKOLE_CATALOGUE_TEST to its build)."""
import base64
import http.cookiejar
import http.server
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


@unittest.skipUnless(os.environ.get('EKOLE_CATALOGUE_TEST'), 'Catalogue cumulatif non fourni')
class CatalogueTests(unittest.TestCase):
    def test_catalogue_projections_and_teacher_release(self):
        repos = Path(__file__).resolve().parents[2]
        env = Environment(repos / 'ekole-quebec', True)
        index = Path(os.environ['EKOLE_CATALOGUE_TEST']).resolve()
        with TemporaryDirectory() as work:
            # Use the real verified build, with a separate database for these fictitious submissions.
            catalogue = Catalogue(index, env.by_id, repos / 'Inkuisite',
                                  database=Path(work) / 'tests.sqlite3', content=env.content, pack=env.pack)
            env.activity_catalogue = catalogue
            with http.server.ThreadingHTTPServer(('127.0.0.1', 0), create_handler(env)) as pupil, \
                 http.server.ThreadingHTTPServer(('127.0.0.1', 0), create_handler(env, True)) as teacher:
                threads = [Thread(target=server.serve_forever) for server in (pupil, teacher)]
                for thread in threads:
                    thread.start()
                try:
                    self.exercise(f'http://127.0.0.1:{pupil.server_port}',
                                  f'http://127.0.0.1:{teacher.server_port}', env)
                finally:
                    pupil.shutdown()
                    teacher.shutdown()
                    for thread in threads:
                        thread.join()

    def exercise(self, pupil, teacher, env):
        browser = build_opener(HTTPCookieProcessor(http.cookiejar.CookieJar()))
        attempts = '/api/activites-locales/tentatives'
        def get_json(host, path, opener=urlopen):
            with opener(host + path, timeout=5) as response:
                return json.load(response)

        def post(host, path, data, opener=urlopen, csrf=None):
            headers = {'Content-Type': 'application/json', 'Origin': host}
            if csrf:
                headers['X-Ekole-CSRF'] = csrf
            with opener(Request(host + path, json.dumps(data).encode(), headers), timeout=5) as response:
                return json.load(response)

        with self.assertRaises(HTTPError) as error:
            get_json(teacher, attempts + '.json')
        self.assertEqual(error.exception.code, 401)
        with browser.open(teacher + '/open?' + urlencode({'key': env.key}), timeout=5):
            pass
        self.assertEqual(len(get_json(teacher, '/api/activites-locales/scenarios.json', browser.open)), 60)
        self.assertEqual(len(get_json(pupil, '/api/portail-spek.json')), 20)
        self.exercise_lessons(pupil, teacher, env, get_json, post, browser)
        if env.activity_catalogue.univers:
            self.exercise_univers(pupil, teacher, env, get_json, post, browser)
        pack = get_json(pupil, '/api/pack.json')
        self.assertEqual(sum(bool(c.get('fiche_decouverte')) for c in pack['cours']), 202)
        fiche = get_json(pupil, '/notions-spek/qc-pri-ad-001/fr/document.json')
        self.assertIn('corps', fiche['title'])
        self.assertNotIn('preuve_attendue', json.dumps(fiche))
        banks = get_json(teacher, '/api/banques-locales.json', browser.open)
        self.assertEqual((len(banks), sum(row['items'] for row in banks)), (202, 2183))
        self.assertEqual(get_json(pupil, '/api/banques-locales/disponibles.json'), [])
        cid = 'qc-pri-ma-009'
        route = f'/api/banques-locales/{cid}.json'
        with self.assertRaises(HTTPError) as error:
            get_json(pupil, route)
        self.assertEqual(error.exception.code, 404)
        bank = get_json(teacher, route, browser.open)
        first = bank['items'][0]
        self.assertIn('original', first)
        base = {'cours': cid, 'item': first['id'], 'source': bank['source'], 'revision': first['revision'],
                'reviewer': 'Fixture locale', 'reason': 'Essai de la chaîne de revue'}
        approval = {**base, 'prompt': 'Question fictive à corriger par une personne.',
                    'stimulus': 'Support fictif.', 'criterion': 'La démarche est expliquée.',
                    'feedback': 'Expliquer une étape.', 'confirmed': True}
        with self.assertRaises(HTTPError) as error:
            post(pupil, '/api/banques-locales/review', approval)
        self.assertEqual(error.exception.code, 401)
        with self.assertRaises(HTTPError) as error:
            post(teacher, '/api/banques-locales/review', {**approval, 'source': 'stale'},
                 browser.open, env.csrf)
        self.assertEqual(error.exception.code, 422)
        reviewed = post(teacher, '/api/banques-locales/review', approval, browser.open, env.csrf)
        self.assertEqual(get_json(pupil, '/api/banques-locales/disponibles.json'), [cid])
        with self.assertRaises(HTTPError) as error:
            post(teacher, '/api/banques-locales/review', approval, browser.open, env.csrf)
        self.assertEqual(error.exception.code, 422)
        start = post(pupil, '/api/banques-locales/start', {'cours': cid})
        item = start['exam']['items'][0]
        self.assertEqual(item['kind'], 'rubric')
        self.assertNotIn('upstream_item', item)
        self.assertNotIn('scoring', item)
        post(teacher, '/api/banques-locales/withdraw', {**base, 'revision': reviewed['revision']},
             browser.open, env.csrf)
        self.assertEqual(get_json(pupil, '/api/banques-locales/disponibles.json'), [])
        with self.assertRaises(HTTPError) as error:
            post(pupil, '/api/banques-locales/start', {'cours': cid})
        self.assertEqual(error.exception.code, 422)
        exam = start['exam']
        submitted = post(pupil, '/api/activite-locale/submit', {
            'attempt_id': start['attempt_id'], 'attempt': {'format': 'inkui.attempt/1.0',
                'exam_id': exam['exam_id'], 'exam_digest': exam['exam_digest'],
                'answers': {item['id']: 'Réponse fictive conservée dans la tentative épinglée.'}}})
        self.assertEqual(submitted['status'], 'awaiting_release')
        coverage = get_json(teacher, '/api/activites-locales/couverture.json', browser.open)
        self.assertEqual(len(coverage), 202)
        self.assertEqual(sum(len(item['activites']) for item in coverage), 12)
        if env.activity_catalogue.univers:
            self.assertEqual(sum(len(item['variantes']) for item in coverage), 12)
        self.assertEqual(sum(len(item['micro_mondes']) for item in coverage), 7)
        with self.assertRaises(HTTPError) as error:
            get_json(pupil, '/api/activites-locales/couverture.json')
        self.assertEqual(error.exception.code, 404)

        if env.activity_catalogue.worlds.node:
            public = get_json(pupil, '/eleve/mondes-v12/data/catalogue.json')
            self.assertEqual(len(public['items']), 7)
            for world in public['items']:
                parameters = world['parameters']
                self.assertNotIn('chosen', parameters)
                self.assertNotIn('order', parameters)
                self.assertTrue(all('valid' not in link for link in parameters.get('links', [])))
                self.assertTrue(all('kind' not in row for row in parameters.get('statements', [])))
                if world['type'] == 'representations':
                    state = {'surface': [], 'bande': [], 'collection': []}
                elif world['type'] == 'repartition':
                    state = {'bins': [-1] * parameters['total']}
                elif world['type'] == 'causalite':
                    state = {'order': [event['id'] for event in parameters['events']], 'links': {}}
                elif world['type'] == 'preuves':
                    state = {'classifications': {}}
                else:
                    state = {'selected': []}
                result = post(pupil, '/api/micro-mondes/verifier', {'id': world['id'], 'state': state})
                self.assertFalse(result['proof_of_mastery'])
            with self.assertRaises(HTTPError) as error:
                post(pupil, '/api/micro-mondes/verifier',
                     {'id': 'recit-liens-causaux', 'state': {'order': [], 'links': {}}})
            self.assertEqual(error.exception.code, 422)
        self.assertIn('Bienvenue', get_json(pupil, '/portail-spek/accueil/fr/document.json')['title'])
        if env.activity_catalogue.explorer:
            collection = get_json(pupil, '/eleve/konstellation/data/catalog.json')
            row = collection['entries'][0]
            graph = get_json(pupil, '/eleve/konstellation/' + row['path'])
            self.assertEqual((len(graph['nodes']), len(graph['edges'])), (202, 85))
        old = get_json(pupil, '/api/integrations/activites.json')
        self.assertTrue(all('reponse' not in item and 'retroaction' not in item for item in old['activites']))
        self.assertTrue(post(pupil, '/api/integrations/activites/verifier',
                             {'cours': 'qc-pri-fr-006', 'choix': 0})['correct'])

        for aid, kind, answer in [('recit-du-spectacle', 'single_choice', 'a'),
                                  ('semis-a-comparer', 'multiple_choice', ['b', 'a'])]:
            query = '?id=' + aid
            created = post(pupil, '/api/activite-locale/start' + query,
                           {'locale': 'fr-CA', 'mode': 'pratique'})
            exam = created['exam']
            self.assertEqual(exam['items'][0]['kind'], kind)
            self.assertNotIn('scoring', exam['items'][0])
            score = post(pupil, '/api/activite-locale/submit' + query, {
                'attempt_id': created['attempt_id'], 'attempt': {'format': 'inkui.attempt/1.0',
                    'exam_id': exam['exam_id'], 'exam_digest': exam['exam_digest'],
                    'answers': {'pratique-choisir': answer}}})
            self.assertEqual(score['score'], 1)

        created = post(pupil, '/api/activite-locale/start?id=gouter-partage',
                       {'locale': 'en', 'mode': 'bilan'})
        attempt_id = created['attempt_id']
        exam = created['exam']
        answer = {'bilan-needed': '5', 'bilan-missing': '3', 'bilan-explain': 'A partial group needs a plate.'}
        result = post(pupil, '/api/activite-locale/submit?id=gouter-partage', {
            'attempt_id': attempt_id, 'attempt': {'format': 'inkui.attempt/1.0',
                'exam_id': exam['exam_id'], 'exam_digest': exam['exam_digest'], 'answers': answer}})
        self.assertEqual(result['status'], 'awaiting_release')
        token = {'attempt_id': attempt_id}

        def teacher_action(action, data):
            return post(teacher, attempts + '/' + action, {**token, **data}, browser.open, env.csrf)

        with self.assertRaises(HTTPError) as error:
            post(teacher, attempts + '/inspect', token, browser.open)
        self.assertEqual(error.exception.code, 403)
        private = teacher_action('inspect', {})['result']
        release = {'reviewer': 'Fixture locale', 'result_digest': private['result_digest']}
        with self.assertRaises(HTTPError) as error:
            teacher_action('release', release)
        self.assertEqual(error.exception.code, 422)
        reviewed = teacher_action('review', {'result_digest': private['result_digest'], 'reviews': {
            'format': 'inkui.reviews/1.0', 'attempt_digest': private['attempt_digest'],
            'items': {'bilan-explain': {'reviewer': 'Fixture locale', 'reason': 'Criterion met',
                'evidence': answer['bilan-explain'], 'feedback': 'Good explanation',
                'next_step': 'Check another group', 'criteria_scores': {'incomplete-group': '1'}}}}})
        with self.assertRaises(HTTPError) as error:
            teacher_action('release', release)
        self.assertEqual(error.exception.code, 422)
        self.assertTrue(teacher_action('release', {**release,
            'result_digest': reviewed['result']['result_digest']})['released'])
        result = post(pupil, '/api/activite-locale/result?id=gouter-partage', token)
        self.assertEqual(result['score'], 3)

    def exercise_univers(self, pupil, teacher, env, get_json, post, browser):
        prefix = '/api/univers'
        profile = {'choices': ['jardinage', 'jazz'], 'default': 'jardinage', 'style': 'pastel'}
        activity = '/api/activite-locale.json?id=division-jardinage'
        fiche = '/univers-spek/jardinage/qc-pri-st-001/fr/'
        with self.assertRaises(HTTPError) as refused:
            get_json(pupil, activity)
        self.assertEqual(refused.exception.code, 404)
        with self.assertRaises(HTTPError) as refused:
            post(pupil, prefix + '/publier', profile, csrf=env.csrf)
        self.assertEqual(refused.exception.code, 401)
        self.assertEqual(post(teacher, prefix + '/publier', profile, browser.open, env.csrf), profile)
        listing = get_json(pupil, prefix + '.json')
        self.assertEqual([row['id'] for row in listing['themes']], profile['choices'])
        self.assertEqual(listing['style'], 'pastel')
        self.assertEqual(len(get_json(teacher, prefix + '.json', browser.open)['themes']), 10)
        self.assertIn('jardin', get_json(pupil, activity)['title'])
        self.assertIn('5 cm', get_json(pupil, '/api/activite-locale.json?id=semis-a-comparer-jardinage')['context'])
        self.assertIn('programme', get_json(pupil, '/api/activite-locale.json?id=recit-du-spectacle-jazz')['context'])
        self.assertIn('Les jardins du village', get_json(pupil, fiche + 'document.json')['subtitle'])
        png = 'iVBORw0KGgoAAAANSUhEUgAAAHgAAAB4CAAAAAAcD2kOAAAAJUlEQVR4nO3BMQEAAADCoPVPbQlPoAAAAAAAAAAAAAAAAAAAPgY4uAABCbhRfwAAAABJRU5ErkJggg=='
        image = {'theme': 'jardinage', 'style': 'pastel', 'alt': 'Image fictive', 'image': png}
        with self.assertRaises(HTTPError) as refused:
            post(pupil, prefix + '/image', image, csrf=env.csrf)
        self.assertEqual(refused.exception.code, 401)
        post(teacher, prefix + '/image', image, browser.open, env.csrf)
        with urlopen(pupil + prefix + '/image/jardinage/pastel', timeout=5) as response:
            self.assertEqual(response.read(), base64.b64decode(png))
        with urlopen(pupil + fiche + 'index.html', timeout=5) as response:
            self.assertIn(b'--accent:#694782', response.read())
        post(teacher, prefix + '/publier', {'choices': [], 'default': '', 'style': 'ekole'},
             browser.open, env.csrf)
        with self.assertRaises(HTTPError) as refused:
            get_json(pupil, fiche + 'document.json')
        self.assertEqual(refused.exception.code, 404)

    def exercise_lessons(self, pupil, teacher, env, get_json, post, browser):
        prefix = '/api/lecons-locales'
        index = get_json(teacher, prefix + '.json', browser.open)
        self.assertEqual(len(index), 6)
        self.assertEqual(sum(len(path['courses']) for path in index), 202)
        self.assertEqual(sum(item['seeded'] for path in index for item in path['courses']), 202)
        for path in index:
            self.assertTrue(any(item['seeded'] for item in path['courses']))
            body = {'parcours': path['id']}
            first = post(teacher, prefix + '/prepare', body, browser.open, env.csrf)
            self.assertEqual(first['created'], len(path['courses']))
            again = post(teacher, prefix + '/prepare', body, browser.open, env.csrf)
            self.assertEqual(again['created'], 0)
            self.assertEqual(again['completed'], 0)

        editorial = env.activity_catalogue.editorial
        path = index[0]
        untouched_id, edited_id = (item['id'] for item in path['courses'][:2])
        with editorial.store.connect() as db:
            for cid in (untouched_id, edited_id):
                draft = editorial.b2.source_scaffold(editorial.source(cid), cid)
                if cid == edited_id:
                    draft['modules'][0]['titre'] = 'Titre rédigé localement'
                db.execute('UPDATE ekole_lessons SET draft=? WHERE course=?',
                           (json.dumps(draft), cid))
        migrated = post(teacher, prefix + '/prepare', {'parcours': path['id']}, browser.open, env.csrf)
        self.assertEqual(migrated['created'], 0)
        self.assertEqual(migrated['completed'], 1)
        self.assertNotEqual(editorial.detail(untouched_id)['draft']['modules'][0]['titre'],
                            'À rédiger pour l’enfant')
        self.assertEqual(editorial.detail(edited_id)['draft']['modules'][0]['titre'],
                         'Titre rédigé localement')

        def lesson(cid):
            return get_json(teacher, prefix + '/' + cid + '.json', browser.open)

        def act(name, data):
            return post(teacher, prefix + '/' + name, data, browser.open, env.csrf)

        first_id, second_id = 'qc-pri-ma-009', 'qc-pri-ap-003'
        first, second = lesson(first_id), lesson(second_id)
        with self.assertRaises(HTTPError) as refused:
            get_json(pupil, prefix + '/' + first_id + '.json')
        self.assertEqual(refused.exception.code, 404)
        preview_route = prefix + '/preview/' + first_id + '.json'
        with self.assertRaises(HTTPError) as refused:
            get_json(pupil, preview_route)
        self.assertEqual(refused.exception.code, 404)
        preview = get_json(teacher, preview_route, browser.open)
        self.assertEqual(preview['revision'], first['revision'])
        self.assertEqual(len(preview['lesson']['modules']), 6)
        self.assertNotIn('teacher_brief', preview['lesson'])
        self.assertFalse(lesson(first_id)['reviewed'])
        self.assertEqual(get_json(pupil, '/api/cours/' + first_id + '.json')['modules'], [])
        for cid, version in ((first_id, first), (second_id, second)):
            act('review', {'course': cid, 'revision': version['revision'],
                           'reviewer': 'Fixture de test', 'confirmed': True})
        revised = act('save', {'course': second_id, 'revision': second['revision'],
                               'modules': second['draft']['modules']})
        with self.assertRaises(HTTPError) as refused:
            act('publish', {'confirmed': True,
                            'courses': {first_id: first['revision'], second_id: second['revision']}})
        self.assertEqual(refused.exception.code, 422)
        self.assertEqual(get_json(pupil, '/api/cours/' + first_id + '.json')['modules'], [])
        act('review', {'course': second_id, 'revision': revised['revision'],
                       'reviewer': 'Fixture de test', 'confirmed': True})
        act('publish', {'confirmed': True,
                        'courses': {first_id: first['revision'], second_id: revised['revision']}})
        result = get_json(pupil, '/api/cours/' + first_id + '.json')
        self.assertEqual(result['modules'], preview['lesson']['modules'])
        self.assertNotIn('teacher_brief', result)
        self.assertNotIn('source_provenance', result)
        self.assertEqual(result, env.activity_catalogue.editorial.export([first_id])[first_id][0])
        act('withdraw', {'course': first_id, 'revision': first['revision'], 'confirmed': True})
        self.assertEqual(get_json(pupil, '/api/cours/' + first_id + '.json')['modules'], [])
