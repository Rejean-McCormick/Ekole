"""Candidate enrichment PRF22 v0.6 — 51 authorial patterns, no authorization.

Keeps original v0.4 bank immutable. Source cross-references identify Ékole
patterns separately from Kontexte exercises and preserve observed (un-pinned) hashes.
"""
from __future__ import annotations
import argparse, csv, hashlib, json, re, sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from composer_core import load_catalogue, compose_draft
from bank_mass import candidates, choose_activities, activity_objective, theory_entry, norm, slug, _j, _csv, _source_snapshots
from prf22_core import build_design, authoring_state, make_handoff, observe_catalogue_sources
from prf22_validator import validate_document

REPO = Path(__file__).resolve().parents[3]
LIBRARY = REPO/'banques/prf22/activites-proposees-v0_6.json'
FORMAT = 'ekole.prf22.banque-candidate/0.6'
SNAPSHOT_FORMAT = 'ekole.prf22.repo-snapshot/0.6'


def load_patterns(catalog, path=LIBRARY):
    path=Path(path).resolve()
    data=json.loads(path.read_text(encoding='utf-8'))
    if data.get('format')!='ekole.prf22.activites-proposees/0.6' or data.get('status')!='authoring_candidates_only':
        raise ValueError('Catalogue des patrons non reconnu')
    ids={x['ref'] for x in catalog.objectives}; refs=set()
    for e in data['entries']:
        if (e['ref'] in refs or e.get('owner')!='Ékole' or e['objectif_ref'] not in ids
            or e.get('statut')!='proposition_non_qualifiee' or not e['consigne'].strip()
            or e['source_type']!='patron_activite_propose'):
            raise ValueError('Patron invalide : '+str(e.get('ref')))
        refs.add(e['ref'])
    return data['entries']


def choose_patterns(template, focus, original, patterns, usage, count=2):
    text=norm(' '.join([template['titre'],template['probleme'],template.get('declencheur','')]))
    matches=[]
    for p in patterns:
        # Only domains explicitly signaled by Kontexte or inferred as a primary focus.
        if p['domaine']!=focus and p['domaine'] not in original:continue
        tags=[norm(x) for x in p['mots_contexte']]
        hits=sum(1 for x in tags if x in text)
        if not hits:continue
        # Discourage non-primary tags; prefer substantive contextual links, then diversify.
        ranked=(2 if p['domaine']==focus else 1)*10 + hits*4
        matches.append((ranked,p))
    # Avoid an unconnected filler activity; a bank proposal can have zero new patterns.
    matches.sort(key=lambda pair:(-pair[0], usage[pair[1]['ref']],pair[1]['ref']))
    selected=[]
    for _,p in matches:
        if p['objectif_ref'] in {x['objectif_ref'] for x in selected}:continue
        selected.append(p)
        usage[p['ref']]+=1
        if len(selected)>=count:break
    return selected


