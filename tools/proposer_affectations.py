#!/usr/bin/env python3
"""Produire un brouillon de répartition des cours Ekole (jamais une affectation officielle).

Ne lit PAS les vagues de construction et n'écrit jamais les affectations validées.
Aucun accès réseau ni dépendance extérieure.
"""
import argparse
import json
import re
from pathlib import Path
from collections import defaultdict
import heapq

YEARS = range(1, 7)
STAGES = range(1, 5)

# Hypothèses didactiques explicites pour deux disciplines; NON une attribution gouvernementale.
# Fondées sur la progression des notions/relations du catalogue, à faire revoir.
YEAR_ANCHORS = {
    'MA': {1:1,2:1,3:2,4:1,5:3,6:1,7:2,8:3,9:3,10:3,11:4,12:3,13:4,14:5,
           15:4,16:5,17:6,18:3,19:3,20:4,21:1,22:2,23:2,24:4,25:1,26:2,
           27:4,28:5,29:6,30:2,31:3,32:4,33:5},
    'FR': {1:1,2:1,3:1,4:2,5:2,6:3,7:4,8:2,9:3,10:4,11:1,12:2,13:2,14:3,
           15:2,16:3,17:4,18:4,19:2,20:2,21:3,22:4,23:5,24:1,25:2,26:5},
}

def load(path): return json.loads(Path(path).read_text(encoding='utf-8-sig'))
def num_id(value):
 m=re.fullmatch(r'qc-pri-([a-z]+)-(\d{3})',value)
 if not m:raise ValueError(f'ID inconnu: {value}')
 return m.group(1).upper(),int(m.group(2))

def generate(catalog, graph):
 courses=catalog['courses'] if 'courses' in catalog else catalog['kristals']
 ids={c['id'] for c in courses}
 if len(ids)!=len(courses) or len(ids)!=202:raise ValueError('Catalogue incomplet ou IDs en doublon (202 requis)')
 records={c['id']:c for c in courses}
 groups=defaultdict(list)
 for c in courses:
  subject,sequence=num_id(c['id']);groups[subject].append((sequence,c['id']))
 for k in groups:groups[k].sort()
 indegree={i:0 for i in ids};children=defaultdict(list); prerequisites=defaultdict(list)
 for e in graph['relations']:
  if e.get('type')!='requires':continue
  course=e['from'];pre=e['to']
  if course not in ids or pre not in ids:raise ValueError('Préalable hors catalogue')
  children[pre].append(course); prerequisites[course].append(pre);indegree[course]+=1
 queue=[id for id in ids if indegree[id]==0];heapq.heapify(queue);topo=[]
 while queue:
  i=heapq.heappop(queue);topo.append(i)
  for child in sorted(children[i]):
   indegree[child]-=1
   if indegree[child]==0:heapq.heappush(queue,child)
 if len(topo)!=len(ids):raise ValueError('Cycle dans les préalables stricts')
 years={};depth={}
 for subject,ordered in groups.items():
  n=len(ordered)
  for position,(number,id) in enumerate(ordered):
   years[id]=YEAR_ANCHORS.get(subject,{}).get(number,1+(6*position)//n)
 for id in topo:
  preds=prerequisites[id]
  depth[id]=1+max((depth[p] for p in preds),default=-1)
  years[id]=max([years[id]]+[years[p] for p in preds])
  if years[id]>6:raise ValueError(f'Niveau dépasse la 6e pour {id}')
 result={f'annee-{y}-etape-{s}':[] for y in YEARS for s in STAGES}
 by_year=defaultdict(list)
 for id in topo:by_year[years[id]].append(id)
 placed={}; evidence={}
 for year in YEARS:
  course_ids=sorted(by_year[year],key=lambda id:(depth[id],num_id(id)[0],num_id(id)[1]))
  n=len(course_ids)
  for k,id in enumerate(course_ids):
   stage=1+(k*4)//n
   key=f'annee-{year}-etape-{stage}'
   result[key].append(id)
   subject,seq=num_id(id)
   deps=sorted(prerequisites[id])
   anchor=seq in YEAR_ANCHORS.get(subject,{})
   reason=('Hypothèse didactique explicite sur la notion et sa complexité; ' if anchor else
           'Position de la notion dans la séquence interne de sa discipline; ')
   reason+='ordre des préalables stricts vérifié, regroupement en quatre périodes indicatives.'
   placed[id]={'annee':year,'etape':stage,'parcours':key,'statut':'proposition_non_validee',
               'methode':'ancrage_didactique' if anchor else 'ordre_intra_discipline',
               'sources':[f'catalogue/202_kristals.json#{id}','catalogue/graphe_pedagogique.json'],
               'prerequis_requires':deps,'justification':reason,'revue_pedagogique_requise':True}
   evidence[id]=reason
 for id in ids:
  for pre in prerequisites[id]:
   assert (placed[pre]['annee'],placed[pre]['etape']) <= (placed[id]['annee'],placed[id]['etape']),f'Erreur progression {pre} -> {id}'
 assert sum(len(x) for x in result.values())==202
 return {'format':'ekole.parcours-propositions/0.1','statut':'brouillon_non_valide','methode':'ancrages_didactiques_MA_FR_et_ordre_id_puis_requires','condition_de_publication':'revue_humaine_et_approbation_par_etablissement',
         'gouvernance':{'pas_de_conversion_des_vagues':True,'cours_distincts_des_parcours':True,'quatre_etapes_pedagogiques':True,
              'bulletins_officiels_distincts':3,'les_annees_ne_sont_pas_homologuees':True,
              'les_preexistants_sont_prioritaires':True},
         'cours_par_etape':result,'affectations_proposees':dict(sorted(placed.items())),
         'totaux':{'cours_proposes':len(placed),'parcours_etape':24,'par_annee':{str(y):len(by_year[y]) for y in YEARS}},
         'note':'Aperçu de navigation uniquement. Aucune affectation n’est validée ou écrite dans parcours-affectations.json.'}

def main():
 p=argparse.ArgumentParser()
 p.add_argument('--root',default=str(Path(__file__).resolve().parents[1]))
 p.add_argument('--out')
 args=p.parse_args()
 root=Path(args.root)
 catpath=root/'catalogue/202_kristals.json'
 if not catpath.exists():catpath=root/'site/data/index.json'
 graphpath=root/'catalogue/graphe_pedagogique.json'
 if not graphpath.exists():
  raise SystemExit('Graphe pédagogique manquant : ne pas fabriquer un ordre scolaire sans preuve')
 result=generate(load(catpath),load(graphpath))
 path=Path(args.out) if args.out else root/'site/data/parcours-propositions.json'
 path.parent.mkdir(parents=True,exist_ok=True)
 # La cible est un fichier de propositions, jamais la table validée/éditoriale.
 if path.name in ('parcours-affectations.json','niveaux-manuel.json'):
  raise SystemExit('Refus : fichier manuel interdit comme sortie')
 path.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(f"Brouillon de navigation: {len(result['affectations_proposees'])} cours, 24 parcours; fichier={path}")

if __name__=='__main__':main()
