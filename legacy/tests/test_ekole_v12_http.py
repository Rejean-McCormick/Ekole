from __future__ import annotations
import json, pathlib, sys, unittest, http.server, threading, urllib.request, urllib.error
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from serve_enseignant import create_handler
class TestTeacherStudio(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.server=http.server.ThreadingHTTPServer(('127.0.0.1',0),create_handler(ROOT,'v12-test-token'))
  cls.thread=threading.Thread(target=cls.server.serve_forever,daemon=True);cls.thread.start()
  cls.url=f'http://127.0.0.1:{cls.server.server_port}'
 @classmethod
 def tearDownClass(cls):cls.server.shutdown();cls.server.server_close();cls.thread.join(timeout=2)
 def get(self,path,cookie=False):
  request=urllib.request.Request(self.url+path)
  if cookie:request.add_header('Cookie','EkoleTeacher=v12-test-token')
  try:
   with urllib.request.urlopen(request,timeout=3) as r:return r.status,r.read()
  except urllib.error.HTTPError as e:return e.code,e.read()
 def test_requires_session(self):
  for path in ['/atelier-v12/','/api/plan-v12.json','/api/cadre-v12/qc-pri-ma-012.json']:
   self.assertEqual(self.get(path)[0],401)
 def test_teacher_studio(self):
  self.assertEqual(self.get('/atelier-v12/',True)[0],200)
  self.assertEqual(self.get('/atelier-v12/app.js',True)[0],200)
  code,raw=self.get('/api/plan-v12.json',True);self.assertEqual(code,200);self.assertEqual(json.loads(raw)['total'],202)
  code,raw=self.get('/api/cadre-v12/qc-pri-ma-012.json',True);self.assertEqual(code,200);self.assertIn('visuels_conceptuels',json.loads(raw))
 def test_invalid_id_not_exposed(self):self.assertEqual(self.get('/api/cadre-v12/../../secret.json',True)[0],404)
if __name__=='__main__':unittest.main()
