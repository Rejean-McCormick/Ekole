"""Contrats autonomes Tandem Ekole: sans enfants, DB, Orgo ou serveur distant."""
from __future__ import annotations
import copy
import http.server
import json
from http.cookiejar import CookieJar
from pathlib import Path
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from launcher import ENGINE, Environment, create_handler
from tandem import load_synthetic_preview, validate_synthetic_preview, PreviewError

EXAMPLE=ENGINE/'tandem'/'fixtures'/'fete-sorciere.synthetic.json'

class ProjectionTests(unittest.TestCase):
    def setUp(self):
        self.example=load_synthetic_preview(EXAMPLE)
    def check_bad(self, change):
        doc=copy.deepcopy(self.example)
        change(doc)
        with self.assertRaises(PreviewError):validate_synthetic_preview(doc)
    def test_valid_fixture(self):
        self.assertEqual(len(self.example['tasks']),4)
    def test_scope_invalid(self):
        self.check_bad(lambda x:x.update(world_id='not-a-uuid'))
    def test_missing_release(self):
        self.check_bad(lambda x:x.pop('world_release_id'))
    def test_wrong_mode(self):
        self.check_bad(lambda x:x.update(mode='real'))
    def test_wrong_authority(self):
        self.check_bad(lambda x:x.update(authority='ekole'))
    def test_student_personal_data_forbidden(self):
        self.check_bad(lambda x:x['tasks'][0].update(learner_name='Prénom'))
    def test_media_payload_forbidden(self):
        self.check_bad(lambda x:x['tasks'][0].update(photo_url='https://example.org/private.jpg'))
    def test_unknown_root_field_forbidden(self):
        self.check_bad(lambda x:x.update(tenant_override='another'))
    def test_duplicate_task(self):
        self.check_bad(lambda x:x['tasks'].append(copy.deepcopy(x['tasks'][0])))
    def test_unsafe_fragment(self):
        self.check_bad(lambda x:x['tasks'][0]['fragment_refs'].append('../private'))
    def test_unknown_state(self):
        self.check_bad(lambda x:x['tasks'][0].update(state='APPROVED_FOR_REAL_PAYMENT'))
    def test_nonstring_state_fail_closed(self):
        self.check_bad(lambda x:x['tasks'][0].update(state=['done']))
    def test_nonstring_fragment_fail_closed(self):
        self.check_bad(lambda x:x['tasks'][0]['fragment_refs'].append({'url':'secret'}))
    def test_duplicate_fragment(self):
        self.check_bad(lambda x:x['tasks'][0]['fragment_refs'].append('lanternes'))
    def test_missing_file(self):
        with self.assertRaises(PreviewError):load_synthetic_preview(EXAMPLE.parent/'missing.json')
    def test_duplicate_json_key(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'file.json';p.write_text('{"a":1,"a":2}',encoding='utf-8')
            with self.assertRaisesRegex(PreviewError,'dupliquée'):load_synthetic_preview(p)
    def test_large_file(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'file.json';p.write_text('0'*131073,encoding='utf-8')
            with self.assertRaises(PreviewError):load_synthetic_preview(p)
    def test_default_disabled_and_public_access_denied(self):
        self.assertIsNone(Environment(None,False).tandem_preview)
        env=Environment(None,False,tandem_preview=self.example)
        self.assertEqual(env.tandem_preview['mode'],'synthetic')
        public=http.server.ThreadingHTTPServer(('127.0.0.1',0),create_handler(env))
        teacher=http.server.ThreadingHTTPServer(('127.0.0.1',0),create_handler(env,True))
        threads=[]
        for srv in (public,teacher):
            th=threading.Thread(target=srv.serve_forever,daemon=True);th.start();threads.append(th)
        try:
            purl=f'http://127.0.0.1:{public.server_port}/api/tandem/preview.json'
            turl=f'http://127.0.0.1:{teacher.server_port}'
            with self.assertRaises(urllib.error.HTTPError) as pub:
                urllib.request.urlopen(purl,timeout=3)
            self.assertEqual(pub.exception.code,404);pub.exception.close()
            with self.assertRaises(urllib.error.HTTPError) as unauth:
                urllib.request.urlopen(turl+'/api/tandem/preview.json',timeout=3)
            self.assertEqual(unauth.exception.code,401);unauth.exception.close()
            opener=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(CookieJar()))
            with opener.open(turl+'/open?key='+env.key,timeout=3):pass
            with opener.open(turl+'/api/tandem/preview.json',timeout=3) as reply:
                projection=json.load(reply)
                self.assertEqual(projection,self.example)
                self.assertNotIn('learner_name',reply.headers)
        finally:
            for srv in (public,teacher):srv.shutdown();srv.server_close()
            for th in threads:th.join(timeout=4)

if __name__=='__main__':unittest.main()
