#!/usr/bin/env python3
"""Compiler le cours depuis des Kristals autonomes épinglés ; jamais depuis les copies v1/v2 du cours.
Les textes et réponses restent déterministes, hors ligne, sans appel IA.
"""
import argparse,json,hashlib,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
COURSE_REL='modules/qc-pri-us-009/experience/histoire-rencontres/REFERENCES_KRISTALS_V3.json'
SLUGS={'societes-autochtones-quebec','rencontres-coloniales-quebec'}
def rd(path):return json.loads(path.read_text(encoding='utf-8'))
def dump(data):return json.dumps(data,ensure_ascii=False,indent=2)+'\n'
def compile_data(root=ROOT, installed=False):
    root=Path(root)
    coursepath=root/('kristals/qc-pri-us-009/experience/histoire-rencontres/REFERENCES_KRISTALS_V3.json' if installed else COURSE_REL)
    if not coursepath.is_file():raise ValueError('références du cours non trouvées : '+str(coursepath))
    c=rd(coursepath)
    if c.get('kristal_cours')!='qc-pri-us-009' or set(x['kristal'] for x in c['dependances'])!=SLUGS:raise ValueError('références du cours incorrectes')
    graph=[]; owners={};sourceowners={}; periods={}; assertions={}
    relations=[];names={}
    for ref in c['dependances']:
        slug=ref['kristal']; base=root/'kristals'/slug
        path=root/ref['local_path']
        if path.resolve()!= (base/'canon/domain/graphe-v3.json').resolve() or not path.is_file():raise ValueError('chemin non canonique : '+slug)
        snap=base/'build/v9/state-snapshot.json'
        if not snap.is_file():raise ValueError('build v9 manquant : '+slug)
        s=rd(snap)
        if s.get('logical_commitment')!=ref['state_logical_commitment'] or s['members'][0]['logical_commitment']!=ref['artifact_logical_commitment']:
            raise ValueError('référence périmée/altérée, revoir et réépingler : '+slug)
        # Verify exact canonical content still matches the *built* artifact, not only an old receipt.
        artifact=next((m for m in s['members'] if m['artifact_id']==ref['artifact_id']),None)
        if artifact is None:raise ValueError('artefact absent du snapshot : '+slug)
        built=list((base/'build/v9/artifacts').glob('*.logical-artifact.json'))
        if len(built)!=1:raise ValueError('build incomplet : '+slug)
        b=rd(built[0])
        if b.get('artifact_id')!=ref['artifact_id']:raise ValueError('artefact construit différent : '+slug)
        # Canon SHA-256 is used as a cheap drift detector in addition to pinned logical commitments.
        if hashlib.sha256(path.read_bytes()).hexdigest()!=ref.get('file_sha256'):
            raise ValueError('contenu canonique modifié depuis l’épinglage : '+slug)
        g=rd(path);graph.append(g)
        if g['slug']!=slug:raise ValueError('graphe mal attribué : '+slug)
        source_ids={x['id'] for x in g['sources']}
        for f in g['assertions']:
            fid=f['id']
            if fid in assertions:raise ValueError('propriété d’assertion double : '+fid)
            if not set(f.get('source_ids',[]))<=source_ids:raise ValueError('preuve sans source : '+fid)
            if not f.get('periode_ref') or not f.get('enonce_fr'):raise ValueError('portée ou énoncé absent : '+fid)
            if not f.get('limites'):raise ValueError('limites absentes : '+fid)
            for p in f.get('preuves',[]):
                if p['source_id'] not in source_ids:raise ValueError('source v3 non résolue '+fid)
            normalized_sources=f.get('source_ids') or [x['source_id'] for x in f.get('preuves',[])]
            assertions[fid]={**f,'source_ids':normalized_sources,'proprietaire':slug}
        for x in g['sources']:
            sourceowners[(slug,x['id'])]=x
        for x in g['periodes']:
            if x['id'] in periods and x!=periods[x['id']]:raise ValueError('période contradictoire : '+x['id'])
            periods[x['id']]=x
        for kind in ('roles','taches','ressources','societes'):
            for x in g[kind]:
                key=(kind,x['id'])
                if key in names and names[key]!=x:raise ValueError('terme partagé contradictoire : '+x['id'])
                names[key]=x
        relations.extend([{**r,'proprietaire':slug} for r in g['relations']])
        owners[slug]=g
    # All selected facts must be accounted for in precisely one independent corpus.
    keys=[fid for group in c['selection_faits'].values() for fid in group]
    if len(keys)!=len(set(keys)):raise ValueError('sélection en double')
    missing=set(keys)-set(assertions)
    if missing:raise ValueError('faits sélectionnés sans Kristal source : '+str(sorted(missing)))
    challenges=[]
    for category,ids in c['selection_faits'].items():
        for fid in ids:
            f=assertions[fid]
            if f.get('eligible_exercice') is False:continue
            # Every option below is a *true claim* from an actual source; wrong selection means wrong for this specific card.
            alternatives=[oid for oid in keys if oid!=fid and oid not in ids and assertions[oid]['enonce_fr']!=f['enonce_fr']]
            options=([fid]+alternatives[:2]);
            if len(options)<3:continue
            shift=len(challenges)%3;options=options[shift:]+options[:shift]
            source_labels=[sourceowners[(f['proprietaire'],sid)].get('title','Source') for sid in f.get('source_ids',[])]
            p=periods[f['periode_ref']]['label']
            challenges.append({'id':'v3:carte:'+fid,'type':'choix_attestation','categorie':category,
              'question':'Quelle fiche du corpus documente cette information ?','indice':f['enonce_fr'],
              'contexte':p,'options':[{'id':x,'label':assertions[x]['enonce_fr']} for x in options],
              'correct_id':fid,'reponse_courte':'Cette fiche est bien documentée pour la période indiquée.',
              'reponse_longue':f['enonce_fr']+' '+f['limites']+' Source(s) : '+', '.join(source_labels)+'.',
              'source_ids':f['source_ids'],'proprietaire':f['proprietaire'],
              'prealables':['notion:source-historique','notion:periode-historique'],
              'attention':'Les autres fiches peuvent être vraies; elles ne répondent simplement pas au repère choisi.'})
    # Generate relation exercises from clearly documented relations, never from claims of impossibility.
    for rel in relations:
        fid=rel.get('fact_ids',[None])[0]
        if fid not in assertions or fid not in keys:continue
        role=names.get(('roles',rel['role_ref']))
        task=names.get(('taches',rel['tache_ref']))
        if not role or not task:continue
        choices=[r for r in relations if r['id']!=rel['id'] and r.get('role_ref')!=rel['role_ref'] and names.get(('roles',r.get('role_ref')))]
        if len(choices)<2:continue
        options=[rel]+choices[:2];n=len(challenges)%3;options=options[n:]+options[:n]
        f=assertions[fid]
        challenges.append({'id':'v3:relation:'+rel['id'],'type':'choix_role','categorie':'roles_et_taches',
          'question':'Dans les fiches sourcées, quel rôle est associé à cette tâche ?','indice':task['label'],
          'contexte':periods[rel['periode_ref']]['label'],
          'options':[{'id':x['id'],'label':names[('roles',x['role_ref'])]['label']} for x in options],
          'correct_id':rel['id'],'reponse_courte':'Le lien rôle–tâche est documenté dans ce contexte.',
          'reponse_longue':f['enonce_fr']+' '+f['limites'], 'source_ids':rel.get('source_ids',[]),
          'proprietaire':rel['proprietaire'],'prealables':['notion:role','notion:tache','notion:periode-historique'],
          'attention':'Choisir une autre fiche ne démontre pas que cet autre rôle était historiquement impossible.'})
    # Student projection: only selected facts and pedagogical metadata, *no teacher solutions or cultural claims invented*.
    student_facts=[{'id':fid,'enonce_fr':assertions[fid]['enonce_fr'],'periode':periods[assertions[fid]['periode_ref']]['label'],
                    'kristal':assertions[fid]['proprietaire'],'source_ids':assertions[fid]['source_ids'], 'limites':assertions[fid]['limites']} for fid in keys]
    visualpath=root/'modules/qc-pri-us-009/experience/histoire-rencontres/RESSOURCES_VISUELLES_V2.json'
    visual=rd(visualpath)['images'] if visualpath.is_file() else []
    return {'format':'ekole.atelier-histoire-v3/3.0','titre':'Rencontres et échanges entre populations',
      'objectif':c['objectif'],'preuve':c['preuve'],'statut':'exploration_non_homologuee',
      'architecture':'Les assertions sont lues dans deux Kristals autonomes; le cours ne détient que sa sélection.',
      'dependances':[{'kristal':x['kristal'],'digest':x['state_logical_commitment']['digest']} for x in c['dependances']],
      'categories':c['selection_faits'],'faits':student_facts,'activites':challenges,
      'sources':[{'id':sid,'title':s.get('title','Source'),'locator':s.get('locator',''),'proprietaire':owner} for (owner,sid),s in sourceowners.items()],
      'images':visual,'limites':['Aucune approbation culturelle ou pédagogique présumée.','Entraînement ≠ preuve de maîtrise.','Une absence dans le corpus ne démontre pas une négation historique.']}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,default=ROOT);ap.add_argument('--prefer-installed',action='store_true');ap.add_argument('--validate-only',action='store_true');args=ap.parse_args()
    data=compile_data(args.root,args.prefer_installed)
    out=args.root/'site/eleve/ateliers/rencontres-quebec/donnees_v3.js'
    if not args.validate_only:
        out.parent.mkdir(parents=True,exist_ok=True)
        out.write_text('window.EKOLE_HISTOIRE_V3 = '+json.dumps(data,ensure_ascii=False,indent=2)+';\n',encoding='utf-8')
    print(f"OK: {len(data['faits'])} faits sélectionnés, {len(data['activites'])} activités, {len(data['dependances'])} Kristals référencés; {'vérifié' if args.validate_only else 'compilé'}")
if __name__=='__main__':main()
