"""Générateur massif local PRF-22: composition candidate, jamais qualification ni admission.

Sources propriétaires: Kontexte. Ne modifie aucun dépôt, ne publie pas et n'utilise
aucune donnée d'enfant. Les liaisons activité-objectif sont une présélection
heuristique traçable; une revue pédagogique reste obligatoire.
"""
from __future__ import annotations
import argparse
import csv
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import sys
import unicodedata

from composer_core import load_catalogue, compose_draft, validate_draft
from prf22_core import build_design, authoring_state, make_handoff, observe_catalogue_sources
from prf22_validator import validate_document

FORMAT='ekole.prf22.banque-candidate/0.4'
# Ce tableau est une proposition documentée de correspondance vers les références
# réelles de Kontexte. Il ne prétend pas être une classification pédagogique officielle.
MICRO_TO_OBJECTIVE={
 1:'qc-pri-ad-002',2:'qc-pri-als-001',3:'qc-pri-als-005',4:'qc-pri-als-007',
 5:'qc-pri-ap-008',11:'qc-pri-ccq-009',12:'qc-pri-da-003',13:'qc-pri-da-006',
 14:'qc-pri-da-001',15:'qc-pri-eps-004',16:'qc-pri-eps-003',17:'qc-pri-eps-010',
 18:'qc-pri-fr-016',19:'qc-pri-fr-006',20:'qc-pri-fr-012',21:'qc-pri-fr-018',
 22:'qc-pri-ma-033',23:'qc-pri-ma-012',24:'qc-pri-ma-002',25:'qc-pri-ma-003',
 26:'qc-pri-ma-004',27:'qc-pri-mu-006',28:'qc-pri-mu-007',29:'qc-pri-st-004',
 31:'qc-pri-us-015',33:'qc-pri-us-004',34:'qc-pri-us-005'
}
# Ces activités exigent une validation humaine contextualisée; on évite leur
# inclusion automatique dans des aventures génériques.
EXCLUDED_MICROS={6:'contexte de vie et développement',7:'genre et stéréotypes',
                 8:'territoire québécois à documenter',9:'prévention des agressions sexuelles',
                 10:'spiritualité et cultures',30:'sociétés algonquiennes vers 1500',
                 32:'sociétés iroquoiennes vers 1500'}
DOMAIN_MICROS={
 'mathematiques':[24,22,25,23,26],
 'francais':[19,20,18,21],
 'sciences':[29],
 'arts':[1,5,12,13,14,27,28],
 'ccq':[11],
 'univers_social':[31,33,34],
 'anglais':[2,3,4],
 'education_physique':[15,16,17],
}
# Adapter le choix de domaines aux mots du problème, sans fabriquer d'objectif.
WORDS_DOMAIN={
 'mathematiques':('calcul','budget','quantit','nombre','commande','caisse','stock','prix','cout','mesur','horaire','temps','porte','itineraire','distance','partag','eau'),
 'francais':('texte','lire','lectur','message','conte','journal','notice','invitation','affiche','mot','histoire','bibliothe','bulletin','rédact','ecrit','discours'),
 'sciences':('plante','jardin','eau','mecan','metal','meteo','semis','laboratoire','temperature','lumiere','ombre','soleil','structure','pont','foret','lac','habitat','compost','sol','animal'),
 'arts':('spectacle','chapeau','scene','musique','danse','costume','creation','photo','conte','lumiere','son','couleur','affiche','origami'),
 'ccq':('partag','village','conseil','vote','entraide','respect','equitable','solidaire','choix','debat','regle','ressource'),
 'univers_social':('carte','territoire','voyage','expedition','societe','histor','temps','passe','itineraire','transport','lieu'),
 'anglais':('multilingue','tradu','anglais','bilingue','langue'),
 'education_physique':('mouvement','velo','parcours','relais','randonnee','deplacement','course','coordination'),
}
ROLE_DOMAIN={'boulanger':'mathematiques','comptable':'mathematiques','fermier':'sciences',
 'mecanicien':'sciences','scientifique':'sciences','inventeur':'sciences',
 'lecteur':'francais','redacteur':'francais','ecrivain':'francais','traducteur':'anglais',
 'musicien':'arts','danseur':'arts','peintre':'arts','clown':'arts','metteur-en-scene':'arts',
 'politicien':'ccq','explorateur':'univers_social','astronaute':'sciences',
 'photographe':'arts','veterinaire':'sciences','messager':'francais'}


