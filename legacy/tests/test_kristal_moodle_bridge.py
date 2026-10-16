"""Contrôle hors ligne du pont polymorphe ; pas de serveur Moodle requis."""
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import kristal_moodle_bridge as bridge


class TestKristalMoodleBridge(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.plan = bridge.build_plan(ROOT)

    def test_counts(self):
        summary = self.plan['summary']
        self.assertEqual(summary['kristals'], 202)
        self.assertEqual(summary['items'], 2183)
        self.assertEqual(summary['native_shapes'], {'undecided': 202})
        self.assertEqual(summary['pedagogical_families'], {
            'generee_sous_contraintes': 36, 'observation_ou_production': 93,
            'paramétrique_controle': 33, 'réponse_argumentée': 40,
        })
        self.assertEqual(summary['relations'], {'requires': 134, 'recommends_before': 99, 'reinforces': 19})

    def test_no_forced_course_or_publish(self):
        self.assertTrue(self.plan['dry_run'])
        self.assertFalse(self.plan['write_authorized'])
        self.assertTrue(all(p['moodle_projection']['selected_kind'] is None for p in self.plan['kristal_projections']))
        self.assertTrue(all(p['moodle_projection']['automatic_course_creation'] is False for p in self.plan['kristal_projections']))
        self.assertTrue(all(p['semantic_state']['logical_commitment'] is None for p in self.plan['kristal_projections']))
        self.assertTrue(all(c['candidate_only'] and c['course_format'] is None for c in self.plan['courses']))

    def test_no_assessment_answers_exported(self):
        text = json.dumps(self.plan, ensure_ascii=False)
        self.assertNotIn('reponse_attendue', text)
        self.assertNotIn('\"corrige\":', text)
        self.assertFalse(any(p['moodle_projection']['automatic_quiz_creation'] for p in self.plan['kristal_projections']))
        self.assertTrue(all(not e['automatic_restriction'] and e['moodle_effect'] is None for e in self.plan['relations']))

    def test_shape_is_opaque(self):
        # Polymorphisme : un type natif arbitraire n'est pas ramené à "cours".
        sample = bridge.read_json(ROOT, 'catalogue/202_kristals.json')['kristals'][0]
        orig = bridge.read_json

        def read_custom(root, path):
            value = orig(root, path)
            if path == f"kristals/{sample['id']}/kristal.workspace.json":
                value['native_model']['kind'] = 'experimental-hypergraph/n-ary/2'
            return value

        with mock.patch.object(bridge, 'read_json', side_effect=read_custom):
            projection, course = bridge.make_projection(ROOT, sample, None)
        self.assertEqual(projection['semantic_state']['native_kind'], 'experimental-hypergraph/n-ary/2')
        self.assertIsNone(projection['moodle_projection']['selected_kind'])
        self.assertTrue(course['candidate_only'])

    def test_bindings_explicit_review_and_no_writes(self):
        kid = self.plan['kristal_projections'][0]['kristal_id']
        with tempfile.TemporaryDirectory() as t:
            p = Path(t) / 'bindings.json'
            def write(choice):
                p.write_text(json.dumps({'format': 'ekole.moodle-bindings/1.0', 'bindings': {kid: choice}}), encoding='utf8')
            write({'projection_kind': 'course', 'moodle_course_id': 251, 'moodle_category_id': 10,
                   'reviewed_by': 'operator-for-test', 'approval_ref': 'test-ticket'})
            selection = bridge.read_bindings(ROOT, p, {kid})
            self.assertEqual(selection[kid][0]['moodle_course_id'], 251)
            with self.assertRaises(bridge.AlignmentError):
                write({'projection_kind': 'course', 'moodle_course_id': 251, 'moodle_category_id': 10})
                bridge.read_bindings(ROOT, p, {kid})
            with self.assertRaises(bridge.AlignmentError):
                write({'projection_kind': 'course', 'moodle_course_id': 251, 'moodle_category_id': 10,
                       'reviewed_by': 'tester', 'approval_ref': 'test', 'write_authorized': True})
                bridge.read_bindings(ROOT, p, {kid})

    def test_multiple_projections_from_single_kristal(self):
        kid = self.plan['kristal_projections'][0]['kristal_id']
        with tempfile.TemporaryDirectory() as t:
            path = Path(t) / 'bindings.json'
            path.write_text(json.dumps({'format': 'ekole.moodle-bindings/1.0', 'bindings': {
                kid: [
                    {'projection_kind': 'resource', 'moodle_course_id': 91,
                     'reviewed_by': 'operator-for-test', 'approval_ref': 'test-a'},
                    {'projection_kind': 'activity', 'moodle_course_id': 92,
                     'reviewed_by': 'operator-for-test', 'approval_ref': 'test-b'},
                ]
            }}), encoding='utf8')
            selections = bridge.read_bindings(ROOT, path, {kid})[kid]
            sample = bridge.read_json(ROOT, 'catalogue/202_kristals.json')['kristals'][0]
            projection, legacy = bridge.make_projection(ROOT, sample, selections)
            self.assertEqual(len(projection['moodle_projection']['selected_projections']), 2)
            self.assertIsNone(projection['moodle_projection']['selected_kind'])
            self.assertIsNone(legacy['moodle_course_id'])
            self.assertFalse(legacy['write_authorized'])

    def test_no_unknown_kristal_bindings(self):
        with tempfile.TemporaryDirectory() as t:
            p = Path(t) / 'bindings.json'
            p.write_text(json.dumps({'format': 'ekole.moodle-bindings/1.0', 'bindings': {
                'unknown': {'projection_kind': 'none'}
            }}), encoding='utf-8')
            with self.assertRaises(bridge.AlignmentError):
                bridge.read_bindings(ROOT, p, {'qc-pri-ad-001'})


if __name__ == '__main__':
    unittest.main()
