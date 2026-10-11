#!/usr/bin/env python3
"""Install v2 alongside v1 without silently replacing local Kristal content.

Dry-run by default, allow idempotent repeat and backup before changed metadata.
"""
from pathlib import Path
import json,argparse,sys,shutil,datetime
HERE=Path(__file__).resolve().parents[1]
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def dumped(x):return (json.dumps(x,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,default=HERE);ap.add_argument('--apply',action='store_true');a=ap.parse_args()
    root=a.root.resolve();src=root/'modules/qc-pri-us-009';target=root/'kristals/qc-pri-us-009'
    if not (target/'kristal.workspace.json').exists() or not (target/'canon/domain/societes-rencontres-v1.json').exists():
        sys.exit('STOP: installer d’abord la v1 via tools/integrer_kristal_histoire.py --root . --restore-missing-frame --apply (option si cadre absent), puis --apply; sauvegarder avant.')
    if read(target/'kristal.workspace.json').get('slug')!='qc-pri-us-009':sys.exit('STOP: mauvais Kristal')
    to_copy=['canon/domain/societes-rencontres-v2.json','sources/source-catalog.v2.json','sources/TRACABILITE_ASSERTIONS_v2.json','experience/histoire-rencontres/RESSOURCES_VISUELLES_V2.json']
    for rel in to_copy:
        if not (src/rel).is_file():sys.exit('STOP: source v2 manquante '+rel)
    outputs={}
    for rel in to_copy:
        path=target/rel;b=(src/rel).read_bytes()
        if path.exists() and path.read_bytes()!=b:sys.exit('STOP: fichier local différent, pas d’écrasement : '+str(path))
        outputs[path]=b
    idxp=target/'canon/state.index.json';idx=read(idxp)
    artifact={'artifact_id':'urn:kristal:qc-pri-us-009:societes-rencontres-v2','path':'canon/domain/societes-rencontres-v2.json','logical_contract':{'id':'ekole.histoire-societes-contextualisees','version':'2.0'},'commitment':{'mode':'compute-json-jcs','profile':'kristal.logical/jcs-sha256-v1'},'scope':{'domain':'univers_social'}}
    registered=[x for x in idx.get('canonical_artifacts',[]) if x.get('artifact_id')==artifact['artifact_id'] or x.get('path')==artifact['path']]
    if registered and registered != [artifact]:sys.exit('STOP: registre du canon v2 en conflit')
    if not registered:idx.setdefault('canonical_artifacts',[]).append(artifact)
    outputs[idxp]=dumped(idx)
    catp=target/'sources/source-catalog.json';cat=read(catp);refcat=read(src/'sources/source-catalog.v2.json')
    registered={x['id']:x for x in cat.get('sources',[])}
    for x in refcat['sources']:
        if x['id'] in registered and x!=registered[x['id']]:sys.exit('STOP: source existante différente '+x['id'])
        if x['id'] not in registered:cat.setdefault('sources',[]).append(x)
    outputs[catp]=dumped(cat)
    changes={p:b for p,b in outputs.items() if not p.exists() or p.read_bytes()!=b}
    for f in changes:print('AJOUT/MODIFICATION',f.relative_to(root))
    print('Bilan',len(changes),'opérations;', 'appliquer' if a.apply else 'prévisualisation')
    if not a.apply or not changes:return
    old={p:(p.read_bytes() if p.exists() else None) for p in changes}
    stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    backup=root/'.ekole-backups/societes-quebec-v2'/stamp
    try:
        for p,b in old.items():
            if b is not None:
                dest=backup/p.relative_to(root);dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(b)
        for p,b in changes.items():p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
    except Exception:
        for p,b in old.items():
            if b is None and p.exists():p.unlink()
            elif b is not None:p.write_bytes(b)
        raise
    print('OK - sources et canon v1 préservés; sauvegardes',backup if backup.exists() else 'non nécessaires')
if __name__=='__main__':main()
