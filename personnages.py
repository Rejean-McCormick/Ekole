"""Catalogue facultatif des personnages d'un paquet; aucun lien avec visuals.py.
Les fichiers ne deviennent publics qu'après statut « pret » ET présence d'un PNG valide.
"""
from __future__ import annotations
import hashlib
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
    if isinstance(data, dict) and data.get('format') == 'ekole.personnages/4':
        return validate_v4(data)
    if isinstance(data, dict) and data.get('format') == 'ekole.personnages/3':
        return validate_v3(data)
    if isinstance(data, dict) and data.get('format') == 'ekole.personnages/2':
        return validate_v2(data)
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
        if 'sha256' in a and (not isinstance(a['sha256'], str)
                              or not re.fullmatch(r'sha256:[0-9a-f]{64}', a['sha256'])):
            raise ValueError('Empreinte de personnage invalide')
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



def validate_v2(data: dict) -> dict:
    """38 rôles/compagnons partagent un portrait neutre, plus leurs poses.

    La validation n’impose pas « 38 » pour permettre l’extension à d’autres packs.
    Chaque pose annoncée par un compagnon doit avoir un seul asset stable.
    """
    companions = data.get('compagnons')
    assets = data.get('assets')
    poses = data.get('poses')
    if not all(isinstance(x, list) for x in (companions, assets, poses)) or not poses or poses[0] != 'neutre':
        raise ValueError('Structure du catalogue de rôles/compagnons invalide')
    if len(set(poses)) != len(poses) or any(not isinstance(p, str) or not ID.fullmatch(p) for p in poses):
        raise ValueError('Liste de poses invalide')
    people = {}
    for c in companions:
        if not isinstance(c, dict) or any(not isinstance(c.get(k), str) or not c[k] for k in ('id','nom','sigle','role_id')):
            raise ValueError('Compagnon-rôle incomplet')
        cid = c['id']
        if not ID.fullmatch(cid) or cid in people or c['role_id'] != cid or c.get('poses') != poses:
            raise ValueError('Identité ou poses du compagnon-rôle incohérentes')
        people[cid] = c
    seen, files, slots = set(), set(), set()
    for a in assets:
        if not isinstance(a, dict) or not isinstance(a.get('id'),str) or not ID.fullmatch(a['id']) or a['id'] in seen:
            raise ValueError('ID de ressource incorrect ou dupliqué')
        seen.add(a['id'])
        filename = a.get('fichier')
        if not isinstance(filename, str) or not re.fullmatch(r'images/(?:[a-z0-9-]+/)+[a-z0-9-]+\.png', filename) or filename in files:
            raise ValueError('Chemin PNG incorrect ou dupliqué')
        files.add(filename)
        if a.get('statut') not in ('a_generer','a_verifier','pret') or not isinstance(a.get('alt'),str) or not a['alt'].strip():
            raise ValueError('Statut ou texte alternatif invalide')
        if 'sha256' in a and (not isinstance(a['sha256'],str) or not re.fullmatch(r'sha256:[0-9a-f]{64}',a['sha256'])):
            raise ValueError('Empreinte de ressource invalide')
        if a.get('type') == 'role':
            cid = a.get('role_id')
            if cid not in people or a['id'] != 'role-'+cid or a.get('pose') != 'neutre':
                raise ValueError('Portrait neutre sans rôle valide')
            slot = (cid, 'neutre')
        elif a.get('type') == 'compagnon':
            cid = a.get('personnage')
            pose = a.get('pose')
            if cid not in people or pose not in poses[1:] or a.get('role_id') != cid or a['id'] != f'compagnon-{cid}-pose-{pose}':
                raise ValueError('Pose sans compagnon-rôle valide')
            slot = (cid, pose)
        else:
            raise ValueError('Type d’image inconnu')
        if slot in slots: raise ValueError('Pose en double')
        slots.add(slot)
    required = {(cid, pose) for cid in people for pose in poses}
    if slots != required:
        raise ValueError(f'Poses absentes ou superflues ({len(required - slots)} manquantes)')
    aliases=data.get('anciens_choix',{})
    if not isinstance(aliases,dict) or any(not isinstance(k,str) or not ID.fullmatch(k) or not isinstance(v,str) or v not in people for k,v in aliases.items()):
        raise ValueError('Ancien choix de compagnon invalide')
    return data

