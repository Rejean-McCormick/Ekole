#!/usr/bin/env python3
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[1]
def j(p):return json.loads((ROOT/p).read_text(encoding='utf-8'))
def main():
 model=j('kristals/modele-organisation-humaine/canon/domain/modele.json')
 canon=j('modules/qc-pri-us-009/canon/domain/societes-rencontres-v1.json')
 cat=j('modules/qc-pri-us-009/sources/source-catalog.additions.json')
 qs=j('modules/qc-pri-us-009/experience/histoire-rencontres/EXERCICES_SEMANTIQUES.json')
 vis=j('modules/qc-pri-us-009/experience/histoire-rencontres/RESSOURCES_VISUELLES.json')
 ids=lambda arr:[x['id'] for x in arr]
 sources=set(ids(cat['sources']));claims={x['id']:x for x in canon['assertions']}
 assert len(sources)==len(cat['sources']) and len(claims)==len(canon['assertions'])
 periods=set(ids(canon['periodes']))
 for f in claims.values():
  assert f['source_ids'] and set(f['source_ids'])<=sources, f['id']
  assert f['periode_ref'] in periods
  assert f['limites'] and f['statut']
 for ex in qs['exercices']:
  ids_=ex.get('fact_ids') or [ex.get('fact_id')]
  assert ids_ and set(ids_)<=set(claims), ex['id']
  assert ex['prerequis'] is not None and ex.get('explication_courte') and ex.get('explication_longue')
  if ex['mode'] in ('choix','cloze'):
   assert sum(1 for v in ex['options'] if v['ref']==ex['reponse_ref'])==1
   # absence de source ne fabrique aucune réponse négative: les distracteurs sont éditorialement explicites.
   assert len(ex['options'])>=2
  elif ex['mode']=='associer':assert len(ex['pairs'])>1
  elif ex['mode']=='ordonner': assert len(ex['elements'])>1
  else: assert ex['mode']=='humain' and ex['criteres_observables']
 for v in vis['images']:
  assert v['concept_prompt'] and v['expected_path'].endswith('.webp') and v['statut']=='description_sans_image'
  assert 'style' not in v['concept_prompt'].lower() # no style directive
 assert not list((ROOT/'site/eleve/ateliers/rencontres-quebec/assets').glob('*.webp')) if (ROOT/'site/eleve/ateliers/rencontres-quebec/assets').exists() else True
 print('OK',len(claims),'faits sourcés,',len(qs['exercices']),'activités,',len(vis['images']),'prompts conceptuels; 0 image générée')
if __name__=='__main__':main()
