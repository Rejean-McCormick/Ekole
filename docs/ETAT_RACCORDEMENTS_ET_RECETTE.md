# État de l'intégration et recette du premier World pédagogique

> **Révision d’architecture — 11 novembre 2026 :** cette page historique est conservée pour ses détails du pilote. La référence transversale actuelle est [Architecture collaborative et interfaces humaines](architecture-collaborative/00_LIRE_EN_PREMIER.md) : Konnaxion y est traité comme **propriétaire des projets, équipes, messages, ressources et portfolios**, Orgo comme propriétaire des tâches des aventures qu’il exécute, et Ékole comme responsable des décisions pédagogiques. Une fonction documentée ou simulée n’est pas nécessairement en production.


**Lecture : 11 novembre 2026, à partir des instantanés et du journal d'installation transmis.** Une validation statique ou un test simulé n'est ni une admission en production, ni une autorisation d'utiliser des dossiers d'enfants.

## 1. Composants présents et frontière à respecter

| Brique | Présent dans les sources | Non démontré comme intégré à une classe réelle |
| --- | --- | --- |
| **Kontexte** | 38 rôles; 17 missions dans le snapshot du 11 novembre (11 historiques + 6 supplémentaires), fragments et dépendances; les 52 étapes des nouvelles missions restent sans `curriculum_ids` | Conversion autorisée de tout scénario vers une séance Orgo déployée. |
| **Ékole Core** | Catalogue de personnages, parcours de rôles, prévisualisation synthétique enseignant `ekole.tandem-teacher-preview/1.0` | Identité élève/enseignant institutionnelle, consultation des Tasks réelles, registre longitudinal de preuves. |
| **Kompose** | Préparation, validation et projection; ADR Orgo autorité unique | Attribution exécutée et approuvée dans une base Orgo scolaire. |
| **Akor** | Intention 11 étapes et vérifications de transfert *review-only* | Commande authentifiée/adoptée pour admission de classe. |
| **Orgo_Worlds** | World's scope, releases, lecteurs et preuves internes simulées P3–P6 | Service de confiance complet, transport et approbations de classes en exploitation. |
| **Orgo** | Work, Case, Task, Signal, systèmes d'attribution et contrôles P2–P12 testés localement | Transaction scolaire persistée et bout en bout avec élèves réels. |
| **Konnaxion** | Backend d'identité/collaboration et adaptateur d'intégration | Parcours scolaire Kidaxion vérifié pour des mineurs. |
| **Kidaxion** | Intention fonctionnelle définie : interface Konnaxion simplifiée | Application et contrats d'interface effectivement branchés. |
| **Inkuisite** | Tentatives/corrections locales | Preuves associées de façon sûre à un dossier scolaire et à un World. |

## 2. Écart concret dans le pilote La Fête de la sorcière

- **Mission éditoriale :** `Kontexte/data/missions/fete-sorciere.json` contient **11 étapes** et **10 personnages**.
- **Aperçu Ékole P1 :** `ekole/tandem/fixtures/fete-sorciere.synthetic.json` contient **4 tâches fictives**; son `scenario_ref` est `fete-sorciere-synthetique`.
- **Akor :** `Akor/examples/tandem/fete-sorciere.11-tasks.intent.synthetic.json` décrit une intention de 11 tâches, non une création en base.
- **P6–P12 Orgo :** la campagne inclut une **simulation transactionnelle dans une Map JavaScript** de 1 Case et 11 Tasks. Les documents indiquent explicitement `production_ready=false`, `runtime_admitted=false`, `db_writes=0` et `network_calls=0`.

**Action :** établir une transformation versionnée, contrôlée et vérifiable des 11 étapes source vers les tâches admises par Orgo. Garder la fixture à 4 tâches comme *exemple historique synthétique*, sans la présenter comme représentation complète du scénario.

## 3. Parcours de recette (d'abord données fictives)

