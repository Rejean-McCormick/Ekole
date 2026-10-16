#!/usr/bin/env python3
"""Garde-fous de maturité Ekole. --strict échoue tant que l’école n'est pas revue.
Jamais de publication institutionnelle automatique à partir d'une réponse de MiniLab.
"""
from __future__ import annotations
import argparse, hashlib, json, pathlib, sys
from compiler_mondes_v12 import compile_mondes
ROOT=pathlib.Path(__file__).resolve().parents[1]
REVIEWS=['exactitude','erreurs_diagnostiques','ergonomie_enfant','accessibilite','preuver_maitrise']
def audit(root=ROOT):
 root=pathlib.Path(root).resolve()
 plan=json.loads((root/'docs/PLAN_TRANSFORMATION_202_V12.json').read_text(encoding='utf-8'))
 if len(plan['cours'])!=202 or len({c['kristal_id'] for c in plan['cours']})!=202:raise ValueError('Catalogue de revue incomplet')
 worlds=compile_mondes(root,check=True)
 statuses={};reviews=0;missing=[];divergences=[]
 for row in plan['cours']:
  kid=row['kristal_id'];frame=root/'kristals'/kid/'experience/CADRE_PEDAGOGIQUE_V12.json'
  statuses[row['etat']]=statuses.get(row['etat'],0)+1
  if row['etat']=='source_complete_absente':missing.append(kid);continue
  if not frame.is_file() or frame.is_symlink():raise ValueError('Cadre absent: '+kid)
  d=json.loads(frame.read_text(encoding='utf-8'))
  if d.get('kristal_id')!=kid or d.get('format')!='ekole.kristal-cadre-v12/1.0':raise ValueError('Cadre corrompu: '+kid)
  checks=d.get('revision_humaine',{})
  if set(checks)!=set(REVIEWS) or not all(isinstance(v,bool) for v in checks.values()):raise ValueError('Revue mal formée: '+kid)
  if all(checks.values()):reviews+=1
  original=root/'kristals'/kid/'authoring/CONTRAT_PEDAGOGIQUE.json'
  if original.is_file():
   src=json.loads(original.read_text(encoding='utf-8'))
   if any(d['source'].get(field)!=src.get(field) for field in ('objectif_observable','preuve_attendue','objectif_id')):divergences.append(kid)
 status={'format':'ekole.qualite-v12/1.0','cours_reference':202,'cadres_a_reviser':200,'pilotes_prototypes':worlds['couverts'],'micro_mondes':worlds['count'],'source_manquante':missing,'statuts':statuses,'revisions_criteres_complets':reviews,'divergences_sources':divergences,'publication_institutionnelle_prete':not(missing or divergences or reviews<200),'pret_pour_prototype_local':worlds['count']>=7 and worlds['couverts']==5}
 return status
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--root',default=ROOT);ap.add_argument('--strict',action='store_true',help='échouer si publication institutionnelle non prête');ap.add_argument('--out');a=ap.parse_args()
 report=audit(a.root);s=json.dumps(report,ensure_ascii=False,indent=2);print(s)
 if a.out:pathlib.Path(a.out).write_text(s+'\n',encoding='utf8')
 if a.strict and not report['publication_institutionnelle_prete']:sys.exit(2)
