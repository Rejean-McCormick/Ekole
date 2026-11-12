# PRF-22 v0.3 — Contrats et propriétaires

## Chaîne de production

`Kontexte (trames, missions, activités, référentiel candidat)` → `Atelier Ékole PRF-22 (plan de conception + justification théorique)` → `plans d'organisation candidats (planificateur local repris de v0.1)` → `revue de l'enseignant` → `handoff proposé`.

**L'export ne passe pas par les API Kompose, Orgo ou Konnaxion.** Le champ `owner_hints` précise seulement les responsabilités envisagées : ce n'est ni un contrat de réception négocié ni une commande exécutable.

| Artefact | Format | Droits ou état |
|---|---|---|
| Kristal de conception | `ekole.situation-orchestrable.design/0.3` | `design_only`, références `unresolved` |
| Brouillon rééditable | `ekole.prf22.authoring/0.3` | Édition locale, sans données réelles |
| Proposition de liaison | `ekole.prf22.handoff/0.3` | `proposal_only_not_authorized`, toutes actions runtime `false` |
| Plan d'équipe/station | `ekole.situation-composition-draft/0.1` | `draft_not_admitted`, participants anonymes fictifs |
| Workspace Arketype | Stub créé par le Kit existant | `published=false`, `authorized_for_publication=false` |

Les empreintes `source_observations[].observed_sha256` documentent **les octets locaux constatés**. Elles ne sont jamais des engagements de provenance de l'éditeur; les `pin_status` demeurent `unresolved`.

## Évolutions minimales par rapport au schéma de conception v0.2

Le contrat v0.3 rend explicites :

- `context.source_situation` : référence externe de la trame ou mission.
- `context.cultural_frame` et `context.language` : maintien du contexte rédigé par l'enseignant.
- `conjectures[].conjecture_statement` : assertion **explicite**, révisable, de la théorie de l'action.

Les autres invariants de v0.2 restent : références non absorbées, objectifs couverts, preuves liées, dépendances sans cycles, 1/8/30 explicités, statut `design_only`, aucune autorité runtime.

## Prochain raccordement (pas dans cette livraison)

1. Définir avec Kompose un vrai **contrat de consommation** des contraintes de stations/rôles et des dépendances; ne pas supposer que le format de transfert candidat est déjà un contrat natif.
2. Résoudre les références des exercices/objectifs par leurs propriétaires, enregistrer les engagements autorisés et licences.
3. Créer une transition explicite « dossier revu → plan approuvé » avec signatures/contrôles métier Ékole.
4. Implémenter les adaptateurs autorisés Orgo et Konnaxion, tester chaque garde de permission avant admission.
5. Créer une qualification de la matérialisation Kristal v11 distincte du simple stub Arketype.

Cette séparation évite que le Kristal soit confondu avec le moteur de séance ou avec les preuves d'apprentissage.
