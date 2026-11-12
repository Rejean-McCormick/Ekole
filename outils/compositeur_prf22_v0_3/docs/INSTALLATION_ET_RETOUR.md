# Installation prudente et retour arrière

## Racines cibles par défaut

- `C:\mycode\Ekole\ekole`
- `C:\mycode\Kristal\Arketype` (l'installateur détecte `arketype/` à l'intérieur si nécessaire)

Dans Ékole, seuls sont ajoutés : `outils/compositeur_prf22_v0_3/` et `LANCER_COMPOSITEUR_PRF22.cmd`.

Dans Arketype, seule est ajoutée `assemblages/situation-pedagogique-orchestrable.json`; deux fichiers JSON non normatifs sont enrichis de PRF-22 : `inventaires/profils-usage.json` et `inventaires/diagrammes-situes.json`. Les 19 archétypes originaux ne sont pas modifiés.

L'installateur vérifie toutes les destinations avant d'écrire; s'il trouve un fichier différent, ou une entrée PRF-22 conflictuelle, il **refuse** d'écraser. Les fichiers modifiés sont sauvegardés dans `%LOCALAPPDATA%\EkolePRF22Installer\<transaction>\backups` avec manifest SHA-256 avant/après.

## Ordre à utiliser

1. Exécuter `PREVISUALISER.cmd`. Lire la liste des écritures.
2. Exécuter `INSTALLER.cmd`.
3. Exécuter `VERIFIER.cmd`.
4. Ouvrir l'atelier avec le lanceur ajouté à Ékole.
5. En cas d'incompatibilité, fermer l'atelier puis lancer `RETOUR_ARRIERE.cmd`.

Le retour arrière refuse de restaurer une ancienne version si un fichier installé a changé depuis. C'est intentionnel : aucune nouvelle modification personnelle ne doit être écrasée. Il faut alors analyser ce conflit manuellement.

Une nouvelle exécution de l'installateur déjà installé est **idempotente** : il n'écrit rien si les fichiers et le profil correspondent exactement.

## Si l'ordinateur ne trouve pas `py`

Utiliser l'interpréteur Python 3 installé, en PowerShell :

```powershell
python .\installation\install.py --dry-run
python .\installation\install.py --install
python .\installation\install.py --verify
python .\installation\install.py --rollback
```

Le module Tkinter est nécessaire pour le GUI; le validateur CLI et l'installateur n'en ont pas besoin. `jsonschema` est **facultatif** pour la validation structurelle locale; pour activer la validation standard complète, l'installer séparément dans le Python qui lance l'atelier.
