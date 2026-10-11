# Ekole v12 — plateforme intégrée, version candidate technique

**Ce qui est finalisé :** architecture des trois applications, conservation du Core, projection contrôlée Élève, bibliothèque MiniLab v9, cinq Kristals pilotes enrichis v11, sept nouveaux micro-mondes v12, atelier d'auteur local, couche conceptuelle d'images non générées, audit et sauvegardes, 202 cadres de transformation source-ancrés.

**Ce qui n'est PAS finalisé :** validation pédagogique terrain des 202 cours; validation officielle des cinq pilotes; sources complètes de deux cours (`qc-pri-fr-004`, `qc-pri-ma-005`); vraie fédération Konstellation v10; authentification multi-utilisateurs; certification de maîtrise; tests systématiques d'accessibilité avec enfants et lecteurs d'écran. **Ne pas déployer comme école publique à ce stade.**

## Installation à la racine du dépôt

1. Sauvegarder le dépôt. Extraire **ce ZIP** à la racine qui contient `site/`, `tools/` et `kristals/`. Les chemins internes n'ont pas de dossier enveloppe. C'est cumulatif v7–v12.
2. Si certains Kristals originaux manquent, **simuler d'abord** :

   `py -3 tools\installer_sources_200_v12.py --root .`

   Puis restaurer uniquement les fichiers manquants :

   `py -3 tools\installer_sources_200_v12.py --root . --apply`

   Le fichier `archives/KRISTALS_200_REFERENCES_ORIGINALES.zip` est la copie fournie des 200 dossiers sources. Aucune source existante n'est écrasée. Les deux références non disponibles restent en attente.
3. Reconstruire les projections :

   `py -3 tools\synchroniser_ekole_apps.py --root .`

4. Lancer `LANCER_EKOLE_3_APPS.bat`, puis **Ctrl+F5**.

## Accès

- **Ekole Core :** `http://127.0.0.1:8765/` (navigation et administration locale existantes).
- **Ekole Élève :** `http://127.0.0.1:8765/eleve/`; micro-mondes `.../eleve/mondes-v12/`.
- **Ekole Enseignant :** serveur local temporaire `127.0.0.1:8766`, bouton **Atelier de conception v12** après ouverture de la session locale.
- **Konstellation Light :** application indépendante sur `127.0.0.1:4177` quand elle est lancée. Une vraie collection v10 doit être vérifiée avant publication.

## Contrats de vérité pédagogique

Les fichiers `kristals/<ID>/experience/CADRE_PEDAGOGIQUE_V12.json` constituent **200 plans de conception individualisés** alignés sur les objectifs, concepts et preuves originaux. Ils ne sont pas automatiquement approuvés. Les cinq `ATELIERS_V12.json` contiennent sept activités complètes. Les scripts `tools/compiler_mondes_v12.py` et `tools/qualite_ekole_v12.py` appliquent des contrôles sur la compilation et les statuts.

- Aucun micro-monde n'émet une décision de maîtrise; tous les retours sont formatifs et inspectables depuis le navigateur.
- Les dossiers enseignant, banques d'items, grilles, annotations et corrigés ne sont pas dans la projection publique Élève.
- L'image conceptuelle est **une description sans style**. Si le fichier est absent, son prompt intégral reste visible. Si le fichier est présent, il ne devient public qu'après approbation manuelle, déclaration de droits, texte alternatif et vérification d'empreinte dans `experience/REVUE_IMAGES_V12.json`. L'illustration ne remplace pas le rendu déterministe des éléments évalués.
- Le plan d'auteur téléchargé doit être réimporté par `tools/appliquer_plan_v12.py` après revue (dry-run par défaut, `--apply` sauvegarde et écrit). Ce flux ne peut pas créer une approbation institutionnelle.

## Qualité et publication

`py -3 tools\qualite_ekole_v12.py --root .` — rapport sur les 202 références.

`py -3 tools\qualite_ekole_v12.py --root . --strict` — **échoue volontairement** tant que les cours ne satisfont pas le contrôle institutionnel.

`py -3 -m unittest discover -s tests -p "test_ekole_v12*.py"` — tests v12.

`node tests\test_mondes_v12.js` — états et erreurs des mini-mondes.

`py -3 tools\export_ekole_eleve_v8.py --root . --out C:\chemin\dossier-nouveau` — export public strict sur une destination neuve, hors dépôt.

Le Core actuel contient encore des ressources enseignants : **ne pas publier le dossier `site/` entier**. Moodle demeure facultatif; les tests historiques nécessitant `kristal.workspace.json` sont hors de portée tant que ces fichiers ne sont pas présents.

## Injecter ultérieurement une image manuellement créée

1. Déposer un `.webp`, `.png` ou `.jpg` au chemin indiqué par `image_path` dans `ATELIERS_V12.json`. Si le fichier manque, **le texte du prompt reste visible intégralement**.
2. Examiner son exactitude pédagogique, ses droits, son texte alternatif et ses dimensions (120 à 4096 pixels par axe).
3. Exécuter :

   `py -3 tools\revoir_image_v12.py --root . --kristal qc-pri-ma-012 --scenario fractions-2-5-multisupport --droits "Création autorisée par ..." --alt "Description accessible du contexte représenté" --apply`

4. Reconstruire avec `py -3 tools\synchroniser_ekole_apps.py --root .`.

Le compilateur calcule l'empreinte du contenu : si l'image est ensuite remplacée ou retouchée, la nouvelle image **ne se publie pas** tant que la revue n'est pas renouvelée.
