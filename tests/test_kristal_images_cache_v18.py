"""Un changement de fichier change la revision publique, sans toucher aux prompts."""
import json
import pathlib
import tempfile
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from compiler_visuels_kristals import compile_layer

class ImagesCacheV18(unittest.TestCase):
    def test_revision_updates_only_when_content_changes(self):
        try:
            from PIL import Image
        except ImportError:
            self.skipTest('Pillow requis pour images réelles')
        with tempfile.TemporaryDirectory() as tmp:
            root=pathlib.Path(tmp)
            data=root/'site/eleve/data/eleves'
            data.mkdir(parents=True)
            data.joinpath('catalogue.json').write_text(json.dumps({'courses':[{'id':'qc-pri-ma-012','title':'Fractions'}]}),encoding='utf-8')
            wid=root/'kristals/qc-pri-ma-012/experience'
            wd=wid/'images'
            wd.mkdir(parents=True)
            (wid/'RESSOURCES_VISUELLES.json').write_text(json.dumps({
                'format':'ekole.kristal-visual-layer/1.0', 'kristal_id':'qc-pri-ma-012',
                'visuels':[{'slot':'concept','placement':'decouvrir','prompt_conceptuel':'Description conceptuelle détaillée, exacte et indépendante de tout style visuel.', 'texte_alternatif':'Illustration de fractions.'}]
            },ensure_ascii=False),encoding='utf-8')
            image=wd/'concept.webp'
            Image.new('RGB',(160,160),(200,30,40)).save(image,'WEBP')
            first=compile_layer(root)['cours']['qc-pri-ma-012']['visuels'][0]
            assert first['url']=='assets/kristals/qc-pri-ma-012/concept.webp'
            self.assertRegex(first['revision'],r'^[a-f0-9]{16}$')
            self.assertEqual(compile_layer(root)['cours']['qc-pri-ma-012']['visuels'][0]['revision'],first['revision'])
            Image.new('RGB',(160,160),(40,30,200)).save(image,'WEBP')
            second=compile_layer(root)['cours']['qc-pri-ma-012']['visuels'][0]
            self.assertNotEqual(first['revision'],second['revision'])
            self.assertEqual(second['url'],first['url'])
            self.assertTrue((root/'site/eleve/assets/kristals/qc-pri-ma-012/concept.webp').is_file())
            image.unlink()
            absent=compile_layer(root)['cours']['qc-pri-ma-012']['visuels'][0]
            self.assertIsNone(absent['url'])
            self.assertIsNone(absent['revision'])
if __name__=='__main__':unittest.main()
