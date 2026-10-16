# Moteur Ekole — Mise à jour UX

La nouvelle interface fait la distinction entre moteur et corpus. Les parcours et cours mis en avant sont définis par le contenu, jamais par le moteur. Les trois extensions facultatives sont chargées depuis `/api/integrations/spek.json`, `/api/integrations/graphe.json` et `/api/integrations/activites.json`.

Le serveur ne livre que ces trois fichiers de ressources JSON **s'ils existent dans le dépôt connecté**. Ils restent exclusivement en lecture seule; aucun répertoire historique ni chemin quelconque n'est publié. L'espace éditeur garde son authentification et sa protection CSRF.

L'application affiche un module de cours à la fois et fournit des liens vers les modules voisins. Voir le rapport principal `RAPPORT_MEGA_UPDATE_3E.md` à la racine de l'archive de livraison.
