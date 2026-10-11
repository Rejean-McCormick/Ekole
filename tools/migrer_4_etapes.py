#!/usr/bin/env python3
"""Migration Ekole v3 18 -> v4 24 positions; non destructive; --apply explicit."""
from pathlib import Path
import argparse,json,datetime,shutil,sys,tempfile,os

def migrate(path,apply=False):
    path=Path(path)
    if not path.exists():
        print('Aucun fichier d’affectations propre à ce dépôt : l’exemple 24 étapes livré sera utilisé par le navigateur. Rien à migrer.')
        return True
    original=path.read_bytes(); data=json.loads(original.decode('utf-8-sig'))
    groups=data.get('cours_par_etape')
    if not isinstance(groups,dict):raise ValueError('cours_par_etape doit être un objet')
    expected={f'annee-{y}-etape-{s}' for y in range(1,7) for s in range(1,5)}
    unexpected=set(groups)-expected
    if unexpected:raise ValueError('Clés inconnues : '+', '.join(sorted(unexpected)))
    missing=expected-set(groups)
    if any(not k.endswith('-etape-4') for k in missing):raise ValueError('Clés manquantes autres que les étapes 4: migration refusée')
    if not missing:
        print('Déjà au format 24 clés : rien à modifier.');return True
    print('Clés à ajouter:',', '.join(sorted(missing)), '\nCours et preuves existants préservés.')
    if not apply:
        print('DRY-RUN seulement. Relancer avec --apply pour enregistrer et créer une sauvegarde.')
        return True
    backup=path.with_name(path.name+'.bak-'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ'))
    shutil.copy2(path,backup)
    for key in missing:groups[key]=[]
    groups_ordered={k:groups[k] for k in sorted(groups, key=lambda key:(int(key.split('-')[1]),int(key.split('-')[3])))}
    data['cours_par_etape']=groups_ordered
    data['format']='ekole.parcours-affectations/0.3'
    data.setdefault('preuves_attribution',{})
    body=(json.dumps(data,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
    tmp=path.with_name(path.name+'.tmp')
    try:
        tmp.write_bytes(body);tmp.replace(path)
    finally:
        if tmp.exists():tmp.unlink()
    print('Migration réalisée. Sauvegarde:',backup.name)
    return True
if __name__=='__main__':
    pa=argparse.ArgumentParser();pa.add_argument('--root',default=str(Path(__file__).resolve().parents[1]));pa.add_argument('--apply',action='store_true');args=pa.parse_args()
    migrate(Path(args.root)/'site/data/parcours-affectations.json',args.apply)
