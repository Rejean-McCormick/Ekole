"""Contrats de l'album d'images Enseignant v21."""
import http.client
import http.server
import json
import pathlib
import sys
import tempfile
import threading
import unittest

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from inventaire_images_v21 import inventory
from serve_enseignant import create_handler

class InventoryTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.root=pathlib.Path(self.temp.name)
        (self.root/'site/eleve/data/eleves').mkdir(parents=True)
        (self.root/'site/eleve/data/eleves/catalogue.json').write_text(json.dumps({'courses':[{'id':'qc-pri-ma-012','title':'Fractions','year_suggestion':3,'step_suggestion':2,'subject':'Mathématique'}]}),encoding='utf-8')
        (self.root/'site/eleve/data/kristals-visuels.json').write_text(json.dumps({'cours':{'qc-pri-ma-012':{'visuels':[{'slot':'concept','url':None}]}}}),encoding='utf-8')
        w=self.root/'kristals/qc-pri-ma-012/experience'
        w.mkdir(parents=True)
        (w/'RESSOURCES_VISUELLES.json').write_text(json.dumps({'visuels':[{'slot':'concept','prompt_conceptuel':'Prompt de test long','placement':'decouvrir'},{'slot':'situation','prompt_conceptuel':'Second prompt'}]}),encoding='utf-8')
        self.ws=w
    def tearDown(self):self.temp.cleanup()
    def test_scan_without_side_effect(self):
        one=inventory(self.root)
        self.assertEqual(one['slot_count'],2)
        self.assertEqual(one['counts']['manquante'],2)
        self.assertEqual(one['items'][0]['year'],3)
        self.assertTrue(one['items'][0]['editable'])
        self.assertEqual(one['items'][0]['prompt'],'Prompt de test long')
    def test_file_presence_vs_publication_and_orphans(self):
        p=self.ws/'images';p.mkdir()
        (p/'concept.webp').write_bytes(b'imagedata-not-reviewed')
        (p/'unassigned.webp').write_bytes(b'imagedata')
        one=inventory(self.root)
        self.assertEqual(one['counts']['a_synchroniser'],1)
        self.assertEqual(one['orphan_count'],1)
        self.assertEqual((p/'unassigned.webp').read_bytes(),b'imagedata')
        pub=self.root/'site/eleve/data/kristals-visuels.json'
        pub.write_text(json.dumps({'cours':{'qc-pri-ma-012':{'visuels':[{'slot':'concept','url':'assets/kristals/qc-pri-ma-012/concept.webp','revision':'abc'}]}}}),encoding='utf-8')
        one=inventory(self.root)
        self.assertEqual(one['counts']['presente'],1)
    def test_draft_is_visible_not_editable(self):
        (self.root/'kristals/qc-pri-ma-012/experience/RESSOURCES_VISUELLES.json').unlink()
        p=self.root/'visuels/KRISTALS_SANS_SOURCE.json';p.parent.mkdir()
        p.write_text(json.dumps({'cours_sans_source':{'qc-pri-ma-012':{'visuels':[{'slot':'concept','prompt_conceptuel':'Prompts brouillon'}]}}}),encoding='utf-8')
        entry=inventory(self.root)['items'][0]
        self.assertFalse(entry['editable'])
        self.assertEqual(entry['status'],'source_absente')

class AlbumHttpTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server=http.server.ThreadingHTTPServer(('127.0.0.1',0),create_handler(ROOT,'demo_token'))
        cls.thread=threading.Thread(target=cls.server.serve_forever,daemon=True);cls.thread.start()
        cls.origin='http://127.0.0.1:'+str(cls.server.server_port)
    @classmethod
    def tearDownClass(cls):cls.server.shutdown();cls.server.server_close();cls.thread.join(timeout=2)
    def req(self,method,path,headers=None):
        c=http.client.HTTPConnection('127.0.0.1',self.server.server_port,timeout=12)
        c.request(method,path,headers=headers or {})
        r=c.getresponse();body=r.read();code=r.status;c.close();return code,body
    def test_requires_teacher_session(self):
        self.assertEqual(self.req('GET','/images-album/')[0],401)
        self.assertEqual(self.req('GET','/api/images-album.json')[0],401)
        self.assertEqual(self.req('POST','/api/images-album/recompiler')[0],401)
    def test_album_and_inventory_auth(self):
        auth={'Cookie':'EkoleTeacher=demo_token'}
        code,body=self.req('GET','/images-album/',auth)
        self.assertEqual(code,200);self.assertIn(b'INVENTAIRE',body)
        code,body=self.req('GET','/images-album/app.js',auth)
        self.assertEqual(code,200);self.assertIn(b'Copier le prompt',body)
        code,body=self.req('GET','/api/images-album.json',auth)
        self.assertEqual(code,200);self.assertEqual(json.loads(body)['course_count'],202)
    def test_sync_rejects_origin_and_csrf(self):
        auth={'Cookie':'EkoleTeacher=demo_token'}
        self.assertEqual(self.req('POST','/api/images-album/recompiler',auth)[0],403)
        self.assertEqual(self.req('POST','/api/images-album/recompiler',{**auth,'Origin':self.origin})[0],403)
    def test_sync_authenticated(self):
        auth={'Cookie':'EkoleTeacher=demo_token'}
        code,body=self.req('GET','/api/image-editor-config.json',auth)
        self.assertEqual(code,200)
        csrf=json.loads(body)['csrf']
        code,body=self.req('POST','/api/images-album/recompiler',{**auth,'Origin':self.origin,'X-Ekole-CSRF':csrf})
        self.assertEqual(code,200)
        self.assertEqual(json.loads(body)['course_count'],202)
    def test_path_not_exposed(self):
        self.assertEqual(self.req('GET','/images-album/../serve_enseignant.py',{'Cookie':'EkoleTeacher=demo_token'})[0],404)

if __name__=='__main__':unittest.main()
