# Validation de l'overlay Ekole v9 — MiniLab

**Statut : prototype d'entraînement, révision pédagogique et tests visuels humains nécessaires.** Testé le 9 octobre 2026.

## Résultats exécutés

- **27 tests Python réussis** après fusion de l'archive `moodle.zip` avec l'overlay cumulatif v9 (Core, Élève, Enseignant, v7/v8/v9).
- **18 scénarios / 9 moteurs** vérifiés par le test JavaScript Node `tests/test_microlab_engine_v9.js` : solutions exactes, états initiaux non résolus, absence de mutation, bornes invalides rejetées.
- **JSON Schema Draft 2020-12** : contrat de catalogue et exemple de 18 scénarios valides.
- **Export Élève strict** : 19 fichiers, dont MiniLab, sans `data/cours/`, sans banque d'évaluation ou espace Enseignant.
- **API Enseignant** : requête non authentifiée sur `/api/labo-catalogue.json` → HTTP 401; cookie temporaire de test → HTTP 200.
- **Prévisualisation HTTP locale** du site Élève exporté : la racine, le MiniLab et les fichiers de moteur / catalogue répondent HTTP 200.
- **Contrôles de syntaxe** de tous les JavaScript du MiniLab exécutés avec `node --check`.

## Limites

- Un test visuel automatisé dans Chromium a été tenté; la navigation HTTP localhost y a renvoyé `ERR_BLOCKED_BY_ADMINISTRATOR`. **Aucun résultat de test visuel navigateur n'est revendiqué.** Vérifier sur Windows, mobile et avec clavier/lecteur d'écran.
- Les 18 scénarios sont **originaux et candidats**, non dérivés des corrigés du Kristal. Les associations facultatives aux cours de mathématique sont à revoir humainement.
- Aucun résultat d'enfant n'est stocké. Les réponses déterministes du labo sont accessibles côté client : n'en faire **aucun examen sécurisé**.
- Aucun appel réel SemantiK, Konstellation v10, Médiathèque ou Moodle n'a été exécuté par le laboratoire.
- Les fichiers Core existants peuvent contenir des corrigés : ne pas les publier sans isolation. Utiliser l'export Élève strict.
