#!/usr/bin/env python3
"""Interrogation locale du Kristal autochtone sans aucune dépendance au cours Ekole.
Ne produit pas de réponses à des questions arbitraires en langage naturel.
"""
from pathlib import Path
import argparse,json
ROOT=Path(__file__).resolve().parents[1]
def query(root=ROOT,search='',period='',society='',limit=100):
    p=Path(root)/'kristals/societes-autochtones-quebec/canon/domain/graphe-v3.json'
    data=json.loads(p.read_text(encoding='utf-8'))
    facts=data['assertions']
    if search:facts=[x for x in facts if search.casefold() in x.get('enonce_fr','').casefold()]
    if period:facts=[x for x in facts if x.get('periode_ref')==period]
    if society:facts=[x for x in facts if x.get('sujet_ref')==society]
    return [{'id':x['id'],'periode_ref':x['periode_ref'],'sujet_ref':x.get('sujet_ref'),
             'enonce_fr':x['enonce_fr'],'source_ids':x.get('source_ids') or [s['source_id'] for s in x.get('preuves',[])],
             'limites':x['limites']} for x in facts[:limit]]
def main():
    ap=argparse.ArgumentParser(description='Lecture hors ligne du Kristal autochtone indépendant')
    ap.add_argument('--root',type=Path,default=ROOT);ap.add_argument('--search',default='');ap.add_argument('--period',default='');ap.add_argument('--society',default='');ap.add_argument('--limit',type=int,default=100);args=ap.parse_args()
    if args.limit<1:ap.error('--limit doit être positif')
    print(json.dumps({'kristal':'societes-autochtones-quebec','statut':'candidate_non_validee','resultats':query(args.root,args.search,args.period,args.society,args.limit)},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
