import json
from pathlib import Path
import tempfile
import unittest
from tools.preparer_mission_collaborative import prepare
HOME = Path(__file__).resolve().parents[2]


def _kamel_root():
    """Accepte les dépôts côte à côte (tests) et l'arborescence Windows réelle."""
    candidates = (
        HOME / 'Kamel',                 # workspace de tests côte à côte
        HOME.parent / 'Kamel' / 'Kamel', # C:\mycode\Kamel\Kamel
    )
    for candidate in candidates:
        if (candidate / 'tools/ekole/print_mission_cards.py').is_file():
            return candidate
    raise AssertionError('Dépôt Kamel introuvable : ' + ', '.join(map(str, candidates)))
class CompletePreparation(unittest.TestCase):
    def test_11_steps_and_no_admission(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            people=root/'pupils.json'
            people.write_text(json.dumps([
                {'eleve_ref':'pupil-01','pratique_souhaitee':['qc-pri-fr-021'],'deja_pratique':[]},
                {'eleve_ref':'pupil-02','pratique_souhaitee':[],'deja_pratique':['qc-pri-ap-003']},
            ]),encoding='utf8')
            output=prepare(kontexte=HOME/'Kontexte',kompose=HOME/'Kompose',mission_id='fete-sorciere',
                           out=root/'result',participants=people,kamel=_kamel_root())
            self.assertEqual(output['step_count'],11)
            self.assertFalse(output['authorizations']['dispatch_allowed'])
            pack=json.loads((root/'result/cartes.json').read_text(encoding='utf8'))
            self.assertEqual(len(pack['cards']),11)
            self.assertTrue((root/'result/cartes-impression.html').exists())
            self.assertNotIn('papier-disponible',json.dumps(pack))
            self.assertTrue(output['role_proposals']['teacher_approval_required'])
    def test_path_escape(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError):
                prepare(kontexte=HOME/'Kontexte',kompose=HOME/'Kompose',mission_id='../private',out=Path(d))
if __name__=='__main__':unittest.main()
