"""Behavioral tests against the self-contained, synthetic Kontexte fixture."""
from __future__ import annotations
import copy
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile

BASE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(BASE/'app'))
from composer_core import compose_draft, load_catalogue, validate_draft
from prf22_core import (build_design, DesignError, authoring_state, load_authoring, export_pack,
                        make_handoff, observe_catalogue_sources, sha)
from prf22_validator import validate_document

TEXT={
 'conjecture_statement':'La mise en comparaison de solutions pourrait favoriser une justification explicite du choix.',
 'expected_action':'Comparer les résultats et expliciter une décision face aux contraintes.',
 'process':'L’enfant analyse les informations reçues et formule une justification.',
 'observation':'Observer les reformulations et les corrections consignées au travail.',
 'evidence':'Une fiche de comparaison qui explique clairement les résultats obtenus.',
 'criterion':'La réponse fait apparaître les calculs et leurs justifications explicites.',
 'disconfirmation':'Une réponse correcte apparaît sans la moindre justification observable.',
 'alternative':'La réussite pourrait provenir d’une aide non déclarée ou d’une copie.',
 'boundary':'Le matériel et les consignes demeurent accessibles et compréhensibles.',
 'interpretation_limit':'Une production collective ne permet pas d’inférer les acquis de chacun.',
 'theory_ids':['sandoval-2014','biggs-align'], 'learning_type':'practice',
 'assessment_requires':'individual_possible'
}


