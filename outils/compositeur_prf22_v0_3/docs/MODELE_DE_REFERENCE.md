# Ékole — Modèle de référence pour les situations pédagogiques orchestrables

**Identifiant** : `EK-PRF22-THEORIE-002`  
**Version** : `0.2.0-candidate` — 12 novembre 2026  
**Statut** : *proposition de spécification de conception*, non canonique, non publiée, non qualifiée pour une séance scolaire.  
**Support** : profil d'usage candidat **PRF-22** `situation-pedagogique-orchestrable`, archétype principal existant **ARK-15** `composition-hybride`, avec l'appui d'**ARK-10** `parcours-pedagogique`.

## 0. Décision

Une **situation pédagogique orchestrable** est une **hypothèse de conception explicite** : un ensemble contextualisé et modifiable d'activités référencées, de rôles, de dépendances et de ressources, conçu pour susciter des processus d'apprentissage observables, associé à des critères de jugement et à des conditions d'adaptation.

Le **Kristal de situation** est le **plan de conception** de cette situation. Il n'est **ni l'exercice source, ni une séance réelle, ni la preuve qu'un apprentissage s'est produit, ni une autorité d'accès**. Il ne contient pas de données identifiantes d'enfants. Une fiche de situation peut contribuer à plusieurs séances; une séance instancie une révision figée et approuvée de la situation.

**Énoncé de cohérence :** aucune situation ne peut revendiquer un objectif pédagogique sans (a) une activité qui rend l'action possible, (b) un processus observable qui justifie la conjecture, (c) une preuve attendue et des critères de jugement adaptés au mode de participation, (d) un contrat d'adaptation qui déclare ce que l'on conserve ou abandonne, et (e) une revue humaine avant usage réel.

Il s'agit d'une **synthèse proposée pour Ékole**, non d'une norme académique préexistante. La cohérence formelle ne démontre ni efficacité, ni équité, ni sécurité en situation réelle.

## 1. Trois niveaux qui ne doivent pas être confondus

| Niveau | Question | Nature | Validation |
|---|---|---|---|
| **Théorie / principe** | Pourquoi ce dispositif pourrait-il soutenir l'apprentissage ? | Modèle explicatif, justification et conjectures | Sources, limites, confrontation empirique |
| **Ingénierie / composition** | Quelles tâches, ressources, rôles et évaluations concevoir ? | Kristal PRF-22 et répertoires indépendants | Contrats, provenance, alignement, expertise pédagogique |
| **Orchestration / séance** | Comment faire fonctionner le plan ici, maintenant, avec ces enfants et ce matériel ? | Instance de séance dérivée et mutable | Permissions, faisabilité, supervision, observations |

Ne pas transformer un vocabulaire scientifique en garantie. Un tag « CSCL » ou « 4C/ID » constitue une **perspective de conception**, pas une preuve d'efficacité. L'instance peut s'écarter du plan, mais cet écart doit être explicité et tracé par les systèmes autorisés.

## 2. Charpente intégratrice : le *Conjecture Mapping*

L'approche de **Sandoval (2014)** distingue les conjectures sur la façon dont une conception devrait fonctionner des conjectures théoriques liant les processus produits aux résultats attendus. Nous l'adaptons comme suit :

`INTENTION / RÉFÉRENTIEL → CONJECTURE → CHOIX DE CONCEPTION → PROCESSUS MÉDIATEUR → INDICE OBSERVABLE → PREUVE + CRITÈRE → JUGEMENT / RÉVISION`

- **Intention** : objectif d'apprentissage référencé avec provenance, prérequis et portée.
- **Conjecture** : assertion falsifiable ou révisable, datée dans un état **non testée** par défaut; elle mentionne les conditions de validité, les explications alternatives et les signaux qui la mettraient en doute.
- **Choix de conception** : activité(s), contextualisation, interactions, soutien, rôles, matériel.
- **Processus médiateur** : opérations réellement recherchées (comparer, expliquer, débattre, réviser). Il ne se déduit pas de la simple participation.
- **Indice observable** : observation ou trace susceptible de corroborer que le processus s'est manifesté, distinct de la preuve finale d'apprentissage.
- **Preuve** : production ou observation à faire apprécier selon des critères explicites, idéalement par plus d'une modalité pertinente.
- **Jugement** : décision humaine et révision; n'est jamais calculée par le Kristal ni par une preuve brute.

