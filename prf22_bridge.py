"""Ékole local teacher-only PRF-22 bank bridge, no student routes or runtime grants.

Designed for the existing dual-port launcher; the caller MUST enforce teacher
cookie/CSRF/same-origin/edition. This module adds a second defense on input size,
file identity and reference immutability. All writes are *new* local revisions.
"""
from __future__ import annotations
import hashlib, json, os, pathlib, re, sys, uuid
from datetime import datetime, timezone

ENGINE=pathlib.Path(__file__).resolve().parent
APP=ENGINE/'outils/compositeur_prf22_v0_3/app'
BANKS=ENGINE/'banques/prf22'
BASE_NAME='candidats-v0_7'
EDITABLE=('conjecture_statement','expected_action','process','observation','evidence','criterion',
          'disconfirmation','alternative','boundary','interpretation_limit')
SAFE_SLUG=re.compile(r'[a-z0-9][a-z0-9-]{0,115}\Z')


def _load(path:pathlib.Path):
    if path.is_symlink() or not path.is_file() or path.stat().st_size>3_000_000:
        raise ValueError('Fichier absent, lien ou trop volumineux')
    return json.loads(path.read_text(encoding='utf-8'))


def _bank():
    for name in (BASE_NAME,'candidats-v0_6','candidats-v0_4'):
        root=(BANKS/name).resolve()
        if (root/'MANIFEST.json').is_file():
            m=_load(root/'MANIFEST.json')
            if m.get('format') not in ('ekole.prf22.banque-candidate/0.7','ekole.prf22.banque-candidate/0.6','ekole.prf22.banque-candidate/0.4'):
                raise ValueError('Format de banque incorrect')
            if len(m.get('entries',[]))!=m.get('entries_count'):
                raise ValueError('Index de banque incomplet')
            return root,m
    raise FileNotFoundError('Banque PRF-22 absente')


def _entries(root,m):
    result={}
    for rec in m['entries']:
        path=pathlib.PurePosixPath(rec['folder'])
        if path.is_absolute() or '..' in path.parts or len(path.parts)!=2 or path.parts[0]!='situations':
            raise ValueError('Chemin de candidat non sûr')
        slug=path.name
        if not SAFE_SLUG.fullmatch(slug) or slug in result:
            raise ValueError('Identifiant de candidat invalide ou dupliqué')
        if not (root/rec['folder']).resolve().is_relative_to(root):
            raise ValueError('Chemin hors de la banque')
        result[slug]=rec
    return result


def index():
    root,m=_bank();e=_entries(root,m)
    return {'format':m['format'],'version':root.name,'entries_count':m['entries_count'],
            'sources':m['source_situations_covered'],'activities_used':m.get('activities_used',m.get('used_activities')),
            'objectives_used':m.get('objectives_used',m.get('used_objectives')),
            'proposed_activities_available':m.get('proposed_activities_available',0),
            'weak_links':m.get('weak_links'),
            'entries':[{'slug':slug,'titre':r['titre'],'source_ref':r['source_ref'],'focale':r['focale'],
                        'quality':r['quality'],'activity_refs':r['activity_refs'],
                        'objective_refs':r['objective_refs'],'proposed_activity_refs':r.get('proposed_activity_refs',[]),
                        'weak_links':r.get('weak_links'), 'direct_links':r.get('direct_links')}
                       for slug,r in e.items()],
            'status':'candidats, revue pédagogique obligatoire'}


def _record(slug):
    if not isinstance(slug,str) or not SAFE_SLUG.fullmatch(slug):raise ValueError('Identifiant invalide')
    root,m=_bank(); rec=_entries(root,m).get(slug)
    if rec is None:raise FileNotFoundError('Candidat inconnu')
    path=(root/rec['folder']).resolve()
    return root,rec,path


def _verified(path,rec,name):
    f=path/name
    if f.is_symlink() or not f.is_file():raise ValueError('Fichier de banque absent ou dangereux')
    raw=f.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=rec['files_sha256'][name]:
        raise ValueError('Empreinte incompatible : '+name)
    return json.loads(raw)


def detail(slug):
    root,rec,path=_record(slug)
    author=_verified(path,rec,'brouillon.json');design=_verified(path,rec,'design.json')
    if design.get('status')!='design_only' or author.get('status')!='design_only':
        raise ValueError('Candidat non éditable')
    # Attach immutable source identity. Revisions are deliberately isolated from the bank.
    sheet = _verified(path,rec,'FICHE_PEDAGOGIQUE.json') if 'FICHE_PEDAGOGIQUE.json' in rec['files_sha256'] else None
    if sheet is not None and (sheet.get('source_ref')!=rec['source_ref'] or sheet.get('status')!='candidat_non_qualifie'):
        raise ValueError('Fiche pédagogique non conforme')
    return {'slug':slug,'meta':{k:rec[k] for k in ('titre','focale','quality','source_ref','justification_provenance')},
            'design':design,'authoring':author,'fiche_pedagogique':sheet,
            'source_sha256':rec['files_sha256']['brouillon.json'],
            'bank':root.name,'revisions':revision_list(slug)}


