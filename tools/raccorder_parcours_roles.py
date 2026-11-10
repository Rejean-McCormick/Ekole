"""Brancher les parcours par rôle à une copie Ekole v7 déjà appliquée."""
from pathlib import Path
import argparse
import os
from tempfile import NamedTemporaryFile


EDITS = {
    'activite_locale.py': [
        (
            '        self.worlds = None\n',
            '''        self.role_paths = None
        if self.univers and self.banks and content and (content / 'data/parcours-roles.json').is_file():
            from parcours_roles import RolePaths
            self.role_paths = RolePaths(content, self.univers, self.banks)
''',
        ),
    ],
    'launcher.py': [
        (
            '            # Catalogue facultatif séparé des images',
            '''            role_paths = env.activity_catalogue.role_paths if env.activity_catalogue else None
            if role_paths and (route == '/api/parcours-roles.json' or route.startswith('/api/parcours-roles/')):
                try:
                    if route == '/api/parcours-roles.json':
                        return self.json(200, role_paths.listing(teacher))
                    detail = re.fullmatch(r'/api/parcours-roles/([a-z0-9-]+)/([a-z0-9-]+)\\.json', route)
                    if detail and not teacher:
                        return self.json(200, role_paths.detail(*detail.groups()))
                    return self.json(404, {'error': 'Mission indisponible.'})
                except KeyError:
                    return self.json(404, {'error': 'Univers ou rôle indisponible.'})
                except sqlite3.Error:
                    return self.json(503, {'error': 'Stockage local indisponible.'})
''',
        ),
        (
            "            bank_route = re.fullmatch(r'/api/banques-locales/(start|review|withdraw)',",
            '''            role_paths = env.activity_catalogue.role_paths if env.activity_catalogue else None
            role_route = re.fullmatch(r'/api/parcours-roles/(pratique|banque)', urllib.parse.urlsplit(self.path).path)
            if role_paths and role_route:
                if teacher:
                    return self.json(403, {'error': 'Ouvre cette mission dans l’espace Élève.'})
                try:
                    return self.json(200, role_paths.start(role_route[1], self.local_json(512)))
                except KeyError:
                    return self.json(404, {'error': 'Univers ou rôle indisponible.'})
                except RequestError as exc:
                    return self.json(exc.status, {'error': str(exc)})
                except (ValueError, TypeError) as exc:
                    return self.json(422, {'error': str(exc)})
                except sqlite3.Error:
                    return self.json(503, {'error': 'Stockage local indisponible.'})
''',
        ),
    ],
    'site/eleve/index.html': [
        ('<script src="/app.js" defer>', '<script src="/parcours-roles.js" defer></script>'),
    ],
    'site/app.js': [
        (
            " if(current().get('page')!=='parcours')a(box,'Choisir aussi un compagnon',{page:'parcours'});",
            " a(box,'Jouer un rôle dans cet univers',{page:'parcours-roles',univers:theme.id},'button-link');\n",
        ),
        (
            " else if(q.get('page')==='missions')",
            " else if(q.get('page')==='parcours-roles'&&window.EkoleParcoursRoles){await window.EkoleParcoursRoles.render(root);}\n",
        ),
    ],
    'enseignant-app/index.html': [
        ('<script src="/app.js" defer>', '<script src="/parcours-roles.js" defer></script>\n'),
    ],
    'enseignant-app/univers.js': [
        (
            ' await update();',
            ' if (window.EkoleRolesEnseignant) await window.EkoleRolesEnseignant(root, {make, json});\n',
        ),
    ],
    'enseignant-app/app.js': [
        (
            "    for(const c of [...state.pack.cours]",
            "    if(state.cfg.banques_questions&&new URLSearchParams(location.search).has('banque_role'))state.section='banks';\n",
        ),
    ],
}


def patched(root):
    changes = {}
    for relative, edits in EDITS.items():
        path = root / relative
        raw = path.read_bytes()
        newline = '\r\n' if b'\r\n' in raw else '\n'
        encoding = 'utf-8-sig' if raw.startswith(b'\xef\xbb\xbf') else 'utf-8'
        text = raw.decode(encoding).replace('\r\n', '\n')
        for anchor, addition in edits:
            combined = addition + anchor
            if combined in text:
                continue
            if text.count(anchor) != 1:
                raise ValueError(f'Point de raccord introuvable ou ambigu dans {path}. Vérifie la copie v7.')
            text = text.replace(anchor, combined, 1)
        output = text.replace('\n', newline).encode(encoding)
        if raw != output:
            changes[path] = output

    path = root / 'enseignant-app/activites-locales.js'
    raw = path.read_bytes()
    text = raw.decode('utf-8')
    newline = '\r\n' if '\r\n' in text else '\n'
    text = text.replace('\r\n', '\n')
    needle = '  if (overview.some(row => row.cours === courseId)) select.value = courseId;'
    replacement = """  const roleLink = new URLSearchParams(location.search);
  const requestedBank = roleLink.get('banque_role') || courseId;
  if (overview.some(row => row.cours === requestedBank)) select.value = requestedBank;"""
    initial = '  if (overview.length) await load();'
    initial_replacement = "  if (overview.length) await load(roleLink.get('question_role'));"
    if replacement not in text or initial_replacement not in text:
        if text.count(needle) != 1 or text.count(initial) != 1:
            raise ValueError(f'Point de raccord de la banque introuvable dans {path}.')
        text = text.replace(needle, replacement).replace(initial, initial_replacement)
        changes[path] = text.replace('\n', newline).encode('utf-8')
    return changes


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--verifier', action='store_true', help='Contrôler les raccords sans écrire')
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    if not (root / 'univers.py').is_file() or not (root / 'enseignant-app/univers.js').is_file():
        parser.exit(1, 'Applique d’abord l’overlay v7 dans C:\\mycode, puis relance ce raccord.\n')
    try:
        changes = patched(root)
        for path, data in changes.items():
            if not args.verifier:
                with NamedTemporaryFile(dir=path.parent, delete=False) as output:
                    output.write(data)
                try:
                    os.chmod(output.name, path.stat().st_mode & 0o777)
                    os.replace(output.name, path)
                finally:
                    Path(output.name).unlink(missing_ok=True)
        print(f'{len(changes)} fichiers à raccorder.' if args.verifier else
              f'{len(changes)} fichiers raccordés. Tu peux relancer Ekole.')
    except (ValueError, OSError, UnicodeError) as exc:
        parser.exit(1, f'{exc}\n')


if __name__ == '__main__':
    main()
