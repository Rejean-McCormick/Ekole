"""Read-only V12 practice projected from the existing micro-world definitions."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
from threading import BoundedSemaphore

ROOT = Path(__file__).resolve().parent / 'legacy/site/eleve/mondes-v12'
ASSETS = {'index.html': 'text/html', 'app.js': 'text/javascript',
          'engine.js': 'text/javascript', 'style.css': 'text/css'}


class MicroWorlds:
    def __init__(self, data, courses):
        self.items = {item['id']: item for item in data}
        if len(self.items) != len(data) or any(item['kristal_id'] not in courses for item in data):
            raise ValueError('Micro-monde dupliqué ou cours inconnu')
        self.catalogue = [student_world(item) for item in data]
        self.node = shutil.which('node')
        self.slots = BoundedSemaphore(4)

    def evaluate(self, data):
        if set(data) != {'id', 'state'} or not isinstance(data['id'], str) or data['id'] not in self.items:
            raise ValueError('Micro-monde inconnu')
        if not self.node:
            raise OSError('Node indisponible')
        if not self.slots.acquire(blocking=False):
            raise OSError('Trop de vérifications simultanées')
        try:
            result = subprocess.run([self.node, str(ROOT / 'verifier-etat.cjs')], check=True, capture_output=True,
                                    encoding='utf-8', timeout=4,
                                    input=json.dumps({'spec': self.items[data['id']], 'state': data['state']}))
            return json.loads(result.stdout)
        except subprocess.CalledProcessError as exc:
            raise ValueError('État de manipulation invalide') from exc
        except subprocess.TimeoutExpired as exc:
            raise OSError('Vérification trop longue') from exc
        finally:
            self.slots.release()


def student_world(item):
    view = {key: item[key] for key in ('id', 'kristal_id', 'type', 'title', 'instruction',
                                      'evaluation', 'source_review')}
    parameters = item['parameters']
    kind = item['type']
    visible = {
        'representations': ('parts', 'group_size'),
        'repartition': ('total', 'bins'),
        'expression': ('gestures', 'intention'),
    }
    if kind == 'causalite':
        # The source array may be in narrative order. Shuffle for presentation.
        events = sorted(parameters['events'], key=lambda event:
                        hashlib.sha256((item['id'] + ':' + event['id']).encode()).digest())
        if [event['id'] for event in reversed(events)] == parameters['order']:
            events = events[1:] + events[:1]
        view['parameters'] = {
            'events': [{key: event[key] for key in ('id', 'text')} for event in events],
            'links': [{key: link[key] for key in ('from', 'to', 'statement')} for link in parameters['links']],
        }
    elif kind == 'preuves':
        view['parameters'] = {'statements': [{key: row[key] for key in ('id', 'text')}
                                             for row in parameters['statements']]}
    else:
        view['parameters'] = {key: parameters[key] for key in visible[kind]}
    return view
