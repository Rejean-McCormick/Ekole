"""Contrôle du contenu pastoral frère actuel, sans publication implicite.

Le catalogue est passé de 12 cours/3 parcours à 32 cours/7 parcours.
Le test vérifie sa structure et l'état non publié de chaque unité.
"""
import json
import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from launcher import ENGINE, load_pack


class PastoralTests(unittest.TestCase):
    def test_pastorale_pack(self):
        root = ENGINE.parent / 'ecole-pastorale'
        pack = load_pack(root)  # Contrôle aussi les chemins et les prérequis.
        self.assertEqual(pack['id'], 'ecole-pastorale')
        self.assertGreaterEqual(len(pack['cours']), 32)
        self.assertGreaterEqual(len(pack['parcours']), 7)
        self.assertEqual(pack['statut'], 'projet_non_publie')

        for cours in pack['cours']:
            with self.subTest(cours=cours['id']):
                self.assertEqual(cours['statut'], 'maquette_non_approuvee')
                doc = json.loads((root / cours['fichier']).read_text(encoding='utf-8'))
                self.assertEqual(doc['id'], cours['id'])
                self.assertEqual(doc.get('statut'), 'proposition_non_validee')
                self.assertIs(doc.get('publication_eleve'), False)
                modules = doc.get('modules')
                self.assertIsInstance(modules, list)
                self.assertGreater(len(modules), 0)
                for module in modules:
                    self.assertIsInstance(module, dict)
                    self.assertIsInstance(module.get('texte'), str)
                    self.assertTrue(module['texte'].strip())

                self.assertTrue(all(value is False for value in doc['validation'].values()))
                self.assertTrue(all(value is False for value in doc['approbations'].values()))


if __name__ == '__main__':
    unittest.main()
