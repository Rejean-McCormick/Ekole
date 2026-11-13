from __future__ import annotations
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'app'))
from prf22_core import DesignError
from prf22_workspace import materialize


class WorkspaceTests(unittest.TestCase):
    def setUp(self):
        self.t=tempfile.TemporaryDirectory();self.addCleanup(self.t.cleanup)
        self.root=Path(self.t.name);self.a=self.root/'arketype';self.parent=self.root/'work'
        (self.a/'inventaires').mkdir(parents=True);self.parent.mkdir()
        (self.a/'arketype.py').write_text('# demo\n',encoding='utf8')
        self.profile=json.loads((ROOT/'tests'/'fixtures'/'profil-usage-PRF-22-CANDIDAT.json').read_text(encoding='utf8'))
        (self.a/'inventaires'/'profils-usage.json').write_text(json.dumps({'profiles':[self.profile]}),encoding='utf8')
        self.design=json.loads((ROOT/'examples'/'exemple-prf22-v03.design.json').read_text(encoding='utf8'))

    def test_preview_no_creation(self):
        fake={'destination':str(self.parent/'my-situation'),'will_write':False}
        with mock.patch('prf22_workspace.subprocess.run',return_value=mock.Mock(returncode=0,stdout=json.dumps(fake),stderr='')) as run:
            result=materialize(self.design,self.a,self.parent,'my-situation',dry_run=True)
        self.assertEqual(result['result'],'preview')
        self.assertFalse((self.parent/'my-situation').exists())
        self.assertIn('--dry-run',run.call_args.args[0])

    def test_reject_missing_profile(self):
        (self.a/'inventaires'/'profils-usage.json').write_text('{"profiles":[]}',encoding='utf8')
        with self.assertRaisesRegex(DesignError,'absent'):
            materialize(self.design,self.a,self.parent,'my-situation',dry_run=True)

    def test_reject_unsafe_slug(self):
        for s in ['../escape','UPPER','a b','', 'a'*81]:
            with self.subTest(slug=s):
                with self.assertRaises(DesignError):materialize(self.design,self.a,self.parent,s,True)

    def test_reject_duplicate_workspace(self):
        (self.parent/'already-exists').mkdir()
        with self.assertRaises(DesignError):materialize(self.design,self.a,self.parent,'already-exists',True)

    def test_reject_unapproved_design(self):
        d=json.loads(json.dumps(self.design));d['governance']['publication_authorized']=True
        with self.assertRaisesRegex(DesignError,'non conforme'):
            materialize(d,self.a,self.parent,'my-situation',True)

if __name__=='__main__':unittest.main()
