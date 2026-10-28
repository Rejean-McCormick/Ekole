"""Aperçu élève éphémère; réutilise Kompose + Kontexte SANS moteur Orgo.

Aucun compte, indice, preuve, progression ni état serveur n'est créé.
Ce module est chargé uniquement par l'espace élève local Ekole.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

VALID_ID = re.compile(r'[a-z0-9][a-z0-9-]{0,79}\Z')
# Liens éditoriaux EXPLICITES vers les exercices de répétition du Studio.
# Ne pas interpréter ces liens comme validation de parcours ou de maîtrise.
EXERCICES_PILOTES = {
    'boulangerie': 'commande-de-pains',
    'jardin-fermier': 'jardin-saisonnier',
    'expedition': 'parcours-livraison',
}


def _source(engine_root: Path):
    parent = engine_root.resolve().parent
    kontexte, kompose = parent / 'Kontexte', parent / 'Kompose'
    if not (kontexte/'data/missions/boulangerie.json').is_file():
        raise ValueError('Dépôt Kontexte absent à côté du moteur Ekole.')
    if not (kompose/'src/kompose/kontexte_preview.py').is_file():
        raise ValueError('Dépôt Kompose absent à côté du moteur Ekole.')
    return kontexte, kompose


def _json(root: Path, rel: str):
    p = root / rel
    if p.is_symlink() or not p.is_file() or not p.resolve().is_relative_to(root.resolve()) or p.stat().st_size > 250_000:
        raise ValueError('Définition de mission inaccessible.')
    return json.loads(p.read_text(encoding='utf-8-sig'))


def _engines(engine_root: Path):
    kontexte, kompose = _source(engine_root)
    kp = str(kompose/'src'); kx = str(kontexte/'src')
    if kp not in sys.path: sys.path.insert(0,kp)
    if kx not in sys.path: sys.path.insert(0,kx)
    from kompose.kontexte_preview import compile_preview, role_projection
    from kontexte.studio import exercise_check
    return kontexte, compile_preview, role_projection, exercise_check


def _plan(kroot: Path, compile_preview, mission_id: str):
    if not isinstance(mission_id,str) or not VALID_ID.fullmatch(mission_id):
        raise ValueError('Mission inconnue.')
    mission = _json(kroot, f'data/missions/{mission_id}.json')
    if mission.get('id') != mission_id or mission.get('year_suggestion') != 3:
        raise ValueError('Mission non prévue pour cette visite.')
    roles = [_json(kroot, f'data/roles/{rid}.json') for rid in mission['roles']]
    return compile_preview(mission, roles)


def catalogue(engine_root:Path):
    kroot, compiler, _, _ = _engines(engine_root)
    missions = []
    for f in sorted((kroot/'data/missions').glob('*.json')):
        if f.is_symlink() or not VALID_ID.fullmatch(f.stem): continue
        plan = _plan(kroot,compiler,f.stem)
        # Champs liste-blanche uniquement ; rien des fragments ni des plans enseignants.
        missions.append({'id':plan['scenario']['id'],
                         'titre':plan['scenario']['title'],
                         'histoire':plan['scenario']['fiction'],
                         'roles':plan['roles'], 'nombre_etapes':len(plan['steps']),
                         'exercice_disponible':plan['scenario']['id'] in EXERCICES_PILOTES})
    return {'format':'ekole.missions-demo/1','mode':'fiction_local_only',
            'note':'Aperçus pédagogiques non approuvés. Aucun Orgo, compte élève ou multijoueur.',
            'missions':missions}


def role(engine_root:Path,mission_id:str,role_id:str):
    kroot, compiler, role_projection, _ = _engines(engine_root)
    plan = _plan(kroot, compiler, mission_id)
    if not isinstance(role_id,str) or not VALID_ID.fullmatch(role_id): raise ValueError('Rôle inconnu.')
    projected = role_projection(plan,role_id)
    role_raw = _json(kroot,f'data/roles/{role_id}.json')
    if role_raw.get('id') != role_id: raise ValueError('Rôle incohérent.')
    exercise = None
    sid = EXERCICES_PILOTES.get(mission_id)
    if sid:
        doc = _json(kroot, 'data/locales/qc/fr-CA/grade3/exercices-deterministes.json')
        ex = next((x for x in doc['exercices'] if x.get('scenario_id') == sid),None)
        if ex: exercise = {'id':sid,'question':ex['question'],'unite':ex['unit']}
    # Pas d'autres étapes/rôles, fragments, indices, réponses, corrigés ou barèmes.
    return {'format':'ekole.role-demo/1', 'mission_id':mission_id,
            'role_id':projected['role_id'],'nom':projected['role_name'],
            'introduction':role_raw['intro']['fr-CA'],
            'actions':role_raw['actions'][:5],
            'etapes':projected['steps'], 'exercice':exercise,
            'mode':'fiction_local_only','validation_humaine_requise':True}


def verify(engine_root:Path,mission_id:str,exercise_id:str,answer:str):
    if not isinstance(mission_id,str) or EXERCICES_PILOTES.get(mission_id) != exercise_id:
        raise ValueError('Calcul non associé à la mission choisie.')
    if not isinstance(answer,str) or not (1 <= len(answer) <= 80):
        raise ValueError('Entre une réponse courte.')
    kroot, compiler, _, check = _engines(engine_root)
    _plan(kroot,compiler,mission_id)
    doc = _json(kroot, 'data/locales/qc/fr-CA/grade3/exercices-deterministes.json')
    exercises = {x['scenario_id']:x for x in doc['exercices']}
    if exercise_id not in exercises: raise ValueError('Exercice inconnu.')
    result=check({'key':'qc3:'+exercise_id,'answer':answer,'level':'standard'},
                 {'exercises':exercises})
    return {'correct':bool(result['correct']), 'feedback':result['feedback'],
            'statut':'pratique_fictive_sans_note', 'maitrise_validee':False}
