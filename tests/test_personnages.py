"""Contrats visuels inter-dépôts et accès public séparé des visuels Kristal."""
import copy
import http.server
import json
from pathlib import Path
import struct
import sys
import tempfile
import threading
import unittest
import urllib.request
import urllib.error
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import personnages
from launcher import Environment, create_handler, ENGINE
ROOT=ENGINE.parent
CAT=ROOT/'ekole-quebec/personnages/catalogue.json'

class CatalogueTests(unittest.TestCase):
    def setUp(self):self.data=json.loads(CAT.read_text(encoding='utf-8'))
    def test_cross_repo_roles_and_companions(self):
        personnages.validate(self.data)
        roles=[json.loads(p.read_text(encoding='utf-8')) for p in (ROOT/'Kontexte/data/roles').glob('*.json')]
        self.assertEqual(len(roles),38)
        assets={a['id']:a for a in self.data['assets']}
        self.assertEqual(len(assets),80)
        self.assertEqual({a['role_id'] for a in assets.values() if a['type']=='role'},{r['id'] for r in roles})
        for r in roles:self.assertEqual(assets[r['visual_id']]['role_id'],r['id'])
        self.assertEqual(len(self.data['compagnons']),5)
        self.assertEqual(self.data['anciens_choix']['cosmos'],'extraterrestre')
        self.assertNotEqual(assets['role-explorateur']['id'],assets['role-extraterrestre']['id'])
    def test_unique_slots_and_safe_paths(self):
        for mutation in ('duplicate','path','year','missing'):
            data=copy.deepcopy(self.data)
            if mutation=='duplicate':data['assets'].append(copy.deepcopy(data['assets'][0]))
            elif mutation=='path':data['assets'][0]['fichier']='images/../../private.png'
            elif mutation=='year':data['assets'][0]['annee']=True
            else:data['assets'].pop(0)
            with self.subTest(mutation=mutation),self.assertRaises(ValueError):personnages.validate(data)
    def test_images_require_review_presence_and_png(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);a=copy.deepcopy(self.data['assets'][0]);p=root/a['fichier'];p.parent.mkdir(parents=True)
            # En-tête suffisant pour le contrôle stdlib; aucun visuel de production créé.
            p.write_bytes(b'\x89PNG\r\n\x1a\n'+struct.pack('>I',13)+b'IHDR'+struct.pack('>II',512,512)+b'\x08\x06\x00\x00\x00'+b'\x00'*4)
            self.assertIsNone(personnages.png(root,a))
            a['statut']='pret';self.assertEqual(personnages.png(root,a),p)
            p.write_bytes(b'x'*33);self.assertIsNone(personnages.png(root,a))
            p.unlink();p.symlink_to(CAT)
            with self.assertRaises(ValueError):personnages.png(root,a)
    def test_empty_pack_and_parent_symlink(self):
        self.assertEqual(personnages.public_inventory(None)['assets'],[])
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);(root/'images').symlink_to(ROOT,target_is_directory=True)
            with self.assertRaises(ValueError):personnages.safe_file(root,'images/private.png')

class ApiTests(unittest.TestCase):
    def test_ready_png_is_served_by_id_only(self):
        import zlib
        def chunk(kind,payload):
            return struct.pack('>I',len(payload))+kind+payload+struct.pack('>I',zlib.crc32(kind+payload)&0xffffffff)
        raw=b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>II',1,1)+b'\x08\x06\x00\x00\x00')+chunk(b'IDAT',zlib.compress(b'\x00\x11\x22\x33\x44'))+chunk(b'IEND',b'')
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);folder=root/'personnages';folder.mkdir()
            pack={'format':'ekole.content-pack/0.1','id':'test','nom':'Test','cours':[],'parcours':[],'personnages':'personnages/catalogue.json'}
            (root/'pack.json').write_text(json.dumps(pack))
            data=json.loads(CAT.read_text(encoding='utf-8'));asset=data['assets'][0];asset['statut']='pret'
            (folder/'catalogue.json').write_text(json.dumps(data))
            path=folder/asset['fichier'];path.parent.mkdir(parents=True);path.write_bytes(raw)
            server=http.server.ThreadingHTTPServer(('127.0.0.1',0),create_handler(Environment(root,False)))
            thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
            url=f'http://127.0.0.1:{server.server_port}'
            try:
                with urllib.request.urlopen(url+'/api/personnages/catalogue.json') as res:public=json.load(res)
                self.assertEqual(sum(a['disponible'] for a in public['assets']),1)
                with urllib.request.urlopen(url+'/api/personnages/image/'+asset['id']) as res:
                    self.assertEqual(res.headers['Content-Type'],'image/png');self.assertEqual(res.read(),raw)
            finally:server.shutdown();server.server_close();thread.join()

    def test_catalogue_and_unavailable_images(self):
        server=http.server.ThreadingHTTPServer(('127.0.0.1',0),create_handler(Environment(ROOT/'ekole-quebec',False)))
        thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
        url=f'http://127.0.0.1:{server.server_port}'
        try:
            with urllib.request.urlopen(url+'/api/personnages/catalogue.json') as res:data=json.load(res)
            self.assertEqual(len(data['assets']),80)
            self.assertTrue(all(a['url'] is None and not a['disponible'] for a in data['assets']))
            self.assertTrue(all('fichier' not in a and 'prompt' not in a for a in data['assets']))
            for id in ('role-fermier','unknown','%2e%2e%2fpack.json'):
                with self.assertRaises(urllib.error.HTTPError) as e:urllib.request.urlopen(url+'/api/personnages/image/'+id)
                self.assertEqual(e.exception.code,404);e.exception.close()
        finally:server.shutdown();server.server_close();thread.join()

if __name__=='__main__':unittest.main()
