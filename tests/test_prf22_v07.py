"""PRF-22 v0.7 : contenu relié, provenance, intégrité, accès enseignant."""
from __future__ import annotations
import hashlib, json, pathlib, shutil, sys, tempfile, unittest
from unittest import mock

ROOT=pathlib.Path(__file__).resolve().parents[1]
APP=ROOT/'outils/compositeur_prf22_v0_3/app'
sys.path.insert(0,str(APP))
sys.path.insert(0,str(ROOT))
from bank_quality_v07 import generate, verify, load_patterns_v07, matches, source_text, details_source
from composer_core import load_catalogue, attach_ekole_activity_patterns
from prf22_validator import validate_document
import prf22_bridge

BANK=ROOT/'banques/prf22/candidats-v0_7'
KONTEXTE=ROOT.parent/'Kontexte'
if not KONTEXTE.is_dir():KONTEXTE=pathlib.Path('/mnt/data/work_prf22_v06/kontexte')

class BankQualityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest=json.loads((BANK/'MANIFEST.json').read_text(encoding='utf-8'))
        cls.catalog=load_catalogue(KONTEXTE)
        cls.patterns=load_patterns_v07(cls.catalog)

    def test_bank_coverage_and_not_qualified(self):
        m=self.manifest
        self.assertEqual(m['entries_count'],137)
        self.assertEqual(m['source_situations_covered'],77)
        self.assertEqual(m['status'],'candidates_non_qualifies')
        self.assertGreaterEqual(m['activities_used'],75)
        self.assertGreaterEqual(m['objectives_used'],50)
        self.assertEqual(m['weak_links'],0)
        self.assertEqual(len(self.patterns),76)

    def test_sources_and_older_banks_remain_separate(self):
        self.assertTrue((ROOT/'banques/prf22/candidats-v0_6/MANIFEST.json').is_file())
        self.assertTrue((ROOT/'banques/prf22/candidats-v0_4/MANIFEST.json').is_file())
        self.assertTrue((ROOT/'banques/prf22/activites-proposees-v0_6.json').is_file())
        owner={p['ref']:(p['owner'],p['domaine']) for p in self.patterns}
        for rec in self.manifest['entries']:
            for ref in rec['proposed_activity_refs']:
                self.assertEqual(owner[ref],('Ékole',rec['focale']))

    def test_no_irrelevant_french_or_math_filler_in_arts(self):
        for slug in ('trame-fete-commune-arts','trame-atelier-metal-arts','mission-fete-sorciere-arts'):
            rec=next(x for x in self.manifest['entries'] if x['folder'].endswith('/'+slug))
            self.assertTrue(all(not ref.startswith('qc-pri-fr-') and not ref.startswith('qc-pri-ma-') for ref in rec['objective_refs']))
            sheet=json.loads((BANK/rec['folder']/'FICHE_PEDAGOGIQUE.json').read_text(encoding='utf-8'))
            self.assertTrue(all(a['motif_de_choix'] and a['preuve'] for a in sheet['activites']))

    def test_editorial_criteria_are_not_old_generic(self):
        for rec in self.manifest['entries']:
            author=json.loads((BANK/rec['folder']/'brouillon.json').read_text(encoding='utf-8'))
            for card in author['theory_entries'].values():
                self.assertNotIn('Comparer la trace à l’objectif',card['criterion'])
                self.assertIn('Critères proposés',card['criterion'])
                self.assertGreater(len(card['expected_action']),95)

    def test_full_schema_and_no_runtime_rights(self):
        for rec in self.manifest['entries']:
            base=BANK/rec['folder']
            design=json.loads((base/'design.json').read_text(encoding='utf-8'))
            self.assertFalse(validate_document(design)[0],rec['folder'])
            self.assertEqual(design['status'],'design_only')
            self.assertFalse(any(design['governance'][k] for k in ('activation_authorized','publication_authorized','student_data_included')))
            handoff=json.loads((base/'handoff.json').read_text(encoding='utf-8'))
            self.assertFalse(any(handoff[k] for k in ('session_admitted','permissions_granted','orgo_world_created','konnaxion_project_created')))
            for n in (1,8,30):
                plan=json.loads((base/f'plan-{n:02}.json').read_text(encoding='utf-8'))
                self.assertEqual(plan['participation']['participant_count'],n)
                self.assertIs(plan['export_hints']['runtime_admitted'],False)

    def test_token_matching_avoids_personne_son(self):
        self.assertFalse(matches('son','une personne annonce'))
        self.assertTrue(matches('son','des sons du village'))
        self.assertTrue(matches('mesur','trois mesures distinctes'))

    def test_catalogue_advanced_editor_loads_v07_patterns(self):
        c=attach_ekole_activity_patterns(load_catalogue(KONTEXTE))
        ids={a['ref'] for a in c.activities}
        self.assertIn('ekoleprop:ap-076',ids)
        self.assertEqual(len(ids),len(c.activities))

    def test_export_no_overwrite_and_integrity(self):
        with tempfile.TemporaryDirectory() as tmp:
            out=pathlib.Path(tmp)/'generated'
            result=generate(KONTEXTE,out,limit=2)
            self.assertEqual(result['propositions'],2)
            self.assertEqual(verify(out,KONTEXTE)['propositions_verifiees'],2)
            with self.assertRaises(FileExistsError):generate(KONTEXTE,out,limit=2)
            side=next(out.glob('situations/*/FICHE_PEDAGOGIQUE.json'))
            side.write_text('{}',encoding='utf-8')
            with self.assertRaisesRegex(ValueError,'Empreinte'):verify(out,KONTEXTE)

    def test_teacher_bridge_reads_sheet_with_hash_protection(self):
        rec=next(x for x in self.manifest['entries'] if x['folder'].endswith('/mission-fete-sorciere-arts'))
        with tempfile.TemporaryDirectory() as d:
            root=pathlib.Path(d)
            bank=root/'candidats-v0_7';folder=bank/rec['folder'];folder.mkdir(parents=True)
            m={**self.manifest,'entries':[rec],'entries_count':1,'source_situations_covered':1}
            (bank/'MANIFEST.json').write_text(json.dumps(m),encoding='utf-8')
            for name in ('design.json','brouillon.json','FICHE_PEDAGOGIQUE.json'):
                shutil.copy2(BANK/rec['folder']/name,folder/name)
            slug=pathlib.PurePosixPath(rec['folder']).name
            with mock.patch.object(prf22_bridge,'BANKS',root):
                idx=prf22_bridge.index();self.assertEqual(idx['version'],'candidats-v0_7')
                d=prf22_bridge.detail(slug)
                self.assertEqual(d['fiche_pedagogique']['status'],'candidat_non_qualifie')
                self.assertEqual(d['meta']['source_ref'],rec['source_ref'])
                (folder/'FICHE_PEDAGOGIQUE.json').write_text('{}',encoding='utf-8')
                with self.assertRaisesRegex(ValueError,'Empreinte'):prf22_bridge.detail(slug)

if __name__=='__main__':unittest.main()
