# 01 — Cartographie des composants et propriété des données

**Principe :** on réutilise les capacités attestées et on établit des *contrats de correspondance* là où les frontières se croisent. Le fait qu'une table ou une page existe dans un dépôt n'implique pas que son intégration scolaire soit terminée.

## Inventaire fonctionnel

| Composant | Capacité vérifiée dans les sources | Ce qu'il ne doit pas devenir |
| --- | --- | --- |
| **Kontexte** | 17 missions dont six nouvelles, 38 rôles, trames, stations et liens pédagogiques candidats | Moteur d'exécution Orgo ou registre des enfants |
| **Ékole** | Portail enseignant, aperçu synthétique Tandem, activités, parcours par rôle | Base des états Orgo ou réseau de messages concurrent |
| **Ékole Québec** | Références, superpositions curriculaires, corpus pour la 3e année | Attribution de notes sans validation |
| **Inkuisite** | Exercices, tentatives, correction locale | Identité scolaire universelle ou registre d'autorité des Worlds |
| **Kompose** | Préparation des équipes/rôles et projections d'allocation | Assignation réelle sans approbation ou droits |
| **Akor** | Intentions et collaboration pédagogique, liens entre missions et opérations | Source des autorisations ou duplicata des Tasks |
| **Orgo_Worlds** | World, releases, membership et isolation pour Orgo | Serveur de projet social |
| **Orgo** | Case, Task, affectations, dépendances, état et orchestration opérationnelle | Interprétation scolaire de la maîtrise |
| **Konnaxion_Worlds** | World/WorldRelease, personas, permissions et isolation Konnaxion | Alias d'un World Orgo |
| **Konnaxion / keenKonnect** | `Project`, `ProjectTeam`, `ProjectMessage`, `ProjectResource`, `ProjectTask`, `ProjectRating` | Double maître des tâches déjà pilotées par Orgo |
| **Konnaxion / KonnectED** | `Evaluation`, `PeerValidation`, `Portfolio`, `LearningProgress`, `KnowledgeResource` | Bulletins scolaires automatiques ou accès public aux évaluations mineures |
| **Konnaxion / EkoH** | Expertise contextualisée, contrôles de visibilité; **Smart Vote** distinct | Classements publics ou scores universels des enfants |
| **Kor** | Projection Android de Konnaxion/Orgo, QR, notifications, réponses, hors ligne | Nouvelle source d'état de Task ou de permission |
| **Kamel** | Cartes, decks, assemblage, mise en page et impression | Générateur d'autorité de QR ou registre de réussite |
| **Interaction Kernel** | Profils, enveloppes, référence, corrélation, reçus dans les intégrations adoptées | Propriétaire des données métiers |
| **Capsule Manager** | Empaquetage, validation, installation de packages Konnaxion et profils de déploiement | Autorité sur l'apprentissage ou la collaboration |

**Karacter et Kolor** peuvent enrichir le personnage et son habillage, sans modifier les permissions, les compétences ou les appartenances réelles.

## La règle du propriétaire unique

| Objet | Propriétaire canonique dans le pilote scolaire | Copies permises |
| --- | --- | --- |
| Trame, mission, rôle-métier, consigne, indice d'auteur | Kontexte | Version épinglée, résumé autorisé |
| World opérationnel, release, membership Orgo | Orgo_Worlds | Référence opaque et statut vérifié |
| Case/Task, statut d'exécution, dépendance, affectation | Orgo | Vue à lecture seule chez Konnaxion/Kidaxion/Ékole |
| World collaboratif et release Konnaxion | Konnaxion_Worlds | Référence externe explicitement liée |
| Projet, équipe, message, fil, ressource, consultation | Konnaxion | Projection minimale et liens dans Ékole |
| Tentative d'exercice | Inkuisite, sous politique Ékole | Événement de preuve et identifiant opaque |
| Décision d'évaluation scolaire, maîtrise, recommandation | Ékole / enseignant | Vue du statut autorisée dans Kidaxion ou le portfolio |
| Présentation de portfolio Konnaxion | KonnectED | Références à preuves approuvées, selon audience |
| Présentation physique ou mobile | Kamel / Kor / Web | Cache et mise en page seulement |

## Attention : `ProjectTask` et `Task`

Konnaxion a **déjà** un modèle `keenkonnect.ProjectTask` avec son état et son assignation. Orgo a **déjà** des Tasks opérationnelles. **Il serait incorrect de synchroniser les deux en écriture bidirectionnelle.**

- **Projet porté uniquement par Konnaxion** : `ProjectTask` peut rester son objet de travail canonique, si aucun contrat Orgo n'a été choisi.
- **Projet/aventure exécuté par Orgo** (notre pilote Ékole) : la Task Orgo est canonique. L'espace Konnaxion affiche des références/projections en lecture seule; toute commande de modification passe par Orgo, qui répond par un statut autoritatif.
- Une correspondance `konnaxion_project_ref` → `orgo_case_ref` ou `orgo_task_ref` doit être explicite, contextualisée et versionnée. **Pas de création automatique d'une seconde ProjectTask modifiable** en parallèle.

De même, `konnected.Evaluation` et `konnected.PeerValidation` ne deviennent pas automatiquement une évaluation scolaire. **Ékole** conserve la décision pédagogique; la publication dans KonnectED est séparée, si la politique de classe l'autorise.

## Optimisations retenues

1. **Moins de copies :** stocker des références croisées, versions et résumés filtrés; éviter de recopier messages, fichiers et scores dans chaque moteur.
2. **Moins de couplage :** les interfaces consomment une projection d'actions permises; elles n'orchestrent pas la mission.
3. **Évolution sûre :** chaque dépôt expose une référence stable; les adaptateurs traduisent les contrats sans inventer des permissions.
4. **Catalogue évolutif :** une mission Kontexte est préparée uniquement lorsqu'une séance est créée, sans charger toute la banque dans Orgo.
5. **Accès scolaires privés :** les points d'API Konnaxion existants doivent être isolés et durcis avant réutilisation, voir [08](08_SECURITE_ET_CONFIDENTIALITE.md).

## Sources de code principales

- `Konnaxion/backend/konnaxion/keenkonnect/models.py` (Project, ProjectTask, ProjectMessage, Team, Resource).
- `Konnaxion/backend/konnaxion/konnected/models.py` (Evaluation, PeerValidation, Portfolio, LearningProgress).
- `Konnaxion/backend/konnaxion/ekoh/models/scores.py` et `access.py`.
- `Konnaxion_Worlds/docs/Technical-Reference/Worlds/04_DATA_OWNERSHIP_MATRIX.md`.
- `Orgo/apps/api/src/orgo/modules/work/work.service.ts`, `Orgo_Worlds/apps/api/src/orgo/modules/worlds/worlds.service.ts`.
- `Kor/adr/0020-mobile-projection-of-konnaxion-orgo.md`.
