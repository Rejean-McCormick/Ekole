# Ekole — Méga-correctif pédagogique v14

## Livraison

Ce paquet est un **overlay**, sans dossier englobant. L'extraire à la **racine exacte** du dépôt Ekole fourni (`site/`, `tools/`, `kristals/` et `enseignant-app/` au même niveau). Sauvegarder ou committer le dépôt avant installation. Le Core, le pont polymorphe Moodle, OpsConsole, les documents pédagogiques et le canon des Kristals ne sont pas supprimés ni réécrits.

## Ce qui est réparé

- **Pas de saisie de réponse libre dans les exercices Élève.** L'estimation historique utilise désormais des propositions sélectionnables. Le champ de recherche de l'encyclopédie demeure une recherche de *fiches*, pas une réponse évaluée.
- **14 moteurs déterministes** : les neuf MiniLabs historiques, plus valeur de position (boutons centaines/dizaines/unités), problèmes à deux décisions, lecture de diagrammes, fractions équivalentes (sélection multiple) et durée écoulée (bonds de temps).
- **51 défis catalogués**; 35 références d'exercice (certaines multiples) attachées à 25 cours par manifeste. Les huit cours de mathématique **provisoirement placés en 3e année** ont chacun au moins une activité liée. Il s'agit d'une couverture d'entraînement **candidate**, pas d'une preuve de maîtrise.
- **Contrat Kristal → outil** : `kristals/<id>/experience/OUTILS_INTERACTIFS_V14.json` (ou `cours-references/<id>/...` si la source complète manque). Aucun exercice n'est proposé automatiquement pour « remplir » un cours. Chaque référence porte sa compétence et une association `proposition_non_validee`.
- **Blocage des mauvais liens** : grade proposée incompatible, ID du cours différent, activité non déclarée. La bibliothèque générale peut toujours explorer d'autres sujets, mais sans prétendre être une activité du cours.
- **Audit des 202 cours** : `docs/AUDIT_ACTIVITES_202_V14.json`, avec objectif source, maturité, année proposée, moteurs à examiner et lacunes. Accessible depuis l'atelier Enseignant sous session locale.
- **Export Élève** mis à jour : les fichiers d'association v14 et les micro-mondes font partie de l'export; ni les dossiers enseignants ni les banques source n'y figurent.
- **Interface adaptée** : labels explicites « atelier lié » ou « découverte accompagnée », contrôles larges, texte lu par le navigateur selon fonctionnalité existante, clavier et tactile sans glisser-déposer obligatoire.

## Installation Windows

1. Sauvegarder / faire un commit du snapshot local.
2. Extraire le ZIP sur les dossiers existants à la racine du dépôt, en autorisant les remplacements. Ne **pas** extraire à l'intérieur de `site/`.
3. Double-cliquer `LANCER_EKOLE_3_APPS.bat`. Il exécute automatiquement la synchronisation puis `compiler_activites_v14.py` avant les serveurs.
4. Actualiser les onglets avec `Ctrl+F5`.

Si la procédure automatique n'est pas possible :

```bat
py -3 tools\synchroniser_ekole_apps.py --root .
py -3 tools\compiler_activites_v14.py --root .
py -3 tools\ekole.py preview
```

L'interface Core démarre sur `http://127.0.0.1:8765/`, Élève sur `http://127.0.0.1:8765/eleve/` et les outils sur `http://127.0.0.1:8765/eleve/labo/`. L'application Enseignant se lance séparément sur le port 8766 avec session locale, depuis le BAT.

### Exemples de cours

- 3e année, lecture de diagrammes : `http://127.0.0.1:8765/eleve/?cours=qc-pri-ma-031`
- 3e année, opérations à étapes : `http://127.0.0.1:8765/eleve/?cours=qc-pri-ma-019`
- 3e année, arrondir : `http://127.0.0.1:8765/eleve/?cours=qc-pri-ma-005`
- Histoire et sociétés : `http://127.0.0.1:8765/eleve/?cours=qc-pri-us-009`

### Vérifications

```bat
py -3 tools\compiler_activites_v14.py --root . --check
py -3 -m unittest discover -s tests -p test_ekole_v14_mega.py -v
node tests\test_microlab_engine_v14.js
```

Le rapport qualité issu des tests est dans `docs/RAPPORT_VALIDATION_MEGA_V14.md`.

## Ce qui n'est pas finalisé

- **177 cours sur 202** n'ont pas encore de référence explicite à un MiniLab vérifiable. Ils gardent leur objectif et leur contenu, sans faux jeu de remplacement. Le travail pédagogique profond et la validation par enseignants sont à faire.
- L'affectation des cours aux années est encore **proposée**; elle ne provient pas d'une approbation scolaire. Les quatre étapes internes sont Automne 1–2 et Hiver 1–2, distinctes des trois bulletins officiels.
- Le contrôle des réponses est **déterministe dans le navigateur**. Les réponses des défis peuvent être inspectées dans ses ressources locales : il s'agit d'entraînement, **pas d'examen inviolable**.
- Le Kristal autochtone est autonome et **ne doit pas être absorbé** dans le cours d'histoire. Les sources et les validations culturelles en attente restent inchangées.
- Aucune image IA n'est générée. Les prompts conceptuels existants apparaissent lorsque leurs images sont absentes. Aucun style n'est imposé.
- Les essais ergonomiques sur de vrais enfants et les revues institutionnelles restent indispensables.
