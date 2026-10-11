# Ekole v8 — Overlay cumulatif Core / Élève / Enseignant

**À extraire directement à la racine du repo Ekole qui contient `site/`, `tools/`, `catalogue/`, `moodle/` et `opsconsole/`.** Cette archive inclut tous les fichiers de l'overlay v7, puis les améliorations v8; elle ne réinstalle pas le contenu canonique des 202 cours.

## Départ Windows

```powershell
cd "C:\mycode\Ekole"
py -3 tools\synchroniser_ekole_apps.py --root .
py -3 tools\ekole.py preview
# Autre console :
py -3 tools\serve_enseignant.py --open
```

Ou double-clique sur `LANCER_EKOLE_3_APPS.bat`.

- **Ekole Core** `http://127.0.0.1:8765/` — navigation, catalogue, administration locale.
- **Ekole Élève** `http://127.0.0.1:8765/eleve/` — années, ateliers, carte, carnet de session.
- **Ekole Enseignant** `http://127.0.0.1:8766/` via le lien éphémère du lanceur — documents, planification, banque de prompts.
- **Konstellation Light** `http://127.0.0.1:4177/` (viewer local indépendant, uniquement s'il est démarré) — pas de collection v10 Ekole publiée. L'application Élève conserve un graphe local et ne montre un lien externe que si une collection v10 HTTPS vérifiée est explicitement configurée.

## Image : du prompt au fichier vérifié

```powershell
# Déposer les images futures (non incluses) sous visuels/images_a_approuver/
# Compléter un manifeste selon visuels/APPROBATION_IMAGES.exemple.json
py -3 tools\compiler_visuels_approuves_v8.py --approvals visuels\APPROBATION_IMAGES.json
# Après revues humaines et vérification du plan :
py -3 tools\compiler_visuels_approuves_v8.py --approvals visuels\APPROBATION_IMAGES.json --apply
```

Le compilateur vérifie ID, chemin, SHA-256, licences, alternative textuelle, revues, taille, format et dimensions (`Pillow` requis à l'application). Il ne génère ni ne publie d'image.

## Export du portail Élève uniquement

```powershell
py -3 tools\export_ekole_eleve_v8.py --root . --out "C:\temp\ekole-eleve-public-v8"
```

L'ancien export v7 reste dans l'archive pour compatibilité avec les tests historiques, mais **il est obsolète** pour la v8. Le nouvel export est une liste d'autorisation stricte et omet les corrigés, les modules enseignants, les prompts privés, les références locales `127.0.0.1:4177` et les fichiers `vendor`.

## Vérifications

```powershell
py -3 -m unittest discover -s tests -p "test_ekole_v8*.py" -v
node --check site\eleve\app.js
node --check site\eleve\atelier-v8.js
```

Voir `docs/EKOLE_V8_VISION_SYSTEME.md` et `livraison/VALIDATION_V8.md`.
