"""Workflow sans génération opaque: brouillon -> revue manuelle -> publication Élève.
Le dossier expert original reste immuable à travers ce workflow.
"""
from __future__ import annotations
import hashlib
import json
import pathlib
import re
import secrets
from visuals import atomic_json

EXPERT_MARKERS=(
    'sans note certificative', 'réponse et critères', 'préalable interne',
    'acquis équivalent', 'accepté si l’élève', 'critères de réussite enseignant',
    'réponse attendue :', 'barème :',
)

def paths(root,cid):
    return root/'brouillons'/'eleve'/(cid+'.json'),root/'publications'/'eleve'/(cid+'.json')


def draft_read(root,cid,expert):
    draft,published=paths(root,cid)
    if draft.is_symlink() or published.is_symlink():raise ValueError('Document symbolique interdit')
    if draft.is_file():
        raw=draft.read_bytes();data=json.loads(raw)
        data['_revision']=hashlib.sha256(raw).hexdigest()
    elif published.is_file():
        data=json.loads(published.read_text(encoding='utf-8-sig'))
        data['_revision']='new'
    else:
        data={'format':'ekole.student-publication/1','id':cid,'titre':expert.get('titre',cid),
              'statut_publication':'brouillon',
              'notice':'Contenu élève en préparation. Validation pédagogique requise.',
              'modules':[{'id':m['id'],'titre':'À rédiger','texte':''} for m in expert.get('modules',[])]}
        data['_revision']='new'
    data['_draft_exists']=draft.is_file()
    data['_published_exists']=published.is_file()
    return data


def validate(new,expert,complete=False):
    if new.get('id') != expert.get('id') or not isinstance(new.get('modules'),list):raise ValueError('Identifiant de cours incorrect')
    original=expert.get('modules',[])
    if len(new['modules']) != len(original):raise ValueError('Structure des étapes incorrecte')
    for n,(before,after) in enumerate(zip(original,new['modules']),1):
        if not isinstance(after,dict) or after.get('id') != before.get('id'):
            raise ValueError('Identifiant d’étape non modifiable')
        title=after.get('titre');body=after.get('texte')
        if not isinstance(title,str) or not isinstance(body,str) or len(title)>140 or len(body)>13000:
            raise ValueError('Titre ou texte de longueur invalide')
        if complete and (not title.strip() or not body.strip()):
            raise ValueError(f'L’étape {n} n’est pas rédigée')
        if complete:
            combined=(title+'\n'+body).lower()
            if any(term in combined for term in EXPERT_MARKERS):raise ValueError(f'Texte expert potentiellement présent à l’étape {n}. Réviser avant publication.')
            if re.search(r'qc-pri-[a-z]{2}-\d{3}',combined):raise ValueError(f'Identifiant interne présent à l’étape {n}')
    return {'format':'ekole.student-publication/1','id':expert['id'],'titre':expert.get('titre',expert['id']),
            'statut_publication':'pilote_non_valide',
            'notice':'Leçon conçue pour l’élève, à valider par un enseignant avant usage en classe.',
            'modules':[{'id':m['id'],'titre':m['titre'],'texte':m['texte']} for m in new['modules']]}


def draft_save(root,cid,incoming,expert):
    doc,destination=paths(root,cid)
    if doc.is_symlink():raise ValueError('Brouillon symbolique interdit')
    prior=doc.read_bytes() if doc.is_file() else None
    revision=hashlib.sha256(prior).hexdigest() if prior is not None else 'new'
    if incoming.get('_revision')!=revision:raise FileExistsError('Brouillon modifié dans une autre fenêtre. Recharge avant de sauvegarder.')
    data=validate(incoming,expert)
    if prior:
        backup=root/'.ekole-sauvegardes'/'brouillons'/'eleve'/cid
        backup.mkdir(parents=True,exist_ok=True)
        (backup/(secrets.token_hex(8)+'.json')).write_bytes(prior)
    atomic_json(doc,data)
    return {'resultat':'brouillon_sauve','_revision':hashlib.sha256(doc.read_bytes()).hexdigest()}


def publish(root,cid,expert):
    draft,destination=paths(root,cid)
    if draft.is_symlink() or not draft.is_file():raise ValueError('Aucun brouillon à publier')
    incoming=json.loads(draft.read_text(encoding='utf-8'))
    data=validate(incoming,expert,True)
    if destination.is_symlink():raise ValueError('Publication symbolique interdite')
    if destination.is_file():
        backup=root/'.ekole-sauvegardes'/'publications'/'eleve'/cid
        backup.mkdir(parents=True,exist_ok=True)
        (backup/(secrets.token_hex(8)+'.json')).write_bytes(destination.read_bytes())
    atomic_json(destination,data)
    return {'resultat':'publie','etapes':len(data['modules'])}
