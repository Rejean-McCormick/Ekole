#!/usr/bin/env python3
"""Applique uniquement le plan d'auteur, avec sauvegarde, sans modifier la source du Kristal.
La proposition ne peut jamais acquérir une approbation automatique.
"""
from __future__ import annotations
import argparse, json, pathlib, re, shutil, hashlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
RE=r'^qc-pri-[a-z]+-\d{3}$'
TEXT_KEYS={'situation_de_depart','action_de_lenfant','necessite_de_validation','evaluation','aide_et_regulation','transfert'}
def apply(root,proposal,*,write=False):
 root=pathlib.Path(root).resolve();src=pathlib.Path(proposal).resolve()
 if not src.is_file() or src.is_symlink():raise ValueError('Proposition illisible')
 data=json.loads(src.read_text(encoding='utf8'));kid=data.get('kristal_id','')
 if not re.fullmatch(RE,kid):raise ValueError('Identifiant incorrect')
 target=root/'kristals'/kid/'experience/CADRE_PEDAGOGIQUE_V12.json'
 if not target.is_file() or target.is_symlink():raise ValueError('Cadre introuvable')
 old=json.loads(target.read_text(encoding='utf8'))
 if data.get('source')!=old.get('source'):raise ValueError('La proposition modifie le contrat source; refusée')
 if data.get('format')!=old.get('format') or data.get('famille_candidate')!=old.get('famille_candidate'):raise ValueError('Contrat incompatible')
 draft=data.get('plan_de_conception',{});vision=data.get('visuels_conceptuels',{})
 if set(draft)!=TEXT_KEYS or not all(isinstance(v,str) and 20<=len(v)<=4000 for v in draft.values()):raise ValueError('Champs de conception invalides')
 if set(vision)!=set(old.get('visuels_conceptuels',{})) or vision.get('fichier_suggere')!=old['visuels_conceptuels']['fichier_suggere'] or not isinstance(vision.get('prompt'),str) or not 20<=len(vision['prompt'])<=3000:raise ValueError('Image non conforme')
 changed=(draft!=old['plan_de_conception'] or vision['prompt']!=old['visuels_conceptuels']['prompt'])
 if not changed:return {'id':kid,'changement':False,'ecrit':False}
 if write:
  archive=root/'livraison/sauvegardes_v12';archive.mkdir(parents=True,exist_ok=True)
  old_bytes=target.read_bytes();digest=hashlib.sha256(old_bytes).hexdigest()[:16]
  backup=archive/(kid+'-'+digest+'.json')
  if not backup.exists():backup.write_bytes(old_bytes)
  old['plan_de_conception']=draft;old['visuels_conceptuels']['prompt']=vision['prompt']
  old['etat_revision']='proposition_editee_non_approuvee'
  # La révision humaine et le verdict institutionnel ne proviennent jamais d'un fichier fourni.
  old['revision_humaine']={key:False for key in old['revision_humaine']}
  tmp=target.with_suffix('.tmp');tmp.write_text(json.dumps(old,ensure_ascii=False,indent=2)+'\n',encoding='utf8');tmp.replace(target)
 return {'id':kid,'changement':changed,'ecrit':write}
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--root',default=ROOT);ap.add_argument('--proposal',required=True);ap.add_argument('--apply',action='store_true');a=ap.parse_args();print(json.dumps(apply(a.root,a.proposal,write=a.apply),ensure_ascii=False))
