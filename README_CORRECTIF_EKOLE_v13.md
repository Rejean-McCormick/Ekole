# Ekole — Correctif v13 : activités vérifiables et adéquation au niveau

Cet overlay est un **correctif ciblé**, pas une révision pédagogique complète des 202 Kristals. À extraire à la racine d'une installation **Ekole v12** avec l'**encyclopédie autonome v4** (ou avant elle; ces deux dossiers seront alors ajoutés sans que le corpus soit dupliqué).

## Défauts corrigés

1. Les pages Élève n'affichent plus de `<textarea>` en réponse à un exercice générique. Elles affichent uniquement les mini-environnements **explicitement associés à ce Kristal** et compatibles avec **l'année proposée**. Sans correspondance, Ekole indique qu'aucun entraînement à validation fiable n'est prêt.
2. Les activités de dénombrement élémentaire ne sont plus proposées sur les fiches de **3e année**. Le dénombrement demeure pertinent en 1re année. La bibliothèque garde ses neuf moteurs, désormais annotés avec une liste d'années **indicatives**. Le MiniLab filtre les défis en présence de `?annee=3`, et bloque un lien direct incompatible avec ce niveau.
3. Pour la 3e année, `qc-pri-ma-012` et `qc-pri-ma-009` continuent à utiliser les micro-mondes v12 (plus complets). Deux nouveaux entraînements pour `qc-pri-ma-008` et deux défis d’arrondissement pour `qc-pri-ma-005` travaillent les groupements liés à la multiplication. **Les autres cours qui n'ont pas encore d'outil pertinent ne reçoivent pas de jeu générique inventé.**
4. Le Kristal autonome des sociétés autochtones reste indépendant. L'encyclopédie Élève propose 3 mini-laboratoires fermés (associer, classer) dont les références renvoient à des fiches existantes. L'absence d'information n'est pas assimilée à une fausseté : les catégories distinguent « documenté dans ces contextes » et « non établi comme règle générale ».
5. Aucun fichier de connaissance du Kristal ni contenu enseignant n'est modifié. Les associations ajoutées restent `illustration_candidate_non_validee` et ne sont jamais des preuves de maîtrise.

## Accès

- `http://127.0.0.1:8765/eleve/?cours=qc-pri-ma-008` : multiplication, groupements manipulables (3e année proposée)
- `http://127.0.0.1:8765/eleve/?cours=qc-pri-ma-012` : fractions multi-représentations v12
- `http://127.0.0.1:8765/eleve/labo/?annee=3` : outils proposés pour 3e année; pas de dénombrement débutant
- `http://127.0.0.1:8765/eleve/encyclopedie-autochtones/` : fiches et activités structurées sur les sociétés

## Critères de qualité non remplis

Les 202 Kristals ne possèdent pas tous des expériences validées. L'attribution des cours aux années demeure une projection à approuver. Les exercices historiques ajoutés sont des **candidats de révision**, et une revue culturelle et une validation auprès de pédagogues et des nations concernées restent indispensables. Aucun navigateur réel ou test avec des enfants n'est revendiqué par la validation de ce correctif.

## Validation

```powershell
py -3 tests\test_ekole_v13_niveaux.py
node tests\test_ekole_v13_niveaux.mjs
```

Après extraction, relancer le serveur Ekole et recharger la page avec `Ctrl+F5`. Aucun `build` n'est nécessaire pour ces fichiers statiques **déjà compilés**; en revanche, une synchronisation future de toute l'application peut régénérer certaines vues et doit être suivie d'une nouvelle vérification v13.
