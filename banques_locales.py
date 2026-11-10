"""Local, versioned review of Québec's imported Inkuisite drafts."""
from collections import Counter
import secrets

from inkui.common import canonical, digest, loads, require
from inkui.exams import build_exam
from inkui.generation import approve_item


class Banks:
    def __init__(self, catalogue, refs, store, courses):
        self.catalogue = catalogue
        self.refs = refs
        self.store = store
        self.courses = courses
        if refs and set(refs) != set(courses):
            raise ValueError('Le catalogue des banques ne correspond pas au corpus')
        for cid, ref in refs.items():
            if type(ref['items']) is not int or ref['items'] < 1:
                raise ValueError('Nombre de questions invalide')
            catalogue.resource(ref, ('banques-privees', cid + '.json'))
        if store and refs:
            with store.connect() as db:
                db.execute("""CREATE TABLE IF NOT EXISTS ekole_question_reviews (
                    revision INTEGER PRIMARY KEY,
                    course TEXT NOT NULL, item TEXT NOT NULL, source TEXT NOT NULL,
                    decision TEXT NOT NULL, payload TEXT NOT NULL)""")
                db.execute("""CREATE INDEX IF NOT EXISTS ekole_question_reviews_source
                           ON ekole_question_reviews(course, source, item, revision)""")

    def read(self, cid):
        require(cid in self.refs, 'Banque inconnue')
        return loads(self.catalogue.resource(self.refs[cid], ('banques-privees', cid + '.json')).decode('utf-8'))

    def decisions(self, db, course=None):
        condition = 'WHERE course = ?' if course else ''
        params = (course,) if course else ()
        rows = db.execute(f"""SELECT * FROM ekole_question_reviews WHERE revision IN (
            SELECT MAX(revision) FROM ekole_question_reviews {condition} GROUP BY course, item, source
        )""", params)
        return [row for row in rows if row['course'] in self.refs
                and row['source'] == self.refs[row['course']]['source']]

    def counts(self):
        with self.store.connect() as db:
            return Counter(row['course'] for row in self.decisions(db) if row['decision'] == 'reviewed')

    def summary(self):
        counts = self.counts()
        return [{'cours': cid, 'titre': self.courses[cid]['titre'], 'items': ref['items'],
                 'reviewed': counts[cid]} for cid, ref in self.refs.items()]

    def detail(self, cid):
        bank = self.read(cid)
        with self.store.connect() as db:
            states = {row['item']: row for row in self.decisions(db, cid)}
        return {'course': cid, 'source': self.refs[cid]['source'], 'items': [
            {'id': item['id'], 'original': item['upstream_item'],
             'prompt': item['prompt'], 'stimulus': item['stimulus'],
             'revision': states[item['id']]['revision'] if item['id'] in states else None,
             'reviewed': states[item['id']]['decision'] == 'reviewed' if item['id'] in states else False,
             'review': loads(states[item['id']]['payload'])
                       if item['id'] in states and states[item['id']]['decision'] == 'reviewed' else None}
            for item in bank['items']]}

    def change(self, data, *, withdraw=False):
        cid, item_id = data.get('cours'), data.get('item')
        require(isinstance(cid, str) and isinstance(item_id, str), 'Référence de question requise')
        bank = self.read(cid)
        original = next((item for item in bank['items'] if item['id'] == item_id), None)
        require(original is not None, 'Question inconnue')
        ref = self.refs[cid]['source']
        require(data.get('source') == ref, 'Source modifiée; rechargez la banque')
        reviewer = self.text(data, 'reviewer', 160)
        reason = self.text(data, 'reason', 1500)
        if withdraw:
            decision, payload = 'withdrawn', {'reviewer': reviewer, 'reason': reason}
        else:
            require(data.get('confirmed') is True, 'Confirmez la revue pour essai local')
            rubric = self.text(data, 'criterion', 1500)
            prompt = self.text(data, 'prompt', 3000)
            stimulus = data.get('stimulus', '')
            require(isinstance(stimulus, str) and len(stimulus) <= 6000, 'Support trop volumineux')
            next_step = self.text(data, 'feedback', 1500)
            adapted = {**original, 'prompt': prompt, 'stimulus': stimulus,
                       'scoring': {'criteria': [{'id': 'reviewed-criterion', 'description': rubric,
                                                 'max_points': 1}]},
                       'feedback': {'correct': 'Critère observé.', 'incorrect': 'Critère à retravailler.',
                                    'next_step': next_step}}
            decision, payload = 'reviewed', approve_item(adapted, reviewer, reason, scope='demo')
        with self.store.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            current = db.execute("""SELECT revision, decision FROM ekole_question_reviews
                                    WHERE course=? AND item=? AND source=? ORDER BY revision DESC LIMIT 1""",
                                 (cid, item_id, ref)).fetchone()
            revision = current['revision'] if current else None
            require(revision == data.get('revision'), 'Question modifiée; rechargez la banque')
            if withdraw:
                require(current and current['decision'] == 'reviewed', 'Question déjà retirée ou en attente')
            saved = db.execute("""INSERT INTO ekole_question_reviews(course,item,source,decision,payload)
                                  VALUES (?,?,?,?,?)""", (cid, item_id, ref, decision, canonical(payload)))
            return {'revision': saved.lastrowid, 'reviewed': not withdraw}

    def create_attempt(self, cid, *, item_ids=None, mission=None):
        require(cid in self.refs, 'Banque inconnue')
        with self.store.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            items = [loads(row['payload']) for row in self.decisions(db, cid)
                     if row['decision'] == 'reviewed' and (item_ids is None or row['item'] in item_ids)]
            require(bool(items), 'Aucune question relue pour ce cours')
            seed = secrets.token_hex(16)
            selected = sorted(items, key=lambda item: digest([seed, item['id']]))[:5]
            objectives = Counter(item['objective_ref'] for item in selected)
            exam = build_exam({'format': 'inkui.bank/1.0', 'id': cid + '-reviewed',
                               'title': self.courses[cid]['titre'], 'items': selected},
                              {'format': 'inkui.blueprint/1.0', 'id': cid + '-bank-demo',
                               'title': (mission or self.courses[cid]['titre']) + ' · Questions relues',
                               'seed': seed, 'scope': 'demo', 'feedback_policy': 'on_release',
                               'sections': [{'objective_ref': ref, 'count': count}
                                            for ref, count in objectives.items()]})
            return self.store.create(exam, transaction=db)

    @staticmethod
    def text(data, key, limit):
        value = data.get(key)
        require(isinstance(value, str) and 0 < len(value.strip()) <= limit, 'Champ de revue invalide : ' + key)
        return value.strip()
