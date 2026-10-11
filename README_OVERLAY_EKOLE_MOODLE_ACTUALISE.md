# Correctif Ekole pour `moodle.zip` actualisé — overlay cumulatif v4

## Résultat de la comparaison

Le `moodle.zip` fourni contient encore le site avec `Vague de construction`, rendu Markdown brut (`<pre>`) et marque « E » : **les corrections précédentes ne sont pas présentes**. Il contient en revanche un nouveau pont Moodle **polymorphe** et une OpsConsole, qui sont **conservés tels quels**.

## Installation

Extraire ce ZIP à la **racine réelle de l'instance Ekole qui contient `site/`, `tools/`, `opsconsole/` et `moodle/`**, sans dossier parent. Par exemple `C:\mycode\Ekole\EKOLE_COMPLET\` si tu as extrait `moodle.zip` à cet endroit. Il remplace seulement `site/index.html`, `site/app.js`, `site/style.css` et ajoute des outils/docs/données de parcours; le SVG d'origine est identique au logo de l'overlay v2. Les 202 fiches publiques existantes et le catalogue restent en place.

Cet overlay **n'inclut pas** `site/data/niveaux-manuel.json` pour éviter d'effacer tes affectations. Si tu as déjà personnalisé `site/data/parcours-affectations.json` dans un autre dépôt, sauvegarde-le avant extraction et fusionne les listes : le fichier fourni est volontairement vide. Si nécessaire, copie `site/data/niveaux-manuel.exemple.json` vers `site/data/niveaux-manuel.json` et remplis `levels_by_course` selon les décisions pédagogiques.

```powershell
cd 'C:\mycode\Ekole\EKOLE_COMPLET'
py -3 tools\valider_parcours.py
py -3 tools\ekole.py build
py -3 tools\ekole.py preview
```

Ouvre http://127.0.0.1:8765/ et actualise avec **Ctrl+F5**. La console peut rester au port 8766. Attention : si le serveur Python 8765 est déjà lancé, interromps-le avant d'en relancer un second; pour une mise à jour purement statique un rafraîchissement du navigateur suffit.

## Terminologie

- **Cours de la bibliothèque** : fiche issue d'un Kristal du catalogue; indépendante des parcours.
- **Parcours d'étape** : ensemble de cours d’une étape pédagogique de durée à définir localement.
- **Parcours d'année** : rassemble quatre étapes pédagogiques plus des cours de l'année dont l'étape reste à définir.
- **Parcours de cycle** : rassemble les années du cycle (2 ans par défaut, 2 ou 3 configurables selon décision).
- **Cours Moodle** : objet applicatif distinct, projeté par le pont polymorphe; il ne se déduit pas à l'identique d'un Kristal.

La proposition de calendrier « quatre étapes pédagogiques, deux à l’automne et deux en hiver » correspond au **modèle demandé** et non à une attestation du calendrier scolaire officiel. La composition est disponible, mais aucune affectation aux étapes n'est inventée.

## À préserver

Aucun remplacement de `tools/ekole.py`, `tools/kristal_moodle_bridge.py`, `moodle/`, `opsconsole/`, `catalogue/`, `site/data/index.json`, `site/data/cours/`, `kristals/` ou `plans/`. Aucun appel à Moodle, SemantiK, Konstellation ou aux services GitHub v10. Aucun identifiant Moodle, état canonique ou année scolaire n'est inventé.

Contrôles locaux : `py -3 -m unittest discover -s tests -p test_ekole_parcours.py -v`, `node tests/test_parcours_logic.mjs`. Voir `livraison/VALIDATION.md` pour les vérifications exécutées ici et les limites.


## Mise à jour v4 — disposition scolaire du Québec

- 4 **étapes pédagogiques Ekole** (2 à l’automne, 2 en hiver), plutôt que 3 × 4 mois.
- 3 **étapes officielles de bulletin** en parallèle; ne pas confondre les deux systèmes.
- 3 cycles de 2 années, 6 années, 24 regroupements d’étape; 202 cours demeurent indépendants.
- Icônes des domaines, logo Ekole, palette `#1e6864`, lecture Markdown et pont Moodle polymorphe conservés.
- Le fichier de données personnalisé `site/data/parcours-affectations.json` n’est **PAS** dans le ZIP. L’exemple 24 étapes sert de repli sur une installation neuve.

### Installation cumulative

Décompresser à la racine réelle du dépôt contenant `site/`, `tools/`, `moodle/` et `opsconsole/`. Ne pas déposer ce ZIP dans `tools/`.

```powershell
py -3 tools\migrer_4_etapes.py                # simuler
py -3 tools\migrer_4_etapes.py --apply        # migrer et sauvegarder, si souhaité
py -3 tools\valider_parcours.py
py -3 tools\ekole.py build
py -3 tools\ekole.py preview
```

Faire ensuite Ctrl+F5. Les dates des étapes pédagogiques sont à qualifier localement, sans affectation automatique.

### Sources de qualification

- **Kristal-ScolQc fourni**, `knowledge-base/sources/assessment_semantics.json` et `knowledge-base/sources/progression_semantics.json` : modèles scolaires et règle de séparation.
- **Gouvernement du Québec**, [Pondérations et libellés du bulletin au préscolaire et au primaire](https://www.quebec.ca/education/prescolaire-primaire-et-secondaire/programmes-formations-evaluation/epreuves-ministerielles-evaluation-apprentissages/ponderations-libelles-bulletin/prescolaire-primaire) : trois bulletins annuels au primaire.
- **Modèle éditorial Ekole**, à approuver : quatre périodes d’apprentissage, deux à l’automne et deux en hiver, sans date ou pondération officielle attribuée.

## Correction terminologique v4.1

La seconde moitié de l’année est nommée **Hiver** (étapes pédagogiques 3 et 4), sans autre mention saisonnière dans les libellés. Les affectations, identifiants d’étapes, trois étapes officielles de bulletin et règles Moodle ne changent pas. Le champ interne `periode` adopte `hiver`; les fichiers d’affectation n’utilisent pas ce champ et sont donc conservés.
