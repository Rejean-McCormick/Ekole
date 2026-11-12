"""Journal pédagogique LOCAL, sous contrôle enseignant, par séance Ékole.

Ce module NE délivre PAS d'identité, d'autorisation Orgo ou de certificat de
maîtrise. Il conserve des références pseudonymes et des observations soumises
à la revue d'un enseignant. À intégrer plus tard avec un vrai SSO scolaire.
"""
from __future__ import annotations
import argparse
import json
import re
import sqlite3
from pathlib import Path
from datetime import datetime, timezone

REF = re.compile(r"[a-zA-Z0-9][a-zA-Z0-9._:-]{1,99}\Z")
SOURCES = {"orgo", "konnaxion", "inkuisite", "enseignant"}
ASSISTANCE = {"autonome", "avec_aide", "non_determinee"}
DECISIONS = {"validee", "a_reprendre", "non_probante"}
SCHEMA = """
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS sessions (
  id TEXT PRIMARY KEY, mission_ref TEXT NOT NULL,
  orgo_world_ref TEXT, konnaxion_project_ref TEXT, created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS attributions (
  session_ref TEXT NOT NULL REFERENCES sessions(id),
  eleve_ref TEXT NOT NULL, task_ref TEXT NOT NULL, role_code TEXT NOT NULL,
  PRIMARY KEY (session_ref,eleve_ref,task_ref)
);
CREATE TABLE IF NOT EXISTS preuves (
  event_ref TEXT PRIMARY KEY,
  session_ref TEXT NOT NULL REFERENCES sessions(id),
  eleve_ref TEXT NOT NULL,task_ref TEXT NOT NULL,
  source TEXT NOT NULL,source_ref TEXT NOT NULL,
  assistance TEXT NOT NULL, observation TEXT NOT NULL,
  content_hash TEXT NOT NULL,created_at TEXT NOT NULL,
  FOREIGN KEY (session_ref,eleve_ref,task_ref)
      REFERENCES attributions(session_ref,eleve_ref,task_ref)
);
CREATE TABLE IF NOT EXISTS revues (
  review_ref TEXT PRIMARY KEY, event_ref TEXT NOT NULL REFERENCES preuves(event_ref),
  decision TEXT NOT NULL, objectif_ref TEXT,
  reviewer_ref TEXT NOT NULL, note TEXT NOT NULL, reviewed_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS ix_preuves_eleve ON preuves(session_ref,eleve_ref,task_ref);
CREATE INDEX IF NOT EXISTS ix_revues_event ON revues(event_ref,reviewed_at);
"""


def _ref(value: str | None, *, required=True):
    if value is None and not required:return None
    if not isinstance(value,str) or not REF.fullmatch(value):
        raise ValueError("Identifiant invalide (sans données personnelles ni espaces)")
    return value


def _now():
    return datetime.now(timezone.utc).isoformat(timespec="microseconds")


def connect(path: Path):
    path.parent.mkdir(parents=True,exist_ok=True)
    db=sqlite3.connect(path)
    db.row_factory=sqlite3.Row
    db.execute('PRAGMA foreign_keys=ON')
    db.executescript(SCHEMA)
    return db


def session(db, *, session_ref,mission_ref,orgo_world_ref=None,konnaxion_project_ref=None):
    values=(_ref(session_ref),_ref(mission_ref),_ref(orgo_world_ref,required=False),_ref(konnaxion_project_ref,required=False))
    with db:
        db.execute('INSERT INTO sessions VALUES (?,?,?,?,?)',(*values,_now()))
    return values[0]


def attribuer(db, *, session_ref,eleve_ref,task_ref,role_code):
    values=tuple(_ref(x) for x in (session_ref,eleve_ref,task_ref,role_code))
    with db:
        db.execute('INSERT INTO attributions VALUES (?,?,?,?)',values)
    return values


def preuve(db, *, event_ref,session_ref,eleve_ref,task_ref,source,source_ref,assistance="non_determinee",observation=""):
    import hashlib
    if source not in SOURCES or assistance not in ASSISTANCE:
        raise ValueError('Source ou assistance inconnue')
    if not isinstance(observation,str) or len(observation)>800:
        raise ValueError('Observation invalide')
    values=tuple(_ref(x) for x in (event_ref,session_ref,eleve_ref,task_ref,source_ref))
    claim={"event_ref":values[0],"session_ref":values[1],"eleve_ref":values[2],"task_ref":values[3],
           "source":source,"source_ref":values[4],"assistance":assistance,"observation":observation}
    digest=hashlib.sha256(json.dumps(claim,sort_keys=True,ensure_ascii=False).encode()).hexdigest()
    old=db.execute('SELECT content_hash FROM preuves WHERE event_ref=?',(values[0],)).fetchone()
    if old:
        if old['content_hash']!=digest:raise ValueError('Réutilisation conflictuelle d’un identifiant de preuve')
        return False  # reprise idempotente
    with db:
        db.execute('''INSERT INTO preuves VALUES (?,?,?,?,?,?,?,?,?,?)''',
                   (values[0],values[1],values[2],values[3],source,values[4],assistance,observation,digest,_now()))
    return True


