"""Missions locales par univers, avec exercices natifs et banque relue Inkuisite."""
import json
import os
from pathlib import Path
import re
import secrets

from inkui.common import digest
from inkui.exams import build_exam
from inkui.generation import approve_item


ID = re.compile(r'[a-z][a-z0-9-]{1,70}')


class RolePaths:
    def __init__(self, content, univers, banks):
        self.univers = univers
        self.banks = banks
        self.paths = {}
        self.roles = {}
        self.bank_items = {}
        path = content / 'data/parcours-roles.json'
        doc = json.loads(path.read_bytes())
        if doc.get('format') != 'ekole.parcours-roles/1' or set(doc['themes']) - univers.themes.keys():
            raise ValueError('Catalogue des parcours par rôle incompatible avec les univers.')
        kontexte = Path(os.environ.get('EKOLE_KONTEXTE') or content.parent / 'Kontexte') / 'data/roles'
        for theme, paths in doc['themes'].items():
            if not ID.fullmatch(theme) or not paths:
                raise ValueError('Univers de missions invalide ou vide.')
            self.paths[theme] = paths
            for role, row in paths.items():
                if not ID.fullmatch(role) or row['course'] not in banks.refs:
                    raise ValueError('Rôle ou cours introuvable : ' + role)
                if role not in self.roles:
                    source = json.loads((kontexte / (role + '.json')).read_bytes())
                    if source['id'] != role or source['format'] != 'kontexte.role/1':
                        raise ValueError('Rôle Kontexte invalide : ' + role)
                    self.roles[role] = source['name']['fr-CA']
                cid = row['course']
                if cid not in self.bank_items:
                    self.bank_items[cid] = {item['id']: item['objective_ref'] for item in banks.read(cid)['items']}
                anchors = row['bank']
                if (not 1 <= len(anchors) <= 5 or len(set(anchors)) != len(anchors)
                        or any(anchor not in self.bank_items[cid] for anchor in anchors)):
                    raise ValueError('Questions de banque introuvables ou dupliquées : ' + role)
                objectives = {self.bank_items[cid][anchor] for anchor in anchors}
                if len(objectives) != 1:
                    raise ValueError('Les questions de la mission doivent viser le même objectif : ' + role)
                row['objective'] = objectives.pop()
                self.practice_exam(theme, role, row, 'validation')

    def choice(self, theme, role):
        if theme not in self.univers.profile()['choices']:
            raise KeyError('Univers fermé')
        return self.paths[theme][role]

    def reviewed(self):
        with self.banks.store.connect() as db:
            return {(row['course'], row['item']) for row in self.banks.decisions(db)
                    if row['decision'] == 'reviewed'}

    def listing(self, teacher=False):
        profile = self.univers.profile()
        keys = self.paths.keys() if teacher else profile['choices']
        reviewed = self.reviewed() if teacher else set()
        themes = []
        for theme in keys:
            if theme not in self.paths:
                continue
            entries = []
            for role, row in self.paths[theme].items():
                entry = {'id': role, 'name': self.roles[role], 'title': row['title']}
                if teacher:
                    cid = row['course']
                    entry.update(course=cid, course_title=self.banks.courses[cid]['titre'],
                                 questions=[{'id': item, 'reviewed': (cid, item) in reviewed}
                                            for item in row['bank']])
                entries.append(entry)
            themes.append({'id': theme, 'name': self.univers.themes[theme]['name'],
                           'open': theme in profile['choices'], 'roles': entries})
        return {'themes': themes, 'default': profile['default']}

    def detail(self, theme, role):
        row = self.choice(theme, role)
        cid = row['course']
        course = self.banks.courses[cid]
        universe = self.univers.describe(theme, cid)
        reviewed = self.reviewed()
        return {'theme': theme, 'role': role, 'name': self.roles[role], 'title': row['title'],
                'scene': row['scene'], 'transfer': row['transfer'], 'course': cid,
                'course_title': course['titre'], 'objective': course['objectif'],
                'spek': universe.get('spek'), 'reviewed': sum((cid, item) in reviewed for item in row['bank'])}

    def start(self, mode, data):
        if set(data) != {'univers', 'role'} or not all(isinstance(value, str) for value in data.values()):
            raise ValueError('Univers et rôle requis.')
        theme, role = data['univers'], data['role']
        row = self.choice(theme, role)
        if mode == 'banque':
            return self.banks.create_attempt(row['course'], item_ids=row['bank'],
                                             mission=self.roles[role] + ' · ' + row['title'])
        exam = self.practice_exam(theme, role, row, secrets.token_hex(16))
        return self.banks.store.create(exam)

    @staticmethod
    def practice_exam(theme, role, row, seed):
        uid = theme + '-' + role
        practice = row['practice']
        kind, answer = practice['kind'], practice['answer']
        item = {
            'id': uid + '-pratique', 'status': 'draft', 'kind': kind, 'points': 1,
            'course_ref': row['course'], 'objective_ref': row['objective'],
            'prompt': practice['prompt'], 'stimulus': row['scene'],
            'feedback': {'correct': 'Ta réponse convient à la situation.',
                         'incorrect': 'Reviens aux indices de la mission.',
                         'next_step': practice['hint']},
            'sources': [{'kind': 'authored_example', 'ref': 'ekole:parcours-roles:' + uid,
                         'content_hash': digest(row), 'locator': '/practice'}],
        }
        if kind == 'numeric':
            item['scoring'] = {'expected': answer, 'tolerance': '0'}
        elif kind in ('single_choice', 'multiple_choice'):
            options = practice['options']
            if len(options) != 3 or any(type(index) is not int or not 0 <= index < len(options) for index in answer):
                raise ValueError('Choix d’exercice invalide : ' + role)
            item['options'] = [{'id': 'abc'[i], 'text': value} for i, value in enumerate(options)]
            item['scoring'] = {'method': 'all_or_nothing', 'correct_ids': ['abc'[i] for i in answer]}
        else:
            raise ValueError('Mécanique de pratique inconnue : ' + role)
        item = approve_item(item, 'Ekole · pratique locale',
                            'Exemple du parcours de rôle pour essai local, à relire avant usage en classe.',
                            scope='demo', reviewed_at='2026-11-09T00:00:00Z')
        return build_exam({'format': 'inkui.bank/1.0', 'id': uid, 'title': row['title'], 'items': [item]},
                          {'format': 'inkui.blueprint/1.0', 'id': uid + '-pratique',
                           'title': row['title'], 'seed': seed, 'scope': 'demo', 'feedback_policy': 'immediate',
                           'sections': [{'objective_ref': row['objective'], 'count': 1}]})
