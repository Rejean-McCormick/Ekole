"""Validateur de brouillon PRF-22 v0.3, sans accès au runtime, sans données d'élèves.

Ce validateur vérifie la cohérence *déclarée*, jamais la validité pédagogique réelle.
Avec jsonschema installé, il vérifie aussi la structure JSON Schema 2020-12.
"""
from __future__ import annotations
import argparse
import json
import pathlib
import re
import sys

SCHEMA_PATH=pathlib.Path(__file__).with_name('situation-orchestrable.design.v0.3.schema.json')


def duplicates(values):
    seen=set(); dup=set()
    for value in values:
        if value in seen:dup.add(value)
        seen.add(value)
    return sorted(dup)


def semantic_errors(d):
    """List errors for a structurally conforming draft (no side effects)."""
    err=[]
    def check(test,msg):
        if not test:err.append(msg)
    try:
        check(d.get('format')=='ekole.situation-orchestrable.design/0.3','format: attendu PRF-22 v0.3')
        p=d['pedagogical_model']; activities=d['activities']; objectives=d['learning']['objectives']; org=d['organization']
        context=d['context']
        check(isinstance(context.get('language'),str) and len(context.get('language',''))>=2,'context.language manquant')
        check(isinstance(context.get('cultural_frame'),str) and len(context.get('cultural_frame',''))>=2,'context.cultural_frame manquant')
        check(isinstance(context.get('source_situation'),dict),'context.source_situation manquant')
        theory=p['theory_refs']; conditions=p['objective_conditions']; did=p['activity_didactics']; conjectures=p['conjectures']; evidences=p['evidence_design']; alignments=p['alignment']; contract=p['adaptation_contract']
        obj_ids={o['id'] for o in objectives}; act_ids={a['id'] for a in activities}; role_ids={r['id'] for r in d['roles']}; theory_ids={t['id'] for t in theory}; evidence_ids={e['id'] for e in evidences}
        for label,items in [('objectifs',objectives),('activités',activities),('rôles',d['roles']),('théories',theory),('conditions',conditions),('didactiques',did),('conjectures',conjectures),('preuves',evidences),('alignements',alignments)]:
            ids=[x.get('id',x.get('objective_id',x.get('activity_id'))) for x in items]
            check(not duplicates(ids),f'{label}: identifiants dupliqués: {duplicates(ids)}')
        check({c['objective_id'] for c in conditions}==obj_ids,'objective_conditions: couverture incomplète ou références inconnues')
        check({a['activity_id'] for a in did}==act_ids,'activity_didactics: couverture incomplète ou références inconnues')
        for a in activities:
            check(set(a['objectives']) <= obj_ids, f"activité {a['id']}: objectifs inconnus")
            check(set(a['role_ids']) <= role_ids, f"activité {a['id']}: rôles inconnus")
        # Graphe de dépendances: références, cycles, boucles directes.
        graph={x:set() for x in act_ids}
        for dep in d['dependencies']:
            before,after=dep['before'],dep['after']
            check(before in act_ids and after in act_ids,f'dépendance inconnue: {before} -> {after}')
            check(before!=after,f'boucle directe: {before}')
            if before in graph and after in graph:graph[before].add(after)
        visiting=set(); visited=set();cycle=False
        def visit(n):
            nonlocal cycle
            if n in visiting:cycle=True; return
            if n in visited:return
            visiting.add(n)
            for m in graph[n]:visit(m)
            visiting.remove(n); visited.add(n)
        for n in graph:visit(n)
        check(not cycle,'dépendances: cycle détecté')
        evidence_by_id={e['id']:e for e in evidences}
        for e in evidences:
            check(set(e['produced_by_activity_ids']) <= act_ids,f"preuve {e['id']}: activités inconnues")
        proc_ids=set()
        for c in conjectures:
            check(len(c.get('conjecture_statement','').strip())>=15, f"conjecture {c.get('id','?')}: énoncé manquant")
            check(set(c['theoretical_basis_ids']) <= theory_ids,f"conjecture {c['id']}: référence théorique inconnue")
            check(set(c['design_activity_ids']) <= act_ids,f"conjecture {c['id']}: activités inconnues")
            check(set(c['intended_objective_ids']) <= obj_ids,f"conjecture {c['id']}: objectifs inconnus")
            for proc in c['mediating_processes']:
                check(proc['id'] not in proc_ids,f"processus dupliqué: {proc['id']}")
                proc_ids.add(proc['id'])
        condition_by_obj={c['objective_id']:c for c in conditions}
        aligned_objectives=set()
        for row in alignments:
            name=row['id']; oid=row['objective_id']; aligned_objectives.add(oid)
            check(oid in obj_ids,f'alignement {name}: objectif inconnu')
            check(set(row['activity_ids']) <= act_ids,f'alignement {name}: activités inconnues')
            check(set(row['process_ids']) <= proc_ids,f'alignement {name}: processus inconnus')
            check(row['evidence_id'] in evidence_ids,f'alignement {name}: preuve inconnue')
            if row['evidence_id'] in evidence_by_id:
                check(bool(set(row['activity_ids']) & set(evidence_by_id[row['evidence_id']]['produced_by_activity_ids'])),f'alignement {name}: preuve non produite par les activités liées')
            if oid in condition_by_obj and condition_by_obj[oid]['assessment_requires']=='peer_interaction':
                check('solo' not in row['assessed_modes'],f'alignement {name}: compétence de pairs évaluée en solo')
            acts_supporting_obj={a['id'] for a in activities if oid in a['objectives']}
            check(bool(set(row['activity_ids']) & acts_supporting_obj),f'alignement {name}: activités ne portent pas cet objectif')
        check(aligned_objectives==obj_ids,f'alignement: objectifs non couverts ou inconnus: {sorted(obj_ids-aligned_objectives)}')
        check(not duplicates([v['learners'] for v in contract['variants']]),'variantes: effectifs dupliqués')
        counts={v['learners'] for v in contract['variants']}
        check({1,8,30} <= counts,'variantes: témoins solo, 8 et 30 obligatoires')
        check({a['learners'] for a in org['adaptations']} <= counts,'variantes: adaptations du plan v0.1 sans contrat correspondant')
        for v in contract['variants']:
            n=v['learners']; mode=v['mode']; preserved=set(v['preserved_objective_ids']); excluded=set(v['non_assessable_objective_ids']);
            check(mode==('solo' if n==1 else 'collaborative'),f'variante {n}: mode incohérent avec effectif')
            check(not(preserved & excluded) and (preserved|excluded)==obj_ids,f'variante {n}: classification incomplète ou contradictoire des objectifs')
            for oid in preserved:
                support=any(r['objective_id']==oid and mode in r['assessed_modes'] for r in alignments)
                check(support,f'variante {n}: objectif {oid} conservé mais non évaluable dans le mode {mode}')
                if n==1 and condition_by_obj.get(oid,{}).get('assessment_requires')=='peer_interaction':
                    check(False,f'variante solo: collaboration entre pairs déclarée préservée ({oid})')
            if n==1:
                for oid,c in condition_by_obj.items():
                    if c['assessment_requires']=='peer_interaction':
                        check(oid in excluded,f'variante solo: compétence nécessitant des pairs non exclue ({oid})')
        check(not d['governance']['publication_authorized'] and not d['governance']['activation_authorized'] and not d['governance']['student_data_included'],'gouvernance: autorité ou données élèves non permises')
        check(d['status']=='design_only' and p['research_plan']['claims_status']=='untested','statut: le brouillon ne peut prétendre à une qualification')
        # Engagement plausible ≠ provenance garantie. Valider syntaxe seulement.
        refs=[c['reference'] for c in objectives]+[a['exercise_ref'] for a in activities]+d['context']['culture_refs']+[d['context']['source_situation']]
        check(all(r['pin_status']=='unresolved' for r in refs),'référence épinglée : qualification et provenance ne peuvent être attribuées par le compositeur')
        for r in refs:
            if r.get('pin_status')=='pinned':
                check(bool(re.fullmatch(r'sha256:[0-9a-f]{64}',r.get('commitment',''))),f"référence {r['resource_id']}: empreinte épinglée mal formée")
    except (KeyError,TypeError,ValueError) as e:
        err.append(f'forme incorrecte empêchant la vérification sémantique: {e}')
    return err


