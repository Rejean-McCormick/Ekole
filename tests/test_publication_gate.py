"""Student APIs must not expose explicit unapproved lesson drafts, even offline."""
from __future__ import annotations
import http.server
import json
from pathlib import Path
import tempfile
import threading
import unittest
import urllib.request
from launcher import Environment, create_handler


class StudentPublicationTests(unittest.TestCase):
    def test_unapproved_derived_student_view_is_suppressed(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            (root/'cours').mkdir(); (root/'publications/eleve').mkdir(parents=True)
            cid='draft-001'
            (root/'cours'/f'{cid}.json').write_text(json.dumps({'id':cid,'modules':[{'texte':'TEACHER-SOURCE-SECRET'}]}))
            (root/'publications/eleve'/f'{cid}.json').write_text(json.dumps({
                'id':cid,'publication_autorisee':False,'modules':[{'texte':'NOT-FOR-STUDENTS'}]}))
            (root/'pack.json').write_text(json.dumps({'format':'ekole.content-pack/0.1',
                'id':'testing-pack','nom':'Draft','statut':'projet_non_publie','politique_publication':'vues_separees',
                'cours':[{'id':cid,'titre':'Draft','fichier':f'cours/{cid}.json','prerequis':[]}], 'parcours':[]}))
            env=Environment(root,False)
            public=env.student_course(cid)
            self.assertEqual(public['modules'],[])
            self.assertNotIn('NOT-FOR-STUDENTS',json.dumps(public))
            with http.server.ThreadingHTTPServer(('127.0.0.1',0),create_handler(env)) as server:
                thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
                try:
                    with urllib.request.urlopen(f'http://127.0.0.1:{server.server_port}/api/cours/{cid}.json',timeout=3) as reply:
                        api=json.load(reply)
                    self.assertEqual(api['modules'],[])
                    self.assertNotIn('TEACHER-SOURCE-SECRET',json.dumps(api))
                finally:
                    server.shutdown();thread.join(timeout=4)


if __name__=='__main__':unittest.main()
