#!/usr/bin/env python3
"""Inventaire non destructif des emplacements d'images Ekole (serveur Enseignant).

Les sources canoniques restent dans kristals/<cours>/experience; les données
publiques sont des projections et non des sources de vérité.
"""
from __future__ import annotations
import json
from pathlib import Path
from collections import Counter

EXTS=('.webp','.png','.jpg','.jpeg')

def inventory(root:Path)->dict:
    root=Path(root).resolve()
    catalog=json.loads((root/'site/eleve/data/eleves/catalogue.json').read_text(encoding='utf-8'))['courses']
    projection_path=root/'site/eleve/data/kristals-visuels.json'
    projected=json.loads(projection_path.read_text(encoding='utf-8')).get('cours',{}) if projection_path.is_file() else {}
    drafts_path=root/'visuels/KRISTALS_SANS_SOURCE.json'
    drafts=json.loads(drafts_path.read_text(encoding='utf-8')).get('cours_sans_source',{}) if drafts_path.is_file() else {}
    items=[];orphans=[]
    for course in catalog:
        kid=course['id']
        ws=root/'kristals'/kid
        manifest=ws/'experience/RESSOURCES_VISUELLES.json'
        has_source=manifest.is_file() and not manifest.is_symlink()
        if has_source:
            visual=json.loads(manifest.read_text(encoding='utf-8')).get('visuels',[])
        else:
            visual=drafts.get(kid,{}).get('visuels',[])
        projected_visuals={v['slot']:v for v in projected.get(kid,{}).get('visuels',[]) if isinstance(v,dict) and isinstance(v.get('slot'),str)}
        known=set()
        for v in visual:
            slot=v.get('slot')
            if not isinstance(slot,str):continue
            known.add(slot)
            current=projected_visuals.get(slot,{})
            image_dir=ws/'experience/images'
            found=[]
            if has_source and not image_dir.is_symlink():
                for ext in EXTS:
                    path=image_dir/(slot+ext)
                    if path.is_file() and not path.is_symlink() and path.resolve().is_relative_to(ws.resolve()):
                        found.append(path)
            url=current.get('url')
            if found and url:status='presente'
            elif found:status='a_synchroniser'
            elif has_source:status='manquante'
            else:status='source_absente'
            items.append({
                'key':kid+'/'+slot,'course_id':kid,'course_title':course.get('title',''),
                'year':course.get('year_suggestion'),'step':course.get('step_suggestion'),
                'subject':course.get('subject',''), 'slot':slot,'placement':v.get('placement',''),
                'concept':v.get('concept',''),'alt':v.get('texte_alternatif',''),
                'prompt':v.get('prompt_conceptuel',''), 'status':status,
                'editable':has_source,'files':[p.name for p in found],
                'public_url':url if isinstance(url,str) and url.startswith('assets/kristals/'+kid+'/') else None,
                'revision':current.get('revision') if isinstance(current.get('revision'),str) else None,
            })
        # Les fichiers non déclarés sont signalés, jamais supprimés ni modifiés.
        image_dir=ws/'experience/images'
        if has_source and image_dir.is_dir() and not image_dir.is_symlink():
            for f in image_dir.iterdir():
                if f.is_file() and not f.is_symlink() and f.suffix.lower() in EXTS and f.stem not in known:
                    orphans.append({'course_id':kid,'file':f.name})
    counts=Counter(item['status'] for item in items)
    return {'format':'ekole.teacher-image-album/1.0','course_count':len(catalog),'slot_count':len(items),
            'counts':dict(counts),'orphan_count':len(orphans),'orphans':orphans,'items':items}

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1]);a=p.parse_args()
    print(json.dumps(inventory(a.root),ensure_ascii=False,indent=2))
