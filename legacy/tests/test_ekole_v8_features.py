import importlib.util,json,pathlib,unittest,tempfile,hashlib,shutil,subprocess,sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
def mod(path,name):
 spec=importlib.util.spec_from_file_location(name,ROOT/path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
ex=mod('tools/export_ekole_eleve_v8.py','export_ekole_v8')
visual=mod('tools/compiler_visuels_approuves_v8.py','visuels_ekole_v8')
class TestEkoleV8(unittest.TestCase):
 def test_all_202_explorations_have_real_sources(self):
  b=json.loads((ROOT/'site/eleve/data/eleves/ateliers-v8.json').read_text());cat=json.loads((ROOT/'site/eleve/data/eleves/catalogue.json').read_text())
  self.assertEqual(b['count'],202);self.assertEqual(len(b['activities']),202)
  self.assertEqual({c['id'] for c in cat['courses']},{x['id'] for x in b['activities']})
  self.assertTrue(all(x['activite_type'] and x['objectif_source'] and x['statut']=='atelier_exploration_non_evaluation' for x in b['activities']))
 def test_six_specialized_labs_and_four_moments(self):
  b=json.loads((ROOT/'site/eleve/data/eleves/ateliers-v8.json').read_text()); lab=[a for a in b['activities'] if a['activite_type']!='reflexion']
  self.assertEqual(len(lab),6);self.assertEqual({x['activite_type'] for x in lab},{'denombrer','fraction','groupes','estimation','lecture','theatre'})
  self.assertTrue(all(a['etapes']==['decouvrir','essayer','expliquer','explorer'] for a in b['activities']))
 def test_teacher_planner_and_cookie_gate(self):
  text=(ROOT/'tools/serve_enseignant.py').read_text()
  self.assertIn("'/planification-v8.js'",text);self.assertIn('EkoleTeacher',text)
  self.assertIn('127.0.0.1',text)
 def test_visual_registries_consistent(self):
  original=json.loads((ROOT/'visuels/INTENTIONS_IMAGES.json').read_text());new=json.loads((ROOT/'visuels/SCENES_V8.json').read_text())
  self.assertEqual(len(original['intents']),227);self.assertEqual(len(new['scenes']),17)
  self.assertTrue(all(x['status']=='non_generee' and 'Sans texte' in x['prompt_image'] for x in new['scenes']))
 def test_child_public_export_strict(self):
  with tempfile.TemporaryDirectory() as t:
   out=pathlib.Path(t)/'child';r=ex.export(ROOT,out)
   # Imported images approved for local preview are additional public
   # assets; the old test counted only the pre-v15 static allowlist.
   self.assertGreaterEqual(r['exported'],len(ex.ALLOWED))
   self.assertEqual(r['exported'],len(set(r['files'])))
   for rel in set(r['files'])-set(ex.ALLOWED):
    self.assertTrue(rel.startswith('assets/kristals/') or rel.startswith('assets/images/') or rel.startswith('mondes-v12/assets/'))
   self.assertTrue((out/'atelier-v8.js').exists())
   self.assertTrue((out/'data/eleves/ateliers-v8.json').exists())
   self.assertFalse((out/'enseignant-app').exists());self.assertFalse((out/'visuels/INTENTIONS_IMAGES.json').exists())
   self.assertFalse((out/'data/cours').exists())
   self.assertIsNone(json.loads((out/'data/konstellation-liens.json').read_text())['preview_local_url'])
 def test_media_compile_rejects_missing_rights(self):
  with tempfile.TemporaryDirectory() as t:
   r=pathlib.Path(t);p=r/'visuels';(p/'images_a_approuver').mkdir(parents=True)
   (p/'INTENTIONS_IMAGES.json').write_text(json.dumps({'intents':[{'visual_id':'accueil-hero'}]}))
   image=(p/'images_a_approuver/accueil-hero.png');image.write_bytes(b'fake')
   approvals=p/'APPROBATION_IMAGES.json'
   approvals.write_text(json.dumps({'format':'ekole.approved-images/1.0','assets':[{'visual_id':'accueil-hero','file':'images_a_approuver/accueil-hero.png','sha256':hashlib.sha256(b'fake').hexdigest(),'licence':'Autorisation originale vérifiée','credit':'Ekole','alt_fr_CA':'Image symbolique du portail','pedagogical_review':True,'accessibility_review':True,'rights_review':False}]}))
   with self.assertRaises(visual.MediaRejection):visual.inspect(r,approvals,check_images=False)
 def test_v8_no_teacher_link_in_child(self):
  text=(ROOT/'site/eleve/index.html').read_text();self.assertNotIn('../enseignant/',text);self.assertNotIn('127.0.0.1',text)
  self.assertIn('atelier-v8.js',text)
 def test_integrations_only_verified_https(self):
  js=(ROOT/'site/eleve/app.js').read_text()
  self.assertIn('verified_collection===true',js);self.assertIn('k.public_url',js)
 def test_legacy_tests_still_recognize_canonical(self):
  self.assertTrue((ROOT/'site/index.html').exists());self.assertTrue((ROOT/'site/eleve/data/visuels_public.json').exists())
if __name__=='__main__':unittest.main()
