# Vérification technique — extraction à deux dépôts

Périmètre vérifié lors de la construction de cette livraison :

- **11 001 fichiers originaux présents** dans l'un des deux dépôts, vérification SHA-256 de chaque copie contre l'archive de travail original : **0 absent, 0 contenu modifié**.
- **8 noms historiques non UTF-8** normalisés pour assurer l'extraction ZIP sur d'autres systèmes. Table de correspondance dans le dépôt QC.
- **202/202 fichiers de cours** identiques aux versions archivées, empreintes dans `CONTROLE_COURS_SHA256.json`.
- **6 parcours scolaires proposés** par le fichier de données `pack.json` ; aucun cycle/année n'est codé dans le moteur actif.
- `python launcher.py --verifier` : lecture du paquet voisin et validation des références réussies.
- `python launcher.py --contenu none --verifier` : moteur vide fonctionnel.
- Six tests automatisés : accès HTTP au portail, chargement des modules, session enseignant, interdiction d'édition par défaut, édition avec sauvegarde sur corpus de test, refus des révisions obsolètes, validation de chemin et intégrité des fichiers d'origine.
- Vérification syntaxique JavaScript (`node --check`) et Python (`py_compile`) réalisée.

**Limite :** l'environnement de test a empêché la navigation automatisée dans Chromium vers le serveur local. Les pages n'ont donc pas fait l'objet d'une recette visuelle par navigateur ici; seuls leurs fichiers statiques et leurs endpoints HTTP sont validés. Les anciens modules actifs du prototype original n'ont pas été rebranchés automatiquement : voir `MIGRATION.md`.