class Prf22Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fixture=tempfile.TemporaryDirectory()
        with zipfile.ZipFile(BASE/'tests'/'fixture_kontexte.zip') as z:z.extractall(cls.fixture.name)
        cls.root=Path(cls.fixture.name)
        cls.catalog=load_catalogue(cls.root)
        cls.act=[a['ref'] for a in cls.catalog.activities[:3]]
        cls.obj=[o['ref'] for o in cls.catalog.objectives[:3]]

    @classmethod
    def tearDownClass(cls):cls.fixture.cleanup()

    def draft(self,n=8,real='fictif',epoch='Époque imaginaire'):
        return compose_draft(self.catalog,'mission:fete-sorciere',self.act,n,4,
            epoch=epoch,cultural_frame='Culture de fiction, non assimilée à une culture existante',
            setting='Village inventé',reality=real,objectives=self.obj,parallel_posts=2)

    def entries(self,collaboration=True):
        result={}
        for i,oid in enumerate(self.obj):
            result[oid]={**copy.deepcopy(TEXT),'activity_refs':[self.act[i]],
                         'assessment_requires':'peer_interaction' if collaboration and i==2 else 'individual_possible'}
        return result

    def build(self,n=8):return build_design(self.draft(n),self.entries())

    def test_source_catalogue(self):
        self.assertGreaterEqual(len(self.catalog.activities),3)
        self.assertEqual(len(self.catalog.objectives),202)

    def test_valid_build_and_schema(self):
        d=self.build();err,checked=validate_document(d,True)
        self.assertEqual(err,[])
        self.assertTrue(checked)
        self.assertEqual(d['format'],'ekole.situation-orchestrable.design/0.3')

    def test_1_to_30_works_and_never_claims_peer_in_solo(self):
        for n in range(1,31):
            with self.subTest(n=n):
                draft=self.draft(n)
                validate_draft(draft)
                design=build_design(draft,self.entries())
                self.assertFalse(design['governance']['activation_authorized'])
                self.assertFalse(design['governance']['student_data_included'])
                v={x['learners']:x for x in design['pedagogical_model']['adaptation_contract']['variants']}
                self.assertIn(n,v)
                self.assertEqual(set(v[1]['non_assessable_objective_ids']), {'obj-03'})
                self.assertNotIn('obj-03',v[1]['preserved_objective_ids'])

    def test_missing_theory_card_rejected(self):
        entries=self.entries();del entries[self.obj[1]]
        with self.assertRaisesRegex(DesignError,'carte théorique absente'):
            build_design(self.draft(),entries)

    def test_missing_alignment_rejected(self):
        entries=self.entries();entries[self.obj[0]]['activity_refs']=[]
        with self.assertRaisesRegex(DesignError,'choisir au moins une activité'):
            build_design(self.draft(),entries)

    def test_orphan_activity_rejected(self):
        entries=self.entries();entries[self.obj[0]]['activity_refs']=[self.act[1]]
        with self.assertRaisesRegex(DesignError,'aucun objectif'):
            build_design(self.draft(),entries)

    def test_unknown_theory_reference_rejected(self):
        entries=self.entries();entries[self.obj[0]]['theory_ids']=['pretend-2026']
        with self.assertRaisesRegex(DesignError,'inconnue'):
            build_design(self.draft(),entries)

    def test_incomplete_evidence_rejected(self):
        entries=self.entries();entries[self.obj[0]]['criterion']=''
        with self.assertRaisesRegex(DesignError,'criterion'):
            build_design(self.draft(),entries)

    def test_dependency_accepts_links_and_forbids_cycles(self):
        ref1,ref2=self.act[:2]
        d=build_design(self.draft(),self.entries(),f'{ref1} > {ref2} : Fiche de relevés transmise')
        self.assertEqual(d['dependencies'][0]['before'],'act-01')
        with self.assertRaisesRegex(DesignError,'cycle'):
            build_design(self.draft(),self.entries(),f'{ref1} > {ref2} : Fiche transmise\n{ref2} > {ref1} : Retour en boucle')

    def test_dependency_unknown_ref_rejected(self):
        with self.assertRaisesRegex(DesignError,'inconnue'):
            build_design(self.draft(),self.entries(),'fake > fake2 : Un document échangé')

    def test_same_activity_different_context(self):
        a=self.build();b=build_design(self.draft(8,'réel','Époque contemporaine'),self.entries())
        self.assertEqual(a['activities'][0]['exercise_ref'],b['activities'][0]['exercise_ref'])
        self.assertNotEqual(a['context']['epoch'],b['context']['epoch'])
        self.assertNotEqual(a['context']['reality_mode'],b['context']['reality_mode'])
        self.assertNotEqual(a['id'],b['id'])

    def test_unresolved_refs_and_real_source_observations(self):
        d=self.build()
        self.assertTrue(all(o['reference']['pin_status']=='unresolved' for o in d['learning']['objectives']))
        self.assertTrue(all(a['exercise_ref']['pin_status']=='unresolved' for a in d['activities']))
        obs=observe_catalogue_sources(self.root,self.draft())
        self.assertGreater(len(obs),0)
        self.assertTrue(all(o['pin_status']=='unresolved' for o in obs))
        self.assertTrue(all(len(o['observed_sha256'])==71 for o in obs))

    def test_cannot_claim_activation_or_pinned_authority(self):
        d=self.build()
        d['governance']['activation_authorized']=True
        self.assertTrue(validate_document(d)[0])
        d=self.build();d['activities'][0]['exercise_ref']['pin_status']='pinned'
        d['activities'][0]['exercise_ref']['commitment']='sha256:'+'a'*64
        self.assertTrue(validate_document(d)[0])

    def test_unqualified_pedagogical_review_only(self):
        d=self.build()
        self.assertTrue(all(c['validation_status']=='untested' for c in d['pedagogical_model']['conjectures']))
        self.assertTrue(all(a['assessment_status']=='planned_only' for a in d['pedagogical_model']['alignment']))
        self.assertEqual(d['pedagogical_model']['research_plan']['claims_status'],'untested')

    def test_export_roundtrip(self):
        with tempfile.TemporaryDirectory() as tmp:
            doc=self.build();draft=self.draft();entries=self.entries()
            target=export_pack(tmp,doc,draft,entries,'',self.root)
            self.assertEqual(len(list(target.iterdir())),7)
            self.assertTrue((target/'organisations-candidates'/'plan-30-participants.json').exists())
            state=load_authoring(target/'brouillon-reedition.json')
            self.assertEqual(doc,build_design(state['draft'],state['theory_entries'],state['dependency_lines']))
            self.assertFalse(json.loads((target/'plan-organisation.proposition.json').read_text())['session_admitted'])
            self.assertEqual(json.loads((target/'VALIDATION_LOCALE.json').read_text())['semantic_validation'],'pass')

    def test_export_is_non_overwriting(self):
        with tempfile.TemporaryDirectory() as tmp:
            target1=export_pack(tmp,self.build(),self.draft(),self.entries(),'',self.root)
            target2=export_pack(tmp,self.build(),self.draft(),self.entries(),'',self.root)
            self.assertNotEqual(target1,target2)
            self.assertTrue(target1.exists() and target2.exists())

    def test_load_rejects_other_formats(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'bad.json';p.write_text('{"format":"future_unknown"}',encoding='utf8')
            with self.assertRaises(DesignError):load_authoring(p)

    def test_cli_validation_and_catalogue(self):
        cmd=[sys.executable,str(BASE/'app'/'prf22_cli.py')]
        result=subprocess.run(cmd+['catalogue','--kontexte',str(self.root)],capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stderr)
        with tempfile.TemporaryDirectory() as tmp:
            d=self.build();p=Path(tmp)/'design.json';p.write_text(json.dumps(d,ensure_ascii=False),encoding='utf8')
            result=subprocess.run(cmd+['valider',str(p),'--require-schema'],capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stderr)

    def test_cli_export_source_drift_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            draft=self.draft();p=Path(tmp)/'state.json'
            p.write_text(json.dumps(authoring_state(draft,self.entries(),'',self.root),ensure_ascii=False),encoding='utf8')
            c=subprocess.run([sys.executable,str(BASE/'app'/'prf22_cli.py'),'exporter',str(p),
                               '--vers',str(Path(tmp)/'exports'),'--kontexte',str(self.root)],capture_output=True,text=True)
            self.assertEqual(c.returncode,0,c.stderr)
            # Compare a tampered recorded digest with original, no source mutation.
            record=json.loads(p.read_text(encoding='utf8'))
            record['source_observations'][0]['observed_sha256']='sha256:'+'0'*64
            p.write_text(json.dumps(record,ensure_ascii=False),encoding='utf8')
            c=subprocess.run([sys.executable,str(BASE/'app'/'prf22_cli.py'),'exporter',str(p),
                               '--vers',str(Path(tmp)/'exports'),'--kontexte',str(self.root)],capture_output=True,text=True)
            self.assertEqual(c.returncode,2)

    def test_conjecture_missing_statement_rejected(self):
        d=self.build();del d['pedagogical_model']['conjectures'][0]['conjecture_statement']
        self.assertTrue(validate_document(d)[0])

    def test_org_handoff_never_grants_permission(self):
        h=make_handoff(self.build(),self.draft())
        self.assertTrue(h['teacher_review_required'])
        self.assertTrue(all(h[k] is False for k in ('orgo_world_created','konnaxion_project_created','session_admitted','permissions_granted','student_data_included')))

if __name__=='__main__':unittest.main()
