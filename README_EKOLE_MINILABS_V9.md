# Ekole v9 — Bibliothèque de petits environnements

**Overlay cumulatif par rapport à la v8.** À extraire au root du repo Ekole avec les mêmes dossiers `site/`, `enseignant-app/`, `tools/`, `docs/`, `tests/`, `visuels/`.

## Démarrage rapide

Depuis le repo Windows :

```powershell
py -3 tools\valider_mini_labs.py
py -3 tools\ekole.py build
py -3 tools\ekole.py preview
```

Puis ouvrir **http://127.0.0.1:8765/eleve/labo/**. Ou démarrer les trois applications avec `LANCER_EKOLE_3_APPS.bat`. Sur une fiche Élève, l'étape « Essayer » propose un accès contextuel au laboratoire.

**Ne pas publier tout `site/`** : Core peut afficher des solutions. Exécuter plutôt l'export Élève strict livré dans v8 (modifié pour v9). L'espace Enseignant reste servi localement sur un serveur distinct avec session temporaire, pas par répertoire statique public.

## Contenu

Neuf moteurs, 18 scénarios originaux vérifiés, URL directe par ID, intégration `iframe`, contrôles tactiles/clavier, rétroactions diagnostiques, indices et recommencer. Les 202 Kristals ne sont pas modifiés. Aucun QCM n'est fabriqué depuis les banques d'évaluation. Voir `docs/EKOLE_MINI_ENVIRONNEMENTS_V9.md`.

**Ce que v9 n'est pas :** une base de données de notes, une évaluation certifiée, un moteur IA de correction libre, un plugin Moodle ou un runtime Konstellation v10 publié.
