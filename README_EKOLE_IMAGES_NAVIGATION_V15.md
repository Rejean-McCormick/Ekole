# Ekole v15 — Atelier d'images et navigation des étapes

**À extraire directement à la racine** du dépôt Ekole v14. Aucune migration des affectations, aucun remplacement des fichiers canoniques Kristal, aucun changement des banques de réponses.

## Les quatre corrections

1. **Enseignant / port 8766** : onglet « Atelier d’images · Prompts et import » et fiches cours. Chaque ressource visuelle provenant d'un manifeste Kristal propose le prompt à copier et une zone de glisser-déposer (ou un bouton pour sélectionner un fichier image téléchargé de ChatGPT). Formats source acceptés PNG/JPEG/WebP, maximum 12 Mo. Conversion en WebP/PNG/JPEG, largeur maximale réglable (768, 1024, 1536 ou 2048 px), conservation des proportions. Le fichier est nommé automatiquement selon le slot du Kristal et installé dans `kristals/<id>/experience/images/<slot>.<extension>`. Recompilation automatique de `site/eleve/data/kristals-visuels.json` et de l'image publique. Le remplacement est **opt-in** avec copie de l'ancien fichier dans `archives/ekole-images/`.
2. **Libellés** : les quatre périodes pédagogiques sont nommées **Étape 1, Étape 2, Étape 3, Étape 4**. Les métadonnées des deux saisons (Automne et Hiver) restent séparées. Ces étapes ne sont pas les trois bulletins scolaires officiels.
3. **Élève** : si l'illustration du Kristal n'existe pas, seul le **texte alternatif / la description du concept** apparaît à sa place, sans champ de prompt, chemin de fichier, ni bouton de copie. L'Enseignant garde les prompts complets. Idem dans les micro-mondes v12 et le lecteur encyclopédique autonome.
4. **MiniLab** : `.../eleve/labo/?outil=aire-cour&annee=5&cours=qc-pri-ma-028` affiche désormais un retour vers la fiche `qc-pri-ma-028` et un accès direct au parcours de 5e année, même depuis un défi ouvert directement. Le contexte de cours est conservé lors de la navigation vers d'autres défis recommandés.

## Installation Windows

1. Sauvegarder le dépôt.
2. Extraire ce ZIP à sa racine, par-dessus le pack v14 (dossiers `site`, `tools`, `enseignant-app`).
3. Vérifier Pillow : `py -3 -c "import PIL; print(PIL.__version__)"`. Si absent : `py -3 -m pip install Pillow`.
4. Fermer l'ancien serveur Enseignant, puis relancer `LANCER_EKOLE_3_APPS.bat`. Le launcher reconstruit la vue Élève et relance l'Enseignant avec ses nouvelles routes.
5. Ouvrir **Ekole Enseignant** dans l'onglet que le lanceur ouvre sur le port 8766, choisir « Atelier d’images · Prompts et import », filtrer par cours et déposer un fichier local. Ne pas essayer de glisser une *URL* depuis un autre site : il faut le **fichier téléchargé**.
6. Rafraîchir Ekole Élève avec **Ctrl+F5** pour voir l'image.

## Important pour la sécurité

- La réception d'images est **uniquement** assurée par le serveur **local Enseignant**, protégé par sa session temporaire, un jeton CSRF et une vérification d'origine. Le serveur Élève (8765) ne possède aucune route d'import.
- Seuls les **emplacements déjà déclarés dans le manifeste** `RESSOURCES_VISUELLES.json` d'un Kristal complet peuvent recevoir une image. Les deux fiches sans Kristal source ne sont pas modifiables par ce canal.
- Les fichiers sont **réencodés par Pillow** (sans conserver les métadonnées EXIF), contrôlés en format/dimensions, et les noms sont dictés par les IDs du Kristal. Le dépôt d'une image est une action d'auteur, **pas une approbation historique, culturelle ou pédagogique**. Vérifier les droits et l'exactitude avant publication scolaire.
- Serveur Enseignant local uniquement, **pas une authentification multiutilisateur de production**.
- Les prompts complets demeurent dans les données de la couche visuelle compilée pour compatibilité v14; leur **affichage et leur copie** ont été supprimés des écrans Élève. Ne pas traiter ces métadonnées comme secrètes dans une exportation publique.

## Vérification

```powershell
py -3 -m unittest discover -s tests -p test_ekole_image_editor_v15.py -v
py -3 -m unittest discover -s tests -p test_ekole_v15_ui.py -v
```

Ces tests couvrent l'authentification, l'origine, le CSRF, la collision, le remplacement sauvegardé, les noms de fichiers, la conversion réelle, les libellés, les descriptions et la navigation. Le test ergonomique en navigateur Windows/tablette reste à exécuter localement.
