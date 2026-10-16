#!/usr/bin/env python3
"""Enregistre deux références épinglées dans le Kristal du cours, sans y recopier les corpus.
Prévisualisation par défaut; --apply avec sauvegarde; aucun écrasement de fichier personnalisé.
"""
from pathlib import Path
import argparse,datetime,json,sys,shutil
ROOT=Path(__file__).resolve().parents[1]
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def bytes_json(d):return (json.dumps(d,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
def plan(root, restore_frame=False, detach_legacy=False):
    root=Path(root).resolve(); target=root/'kristals/qc-pri-us-009'; frame=root/'cadres-source/qc-pri-us-009'
    source=root/'cours-references/qc-pri-us-009/REFERENCES_KRISTALS_V3.json'
    if not source.is_file():raise ValueError('Manifest de références v3 absent')
    c=read(source)
    if not (target/'kristal.workspace.json').exists():
        if not restore_frame:raise ValueError('Cadre du cours absent. Réessayer avec --restore-missing-course-frame.')
        if not (frame/'kristal.workspace.json').is_file():raise ValueError('Cadre modèle absent')
    wp=target/'kristal.workspace.json'; wsp=read(wp) if wp.is_file() else read(frame/'kristal.workspace.json')
    if wsp.get('slug')!='qc-pri-us-009':raise ValueError('Kristal de cours incorrect')
    edits={}
    if restore_frame:
        for p in frame.rglob('*'):
            if p.is_file():
                dest=target/p.relative_to(frame)
                if not dest.exists():edits[dest]=p.read_bytes()
    # Validate refs and source integrity *before* changing the course.
    for ref in c['dependances']:
        g=root/ref['local_path']; slug=ref['kristal']
        if not g.is_file():raise ValueError('Kristal externe manquant: '+slug)
        import hashlib
        if hashlib.sha256(g.read_bytes()).hexdigest()!=ref['file_sha256']:raise ValueError('Corpus externe modifié: '+slug)
        s=read(root/'kristals'/slug/'build/v9/state-snapshot.json')
        if s['logical_commitment']!=ref['state_logical_commitment']:raise ValueError('Version v9 épinglée incorrecte: '+slug)
    dest=target/'experience/histoire-rencontres/REFERENCES_KRISTALS_V3.json'
    new=source.read_bytes()
    if dest.exists() and dest.read_bytes()!=new:raise ValueError('Référence cours personnalisée : STOP, résoudre explicitement '+str(dest))
    if not dest.exists():edits[dest]=new
    # Course owns a canonical selection, never the external historical assertions.
    selection_src=root/'cours-references/qc-pri-us-009/SELECTION_PEDAGOGIQUE_V3.json'
    selected=read(selection_src)
    if selected.get('selection_faits')!=c.get('selection_faits'):raise ValueError('Sélection canonique incohérente')
    selection_dest=target/'canon/domain/SELECTION_PEDAGOGIQUE_V3.json'
    if selection_dest.exists() and selection_dest.read_bytes()!=selection_src.read_bytes():
        raise ValueError('Sélection du cours personnalisée : STOP, réviser explicitement')
    if not selection_dest.exists():edits[selection_dest]=selection_src.read_bytes()
    idx_path=target/'canon/state.index.json'
    idx=read(idx_path) if idx_path.is_file() else read(frame/'canon/state.index.json')
    # Legacy v1/v2 facts may still be registered as course-owned canonical artifacts.
    # They remain on disk for archives, but their old canonical ownership must be
    # detached explicitly to prevent a duplicated source of historical truth.
    legacy_ids={'urn:kristal:qc-pri-us-009:societes-rencontres','urn:kristal:qc-pri-us-009:societes-rencontres-v2'}
    legacy=[a for a in idx.get('canonical_artifacts',[]) if a.get('artifact_id') in legacy_ids]
    if legacy and not detach_legacy:
        raise ValueError('Le cours revendique encore '+str(len(legacy))+' artefacts historiques v1/v2. Réessayer avec --detach-legacy après une sauvegarde : les fichiers seront conservés, mais retirés du canon actif du cours.')
    if legacy:
        print('DÉTACHEMENT EXPLICITE des artefacts historiques du cours :',*[a['artifact_id'] for a in legacy])
        idx['canonical_artifacts']=[a for a in idx['canonical_artifacts'] if a.get('artifact_id') not in legacy_ids]
    refs=idx.setdefault('external_references',[])
    for ref in c['dependances']:
        item={'state_ref':ref['state_ref'],'logical_commitment':ref['state_logical_commitment']}
        others=[x for x in refs if x.get('state_ref')==ref['state_ref']]
        if others and others != [item]:raise ValueError('Épinglage préexistant différent : '+ref['kristal'])
        if not others:refs.append(item)
    art={'artifact_id':'urn:kristal:qc-pri-us-009:selection-pedagogique-v3',
         'path':'canon/domain/SELECTION_PEDAGOGIQUE_V3.json',
         'logical_contract':{'id':'ekole.selection-pedagogique','version':'3.0'},
         'commitment':{'mode':'compute-json-jcs','profile':'kristal.logical/jcs-sha256-v1'},
         'scope':{'domain':'univers_social'}}
    arts=idx.setdefault('canonical_artifacts',[])
    matching=[x for x in arts if x.get('artifact_id')==art['artifact_id'] or x.get('path')==art['path']]
    if matching and matching != [art]:raise ValueError('Collision registre de sélection v3')
    if not matching:arts.append(art)
    idx['notes']='Le cours conserve sa sélection pédagogique v3. Le graphe des nations et celui des rencontres appartiennent aux Kristals autonomes; anciennes versions v1/v2 non utilisées dans la projection v3.'
    if not idx_path.exists() or idx_path.read_bytes()!=bytes_json(idx):edits[idx_path]=bytes_json(idx)
    # Existing original ownership from v1/v2 is historic; modify workspace ownership only if it can be updated safely.
    neww=__import__('copy').deepcopy(wsp)
    own=neww.setdefault('semantic_ownership',{})
    owns=own.setdefault('owns',[])
    if detach_legacy:
        old_claim='faits sourcés sur les rencontres et échanges du cours qc-pri-us-009'
        if old_claim in owns:owns.remove(old_claim)
    note='sélection pédagogique et progression du cours qc-pri-us-009 (pas le corpus historique externe)'
    if note not in owns:owns.append(note)
    dont=own.setdefault('does_not_own',[])
    for slug in ('societes-autochtones-quebec','rencontres-coloniales-quebec'):
        n='assertions et relations canoniques du Kristal '+slug
        if n not in dont:dont.append(n)
    if wp.is_file() and wp.read_bytes()!=bytes_json(neww) or not wp.is_file():edits[wp]=bytes_json(neww)
    return edits

def main():
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=ROOT);p.add_argument('--apply',action='store_true');p.add_argument('--restore-missing-course-frame',action='store_true');p.add_argument('--detach-legacy',action='store_true',help='Retirer les anciens artefacts historiques v1/v2 du canon actif du cours, en conservant leurs fichiers et une sauvegarde');a=p.parse_args()
    try:edits=plan(a.root,a.restore_missing_course_frame,a.detach_legacy)
    except (ValueError,KeyError,FileNotFoundError) as exc:sys.exit('STOP : '+str(exc))
    root=a.root.resolve()
    for dest in edits:print('AJOUT/MODIFICATION',dest.relative_to(root))
    print(len(edits),'modifications','(PRÉVISUALISATION)' if not a.apply else '(APPLICATION)')
    if not a.apply or not edits:return
    old={p:(p.read_bytes() if p.exists() else None) for p in edits}
    stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    backup=root/'.ekole-backups'/'references-cours-v3'/stamp
    try:
        for path,content in old.items():
            if content is not None:
                dest=backup/path.relative_to(root);dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(content)
        for path,content in edits.items():
            path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(content)
    except Exception:
        for path,content in old.items():
            if content is None and path.exists():path.unlink()
            elif content is not None:path.write_bytes(content)
        raise
    print('Références épinglées installées; aucun fait v3 copié dans le cours.')
if __name__=='__main__':main()
