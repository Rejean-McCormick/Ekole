# Ekole v21 — Gestionnaire d'images pédagogiques

## Installation

1. Fermer les serveurs Ekole et sauvegarder le dépôt, particulièrement les images personnalisées.
2. Extraire **ce ZIP à la racine `C:\mycode\Ekole\`**, au même niveau que `site/`, `tools/`, `enseignant-app/` et `kristals/`.
3. Relancer `LANCER_EKOLE_3_APPS.bat`.
4. Dans la session Enseignant ouverte par le lanceur, ouvrir **« Album et inventaire des images »**, ou naviguer vers `/images-album/` sur le port 8766 avec la session Enseignant active.

## Fonctionnement

- Inventaire des **emplacements déclarés dans les 202 cours**, avec état issu du disque et de la projection Élève. Les images autonomes hors des manifestes visuels des cours ne sont pas encore administrées dans cet album.
- Filtres **année proposée, matière, cours, emplacement, statut, recherche libre**. Vue grille/liste avec pagination, export CSV de la sélection.
- Une vignette ouvre les détails : **image actuelle ou description**, prompt intégral et code `EKOLE-IMG-...` (la consigne précise de ne pas dessiner ce code), copie, dépôt d'une nouvelle image, format WebP/PNG/JPEG, largeur et suppression.
- Avant l'enregistrement, l'aperçu local utilise le fichier choisi; après, la fiche et l'inventaire se rafraîchissent. Remplacer une image requiert une confirmation explicite. Les anciennes images sont sauvegardées dans `archives/ekole-images/`.
- **Cadres :** les sept styles v20, taille et couleur de bordure `#1e6864` modifiables et prévisualisables directement dans les détails. Le réglage v21 est **global à l'espace Élève**, comme la v20, et se sauvegarde via `/api/cadres-images.json`; pas encore de cadre spécifique par image.
- **Synchroniser avec Ekole Élève** reconstruit la projection visuelle et les fichiers publics depuis les sources Kristal, utile après une restauration ou une copie manuelle. Ne génère aucune image.
- Les deux cours dont la couche visuelle est encore provisoire sont visibles mais **l'import y est désactivé**, faute de manifeste canonique à mettre à jour.
- Les images non déclarées trouvées dans les dossiers des cours sont comptées comme fichiers à vérifier et **jamais supprimées automatiquement**.

## Sécurité et limites

L'album, les prompts complets et les commandes d'import/suppression sont servis uniquement par la **session locale Enseignant** sur `127.0.0.1:8766`. Le CSRF et l'Origin sont contrôlés côté serveur; les chemins d'import correspondent à des emplacements autorisés par un manifeste Kristal. Aucune nouvelle ressource de cet éditeur n'est ajoutée à l'export statique Élève. Ce n'est pas une authentification de production sur réseau scolaire.

L'état de l'album reflète les **fichiers de l'installation sur laquelle Ekole tourne**, pas les images présentes dans le snapshot utilisé pour développer l'overlay. Les années proposées restent à confirmer pédagogiquement. Les images historiques ou mathématiques doivent toujours être relues avant publication.

## Tests

```powershell
py -3 -m unittest discover -s tests -p test_ekole_images_album_v21.py -v
```

`node --check enseignant-app\images-album\app.js` contrôle la syntaxe du script.

Les tests HTTP, les tests Python et le contrôle JavaScript ont été exécutés sur une copie du dépôt. L'ouverture visuelle dans Chromium a été bloquée par l'environnement d'évaluation; vérifier l'apparence sur Windows.
