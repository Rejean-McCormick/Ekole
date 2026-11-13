# Ékole PRF-22 v0.6 — banque enrichie et studio enseignant intégré

## Résultat

- **137 propositions** issues des mêmes **77 sources Kontexte**; la banque initiale `candidats-v0_4/` demeure versionnée et inchangée.
- Bibliothèque indépendante **51 patrons d'activités candidates** rédigés pour Ékole. Aucune des 51 ressources n'est présentée comme un exercice source Kontexte ou comme une ressource homologuée.
- **76 activités distinctes mobilisées et 64 objectifs distincts**, versus 26 et 25 dans la banque v0.4. Ne pas interpréter ces chiffres comme une augmentation démontrée de la qualité.
- Nouvel espace `/prf22/index.html` **dans le même atelier enseignant Ékole** (pas de deuxième application serveur).
- Révision en navigateur des conjectures, observations, preuves et critères, enregistrée séparément sous `banques/prf22/revisions-local/`.
- Toute révision conserve les références, l'origine et le statut **non approuvé**; aucune création de World, séance, équipe ou accès enfant.

## Démarrer sur Windows

Depuis `C:\mycode\Ekole\ekole` :

1. `VERIFIER_BANQUE_ENRICHIE_PRF22.cmd` : vérifier les 137 dossiers et leurs empreintes (les sources Kontexte doivent correspondre au snapshot).
2. `LANCER_ATELIER_SITUATIONS_PRF22.cmd` : démarrer l'éditeur Web local avec les sauvegardes locales activées; la fenêtre du lanceur fournit un **lien de session enseignant** (token local).
3. Depuis la page principale de l'éditeur, cliquer **Situations PRF-22 · Compositeur**; ou sur le même serveur enseignant accéder à `/prf22/index.html`.
4. Rechercher une situation, sélectionner un objectif, revoir les champs et cliquer « Enregistrer une révision locale ».
5. `GENERER_BANQUE_ENRICHIE_PRF22.cmd` : créer une nouvelle banque candidate sous `banques/prf22/generations/`, avec vérification et sans écraser les banques précédentes.

Pour un démarrage Ékole avec un dépôt de contenu, conserver le lanceur existant de ce dépôt. Le nouveau studio est disponible sur le serveur d'édition déjà authentifié du moteur Ékole. Le compositeur Tkinter avancé et sa commande d’export reconnaissent aussi les 51 patrons complémentaires Ékole, avec provenance propre. L'enregistrement demande l'option `--edition`.

## Contrats de sécurité et limites

- L'API `/api/prf22/*` n'existe que sur le serveur enseignant et requiert sa session; le portail élève ne peut lire ni index ni dossiers.
- Pour écrire : `--edition`, session enseignante, `X-Ekole-CSRF`, `Origin` et `Host` locaux, taille bornée, schéma PRF-22 validé.
- Les demandes de révision n'ont accès **qu'aux champs textuels pédagogiques**; impossible de substituer une activité, l'identifiant de source, la qualification, les permissions, ou de modifier la banque immuable.
- Révisions locales non commitées automatiquement et non exposées au portail élève.
- Les patrons Ékole sont des hypothèses de conception, **pas** des exercices évalués ou approuvés. Les rapprochements objectifs/activités restent heuristiques. L'exactitude historique/culturelle, les programmes, l'accessibilité et la faisabilité des postes demandent une revue humaine.
- Un parcours solo ne démontre aucune compétence de collaboration avec des pairs. Les plans de 30 participants nécessitent vérification du matériel, de l'espace et de l'encadrement.
- La page Web intégrée révise les **propositions existantes**; le compositeur avancé Tkinter demeure utile pour créer une situation de zéro et modifier activités/organisations. Une fusion complète des deux éditeurs n'est pas encore livrée.

## Propriété des composants

- Kontexte : scénarios, activités et objectifs historiques; **inchangés**.
- Ékole : bibliothèque complémentaire, index de composition, studio de révision, métadonnées, validation locale.
- Arketype/Kristal : PRF-22 demeure un profil de conception, pas une activation.
- Kompose/Orgo/Konnaxion : pas de mutation dans ce lot; transmissions candidates seulement.

## Reproductibilité

- `banques/prf22/candidats-v0_6/MANIFEST.json` lie les sources Kontexte par SHA-256 et conserve la provenance séparée des activités proposées Ékole.
- `SNAPSHOT_SHA256.json` contrôle les documents, brouillons, handoffs, **ainsi que les plans 1/8/30**.
- Le générateur refuse d'écraser une sortie existante.
- L'installateur peut rétablir les fichiers antérieurs, mais ne supprime pas les révisions locales créées après coup.
