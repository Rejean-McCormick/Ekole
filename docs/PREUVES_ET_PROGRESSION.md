# Ékole : preuves, réalisations et recommandations pédagogiques

> **Révision d’architecture — 11 novembre 2026 :** cette page historique est conservée pour ses détails du pilote. La référence transversale actuelle est [Architecture collaborative et interfaces humaines](architecture-collaborative/00_LIRE_EN_PREMIER.md) : Konnaxion y est traité comme **propriétaire des projets, équipes, messages, ressources et portfolios**, Orgo comme propriétaire des tâches des aventures qu’il exécute, et Ékole comme responsable des décisions pédagogiques. Une fonction documentée ou simulée n’est pas nécessairement en production.


## 1. Règle fondamentale

**Une tâche Orgo terminée n'est jamais, à elle seule, une preuve de maîtrise scolaire.** Orgo sait *ce qui a été coordonné et accompli*; Ékole doit savoir *ce que l'enfant a réellement essayé, expliqué, compris et transféré*. Deux enfants ayant contribué à la même production collective peuvent présenter des apprentissages différents.

Le référentiel proposé dans `Kontexte/docs/ekole-orgo/04_REFERENTIEL_PREUVES_ET_RAPPORTS.md` distingue notamment `encountered`, `practiced`, `demonstrated`, `mastery_level`, `validation_status` et `transfer`. Il décrit les objets de conception `EvidenceLog`, `CurriculumMap` et `CurriculumReadModel`. **Le fait qu'ils soient documentés ne prouve pas qu'un registre longitudinal élève soit disponible dans Ékole Core.**

## 2. Vue d'ensemble d'une preuve proposée

Une observation pédagogique devrait pouvoir associer :

- une **identité d'élève vérifiée** dans le service scolaire sécurisé, non dans un JSON public;
- une référence de **séance, World, mission, étape et tâche** (sans copier le contenu privé du World);
- une référence d'**objectif/curriculum** existant dans Ékole, et le critère réellement observé;
- une **tentative** et son résultat : nombre d'essais, aide reçue, autonomie, contexte;
- un **artefact ou constat observable** (réponse, mesure, explication, production), filtré selon les règles de confidentialité;
- le **mode de validation** (`human_review`, pratique déterministe, etc.) et la décision de l'enseignant;
- une **date** et une provenance vérifiable permettant de réviser la conclusion.

Ce schéma est un **contrat conceptuel** à faire adopter et implémenter par Ékole; les noms des champs ci-dessus ne doivent pas être présentés comme une API déjà publiée.

## 3. Exemples

**La Fête de la sorcière — papier à invitations.** Deux personnages rassemblent des données : 6 invitations, 2 invitations/feuille, 2 feuilles disponibles. Une tâche commune peut être terminée lorsque le groupe trouve qu'il manque une feuille. Ékole doit distinguer : qui a lu les données, qui a fait le calcul, qui a expliqué la solution, qui a reçu une aide, puis les compétences démontrées par chaque enfant.

**La Grande randonnée à vélo — glacerie fictive.** La réussite d'une addition de monnaie compte comme pratique de calcul; expliquer correctement le raisonnement de façon autonome dans un autre scénario peut renforcer la preuve de transfert. L'achat est simulé; aucune vraie transaction n'est réalisée.

**Le rallye des métiers — station de coiffeuse.** Le fait d'avoir accueilli un camarade ne suffit pas. Une grille d'observation peut noter une consigne intelligible, une question pertinente, l'écoute et l'ajustement d'explication, avec soutien si nécessaire.

## 4. Comment choisir les prochaines tâches

Le professeur doit voir :

1. **Exposition** : les objectifs déjà rencontrés et ceux presque absents.
2. **Pratique** : nombre de tentatives pertinentes, en distinguant les répétitions identiques.
3. **Réussite** : réussites observables et stabilité dans plusieurs situations.
4. **Autonomie** : fait seul, avec partenaire, guidé ou seulement observé.
5. **Transfert** : capacité de réutiliser le savoir dans une nouvelle aventure.
6. **Incertitude** : preuves insuffisantes, contradictoires, non comparables ou en attente de validation.

Le système peut alors **proposer** une mission/rôle qui offre des occasions d'exercer un objectif moins bien couvert; **l'enseignant approuve** et peut adapter. Pas de diagnostic public, d'étiquette de difficulté, de classement d'enfants ni d'affectation punitive. L'entraide reste la finalité : un enfant peut être utile à l'équipe tout en progressant dans un domaine moins maîtrisé.

## 5. Ce qui est effectivement disponible

- Ékole Core contient un portail, des parcours de rôles et une prévisualisation Tandem **enseignant seulement**, mais pas de registre scolaire multiélève authentifié démontré.
- Inkuisite sait stocker localement des **tentatives et corrections**; il ne constitue pas à lui seul une identité scolaire ou une vue de maîtrise longitudinale liée aux Worlds Orgo.
- Les correspondances `curriculum_ids` des missions Kontexte sont des **pistes** à qualifier, non un programme ministériel automatiquement certifié.

## 6. Conditions de qualification

Aucune collecte d'identité réelle sans authentification, autorisations, durée de conservation, politique d'accès des parents/enseignants et contrôles de publication. Une observation issue d'Orgo est une **source de contexte**, pas une validation pédagogique déléguée à Orgo ou à Konnaxion.

**Références :** `Kontexte/docs/ekole-orgo/04_REFERENTIEL_PREUVES_ET_RAPPORTS.md`, `Kontexte/docs/ekole-orgo/01_ETAT_DES_LIEUX_ET_INVARIANTS.md`, `Kontexte/data/missions/fete-sorciere.json`, `Ekole/docs/TANDEM_EKOLE_ORGO_PREVIEW_P1.md`.


## Condition de qualification de la banque étendue (11 novembre 2026)

Les 52 étapes des six nouvelles missions Kontexte possèdent pour l’instant `curriculum_ids: []`. Un statut Orgo `done` ou une tentative Inkuisite ne peut pas être converti en acquis validé en l’absence d’un lien curriculum explicitement approuvé et d’une observation pédagogique attribuable à un élève autorisé. Les identifiants de mission et de rôle ne doivent pas être utilisés comme identifiants d’élève.
