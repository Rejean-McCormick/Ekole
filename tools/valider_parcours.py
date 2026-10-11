#!/usr/bin/env python3
"""Contrôles hors ligne de la projection de parcours. Aucun état Kristal/Moodle n'est modifié."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from collections import Counter


def parse(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def validate(school, allocations, old_years=None, course_ids=None):
    """Retourne (erreurs, avertissements). Les données sont des dict JSON."""
    errors=[];warnings=[]
    def error(s): errors.append(s)
    years=school.get('annees',[])
    nums=[a.get('niveau') for a in years]
    if nums != list(range(1,7)): error('Années scolaires attendues : 1, 2, 3, 4, 5, 6 (ordre stable)')
    stages=school.get('etapes',[])
    if [(e.get('numero'),e.get('periode')) for e in stages]!=[(1,'automne'),(2,'automne'),(3,'hiver'),(4,'hiver')]:
        error('Quatre étapes pédagogiques Ekole attendues : 2 automne, 2 hiver')
    if school.get('modele_bulletin_officiel',{}).get('etapes')!=3:
        error('La référence officielle distincte doit conserver trois étapes de bulletin')
    cycles=school.get('cycles',[])
    ids=[c.get('id') for c in cycles]
    if len(set(ids))!=len(ids): error('Cycle ID dupliqué')
    all_years=[]
    for c in cycles:
        y=c.get('annees',[])
        if not isinstance(y,list) or not 2<=len(y)<=3 or len(y)!=len(set(y)):
            error(f'Cycle {c.get("id")}: 2 ou 3 années distinctes requises')
        else:
            if sorted(y)!=list(range(min(y), max(y)+1)):
                error(f'Cycle {c.get("id")}: années non consécutives')
        all_years+=y if isinstance(y,list) else []
    if sorted(all_years)!=list(range(1,7)): error('Tous les niveaux doivent appartenir à exactement un cycle')
    groups=allocations.get('cours_par_etape',{})
    expected={f'annee-{year}-etape-{stage}' for year in range(1,7) for stage in range(1,5)}
    if not isinstance(groups,dict):
        error('cours_par_etape doit être un objet'); groups={}
    if not set(groups).issubset(expected): error('Clés d’affectation inconnues')
    missing=expected-set(groups)
    if missing and all(k.endswith('-etape-4') for k in missing):
        warnings.append('Table v3 détectée (18 étapes) : les six nouvelles étapes 4 sont vides en mémoire; exécuter la migration contrôlée pour enregistrer les 24 clés.')
    elif missing: error('Clés année-étape manquantes autres que les six nouvelles étapes 4')
    course_by_stage={}
    for key,values in groups.items():
        if not isinstance(values,list):
            error(f'{key}: liste attendue');continue
        if len(values)!=len(set(values)):
            error(f'{key}: cours dupliqué')
        for course_id in values:
            if not isinstance(course_id,str) or not course_id.startswith('qc-pri-'):
                error(f'{key}: ID cours invalide')
            elif course_ids is not None and course_id not in course_ids:
                error(f'{key}: cours absent du catalogue : {course_id}')
            course_by_stage.setdefault(course_id,[]).append(key)
    proofs=allocations.get('preuves_attribution',{})
    if not isinstance(proofs,dict): error('preuves_attribution doit être un objet');proofs={}
    for id,keys in course_by_stage.items():
        if not isinstance(proofs.get(id),str) or not proofs[id].strip():
            error(f'{id}: affectation à une étape sans justification')
    if old_years is not None:
        levels=old_years.get('levels_by_course',{})
        if not isinstance(levels,dict): error('levels_by_course doit être un objet');levels={}
        for id,year in levels.items():
            if str(year) not in ('1','2','3','4','5','6'):
                error(f'Ancien niveau invalide : {id}')
                continue
            if course_ids is not None and id not in course_ids:
                error(f'Ancien ID cours inconnu : {id}')
            placed={int(x.split('-')[1]) for x in course_by_stage.get(id,[])}
            if placed and int(year) not in placed:
                warnings.append(f'{id}: année héritée différente des étapes affectées, revue nécessaire')
    if not any(groups.get(key,[]) for key in expected):
        warnings.append('Aucun cours n’est actuellement affecté à une étape : les 24 parcours sont des contenants à remplir.')
    return errors,warnings


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--root',default=str(Path(__file__).resolve().parents[1]))
    a=p.parse_args()
    root=Path(a.root)
    school=parse(root/'site/data/organisation-parcours.json')
    membership=parse(root/'site/data/parcours-affectations.json') if (root/'site/data/parcours-affectations.json').exists() else parse(root/'site/data/parcours-affectations.4-etapes.exemple.json')
    oldpath=root/'site/data/niveaux-manuel.json'
    old=parse(oldpath) if oldpath.exists() else None
    cat=root/'site/data/index.json'
    ids={r['id'] for r in parse(cat)['courses']} if cat.exists() else None
    errors,warnings=validate(school,membership,old,ids)
    print(json.dumps({'result':'PASS' if not errors else 'FAIL','cycles':len(school['cycles']),
            'annees':len(school['annees']),'etapes_par_annee':len(school['etapes']),
            'parcours_etape':len(membership['cours_par_etape']),
            'cours_catalogue':len(ids) if ids is not None else None,
            'bulletins_officiels':school.get('modele_bulletin_officiel',{}).get('etapes'),
            'erreurs':errors,'avertissements':warnings},ensure_ascii=False,indent=2))
    raise SystemExit(1 if errors else 0)
if __name__=='__main__':main()
