# Livraison overlay Ekole — affectations proposées v5

## Portée

Ce correctif ajoute un classement **provisoire** (ni approuvé ni conforme officiellement aux niveaux/étapes) des 202 cours dans les 6 années et 24 parcours d'étape. Il se pose sur l'overlay Ekole v4.1 et ne modifie ni les Kristals, ni Moodle, ni OpsConsole. Il conserve les 4 étapes de navigation (2 Automne, 2 Hiver) séparées des 3 bulletins officiels.

## Vérifications exécutées

- 8 tests Python : réussis sur la fusion `moodle.zip` + v4.1 + v5.
- Test de cohérence JavaScript en contexte Node : réussi (échantillon Mathématique 3e année et préséance des affectations manuelles).
- Test JavaScript du parcours v4.1 : réussi.
- Syntaxe de `site/app.js` : `node --check` réussi.
- `valider_parcours.py` : PASS pour les conteneurs (avec avertissement attendu car les **affectations manuelles/validées** sont vides ; ce validateur ne traite volontairement pas les brouillons).
- 202 IDs de propositions uniques ; 24 conteneurs non vides ; respect des 134 liens de préalables stricts et 6 années.
- Un changement fictif des `vague` de chaque cours ne change pas les propositions.
- `site/data/niveaux-manuel.json` et `site/data/parcours-affectations.json` non inclus : pas d'effacement des données locales.

## Limites

- Répartition pédagogique fondée en partie sur le rang des IDs, des hypothèses didactiques en français/mathématique et le graphe `requires`; **pas** sur une validation programme par année / par discipline.
- L'étape proposée est un emplacement de navigation, non une programmation annuelle officielle ou une période de bulletin.
- Aucune intégration Moodle ou qualification d'état Kristal v10 exécutée.
- Aucun test visuel automatisé en navigateur réel effectué pour la présente livraison.
- Revue humaine obligatoire avant de présenter les suggestions comme affectations fermes.

## Fichiers préservés
- `site/data/parcours-affectations.json` : non inclus, non modifié
- `site/data/niveaux-manuel.json` : non inclus, non modifié
- `kristals/` : non inclus, non modifié
- `moodle/` : non inclus, non modifié
- `opsconsole/` : non inclus, non modifié
