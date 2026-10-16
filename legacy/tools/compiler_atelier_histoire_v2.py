#!/usr/bin/env python3
"""Compilation v2 : corpus sourcé -> vues Élève hors ligne, sans IA, sans inférence négative."""
from pathlib import Path
import argparse, json, hashlib
HOME=Path(__file__).resolve().parents[1]
MOD='modules/qc-pri-us-009'
def load(p):return json.loads(p.read_text(encoding='utf-8'))
def compile_v2(root=HOME,installed=False):
    mod=root/MOD; ins=root/'kristals/qc-pri-us-009'
    base=ins if installed and (ins/'canon/domain/societes-rencontres-v2.json').exists() else mod
    g=load(base/'canon/domain/societes-rencontres-v2.json')
    cat=load(base/'sources/source-catalog.v2.json')
    proofs=load(base/'sources/TRACABILITE_ASSERTIONS_v2.json')
    visual=load(base/'experience/histoire-rencontres/RESSOURCES_VISUELLES_V2.json')
    ids=lambda key:{i['id']:i for i in g[key]}
    facts=ids('assertions');periods=ids('periodes');soc=ids('societes');roles=ids('roles');tasks=ids('taches');ress=ids('ressources')
    refs={s['id']:s for s in cat['sources']};rel=g['relations_situees_v2'];nrm=g['regles_attestees']
    required={'source_ids','fact_ids','role_ref','tache_ref','ressource_ref','societe_ref','periode_ref'}
    assert len(facts)==len(g['assertions']) and len(refs)==len(cat['sources'])
    for f in facts.values():
        if not set(f['source_ids'])<=refs.keys() or f['periode_ref'] not in periods:raise ValueError('fait invalide '+f['id'])
        if not f.get('limites'):raise ValueError('limite absente '+f['id'])
    for r in rel:
        if not required<=r.keys():raise ValueError('relation incomplète '+r['id'])
        for key,vocab in [('role_ref',roles),('tache_ref',tasks),('ressource_ref',ress),('societe_ref',soc),('periode_ref',periods)]:
            if r[key] not in vocab:raise ValueError(key+' non résolu '+r['id'])
        if not set(r['source_ids'])<=refs.keys() or not set(r['fact_ids'])<=facts.keys():raise ValueError('preuve relation manquante '+r['id'])
        if any(facts[fid]['periode_ref']!=r['periode_ref'] for fid in r['fact_ids']):raise ValueError('anachronisme relation '+r['id'])
    for n in nrm:
        if not n.get('interpretation') or n['periode_ref'] not in periods or not set(n['source_ids'])<=refs.keys():raise ValueError('règle invalide '+n['id'])
        if n['sujet_ref'] not in soc or n['action_ref'] not in tasks:raise ValueError('règle sans sujet ou action '+n['id'])
    evidence={(x['assertion_id'],x['source_id']):x for x in proofs['assertions']}
    for f in facts.values():
        if any((f['id'],s) not in evidence for s in f['source_ids']):raise ValueError('provenance incomplète '+f['id'])
    # Entraînements produits uniquement à partir de paires positives explicitement attestées.
    challenges=[]
    for r in rel:
        # Candidates distinctes for documented cards; comparing an existing pair avoids inferring worldly negatives.
        others=[x for x in rel if x['id']!=r['id'] and x['role_ref']!=r['role_ref']]
        # stable, curated by distinct positive entries (all carry source IDs)
        choices=[r]+next_distinct(others,r,2)
        if len(choices)<3:continue
        label=tasks[r['tache_ref']]['label']+' · '+ress[r['ressource_ref']]['label']
        options=[{'id':x['id'],'label':roles[x['role_ref']]['label'],'documented_fact':x['fact_ids'][0]} for x in choices]
        challenges.append({
            'id':'gen:'+r['id'].split(':',1)[1],'type':'choisir_fiche','periode_ref':r['periode_ref'],
            'titre':'Rôle et action documentés','question':'Dans les fiches documentées ici, quel rôle est associé à « '+label+' » ?',
            'options':options,'correct_ref':r['id'],'fact_ids':r['fact_ids'],'source_ids':r['source_ids'],
            'reponse_courte':'Cette association est documentée pour ce groupe et cette époque.',
            'explication_longue':facts[r['fact_ids'][0]]['enonce_fr']+' '+facts[r['fact_ids'][0]]['limites'],
            'indices':['Observe la tâche et la ressource demandées.','Vérifie aussi l’époque et la société de chaque fiche.'],
            'prealables':prealables_pour(r),'evaluation':'entrainement_verifiable_pas_maitrise',
            'limite':'Comparer des fiches attestées ne signifie pas que les autres rôles étaient impossibles dans l’histoire.'})
    # From the same graph, factual prompts requiring an association (not repeated written quizzes).
    batches=[['innus-ainés','innus-outils','innus-peche'],['wendat-mandat','wendat-grand-chef','kiskakons-paix']]
    for j,batch in enumerate(batches,1):
        candidates=[x for x in rel if x['id'] in {'relation:'+y for y in batch}]
        if len(candidates)!=3:raise ValueError('jeu association source incomplet')
        challenges.append({'id':f'gen:associer-{j}','type':'associer','titre':'Relier des rôles et leurs tâches','periode_ref':'multi','question':'Relie chaque rôle à la tâche de sa fiche documentée.',
          'pairs':[{'left_id':x['role_ref'],'left':roles[x['role_ref']]['label'],'right_id':x['tache_ref'],'right':tasks[x['tache_ref']]['label'],'relation_id':x['id']} for x in candidates],
          'source_ids':sorted({s for x in candidates for s in x['source_ids']}),'fact_ids':[x['fact_ids'][0] for x in candidates],
          'reponse_courte':'Chaque lien proposé existe dans les fiches contextualisées.', 'explication_longue':'Ces associations décrivent des pratiques ou mandats situés. Elles ne définissent pas toutes les possibilités de chaque personne ou nation.',
          'indices':['Lis les fonctions avant de regarder les tâches.','Associe d’abord les tâches les plus précises.'],'prealables':['concept:role','concept:tache'],'evaluation':'entrainement_verifiable_pas_maitrise'})
    # Date cards: chronologically ordered source-supported landmarks (not inference of exact year from 1760+).
    chronology=[('1608','fait:champlain-1608','Établissement de Québec'),('1701','fait:paix-date','Grande Paix de Montréal'),('après 1760','fait:pouvoir-apres1760','Changement d’autorité coloniale'),('1825','fait:wendat-1825','Démarche politique wendat')]
    challenges.append({'id':'gen:chronologie','type':'chronologie','periode_ref':'multi','titre':'Repères chronologiques',
      'question':'Place ces fiches historiques dans l’ordre chronologique.',
      'elements':[{'id':fid,'label':l,'annee':y} for y,fid,l in chronology], 'correct_refs':[a[1] for a in chronology],
      'source_ids':sorted({s for _,fid,_ in chronology for s in facts[fid]['source_ids']}),'fact_ids':[fid for _,fid,_ in chronology],
      'indices':['Observe les siècles indiqués.','Le début du XVIIe siècle précède la paix de 1701.'],
      'reponse_courte':'Les événements sont replacés dans leur ordre historique.',
      'explication_longue':'La date d’un événement ne résume pas toute l’histoire; les sociétés autochtones existaient bien avant 1608 et existent encore aujourd’hui.',
      'prealables':['concept:siecle'],'evaluation':'entrainement_verifiable_pas_maitrise'})
    # Norms are carefully classified by SOURCE AUTHORITY, not by fantasy historical legal universality.
    for n in nrm:
        fact=facts[n['fact_ids'][0]]
        colonial=n['periode_ref']=='periode:1701'
        challenges.append({'id':'gen:'+n['id'].split(':',1)[1],'type':'distinguer_source','periode_ref':n['periode_ref'],
          'titre':'Qui affirme cette règle ?','question':'Cette responsabilité ou proposition est décrite par quelle source et pour quelle époque ?',
          'options':[{'id':'document-colonial-1701','label':'Un document colonial de 1701'},{'id':'nation-wendat-actuelle','label':'Le site de la Nation Wendat aujourd’hui'}],
          'correct_ref':'document-colonial-1701' if colonial else 'nation-wendat-actuelle',
          'fact_ids':n['fact_ids'],'source_ids':n['source_ids'],'reponse_courte':fact['enonce_fr'],
          'explication_longue':n['interpretation'],'indices':['Regarde le nom de la source.','Cherche l’époque indiquée à côté du document.'],
          'prealables':['concept:source','concept:epoque'],'evaluation':'entrainement_source_non_droit_general',
          'limite':'Une source est située : elle ne parle pas au nom de toutes les nations et de tous les temps.'})
    # Some assessments cannot have automatic correctness.
    challenges.append({'id':'gen:comparaison-sources','type':'observation_humaine','periode_ref':'multi','titre':'Comparer les voix et les époques',
        'question':'Avec un adulte, compare un passage du traité de 1701 avec une présentation contemporaine rédigée par la Nation Wendat. Qui parle ? Pour qui ? Que peut-on conclure, et que ne sait-on pas ?',
        'source_ids':['src:pac-texte-1701','src:wendat-histoire-2026'],'fact_ids':['fait:1701-appel-non-vengeance','fait:wendat-conseil-redevabilite'],
        'criteres':['Identifie deux sources et leurs périodes.','Explique la différence entre parole coloniale conservée et autodescription d’une nation aujourd’hui.','Ne suppose pas que le texte colonial remplace la voix des nations.'],
        'evaluation':'revue_humaine_aucun_score'})
    questions=[{'id':'question:'+f['id'].split(':',1)[1],'question':'Que savons-nous de « '+label+' » ?', 'fact_id':f['id'],'periode_ref':f['periode_ref']} for f,label in [(facts[x], ' '.join(x.split(':')[1].replace('-',' ').split())) for x in ['fait:wendat-conseil-redevabilite','fait:innus-recits-ete','fait:1701-discours-kiskakons','fait:1701-chasse-accord','fait:wendat-langue-vivante']]]
    public={'format':'ekole.societes-eleve/2.0','titre':g['titre'],'statut':'CANDIDAT DOCUMENTAIRE, PAS APPROUVÉ PAR LES NATIONS','description':'Fiches de sources et exercices déterministes. Aucun score de maîtrise scolaire.',
      'periodes':[{'id':p['id'],'label':p['label'],'note':p['note']} for p in g['periodes']],
      'faits':[{'id':f['id'],'texte':f['enonce_fr'],'periode_ref':f['periode_ref'],'sources':f['source_ids'],'limites':f['limites'],'ancrage':f.get('ancrage_documentaire','Ancrage précis à compléter.')} for f in g['assertions']],
      'roles':[{'id':r['id'],'label':r['label']} for r in g['roles']],
      'taches':[{'id':t['id'],'label':t['label']} for t in g['taches']],
      'ressources':[{'id':t['id'],'label':t['label']} for t in g['ressources']],
      'societes':[{'id':s['id'],'label':s['label']} for s in g['societes']],
      'relations':rel,'normes':nrm,'defis':challenges,'questions':questions,
      'sources':[{'id':s['id'],'titre':s['title'],'url':s['locator'],'limites':s.get('limitations','')} for s in cat['sources']],
      'visuels':visual['images'],'generation_images':False,'generation_reponses_ia':False,
      'politique_donnees':'Pas de profil enfant, pas de correction par IA, pas de sauvegarde des réponses.'}
    return public

def next_distinct(others,ref,count):
    seen={ref['role_ref']};result=[]
    for x in others:
        if x['role_ref'] in seen:continue
        result.append(x);seen.add(x['role_ref'])
        if len(result)==count:break
    return result

def prealables_pour(r):
    return ['concept:epoque','concept:role','concept:tache']

def main():
    p=argparse.ArgumentParser(description='Compile le graphe v2 vers un atelier public sans IA.');p.add_argument('--root',type=Path,default=HOME);p.add_argument('--prefer-installed',action='store_true')
    a=p.parse_args();root=a.root.resolve();data=compile_v2(root,a.prefer_installed)
    dest=root/'site/eleve/ateliers/rencontres-quebec/donnees_v2.js';dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text('window.EKOLE_SOC_V2 = '+json.dumps(data,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+';\n',encoding='utf-8')
    print('OK version 2 :',len(data['faits']),'faits,',len(data['defis']),'activités déterministes/observation,',len(data['normes']),'normes, fichier',dest.relative_to(root))
if __name__=='__main__':main()
