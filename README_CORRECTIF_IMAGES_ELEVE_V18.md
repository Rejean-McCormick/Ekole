# Ekole v18 — Corriger les images présentes mais invisibles sur les fiches Élève

## Symptôme reproduit
Le fichier `/eleve/assets/kristals/qc-pri-ma-012/concept.webp` s'ouvre directement, mais le cours `qc-pri-ma-012` continue d'afficher « Description de l’image » dans Découvrir.

## Cause et correctif
Dans `site/eleve/app.js`, l’image était à la fois masquée avec `hidden` et demandée avec `loading="lazy"`. Le navigateur peut ne jamais télécharger une image masquée, empêchant l'événement `load` de remplacer le texte. Le correctif précharge l'image sans la masquer et l'insère dans la fiche une fois chargée, en conservant la description si le fichier manque ou échoue.

`tools/compiler_visuels_kristals.py` publie désormais une révision SHA-256 de l'image dans le registre public. L'URL est indexée par cette révision pour éviter une ancienne copie du navigateur lorsque l'enseignant remplace l'image. Le chemin et le nom du fichier restent inchangés.

## Installation
1. Fermer les deux applications Ekole.
2. Extraire le ZIP à la racine `C:\mycode\Ekole`, en remplaçant les fichiers du correctif.
3. Relancer `LANCER_EKOLE_3_APPS.bat` (il recompilera le registre visuel).
4. Ouvrir `http://127.0.0.1:8765/eleve/?cours=qc-pri-ma-012`, puis faire **Ctrl+F5** une fois.

Ne pas réimporter les images existantes. Une image absente reste correctement remplacée par sa description.

## Tests facultatifs
```powershell
py -3 -m unittest discover -s tests -p test_kristal_images_cache_v18.py -v
node tests\test_kristal_images_visibles_v18.mjs
```

## Portée
Sur une copie Ekole + overlays v16/v17 : 186 tests Python et tests JS v16, v17, v18 réussis. Test de comportement image dans Chromium via document isolé réussi. La navigation HTTP du site complet depuis le navigateur automatisé a été bloquée par la politique de l’environnement ; valider l’affichage sur le navigateur Windows après installation.

Ce ZIP ne contient ni images, ni manifestes canoniques, ni nouvelle sélection de cours.
