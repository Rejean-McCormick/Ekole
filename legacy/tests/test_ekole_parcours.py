import json,unittest,sys,copy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
import valider_parcours
config=json.loads((ROOT/'site/data/organisation-parcours.json').read_text(encoding='utf8'))
base=json.loads((ROOT/'site/data/parcours-affectations.4-etapes.exemple.json').read_text(encoding='utf8'))
old=json.loads((ROOT/'site/data/niveaux-manuel.exemple.json').read_text(encoding='utf8'))
class TestQuatreEtapes(unittest.TestCase):
 def test_four_periods_and_three_bulletins(self):
  self.assertEqual([e['periode'] for e in config['etapes']],['automne','automne','hiver','hiver'])
  self.assertEqual(config['modele_bulletin_officiel']['etapes'],3)
 def test_season_is_hiver(self):
  self.assertEqual(config['calendrier']['nom_saison_2'],'Hiver')
  self.assertEqual([x['periode'] for x in config['etapes']], ['automne','automne','hiver','hiver'])
  script=(ROOT/'site/app.js').read_text(encoding='utf-8')
  page=(ROOT/'site/index.html').read_text(encoding='utf-8')
  self.assertIn('Hiver',script)
  self.assertNotIn('Hiver et printemps',script+page)
  self.assertNotIn('hiver-printemps',script+page)
 def test_24_paths_6_years_3_cycles(self):
  errors,warnings=valider_parcours.validate(config,base,old,{'qc-pri-ma-001'})
  self.assertEqual(errors,[])
  self.assertEqual(len(base['cours_par_etape']),24)
  self.assertTrue(warnings)
 def test_legacy_18_keys_preserved(self):
  a=copy.deepcopy(base)
  for y in range(1,7):a['cours_par_etape'].pop(f'annee-{y}-etape-4')
  a['cours_par_etape']['annee-1-etape-2']=['qc-pri-ma-001'];a['preuves_attribution']['qc-pri-ma-001']='Décision pédagogique traçable'
  errors,warnings=valider_parcours.validate(config,a,old,{'qc-pri-ma-001'})
  self.assertEqual(errors,[])
  self.assertTrue(any('v3' in s for s in warnings))
 def test_reject_unknown_course(self):
  a=copy.deepcopy(base);a['cours_par_etape']['annee-3-etape-4']=['qc-pri-ma-999'];a['preuves_attribution']['qc-pri-ma-999']='Approbation'
  errors,_=valider_parcours.validate(config,a,old,{'qc-pri-ma-001'})
  self.assertTrue(any('absent' in s for s in errors))
 def test_reject_course_without_proof(self):
  a=copy.deepcopy(base);a['cours_par_etape']['annee-2-etape-4']=['qc-pri-ma-001']
  errors,_=valider_parcours.validate(config,a,old,{'qc-pri-ma-001'})
  self.assertTrue(any('justification' in s for s in errors))
 def test_cycles_2_or_3_years(self):
  alt=copy.deepcopy(config);alt['cycles']=[{'id':'c1','annees':[1,2,3]},{'id':'c2','annees':[4,5,6]}]
  errors,_=valider_parcours.validate(alt,base,old)
  self.assertEqual(errors,[])
 def test_invalid_five_periods(self):
  alt=copy.deepcopy(config);alt['etapes'].append({'numero':5,'periode':'hiver'})
  errors,_=valider_parcours.validate(alt,base,old)
  self.assertTrue(any('Quatre' in s for s in errors))
 def test_full_prior_overlay_fixes(self):
  self.assertGreater((ROOT/'site/assets/ekole-logo.svg').stat().st_size,300)
  self.assertIn('#1e6864',(ROOT/'site/style.css').read_text())
  js=(ROOT/'site/app.js').read_text()
  self.assertIn('function renderMarkdown(',js)
  self.assertIn('function renderCycles(',js)
  self.assertNotIn('filterByWave',js)
  html=(ROOT/'site/index.html').read_text()
  self.assertNotIn('id="wave"',html)
  self.assertIn('<option value="4">Étape 4',html)
 def test_no_layout_overwrite_of_real_allocation(self):
  self.assertTrue((ROOT/'site/data/parcours-affectations.4-etapes.exemple.json').exists())
  # Un fichier local v3 éventuellement présent doit être lisible, pas écrasé.
  local=ROOT/'site/data/parcours-affectations.json'
  if local.exists():self.assertIn(len(json.loads(local.read_text())['cours_par_etape']),(18,24))
if __name__=='__main__':unittest.main()
