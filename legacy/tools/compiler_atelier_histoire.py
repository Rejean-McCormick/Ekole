#!/usr/bin/env python3
"""Compile, hors ligne, les faits d'un Kristal en jeu public sans banques de correction."""
from pathlib import Path
import argparse, json, sys
HERE=Path(__file__).resolve().parents[1]
def load(p): return json.loads(p.read_text(encoding='utf-8'))
def compile_game(root=HERE, prefer_installed=False):
    module=root/'modules/qc-pri-us-009'
    installed=root/'kristals/qc-pri-us-009'
    base=(installed if prefer_installed and (installed/'canon/domain/societes-rencontres-v1.json').exists() else module)
    canon=load(base/'canon/domain/societes-rencontres-v1.json')
    exercises=load(base/'experience/histoire-rencontres/EXERCICES_SEMANTIQUES.json')['exercices']
    visuals=load(base/'experience/histoire-rencontres/RESSOURCES_VISUELLES.json')['images']
    cat=load(base/'sources/source-catalog.additions.json') if (base/'sources/source-catalog.additions.json').exists() else load(module/'sources/source-catalog.additions.json')
    assert_by_id={a['id']:a for a in canon['assertions']}
    source_by_id={s['id']:s for s in cat['sources']}
    periods={p['id']:p['label'] for p in canon['periodes']}
    result=[]
    for e in exercises:
        used=e.get('fact_ids') or [e.get('fact_id')]
        if not used or any(v not in assert_by_id for v in used):raise ValueError('Référence de fait manquante pour '+e['id'])
        refs=set()
        for fid in used:
            a=assert_by_id[fid]
            if not a.get('source_ids'):raise ValueError('Fait non sourcé: '+fid)
            refs.update(a['source_ids'])
        if refs-set(source_by_id):raise ValueError('Sources non résolues: '+e['id'])
        mode=e['mode']
        if mode in ('choix','cloze'):
            opts=e['options'];good=e['reponse_ref']
            if len(set(o['ref'] for o in opts))!=len(opts) or sum(o['ref']==good for o in opts)!=1:raise ValueError('Choix non discriminant '+e['id'])
            # An explicit correct response is allowed only when bound to a sourced claim or a manually justified pedagogical bridge.
            a=assert_by_id[used[0]]
            allowed={a['sujet_ref'],a['objet_ref']}
            if good not in allowed and not e.get('distracteurs_revu') and not e.get('pedagogical_bridge'):
                raise ValueError('Réponse sans relation canonique ni pont éditorial: '+e['id'])
        if mode=='associer':
            if len(e['pairs'])<2 or any(p['fact_id'] not in used for p in e['pairs']):raise ValueError('Paires non traçables '+e['id'])
        if mode=='ordonner':
            y=[x['year'] for x in e['elements']]
            if y != sorted(y) or len(set(y))!=len(y):raise ValueError('Chronologie incohérente '+e['id'])
        result.append(dict(e,preuves_sources=sorted(refs),type_validation='humaine' if mode=='humain' else 'deterministe_entraînement'))
    visible_sources=[{'id':s['id'],'title':s['title'],'url':s['locator'],'limitations':s.get('limitations','')} for s in cat['sources']]
    if any(not s['url'].startswith('https://') for s in visible_sources):raise ValueError('URL source invalide')
    return {'format':'ekole.histoire-eleve-public/1.0','title':canon['titre'],'statut':'ENTRAÎNEMENT — CONTENU CANDIDAT À REVOIR, NON CERTIFIÉ','objectif':canon['objectif_existant'],'periodes':periods,'faits':[{'id':a['id'],'periode_ref':a['periode_ref'],'texte':a['enonce_fr'],'sources':a['source_ids'],'limites':a['limites']} for a in canon['assertions']],'liaisons':canon['liaisons_role_tache'],'roles':canon['roles'],'taches':canon['taches'],'ressources':canon['ressources'],'exercices':result,'visuels':visuals,'sources':visible_sources,'questions_guides':[
       {'question':'Comment les familles étaient-elles organisées dans des villages historiques wendat ?','fact_id':'fait:wendat-maisons'},
       {'question':'À quoi renvoie le territoire nommé Nitassinan ?','fact_id':'fait:innus-saisons'},
       {'question':'Qui exerce des responsabilités collectives dans la Nation Wendat aujourd’hui ?','fact_id':'fait:wendat-conseil-actuel'},
       {'question':'Quelles démarches politiques ont mené des représentants wendat en 1825 ?','fact_id':'fait:wendat-1825'},
       {'question':'Qu’est-ce qui change après 1760 dans les administrations coloniales ?','fact_id':'fait:pouvoir-apres1760'},
       {'question':'Qui vivait sur ce territoire avant les établissements français ?','fact_id':'fait:peuples-avant'},
       {'question':'Que s’est-il passé à Québec en 1608 ?','fact_id':'fait:champlain-1608'},
       {'question':'Quels biens étaient échangés ?','fact_id':'fait:commerce-fourrures'},
       {'question':'Qui a participé à la Grande Paix ?','fact_id':'fait:paix-participants'},
       {'question':'Qui était Kondiaronk dans cette histoire ?','fact_id':'fait:kondiaronk'},
       {'question':'Les peuples autochtones existent-ils encore aujourd’hui ?','fact_id':'fait:vie-aujourdhui'}
      ]}
def main():
    ap=argparse.ArgumentParser(description='Compile le contenu public Élève depuis les faits sourcés (zéro IA, zéro réseau).')
    ap.add_argument('--root',type=Path,default=HERE);ap.add_argument('--prefer-installed',action='store_true')
    args=ap.parse_args();root=args.root.resolve();data=compile_game(root,args.prefer_installed)
    dest=root/'site/eleve/ateliers/rencontres-quebec/donnees.js';dest.parent.mkdir(parents=True,exist_ok=True)
    text='window.EKOLE_HISTOIRE = '+json.dumps(data,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+';\n'
    dest.write_text(text,encoding='utf-8');print('OK',len(data['faits']),'faits,',len(data['exercices']),'activités,',dest.relative_to(root))
if __name__=='__main__':main()
