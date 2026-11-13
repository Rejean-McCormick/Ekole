"""Contrôle hors ligne des candidats PRF-22 versionnés dans Ékole.

Contrôle strict des empreintes des fichiers déjà indexés, du schéma, des plans
anonymes et du refus explicite de toute autorité d'exécution.
Ne prétend pas certifier l'exactitude des liens pédagogiques.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import sys
from prf22_validator import validate_document

def verify(bank: Path) -> dict:
    bank=bank.resolve()
    m=json.loads((bank/'MANIFEST.json').read_text(encoding='utf-8'))
    if m.get('format')!='ekole.prf22.banque-candidate/0.4' or m.get('status')!='candidates_non_qualifies':
        raise ValueError('Format ou statut de banque incorrect')
    # Snapshot immuable : inclut les plans 1/8/30 et les catalogues.
    snapshot=json.loads((bank/'SNAPSHOT_SHA256.json').read_text(encoding='utf-8'))
    if snapshot.get('format')!='ekole.prf22.repo-snapshot/0.5':
        raise ValueError('Manifeste des empreintes manquant ou incompatible')
    recorded=snapshot['files']
    existing={p.relative_to(bank).as_posix() for p in bank.rglob('*') if p.is_file() and p.name!='SNAPSHOT_SHA256.json'}
    if existing!=set(recorded):
        raise ValueError('Fichiers de la banque manquants ou non indexés')
    for rel,expected in recorded.items():
        target=(bank/rel).resolve()
        if not target.is_relative_to(bank):
            raise ValueError('Chemin hors de la banque')
        if hashlib.sha256(target.read_bytes()).hexdigest()!=expected:
            raise ValueError('Empreinte de la banque incorrecte : '+rel)
    records=m.get('entries',[])
    if not records or m.get('entries_count')!=len(records):
        raise ValueError('Index incomplet ou nombre de propositions incohérent')
    seen=set(); sources=set()
    for rec in records:
        rel=Path(rec['folder'])
        if rel.is_absolute() or '..' in rel.parts:
            raise ValueError('Chemin dangereux dans index : '+str(rel))
        folder=(bank/rel).resolve()
        if not folder.is_relative_to(bank):
            raise ValueError('Référence sortant de la banque : '+str(rel))
        if str(rel) in seen:raise ValueError('Dossier dupliqué : '+str(rel))
        seen.add(str(rel)); sources.add(rec['source_ref'])
        for fname in ('design.json','brouillon.json','handoff.json'):
            path=folder/fname
            observed=hashlib.sha256(path.read_bytes()).hexdigest()
            if observed!=rec['files_sha256'][fname]:
                raise ValueError('Empreinte invalide : '+str(path))
        design=json.loads((folder/'design.json').read_text(encoding='utf-8'))
        errors,_=validate_document(design)
        if errors:raise ValueError('Contrat PRF-22 non conforme : '+str(rel)+' '+repr(errors[:2]))
        flags=design['governance']
        if flags['activation_authorized'] or flags['publication_authorized'] or flags['student_data_included']:
            raise ValueError('Droit ou données élèves interdits : '+str(rel))
        handoff=json.loads((folder/'handoff.json').read_text(encoding='utf-8'))
        if any(handoff.get(k) is not False for k in
               ('session_admitted','permissions_granted','konnaxion_project_created','orgo_world_created')):
            raise ValueError('Handoff non neutre : '+str(rel))
        for count in (1,8,30):
            plan=json.loads((folder/f'plan-{count:02d}.json').read_text(encoding='utf-8'))
            part=plan['participation']; teams=part['teams']; rounds=part['rotation']
            if sum(int(t['size']) for t in teams)!=count or part['anonymized_placeholder_only'] is not True:
                raise ValueError('Organisation incorrecte : '+str(rel))
            assigned={(a['team_id'],a['station_id']) for r in rounds for a in r['assignments'] if a['station_id']}
            if len(assigned)!=len(teams)*len(part['stations']):
                raise ValueError('Station manquante ou dupliquée : '+str(rel))
            for r in rounds:
                pids=[a['post_id'] for a in r['assignments'] if a['post_id']]
                if len(pids)!=len(set(pids)):
                    raise ValueError('Conflit de poste : '+str(rel))
    if len(sources)!=m.get('source_situations_covered'):
        raise ValueError('Couverture des sources incohérente')
    return {'bank':str(bank),'propositions_verifiees':len(records),'situations_sources':len(sources),
            'statut':'structures vérifiées; revue pédagogique obligatoire'}

def main(argv=None):
    p=argparse.ArgumentParser()
    p.add_argument('--banque',type=Path,required=True)
    args=p.parse_args(argv)
    try:print(json.dumps(verify(args.banque),ensure_ascii=False,indent=2));return 0
    except (OSError,ValueError,KeyError,TypeError) as exc:
        print('ÉCHEC :',exc,file=sys.stderr);return 2
if __name__=='__main__':sys.exit(main())
