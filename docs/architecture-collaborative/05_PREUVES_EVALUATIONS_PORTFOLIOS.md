# 05 — Réussites, évaluations, progrès et portfolios

## Quatre concepts distincts

1. **Activité réalisée** : fait opérationnel, par exemple « la Task Orgo a été terminée ».
2. **Contribution collaborative** : fait social, par exemple « une ressource a été déposée dans un projet Konnaxion » ou « un indice a été partagé ».
3. **Preuve pédagogique** : observation interprétable liée à un objectif, au contexte de travail et au niveau d'aide.
4. **Compétence reconnue** : décision pédagogique de l'enseignant fondée sur une ou plusieurs preuves.

Aucun des trois premiers n'implique automatiquement le quatrième.

## Sources de preuve — sans double stockage inutile

| Provenance | Exemple | Propriétaire | Ce que reçoit Ékole |
| --- | --- | --- | --- |
| Orgo | Task terminée et revue | Orgo | Référence de tâche, état admis, horodatage et acteur authentifié |
| Konnaxion | Contribution, message, aide ou ressource | Konnaxion | Référence d'interaction, contexte, auteur et audience autorisée; pas nécessairement le texte brut |
| Inkuisite | Tentative, réponses, résultat d'exercice | Inkuisite | Identifiant de tentative, objectif candidat, résultat et référence de correction |
| Ékole / enseignant | Observation en classe, réalisation papier, autonomie, démarche | Ékole | Note d'observation protégée, critère, validation et provenance |
| KonnectED | Évaluation ou portfolio générique | Konnaxion | Projection interopérable **si** un accord de correspondance et d'audience existe |

Ékole peut constituer un **EvidenceLog** de références vérifiées. Il ne doit ni recopier tous les messages sociaux ni déduire l'identité d'un enfant de son personnage ou d'un QR.

## Schéma de preuve pédagogique proposé

```json
{
  "evidence_ref": "ev-demo-001",
  "session_ref": "seance-demo-001",
  "subject_ref": "eleve-pseudonyme-001",
  "objective_ref": "objectif-revu-001",
  "source": { "owner": "orgo", "object_ref": "task-demo-003", "receipt_ref": "receipt-demo-003" },
  "observation": "A expliqué la vérification des pneus à une autre équipe",
  "assistance": "peer_supported",
  "evidence_state": "submitted_for_review",
  "review": { "decision": "pending", "reviewer_ref": null }
}
```

Ceci est **un exemple de structure cible**, pas un événement produit par le code. La source concrète est attestée uniquement après un reçu vérifié du propriétaire et le contrôle de la bonne séance. Une preuve peut être invalide, retirée ou corrigée sans effacer l'audit.

## Suivi utile à l'enseignant

Pour chaque objectif :

- occasions rencontrées (`encountered`), tentatives (`practiced`), démonstrations (`demonstrated`);
- nombre de tentatives et de réussites, **distinguées** de la qualité/variété des preuves;
- autonomie : seul, en équipe, avec aide, guidage adulte;
- contexte : même type d'exercice répété ou transfert dans une nouvelle situation;
- date, version de consigne, critère d'observation, statut de revue;
- décisions et prochaines opportunités recommandées, sans classement de la classe.

Les 55 associations de compétences du lot 2 sont des **candidats non approuvés**. Ne pas renseigner les `curriculum_ids` ni déduire une maîtrise sans revue pédagogique. Les dix missions historiques bloquées pour sécurité structurée restent bloquées.

## Deux portfolios, pas deux vérités

**Portfolio pédagogique Ékole** : collection privée et contextualisée de réalisations, réflexions, critères d'évaluation, décisions enseignantes et progrès d'une personne. La référence d'évaluation scolaire demeure dans Ékole.

**Portfolio Konnaxion / KonnectED** : présentoir collaboratif de ressources, réalisations ou certifications lorsque la politique et les permissions l'autorisent. Son modèle actuel `Portfolio.items` pointe vers des `KnowledgeResource`. Les preuves Ékole ne sont pas des `KnowledgeResource` par magie : établir un **adaptateur de références approuvées** et une règle de visibilité explicite.

L'enfant peut sélectionner « mon affiche », « le texte que j'ai écrit », « le calcul que j'ai corrigé », « l'aide que j'ai apportée ». Le système doit distinguer :

- **portfolio privé** élève–enseignant–personnes autorisées;
- **vitrine de projet de classe** (artefacts collectifs seulement après revue);
- **publication externe** (désactivée par défaut pour le pilote et soumise à un processus distinct).

Des droits de retrait, correction, traçabilité de copropriété et conservation sont nécessaires. Une photo ou une voix d'enfant ne doit pas être rendue publique par simple ajout à un projet.

## Évaluations et interactions sociales

`konnected.Evaluation` stocke score et métadonnées; `PeerValidation` contient une décision de pair; `Portfolio` contient une collection. Ces objets existent, mais leurs règles génériques **ne remplacent pas une grille scolaire**. L'enseignant décide si une validation par les pairs est utile comme rétroaction; elle **ne valide jamais automatiquement** une note.

**Jamais** utiliser `ProjectRating` (+1/-1), Smart Vote pondéré par EkoH, réputation, popularité d'un message, volume d'interactions ou temps de connexion comme mesure de valeur personnelle, de compétence ou de réussite d'un enfant. L'entraide peut être documentée par une observation contextualisée, jamais par un score public de personne.

## Recommandation d'activités

Ékole peut proposer des tâches selon : manque d'occasions, diversité des situations, preuves encore provisoires, préférences et contraintes de la classe. Les propositions restent **explicables et modifiables par l'enseignant** : « deux occasions observées, aucune démonstration autonome » plutôt qu'une étiquette permanente de faiblesse. Préserver la complémentarité : un enfant peut aider sur sa force et pratiquer un domaine à développer au cours d'une autre mission.

## Revue et audit

Chaîne cible : `source event → preuve candidate → revue pédagogique → état de compétence → recommandation → portfolio sélectionné`. Chaque transition conserve `who/when/why/which version`. Le retrait d'une publication ne doit pas effacer la décision pédagogique originale, qui reste soumise aux règles de conservation du dossier scolaire.
