"""Tests du contrat moteur/paquet, des serveurs et de la session locale."""
from __future__ import annotations
import hashlib
import http.server
import json
import pathlib
import sys
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from http.cookiejar import CookieJar
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]))
from launcher import ENGINE, Environment, create_handler, load_pack

CONTENT=ENGINE.parent/'ekole-quebec'


def request(url, *, data=None, headers=None, opener=None):
    req=urllib.request.Request(url,data=data,headers=headers or {})
    return opener.open(req,timeout=3) if opener else urllib.request.urlopen(req,timeout=3)

class PackTests(unittest.TestCase):
    def test_content_pack_and_originals(self):
        self.assertEqual(len(load_pack(CONTENT)['cours']),202)
        sha=json.loads((CONTENT/'CONTROLE_COURS_SHA256.json').read_text(encoding='utf-8'))
        self.assertEqual(len(sha),202)
        for filename,digest in sha.items():
            source=(CONTENT/'historique/clients/site/data/cours'/filename)
            current=(CONTENT/'cours'/filename)
            self.assertTrue(source.is_file() and current.is_file())
            self.assertEqual(hashlib.sha256(source.read_bytes()).hexdigest(),digest)
            self.assertEqual(hashlib.sha256(current.read_bytes()).hexdigest(),digest)

    def test_engine_starts_without_content(self):
        pack=load_pack(None)
        self.assertEqual(pack['cours'],[])
        self.assertEqual(Environment(None,False).pack['id'],'sans-contenu')

    def test_invalid_reference_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root=pathlib.Path(td)
            (root/'pack.json').write_text(json.dumps({'format':'ekole.content-pack/0.1','id':'bad',
                'nom':'Fake','cours':[{'id':'../secret','titre':'Invalid','fichier':'cours/../secret.json'}],
                'parcours':[]}),encoding='utf8')
            with self.assertRaises(ValueError):load_pack(root)

class ServerTests(unittest.TestCase):
    def setUp(self):
        self.env=Environment(CONTENT, False)
        self.public=http.server.ThreadingHTTPServer(('127.0.0.1',0),create_handler(self.env))
        self.teacher=http.server.ThreadingHTTPServer(('127.0.0.1',0),create_handler(self.env,True))
        self.threads=[]
        for srv in (self.public,self.teacher):
            thread=threading.Thread(target=srv.serve_forever,daemon=True);thread.start();self.threads.append(thread)
        self.public_url=f'http://127.0.0.1:{self.public.server_port}'
        self.teacher_url=f'http://127.0.0.1:{self.teacher.server_port}'

    def tearDown(self):
        for srv in (self.public,self.teacher):srv.shutdown();srv.server_close()
        for thread in self.threads:thread.join(timeout=5)

    def test_navigation_and_modules(self):
        with request(self.public_url+'/api/health') as r:
            self.assertEqual(json.load(r)['cours'],202)
            self.assertEqual(r.headers['X-Content-Type-Options'],'nosniff')
        with request(self.public_url+'/api/pack.json') as r:
            self.assertEqual(len(json.load(r)['parcours']),6)
        with request(self.public_url+'/api/cours/qc-pri-ma-001.json') as r:
            self.assertEqual(json.load(r)['modules'],[])  # Corpus expert jamais publié sans adaptation
        with request(self.public_url+'/eleve/') as r:
            self.assertIn('apprenant',r.read().decode('utf-8').lower())
        with self.assertRaises(urllib.error.HTTPError) as cx:
            request(self.public_url+'/api/cours/nonexistant.json')
        self.assertEqual(cx.exception.code,404)
        cx.exception.close()

    def test_teacher_session_restrictions(self):
        with self.assertRaises(urllib.error.HTTPError) as cm:
            request(self.teacher_url+'/api/pack.json')
        self.assertEqual(cm.exception.code,401)
        cm.exception.close()
        opener=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(CookieJar()))
        with request(self.teacher_url+'/open?key='+self.env.key,opener=opener) as resp:
            self.assertIn('Ekole',resp.read().decode())
        with request(self.teacher_url+'/api/editor-config',opener=opener) as resp:
            self.assertEqual(json.load(resp)['edition'],False)
        with self.assertRaises(urllib.error.HTTPError) as cx:
            request(self.teacher_url+'/api/cours/qc-pri-ma-001.json',opener=opener,
                    data=b'{}',headers={'Content-Type':'application/json','Origin':self.teacher_url,'X-Ekole-CSRF':self.env.csrf})
        self.assertEqual(cx.exception.code,403)
        cx.exception.close()

class EditTests(unittest.TestCase):
    def test_editor_saves_text_with_backup_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=pathlib.Path(tmp)
            (root/'cours').mkdir()
            course={'id':'demo-001','titre':'Démonstration','modules':[{'id':'intro','titre':'Introduction','texte':'Avant'}]}
            raw=(json.dumps(course,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
            (root/'cours/demo-001.json').write_bytes(raw)
            pack={'format':'ekole.content-pack/0.1','id':'demo','nom':'Essai','cours':
                  [{'id':'demo-001','titre':'Démonstration','fichier':'cours/demo-001.json','prerequis':[]}],
                  'parcours':[]}
            (root/'pack.json').write_text(json.dumps(pack),encoding='utf8')
            env=Environment(root,True)
            srv=http.server.ThreadingHTTPServer(('127.0.0.1',0),create_handler(env,True))
            t=threading.Thread(target=srv.serve_forever,daemon=True);t.start()
            try:
                url=f'http://127.0.0.1:{srv.server_port}'
                opener=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(CookieJar()))
                request(url+'/open?key='+env.key,opener=opener).close()
                headers={'Content-Type':'application/json','Origin':url,'X-Ekole-CSRF':env.csrf}
                course['modules'][0]['texte']='Après'
                course['_revision']=hashlib.sha256(raw).hexdigest()
                with request(url+'/api/cours/demo-001.json',opener=opener,headers=headers,
                             data=json.dumps(course,ensure_ascii=False).encode('utf-8')) as resp:
                    result=json.load(resp)
                self.assertEqual(result['resultat'],'enregistre')
                self.assertEqual(json.loads((root/'cours/demo-001.json').read_text(encoding='utf-8'))['modules'][0]['texte'],'Après')
                self.assertIn('Après'.encode('utf-8'), (root/'cours/demo-001.json').read_bytes())
                with request(url+'/api/cours/demo-001.json',opener=opener) as response:
                    self.assertIn('application/json; charset=utf-8',response.headers.get('Content-Type',''))
                    self.assertEqual(json.load(response)['modules'][0]['texte'],'Après')
                self.assertEqual(len(list((root/'cours').glob('*.backup-*'))),1)
                with self.assertRaises(urllib.error.HTTPError) as duplicate:
                    request(url+'/api/cours/demo-001.json',opener=opener,headers=headers,
                            data=json.dumps(course,ensure_ascii=False).encode('utf-8'))
                self.assertEqual(duplicate.exception.code,409)
                duplicate.exception.close()
            finally:
                srv.shutdown();srv.server_close();t.join(timeout=5)

if __name__=='__main__':unittest.main()
