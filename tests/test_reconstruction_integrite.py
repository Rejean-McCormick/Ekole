"""Régression de l'intégration: ne teste jamais l'approbation culturelle."""
import json, pathlib, unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
class ReconstructionIntegrity(unittest.TestCase):
 def test_three_autonomous_v9_builds(self):
  for slug in ('modele-organisation-humaine','societes-autochtones-quebec','rencontres-coloniales-quebec'):
   self.assertTrue((ROOT/'kristals'/slug/'build/v9/build-receipt.json').is_file())
 def test_logos_present_for_static_export(self):
  for name in ('site/assets/ekole-logo.svg','site/eleve/assets/ekole-logo.svg'):
   self.assertGreater((ROOT/name).stat().st_size,300)
 def test_four_step_containers_and_preserved_courses(self):
  d=json.loads((ROOT/'site/data/parcours-affectations.json').read_text(encoding='utf8'))
  keys={f'annee-{y}-etape-{e}' for y in range(1,7) for e in range(1,5)}
  self.assertEqual(set(d['cours_par_etape']),keys)
  self.assertEqual(len(json.loads((ROOT/'catalogue/202_kristals.json').read_text(encoding='utf8'))['kristals']),202)
 def test_v4_remains_autonomous(self):
  self.assertTrue((ROOT/'kristals/societes-autochtones-quebec/canon/domain/encyclopedie-v4.json').is_file())
  self.assertFalse((ROOT/'modules/qc-pri-us-009/canon/domain/encyclopedie-v4.json').exists())
if __name__=='__main__':unittest.main()
