#!/usr/bin/env python3
"""Restaure uniquement les fichiers ABSENTS des cinq Kristals pilotes.
Le répertoire sources est une référence immuable, jamais une migration silencieuse.
"""
from __future__ import annotations
import argparse,pathlib,shutil
ROOT=pathlib.Path(__file__).resolve().parents[1]
def restore(root,apply=False):
 root=pathlib.Path(root).resolve();origin=root/'ressources_pilotes_originaux'/'kristals'
 result={'deja_presents':0,'a_installer':0,'installes':0}
 for source in sorted(origin.glob('qc-pri-*/*/*')):
  if not source.is_file():continue
  kid=source.relative_to(origin).parts[0]
  if source.is_symlink():raise ValueError('Lien symbolique source interdit')
  target=root/'kristals'/source.relative_to(origin)
  if target.is_symlink():raise ValueError('Lien cible interdit')
  if target.exists():result['deja_presents']+=1;continue
  result['a_installer']+=1
  if apply:
   target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,target);result['installes']+=1
 print(('APPLICATION' if apply else 'SIMULATION'),result)
 return result
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--root',type=pathlib.Path,default=ROOT);p.add_argument('--apply',action='store_true')
 a=p.parse_args();restore(a.root,a.apply)
