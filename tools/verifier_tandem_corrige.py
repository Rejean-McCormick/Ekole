#!/usr/bin/env python3
"""Vérification locale coordonnée : aucune admission, écriture réseau, ni création de World.

Utilise l'arborescence des dépôts sur C:/mycode ; --workspace permet des dépôts
côte à côte pour tester un overlay avant de l'installer sous Windows.
"""
from __future__ import annotations

import argparse
import importlib.util
import os
from pathlib import Path
import shutil
import subprocess
import sys


def paths(workspace: Path | None = None) -> dict[str, Path]:
    if workspace is not None:
        base = workspace.resolve()
        mapping = {name: base / name for name in ('Kontexte','Kompose','ekole','Kamel','Kor','Orgo_Worlds','Konnaxion')}
    else:
        mycode = Path('C:/mycode')
        mapping = {
            'Kontexte': mycode / 'Ekole/Kontexte',
            'Kompose': mycode / 'Ekole/Kompose',
            'ekole': mycode / 'Ekole/ekole',
            'Kamel': mycode / 'Kamel/Kamel',
            'Kor': mycode / 'Kor/kor',
            'Orgo_Worlds': mycode / 'Orgo/Orgo_Worlds',
            'Konnaxion': mycode / 'Konnaxion/Konnaxion',
        }
    return mapping


def main(argv=None) -> int:
    parser=argparse.ArgumentParser(description='Contrôles locaux : aucune admission dans Orgo')
    parser.add_argument('--workspace',type=Path,help='Dépôts extraits côte à côte')
    args=parser.parse_args(argv)
    roots=paths(args.workspace)
    results=[]
    py=sys.executable

    def run(label,repo,command,*,cwd=None,pythonpath=False,optional=False):
        root=roots[repo]
        if not root.is_dir():
            status='NON QUALIFIÉ' if optional else 'ÉCHEC'
            print(f'[{status}] {label} : dépôt absent {root}',flush=True)
            results.append((label,status))
            return
        env=os.environ.copy()
        if pythonpath:
            env['PYTHONPATH']=str(root/'src')+os.pathsep+env.get('PYTHONPATH','')
        print(f'\n[TEST] {label}',flush=True)
        try:
            proc=subprocess.run(command,cwd=cwd or root,env=env,timeout=180)
            status='OK' if proc.returncode==0 else 'ÉCHEC'
        except (FileNotFoundError,subprocess.TimeoutExpired) as exc:
            status='NON QUALIFIÉ' if optional else 'ÉCHEC'
            print(f'[{status}] {exc}',flush=True)
        print(f'[{status}] {label}',flush=True)
        results.append((label,status))

    run('Kontexte : missions et cartes','Kontexte',[py,'-m','pytest','-q'],pythonpath=True)
    run('Kompose : propositions de rôles','Kompose',[py,'-m','pytest','-q','tests'],pythonpath=True)
    run('Ékole : ledger','ekole',[py,'-m','unittest','discover','-s','tests','-p','test_portfolio_ledger.py'])
    run('Ékole : préparation avec le vrai dépôt Kamel','ekole',[py,'-m','unittest','discover','-s','tests','-p','test_preparer_mission_collaborative.py'])
    run('Kamel : génération des cartes','Kamel',[py,'-m','unittest','tools.ekole.test_print_mission_cards'])
    # Le profil de projection est une unité pure. Le conftest Kor charge toute
    # l'application FastAPI et PyJWT, non requis pour CE test isolé.
    run('Kor : profil Kidaxion isolé','Kor',[py,'-m','pytest','-q','--noconftest','tests/test_kidaxion_profile.py'],pythonpath=True)
    run('Orgo_Worlds : six packs de revue','Orgo_Worlds',[py,'-m','unittest','-v','test_generate_review_worlds.py'],cwd=roots['Orgo_Worlds']/'tools/ekole')
    if shutil.which('node'):
        run('Konnaxion : intentions Kidaxion','Konnaxion',['node','--test','frontend/lib/__tests__/kidaxion-intents.node.test.mjs'],optional=True)
    else:
        print('[NON QUALIFIÉ] Konnaxion : Node.js absent',flush=True)
        results.append(('Konnaxion : intentions Kidaxion','NON QUALIFIÉ'))
    # La présence du paquet se contrôle sans lancer un sous-processus importateur.
    # Cela évite que la vérification des dépendances bloque les tests locaux.
    if importlib.util.find_spec('jwt') is None:
        print('\n[ENVIRONNEMENT] PyJWT absent du Python de ce contrôle. '
              'Le profil Kor isolé peut passer; le serveur Kor complet reste NON QUALIFIÉ.',flush=True)
        print('[INSTALLATION CONSEILLÉE] Dans un venv Kor : python -m pip install -e .',flush=True)
    else:
        print('\n[ENVIRONNEMENT] PyJWT détecté dans cet interpréteur (cela ne garantit pas le serveur Kor complet).',flush=True)
    good=sum(status=='OK' for _,status in results)
    fail=sum(status=='ÉCHEC' for _,status in results)
    nq=sum(status=='NON QUALIFIÉ' for _,status in results)
    print(f'\n[BILAN] {good} vérifications réussies, {fail} échec(s), {nq} non qualifiée(s).',flush=True)
    print('[LIMITE] Aucun World réel, aucune autorisation enseignant, aucun élève ou portfolio publié.',flush=True)
    return 2 if fail else (3 if nq else 0)


if __name__=='__main__':
    raise SystemExit(main())
