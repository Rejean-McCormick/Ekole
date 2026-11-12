# Lot coordonné 2 — état réellement livré (11 novembre 2026)

## Résumé

Ce lot reste **synthétique, hors ligne et non déployé**. Il complète le premier overlay coordonné sans modifier les autorités des dépôts. Les fichiers de compétences et de sécurité ne sont pas des validations officielles, des autorisations scolaires ni des résultats d'élèves.

| Dépôt | Modification exécutable | Limite |
| --- | --- | --- |
| Kontexte | 55 correspondances candidates + validateur et tests; revue des 10 anciens scénarios | Aucun `curriculum_ids` approuvé ajouté; dix missions toujours bloquées |
| Orgo_Worlds | Paquet `ekole-fete-sorciere` et scénario de revue des 11 étapes, reconnu par l'injecteur Orgo | Ne crée pas un World scolaire effectif; aucune identité élève ou station active |
| Konnaxion | Constructeur limité d'intentions Kidaxion + tests | Aucun écran Kidaxion connecté ni autorisation serveur |
| Ékole | Audit multi-dépôts renforcé : candidats, intégrité du scénario, sûreté | Aucun moteur scolaire ajouté, aucune progression réelle d'enfant collectée |

## Interfaces et responsabilités retenues

- **Kontexte** est propriétaire des missions, rôles de scénario, fragments narratifs et correspondances candidates. Sa banque actuelle compte 17 missions; l'audit B5 conserve séparément les 11 historiques.
- **Kompose** propose l'attribution des personnages; l'approbation enseignante reste obligatoire.
- **Akor** transporte les intentions sous restrictions; il ne crée pas d'autorisation.
- **Orgo_Worlds** gère les Worlds/release; un world pack source est un **descripteur de scénario**, pas l'identité d'un World actif.
- **Orgo** est seul autorisé à écrire les Case/Task et à gérer le travail. Le pack `REVUE` utilise l'injecteur Orgo uniquement pour la préparation synthétique. Les dépendances des étapes y restent des métadonnées de conception, **pas** des transitions métier.
- **Konnaxion** est propriétaire de la communication. Le constructeur Kidaxion construit uniquement des **demandes non autoritatives**, sans corps de fragments; le serveur doit vérifier la séance, l'identité et les droits avant chaque action.
- **Ékole** est propriétaire de l'interprétation pédagogique et des preuves; réussir une Task ne prouve pas une maîtrise. **Inkuisite** conserve les exercices et tentatives selon ses propres contrôles.

## La banque et la revue pédagogique

`Kontexte/integrations/ekole/banque-worlds.curriculum-candidates.json` contient 55 liens *candidate_unreviewed* vers les Kristals du catalogue interne de 202 items, sur 7 missions (3 étapes de la fête et 52 des 6 nouvelles). Chaque entrée indique la version de mission et le SHA-256 de la consigne. Le fichier `REVUE_PEDAGOGIQUE_55_CANDIDATS.csv` facilite une validation humaine : colonnes décision, critère observable et commentaire.

**Ne pas copier automatiquement ces candidats dans `curriculum_ids`.** Une revue enseignante doit examiner la pertinence, définir la preuve observable, identifier éventuellement une source officielle et décider par version. Aucun enfant n'a été évalué par ce lot.

`Kontexte/integrations/ekole/securite-missions-historiques-a-revoir.json` identifie les dix missions avec garanties structurées manquantes. On n'a *pas* ajouté silencieusement les propriétés qui autoriseraient leur prévisualisation.

## Vérifications

Dans Kontexte : `PYTHONPATH=src python -m unittest discover -s tests -q` et `PYTHONPATH=src python -m kontexte.curriculum_candidates --json`.

Dans Orgo_Worlds : `node tools/world-scenario/cli.mjs validate-all ekole-fete-sorciere` puis `node tools/world-scenario/cli.mjs plan ekole-fete-sorciere REVUE`, en ayant Orgo accessible sous `C:\mycode\Orgo\Orgo`.

Dans Konnaxion : `node --test frontend/lib/__tests__/kidaxion-intents.node.test.mjs`.

Dans Ékole : `python tools/verifier_ecosysteme_tandem.py` (aussi `--workspace` pour copies locales).

Les tests ne font **aucun appel à un service scolaire**, ne vérifient **aucune authentification réelle**, ne produisent **aucune preuve de compétence** et ne créent **aucun World actif**.

## Conditions avant une séance réelle

1. Créer et publier un World scolaire avec tenant, version, participants et droits côté serveur; obtenir une preuve de portée signée et vérifiable.
2. Construire les tâches d'élèves et dépendances effectives dans Orgo (pas des Tasks de revue), avec assignations après décision enseignante.
3. Faire vérifier les droits avant *chaque* station, indice et interaction Konnaxion; construire l'interface Kidaxion qui n'émet que des intentions.
4. Raccorder les preuves à une identité scolaire consentie/autorisé, faire revoir les événements et valider les correspondances pédagogiques. Les exemples de SQLite de développement ne sont pas un registre de production pour mineurs.
5. Mettre en place des tests intégrés avec services, contrôles d'accès, tests d'isolation multi-classes, confidentialité et mécanisme de suppression.

**Ce lot ne livre pas ces capacités de production.**
