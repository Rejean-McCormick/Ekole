#!/usr/bin/env python3
"""Ajoute de *vraies* sections aux guides source, explicitement, avec SHA et sauvegardes.
Mode par défaut = lecture seule. Aucun changement si la source est personnalisée.
"""
from __future__ import annotations
import argparse,json,hashlib,pathlib,shutil
ROOT=pathlib.Path(__file__).resolve().parents[1]
MARK='<!-- EKOLE_V11_ENRICHISSEMENT_SOURCE_MANUEL_A_REVOIR -->'
DOCS={'contenu/03_ENSEIGNEMENT_GUIDE.md':'experience/ANNEXE_GUIDE_v11.md',
      'contenu/04_PRATIQUE_ACCOMPAGNEE.md':'experience/ANNEXE_PRATIQUE_v11.md'}
def apply(root,do_apply=False):
 root=pathlib.Path(root).resolve(); expected=json.loads((root/'livraison/EMPREINTES_SOURCES_GUIDES_v11.json').read_text(encoding='utf8'))
 counts={'deja_applique':0,'compatibles':0,'ajoutes':0,'absents':0,'personnalises_ignores':0}
 for kid,hashes in sorted(expected.items()):
  for doc,extension in DOCS.items():
   target=root/'kristals'/kid/doc;append=root/'kristals'/kid/extension
   if not target.is_file() or not append.is_file():counts['absents']+=1;continue
   if target.is_symlink() or append.is_symlink():raise ValueError('Lien symbolique non accepté : '+str(target))
   raw=target.read_bytes()
   if MARK.encode() in raw:counts['deja_applique']+=1;continue
   if hashlib.sha256(raw).hexdigest()!=hashes[doc]:
    print('PERSONNALISE, ignoré (fusion manuelle) :',target.relative_to(root))
    counts['personnalises_ignores']+=1;continue
   counts['compatibles']+=1
   if not do_apply:continue
   backup=root/'sauvegardes_ekole_v11'/kid/doc
   if backup.exists():raise FileExistsError('Sauvegarde déjà présente : '+str(backup))
   backup.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(target,backup)
   text=raw.decode('utf8').rstrip()+f'\n\n---\n\n{MARK}\n\n'+append.read_text(encoding='utf8')+'\n'
   target.write_text(text,encoding='utf8');counts['ajoutes']+=1
 print(('APPLICATION' if do_apply else 'SIMULATION')+':',counts)
 return counts
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--root',type=pathlib.Path,default=ROOT);p.add_argument('--apply',action='store_true')
 x=p.parse_args();apply(x.root,x.apply)
