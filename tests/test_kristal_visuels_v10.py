"""Vérifie la couche conceptuelle sans charger de contenu enseignant vers l'élève."""
import json
import pathlib
import re
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from compiler_visuels_kristals import compile_layer

class KristalVisualLayerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.public=compile_layer(ROOT, strict=True)
        cls.catalogue=json.loads((ROOT/'site/eleve/data/eleves/catalogue.json').read_text(encoding='utf-8'))

    def test_counts_and_two_unavailable_sources(self):
        self.assertEqual(self.public['nb_references'],202)
        self.assertEqual(self.public['nb_couches_kristal'],200)
        self.assertEqual(self.public['nb_cours_couverts'],202)
        absent={id for id,v in self.public['cours'].items() if v['statut_source']!='kristal_disponible'}
        self.assertEqual(absent,{'qc-pri-fr-004','qc-pri-ma-005'})

    def test_every_course_has_concept_and_situation_prompts(self):
        for id,item in self.public['cours'].items():
            by={v['slot']:v for v in item['visuels']}
            self.assertTrue({'concept','situation'}.issubset(by),id)
            for v in by.values():
                self.assertGreaterEqual(len(v['prompt']),60)
                self.assertIn(id,v['fichier_attendu'])
                self.assertIn(v['placement'],('decouvrir','essayer','explorer'))

    def test_200_manifest_sources_retain_objective(self):
        for id,item in self.public['cours'].items():
            if item['statut_source']!='kristal_disponible':continue
            path=ROOT/'kristals'/id/'experience/RESSOURCES_VISUELLES.json'
            d=json.loads(path.read_text(encoding='utf-8'))
            self.assertEqual(d['source']['contrat'],'authoring/CONTRAT_PEDAGOGIQUE.json')
            objective=d['source']['objectif_observable']
            self.assertTrue(objective)
            self.assertIn(objective,d['visuels'][0]['prompt_conceptuel'])
            self.assertEqual(d['statut'],'proposition_a_valider')

    def test_images_present_only_for_real_files_and_fallbacks(self):
        # Since v15 teachers may import their own images; do NOT delete them to
        # satisfy the v10's historical "zero images" snapshot assumption.
        self.assertEqual(sum(len(v['visuels']) for v in self.public['cours'].values()),406)
        published=0
        for cid,course in self.public['cours'].items():
            for visual in course['visuels']:
                image=ROOT/visual['fichier_attendu']
                if visual['statut']=='image_disponible':
                    published+=1
                    self.assertTrue(image.is_file() and image.stat().st_size>0)
                    self.assertTrue(visual['url'].startswith(f'assets/kristals/{cid}/'))
                else:
                    self.assertIsNone(visual['url'])
                    self.assertEqual(visual['statut'],'prompt_visible')
        self.assertEqual(self.public['nb_images'],published)

    def test_course_with_real_microlabs_only_candidate_links(self):
        c=json.loads((ROOT/'kristals/qc-pri-ma-012/experience/RESSOURCES_VISUELLES.json').read_text(encoding='utf-8'))
        ids={x['id'] for x in c['liens_bibliotheque']['scenarios_existants']}
        self.assertEqual(ids,{'fractions-3-8','fractions-2-5'})
        self.assertTrue(all(x['statut']!='approuve' for x in c['liens_bibliotheque']['scenarios_existants']))

    def test_prompts_not_style_directives_or_answers(self):
        full=json.dumps(self.public,ensure_ascii=False)
        for forbidden in ['BANQUE_ITEMS','reponse_attendue','corrigé :','Flat-friendly','paper cutout','palette #','watercolor illustration']:
            self.assertNotIn(forbidden,full)

    def test_public_renderer_load_and_fallback(self):
        s=(ROOT/'site/eleve/app.js').read_text(encoding='utf-8')
        self.assertIn('data/kristals-visuels.json',s)
        self.assertIn("child(missing,'p','kristal-prompt-body',item.alt||item.concept",s)
        self.assertNotIn('Copier ce prompt',s)
        self.assertNotIn('item.prompt',s)
        self.assertIn("pic.onerror=()=>{missing.hidden=false;};",s)
        self.assertIn("pic.loading='eager'",s)
        self.assertNotIn("pic.loading='lazy';pic.alt=",s)

if __name__=='__main__':unittest.main()
