# Ekole · Sociétés autochtones et rencontres au Québec — v3 modulaire

**NOUVEAU : le Kristal autochtone est autonome, distinct du cours.** La v3 n'exige aucune IA à l’exécution et ne génère aucune image.

## Architecture

```text
kristals/
  modele-organisation-humaine/            Ontologie générale : rôle, tâche, ressource, règle
  societes-autochtones-quebec/             30 assertions et 13 relations, 4 responsabilités/normes, indépendant de l'école
  rencontres-coloniales-quebec/            25 assertions et 5 relations, 2 normes, indépendant du cours
  qc-pri-us-009/                           Cours existant : SA sélection, SES objectifs, SES références épinglées
```

Le cours ne contient **aucune copie des assertions de la v3**. Il sélectionne 22 assertions réparties entre les deux Kristals autonomes. Les deux corpus restent disponibles pour d'autres cours et d'autres applications, même sans Ekole. Le modèle polymorphe `modele-organisation-humaine` est distinct de ces deux corpus.

Le graphe couvre, à titre **documentaire candidat**, des descriptions situées de nations (notamment Wendat et Innue), de rencontres, de négociations et de changements coloniaux. Les sociétés autochtones ne sont jamais traitées comme une seule société. Les deux Kristals restent à revoir par les nations concernées et des spécialistes.

## Installation Windows sur la racine du dépôt Ekole

**Sauvegarder ou committer ton dépôt avant d'extraire un overlay ZIP : l’extraction elle-même peut remplacer des fichiers locaux.** Les outils d'installation ci-dessous ne suppriment pas les fichiers historiques et refusent une sélection personnalisée divergente.

1. Extraire le ZIP à la racine, au niveau de `site/`, `tools/`, `kristals/`.
2. Vérifier les références, puis prévisualiser la migration :

```powershell
py -3 tools\integrer_references_histoire_v3.py --root . --detach-legacy --restore-missing-course-frame
```

3. Après lecture de la prévisualisation, appliquer :

```powershell
py -3 tools\integrer_references_histoire_v3.py --root . --detach-legacy --restore-missing-course-frame --apply
py -3 tools\compiler_atelier_histoire_v3.py --root . --prefer-installed
```

`--detach-legacy` retire uniquement les **enregistrements canoniques historiques v1/v2 connus** du Kristal de cours. Les deux fichiers `societes-rencontres-v1.json` et `societes-rencontres-v2.json` restent physiquement présents et sauvegardables; les scénarios v1/v2 restent accessibles comme archives. Les autres artefacts canoniques du cours restent inchangés. **Attention :** si une application externe a épinglé l'ancien état v1/v2 du cours, elle devra migrer explicitement sa référence; le script ne met pas ces consommateurs à jour.

4. Démarrer le serveur Ekole habituel. Ouvrir :

`http://127.0.0.1:8765/eleve/ateliers/rencontres-quebec/version-v3.html`

La compilation existe aussi sans installation du cours, pour prévisualiser le nouvel atelier :

```powershell
py -3 tools\compiler_atelier_histoire_v3.py --root .
```

## Interroger le Kristal autochtone sans Ekole

```powershell
py -3 tools\interroger_societes_autochtones_v3.py --root . --search "wendat"
py -3 tools\interroger_societes_autochtones_v3.py --root . --period "periode:actuel"
```

L'outil parcourt **exclusivement** `kristals/societes-autochtones-quebec/`. Il retourne les faits, leurs périodes, limites et sources, sans avoir besoin de `qc-pri-us-009`, de Moodle ou d'une IA.

Pour les trois Kristals, la commande `py -3 kristals\<slug>\tools\kristal.py check kristals\<slug>` vérifie la structure. Un build v9 candidat est fourni pour les corpus autonomes. Il ne signifie pas publication v10 ou validation culturelle.

## Couche d'images

Les illustrations ne sont **ni créées ni stylisées**. Les prompts conceptuels restent visibles dans la page v3 tant que l'image n'existe pas au chemin attendu. Les diagrammes évaluant des valeurs exactes restent des rendus calculables, pas des images génératives non vérifiées.

## Limites éditoriales et pédagogiques

- Faits sourcés, mais certaines références héritées nécessitent encore des ancrages fins et une relecture indépendante.
- Certaines connaissances culturelles exigent consentement, contexte et validation par les nations; aucun droit de réutiliser leurs savoirs n'est présumé.
- Les 26 activités compilées sont des **entraînements vérifiables et contextualisés**, pas des preuves de maîtrise. Plusieurs sont simples et doivent être enrichies pédagogiquement.
- Les exercices sur la violence et les injustices coloniales ne sont pas transformés en concours de points; discussion encadrée par un adulte.
- Les vues v1/v2 contiennent toujours des copies historiques; **seule la compilation v3** utilise les corpus autonomes.
- La version v3 travaille hors ligne une fois ses fichiers locaux présents; les liens externes vers les sources nécessitent Internet.
- Pas de SemantiK Architect connecté dans cet overlay. Les énoncés restent en phrases déjà présentes dans les assertions, pas des nouvelles phrases composées par SemantiK.
