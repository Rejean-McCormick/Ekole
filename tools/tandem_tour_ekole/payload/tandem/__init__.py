"""Prévisualisation Ekole/Orgo locale, synthétique, sans rôle d'orchestrateur."""
from .projection import load_synthetic_preview, validate_synthetic_preview, PreviewError
__all__ = ["load_synthetic_preview", "validate_synthetic_preview", "PreviewError"]
