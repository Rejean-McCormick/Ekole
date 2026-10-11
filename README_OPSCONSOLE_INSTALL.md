# Installation — Ekole OpsConsole

Extraire cet **overlay directement à la racine de ton dépôt Ekole**. Il ne contient pas de dossier englobant.

Si tu as gardé le dossier indiqué précédemment :

```text
C:\mycode\Ekole\Ekole_Pack_v10_GitHub_Moodle_202\
```

Le ZIP ajoute `START_EKOLE_OPSCONSOLE.bat`, `opsconsole/`, `scripts/START_EKOLE_OPSCONSOLE.*` et `docs/09_OPSCONSOLE_EKOLE.md`. Les 202 Kristals, le catalogue, le portail, Moodle et les dépôts externes ne sont pas remplacés.

## Ouvrir

Double-cliquer sur `START_EKOLE_OPSCONSOLE.bat`, puis ouvrir `http://127.0.0.1:8766/` si le navigateur ne s'ouvre pas automatiquement.

Ou en PowerShell :

```powershell
cd "C:\mycode\Ekole\Ekole_Pack_v10_GitHub_Moodle_202"
py -3 opsconsole\ekole_ops.py --check
py -3 opsconsole\ekole_ops.py
```

Le site Ekole se lance séparément depuis le panneau, sur `http://127.0.0.1:8765/`.

## Fonctionnalités

Vue d'ensemble, inspection des 202 Kristals, lanceur des outils `verify`, `build`, `moodle-plan`, `pages-zip`, prévisualisation du site, simulation et copie vers **un répertoire statique local externe** avec confirmation, Git en lecture seule, état des ponts, journal de la session.

Pas de lancement à distance, pas de publication GitHub, pas d'écriture Moodle, pas d'exécution de commandes libres.

## Vérifier la console

```powershell
py -3 -m unittest discover -s opsconsole\tests -v
```

Documentation détaillée : `opsconsole/README.md` et `docs/09_OPSCONSOLE_EKOLE.md`.
