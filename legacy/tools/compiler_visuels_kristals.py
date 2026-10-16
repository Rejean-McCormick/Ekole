#!/usr/bin/env python3
"""Compile la couche visuelle des Kristals en données PUBLIQUES sans corrigés.

Un fichier existe uniquement si un auteur le dépose dans kristals/<id>/experience/images/.
Les fichiers absents produisent un prompt visible dans l'interface, jamais une image inventée.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import sys
from pathlib import Path

ID = re.compile(r"^qc-pri-[a-z]+-[0-9]{3}$")
SLOT = re.compile(r"^[a-z][a-z0-9_-]{1,48}$")
EXTS = (".webp", ".png", ".jpg", ".jpeg")
F = "ekole.kristal-visual-layer/1.0"
PUB = "ekole.kristal-visual-public/1.0"
MAX_FILE = 12 * 1024 * 1024


def safe_image(p: Path, workspace: Path) -> bool:
    """Reject links, external paths, oversize files, misleading extension and malformed images."""
    if not p.is_file() or p.is_symlink() or p.stat().st_size > MAX_FILE or p.stat().st_size < 20:
        return False
    if not p.resolve().is_relative_to(workspace.resolve()):
        return False
    try:
        from PIL import Image
        with Image.open(p) as im:
            fmt = im.format
            width, height = im.size
            if im.n_frames != 1 or width < 120 or height < 120 or width * height > 30_000_000:
                return False
            if fmt != {'.webp':'WEBP','.png':'PNG','.jpg':'JPEG','.jpeg':'JPEG'}.get(p.suffix.lower()):
                return False
            im.verify()
        return True
    except Exception:
        # Pillow requis pour publier les images ; pas pour compiler les prompts.
        return False


def compile_layer(root: Path, strict: bool = False) -> dict:
    root = root.resolve()
    catalogue_path = root/'site/eleve/data/eleves/catalogue.json'
    courses = json.loads(catalogue_path.read_text(encoding='utf-8'))['courses']
    dest = root/'site/eleve/data/kristals-visuels.json'
    img_dest = root/'site/eleve/assets/kristals'
    drafts_path = root/'visuels/KRISTALS_SANS_SOURCE.json'
    drafts = json.loads(drafts_path.read_text(encoding='utf-8')) if drafts_path.is_file() else {}
    byid = {}
    warnings = []
    img_count = 0
    manifest_count = 0
    for c in courses:
        kid = c['id']
        if not ID.fullmatch(kid):
            raise ValueError('Identifiant invalide du catalogue : '+str(kid))
        workspace = root/'kristals'/kid
        manifest_path = workspace/'experience/RESSOURCES_VISUELLES.json'
        found = manifest_path.is_file() and not manifest_path.is_symlink()
        if found:
            raw = json.loads(manifest_path.read_text(encoding='utf-8'))
            if raw.get('format') != F or raw.get('kristal_id') != kid:
                raise ValueError('Manifeste visuel invalide : '+str(manifest_path))
            manifest_count += 1
            visual_list = raw.get('visuels', [])
            composants = raw.get('liens_bibliotheque', {}).get('composants_envisages', [])
            scenarios = raw.get('liens_bibliotheque', {}).get('scenarios_existants', [])
        else:
            draft = drafts.get('cours_sans_source', {}).get(kid)
            if not draft:
                warnings.append('Source et couche visuelle absentes : '+kid)
                continue
            visual_list = draft['visuels']
            composants = []
            scenarios = []
        pub_visuals = []
        for v in visual_list:
            slot = v.get('slot')
            if not isinstance(slot, str) or not SLOT.fullmatch(slot):
                raise ValueError('Slot invalide : '+repr(slot))
            prompt = v.get('prompt_conceptuel', '')
            if not isinstance(prompt, str) or len(prompt) < 60:
                raise ValueError('Prompt absent ou trop court : '+kid+'/'+slot)
            output_url = None
            actual_format = None
            image_revision = None
            if found:
                # Tous les formats acceptés, sans génération ni redimensionnement.
                for ext in EXTS:
                    src = workspace/'experience/images'/(slot+ext)
                    if not src.exists() and not src.is_symlink():
                        continue
                    if not safe_image(src, workspace):
                        warnings.append('Image ignorée (intégrité ou contrôle manquant) : '+str(src.relative_to(root)))
                        continue
                    target = img_dest/kid/(slot+ext)
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(src, target)
                    output_url = 'assets/kristals/'+kid+'/'+slot+ext
                    actual_format = ext[1:]
                    # Identifiant par contenu pour renouveler le cache après remplacement.
                    image_revision = hashlib.sha256(src.read_bytes()).hexdigest()[:16]
                    img_count += 1
                    break
            pub_visuals.append({
                'slot':slot, 'placement':v.get('placement','decouvrir'), 'role':v.get('role','illustration'),
                'concept':v.get('concept',''), 'prompt':prompt,
                'alt':v.get('texte_alternatif',''),
                'fichier_attendu':'kristals/'+kid+'/experience/images/'+slot+'.webp',
                'extensions_autorisees':list(EXTS),
                'url':output_url, 'format_reel':actual_format, 'revision':image_revision,
                'statut':'image_disponible' if output_url else 'prompt_visible',
                'source_niveau':'kristal' if found else 'catalogue_sans_source',
                'outils':v.get('outils_associes',[]),
                'ancrage_contenu':v.get('ancrage_contenu'),
            })
        byid[kid] = {
            'id':kid,
            'titre':c.get('title',''),
            'statut_source':'kristal_disponible' if found else 'source_absente_a_completer',
            'statut_pedagogique':'proposition_a_valider',
            'composants_envisages':composants,
            'scenarios_existants':scenarios,
            'visuels':pub_visuals,
        }
    data = {'format':PUB,'politique':'Prompts conceptuels visibles si image absente; aucune correction publiee; aucune evaluation automatique liee aux visuels.',
            'nb_references':len(courses),'nb_couches_kristal':manifest_count,'nb_cours_couverts':len(byid),
            'nb_images':img_count,'cours':byid, 'avertissements':warnings}
    if strict and (len(courses)!=202 or len(byid)!=202 or manifest_count!=200):
        raise ValueError('Couverture incomplète : '+str((len(courses),len(byid),manifest_count)))
    dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(f"Kristals visuels : {manifest_count} sources; {len(byid)}/{len(courses)} fiches; {img_count} images approuvables copiées; {len(warnings)} avertissements")
    for w in warnings[:10]: print('ATTENTION :',w,file=sys.stderr)
    return data


if __name__ == '__main__':
    ap=argparse.ArgumentParser(description='Compiler les intentions visuelles et les images déjà déposées dans les Kristals')
    ap.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1]);ap.add_argument('--strict',action='store_true')
    args=ap.parse_args();compile_layer(args.root,args.strict)
