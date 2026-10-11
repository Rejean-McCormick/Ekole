# EKole — PACK REUNI — LIRE EN PREMIER

Cette archive réunit deux livrables locaux :
- Ekole_Pack_v10_202_Kristals_Moodle_Polymorphe.zip (202 Kristals et plan de projection Moodle)
- Ekole_OpsConsole_Overlay_v0.1(1).zip (surface de pilotage locale Ekole)

## Où l'extraire (Windows)

Creer, si besoin, le dossier C:\mycode\Ekole\EKOLE_COMPLET\ puis EXTRAIRE LE CONTENU de cette archive directement dans ce dossier (sans sous-dossier ZIP additionnel).

Exemple :
C:\mycode\Ekole\EKOLE_COMPLET\README.md
C:\mycode\Ekole\EKOLE_COMPLET\kristals\
C:\mycode\Ekole\EKOLE_COMPLET\opsconsole\
C:\mycode\Ekole\EKOLE_COMPLET\START_EKOLE_OPSCONSOLE.bat

Pour utiliser un projet Ekole existant, faire une sauvegarde d'abord puis extraire dans sa RACINE, et non dans Moodle, ni dans UCKK Ops Console.

## Démarrer

Double cliquer sur START_EKOLE_OPSCONSOLE.bat (Python 3 nécessaire).
L'interface locale est à http://127.0.0.1:8766/
Le site Ekole est démarré séparément sur http://127.0.0.1:8765/

## Test

Dans PowerShell, à la racine du projet :
py -3 opsconsole\ekole_ops.py --check
py -3 -m unittest discover -s opsconsole\tests -v

## Limites

La console Ekole est un prototype LOCAL. Elle ne remplace pas la UCKK Ops Console de l'environnement principal, n'effectue aucune écriture Moodle réelle et ne publie pas de Kristals canoniques. L'alignement Moodle reste un plan et nécessite une intégration contrôlée. Les 202 workspaces ne sont pas des états Kristal v9/v10 officiellement qualifiés.

Sources : README_OPSCONSOLE_INSTALL.md, opsconsole/README.md, docs/09_OPSCONSOLE_EKOLE.md et docs/09_KRISTAL_MOODLE_POLYMORPHE.md.
