"""Non-destructive tests for the Ekole OpsConsole local API and policies."""
import json
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import ekole_ops as ops

class OpsConsoleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ops.ThreadingHTTPServer(('127.0.0.1',0), ops.Handler)
        cls.thread = threading.Thread(target=cls.server.serve_forever,daemon=True)
        cls.thread.start()
        cls.base = 'http://127.0.0.1:' + str(cls.server.server_port)

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=2)

    def request(self, route, *, action=None, token=None, origin=None):
        if action is None:
            req = urllib.request.Request(self.base+route)
        else:
            headers={'Content-Type':'application/json','X-Ekole-Token':token or ''}
            if origin: headers['Origin']=origin
            req=urllib.request.Request(self.base+route, data=json.dumps(action).encode(),headers=headers,method='POST')
        try:
            with urllib.request.urlopen(req,timeout=10) as resp:
                return resp.status,resp.read(),resp.headers
        except urllib.error.HTTPError as e:
            return e.code,e.read(),e.headers

    def test_layout(self):
        self.assertTrue(ops.check_install()['success'])
        self.assertTrue((ops.ROOT/'site/index.html').exists())

    def test_overview_and_catalog(self):
        r=ops.overview()
        self.assertEqual(r['catalog']['declared'],202)
        self.assertEqual(len(ops.courses()['courses']),202)

    def test_detail(self):
        d=ops.inspect_kristal('qc-pri-ma-001')
        self.assertEqual(d['record']['id'],'qc-pri-ma-001')
        self.assertEqual(d['files']['count'],14)
        self.assertGreaterEqual(d['evaluation']['items'],8)

    def test_path_rejection(self):
        for path in [str(ops.ROOT),str(ops.ROOT/'site'),str(ops.ROOT/'export'),'', ' '*2]:
            with self.subTest(path=path), self.assertRaises(ValueError):ops.check_target(path)
        with self.assertRaises(ValueError):ops.inspect_kristal('../../invalid')

    def test_http_index_and_health(self):
        status,payload,headers=self.request('/')
        self.assertEqual(status,200)
        self.assertIn(b'Ekole',payload)
        self.assertIn(ops.service.token.encode(),payload)
        self.assertIn('no-store',headers['Cache-Control'])
        status,payload,_=self.request('/api/health')
        self.assertEqual(status,200)
        self.assertTrue(json.loads(payload)['success'])

    def test_http_course_inspection(self):
        status,payload,_=self.request('/api/course?id=qc-pri-fr-004')
        self.assertEqual(status,200)
        self.assertEqual(json.loads(payload)['record']['id'],'qc-pri-fr-004')
        status,payload,_=self.request('/api/course?id=..%2F..%2Fetc')
        self.assertEqual(status,400)

    def test_no_post_without_token(self):
        status,_,_=self.request('/api/action',action={'action':'build'})
        self.assertEqual(status,403)

    def test_origin_check(self):
        status,_,_=self.request('/api/action',action={'action':'verify'},token=ops.service.token,origin='https://evil.example')
        self.assertEqual(status,403)

    def test_unknown_action_rejected(self):
        status,payload,_=self.request('/api/action',action={'action':'git-push'},token=ops.service.token)
        self.assertEqual(status,400)
        self.assertIn('refus',json.loads(payload)['error'])

    def test_local_deploy_requires_simulation(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError):
                ops.service.action({'action':'deploy-local-apply','target':d,'confirmation':ops.LOCAL_CONFIRMATION})

    def test_safe_public_export(self):
        ops.verify_public_files()

if __name__=='__main__': unittest.main()
