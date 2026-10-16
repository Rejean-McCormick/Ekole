#!/usr/bin/env python3
"""Projection publique *filtrée* des séquences Ekole v11.
Ne lit pas de corrigés et ne copie jamais les notes réservées à l'enseignant.
"""
from __future__ import annotations
import argparse,json,pathlib,re
ROOT=pathlib.Path(__file__).resolve().parents[1]
ID=re.compile(r'^qc-pri-[a-z]+-\d{3}$')
KEYS=('decouvrir','essayer','expliquer','explorer')
FMT='ekole.kristal-experience/2.0-proposition'

def compile_experiences(root):
 root=pathlib.Path(root).resolve()
 cat=json.loads((root/'site/eleve/data/eleves/catalogue.json').read_text(encoding='utf8'))
 labs=json.loads((root/'site/eleve/labo/data/catalogue.json').read_text(encoding='utf8'))
 scenarios={c['id']:c for c in labs['items']}
 output={};missing=[]
 for item in cat['courses']:
  kid=item['id']
  if not ID.fullmatch(kid):raise ValueError('ID de cours invalide')
  path=root/'kristals'/kid/'experience/SCENARIO_APPRENTISSAGE.json'
  if not path.exists():missing.append(kid);continue
  if path.is_symlink():raise ValueError('Manifest lien symbolique')
  src=json.loads(path.read_text(encoding='utf8'))
  if src.get('format')!=FMT or src.get('kristal_id')!=kid or src.get('statut')!='prototype_revue_pedagogique_requise':
   raise ValueError('Scénario v11 incompatible : '+kid)
  phases=src['progression_enfant']
  if set(phases)!=set(KEYS):raise ValueError('Phases manquantes '+kid)
  public_phases={}
  for k in KEYS:
   phase=phases[k]
   for field in ('titre_enfant','consigne_enfant','statut_validation'):
    if not isinstance(phase.get(field),str) or len(phase[field])<8:raise ValueError('Champ manquant '+kid+'/'+k+'/'+field)
   public_phases[k]={f:phase[f] for f in ('titre_enfant','consigne_enfant','statut_validation')}
  uses=[]
  for x in src.get('outils_interactifs',[]):
   tool=x['id'];lab=scenarios.get(tool)
   if not lab or lab.get('source_kristal_id')!=kid:raise ValueError('Lab mal relié : '+kid+'/'+tool)
   if x.get('statut')!='entrainement_candidat_non_certifie':raise ValueError('Lab non certifié mal déclaré')
   uses.append({'id':tool,'titre':lab['title'],'mode':'entrainement_non_certifie'})
  output[kid]={'id':kid,'titre_enfant':src['alias_enfant'],'statut':'prototype_a_valider',
               'phases':public_phases,'outils':uses,'evaluation':'Aucune maîtrise attestée dans Ekole Élève.'}
 if len(cat['courses'])!=202:raise ValueError('Catalogue différent de 202')
 # Ne compiler aucune métadonnée enseignante ni réponse attendue, par construction.
 data={'format':'ekole.experiences-publiques/1.0','references':len(cat['courses']),
       'experiences_pilotes':len(output),'en_attente':len(missing),
       'notice':'Prototypes à réviser; non certificatifs; corrigés exclus.','cours':output}
 dest=root/'site/eleve/data/kristals-experiences.json';dest.parent.mkdir(parents=True,exist_ok=True)
 dest.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 print(f'Ekole expériences : {len(output)} pilotes; {len(missing)} sans séquence v11; aucune correction copiée.')
 return data
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--root',type=pathlib.Path,default=ROOT)
 args=parser.parse_args();compile_experiences(args.root)
