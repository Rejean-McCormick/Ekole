#!/usr/bin/env python3
"""Rebuild & copy child catalogue to site/eleve; validate visual intents; no deletion or model calls."""
from __future__ import annotations
import argparse, pathlib, subprocess, sys, json, shutil
ROOT=pathlib.Path(__file__).resolve().parents[1]
def sync(root):
 root=pathlib.Path(root).resolve()
 proc=subprocess.run([sys.executable,str(root/'tools/construire_vue_enfant.py'),'--root',str(root)],capture_output=True,text=True)
 if proc.returncode:raise RuntimeError('Construction élève échouée: '+proc.stderr)
 src=root/'site/data/eleves/catalogue.json'
 if len(json.loads(src.read_text(encoding='utf-8'))['courses'])!=202:raise ValueError('Catalogue incomplet')
 dest=root/'site/eleve/data/eleves/catalogue.json';dest.parent.mkdir(parents=True,exist_ok=True)
 shutil.copyfile(src,dest)
 if not (root/'site/eleve/data/visuels_public.json').is_file():raise FileNotFoundError('Emplacements publics absents')
 registry=json.loads((root/'visuels/INTENTIONS_IMAGES.json').read_text(encoding='utf-8'))
 ids=[v['visual_id'] for v in registry['intents']]
 if len(ids)!=len(set(ids)) or len(ids)<202:raise ValueError('Identifiants visuels incomplets/dupliqués')
 # La couche conceptuelle est compilée depuis les manifests locaux des Kristals.
 from compiler_visuels_kristals import compile_layer
 visual_data=compile_layer(root)
 if visual_data['nb_cours_couverts']!=202:raise ValueError('Couche visuelle incomplète')
 from compiler_experiences_v11 import compile_experiences
 compile_experiences(root)
 from compiler_mondes_v12 import compile_mondes
 worlds=compile_mondes(root)
 if worlds['couverts']!=5 or worlds['count']!=7:raise ValueError('Micro-mondes v12 incomplets')
 print('Ekole: 202 cours projetés pour l’élève; visuels non générés:',len(ids), 'aucun accès Moodle')
 return True
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--root',default=str(ROOT));a=p.parse_args();sync(a.root)
