"""Private B2 work, explicit human review and atomic local release by course or lot."""
from datetime import datetime, timezone
import importlib
import json
import secrets
import sys


def load_b2(root):
    tools = root / 'outils'
    sys.path.insert(0, str(tools))
    try:
        return importlib.import_module('b2_pipeline.core')
    finally:
        sys.path.pop(0)


class Editorial:
    def __init__(self, root, seeds, pack, store):
        self.root, self.seeds, self.store = root, seeds, store
        self.courses = {course['id']: course for course in pack['cours']}
        self.paths = {path['id']: path for path in pack['parcours']}
        self.grades = {cid: int(path['id'].split('-')[-1]) for path in pack['parcours'] for cid in path['cours_ids']}
        self.b2 = load_b2(root)
        if set(seeds) - set(self.courses):
            raise ValueError('Brouillon prérempli hors corpus')
        if store:
            with store.connect() as db:
                db.execute("""CREATE TABLE IF NOT EXISTS ekole_lessons (
                    course TEXT PRIMARY KEY, revision TEXT NOT NULL, draft TEXT NOT NULL, review TEXT,
                    publication TEXT, publication_source TEXT, publication_revision TEXT)""")
                db.execute("""CREATE TABLE IF NOT EXISTS ekole_lesson_events (
                    seq INTEGER PRIMARY KEY, course TEXT NOT NULL, event TEXT NOT NULL,
                    revision TEXT NOT NULL, time TEXT NOT NULL, payload TEXT NOT NULL)""")

    @staticmethod
    def row(db, cid):
        return db.execute('SELECT * FROM ekole_lessons WHERE course=?', (cid,)).fetchone()

    def source(self, cid):
        if not isinstance(cid, str) or cid not in self.courses:
            raise ValueError('Cours inconnu')
        source = self.b2.source_info(self.root, cid)
        source['grade'] = self.grades.get(cid, 3)
        return source

    def new_draft(self, cid, source):
        draft = self.b2.source_scaffold(source, cid)
        if cid in self.seeds:
            for step, seed in zip(draft['modules'], self.seeds[cid]):
                step.update(titre=seed['titre'], blocks=seed['blocks'])
        return draft

    def summary(self):
        with self.store.connect() as db:
            rows = {row['course']: row for row in db.execute(
                'SELECT course, revision, review IS NOT NULL AS reviewed, publication_revision FROM ekole_lessons')}
        return [{'id': path['id'], 'title': path['titre'], 'courses': [
            {'id': cid, 'title': self.courses[cid]['titre'], 'seeded': cid in self.seeds,
             'draft': cid in rows, 'reviewed': bool(rows[cid]['reviewed']) if cid in rows else False,
             'revision': rows[cid]['revision'] if cid in rows else None,
             'published': bool(rows[cid]['publication_revision']) if cid in rows else False}
            for cid in path['cours_ids']]} for path in self.paths.values()]

    def detail(self, cid):
        source = self.source(cid)
        with self.store.connect() as db:
            row = self.row(db, cid)
        draft = json.loads(row['draft']) if row else self.new_draft(cid, source)
        return {'revision': row['revision'] if row else None, 'draft': draft,
                'seeded': cid in self.seeds, 'reviewed': bool(row and row['review']),
                'published': bool(row and row['publication']),
                'stale': draft['source_provenance'] != source['hashes'] or draft['grade'] != source['grade'],
                'source': {**{key: source['contract'].get(key) for key in
                              ('objectif_observable', 'concepts', 'preuve_attendue')},
                           'reading': f'kristals/{cid}/contenu/01_NOTIONS_ET_EXEMPLES.md'}}

    def prepare(self, pid):
        if not isinstance(pid, str) or pid not in self.paths:
            raise ValueError('Parcours inconnu')
        candidates = self.paths[pid]['cours_ids']
        drafts = []
        for cid in candidates:
            source = self.source(cid)
            drafts.append((cid, self.b2.source_scaffold(source, cid), self.new_draft(cid, source)))
        created = completed = 0
        with self.store.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            for cid, blank, draft in drafts:
                row = self.row(db, cid)
                if row is None:
                    db.execute('INSERT INTO ekole_lessons(course,revision,draft) VALUES(?,?,?)',
                               (cid, secrets.token_hex(16), json.dumps(draft, ensure_ascii=False)))
                    created += 1
                elif (cid in self.seeds and not row['review'] and not row['publication']
                      and json.loads(row['draft']) == blank):
                    revision = secrets.token_hex(16)
                    db.execute('UPDATE ekole_lessons SET draft=?,revision=? WHERE course=?',
                               (json.dumps(draft, ensure_ascii=False), revision, cid))
                    self.event(db, cid, 'seeded', revision, {'draft': draft})
                    completed += 1
        return {'created': created, 'completed': completed, 'courses': len(candidates)}

    def preview(self, cid):
        detail = self.detail(cid)
        public = self.b2.student_publication(detail['draft'], self.source(cid))
        public['notice'] = 'Aperçu privé du brouillon élève.'
        return {'revision': detail['revision'], 'lesson': public}

    def save(self, cid, data):
        source = self.source(cid)
        modules = data.get('modules')
        with self.store.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            row = self.row(db, cid)
            self.expect_revision(row, data.get('revision'))
            draft = json.loads(row['draft']) if row else self.new_draft(cid, source)
            if data.get('rebase') is True:
                if not row:
                    raise ValueError('Aucun brouillon à réaligner')
                # Retain the authored draft and bind it to the current source for a new human review.
                draft['source_provenance'] = source['hashes']
                draft['grade'] = source['grade']
                draft['teacher_brief'] = self.new_draft(cid, source)['teacher_brief']
            else:
                draft['modules'] = modules
            self.b2.validate_draft(draft, source, complete=False)
            revision = secrets.token_hex(16)
            db.execute("""INSERT INTO ekole_lessons(course,revision,draft) VALUES(?,?,?)
                        ON CONFLICT(course) DO UPDATE SET revision=excluded.revision,draft=excluded.draft,review=NULL""",
                       (cid, revision, json.dumps(draft, ensure_ascii=False)))
            self.event(db, cid, 'saved', revision, {'draft': draft})
        return self.detail(cid)

    def review(self, cid, data):
        source = self.source(cid)
        reviewer = data.get('reviewer')
        if not isinstance(reviewer, str) or len(reviewer.strip()) > 160:
            raise ValueError('Nom de relecture invalide')
        with self.store.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            row = self.row(db, cid)
            self.expect_revision(row, data.get('revision'))
            if not row:
                raise ValueError('Enregistrez le brouillon avant la revue')
            receipt = self.b2.review_receipt(json.loads(row['draft']), reviewer,
                'Je confirme avoir relu tout le contenu élève et vérifié les corrigés et données privées.',
                source, data.get('confirmed') is True)
            db.execute('UPDATE ekole_lessons SET review=? WHERE course=?',
                       (json.dumps(receipt, ensure_ascii=False), cid))
            self.event(db, cid, 'reviewed', row['revision'], receipt)
        return self.detail(cid)

    def publish(self, courses, confirmed):
        if confirmed is not True or not isinstance(courses, dict) or not 1 <= len(courses) <= 202:
            raise ValueError('Sélection et confirmation de diffusion locale requises')
        sources = {cid: self.source(cid) for cid in courses}
        with self.store.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            for cid, expected in courses.items():
                row = self.row(db, cid)
                self.expect_revision(row, expected)
                if not row or not row['review']:
                    raise ValueError('Revue manquante : ' + cid)
                draft, receipt = json.loads(row['draft']), json.loads(row['review'])
                source = sources[cid]
                if receipt['draft_sha256'] != self.b2.digest_object(draft) or receipt['source_provenance'] != source['hashes']:
                    raise ValueError('Revue périmée : ' + cid)
                public = self.b2.student_publication(draft, source)
                if (row['publication_revision'] == expected and row['publication_source']
                        and json.loads(row['publication_source']) == source['hashes']):
                    continue
                db.execute("""UPDATE ekole_lessons SET publication=?,publication_source=?,publication_revision=?
                              WHERE course=?""",
                           (json.dumps(public, ensure_ascii=False), json.dumps(source['hashes']), expected, cid))
                self.event(db, cid, 'published_local', expected, {'review': receipt, 'draft': draft})
        return {'published': list(courses)}

    def withdraw(self, cid, data):
        with self.store.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            row = self.row(db, cid)
            self.expect_revision(row, data.get('revision'))
            if data.get('confirmed') is not True or not row or not row['publication']:
                raise ValueError('Aucune version locale ou retrait non confirmé')
            db.execute("""UPDATE ekole_lessons SET publication=NULL,publication_source=NULL,
                          publication_revision=NULL WHERE course=?""", (cid,))
            self.event(db, cid, 'withdrawn', row['publication_revision'], {})
        return self.detail(cid)

    def published_ids(self):
        with self.store.connect() as db:
            return {row['course'] for row in db.execute(
                'SELECT course FROM ekole_lessons WHERE publication IS NOT NULL')}

    def publication(self, cid):
        with self.store.connect() as db:
            row = self.row(db, cid)
        if row and row['publication']:
            return json.loads(row['publication'])
        return None

    def export(self, requested):
        with self.store.connect() as db:
            db.execute('BEGIN')
            rows = {row['course']: row for row in db.execute(
                'SELECT course,publication,publication_source,publication_revision FROM ekole_lessons '
                'WHERE publication IS NOT NULL')}
            selected = sorted(rows if requested is None else set(requested))
            if not selected:
                raise ValueError('Aucune leçon relue et diffusée localement à exporter')
            result = {}
            for cid in selected:
                row = rows.get(cid)
                if not row:
                    raise ValueError('Leçon sans diffusion locale : ' + cid)
                source = self.source(cid)
                if json.loads(row['publication_source']) != source['hashes']:
                    raise ValueError('Sources de la publication modifiées : ' + cid)
                revision = row['publication_revision']
                event = db.execute(
                    'SELECT payload FROM ekole_lesson_events WHERE course=? AND revision=? AND event=? '
                    'ORDER BY seq DESC LIMIT 1', (cid, revision, 'published_local')).fetchone()
                if not event:
                    raise ValueError('Reçu de diffusion introuvable : ' + cid)
                data = json.loads(event['payload'])
                draft, receipt = data['draft'], data['review']
                if (receipt['draft_sha256'] != self.b2.digest_object(draft)
                        or receipt['source_provenance'] != source['hashes']):
                    raise ValueError('Reçu incompatible : ' + cid)
                public = self.b2.student_publication(draft, source)
                if public != json.loads(row['publication']):
                    raise ValueError('Leçon exportée différente de la diffusion : ' + cid)
                result[cid] = (public, draft, revision)
        return result

    @staticmethod
    def expect_revision(row, value):
        if value != (row['revision'] if row else None):
            raise ValueError('Brouillon modifié; rechargez la leçon')

    @staticmethod
    def event(db, cid, kind, revision, payload):
        db.execute('INSERT INTO ekole_lesson_events(course,event,revision,time,payload) VALUES(?,?,?,?,?)',
                   (cid, kind, revision, datetime.now(timezone.utc).isoformat(), json.dumps(payload, ensure_ascii=False)))
