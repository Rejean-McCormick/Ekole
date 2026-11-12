# 08 — Sécurité, droits et confidentialité des enfants

**Statut :** conditions de mise en service, non attestées par les snapshots. Les protections d'un produit généraliste ne peuvent pas être supposées adéquates pour des dossiers d'élèves de primaire.

## Problème réel repéré dans le code Konnaxion

Les `ProjectViewSet`, `ProjectResourceViewSet`, `ProjectTaskViewSet`, `ProjectMessageViewSet` et plusieurs autres surfaces de `backend/konnaxion/keenkonnect/api_views.py` utilisent `permissions.IsAuthenticatedOrReadOnly`. Le commentaire de `ProjectMessageViewSet` précise que **la lecture est ouverte à tous par défaut**. Même si d'autres filtres ou déploiements peuvent intervenir, ce code **ne démontre pas** une isolation de classe suffisante pour diffuser des conversations d'enfants.

**Conséquence :** ne pas brancher Kidaxion sur ces endpoints tels quels pour une classe réelle. Ajouter une politique **côté serveur** de membre/projet/World/séance et des querysets limités, puis tester les accès négatifs. Masquer des boutons dans le frontend ne protège rien.

## Garanties obligatoires

1. **Identité vérifiée :** e-mail scolaire seul ne suffit pas; une authentification scolaire compatible avec la situation locale, session courte et révocation contrôlée. Personnages non authentifiants.
2. **Worlds isolés :** Konnaxion_Worlds et Orgo_Worlds ont chacun leurs propres memberships, permissions, releases et périmètres; tout pont est explicitement autorisé.
3. **Moindre privilège :** l'enfant ne voit que sa classe, sa séance, sa mission, ses interactions et les données publiées pour son rôle. Enseignants/administrateurs sont soumis à leurs propres contrôles.
4. **Séparation des droits :** lire une tâche, transmettre un indice, modifier un projet, approuver une compétence ou publier un portfolio sont des privilèges différents.
5. **Modération et supervision :** audience fermée, rapports/signalements, gestion d'un enfant absent, suspension d'une station, contrôle des ressources et des messages.
6. **Évaluations protégées :** résultats, portfolios et rétroactions privés par défaut, pas de recherche globale ni d'affichage public des profils EkoH.
7. **Documents et médias :** pas de photos/voix nominatives sans base d'autorisation et politique scolaire explicite. Provenance, copropriété, retrait et journal d'accès.
8. **Consentement et conservation :** politiques de finalité, rétention, export, correction et suppression documentées avec l'établissement responsable; éviter la télémétrie superflue.
9. **Journalisation proportionnée :** conserver des traces d'autorisation et reçus sans recopier du contenu sensible. Chiffrer les transferts; protéger les données au repos selon le déploiement.
10. **Accessibilité :** équivalents papier, lecture assistée, absence de sanction pour impossibilité de scanner un QR ou d'avoir un appareil.

## Risques propres aux trois interfaces

| Risque | Défense requise |
| --- | --- |
| Chromebook partagé et autre élève déjà connecté | Session bornée, écran de sortie explicite, purge de cache, aucune identification par simple courriel saisi |
| QR Kamel photocopié ou photographié | Pas de secret durable sur la carte; identification + vérification côté serveur; QR d'action court, signé et anti-rejeu si nécessaire |
| Kor hors ligne affiche une vieille assignation | Marquer « à revalider »; appliquer révocation/expiration; aucun résultat affiché comme committé sans reçu propriétaire |
| Cross-World ou cross-classe | Validation stricte de tuple World/release/projet/séance/participant; pas de fallback à un World par défaut |
| Utilisation des votes/popularité pour noter | Votes thématiques simples; interdiction de convertir `ProjectRating`, EkoH ou nombre de messages en note |
| Document de groupe privé accessible par lien direct | Authentifier le téléchargement, contrôler l'audience et la durée des URLs; tester l'accès anonyme |
| Message contenant un indice privé avant déblocage | Condition de déblocage autorisée dans Orgo; projection filtrée; Konnaxion ne déduit pas l'autorisation du seul `role_code` |
| Retrait d'une permission en cours d'activité | Invalider sessions, invitations, caches et liens; maintenir la traçabilité de la révocation |

## Ce qui ne constitue pas une autorisation

Une validation JSON, la présence d'un World Pack, l'injecteur synthétique Orgo, une prévisualisation enseignant, un scénario à 11 tâches, une demande `kidaxion-intents.mjs`, un code QR, une carte et même un reçu de transport ne suffisent **jamais**, pris seuls, à admettre une action scolaire réelle.

## Séquence de qualification obligatoire

1. Revue sécurité des API Konnaxion et Orgo utilisées.
2. Tests d'isolation avec **deux classes, deux élèves, deux enseignants et deux Worlds**.
3. Tests de droits anonymes, permissions révoquées, ID devinés, ressources directes, messages privés, QR copiés et retries.
4. Validation de la conservation et des audiences du portfolio et des évaluations.
5. Essai supervisé avec identités fictives, puis autorisations institutionnelles nécessaires avant toute utilisation avec de vrais enfants.

**Blocage de production :** tant que ces conditions ne sont pas remplies, les interactions restent des simulations ou des maquettes, et toutes les données de tests doivent être synthétiques.
