from __future__ import annotations
import copy
import json
from pathlib import Path
import subprocess
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'app'))
from prf22_schema_portable import validate_subset

class PortableTests(unittest.TestCase):
    def setUp(self):
        self.schema=json.loads((ROOT/'app'/'situation-orchestrable.design.v0.3.schema.json').read_text(encoding='utf8'))
        self.design=json.loads((ROOT/'examples'/'exemple-prf22-v03.design.json').read_text(encoding='utf8'))

    def test_structure_portable_accepts_known_example(self):
        self.assertEqual(validate_subset(self.schema,self.design),[])

    def test_structure_rejects_bool_integer_and_unknown_field(self):
        d=copy.deepcopy(self.design)
        d['organization']['preferred_team_size']=True
        d['unexpected']={'teacher_authorized':True}
        err=validate_subset(self.schema,d)
        self.assertTrue(any('preferred_team_size' in msg for msg in err))
        self.assertTrue(any('unexpected' in msg for msg in err))

    def test_without_third_party_dependency(self):
        result=subprocess.run([sys.executable,'-S',str(ROOT/'app'/'prf22_cli.py'),'valider',
                               str(ROOT/'examples'/'exemple-prf22-v03.design.json')],capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)
        self.assertIn('portable',result.stdout)

    def test_full_schema_flag_requires_jsonschema(self):
        result=subprocess.run([sys.executable,'-S',str(ROOT/'app'/'prf22_cli.py'),'valider',
                               str(ROOT/'examples'/'exemple-prf22-v03.design.json'),'--require-schema'],capture_output=True,text=True)
        self.assertNotEqual(result.returncode,0)
        self.assertIn('jsonschema non installé',result.stdout)

if __name__=='__main__':unittest.main()
