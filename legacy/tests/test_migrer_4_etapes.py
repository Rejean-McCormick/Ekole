import json,importlib.util,tempfile,unittest,io,contextlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('migrer',ROOT/'tools/migrer_4_etapes.py')
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
EXAMPLE=json.loads((ROOT/'site/data/parcours-affectations.4-etapes.exemple.json').read_text())
class MigrationTests(unittest.TestCase):
 def test_non_destructive_copy_and_idempotence(self):
  with tempfile.TemporaryDirectory() as directory:
   p=Path(directory)/'parcours-affectations.json'
   old=json.loads(json.dumps(EXAMPLE))
   for year in range(1,7):old['cours_par_etape'].pop(f'annee-{year}-etape-4')
   old['cours_par_etape']['annee-3-etape-1']=['qc-pri-ma-001']
   old['preuves_attribution']['qc-pri-ma-001']='Revue institutionnelle explicite'
   p.write_text(json.dumps(old,ensure_ascii=False),encoding='utf8')
   initial=p.read_bytes()
   with contextlib.redirect_stdout(io.StringIO()):mod.migrate(p,False)
   self.assertEqual(p.read_bytes(),initial)
   with contextlib.redirect_stdout(io.StringIO()):mod.migrate(p,True)
   data=json.loads(p.read_text())
   self.assertEqual(len(data['cours_par_etape']),24)
   self.assertEqual(data['cours_par_etape']['annee-3-etape-1'],['qc-pri-ma-001'])
   self.assertEqual(data['preuves_attribution']['qc-pri-ma-001'],'Revue institutionnelle explicite')
   self.assertEqual(len(list(p.parent.glob(p.name+'.bak-*'))),1)
   with contextlib.redirect_stdout(io.StringIO()):mod.migrate(p,True)
   self.assertEqual(len(list(p.parent.glob(p.name+'.bak-*'))),1)
 def test_invalid_key_rejected_without_modification(self):
  with tempfile.TemporaryDirectory() as directory:
   p=Path(directory)/'parcours-affectations.json'
   data=json.loads(json.dumps(EXAMPLE));data['cours_par_etape']['annee-7-etape-1']=[]
   p.write_text(json.dumps(data),encoding='utf8');raw=p.read_bytes()
   with self.assertRaises(ValueError):mod.migrate(p,True)
   self.assertEqual(p.read_bytes(),raw)
 def test_missing_file_is_noop(self):
  with tempfile.TemporaryDirectory() as directory:
   with contextlib.redirect_stdout(io.StringIO()):self.assertTrue(mod.migrate(Path(directory)/'missing.json',True))
if __name__=='__main__':unittest.main()
