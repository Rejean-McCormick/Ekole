"""Explicitly enabled local exercise backed by the sibling Inkuisite engine."""
import hashlib
import importlib
import json
import re
import sys
from personnages import safe_file
from mondes_v12 import MicroWorlds
from lecons_locales import Editorial
from univers import Univers

ID = re.compile(r'[a-z][a-z0-9-]{1,79}')
TOKEN = re.compile(r'[A-Za-z0-9_-]{43}')
MODES = {'pratique': 'immediate', 'bilan': 'on_release'}
LOCALES = ('fr-CA', 'en')


class Activity:
    def __init__(self, path, db_path, courses, inkui_root, verify_only=False):
        if not (inkui_root / 'inkui' / 'exams.py').is_file():
            raise ValueError('Dépôt frère Inkuisite introuvable')
        sys.path.insert(0, str(inkui_root))
        try:
            common = importlib.import_module('inkui.common')
            exams = importlib.import_module('inkui.exams')
            storage = importlib.import_module('inkui.storage')
        finally:
            sys.path.pop(0)
        bundle = common.read_json(path)
        if bundle.get('format') != 'ekole.local-activity-bundle/1' or bundle.get('course') not in courses:
            raise ValueError('Projection locale incompatible avec le corpus')
        self.id = bundle['id']
        if not ID.fullmatch(self.id):
            raise ValueError('Identifiant d’activité invalide')
        self.course = bundle['course']
        self.scenario = bundle.get('scenario')
        self.views = bundle['views']
        self.exams = bundle['exams']
        self.loads = common.loads
        self.student_exam = exams.student_exam
        if set(self.views) != set(LOCALES) or set(self.exams) != set(LOCALES):
            raise ValueError('Langues de la projection locale invalides')
        for locale in LOCALES:
            self.view(locale)
            if set(self.exams[locale]) != set(MODES):
                raise ValueError('Modes de la projection locale invalides')
            for mode, policy in MODES.items():
                exam = exams.verify_exam(self.exams[locale][mode])
                if (exam['blueprint']['scope'] != 'demo' or exam['blueprint']['feedback_policy'] != policy
                        or any(item['course_ref'] != self.course for item in exam['items'])):
                    raise ValueError('Seuls les examens de démonstration de ce cours sont admis')
        self.store = None if verify_only else storage.Store(db_path)

    def view(self, locale):
        view = self.views[locale]
        # Explicit projection. A private exam and its grading rules are never returned here.
        projected = {key: view[key] for key in (
            'id', 'locale', 'revision', 'title', 'subtitle', 'heading', 'objective', 'prerequisite',
            'context', 'group', 'compare', 'reflection', 'limits')}
        if 'character' in view:
            projected['character'] = view['character']
        projected['cases'] = {mode: view['cases'][mode] for mode in MODES}
        projected['labels'] = {key: view['labels'][key] for key in (
            'pratique', 'bilan', 'submit', 'refresh', 'restart', 'pending', 'score', 'review')}
        # Use the same student allowlist as starting an exam, including for older bundles.
        projected['prompts'] = {item['id']: item['prompt']
                                for exam in self.exams[locale].values()
                                for item in self.student_exam(exam)['items']}
        if 'practice' in view:
            projected['practice'] = {key: view['practice'][key] for key in ('invitations', 'per_sheet')}
            projected['labels'].update({key: view['labels'][key] for key in (
                'add_sheet', 'undo_sheet', 'placement')})
        return projected

    def perform(self, action, data):
        if not isinstance(data, dict):
            raise ValueError('Objet JSON attendu')
        if action == 'start':
            if set(data) != {'locale', 'mode'} or data['locale'] not in LOCALES or data['mode'] not in MODES:
                raise ValueError('Langue ou mode inconnu')
            return self.store.create(self.exams[data['locale']][data['mode']])
        token = data.get('attempt_id')
        if not isinstance(token, str) or not TOKEN.fullmatch(token):
            raise ValueError('Identifiant de tentative invalide')
        if action == 'result' and set(data) == {'attempt_id'}:
            return self.store.public_result(token)
        if action == 'submit' and set(data) == {'attempt_id', 'attempt'}:
            return self.store.submit(token, data['attempt'])
        raise ValueError('Données de tentative invalides')


