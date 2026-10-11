#!/usr/bin/env python3
"""Strict allowlist. Export ONLY public app under site/eleve to new folder. No corrigés."""
import argparse,json,pathlib,shutil,re
ROOT=pathlib.Path(__file__).resolve().parents[1]
ALLOWED=('index.html','app.js','style.css','assets/ekole-logo.svg','data/eleves/catalogue.json',
         'data/eleves/integrations.json','data/eleves/konstellation-light-candidat.json',
         'data/konstellation-liens.json','data/visuels_public.json')
def export(root,out):
 root=pathlib.Path(root).resolve();out=pathlib.Path(out).resolve()
 if root==out or root in out.parents:raise ValueError('Destination sous le repo refusée')
 if out.exists():raise FileExistsError('Destination doit être nouvelle : aucun écrasement')
 src=root/'site/eleve'
 for rel in ALLOWED:
  if not (src/rel).is_file():raise FileNotFoundError('Export incomplet: '+rel)
 out.mkdir(parents=True)
 for rel in ALLOWED:
  dst=out/rel;dst.parent.mkdir(parents=True,exist_ok=True)
  raw=(src/rel).read_bytes()
  if rel=='index.html':
   raw=re.sub(rb'<a\s+href="(?:\.\./(?:enseignant/)?|http://127\.0\.0\.1:4177/)[^"]*"[^>]*>.*?</a>',b'',raw,flags=re.DOTALL)
  if rel=='data/konstellation-liens.json':
   obj=json.loads(raw)
   obj['preview_local_url']=None
   obj['note']='Lien demo locale retire de cet export public. Connecter une collection v10 verifiee apres revue.'
   raw=(json.dumps(obj,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
  dst.write_bytes(raw)
 assert len(list(out.rglob('*.json')))==5
 for f in out.rglob('*'):
  if f.is_file():
   contents=f.read_bytes()
   if any(s in f.as_posix() for s in ('data/cours/','BANQUE_ITEMS','enseignant-app','visuels/INTENTIONS_IMAGES')):raise RuntimeError('Export non autorisé')
 j=json.loads((out/'data/eleves/catalogue.json').read_text(encoding='utf-8'))
 assert len(j['courses'])==202
 return len(ALLOWED)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--root',default=str(ROOT));p.add_argument('--out',required=True);a=p.parse_args()
 print('Ekole Élève, fichiers publics uniquement:',export(a.root,a.out))