def norm(text):
    return ''.join(c for c in unicodedata.normalize('NFKD',str(text).casefold()) if not unicodedata.combining(c))


def themes(text):
    t=norm(text)
    return {d for d,words in WORDS_DOMAIN.items() if any(w in t for w in words)}


def domain_scores(template):
    source=f"{template['titre']} {template['probleme']} {template.get('declencheur','')}"
    t=norm(source)
    original=list(dict.fromkeys(template.get('domaines_potentiels',[])))
    score={d:0 for d in DOMAIN_MICROS}
    for d in original:
        if d in score: score[d]+=10
    for d,words in WORDS_DOMAIN.items():score[d]+=sum(4 for w in words if w in t)
    for role in template.get('roles',[]):
        domain=ROLE_DOMAIN.get(role)
        if domain:score[domain]+=1
    return sorted(score,key=lambda k:(-score[k],k)),score,original


def activity_objective(a):
    if a['ref'].startswith('micro:'):
        num=int(a['ref'].split('-')[-1])
        return MICRO_TO_OBJECTIVE.get(num)
    t=norm(a.get('titre',''))
    if 'ml' in t or 'cm' in t or 'metre' in t or 'm ' in t: return 'qc-pri-ma-025'
    if 'minute' in t: return 'qc-pri-ma-026'
    if 'partage' in t and ('egalement' in t or 'group' in t):return 'qc-pri-ma-009'
    if 'reste' in t or 'manque' in t: return 'qc-pri-ma-007'
    if any(w in t for w in ['chacune','chacun','lots de','rangees','numeros de']):return 'qc-pri-ma-008'
    if any(w in t for w in ['total','somme','puis']):return 'qc-pri-ma-006'
    return 'qc-pri-ma-033'


def det_score(template,activity):
    a=norm(activity.get('titre','')); t=norm(template['titre']+' '+template['probleme'])
    twords={x for x in re.findall(r'\w+',t) if len(x)>3}
    awords={x for x in re.findall(r'\w+',a) if len(x)>3}
    overlap=len(twords&awords)
    # Certains champs répètent un problème générique, on priorise les motifs précis.
    special=[('boulanger',('pains','boulanger','plateaux')),
             ('spectacle',('spectacle','chaises','minutes')),
             ('jardin',('plante','plant','pots','eau')),
             ('eau',('pots','eau','ml')),
             ('invitation',('invitations','feuilles')),
             ('marche',('klownkoins','articles','cout')),
             ('velo',('distance','parcourt')),
             ('chapeau',('chapeaux','etoiles')),
             ('stock',('articles','feuilles'))]
    for marker,words in special:
        if marker in t and any(w in a for w in words):overlap+=3
    return overlap


