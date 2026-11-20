# Ékole — moteur pédagogique local

Ce dépôt est le moteur neutre et commun aux deux contenus `ekole-quebec` et `ecole-pastorale`. Il comprend portail, espace apprenant, éditeur textuel local, API JSON et code historique isolé sous `legacy/`. L'ensemble est prévu pour Python 3.10+ sans dépendances tierces.

- [Comprendre l’écosystème Ékole](docs/ECOSYSTEME.md) · Packs, outils associés, parcours d’usage et documentation des dépôts.
- [Démarrer Ékole](docs/DEMARRAGE.md) · Choisir un pack, vérifier son installation et ouvrir le portail.
- [Consulter la documentation](docs/README.md) · Guides auteur, navigation assistée, architecture collaborative et intégrations.

## Emplacement Windows

```text
C:\mycode\Ekole\
  ekole\             (moteur)
  ekole-quebec\      (202 cours scolaires conservés)
  ecole-pastorale\   (32 cours candidats, 7 parcours (prototype non approuvé))
```

**Lancement recommandé :** double-cliquez sur `..\ekole-quebec\LANCER_EKOLE_QUEBEC.bat` ou `..\ecole-pastorale\LANCER_PASTORALE.bat`. Le choix du corpus ne demande aucune modification de configuration. Les deux lanceurs ouvrent des ports séparés (21150/21151 et 21153/21154 respectivement).

Si seul le moteur doit être démarré : `LANCER_EKOLE.bat`, ou `python launcher.py --contenu none`.

## Interfaces

- Québec : `http://127.0.0.1:21150/`, apprenant à `.../eleve/` et éditeur sur port 21151 avec lien privé imprimé dans le terminal.
- Pastorale : `http://127.0.0.1:21153/`, apprenant à `.../eleve/` et éditeur sur port 21154 avec lien privé imprimé dans le terminal.

Les deux éditeurs sont **en lecture seule par défaut**. Ajouter `--edition` au lanceur pour autoriser la modification des textes de cours et créer des sauvegardes adjacentes. L'éditeur est local, non destiné à un usage public multiutilisateur.

## Contrat d'interface

Le moteur charge `pack.json` et `cours/<id>.json` depuis le dépôt sélectionné par `--contenu CHEMIN`, conformément à `contracts/content-pack.schema.json`. La valeur `--contenu auto` est refusée si les deux dépôts sont présents pour éviter toute sélection accidentelle.

## Tests

Depuis `ekole/` : `python -m unittest discover -s tests -v` (certaines suites exigent les packs frères ou des composants voisins) ou `python launcher.py --contenu ../ecole-pastorale --verifier`.

## Tandem / Orgo — préparation locale P1

Orgo possède les tâches des aventures que lui confie la séance. Ékole exécute aussi des activités pédagogiques locales. Pour la préparation Tandem, Ékole propose une **prévisualisation synthétique réservée à l’enseignant**, sans connexion Orgo ni identité d’élève : voir [l’aperçu Tandem P1](docs/TANDEM_EKOLE_ORGO_PREVIEW_P1.md). Le mode est **désactivé par défaut**. Ne pas utiliser pour des enfants réels ni comme mécanisme d’autorisation.

## Limites

Cette version exploite le portail Core, la vue apprenant et l'éditeur textuel; les visualisations historiques avancées et les anciens connecteurs Moodle restent archivés dans `legacy/`, pas encore portés sur ces surfaces. Les contenus présents sont candidats, non publiés et non certifiés. Aucune affiliation institutionnelle n'est présumée. Le service écoute uniquement sur 127.0.0.1.

## Vérification des intégrations satellites (27 octobre 2026)

Voir [le contrôle de compatibilité et les limites de qualification](docs/Integration-Verification-2026-10-27.md). Les versions et statuts externes doivent être vérifiés avant tout déploiement.
## Final-system integration reference (Branch 06)

The [English education-boundary specification](docs/FINAL_SYSTEM_EDUCATION_ALIGNMENT.md) describes implemented safety checks, local test instructions, cross-owner responsibilities and still-unapproved interfaces. It does **not** assert a deployed Orgo/Moodle workflow.

## Personnages et médias

Le moteur lit les catalogues `ekole.personnages/1` à `/4`. Le pack sélectionné détermine le format, les rôles et les fichiers effectivement disponibles. Voir [l’intégration des personnages](docs/PERSONNAGES_ALIGNMENT.md) et [les sources du pack Québec](https://github.com/Rejean-McCormick/Ekole-Quebec/blob/main/personnages/README.md).
