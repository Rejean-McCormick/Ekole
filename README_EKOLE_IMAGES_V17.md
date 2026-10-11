# Ekole v17 — Supprimer une image et identifier son prompt sans inscrire le code dans l'illustration

Overlay à **extraire à la racine** de `C:\mycode\Ekole\` après Ekole v16.
Il modifie l'atelier Enseignant seulement, son serveur local et les tests associés. Il ne fournit aucune image et ne remplace aucun Kristal canonique.

## Fonctionnement

- **Effacer l'image** apparaît dans chaque emplacement d'illustration déjà occupé de l'atelier Enseignant (port 8766). Confirmation obligatoire, avec sauvegarde privée du fichier original dans `archives/ekole-images/<cours>/` avant toute suppression.
- La suppression régénère `site/eleve/data/kristals-visuels.json`, retire les copies publiques identiques de l'image supprimée, et remplace **immédiatement** la vignette Enseignant par le cadre sans image. Les autres fichiers, notamment les ressources personnalisées différentes, ne sont pas effacés.
- Le bouton est désactivé lorsqu'aucune image n'est installée. Après une nouvelle installation il devient disponible sans actualiser la page.
- Le prompt copié contient désormais une **référence stable de production**, par exemple `EKOLE-IMG-QC-PRI-MA-028-CONCEPT`. Le prompt précise que cette référence est **hors image** et ne doit pas être dessinée, ni devenir une étiquette ou un filigrane.
- Ce code est calculé dans l'atelier Enseignant à partir du Kristal et de l'emplacement, et n'est pas ajouté à l'interface Élève ni aux pixels par Ekole.

> Un générateur d'image externe peut ignorer une consigne de non-affichage du code. **Vérifier visuellement l'image produite avant de l'installer**; Ekole ne prétend pas détecter automatiquement un code écrit dans ses pixels.

## Installation (Windows)

1. Fermer les serveurs Ekole et faire une sauvegarde si des modifications manuelles récentes sont importantes.
2. Extraire ce ZIP dans `C:\mycode\Ekole\` en conservant les répertoires `enseignant-app/`, `tools/` et `tests/`.
3. Relancer `LANCER_EKOLE_3_APPS.bat` et ouvrir l'atelier d'images du portail Enseignant (port 8766).
4. Si l'ancienne version reste en cache, utiliser `Ctrl+F5`.

## Vérification

```powershell
py -3 -m unittest discover -s tests -p "test_ekole_image_editor_v17.py" -v
node tests\test_ekole_image_editor_v17.mjs
```

Le serveur de suppression exige la **session Enseignant locale**, un jeton CSRF, l'origine locale et la confirmation explicite. La sauvegarde est hors de `site/eleve`. Les anciennes images des onglets Élève déjà ouverts nécessitent un rafraîchissement de ces onglets.

## Portée

Cet atelier gère les **emplacements déclarés des Kristals de cours** (`qc-pri-...`). Les illustrations des Kristals encyclopédiques autonomes qui ont leur propre format documentaire demandent un branchement distinct. Aucun contrôle culturel ou pédagogique automatique n'est prétendu.
