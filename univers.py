"""Catalogue des univers et choix de diffusion de l’enseignant."""
from html import escape
import json
import re

from visuals import MIMES, image_info

STYLES = {
    'ekole': ('Ekole', 'Couleurs naturelles et contrastes nets.'),
    'pastel': ('Pastel', 'Aplats pastel, contours foncés et fond clair sans texte.'),
    'ardoise': ('Ardoise', 'Bleu ardoise, blancs chauds et contrastes nets.'),
    'vif': ('Couleurs vives', 'Couleurs franches, avec peu d’éléments par plan.'),
}
SPEK_COLOURS = {'pastel': ('#694782', '#f0e5f8'), 'ardoise': ('#36576e', '#e4edf3'),
                'vif': ('#9a3f16', '#ffebda')}
FAMILIES = dict.fromkeys(('fr', 'als', 'ale', 'fls', 'ilss'), 'langues')
FAMILIES.update(dict.fromkeys(('ad', 'ap', 'da', 'mu'), 'arts'))
FAMILIES.update({'ma': 'ma', 'st': 'st', 'ccq': 'societe', 'us': 'societe', 'eps': 'eps'})
ID = re.compile(r'[a-z][a-z0-9-]{1,50}')


class Univers:
    def __init__(self, catalogue, data, variants, pages, courses, store):
        self.store = store
        self.courses = courses
        self.catalogue = catalogue
        self.themes = {}
        scenarios = {row['id']: row for row in catalogue.scenarios}
        for row in data['themes']:
            key = row['id']
            if (not ID.fullmatch(key) or key in self.themes or row['scenario'] not in scenarios
                    or set(row['frames']) != set(FAMILIES.values())):
                raise ValueError('Univers incomplet ou dupliqué')
            self.themes[key] = row
        if data['format'] != 'ekole.univers/1' or set(variants) - self.themes.keys():
            raise ValueError('Catalogue des univers incompatible')
        self.variants = variants
        self.pages = pages
        if pages and (set(pages) != set(self.themes) or any(set(rows) != set(courses) for rows in pages.values())):
            raise ValueError('Couverture Spek des univers incomplète')
        if store:
            with store.connect() as db:
                db.executescript("""
                    CREATE TABLE IF NOT EXISTS ekole_universe_profile (
                        id INTEGER PRIMARY KEY CHECK (id = 1), choices TEXT NOT NULL,
                        default_theme TEXT NOT NULL, style TEXT NOT NULL);
                    CREATE TABLE IF NOT EXISTS ekole_universe_images (
                        theme TEXT NOT NULL, style TEXT NOT NULL, alt TEXT NOT NULL,
                        mime TEXT NOT NULL, image BLOB NOT NULL, PRIMARY KEY (theme, style));
                """)

    def profile(self):
        with self.store.connect() as db:
            row = db.execute('SELECT choices, default_theme, style FROM ekole_universe_profile WHERE id=1').fetchone()
        if row is None:
            return {'choices': [], 'default': '', 'style': 'ekole'}
        choices = [key for key in json.loads(row['choices']) if key in self.themes]
        default = row['default_theme']
        return {'choices': choices, 'default': default if default in choices else (choices[0] if choices else ''),
                'style': row['style'] if row['style'] in STYLES else 'ekole'}

    def publish(self, data):
        choices, default, style = data.get('choices'), data.get('default'), data.get('style')
        if (not isinstance(choices, list) or any(not isinstance(key, str) or key not in self.themes for key in choices)
                or len(set(choices)) != len(choices) or not isinstance(style, str) or style not in STYLES
                or not isinstance(default, str) or (default not in choices if choices else default != '')):
            raise ValueError('Choisis un thème de départ parmi les thèmes proposés et un style valide.')
        with self.store.connect() as db:
            db.execute('INSERT OR REPLACE INTO ekole_universe_profile VALUES (1, ?, ?, ?)',
                       (json.dumps(choices), default, style))
        return self.profile()

    def listing(self, teacher=False):
        profile = self.profile()
        keys = self.themes if teacher else profile['choices']
        rows = [{field: self.themes[key][field] for field in ('id', 'name', 'intro', 'companion')} for key in keys]
        result = {**profile, 'themes': rows}
        if teacher:
            result['styles'] = [{'id': key, 'name': name, 'prompt': prompt}
                                for key, (name, prompt) in STYLES.items()]
        return result

    def describe(self, key, course=None, teacher=False):
        profile = self.profile()
        if key not in self.themes or (not teacher and key not in profile['choices']):
            raise KeyError(key)
        if course is not None and course not in self.courses:
            raise KeyError(course)
        theme = self.themes[key]
        result = {field: theme[field] for field in ('id', 'name', 'intro', 'companion')}
        result['style'] = profile['style']
        with self.store.connect() as db:
            image = db.execute('SELECT alt FROM ekole_universe_images WHERE theme=? AND style=?',
                               (key, profile['style'])).fetchone()
        if image:
            result['image'] = {'url': f'/api/univers/image/{key}/{profile["style"]}', 'alt': image['alt']}
        if course:
            family = FAMILIES.get(course.split('-')[2])
            result['frame'] = theme['frames'].get(family, theme['intro'])
            result['activity'] = self.variants.get(key, {}).get(course)
            if course in self.pages.get(key, {}):
                result['spek'] = f'/univers-spek/{key}/{course}/fr/index.html'
        if teacher:
            result['frames'] = theme['frames']
        return result

    def spek(self, key, course, name):
        detail = self.describe(key, course)
        ref = self.pages[key][course][name]
        body = self.catalogue.resource(ref, ('univers-spek', key, course, 'fr', name))
        if name == 'document.json':
            return body
        return self.decorate(body, detail, course)

    def decorate(self, body, detail, course=None):
        colours = SPEK_COLOURS.get(detail['style'])
        if colours:
            accent, soft = colours
            css = f'<style>:root{{--accent:{accent};--soft:{soft}}}</style>'
            body = body.replace(b'</head>', css.encode() + b'</head>', 1)
        pieces = []
        if course:
            href = '/eleve/?cours=' + escape(course, quote=True)
            pieces.append(f'<p><a href="{href}">Retour au cours Ekole</a></p>')
        if image := detail.get('image'):
            url, alt = (escape(image[key], quote=True) for key in ('url', 'alt'))
            pieces.append(f'<p><img src="{url}" alt="{alt}" style="max-width:100%;max-height:300px"></p>')
        return body.replace(b'<main class="wrapper">', b'<main class="wrapper">' + ''.join(pieces).encode(), 1)

    def save_image(self, key, style, alt, raw):
        if (key not in self.themes or style not in STYLES or not isinstance(alt, str)
                or not 1 <= len(alt.strip()) <= 240 or not 30 <= len(raw) <= 600_000):
            raise ValueError('Image, description ou style invalide (600 ko maximum).')
        fmt, width, height = image_info(raw)
        if width > 4096 or height > 4096:
            raise ValueError('Dimensions de l’image invalides.')
        with self.store.connect() as db:
            db.execute('INSERT OR REPLACE INTO ekole_universe_images VALUES (?, ?, ?, ?, ?)',
                       (key, style, alt.strip(), MIMES[fmt], raw))

    def image(self, key, style):
        profile = self.profile()
        if key not in profile['choices'] or style != profile['style']:
            raise KeyError(key)
        with self.store.connect() as db:
            row = db.execute('SELECT mime, image FROM ekole_universe_images WHERE theme=? AND style=?',
                             (key, style)).fetchone()
        if row is None:
            raise KeyError(key)
        return row['mime'], row['image']
