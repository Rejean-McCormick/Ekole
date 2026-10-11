"""Ekole v17: safe image deletion, validation and clean student projection."""
from __future__ import annotations
import json, pathlib, sys, unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tests'))
from test_ekole_image_editor_v15 import ImageEditorV15Test

class ImageEditorV17Test(ImageEditorV15Test):
    def delete(self, *, csrf=None, origin=None, confirm='yes', authenticated=True, slot='concept'):
        headers={'Origin':self.origin if origin is None else origin,
                 'X-Ekole-CSRF':self.session() if csrf is None else csrf,
                 'X-Ekole-Delete-Confirm':confirm}
        if authenticated:headers['Cookie']=self.cookie
        return self.call('DELETE',f'/api/visual-image/qc-pri-ma-012/{slot}',headers=headers)

    def test_delete_restores_placeholder_removes_public_and_keeps_private_backup(self):
        status,raw=self.upload(self.png());self.assertEqual(status,201,raw)
        saved=json.loads(raw)
        canonical=self.root/'kristals/qc-pri-ma-012/experience/images/concept.webp'
        public=self.root/'site/eleve/assets/kristals/qc-pri-ma-012/concept.webp'
        self.assertTrue(canonical.exists())
        self.assertTrue(public.exists())
        original=canonical.read_bytes()
        status,body=self.delete();self.assertEqual(status,200,body)
        result=json.loads(body)
        self.assertEqual(result['status'],'deleted')
        self.assertEqual(result['public_url'],None)
        self.assertIn('concept.webp',result['deleted_files'])
        self.assertFalse(canonical.exists())
        self.assertFalse(public.exists(), 'The former student copy must not survive removal')
        backup_dir=self.root/'archives/ekole-images/qc-pri-ma-012'
        self.assertTrue(any(p.read_bytes()==original for p in backup_dir.glob('concept.webp.suppression-*.bak')))
        projected=json.loads((self.root/'site/eleve/data/kristals-visuels.json').read_text())
        visual=projected['cours']['qc-pri-ma-012']['visuels'][0]
        self.assertIsNone(visual['url'])
        self.assertEqual(visual['statut'],'prompt_visible')
        status,_=self.call('GET','/api/kristal-image/qc-pri-ma-012/concept.webp',headers={'Cookie':self.cookie})
        self.assertEqual(status,404)
        status,_=self.delete()
        self.assertEqual(status,404)

    def test_delete_is_teacher_only_and_requires_explicit_confirmation(self):
        status,_=self.upload(self.png());self.assertEqual(status,201)
        csrf=self.session()
        self.assertEqual(self.delete(authenticated=False,csrf=csrf)[0],401)
        self.assertEqual(self.delete(csrf='bad')[0],403)
        self.assertEqual(self.delete(origin='http://evil.invalid',csrf=csrf)[0],403)
        self.assertEqual(self.delete(confirm='no',csrf=csrf)[0],400)
        self.assertEqual(self.delete(slot='nonexistent',csrf=csrf)[0],422)
        self.assertEqual(self.call('DELETE','/api/visual-image/qc-pri-ma-012/%2e%2e',headers={'Cookie':self.cookie})[0],404)
        self.assertTrue((self.root/'kristals/qc-pri-ma-012/experience/images/concept.webp').exists())

    def test_delete_keeps_unrelated_and_custom_public_files(self):
        status,_=self.upload(self.png());self.assertEqual(status,201)
        folder=self.root/'site/eleve/assets/kristals/qc-pri-ma-012'
        (folder/'another.webp').write_bytes(b'unrelated-custom-file')
        (folder/'concept.png').write_bytes(b'different-custom-version')
        status,raw=self.delete();self.assertEqual(status,200,raw)
        self.assertEqual((folder/'another.webp').read_bytes(),b'unrelated-custom-file')
        self.assertEqual((folder/'concept.png').read_bytes(),b'different-custom-version')

    def test_delete_rejects_symlinks_in_canonical_slot(self):
        status,_=self.upload(self.png());self.assertEqual(status,201)
        p=self.root/'kristals/qc-pri-ma-012/experience/images/concept.webp'
        content=p.read_bytes();p.unlink()
        outsider=self.root/'unrelated-image.webp';outsider.write_bytes(content)
        try:p.symlink_to(outsider)
        except (OSError,NotImplementedError):self.skipTest('Symlinks unavailable')
        status,_=self.delete();self.assertEqual(status,403)
        self.assertEqual(outsider.read_bytes(),content)

if __name__=='__main__':unittest.main()
