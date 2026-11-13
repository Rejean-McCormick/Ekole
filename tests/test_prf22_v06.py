"""PRF-22 v0.6: teacher isolation, provenance, local-only revisions."""
from __future__ import annotations
import hashlib, http.server, json, pathlib, shutil, tempfile, threading, unittest
from unittest import mock
from urllib.request import Request, urlopen
from urllib.error import HTTPError
import launcher, prf22_bridge

ENGINE=pathlib.Path(__file__).resolve().parents[1]
BANK=ENGINE/'banques/prf22/candidats-v0_6'
SLUG='mission-boulangerie-mathematiques'


class LocalBridgeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory()
        cls.root=pathlib.Path(cls.temp.name)
        (cls.root/'candidats-v0_6/situations'/SLUG).mkdir(parents=True)
        master=json.loads((BANK/'MANIFEST.json').read_text(encoding='utf-8'))
        rec=next(x for x in master['entries'] if x['folder'].endswith('/'+SLUG))
        master['entries']=[rec];master['entries_count']=1;master['source_situations_covered']=1
        (cls.root/'candidats-v0_6/MANIFEST.json').write_text(json.dumps(master),encoding='utf-8')
        for name in ('brouillon.json','design.json','handoff.json'):
            shutil.copy2(BANK/rec['folder']/name,cls.root/'candidats-v0_6'/rec['folder']/name)
        shutil.copy2(ENGINE/'banques/prf22/activites-proposees-v0_6.json',cls.root/'activites-proposees-v0_6.json')
        cls.patcher=mock.patch.object(prf22_bridge,'BANKS',cls.root);cls.patcher.start()

    @classmethod
    def tearDownClass(cls):
        cls.patcher.stop();cls.temp.cleanup()

    def setUp(self):
        self.env=launcher.Environment(None,True)
        self.servers=[]
        for teacher in (False,True):
            s=http.server.ThreadingHTTPServer(('127.0.0.1',0),launcher.create_handler(self.env,teacher))
            t=threading.Thread(target=s.serve_forever,daemon=True);t.start();self.servers.append(s)
        self.addCleanup(self.stop)

    def stop(self):
        for s in self.servers:s.shutdown();s.server_close()

    def request(self,teacher,path,*,cookie=False,csrf=False,origin=True,method='GET',payload=None):
        s=self.servers[int(teacher)]
        url=f'http://127.0.0.1:{s.server_port}'+path
        headers={}
        if cookie:headers['Cookie']='EkoleTeacher='+self.env.key
        if method=='POST':
            headers['Content-Type']='application/json'
            headers['Origin']=f'http://127.0.0.1:{s.server_port}' if origin else 'http://untrusted.invalid'
        if csrf:headers['X-Ekole-CSRF']=self.env.csrf
        raw=json.dumps(payload).encode('utf-8') if payload is not None else None
        try:
            with urlopen(Request(url,headers=headers,data=raw,method=method),timeout=12) as r:
                data=r.read();return r.status,json.loads(data) if r.headers.get_content_type()=='application/json' else data
        except HTTPError as e:
            return e.code,e.read()

    def test_index_is_teacher_only(self):
        self.assertEqual(self.request(False,'/api/prf22/index.json')[0],404)
        self.assertEqual(self.request(True,'/api/prf22/index.json')[0],401)
        status,data=self.request(True,'/api/prf22/index.json',cookie=True)
        self.assertEqual(status,200);self.assertEqual(data['entries_count'],1)
        self.assertEqual(self.request(False,'/prf22/index.html')[0],404)
        self.assertEqual(self.request(True,'/prf22/index.html',cookie=True)[0],200)

    def test_provenance_is_not_relabelled(self):
        status,data=self.request(True,f'/api/prf22/situation/{SLUG}.json',cookie=True)
        self.assertEqual(status,200)
        owners={x['exercise_ref']['owner'] for x in data['design']['activities']}
        self.assertEqual(owners,{'Ékole','Kontexte'})
        self.assertTrue(all(x['pin_status']=='unresolved' for x in data['authoring']['source_observations']))

    def test_security_rejects_bad_csrf_origin_and_structure(self):
        status,data=self.request(True,f'/api/prf22/situation/{SLUG}.json',cookie=True)
        author=data['authoring'];entries=author['theory_entries']
        editable={goal:{k:value for k,value in card.items() if k in prf22_bridge.EDITABLE}
                  for goal,card in entries.items()}
        payload={'slug':SLUG,'source_sha256':data['source_sha256'],'theory_entries':editable,'note':'Révision fictive.'}
        self.assertEqual(self.request(False,'/api/prf22/reviser',method='POST',payload=payload)[0],401)
        self.assertEqual(self.request(True,'/api/prf22/reviser',cookie=True,method='POST',payload=payload)[0],403)
        self.assertEqual(self.request(True,'/api/prf22/reviser',cookie=True,csrf=True,origin=False,method='POST',payload=payload)[0],403)
        tampered=json.loads(json.dumps(payload));tampered['theory_entries'][next(iter(editable))]['activity_refs']=['fake']
        self.assertEqual(self.request(True,'/api/prf22/reviser',cookie=True,csrf=True,method='POST',payload=tampered)[0],422)
        tampered=json.loads(json.dumps(payload));tampered['source_sha256']='a'*64
        self.assertEqual(self.request(True,'/api/prf22/reviser',cookie=True,csrf=True,method='POST',payload=tampered)[0],422)

    def test_successful_local_revision_keeps_bank_immutable(self):
        status,data=self.request(True,f'/api/prf22/situation/{SLUG}.json',cookie=True)
        self.assertEqual(status,200)
        entries=data['authoring']['theory_entries']
        edited={goal:{k:v for k,v in card.items() if k in prf22_bridge.EDITABLE} for goal,card in entries.items()}
        goal=next(iter(edited));edited[goal]['criterion']='Justifier le raisonnement par deux traces observées dans la démonstration fictive.'
        before=hashlib.sha256((self.root/'candidats-v0_6/situations'/SLUG/'design.json').read_bytes()).hexdigest()
        status,result=self.request(True,'/api/prf22/reviser',cookie=True,csrf=True,method='POST',payload={
            'slug':SLUG,'source_sha256':data['source_sha256'],'theory_entries':edited,'note':'Conserver la trace.'})
        self.assertEqual(status,200,result);self.assertTrue(result['saved']);self.assertIn('local_non_approuve',result['status'])
        after=hashlib.sha256((self.root/'candidats-v0_6/situations'/SLUG/'design.json').read_bytes()).hexdigest()
        self.assertEqual(before,after)
        rev=result['revision']
        status,saved=self.request(True,f'/api/prf22/revision/{SLUG}/{rev}.json',cookie=True)
        self.assertEqual(status,200);self.assertEqual(saved['authoring']['theory_entries'][goal]['criterion'],edited[goal]['criterion'])
        self.assertFalse(saved['design']['governance']['publication_authorized'])
        self.assertFalse(saved['design']['governance']['activation_authorized'])

    def test_read_only_still_permits_teacher_inspection(self):
        self.env.edition=False
        self.assertEqual(self.request(True,'/api/prf22/index.json',cookie=True)[0],200)
        self.assertEqual(self.request(True,'/api/prf22/reviser',cookie=True,csrf=True,method='POST',payload={'a':1})[0],403)

if __name__=='__main__':unittest.main()