Les conjectures doivent permettre l'échec informatif : absence de débat, résolution purement mécanique, surcharge cognitive, dépendance à un camarade absent, impossibilité d'observer l'apprentissage individuel, etc.

## 3. Fonctions distinctes des cadres scientifiques

| Cadre | Rôle dans PRF-22 | Ce qu'il **ne** donne pas |
|---|---|---|
| **Alignement constructif — Biggs** | Obligation de relier objectif, activité, action attendue, preuve et critère. | Aucun verdict automatique sur la qualité de la mesure ou du critère. |
| **4C/ID — van Merriënboer, Kirschner** | Vérifier la place des **tâches entières**, de l'information de soutien, des indications procédurales et, au besoin, de l'entraînement ciblé. | Les quatre composantes ne doivent pas devenir quatre exercices obligatoires; ne prouve pas une adaptation au primaire. |
| **Cadre conversationnel — Laurillard** | Caractériser les fonctions d'apprentissage : acquisition, enquête, pratique, discussion, collaboration, production. | Une distribution équilibrée des catégories n'est pas une formule d'efficacité. |
| **Scripts collaboratifs / CSCL — Kobbe et al.** | Décrire les participants, rôles, groupes, ressources, activités, distributions et séquences. | Une tâche « en groupe » ne suffit pas à démontrer une compétence collaborative. |
| **Orchestration de classe — Dillenbourg et travaux connexes** | Contraintes de salle, stations, temps, dépendances, imprévus et gestes d'ajustement de l'enseignant. | Le simulateur ne connaît pas à lui seul les vraies capacités de la classe. |
| **CAST UDL 3.0** | Prévoir plusieurs voies d'accès et d'expression sans effacer la compétence réellement évaluée; documenter les obstacles et biais possibles. | Une liste de modalités ne suffit pas à certifier l'accessibilité. |
| **Recherche fondée sur la conception** | Capitaliser observations, contre-exemples et révisions successives. | Un essai en classe ne prouve pas une efficacité générale ni une causalité isolée. |

Les contextes historiques et culturels ne sont pas de simples habillages : toute transformation susceptible de changer les connaissances requises, les normes de représentation, les instruments ou la difficulté demande une nouvelle revue.

## 4. Ontologie minimale et propriétés

### 4.1 Types d'objets (identité séparée)

| Type | Sens et invariant | Propriétaire / porteur envisagé |
|---|---|---|
| `LearningObjective` | Compétence/connaissance visée, critère ou référentiel; identité et version externe | Ékole / référentiel autorisé |
| `ReusableActivity` | Exercice, enquête, tâche entière, aide, entraînement; jamais copié dans une situation | Répertoire externe, responsable à définir |
| `SituatedContext` | Prémisse, époque, lieux, langue, culture, statut réel/fictif, sources et limites | Kontexte et sources pertinentes |
| `DesignConjecture` | Pourquoi certains choix pourraient susciter certains processus | PRF-22 (hypothèse de conception) |
| `AlignmentLink` | Objectif → activité(s) → action → preuve → critère → modalité d'appréciation | PRF-22 |
| `CollaborationScript` | Rôles pédagogiques, dépendances, transferts de productions, conditions de pair | PRF-22 / patrons externes |
| `AdaptationContract` | Invariants, transformations possibles, objectifs non évaluables, barrières | PRF-22 |
| `OrganizationProposal` | Équipes, postes, rotations, durée, ressources et replis possibles pour N | Kompose (dérivé, à approuver) |
| `SessionInstance` | Acteurs réels, classe, autorisations, état d'exécution | Orgo / Konnaxion, selon frontières existantes |
| `LearningEvidence` | Production/observation liée à un participant et jugée par l'enseignant | Ékole et systèmes autorisés; **jamais** dans le Kristal public |

### 4.2 Relations et contraintes

- `Situation` **référence** `Objective`, `Activity`, `Context` ; ces objets conservent leur propriétaire, ID, révision et provenance.
- `Conjecture` **s'appuie sur** des sources théoriques explicitement désignées ; elle **prévoit** des processus médiateurs et des résultats, sans les affirmer comme réalisés.
- `AlignmentLink` lie **exactement** un objectif à une ou plusieurs activités, une preuve définie, des critères et un ou plusieurs modes d'évaluation (`solo`, `collaborative`).
- `AdaptationVariant` annonce pour chaque effectif traité quels objectifs demeurent évaluables et lesquels ne le sont pas. Les deux ensembles sont disjoints et couvrent les objectifs prévus dans ce brouillon.
- `ObjectiveCondition.assessment_requires = peer_interaction` interdit d'affirmer l'évaluation de cet objectif en mode `solo`.
- `Dependency(before, after)` doit désigner des activités existantes et ne pas créer de cycle; son *handoff* reste une **production conceptuelle**, non un transfert autorisé de données personnelles.
- Les rôles pédagogiques ne créent aucun rôle de sécurité, et aucune référence non résolue ne devient automatiquement épinglée ou qualifiée.
- `design_only` et les booléens d'autorisation à `false` sont obligatoires dans ce candidat.

