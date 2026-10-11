import importlib.util
import json
import pathlib
import unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('prop', ROOT/'tools/proposer_affectations.py')
prop=importlib.util.module_from_spec(spec);spec.loader.exec_module(prop)
class TestPropositions(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.cat=json.loads((ROOT/'catalogue/202_kristals.json').read_text(encoding='utf8'))
  cls.graph=json.loads((ROOT/'catalogue/graphe_pedagogique.json').read_text(encoding='utf8'))
  cls.p=json.loads((ROOT/'site/data/parcours-propositions.json').read_text(encoding='utf8'))
 def test_ids(self):self.assertEqual(set(self.p['affectations_proposees']),{x['id'] for x in self.cat['kristals']})
 def test_24_stage_containers(self):
  self.assertEqual(len(self.p['cours_par_etape']),24)
  self.assertEqual(sum(len(v) for v in self.p['cours_par_etape'].values()),202)
  self.assertTrue(all(self.p['cours_par_etape'][f'annee-{y}-etape-{e}'] for y in range(1,7) for e in range(1,5)))
 def test_all_draft_with_sources(self):
  self.assertTrue(all(x['statut']=='proposition_non_validee' and x['sources'] and x['revue_pedagogique_requise'] for x in self.p['affectations_proposees'].values()))
 def test_prerequisite_order(self):
  a=self.p['affectations_proposees']
  for r in self.graph['relations']:
   if r['type']=='requires':
    x,y=a[r['from']],a[r['to']]
    self.assertLessEqual((y['annee'],y['etape']),(x['annee'],x['etape']))
 def test_math_year_3_not_empty(self):
  self.assertTrue(any(i.startswith('qc-pri-ma-') and x['annee']==3 for i,x in self.p['affectations_proposees'].items()))
 def test_deterministic(self):self.assertEqual(prop.generate(self.cat,self.graph),self.p)
 def test_no_wave_assignment(self):
  import copy
  changed=copy.deepcopy(self.cat)
  for row in changed['kristals']:
   row['vague'] = 99
  self.assertEqual(prop.generate(self.cat,self.graph),prop.generate(changed,self.graph))
 def test_manual_affectations_are_separate_from_proposals(self):
  # Preserve actual user decisions, if any. They must never be replaced
  # automatically by the unapproved 202 course placement suggestions.
  path=ROOT/'site/data/parcours-affectations.json'
  if path.exists():
   manual=json.loads(path.read_text(encoding='utf-8'))
   self.assertNotIn('affectations_proposees',manual)
   self.assertEqual(len(manual['cours_par_etape']),24)
   known={x['id'] for x in self.cat['kristals']}
   for key,courses in manual['cours_par_etape'].items():
    self.assertIn(key,{f'annee-{y}-etape-{e}' for y in range(1,7) for e in range(1,5)})
    self.assertTrue(set(courses)<=known)
  other=ROOT/'site/data/niveaux-manuel.json'
  if other.exists():self.assertIsInstance(json.loads(other.read_text(encoding='utf-8')),dict)
if __name__=='__main__':unittest.main()
