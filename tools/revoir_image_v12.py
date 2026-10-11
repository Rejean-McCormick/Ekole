#!/usr/bin/env python3
"""Enregistrer explicitement une revue de fichier image manuel avant publication Élève.
N'effectue AUCUNE génération ou transformation d'image.
"""
from __future__ import annotations
import argparse, hashlib, json, pathlib, re
from PIL import Image
ROOT=pathlib.Path(__file__).resolve().parents[1]
def review(root,kid,scenario,*,rights,alt,apply=False):
 root=pathlib.Path(root).resolve()
 if not re.fullmatch(r'qc-pri-[a-z]+-\d{3}',kid) or not re.fullmatch(r'[a-z0-9-]{4,64}',scenario):raise ValueError('Identifiant incorrect')
 if not isinstance(rights,str) or len(rights.strip())<8 or not isinstance(alt,str) or len(alt.strip())<12:raise ValueError('Droits ou texte alternatif insuffisants')
 config=root/'kristals'/kid/'experience/ATELIERS_V12.json'
 if not config.is_file() or config.is_symlink():raise ValueError('Atelier Kristal absent')
 ateliers=json.loads(config.read_text(encoding='utf8'))
 item=next((x for x in ateliers['micro_mondes'] if x['id']==scenario),None)
 if not item:raise ValueError('Scénario absent du Kristal')
 file=root/'kristals'/kid/item['image_path']
 if not file.is_file() or file.is_symlink() or not file.resolve().is_relative_to((root/'kristals'/kid/'experience/images').resolve()):raise ValueError('Image absente / chemin illégal')
 with Image.open(file) as im:
  if im.format not in ('WEBP','PNG','JPEG'):raise ValueError('Format image non autorisé')
  dims=(im.width,im.height)
  if min(dims)<120 or max(dims)>4096:raise ValueError('Dimensions hors limites')
  im.verify()
 digest=hashlib.sha256(file.read_bytes()).hexdigest()
 info={'etat':'approuve_pour_apercu_eleve','sha256':digest,'droits':rights.strip(),'texte_alternatif':alt.strip(),'resolution_px':list(dims),'fichier':item['image_path'],'notes':'Revue explicite du fichier déjà créé manuellement; aucun jugement pédagogique automatique.'}
 dest=root/'kristals'/kid/'experience/REVUE_IMAGES_V12.json'
 if apply:
  if dest.is_symlink():raise ValueError('Revue symbolique')
  registry=json.loads(dest.read_text(encoding='utf8')) if dest.exists() else {}
  registry[scenario]=info
  dest.write_text(json.dumps(registry,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 return {'id':kid,'scenario':scenario,'appliquer':apply,'taille':list(dims),'sha256':digest,'fichier_revue':str(dest)}
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--root',default=ROOT);a.add_argument('--kristal',required=True);a.add_argument('--scenario',required=True);a.add_argument('--droits',required=True);a.add_argument('--alt',required=True);a.add_argument('--apply',action='store_true');v=a.parse_args()
 print(json.dumps(review(v.root,v.kristal,v.scenario,rights=v.droits,alt=v.alt,apply=v.apply),ensure_ascii=False,indent=2))
