import importlib.util
import json
import pathlib
import subprocess
import tempfile
import unittest
from http.server import ThreadingHTTPServer
from threading import Thread
from urllib.request import urlopen, Request
from urllib.error import HTTPError
ROOT=pathlib.Path(__file__).resolve().parents[1]

class TestMiniLabsV9(unittest.TestCase):
    def test_deterministic_engine(self):
        r=subprocess.run(['node','tests/test_microlab_engine_v9.js','.'],cwd=ROOT,capture_output=True,text=True,timeout=30)
        self.assertEqual(r.returncode,0,msg=r.stderr+r.stdout)
    def test_pilot_links_not_claimed_as_qualification(self):
        c=json.loads((ROOT/'site/eleve/labo/data/catalogue.json').read_text(encoding='utf8'))
        self.assertGreaterEqual(c['count'],20)
        self.assertGreaterEqual(len({a['type'] for a in c['items']}),9)
        self.assertTrue(all(a['status']=='prototype_revue_humaine' and a['validation_mode']=='deterministic_practice' for a in c['items']))
        self.assertTrue(all(a['association_status'] in ('illustration_candidate_non_validee','proposition_ciblee_v14_non_approuvee') for a in c['items'] if a.get('source_kristal_id')))
    def test_student_site_no_teacher_source_bank(self):
        spec=importlib.util.spec_from_file_location('public_export_v8_updated',ROOT/'tools/export_ekole_eleve_v8.py')
        mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
        with tempfile.TemporaryDirectory() as t:
            dest=pathlib.Path(t)/'kid'
            mod.export(ROOT,dest)
            self.assertTrue((dest/'labo/index.html').is_file())
            self.assertTrue((dest/'labo/embed.js').is_file())
            self.assertFalse((dest/'data/cours').exists())
            self.assertFalse((dest/'enseignant-app').exists())
            self.assertFalse((dest/'visuels/INTENTIONS_IMAGES.json').exists())
    def test_teacher_labo_catalogue_requires_session(self):
        spec=importlib.util.spec_from_file_location('teacher_handler_v9',ROOT/'tools/serve_enseignant.py')
        mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
        server=ThreadingHTTPServer(('127.0.0.1',0),mod.create_handler(ROOT,'local-test-cookie-token'))
        thread=Thread(target=server.serve_forever,daemon=True);thread.start()
        try:
            url=f'http://127.0.0.1:{server.server_port}/api/labo-catalogue.json'
            with self.assertRaises(HTTPError) as err:urlopen(url,timeout=4)
            self.assertEqual(err.exception.code,401)
            req=Request(url,headers={'Cookie':'EkoleTeacher=local-test-cookie-token'})
            with urlopen(req,timeout=4) as r:
                self.assertGreaterEqual(json.loads(r.read())['count'],20)
        finally:
            server.shutdown();server.server_close();thread.join(timeout=3)
    def test_entrypoints_and_unmodified_core(self):
        self.assertIn('labo/',(ROOT/'site/eleve/index.html').read_text())
        self.assertIn('labo/?cours=',(ROOT/'site/eleve/app.js').read_text())
        self.assertIn('get(\'/api/labo-catalogue.json\')',(ROOT/'enseignant-app/app.js').read_text())

if __name__=='__main__':unittest.main()
