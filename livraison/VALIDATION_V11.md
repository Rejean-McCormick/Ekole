# Ekole v11 — validation et limites

La validation est conduite sur une base Ekole issue de `moodle.zip` + overlay v10, puis avec les **cinq sources Kristal originales** extraites de `kristals(9).zip` et l'overlay v11. L'overlay seul n'est pas un dépôt autonome complet.

## Vérifié

- 202 références Élève et 200 manifestations de prompts disponibles; 2 références sans source complète.
- Cinq scénarios Kristal profondément contextualisés, quatre moments chacun, et deux nouveaux défis non notés.
- 20 scénarios MiniLab répartis sur 9 moteurs, validations JS déterministes (sans inférence de maîtrise).
- Compilateur d'expériences : export par liste blanche; pas de rubrique réservée à l'enseignant, ni de banque d'items source.
- API d'expériences côté Enseignant : `401` sans session, `200` avec cookie temporaire valide.
- Export public Élève : compilé hors du dépôt, 202 références; aucune banque de réponses source, dossier enseignant ou prompt d'administration.
- Outil de migration : simulation, sauvegarde, ajout unique et détection des modifications par SHA; aucun écrasement silencieux.
- Syntaxe JS des interfaces Élève et Enseignant.
- Aucune image générée dans l'archive.

## Limites et blocage volontaire

- Le test du pont Moodle historique attend `kristal.workspace.json` dans tous les Kristals : ces fichiers ne sont pas présents dans les sources pédagogiques disponibles. Ce test **n'a pas été validé** sur cette base partielle et n'est pas résolu par cette livraison.
- Les nouveaux exercices récit et sciences ne valident pas à eux seuls les preuves de maîtrise des Kristals correspondants.
- Les 195 autres Kristals ne sont pas refondus individuellement; ils conservent l'expérience précédente avec un plan d'audit préparatoire.
- Les deux dossiers sources manquants ne sont pas inventés.
- Aucune validation en classe, ergonomie tactile et lecteur d'écran, ni évaluation externe du contenu n'a été réalisée.
- Les affectations d'année et de période restent proposées, non homologuées.

## Exécution locale

```powershell
py -3 tools\installer_sources_pilotes_v11.py --root . --apply
py -3 tools\synchroniser_ekole_apps.py --root .
py -3 tools\valider_mini_labs.py
py -3 -m unittest discover -s tests -p "test_refonte_kristals_v11.py"
```

Le pont Moodle reste optionnel et ne constitue pas le moteur pédagogique de l'élève.
