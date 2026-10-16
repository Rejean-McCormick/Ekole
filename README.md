# Ekole — moteur pédagogique neutralisé

Ce dépôt est le moteur neutre et commun aux deux contenus `ekole-quebec` et `ecole-pastorale`. Il comprend portail, espace apprenant, éditeur textuel local, API JSON et code historique isolé sous `legacy/`. L'ensemble est prévu pour Python 3.10+ sans dépendances tierces.

## Emplacement Windows

```text
C:\mycode\Ekole\
  ekole\             (moteur)
  ekole-quebec\      (202 cours scolaires conservés)
  ecole-pastorale\   (12 trames de cours, 3 parcours)
```

**Lancement recommandé :** double-cliquez sur `..\ekole-quebec\LANCER.bat` ou `..\ecole-pastorale\LANCER.bat`. Le choix du corpus ne demande aucune modification de configuration. Les deux lanceurs ouvrent des ports séparés (8765/8766 et 8775/8776 respectivement).

Si seul le moteur doit être démarré : `LANCER_EKOLE.bat`, ou `python launcher.py --contenu none`.

## Interfaces

- Québec : `http://127.0.0.1:8765/`, apprenant à `.../eleve/` et éditeur sur port 8766 avec lien privé imprimé dans le terminal.
- Pastorale : `http://127.0.0.1:8775/`, apprenant à `.../eleve/` et éditeur sur port 8776 avec lien privé imprimé dans le terminal.

Les deux éditeurs sont **en lecture seule par défaut**. Ajouter `--edition` au lanceur pour autoriser la modification des textes de cours et créer des sauvegardes adjacentes. L'éditeur est local, non destiné à un usage public multiutilisateur.

## Contrat d'interface

Le moteur charge `pack.json` et `cours/<id>.json` depuis le dépôt sélectionné par `--contenu CHEMIN`, conformément à `contracts/content-pack.schema.json`. La valeur `--contenu auto` est refusée si les deux dépôts sont présents pour éviter toute sélection accidentelle.

## Tests

Depuis `ekole/` : `python -m unittest discover -s tests -v` (les deux dépôts frères doivent être présents) ou `python launcher.py --contenu ../ecole-pastorale --verifier`.

## Limites

Cette version exploite le portail Core, la vue apprenant et l'éditeur textuel; les visualisations historiques avancées et les anciens connecteurs Moodle restent archivés dans `legacy/`, pas encore portés sur ces surfaces. Les contenus présents sont candidats, non publiés et non certifiés. Aucune affiliation institutionnelle n'est présumée. Le service écoute uniquement sur 127.0.0.1.
