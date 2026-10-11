"""Ekole v20: the colored frame is persistent, validated, public and backwards-compatible."""
from __future__ import annotations
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
from serve_enseignant import create_handler

LEGACY={'format':'ekole.image-frames/1.0','style':'carte','size':'normal'}

class ColoredFrameApiTest(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.root=pathlib.Path(self.temp.name)
        self.path=self.root/'site/eleve/data/cadres-images.json'
        self.path.parent.mkdir(parents=True)
        self.path.write_text(json.dumps(LEGACY),encoding='utf-8')
        self.server=http.server.ThreadingHTTPServer(('127.0.0.1',0),create_handler(self.root,'session_test_key'))
        self.thread=threading.Thread(target=self.server.serve_forever,daemon=True)
        self.thread.start()
        self.host='127.0.0.1';self.port=self.server.server_port
        self.auth={'Cookie':'EkoleTeacher=session_test_key'}
        self.origin=f'http://127.0.0.1:{self.port}'
    def tearDown(self):
        self.server.shutdown();self.server.server_close();self.thread.join();self.temp.cleanup()
    def req(self,method,path,body=None,headers=None):
        con=http.client.HTTPConnection(self.host,self.port,timeout=7)
        con.request(method,path,body=body,headers=headers or {})
        response=con.getresponse();code=response.status;raw=response.read();con.close()
        return code,raw
    def csrf(self):
        code,data=self.req('GET','/api/image-editor-config.json',headers=self.auth)
        self.assertEqual(code,200)
        return json.loads(data)['csrf']
    def save(self,cfg,override=None):
        data=json.dumps(cfg).encode('utf-8')
        headers={**self.auth,'Origin':self.origin,'Content-Type':'application/json','X-Ekole-CSRF':self.csrf(),**(override or {})}
        return self.req('POST','/api/cadres-images.json',data,headers)
    def test_legacy_configuration_keeps_previous_selection(self):
        code,raw=self.req('GET','/api/cadres-images.json',headers=self.auth)
        self.assertEqual(code,200)
        self.assertEqual(json.loads(raw),LEGACY)
        self.assertEqual(self.save(LEGACY)[0],200)
        self.assertEqual(json.loads(self.path.read_text(encoding='utf-8')),LEGACY)
    def test_colored_border_round_trip(self):
        cfg={**LEGACY,'style':'bordure','borderColor':'#1e6864'}
        code,raw=self.save(cfg)
        self.assertEqual(code,200,raw)
        self.assertEqual(json.loads(raw),cfg)
        self.assertEqual(json.loads(self.path.read_text(encoding='utf-8')),cfg)
        custom={**cfg,'borderColor':'#D45D19'}
        code,raw=self.save(custom)
        self.assertEqual(code,200,raw)
        self.assertEqual(json.loads(raw)['borderColor'],'#d45d19')
    def test_rejects_invalid_or_injected_colors(self):
        baseline=self.path.read_bytes()
        for color in ['red','#fff','#12345g','#12345678','var(--x)','url(javascript:alert(1))','black;position:fixed',None,123]:
            with self.subTest(color=color):
                cfg={**LEGACY,'style':'bordure','borderColor':color}
                self.assertEqual(self.save(cfg)[0],422)
                self.assertEqual(self.path.read_bytes(),baseline)
        cfg={**LEGACY,'style':'bordure','borderColor':'#1e6864','extra':'unexpected'}
        self.assertEqual(self.save(cfg)[0],422)
    def test_old_payload_can_request_new_style_with_default(self):
        cfg={**LEGACY,'style':'bordure'}
        code,data=self.save(cfg)
        self.assertEqual(code,200,data)
        self.assertEqual(json.loads(data)['borderColor'],'#1e6864')
    def test_configuration_requires_teacher_and_same_origin(self):
        cfg={**LEGACY,'style':'bordure','borderColor':'#1e6864'}
        code,_=self.req('GET','/api/cadres-images.json')
        self.assertEqual(code,401)
        code,_=self.save(cfg,{'Origin':'http://attacker.example'})
        self.assertEqual(code,403)
        code,_=self.save(cfg,{'X-Ekole-CSRF':'wrong'})
        self.assertEqual(code,403)
        self.assertEqual(json.loads(self.path.read_text(encoding='utf-8')),LEGACY)

class ColoredFrameAssetsTest(unittest.TestCase):
    def test_css_preserves_math_illustrations_and_placeholder(self):
        css=(ROOT/'site/eleve/cadres-images.css').read_text(encoding='utf-8')
        self.assertIn('data-image-frame="bordure"',css)
        self.assertIn('border:5px solid var(--ekole-image-border-color,#1e6864)',css)
        self.assertIn('has-media:not(.kristal-visual-compact)',css)
        self.assertIn('object-fit:contain',css)
        self.assertIn('kristal-visual-compact',css)
        self.assertNotIn('object-fit:cover',css.split('/* 7. Colored frame.')[1])
    def test_student_live_reload_and_teacher_live_preview(self):
        student=(ROOT/'site/eleve/app.js').read_text(encoding='utf-8')
        teacher=(ROOT/'enseignant-app/cadres-images/app.js').read_text(encoding='utf-8')
        html=(ROOT/'enseignant-app/cadres-images/index.html').read_text(encoding='utf-8')
        self.assertIn('--ekole-image-border-color',student)
        self.assertIn('visibilitychange',student)
        self.assertIn('bordure',student)
        self.assertIn('borderColorPicker',html)
        self.assertIn('borderColorHex',html)
        self.assertIn("DEFAULT_COLOR='#1e6864'",teacher)
        self.assertIn('saved.borderColor',teacher)
    def test_configurable_color_has_legacy_default(self):
        teacher=(ROOT/'enseignant-app/cadres-images/app.js').read_text(encoding='utf-8')
        student=(ROOT/'site/eleve/app.js').read_text(encoding='utf-8')
        self.assertIn("validHex(conf.borderColor)?conf.borderColor.toLowerCase():DEFAULT_COLOR",teacher)
        self.assertIn("frameConfig.borderColor||''",student)

if __name__=='__main__':unittest.main()
