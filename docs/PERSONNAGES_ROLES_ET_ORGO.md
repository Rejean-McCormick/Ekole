# Personnages-métiers, rôles et attribution dans Orgo

> **Révision d’architecture — 11 novembre 2026 :** cette page historique est conservée pour ses détails du pilote. La référence transversale actuelle est [Architecture collaborative et interfaces humaines](architecture-collaborative/00_LIRE_EN_PREMIER.md) : Konnaxion y est traité comme **propriétaire des projets, équipes, messages, ressources et portfolios**, Orgo comme propriétaire des tâches des aventures qu’il exécute, et Ékole comme responsable des décisions pédagogiques. Une fonction documentée ou simulée n’est pas nécessairement en production.


## 1. Les personnages existent déjà : ne pas les recréer

Dans Kontexte, les **38 rôles** (instantané fourni) sont décrits par `data/roles/<id>.json` au format `kontexte.role/1`. Un rôle porte un identifiant stable, un nom, un contexte, des actions, objets, problèmes, partenaires et un `visual_id`. Exemples :

| Rôle narratif | ID Kontexte | Visuel attendu | Exemples de contributions |
| --- | --- | --- | --- |
| Fermier | `fermier` | `role-fermier` | Semer, mesurer, récolter; aider le boulanger. |
| Sorcière | `sorciere` | `role-sorciere` | Préparer une fête, répartir les informations et inviter. |
| Coiffeuse | `coiffeuse` | `role-coiffeuse` | Jouer une station de métier, écouter, expliquer, organiser. |
| Boulanger | `boulanger` | `role-boulanger` | Participer aux situations de production et de quantités. |

**Kolor** est une source de créations/exports visuels; le catalogue de personnages consommé par Ékole reste le mécanisme décrit dans [PERSONNAGES_ALIGNMENT.md](PERSONNAGES_ALIGNMENT.md). L'identifiant d'image est `role-<id>`; le moteur Ékole ne doit pas coder en dur la liste des noms et PNG.

## 2. Trois objets différents, une liaison contrôlée

1. **Personnage-métier / rôle narratif** : `role_id` ou `role_code` tel que `fermier`; définit le sens de la mission et son habillage.
2. **Enfant participant** : identité scolaire réelle, protégée, connue d'un service authentifié; ce n'est jamais `fermier` ni un identifiant fictif dans le pack.
3. **Attribution opérationnelle Orgo** : une tâche assignée à un acteur autorisé, sous contrôle d'identité, tenant/World/release et des règles de l'enseignant.

La base Orgo comprend notamment `Task.assignee_role`, `Task.owner_user_id` et `TaskAssignment` dans `apps/api/prisma/schema.prisma`. **Cela ne signifie pas que le champ de rôle narratif du pack soit automatiquement mappé vers une attribution d'un enfant réel.** L'adaptateur doit résoudre explicitement la relation et vérifier les permissions. Le rôle « sorcière » ne doit jamais devenir un rôle IAM/RBAC donnant des droits à un compte.

## 3. Parcours cible d'un rôle

```text
Kontexte : rôle « fermier », tâches et partenaires du scénario
       |
Ékole : profil pédagogique + intérêts (accès strictement enseignant)
       |
Kompose : proposition de casting (forces + besoins de pratique + équité)
       |
Enseignant : confirme / corrige / remplace le rôle
       |
Orgo : associe l'enfant autorisé à la Task et au rôle du World
       |
Kidaxion : montre au participant sa mission et ses interactions permises
       |
Ékole : observe et révise les preuves propres à chaque compétence
```

La distribution ne doit pas enfermer toujours l'enfant dans ce qu'il maîtrise déjà. Le système peut proposer un rôle de force qui aide l'équipe, puis un rôle avec soutien pour pratiquer un apprentissage à consolider. Un rôle ne se déduit pas d'un score unique. Une préférence, un besoin d'accessibilité ou l'absence d'un enfant peuvent justifier un autre casting **approuvé par l'enseignant**.

## 4. Détails d'interopérabilité à ne pas mélanger

| Couche | Champ ou mécanisme vu dans les sources | Portée actuelle |
| --- | --- | --- |
| Kontexte | `mission.roles[]`, `steps[].role`, `roles/<id>.json` | Définition d'une mission et d'un rôle. |
| Kompose | `role_id` projeté et validation préparatoire | Préparation/aperçu, sans mutation de Task Orgo. |
| Ékole | `visual_id = role-<role_id>`, catalogue de personnages et pilote `/eleve/` | Habillage et parcours local; choix conservé en `sessionStorage`, **pas une identité de classe**. |
| Ékole P1 | `role_code`, `task_ref` dans `ekole.tandem-teacher-preview/1.0` | Démonstration réservée à l'enseignant. |
| Orgo | `assignee_role`, `owner_user_id`, `TaskAssignment` | Primitives d'affectation réelles, raccordement scolaire à qualifier. |
| Orgo_Worlds | World, release, membership | Contexte à vérifier par un service de confiance. |

## 5. Stations incarnées

Une station « salon de coiffure » peut être animée par l'enfant jouant la coiffeuse. Son action est une **simulation** (pas de vrais ciseaux ni de coupe). L'enfant reçoit un script pédagogique court, pose une question, écoute la réponse et transmet l'indice que la quête autorise. Le passage à la station peut fournir une observation d'expression orale ou de coopération, mais ne prouve **pas automatiquement** la maîtrise d'une compétence.

## 6. Critères de réussite du raccordement

- La même chaîne d'IDs relie Kontexte (`fermier`) → Kompose (`role_id`) → Ékole (`role-fermier`) → projection Orgo (`role_code`) sans renommer arbitrairement le personnage.
- L'enseignant peut voir, réviser et confirmer les attributions avant toute exécution réelle.
- Un enfant n'accède qu'aux tâches/fragments permis à sa session, même en changeant de personnage.
- Les substitutions, absences, retours en arrière et échanges d'indices ne déclenchent aucun accès indu.
- Une réalisation individuelle peut être reliée à une preuve Ékole sans donner à Orgo la propriété des évaluations scolaires.

**Références :** `Kontexte/data/roles/`, `Kontexte/data/missions/`, `Kompose/docs/04-diagnostic-et-attribution.md`, `Ekole/docs/PERSONNAGES_ALIGNMENT.md`, `Orgo/apps/api/prisma/schema.prisma`.
