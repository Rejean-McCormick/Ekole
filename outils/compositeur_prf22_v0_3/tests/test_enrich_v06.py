from __future__ import annotations
import json, pathlib, sys, tempfile, unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
REPO=ROOT.parents[1]
sys.path.insert(0,str(ROOT/'app'))
from composer_core import load_catalogue
from bank_enrich import load_patterns, generate, verify, LIBRARY
from prf22_validator import validate_document

class EnrichTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ekole=pathlib.Path(__file__).resolve().parents[3]
        cls.bank=cls.ekole/'banques/prf22/candidats-v0_6'
        cls.context=pathlib.Path('/mnt/data/work_prf22_v06/kontexte')
        # May be absent on Windows test runners; discover sibling Kontexte.
        if not cls.context.exists():cls.context=cls.ekole.parent/'Kontexte'

    def test_pattern_library_identifies_owner_and_real_references(self):
        catalog=load_catalogue(self.context);patterns=load_patterns(catalog)
        self.assertEqual(len(patterns),51)
        self.assertEqual(len({x['ref'] for x in patterns}),51)
        self.assertTrue(all(x['owner']=='Ékole' and x['objectif_ref'] in {o['ref'] for o in catalog.objectives} for x in patterns))

    def test_enriched_bank_is_distinct_and_unapproved(self):
        m=json.loads((self.bank/'MANIFEST.json').read_text(encoding='utf-8'))
        self.assertEqual(m['entries_count'],137);self.assertEqual(m['source_situations_covered'],77)
        self.assertGreater(m['objectives_used'],25)
        self.assertGreater(m['activities_used'],49)
        self.assertEqual(m['status'],'candidates_non_qualifies')
        self.assertGreater(m['proposed_activities_used'],45)

    def test_proposed_sources_are_never_claimed_as_kontexte(self):
        m=json.loads((self.bank/'MANIFEST.json').read_text(encoding='utf-8'))
        for rec in m['entries']:
            d=json.loads((self.bank/rec['folder']/'design.json').read_text(encoding='utf-8'))
            lookup={x['exercise_ref']['resource_id']:x['exercise_ref']['owner'] for x in d['activities']}
            self.assertTrue(all(lookup[ref]=='Ékole' for ref in rec['proposed_activity_refs']))
            self.assertFalse(d['governance']['activation_authorized'])
            self.assertFalse(d['governance']['publication_authorized'])
            self.assertFalse(d['governance']['student_data_included'])
            self.assertFalse(validate_document(d)[0])

    def test_generation_and_source_integrity(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=pathlib.Path(tmp)/'newbank'
            report=generate(self.context,root,limit=2)
            self.assertEqual(report['propositions'],2)
            result=verify(root,self.context)
            self.assertEqual(result['propositions_verifiees'],2)
            file=next((root/'situations').rglob('plan-01.json'))
            contents=file.read_bytes()
            try:
                file.write_bytes(b'{"corrupted":true}')
                with self.assertRaisesRegex(ValueError,'Empreinte'):verify(root,self.context)
            finally:file.write_bytes(contents)

if __name__=='__main__':unittest.main()
