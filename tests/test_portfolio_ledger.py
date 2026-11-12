from pathlib import Path
import sqlite3
import tempfile
import unittest
from tandem.portfolio_ledger import connect,session,attribuer,preuve,revue,rapport,portfolio_candidates

class EvidenceLedgerTest(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.db=connect(Path(self.temp.name)/'journal.sqlite3')
        session(self.db,session_ref='seance-demo',mission_ref='fete-sorciere')
        attribuer(self.db,session_ref='seance-demo',eleve_ref='eleve-pseudo1',task_ref='invitation',role_code='sorciere')
    def tearDown(self):
        self.db.close();self.temp.cleanup()
    def test_requires_assignment(self):
        with self.assertRaises(sqlite3.IntegrityError):
            preuve(self.db,event_ref='evt-2',session_ref='seance-demo',eleve_ref='autre-eleve',task_ref='invitation',source='orgo',source_ref='receipt-2')
    def test_review_no_automatic_mastery(self):
        kw={'event_ref':'evt-1','session_ref':'seance-demo','eleve_ref':'eleve-pseudo1','task_ref':'invitation','source':'orgo','source_ref':'receipt-1','assistance':'avec_aide'}
        self.assertTrue(preuve(self.db,**kw))
        self.assertFalse(preuve(self.db,**kw))
        before=rapport(self.db,'seance-demo','eleve-pseudo1')
        self.assertEqual(before['preuves_validees_par_enseignant'],0)
        with self.assertRaises(ValueError):preuve(self.db,**{**kw,'assistance':'autonome'})
        revue(self.db,review_ref='review-1',event_ref='evt-1',decision='validee',reviewer_ref='prof-pseudo1',objectif_ref='qc-pri-fr-021')
        after=rapport(self.db,'seance-demo','eleve-pseudo1')
        self.assertEqual(after['tentatives'],1)
        self.assertEqual(after['preuves_validees_par_enseignant'],1)
        self.assertFalse(after['maitrise_automatique'])
        portfolio=portfolio_candidates(self.db,'seance-demo','eleve-pseudo1')
        self.assertEqual(len(portfolio['items']),1)
        self.assertFalse(portfolio['publication_authorized'])
        self.assertFalse(portfolio['konnaxion_portfolio_written'])
    def test_prevents_pii_in_identifiers(self):
        with self.assertRaises(ValueError):attribuer(self.db,session_ref='seance-demo',eleve_ref='Nom Prénom',task_ref='invitation',role_code='sorciere')
if __name__=='__main__':unittest.main()
