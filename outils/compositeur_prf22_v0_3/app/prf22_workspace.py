"""Explicit, local Arketype Kit workspace creation for a PRF-22 design-only file.

Leaves `canon/` untouched; never publishes, activates, records students or mints
Framework v11 identities. Arketype owns the workspace topology and local Kit.
"""
from __future__ import annotations
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys

from prf22_core import sha, DesignError
from prf22_validator import validate_document

SLUG=re.compile(r'[a-z0-9]+(?:-[a-z0-9]+)*\Z')


def find_arketype(path: Path) -> Path:
    r=Path(path).expanduser().resolve()
    if (r/'arketype.py').is_file() and (r/'inventaires'/'profils-usage.json').is_file():return r
    if (r/'arketype'/'arketype.py').is_file():return r/'arketype'
    raise DesignError('Arketype introuvable : '+str(r))


def materialize(design: dict, arketype_root: Path, parent: Path, slug: str, dry_run: bool=True) -> dict:
    err,standard=validate_document(design)
    if err:raise DesignError('Kristal de conception non conforme : '+str(err[:4]))
    if not SLUG.fullmatch(slug or '') or len(slug)>80:raise DesignError('Slug requis : minuscules, chiffres et tirets, maximum 80 caractères')
    root=find_arketype(arketype_root)
    parent=Path(parent).expanduser().resolve(strict=True)
    if not parent.is_dir():raise DesignError('Le dossier parent doit exister')
    destination=parent/slug
    if destination.exists() or destination.is_symlink():raise DesignError('Workspace existe déjà : '+str(destination))
    prof=json.loads((root/'inventaires'/'profils-usage.json').read_text(encoding='utf-8'))
    if not any(p.get('id')=='PRF-22' and p.get('slug')=='situation-pedagogique-orchestrable' for p in prof.get('profiles',[])):
        raise DesignError('Profil PRF-22 absent : installer le profil Arketype avant de matérialiser')
    args=[sys.executable,str(root/'arketype.py'),'compose',
          '--profile','situation-pedagogique-orchestrable','--slug',slug,
          '--title',design['title'],'--parent',str(parent),'--authoring','legacy']
    if dry_run:args.append('--dry-run')
    result=subprocess.run(args,cwd=str(root),capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=180)
    if result.returncode:
        # Readable, bounded diagnostic, do not echo secrets or environment.
        raise DesignError('Arketype refuse le workspace : '+(result.stderr or result.stdout)[-1600:])
    if dry_run:
        return {'result':'preview','destination':str(destination),'will_write':False,
                'arketype_preview':json.loads(result.stdout)}
    try:
        meta=json.loads((destination/'arketype.instance.json').read_text(encoding='utf-8'))
        if (meta.get('published') is not False or meta.get('authorized_for_publication') is not False or
            meta.get('use_case_profile')!='situation-pedagogique-orchestrable'):
            raise DesignError('Workspace Arketype créé avec un état inattendu; vérifier manuellement '+str(destination))
        target=destination/'design'/'prf22-situation.design.json'
        with target.open('x',encoding='utf-8') as f:
            json.dump(design,f,ensure_ascii=False,indent=2);f.write('\n')
        receipt={'format':'ekole.prf22.arketype-binding/0.3','status':'design_only',
                 'profile':'PRF-22','design_id':design['id'], 'design_sha256':'sha256:'+sha(design),
                 'canonical_artifact_registered':False,'framework_v11_identity_minted':False,
                 'published':False,'activated':False,'session_authorized':False}
        with (destination/'design'/'prf22-local-binding.json').open('x',encoding='utf-8') as f:
            json.dump(receipt,f,ensure_ascii=False,indent=2);f.write('\n')
    except Exception:
        # Do not remove an Arketype-created directory if it may now contain user edits.
        # Leave it present with an error so the operator can inspect it safely.
        raise
    return {'result':'workspace_created','destination':str(destination),
            'canonical_registered':False,'publication_authorized':False}
