"""Variantes de visuels publiées par Atelier Images, par thème de cours."""
import re

import visuals

THEME = re.compile(r'[a-z0-9-]{1,64}')


def image(root, cid, slot, theme):
    if not THEME.fullmatch(theme):
        return None
    path = root / 'publications' / 'visuels-themes' / theme / cid / (slot + '.webp')
    if path.is_symlink() or not path.resolve().is_relative_to(root.resolve()) or not path.is_file():
        return None
    return path


def inventory(root, cid, theme):
    entries = {v['slot']: v for v in visuals.public_inventory(root, cid)['visuels']}
    for slot, entry in visuals.entries(root, cid).items():
        if image(root, cid, slot, theme):
            entries[slot] = {'slot': slot, 'placement': entry.get('placement', ''),
                             'alt': entry.get('texte_alternatif') or 'Illustration de la leçon',
                             'url': f'/api/media/{cid}/{slot}?theme={theme}'}
    return {'cours_id': cid, 'visuels': list(entries.values())}