## 5. Contrat de transformation — du solo à 30 enfants

Chaque variante doit préciser : nombre de participants, mode (`solo` / `collaborative`), arrangement envisagé, substitutions, objectifs conservés, objectifs explicitement non évaluables, contrôle du matériel et revue enseignante. Les modes sont définis en termes de **possibilités de preuve**, pas comme une propriété ontologique d'un enfant.

**Invariants obligatoires** : identité et sens de l'objectif, critères adaptés et justifiés, absence de fabrication de preuve, distinction des faits et de la fiction, provenance, frontières de permission, et explicitation des adaptations qui changent la difficulté.

**Transformations envisageables** : époque, narration, personnage, support (Web, Kor, Kamel, papier), groupes, ordre compatible avec dépendances, granularité et temps. Elles nécessitent parfois une requalification pédagogique.

**Transformations interdites sans redéfinition d'objectif** : déclarer une négociation réelle lorsqu'un enfant joue seul; considérer l'expression écrite et l'interaction orale comme identiques lorsque la compétence évaluée exige l'une d'elles; annoncer comme « même difficulté » une activité qui a changé les unités ou prérequis; inventer une source historique pour crédibiliser un récit.

| Effectif témoin | Organisation *candidate* | Conséquence d'évaluation |
|---|---|---|
| 1 | Parcours individuel et documents/indices de substitution | Mesure et explication possibles; **collaboration avec pair non évaluable** |
| 8 | Deux équipes de quatre et échanges vérifiables | Collaboration potentiellement observable sous réserve d'une preuve individuelle suffisante |
| 30 | Environ huit équipes; stations répliquées **seulement si** matériel/encadrement réellement disponibles | Même cible possible, mais attention à l'observation de chaque enfant et à l'équité des rôles |

L'optimiseur ne doit jamais inférer des stations disponibles à partir du nombre d'équipes; il doit demander la capacité et les contraintes effectives à l'enseignant.

## 6. Exigences de validation

### 6.1 Contrôles automatiques (structurels, non pédagogiques)

1. JSON conforme au schéma; toutes les références croisées existent et les identifiants sont uniques.
2. Objectifs, activités, preuves et critères sont liés, avec modes d'évaluation déclarés.
3. Conjectures liées à au moins une source scientifique, un dispositif, un processus médiateur, un résultat et une possibilité de réfutation.
4. Graphe de dépendances acyclique et sans lien vers une activité inconnue.
5. Pour chaque variante, tous les objectifs sont classés « conservé » ou « non évaluable »; aucun objectif nécessitant des pairs n'est évaluable en solo.
6. La version est `design_only`; aucune publication, activation, permission ou donnée d'élève dans le plan.
7. Les références marquées `pinned` exigent un engagement explicite; l'exemple reste volontairement `unresolved`.

### 6.2 Revues humaines obligatoires avant diffusion pédagogique

- **Pédagogique** : exactitude, prérequis, charge, validité des critères, preuve individuelle.
- **Contextuelle** : époques, cultures, langues, histoire réelle/fiction, représentations.
- **Inclusive** : accessibilité, barrière à la lecture/écriture, modalités alternatives sans altération implicite de l'objectif.
- **Opérationnelle** : effectifs, matériel, temps, absence, risques de blocage, replanification.
- **Autorité** : licences, provenance/version des ressources, permissions Konnaxion, approbation Ékole et Orgo.

Un test de schéma réussi ne remplace aucune de ces revues.

## 7. Processus de conception et maturité

1. **Brouillon** — références et hypothèses non testées; peut être visualisé, validé structurellement et révisé.
2. **Revue de conception documentée** — analyses humaines écrites et corrections; **ne confère toujours aucun droit d'activation**.
3. **Pilote autorisé** — instance créée par les services compétents avec comptes, ressources et consentements/licences nécessaires; observations séparées du plan public.
4. **Révision fondée sur observations** — version nouvelle du Kristal avec changements tracés, hypothèses révisées et limites conservées.

