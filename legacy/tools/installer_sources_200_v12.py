#!/usr/bin/env python3
"""Restaurer les sources pédagogiques originales manquantes, sans écraser.
Le paquet référentiel n'est pas une approbation pédagogique.
"""
from __future__ import annotations
import argparse, pathlib, zipfile, re, hashlib, json
ROOT=pathlib.Path(__file__).resolve().parents[1]
RE=re.compile(r'^kristals/qc-pri-[a-z]+-\d{3}/[a-zA-Z0-9_.\-/]+$')
ZIPNAME='archives/KRISTALS_200_REFERENCES_ORIGINALES.zip'
def restore(root=ROOT,*,apply=False):
 root=pathlib.Path(root).resolve();archive=root/ZIPNAME
 if not archive.is_file() or archive.is_symlink():raise FileNotFoundError(archive)
 todo=[];existing=0;ids=set()
 with zipfile.ZipFile(archive) as z:
  infos=[i for i in z.infolist() if not i.is_dir()]
  if len(infos)>5000 or sum(i.file_size for i in infos)>25_000_000 or any(i.file_size>500_000 for i in infos):raise ValueError('Archive de sources hors limites')
  for info in infos:
   name=info.filename
   if not RE.fullmatch(name) or '..' in pathlib.PurePosixPath(name).parts:raise ValueError('Chemin ZIP dangereux: '+name)
   # Le ZIP source ne doit contenir ni liens symboliques, ni exécutables cachés.
   if ((info.external_attr>>16)&0o170000)==0o120000:raise ValueError('Lien symbolique dans ZIP')
   kid=name.split('/')[1];ids.add(kid)
   target=root/name
   if not target.resolve().is_relative_to(root):raise ValueError('Chemin sortant')
   if target.is_symlink():raise ValueError('Lien symbolique existant: '+name)
   if target.exists():existing+=1;continue
   if any(p.is_symlink() for p in list(target.parents)[:-1] if p!=root and root in p.parents):raise ValueError('Parent symbolique')
   todo.append(info)
  if len(ids)!=200:raise ValueError('200 dossiers sources attendus, trouvé '+str(len(ids)))
  if apply:
   for info in todo:
    path=root/info.filename;path.parent.mkdir(parents=True,exist_ok=True)
    try:
     with path.open('xb') as f:f.write(z.read(info))
    except FileExistsError:pass
 return {'dossiers_reference':len(ids),'fichiers_existants_preserves':existing,'fichiers_a_restaurer':len(todo),'effectivement_ecrits':len(todo) if apply else 0,'dry_run':not apply}
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--root',default=ROOT);ap.add_argument('--apply',action='store_true');a=ap.parse_args()
 print(json.dumps(restore(a.root,apply=a.apply),ensure_ascii=False,indent=2))
