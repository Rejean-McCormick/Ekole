"""Protect updated Moodle bridge and OpsConsole by checking overlay file boundaries."""
import pathlib,json,unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
class TestActualise(unittest.TestCase):
 def test_updated_poly_bridge_preserved(self):
  self.assertTrue((ROOT/'tools/kristal_moodle_bridge.py').exists())
  self.assertTrue((ROOT/'moodle/contracts/kristal-moodle-projection.schema.json').exists())
  self.assertTrue((ROOT/'opsconsole/ekole_ops.py').exists())
 def test_no_course_id_claims(self):
  s=(ROOT/'site/app.js').read_text(encoding='utf-8')
  self.assertIn('plusieurs Kristals',s)
  self.assertIn('cours Moodle',s)
 def test_202_public_courses_untouched(self):
  index=json.loads((ROOT/'site/data/index.json').read_text(encoding='utf-8-sig'))
  self.assertEqual(len(index['courses']),202)
  self.assertEqual(len(list((ROOT/'site/data/cours').glob('*.json'))),202)
 def test_meta_distinctions(self):
  p=json.loads((ROOT/'site/data/organisation-parcours.json').read_text())
  self.assertEqual(len(p['cycles']),3)
  self.assertEqual(len(p['etapes']),4)
  self.assertEqual(p['modele_bulletin_officiel']['etapes'],3)
  self.assertEqual(sum(len(c['annees']) for c in p['cycles']),6)
if __name__=='__main__':unittest.main()
