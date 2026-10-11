#!/usr/bin/env python3
"""Consultation / compilation déterministe du Kristal autonome.
Aucune IA, aucun accès internet. Une correspondance faible n'est JAMAIS une réponse.
"""
from pathlib import Path
import argparse, json, re, unicodedata

SLUG='societes-autochtones-quebec'
RELPATH=f'kristals/{SLUG}/canon/domain/encyclopedie-v4.json'
EXPORT='site/eleve/encyclopedie-autochtones/bibliotheque.json'
STOP={'est','ce','que','qui','quels','quelles','quoi','comment','pourquoi','les','des','une','un','la','le','l','a','en','dans','de','du','au','aux','sur','ils','elles','et','pour','avec','c','d','s','t','y','fait','fais','avoir','avait','étaient','etaient','il','elle','tu','vous','ont','était','etait','puis','genre','dont','cette','cet','leur','leurs','entre','tous','tout','ça','ca','pas','se','sont','nous','par','comme'}
def norm(s):
    s=unicodedata.normalize('NFKD',str(s).casefold());s=''.join(c for c in s if not unicodedata.combining(c))
    s=re.sub(r'[^a-z0-9]+',' ',s)
    s=' '.join(s.split())
    replacements={'zeroquains':'iroquoiens','iroquosiens':'iroquoiens','iroquains':'iroquoiens','tanaient':'tannaient','tanaient':'tannaient','nomades':'nomade'}
    return ' '.join(replacements.get(t,t) for t in s.split())
def tokens(s):
    return {t.rstrip('s') if len(t)>5 else t for t in norm(s).split() if t not in STOP and len(t)>2}
def load(root):
    path=Path(root)/RELPATH
    return json.loads(path.read_text(encoding='utf-8'))
def validate(data):
    errors=[]
    arts=data['articles']; ids={a['id'] for a in arts}; sids={s['id'] for s in data['sources']}
    if len(ids)!=len(arts):errors.append('Identifiants article dupliqués')
    if len(sids)!=len(data['sources']):errors.append('Sources dupliquées')
    topics={t['id'] for t in data['themes']}
    if len(topics)!=len(data['themes']):errors.append('Thèmes dupliqués')
    for x in arts:
        if x['theme'] not in topics:errors.append(f'Thème inconnu {x["id"]}')
        if not x['societe'] or not x['epoque']:errors.append(f'Contexte manquant {x["id"]}')
        if not x.get('reponse_courte') or not x.get('explication_detaillee'):errors.append(f'Réponse vide {x["id"]}')
        for sr in x['sources']:
            if sr['id'] not in sids:errors.append(f'Source introuvable {x["id"]} {sr["id"]}')
        for p in x.get('prerequis',[]):
            if p not in ids:errors.append(f'Prérequis inconnu {x["id"]} {p}')
    qids=set()
    for q in data['entrainements']:
        if q['id'] in qids:errors.append('Activité dupliquée '+q['id'])
        qids.add(q['id'])
        if q['entree_ref'] not in ids:errors.append(f'Exercice sans article {q["id"]}')
        opts={o['id'] for o in q['options']}
        if len(opts)!=len(q['options']) or q['bonne_option'] not in opts: errors.append(f'Options mal définies {q["id"]}')
        for s in q['source_refs']:
            if s not in sids:errors.append(f'Source d’activité absente {q["id"]}')
    for c in data.get('chapitres',[]):
        if c['theme'] not in topics or len(c['sections'])<2:errors.append('Chapitre incomplet '+c['theme'])
        for source in c['source_ids']:
            if source not in sids:errors.append('Source de chapitre inconnue '+source)
    for v in data['visuels']:
        if v['theme'] not in topics:errors.append(f'Thème visuel inconnu {v["id"]}')
        if not v['prompt'] or not re.fullmatch(r'images/[a-z0-9_-]+\.webp',v['image_attendue']):errors.append(f'Prompt/chemin non conforme {v["id"]}')
    return errors

def search(data,question):
    q=norm(question); qt=tokens(question)
    if not qt:return []
    ranking=[]
    for a in data['articles']:
        head=[a['question'],*a.get('formulations',[])]
        if any(q==norm(h) for h in head):return [(1.0,a)]
        forms=[tokens(t) for t in head]
        kw=tokens(' '.join(a['mots_cles']))
        # high-confidence direct question overlap. The keywords are only for discovering suggested questions.
        direct=max((len(qt&f)/(len(qt|f) or 1) for f in forms),default=0)
        overlap=len(qt&kw)/(len(qt) or 1)
        score=max(direct,0.50*overlap)
        if score>0.18:ranking.append((round(score,3),a))
    return sorted(ranking,key=lambda z:(-z[0],z[1]['id']))[:8]

def answer(data,question):
    matches=search(data,question)
    if not matches:return {'statut':'non_documente','message':'Je ne trouve pas de réponse suffisamment précise. Choisis un thème ou reformule en nommant la nation et l’époque.','suggestions':[]}
    score,best=matches[0]
    if score>=0.72 and (len(matches)==1 or score-matches[1][0]>=0.15):
        return {'statut':'reponse_du_corpus','article':best,'score':score}
    return {'statut':'choix_de_question','message':'J’ai trouvé des fiches proches. Choisis celle qui correspond exactement à ta question :','suggestions':[{'id':a['id'],'question':a['question'],'score':s} for s,a in matches[:5]]}

def compile_view(data):
    # Public articles and training only. No protected materials or learner tracking.
    return {k:data[k] for k in ('format','titre','themes','chapitres','sources','articles','entrainements','visuels','politique')}

def main():
    parser=argparse.ArgumentParser(description='Consulter et compiler le Kristal autochtone hors ligne')
    parser.add_argument('--root',default='.',help='Racine Ekole : contient kristals/')
    parser.add_argument('--question',help='Question en français : recherche prudente et propositions en cas d’ambiguïté')
    parser.add_argument('--search',help='Rechercher des thèmes ou mots-clés')
    parser.add_argument('--id',help='Identifiant exact d’article')
    parser.add_argument('--list-topics',action='store_true')
    parser.add_argument('--check',action='store_true')
    parser.add_argument('--compile',action='store_true')
    args=parser.parse_args()
    data=load(args.root);errors=validate(data)
    if errors: raise SystemExit('\n'.join(errors))
    if args.check:print(f'OK : {len(data["articles"])} fiches, {len(data["sources"])} références, {len(data["entrainements"])} exercices')
    if args.list_topics:
        for t in data['themes']:
            print(t['id']+' : '+t['titre'])
    if args.id:
        a=next((x for x in data['articles'] if x['id']==args.id),None)
        print(json.dumps(a if a else {'statut':'inconnu'},ensure_ascii=False,indent=2))
    if args.question:print(json.dumps(answer(data,args.question),ensure_ascii=False,indent=2))
    if args.search:
        for score,a in search(data,args.search):print(f'{score:.2f} | {a["id"]} | {a["question"]}')
    if args.compile:
        target=Path(args.root)/EXPORT;target.parent.mkdir(parents=True,exist_ok=True)
        target.write_text(json.dumps(compile_view(data),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        print('Compilé :',target)
if __name__=='__main__':main()
