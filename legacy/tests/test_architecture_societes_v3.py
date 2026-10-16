"""Contrat d'autonomie, épinglage, non-écrasement et compilation locale du cours."""
import importlib.util,json,shutil,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def load(rel,name):
 spec=importlib.util.spec_from_file_location(name,ROOT/rel);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
compiler=load('tools/compiler_atelier_histoire_v3.py','compiler_v3')
installer=load('tools/integrer_references_histoire_v3.py','installer_v3')
ind_query=load('tools/interroger_societes_autochtones_v3.py','interroger_v3')
def rd(p):return json.loads(p.read_text(encoding='utf-8'))

class ArchitectureV3(unittest.TestCase):
 def test_trois_kristals_autonomes(self):
  for slug in ('modele-organisation-humaine','societes-autochtones-quebec','rencontres-coloniales-quebec'):
   self.assertEqual(rd(ROOT/'kristals'/slug/'kristal.workspace.json')['slug'],slug)
 def test_faits_un_seul_proprietaire(self):
  g=[rd(ROOT/'kristals'/s/'canon/domain/graphe-v3.json') for s in ('societes-autochtones-quebec','rencontres-coloniales-quebec')]
  facts=[[x['id'] for x in a['assertions']] for a in g]
  self.assertEqual([len(f) for f in facts],[30,25]);self.assertFalse(set(facts[0]) & set(facts[1]))
  self.assertEqual(len(facts[0]+facts[1]),55)
 def test_kristal_autochtone_reutilisable_sans_cours(self):
  items=ind_query.query(ROOT,search='wendat')
  self.assertGreater(len(items),3)
  self.assertTrue(all(x['source_ids'] for x in items))
  self.assertTrue(all(x['limites'] for x in items))
 def test_cours_sans_assertions(self):
  c=rd(ROOT/'cours-references/qc-pri-us-009/SELECTION_PEDAGOGIQUE_V3.json')
  self.assertFalse('assertions' in c);self.assertFalse('societes' in c)
  self.assertEqual(len(set(sum(c['selection_faits'].values(),[]))),22)
 def test_reference_epinglee_et_compilation(self):
  data=compiler.compile_data(ROOT)
  self.assertEqual(len(data['faits']),22);self.assertEqual(len(data['dependances']),2)
  self.assertGreaterEqual(len(data['activites']),20)
  self.assertTrue(all(a['correct_id'] in {x['id'] for x in a['options']} for a in data['activites']))
 def test_source_modifiee_echoue(self):
  with tempfile.TemporaryDirectory() as d:
   r=Path(d);self.mini_copy(r)
   p=r/'kristals/societes-autochtones-quebec/canon/domain/graphe-v3.json'
   p.write_text(p.read_text().replace('Une fiche ne décrit pas une nation entière','La fiche a été modifiée'),encoding='utf-8')
   with self.assertRaisesRegex(ValueError,'modifié'):compiler.compile_data(r)
 def test_reference_de_cours_inventee_refusee(self):
  with tempfile.TemporaryDirectory() as d:
   r=Path(d);self.mini_copy(r)
   p=r/compiler.COURSE_REL;doc=rd(p);doc['selection_faits']['diplomatie'].append('fait:inventé')
   p.write_text(json.dumps(doc,ensure_ascii=False),encoding='utf-8')
   with self.assertRaisesRegex(ValueError,'sans Kristal'):compiler.compile_data(r)
 def test_installation_non_destructive_idempotente(self):
  with tempfile.TemporaryDirectory() as d:
   r=Path(d);self.mini_copy(r);self.assertFalse((r/'kristals/qc-pri-us-009').exists())
   edits=installer.plan(r,restore_frame=True)
   for p,b in edits.items():p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
   self.assertEqual(len(installer.plan(r,restore_frame=True)),0)
   c=rd(r/'kristals/qc-pri-us-009/canon/domain/SELECTION_PEDAGOGIQUE_V3.json')
   self.assertNotIn('assertions',c)
 def test_refuse_ecraser_une_selection_personnalisee(self):
  with tempfile.TemporaryDirectory() as d:
   r=Path(d);self.mini_copy(r)
   edits=installer.plan(r,restore_frame=True)
   for p,b in edits.items():p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
   f=r/'kristals/qc-pri-us-009/canon/domain/SELECTION_PEDAGOGIQUE_V3.json'
   f.write_text('{"edited_by":"personne"}',encoding='utf-8')
   with self.assertRaisesRegex(ValueError,'personnalisée'):installer.plan(r)
 @staticmethod
 def mini_copy(root):
  for rel in ('cours-references','modules/qc-pri-us-009/experience/histoire-rencontres/REFERENCES_KRISTALS_V3.json',
              'modules/qc-pri-us-009/experience/histoire-rencontres/RESSOURCES_VISUELLES_V2.json',
              'cadres-source/qc-pri-us-009'):
   src=ROOT/rel;dst=root/rel
   if src.is_dir():shutil.copytree(src,dst)
   else:dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst)
  for slug in ('societes-autochtones-quebec','rencontres-coloniales-quebec'):
   src=ROOT/'kristals'/slug;dst=root/'kristals'/slug
   for rel in ('canon/domain/graphe-v3.json','build/v9/state-snapshot.json'):
    p=src/rel;q=dst/rel;q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
   (dst/'build/v9/artifacts').mkdir(parents=True,exist_ok=True)
   for p in (src/'build/v9/artifacts').glob('*.json'):shutil.copy2(p,dst/'build/v9/artifacts'/p.name)
if __name__=='__main__':unittest.main()
