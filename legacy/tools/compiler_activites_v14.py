#!/usr/bin/env python3
"""Ekole v14: compile per-Kristal tool references into public, answer-free mappings and private QA coverage.
This is a structural check, not a pedagogic or cultural approval.
"""
from __future__ import annotations
import argparse, json, pathlib, collections
ROOT=pathlib.Path(__file__).resolve().parents[1]

def jread(p):return json.loads(p.read_text(encoding='utf-8'))
def put(p,data):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def proposal(c):
 """Editor-only work queue, never used to publish an automatically selected lab."""
 text=(c['title']+' '+c['objective']).lower();subject=c['subject']
 if subject=='Mathématique':
  rules=[(('fraction','dénominateur'),['fraction','equivalence']), (('diagramme','donnée','tableau'),['diagramme','classer']), (('durée','horaire','temps'),['duree']), (('géométr','figure','symétrie','angle'),['grille','classer']), (('nombre','calcul','addition','soustraction','multiplic','division'),['probleme','position','jetons'])]
  for keys,engines in rules:
   if any(k in text for k in keys):return engines,'Formaliser les relations mathématiques et les erreurs diagnostiques avant de publier.'
  return ['probleme'],'Définir la manipulation et sa preuve distincte du résultat.'
 if 'Français' in subject or 'Anglais' in subject or 'Intégration linguistique' in subject:
  return ['ordonner','associer'],'Vérifier le sens et la langue; ne pas réduire la lecture ou la production à un choix.'
 if 'Science' in subject:
  return ['classer','ordonner','grille'],'Distinguer observation, interprétation et expérimentation; vérifier les sources.'
 if 'Géographie' in subject:return ['grille','ordonner','associer'],'Conserver le contexte des sources, des lieux et des époques; revue historique nécessaire.'
 if any(x in subject for x in ('Art ','Arts ','Danse','Musique','Éducation physique')):
  return [],'Observation humaine requise pour les compétences expressives et motrices.'
 return ['associer','classer'],'Valider les significations et les perspectives; ne pas scorer une opinion.'

def compile(root,write=True):
 root=pathlib.Path(root).resolve();student=jread(root/'site/eleve/data/eleves/catalogue.json');labs=jread(root/'site/eleve/labo/data/catalogue.json');courses=student['courses'];items=labs['items']
 if len(courses)!=202 or len({x['id'] for x in courses})!=202:raise ValueError('202 courses required')
 if len(items)!=len({x['id'] for x in items}):raise ValueError('duplicate exercise identifiers')
 bylab={x['id']:x for x in items};associations={};public={};diagnostics=[]
 for c in courses:
  cid=c['id'];original=root/'kristals'/cid/'experience/OUTILS_INTERACTIFS_V14.json';candidate=root/'cours-references'/cid/'OUTILS_INTERACTIFS_V14_CANDIDATS.json'
  src=original if original.is_file() else candidate
  linked=[]
  if src.is_file():
   m=jread(src)
   if m.get('format')!='ekole.kristal-interactions/1.0' or m.get('kristal_id')!=cid or m.get('etat')!='proposition_non_validee':raise ValueError('invalid manifest '+str(src))
   ids=[a['id'] for a in m['activites']]
   if len(ids)!=len(set(ids)):raise ValueError('duplicate references '+cid)
   for ref in m['activites']:
    id=ref['id'];q=bylab.get(id)
    if not q:raise ValueError('missing exercise '+cid+'/'+id)
    if q.get('source_kristal_id')!=cid:raise ValueError('ownership mismatch '+cid+'/'+id)
    if c['year_suggestion'] not in q.get('annees_proposees',[]):raise ValueError('grade mismatch '+cid+'/'+id)
    if not ref.get('competence_ciblee'):raise ValueError('objective missing '+cid+'/'+id)
    linked.append({'id':id,'type':q['type'],'title':q['title'],'competence_ciblee':ref['competence_ciblee'],'statut':'a_valider','annee_proposee':c['year_suggestion']})
  associations[cid]=[x['id'] for x in linked]
  public[cid]=linked
  diagnostics.append({'id':cid,'titre':c['title'],'discipline':c['subject'],'annee_proposee':c['year_suggestion'],'affectation':c['placement_status'],'objectif_source':c['objective'],'moteurs_a_etudier':proposal(c)[0],'prochaine_action':proposal(c)[1],'nombre_activites':len(linked),'types':sorted(set(q['type'] for q in (bylab[x['id']] for x in linked))),'etat':'prototypes_a_revoir' if linked else 'a_concevoir','source_manifest':str(src.relative_to(root)) if src.is_file() else None,'source_kristal':(root/'kristals'/cid/'kristal.workspace.json').is_file()})
 summary={'cours':len(courses),'cours_avec_outil':sum(x['nombre_activites']>0 for x in diagnostics),'cours_sans_outil':sum(x['nombre_activites']==0 for x in diagnostics),'defis_catalogue':len(items),'defis_lies':sum(len(x) for x in associations.values()),'moteurs':len(set(x['type'] for x in items)),'par_annee':{str(y):{'total':sum(x['annee_proposee']==y for x in diagnostics),'avec_outil':sum(x['annee_proposee']==y and x['nombre_activites']>0 for x in diagnostics)} for y in range(1,7)}}
 out={'format':'ekole.activities-references/1.0','etat':'propositions_pedagogiques_non_approuvees','cours':public,'couverture':summary}
 guard={'format':'ekole.activities-access/1.0','cours':associations,'annees_proposees':{c['id']:c['year_suggestion'] for c in courses}}
 report={'format':'ekole.quality-audit/1.0','avertissement':'Validation technique seulement. Aucune habilitation, maîtrise, ni homologation confirmée.','statistiques':summary,'cours':diagnostics}
 if write:
  put(root/'site/eleve/data/activites-v14.json',out)
  put(root/'site/eleve/labo/data/associations-v14.json',guard)
  put(root/'docs/AUDIT_ACTIVITES_202_V14.json',report)
 return report
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--root',default=ROOT);p.add_argument('--check',action='store_true');a=p.parse_args();r=compile(a.root,not a.check);print(json.dumps(r['statistiques'],ensure_ascii=False,indent=2))
