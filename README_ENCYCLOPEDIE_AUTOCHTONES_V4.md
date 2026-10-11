# Kristal autonome — Encyclopédie des sociétés autochtones au Québec (v4)

## Pourquoi cette évolution ?

La v3 était un petit graphe historique réutilisable. Les enfants ont besoin d'un **manuel consultable et interrogeable** sur la vie quotidienne, les habitations, les familles, les activités, les voyages, les techniques, les échanges, les langues et la vie contemporaine. Cette v4 ajoute **65 fiches documentaires**, **11 chapitres thématiques**, **27 références**, **57 liens de préalables pédagogiques**, **20 entraînements non certificatifs**, **11 prompts conceptuels** et un **lecteur hors ligne**.

**Ce n'est PAS une encyclopédie complète et validée par les nations.** Les fiches contiennent une synthèse originale et contextualisée; elles ne remplacent pas la recherche historique, archéologique et les perspectives des nations. Les sources pointent à des pages et rubriques identifiables, mais les ancrages fins jusqu'aux passages et la revue contradictoire restent à compléter.

## Architecture à conserver

- `kristals/societes-autochtones-quebec/` **possède** les connaissances v3 et les nouveaux articles v4. Indépendant d'Ekole, de Moodle et de SemantiK.
- `kristals/.../canon/domain/graphe-v3.json` : source **inchangée**. Son reçu `build/v9` d'origine **reste inchangé**, pour les références existantes.
- `kristals/.../canon/domain/encyclopedie-v4.json` : **nouvel artefact canonique** dans `canon/state.index.json`. `build-candidats/v4/` est une capture du build v9 candidat de ce nouvel état (pas une publication v10).
- `cours-references/qc-pri-us-009/PROPOSITION_EXTENSION_ENCYCLOPEDIQUE_V4.json` : une **proposition de sélection**, pas un cours modifié. Les références v3 du cours restent épinglées et intactes.
- `site/eleve/encyclopedie-autochtones/` : lecteur statique et exercices, compilés à partir de ce Kristal. **Sans IA à l'exécution**. Aucune donnée d'élève conservée.
- `tools/encyclopedie_autochtones_v4.py` : consultation hors ligne, validation, compilation.

## Installation — à la racine Ekole

Sauvegarder ou committer le dépôt **avant d'extraire**. Extraire le ZIP à la racine où se trouvent `site/`, `tools/` et `kristals/`. Aucun script n'écrase le cours `qc-pri-us-009`, le Core, l'OpsConsole, Moodle ni les anciennes sources de la v3.

```powershell
py -3 tools\encyclopedie_autochtones_v4.py --root . --check
py -3 tools\encyclopedie_autochtones_v4.py --root . --compile
```

Lancer le serveur Ekole habituel (`LANCER_EKOLE_3_APPS.bat`) et ouvrir :

`http://127.0.0.1:8765/eleve/encyclopedie-autochtones/`

Le lien vers la vue autonome peut être ajouté aux cartes d'activité ou aux menus d'Ekole, après revue de l'enseignant. La proposition de référence v4 du cours **n'est pas publiée ni automatiquement activée**.

### Interroger le Kristal sans site Web

```powershell
py -3 tools\encyclopedie_autochtones_v4.py --root . --list-topics
py -3 tools\encyclopedie_autochtones_v4.py --root . --question "Qui préparait les peaux ?"
py -3 tools\encyclopedie_autochtones_v4.py --root . --question "De quoi était fait le fil à pêche ?"
py -3 tools\encyclopedie_autochtones_v4.py --root . --search "palissades"
```

Une question trop large ou sans correspondance **retourne une invitation à préciser, ou des fiches candidates**, jamais une nouvelle réponse factuelle improvisée. Le texte libre est un **moteur de recherche déterministe**, pas une compréhension générative du langage naturel. Les exercices n'exigent pas de saisie ouverte.

### Images à produire PLUS TARD

Le registre des **11 intentions visuelles** porte le concept, le prompt sans style, l'alt et le chemin d'image souhaité, par ex. `site/eleve/encyclopedie-autochtones/images/habiter.webp`. Si l'image n'existe pas ou ne charge pas, **le prompt est montré en toutes lettres**. Aucune image n'est fournie.

Une illustration historique culturellement spécifique exige une vérification des sources et la consultation appropriée; les diagrammes calculant des quantités exactes restent du ressort des moteurs déterministes.

## Précautions de fond

1. « Iroquoiens » (ensemble linguistique), Iroquoiens du Saint-Laurent, Wendat, Haudenosaunee, Innus, Inuit : **ne pas confondre**.
2. Les catégories actuelles des « onze nations » ne définissent pas les sociétés de l'an 1500.
3. Les rôles décrits par genre représentent des pratiques scolaires historiques, **pas des interdictions universelles**.
4. Les chiffres de longueur, de population et de fréquence de déplacement dépendent des sources et des sites, et n'ont pas de statut de loi.
5. L'absence de donnée n'est pas une preuve de fausseté. Les réponses « non attesté » et « cela dépend » sont des réponses de qualité.
6. L'approbation culturelle / historique n'est **pas obtenue**. Aucune connaissance ou image protégée ne peut être présumée libre de réutilisation.
7. Les 20 exercices sont des **entraînements formatifs** et non des preuves officielles de maîtrise. Les réponses se trouvent nécessairement dans le JSON élève accessible : pas de sécurité d'examen.
8. La v4 ne fabrique pas de nouvelles phrases par SemantiK : elle donne à SemantiK une structure de contenus réutilisables, à intégrer lors d'une étape ultérieure.

## Validation

```powershell
py -3 -m unittest discover -s tests -v
```

Le contrôle du kit et un build v9 **candidat** ont été exécutés en mode isolé. Le reçu historique v3 par défaut a ensuite été restauré **byte pour byte** afin de ne pas briser les références de cours antérieures. Pour republier ou activer la v4, il faut une revue et une migration explicite des consommateurs.
