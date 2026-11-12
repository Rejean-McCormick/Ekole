#!/usr/bin/env python3
"""Un seul parcours de préparation Ékole/Kompose/Kontexte/Kamel.

Ne crée PAS de World réel, n'envoie PAS de messages, ne distribue PAS de
rôles à des enfants et ne déclare aucune compétence maîtrisée.
Les fichiers sont préparés pour la revue d'un enseignant; l'admission du
runtime devra passer par les propriétaires Orgo/Konnaxion autorisés.
"""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys


def _file_inside(root: Path, candidate: Path):
    root=root.resolve(strict=True)
    target=candidate.absolute()
    if target.is_symlink() or not target.is_file() or not target.resolve().is_relative_to(root):
        raise ValueError('Mission hors de Kontexte ou lien symbolique interdit')
    return target


def _load_module(name, path: Path):
    if not path.is_file() or path.is_symlink():
        raise ValueError('Module propriétaire absent : '+str(path))
    spec=importlib.util.spec_from_file_location(name,path)
    if spec is None or spec.loader is None:raise ValueError('Module illisible')
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def prepare(*,kontexte:Path,kompose:Path,mission_id:str,out:Path,
            participants:Path|None=None,kamel:Path|None=None,base_url:str|None=None):
    # Conserve les propriétaires: les règles de sécurité des cartes et de
    # distribution ne sont PAS recodées dans Ékole.
    cards_mod=_load_module('ekole_owner_kontexte_cards',kontexte/'src/kontexte/kidaxion_cards.py')
    roles_mod=_load_module('ekole_owner_kompose_roles',kompose/'src/kompose/school_role_proposals.py')
    if not cards_mod.IDENTIFIER.fullmatch(mission_id):raise ValueError('Identifiant de mission invalide')
    mission_path=_file_inside(kontexte,kontexte/'data/missions'/f'{mission_id}.json')
    raw=mission_path.read_bytes()
    mission=json.loads(raw)
    if mission.get('id')!=mission_id:raise ValueError('Référence de mission divergente')
    card_pack=cards_mod.project_cards(mission)
    suggestions=None
    if participants:
        if participants.is_symlink() or not participants.is_file() or participants.stat().st_size>128000:
            raise ValueError('Dossier anonymisé des participants invalide')
        people=json.loads(participants.read_text(encoding='utf8'))
        suggestions=roles_mod.propose_roles(mission,people)
    output={
      'format':'ekole.collaborative-teacher-plan/1',
      'mission_ref':mission_id,'mission_sha256':hashlib.sha256(raw).hexdigest(),
      'role_count':len(mission['roles']),'step_count':len(mission['steps']),
      'preparation_mode':'teacher_review_only', 'authorizations':{
          'orgo_runtime_admitted':False,'konnaxion_project_linked':False,
          'teacher_approved':False,'dispatch_allowed':False},
      'role_proposals':suggestions,
      'cards_file':'cartes.json',
      'print_file':'cartes-impression.html' if kamel else None,
    }
    # Produce files only in an explicit output directory; do not touch repos.
    out=out.resolve()
    out.mkdir(parents=True,exist_ok=True)
    (out/'cartes.json').write_text(json.dumps(card_pack,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    if kamel:
        printmod=_load_module('ekole_owner_kamel_print',kamel/'tools/ekole/print_mission_cards.py')
        html=printmod.render(card_pack,base_url=base_url,monochrome=True)
        (out/'cartes-impression.html').write_text(html,encoding='utf8')
    (out/'plan-enseignant.json').write_text(json.dumps(output,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    return output


def main(argv=None):
    parser=argparse.ArgumentParser(description='Préparer une aventure multi-rôles en revue seulement')
    home=Path(__file__).resolve().parents[2]
    parser.add_argument('--kontexte',type=Path,default=home/'Kontexte')
    parser.add_argument('--kompose',type=Path,default=home/'Kompose')
    parser.add_argument('--mission',default='fete-sorciere')
    parser.add_argument('--participants',type=Path,help='Profils PSEUDONYMES, aucun nom ou courriel')
    parser.add_argument('--kamel',type=Path,help='Racine du dépôt Kamel pour produire un HTML imprimable')
    parser.add_argument('--url',help='Portail HTTPS authentifié, QR de consultation seulement')
    parser.add_argument('--out',required=True,type=Path)
    args=parser.parse_args(argv)
    payload=prepare(kontexte=args.kontexte,kompose=args.kompose,mission_id=args.mission,out=args.out,
                    participants=args.participants,kamel=args.kamel,base_url=args.url)
    print(json.dumps({'ok':True,'mission':payload['mission_ref'],'etapes':payload['step_count'],
                      'statut':'REVUE_SEULEMENT','out':str(args.out)},ensure_ascii=False))
if __name__=='__main__':main()
