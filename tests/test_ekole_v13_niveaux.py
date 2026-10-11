import json, unittest, pathlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
class Tests(unittest.TestCase):
 def setUp(self):
  self.lab=json.loads((ROOT/'site/eleve/labo/data/catalogue.json').read_text())['items']
  self.ids={x['id'] for x in self.lab}
 def test_graded(self):
  self.assertTrue(all(isinstance(x['annees_proposees'],list) and all(1<=y<=6 for y in x['annees_proposees']) for x in self.lab))
 def test_no_primary_count_in_third(self):
  self.assertTrue(all(3 not in x['annees_proposees'] for x in self.lab if x['id'] in ('droite-12','droite-7') or x['type']=='estimer'))
 def test_source_math(self):
  self.assertTrue(all(x in self.ids for x in ['multiplier-6x4','multiplier-5x6','arrondir-147','arrondir-263']))
 def test_history_closed(self):
  self.assertTrue(all(x in self.ids for x in ['histoire-relier-fonctions','histoire-faits-limites','histoire-innu-iroquois']))
 def test_no_free_answer(self):
  for name in ('app.js','atelier-v8.js'):
   data=(ROOT/'site/eleve'/name).read_text()
   self.assertNotIn("'textarea'",data)
 def test_encyclopedia(self):
  js=(ROOT/'site/eleve/encyclopedie-autochtones/app.js').read_text()
  self.assertIn('function addStructuredLabs',js)
 def test_deterministic_engine_unchanged(self):
  self.assertNotIn('site/eleve/labo/engine.js',json.loads((ROOT/'MANIFEST_V13.json').read_text())['files']) # correctif does not replace deterministic engine
if __name__=='__main__':unittest.main()
