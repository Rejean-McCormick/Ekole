"""V2: provenance/temporalité, génération sûre, intégration sans écrasement."""
from pathlib import Path
import unittest,json,subprocess,tempfile,shutil,sys,importlib.util
ROOT=Path(__file__).resolve().parents[1]
modpath=ROOT/'tools/compiler_atelier_histoire_v2.py'
spec=importlib.util.spec_from_file_location('compile_v2_test',modpath);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
def j(rel):return json.loads((ROOT/rel).read_text(encoding='utf-8'))
class SocietesV2Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.output=m.compile_v2(ROOT)
  cls.g=j('modules/qc-pri-us-009/canon/domain/societes-rencontres-v2.json')
  cls.old=j('modules/qc-pri-us-009/canon/domain/societes-rencontres-v1.json')
 def test_precise_counts(self):
  self.assertEqual(len(self.output['faits']),37);self.assertEqual(len(self.output['defis']),16)
  self.assertEqual(len(self.output['normes']),4);self.assertEqual(len(self.output['visuels']),13)
 def test_legacy_unchanged_and_versioned(self):
  self.assertEqual(len(self.old['assertions']),23);self.assertEqual(self.old['regles_attestees'],[])
  self.assertEqual(self.g['herite_de'],'canon/domain/societes-rencontres-v1.json')
  self.assertEqual(self.g['assertions'][:23],self.old['assertions'])
 def test_id_unique(self):
  for key in ('societes','roles','taches','ressources','assertions','periodes','regles_attestees','relations_situees_v2'):
   ids=[x['id'] for x in self.g[key]];self.assertEqual(len(ids),len(set(ids)),key)
 def test_assertions_provenances_all(self):
  sources={x['id'] for x in self.output['sources']};factids={x['id'] for x in self.output['faits']}
  ev=j('modules/qc-pri-us-009/sources/TRACABILITE_ASSERTIONS_v2.json')['assertions']
  keyed={(a['assertion_id'],a['source_id']) for a in ev}
  for fact in self.output['faits']:
   self.assertTrue(fact['sources']);self.assertTrue(set(fact['sources'])<=sources)
   self.assertTrue(all((fact['id'],s) in keyed for s in fact['sources']))
   self.assertTrue(fact['limites'])
 def test_period_context_for_relations(self):
  claims={x['id']:x for x in self.g['assertions']}
  for r in self.g['relations_situees_v2']:
   for id in r['fact_ids']:self.assertEqual(claims[id]['periode_ref'],r['periode_ref'])
 def test_normative_speech_does_not_claim_universal_authority(self):
  for n in self.g['regles_attestees']:
   self.assertTrue(n['source_ids']);self.assertTrue(n['interpretation'])
   if n['periode_ref']=='periode:1701':
    self.assertEqual(n['sujet_ref'],'soc:autorites-francaises-1701')
    self.assertEqual(n['statut'],'discours_historique_pas_regle_universelle')
 def test_positive_only_choices(self):
  relations={x['id']:x for x in self.output['relations']}
  for ex in self.output['defis']:
   if ex['type']=='choisir_fiche':
    choices={x['id'] for x in ex['options']}
    self.assertIn(ex['correct_ref'],choices)
    self.assertEqual(len(choices),len(ex['options']))
    self.assertTrue(choices<=relations.keys())
   self.assertNotIn('pensionnats',ex['titre'].lower())
 def test_associations_graph_only(self):
  for ex in self.output['defis']:
   if ex['type']!='associer':continue
   documented={r['id'] for r in self.output['relations']}
   self.assertTrue(all(p['relation_id'] in documented for p in ex['pairs']))
 def test_images_prompts_and_no_generated_images(self):
  for x in self.output['visuels']:
   self.assertEqual(x['statut'],'description_sans_image')
   self.assertTrue(x['concept_prompt'])
   self.assertTrue(x['expected_path'].endswith('.webp'))
   self.assertFalse((ROOT/'site/eleve/ateliers/rencontres-quebec'/x['expected_path']).exists())
 def test_public_excludes_internal_review_ids(self):
  self.assertNotIn('TRACABILITE_ASSERTIONS',json.dumps(self.output))
  self.assertFalse(self.output['generation_images'])
  self.assertFalse(self.output['generation_reponses_ia'])
 def test_generator_rejects_anachronism(self):
  with tempfile.TemporaryDirectory() as tmp:
   t=Path(tmp);shutil.copytree(ROOT/'modules',t/'modules')
   gpath=t/'modules/qc-pri-us-009/canon/domain/societes-rencontres-v2.json'
   c=json.loads(gpath.read_text());c['relations_situees_v2'][0]['periode_ref']='periode:1701';gpath.write_text(json.dumps(c))
   with self.assertRaisesRegex(ValueError,'anachronisme'):m.compile_v2(t)
 def test_generator_rejects_source_absent(self):
  with tempfile.TemporaryDirectory() as tmp:
   t=Path(tmp);shutil.copytree(ROOT/'modules',t/'modules')
   gpath=t/'modules/qc-pri-us-009/canon/domain/societes-rencontres-v2.json'
   c=json.loads(gpath.read_text());c['assertions'][-1]['source_ids']=['src:inventee'];gpath.write_text(json.dumps(c))
   with self.assertRaisesRegex(ValueError,'fait invalide'):m.compile_v2(t)
 def test_installer_dry_run_idempotent_preserves_source(self):
  with tempfile.TemporaryDirectory() as tmp:
   t=Path(tmp);shutil.copytree(ROOT/'modules',t/'modules')
   (t/'tools').mkdir();shutil.copy2(ROOT/'tools/integrer_kristal_histoire_v2.py',t/'tools/integrer_kristal_histoire_v2.py')
   ins=t/'kristals/qc-pri-us-009';(ins/'canon/domain').mkdir(parents=True);(ins/'sources').mkdir(parents=True)
   (ins/'kristal.workspace.json').write_text(json.dumps({'slug':'qc-pri-us-009'}))
   shutil.copy2(ROOT/'modules/qc-pri-us-009/canon/domain/societes-rencontres-v1.json',ins/'canon/domain/societes-rencontres-v1.json')
   (ins/'canon/state.index.json').write_text(json.dumps({'canonical_artifacts':[]}))
   (ins/'sources/source-catalog.json').write_text(json.dumps({'sources':[]}))
   marker=ins/'CUSTOM.txt';marker.write_text('personalized')
   run=[sys.executable,str(t/'tools/integrer_kristal_histoire_v2.py'),'--root',str(t)]
   x=subprocess.run(run,capture_output=True,text=True);self.assertEqual(x.returncode,0,x.stderr)
   self.assertFalse((ins/'canon/domain/societes-rencontres-v2.json').exists())
   x=subprocess.run(run+['--apply'],capture_output=True,text=True);self.assertEqual(x.returncode,0,x.stderr)
   x=subprocess.run(run+['--apply'],capture_output=True,text=True);self.assertEqual(x.returncode,0,x.stderr);self.assertIn('Bilan 0 opérations',x.stdout)
   self.assertEqual(marker.read_text(),'personalized')
   (ins/'canon/domain/societes-rencontres-v2.json').write_text('CUSTOM')
   x=subprocess.run(run+['--apply'],capture_output=True,text=True);self.assertNotEqual(x.returncode,0)
   self.assertEqual((ins/'canon/domain/societes-rencontres-v2.json').read_text(),'CUSTOM')
if __name__=='__main__':unittest.main()
