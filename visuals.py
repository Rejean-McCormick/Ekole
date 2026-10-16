"""Ressources visuelles des Kristals: dépôt, approbation et lecture publique contrôlée.
Aucun appel à un service d'IA; Python stdlib uniquement.
"""
from __future__ import annotations
import hashlib
import json
import os
import pathlib
import secrets
import struct

EXTS = {'png':'png','jpeg':'jpg','webp':'webp'}
MIMES = {'png':'image/png','jpeg':'image/jpeg','webp':'image/webp'}
MAX_BYTES = 12 * 1024 * 1024


def image_info(buf: bytes):
    """Détecte format et dimensions à partir des en-têtes (sans décoder le raster)."""
    if buf[:8] == b'\x89PNG\r\n\x1a\n' and buf[12:16] == b'IHDR':
        width, height = struct.unpack('>II',buf[16:24]); fmt='png'
    elif buf[:2] == b'\xff\xd8':
        fmt='jpeg'; width=height=0; off=2
        while off < len(buf)-10:
            if buf[off] != 0xff: off+=1; continue
            while off<len(buf) and buf[off]==0xff:off+=1
            if off>=len(buf):break
            mark=buf[off];off+=1
            if mark==0xd9 or mark==0xda:break
            if mark in (0x01,*range(0xd0,0xd9)):continue
            if off+2>len(buf):break
            length=int.from_bytes(buf[off:off+2],'big')
            if length<2 or off+length>len(buf):break
            if mark in (0xc0,0xc1,0xc2,0xc3,0xc5,0xc6,0xc7,0xc9,0xca,0xcb,0xcd,0xce,0xcf):
                height=int.from_bytes(buf[off+3:off+5],'big');width=int.from_bytes(buf[off+5:off+7],'big');break
            off+=length
    elif buf[:4]==b'RIFF' and buf[8:12]==b'WEBP':
        fmt='webp';width=height=0;tag=buf[12:16]
        if tag==b'VP8X' and len(buf)>=30:
            width=1+int.from_bytes(buf[24:27],'little');height=1+int.from_bytes(buf[27:30],'little')
        elif tag==b'VP8L' and len(buf)>=25 and buf[20]==0x2f:
            bits=int.from_bytes(buf[21:25],'little');width=(bits&0x3fff)+1;height=((bits>>14)&0x3fff)+1
        elif tag==b'VP8 ' and len(buf)>=30 and buf[23:26]==b'\x9d\x01\x2a':
            width=int.from_bytes(buf[26:28],'little')&0x3fff;height=int.from_bytes(buf[28:30],'little')&0x3fff
    else:
        raise ValueError('Fichier non reconnu comme PNG, JPEG ou WebP')
    if not 120<=width<=8192 or not 120<=height<=8192:
        raise ValueError('Dimensions invalides: 120 à 8192 pixels par côté')
    return fmt,width,height


def manifest(root: pathlib.Path, cid: str):
    p=root/'kristals'/cid/'experience'/'RESSOURCES_VISUELLES.json'
    if p.is_symlink() or not p.is_file() or not p.resolve().is_relative_to(root.resolve()):return None
    obj=json.loads(p.read_text(encoding='utf-8-sig'))
    if not isinstance(obj.get('visuels'),list):return None
    return obj


def entries(root,cid):
    data=manifest(root,cid)
    return {x['slot']:x for x in data.get('visuels',[]) if isinstance(x,dict) and isinstance(x.get('slot'),str) and x['slot'].isidentifier()} if data else {}


def images_dir(root,cid):
    p=root/'kristals'/cid/'experience'/'images'
    if p.is_symlink() or not p.resolve().is_relative_to(root.resolve()):raise ValueError('Dossier visuel interdit')
    return p


def locate(root,cid,slot):
    folder=images_dir(root,cid)
    for suffix in ('webp','png','jpg','jpeg'):
        f=folder/f'{slot}.{suffix}'
        if f.is_file() and not f.is_symlink() and f.resolve().is_relative_to(root.resolve()):return f
    return None


