# Scénarios, banque d'activités et Worlds Orgo

> **Révision d’architecture — 11 novembre 2026 :** cette page historique est conservée pour ses détails du pilote. La référence transversale actuelle est [Architecture collaborative et interfaces humaines](architecture-collaborative/00_LIRE_EN_PREMIER.md) : Konnaxion y est traité comme **propriétaire des projets, équipes, messages, ressources et portfolios**, Orgo comme propriétaire des tâches des aventures qu’il exécute, et Ékole comme responsable des décisions pédagogiques. Une fonction documentée ou simulée n’est pas nécessairement en production.


## 1. Intention pédagogique

Un scénario pose un **problème collectif concret ou imaginaire** qui ne se résout pas par la seule exécution d'une fiche individuelle. Chaque enfant incarne un personnage-métier, détient parfois une information ou une compétence utile, et contribue à une production commune. Les situations sont découpées en tâches observables (chercher, mesurer, compter, expliquer, écrire, voter, fabriquer sans risque, vérifier, transmettre).

**Convention de conception retenue pour Ékole : un scénario thématique = un World Orgo identifiable et limité.** *La Fête de la sorcière* forme un World; *La Grande randonnée à vélo* en forme un autre. Le World n'est pas l'ensemble du programme de l'année. Il rend l'aventure compréhensible à l'enfant et maîtrisable par l'enseignant. Cette convention est une **cible d'intégration pédagogique**, pas une affirmation que ces Worlds existent déjà dans une base Orgo.

Une autre classe ou une autre exécution ne doit pas réutiliser aveuglément les permissions ou l'état d'une séance précédente : tenant, classe/participants, session et release doivent être isolés et vérifiés par les autorités respectives.

## 2. Ce qui existe déjà

- **Kontexte** possède les sources de scénario `data/missions/*.json` au format `kontexte.mission/1`, les personnages `data/roles/*.json`, des fragments d'information, étapes, dépendances, jointures et références pédagogiques. Dans l'instantané étudié : **11 missions et 38 rôles**.
- L'installation confirmée par l'utilisateur ajoute **six fichiers de mission** dans `C:\mycode\Ekole\Kontexte\data\missions`, portant son installation locale à **17 missions**, sans créer 17 Worlds runtime.
- Le corpus Kontexte possède aussi **60 trames de problèmes**, **60 déclinaisons québécoises de 3e année**, **34 micro-situations** et une proposition de parcours de **36 semaines**. Ce sont des ressources éditoriales qui se recoupent, pas autant de Worlds déployés.
- **Ékole Core** a un aperçu synthétique enseignant `ekole.tandem-teacher-preview/1.0` et des parcours/visuels de rôles. Il ne devient pas le moteur d'exécution Orgo.
- **Orgo_Worlds** est responsable de `World`, `WorldRelease`, membership et contexte de World; **Orgo** gère `Case`, `Task`, `Signal`, workflows, attributions et transitions.
- **Kompose** prépare et valide le contenu, les contraintes et les propositions de distribution; **Akor** vérifie des intentions/passerelles dans les limites des contrats de revue. La présence de ces outils ne prouve pas l'admission de missions scolaires réelles.

## 3. Modèle de fonctionnement cible

```text
Banque Kontexte : scenario_id, version, personnages, étapes, indices, objectifs
        |
        v
Kompose (préparation et attribution proposée) + Akor (passerelle contrôlée)
        |           [revue de l'enseignant]
        v
Orgo_Worlds : World + WorldRelease + portée des participants
        |
        v
Orgo : Work/Case + Tasks + dépendances + affectations + autorisations
        |                              |
        v                              v
Kidaxion via Konnaxion           Ékole : preuves, progression
(interfaces enfant)             (autorité pédagogique)
```

**Une station n'est pas nécessairement un World.** Par exemple, l'atelier vélo, la glacerie et l'observation d'une fleur sont des stations/étapes du World *Grande randonnée à vélo*. Une tâche peut être collective, individuelle ou nécessiter une rencontre. On évite de créer une Task Orgo pour chaque clic et de dupliquer tous les exercices scolaires dans Orgo.

### Entités à conserver distinctes

| Référence | Provenance / autorité | Sens |
| --- | --- | --- |
| `mission.id`, `steps[].id`, `roles[]` | Kontexte | Définition stable du problème et du rôle narratif. |
| `visual_id = role-<id>` | Kontexte / catalogue visuel Ékole | Représentation du personnage, sans privilège système. |
| `curriculum_ids` | Mission Kontexte, mappage pédagogique à valider dans Ékole | Objectifs candidats, pas notes automatiques. |
| `World`, `WorldRelease`, membership | Orgo_Worlds | Cadre/version de l'aventure et portée. |
| `Case`, `Task`, statut et attribution | Orgo | Exécution et décisions opérationnelles. |
| `task_ref`, `role_code` | Références de projection/intention | Jointure à vérifier; le JSON d'aperçu n'est pas une Task autorisée. |
| Preuve pédagogique / validation | Ékole | Observation d'une compétence, indépendamment de la Task. |

