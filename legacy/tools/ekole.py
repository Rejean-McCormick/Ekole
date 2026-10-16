#!/usr/bin/env python3
"""Ekole offline tools. Stdlib only. No network side effects, no Moodle writes."""
import argparse, json, pathlib, re, sys, hashlib, shutil, http.server, socketserver
ROOT=pathlib.Path(__file__).resolve().parents[1]
def load(p):return json.loads((ROOT/p).read_text(encoding='utf-8-sig'))
def write(p,obj):
 f=ROOT/p;f.parent.mkdir(parents=True,exist_ok=True);f.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def validate():
 cat=load('catalogue/202_kristals.json');gr=load('catalogue/graphe_pedagogique.json');rec=cat['kristals'];ids={r['id'] for r in rec};errs=[];checks=0;ni=0
 if len(rec)!=202 or len(ids)!=202:errs.append('registre non unique ou incomplet')
 expected=['authoring/PARCOURS.md','authoring/CONTRAT_PEDAGOGIQUE.json','contenu/01_NOTIONS_ET_EXEMPLES.md','contenu/02_DIAGNOSTIC.md','contenu/03_ENSEIGNEMENT_GUIDE.md','contenu/04_PRATIQUE_ACCOMPAGNEE.md','contenu/05_PRATIQUE_AUTONOME.md','contenu/06_REMEDIATION_ET_TRANSFERT.md','evaluation/PLAN_EVALUATION.md','evaluation/BANQUE_ITEMS.json','evaluation/GRILLE_MAITRISE.md','sources/REFERENCES_CONTENU.md','livraison/MANIFEST.json','livraison/VALIDATION.md']
 for r in rec:
  id=r['id'];base=ROOT/'kristals'/id
  for rel in expected:
   p=base/rel;checks+=1
   if not p.exists() or not p.stat().st_size:errs.append(f'{id}: fichier absent/vide {rel}')
  if not (base/'kristal.workspace.json').exists():errs.append(f'{id}: frame workspace absente')
  try:
   contract=json.loads((base/'authoring/CONTRAT_PEDAGOGIQUE.json').read_text(encoding='utf-8-sig'))
   bank=json.loads((base/'evaluation/BANQUE_ITEMS.json').read_text(encoding='utf-8-sig'))
   manifest=json.loads((base/'livraison/MANIFEST.json').read_text(encoding='utf-8-sig'))
   front=(base/'authoring/PARCOURS.md').read_text(encoding='utf-8-sig')
   if contract.get('kristal_id')!=id or bank.get('kristal_id')!=id:errs.append(f'{id}: ID contrat/banque')
   if r['objectif']!=contract.get('objectif_observable') or r['preuve']!=contract.get('preuve_attendue'):errs.append(f'{id}: contrat vs catalogue')
   if sorted(r['prerequis'])!=sorted(contract.get('prerequis_bloquants',[])):errs.append(f'{id}: prerequis catalogue')
   if not re.search(r'(?m)^id:\s*'+re.escape(id)+r'\s*$',front):errs.append(f'{id}: frontmatter id')
   if not front.startswith('---\n') and not front.startswith('---\r\n'):errs.append(f'{id}: YAML frontmatter absent')
   sections=re.findall(r'(?m)^##\s+(\d+)\.',front)
   if sorted(set(map(int,sections)))!=list(range(1,13)):errs.append(f'{id}: 12 sections')
   items=bank.get('items',[]);ni+=len(items)
   if len(items)<8 or len({q['item_id'] for q in items})!=len(items):errs.append(f'{id}: items insuffisants ou doublons')
   for j,q in enumerate(items,1):
    if q.get('item_id')!=f'{id}-q-{j:03d}':errs.append(f'{id}: numero item {j}')
   if sorted(manifest.get('files',[]))!=sorted(f'kristals/{id}/{x}' for x in expected):errs.append(f'{id}: manifest files')
  except Exception as e:errs.append(f'{id}: parse {e}')
 for rel in gr.get('relations',[]):
  checks+=1
  if rel.get('from') not in ids or rel.get('to') not in ids:errs.append(f'graphe lien non resolu: {rel.get("id")}')
 for slug in load('organisation/kristal-portail-ekole.candidat.json')['pages']:
  checks+=1
  if not (ROOT/'organisation/pages'/f'{slug}.json').exists():errs.append(f'page absente: {slug}')
 for doc in ['catalogue/202_kristals.json','catalogue/graphe_pedagogique.json','organisation/assemblages_disciplines.json','organisation/assemblages_annees.json']:
  checks+=1
  try:load(doc)
  except Exception as e:errs.append(f'json {doc}: {e}')
 print(json.dumps({'result':'PASS' if not errs else 'FAIL','kristals':len(ids),'items':ni,'relations':len(gr.get('relations',[])),'checks':checks,'errors':errs[:40],'truncated_errors':max(0,len(errs)-40)},ensure_ascii=False,indent=2))
 return not errs
