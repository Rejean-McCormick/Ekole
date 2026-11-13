#!/usr/bin/env python3
"""Offline PRF-22 v0.3: catalogue, inspect work draft, validate design, export handoff."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys

from composer_core import load_catalogue
from prf22_core import build_design, export_pack, load_authoring
from prf22_validator import validate_document
from prf22_workspace import materialize


def main(argv=None) -> int:
    parser=argparse.ArgumentParser(description='Atelier PRF-22 — hors ligne, conception uniquement')
    sub=parser.add_subparsers(dest='command',required=True)
    cat=sub.add_parser('catalogue',help='Afficher le résumé des sources Kontexte')
    cat.add_argument('--kontexte',type=Path,required=True)
    v=sub.add_parser('valider',help='Vérifier un Kristal de conception (ni revue ni séance)')
    v.add_argument('design',type=Path)
    v.add_argument('--require-schema',action='store_true')
    b=sub.add_parser('exporter',help='Créer un dossier à partir d’un brouillon déjà rédigé')
    b.add_argument('authoring',type=Path)
    b.add_argument('--vers',type=Path,required=True)
    b.add_argument('--kontexte',type=Path,help='Confirmer les fichiers sources et leurs empreintes observées')
    w=sub.add_parser('kristal',help='Prévisualiser ou créer explicitement un workspace Kristal local, non canonique')
    w.add_argument('design',type=Path)
    w.add_argument('--arketype',type=Path,required=True)
    w.add_argument('--parent',type=Path,required=True)
    w.add_argument('--slug',required=True)
    w.add_argument('--write',action='store_true',help='Action explicite: créer le workspace non publié')
    args=parser.parse_args(argv)
    try:
        if args.command=='catalogue':
            c=load_catalogue(args.kontexte)
            print(f'Kontexte : {c.trames_count} trames, {c.missions_count} missions, {len(c.activities)} activités, {len(c.objectives)} objectifs, {len(c.roles)} rôles')
            return 0
        if args.command=='valider':
            design=json.loads(args.design.read_text(encoding='utf-8'))
            err,used=validate_document(design,require_schema=args.require_schema)
            print('Contrat structurel :', 'JSON Schema 2020-12 vérifié' if used else 'sous-ensemble portable vérifié; jsonschema optionnel')
            for e in err:print('ÉCHEC :',e)
            if not err:print('OK structure déclarée; aucune qualification pédagogique ni autorisation de séance')
            return 1 if err else 0
        if args.command=='kristal':
            design=json.loads(args.design.read_text(encoding='utf-8'))
            result=materialize(design,args.arketype,args.parent,args.slug,dry_run=not args.write)
            print(json.dumps(result,ensure_ascii=False,indent=2))
            return 0
        if args.command=='exporter':
            state=load_authoring(args.authoring)
            if args.kontexte:
                from composer_core import attach_ekole_activity_patterns
                c=attach_ekole_activity_patterns(load_catalogue(args.kontexte))
                for a in state['draft']['activity_bindings']:c.activity(a['activity_ref'])
                for o in state['draft']['learning_objective_links']:c.objective(o['objective_ref'])
                if state.get('source_observations'):
                    from prf22_core import observe_catalogue_sources
                    current={x['relative_path']:x['observed_sha256'] for x in observe_catalogue_sources(c.root,state['draft'])}
                    for previous in state['source_observations']:
                        if current.get(previous['relative_path'])!=previous['observed_sha256']:
                            raise ValueError('Source Kontexte changée depuis le brouillon : '+previous['relative_path'])
            design=build_design(state['draft'],state['theory_entries'],state['dependency_lines'])
            target=export_pack(args.vers,design,state['draft'],state['theory_entries'],state['dependency_lines'],
                               args.kontexte)
            print('Dossier de conception exporté :',target)
            return 0
    except (OSError,KeyError,ValueError,TypeError,json.JSONDecodeError) as e:
        print('ÉCHEC :',e,file=sys.stderr)
        return 2
    return 2

if __name__=='__main__':sys.exit(main())
