#!/usr/bin/env python3
"""Compile reviewed media into student's allowlisted assets (no generation, no remote calls).
No modification on --dry-run. Does not forge a v9 or v10 publication.
Requires Pillow to validate dimensions and file format when applying.
"""
from __future__ import annotations
import argparse,hashlib,json,pathlib,re,shutil
ROOT=pathlib.Path(__file__).resolve().parents[1]

class MediaRejection(ValueError):pass

def inspect(root, approvals, check_images=False):
    root=pathlib.Path(root).resolve(); approvals=pathlib.Path(approvals).resolve()
    registry=json.loads((root/'visuels/INTENTIONS_IMAGES.json').read_text(encoding='utf-8'))
    allowed={v['visual_id']:v for v in registry['intents']}
    manifest=json.loads(approvals.read_text(encoding='utf-8'))
    if manifest.get('format')!='ekole.approved-images/1.0':raise MediaRejection('Format manifeste incompatible')
    seen=set();selected=[]
    for m in manifest.get('assets',[]):
        id=m.get('visual_id');src=m.get('file')
        if id not in allowed or id in seen:raise MediaRejection('Identifiant inconnu ou répété')
        seen.add(id)
        if not isinstance(src,str) or not re.fullmatch(r'images_a_approuver/[a-zA-Z0-9._-]+\.(webp|png)',src):raise MediaRejection('Chemin d image non autorisé')
        source=(root/'visuels'/src).resolve()
        if not source.is_relative_to((root/'visuels/images_a_approuver').resolve()):raise MediaRejection('Path traversal')
        if not source.is_file() or source.is_symlink():raise MediaRejection('Fichier source absent ou symlink')
        if any(m.get(k) is not True for k in ['pedagogical_review','accessibility_review','rights_review']):raise MediaRejection('Revue manquante')
        if not isinstance(m.get('alt_fr_CA'),str) or len(m['alt_fr_CA'].strip())<8:raise MediaRejection('Texte alternatif insuffisant')
        if not isinstance(m.get('licence'),str) or len(m['licence'].strip())<12:raise MediaRejection('Droit non documenté')
        if not isinstance(m.get('credit'),str) or len(m['credit'].strip())<3:raise MediaRejection('Crédit manquant')
        raw=source.read_bytes()
        if len(raw)>6_000_000:raise MediaRejection('Fichier trop gros')
        digest=hashlib.sha256(raw).hexdigest()
        if m.get('sha256')!=digest:raise MediaRejection('Empreinte SHA256 incorrecte')
        if check_images:
            try:
                from PIL import Image
                with Image.open(source) as im:
                    im.verify()
                with Image.open(source) as im:
                    if im.format not in ('WEBP','PNG'):raise MediaRejection('Image hors des formats WEBP/PNG')
                    w,h=im.size
                    if w<160 or h<160 or w>7000 or h>7000:raise MediaRejection('Dimensions insuffisantes/excessives')
            except ImportError:raise MediaRejection('Pillow requis pour vérifier des images réelles')
        # Re-encode/copy to same original format; declared approved future path is not used blindly
        output=f'assets/images/{id}.{source.suffix.lstrip(".")}'
        selected.append({'visual_id':id,'path':output,'alt_fr_CA':m['alt_fr_CA'].strip(),'sha256':digest,
                         'rights_notice':m['licence'],'credit':m['credit'],'review_status':'approved_for_local_student_preview',
                         '_private_file':str(source)})
    return selected

def compile_assets(root,approvals,apply=False):
    root=pathlib.Path(root).resolve(); entries=inspect(root,approvals,check_images=apply)
    if not apply:return {'mode':'dry-run','approved_count':len(entries),'files':[e['path'] for e in entries]}
    out_dir=root/'site/eleve/assets/images'
    if out_dir.is_symlink():raise MediaRejection('Repertoire image symlink interdit')
    out_dir.mkdir(parents=True,exist_ok=True)
    if not out_dir.resolve().is_relative_to((root/'site/eleve').resolve()):raise MediaRejection('Destination hors du site')
    result=[]
    for e in entries:
        target=root/'site/eleve'/e['path']
        # collision guard; no removal of prior images, no silent overwrites
        if target.is_symlink() or not target.resolve().is_relative_to((root/'site/eleve').resolve()):
            raise MediaRejection('Destination symlink / hors du site')
        if target.exists() and hashlib.sha256(target.read_bytes()).hexdigest()!=e['sha256']:
            raise MediaRejection('Fichier déjà présent avec contenu différent : '+e['path'])
    for e in entries:
        target=root/'site/eleve'/e['path'];target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(e['_private_file'],target)
        result.append({k:v for k,v in e.items() if not k.startswith('_')})
    manifest={'format':'ekole.image-placement/1.0','status':'images_approuvees_localement_non_publiees','assets':result}
    dest=root/'site/eleve/data/assets-manifest.json'
    dest.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return {'mode':'applied','approved_count':len(result),'manifest':str(dest)}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',default=str(ROOT));p.add_argument('--approvals',required=True)
    p.add_argument('--apply',action='store_true');a=p.parse_args();print(json.dumps(compile_assets(a.root,a.approvals,a.apply),ensure_ascii=False,indent=2))
