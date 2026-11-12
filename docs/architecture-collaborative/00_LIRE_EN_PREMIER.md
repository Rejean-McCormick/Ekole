# Ékole — architecture collaborative et interfaces humaines

**Révision :** 2026-11-11 · **Statut :** référence de conception, fondée sur les snapshots fournis, **pas** certification d'un déploiement scolaire.

## Objectif

Permettre à une enseignante ou à un enseignant de choisir une aventure thématique, de préparer un projet de classe avec des personnages-métiers, d'organiser des tâches, de faire collaborer les élèves sur plusieurs supports, puis d'observer leurs apprentissages et de composer un portfolio personnel et collectif. **Ékole est le pilote éducatif d'une mécanique réutilisable** en entreprise, dans un organisme, une administration ou un collectif artistique. Seules les règles de présentation, de protection et d'évaluation changent selon le contexte.

## Une aventure, deux dimensions, trois accès

```text
       KONTEXTE : banque de situations et personnages
                      │
              KOMPOSE + AKOR
       préparation / intentions contrôlées
                      │
          aventure / classe / séance (liens explicites)
                 ╱                    ╲
  Orgo_Worlds + Orgo              Konnaxion_Worlds + Konnaxion
  World opérationnel             World et projet collaboratifs
  Case, Task, état,             équipe, échanges, ressources,
  dépendances, attribution       discussions, votes, portfolio
                 ╲                    ╱
             surfaces Kidaxion adaptées
             WEB · KOR · KAMEL (carte / QR)
                      │
         ÉKOLE + INKUISITE + référentiel
     tentatives, preuves, évaluation par l'enseignant,
            progression et portfolio scolaire
```

*Le schéma est conceptuel : il ne suppose pas que les deux types de Worlds aient les mêmes identifiants, ni que tous ces raccordements soient déjà opérationnels.*

## Règles structurantes

1. **Une aventure thématique** (ex. *La Fête de la sorcière*) est une définition réutilisable dans Kontexte. Pour le pilote, **un World Orgo par scénario** est la convention de découpage du travail, mais une *séance* est une occurrence distincte, bornée à une classe et une version.
2. **Konnaxion n'est pas seulement un transport de messages.** Il gère sa propre vie collaborative. On relie explicitement la séance Orgo au projet et au contexte Konnaxion pertinents.
3. **Un objet, un propriétaire.** Pour les tâches d'une mission Orgo, Orgo est canonique; pour les messages/ressources/projets Konnaxion, Konnaxion est canonique; pour la décision pédagogique, Ékole est canonique. Les vues croisées sont des *projections*, pas des doubles écritures.
4. **Kidaxion est une expérience jeunesse**, non un troisième moteur : elle présente les actions autorisées sur navigateur Chromebook, Kor (Android) ou carte Kamel imprimée.
5. **Identité ≠ personnage ≠ permission.** Le rôle `fermier` est narratif; l'autorisation est personnelle, bornée à une séance et vérifiée côté serveur.
6. **Réalisation ≠ maîtrise.** Orgo peut confirmer une tâche, Konnaxion une contribution, Inkuisite une tentative; l'enseignant détermine ce que ces événements prouvent pédagogiquement.
7. **La confidentialité scolaire l'emporte sur les défauts publics** des produits génériques. Aucun déploiement à de vrais mineurs avant contrôle de la lecture, de l'écriture, de l'audience et de la conservation.
8. **Pas de duplication d'infrastructures.** Ni deuxième moteur de Task dans Ékole, ni copie du portfolio Konnaxion, ni second transport des interactions, ni jeton de pouvoir caché dans une carte.

## Parcours de lecture

| Document | Décision documentée |
| --- | --- |
| [01 — Cartographie et autorités](01_CARTOGRAPHIE_ET_AUTORITES.md) | Ce qui existe, qui possède quoi, éviter les doublons |
| [02 — Worlds, projets et séances](02_WORLDS_PROJETS_ET_SEANCES.md) | Limites de monde, identité, cardinalités et liaison explicite |
| [03 — Collaboration Konnaxion](03_KONNAXION_COLLABORATION.md) | Équipes, messages, ressources, contributions, votes, évaluations |
| [04 — Web, Kor, Kamel et Kidaxion](04_KIDAXION_WEB_KOR_KAMEL.md) | Trois surfaces, mêmes actions et références |
| [05 — Réussites, évaluation, portfolio](05_PREUVES_EVALUATIONS_PORTFOLIOS.md) | Chaîne de preuve et rôles respectifs d'Ékole et KonnectED |
| [06 — Contrats et échanges](06_CONTRATS_ET_EVENEMENTS.md) | Identifiants, commandes, événements et idempotence |
| [07 — Parcours concrets](07_SCENARIOS_ET_PARCOURS.md) | Fête, vélo, spectacle, mamie et stations |
| [08 — Sécurité des enfants](08_SECURITE_ET_CONFIDENTIALITE.md) | Barrières de mise en service et modèles de menace |
| [09 — Feuille de route et recette](09_FEUILLE_DE_ROUTE_ET_RECETTE.md) | Mise en œuvre minimale et tests de bout en bout |
| [10 — Sources et statut](10_SOURCES_ET_STATUT.md) | Fichiers réellement examinés; état prouvé, proposé ou bloqué |

La note [CONTRAT_LIAISON_SEANCE.exemple.json](CONTRAT_LIAISON_SEANCE.exemple.json) est **un exemple proposé**, non un contrat déjà déployé. Le document [CONTRAT_LIAISON_SEANCE.schema.json](CONTRAT_LIAISON_SEANCE.schema.json) est destiné à qualifier les adaptations futures, pas à admettre une séance en production.

## Portée de cette livraison

Mise à jour **documentaire** du dépôt `C:\mycode\Ekole\ekole`. Elle ne déploie pas de World, ne crée aucun compte d'enfant, ne change aucune permission serveur et ne rend ni Kor, ni Kamel, ni Kidaxion opérationnels pour la classe. Les lots Tandem antérieurs restent tels quels.
