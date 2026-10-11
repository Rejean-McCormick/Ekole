# Ekole — Organisations humaines et sociétés du Québec — V2 (candidate documentaire)

**Paquet cumulatif avec v1**, pour la racine du dépôt Ekole. Il enrichit le Kristal `qc-pri-us-009` et le modèle autonome `modele-organisation-humaine`, sans effacer le corpus v1.

## Installation contrôlée (Windows)

1. Faire une copie ou un commit du dépôt avant extraction du ZIP.
2. Extraire le ZIP **dans le répertoire contenant** `site/`, `tools/`, `kristals/` (s'il existe). Les noms de fichiers v1 déjà personnalisés ne sont pas modifiés par l'installateur v2, mais les fichiers de l'overlay ZIP à la racine peuvent remplacer les scripts ou pages du portail : sauvegarder est obligatoire.
3. Si `kristals/qc-pri-us-009` ne contient pas encore sa couche v1, l'installer en premier :

```powershell
py -3 tools\integrer_kristal_histoire.py --root . --restore-missing-frame --apply
```

4. Prévisualiser, puis installer **seulement les nouveaux fichiers v2** :

```powershell
py -3 tools\integrer_kristal_histoire_v2.py --root .
py -3 tools\integrer_kristal_histoire_v2.py --root . --apply
```

5. Construire les données publiques Élève depuis le Kristal installé :

```powershell
py -3 tools\compiler_atelier_histoire_v2.py --root . --prefer-installed
py -3 tools\valider_kristal_histoire.py
py -3 -m unittest discover -s tests -p "test_societes_v2.py"
```

6. Démarrer le serveur Ekole existant et ouvrir :

`http://127.0.0.1:8765/eleve/ateliers/rencontres-quebec/`

La v1 demeure accessible à `.../rencontres-quebec/version-v1.html`.

## Ce qui est maintenant réel

- 37 assertions (23 héritées et 14 nouvelles), **22 sources répertoriées**, chacune contextualisée; les 14 nouvelles assertions possèdent un repère de section précis (pas encore une citation archivistique complète).
- 8 relations v2 rôle → tâche → ressource → période → fait → source; 4 règles/mandats attribués et datés.
- Comparaison des descriptions historiques wendat, de pratiques saisonnières innues, du traité colonial de 1701 et de responsabilités wendat actuelles, **sans confondre leurs systèmes d'autorité**.
- 16 activités v2 produites à partir de relations et règles typées : 8 choix parmi des fiches sourcées, 2 associations, 1 chronologie, 4 distinctions de provenance, 1 activité de comparaison à observation humaine. Les 22 exercices v1 restent accessibles séparément. **38 activités différentes au total, deux parcours distincts; aucune validation de maîtrise certifiée.**
- 13 concepts d'images sans style ni image générée. Chaque prompt reste visible si le fichier n'est pas présent ou ne se charge pas.
- Les programmes s'exécutent sans IA et les données compilées fonctionnent sans réseau. Les liens vers les sources nécessitent Internet si l'enfant les ouvre.

## Principes non négociables

- « Autochtones » n'est pas une société homogène; « Blancs » est remplacé selon le contexte par **colons français, autorités françaises, administration britannique, commerçants européens**, sans effacer la question des relations coloniales.
- Ne pas confondre source coloniale transcrite, autodescription contemporaine d'une nation, pratique historiquement décrite, droit ou norme.
- Aucun savoir cérémoniel ou récit culturel particulier ne doit être fabriqué ou illustré sans consentement adapté.
- Une relation non encodée ne devient jamais « historiquement fausse » par défaut.
- Le système ne note pas les injustices et violences coloniales. Ces contenus appellent une médiation éducative et humaine.

## Statut explicite

**Candidate de recherche et d'entraînement.** Vérification externe des liens, ancrages du corpus v1, revue par les nations concernées, co-conception, vérification d'accessibilité et essai en classe restent à faire. **Le build v9 Local Kristal n'est pas une publication v10.**

## Fichiers structurants

- `kristals/modele-organisation-humaine/canon/domain/extension-v2.json` : ontologie vérifiable.
- `modules/qc-pri-us-009/canon/domain/societes-rencontres-v2.json` : nouveau graphe sans effacement v1.
- `modules/qc-pri-us-009/sources/TRACABILITE_ASSERTIONS_v2.json` : provenance et sections.
- `tools/compiler_atelier_histoire_v2.py` : génération des activités sans IA.
- `tools/integrer_kristal_histoire_v2.py` : installation non destructive.
- `docs/BILAN_COUVERTURE_V2.json` : lacunes mesurées, non masquées.
