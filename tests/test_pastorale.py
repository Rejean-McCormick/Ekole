"""Valide le contenu pastoral du dépôt frère et ses cours accessibles par API."""
import json, pathlib, sys, unittest
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from launcher import ENGINE, load_pack

class PastoralTests(unittest.TestCase):
    def test_pastorale_pack(self):
        root=ENGINE.parent/'ecole-pastorale'
        pack=load_pack(root)
        self.assertEqual(pack['id'],'ecole-pastorale')
        self.assertEqual(len(pack['cours']),12)
        self.assertEqual(len(pack['parcours']),3)
        self.assertTrue(all(c['statut']=='brouillon_a_valider' for c in pack['cours']))
        for c in pack['cours']:
            doc=json.loads((root/c['fichier']).read_text(encoding='utf-8'))
            self.assertEqual(doc['id'], c['id'])
            self.assertEqual(len(doc['modules']),2)
            self.assertTrue(all(mod['texte'].strip() for mod in doc['modules']))

if __name__=='__main__': unittest.main()
