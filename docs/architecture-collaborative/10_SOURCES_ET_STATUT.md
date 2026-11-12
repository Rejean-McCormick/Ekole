# 10 — Traçabilité : sources inspectées, faits et limites

**Audit documentaire : 11 novembre 2026.** Sources : snapshots joints dans cette conversation, en particulier les nouvelles archives `znapshot_Konnaxion_11111324.zip`, `znapshot_Konnaxion_Worlds_11111323.zip`, `znapshot_Konnaxion_Capsule_Manager_11111325.zip`, `docs.zip`, plus `znapshot_kor_11111301.zip`, `znapshot_Kamel_11111301.zip`, les snapshots Ékole/Orgo/Kontexte et les overlays des lots 1 et 2. **Aucun service réel ni compte scolaire n'a été interrogé.**

## Sources de première main

| Sujet | Chemin source / statut |
| --- | --- |
| Projet Konnaxion, tâches, ressources, équipes, messages | `Konnaxion/backend/konnaxion/keenkonnect/models.py` — **code présent** |
| Routes et permissions Konnaxion projets | `Konnaxion/backend/konnaxion/keenkonnect/api_views.py` — **code présent; restrictions scolaires non vérifiées** |
| Évaluation, validation par les pairs, portfolio | `Konnaxion/backend/konnaxion/konnected/models.py`, `api_views.py` — **code présent, intégration Ékole absente** |
| EkoH et visibilité | `Konnaxion/backend/konnaxion/ekoh/models/scores.py`, `models/access.py`, `models/privacy.py` — **code présent; usage jeunesse à restreindre** |
| Consultation et Smart Vote | `Konnaxion/backend/konnaxion/smart_vote/models/consultation.py` et documentation associée — **capacité générique, pas vote scolaire prêt** |
| Isolation collaborative | `Konnaxion_Worlds/docs/Technical-Reference/Worlds/00_CANONICAL_SPEC.md`, `04_DATA_OWNERSHIP_MATRIX.md`, `08_ACCOUNTS_PERSONAS_EKOH_SMARTVOTE.md` — **architecture et runtime à qualifier pour le pilote** |
| Universes Konnaxion | `docs.zip/docs/KX_UNIVERSE_PACK_V1.md`, `STANDARD_OVERVIEW.md` — **composition/World releases, pas source d'une séance Orgo** |
| Packaging Konnaxion | `Konnaxion_Capsule_Manager/docs/DOC-20_Konnaxion_Package_Types_and_Artifact_Lifecycle.md` — **déploiement, non propriétaire des projets** |
| Présentation mobile | `Kor/adr/0020-mobile-projection-of-konnaxion-orgo.md`, `docs/04_BOUNDARIES_AND_OWNERSHIP.md`, `docs/10_MANDATE_QR.md` — **projection et QR, pas portail élève terminé** |
| Cartes imprimables | `Kamel/docs/06-cartes-et-editions.md`, `docs/14-securite-gouvernance-et-publication.md` — **rendu/édition, pas admission QR Orgo** |
| Orgo / Orgo_Worlds | `Orgo/apps/api/src/orgo/modules/work/work.service.ts`, `Orgo_Worlds/apps/api/src/orgo/modules/worlds/worlds.service.ts` — **moteurs propres, session scolaire non admise** |
| Missions et personnages | `Kontexte/data/missions/*.json`, `data/roles/*.json`, `docs/ekole-orgo/` — **17 missions, 38 rôles après overlays** |
| Ékole et preuves | `ekole/activite_locale.py`, `tandem/projection.py`, `docs/PREUVES_ET_PROGRESSION.md`; `Inkuisite` — **briques locales, pas longitudinal complet** |
| Kidaxion, lot 2 | `Konnaxion/frontend/lib/kidaxion-intents.mjs` (overlay lot 2) — **constructeur de demandes non autoritatives, pas UI ni serveur scolaire** |
| Préparation Orgo | `Orgo_Worlds/world-packs/ekole-fete-sorciere` (overlay lot 2) — **revue synthétique des 11 tâches, pas création runtime** |

## Résultats conservés des lots antérieurs

- Overlay documentaire v2 Ékole : 7 documents dans `docs/`, installation confirmée par journal utilisateur.
- Lot coordonné 1 : 23 fichiers répartis dans 9 dépôts, empreintes vérifiées par journal utilisateur; audit en lecture seule : 17 missions, 92 étapes, 38 rôles, 7 intentions synthétiques.
- Lot 2 : 16 fichiers vérifiés par journal utilisateur, 55 liens pédagogiques **candidats** dans 7 missions, garde-fous structurés pour les 10 missions historiques et pack de revue de la fête. Une validation structurelle ne vaut ni approbation de compétence ni admission runtime.

## Décisions de conception nouvellement proposées

1. **Liaison de séance** entre contexte Ékole, World Orgo, World Konnaxion et projet Konnaxion, sans fusion des identifiants. Non implémentée.
2. **Une seule autorité de tâche** par projet : Orgo pour l'aventure Ékole; Konnaxion peut rester propriétaire des tâches de projets qui lui sont propres. À ratifier dans les adaptateurs.
3. **Portfolio à double perspective** : décision pédagogique privée Ékole; exposition choisie et contrôlée de références dans KonnectED. Adaptateur absent.
4. **Kidaxion multicanal** : présentation Web/Chromebook, Kor/Android et Kamel/papier, tous adressant des propriétaires métiers existants. Portail Kidaxion non opérationnel.
5. **Passerelle jeunesse de sécurité** : identité scolaire vérifiée, contrôle d'audience, modération, querysets privés. Bloquant avant données réelles.

## Principaux problèmes ouverts

- `ProjectMessageViewSet` et d'autres `ViewSet` Konnaxion exposent une configuration `IsAuthenticatedOrReadOnly`; **audience scolaire fermée non démontrée**.
- Séances, rôles, identités et World memberships ne sont pas liés en runtime de bout en bout.
- Deux modèles de tâches (`ProjectTask` et Orgo `Task`) exigent un mode maître/miroir explicite.
- Les 55 liens pédagogiques candidats attendent une revue; les dix missions historiques non sûres restent bloquées.
- Le modèle KonnectED `Portfolio.items` est une relation vers `KnowledgeResource`, pas directement vers les preuves Ékole.
- Kamel ne génère pas les QR de tâche autorisés; Kor n'est pas une interface scolaire Chromebook universelle.

## Règle de lecture de cette documentation

**Présent dans le code** = classe, route ou service observable. **Documenté** = intention ou contrat dans un document du dépôt. **Simulé** = vérifié sur fixture de démonstration. **Proposé** = conception nouvelle. **Opérationnel avec des enfants** = exige une recette intégrée et une approbation institutionnelle, **non démontrées ici**. Ne jamais confondre ces états.
