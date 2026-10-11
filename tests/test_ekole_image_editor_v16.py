"""Regression: thumbnail CSP and generated image may be retrieved right after upload."""
from __future__ import annotations
import json, pathlib, sys, unittest, shutil
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tests'))
from test_ekole_image_editor_v15 import ImageEditorV15Test

class ImageEditorV16Test(ImageEditorV15Test):
    def test_live_preview_and_image_retrieval(self):
        teacher=self.root/'enseignant-app';teacher.mkdir(exist_ok=True)
        for filename in ('index.html','style.css'):
            shutil.copyfile(ROOT/'enseignant-app'/filename,teacher/filename)
        token=self.session()
        status,html=self.call('GET','/index.html',headers={'Cookie':self.cookie})
        self.assertEqual(status,200)
        self.assertRegex(html,rb'images-editor-v15[.]js[?]v=(?:16|17)')
        status,css=self.call('GET','/style.css?v=16',headers={'Cookie':self.cookie})
        self.assertEqual(status,200)
        self.assertIn(b'.button.is-copied',css)
        status,raw=self.upload(self.png(),token=token)
        self.assertEqual(status,201,raw.decode())
        saved=json.loads(raw)
        self.assertEqual(saved['public_url'],'assets/kristals/qc-pri-ma-012/concept.webp')
        status,image=self.call('GET','/api/kristal-image/qc-pri-ma-012/concept.webp?v='+saved['sha256'][:24],headers={'Cookie':self.cookie})
        self.assertEqual(status,200)
        self.assertTrue(image.startswith(b'RIFF') and b'WEBP' in image[:20])
        self.assertEqual(self.call('GET','/api/kristal-image/qc-pri-ma-012/concept.webp?v=abc')[0],401)
    def test_editor_csp_allows_blob_thumbnail(self):
        import http.client
        conn=http.client.HTTPConnection('127.0.0.1',self.port,timeout=10)
        conn.request('GET','/',headers={'Cookie':self.cookie})
        response=conn.getresponse()
        self.assertEqual(response.status,404 if not (self.root/'enseignant-app/index.html').exists() else 200)
        self.assertIn("img-src 'self' data: blob:",response.getheader('Content-Security-Policy'))
        response.read();conn.close()

if __name__=='__main__':unittest.main()