def choose_activities(catalog,template,focus,ranked,score):
    micro={int(a['ref'].split('-')[-1]):a for a in catalog.activities if a['ref'].startswith('micro:')}
    det=[a for a in catalog.activities if a['ref'].startswith('det:')]
    selected=[]
    t=norm(template['titre']+' '+template['probleme'])
    preferred=list(DOMAIN_MICROS[focus])
    if focus=='arts':
        if any(w in t for w in ('spectacle','scene','theatre','comedie','clown','personnage')):
            preferred=[1,13,12,14,5,27,28]
        elif any(w in t for w in ('musique','son','chant','concert')):
            preferred=[27,28,5]
        elif any(w in t for w in ('danse','mouvement')):
            preferred=[12,13,14]
        else:
            # Banque actuelle: pas de micro-exercice de production d'arts plastiques.
            # Ne jamais lui substituer abusivement une activité de théâtre.
            preferred=[5]
    elif focus=='mathematiques':
        if any(w in t for w in ('fraction','portion','recette')):preferred=[23,22,24]
        elif any(w in t for w in ('budget','caisse','cout','taxe','commande','prix','stock')):preferred=[22,25,24]
        elif any(w in t for w in ('suite','regul','sequence')):preferred=[26,22,24]
        else:preferred=[24,22,25,23,26]
    elif focus=='univers_social':
        preferred=[33,34,31] if any(w in t for w in ('carte','territoire','lieu','habitat')) else [31,34,33]
    elif focus=='francais':
        preferred=[20,21,19,18] if any(w in t for w in ('redig','ecrit','affiche','invitation','bulletin')) else [19,20,18,21]
    for number in preferred:
        if number in MICRO_TO_OBJECTIVE:
            selected.append(micro[number])
        if len(selected)>=2:break
    if focus=='mathematiques' and det:
        match=sorted(det,key=lambda a:(-det_score(template,a),a['ref']))
        # Un exercice déterministe hors sujet ne doit pas être inséré simplement
        # pour obtenir artificiellement une troisième activité.
        if det_score(template,match[0])>=2:
            selected=selected[:1]+[match[0]]+selected[1:2]
    # Complément(s) à partir des domaines de la situation; alignement révisable.
    others=[d for d in ranked if d!=focus and score[d]>0 and d!='ccq']
    for d in others:
        order=list(DOMAIN_MICROS[d])
        if d=='arts' and not any(w in t for w in ('spectacle','scene','clown','personnage','danse','musique','son')):
            order=[5]
        for number in order:
            if number in MICRO_TO_OBJECTIVE and micro[number]['ref'] not in {x['ref'] for x in selected}:
                selected.append(micro[number]);break
        if len(selected)>=3:break
    # Pas de remplissage arbitraire: 2 activités suffisent si la banque n'a pas
    # de ressource pertinente dans les domaines de la trame.
    return selected[:3]


def theory_entry(template,activity,objective):
    # On reste au conditionnel. L'activité réelle est citée, pas réécrite.
    title=activity['titre'].strip().rstrip('.')
    objective_text=objective['objectif'].strip().rstrip('.')
    consigne=activity.get('consigne','').strip()
    proof=activity.get('preuve_attendue','').strip()
    evidence=f"Trace candidate de l’activité « {title} » : {proof or objective['preuve_attendue']}. À confirmer selon la réalisation de l’enfant."
    domain='mathematiques' if objective['ref'].startswith('qc-pri-ma-') else None
    learning='practice'
    if objective['ref'].startswith('qc-pri-fr-') or objective['ref'].startswith('qc-pri-als-') or objective['ref'].startswith('qc-pri-us-'):learning='inquiry'
    if objective['ref'].startswith('qc-pri-ap-') or objective['ref'].startswith('qc-pri-da-') or objective['ref'].startswith('qc-pri-mu-'):learning='production'
    if objective['ref'].startswith('qc-pri-ccq-'):learning='discussion'
    if objective['ref'].startswith('qc-pri-st-'):learning='inquiry'
    return {
       'theory_ids':['sandoval-2014','biggs-align','laurillard'],
       'learning_type':learning,'assessment_requires':'individual_possible',
       'fourcid_component':'learning_task' if learning in ('inquiry','production') else 'part_task_practice',
       'duration_minutes':20 if activity['source_type']=='micro_situation' else 10,
       'activity_refs':[activity['ref']],
       'conjecture_statement':f"Dans « {template['titre']} », proposer « {title} » pourrait contribuer à l'objectif « {objective['titre']} »; cette hypothèse reste à vérifier en contexte.",
       'expected_action':f"Réaliser l'activité proposée : {consigne or title}. Expliquer les choix avec un soutien adapté.",
       'process':f"L'enfant mobilise les actions nécessaires pour : {objective_text}. Le lien entre l'activité et cet objectif est une proposition à vérifier.",
       'observation':f"Observer les étapes suivies dans « {title} » et demander à l'enfant d'expliquer ou de représenter sa démarche.",
       'evidence':evidence,
       'criterion':f"Comparer la trace à l'objectif « {objective['titre']} » et aux critères de la source; jugement final réservé à l'enseignant.",
       'disconfirmation':f"L'enfant ne peut expliquer ou démontrer le processus attendu après un accompagnement adapté; l'hypothèse est à revoir.",
       'alternative':f"La trace peut résulter d'une aide adulte, d'un modèle copié ou de prérequis déjà acquis, plutôt que de l'activité seule.",
       'boundary':f"Adapter la difficulté et le support; vérifier prérequis, matériel, culture, accessibilité et pertinence de « {title} ».",
       'interpretation_limit':f"Une production dans « {template['titre']} » ne démontre pas à elle seule une maîtrise individuelle transférable ni un effet causal.",
    }


