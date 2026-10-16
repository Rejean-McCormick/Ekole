import importlib.util,json,pathlib,tempfile,unittest,threading,urllib.request,urllib.error,secrets,shutil
ROOT=pathlib.Path(__file__).resolve().parents[1]
SERVER=ROOT/'tools/serve_enseignant.py'
spec=importlib.util.spec_from_file_location('serve_enseignant_v7',SERVER)
server=importlib.util.module_from_spec(spec);spec.loader.exec_module(server)
spec2=importlib.util.spec_from_file_location('export_enfant_v7',ROOT/'tools/export_ekole_eleve_v7.py')
exporter=importlib.util.module_from_spec(spec2);spec2.loader.exec_module(exporter)
class TestThreeApps(unittest.TestCase):
 def test_three_starts(self):
  self.assertIn('Ekole Core',(ROOT/'site/index.html').read_text(encoding='utf-8'))
  self.assertTrue((ROOT/'site/eleve/index.html').is_file())
  self.assertTrue((ROOT/'enseignant-app/index.html').is_file())
 def test_visual_registry(self):
  j=json.loads((ROOT/'visuels/INTENTIONS_IMAGES.json').read_text())
  intents=j['intents'];ids=[x['visual_id'] for x in intents]
  self.assertEqual(len(intents),227);self.assertEqual(len(ids),len(set(ids)))
  self.assertEqual(len([x for x in intents if x.get('kristal_id')]),202)
  self.assertTrue(all(x['asset_path_actuel'] is None and x['status']=='non_generee' and x['prompt_image'] for x in intents))
 def test_public_visuels_exclude_prompts(self):
  p=json.loads((ROOT/'site/eleve/data/visuels_public.json').read_text())
  self.assertEqual(len(p['placeholders']),226)
  self.assertNotIn('prompt_image',p['placeholders'][0])
 def test_konstellation_link_not_false_v10(self):
  j=json.loads((ROOT/'site/eleve/data/konstellation-liens.json').read_text())
  self.assertFalse(j['verified_public_v10']);self.assertIsNone(j['public_collection_url'])
  self.assertEqual(j['preview_local_url'],'http://127.0.0.1:4177/')
 def test_student_export_isolated(self):
  with tempfile.TemporaryDirectory() as td:
   out=pathlib.Path(td)/'student'; n=exporter.export(ROOT,out)
   self.assertEqual(n,9);self.assertFalse((out/'data/cours').exists())
   self.assertFalse((out/'enseignant-app').exists());self.assertFalse((out/'data/index.json').exists())
 def test_teacher_requires_cookie(self):
  from http.server import ThreadingHTTPServer
  token=secrets.token_urlsafe(32)
  srv=ThreadingHTTPServer(('127.0.0.1',0),server.create_handler(ROOT,token))
  t=threading.Thread(target=srv.serve_forever,daemon=True);t.start()
  base='http://127.0.0.1:'+str(srv.server_port)
  try:
   with self.assertRaises(urllib.error.HTTPError) as c:
    urllib.request.urlopen(base+'/api/visuals.json',timeout=3)
   self.assertEqual(c.exception.code,401)
   with self.assertRaises(urllib.error.HTTPError) as c:
    urllib.request.urlopen(base+'/api/course/../../file.json',timeout=3)
   self.assertEqual(c.exception.code,401)
   req=urllib.request.Request(base+'/api/visuals.json',headers={'Cookie':'EkoleTeacher='+token})
   with urllib.request.urlopen(req,timeout=3) as r:
    self.assertEqual(r.status,200);j=json.load(r)
   self.assertEqual(len(j['intents']),227)
   req=urllib.request.Request(base+'/api/course/qc-pri-ma-012.json',headers={'Cookie':'EkoleTeacher='+token})
   with urllib.request.urlopen(req,timeout=3) as r:self.assertEqual(r.status,200)
  finally:srv.shutdown();srv.server_close()
 def test_no_api_secrets_student(self):
  for x in (ROOT/'site/eleve').rglob('*'):
   if x.is_file() and x.suffix in ('.js','.json','.html'):
    c=x.read_text(encoding='utf-8')
    self.assertNotIn('BANQUE_ITEMS',c)
if __name__=='__main__':unittest.main()
