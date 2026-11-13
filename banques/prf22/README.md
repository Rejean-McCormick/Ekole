# Ékole · Banque de situations PRF-22

- `candidats-v0_4/` : lot initial versionné, 137 propositions, historique conservé, **ne pas écraser**.
- `candidats-v0_6/` : lot enrichi versionné, 137 propositions avec références des patrons Ékole et des exercices Kontexte distinctes.
- `activites-proposees-v0_6.json` : répertoire indépendant de patrons d'activités *auteur Ékole*, non homologués.
- `generations/` : nouvelles générations en lecture/écriture locale, ignorées par Git.
- `revisions-local/` : révisions pédagogiques locales, ignorées par Git, non publiées.

Utiliser `VERIFIER_BANQUE_PRF22.cmd` pour le lot ancien et `VERIFIER_BANQUE_ENRICHIE_PRF22.cmd` pour le nouveau.
L'atelier enseignant Ékole inclut `/prf22/index.html` sur le **port enseignant**, avec session locale. Pour enregistrer des révisions, démarrer Ékole avec `--edition` (ou `LANCER_ATELIER_SITUATIONS_PRF22.cmd`).

**Aucun Kristal, World, compte ou admission élève ne résulte de ces documents.** Les plans pour 1, 8 et 30 enfants sont des estimations de ressources, non des séances opérationnelles. Les objectifs sélectionnés dans les propositions ne sont pas validés pédagogiquement.

## Banque qualité v0.7

- `candidats-v0_7/` : 137 situations liées aux mêmes 77 sources Kontexte, avec justification de chaque activité et dossier `FICHE_PEDAGOGIQUE.json`. Les anciens lots restent inchangés.
- `activites-proposees-v0_7.json` : 51 patrons préexistants + 25 patrons ciblés Ékole, tous **non qualifiés**, avec provenance distincte des exercices Kontexte.
- `VERIFIER_BANQUE_QUALITE_PRF22.cmd` : contrôle les empreintes de tous les fichiers, le schéma et la non-activation des plans.
- `GENERER_BANQUE_QUALITE_PRF22.cmd` : génère une nouvelle version locale sous `generations/` sans écraser les banques versionnées.
- L'atelier enseignant `/prf22/index.html` affiche les ancrages, consignes, critères, preuves et lacunes; les révisions restent dans `revisions-local/`.

**Cohérence ≠ qualification** : les associations restent des hypothèses. Les programmes, contenus et matériels nécessitent une validation humaine; aucune publication ni admission enfant n'est possible depuis cette banque.
