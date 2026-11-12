# 04 — Kidaxion : une expérience commune sur Web, Kor et Kamel

**Positionnement :** Kidaxion est le **profil d'interaction jeunesse** au-dessus des actions Orgo et des espaces Konnaxion autorisés. Il n'est ni une nouvelle base sociale, ni un nouveau moteur de tâches, ni forcément une nouvelle application autonome.

## Trois canaux réels ou potentiels

| Canal | Usage adapté | État vérifié | Limite |
| --- | --- | --- | --- |
| **Web hébergé** | Chromebook scolaire : accès sans installation; projet, tâches, messages, productions et portfolio | Ékole et Konnaxion possèdent des interfaces Web, **pas** un portail Kidaxion scolaire de bout en bout | Construire une vue intégrée et authentifiée; courriel seul insuffisant |
| **Kor** | Android : recevoir alertes, voir surfaces autorisées, scanner QR, envoyer réponse, consulter les objets | ADR et code de projection mobile, QR et files hors ligne présents | Le profil jeunesse et la liaison scolaire ne sont pas qualifiés; pas une application Chromebook universelle |
| **Kamel** | Cartes imprimées : personnage, station, consignes, indice, rappel, vérification à quatre étapes | Compilation/assemblage/rendu et impression présents | QR d'action, émission/validation de droits et remontée vers Orgo non raccordés |

Le **navigateur Chromebook** est le canal principal recommandé pour commencer. Kor peut être un autre terminal lorsque le parc et l'âge l'autorisent. Kamel est une **vraie interface humaine** même sans écran : l'enseignant peut recevoir et valider une réponse faite sur papier, puis la saisir dans le système sous son propre compte.

## Contrat d'affichage minimal

L'écran ou la carte affiche uniquement :

- **Où je suis** : aventure, classe/séance, station ou groupe (noms adaptés à l'enfant).
- **Mon personnage** : fermier, sorcière, messager... sans exposer la structure de permissions.
- **Ce que je fais maintenant** : une action principale, consigne courte, image/pictogramme si pertinent.
- **À qui demander de l'aide** : personne ou groupe autorisé, sans annuaire global.
- **Ce que je peux partager** : champ ou document filtré, et sa portée.
- **Ce que j'ai fait** : tentative envoyée, en révision, confirmée ou à reprendre.
- **Mon portfolio** : sélection privée de travaux et commentaires approuvés, pas un tableau de classement.

Actions proposées (seulement si autorisées) : `voir_ma_mission`, `ouvrir_ma_tache`, `demander_aide`, `partager_ressource`, `proposer_indice`, `envoyer_reponse`, `demander_revision`, `voir_retroaction`, `choisir_une_realisation_portfolio`.

Une vue ne doit **jamais** interpréter un bouton « J'ai terminé » comme une réussite pédagogique. Elle affiche l'état renvoyé par l'autorité métier.

## Sémantique d'action cohérente

```text
Interface Web / Kor / Kamel
   → intention minimale (référence + action)
   → authentification / droits / contexte côté serveur
   → service propriétaire Orgo OU Konnaxion OU Ékole
   → accusé de réception / décision / projection fraîche
```

Distinguer à l'écran :

1. **Brouillon local** : pas transmis.
2. **Envoyé** : transport reçu, propriétaire pas encore confirmé.
3. **Accepté** : domaine propriétaire a admis l'action.
4. **Réalisé / approuvé** : état métier changé, ou preuve revue selon son propriétaire.

Ces états protègent notamment les usages hors ligne de Kor et les scans répétés.

## Cartes Kamel et QR

Trois profils de carte doivent être distingués :

- **Carte informative** : station, rôle, consigne, illustration, code court. Aucun secret.
- **Carte de navigation** : QR ouvrant un lien vers une tâche dans le contexte du bon World; l'enfant doit **quand même** être authentifié.
- **Carte d'action ponctuelle** : si un QR signé devient nécessaire, il doit être émis par un service de confiance, scoped à une action/séance, expirant, révocable, anti-rejeu et avec validation de porteur. Kamel n'émet pas lui-même la permission.

Une photocopie de carte ou une capture d'écran ne doit jamais permettre de soumettre le travail d'autrui. Impression N&B possible : contraste suffisant, symbole lisible sans couleur, texte/numéro de rechange si QR impossible. Aucun nom complet, résultat scolaire confidentiel ou token réutilisable sur une carte.

## Expérience 3e année

- Français québécois simple, vocabulaire court, boutons larges, support clavier, lecteur d'écran, option d'écoute lorsque disponible.
- Progression par petites étapes : une tâche principale, aide à la demande, reprise sans humiliation.
- Pas de fil public ni de compteur de popularité; les échanges suivent l'audience autorisée.
- Possibilité d'être **acteur de station** (ex. coiffeuse incarnée) ou **participant en quête**, avec le même contrôle d'identité.
- Séance courte et récupérable; appareil partagé avec déconnexion explicite et protection des caches.

## Utilisation transversale

En usine, l'écran pourra exposer davantage de détails techniques et l'application Kor sera centrale. Dans une collectivité, le vote et la co-création pourront être plus riches. Le contrat métier reste identique; **seuls le profil de présentation, les habilitations et le niveau de preuve changent**.

## Sources / état

- `Kor/adr/0020-mobile-projection-of-konnaxion-orgo.md` : projection, pas second système.
- `Kor/docs/04_BOUNDARIES_AND_OWNERSHIP.md`, `docs/10_MANDATE_QR.md` : états, preuves de mandat, hors ligne.
- `Kamel/docs/06-cartes-et-editions.md`, `docs/14-securite-gouvernance-et-publication.md` : rendu, édition, publication.
- `Konnaxion/frontend/lib/kidaxion-intents.mjs` (lot 2 installé par overlay) : création d'intentions contrôlées **hors autorisation serveur**.
