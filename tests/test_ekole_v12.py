from __future__ import annotations
import json, pathlib, sys, unittest, tempfile
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from compiler_mondes_v12 import compile_mondes
from qualite_ekole_v12 import audit
from appliquer_plan_v12 import apply
class TestV12(unittest.TestCase):
 def test_projection(self):
  d=compile_mondes(ROOT,check=True);self.assertEqual(d['count'],7);self.assertEqual(d['couverts'],5)
  for x in d['items']:
   self.assertEqual(x['evaluation'],'entrainement_non_certifiant');self.assertNotIn('teacher_review',x);self.assertNotIn('preuve_attendue',x)
 def test_maturite(self):
  d=audit(ROOT);self.assertEqual(d['cours_reference'],202);self.assertFalse(d['publication_institutionnelle_prete']);self.assertTrue(d['pret_pour_prototype_local']);self.assertEqual(len(d['source_manquante']),2)
 def test_200_plans_sources(self):
  d=json.loads((ROOT/'docs/PLAN_TRANSFORMATION_202_V12.json').read_text());self.assertEqual(len(d['cours']),202)
  for x in d['cours']:
   if x['etat']=='source_complete_absente':continue
   p=ROOT/x['chemin'];self.assertTrue(p.is_file(),x['kristal_id'])
   v=json.loads(p.read_text());self.assertEqual(v['kristal_id'],x['kristal_id']);self.assertIn('prompt',v['visuels_conceptuels'])
 def test_application_protegee(self):
  course='qc-pri-ma-012';d=json.loads((ROOT/'kristals'/course/'experience/CADRE_PEDAGOGIQUE_V12.json').read_text())
  with tempfile.TemporaryDirectory() as t:
   p=pathlib.Path(t)/'essai.json';d['source']['objectif_observable']='CORROMPU';p.write_text(json.dumps(d),encoding='utf8')
   with self.assertRaises(ValueError):apply(ROOT,p,write=False)
 def test_prompt_v12_non_style(self):
  d=json.loads((ROOT/'site/eleve/mondes-v12/data/catalogue.json').read_text());self.assertEqual(d['count'],7)
  for x in d['items']:self.assertIn('sans imposer de style',x['prompt_visuel']);self.assertNotIn('image_url',x)
if __name__=='__main__':unittest.main()
