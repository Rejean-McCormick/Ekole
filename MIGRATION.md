# Journal du découplage Ekole

## Réalisé

- Source Ekole originale de 11 001 fichiers copiée *sans suppression*; `ekole-quebec/historique/INDEX_DEPLACEMENT.json` associe chaque chemin d'origine à sa localisation après séparation.
- Moteur Core sans référence structurelle au primaire, lecture automatique du dépôt frère.
- Espace apprenant générique (consultation de cours et parcours); fonctionne avec n'importe quel pack conforme.
- Atelier local protégé, en lecture seule par défaut, édition optionnelle des textes avec sauvegarde.
- Fichiers cours originaux dans le paquet QC, répliques identiques à ceux de l'archive historique. `CONTROLE_COURS_SHA256.json` fournit les empreintes initiales.
- Aucun accès réseau externe, aucune IA ni opération Moodle déclenchée par le launcher.

## Encore à porter (travail nécessaire, non simulé)

- Application Élève historique : modes année/étape, MiniLabs, micro-mondes, visualisations du primaire, médias et intégrations avancées.
- Atelier Enseignant historique : gestion d'images, cadres visuels, plans, retours et compilateurs spécialisés.
- OpsConsole et scripts historiques, qui présument encore 202 cours `qc-pri-...`, des années 1-6 ou des parcours scolaires.
- Projections Moodle, exports, Konstellation et API de gestion, contrôle d'accès multiutilisateur, comptes et évaluations.
- Validation juridique des licences des médias, provenance par assertion et workflow éditorial d'approbation.

Les anciens codes sources de ces fonctions sont **préservés** sous `ekole/legacy/`, tandis que leurs données et configurations historiques sont dans le dépôt QC. Ces fonctions mais **ne sont pas activées** par le nouveau lanceur. Cette réserve est délibérée : neutraliser le moteur n'autorise pas à interpréter un ancien outil spécialisé comme un module générique déjà compatible.
