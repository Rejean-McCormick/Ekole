# 06 — Contrats d'interopérabilité et sémantique des événements

**Statut :** proposition pour le prochain raccordement exécutable. Ce document ne modifie ni Interaction Kernel ni les contrats existants. Les nouveaux noms de messages ci-dessous sont des **concepts de domaine**, à mapper aux profils IK réellement adoptés, après vérification de leurs versions.

## Objectifs de l'interface commune

- Présenter à chaque utilisateur la même séance, la même tâche et les mêmes actions possibles sur Web, Kor et Kamel.
- Lier le World Orgo à un World et un projet Konnaxion **sans confondre leurs identités et releases**.
- Transmettre une commande au **propriétaire** avec un reçu vérifiable, pas mettre à jour sa base de données depuis une autre application.
- Documenter l'apprentissage sans recopier le contenu privé ni tirer une conclusion pédagogique automatique.

## Identifiants

| Référence proposée | Rôle | Règle |
| --- | --- | --- |
| `scenario_ref`, `scenario_version`, `scenario_sha256` | Modèle Kontexte utilisé | Épinglé pour la séance |
| `session_ref` | Occurrence pédagogique Ékole | Stable, non réutilisable entre classes |
| `school_scope_ref`, `group_ref` | Périmètre de droits | Issus d'un registre scolaire autorisé, jamais du client |
| `orgo_world_ref`, `orgo_release_ref`, `orgo_case_ref`, `orgo_task_ref` | Références opérationnelles | Autorité Orgo/Orgo_Worlds |
| `konnaxion_world_ref`, `konnaxion_release_ref`, `konnaxion_project_ref` | Références de collaboration | Autorité Konnaxion/Konnaxion_Worlds |
| `subject_ref`, `member_ref`, `role_code` | Personne scolaire, appartenance, personnage | Trois identités **distinctes** |
| `correlation_ref`, `causation_ref`, `idempotency_ref` | Traçabilité des opérations | Respecter les champs IK adoptés; unique par effet souhaité |
| `owner_receipt_ref`, `authority_ref` | Admission par le propriétaire | Transport reçu ≠ action acceptée |

L'exemple et le schéma de liaison se trouvent à côté du présent document. Ils doivent rester hors du runtime tant qu'un contrat inter-dépôts n'est pas ratifié.

## Commande, lecture et événement

**Commande** : demande explicite, ex. « soumettre une réponse pour Task X ». Elle doit être authentifiée et autorisée **par le service propriétaire**.

**Lecture/projection** : réponse filtrée, mise en cache éventuellement, sans autorité nouvelle. Elle ne doit pas exposer plus de données que la source.

**Événement** : fait confirmé par le propriétaire, ex. Task terminée, message modéré, tentative enregistrée. Il contient un identifiant de source et une portée; son transport ne suffit pas à qualifier une preuve pédagogique.

| Fait / intention de domaine | Source et écriture autorisée | Consommateur possible | Observation |
| --- | --- | --- | --- |
| `assignment.proposed` | Kompose | Enseignant/Ékole | Proposition, pas permission |
| `assignment.approved` | Enseignant dans un service d'approbation sécurisé | Adaptateur d'admission Orgo | Doit rester distincte de l'assignation committée |
| `orgo.task.assigned` | Orgo | Kidaxion, Ékole | Projection autorisée |
| `orgo.task.status_changed` | Orgo | Konnaxion (lecture), Ékole | État réel de travail, pas une note |
| `konnaxion.project.contribution_added` | Konnaxion | Ékole | Référence et contexte, pas copie générale de contenu |
| `konnaxion.project.message_moderated` | Konnaxion | Kidaxion, enseignant | Selon visibilité et modération |
| `inkuisite.attempt.recorded` | Inkuisite (nom **illustratif**, pas profil existant) | Ékole | Corrélation à identité et exercice vérifiées |
| `ekole.evidence.reviewed` | Ékole / enseignant | Portfolio Kidaxion/Konnaxion si autorisé | Décision de compétence distincte |
| `ekole.portfolio.selection_approved` | Ékole | Projection KonnectED | Partage facultatif, pas donnée scolaire brute |

**Important :** ces étiquettes ne sont pas des routes HTTP ni des profils Interaction Kernel existants. Elles décrivent les transferts nécessaires à spécifier et versionner.

## Admission et idempotence

La passerelle évalue, dans cet ordre :

1. authenticité de l'acteur (compte/session scolaire vérifié);
2. portée de classe/séance, World + release et éventuel projet Konnaxion;
3. appartenance et action permise côté propriétaire;
4. état courant de la tâche/interaction et version de ressource;
5. règles particulières (modération, auteur, approbation enseignant, expiration QR);
6. prévention des répétitions par clé d'idempotence (un scan ou retry ne crée pas deux réalisations);
7. conservation du reçu et de la décision (`rejected`, `accepted`, `committed`, `reviewed`).

Les clients n'envoient jamais un `teacher_authorized: true` ou un `dispatch_allowed: true` auto-attribué; seuls les services compétents prennent ces décisions.

## Résilience

- **Panne Konnaxion** : Orgo conserve la Task; les messages ne sont pas déclarés envoyés si aucun reçu n'existe; le client peut proposer un brouillon.
- **Panne Orgo** : Konnaxion peut afficher l'état connu comme *potentiellement périmé*; aucune clôture locale de Task.
- **Panne Ékole** : travail et interactions continuent selon leurs permissions; les preuves sont mises en attente, dédupliquées et revues plus tard.
- **Kor hors ligne** : requête en file, statut non confirmé; cache chiffré ou limité selon politique.
- **QR imprimé** : ouverture d'une référence; absence de réseau doit donner une procédure supervisée, pas une admission fictive.

## Journal de traçabilité minimal

Pour chaque demande : `request_ref`, source/canal (`web`, `kor`, `kamel`, `teacher`), références de portée, type d'action, `idempotency_ref`, verdict du propriétaire, horodatage, source de politique et motifs de rejet lisibles. **Ne pas journaliser les secrets, contenus personnels, réponses brutes ou identifiants accessibles au public** inutilement.

## Contrat d'exemple

Le schéma JSON compagnon représente **le lien entre les mondes et la séance** sans habilitation incorporée. Toute action réelle exige l'authentification et la politique du propriétaire : le simple fait qu'un objet valide le schéma ne confère aucun accès.