Ne pas fusionner `design_review` et `runtime_authorization` : un projet peut être revu mais non autorisé, ou être techniquement lançable mais pédagogiquement inacceptable.

## 8. Articulation avec les logiciels

| Composant | Responsabilité | Frontière |
|---|---|---|
| **Arketype** | Guide la forme de la situation : PRF-22 sur ARK-15, ARK-10 en appui | Ne devient pas moteur de cours |
| **Kristal Framework / Authoring Kit / KristalDiag** | Identité, structure, révisions, références, contrôles de conformité technique | Ne certifie pas l'efficacité pédagogique ni l'autorisation scolaire |
| **Kontexte** | Situations, sources, contexte, personnages et paramètres narratifs | Ne possède pas nécessairement les exercices référencés |
| **Ékole** | Objectifs, interprétations et décisions pédagogiques, suivi autorisé | N'invente pas une preuve issue d'une simulation |
| **Kompose** | Propose composition opérationnelle, groupements, rotations et adaptations | Plans candidats ≠ affectations autorisées |
| **Orgo / Orgo_Worlds** | Exécute des étapes et états autorisés | Le PRF-22 n'admet pas un World |
| **Konnaxion** | Équipes réelles, projets, communications, identités, permissions | Un rôle de mission ne confère pas un accès |
| **Kor / Kamel / Konnaxion Kids** | Projections d'interaction adaptées au public | Ne deviennent pas systèmes d'autorité distincts |

### Interfaces minimales (proposition, non encore implémentées)

- `GET /catalogue/activities` : activités réutilisables, objectifs, capacité, versions.
- `compose(situation_revision, learner_count, resource_constraints)` → `OrganizationProposal` + alertes, **pas** une séance.
- `review(proposal, teacher_attestation, context_review)` → journal externe d'avis, pas activation.
- `authorize_and_instantiate(...)` : appel distinct à définir avec les systèmes propriétaires; impossible depuis ce prototype.

Ces noms sont des **interfaces de conception**; ils ne prétendent pas correspondre à des routes existantes dans les dépôts.

## 9. Fichiers formels du candidat

- `modele/situation-orchestrable.design.v0.2.schema.json` : extension additive stricte du schéma v0.1 (champ requis `pedagogical_model`).
- `exemples/fete-sorciere-theorie.design.json` : exemple fictif non exécutable; objectifs et exercices non résolus.
- `modele/valider_prf22.py` : vérificateur structurel/sémantique local, sans permission d'exécution.
- `tests/test_modele.py` : tests positifs et négatifs, dont le cas solo et les cycles de dépendances.

Toute promotion vers Framework v11/Kristal canonique exige une **décision séparée** : ce schéma ne se substitue pas aux contrats versionnés du Framework et n'invente aucun engagement KQ/KP/KA/KS.

## 10. Bibliographie vérifiée (références de conception, non certification de la proposition)

1. **Sandoval, W. (2014)**. *Conjecture Mapping: An Approach to Systematic Educational Design Research*. *Journal of the Learning Sciences*, 23(1), 18–36. DOI : https://doi.org/10.1080/10508406.2013.778204
2. **Biggs, J. (2003)**. *Teaching for Quality Learning at University* — principe d'alignement constructif. Présentation institutionnelle : https://itali.uq.edu.au/teaching-guidance/principles-learning/guiding-theories-and-frameworks/teaching-frameworks-and-models
3. **van Merriënboer, J. J. G. et Kirschner, P. A.**. *4C/ID* (modèle à quatre composantes). https://www.4cid.org/about/
4. **Laurillard, D.**. *Conversational Framework* / six formes d'apprentissage. Présentation par UCL : https://www.ucl.ac.uk/short-courses/staff-resources/course-design/designing-learning-activities
5. **Kobbe, L. et al. (2007)**. *Specifying computer-supported collaboration scripts*. *International Journal of Computer-Supported Collaborative Learning*. DOI : https://doi.org/10.1007/s11412-007-9014-4
6. **CAST (2024)**. *Universal Design for Learning Guidelines 3.0*. https://udlguidelines.cast.org/

**Traçabilité :** points 0, 4, 5, 6 et 8 constituent des **décisions proposées pour Ékole**, inspirées des travaux ci-dessus et des snapshots fournis; aucun de ces auteurs n'a validé PRF-22 ni l'architecture Ékole.
