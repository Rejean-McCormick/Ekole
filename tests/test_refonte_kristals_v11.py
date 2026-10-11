"""Vérifications v11 : profondeur, garde-fous et frontière élève/enseignant."""
import json,pathlib,sys,tempfile,shutil,unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from compiler_experiences_v11 import compile_experiences
from appliquer_revisions_guides_v11 import apply,MARK
IDS={'qc-pri-ma-012','qc-pri-ma-009','qc-pri-fr-008','qc-pri-st-001','qc-pri-ad-001'}
class RefonteV11(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.data=compile_experiences(ROOT)
 def test_five_source_grounded_pilots(self):
  self.assertEqual(set(self.data['cours']),IDS)
  self.assertEqual(self.data['references'],202)
  self.assertEqual(self.data['en_attente'],197)
  for k in IDS:
   exp=json.loads((ROOT/'kristals'/k/'experience/SCENARIO_APPRENTISSAGE.json').read_text())
   contract=json.loads((ROOT/'kristals'/k/'authoring/CONTRAT_PEDAGOGIQUE.json').read_text())
   self.assertEqual(contract['objectif_observable'],exp['source']['objectif_observable'])
   self.assertEqual(contract['preuve_attendue'],exp['source']['preuve_attendue'])
   self.assertEqual(set(exp['progression_enfant']),{'decouvrir','essayer','expliquer','explorer'})
   self.assertTrue(exp['limitations'] and exp['erreurs_et_relances'])
 def test_no_banks_or_teacher_diagnostics_in_student_export(self):
  public=(ROOT/'site/eleve/data/kristals-experiences.json').read_text(encoding='utf8')
  self.assertNotIn('BANQUE_ITEMS',public)
  self.assertNotIn('erreurs_et_relances',public)
  self.assertNotIn('consignes_enseignant',public)
  self.assertNotIn('reponse_attendue',public)
  self.assertIn('non_certifie',public)
 def test_pilots_visible_and_legacy_unchanged(self):
  app=(ROOT/'site/eleve/app.js').read_text()
  self.assertIn('STATE.experiences',app)
  self.assertIn("if(exp){child(content,'h2','',exp.phases.expliquer.titre_enfant)",app)
  self.assertIn('aucun champ libre ni score automatique',app)
  self.assertIn("if(!(STATE.labV13.get(id)||[]).length",app)
 def test_prompts_style_agnostic_and_user_images_preserved(self):
  for kid in IDS:
   manifest=json.loads((ROOT/'kristals'/kid/'experience/RESSOURCES_VISUELLES.json').read_text())
   for v in manifest['visuels']:
    self.assertIn('prompt_conceptuel',v)
    self.assertIn('sans imposer de style',v['prompt_conceptuel'].lower())
    asset=ROOT/'kristals'/kid/'experience/images'/(v['slot']+'.webp')
    if asset.exists():
     self.assertGreater(asset.stat().st_size,32)
     self.assertEqual(asset.read_bytes()[:4],b'RIFF')
 def test_202_review_has_provenance(self):
  c=json.loads((ROOT/'docs/CARNET_DE_REFONTE_202_v11.json').read_text())
  self.assertEqual(c['count'],202)
  self.assertEqual(sum(x['statut']=='pilote_structure_a_revoir' for x in c['cours']),5)
  self.assertEqual(sum(x['statut']=='en_attente_de_conception_humaine' for x in c['cours']),195)
  self.assertEqual(sum(x['statut']=='source_complete_absente' for x in c['cours']),2)
 def test_dry_run_originals_protected(self):
  before=(ROOT/'kristals/qc-pri-ma-012/contenu/03_ENSEIGNEMENT_GUIDE.md').read_bytes()
  stats=apply(ROOT,False)
  after=(ROOT/'kristals/qc-pri-ma-012/contenu/03_ENSEIGNEMENT_GUIDE.md').read_bytes()
  self.assertEqual(before,after)
  self.assertGreaterEqual(sum(stats.values()),10)
 def test_apply_adds_once_with_backup_and_conflict(self):
  with tempfile.TemporaryDirectory() as tmp:
   local=pathlib.Path(tmp)
   manifests=json.loads((ROOT/'livraison/EMPREINTES_SOURCES_GUIDES_v11.json').read_text())
   (local/'livraison').mkdir(parents=True)
   (local/'livraison/EMPREINTES_SOURCES_GUIDES_v11.json').write_text(json.dumps({'qc-pri-ma-012':manifests['qc-pri-ma-012']}))
   for f in ['contenu/03_ENSEIGNEMENT_GUIDE.md','contenu/04_PRATIQUE_ACCOMPAGNEE.md','experience/ANNEXE_GUIDE_v11.md','experience/ANNEXE_PRATIQUE_v11.md']:
    source=ROOT/'kristals/qc-pri-ma-012'/f;target=local/'kristals/qc-pri-ma-012'/f
    target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,target)
   original=(local/'kristals/qc-pri-ma-012/contenu/03_ENSEIGNEMENT_GUIDE.md').read_bytes()
   self.assertEqual(apply(local,False)['ajoutes'],0)
   self.assertEqual(apply(local,True)['ajoutes'],2)
   self.assertEqual(apply(local,True)['deja_applique'],2)
   self.assertIn(MARK,(local/'kristals/qc-pri-ma-012/contenu/03_ENSEIGNEMENT_GUIDE.md').read_text())
   self.assertEqual(original,(local/'sauvegardes_ekole_v11/qc-pri-ma-012/contenu/03_ENSEIGNEMENT_GUIDE.md').read_bytes())
 def test_no_auto_grading_for_theater(self):
  x=self.data['cours']['qc-pri-ad-001']
  self.assertEqual(x['outils'],[])
  self.assertIn('aucun',x['evaluation'].lower())
if __name__=='__main__':unittest.main()
