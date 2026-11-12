# Kidaxion : interface enfant simplifiée de Konnaxion

> **Révision d’architecture — 11 novembre 2026 :** cette page historique est conservée pour ses détails du pilote. La référence transversale actuelle est [Architecture collaborative et interfaces humaines](architecture-collaborative/00_LIRE_EN_PREMIER.md) : Konnaxion y est traité comme **propriétaire des projets, équipes, messages, ressources et portfolios**, Orgo comme propriétaire des tâches des aventures qu’il exécute, et Ékole comme responsable des décisions pédagogiques. Une fonction documentée ou simulée n’est pas nécessairement en production.


## Statut et périmètre

**Kidaxion est le nom retenu pour l'interface enfant simplifiée de Konnaxion.** Il s'agit d'un **composant cible**, non d'un moteur distinct, et **aucune implémentation Kidaxion n'a été identifiée dans les instantanés fournis**. Ce document est une spécification fonctionnelle d'intégration, pas une API déjà disponible.

La conversation, la transmission d'un message, les destinataires et les capacités de communication relèvent de **Konnaxion** et de ses contrats. La disponibilité d'un indice ou le déblocage d'une étape relèvent **d'Orgo**. Les contenus d'apprentissage et la validation des réussites relèvent **d'Ékole**.

## Ce que voit l'enfant dans un World

Une interface très courte et accessible :

- **Mon personnage** : portrait, nom et rôle du jour.
- **Ma mission** : une consigne à la fois, le matériel et l'étape actuelle.
- **Demander de l'aide** : requête à un camarade/enseignant autorisé.
- **Partager un indice** : le transmettre uniquement quand Orgo le permet.
- **J'ai terminé** : soumettre une réalisation ou demander une validation, sans déclarer soi-même une maîtrise.

Des aides visuelles, des consignes orales et un mode de secours enseignant doivent permettre de poursuivre sans dépendre d'un téléphone ou d'une lecture autonome avancée.

## Exemple : rencontre à une station

1. Dans le World *Rallye des métiers*, un enfant incarne la **coiffeuse** et anime une station fictive.
2. Une autre équipe y arrive avec un objectif concret : trouver l'indice qui lui manque.
3. La coiffeuse pose la question prévue, laisse l'autre équipe raisonner et donne un retour.
4. Orgo contrôle si la condition de rencontre est satisfaite et quel **fragment autorisé** peut être révélé.
5. Kidaxion affiche l'information autorisée et Konnaxion transporte l'interaction si un service de communication est nécessaire.
6. L'enseignant peut observer l'échange et, si pertinent, enregistrer dans Ékole une preuve située (expression orale, lecture, collaboration), distincte du statut de la Task.

Aucune conversation libre non modérée ou interaction avec des inconnus ne découle de cette conception. Dans la randonnée à vélo, la rencontre avec une personne nouvellement arrivée dans le pays doit être **une scène préparée et supervisée**, sans demande d'information personnelle.

## Types d'interactions à supporter

| Action | Responsable du contrôle | Conséquence envisagée |
| --- | --- | --- |
| Demander une explication | Konnaxion + règles de session/enseignant | Message ciblé, sans dévoilement de données scolaires privées. |
| Rencontre entre deux personnages | Orgo, avec événements autorisés | Validation d'une condition de quête. |
| Partage d'un fragment | Orgo autorise, Konnaxion transporte | Indice visible seulement par le destinataire autorisé. |
| Vote sur la thématique d'un spectacle | Mécanique de scénario à approuver | Choix collectif traçable, sans classement individuel public. |
| Aide à un pair | Événement/observation distincte | N'est pas convertie automatiquement en note ni en compétence. |
| Absence ou blocage | Enseignant + Orgo | Réaffectation ou fragment de secours, sans pénaliser l'enfant. |

## Garde-fous avant une utilisation réelle

- Identités de mineurs attestées et cloisonnement classe/World/session.
- Permissions côté serveur, jamais déduites du seul affichage ou d'un `role_code`.
- Destinataires autorisés, contenu minimal, audit et durée de conservation définie.
- Aucun accès général à la messagerie Konnaxion par simple appartenance narrative.
- Consentements explicites pour médias, absence de publication d'images d'enfants par défaut.
- Revue humaine avant qu'une interaction ou un média devienne une preuve scolaire conservée.

**Références :** `Konnaxion` et son adaptateur `interaction_kernel`, `Orgo/apps/api/src/orgo/integrations/konnaxion/`, `Kontexte/docs/ekole-orgo/06_MEDIAS_IDENTITE_CONFIDENTIALITE.md`, `Kontexte/data/missions/fete-sorciere.json`.
