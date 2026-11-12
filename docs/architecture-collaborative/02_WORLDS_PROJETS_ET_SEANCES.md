# 02 — Worlds, projets, classes, séances et identités

## Cinq objets, pas un seul

| Objet | Définition | Identifiant / propriété |
| --- | --- | --- |
| **Scénario** | Modèle thématique réutilisable (*La Fête de la sorcière*) | `scenario_ref` + version Kontexte |
| **World Orgo** | Conteneur opérationnel du scénario et de ses ressources de travail | `orgo_world_ref` + release Orgo_Worlds |
| **World Konnaxion** | Contexte isolé des conversations, projets, participants, ressources et portfolios | `konnaxion_world_ref` + release Konnaxion_Worlds |
| **Projet Konnaxion** | Groupe collaboratif avec équipe, ressources, messages, éventuellement tâches Konnaxion natives | `project_ref` dans un World Konnaxion |
| **Séance de classe** | Occurrence pédagogique concrète : date, groupe, enseignant, participants, état, objectifs et World(s) liés | `session_ref` Ékole et références croisées vérifiées |

**Convention du pilote :** *un scénario = un World Orgo* pour faciliter la compréhension et limiter la charge. Cela ne signifie **ni** une installation serveur par World, **ni** qu'une seule classe ou une seule séance possède ce scénario pour toujours. Le modèle doit prendre en charge plusieurs séances et groupes utilisant le même scénario versionné **sans partager leurs données**.

Un World Konnaxion peut héberger l'espace collaboratif associé à la séance. Son cycle de vie, son schéma et ses identités restent distincts de ceux d'Orgo. Il n'existe **aucune identité universelle implicite** entre ces deux types de Worlds. Éviter aussi de créer un World Konnaxion par petite tâche : préférer un espace par périmètre de collaboration, selon l'isolation requise.

## Liaison contrôlée proposée (non implémentée)

L'objet de rapprochement Ékole doit conserver les *références opaques* suivantes, sans tokens, adresses de mineurs ou secrets :

```text
scenario_ref + scenario_version + scenario_hash
school_scope_ref + group_ref + session_ref
orgo_world_ref + orgo_release_ref + orgo_case_ref
konnaxion_world_ref + konnaxion_release_ref + konnaxion_project_ref
issuer_ref + teacher_approval_ref + access_policy_ref
status + timestamps + audit_ref
```

En plus, une correspondance de personne distincte des personnages-métiers relie l'identité scolaire vérifiée, le membre Orgo et le membre Konnaxion. Une personne peut incarner différents personnages selon la séance. Un personnage peut être transmis à un coéquipier sans transférer automatiquement la permission de l'utilisateur précédent.

**Exemple structurée :** [CONTRAT_LIAISON_SEANCE.exemple.json](CONTRAT_LIAISON_SEANCE.exemple.json) et [son schéma](CONTRAT_LIAISON_SEANCE.schema.json). Ces fichiers sont une *proposition d'interface* pour la prochaine phase, non des preuves d'autorité.

## Cycle de vie de la séance

```text
DRAFT → PREPARED → AWAITING_TEACHER_APPROVAL
      → AUTHORIZED (après admission côté propriétaires)
      → ACTIVE → PAUSED / COMPLETED → REVIEWED → ARCHIVED
```

- `PREPARED` : scénario vérifié et attribution proposée, sans état de Task réel ni autorisation d'enfant.
- `AWAITING_TEACHER_APPROVAL` : l'enseignant examine tâches, sécurité, rôles, critères et accès.
- `AUTHORIZED` : World, release, identité, membership et droits sont vérifiés par les **services propriétaires**. L'approbation de l'enseignant ne remplace pas cette admission.
- `ACTIVE` : Orgo accepte des commandes opérationnelles; Konnaxion peut accepter des contributions dans le bon contexte.
- `COMPLETED` : l'aventure peut être terminée alors que les évaluations individuelles restent à revoir.
- `REVIEWED` : les preuves pertinentes ont reçu une décision pédagogique.

Cette machine d'états décrit un **coordonnateur de présentation Ékole** à concevoir. Elle ne doit pas dupliquer les machines d'état internes d'Orgo ou de Konnaxion.

## Versions et stabilité

- Épingler la version de mission et son empreinte au lancement; ne pas réécrire le scénario sous une séance historique.
- Épingler chaque `WorldRelease` explicite. Une promotion future n'autorise pas la réinterprétation des preuves d'une séance passée.
- Conserver les identifiants réels comme des **références extérieures opaques** : ne pas supposer `world_key` ou `task_ref` identiques entre produits.
- Une correction de consigne doit produire une révision/événement traçable; les preuves antérieures gardent leur contexte source.
- Dissocier le droit de *voir* une ressource de celui de *soumettre* une action, et de celui de *valider* une réussite.

## Cas à couvrir

Deux classes lancent *La Fête de la sorcière* simultanément; un élève change de personnage; un groupe partage un Chromebook; un World Konnaxion change de release; une carte papier est photographiée; une station est suspendue; un enseignant clôt le projet mais n'a pas fini l'évaluation. **Aucun de ces événements ne doit exposer les données d'une autre classe ni réécrire des résultats passés.**
