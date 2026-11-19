# L’écosystème Ékole

Ékole est le moteur pédagogique local de l’écosystème kOA. Il fournit un portail élève, un éditeur enseignant et des interfaces JSON. Un pack indépendant fournit les cours, les parcours et les sources auteur. Autour du moteur et des packs, des outils autonomes permettent de préparer une activité, mener une aventure collective, produire des médias, évaluer et diffuser.

Pour vous repérer dans l’ensemble de kOA, consultez [la documentation kOA Digital Ecosystem](https://github.com/Rejean-McCormick/kOA-Digital-Ecosystem/blob/main/docs/index.md), [la carte des responsabilités](https://github.com/Rejean-McCormick/kOA-Digital-Ecosystem/blob/main/docs/2-Technical-Reference/10-system/authority-map.md) et [la fiche Ékole dans la carte kOA](https://github.com/Rejean-McCormick/kOA-Digital-Ecosystem/blob/main/docs/1-Overview/Components-Skope-and-Ekole.md).

## Choisir un parcours

| Vous voulez… | Commencez ici |
| --- | --- |
| Essayer le portail ou l’éditeur | [Démarrer le moteur](DEMARRAGE.md) et choisir un pack. La [visite guidée de la division](../visite-client/LISEZ-MOI.md) présente le parcours local. |
| Enseigner au primaire québécois | [Ékole Québec](https://github.com/Rejean-McCormick/Ekole-Quebec/blob/main/README.md) fournit 202 cours candidats, six parcours, des sources Kristal et des ressources pédagogiques. [Les invitations de Mila](https://github.com/Rejean-McCormick/Ekole-Quebec/blob/main/activites/invitations-mila/README.md) donne un exemple d’activité de division et de ses projections locales. |
| Préparer une activité pastorale catholique | [Ékole Pastorale](https://github.com/Rejean-McCormick/Ekole-Pastorale/blob/main/README.md) fournit 32 cours prototypes et sept parcours, avec deux branches : message et tradition vivante, miracles et mystères. Pour travailler sur le contenu, suivez [les règles éditoriales et de protection du pack](https://github.com/Rejean-McCormick/Ekole-Pastorale/blob/main/docs/GOUVERNANCE_ET_ETHIQUE.md). |
| Chercher une situation ou préparer une aventure | [Banque PRF-22](PRF22_BANQUE_REPO.md) pour les propositions en atelier enseignant. [Kontexte](https://github.com/Rejean-McCormick/Kontexte/blob/main/README.md) pour les trames, missions et personnages-métiers. [Architecture collaborative](architecture-collaborative/00_LIRE_EN_PREMIER.md) pour le trajet de classe. |
| Préparer une évaluation ou un portfolio | [Preuves, évaluations et portfolios](architecture-collaborative/05_PREUVES_EVALUATIONS_PORTFOLIOS.md) pour passer d’une tentative ou d’une observation à une revue enseignante et, si autorisé, à une sélection pour le portfolio. |
| Illustrer un cours, explorer ses concepts ou en faire une page | Voir [le guide auteur et publication](AUTEUR_ET_PUBLICATION.md). |
| Imprimer un calendrier familial | [Kalendar](https://github.com/Rejean-McCormick/Ekole-Kalendar/blob/main/README.md) permet de choisir un calendrier scolaire, d’ajouter des horaires et d’imprimer. Il fonctionne indépendamment des comptes et du suivi d’Ékole. |

Le moteur charge le pack sélectionné via `pack.json`. Pour réviser une leçon, partez des sources et des règles éditoriales du pack. Les projections destinées à l’élève sont produites à partir de ces sources. L’état candidat d’un cours, sa disponibilité dans le portail local et son autorisation de diffusion sont trois informations distinctes.

## Préparer et suivre une aventure

| Étape | Qui intervient et où lire |
| --- | --- |
| Choisir le scénario | **Kontexte** conserve les étapes, personnages, stations et fragments. Voir [les raccords Ékole–Orgo de Kontexte](https://github.com/Rejean-McCormick/Kontexte/blob/main/docs/ekole-orgo/README.md). |
| Préparer la séance | **Kompose** propose une répartition de rôles et prépare une simulation. **Akor** structure les intentions de collaboration. L’enseignant examine le plan. Voir [la documentation Tandem de Kompose](https://github.com/Rejean-McCormick/Kompose/blob/main/docs/TANDEM_P1_ORGO_EKOLE_ALIGNMENT.md) et [le mode revue d’Akor](https://github.com/Rejean-McCormick/Akor/blob/main/docs/TANDEM_EDUCATION_P2_REVIEW_ONLY.md). |
| Exécuter le travail | [Orgo](https://github.com/Rejean-McCormick/Orgo/blob/master/README.md) possède les Case, Task, affectations et transitions qu’il exécute. [Orgo Worlds](https://github.com/Rejean-McCormick/Orgo-Worlds/blob/main/docs/Technical-Reference/Worlds/04_DATA_OWNERSHIP_MATRIX.md) possède les Worlds opérationnels, releases et appartenances de son domaine. |
| Collaborer | [Konnaxion](https://github.com/Rejean-McCormick/Konnaxion/blob/main/README.md) possède les projets, équipes, échanges et ressources. [Konnaxion Worlds](https://github.com/Rejean-McCormick/Konnaxion-Worlds/blob/main/docs/Technical-Reference/Worlds/04_DATA_OWNERSHIP_MATRIX.md) conserve son propre périmètre. Pour une aventure exécutée par Orgo, la vue collaborative peut afficher une référence à la Task Orgo. Les projets propres à Konnaxion peuvent conserver leurs `ProjectTask`. |
| Présenter l’action à l’élève | [Kidaxion, Web, Kor et Kamel](architecture-collaborative/04_KIDAXION_WEB_KOR_KAMEL.md) décrit les surfaces, les cartes et les actions permises. Le [lot multicanal](architecture-collaborative/11_LOT_CODE_MULTICANAL_2026_11_11.md) détaille la préversion Web, les projections locales et les raccords à qualifier. |
| Recueillir et examiner les preuves | **Inkuisite** gère les items, tentatives et corrections dans son périmètre. **Ékole et l’enseignant** apprécient ce qu’une observation démontre par rapport à un objectif. **KonnectED** peut présenter une sélection approuvée selon l’audience. Voir [le trajet des preuves](architecture-collaborative/05_PREUVES_EVALUATIONS_PORTFOLIOS.md). |

**Exemple : La Fête de la sorcière.** Ouvrez [la mission source, avec ses rôles et étapes](https://github.com/Rejean-McCormick/Kontexte/blob/main/data/missions/fete-sorciere.json), puis le [parcours de préparation et de recette](architecture-collaborative/07_SCENARIOS_ET_PARCOURS.md). Le plan enseignant et les cartes du lot multicanal sont utilisables en revue locale. Pour une classe réelle, vérifiez la séance, les versions des Worlds, les appartenances et l’admission par les services propriétaires. Les [conditions de recette](architecture-collaborative/09_FEUILLE_DE_ROUTE_ET_RECETTE.md) précisent ce que chaque raccord doit confirmer.

Une mission réutilisable, une séance de classe, un World Orgo et un projet Konnaxion ont chacun leur référence. Utilisez les [contrats et événements](architecture-collaborative/06_CONTRATS_ET_EVENEMENTS.md) pour les relier et les profils de l’[Interaction Kernel](https://github.com/Rejean-McCormick/Interaction-Kernel/blob/main/README.md) là où ils sont adoptés. Le personnage joué et le QR servent à l’interaction. Les droits de lecture et d’écriture sont vérifiés par le service propriétaire, selon la [politique de confidentialité de la séance](architecture-collaborative/08_SECURITE_ET_CONFIDENTIALITE.md).

## Créer et diffuser

| Besoin | Documentation de référence |
| --- | --- |
| Imaginer un personnage ou produire des visuels | [Karacter](https://github.com/Rejean-McCormick/Karacter/blob/main/README.md) pour les fiches de personnages fictifs, [Kolor Studio](https://github.com/Rejean-McCormick/Kolor/blob/main/README.md) pour les palettes et planches de rôles, [Atelier Images](https://github.com/Rejean-McCormick/Ekole-Atelier-Images/blob/main/LISEZ-MOI.md) pour les prompts, générations et comparaisons. Le pack choisit et approuve l’image qui entre dans le cours. |
| Suivre la source d’une activité | Les Kristals du pack portent le contenu et sa provenance. Le [Framework Kristal](https://github.com/Rejean-McCormick/Kristal-Framework/blob/main/README.md) décrit ses contrats et versions. [Konstellation](https://github.com/Rejean-McCormick/Konstellation/blob/main/README.md) explore les surfaces de lecture autorisées. |
| Préparer une page dans une autre langue | [SemantiK Architect](https://github.com/Rejean-McCormick/SemantiK-Architect/blob/main/README.md) réalise les unités de sens selon les profils et langues pris en charge. Le [Runtime Orchestrator](https://github.com/Rejean-McCormick/SemantiK_Runtime_Orchestrator/blob/main/README.md) coordonne les versions des RuntimeSets. [Spek](https://github.com/Rejean-McCormick/Spek/blob/main/README.md) compose les pages à partir des unités, des textes relus et d’un gabarit. Voir [le guide des réalisations dans les gabarits Spek](https://github.com/Rejean-McCormick/Spek/blob/main/docs/REALISATION_SEMANTIK_TEMPLATES_2026-11-02_FR.md). |
| Préparer une projection vers Moodle | Le [pont Moodle candidat d’Ékole Québec](https://github.com/Rejean-McCormick/Ekole-Quebec/blob/main/moodle/README.md) documente le plan à blanc et le lecteur proposé pour `local_uckk`. [UCKK](https://github.com/Rejean-McCormick/UCKK/blob/main/README.md) reste la destination campus distincte. Une écriture dans Moodle dépend du contrat adopté et du résultat confirmé par la destination. |

Une page Spek, un visuel approuvé, une projection Moodle et une publication Kristal suivent leurs propres règles de version, d’audience et d’autorisation. Pour les limites actuelles du moteur et de ses projections, voyez la [référence d’intégration Ékole](FINAL_SYSTEM_EDUCATION_ALIGNMENT.md).

## Naviguer d’un outil à l’autre

Ce repère s’applique aussi à une interface assistée par IA. Partez de l’intention de la personne et gardez le fil : pack, parcours, langue, cours ou mission, puis séance et projet si ces références sont accessibles. Dirigez la demande vers le propriétaire de l’objet. Présentez la prochaine action possible dans le contexte courant et précisez le statut d’une opération : brouillon, aperçu, demande transmise, action confirmée ou revue humaine.

- « Je veux continuer mon cours » → retrouvez le parcours et l’activité dans la vue élève du pack actif.
- « Prépare la fête pour ma classe » → ouvrez la mission Kontexte et le plan enseignant. Pour ouvrir la séance, reprenez les mêmes références et vérifiez l’admission côté Orgo.
- « J’ai terminé » → consultez l’état de la tâche ou de la tentative. Ékole et l’enseignant examinent ensuite ce que le résultat permet de reconnaître.
- « Publie cette fiche » → identifiez l’audience et le canal, vérifiez la révision et l’autorisation correspondantes, puis indiquez le statut confirmé par le propriétaire.

[Retour à l’index de la documentation](README.md)

## Guides de travail

Suivez [le démarrage](DEMARRAGE.md), [la conception et la publication](AUTEUR_ET_PUBLICATION.md) ou [les instructions de navigation assistée](NAVIGATION_IA.md) selon le travail à faire.
