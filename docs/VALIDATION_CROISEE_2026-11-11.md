# Validation croisée Ékole × Orgo × Kidaxion — 11 novembre 2026

> Statut : audit du code contenu dans les 13 dépôts fournis, hors exécution de services réels. Ce document ne vaut ni qualification de production ni preuve de conformité pour des comptes d’enfants.

## 1. Dépôts reçus et périmètre

- `C:\mycode\Ekole\ekole` : moteur et documentation Ékole Core.
- `C:\mycode\Ekole\Kontexte` : missions, rôles, trames, liens pédagogiques et banque installée.
- `C:\mycode\Orgo\Orgo` et `C:\mycode\Orgo\Orgo_Worlds` : moteur de tâches, contrôle des Worlds, intégration/scenario injector.
- Deux SmartDump supplémentaires : `Akor`, `Kompose`, `Kolor`, `Konnaxion`, `Konnaxion_Worlds`, `Inkuisite`, `ekole-quebec`, `Karacter` et `interaction_kernel`.

Les SmartDump du 11 novembre ont été comparés aux copies fournies antérieurement. Les fichiers source communs sont identiques; les différences observées concernent leurs index `SMARTDUMP_INDEX.txt` régénérés.

## 2. Invariants confirmés

| Responsabilité | Source effectivement examinée | Conclusion |
| --- | --- | --- |
| Missions et rôles narratifs | Kontexte `data/missions/*.json`, `data/roles/*.json` | **38 rôles** et **17 missions** dans le snapshot; les six nouvelles sont présentes. |
| Contexte curriculaire | Kontexte `data/catalogue/202_kristals.json`; `src/kontexte/models.py` | **202 références internes** reconnues par le validateur; ne signifie pas accréditation scolaire. |
| Préparation et allocation | Kompose `docs/04-diagnostic-et-attribution.md`, `src/kompose/allocation_policy.py`, `tandem_handoff.py` | Préparation et contrat de prévisualisation présents; solveur d’affectation sous contraintes **décrit, non implémenté**. |
| Intention et liaison | Akor `src/akor/tandem_intent.py`, `tandem_authority_request.py` | Simulation/contrats de transport; pas admission scolaire autorisée. |
| World et release | Orgo_Worlds `apps/api/src/orgo/modules/worlds/worlds.service.ts`, `docs/Technical-Reference/Worlds/04_DATA_OWNERSHIP_MATRIX.md` | Orgo_Worlds est propriétaire de World, WorldRelease et WorldMembership; **pas** des Tasks/Case. |
| Tâches réelles | Orgo `apps/api/src/orgo/modules/work/work.service.ts`, `work.contract.ts` | Case/Task et assignations existent; `assignee_role` ne suffit pas à identifier ni autoriser un enfant. |
| Injection de scénarios | Orgo `tools/scenario-injector/`, Orgo_Worlds `docs/Technical-Reference/Worlds/WORLD_SCENARIO_INJECTION.md` | Il existe un injecteur officiel `orgo.scenario.v1`, utilisé dans des scénarios synthétiques avec `--apply` explicite; **ne pas** l’assimiler à une admission scolaire. |
| Personnages et visuels | Ékole `docs/PERSONNAGES_ALIGNMENT.md`, `personnages.py`, Kolor `data/roles.json` | Personnage-métier = perspective; visuel `role-<id>`; permission/identité informatique séparées. |
| Prévisualisation enseignante | Ékole `tandem/projection.py`, contrat `ekole-tandem-teacher-preview.schema.json` | Fonctionne en local et sur des fixtures synthétiques, **pas** avec de vraies tâches Orgo. |
| Konnaxion et Kidaxion | Konnaxion et Konnaxion_Worlds; recherche des sources `Kidaxion` | Infrastructure de communication et Worlds disponible. Aucune implémentation Kidaxion proprement dite identifiée. |
| Progrès de l’élève | Ékole `activite_locale.py`, Inkuisite et Kontexte `docs/ekole-orgo/04_REFERENTIEL_PREUVES_ET_RAPPORTS.md` | Exercices et modèle de preuves existent, mais aucun registre complet et authentifié de maîtrise individuelle ne se déduit des snapshots. |

## 3. Points de rupture démontrés

### A. Extension du catalogue Kontexte : verrou historique B5

Dans la copie exacte de Kontexte fournie le 11 novembre :

```text
python -m kontexte --repo <racine> validate
OK: 38 rôles, 17 missions, 202 références Ekole internes

PYTHONPATH=src python -m unittest discover -s tests -p 'test_*.py' -q
Ran 78 tests in 1.931s
FAILED (failures=1, errors=9)
```

- `src/kontexte/qc3_b5.py`, fonction `gather` : exige `len(missions)==11`.
- `tests/test_studio.py::test_full_catalogue` : attend `(38,11,60,60)` au lieu de `(38,17,60,60)`.
- **Contre-test contrôlé** : sur une copie de travail, après retrait temporaire des six fichiers ajoutés, les mêmes 78 tests passent (`OK`). Après le test, les six fichiers ont été rétablis.

**Correction recommandée** : conserver un **ensemble explicite des 11 identifiants historiques B5**, vérifier sa présence et son contenu, puis tester séparément le catalogue étendu. Ne pas supprimer les garde-fous B5, et ne pas remplacer sans analyse `11` par `17` dans toutes les statistiques, car ces statistiques sont liées à un audit historique figé.

### B. Objectifs pédagogiques des nouvelles missions

