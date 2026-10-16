#!/usr/bin/env python3
"""Intégration transactionnelle de qc-pri-us-009, sans écrasement silencieux."""
from pathlib import Path
import json,argparse,shutil,datetime,hashlib,sys
HERE=Path(__file__).resolve().parents[1]
def read_json(p):return json.loads(p.read_text(encoding='utf-8'))
def json_bytes(v):return (json.dumps(v,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=HERE);p.add_argument('--apply',action='store_true');p.add_argument('--restore-missing-frame',action='store_true');a=p.parse_args()
 root=a.root.resolve();src=root/'modules/qc-pri-us-009';target=root/'kristals/qc-pri-us-009'
 if not (target/'kristal.workspace.json').exists():
  frame=root/'cadres-source/qc-pri-us-009'
  if not a.restore_missing_frame:
   sys.exit('STOP: le cadre Kristal qc-pri-us-009 est absent. Pour ajouter uniquement les fichiers manquants du cadre joint, utiliser --restore-missing-frame --apply.')
  if not frame.exists():sys.exit('STOP: cadre source absent')
  missing=[f for f in frame.rglob('*') if f.is_file() and not (target/f.relative_to(frame)).exists()]
  print('CADRE :',len(missing),'fichiers manquants à restaurer sans écrasement.')
  if not a.apply:
   for f in missing:print('AJOUT CADRE',f.relative_to(frame))
   return
  for f in missing:
   d=target/f.relative_to(frame);d.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(f,d)
  if not (target/'kristal.workspace.json').exists():sys.exit('STOP: cadre incomplet après tentative de restauration')
 if not src.exists():sys.exit('STOP: module source introuvable')
 workspace=read_json(target/'kristal.workspace.json')
 if workspace.get('slug')!='qc-pri-us-009':sys.exit('STOP: workspace incorrect')
 indexp=target/'canon/state.index.json';catp=target/'sources/source-catalog.json'
 if not indexp.exists() or not catp.exists():sys.exit('STOP: index ou catalogue existant manquant')
 index=read_json(indexp);cat=read_json(catp)
 additions=read_json(src/'sources/source-catalog.additions.json')['sources']
 oldids={s['id']:s for s in cat.get('sources',[])}
 for s in additions:
  if s['id'] in oldids and oldids[s['id']]!=s:sys.exit('STOP: source déjà enregistrée avec contenu différent '+s['id'])
  if s['id'] not in oldids:cat.setdefault('sources',[]).append(s)
 artifact={'artifact_id':'urn:kristal:qc-pri-us-009:societes-rencontres','path':'canon/domain/societes-rencontres-v1.json','logical_contract':{'id':'ekole.histoire-societes-rencontres','version':'1.0'},'commitment':{'mode':'compute-json-jcs','profile':'kristal.logical/jcs-sha256-v1'},'scope':{'domain':'univers_social'}}
 existing=[x for x in index.get('canonical_artifacts',[]) if x['artifact_id']==artifact['artifact_id'] or x['path']==artifact['path']]
 if existing and existing != [artifact]:sys.exit('STOP: collision avec un artifact déjà déclaré')
 if not existing:index.setdefault('canonical_artifacts',[]).append(artifact)
 # Keep existing authoring status/profile/scope unless the frame is a stub.
 if workspace.get('status')=='stub':workspace['status']='building'
 native=workspace.setdefault('native_model',{})
 if native.get('kind') in ('undecided',None):native.update(kind='graphe_historique_multicouche',description='Rôles, tâches, ressources et faits sourcés avec overlays temporels.',canonical_paths=['canon/domain'])
 owns=workspace.setdefault('semantic_ownership',{}).setdefault('owns',[])
 if 'faits sourcés sur les rencontres et échanges du cours qc-pri-us-009' not in owns:owns.append('faits sourcés sur les rencontres et échanges du cours qc-pri-us-009')
 outputs={indexp:json_bytes(index),catp:json_bytes(cat),target/'kristal.workspace.json':json_bytes(workspace)}
 for path in src.rglob('*'):
  if not path.is_file() or path.name=='source-catalog.additions.json':continue
  rel=path.relative_to(src)
  if rel.as_posix()=='canon/domain/societes-rencontres-v1.json' or rel.parts[0] in ('experience','docs'):
   dest=target/rel
   b=path.read_bytes()
   if dest.exists() and dest.read_bytes()!=b:sys.exit('STOP: fichier local modifié, pas d’écrasement : '+str(dest))
   outputs[dest]=b
 changes={p:b for p,b in outputs.items() if not p.exists() or p.read_bytes()!=b}
 for f in changes:print('AJOUT/MODIFICATION',f.relative_to(root))
 print('Bilan',len(changes),'opérations;', 'prévisualisation' if not a.apply else 'application demandée')
 if not a.apply:return
 if not changes:return
 stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
 backup=root/'.ekole-backups'/'societes-quebec'/stamp
 try:
  # Prepare copies before touching target; reversible even for unforeseen I/O errors.
  old={p:p.read_bytes() if p.exists() else None for p in changes}
  for f,b in old.items():
   if b is not None:
    dest=backup/f.relative_to(root);dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(b)
  for f,b in changes.items():f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(b)
 except Exception:
  for f,b in old.items():
   if b is None and f.exists():f.unlink()
   elif b is not None:f.write_bytes(b)
  raise
 print('OK intégration; sauvegardes dans',backup if backup.exists() else 'aucune requise')
if __name__=='__main__':main()
