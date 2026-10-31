"""Catalogue facultatif des personnages d'un paquet; aucun lien avec visuals.py.
Les fichiers ne deviennent publics qu'après statut « pret » ET présence d'un PNG valide.
"""
from __future__ import annotations
import json
import re
import struct
from pathlib import Path, PurePosixPath

ID = re.compile(r'[a-z][a-z0-9-]{0,79}\Z')
CATALOGUE = re.compile(r'[A-Za-z0-9_-]+/catalogue\.json\Z')
MAX_BYTES = 12 * 1024 * 1024


def safe_file(root: Path, relative: str) -> Path:
    """Interdit traversées, chemins absolus et liens, y compris répertoires parents."""
    if not isinstance(relative, str) or '\\' in relative:
        raise ValueError('Chemin de personnage invalide')
    parts = relative.split('/')
    if not parts or any(p in ('', '.', '..') for p in parts) or PurePosixPath(relative).is_absolute():
        raise ValueError('Chemin de personnage invalide')
    candidate = root
    for part in parts:
        candidate = candidate / part
        if candidate.is_symlink():
            raise ValueError('Lien symbolique de personnage interdit')
    if not candidate.resolve().is_relative_to(root.resolve()):
        raise ValueError('Chemin de personnage hors catalogue')
    return candidate


def validate(data: dict) -> dict:
    if not isinstance(data, dict) or data.get('format') != 'ekole.personnages/1':
        raise ValueError('Format de catalogue personnages invalide')
    if not isinstance(data.get('compagnons'), list) or not isinstance(data.get('assets'), list):
        raise ValueError('Compagnons et assets doivent être des listes')
    people = {}
    for c in data['compagnons']:
        if not isinstance(c, dict) or not isinstance(c.get('id'), str) or not ID.fullmatch(c['id']) or c['id'] in people:
            raise ValueError('Identifiant de compagnon invalide ou dupliqué')
        if any(not isinstance(c.get(k), str) or not c[k] for k in ('nom','univers_id','univers','sigle')):
            raise ValueError('Description de compagnon incomplète')
        years = c.get('annees'); poses = c.get('poses')
        if not isinstance(years, list) or not years or any(type(y) is not int or not 1 <= y <= 6 for y in years) or len(set(years)) != len(years):
            raise ValueError('Années de compagnon invalides')
        if not isinstance(poses, list) or any(not isinstance(p,str) or not ID.fullmatch(p) for p in poses) or len(set(poses)) != len(poses):
            raise ValueError('Poses invalides')
        if 'role_id' in c and (not isinstance(c['role_id'],str) or not ID.fullmatch(c['role_id'])):
            raise ValueError('Référence de rôle invalide')
        people[c['id']] = c
    seen, files, slots = set(), set(), set()
    for a in data['assets']:
        if not isinstance(a, dict) or not isinstance(a.get('id'),str) or not ID.fullmatch(a['id']) or a['id'] in seen:
            raise ValueError('Identifiant visuel invalide ou dupliqué')
        seen.add(a['id'])
        path = a.get('fichier')
        if not isinstance(path,str) or not re.fullmatch(r'images/(?:[a-z0-9-]+/)+[a-z0-9-]+\.png',path) or path in files:
            raise ValueError('Fichier PNG invalide ou dupliqué')
        files.add(path)
        if a.get('statut') not in ('a_generer','a_verifier','pret') or not isinstance(a.get('alt'),str) or not a['alt'].strip():
            raise ValueError('Statut ou texte alternatif invalide')
        if a.get('type') == 'role':
            rid = a.get('role_id')
            if not isinstance(rid,str) or not ID.fullmatch(rid) or a['id'] != 'role-'+rid:
                raise ValueError('Référence visuelle de rôle incohérente')
            slot = ('role',rid)
        elif a.get('type') == 'compagnon':
            pid = a.get('personnage'); year = a.get('annee'); pose = a.get('pose')
            if not isinstance(pid,str) or pid not in people:
                raise ValueError('Personnage inconnu')
            if year is not None:
                if type(year) is not int or year not in people[pid]['annees'] or pose != 'debout':
                    raise ValueError('Variante scolaire invalide')
                expected = f'compagnon-{pid}-annee-{year:02}'
            else:
                if not isinstance(pose,str) or pose not in people[pid]['poses']: raise ValueError('Pose inconnue')
                expected = f'compagnon-{pid}-pose-{pose}'
            if a['id'] != expected: raise ValueError('Identifiant de variante incohérent')
            slot = ('compagnon',pid,year,pose)
        else:
            raise ValueError('Type de personnage inconnu')
        if slot in slots: raise ValueError('Variante dupliquée')
        slots.add(slot)
    for c in people.values():
        for y in c['annees']:
            if ('compagnon',c['id'],y,'debout') not in slots: raise ValueError('Année manquante')
        for p in c['poses']:
            if ('compagnon',c['id'],None,p) not in slots: raise ValueError('Pose manquante')
        if c.get('role_id') and ('role',c['role_id']) not in slots: raise ValueError('Rôle du compagnon absent')
    aliases = data.get('anciens_choix',{})
    if not isinstance(aliases,dict) or any(not isinstance(k,str) or not ID.fullmatch(k) or not isinstance(v,str) or v not in people for k,v in aliases.items()):
        raise ValueError('Anciens choix invalides')
    return data


def load(root: Path | None, pack: dict):
    relative = pack.get('personnages')
    if root is None or relative is None: return None
    if not isinstance(relative,str) or not CATALOGUE.fullmatch(relative):
        raise ValueError('Référence de catalogue personnages invalide')
    path = safe_file(root,relative)
    if not path.is_file() or path.stat().st_size > 1_000_000: raise ValueError('Catalogue personnages absent ou trop volumineux')
    return path.parent, validate(json.loads(path.read_text(encoding='utf-8-sig')))


def png(root: Path, asset: dict):
    if asset['statut'] != 'pret': return None
    path = safe_file(root,asset['fichier'])
    if not path.is_file() or not 33 <= path.stat().st_size <= MAX_BYTES: return None
    with path.open('rb') as f: head = f.read(33)
    if head[:8] != b'\x89PNG\r\n\x1a\n' or head[12:16] != b'IHDR': return None
    w,h = struct.unpack('>II',head[16:24])
    return path if 1 <= w <= 8192 and 1 <= h <= 8192 else None


def public_inventory(loaded):
    if loaded is None:
        return {'format':'ekole.personnages/1','compagnons':[],'anciens_choix':{},'assets':[]}
    root,data = loaded
    assets=[]
    for a in data['assets']:
        public={k:v for k,v in a.items() if k in ('id','type','personnage','annee','pose','role_id','alt')}
        present = png(root,a) is not None
        public['disponible'] = present
        public['url'] = '/api/personnages/image/'+a['id'] if present else None
        assets.append(public)
    return {'format':data['format'],'compagnons':data['compagnons'],
            'anciens_choix':data.get('anciens_choix',{}),'assets':assets}


def image_file(loaded, asset_id):
    if loaded is None: return None
    root,data = loaded
    asset = next((a for a in data['assets'] if a['id']==asset_id),None)
    return png(root,asset) if asset else None
