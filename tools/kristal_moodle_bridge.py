#!/usr/bin/env python3
"""Pont de projection Kristal -> Moodle, strictement hors ligne / sans écriture Moodle.

Ne cristallise pas de State v9 et ne fabrique pas de publication v10.
Stdlib seulement. Moodle demeure un consommateur de projections, jamais le canon.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SECTIONS = (
    ('Notions et exemples', '01_NOTIONS_ET_EXEMPLES.md'),
    ('Diagnostic', '02_DIAGNOSTIC.md'),
    ('Enseignement guidé', '03_ENSEIGNEMENT_GUIDE.md'),
    ('Pratique accompagnée', '04_PRATIQUE_ACCOMPAGNEE.md'),
    ('Pratique autonome', '05_PRATIQUE_AUTONOME.md'),
    ('Remédiation et transfert', '06_REMEDIATION_ET_TRANSFERT.md'),
)
# Ces types sont des familles pédagogiques observées, NON des formes natives Kristal.
ASSESSMENT_CANDIDATES = {
    'observation_ou_production': ('assign', 'offline_observation', 'manual_rubric'),
    'réponse_argumentée': ('assign', 'qtype_essay', 'manual_rubric'),
    'paramétrique_controle': ('quiz_after_independent_parameter_validation', 'manual_rubric'),
    'generee_sous_contraintes': ('reviewed_fixed_items_only', 'assign', 'manual_rubric'),
}
PROJECTION_KINDS = {'none', 'course', 'resource', 'activity', 'navigation'}
ALLOWED_RELATIONS = {'requires', 'recommends_before', 'reinforces'}


class AlignmentError(ValueError):
    pass


def read_json(root: Path, path: str) -> Any:
    return json.loads((root / path).read_text(encoding='utf-8-sig'))


def fingerprint(root: Path, relative: str) -> dict[str, str]:
    file = (root / relative)
    if not file.is_file():
        raise AlignmentError(f'Fichier source introuvable : {relative}')
    return {'path': relative, 'sha256_file_bytes': hashlib.sha256(file.read_bytes()).hexdigest()}


def read_bindings(root: Path, input_path: str | Path | None, source_ids: set[str]) -> dict[str, list[dict[str, Any]]]:
    """Un même Kristal peut être projeté 0..n fois, vers 0..n cours Moodle.

    Accepte aussi un binding-objet legacy, normalisé en liste à une entrée.
    Les catégories de vues sont des types de projections Moodle, PAS des types Kristal.
    """
    if input_path is None:
        return {}
    path = Path(input_path)
    if not path.is_absolute():
        path = root / path
    data = json.loads(path.read_text(encoding='utf-8-sig'))
    if data.get('format') != 'ekole.moodle-bindings/1.0':
        raise AlignmentError('Format de bindings inattendu')
    bindings = data.get('bindings')
    if not isinstance(bindings, dict):
        raise AlignmentError('bindings doit être un objet indexé par kristal_id')
    unknown = set(bindings) - source_ids
    if unknown:
        raise AlignmentError('Bindings pour Kristals inconnus : ' + ', '.join(sorted(unknown)))
    normalized = {}
    for kid, raw in bindings.items():
        targets = raw if isinstance(raw, list) else [raw]
        if not targets:
            normalized[kid] = []
            continue
        seen = set()
        for b in targets:
            if not isinstance(b, dict) or b.get('projection_kind') not in PROJECTION_KINDS:
                raise AlignmentError(f'{kid}: projection_kind invalide')
            kind = b['projection_kind']
            for name in ('moodle_course_id', 'moodle_category_id'):
                value = b.get(name)
                if value is not None and (isinstance(value, bool) or not isinstance(value, int) or value <= 0):
                    raise AlignmentError(f'{kid}: {name} doit être un entier positif ou null')
            if kind in ('course', 'resource', 'activity') and b.get('moodle_course_id') is None:
                raise AlignmentError(f'{kid}: identification explicite du cours Moodle obligatoire')
            if kind == 'course' and b.get('moodle_category_id') is None:
                raise AlignmentError(f'{kid}: catégorie Moodle explicite obligatoire')
            if kind in ('none', 'navigation') and b.get('moodle_course_id') is not None:
                raise AlignmentError(f'{kid}: cours Moodle non pertinent pour projection {kind}')
            if kind != 'none':
                for field in ('reviewed_by', 'approval_ref'):
                    if not isinstance(b.get(field), str) or not b[field].strip():
                        raise AlignmentError(f'{kid}: {field} requis pour un choix de projection')
            if b.get('write_authorized', False):
                raise AlignmentError(f'{kid}: aucune écriture Moodle autorisable par ce fichier')
            identity = (kind, b.get('moodle_course_id'), b.get('moodle_category_id'))
            if identity in seen:
                raise AlignmentError(f'{kid}: projection dupliquée : {identity}')
            seen.add(identity)
        if len(targets) > 1 and any(b['projection_kind'] == 'none' for b in targets):
            raise AlignmentError(f'{kid}: none ne se combine pas avec une projection active')
        normalized[kid] = targets
    return normalized

def candidate_for_family(family_type: str) -> dict[str, Any]:
    return {
        'pedagogical_family': family_type,
        'moodle_activity_candidates': list(ASSESSMENT_CANDIDATES.get(family_type, ())),
        'mapping_decision': 'human_review_required',
        'automated_question_conversion': False,
        'automated_marking': False,
        'item_publication_allowed': False,
        'reason': 'Les banques et critères nécessitent revue humaine; préserver les preuves et leurs modalités.',
    }


def make_projection(root: Path, r: dict[str, Any], b: list[dict[str, Any]] | None) -> tuple[dict[str, Any], dict[str, Any]]:
    kid = r['id']
    base = f'kristals/{kid}'
    workspace = read_json(root, f'{base}/kristal.workspace.json')
    contract = read_json(root, f'{base}/authoring/CONTRAT_PEDAGOGIQUE.json')
    bank = read_json(root, f'{base}/evaluation/BANQUE_ITEMS.json')
    if workspace.get('slug') != kid or contract.get('kristal_id') != kid or bank.get('kristal_id') != kid:
        raise AlignmentError(f'{kid}: identités source incohérentes')
    if workspace.get('state_ref') is None:
        raise AlignmentError(f'{kid}: state_ref manquant')
    if not isinstance(workspace.get('native_model'), dict):
        raise AlignmentError(f'{kid}: native_model manquant')
    if len(contract.get('familles', [])) == 0:
        raise AlignmentError(f'{kid}: aucune famille pédagogique disponible')
    if len(bank.get('items', [])) != r['nombre_items']:
        raise AlignmentError(f'{kid}: banque != registre (nombre_items)')
    if r['objectif'] != contract.get('objectif_observable') or r['preuve'] != contract.get('preuve_attendue'):
        raise AlignmentError(f'{kid}: contrat et catalogue discordants')
    for _, name in SECTIONS:
        if not (root / base / 'contenu' / name).is_file():
            raise AlignmentError(f'{kid}: contenu manquant : {name}')

    families = []
    for family in contract['familles']:
        typ = family.get('type')
        if not isinstance(typ, str) or not typ:
            raise AlignmentError(f'{kid}: famille sans type')
        fam = candidate_for_family(typ)
        fam['family_id'] = family.get('family_id')
        fam['review_status'] = family.get('review_status', 'unknown')
        families.append(fam)

    # Un type sémantique domain-native demeure opaque et non limité à un enum.
    shape = workspace['native_model']
    targets = b or []
    # Les champs legacy ne peuvent résumer sans ambiguïté qu'une sélection unique.
    binding = targets[0] if len(targets) == 1 else {}
    selected = binding.get('projection_kind')
    paths = [f'{base}/contenu/{name}' for _, name in SECTIONS]
    record = {
        'kristal_id': kid,
        'state_ref': workspace['state_ref'],
        'identity': {'title': workspace.get('title', r['titre']), 'workspace_status': workspace.get('status')},
        'semantic_state': {
            'native_kind': shape.get('kind'),
            'native_canonical_paths': shape.get('canonical_paths', []),
            'logical_commitment': None,
            'state_commitment': None,
            'v9_qualification': 'not_established',
            'v10_publication': 'not_established',
            'does_moodle_own_semantics': False,
        },
        'authoring': {
            'source_contract': fingerprint(root, f'{base}/authoring/CONTRAT_PEDAGOGIQUE.json'),
            'source_item_bank': fingerprint(root, f'{base}/evaluation/BANQUE_ITEMS.json'),
            'source_manifest': fingerprint(root, f'{base}/livraison/MANIFEST.json'),
            'items_count': len(bank['items']),
            'review_status': contract.get('statut', 'unknown'),
            'objective': r['objectif'],
            'expected_evidence': r['preuve'],
            'pedagogical_families': families,
        },
        'moodle_projection': {
            'projection_status': 'reviewed_bindings_not_deployed' if any(t['projection_kind'] != 'none' for t in targets) else ('explicitly_not_projected' if selected == 'none' else 'candidate_unselected'),
            'selected_kind': selected,
            'selected_projections': targets,
            'multiple_views_allowed': True,
            'allowed_candidate_kinds': sorted(PROJECTION_KINDS),
            'mode': 'read_only_dry_run',
            'moodle_course_id': binding.get('moodle_course_id'),
            'moodle_category_id': binding.get('moodle_category_id'),
            'binding_review': {
                'reviewed_by': binding.get('reviewed_by'),
                'approval_ref': binding.get('approval_ref'),
            },
            'source_sections': [{'label': label, 'source_path': path, 'recommended_moodle_resources': ['page', 'book']} for (label, _), path in zip(SECTIONS, paths)],
            'automatic_course_creation': False,
            'automatic_quiz_creation': False,
            'automatic_grade_import': False,
            'automatic_enrollment': False,
            'access_permissions_from_moodle_only': True,
        },
    }
    # Compatibilité documentaire avec tools/ekole.py et tests préexistants :
    # "courses" désigne des CANDIDATS, pas 202 cours à créer.
    course = {
        'source_id': kid, 'state_ref': workspace['state_ref'],
        'moodle_course_id': binding.get('moodle_course_id') if selected == 'course' else None,
        'category_id': binding.get('moodle_category_id') if selected == 'course' else None,
        'name': r['titre'], 'discipline': r['discipline'],
        'course_format': None, 'candidate_only': True,
        'selected_projection_kind': selected,
        'sections': [{'position': i, 'name': label, 'source': path, 'target_resource': 'page_or_book_candidate'}
                     for i, ((label, _), path) in enumerate(zip(SECTIONS, paths), 1)],
        'assessment': {'status': 'human_review_required', 'quiz_created': False, 'question_bank_created': False,
                       'family_types': [f['pedagogical_family'] for f in families],
                       'source_family': r['family_id']},
        'requires': r['prerequis'], 'availability_rule': 'never_autolock_requires_diagnostic_equivalence_policy',
        'write_authorized': False,
    }
    return record, course


def make_relation(e: dict[str, Any], source_ids: set[str]) -> dict[str, Any]:
    if e.get('from') not in source_ids or e.get('to') not in source_ids:
        raise AlignmentError('Relation inconnue : ' + str(e.get('id')))
    kind = e.get('type')
    if kind not in ALLOWED_RELATIONS:
        raise AlignmentError('Type de relation non pris en charge sans revue : ' + str(kind))
    return {
        'relation_id': e.get('id'), 'type': kind, 'from': e['from'], 'to': e['to'],
        'source_validation': e.get('statut_validation'), 'provenance': e.get('provenance'),
        'moodle_effect': None,
        'policy': ('human_review_diagnostic_equivalence_before_availability' if kind == 'requires'
                   else 'advisory_non_blocking' if kind == 'recommends_before' else 'enrichment_non_blocking'),
        'automatic_restriction': False,
    }


def build_plan(root: Path = ROOT, bindings: str | Path | None = None) -> dict[str, Any]:
    root = Path(root).resolve()
    catalogue = read_json(root, 'catalogue/202_kristals.json')
    graph = read_json(root, 'catalogue/graphe_pedagogique.json')
    records = catalogue['kristals']
    source_ids = {r['id'] for r in records}
    if len(source_ids) != len(records) or len(source_ids) != catalogue['count']:
        raise AlignmentError('Catalogue : identités non uniques ou count erroné')
    binding_map = read_bindings(root, bindings, source_ids)
    projections, courses = [], []
    for record in records:
        projection, course = make_projection(root, record, binding_map.get(record['id']))
        projections.append(projection)
        courses.append(course)
    relations = [make_relation(e, source_ids) for e in graph['relations']]
    shapes = Counter(p['semantic_state']['native_kind'] for p in projections)
    family_types = Counter(f['pedagogical_family'] for p in projections for f in p['authoring']['pedagogical_families'])
    relation_types = Counter(e['type'] for e in relations)
    selected = Counter(kind for p in projections for kind in ([t['projection_kind'] for t in p['moodle_projection']['selected_projections']] or ['unselected']))
    return {
        'format': 'ekole.kristal-moodle-projection-plan/1.0',
        'dry_run': True, 'is_deployment': False, 'plugin_owner': 'local_uckk',
        'mapping_status': 'explicit_bindings_only', 'write_authorized': False,
        'semantic_authority': 'Kristal_sources_only', 'operational_authority': 'Moodle_only',
        'source_refs_are_not_v9_commitments': True,
        'source_catalogue_sha256_file_bytes': fingerprint(root, 'catalogue/202_kristals.json')['sha256_file_bytes'],
        'summary': {'kristals': len(projections), 'items': sum(p['authoring']['items_count'] for p in projections),
                    'native_shapes': dict(sorted(shapes.items())), 'pedagogical_families': dict(sorted(family_types.items())),
                    'relations': dict(sorted(relation_types.items())), 'binding_choices': dict(sorted(selected.items())),
                    'requires_human_pedagogical_review': len(projections)},
        'kristal_projections': projections,
        'relations': relations,
        'courses': courses,
        'warning': 'Plan candidat hors ligne. Aucune écriture Moodle, aucune qualification v9/v10, aucune publication de banque de réponses.',
    }


def main() -> int:
    parser = argparse.ArgumentParser(description='Auditer et planifier Kristal -> Moodle sans accès serveur')
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--bindings', type=Path, help='JSON de mapping revu; absent par défaut')
    parser.add_argument('--output', type=Path, default=Path('plans/moodle_projection_dry_run.json'))
    parser.add_argument('--audit-only', action='store_true', help='Imprimer uniquement les compteurs sans écrire de fichier')
    args = parser.parse_args()
    try:
        plan = build_plan(args.root, args.bindings)
        if not args.audit_only:
            path = args.output if args.output.is_absolute() else args.root / args.output
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        print(json.dumps({'result': 'PASS', **plan['summary'], 'dry_run': True,
                          'output': None if args.audit_only else str(path)}, ensure_ascii=False, indent=2))
        return 0
    except (AlignmentError, KeyError, TypeError, ValueError, OSError) as exc:
        print(json.dumps({'result': 'FAIL', 'error': str(exc)}, ensure_ascii=False))
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