def revision_list(slug):
    if not SAFE_SLUG.fullmatch(slug):raise ValueError('Slug invalide')
    folder=BANKS/'revisions-local'/slug
    if not folder.is_dir():return []
    return sorted([p.name for p in folder.iterdir() if p.is_dir() and re.fullmatch(r'rev-[0-9TZ-]{8,40}-[a-f0-9]{8}',p.name)],reverse=True)[:40]


def catalogue():
    root,m=_bank()
    library=_load(BANKS/('activites-proposees-v0_7.json' if root.name=='candidats-v0_7' else 'activites-proposees-v0_6.json'))
    return {'format':library['format'],'proposals':library['entries'],
            'notice':'Patrons Ékole candidats, distincts des exercices appartenant à Kontexte; aucune qualification.'}


def revise(payload):
    """Save only pedagogical draft text; never edit owner/reference IDs nor grant authorization."""
    if not isinstance(payload,dict) or set(payload)!={'slug','source_sha256','theory_entries','note'}:
        raise ValueError('Requête de révision non reconnue')
    slug=payload['slug'];root,rec,path=_record(slug)
    if rec['files_sha256']['brouillon.json']!=payload['source_sha256']:
        raise ValueError('La banque a changé; recharger le brouillon')
    author=_verified(path,rec,'brouillon.json')
    existing=author['theory_entries'];incoming=payload['theory_entries']
    if not isinstance(incoming,dict) or set(incoming)!=set(existing):
        raise ValueError('Les identifiants pédagogiques ne peuvent pas être modifiés ici')
    note=payload['note']
    if not isinstance(note,str) or len(note)>4000:
        raise ValueError('Note de revue trop longue')
    from copy import deepcopy
    edited=deepcopy(existing)
    for goal,proposed in incoming.items():
        if not isinstance(proposed,dict) or set(proposed)!=set(EDITABLE):
            raise ValueError('Seuls les champs pédagogiques peuvent être révisés')
        for key in EDITABLE:
            text=proposed[key]
            if not isinstance(text,str) or not 12<=len(text.strip())<=4000:
                raise ValueError('Texte pédagogique trop court ou trop long : '+key)
            edited[goal][key]=text.strip()
    sys.path.insert(0,str(APP)) if str(APP) not in sys.path else None
    from prf22_core import build_design
    from prf22_validator import validate_document
    draft=author['draft'];design=build_design(draft,edited,author.get('dependency_lines',''))
    errors,_=validate_document(design)
    if errors:raise ValueError('Conception non conforme : '+ '; '.join(errors[:3]))
    if (design.get('status')!='design_only' or design['governance']['activation_authorized']
        or design['governance']['publication_authorized'] or design['governance']['student_data_included']):
        raise ValueError('Une révision ne peut donner aucune autorité')
    edited_author={**author,'theory_entries':edited}
    # Never write into the versioned candidate bank, teacher public directory, or Kontexte.
    parent=(BANKS/'revisions-local'/slug)
    if parent.is_symlink() or (BANKS/'revisions-local').is_symlink():
        raise ValueError('Chemin de révision symbolique interdit')
    parent.mkdir(parents=True,exist_ok=True)
    unique='rev-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'-'+uuid.uuid4().hex[:8]
    target=parent/unique
    target.mkdir(exist_ok=False)
    def write(name,obj):
        dest=target/name
        with dest.open('x',encoding='utf-8',newline='\n') as stream:
            json.dump(obj,stream,ensure_ascii=False,indent=2);stream.write('\n')
    try:
        write('brouillon.json',edited_author)
        write('design.json',design)
        write('REVUE.json',{'format':'ekole.prf22.revue-locale/0.6','status':'pending_teacher_review',
            'note':note,'source_slug':slug,'bank':root.name,'source_sha256':payload['source_sha256'],
            'design_status':'design_only','rights_granted':False})
    except Exception:
        import shutil;shutil.rmtree(target);raise
    return {'saved':True,'revision':unique,'status':'brouillon_local_non_approuve','directory':str(target)}


def read_revision(slug,revision):
    if not SAFE_SLUG.fullmatch(slug) or not isinstance(revision,str) or revision not in revision_list(slug):
        raise FileNotFoundError('Révision inconnue')
    root=BANKS/'revisions-local'/slug/revision
    if root.is_symlink() or not root.resolve().is_relative_to(BANKS.resolve()):
        raise ValueError('Chemin de révision dangereux')
    author=_load(root/'brouillon.json');design=_load(root/'design.json');review=_load(root/'REVUE.json')
    if author.get('status')!='design_only' or design.get('status')!='design_only':
        raise ValueError('Révision non admissible')
    return {'revision':revision,'authoring':author,'design':design,'review':review}