def validate_v3(data: dict) -> dict:
    """Deux compagnons (garçon/fille) par rôle, huit poses chacun.

    Préserve les IDs v2 pour les garçons, y compris le visuel canonique
    role-<id> utilisé par Kontexte et les cartes de rôle.
    """
    validate_v2_compatible = data.get('poses')
    if not isinstance(validate_v2_compatible, list) or len(validate_v2_compatible) != 8 or validate_v2_compatible[0] != 'neutre':
        raise ValueError('Huit poses requises')
    if data.get('presentations') != ['garcon', 'fille']:
        raise ValueError('Présentations garçon/fille requises')
    people = data.get('compagnons')
    assets = data.get('assets')
    if not isinstance(people, list) or not isinstance(assets, list):
        raise ValueError('Compagnons/assets manquants')
    lookup = {}
    for c in people:
        if not isinstance(c, dict) or any(not isinstance(c.get(k), str) or not c[k] for k in ('id','nom','sigle','role_id','presentation')):
            raise ValueError('Compagnon incomplet')
        role, presentation, cid = c['role_id'], c['presentation'], c['id']
        if (not ID.fullmatch(role) or presentation not in ('garcon','fille') or
            cid != (role if presentation == 'garcon' else role+'-fille') or
            cid in lookup or c.get('poses') != validate_v2_compatible):
            raise ValueError('Compagnon garçon/fille incohérent')
        lookup[cid] = c
    roles = {c['role_id'] for c in people}
    if len(people) != len(roles)*2 or any(f'{r}-fille' not in lookup or r not in lookup for r in roles):
        raise ValueError('Il faut un garçon et une fille par rôle')
    seen_ids, seen_files, slots = set(), set(), set()
    for a in assets:
        if not isinstance(a, dict) or not isinstance(a.get('id'), str) or not ID.fullmatch(a['id']) or a['id'] in seen_ids:
            raise ValueError('ID de ressource incorrect ou répété')
        seen_ids.add(a['id'])
        filename = a.get('fichier')
        if (not isinstance(filename, str) or
            not re.fullmatch(r'images/(?:[a-z0-9-]+/)+[a-z0-9-]+\.png', filename) or filename in seen_files):
            raise ValueError('Chemin PNG incorrect ou répété')
        seen_files.add(filename)
        if a.get('statut') not in ('a_generer','a_verifier','pret') or not isinstance(a.get('alt'),str) or not a['alt'].strip():
            raise ValueError('Statut/texte alternatif invalide')
        if 'sha256' in a and (not isinstance(a['sha256'],str) or not re.fullmatch(r'sha256:[0-9a-f]{64}',a['sha256'])):
            raise ValueError('Empreinte invalide')
        role, presentation = a.get('role_id'), a.get('presentation')
        cid = role if presentation == 'garcon' else (role+'-fille' if presentation == 'fille' and isinstance(role,str) else None)
        if cid not in lookup or lookup[cid]['presentation'] != presentation:
            raise ValueError('Identité de ressource sans compagnon')
        if a.get('type') == 'role':
            expected_id = f'role-{cid}'
            expected_file = f'images/roles/{cid}.png'
            pose = 'neutre'
            if a.get('pose') != 'neutre': raise ValueError('Portrait neutre invalide')
        elif a.get('type') == 'compagnon':
            pose = a.get('pose')
            if pose not in validate_v2_compatible[1:] or a.get('personnage') != cid:
                raise ValueError('Pose ou propriétaire invalide')
            expected_id = f'compagnon-{cid}-pose-{pose}'
            expected_file = f'images/compagnons/{cid}/pose-{pose}.png'
        else:
            raise ValueError('Type invalide')
        if a['id'] != expected_id or filename != expected_file or (cid,pose) in slots:
            raise ValueError('Identifiant/chemin/pose incohérent')
        slots.add((cid,pose))
    expected = {(cid,pose) for cid in lookup for pose in validate_v2_compatible}
    if slots != expected: raise ValueError('Pose manquante ou superflue')
    aliases=data.get('anciens_choix',{})
    if not isinstance(aliases,dict) or any(not isinstance(k,str) or not ID.fullmatch(k) or not isinstance(v,str) or v not in lookup for k,v in aliases.items()):
        raise ValueError('Ancien choix invalide')
    return data


