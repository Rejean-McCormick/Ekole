# Moteur neutre Ekole v3

Ajouts : `visuals.py`, `publications.py`, API de brouillons/publications élèves distincte du dossier expert, contrôle manuel de publication des images et nouvel atelier enseignant.

- Dans un paquet déclarant `politique_publication: vues_separees`, l'API publique retourne uniquement `publications/eleve/<id>.json` ou une fiche « en préparation ». L'API Enseignant protégée fournit toujours les textes experts.
- Les autres dépôts sans cette politique conservent le comportement historique de lecture publique (compatibilité; à migrer lorsqu'ils ont des contenus enseignants distincts).
- `--edition` doit être explicitement activé pour les modifications; serveur toujours lié à `127.0.0.1`.
- Après remplacement d'une image, sa publication est annulée. Copies sauvegardées sous `.ekole-sauvegardes` du dépôt contenu.

Voir `RAPPORT_MEGA_UPDATE_3E_V3.md` dans le ZIP complet.
