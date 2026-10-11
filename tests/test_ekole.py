import unittest, subprocess, sys, pathlib, json
ROOT=pathlib.Path(__file__).resolve().parents[1]
class TestEkole(unittest.TestCase):
 def test_catalogue(self):
  x=json.loads((ROOT/'catalogue/202_kristals.json').read_text());self.assertEqual(x['count'],202);self.assertEqual(len({r['id'] for r in x['kristals']}),202)
 def test_pages(self):
  x=json.loads((ROOT/'organisation/kristal-portail-ekole.candidat.json').read_text());self.assertEqual(len(x['pages']),20)
 def test_no_hidden_moodle_ids(self):
  x=json.loads((ROOT/'plans/moodle_projection_dry_run.json').read_text());self.assertEqual(len(x['courses']),202);self.assertTrue(x['dry_run']);self.assertTrue(all(c['moodle_course_id'] is None for c in x['courses']))
 def test_site_avoid_assessment_export(self):
  files={p.name for p in (ROOT/'site/data/cours').glob('*.json')};self.assertEqual(len(files),202)
  self.assertFalse(any('BANQUE_ITEMS' in p.name for p in (ROOT/'site').rglob('*') if p.is_file()))
 def test_catalogue_graph(self):
  ids={r['id'] for r in json.loads((ROOT/'catalogue/202_kristals.json').read_text())['kristals']};g=json.loads((ROOT/'catalogue/graphe_pedagogique.json').read_text());self.assertEqual(len(g['relations']),252);self.assertTrue(all(e['from'] in ids and e['to'] in ids for e in g['relations']))
 def test_isolation(self):
  self.assertFalse((ROOT/'site/vendor').exists());self.assertFalse((ROOT/'.kristal/node.json').exists())
if __name__=='__main__':unittest.main()
