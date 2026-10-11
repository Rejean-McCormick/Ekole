"""Local teacher-image upload integration: permissions, slots, normalization, rollback."""
import http.client, http.server, io, json, pathlib, socket, sys, tempfile, threading, unittest
from PIL import Image

TOOLS=pathlib.Path(__file__).resolve().parents[1]/'tools'
sys.path.insert(0,str(TOOLS))
from serve_enseignant import create_handler

class ImageEditorV15Test(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=pathlib.Path(self.tmp.name)
        kid='qc-pri-ma-012'
        p=self.root/'kristals'/kid/'experience';p.mkdir(parents=True)
        data={'format':'ekole.kristal-visual-layer/1.0','kristal_id':kid,'visuels':[{'slot':'concept','prompt_conceptuel':'Description pedagogique conceptuelle complete sans style impose et sans solution en image.'}]}
        (p/'RESSOURCES_VISUELLES.json').write_text(json.dumps(data),encoding='utf-8')
        cat=self.root/'site/eleve/data/eleves';cat.mkdir(parents=True)
        (cat/'catalogue.json').write_text(json.dumps({'courses':[{'id':kid,'title':'Fractions'}]}),encoding='utf-8')
        vs=self.root/'visuels';vs.mkdir()
        (vs/'KRISTALS_SANS_SOURCE.json').write_text('{}',encoding='utf-8')
        self.server=http.server.ThreadingHTTPServer(('127.0.0.1',0),create_handler(self.root,'test_session_token'))
        self.port=self.server.server_port
        self.thread=threading.Thread(target=self.server.serve_forever,daemon=True);self.thread.start()
        self.cookie='EkoleTeacher=test_session_token';self.origin=f'http://127.0.0.1:{self.port}'
    def tearDown(self):
        self.server.shutdown();self.server.server_close();self.thread.join();self.tmp.cleanup()
    def call(self,method,path,body=None,headers=None):
        conn=http.client.HTTPConnection('127.0.0.1',self.port,timeout=12)
        conn.request(method,path,body=body,headers=headers or {})
        r=conn.getresponse();data=r.read();status=r.status;conn.close();return status,data
    def session(self):
        status,raw=self.call('GET','/api/image-editor-config.json',headers={'Cookie':self.cookie})
        self.assertEqual(status,200);return json.loads(raw)['csrf']
    def png(self):
        out=io.BytesIO();Image.new('RGB',(800,400),'#aadede').save(out,'PNG');return out.getvalue()
    def upload(self,raw,token=None,replace=False,slot='concept',imageformat='webp',origin=None):
        return self.call('POST',f'/api/visual-upload/qc-pri-ma-012/{slot}',raw,{'Cookie':self.cookie,'Origin':self.origin if origin is None else origin,'X-Ekole-CSRF':token if token is not None else self.session(),'X-Ekole-Format':imageformat,'X-Ekole-Max-Width':'768','X-Ekole-Replace':'yes' if replace else 'no','Content-Type':'application/octet-stream'})
    def test_cannot_use_without_session_or_csrf_or_origin(self):
        raw=self.png();csrf=self.session()
        c,b=self.call('POST','/api/visual-upload/qc-pri-ma-012/concept',raw,{'Origin':self.origin,'X-Ekole-CSRF':csrf,'Content-Type':'application/octet-stream'})
        self.assertEqual(c,401)
        self.assertEqual(self.upload(raw,token='bad')[0],403)
        self.assertEqual(self.upload(raw,token=csrf,origin='http://attacker.invalid')[0],403)
        self.assertEqual(self.upload(raw,slot='secret-data')[0],422)
    def test_roundtrip_resize_recompile_and_explicit_replace(self):
        img=self.png();status,raw=self.upload(img)
        self.assertEqual(status,201,raw.decode());output=json.loads(raw)
        self.assertEqual(output['file_name'],'concept.webp');self.assertEqual((output['width'],output['height']),(768,384))
        path=self.root/'kristals/qc-pri-ma-012/experience/images/concept.webp'
        self.assertTrue(path.is_file())
        public=json.loads((self.root/'site/eleve/data/kristals-visuels.json').read_text())
        self.assertEqual(public['cours']['qc-pri-ma-012']['visuels'][0]['url'],'assets/kristals/qc-pri-ma-012/concept.webp')
        self.assertEqual(self.upload(img)[0],409)
        s,b=self.upload(img,replace=True,imageformat='png')
        self.assertEqual(s,201,b.decode());self.assertFalse(path.exists())
        self.assertTrue((path.parent/'concept.png').exists())
        self.assertEqual(len(list((self.root/'archives/ekole-images/qc-pri-ma-012').glob('*.bak'))),1)
    def test_reject_garbage(self):
        self.assertEqual(self.upload(b'NOT_IMAGE'*100)[0],422)
    def test_no_student_upload_route(self):
        self.assertEqual(self.call('GET','/api/visual-upload/qc-pri-ma-012/concept',headers={'Cookie':self.cookie})[0],404)
if __name__=='__main__':unittest.main()
