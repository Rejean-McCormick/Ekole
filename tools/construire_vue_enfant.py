#!/usr/bin/env python3
"""Projection de navigation élève; respecte les affectations manuelles."""
import argparse,json,pathlib,re

def load(p,required=True):
 if not p.is_file():
  if required:raise FileNotFoundError(p)
  return None
 return json.loads(p.read_text(encoding='utf-8-sig'))
def assemble(root):
 root=pathlib.Path(root);d=root/'site/data'
 cat=load(d/'index.json');prop=load(d/'parcours-propositions.json');g=load(root/'catalogue/graphe_pedagogique.json')
 approved=load(d/'parcours-affectations.json',False) or {};years=load(d/'niveaux-manuel.json',False) or {}
 courses=cat['courses'];ids={c['id'] for c in courses}
 if len(ids)!=202 or len(courses)!=202 or set(prop['affectations_proposees'])!=ids:raise ValueError('202 cours complets attendus')
 manual={}
 for key,course_ids in approved.get('cours_par_etape',{}).items():
  m=re.fullmatch('annee-([1-6])-etape-([1-4])',key)
  if not m:raise ValueError('Clé manuelle invalide: '+key)
  for cid in course_ids:
   if cid not in ids:raise ValueError('ID manuel absent: '+cid)
   manual.setdefault(cid,(int(m[1]),int(m[2]),'affectation_manuelle'))
 for cid,y in years.get('levels_by_course',{}).items():
  if cid not in ids or not isinstance(y,int) or not 1<=y<=6:raise ValueError('Niveau manuel invalide: '+cid)
  manual.setdefault(cid,(y,0,'annee_manuelle_etape_inconnue'))
 records=[]
 for c in courses:
  cid=c['id'];p=prop['affectations_proposees'][cid]
  m=re.fullmatch('annee-([1-6])-etape-([1-4])',p['parcours'])
  if not m or p['statut']!='proposition_non_validee':raise ValueError('Proposition invalide '+cid)
  y,s,status=manual.get(cid,(int(m[1]),int(m[2]),'proposition_non_validee'))
  records.append({'id':cid,'title':c['titre'],'subject':c['discipline'],'year_suggestion':y,'step_suggestion':s,'objective':c['objectif'],'placement_status':status})
 edges=[{'from':e['from'],'to':e['to'],'type':e['type']} for e in g['relations'] if e['from'] in ids and e['to'] in ids and e['type'] in ('requires','recommends_before','reinforces')]
 return {'format':'ekole.student-navigation/0.1','status':'pedagogical_preview_unreviewed','count':202,'courses':records,'links':edges,'four_stages':{'1':'Étape 1','2':'Étape 2','3':'Étape 3','4':'Étape 4'},'metadata_notice':'Affectations proposées; décisions manuelles prioritaires. Non officiel.'}
def main():
 p=argparse.ArgumentParser();p.add_argument('--root',default='.');a=p.parse_args();root=pathlib.Path(a.root);out=root/'site/data/eleves/catalogue.json'
 data=assemble(root);out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 print('Projection élève:',len(data['courses']),'cours. Résultats non homologués.')
if __name__=='__main__':main()
