"""Projection PREVIEW Ekole de missions synthétiques. Pas un contrat API Orgo.

Aucune opération réseau, aucune écriture, aucun événement sortant. Format fermé:
les identités, données scolaires, indices privés et médias sont interdits.
"""
from __future__ import annotations

import json
from pathlib import Path
import re
from uuid import UUID

MAX_BYTES = 131_072
ID = re.compile(r"[a-zA-Z0-9][a-zA-Z0-9_-]{1,63}\Z")
STATES = frozenset({"waiting", "ready", "in_progress", "done", "blocked"})
TOP_FIELDS = frozenset({"format", "mode", "authority", "tenant_id", "world_id", "world_release_id",
                        "scenario_ref", "workflow_ref", "tasks"})
TASK_FIELDS = frozenset({"task_ref", "role_code", "state", "fragment_refs"})


class PreviewError(ValueError):
    """La projection ne peut pas être présentée en toute sécurité."""


def _uuid(value, field):
    if not isinstance(value, str):
        raise PreviewError(f"{field}: UUID manquant")
    try:
        parsed = UUID(value)
    except (ValueError, AttributeError):
        raise PreviewError(f"{field}: UUID invalide") from None
    if not parsed.int or str(parsed) != value.lower():
        raise PreviewError(f"{field}: UUID non canonique")


def _id(value, field):
    if not isinstance(value, str) or not ID.fullmatch(value):
        raise PreviewError(f"{field}: identifiant invalide")


def validate_synthetic_preview(value: object) -> dict:
    if not isinstance(value, dict) or set(value) != TOP_FIELDS:
        raise PreviewError("Structure de projection inconnue ou champ sensible non prévu")
    if value["format"] != "ekole.tandem-teacher-preview/1.0":
        raise PreviewError("Format de projection non reconnu")
    if value["mode"] != "synthetic" or value["authority"] != "orgo":
        raise PreviewError("Seul l'aperçu synthétique, sous autorité opérationnelle Orgo, est permis")
    for field in ("tenant_id", "world_id", "world_release_id"):
        _uuid(value[field], field)
    for field in ("scenario_ref", "workflow_ref"):
        _id(value[field], field)
    tasks = value["tasks"]
    if not isinstance(tasks, list) or not 1 <= len(tasks) <= 50:
        raise PreviewError("Liste de tâches invalide")
    seen = set()
    for task in tasks:
        if not isinstance(task, dict) or set(task) != TASK_FIELDS:
            raise PreviewError("Tâche invalide ou champ non autorisé (donnée personnelle?)")
        for field in ("task_ref", "role_code"):
            _id(task[field], field)
        if task["task_ref"] in seen:
            raise PreviewError("Référence de tâche dupliquée")
        seen.add(task["task_ref"])
        if not isinstance(task["state"], str) or task["state"] not in STATES:
            raise PreviewError("État de prévisualisation non reconnu")
        fragments = task["fragment_refs"]
        if not isinstance(fragments, list) or len(fragments) > 8:
            raise PreviewError("Références de fragments invalides")
        for ref in fragments:
            _id(ref, "fragment_ref")
        if len(set(fragments)) != len(fragments):
            raise PreviewError("Fragment dupliqué")
    # Retour JSON pur; aucune normalisation qui modifierait une identité ou le scope.
    return value


def load_synthetic_preview(path: str | Path) -> dict:
    p = Path(path).expanduser()
    if p.is_symlink() or not p.is_file():
        raise PreviewError("Fichier local régulier requis; liens symboliques refusés")
    if p.stat().st_size > MAX_BYTES:
        raise PreviewError("Fichier de projection trop volumineux")
    try:
        # Refus des clés dupliquées pour éviter les divergences entre validateurs.
        def pairs(items):
            obj = {}
            for key, val in items:
                if key in obj:
                    raise PreviewError("Clé JSON dupliquée")
                obj[key] = val
            return obj
        value = json.loads(p.read_text(encoding="utf-8"), object_pairs_hook=pairs)
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise PreviewError("Projection JSON non lisible") from exc
    return validate_synthetic_preview(value)
