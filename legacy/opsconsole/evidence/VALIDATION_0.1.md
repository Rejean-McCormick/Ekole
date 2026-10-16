# Validation Ekole OpsConsole 0.1 — 2026-10-09

## Tests exécutés sur une copie du pack Ekole

- Test de syntaxe Python avec `py_compile` : réussi.
- Test de syntaxe JavaScript avec `node --check` : réussi.
- `ekole_ops.py --check` : réussi, neuf chemins essentiels présents.
- `python -m unittest discover` : **11 tests réussis** (inspection des 202, intégrité du détail d'un Kristal, HTTP local, jeton CSRF, refus des actions arbitraires, destinations refusées, refus d'appliquer sans simulation, export public).
- Commandes réelles `tools/ekole.py verify`, `build`, `moodle-plan`, `pages-zip` : toutes exécutées avec succès sur la copie.
- Prévisualisation : serveur local démarré puis arrêté dans la copie.
- Déploiement : simulation vers un répertoire temporaire externe; confirmation erronée rejetée; application de copie autorisée réussie sur ce répertoire temporaire.
- Vérification de la structure ZIP : à réaliser à la création de l'archive finale (voir contrôles de sortie).

## Limites

- Pas de test d'intégration réel à Moodle, GitHub, SemantiK, Konstellation ou la Médiathèque.
- Essai visuel Chromium bloqué par les restrictions d'accès locales du conteneur; l'interface n'a **pas** été validée visuellement en navigateur dans cet environnement.
- Lancement Windows (`.bat`, PowerShell) non exécuté en environnement Windows; vérification manuelle sur Windows recommandée.
- Aucun état Kristal v9/v10 n'a été créé ni publié par cet outil.
