"""Publication locale des portraits relus dans Kolor Studio."""
import hashlib
import io
import json
import os
from pathlib import Path
import re

from personnages import MAX_BYTES, safe_file

ROLE_ID = re.compile(r'role-[a-z][a-z0-9-]{0,74}')
SHA = re.compile(r'[a-f0-9]{64}')


def export_rows(manifest):
    if manifest.is_symlink() or not manifest.is_file() or manifest.stat().st_size > 1_000_000:
        raise ValueError('Manifeste Kolor absent ou invalide.')
    data = json.loads(manifest.read_bytes())
    if not isinstance(data, dict) or data.get('format') != 'kolor.studio.export/1':
        raise ValueError('Manifeste Kolor Studio attendu.')
    records = data.get('roles')
    if not isinstance(records, list) or len(records) > 200:
        raise ValueError('Liste des rôles Kolor invalide.')
    rows = {}
    for row in records:
        if not isinstance(row, dict) or not isinstance(row.get('visual_id'), str):
            raise ValueError('Rôle Kolor invalide.')
        role = row['visual_id']
        if not ROLE_ID.fullmatch(role) or role in rows:
            raise ValueError('Rôle Kolor invalide ou dupliqué.')
        rows[role] = row
    return rows


def export_png(manifest, row):
    if row.get('statut') != 'pret':
        raise ValueError('Le portrait doit être marqué prêt dans Kolor Studio.')
    role = row['visual_id'].removeprefix('role-')
    expected = f'images/roles/{role}.png'
    if row.get('chemin') != expected:
        raise ValueError('Chemin canonique du rôle attendu.')
    image = safe_file(manifest.parent, expected)
    if not image.is_file() or not 33 <= image.stat().st_size <= MAX_BYTES:
        raise ValueError('PNG absent ou taille invalide.')
    with image.open('rb') as stream:
        raw = stream.read(MAX_BYTES + 1)
    if not 33 <= len(raw) <= MAX_BYTES or raw[:16] != b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR':
        raise ValueError('Portrait PNG invalide.')
    if int.from_bytes(raw[16:20], 'big') != 512 or int.from_bytes(raw[20:24], 'big') != 512:
        raise ValueError('Portrait PNG de 512 × 512 requis.')
    return raw


def verify_png(raw):
    try:
        from PIL import Image
    except ImportError as exc:
        raise ValueError('Installe Pillow dans le Python qui lance Ekole pour publier les portraits.') from exc
    try:
        with Image.open(io.BytesIO(raw)) as png:
            if png.format != 'PNG' or png.size != (512, 512):
                raise ValueError('Portrait PNG de 512 × 512 requis.')
            png.verify()
        with Image.open(io.BytesIO(raw)) as png:
            png.load()
    except (OSError, SyntaxError) as exc:
        raise ValueError('Portrait PNG illisible.') from exc


class KolorRoles:
    def __init__(self, content, inventory, store):
        self.manifest = Path(os.environ.get('EKOLE_KOLOR_EXPORTS')
                             or content.parent / 'Kolor/projet/exports') / 'manifest.json'
        self.roles = {asset['id']: asset['alt'] for asset in inventory['assets'] if asset['type'] == 'role'}
        self.store = store
        with store.connect() as db:
            db.execute("""CREATE TABLE IF NOT EXISTS ekole_kolor_roles (
                role TEXT PRIMARY KEY, sha256 TEXT NOT NULL, image BLOB NOT NULL)""")

    def published(self):
        with self.store.connect() as db:
            return {row['role']: row['sha256'] for row in db.execute('SELECT role, sha256 FROM ekole_kolor_roles')
                    if row['role'] in self.roles}

    def listing(self):
        published = self.published()
        try:
            rows = export_rows(self.manifest)
            message = ''
        except (OSError, ValueError):
            rows = {}
            message = 'Aucun manifeste Kolor Studio lisible. Exporte les rôles dans Kolor Studio.'
        result = []
        for role, alt in self.roles.items():
            row = rows.get(role)
            entry = {'id': role, 'name': alt, 'published': published.get(role)}
            if row is None:
                entry['state'] = 'absent'
            elif row.get('statut') != 'pret':
                entry['state'] = 'a_verifier'
            else:
                try:
                    raw = export_png(self.manifest, row)
                    entry.update(state='pret', candidate=hashlib.sha256(raw).hexdigest())
                except (OSError, ValueError):
                    entry['state'] = 'png_indisponible'
            result.append(entry)
        return {'roles': result, 'message': message}

    def candidate(self, role, expected, rows=None):
        if not isinstance(expected, str) or not SHA.fullmatch(expected) or role not in self.roles:
            raise ValueError('Portrait ou empreinte invalide.')
        if rows is None:
            rows = export_rows(self.manifest)
        raw = export_png(self.manifest, rows.get(role, {}))
        if hashlib.sha256(raw).hexdigest() != expected:
            raise ValueError('Portrait modifié dans Kolor Studio. Actualise la liste.')
        return raw

    def publish(self, selection):
        if not isinstance(selection, dict) or not 1 <= len(selection) <= len(self.roles):
            raise ValueError('Choisis les portraits à publier.')
        rows = export_rows(self.manifest)
        with self.store.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            total = 0
            for role, expected in selection.items():
                raw = self.candidate(role, expected, rows)
                total += len(raw)
                if total > 48 * 1024 * 1024:
                    raise ValueError('Lot trop volumineux. Publie en plusieurs lots.')
                verify_png(raw)
                db.execute('INSERT OR REPLACE INTO ekole_kolor_roles VALUES (?,?,?)', (role, expected, raw))
        return {'published': len(selection)}

    def withdraw(self, role, expected):
        if not isinstance(role, str) or role not in self.roles or not isinstance(expected, str):
            raise ValueError('Portrait publié requis.')
        with self.store.connect() as db:
            result = db.execute('DELETE FROM ekole_kolor_roles WHERE role=? AND sha256=?', (role, expected))
            if result.rowcount != 1:
                raise ValueError('Portrait modifié. Actualise la liste.')
        return {'withdrawn': role}

    def image(self, role):
        if role not in self.roles:
            return None
        with self.store.connect() as db:
            row = db.execute('SELECT image FROM ekole_kolor_roles WHERE role=?', (role,)).fetchone()
        return row['image'] if row else None