| Étape | Condition observable | Propriétaire |
| --- | --- | --- |
| 1. Choisir la fête | L'enseignant voit la mission, ses objectifs, 10 rôles et 11 étapes d'origine. | Kontexte / Ékole |
| 2. Préparer les rôles | Proposition explicable; modifications et accord de l'enseignant. | Kompose / Ékole |
| 3. Préparer le World | World et WorldRelease cohérents, tenant isolé; appartenance établie par serveur de confiance. | Orgo_Worlds |
| 4. Admettre la séance | Authentification, autorisations, consentements pertinents et idempotence vérifiés; refus sûr sinon. | Orgo |
| 5. Créer le Work | Case/Tasks authentiques persistées, dépendances cohérentes et attribution aux acteurs autorisés. | Orgo |
| 6. Jouer les stations | Kidaxion n'affiche qu'une mission à la fois; Konnaxion transporte une interaction autorisée; le bon fragment est libéré. | Konnaxion/Kidaxion + Orgo |
| 7. Vérifier l'apprentissage | Ékole recueille des observations individualisées et l'enseignant valide, sans inférer une maîtrise de `done`. | Ékole |
| 8. Recommander la suite | Une autre mission propose de nouvelles occasions ciblées, sans assignation automatique non revue. | Ékole / enseignant |

## 4. Tests négatifs indispensables

- Mauvais tenant, World archivé, mauvaise release, participant absent/révoqué ou session périmée : **aucune tâche ni indice divulgué**.
- Rejeu, interruption ou double lancement : **aucune duplication de Case/Task**.
- Échec d'approbation enseignante : **aucune admission**.
- Choix de personnage seul dans `sessionStorage` : **aucun droit opérationnel**.
- « J'ai terminé » envoyé par un enfant : **aucune maîtrise Ékole attribuée sans preuve**.
- Média d'un enfant sans autorisation applicable : **aucune publication**.
- Absence d'un personnage clé : **plan de secours sous contrôle enseignant**, pas d'impasse ni de pénalité automatique.

## 5. Travail dans l'ordre

1. **Aligner sans doublonner :** ids des personnages, 11 étapes de la fête, correspondances `curriculum_ids` et formats d'intention.
2. **Vérifier les frontières :** identité scolaire, tenant/World/release, approuvabilité et revue enseignant.
3. **Implémenter le pont admis Orgo :** transaction persistante, idempotence, tests de refus et journaux d'audit.
4. **Brancher Kidaxion :** stations, messages autorisés et indices sous contrôle d'Orgo.
5. **Relier Ékole :** preuves individualisées, revue, conservation et recommandation de nouvelles activités.
6. **Déployer progressivement la banque :** d'abord la fête, ensuite une nouvelle mission comme la randonnée à vélo.

## 6. Sources de référence

- `Ekole/docs/PERSONNAGES_ALIGNMENT.md` et `TANDEM_EKOLE_ORGO_PREVIEW_P1.md`
- `Kontexte/docs/ekole-orgo/00_LIRE_EN_PREMIER.md` à `09_ADR_ORGO_GRAND_ORCHESTRATEUR.md`
- `Akor/docs/TANDEM_EDUCATION_P2_REVIEW_ONLY.md` et `Akor/docs/FINAL_SYSTEM_EDUCATION_ALIGNMENT.md`
- `Kompose/docs/adr/0008-tandem-orgo-operational-authority.md`
- `Orgo/tools/tandem-education/p6-p12/README_ONE_PASS.md`
- `Orgo_Worlds/docs/TANDEM_EDU_P6_P12_BRIDGE_CONTRACT.md`
- `Orgo_Worlds/docs/Technical-Reference/Worlds/WORLD_SCENARIO_INJECTION.md`

Ce document **ne remplace pas** les ADR et les contrats des dépôts propriétaires. Il sert à aligner le travail d'intégration à partir de la vue Ékole.


## Validation complémentaire du 11 novembre 2026

La validation `python -m kontexte validate` reconnaît les 38 rôles, 17 missions et 202 références internes. La suite Kontexte de 78 tests produit 9 erreurs et 1 échec : le contrôle historique B5 et le test Studio supposent encore exactement 11 missions. Lorsqu’on retire temporairement les six nouvelles missions sur une copie de test, les 78 tests passent. Il faut conserver la base historique B5 comme sous-ensemble explicite, et vérifier indépendamment la banque étendue, plutôt que remplacer aveuglément 11 par 17 partout. Voir [validation croisée](VALIDATION_CROISEE_2026-11-11.md).
