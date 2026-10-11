"""Public presentation: labels, back links, image descriptions and no copy action."""
import json, pathlib, re, unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
class EkoleV15UITest(unittest.TestCase):
    def read(self,rel):return (ROOT/rel).read_text(encoding='utf-8')
    def test_labels_and_generator(self):
        ui=self.read('site/eleve/app.js')
        self.assertIn("'Étape 1','Étape 2','Étape 3','Étape 4'",ui)
        self.assertNotIn('Automne 1',ui)
        self.assertNotIn('Hiver 2',ui)
        self.assertIn("'1':'Étape 1'",self.read('tools/construire_vue_enfant.py'))
        html=self.read('site/index.html')
        self.assertRegex(html,r'<option value="4">Étape 4</option>')
    def test_student_only_description(self):
        js=self.read('site/eleve/app.js')
        self.assertNotIn('Copier ce prompt',js)
        self.assertNotIn('item.prompt',js)
        self.assertIn('item.alt||item.concept',js)
        world=self.read('site/eleve/mondes-v12/app.js')
        self.assertNotIn('Copier le prompt',world)
        self.assertNotIn('s.prompt_visuel',world)
        encyclopedia=self.read('site/eleve/encyclopedie-autochtones/app.js')
        self.assertNotIn('fallback.append(node(\'p\',v.prompt))',encyclopedia)
    def test_return_to_year_and_course(self):
        ui=self.read('site/eleve/labo/app.js')
        self.assertIn("'../?cours='+encodeURIComponent(course)",ui)
        self.assertIn("'../?annee='+grade",ui)
        self.assertIn('backToCourse',self.read('site/eleve/labo/index.html'))
        self.assertIn('backToPath',self.read('site/eleve/labo/index.html'))
    def test_editor_is_teacher_only(self):
        self.assertIn('images-editor-v15.js',self.read('enseignant-app/index.html'))
        self.assertNotIn('images-editor-v15.js',self.read('site/eleve/index.html'))
        self.assertNotIn('visual-upload',self.read('tools/export_ekole_eleve_v8.py'))
if __name__=='__main__':unittest.main()
