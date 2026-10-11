#!/usr/bin/env python3
"""Compile les micro-mondes depuis les Kristals; whitelist publique; zéro correction source.
Le JSON publié est lisible par l'enfant : jamais l'utiliser pour certifier une maîtrise.
"""
from __future__ import annotations
import argparse, json, pathlib, re, hashlib, shutil
ROOT=pathlib.Path(__file__).resolve().parents[1]
ID=re.compile(r'^qc-pri-[a-z]+-\d{3}$')
TYPES={'representations','repartition','causalite','preuves','expression'}
PUBLIC={'id','kristal_id','type','title','instruction','parameters','evaluation','source_review','premisse','prompt_visuel','image_path','representation'}

def compile_mondes(root=ROOT, *, check=False):
 root=pathlib.Path(root).resolve()
 public=json.loads((root/'site/eleve/data/eleves/catalogue.json').read_text(encoding='utf8'))
 if len(public['courses'])!=202:raise ValueError('202 références requises')
 course_ids={c['id'] for c in public['courses']}
 items=[]; seen=set(); ids=[]
 for kid in sorted(course_ids):
  base=root/'kristals'/kid/'experience/ATELIERS_V12.json'
  if not base.exists():continue
  if base.is_symlink():raise ValueError('Lien symbolique interdit: '+str(base))
  data=json.loads(base.read_text(encoding='utf8'))
  if data.get('format')!='ekole.kristal-atelier-v12/1.0' or data.get('kristal_id')!=kid:raise ValueError('Contrat incompatible: '+kid)
  if data.get('statut')!='prototype_revue_pedagogique_requise':raise ValueError('Statut non vérifié: '+kid)
  src=data.get('source_immutable',{})
  if src.get('file')!='authoring/CONTRAT_PEDAGOGIQUE.json':raise ValueError('Source non vérifiable')
  actual=root/'kristals'/kid/'authoring/CONTRAT_PEDAGOGIQUE.json'
  if actual.is_file():
   contract=json.loads(actual.read_text(encoding='utf8'))
   if any(src.get(key)!=contract.get(key) for key in ('objectif_id','objectif_observable','preuve_attendue')):raise ValueError('Écart par rapport à la source: '+kid)
  else:
   # Overlay cumulatif applicable avant restauration des originaux (v11).
   alternative=root/'ressources_pilotes_originaux/kristals'/kid/'authoring/CONTRAT_PEDAGOGIQUE.json'
   if not alternative.is_file():raise FileNotFoundError('Contrat pilote manquant: '+str(actual))
   contract=json.loads(alternative.read_text(encoding='utf8'))
   if any(src.get(key)!=contract.get(key) for key in ('objectif_id','objectif_observable','preuve_attendue')):raise ValueError('Écart source pilote: '+kid)
  for a in data.get('micro_mondes',[]):
   if a.get('kristal_id')!=kid or a.get('type') not in TYPES or a.get('evaluation')!='entrainement_non_certifiant' or a.get('source_review')!='revue_requise':raise ValueError('Atelier inadmissible: '+kid)
   name=a.get('id','')
   if not re.fullmatch('[a-z0-9-]{4,64}',name) or name in seen:raise ValueError('Atelier dupliqué/invalide: '+name)
   seen.add(name)
   if not all(isinstance(a.get(k),str) and len(a[k])>10 for k in ('title','instruction','prompt_visuel')):raise ValueError('Contenu incomplet: '+name)
   if not re.fullmatch(r'experience/images/[a-z0-9-]+\.(?:webp|png|jpg|jpeg)',a.get('image_path','')):raise ValueError('Fichier visuel dangereux: '+name)
   projected={k:a[k] for k in PUBLIC if k in a}
   # Une image n'est publiée que si sa revue, ses droits et son empreinte concordent.
   image=root/'kristals'/kid/a['image_path']
   review=root/'kristals'/kid/'experience/REVUE_IMAGES_V12.json'
   if image.is_file():
    if image.is_symlink() or not image.resolve().is_relative_to((root/'kristals'/kid/'experience/images').resolve()):
     raise ValueError('Image hors dossier: '+name)
    if review.is_file():
     decisions=json.loads(review.read_text(encoding='utf8'))
     decision=decisions.get(name,{})
     raw=image.read_bytes();digest=hashlib.sha256(raw).hexdigest()
     if decision.get('etat')=='approuve_pour_apercu_eleve' and decision.get('sha256')==digest and decision.get('droits') and len(decision.get('texte_alternatif',''))>=12:
      from PIL import Image
      with Image.open(image) as im:
       im.verify()
      with Image.open(image) as im:
       if im.width<120 or im.height<120 or im.width>4096 or im.height>4096:raise ValueError('Dimensions image non autorisées')
      rel='assets/'+kid+'/'+image.name
      dest=root/'site/eleve/mondes-v12'/rel
      if not check:
       dest.parent.mkdir(parents=True,exist_ok=True)
       shutil.copyfile(image,dest)
      projected['image_url']=rel
      projected['image_alt']=decision['texte_alternatif']
      projected['image_sha256']=digest
   items.append(projected)
  ids.append(kid)
 result={'format':'ekole.micro-mondes-public/1.0','statut':'pratique_exploratoire_pas_certification','couverts':len(ids),'count':len(items),'items':items,'notice':'Aucun résultat n’atteste une maîtrise. Vérification partielle uniquement. Le contenu des solutions d’entraînement est inspectable dans le navigateur.'}
 dest=root/'site/eleve/mondes-v12/data/catalogue.json'
 if not check:
  dest.parent.mkdir(parents=True,exist_ok=True)
  dest.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 return result
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--root',default=ROOT);ap.add_argument('--check',action='store_true');a=ap.parse_args()
 d=compile_mondes(a.root,check=a.check);print('Micro-mondes v12:',d['couverts'],'Kristals pilotes,',d['count'],'scénarios non certifiants')
