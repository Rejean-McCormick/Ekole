# 03 — Konnaxion : projets collaboratifs, interactions et participation

**Décision :** Konnaxion est un **espace de coopération à part entière**. Dans Ékole, l'enfant peut y construire quelque chose avec d'autres, contribuer des ressources, solliciter de l'aide, choisir une orientation, partager et réfléchir à son travail. Orgo ne remplace pas cette dimension sociale.

## Capacités déjà identifiées

### keenKonnect / Konstruct

Le code du dépôt Konnaxion contient :

- `Project` — projet et cycle de vie général;
- `ProjectTeam` — membres et rôle de collaboration (`owner`, `collaborator`, `mentor`), distinct des personnages et des rôles de sécurité Orgo;
- `ProjectMessage` — messages dans un projet;
- `ProjectResource` — fichiers, liens et versions;
- `ProjectTask` — tâches natives Konnaxion (ne pas confondre avec les Tasks Orgo);
- `ProjectRating` — signal communautaire générique `+1/-1` (**ne pas utiliser pour noter des enfants**).

Les APIs et pages de projet existent dans le dépôt, mais les restrictions d'accès par défaut de certains endpoints **ne conviennent pas à des espaces scolaires privés**. Les parties « ouvertes en lecture » ne doivent pas être exposées directement à des mineurs; voir [08](08_SECURITE_ET_CONFIDENTIALITE.md).

### KonnectED

Le code contient `CertificationPath`, `Evaluation`, `PeerValidation`, `Portfolio`, `KnowledgeResource`, `LearningProgress`, ainsi que des routes API. Cela constitue une base réutilisable pour des vues de parcours, validations et portfolios, **pas** une connexion automatique avec les objectifs du programme québécois ni les notes Ékole.

Le `Portfolio` actuel possède un champ `items` associé à `KnowledgeResource` : il ne représente pas encore une collection canonique de preuves scolaires Ékole. Le raccordement doit référencer les travaux approuvés, sans dupliquer des dossiers privés.

### EkoH, votes et co-création

- **EkoH** : expertise contextuelle et règles de visibilité. Utilisation possible pour *proposer* des complémentarités sous contrôle de l'enseignant; **aucun classement public des enfants**, aucune note d'éthique, aucune inférence de personnalité.
- **Smart Vote et consultations** : capacités génériques de consultation et lecture pondérée selon contexte. En école primaire, un vote pour le thème d'un spectacle doit normalement être **simple, accessible et non pondéré par une réputation**. Choix transparent, droit de retrait et supervision.
- **Forums, contributions et mentorat** : des surfaces et modèles existent dans KonnectED; une fonctionnalité démontrée dans une interface ne vaut pas validation scolaire des droits de participation. La classe utilise uniquement le sous-ensemble autorisé.

## Une seule expérience collective, plusieurs objets propriétaires

Exemple *Le spectacle des histoires* :

1. **Décider ensemble.** Un projet Konnaxion de classe propose trois thèmes; vote supervisé, règles explicites, résultat partagé.
2. **Rassembler.** Les élèves déposent des mots-clés, images autorisées et idées dans les ressources du projet; tout média est modéré.
3. **Produire.** Orgo gère les tâches « écrire une scène », « vérifier le budget », « préparer les accessoires », « répéter » et leurs dépendances.
4. **Demander de l'aide.** Konnaxion relie les participants autorisés; une action d'entraide peut être attestée sans créer une nouvelle Task concurrente.
5. **Contribuer.** Les enfants partagent des extraits ou références de créations, avec auteur, droits, contexte et éventuelle co-création.
6. **Évaluer.** Ékole recueille observations, tentatives et preuves, puis l'enseignant valide ce qui a été appris.
7. **Constituer le portfolio.** L'élève choisit avec l'enseignant des éléments approuvés; Konnaxion peut en fournir une présentation contrôlée, sans publier le dossier scolaire.

## Modèle d'interaction minimum

Une interaction collaborative doit avoir :

`interaction_ref`, `session_ref`, `project_ref`, `actor_ref`, `target_ref?`, `purpose`, `kind`, `created_at`, `visibility`, `moderation_state`, `source_artifact_ref?`, `owner_receipt_ref`.

**Types utiles en classe :** question, réponse, aide sollicitée, aide offerte, ressource déposée, commentaire supervisé, choix/vote, proposition d'indice, rétroaction reçue et réflexion individuelle.

Une interaction n'est **pas** automatiquement une preuve de maîtrise : elle peut constituer une **observation** à examiner. L'enseignant doit pouvoir distinguer contribution individuelle, coécriture, aide reçue, aide apportée et simple présence.

## Conflits de propriété à résoudre

| Situation | Règle |
| --- | --- |
| Une tâche Orgo apparaît dans un projet Konnaxion | Afficher un lien et un état projeté; modifier par commande Orgo uniquement |
| Un projet Konnaxion natif a ses `ProjectTask` | Conserver leur propriétaire Konnaxion si aucun Orgo n'est impliqué |
| Un message annonce « c'est fini » | Message enregistré par Konnaxion; **ne change pas** seul l'état Orgo |
| Un élève reçoit plusieurs « j'aime » | Signal social, **pas** une note ni une preuve de compétence |
| Un membre est retiré de la séance | Révoquer les capacités de lecture/écriture dans chaque propriétaire; le cache mobile doit expirer |
| Une ressource est ajoutée au portfolio | Référence approuvée et audience validée, pas diffusion automatique |

## Optimisation produit : un adaptateur scolaire mince

Construire **une projection autorisée** des projets et des actions pertinentes, à partir des API propriétaires, plutôt qu'un nouveau « réseau social Ékole ». L'adaptateur ne possède ni les messages, ni les fichiers, ni les scores; il conserve des références, décisions d'accès et reçus pour l'expérience. Il peut servir plus tard de profil simplifié dans une usine ou un organisme, avec des critères de droits différents.

## Sources

`Konnaxion/backend/konnaxion/keenkonnect/models.py`, `api_views.py`; `backend/konnaxion/konnected/models.py`, `api_views.py`; `backend/konnaxion/ekoh/models/access.py`; `backend/konnaxion/smart_vote/models/consultation.py`; `Konnaxion_Worlds/docs/Technical-Reference/Worlds/08_ACCOUNTS_PERSONAS_EKOH_SMARTVOTE.md`.
