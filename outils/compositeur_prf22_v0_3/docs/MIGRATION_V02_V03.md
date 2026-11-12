# Migration PRF-22 v0.2 → atelier v0.3

La v0.2 livrait une spécification et un exemple théorique. La v0.3 est une **extension candidate du modèle** et un outil utilisable, non une migration officielle du Framework Kristal :

- **Nouveau** : édition directe dans les catalogues Kontexte (trames, activités et objectifs indépendants) avec sauvegarde locale.
- **Nouveau** : cartes pédagogiques par objectif; conjecture écrite, critères, réfutation, alternatives et conditions de validité.
- **Nouveau** : liens d'activités choisis par l'enseignant, contrôle des dépendances, rôle individuel et collaboration explicités.
- **Nouveau** : schéma `design/0.3` avec provenance de situation et énoncé de conjecture.
- **Nouveau** : export multi-effectifs et documents de revue, plus liaison à un workspace Arketype sur demande.
- **Conservé** : trois couches théories/ingénierie/séance, ARK-15 + ARK-10, statut `design_only` et refus d'une autorité runtime implicite.

L'ancien exemple v0.2 est conservé comme **source historique et bibliographique** dans `examples/fete-sorciere-theorie.design.json`. Il n'est **pas** valide comme document v0.3 et ne doit pas être converti en remplaçant seulement son numéro de format. Le nouveau dossier `examples/exemple-prf22-v03.*` montre une conception distincte candidate construite avec des références Kontexte.

L'ancien compositeur v0.1 reste intact : ce pack ajoute un atelier côte à côte (`outils/compositeur_prf22_v0_3/`) et réutilise sa logique de catalogue/rotation dans le nouvel atelier. Les plans d'organisation restent des simulations de capacité et doivent être revus.
