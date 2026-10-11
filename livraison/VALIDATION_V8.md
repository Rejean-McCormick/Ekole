# Validation réelle — Ekole v8

- Base de test: archive actualisée `moodle.zip` + cumul v7/v8.
- 202 cours sources indexés, 202 fiches Élève, six ateliers pilotes, 17 prompts additionnels.
- 9 tests Python v8 réussis; 7 tests historiques v7 réussis.
- Contrôles Node (`--check` et tests de calcul déterministe) réussis.
- Export Élève par liste blanche vérifié; réponses des cours non accessibles sur le serveur Élève.
- Le serveur Enseignant refuse un accès non authentifié à la nouvelle ressource.
- Aucun fichier `moodle/`, `opsconsole/`, `catalogue/` ou `site/data/cours/` existant n’a changé pendant la fusion d’essai.
- Limitations: tentative Playwright/Chromium bloquée par la politique réseau de cet environnement (`ERR_BLOCKED_BY_ADMINISTRATOR`) : aucun test visuel réussi; aucun test Moodle réel; aucune image générée; Konstellation v10 non raccordé; classement scolaire non qualifié.
