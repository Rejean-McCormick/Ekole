from pathlib import Path
import unittest, json, subprocess, tempfile, shutil, sys, importlib.util, zipfile, io
ROOT=Path(__file__).resolve().parents[1]
source=ROOT/'tools/compiler_atelier_histoire.py'
spec=importlib.util.spec_from_file_location('compile_histoire',source)
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class HistoireTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pub=m.compile_game(ROOT)
        cls.canon=json.loads((ROOT/'modules/qc-pri-us-009/canon/domain/societes-rencontres-v1.json').read_text(encoding='utf-8'))
    def test_vingt_trois_faits(self):self.assertEqual(len(self.pub['faits']),23)
    def test_vingt_deux_activites(self):self.assertEqual(len(self.pub['exercices']),22)
    def test_aucune_source_manquante(self):
        ids={x['id'] for x in self.pub['sources']}
        self.assertTrue(all(set(f['sources'])<=ids for f in self.pub['faits']))
    def test_choix_uniques(self):
        for e in self.pub['exercices']:
            if e['mode'] in ('cloze','choix'):
                self.assertEqual(sum(x['ref']==e['reponse_ref'] for x in e['options']),1)
                self.assertGreaterEqual(len(e['options']),2)
    def test_regles_non_inventees(self):
        self.assertEqual(self.canon['regles_attestees'],[])
    def test_pas_de_qui_est_blanc_comme_nation(self):
        self.assertNotIn('blancs', ' '.join(x['label'] for x in self.canon['societes']).lower())
    def test_couches_historiques(self):
        ps={x['id'] for x in self.canon['periodes']}
        for x in ('periode:avant-contact','periode:1701','periode:actuel'):self.assertIn(x,ps)
    def test_pas_d_image_generee(self):
        v=self.pub['visuels'];self.assertEqual(len(v),6)
        self.assertTrue(all(x['concept_prompt'] and x['expected_path'].endswith('.webp') for x in v))
    def test_pas_d_anachronisme_institutionnel(self):
        f=next(f for f in self.canon['assertions'] if f['id']=='fait:pensionnats')
        self.assertEqual(f['sujet_ref'],'soc:institutions-coloniales-canadiennes-19e-20e')
        self.assertNotEqual(f['sujet_ref'],'soc:autorites-britanniques-apres1760')
    def test_sources_inuit_wendat_innu_presentes(self):
        sources={s['id'] for s in self.pub['sources']}
        self.assertTrue({'src:wendat-histoire','src:nametau-territoire','src:wendat-archives'}<=sources)
    def test_questions_depuis_faits(self):
        ids={f['id'] for f in self.pub['faits']}
        for q in self.pub['questions_guides']:self.assertIn(q['fact_id'],ids)
    def test_observation_humaine(self):
        x=next(x for x in self.pub['exercices'] if x['mode']=='humain')
        self.assertEqual(x['type_validation'],'humaine')
        self.assertTrue(x['criteres_observables'])
    def test_install_dry_run_et_idempotence(self):
        with tempfile.TemporaryDirectory() as td:
            t=Path(td)
            shutil.copytree(ROOT/'modules',t/'modules')
            (t/'tools').mkdir();shutil.copy2(ROOT/'tools/integrer_kristal_histoire.py',t/'tools/integrer_kristal_histoire.py')
            dest=t/'kristals/qc-pri-us-009';(dest/'canon').mkdir(parents=True);(dest/'sources').mkdir()
            (dest/'kristal.workspace.json').write_text(json.dumps({'slug':'qc-pri-us-009','status':'stub','native_model':{'kind':'undecided'},'semantic_ownership':{'owns':[]}}),encoding='utf-8')
            (dest/'canon/state.index.json').write_text(json.dumps({'canonical_artifacts':[], 'external_references':[],'derived_artifacts':[]}),encoding='utf-8')
            (dest/'sources/source-catalog.json').write_text(json.dumps({'format':'kristal.source-catalog/2.0.0','sources':[]}),encoding='utf-8')
            marker=dest/'contenu/EXISTANT.md';marker.parent.mkdir();marker.write_text('Ne pas modifier',encoding='utf-8');oldvis=dest/'experience/RESSOURCES_VISUELLES.json';oldvis.parent.mkdir(exist_ok=True);oldvis.write_text('VISUELS V10 EXISTANTS',encoding='utf-8')
            cli=[sys.executable,str(t/'tools/integrer_kristal_histoire.py'),'--root',str(t)]
            x=subprocess.run(cli,capture_output=True,text=True);self.assertEqual(x.returncode,0,x.stderr)
            self.assertFalse((dest/'canon/domain/societes-rencontres-v1.json').exists())
            x=subprocess.run(cli+['--apply'],capture_output=True,text=True);self.assertEqual(x.returncode,0,x.stderr)
            self.assertTrue((dest/'canon/domain/societes-rencontres-v1.json').exists())
            self.assertEqual(marker.read_text(),'Ne pas modifier');self.assertEqual(oldvis.read_text(),'VISUELS V10 EXISTANTS')
            x=subprocess.run(cli+['--apply'],capture_output=True,text=True);self.assertEqual(x.returncode,0,x.stderr)
            self.assertIn('Bilan 0 opérations',x.stdout)
            # edited source must not be overwritten
            patch=dest/'experience/histoire-rencontres/RESSOURCES_VISUELLES.json';patch.write_text('MODIFIE MANUELLEMENT',encoding='utf-8')
            x=subprocess.run(cli+['--apply'],capture_output=True,text=True);self.assertNotEqual(x.returncode,0)
            self.assertEqual(patch.read_text(),'MODIFIE MANUELLEMENT')
if __name__=='__main__':unittest.main()