def src_hash(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def verify(output:Path, catalog_root:Path, library:Path=LIBRARY):
    output=Path(output).resolve(); catalog=load_catalogue(catalog_root)
    m=json.loads((output/'MANIFEST.json').read_text(encoding='utf-8'))
    if m.get('format')!=FORMAT or m.get('status')!='candidates_non_qualifies':
        raise ValueError('Format ou statut de banque incorrect')
    if m['source_hashes']!=_source_snapshots(catalog):
        raise ValueError('Sources Kontexte modifiées : reconstruire la banque')
    if m['library_sha256']!=src_hash(library):
        raise ValueError('Patrons Ékole modifiés : reconstruire la banque')
    snapshot=json.loads((output/'SNAPSHOT_SHA256.json').read_text(encoding='utf-8'))
    if snapshot.get('format')!=SNAPSHOT_FORMAT:raise ValueError('Manifeste SHA-256 invalide')
    existing={p.relative_to(output).as_posix() for p in output.rglob('*') if p.is_file() and p.name!='SNAPSHOT_SHA256.json'}
    if existing!=set(snapshot['files']):raise ValueError('Fichiers de banque manquants ou non indexés')
    for rel,expected in snapshot['files'].items():
        p=(output/rel).resolve()
        if not p.is_relative_to(output) or p.is_symlink() or src_hash(p)!=expected:
            raise ValueError('Empreinte erronée : '+rel)
    sources=set()
    if len(m['entries'])!=m['entries_count']:raise ValueError('Index incomplet')
    for e in m['entries']:
        folder=(output/e['folder']).resolve()
        if not folder.is_relative_to(output):raise ValueError('Dossier hors de la banque')
        sources.add(e['source_ref'])
        document=json.loads((folder/'design.json').read_text(encoding='utf-8'))
        errors,_=validate_document(document)
        if errors:raise ValueError(f"Contrat invalide {e['folder']}: {errors[:2]}")
        refs={a['exercise_ref']['resource_id']:a['exercise_ref']['owner'] for a in document['activities']}
        if any(refs.get(ref)!='Ékole' for ref in e['proposed_activity_refs']):
            raise ValueError('Patron présenté sous une fausse provenance')
        h=json.loads((folder/'handoff.json').read_text(encoding='utf-8'))
        if any(h.get(k) is not False for k in ('session_admitted','permissions_granted','orgo_world_created','konnaxion_project_created')):
            raise ValueError('Admission interdite')
        for n in (1,8,30):
            p=json.loads((folder/f'plan-{n:02}.json').read_text(encoding='utf-8'))
            if p['participation']['participant_count']!=n or p['export_hints']['runtime_admitted'] is not False:
                raise ValueError('Plan incompatible')
    if len(sources)!=m['source_situations_covered']:raise ValueError('Couverture source erronée')
    return {'propositions_verifiees':len(m['entries']),'sources':len(sources),'patrons_utilises':m['proposed_activities_used'],'objectifs_utilises':m['objectives_used'],'statut':'candidats seulement'}


def generate(catalog_root:Path, output:Path, *, library=LIBRARY, limit=0):
    catalog_root=Path(catalog_root).resolve();output=Path(output)
    if output.exists():raise FileExistsError('Sortie déjà existante : '+str(output))
    catalog=load_catalogue(catalog_root)
    library=Path(library).resolve()
    patterns=load_patterns(catalog,library)
    for p in patterns:
        catalog.activities.append({**p,'objective_candidate':p['objectif_ref']})
    # Source hashes exclude authored supplemental sources (tracked separately).
    baseline=load_catalogue(catalog_root)
    hashes=_source_snapshots(baseline)
    output.mkdir(parents=True)
    entries=[];usage=Counter(); used_goal=Counter(); used_act=Counter(); prio=[]
    for idx,(t,focus,ranked,score,original) in enumerate(candidates(catalog)):
        if limit and idx>=limit:break
        selected=choose_activities(baseline,t,focus,ranked,score)
        proposals=choose_patterns(t,focus,original,patterns,usage,count=2)
        acts=selected+proposals
        if not acts:continue
        refs=[a['ref'] for a in acts]
        mappings={a['ref']: (a['objectif_ref'] if a in proposals else activity_objective(a)) for a in acts}
        objectives=list(dict.fromkeys(mappings.values()))
        if any(v not in {o['ref'] for o in catalog.objectives} for v in objectives):
            raise ValueError('Objectif inconnu dans la sélection')
        draft=compose_draft(catalog,t['ref'],refs,8,4,
            epoch='Période à préciser selon la situation (simulation)',
            cultural_frame='Cadre fictif candidat; revue culturelle et historique requise',
            setting='Lieu de la situation source; à documenter', reality='fictif',
            objectives=objectives,notes='Enrichissement v0.6 : liens générés, provenance distincte Kontexte / Ékole.',parallel_posts=3)
        byref={a['ref']:a for a in acts}
        cards={}
        for goal in objectives:
            group=[byref[r] for r in refs if mappings[r]==goal]
            primary=group[0]; card=theory_entry(t,primary,catalog.objective(goal))
            card['activity_refs']=[a['ref'] for a in group]
            if primary in proposals:
                card['expected_action']=primary['consigne']+' Expliquer comment cette action sert le problème posé.'
                card['observation']='Observer les étapes explicitement demandées : '+primary['consigne']
                card['evidence']='Trace candidate : '+primary['preuve_attendue']+' Une production ne prouve pas à elle seule la maîtrise.'
                card['criterion']='Critères candidats à examiner avec l’enseignant : '+primary['critere_candidat']
                card['boundary']='Patron conçu par Ékole (non source Kontexte), à adapter : âge, matériel, accessibilité, droits, contexte culturel.'
                card['conjecture_statement']=f"L'activité candidate « {primary['titre']} » pourrait aider à travailler « {catalog.objective(goal)['titre']} » dans « {t['titre']} »; lien non démontré."
            cards[goal]=card
        design=build_design(draft,cards)
        errors,full=validate_document(design)
        if errors:raise ValueError(f'PRF-22 invalide {t["ref"]} {focus}: {errors[:2]}')
        observed=observe_catalogue_sources(catalog_root,draft)
        handoff=make_handoff(design,draft,observed)
        slugname=slug(t['ref']+'-'+focus);folder='situations/'+slugname
        dest=output/folder;dest.mkdir(parents=True)
        _j(dest/'design.json',design)
        author=authoring_state(draft,cards)
        author['source_observations']=observed
        _j(dest/'brouillon.json',author)
        _j(dest/'handoff.json',handoff)
        for n in (1,8,30):
            plan=compose_draft(catalog,t['ref'],refs,n,4,
                epoch=draft['world_context']['epoch'],cultural_frame=draft['world_context']['cultural_frame'],
                setting=draft['world_context']['place'],reality='fictif',objectives=objectives,parallel_posts=3 if n==30 else 1)
            _j(dest/f'plan-{n:02}.json',plan)
        quality='REVUE_PRIORITAIRE' if not proposals or t['source_type']=='mission' or focus not in original else 'REVUE_OBLIGATOIRE'
        e={'id':design['id'],'titre':t['titre'],'source_ref':t['ref'],'source_type':t['source_type'],
           'focale':focus,'folder':folder,'activity_refs':refs,'objective_refs':objectives,
           'proposed_activity_refs':[p['ref'] for p in proposals],
           'quality':quality,'justification_provenance':('Activités Kontexte + patrons Ékole proposés. ' if proposals else 'Aucun nouveau patron pertinent. ')+
               'Correspondances heuristiques, vérification humaine obligatoire.',
           'files_sha256':{name:src_hash(dest/name) for name in ('design.json','brouillon.json','handoff.json','plan-01.json','plan-08.json','plan-30.json')}}
        entries.append(e)
        prio.append({'source':t['ref'],'focale':focus,'statut':quality,'patrons':', '.join(p['ref'] for p in proposals)})
        used_act.update(refs);used_goal.update(objectives)
    manifest={'format':FORMAT,'status':'candidates_non_qualifies','created_utc':datetime.now(timezone.utc).isoformat(),
       'source_root_hint':str(catalog_root),'source_hashes':hashes,'library_sha256':src_hash(library),
       'source_count':len(catalog.templates),'entries_count':len(entries),
       'source_situations_covered':len({e['source_ref'] for e in entries}),
       'original_activities_available':len(baseline.activities),'proposed_activities_available':len(patterns),
       'proposed_activities_used':len(usage),'activities_used':len(used_act),'objectives_used':len(used_goal),
       'scope':'conception non qualifiée; aucune séance ni droit', 'entries':entries}
    _j(output/'MANIFEST.json',manifest)
    _csv(output/'BANQUE_SITUATIONS.csv',['titre','source_ref','focale','quality','folder','activity_refs','objective_refs'],entries)
    _csv(output/'REVUE_PRIORITAIRE.csv',['source','focale','statut','patrons'],prio)
    _csv(output/'CATALOGUE_ACTIVITES_PROPOSEES.csv',['ref','titre','domaine','objectif_ref','consigne','preuve_attendue','critere_candidat'],patterns)
    (output/'RAPPORT.md').write_text(f'''# Banque Ékole PRF-22 v0.6 — propositions non qualifiées\n\n- {len(entries)} compositions pour {manifest['source_situations_covered']} sources Kontexte.\n- Catalogue Kontexte inchangé : {len(baseline.activities)} activités; {len(baseline.objectives)} objectifs.\n- Bibliothèque complémentaire Ékole : {len(patterns)} patrons proposés, **distincts des exercices Kontexte**.\n- Couverture de cette génération : {len(used_act)} activités distinctes, {len(used_goal)} objectifs distincts.\n- Patrons Ékole effectivement employés : {len(usage)} / {len(patterns)}.\n- {sum(e['quality']=='REVUE_PRIORITAIRE' for e in entries)} propositions en revue prioritaire.\n- Chaque cas a des variantes pour 1, 8 et 30 participants, sans données personnelles.\n\nLes patrons sont des propositions rédactionnelles non essayées avec des enfants, pas des ressources homologuées. Les rapprochements sont heuristiques et restent révisables. Le nombre de cas n'est pas une mesure de qualité. Une variante solo n'évalue pas la collaboration entre pairs. La présence de postes parallèles ne prouve pas leur faisabilité matérielle.\n\nAucune activation Orgo, création de World, admission Konnaxion ou publication élève.\n''',encoding='utf-8')
    files={p.relative_to(output).as_posix():src_hash(p) for p in output.rglob('*') if p.is_file()}
    _j(output/'SNAPSHOT_SHA256.json',{'format':SNAPSHOT_FORMAT,'files':files})
    return {'propositions':len(entries),'sources':manifest['source_situations_covered'],
            'patrons_disponibles':len(patterns),'patrons_utilises':len(usage),'activites_distinctes':len(used_act),
            'objectifs_distincts':len(used_goal),'revue_prioritaire':sum(e['quality']=='REVUE_PRIORITAIRE' for e in entries)}


def main(argv=None):
    p=argparse.ArgumentParser()
    p.add_argument('--kontexte',type=Path,default=Path(r'C:\mycode\Ekole\Kontexte'))
    p.add_argument('--vers',required=True,type=Path)
    p.add_argument('--patrons',type=Path,default=LIBRARY)
    p.add_argument('--limite',type=int,default=0)
    p.add_argument('--verifier',action='store_true')
    a=p.parse_args(argv)
    try: result=verify(a.vers,a.kontexte,a.patrons) if a.verifier else generate(a.kontexte,a.vers,library=a.patrons,limit=a.limite)
    except (OSError,ValueError,KeyError,TypeError) as exc:
        print('[ÉCHEC]',exc,file=sys.stderr);return 2
    print(json.dumps(result,ensure_ascii=False,indent=2));return 0

if __name__=='__main__':sys.exit(main())
