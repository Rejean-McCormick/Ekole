"""Banque PRF-22 v0.7 : sélection traçable et fiches pédagogiques non qualifiées.

Aucune IA, service réseau, inscription, publication ni activation. Les patrons Ékole
restent des propositions; les exercices et les objectifs Kontexte restent externes.
La présence de données contextuelles ne crée pas de preuves pédagogiques.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
from functools import lru_cache
import json
from pathlib import Path
import re
import sys

from composer_core import load_catalogue, compose_draft
from bank_mass import (candidates, MICRO_TO_OBJECTIVE, DOMAIN_MICROS, norm, slug,
                       activity_objective, theory_entry, _j, _csv, _source_snapshots)
from bank_enrich import src_hash
from prf22_core import build_design, authoring_state, make_handoff, observe_catalogue_sources
from prf22_validator import validate_document

ROOT=Path(__file__).resolve().parents[3]
LIBRARY_V07=ROOT/'banques/prf22/activites-proposees-v0_7.json'
FORMAT='ekole.prf22.banque-candidate/0.7'
SNAPSHOT_FORMAT='ekole.prf22.repo-snapshot/0.7'
WEAK={'village','classe','atelier','fete','projet','creation','collectif','mission','objet','choix','partage','temps','lieu','equipe','eau','son'}
MICRO_HINTS={
 1:['personnage','scene','spectacle','representation','jeu de role'],
 2:['anglais','langue','consigne','bilingue'],3:['anglais','langue','dialogue','bilingue'],4:['anglais','message','langue','traduction'],
 5:['oeuvre','creation','photo','affiche','exposition','artistique','costume'],
 11:['regle','conseil','decider','debat'],
 12:['danse','mouvement','spectacle'],13:['scene','spectacle','theatre','improviser'],14:['scene','spectacle','public'],
 15:['parcours','velo','randonnee','course','relais'],16:['equipe','course','relais','parcours'],17:['securite','velo','risque','parcours'],
 18:['consigne','notice','mode emploi','instruction','guide'],19:['indice','mystere','inference','enquete','secret'],
 20:['ecrire','rediger','invitation','affiche','journal','message','annonce','guide'],21:['texte','reviser','correction','lettre','ecriture'],
 22:['calcul','prix','cout','budget','caisse','achat','quantite'],23:['recette','portion','fraction','partager'],
 24:['nombre','quantite','stock','commande','comparer','budget','mesure','calcul'],
 25:['geometrie','figure','forme','maquette','plan','pont'],26:['suite','regularite','motif','sequence'],
 27:['musique','son','rythme','chant','spectacle'],28:['musique','ecouter','son','ambiance','spectacle'],
 29:['observation','experience','laboratoire','hypothese','tester','essai','plante','structure','eau'],
 31:['temps','histoire','evolution','chronologie','passe'],33:['carte','lieu','territoire','plan','itineraire'],34:['enquete','document','comparaison','source','historique']
}


def load_patterns_v07(catalog,path=LIBRARY_V07):
    data=json.loads(Path(path).read_text(encoding='utf-8'))
    if data.get('format')!='ekole.prf22.activites-proposees/0.7' or data.get('status')!='authoring_candidates_only':
        raise ValueError('Bibliothèque v0.7 non reconnue')
    ids={o['ref'] for o in catalog.objectives};refs=set()
    for p in data['entries']:
        if p['ref'] in refs or p['owner']!='Ékole' or p['objectif_ref'] not in ids or p['statut']!='proposition_non_qualifiee':
            raise ValueError('Patron non conforme')
        refs.add(p['ref'])
    return data['entries']


def matches(tag,text):
    """Correspondance token/préfixe, pas 'son' dans 'personne'."""
    tag=norm(tag).strip()
    if not tag:return False
    if ' ' in tag:return tag in text
    # Court mot : singulier/pluriel, sans capture de morceaux de mots (son != personne).
    if len(tag)<=3:
        return bool(re.search(r'(?<!\w)'+re.escape(tag)+r's?(?!\w)',text))
    return bool(re.search(r'(?<!\w)'+re.escape(tag)+r'\w*(?!\w)',text))


def details_source(source_root, template):
    if template['source_type']=='trame':
        d=json.loads((source_root/'data/trames/catalogue-neutral-v0.2.json').read_text(encoding='utf-8'))
        raw=next(x for x in d['scenarios'] if x['id']==template['source_id'])
        return {'declencheur':raw.get('declencheur',''), 'probleme':raw.get('tension',''),
                'informations':raw.get('informations_a_reunir',[]), 'actions':raw.get('actions',[]),
                'production':raw.get('resultat',''), 'rebond':raw.get('rebond_possible',''),
                'axes':raw.get('axes_de_variation',[]),
                'source_document':template['source_relpath'], 'niveaux_suggeres':raw.get('niveaux_suggeres','')}
    raw=json.loads((source_root/template['source_relpath']).read_text(encoding='utf-8'))
    steps=raw.get('steps',[])
    return {'declencheur':template.get('declencheur',''), 'probleme':template['probleme'],
            'informations':['Fragments de la mission : diffusion conditionnelle par Orgo, non affichés ici'], 'actions':[],
            'production':'Étapes prévues par la mission : '+', '.join(str(x.get('id','')) for x in steps if isinstance(x,dict))[:160],
            'rebond':'', 'axes':[], 'source_document':template['source_relpath'],
            'niveaux_suggeres':'à déterminer', 'etapes_source': [s.get('id','') for s in steps if isinstance(s,dict)],
            'etapes_consignes': [s.get('instruction',{}).get('fr-CA','') for s in steps if isinstance(s,dict)]}


def source_text(template,ctx):
    # Titles, concrete problem, source actions and intended production, not broad axes.
    return norm(' '.join([template['titre'],ctx['probleme'],ctx['declencheur'],
                          ctx['production'], ' '.join(ctx.get('actions',[])),
                          ' '.join(ctx.get('informations',[])), ' '.join(ctx.get('etapes_consignes',[])), ' '.join(template.get('roles',[]))]))


def score_pattern(pattern,text,focus):
    if pattern['domaine']!=focus:return None
    hits=[t for t in pattern['mots_contexte'] if matches(t,text)]
    strong=[h for h in hits if norm(h) not in WEAK]
    weak=[h for h in hits if h not in strong]
    if not hits:return None
    # weak generic tags are never sufficient for a supposed strong alignment.
    return {'confidence':'ancrage_direct' if strong else 'ancrage_generique_a_revoir',
            'hits':strong+weak,'strong_hits':strong,
            'score':min(len(strong),3)*8+min(len(weak),3)*1,
            'reason':('Indices issus du titre, des productions, rôles ou étapes sources : '+', '.join(strong)) if strong else
                     ('Correspondance générique seulement ('+', '.join(weak)+') : vérifier la pertinence')}


@lru_cache(maxsize=8)
def micro_catalog(source_root):
    raw=json.loads((source_root/'data/locales/qc/fr-CA/grade3/micro-situations-34.json').read_text(encoding='utf-8'))
    return {x['id']:x for x in raw['modules']}


def score_micro(activity,template,focus,text,source_root):
    ref=activity['ref']; n=int(ref.rsplit('-',1)[1]);
    if n not in DOMAIN_MICROS.get(focus,[]) or n not in MICRO_TO_OBJECTIVE:return None
    mod=micro_catalog(source_root)[ref.split(':',1)[1]]
    hits=[x for x in MICRO_HINTS.get(n,[]) if matches(x,text)]
    exact=template['source_type']=='trame' and mod.get('parent_trame_culturellement_neutre')==template['source_id']
    if not hits and not exact:return None
    return {'confidence':'ancrage_direct' if hits or exact else 'ancrage_generique_a_revoir',
            'hits':hits,'strong_hits':hits,'score':(12 if exact else 0)+min(len(hits),3)*6,
            'reason':('Micro-situation explicitement reliée à cette trame Kontexte. ' if exact else '')+
                      ('Indices thématiques : '+', '.join(hits) if hits else 'Revue de l’ancrage nécessaire')}


def choose(template,ctx,focus,patterns,catalog,source_root):
    """Focale unique; pas de remplissage interdisciplinaire automatique."""
    text=source_text(template,ctx)
    found=[]
    for p in patterns:
        detail=score_pattern(p,text,focus)
        if detail is not None:found.append((p,detail,'Ékole'))
    for a in catalog.activities:
        if not a['ref'].startswith('micro:'):continue
        detail=score_micro(a,template,focus,text,source_root)
        if detail is not None:found.append((a,detail,'Kontexte'))
    # avoid preferring a weaker micro because its field uses generic tags; also spread goals.
    found.sort(key=lambda x:(-x[1]['score'], x[2]!='Ékole',x[0]['ref']))
    selected=[];goals=set()
    for a,d,owner in found:
        obj=a['objectif_ref'] if owner=='Ékole' else activity_objective(a)
        if not obj or obj in goals:continue
        # require a genuine contextual anchor for every chosen activity.
        if not d['strong_hits'] and d['score']<3:continue
        selected.append((a,d,owner,obj));goals.add(obj)
        if len(selected)>=3:break
    # Rescue a sparse situation with one transparent weakly supported candidate,
    # rather than inventing an unconnected task or a different discipline.
    if not selected and found:
        a,d,owner=found[0];obj=a['objectif_ref'] if owner=='Ékole' else activity_objective(a)
        if obj:selected.append((a,d,owner,obj))
    # True gap: fall back to one same-discipline micro, clearly marked as ungrounded,
    # so an editorially reviewable situation exists for all 77 sources.
    if not selected:
        for number in DOMAIN_MICROS[focus]:
            if number not in MICRO_TO_OBJECTIVE:continue
            a=next((x for x in catalog.activities if x['ref']==f'micro:enseignement-explicite-{number:03}'),None)
            if a:
                selected.append((a,{'confidence':'lacune_a_completer','hits':[], 'strong_hits':[], 'score':0,
                                    'reason':'Aucune activité précisément ancrée : association de discipline seulement, à remplacer ou justifier'},
                                'Kontexte',activity_objective(a)));break
    if not selected:raise ValueError('Aucune activité dans la discipline '+focus)
    return selected


def editorial_card(template,ctx,a,detail,owner,obj,goal):
    """Transform the original Kontexte/Ékole activity without inventing facts or criteria officiality."""
    b=theory_entry(template,a,goal)
    title=a['titre'].strip().rstrip('.')
    consigne=a.get('consigne','').strip().rstrip('.') or title
    proof=a.get('preuve_attendue','').strip().rstrip('.') or goal['preuve_attendue'].strip().rstrip('.')
    production=ctx['production']
    inputs=', '.join(ctx['informations'][:3]) if ctx['informations'] else 'documents ou données à préparer par l’enseignant'
    crit=a.get('critere_candidat','').strip().rstrip('.')
    if not crit:
        crit=f"Trace attendue clairement identifiable ({proof}); lien observable avec « {goal['objectif'].strip().rstrip('.')} »; explication individuelle vérifiable"
    b.update({
      'conjecture_statement':f"Si l’enfant réalise « {title} » pour contribuer à « {production} » dans « {template['titre']} », il pourrait exercer « {goal['titre']} ». L’effet et la difficulté restent à examiner.",
      'expected_action':f"Pour résoudre « {ctx['probleme']} », proposer la tâche suivante : {consigne}. Mettre à disposition : {inputs}. Livrable de la situation : {production}. Les données et le matériel précis sont à fournir avant usage.",
      'process':f"Repérer dans la réalisation les opérations demandées par « {title} » : {consigne}. Vérifier qu’elles se rapportent effectivement à « {goal['objectif'].strip().rstrip('.')} ».",
      'observation':f"Pendant « {title} », noter les démarches de l'enfant et recueillir la production. Demander une explication courte de la décision ou du résultat, sans la suggérer.",
      'evidence':f"Trace attendue selon la ressource {owner} : {proof}. La conserver uniquement dans un dispositif autorisé, sans données d’enfant dans ce brouillon.",
      'criterion':f"Critères proposés, à préciser et à faire valider : {crit}. La simple réalisation de l'activité ne suffit pas à conclure à la maîtrise.",
      'disconfirmation':f"L'enfant réalise la production sans pouvoir montrer l'opération visée par « {goal['titre']} », ou n'arrive pas à justifier une étape malgré des soutiens adaptés.",
      'alternative':f"Le résultat peut refléter les prérequis, l'aide reçue, un exemple copié ou une coopération non observable séparément, plutôt que cette activité seule.",
      'boundary':f"Ancrage : {detail['reason']}. Vérifier pertinence, niveau, accessibilité, durée, matériel et cohérence avec le résultat « {production} ». Adapter si le contexte change.",
      'interpretation_limit':f"La trace prévue dans « {template['titre']} » ne démontre ni transfert hors situation, ni efficacité causale, ni compétence de collaboration entre pairs pour un participant seul."
    })
    if owner=='Ékole':b['duration_minutes']=a['duree_minutes']
    return b


def fiche(template,ctx,focus,selected,catalog):
    activities=[]
    for a,d,owner,obj in selected:
        activities.append({'activite_ref':a['ref'],'proprietaire':owner,'objectif_ref':obj,
            'titre':a['titre'],'place_dans_la_situation':'centrale_candidate',
            'confiance':d['confidence'],'mots_sources_observes':d['hits'],
            'motif_de_choix':d['reason'],
            'consigne_source':a.get('consigne','').strip(),
            'consigne_contextualisee':f"Dans « {template['titre']} », accomplir « {a['titre']} » pour contribuer à « {ctx['production']} ». {a.get('consigne','').strip()}".strip(),
            'preuve':a.get('preuve_attendue',''),
            'critere_propose':a.get('critere_candidat') or f"Vérifier la trace attendue pour « {catalog.objective(obj)['titre']} » et demander une justification observable.",
            'materiel_a_confirmer':True,'verification_humaine_requise':True})
    weakness=[x for x in activities if x['confiance']!='ancrage_direct']
    return {'format':'ekole.prf22.fiche-pedagogique/0.7','status':'candidat_non_qualifie',
       'source_ref':template['ref'],'focale':focus,'question_motrice':ctx['probleme'],
       'declencheur_source':ctx['declencheur'],'informations_a_preparer':ctx['informations'],
       'actions_source':ctx['actions'],'production_attendue_source':ctx['production'],
       'rebond_source':ctx['rebond'],'niveaux_suggeres_source':ctx['niveaux_suggeres'],
       'activites':activities,'lacunes':([
           'Préciser des données, supports et matériel concrets avant de faire réaliser les activités',
           'Vérifier l’adéquation au groupe, la sécurité et les ressources disponibles',
           'Faire confirmer les critères par un enseignant avant usage réel']+
           (['Au moins une activité n’a qu’un ancrage générique ou manque d’ancrage; la remplacer ou la justifier.'] if weakness else [])),
       'adaptations':{
         '1':{'modalite':'individuel','conservation':'objectif disciplinaire seulement',
              'limite':'Aucune compétence de collaboration entre pairs ne peut être évaluée en solo'},
         '8':{'modalite':'équipes candidates','controle':'Répartition des rôles, dépendances et contribution de chaque enfant à vérifier'},
         '30':{'modalite':'stations candidates','controle':'Nombre de postes, matériel, bruit, temps et encadrement réels à confirmer'}},
       'decision':'Aucune qualification pédagogique, publication, séance, compte ou admission permise'}


def verify(output:Path,catalog_root:Path,library:Path=LIBRARY_V07):
    output=Path(output).resolve();catalog_root=Path(catalog_root).resolve()
    baseline=load_catalogue(catalog_root)
    manifest=json.loads((output/'MANIFEST.json').read_text(encoding='utf-8'))
    if manifest.get('format')!=FORMAT or manifest.get('status')!='candidates_non_qualifies':raise ValueError('Format incorrect')
    if manifest['source_hashes']!=_source_snapshots(baseline):raise ValueError('Sources Kontexte modifiées')
    if manifest['library_sha256']!=src_hash(library):raise ValueError('Patrons Ékole modifiés')
    snapshot=json.loads((output/'SNAPSHOT_SHA256.json').read_text(encoding='utf-8'))
    if snapshot.get('format')!=SNAPSHOT_FORMAT:raise ValueError('Manifeste de contrôle invalide')
    existing={p.relative_to(output).as_posix() for p in output.rglob('*') if p.is_file() and p.name!='SNAPSHOT_SHA256.json'}
    if existing!=set(snapshot['files']):raise ValueError('Fichiers manquants ou non recensés')
    for rel,expected in snapshot['files'].items():
        p=(output/rel).resolve()
        if not p.is_relative_to(output) or p.is_symlink() or src_hash(p)!=expected:
            raise ValueError('Empreinte invalide : '+rel)
    if len(manifest['entries'])!=manifest['entries_count']:raise ValueError('Nombre d’entrées invalide')
    sources=set(); activity_ids={x['ref'] for x in baseline.activities}|{x['ref'] for x in load_patterns_v07(baseline,library)}
    objective_ids={x['ref'] for x in baseline.objectives}
    for rec in manifest['entries']:
        src=rec['source_ref'];sources.add(src)
        folder=(output/rec['folder']).resolve()
        if not folder.is_relative_to(output) or folder.is_symlink():raise ValueError('Chemin dangereux')
        design=json.loads((folder/'design.json').read_text(encoding='utf-8'))
        author=json.loads((folder/'brouillon.json').read_text(encoding='utf-8'))
        sheet=json.loads((folder/'FICHE_PEDAGOGIQUE.json').read_text(encoding='utf-8'))
        errors,_=validate_document(design)
        if errors:raise ValueError(f'Contrat PRF-22 invalide {src}: {errors[:2]}')
        if sheet['status']!='candidat_non_qualifie' or sheet['source_ref']!=src:raise ValueError('Fiche déliée')
        refs=[a['activite_ref'] for a in sheet['activites']]
        if refs!=rec['activity_refs'] or refs!=[a['exercise_ref']['resource_id'] for a in design['activities']]:raise ValueError('Alignement activités/fiche invalide')
        if any(x not in activity_ids for x in refs) or any(x not in objective_ids for x in rec['objective_refs']):raise ValueError('Référence inconnue')
        if set(author['theory_entries'])!=set(rec['objective_refs']):raise ValueError('Carte d’alignement incomplète')
        if not all(len(author['theory_entries'][o]['criterion'])>50 for o in rec['objective_refs']):raise ValueError('Critère insuffisant')
        if any(design['governance'].get(k) is not False for k in ('activation_authorized','publication_authorized','student_data_included')):
            raise ValueError('Droit interdit')
        handoff=json.loads((folder/'handoff.json').read_text(encoding='utf-8'))
        if any(handoff.get(k) is not False for k in ('session_admitted','permissions_granted','orgo_world_created','konnaxion_project_created')):
            raise ValueError('Handoff non sûr')
        for n in (1,8,30):
            plan=json.loads((folder/f'plan-{n:02}.json').read_text(encoding='utf-8'))
            if plan['participation']['participant_count']!=n or plan['export_hints']['runtime_admitted'] is not False:raise ValueError('Plan invalide')
    if len(sources)!=manifest['source_situations_covered']:raise ValueError('Couverture de source erronée')
    return {'propositions_verifiees':len(manifest['entries']),'sources':len(sources),
            'activites_distinctes':manifest['activities_used'],'objectifs_distincts':manifest['objectives_used'],
            'associations_generiques':manifest['weak_links'],'statut':'révision pédagogique obligatoire'}


def generate(catalog_root:Path,output:Path,*,library:Path=LIBRARY_V07,limit:int=0):
    catalog_root=Path(catalog_root).resolve();output=Path(output);library=Path(library).resolve()
    if output.exists():raise FileExistsError('Dossier déjà présent : '+str(output))
    baseline=load_catalogue(catalog_root);patterns=load_patterns_v07(baseline,library)
    lookup={o['ref']:o for o in baseline.objectives}
    c=load_catalogue(catalog_root)
    for p in patterns:c.activities.append({**p,'objective_candidate':p['objectif_ref']})
    entries=[];activ=Counter();objcount=Counter();weak_total=0
    output.mkdir(parents=True)
    for idx,(t,focus,ranked,score,original) in enumerate(candidates(baseline)):
        if limit and idx>=limit:break
        ctx=details_source(catalog_root,t)
        selected=choose(t,ctx,focus,patterns,baseline,catalog_root)
        if not selected:continue
        refs=[x[0]['ref'] for x in selected]
        goals=list(dict.fromkeys(x[3] for x in selected))
        # Exact source metadata remain in the sidecar; the authored draft stays schema-compatible.
        draft=compose_draft(c,t['ref'],refs,8,4,objectives=goals,
             epoch='Période de simulation à préciser selon la trame',
             cultural_frame='Aucune culture réelle attribuée; sources et droits à valider',
             setting='Lieu de la situation source, à préciser par l’enseignant',reality='fictif',
             notes='V0.7 : focalisation disciplinaire et choix d’activités explicitement justifiés; aucune validation pédagogique.',
             parallel_posts=3)
        cards={}
        for a,d,owner,goal in selected:
            if goal in cards:cards[goal]['activity_refs'].append(a['ref']);continue
            cards[goal]=editorial_card(t,ctx,a,d,owner,goal,lookup[goal])
        design=build_design(draft,cards)
        errors,_=validate_document(design)
        if errors:raise ValueError(f'{t["ref"]}: schéma invalide {errors[:3]}')
        observed=observe_catalogue_sources(catalog_root,draft)
        handoff=make_handoff(design,draft,observed)
        side=fiche(t,ctx,focus,selected,baseline)
        folder='situations/'+slug(t['ref']+'-'+focus)
        dest=output/folder;dest.mkdir(parents=True)
        _j(dest/'design.json',design)
        author=authoring_state(draft,cards);author['source_observations']=observed
        _j(dest/'brouillon.json',author)
        _j(dest/'handoff.json',handoff)
        _j(dest/'FICHE_PEDAGOGIQUE.json',side)
        for n in (1,8,30):
            plan=compose_draft(c,t['ref'],refs,n,4,objectives=goals,
                epoch=draft['world_context']['epoch'],cultural_frame=draft['world_context']['cultural_frame'],
                setting=draft['world_context']['place'],reality='fictif',parallel_posts=3 if n==30 else 1)
            _j(dest/f'plan-{n:02}.json',plan)
        weak=sum(x[1]['confidence']!='ancrage_direct' for x in selected);weak_total+=weak
        quality='REVUE_PRIORITAIRE' if weak or t['source_type']=='mission' else 'REVUE_OBLIGATOIRE'
        rec={'id':design['id'],'titre':t['titre'],'source_ref':t['ref'],'source_type':t['source_type'],
           'focale':focus,'folder':folder,'activity_refs':refs,'objective_refs':goals,
           'proposed_activity_refs':[a['ref'] for a,d,owner,g in selected if owner=='Ékole'],
           'quality':quality,'justification_provenance':f"Sélection centrée sur {focus}; {len(selected)} activité(s), dont {weak} correspondance(s) faible(s). Sources Kontexte et propositions Ékole non qualifiées.",
           'weak_links':weak,'direct_links':len(selected)-weak,
           'files_sha256':{p.name:src_hash(p) for p in dest.iterdir() if p.is_file()}}
        entries.append(rec);activ.update(refs);objcount.update(goals)
    manifest={'format':FORMAT,'status':'candidates_non_qualifies',
       'created_utc':datetime.now(timezone.utc).isoformat(timespec='seconds'),
       'source_root_hint':'Kontexte — racine configurable, sources contrôlées par empreintes','source_hashes':_source_snapshots(baseline),
       'library_sha256':src_hash(library),'source_count':len(baseline.templates),
       'entries_count':len(entries),'source_situations_covered':len({e['source_ref'] for e in entries}),
       'original_activities_available':len(baseline.activities),'proposed_activities_available':len(patterns),
       'proposed_activities_used':len({r for e in entries for r in e['proposed_activity_refs']}),
       'activities_used':len(activ),'objectives_used':len(objcount),'weak_links':weak_total,
       'scope':'hypothèses de conception; non qualifiées; aucun droit ou séance', 'entries':entries}
    _j(output/'MANIFEST.json',manifest)
    _csv(output/'BANQUE_SITUATIONS.csv',['titre','source_ref','focale','quality','weak_links','folder','activity_refs','objective_refs'],entries)
    _csv(output/'REVUE_PRIORITAIRE.csv',['source_ref','focale','quality','weak_links','justification_provenance'],entries)
    _csv(output/'CATALOGUE_ACTIVITES_PROPOSEES.csv',['ref','titre','domaine','objectif_ref','consigne','preuve_attendue','critere_candidat'],patterns)
    (output/'RAPPORT.md').write_text(f'''# Banque PRF-22 v0.7 — cohérence et traçabilité\n\n- **{len(entries)} propositions** pour **{manifest['source_situations_covered']} situations sources** de Kontexte.\n- {len(activ)} activités et {len(objcount)} objectifs distincts effectivement reliés.\n- **{weak_total} lien(s) signalé(s) faible(s) par les règles automatiques**, sur {sum(len(e['activity_refs']) for e in entries)} associations retenues. Ce décompte n’est pas une certification de pertinence.\n- Focale disciplinaire isolée : aucune activité de français ou mathématiques ajoutée automatiquement à une situation d’arts.\n- 1 fiche éditoriale par situation : question, informations, résultat, justification de chaque activité, preuves, critères et lacunes.\n- Trois plans candidats 1 / 8 / 30 enfants par situation.\n- La banque v0.4 et la v0.6 doivent être conservées sans changement, ainsi que les révisions locales.\n\n**Attention** : toutes les associations restent candidates. Les contrôles automatiques peuvent manquer des associations faibles ou des lacunes de contenu, même quand le compteur vaut zéro. Une revue pédagogique et, si nécessaire, de nouveaux exercices spécifiques restent indispensables. Aucune publication ou admission n’est permise.\n''',encoding='utf-8')
    _j(output/'SNAPSHOT_SHA256.json',{'format':SNAPSHOT_FORMAT,
        'files':{p.relative_to(output).as_posix():src_hash(p) for p in output.rglob('*') if p.is_file()}})
    return {'propositions':len(entries),'sources':manifest['source_situations_covered'],
            'activites_distinctes':len(activ),'objectifs_distincts':len(objcount),
            'liens_generiques':weak_total,'liens_total':sum(len(e['activity_refs']) for e in entries)}


def main(argv=None):
    p=argparse.ArgumentParser(description='Ékole PRF-22 v0.7 — génération sans publication')
    p.add_argument('--kontexte',type=Path,default=Path(r'C:\mycode\Ekole\Kontexte'))
    p.add_argument('--vers',required=True,type=Path)
    p.add_argument('--patrons',type=Path,default=LIBRARY_V07)
    p.add_argument('--limite',type=int,default=0)
    p.add_argument('--verifier',action='store_true')
    a=p.parse_args(argv)
    try:r=verify(a.vers,a.kontexte,a.patrons) if a.verifier else generate(a.kontexte,a.vers,library=a.patrons,limit=a.limite)
    except (OSError,ValueError,KeyError,TypeError) as exc:
        print('[ÉCHEC]',exc,file=sys.stderr);return 2
    print(json.dumps(r,ensure_ascii=False,indent=2));return 0
if __name__=='__main__':raise SystemExit(main())