class Catalogue:
    def __init__(self, index, courses, inkui_root, verify_only=False, *, database=None, content=None, pack=None):
        root = index.parent
        data = json.loads(index.read_bytes())
        if data.get('format') != 'ekole.local-activity-catalogue/1' or not data.get('entries'):
            raise ValueError('Catalogue d’activités locales invalide')
        self.activities = {}
        self.pages = {}
        self.activity_themes = {}
        variants = {}
        self.scenarios = [{key: row[key] for key in ('id', 'titre', 'famille', 'resultat')}
                          for row in data['scenarios']]
        db_path = database or safe_file(root, 'tentatives.sqlite3')
        for entry in data['entries']:
            item = Activity(safe_file(root, entry['bundle']), db_path, courses, inkui_root, verify_only)
            if item.id in self.activities or set(entry['pages']) != {'fr', 'en'}:
                raise ValueError('Activité dupliquée ou pages manquantes')
            self.activities[item.id] = item
            self.pages[item.id] = entry['pages']
            if theme := entry.get('theme'):
                self.activity_themes[item.id] = theme
                by_course = variants.setdefault(theme, {})
                if item.course in by_course:
                    raise ValueError('Variante thématique dupliquée')
                by_course[item.course] = {'id': item.id, 'titre': item.views['fr-CA']['title'], 'spek': True}
        self.portal = {}
        for entry in data.get('portal', []):
            if not ID.fullmatch(entry['id']) or entry['id'] in self.portal or set(entry['pages']) != {'fr'}:
                raise ValueError('Page du portail dupliquée ou invalide')
            self.portal[entry['id']] = {'title': entry['title'], 'pages': entry['pages']}
        self.root = root
        self.editorial = None
        if data.get('lessons') and content is not None and pack is not None:
            seeds = json.loads(self.resource(data['lessons'], ('lecons-candidates.json',)))
            self.editorial = Editorial(content, seeds, pack, next(iter(self.activities.values())).store)

        self.univers = None
        if data.get('univers'):
            themes = json.loads(self.resource(data['univers'], ('univers.json',)))
            self.univers = Univers(self, themes, variants, data.get('univers_pages', {}), courses,
                                    next(iter(self.activities.values())).store)
        elif variants:
            raise ValueError('Variantes sans catalogue des univers')

        self.notions = data.get('notions', {})
        if self.notions and set(self.notions) != set(courses):
            raise ValueError('Les fiches de découverte ne couvrent pas le pack')
        self.banks = None
        if data.get('banks'):
            bank_module = importlib.import_module('banques_locales')
            self.banks = bank_module.Banks(self, data['banks'], next(iter(self.activities.values())).store, courses)
        self.worlds = None
        if data.get('worlds'):
            raw = self.resource(data['worlds'], ('micro-mondes-prives.json',))
            self.worlds = MicroWorlds(json.loads(raw)['items'], courses)
        self.explorer = data.get('explorer', {})
        for name in self.explorer:
            self.explorer_file(name)
        for pages in [*self.pages.values(), *self.notions.values(), *(entry['pages'] for entry in self.portal.values())]:
            for lang, files in pages.items():
                if set(files) != {'index.html', 'document.json'}:
                    raise ValueError('Sortie Spek incomplète')
                for name, ref in files.items():
                    self.resource(ref, (lang, name))

    def resource(self, ref, suffix):
        path = safe_file(self.root, ref['path'])
        if path.parts[-len(suffix):] != suffix or path.stat().st_size > 2_000_000:
            raise ValueError('Fichier Spek invalide')
        content = path.read_bytes()
        if ref['sha256'] != 'sha256:' + hashlib.sha256(content).hexdigest():
            raise ValueError('Fichier Spek modifié depuis le build')
        return content

    def explorer_file(self, name):
        if name not in {
            'index.html', 'app.js', 'style.css', 'sw.js', 'graph-core.mjs', 'profile.mjs',
            'semantic-display.mjs', 'assets/uckk-logo.svg', 'data/catalog.json'
        } and not re.fullmatch(r'data/pack-[0-9a-f]{64}\.json', name):
            raise ValueError('Fichier Konstellation non autorisé')
        return self.resource(self.explorer[name], tuple(name.split('/')))

    def page(self, group, item_id, lang, name):
        if group == 'apercus-spek':
            pages = self.pages[item_id]
        elif group == 'notions-spek':
            pages = self.notions[item_id]
        else:
            pages = self.portal[item_id]['pages']
        return self.resource(pages[lang][name], (lang, name))


def teacher_attempt(store, action, data):
    token = data.get('attempt_id')
    if not isinstance(token, str) or not TOKEN.fullmatch(token):
        raise ValueError('Tentative invalide')
    if action != 'inspect':
        version = data.get('result_digest')
        if not isinstance(version, str) or not re.fullmatch(r'sha256:[0-9a-f]{64}', version):
            raise ValueError('Version de résultat requise')
        if action == 'review':
            store.review(token, data.get('reviews'), version)
        elif action == 'release':
            store.release(token, data.get('reviewer'), version, require_complete=True)
    row = store.inspect(token)
    exam, attempt, result = row['exam'], row['attempt'], row['result']
    return {
        'attempt_id': token, 'title': exam['blueprint']['title'],
        'released': bool(row['released']), 'result': result,
        'items': [{**{key: item[key] for key in ('id', 'kind', 'prompt')},
                   'answer': attempt['answers'].get(item['id']) if attempt else None,
                   'option_labels': {option['id']: option['text'] for option in item.get('options', [])},
                   'criteria': item['scoring'].get('criteria', [])}
                  for item in exam['items']],
    }
