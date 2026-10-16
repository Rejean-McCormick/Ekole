from pathlib import Path
import sys,json,unittest,tempfile,shutil
R=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(R/'tools'))
from compiler_activites_v14 import compile
class MegaV14(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.report=compile(R,False);cls.cat=json.loads((R/'site/eleve/labo/data/catalogue.json').read_text());cls.pub=json.loads((R/'site/eleve/data/activites-v14.json').read_text())
 def test_all_202_accounted(self):
  self.assertEqual(len(self.report['cours']),202);s=self.report['statistiques'];self.assertEqual(s['cours_sans_outil']+s['cours_avec_outil'],202)
  self.assertTrue(all(x['etat'] in ('a_concevoir','prototypes_a_revoir') for x in self.report['cours']))
 def test_third_math(self):
  x=[c for c in self.report['cours'] if c['discipline']=='Mathématique' and c['annee_proposee']==3];self.assertEqual(len(x),8);self.assertTrue(all(c['nombre_activites'] for c in x))
 def test_catalog_14(self):self.assertEqual(len({x['type'] for x in self.cat['items']}),14);self.assertEqual(len(self.cat['items']),51)
 def test_no_basic_counting_grade3(self):
  self.assertTrue(all(x['id']!='partage-12' for x in self.pub['cours']['qc-pri-ma-009']))
  self.assertTrue(all(q['id'] not in ('droite-7','droite-12','estime-48','estime-73') for q in self.cat['items'] if 3 in q.get('annees_proposees',[])))
 def test_ownership(self):
  m={q['id']:q for q in self.cat['items']}
  for cid,acts in self.pub['cours'].items():
   for x in acts:self.assertEqual(m[x['id']]['source_kristal_id'],cid)
 def test_public_metadata_no_answers(self):
  text=json.dumps(self.pub['cours']);self.assertNotIn('answer',text);self.assertNotIn('correct',text);self.assertNotIn('parameters',text)
 def test_guard_and_teacher(self):
  self.assertIn('allowedByCourse',(R/'site/eleve/labo/app.js').read_text());self.assertIn('activites-v14.json',(R/'site/eleve/app.js').read_text());self.assertIn('/api/couverture-v14.json',(R/'tools/serve_enseignant.py').read_text())
 def test_live_student_scripts_no_text_answer(self):
  for rel in ('site/eleve/app.js','site/eleve/labo/app.js'):
   s=(R/rel).read_text();self.assertNotIn("'textarea'",s);self.assertNotIn("'input','estimate'",s)
 def test_compiler_with_no_eligible_manifests(self):
  with tempfile.TemporaryDirectory() as t:
   T=Path(t)
   for rel in ('site/eleve/data/eleves/catalogue.json','site/eleve/labo/data/catalogue.json'):
    p=T/rel;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(R/rel,p)
   self.assertEqual(compile(T,False)['statistiques']['cours_avec_outil'],0)
 def test_export_allowlist_v14(self):
  import importlib.util
  spec=importlib.util.spec_from_file_location('ekole_v14_export',R/'tools/export_ekole_eleve_v8.py')
  mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
  with tempfile.TemporaryDirectory() as tmp:
   mod.export(R,Path(tmp)/'student')
   P=Path(tmp)/'student'
   self.assertTrue((P/'data/activites-v14.json').exists())
   self.assertTrue((P/'labo/data/associations-v14.json').exists())
   self.assertFalse((P/'kristals').exists());self.assertFalse((P/'enseignant-app').exists())
   self.assertFalse((P/'data/cours').exists())
 def test_teacher_api_protected(self):
  import importlib.util
  from http.server import ThreadingHTTPServer
  from threading import Thread
  from urllib.request import urlopen,Request
  from urllib.error import HTTPError
  sp=importlib.util.spec_from_file_location('teacher_v14',R/'tools/serve_enseignant.py');module=importlib.util.module_from_spec(sp);sp.loader.exec_module(module)
  server=ThreadingHTTPServer(('127.0.0.1',0),module.create_handler(R,'v14-test-token'))
  t=Thread(target=server.serve_forever,daemon=True);t.start()
  try:
   url=f'http://127.0.0.1:{server.server_port}/api/couverture-v14.json'
   with self.assertRaises(HTTPError) as ctx:urlopen(url,timeout=3)
   self.assertEqual(ctx.exception.code,401)
   with urlopen(Request(url,headers={'Cookie':'EkoleTeacher=v14-test-token'}),timeout=3) as rsp:
    self.assertEqual(json.load(rsp)['statistiques']['cours'],202)
  finally:server.shutdown();server.server_close();t.join(timeout=2)
 def test_ownership_tamper(self):
  with tempfile.TemporaryDirectory() as t:
   T=Path(t)
   for rel in ('site/eleve/data/eleves/catalogue.json','site/eleve/labo/data/catalogue.json','kristals/qc-pri-ma-019/experience/OUTILS_INTERACTIFS_V14.json'):
    p=T/rel;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(R/rel,p)
   p=T/'kristals/qc-pri-ma-019/experience/OUTILS_INTERACTIFS_V14.json';j=json.loads(p.read_text());j['activites'][0]['id']='fractions-3-8';p.write_text(json.dumps(j))
   with self.assertRaisesRegex(ValueError,'ownership mismatch'):compile(T,False)
if __name__=='__main__':unittest.main()
