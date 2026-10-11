# Ekole — Correctif ciblé Atelier d'images v16

## Installation (Windows)

1. Fermer `LANCER_EKOLE_3_APPS.bat` et les anciens serveurs Enseignant.
2. Faire une sauvegarde du dossier Ekole.
3. Extraire **ce ZIP à la racine** `C:\mycode\Ekole\`, là où se trouvent `enseignant-app\` et `tools\`.
4. Redémarrer `LANCER_EKOLE_3_APPS.bat`.
5. Dans Ekole Enseignant (port 8766), ouvrir « Atelier d'images · Prompts et import » et sélectionner un cours.

## Changements

- « Copier le prompt » devient « ✓ Prompt copié ! » pendant environ 3 secondes **seulement si la copie a réussi**. En cas d'échec, un message clair remplace le libellé.
- La prévisualisation utilise une URL `blob:` et la politique CSP du **serveur Enseignant uniquement** autorise ces miniatures temporaires. Aucune politique du site Élève n'est changée.
- Après un import confirmé par le serveur, la nouvelle image est ajoutée **dans la même fiche**, sans rechargement et sans détruire le formulaire. L'URL est rafraîchie avec l'empreinte du fichier pour éliminer le risque d'une vieille image en cache.
- Un bouton « Actualiser les images » permet de relire manuellement le manifeste de l'atelier, sans recharger tout Ekole.
- La recompilation existante continue à copier l'image validée dans `site/eleve/assets/kristals/`. Le serveur Enseignant reste sur `127.0.0.1:8766` et vérifie toujours session, origine, CSRF et emplacement déclaré dans le Kristal.

## Tester

À la racine d'Ekole :

```powershell
py -3 -m unittest discover -s tests -p test_ekole_image_editor_v16.py -v
node tests\test_ekole_image_editor_v16.mjs
```

Vérifications réalisées sur copie du dépôt : 173 tests Python réussis (ensemble du dépôt), test d'interaction JavaScript réussi et requête HTTP de l'image nouvellement enregistrée réussie. Le rendu sur le navigateur Windows de l'utilisateur n'a pas été reproduit ici.

## Portée

Le correctif touche exclusivement l'atelier **Enseignant**. Une page Élève **déjà ouverte** dans un autre onglet n'est pas automatiquement rafraîchie en temps réel; l'image est disponible dès la consultation suivante de la fiche ou après une actualisation de cet onglet. Il n'y a ni génération d'image, ni changement des connaissances canoniques.
