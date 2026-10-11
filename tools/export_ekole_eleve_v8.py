#!/usr/bin/env python3
"""Strict student-only static export, no teacher data, no source answer keys. No overwrite."""
import pathlib,json,shutil,re,argparse,hashlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
ALLOWED=('index.html','app.js','atelier-v8.js','style.css','v8.css','assets/ekole-logo.svg',
         'data/eleves/catalogue.json','data/eleves/ateliers-v8.json',
         'data/eleves/integrations.json','data/eleves/konstellation-light-candidat.json',
         'data/konstellation-liens.json','data/visuels_public.json','data/assets-manifest.json',
         'data/kristals-visuels.json','data/kristals-experiences.json','data/activites-v14.json',
         'labo/index.html','labo/lab.css','labo/app.js','labo/engine.js','labo/embed.js','labo/data/catalogue.json','labo/data/associations-v14.json',
         'mondes-v12/index.html','mondes-v12/style.css','mondes-v12/engine.js','mondes-v12/app.js','mondes-v12/data/catalogue.json')

def export(root,out):
    root=pathlib.Path(root).resolve();out=pathlib.Path(out).resolve();src=root/'site/eleve'
    if out==root or root in out.parents or src==out:raise ValueError('Exporter hors du dépôt pour isoler les données')
    if out.exists():raise FileExistsError('Destination doit être nouvelle : aucune suppression')
    manifest=json.loads((src/'data/assets-manifest.json').read_text(encoding='utf-8'))
    extra=[]
    for m in manifest.get('assets',[]):
        rel=m.get('path','')
        if not re.fullmatch(r'assets/images/[a-z0-9_-]+\.(webp|png)',rel):raise ValueError('Asset non autorisé dans manifeste')
        p=src/rel
        if not p.resolve().is_relative_to(src.resolve()) or not p.is_file() or p.is_symlink() or hashlib.sha256(p.read_bytes()).hexdigest()!=m['sha256']:
            raise ValueError('Asset manquant ou empreinte incorrecte')
        if m.get('review_status')!='approved_for_local_student_preview':raise ValueError('Validation absente')
        extra.append(rel)
    # Ne copier que les images référencées par le manifeste public compilé,
    # jamais le dossier source Kristal ou les réponses de l'enseignant.
    public_visuels=json.loads((src/'data/kristals-visuels.json').read_text(encoding='utf-8'))
    for course in public_visuels.get('cours',{}).values():
        for v in course.get('visuels',[]):
            rel=v.get('url')
            if not rel:continue
            if not re.fullmatch(r'assets/kristals/qc-pri-[a-z]+-[0-9]{3}/[a-z][a-z0-9_-]{1,48}\.(webp|png|jpg|jpeg)',rel):
                raise ValueError('Chemin de visuel Kristal non autorisé: '+str(rel))
            p=src/rel
            if not p.is_file() or p.is_symlink() or not p.resolve().is_relative_to(src.resolve()):
                raise ValueError('Image Kristal compilée absente ou invalide: '+rel)
            extra.append(rel)
    # Images v12 seulement si présentes dans la projection validée et empreinte correcte.
    worlds=json.loads((src/'mondes-v12/data/catalogue.json').read_text(encoding='utf-8'))
    for item in worlds.get('items',[]):
        rel=item.get('image_url')
        if not rel:continue
        full='mondes-v12/'+rel
        if not re.fullmatch(r'mondes-v12/assets/qc-pri-[a-z]+-\d{3}/[a-z0-9-]+\.(webp|png|jpg|jpeg)',full):
            raise ValueError('Image v12 chemin non autorisé')
        path=src/full
        if path.is_symlink() or not path.is_file() or not path.resolve().is_relative_to(src.resolve()):
            raise ValueError('Image v12 invalide')
        if hashlib.sha256(path.read_bytes()).hexdigest()!=item.get('image_sha256'):
            raise ValueError('Image v12 empreinte discordante')
        extra.append(full)
    # New course->tool references contain no lesson-source answer bank; verify IDs and ownership.
    refs=json.loads((src/'data/activites-v14.json').read_text(encoding='utf-8'))
    guard=json.loads((src/'labo/data/associations-v14.json').read_text(encoding='utf-8'))
    labs=json.loads((src/'labo/data/catalogue.json').read_text(encoding='utf-8'))
    byid={q['id']:q for q in labs['items']}
    if refs.get('format')!='ekole.activities-references/1.0' or guard.get('format')!='ekole.activities-access/1.0':
        raise ValueError('Projections v14 non reconnues')
    for course,activities in refs['cours'].items():
        ids=[x['id'] for x in activities]
        if guard['cours'].get(course)!=ids or any(byid.get(id,{}).get('source_kristal_id')!=course for id in ids):
            raise ValueError('Association de cours invalide: '+course)
    copied=[];out.mkdir(parents=True)
    for rel in [*ALLOWED,*extra]:
        p=src/rel
        if not p.is_file():raise FileNotFoundError(rel)
        t=out/rel;t.parent.mkdir(parents=True,exist_ok=True)
        raw=p.read_bytes()
        if rel=='data/konstellation-liens.json':
            j=json.loads(raw);j['preview_local_url']=None
            j['note']='Démonstration localhost retirée de la version élève publique. Publication v10 non revendiquée.'
            raw=(json.dumps(j,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
        if rel=='data/visuels_public.json':
            j=json.loads(raw);j['source']='identifiants_visuels_publics_candidats';raw=(json.dumps(j,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
        if rel=='data/eleves/integrations.json':
            j=json.loads(raw);j['konstellation_light']['enabled']=False;j['konstellation_light']['public_url']=None
            j['konstellation_light']['verified_collection']=False
            raw=(json.dumps(j,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
        t.write_bytes(raw);copied.append(rel)
    if len(json.loads((out/'data/eleves/catalogue.json').read_text(encoding='utf-8'))['courses'])!=202:
        raise ValueError('Catalogue incomplet')
    for p in out.rglob('*'):
        if p.is_file() and p.suffix in ('.json','.js','.html'):
            s=p.read_text(encoding='utf-8')
            if 'BANQUE_ITEMS' in s or 'INTENTIONS_IMAGES' in s or 'teacher_session' in s:
                raise ValueError('Référence aux données adultes: '+str(p))
    return {'exported':len(copied),'source':str(src),'destination':str(out),'files':copied}

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--root',default=str(ROOT));ap.add_argument('--out',required=True)
    args=ap.parse_args();print(json.dumps(export(args.root,args.out),ensure_ascii=False,indent=2))