def review_path(root,cid):
    return root/'publications'/'visuels'/f'{cid}.json'


def review(root,cid):
    file=review_path(root,cid)
    if file.is_symlink():raise ValueError('Fichier de validation interdit')
    if not file.is_file():return {'format':'ekole.visual-review/1','cours_id':cid,'published':{}}
    data=json.loads(file.read_text(encoding='utf-8'))
    if not isinstance(data.get('published'),dict):raise ValueError('Format de revue invalide')
    return data


def atomic_json(path,obj):
    path.parent.mkdir(parents=True,exist_ok=True)
    if path.is_symlink():raise ValueError('Chemin de validation interdit')
    temp=path.with_name(path.name+'.tmp-'+secrets.token_hex(5))
    try:
        temp.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
        os.replace(temp,path)
    finally:temp.unlink(missing_ok=True)


def published_file(root,cid,slot):
    info=review(root,cid).get('published',{}).get(slot)
    if not info:return None
    p=locate(root,cid,slot)
    if not p or p.name!=info.get('file_name'):return None
    if hashlib.sha256(p.read_bytes()).hexdigest()!=info.get('sha256'):return None
    return p


def teacher_inventory(root,cid):
    data=entries(root,cid);published=review(root,cid)['published']
    output=[]
    for slot,v in data.items():
        f=locate(root,cid,slot)
        output.append({'slot':slot,'placement':v.get('placement',''),'alt':v.get('texte_alternatif',''),
                       'prompt':v.get('prompt_conceptuel',''),'statut_source':v.get('statut',''),
                       'file_name':f.name if f else None,'published': bool(published_file(root,cid,slot))})
    return {'cours_id':cid,'visuels':output,'edition_possible':True}


def public_inventory(root,cid):
    output=[]
    for slot,v in entries(root,cid).items():
        if published_file(root,cid,slot):
            output.append({'slot':slot,'placement':v.get('placement',''),
                           'alt':v.get('texte_alternatif','Illustration de la leçon'),
                           'url':f'/api/media/{cid}/{slot}'})
    return {'cours_id':cid,'visuels':output}


def save_image(root,cid,slot,buf,replace=False):
    if not 30<=len(buf)<=MAX_BYTES:raise ValueError('Taille de fichier invalide (12 Mo maximum)')
    fmt,width,height=image_info(buf)
    images=images_dir(root,cid);images.mkdir(parents=True,exist_ok=True)
    old=locate(root,cid,slot)
    if old and not replace:raise FileExistsError('Une image est déjà présente. Confirmer son remplacement.')
    new=images/f'{slot}.{EXTS[fmt]}'
    backup=None
    if old:
        backup_dir=root/'.ekole-sauvegardes'/'visuels'/cid
        backup_dir.mkdir(parents=True,exist_ok=True)
        backup=backup_dir/(old.name+'.'+secrets.token_hex(8)+'.bak')
        backup.write_bytes(old.read_bytes())
    temp=images/(slot+'.tmp-'+secrets.token_hex(8))
    try:
        temp.write_bytes(buf)
        os.replace(temp,new)
        if old and old!=new:old.unlink()
    finally:temp.unlink(missing_ok=True)
    current=review(root,cid);current['published'].pop(slot,None)
    atomic_json(review_path(root,cid),current)
    return {'file_name':new.name,'width':width,'height':height,'format':fmt,'published':False,'backup':backup.name if backup else None}


def set_publication(root,cid,slot,enable):
    data=review(root,cid)
    if enable:
        f=locate(root,cid,slot)
        if not f:raise ValueError('Aucune image à approuver')
        data['published'][slot]={'file_name':f.name,'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),
                                  'validation':'confirmation_manuelle_enseignant'}
    else:data['published'].pop(slot,None)
    atomic_json(review_path(root,cid),data)
    return {'published':bool(enable)}