def slug(s):
    x=norm(s).replace('’','-').replace("'",'-')
    x=re.sub('[^a-z0-9]+','-',x).strip('-')
    return x[:78] or 'sans-titre'


def _j(path, content):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(content,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')


def _csv(path,headers,rows):
    with path.open('w',newline='',encoding='utf-8-sig') as f:
        wr=csv.DictWriter(f,fieldnames=headers,extrasaction='ignore',delimiter=';')
        wr.writeheader();wr.writerows(rows)


def candidates(catalog):
    for template in catalog.templates:
        ranked,score,original=domain_scores(template)
        # Deux focales par trame; une par mission (les domaines des missions
        # sont inférés de titres et rôles, pas qualifiés par Kontexte).
        count=2 if template['source_type']=='trame' else 1
        focus_domains=[]
        for d in ranked:
            if score[d]>0 and d not in focus_domains and d!='ccq':focus_domains.append(d)
            if len(focus_domains)>=count:break
        if len(focus_domains)<count:
            for d in ('francais','mathematiques'):
                if d not in focus_domains:focus_domains.append(d)
                if len(focus_domains)>=count:break
        for focus in focus_domains:
            yield template, focus, ranked, score,original


def _source_snapshots(catalog):
    names=set([t['source_relpath'] for t in catalog.templates]+[a['source_relpath'] for a in catalog.activities]+[o['source_relpath'] for o in catalog.objectives])
    return {name:hashlib.sha256((catalog.root/name).read_bytes()).hexdigest() for name in sorted(names)}


def generate(catalog_root:Path, output:Path, *, limit=0, verify_only=False):
    catalog=load_catalogue(catalog_root)
    source_hashes=_source_snapshots(catalog)
    if verify_only:
        manifest=json.loads((output/'MANIFEST.json').read_text(encoding='utf-8'))
        if manifest['source_hashes']!=source_hashes:
            raise ValueError('Les sources Kontexte ont évolué : reconstruire la banque; ne pas réutiliser des liens obsolètes.')
        checked=0
        for rec in manifest['entries']:
            folder=output/rec['folder']
            for name in ('design.json','brouillon.json','handoff.json'):
                p=folder/name
                if hashlib.sha256(p.read_bytes()).hexdigest()!=rec['files_sha256'][name]:
                    raise ValueError('Fichier manquant ou modifié : '+str(p))
            design=json.loads((folder/'design.json').read_text(encoding='utf-8'))
            errors,_=validate_document(design)
            if errors:raise ValueError('Schéma invalide : '+str(folder)+': '+str(errors[:3]))
            checked+=1
        return {'verified':checked,'sources':len(source_hashes)}
    if output.exists():
        raise FileExistsError('Le dossier de sortie existe déjà : '+str(output)+'; choisir un dossier neuf (aucun écrasement).')
    output.mkdir(parents=True)
    entries=[];issues=[]; objective_counts=Counter(); act_counts=Counter()
    for idx,(t,focus,ranked,score,original) in enumerate(candidates(catalog)):
        if limit and idx>=limit:break
        activities=choose_activities(catalog,t,focus,ranked,score)
        activity_refs=[a['ref'] for a in activities]
        mapped=[]
        for a in activities:
            target=activity_objective(a)
            if target not in {o['ref'] for o in catalog.objectives}:
                raise ValueError('Aucun objectif référencé pour '+a['ref']+': '+str(target))
            mapped.append(target)
        objectives=list(dict.fromkeys(mapped))
        if len(objectives)<1:
            raise ValueError('Aucun objectif vérifiable : '+t['ref'])
        participation=8
        draft=compose_draft(catalog,t['ref'],activity_refs,participation,4,
                            epoch='Période à préciser selon la situation (simulation)',
                            cultural_frame='Cadre fictionnel non attribué à une culture réelle; validation enseignante',
                            setting='Lieu de la situation source; à préciser pour la classe',
                            reality='fictif',language='fr-CA',objectives=objectives,
                            notes=f'Focale proposée : {focus}. Sources Kontexte réelles; choix automatique non qualifié.',
                            parallel_posts=3)
        # Pour un même objectif, préserver toutes les activités qui le sollicitent.
        cards={ref:theory_entry(t, next(a for a in activities if activity_objective(a)==ref),catalog.objective(ref)) for ref in objectives}
        for a in activities:
            target=activity_objective(a)
            if a['ref'] not in cards[target]['activity_refs']:
                cards[target]['activity_refs'].append(a['ref'])
        design=build_design(draft,cards)
        errors,full=validate_document(design)
        if errors:raise ValueError(f"{t['ref']} {focus}: {errors[:3]}")
        handoff=make_handoff(design,draft,observe_catalogue_sources(catalog.root,draft))
        name=slug(t['ref']+'-'+focus)
        folder=Path('situations')/name
        base=output/folder
        base.mkdir(parents=True)
        _j(base/'design.json',design)
        _j(base/'brouillon.json',authoring_state(draft,cards,'',catalog.root))
        _j(base/'handoff.json',handoff)
        for n in (1,8,30):
            plan=compose_draft(catalog,t['ref'],activity_refs,n,4,
                               epoch=draft['world_context']['epoch'],
                               cultural_frame=draft['world_context']['cultural_frame'],
                               setting=draft['world_context']['place'],reality='fictif',
                               objectives=objectives,parallel_posts=3 if n==30 else 1)
            _j(base/f'plan-{n:02d}.json',plan)
        low_confidence=(t['source_type']=='mission' or focus not in original or
                        (focus in ('arts','sciences','ccq') and len([a for a in activities if a['ref'].startswith('micro:') and int(a['ref'].split('-')[-1]) in DOMAIN_MICROS[focus]]) < 2))
        explanation='Domaine proposé par les mots et rôles; non explicite dans la mission.' if t['source_type']=='mission' else ('Domaine non déclaré dans cette trame.' if focus not in original else 'Domaine déclaré comme potentiel dans Kontexte; lien activité-objectif généré et à vérifier (exercice disciplinaire parfois absent).' )
        rec={'id':design['id'],'titre':t['titre'],'source_ref':t['ref'],'source_type':t['source_type'],
             'focale':focus,'folder':folder.as_posix(),'activity_refs':activity_refs,'objective_refs':objectives,
             'quality':'REVUE_PRIORITAIRE' if low_confidence else 'REVUE_OBLIGATOIRE',
             'justification_provenance':explanation,'full_json_schema':full,
             'files_sha256':{name:hashlib.sha256((base/name).read_bytes()).hexdigest() for name in ('design.json','brouillon.json','handoff.json')}}
        entries.append(rec)
        issues.append({'source':t['ref'],'focale':focus,'statut':rec['quality'],
                       'remarque':explanation})
        for ref in objectives:objective_counts[ref]+=1
        for ref in activity_refs:act_counts[ref]+=1
    manifest={'format':FORMAT,'generated_utc':datetime.now(timezone.utc).isoformat(timespec='seconds'),
              'status':'candidates_non_qualifies','source_root_hint':str(catalog_root),
              'source_hashes':source_hashes,'source_count':len(catalog.templates),
              'activity_catalogue_count':len(catalog.activities),
              'objective_catalogue_count':len(catalog.objectives),'entries_count':len(entries),
              'source_situations_covered':len({x['source_ref'] for x in entries}),
              'used_activities':len(act_counts),'used_objectives':len(objective_counts),
              'scope':'CONCEPTION_UNIQUEMENT; aucune séance, admission, compte ou qualification',
              'entries':entries}
    _j(output/'MANIFEST.json',manifest)
    _csv(output/'BANQUE_SITUATIONS.csv', ['titre','source_ref','focale','quality','folder','activites','objectifs'],
         [dict(x,activites=', '.join(x['activity_refs']),objectifs=', '.join(x['objective_refs'])) for x in entries])
    _csv(output/'CATALOGUE_ACTIVITES.csv',['ref','titre','type','domaine','preuve','objectif_candidat'],[
        {'ref':a['ref'],'titre':a['titre'],'type':a['source_type'],'domaine':a.get('domaine',''),
         'preuve':a.get('preuve_attendue',''),'objectif_candidat':activity_objective(a) if activity_objective(a) else 'NON_COUPLE'} for a in catalog.activities])
    _csv(output/'CATALOGUE_OBJECTIFS.csv',['ref','titre','discipline','objectif','preuve'],[
        {'ref':o['ref'],'titre':o['titre'],'discipline':o['discipline'],'objectif':o['objectif'],'preuve':o['preuve_attendue']} for o in catalog.objectives])
    _csv(output/'REVUE_PRIORITAIRE.csv',['source','focale','statut','remarque'],issues)
    audit=f'''# Rapport de génération — Banque PRF-22 v0.4

**{len(entries)} propositions** pour **{manifest['source_situations_covered']} situations sources** de Kontexte.

- Répertoire indépendant : {len(catalog.activities)} activités et {len(catalog.objectives)} objectifs candidats ; aucun contenu original modifié.
- Liens utilisés : {len(act_counts)} activités distinctes, {len(objective_counts)} objectifs distincts. Cela ne couvre pas tous les référentiels.
- {sum(x['quality']=='REVUE_PRIORITAIRE' for x in entries)} liens signalés pour revue prioritaire.
- Chaque proposition : document PRF-22 v0.3, brouillon éditable, handoff non autorisé, plans pour 1/8/30.
- Tests du schéma exécutés sur chaque document; les choix sémantiques sont **heuristiques**.
- Les sources historiques et culturelles restent **non vérifiées**. Les sources originales ne sont pas des contenus pédagogiques certifiés.
- Aucun accès, élève, World, projet Konnaxion, séance ou droit Orgo créé.
- Les postes parallèles à 30 élèves ne sont que des hypothèses matérielles à confirmer.
- La variante solo n'évalue pas la collaboration réelle entre pairs. Toutes les cartes générées sont formulées pour une pratique individuelle possible et ne prétendent pas évaluer cette compétence.

## Vérifications obligatoires avant usage

1. Inspecter les correspondances activité/objectif et le niveau scolaire, surtout les liens de soutien interdisciplinaires.
2. Examiner la qualité du contexte, la véracité des faits, la représentation culturelle, les ressources et l'accessibilité.
3. Spécifier les consignes concrètes, critères, durée, rôles et preuves possibles dans une séance réelle.
4. Réviser les conjectures théoriques : elles sont produites au conditionnel et ne constituent pas une efficacité démontrée.
5. Confirmer les postes, les groupes, les permissions et le jugement de l'enseignant avant toute activité réelle.

Les micro-situations {', '.join(str(x) for x in sorted(EXCLUDED_MICROS))} sont exclues de l'appariement automatique (sensibilité documentaire, culturelle ou sécurité); elles restent consultables dans le répertoire intégral.
'''
    (output/'RAPPORT.md').write_text(audit,encoding='utf-8')
    return {'created':len(entries),'sources':manifest['source_situations_covered'],
            'used_activities':len(act_counts),'used_objectives':len(objective_counts),
            'priority':sum(x['quality']=='REVUE_PRIORITAIRE' for x in entries)}


def main(argv=None):
    p=argparse.ArgumentParser(description='Banque PRF-22 v0.4 — génération hors ligne sans droits')
    p.add_argument('--kontexte',type=Path,default=Path(r'C:\mycode\Ekole\Kontexte'))
    p.add_argument('--vers',type=Path,required=True)
    p.add_argument('--limite',type=int,default=0,help='Pour essais: nombre de propositions')
    p.add_argument('--verifier',action='store_true',help='Vérifier une banque existante et les sources, sans écrire')
    args=p.parse_args(argv)
    try:
        result=generate(args.kontexte,args.vers,limit=args.limite,verify_only=args.verifier)
    except (ValueError,OSError,KeyError,TypeError) as exc:
        print('ERREUR:',exc,file=sys.stderr)
        return 2
    print(json.dumps(result,ensure_ascii=False,indent=2))
    return 0

if __name__=='__main__':sys.exit(main())
