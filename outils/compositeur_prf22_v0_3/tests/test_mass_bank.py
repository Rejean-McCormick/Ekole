from pathlib import Path
import json
import os
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'app'))
import bank_mass
from prf22_validator import validate_document

class BankTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root=ROOT.parents[1]/'banques'/'prf22'/'candidats-v0_4'
        cls.manifest=json.loads((cls.root/'MANIFEST.json').read_text(encoding='utf-8'))
        cls.entries=cls.manifest['entries']

    def test_137_propositions_77_sources(self):
        self.assertEqual(len(self.entries),137)
        self.assertEqual(len({e['source_ref'] for e in self.entries}),77)
        self.assertEqual(self.manifest['source_situations_covered'],77)

    def test_distinct_and_unqualified(self):
        self.assertEqual(len({e['id'] for e in self.entries}),137)
        self.assertEqual(len({e['folder'] for e in self.entries}),137)
        self.assertEqual(self.manifest['status'],'candidates_non_qualifies')

    def test_410_plus_plans_exist(self):
        for e in self.entries:
            for n in (1,8,30):
                self.assertTrue((self.root/e['folder']/f'plan-{n:02d}.json').is_file())

    def test_no_sensitive_micro_auto_selected(self):
        for e in self.entries:
            for a in e['activity_refs']:
                if a.startswith('micro:'):
                    self.assertNotIn(int(a.rsplit('-',1)[-1]),bank_mass.EXCLUDED_MICROS)

    def test_als_vs_fr_mapping(self):
        self.assertEqual(bank_mass.MICRO_TO_OBJECTIVE[4],'qc-pri-als-007')

    def test_blueprints_all_valid(self):
        for e in self.entries:
            d=json.loads((self.root/e['folder']/'design.json').read_text(encoding='utf-8'))
            errors,_=validate_document(d)
            self.assertFalse(errors,(e['folder'],errors[:2]))
            self.assertFalse(d['governance']['activation_authorized'])
            self.assertFalse(d['governance']['publication_authorized'])
            self.assertFalse(d['governance']['student_data_included'])

    def test_plan_capacity_and_coverage(self):
        for e in self.entries:
            for n in (1,8,30):
                p=json.loads((self.root/e['folder']/f'plan-{n:02d}.json').read_text(encoding='utf-8'))
                part=p['participation'];teams=part['teams'];rounds=part['rotation']
                self.assertEqual(sum(t['size'] for t in teams),n)
                self.assertTrue(part['anonymized_placeholder_only'])
                self.assertEqual(part['role_validation'],'teacher_required')
                visited={(a['team_id'],a['station_id']) for r in rounds for a in r['assignments'] if a['station_id']}
                self.assertEqual(len(visited),len(teams)*len(part['stations']))
                for r in rounds:
                    used=[]
                    for a in r['assignments']:
                        if a['post_id']: used.append(a['post_id'])
                    self.assertEqual(len(used),len(set(used)))

    def test_handoff_explicitly_unadmitted(self):
        for e in self.entries:
            h=json.loads((self.root/e['folder']/'handoff.json').read_text(encoding='utf-8'))
            self.assertFalse(h['session_admitted'])
            self.assertFalse(h['permissions_granted'])
            self.assertFalse(h['konnaxion_project_created'])
            self.assertFalse(h['orgo_world_created'])

    def test_verify_with_source_and_tamper(self):
        # Verification of built-in bank with original snapshot is done separately;
        # here an integrity violation must be detected even if source hashes match.
        with tempfile.TemporaryDirectory() as td:
            tmp=Path(td)
            src=tmp/'sources';src.mkdir()
            # Rebuild minimal source tree directly from the included catalogue zip.
            import zipfile
            with zipfile.ZipFile(ROOT/'tests'/'fixture_kontexte.zip') as z:z.extractall(src)
            out=tmp/'bank'
            bank_mass.generate(src,out,limit=1)
            self.assertEqual(bank_mass.generate(src,out,verify_only=True)['verified'],1)
            with self.assertRaises(FileExistsError):bank_mass.generate(src,out,limit=1)
            doc=next(out.glob('situations/*/design.json'))
            doc.write_text(doc.read_text(encoding='utf-8')+' ',encoding='utf-8')
            with self.assertRaises(ValueError):bank_mass.generate(src,out,verify_only=True)

    def test_observed_hashes_but_no_pins(self):
        for e in self.entries[:25]:
            h=json.loads((self.root/e['folder']/'handoff.json').read_text(encoding='utf-8'))
            self.assertTrue(h['source_observations'])
            self.assertTrue(all(x['pin_status']=='unresolved' for x in h['source_observations']))

if __name__=='__main__':unittest.main()