def build():
 root=load('organisation/kristal-portail-ekole.candidat.json');cat=load('catalogue/202_kristals.json')
 public={'format':'ekole.public-index/0.1','count':len(cat['kristals']),'courses':[{k:r[k] for k in ['id','titre','discipline','discipline_code','vague','objectif','preuve','prerequis']} for r in cat['kristals']], 'pages':[],'languages':{'fr-CA':'draft','en':'not_available'}}
 for slug in root['pages']:
  page=load('organisation/pages/'+slug+'.json')
  public['pages'].append({'slug':slug,'titre':page['titre'],'public_cible':page['public_cible'],'utterances':[u['fr-CA'] for u in page['utterances']]})
 write('site/data/index.json',public)
 print('Site data regenerated:',len(public['courses']),'cours;',len(public['pages']),'pages. Aucune banque d’évaluation exposée.')
 return True
def moodle_plan():
 # Adaptateur polymorphe. Conserve "courses" uniquement comme liste de CANDIDATS
 # historiques; un Kristal ne devient pas automatiquement un cours Moodle.
 from kristal_moodle_bridge import build_plan
 out = build_plan(ROOT)
 write('plans/moodle_projection_dry_run.json', out)
 print('Moodle polymorphic dry-run plan written; Kristals:', out['summary']['kristals'])
 return True

def dplan(target,apply):
 src=(ROOT/'site').resolve();dest=pathlib.Path(target).expanduser().resolve()
 if dest==ROOT or ROOT in dest.parents or src==dest:raise ValueError('Cible dans Ekole interdite; choisir un dossier externe dédié au site statique.')
 if dest.exists() and (dest/'.git').exists():raise ValueError('Cible Git bloquée : vérifier le dépôt et choisir un répertoire de publication distinct.')
 files=[p for p in src.rglob('*') if p.is_file()];add=[];change=[];same=[]
 for p in files:
  r=p.relative_to(src);q=dest/r
  if not q.exists():add.append(str(r))
  elif hashlib.sha256(p.read_bytes()).digest()!=hashlib.sha256(q.read_bytes()).digest():change.append(str(r))
  else:same.append(str(r))
 print(json.dumps({'mode':'APPLY' if apply else 'DRY_RUN','source':'site/ uniquement','target':str(dest),'add':len(add),'change':len(change),'unchanged':len(same),'delete':0,'sample_add':add[:8],'sample_change':change[:8]},ensure_ascii=False,indent=2))
 if apply:
  if not validate():raise RuntimeError('La validation a échoué. Copie refusée.')
  if not (ROOT/'site/data/index.json').exists():build()
  import datetime
  backups=[]
  for p in files:
   r=p.relative_to(src);q=dest/r;q.parent.mkdir(parents=True,exist_ok=True)
   if q.exists() and q.read_bytes()!=p.read_bytes():
    suffix='.ekole-backup-'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    b=q.with_name(q.name+suffix);shutil.copy2(q,b);backups.append(str(b))
   shutil.copy2(p,q)
  print('Copied',len(files),'files. Backups:',len(backups))
 return True
def main():
 pa=argparse.ArgumentParser(description='Ekole offline toolkit — no network writes')
 sub=pa.add_subparsers(dest='cmd',required=True)
 for a in ['verify','build','preview','moodle-plan','pages-zip']:sub.add_parser(a)
 dp=sub.add_parser('deploy');dp.add_argument('--target',required=True);dp.add_argument('--apply',action='store_true')
 a=pa.parse_args()
 if a.cmd=='verify':sys.exit(0 if validate() else 1)
 if a.cmd=='build':sys.exit(0 if build() else 1)
 if a.cmd=='moodle-plan':sys.exit(0 if moodle_plan() else 1)
 if a.cmd=='deploy':sys.exit(0 if dplan(a.target,a.apply) else 1)
 if a.cmd=='pages-zip':
  import zipfile
  if not validate():sys.exit(1)
  build()
  dest=ROOT/'dist/ekole-site-preview.zip';dest.parent.mkdir(parents=True,exist_ok=True)
  with zipfile.ZipFile(dest,'w',zipfile.ZIP_DEFLATED) as z:
   for f in sorted((ROOT/'site').rglob('*')):
    if f.is_file():z.write(f,f.relative_to(ROOT/'site').as_posix())
  with zipfile.ZipFile(dest) as z:assert z.testzip() is None
  print('Static preview ZIP:',dest,'(not published)')
  return
 if a.cmd=='preview':
  if not (ROOT/'site/data/index.json').exists():build()
  class Handler(http.server.SimpleHTTPRequestHandler):
   def __init__(self,*args,**kwargs):super().__init__(*args,directory=str(ROOT/'site'),**kwargs)
  print('Local preview: http://127.0.0.1:8765/ (Ctrl+C to stop)')
  with http.server.ThreadingHTTPServer(('127.0.0.1',8765),Handler) as server:server.serve_forever()
if __name__=='__main__':main()