def validate_v4(data: dict) -> dict:
    """Cinq variantes d'origine, deux genres. Conservation stricte des IDs /3."""
    from collections import Counter
    from copy import deepcopy
    origins = ['original','asiatique','noir','autochtone','arabe']
    if (data.get('origines') != origins or data.get('presentations') != ['garcon','fille'] or
        not isinstance(data.get('poses'),list) or len(data['poses'])!=8):
        raise ValueError('Origines, présentations ou poses invalides.')
    people = data.get('compagnons');assets=data.get('assets')
    if not isinstance(people,list) or not isinstance(assets,list):
        raise ValueError('Catalogue incomplet.')
    roles={c.get('role_id') for c in people if isinstance(c,dict)}
    if None in roles or not roles or len(people)!=len(roles)*10 or len(assets)!=len(roles)*80:
        raise ValueError('Couverture rôles × genres × variantes × poses incomplète.')
    index={}
    for c in people:
        role,genre,origine=c.get('role_id'),c.get('presentation'),c.get('origine')
        if (not isinstance(role,str) or not ID.fullmatch(role) or genre not in ['garcon','fille'] or origine not in origins):
            raise ValueError('Identité de compagnon invalide.')
        cid=role+('-fille' if genre=='fille' else '')+('-'+origine if origine!='original' else '')
        if c.get('id')!=cid or cid in index or c.get('poses')!=data['poses']:
            raise ValueError('Identifiant de compagnon incohérent ou répété.')
        index[cid]=c
    slots=set(); seen=set(); paths=set()
    for a in assets:
        if not isinstance(a,dict) or not isinstance(a.get('id'),str) or not ID.fullmatch(a['id']) or a['id'] in seen:
            raise ValueError('Ressource dupliquée ou invalide.')
        seen.add(a['id'])
        cid=a['id'][5:] if a.get('type')=='role' else a.get('personnage')
        c=index.get(cid)
        if not c or a.get('role_id')!=c['role_id'] or a.get('origine')!=c['origine'] or a.get('presentation')!=c['presentation']:
            raise ValueError('Ressource sans compagnon de même genre/origine.')
        pose=a.get('pose');fil=a.get('fichier')
        if a['type']=='role':
            expect='role-'+cid;expectedfile='images/roles/'+cid+'.png'
            if pose!='neutre': raise ValueError('Maître invalide.')
        elif a['type']=='compagnon':
            if pose not in data['poses'][1:]:raise ValueError('Pose invalide.')
            expect=f'compagnon-{cid}-pose-{pose}';expectedfile=f'images/compagnons/{cid}/pose-{pose}.png'
        else:raise ValueError('Type invalide.')
        if a['id']!=expect or fil!=expectedfile or fil in paths:
            raise ValueError('ID ou chemin de ressource invalide.')
        if a.get('statut') not in ('a_generer','a_verifier','pret') or not isinstance(a.get('alt'),str) or not a['alt']:
            raise ValueError('Statut ou description invalide.')
        if 'sha256' in a and (not isinstance(a['sha256'],str) or not re.fullmatch(r'sha256:[0-9a-f]{64}',a['sha256'])):
            raise ValueError('Empreinte invalide.')
        paths.add(fil);slots.add((cid,pose))
    if slots!={(cid,pose) for cid in index for pose in data['poses']}:
        raise ValueError('Poses manquantes.')
    aliases=data.get('anciens_choix',{})
    if not isinstance(aliases,dict) or any(v not in index for v in aliases.values()):
        raise ValueError('Ancien choix invalide.')
    return data


def validate_free_illustrations(data: dict) -> None:
    """Vérifie la collection indépendante sans modifier le contrat /4 historique."""
    libres = data.get('illustrations_libres', [])
    if not isinstance(libres,list) or len(libres)>len(data.get('poses',[]))*len({c['role_id'] for c in data.get('compagnons',[])}):
        raise ValueError('Collection d’illustrations libres invalide.')
    roles={c['role_id'] for c in data.get('compagnons',[])}
    poses=set(data.get('poses',[]))
    seen=set()
    for a in libres:
        if not isinstance(a,dict) or a.get('type')!='libre':
            raise ValueError('Illustration libre invalide.')
        rid,pose=a.get('role_id'),a.get('pose')
        key=f'libre-{rid}-{pose}'
        if (rid not in roles or pose not in poses or a.get('id')!=key or key in seen or
            a.get('fichier')!=f'images/illustrations-libres/{rid}/{pose}.png' or
            a.get('origine') not in ('original','asiatique','noir','autochtone','arabe') or
            a.get('presentation') not in ('garcon','fille') or
            a.get('statut') not in ('a_generer','a_verifier','pret') or
            not isinstance(a.get('alt'),str) or not a.get('alt')):
            raise ValueError('Description d’illustration libre incorrecte.')
        sha=a.get('sha256')
        if sha is not None and (not isinstance(sha,str) or not re.fullmatch(r'sha256:[0-9a-f]{64}',sha)):
            raise ValueError('Empreinte d’illustration libre incorrecte.')
        seen.add(key)


