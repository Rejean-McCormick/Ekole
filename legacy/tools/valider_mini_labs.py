#!/usr/bin/env python3
"""Validation hors ligne des défis MiniLab. Ne modifie aucun contenu source."""
import json,pathlib,subprocess,sys
ROOT=pathlib.Path(__file__).resolve().parents[1]

def verify(root=ROOT):
    source=root/'site/eleve/labo/data/catalogue.json'
    bank=json.loads(source.read_text(encoding='utf8'))
    if bank.get('format')!='ekole.microlab-catalog/0.1':raise ValueError('Format de catalogue non reconnu')
    cases=bank.get('items',[])
    ids=[x.get('id') for x in cases]
    if bank.get('count')!=len(cases) or len(cases)<9 or len(ids)!=len(set(ids)):raise ValueError('Nombre/IDs incorrects')
    forbidden={'published','certified','mastery_pass'}
    for x in cases:
        if x.get('status')!='prototype_revue_humaine' or x.get('validation_mode')!='deterministic_practice':raise ValueError('Statut inexact: '+str(x.get('id')))
        if x.get('association_status') not in ('generique_sans_lien_cours','illustration_candidate_non_validee'):raise ValueError('Lien sans qualification')
        if x.get('source_kristal_id') is not None and not str(x['source_kristal_id']).startswith('qc-pri-'):raise ValueError('ID source invalide')
        if any(x.get(k) for k in forbidden):raise ValueError('Statut de publication inadmissible')
        if len(x.get('hints',[]))<2:raise ValueError('Indices insuffisants')
    runner=root/'tests/test_microlab_engine_v9.js'
    try:r=subprocess.run(['node',str(runner),str(root)],text=True,capture_output=True,check=False,timeout=30)
    except FileNotFoundError:raise ValueError('Node.js requis pour exécuter les tests du moteur')
    if r.returncode:raise ValueError('Tests déterministes échoués: '+r.stdout+r.stderr)
    return {'status':'PASS','scenarios':len(cases),'engine_types':len({x['type'] for x in cases}),'details':r.stdout.strip()}

if __name__=='__main__':
    try:print(json.dumps(verify(),ensure_ascii=False,indent=2))
    except Exception as exc:print('ERREUR:',exc,file=sys.stderr);sys.exit(1)
