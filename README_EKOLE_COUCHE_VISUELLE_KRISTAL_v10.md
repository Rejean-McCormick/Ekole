# Ekole · Couche conceptuelle d'images dans les Kristals — overlay v10

## Objectif et périmètre

Cet overlay prolonge la **bibliothèque Ekole MiniLab v9**. Il ne dessine, n'importe et ne génère **aucune image**. Il n'impose **aucun style graphique**, palette, mascotte ou modèle d'IA. Les prompts décrivent uniquement le concept à représenter en fonction des objectifs et notions des Kristals.

- 200 Kristals complets de `kristals(9).zip` ont reçu `experience/RESSOURCES_VISUELLES.json`, sans toucher aux fichiers `authoring/`, `contenu/`, `evaluation/` ou `sources/`.
- Le catalogue élève conserve 202 références. Les deux sources absentes (`qc-pri-fr-004`, `qc-pri-ma-005`) ont un **brouillon séparé**, non intégré à une fausse source : `visuels/KRISTALS_SANS_SOURCE.json`.
- 406 intentions de visuels couvrent l'ensemble du catalogue : **2 par cours**, plus 2 contextes pour les Kristals associés à des scénarios MiniLab existants.
- Les propositions liées aux mini-environnements sont **indicatives, à revoir**. Aucune nouvelle preuve de maîtrise ni règle de correction n'est créée.

## Structure dans chaque Kristal

```
kristals/qc-pri-ma-012/
  authoring/                     (conservé)
  contenu/                       (conservé)
  evaluation/                    (conservé)
  experience/
    RESSOURCES_VISUELLES.json    (nouveau : deux ou trois slots conceptuels)
    images/                     (à créer manuellement lorsque les images existent)
      concept.webp              (fichier préféré, non livré)
      situation.webp            (fichier préféré, non livré)
      support-outil.webp        (si le slot existe)
```

Chaque slot contient : `placement`, `concept`, `prompt_conceptuel`, `texte_alternatif`, `role`, `fichier_preferentiel`, `formats_acceptes`, `outils_associes` et son **origine dans le contrat pédagogique**.

Les images non encore produites ne sont **pas** dans le ZIP. Le chemin préféré est `.webp` mais `.png`, `.jpg` et `.jpeg` sont également reconnus. La dimension et le format peuvent être ajustés manuellement avant de déposer le fichier. Un fichier est refusé s'il est invalide, démesuré, symboliquement lié ou de format trompeur.

## Comportement de l'interface

À `http://127.0.0.1:8765/eleve/?cours=qc-pri-ma-012`, onglet **Découvrir** :

- Si `kristals/qc-pri-ma-012/experience/images/concept.webp` (ou autre extension reconnue) est absent : le **prompt conceptuel complet** et le chemin attendu s'affichent, avec un bouton de copie.
- Si le fichier existe et est valide : le compilateur le copie vers l'emplacement public du portail Élève, et le navigateur montre l'image. En cas d'échec du chargement, retour au prompt.
- L'onglet **Explorer** utilise le slot `situation`. Le slot `support-outil`, lorsqu'il existe, apparaît dans **Essayer**.
- Ekole Enseignant montre les intentions de chaque cours avec les chemins et les prompts; l'ancien registre d'images éditoriales n'est plus la référence pour les cours.

## Installation

1. Extraire cet overlay **à la racine du dépôt Ekole** : même niveau que `site/`, `tools/`, `kristals/` et `enseignant-app/`. Il contient la v9 cumulative.
2. Ne pas supprimer ni remplacer les autres répertoires des Kristals.
3. Exécuter :

```powershell
py -3 tools\synchroniser_ekole_apps.py --root .
```

Ou lancer `LANCER_EKOLE_3_APPS.bat`, qui appelle automatiquement la synchronisation et donc le compilateur visuel.

Lorsque tu ajoutes manuellement une image, exécute :

```powershell
py -3 tools\compiler_visuels_kristals.py --root .
```

Puis recharge la page Élève avec `Ctrl+F5`. **Pillow** est requis pour prendre en compte les images réelles (`py -3 -m pip install Pillow`) ; il n'est pas requis pour afficher les prompts sans images.

## Export Élève

L'export statique v8/v9 a été adapté : il copie `data/kristals-visuels.json` et uniquement les fichiers média compilés qui y sont référencés. Il ne copie **pas** `kristals/`, `evaluation/`, les banques de réponses, les prompts d'administration hérités ou l'application Enseignant. Avant une publication scolaire réelle, procéder à la revue des contenus et des droits des images.

```powershell
py -3 tools\export_ekole_eleve_v8.py --root . --out C:\ekole-eleve-public
```

La destination doit être nouvelle et située **hors** du dépôt.

## Ce que cet overlay ne prétend pas faire

- Aucun modèle d'IA ou générateur d'image n'est appelé.
- Les 202 cours n'ont pas été transformés en 202 évaluations interactives certifiées.
- Les 2 Kristals absents ne sont pas reconstitués par supposition.
- Les images d'une quantité mathématique exacte ou d'une interface évaluée doivent être calculées par MiniLab, **pas demandées à un générateur d'images**.
- L'interface Enseignant est une prévisualisation locale à session temporaire, pas une authentification multiutilisateur de production.