## 4. Exemple vérifié : La Fête de la sorcière

Source canonique de contenu : `Kontexte/data/missions/fete-sorciere.json`.

La mission source a **10 rôles** (`sorciere`, `origamiste`, `traducteur`, `messager`, `metteur-en-scene`, `redacteur`, `lecteur`, `regisseur`, `comptable`, `photographe`) et **11 étapes**. Les personnes détiennent des fragments différents. Ainsi, la sorcière connaît le besoin en invitations; le messager connaît le rendement et le stock de papier. Leur échange permet de calculer le manque. Les autres tâches produisent entre autres une invitation, un discours, une scène, un budget fictif et la documentation des œuvres. L'enseignant supervise les publications et validations.

Ces onze **étapes Kontexte ne sont pas onze Tasks persistées en Orgo** dans le snapshot fourni. La fixture `ekole/tandem/fixtures/fete-sorciere.synthetic.json` n'en montre que **quatre**, avec `scenario_ref: fete-sorciere-synthetique`. Ce jeu de démonstration P1 ne doit jamais remplacer la mission source à 11 étapes. Il faut traiter explicitement la réconciliation de ces versions avant le pilote intégré.

## 5. Exemples pour faire grandir la banque

- **Le grand ménage chez mamie** : inventorier les zones, trier, prévoir le matériel, partager les responsabilités, expliquer des critères d'ordre. Ne pas employer de produits dangereux.
- **La grande randonnée à vélo** : atelier de préparation et vérifications adaptées; trajet, orientation, repérage d'un animal ou d'une fleur, dialogue de rencontre respectueux et achats fictifs de crème glacée; problèmes de mesure, sciences, lecture et monnaie.
- **Le spectacle des histoires inventées** : collecte de mots-clés, vote, choix d'une trame, rédaction, répétitions, costumes simulés et représentation; les rôles de rédacteur, lecteur et régisseur apportent des éléments distincts.
- **Le rallye des métiers** : stations incarnées (par exemple coiffeuse simulant son travail avec les doigts), chacune révélant un indice ou une question nécessaire à la quête d'une autre équipe.

Les six nouveaux JSON sont installés dans **Kontexte** par l'overlay de banque. **Ékole ne doit pas en conserver une deuxième copie canonique**. Le catalogue local `Kontexte/docs/banque-worlds/catalogue.json` sert à la découverte/documentation, pas à l'autorisation d'exécuter une tâche.

## 6. Règle d'admission future

Un enseignant choisit une mission et révise ses objectifs, ses rôles et les adaptations. Le système vérifie les identités, la portée classe/World/release et l'approbation. Seulement ensuite une passerelle autorisée prépare l'exécution dans Orgo, avec des références stables et de l'idempotence. Les fragments privés ne doivent être révélés qu'au participant autorisé, à l'étape autorisée. Aucun import automatique depuis un dossier de JSON vers la base Orgo ne doit être présumé.

### Références de code et docs (dépôts frères)

- `Kontexte/docs/ekole-orgo/02_ARCHITECTURE_CIBLE.md`, `03_FRAME_UNIVERSEL_ROLES_ET_MISSIONS.md`, `05_PILOTE_FETE_SORCIERE.md`
- `Kontexte/data/missions/fete-sorciere.json` et `data/roles/*.json`
- `Kompose/docs/adr/0008-tandem-orgo-operational-authority.md`
- `Orgo_Worlds/docs/Technical-Reference/Worlds/WORLD_SCENARIO_INJECTION.md`
- `Orgo/tools/scenario-injector/` (outil existant, **pas** une preuve d'intégration éducative)


## État du catalogue dans le snapshot du 11 novembre 2026

Le dépôt Kontexte livré contient **17 fichiers de mission** (`data/missions/`), dont les six missions de la banque. Le code `qc3_b5.py` et le test `test_studio.py` présupposent encore 11 missions historiques. Les 52 étapes des six nouvelles missions sont structurellement valides mais n’ont **aucun objectif `curriculum_ids` renseigné** : elles ne doivent donc pas contribuer automatiquement à une preuve de maîtrise Ékole. On conserve leurs scénarios comme candidats, et on prépare les mappings pédagogiques avec validation enseignante avant exécution réelle.