def revue(db, *, review_ref,event_ref,decision,reviewer_ref,objectif_ref=None,note=''):
    if decision not in DECISIONS:raise ValueError('Décision inconnue')
    if not isinstance(note,str) or len(note)>800:raise ValueError('Note invalide')
    vals=(_ref(review_ref),_ref(event_ref),decision,_ref(objectif_ref,required=False),_ref(reviewer_ref),note,_now())
    with db:
        db.execute('INSERT INTO revues VALUES (?,?,?,?,?,?,?)',vals)
    return vals[0]


def rapport(db,session_ref,eleve_ref):
    session_ref=_ref(session_ref);eleve_ref=_ref(eleve_ref)
    session_row=db.execute('SELECT id,mission_ref FROM sessions WHERE id=?',(session_ref,)).fetchone()
    if session_row is None:raise ValueError('Séance inconnue')
    rows=db.execute('''SELECT a.task_ref,a.role_code,p.event_ref,p.source,p.assistance,p.created_at,
        (SELECT decision FROM revues WHERE event_ref=p.event_ref ORDER BY reviewed_at DESC, review_ref DESC LIMIT 1) decision,
        (SELECT objectif_ref FROM revues WHERE event_ref=p.event_ref ORDER BY reviewed_at DESC, review_ref DESC LIMIT 1) objectif_ref
        FROM attributions a LEFT JOIN preuves p
        ON a.session_ref=p.session_ref AND a.eleve_ref=p.eleve_ref AND a.task_ref=p.task_ref
        WHERE a.session_ref=? AND a.eleve_ref=? ORDER BY a.task_ref,p.created_at''',(session_ref,eleve_ref)).fetchall()
    attempted=sum(x['event_ref'] is not None for x in rows)
    validated=sum(x['decision']=='validee' for x in rows)
    return {'format':'ekole.learning-ledger-report/1', 'session_ref':session_ref,
            'mission_ref':session_row['mission_ref'], 'eleve_ref':eleve_ref,
            'tentatives':attempted, 'preuves_validees_par_enseignant':validated,
            'maitrise_automatique':False, 'entrees':[dict(row) for row in rows]}




def portfolio_candidates(db,session_ref,eleve_ref):
    """Private, reference-only showcase candidates reviewed by a teacher.

    This never writes Konnaxion Portfolio and never publishes to a child or
    third party. A second explicit publication decision is still required.
    """
    report=rapport(db,session_ref,eleve_ref)
    latest={}
    for record in report['entrees']:
        if record['event_ref'] is not None:
            latest[record['event_ref']]=record
    approved=[{'event_ref':r['event_ref'],'task_ref':r['task_ref'],
               'role_code':r['role_code'],'objectif_ref':r['objectif_ref'],
               'assistance':r['assistance'],'source':r['source']}
              for r in latest.values() if r['decision']=='validee']
    return {'format':'ekole.portfolio-candidates/1',
            'scope':'private_teacher_review_only',
            'session_ref':_ref(session_ref),'eleve_ref':_ref(eleve_ref),
            'publication_authorized':False,'konnaxion_portfolio_written':False,
            'items':approved}

def main(argv=None):
    p=argparse.ArgumentParser(description='Ékole: registre local de preuves sous revue enseignante (pas de SSO)')
    p.add_argument('--db',type=Path,required=True)
    sub=p.add_subparsers(dest='action',required=True)
    a=sub.add_parser('seance');a.add_argument('session_ref');a.add_argument('mission_ref')
    a=sub.add_parser('attribuer');[a.add_argument(x) for x in ('session_ref','eleve_ref','task_ref','role_code')]
    a=sub.add_parser('observer');[a.add_argument(x) for x in ('event_ref','session_ref','eleve_ref','task_ref','source','source_ref')]
    a.add_argument('--assistance',default='non_determinee');a.add_argument('--observation',default='')
    a=sub.add_parser('revoir');[a.add_argument(x) for x in ('review_ref','event_ref','decision','reviewer_ref')]
    a.add_argument('--objectif-ref');a.add_argument('--note',default='')
    a=sub.add_parser('rapport');a.add_argument('session_ref');a.add_argument('eleve_ref')
    a=sub.add_parser('portfolio');a.add_argument('session_ref');a.add_argument('eleve_ref')
    args=p.parse_args(argv)
    with connect(args.db) as db:
        if args.action=='seance':out=session(db,session_ref=args.session_ref,mission_ref=args.mission_ref)
        elif args.action=='attribuer':out=attribuer(db,session_ref=args.session_ref,eleve_ref=args.eleve_ref,task_ref=args.task_ref,role_code=args.role_code)
        elif args.action=='observer':out=preuve(db,event_ref=args.event_ref,session_ref=args.session_ref,eleve_ref=args.eleve_ref,task_ref=args.task_ref,source=args.source,source_ref=args.source_ref,assistance=args.assistance,observation=args.observation)
        elif args.action=='revoir':out=revue(db,review_ref=args.review_ref,event_ref=args.event_ref,decision=args.decision,reviewer_ref=args.reviewer_ref,objectif_ref=args.objectif_ref,note=args.note)
        elif args.action=='portfolio':out=portfolio_candidates(db,args.session_ref,args.eleve_ref)
        else:out=rapport(db,args.session_ref,args.eleve_ref)
    print(json.dumps(out,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