Dans les six fichiers `data/missions/{grand-menage-chez-mamie,mystere-de-la-bibliotheque,pique-nique-des-saisons,rallye-des-metiers,randonnee-a-velo,spectacle-des-histoires}.json`, les **52 étapes** ont `curriculum_ids: []`. Elles sont valides comme scénarios, mais ne peuvent alimenter une progression curriculaire par compétence sans un mapping validé. Définir les objectifs candidats à partir des références et overlays Ékole/Québec, puis obtenir la revue pédagogique voulue.

### C. Documentation Ékole absente de l'instantané reçu

Le snapshot `ekole_Code_snapshot.zip` contient seulement :

- `docs/FINAL_SYSTEM_EDUCATION_ALIGNMENT.md`
- `docs/Integration-Verification-2026-10-27.md`
- `docs/PERSONNAGES_ALIGNMENT.md`
- `docs/TANDEM_EKOLE_ORGO_PREVIEW_P1.md`

Les six pages du précédent overlay documentaire ne sont pas visibles. Elles ne doivent pas être considérées installées tant qu’une vérification locale ne l’a pas confirmé. Le présent overlay ajoute ces pages et cette validation, sans altérer les quatre pages historiques.

### D. Fixture Ékole à 4 Tasks et mission source à 11 Steps

`ekole/tandem/fixtures/fete-sorciere.synthetic.json` contient quatre tâches synthétiques. `Kontexte/data/missions/fete-sorciere.json` a onze étapes. La projection synthétique du professeur ne constitue pas encore une session World opérationnelle. Faire correspondre les références et versions sans réutiliser les UUID fictifs.

### E. Interfaces d'autorisation non opérationnelles

Les documents `Orgo/docs/Technical-Reference/TANDEM_EDUCATION_P5_SIGNED_WORLD_PREFLIGHT.md` et `Orgo_Worlds/docs/TANDEM_EDU_P6_P12_BRIDGE_CONTRACT.md` précisent que les ports, témoins signés et contrats ne constituent pas une route NestJS autorisée ni un registre réel des approbations enseignantes. Une transaction serveur, l’authentification mutuelle et les permissions/approbations persistées restent à connecter.

### F. Frontières entre Orgo_Worlds et Konnaxion_Worlds

Les deux infrastructures ne doivent pas partager implicitement des permissions ou des identifiants. La session autorisée, la portée du World, les messages et les indices doivent être reliés par un adaptateur explicite. Kidaxion reste une **interface enfant cible de Konnaxion**, et non une deuxième base d’autorisations.

## 4. Vérifications exécutées localement

| Commande / cible | Résultat | Précaution |
| --- | --- | --- |
| `python -m kontexte validate` | **OK**, 38 rôles, 17 missions, 202 références | Validation statique de fichiers. |
| 78 tests Kontexte avec 17 missions | **9 erreurs, 1 échec** | B5 et test Studio exigent 11. |
| 78 tests Kontexte avec les 11 missions historiques (copie seulement) | **78/78 OK** | Contrôle causal : les six missions supplémentaires ont ensuite été restaurées. |
| 26 tests Ékole ciblant Tandem/personnages/parcours/Kolor | **18 réussis, 8 ignorés** | Les tests ignorés réclament un corpus ou des dépendances absents de cette exécution isolée. |
| `node --test scripts/tests/tandem-education-*.test.mjs` sous Orgo_Worlds | **23/23 réussis** | Contrats/simulations hors ligne, pas le runtime. |
| Test supplémentaire de sécurité Worlds `.ts` sous Node 22 non configuré | **Non exécuté correctement** (`ERR_UNKNOWN_FILE_EXTENSION`) | Limitation de la commande de test brute, pas une vulnérabilité avérée. |

Les tests de bout en bout avec base Orgo, classe authentifiée, Konnaxion et données réelles **n'ont pas été lancés**.

## 5. Plan d'optimisation minimal

1. **Kontexte** : isoler l’inventaire des 11 missions B5 historiques de la banque étendue; mettre à jour les attentes du Studio; ajouter des tests contre la régression des deux ensembles.
2. **Kontexte ↔ Ékole** : relier les 52 étapes nouvelles à des objectifs candidats et critères de preuve, puis valider pédagogiquement sans inférer une maîtrise automatique.
3. **Orgo_Worlds ↔ Orgo** : qualifier une session scolaire de *La Fête de la sorcière* avec WorldRelease, accord enseignant, identité/permissions et idempotence; utiliser les surfaces officielles d’injection et d’attribution.
4. **Kompose/Akor** : relier les `role_code` aux assignations réelles Orgo, sans traiter un rôle narratif comme permission; conserver le contrôle enseignant et l’équité d’attribution.
5. **Konnaxion/Kidaxion** : prototyper les seules interactions autorisées (mission, demande d’aide, indice, fin de tâche), sous contexte et audience strictement limités.
6. **Ékole** : enregistrer les preuves attribuables à un enfant autorisé, avec revue humaine, puis calculer les besoins pédagogiques sans traiter un `Task done` comme maîtrise.

## 6. Critère de fin

Un enseignant peut sélectionner un scénario, préparer et approuver les rôles, lancer **une séance World isolée**, permettre aux enfants de coopérer dans Kidaxion, observer des transitions Orgo **authentifiées**, puis consulter dans Ékole les réalisations **et** les preuves pédagogiques revues. En l'absence de ces critères, le statut reste « intégration en cours ».
