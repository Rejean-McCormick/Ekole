# Rapport de validation locale — PRF-22 v0.3

**Date : 12 novembre 2026.** Tests réalisés dans un environnement Linux d'exécution, avec snapshots de code fournis; **pas de test natif sur Windows ni sur les bases/services réels de l'utilisateur**.

- **36 tests automatisés** réussis : conception 1–30, objectifs/références, cycle de dépendances, refus solo pour objectifs exigeant des pairs, export, dérive de sources, vérification portable sans `jsonschema`, installation idempotente, sauvegarde/retour arrière, refus de conflits et simulation d'échec d'écriture.
- **Essai GUI (Tkinter/Xvfb)** : ouverture et import d'un brouillon de l'exemple, 3 objectifs/activités/conjectures affichés, contrôle PRF-22 positif, export de dossier réel hors ligne.
- **Vérification de schéma** : `jsonschema` 4.26 sur le poste de validation, plus une vérification avec `python -S` sans dépendances tiers.
- **Essai Arketype (copie complète du snapshot)** : installation du profil, `arketype.py profile situation-pedagogique-orchestrable`, `arketype.py compose --profile ... --dry-run`, création effective d'un workspace local neutre, dépôt du blueprint dans `design/`, aucun fichier dans `canon/domain/`, puis retour arrière de l'installation réussi.
- **Validation globale Arketype sur snapshots** : 20 erreurs dans le snapshot initial, 20 après intégration. Elles concernent notamment des reçus `build/v9/build-receipt.json` absents de l'archive. Leur quantité n'a pas augmenté; la qualification globale Arketype ne peut donc pas être annoncée.

## Limites de validité

Ces tests démontrent des propriétés **logicielles et structurelles**. Ils ne démontrent ni qualité théorique des hypothèses rédigées, ni apprentissages d'enfants, ni justesse culturelle, ni équivalence réelle des variantes, ni capacité des stations/enseignants, ni admission Orgo/Konnaxion.

## Vérifier dans le dossier décompressé

```powershell
py -3 -m unittest discover -s tests -v
py -3 .\app\prf22_cli.py valider .\examples\exemple-prf22-v03.design.json
py -3 .\app\prf22_cli.py valider .\examples\exemple-prf22-v03.design.json --require-schema
```

La troisième commande demande le module Python optionnel `jsonschema` et doit échouer explicitement en son absence.