def validate_free_illustrations(data: dict) -> None:
    """Vérifie la collection indépendante sans modifier le contrat /4 historique."""
    libres = data.get('illustrations_libres', [])
    if not isinstance(libres,list) or len(libres)>len(data.get('poses',[]))*len({c['role_id'] for c in data.get('compagnons',[])}):
        raise ValueError('Collection d’illustrations libres invalide.')
    roles={c['role_id'] for c in data.get('compagnons',[])}
    poses=set(data.get('poses',[]))
    seen=set()
    for a in libres:
        if not isinstance(a,dict) or a.get('type')!='libre':
            raise ValueError('Illustration libre invalide.')
        rid,pose=a.get('role_id'),a.get('pose')
        key=f'libre-{rid}-{pose}'
        if (rid not in roles or pose not in poses or a.get('id')!=key or key in seen or
            a.get('fichier')!=f'images/illustrations-libres/{rid}/{pose}.png' or
            a.get('origine') not in ('original','asiatique','noir','autochtone','arabe') or
            a.get('presentation') not in ('garcon','fille') or
            a.get('statut') not in ('a_generer','a_verifier','pret') or
            not isinstance(a.get('alt'),str) or not a.get('alt')):
            raise ValueError('Description d’illustration libre incorrecte.')
        sha=a.get('sha256')
        if sha is not None and (not isinstance(sha,str) or not re.fullmatch(r'sha256:[0-9a-f]{64}',sha)):
            raise ValueError('Empreinte d’illustration libre incorrecte.')
        seen.add(key)


def load(root: Path | None, pack: dict):
    relative = pack.get('personnages')
    if root is None or relative is None: return None
    if not isinstance(relative,str) or not CATALOGUE.fullmatch(relative):
        raise ValueError('Référence de catalogue personnages invalide')
    path = safe_file(root,relative)
    if not path.is_file() or path.stat().st_size > 4_000_000: raise ValueError('Catalogue personnages absent ou trop volumineux')
    data = validate(json.loads(path.read_text(encoding='utf-8-sig')))
    if data.get('format') == 'ekole.personnages/4': validate_free_illustrations(data)
    return path.parent, data


def png(root: Path, asset: dict):
    if asset['statut'] != 'pret': return None
    path = safe_file(root,asset['fichier'])
    if not path.is_file() or not 33 <= path.stat().st_size <= MAX_BYTES: return None
    with path.open('rb') as f: head = f.read(33)
    if head[:8] != b'\x89PNG\r\n\x1a\n' or head[12:16] != b'IHDR': return None
    expected = asset.get('sha256')
    if expected and expected != 'sha256:' + hashlib.sha256(path.read_bytes()).hexdigest():
        return None
    w,h = struct.unpack('>II',head[16:24])
    return path if 1 <= w <= 8192 and 1 <= h <= 8192 else None


def public_inventory(loaded, published=()):
    if loaded is None:
        return {'format':'ekole.personnages/1','compagnons':[],'anciens_choix':{},'assets':[]}
    root,data = loaded
    assets=[]
    for a in [*data['assets'], *data.get('illustrations_libres',[])]:
        public={k:v for k,v in a.items() if k in ('id','type','personnage','annee','pose','role_id','presentation','origine','alt')}
        present = a['id'] in published or png(root,a) is not None
        public['disponible'] = present
        public['url'] = '/api/personnages/image/'+a['id'] if present else None
        assets.append(public)
    return {'format':data['format'],'compagnons':data['compagnons'],
            'anciens_choix':data.get('anciens_choix',{}),'assets':assets}


def image_file(loaded, asset_id):
    if loaded is None: return None
    root,data = loaded
    asset = next((a for a in [*data['assets'], *data.get('illustrations_libres',[])] if a['id']==asset_id),None)
    return png(root,asset) if asset else None