def validate_document(document,require_schema=False):
    """Portable contract first, then full Draft202012Validator if installed.

    Return (errors, full_schema_checked). Portable checks cover the bundled v0.3
    keyword set, NOT full JSON Schema 2020-12.
    """
    from prf22_schema_portable import validate_subset
    schema=json.loads(SCHEMA_PATH.read_text(encoding='utf-8'))
    errors=validate_subset(schema,document)
    used_schema=False
    try:
        from jsonschema import Draft202012Validator
    except ImportError:
        if require_schema:errors.append('jsonschema non installé: validation standard complète demandée')
    else:
        Draft202012Validator.check_schema(schema)
        used_schema=True
        for e in sorted(Draft202012Validator(schema).iter_errors(document),key=lambda x:tuple(str(a) for a in x.absolute_path)):
            msg='JSON Schema '+'.'.join(map(str,e.absolute_path))+': '+e.message
            if msg not in errors:errors.append(msg)
    if not errors:errors+=semantic_errors(document)
    return errors,used_schema


def main():
    p=argparse.ArgumentParser(description='Vérifier un brouillon PRF-22 v0.3 sans activation')
    p.add_argument('path',type=pathlib.Path)
    p.add_argument('--require-schema',action='store_true',help='échec si jsonschema absent')
    args=p.parse_args()
    try: doc=json.loads(args.path.read_text(encoding='utf-8'))
    except (OSError,ValueError) as e: print('ERREUR: document illisible:',e); return 2
    errors,checked=validate_document(doc,args.require_schema)
    print('Contrat structurel:', 'JSON Schema 2020-12 validé' if checked else 'vérifié par validateur portable (sous-ensemble; jsonschema non installé)')
    if errors:
        for e in errors:print('ÉCHEC:',e)
        return 1
    print('OK: cohérence déclarative, sans qualification pédagogique ni droit de publication/activation')
    return 0
if __name__=='__main__':sys.exit(main())
