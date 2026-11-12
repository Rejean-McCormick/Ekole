# 09 — Mise en œuvre optimisée et recette commune

**Principe de livraison :** développer la chaîne **en tranches verticales** vérifiables, sans gros déploiement simultané, sans double écriture et sans réduire les barrières de sécurité pour faire passer une démonstration.

## Ordre de construction recommandé

### P0 — Contrat commun et preuve d'isolation (bloquant)

**Dépôts :** Ékole, Orgo/Orgo_Worlds, Konnaxion/Konnaxion_Worlds, Kompose, Akor, Interaction Kernel si profil nécessaire.

- Ratifier les identifiants de séance, versions, références de Worlds, projet et objet Task.
- Décider quelle API assure la liaison des deux types de Worlds et l'identité scolaire vérifiée.
- Épingler le propriétaire de chaque écriture (voir 01), refuser les doublons de Task.
- Durcir la lecture et l'écriture des projets/messages/ressources Konnaxion (code actuellement trop ouvert pour des classes privées).
- Valider identité, enseignant, appartenances et protection des enfants avec **deux classes fictives**.

**Terminé lorsque :** aucune demande anonyme, étrangère à la classe, expirée ou issue d'un mauvais World ne peut lire ou modifier un objet scolaire.

### P1 — Une séance « La Fête de la sorcière » réelle et minimale

**Dépôts :** Kontexte, Orgo_Worlds, Orgo, Kompose, Akor, Ékole.

- Sélectionner le scénario Kontexte versionné et vérifier les garanties structurées.
- Enseignant prépare, modifie et approuve les personnages/équipes proposés.
- Créer **une séance réelle** liée à un World Orgo isolé et à la Case/aux Tasks autorisées; ne plus utiliser la fixture de revue synthétique comme preuve de production.
- Un enfant fictif voit une tâche, répond et reçoit un état **confirmé par Orgo**.
- Un enseignant peut suspendre, rejeter, reprendre et clôturer les opérations.

**Terminé lorsque :** tâche et dépendance réelles prouvées avec contrôle des droits, sans contourner l'injecteur et sans admission implicite.

### P2 — Collaboration Konnaxion réelle dans la même séance

**Dépôts :** Konnaxion, Konnaxion_Worlds, Ékole (projection), éventuellement Kor.

- Associer explicitement le projet Konnaxion à la séance et au World Orgo.
- Isoler équipe, conversation, ressource et audience; mapper les identités sous politique scolaire.
- Demande d'aide + réponse + ressource + indice libéré, avec traces et modération.
- Une Task Orgo apparaît en consultation dans le projet, **sans deuxième état modifiable**.
- Démontrer un projet Konnaxion autonome où `ProjectTask` reste propriétaire lorsque Orgo n'est pas impliqué.

**Terminé lorsque :** l'interaction est conservée par Konnaxion et le travail opérationnel par Orgo, avec reçus d'autorité distincts.

### P3 — Évaluation et portfolio

**Dépôts :** Ékole, Inkuisite, Kontexte, Konnaxion / KonnectED.

- Faire revoir par l'enseignant les 55 correspondances candidates avant de les utiliser comme liens curriculaires reconnus.
- Relier les tentatives et observations au bon enfant, à la bonne consigne et au bon objectif validé.
- Valider séparément `tentative`, `tâche réalisée`, `preuve acceptée`, `compétence démontrée` et `réalisation sélectionnée au portfolio`.
- Adapter une **projection sécurisée** du portfolio KonnectED, plutôt que recopier les dossiers et notes scolaires.
- Produire un bilan pour l'enseignant avec explication des recommandations, jamais un rang public d'enfants.

**Terminé lorsque :** une réussite avec aide puis une réussite autonome sont correctement distinguées et la publication d'un artefact peut être retirée sans perdre le suivi pédagogique.

### P4 — Trois interfaces du même travail

**Dépôts :** Ékole/Kidaxion Web, Kor, Kamel, services propriétaires.

- Une même Task accessible depuis un navigateur Chromebook puis Kor Android et une carte Kamel.
- Impression noir et blanc/couleur; QR de navigation sans secret; variante supervisée hors caméra.
- Test de reprise après panne, de double scan et de tentative hors ligne.
- Profil d'expérience jeunesse simple, sans nouvelle base de missions ni de permissions.

**Terminé lorsque :** les trois canaux aboutissent à **un seul état métier confirmé** et à une preuve pédagogique rattachée au même `session_ref`.

## Jeu de tests de bout en bout

| Cas | Résultat attendu |
| --- | --- |
| Deux classes utilisent le même scénario | Aucun mélange de participants, fichiers, messages ou preuves |
| Élève A tente de consulter la Task/ressource de B | Rejet côté serveur; pas seulement bouton caché |
| Ancienne carte/QR de la séance précédente | Pas de mutation, statut explicite de refus |
| Même action envoyée deux fois | Une seule mutation canonique; reçus corrélés |
| Élève demande de l'aide sur la tâche | Konnaxion conserve l'interaction, Orgo conserve la Task |
| Message « travail fini », Task pas encore validée | Pas de clôture automatique Orgo ni de compétence attribuée |
| Proposer/choisir le thème d'un spectacle | Vote de projet supervisé, pas notation des participants |
| Connexion perdue pendant un envoi Kor | Brouillon/pending; pas de faux succès |
| Une carte papier est utilisée sans appareil | L'enseignant peut entrer une observation avec traçabilité |
| Enseignant refuse une preuve pédagogique | Task éventuellement terminée, compétence non démontrée |
| Un travail collectif est choisi pour portfolio | Authorship/coproduction reconnus, audience contrôlée et révocable |
| Retrait d'un élève d'une séance | Plus d'accès aux nouveaux événements, caches invalidés |
| Release Konnaxion/Orgo promue entre deux séances | Historique reste associé à la version réellement utilisée |

## Indicateurs d'optimisation

- **Un seul état par objet canonique** : aucune divergence Orgo Task / Konnaxion ProjectTask pour un projet piloté Orgo.
- **Rapidité pédagogique** : le professeur peut choisir, préparer et lancer une aventure sans comprendre l'architecture technique.
- **Faible charge cognitive** : l'enfant voit une action principale et une aide claire.
- **Reprise fiable** : doublons, panne, QR copié et hors ligne sont explicites et récupérables.
- **Portabilité du contenu** : une mission Kontexte n'est ni copiée à l'identique dans les cinq applications ni activée pour toutes les classes.
- **Traçabilité** : chaque réussite renvoie à une source, une séance, un objectif et une décision, sans journal excessif de données personnelles.

## Conditions de déploiement

Les lots précédents sont des **tests de code et de préparation**, pas une admission d'élèves. Avant production : essais réels sur des services intégrés, authentification, politiques d'accès, sécurité des médias et des portfolios, validation institutionnelle et protocole de retrait. Aucun « taux de complétion » de cette architecture n'est inféré à partir des seules simulations.
