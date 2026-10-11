# Ekole v20 — Bordure colorée personnalisable

Compatible avec l’overlay Ekole v19. Extraire ce ZIP **à la racine `C:\mycode\Ekole`** et accepter le remplacement des fichiers du configurateur et de l’interface. Fermer puis relancer `LANCER_EKOLE_3_APPS.bat`.

Ouvrir `http://127.0.0.1:8766/cadres-images/` dans la session Ekole Enseignant. Choisir « **Bordure colorée** », puis la couleur grâce au sélecteur ou au champ hexadécimal. **Valeur par défaut : `#1e6864`**. L’aperçu est instantané. Cliquer sur « Enregistrer pour Ekole Élève ».

Les fiches Élève affichent une bordure de couleur autour des **images présentes uniquement**; les descriptions d’images absentes gardent leur style pointillé. Les images ne sont pas rognées et les miniatures sont inchangées.

**Aucune image, aucun Kristal et aucun fichier `site/eleve/data/cadres-images.json` n’est inclus** dans cet overlay : un choix v19 déjà enregistré est donc préservé. L’éditeur lit les anciennes configurations sans couleur en employant `#1e6864`. Une couleur invalide est rejetée, y compris côté serveur. L’export Élève existant fonctionne avec les mêmes fichiers de styles et de configuration.

Tests : `py -3 -m unittest discover -s tests -p test_ekole_cadres_images_v20.py -v`.
