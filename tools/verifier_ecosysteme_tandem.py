#!/usr/bin/env python3
"""Audit MULTI-DEPOTS local, lecture seule, données synthétiques uniquement.

N'ouvre aucun serveur. Ne crée ni World, ni Case, ni Task, ni identité enfant.
Le statut validé ici est la conformité des contrats de prévisualisation, pas
l'admission effective par Orgo, Orgo_Worlds ou Konnaxion.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

UUIDS = {
    'tenant_id': '11111111-1111-4111-8111-111111111111',
    'world_id': '22222222-2222-4222-8222-222222222222',
    'world_release_id': '33333333-3333-4333-8333-333333333333',
}


def locate(workspace: Path | None) -> dict[str, Path]:
    if workspace:
        home = workspace.resolve()
        repos = {name: home / name for name in (
            'ekole','Kontexte','Kompose','Akor','Orgo','Orgo_Worlds','Kolor',
        )}
        repos['Akor'] = (repos['Akor'] / 'Akor') if (repos['Akor'] / 'Akor').is_dir() else repos['Akor']
    else:
        home = Path('C:/mycode')
        repos = {'ekole': home/'Ekole/ekole','Kontexte':home/'Ekole/Kontexte',
            'Kompose':home/'Ekole/Kompose','Akor':home/'Ekole/Akor',
            'Orgo':home/'Orgo/Orgo','Orgo_Worlds':home/'Orgo/Orgo_Worlds',
            'Kolor':home/'Ekole/Kolor'}
        # Le snapshot Akor comporte le dépôt Python sous Akor/Akor.
        if (repos['Akor']/'Akor/src/akor').is_dir():
            repos['Akor'] = repos['Akor']/'Akor'
    for name, path in repos.items():
        if not path.is_dir():
            raise RuntimeError(f'Depot requis absent : {name} ({path})')
    return repos


def run(workspace: Path | None = None) -> dict:
    repos = locate(workspace)
    for src in (repos['Kontexte']/'src',repos['Akor']/'src',repos['Kompose']/'src'):
        sys.path.insert(0,str(src))
    from kontexte.cli import read_all
    from kontexte.tandem import build_teacher_preview
    from kontexte.orgo import scenario_fixture
    from kontexte.qc3_b5 import B5_HISTORICAL_MISSIONS, gather
    from kontexte.curriculum_candidates import audit as audit_curriculum_candidates
    from akor.tandem_intent import prepare_intent
    from kompose.tandem_handoff import verify_initial_design_preview

    _,roles,missions=read_all(repos['Kontexte'])
    b5=gather(repos['Kontexte'])
    candidate_audit=audit_curriculum_candidates(repos['Kontexte'])
    review_manifest=json.loads((repos['Orgo_Worlds']/'world-packs/ekole-fete-sorciere/world-pack.json').read_text(encoding='utf-8'))
    actual_sha=hashlib.sha256((repos['Kontexte']/'data/missions/fete-sorciere.json').read_bytes()).hexdigest()
    if review_manifest.get('source',{}).get('sha256')!=actual_sha:
        raise RuntimeError('World pack REVUE construit sur une version différente de La Fête de la sorcière')
    if set(b5['missions'])!=B5_HISTORICAL_MISSIONS:
        raise RuntimeError('Le referentiel B5 historique a ete modifie')
    kolor=json.loads((repos['Kolor']/'data/roles.json').read_text(encoding='utf-8'))
    visual={r['id']:r['visual_id'] for r in kolor}
    if len(roles)!=38 or set(roles)!=set(visual):
        raise RuntimeError('Inventaire Kontexte / Kolor non identique (38 roles attendus)')
    if any(visual[rid]!='role-'+rid for rid in roles):
        raise RuntimeError('Incoherence des identifiants visuels Kolor')

    rows=[]
    preview_blockers=[]
    with tempfile.TemporaryDirectory(prefix='tandem_conformance_') as temp:
        tmp=Path(temp)
        for mid,mission in sorted(missions.items()):
            safety=mission.get('safety')
            preview_enabled=(isinstance(safety,dict) and
                safety.get('real_spending') is False and
                safety.get('real_taxes') is False and
                safety.get('publication_default')=='private')
            intent=None
            if preview_enabled:
                preview=build_teacher_preview(mission,**UUIDS,workflow_ref='revue-synthetique')
                if not verify_initial_design_preview(preview,mission)['initial_state_checked']:
                    raise RuntimeError(f'Mission non conforme Kompose : {mid}')
                preview_path=tmp/(mid+'.preview.json')
                preview_path.write_text(json.dumps(preview,ensure_ascii=False,indent=2),encoding='utf-8')
                intent=prepare_intent(kontexte=repos['Kontexte'],kompose=repos['Kompose'],
                    ekole=repos['ekole'],preview=preview_path,**UUIDS)
                if any(intent[key] is not False for key in (
                    'runtime_admitted','teacher_authorized','permissions_verified',
                    'world_release_verified','dispatch_allowed','may_publish_to_child')):
                    raise RuntimeError('Intention Akor revendiquant une autorisation')
            else:
                preview_blockers.append(mid)
            rows.append({'mission_id':mid,'steps':len(mission['steps']),
                         'missing_curriculum_links':sum(not s.get('curriculum_ids') for s in mission['steps']),
                         'intent':intent,'scenario_fixture':scenario_fixture(mission)})
        # Node valide les contrats existants des deux proprietaires Orgo sans import runtime.
        payload=tmp/'plans.json'
        payload.write_text(json.dumps(rows,ensure_ascii=False),encoding='utf-8')
        js=Path(__file__).with_name('verifier_ecosysteme_tandem.mjs')
        node=subprocess.run(['node',str(js),str(repos['Orgo']),str(repos['Orgo_Worlds']),str(payload)],
                            capture_output=True,text=True,check=False,timeout=90)
        if node.returncode:
            raise RuntimeError('Echec des contrats Orgo/Worlds : '+(node.stderr or node.stdout)[:2000])
        node_result=json.loads(node.stdout)
    missing={x['mission_id']:x['missing_curriculum_links'] for x in rows if x['missing_curriculum_links']}
    return {
        'format':'ekole.tandem-offline-audit/1.0',
        'scope':'synthetic_read_only_no_runtime_admission',
        'missions_checked':len(rows), 'historic_b5_missions':len(B5_HISTORICAL_MISSIONS),
        'roles_kontexte_kolor':len(roles),'tasks_checked':sum(x['steps'] for x in rows),
        'world_contracts_checked':node_result['world_contracts_checked'],
        'candidate_links_pending_teacher_review':candidate_audit['proposals_checked'],
        'world_review_source_hash_verified':True,
        'curriculum_approved_links_added':candidate_audit['remaining_approved_links_created'],
        'world_pack_review_steps':node_result['world_pack_review_steps'],
        'preview_blocked_missing_structured_safety':preview_blockers,
        'orgo_review_fixtures_checked':node_result['orgo_review_fixtures_checked'],
        'missions_with_curriculum_gaps':missing,
        'runtime_admitted':False,'teacher_authorized':False,'dispatch_allowed':False,
        'kidaxion_implemented_by_this_check':False,
    }


def main(argv=None) -> int:
    p=argparse.ArgumentParser(description='Conformite hors ligne des contrats Tandem (sans ecriture Orgo)')
    p.add_argument('--workspace',type=Path,help='Dossier contenant les repos extraits a plat (test hors Windows)')
    p.add_argument('--out',type=Path,help='Rapport JSON (aucune donnee personnelle)')
    args=p.parse_args(argv)
    try:
        result=run(args.workspace)
        report=json.dumps(result,indent=2,ensure_ascii=False)+'\n'
        if args.out:
            args.out.parent.mkdir(parents=True,exist_ok=True)
            args.out.write_text(report,encoding='utf-8')
        print(report,end='')
        return 0
    except (RuntimeError,OSError,ValueError,subprocess.TimeoutExpired) as exc:
        print('[ECHEC] '+str(exc),file=sys.stderr)
        return 1
if __name__=='__main__':raise SystemExit(main())
