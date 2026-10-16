import importlib.util,json,hashlib,unittest
from pathlib import Path

HERE=Path(__file__).resolve().parent.parent
spec=importlib.util.spec_from_file_location('ency_v4',HERE/'tools/encyclopedie_autochtones_v4.py')
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
DATA=mod.load(HERE)
class Corpus(unittest.TestCase):
 def test_validator(self): self.assertEqual(mod.validate(DATA),[])
 def test_enriched_independent(self):
  self.assertGreaterEqual(len(DATA['articles']),60)
  self.assertEqual(len(DATA['entrainements']),20)
  self.assertEqual(len(DATA['chapitres']),11)
  self.assertGreaterEqual(sum(len(a['prerequis']) for a in DATA['articles']),55)
  self.assertEqual(len(DATA['visuels']),11)
  self.assertGreaterEqual(len(DATA['sources']),25)
 def test_every_article_contextualized_and_sourced(self):
  for x in DATA['articles']:
   self.assertTrue(x['societe'] and x['epoque'] and x['sources'] and x['reponse_courte'])
   self.assertTrue(x['precision'] and x['statut_revue'])
 def test_anti_hallucination_gender(self):
  r=mod.answer(DATA,'Est-ce que les hommes tannaient les peaux ?')
  self.assertEqual(r['statut'],'reponse_du_corpus')
  self.assertIn('vers 1500',r['article']['reponse_courte'])
 def test_anti_hallucination_fishing_fiber(self):
  a=next(a for a in DATA['articles'] if a['id']=='ens-v4:fil-peche')
  self.assertIn('ne peux pas certifier',a['reponse_courte'])
  self.assertIn('ortie',a['explication_detaillee'])
 def test_clan_facade_nuance(self):
  a=next(a for a in DATA['articles'] if a['id']=='ens-v4:symboles-maison')
  self.assertIn('ne confirme pas',a['reponse_courte'])
 def test_longhouse_range(self):
  a=next(a for a in DATA['articles'] if a['id']=='ens-v4:nombre-maison')
  self.assertIn('25 à 60',a['reponse_courte'])
 def test_unknown_returns_no_generated_fact(self):
  r=mod.answer(DATA,'Quels animaux dormaient en lévitation sous la rivière lunaire ?')
  self.assertNotEqual(r['statut'],'reponse_du_corpus')
 def test_generic_question_does_not_invent(self):
  r=mod.answer(DATA,'Les autochtones avaient-ils tous les mêmes droits ?')
  self.assertNotEqual(r['statut'],'reponse_du_corpus')
 def test_exact_lookup(self):
  r=mod.answer(DATA,'Qui habitait dans les maisons longues ?')
  self.assertEqual(r['statut'],'reponse_du_corpus')
  self.assertEqual(r['article']['id'],'ens-v4:maisons-longues')
 def test_sources_bounded_and_unique(self):
  sources={s['id'] for s in DATA['sources']}
  for q in DATA['entrainements']:
   a=next(a for a in DATA['articles'] if a['id']==q['entree_ref'])
   self.assertEqual(set(q['source_refs']),{s['id'] for s in a['sources']})
  self.assertTrue(sources)
 def test_no_images_generated(self):
  site=HERE/'site/eleve/encyclopedie-autochtones'
  self.assertEqual(list(site.rglob('*.webp'))+list(site.rglob('*.png'))+list(site.rglob('*.jpg')),[])
 def test_v3_source_unchanged(self):
  checks={'canon/domain/graphe-v3.json':'d0b3183bf6f585b26f863dbffcc2f3ef1974660bceb3ef46ee9578a398e61751','build/v9/build-receipt.json':'12d50d381d4d7e2b59fd50fa04f079abbb106bc9b87e93e7bfefbf09ad01a676'}
  for f,digest in checks.items():
   p=HERE/'kristals/societes-autochtones-quebec'/f
   self.assertEqual(hashlib.sha256(p.read_bytes()).hexdigest(),digest)
 def test_course_references_autonomous_corpus_without_embedding_it(self):
  # The complete Ekole repository contains courses and modules by design.
  # A domain Kristal must still own the encyclopedia; course-specific
  # files must not contain another physical copy of that corpus.
  self.assertTrue((HERE/'kristals/societes-autochtones-quebec/canon/domain/encyclopedie-v4.json').is_file())
  for area in (HERE/'kristals/qc-pri-us-009',HERE/'modules/qc-pri-us-009'):
   self.assertEqual(list(area.rglob('encyclopedie-v4.json')) if area.exists() else [],[])
 def test_export_compiles(self):
  p=HERE/'site/eleve/encyclopedie-autochtones/bibliotheque.json'
  d=json.loads(p.read_text(encoding='utf-8'))
  self.assertEqual(len(d['articles']),len(DATA['articles']))
  self.assertNotIn('compte_eleve',d)
if __name__=='__main__':unittest.main()
