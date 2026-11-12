# Contrats formels minimaux — PRF-22 v0.2

## 1. Définition

Une situation de conception s'écrit symboliquement :

\[
S=(O,X,C,R,D,H,A,P,T,V)
\]

avec :

- \(O\) : objectifs pédagogiques externes versionnés;
- \(X\) : activités/exercices externes versionnés;
- \(C\) : contexte situé, ses sources et limites;
- \(R\) : rôles **pédagogiques**, distincts des rôles de sécurité;
- \(D\subseteq X\times X\) : dépendances de production entre activités;
- \(H\) : conjectures de conception, processus médiateurs et limites;
- \(A\) : liens d'alignement objectif–activité–processus–preuve–critère;
- \(P\) : spécifications de preuves attendues **sans données nominatives**;
- \(T\) : contrat de transformation/adaptation;
- \(V\) : exigences de revue, provenance, conditions de validation.

Cette notation est **une proposition formelle d'Ékole**; elle ne vient pas telle quelle de Sandoval, Biggs, Laurillard ou IMS Learning Design.

## 2. Invariants déclaratifs

### I-1 : Couverture des objectifs

Pour tout objectif déclaré \(o\), il existe au moins un lien d'alignement qui le nomme, désigne une activité, un processus attendu, une preuve et des critères :

\[
\forall o\in O,\ \exists a\in A:\ a.objective=o\ \land\ a.activity\neq\varnothing\ \land\ a.evidence\in P\ \land\ a.criteria\neq\varnothing.
\]

**Limite** : la couverture syntaxique ne garantit ni la qualité de la preuve ni la validité du critère.

### I-2 : Dépendances bien formées

Le graphe \(G=(X,D)\) est orienté et acyclique; toute extrémité d'une dépendance fait référence à une activité de \(X\). Son *handoff* est un objet conceptuel, pas une autorisation de transférer des données.

### I-3 : Couverture et modes d'évaluation par variante

Pour une variante \(t_n\) de \(n\) participants :

\[
O = O_{\text{préservés}}(t_n)\ \dot\cup\ O_{\text{non-évaluables}}(t_n).
\]

Un objectif préservé exige un lien d'alignement évaluable dans le mode de cette variante. Un objectif marqué **nécessitant une interaction réelle entre pairs** satisfait :

\[
\text{peerRequired}(o)\ \land\ n=1\ \Rightarrow\ o\in O_{\text{non-évaluables}}(t_1).
\]

Il ne suffit pas de renommer un pair virtuel pour contourner l'invariant.

### I-4 : Provenance et pouvoirs

Les références externes ne passent de `unresolved` à `pinned` qu'après une vérification indépendante par le dépôt propriétaire. L'existence d'une chaîne ressemblant à un SHA-256 ne suffit pas à prouver l'authenticité. Le validateur ne vérifie **que la forme** de ces engagements.

Un document portant `design_only` n'autorise ni publication, ni activation, ni accès à une classe, ni écriture de résultats d'élèves.

## 3. Fonction de planification (future)

On définit une fonction pure *candidate* :

\[
\Phi(S,n,\rho)\longrightarrow\left\{\begin{array}{l}
\operatorname{Proposal}(groupes,postes,rotations,alertes),\\
\operatorname{Conflict}(contraintes\ non\ satisfaites)
\end{array}\right.
\]

avec \(1\le n\le 30\) et \(\rho\) représentant les ressources effectivement disponibles, durées, matériels, locaux, encadrement et contraintes de la classe. \(\Phi\) ne doit pas inventer \(\rho\); la confirmation vient de l'enseignant. Le résultat reste une **proposition** à approuver.

Aucune telle fonction complète n'est implémentée dans ce dossier v0.2. Le compositeur v0.1 possédait un calcul local de rotations, mais son optimisation ne remplace pas l'instanciation autorisée dans Orgo.

## 4. Critères d'acceptation techniques

| ID | Critère | Vérification actuelle |
|---|---|---|
| `T-01` | Enveloppe de conception valide | JSON Schema |
| `T-02` | Références d'objets présentes et uniques | Validateur sémantique |
| `T-03` | Dépendances sans cycle | Validateur sémantique |
| `T-04` | Objectif lié à une activité/preuve/critères | Schéma + validateur |
| `T-05` | Conjecture liée à théorie, activités, objectifs et processus | Schéma + validateur |
| `T-06` | Chaque variante classe tous les objectifs | Validateur sémantique |
| `T-07` | Objectif collaboratif impossible à évaluer en solo | Validateur sémantique |
| `T-08` | Aucun pouvoir d'activation ni donnée enfant dans le brouillon | JSON Schema |
| `H-01` | Alignement pédagogiquement valide | **Non automatisable; revue humaine** |
| `H-02` | Sources historiques et cultures justement représentées | **Non automatisable; revue humaine** |
| `H-03` | Preuves adéquates, interprétation prudente | **Non automatisable; revue humaine** |
| `H-04` | Stations, temps et encadrement matériellement réalisables | **Non automatisable ici; confirmation de terrain** |
| `H-05` | Autorisation scolaire et accès | **Contrôles extérieurs au Kristal** |

**Important** : des tests qui passent signifient « cohérence déclarative vérifiée », pas « efficacité pédagogique démontrée ».
