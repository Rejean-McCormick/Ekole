# Ekole — correctif des parcours v5 (répartition indicative)

Ce ZIP est un **overlay à extraire au ROOT du repo Ekole**, sur la version cumulée v4.1. Il ne contient pas de dossier parent.

Le problème observé (« 0 cours » par année) vient de l'absence de liens entre les 202 fiches et les 24 conteneurs de parcours. Ce patch fournit une **proposition calculée** de répartition en 6 années et 4 étapes pédagogiques. Les filtres fonctionnent maintenant avec cette proposition, mais elle n'est pas homologuée. Les bulletins officiels restent structurés en trois étapes distinctes.

## Ce qui est modifié

- `site/app.js` : charge une table de propositions, puis fusionne en mémoire avec les attributions existantes. Les attributions manuelles d'étape **ou de niveau** sont prioritaires; une proposition ne les écrase jamais.
- `site/style.css` : avertissement très visible « proposition à valider ».
- `site/data/parcours-propositions.json` : les 202 suggestions identifiées, justifiées par le registre, les objectifs et les préalables.
- `tools/proposer_affectations.py` : reconstruire les suggestions de façon déterministe à partir du catalogue et du graphe (jamais des vagues).
- `tests/test_propositions_affectations.py` et `tests/test_propositions_logic.mjs` : contrôles.
- `docs/REPARTITION_PROPOSEE.md` : méthode, droits et limites.

## Installation et lancement

Décompresser à la racine, en remplaçant uniquement `site/app.js` et `site/style.css`. Ne pas toucher à `site/data/parcours-affectations.json` ni à `site/data/niveaux-manuel.json`.

```powershell
cd "C:\mycode\Ekole\Ekole_Pack_v10_GitHub_Moodle_202"
py -3 tools\ekole.py build
py -3 tools\valider_parcours.py
py -3 tools\ekole.py preview
```

Ctrl+F5 dans le navigateur. Pour régénérer les hypothèses (si le catalogue et le graphe sont présents) :

```powershell
py -3 tools\proposer_affectations.py
```

Pour **valider** une proposition, une personne compétente doit l'examiner puis l'inscrire explicitement dans la table éditoriale `parcours-affectations.json`, avec `preuves_attribution`. Il ne faut pas copier en bloc les 202 propositions comme faits approuvés.
