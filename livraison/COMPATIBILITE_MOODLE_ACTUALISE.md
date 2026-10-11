# Compatibilité vérifiée avec le `moodle.zip` fourni (9 octobre 2026)

## Audit de l'archive source

- `moodle.zip` comporte 389 entrées ZIP (353 fichiers non-répertoire).
- 202 fiches publiques de cours sous `site/data/cours/`, 202 entrées `site/data/index.json`, 14 disciplines et 20 pages institutionnelles.
- `site/index.html` a encore le champ `id="wave"` et ne contient ni le filtre d'étape ni les nouvelles vues par cycles; `site/app.js` affiche le Markdown sous `<pre>`.
- `opsconsole/`, `moodle/`, `tools/kristal_moodle_bridge.py` et le plan Moodle **polymorphe** existent : ils sont préservés exactement.
- `moodle.zip` n'inclut **aucun dossier `kristals/` complet**, malgré les références documentaires aux 202 workspaces. Les fiches publiques et le registre ne les remplacent pas.

## Politique de remplacement

Les **seuls fichiers existants remplacés** sont `site/index.html`, `site/app.js`, `site/style.css` et `site/assets/ekole-logo.svg`. Le logo précédent est conservé (contenu SVG identique). Tout le reste de l'overlay est **nouveau**. `site/data/niveaux-manuel.json`, lorsqu'il existe, n'est pas inclus et n'est jamais écrasé.

Le pont Moodle polymorphe n'impose **pas** une correspondance Kristal ↔ cours Moodle; les parcours scolaires sont de nouvelles projections côté Ekole seulement. La console d'opérations existante ne reçoit pas de nouvelle commande risquée et reste indépendante.

## Tests du dépôt actualisé

Les tests métiers de parcours et la fusion des fichiers ont réussi sur une copie extraite de `moodle.zip` avec l'overlay appliqué. `tools/ekole.py build` fonctionne avec le catalogue public.

**Limite vérifiée :** la suite complète de tests de l'archive fournie échoue sur `test_kristal_moodle_bridge` et une épreuve `opsconsole.test_detail` faute du répertoire `kristals/`. L'overlay ne répare pas artificiellement ces sources manquantes. En replaçant les workspaces auteurs exacts dans le dépôt, relancer `py -3 tools\ekole.py verify`, la suite d'épreuves du pont Moodle et celle de l'OpsConsole.

Aucune connexion à une instance Moodle n'a été établie, aucun navigateur graphique complet n'a été validé, aucune publication v10 n'a été lancée.

**Migration :** aucune affectation existante n’est remplacée. Un fichier d’exemple contient 24 clés; le script `tools/migrer_4_etapes.py` simule puis complète les seules six étapes 4 manquantes sous `--apply`, avec sauvegarde automatique. Le navigateur affiche les étapes 4 vides tant que le vrai fichier n’est pas migré.

## Extension v4 conforme au modèle scolaire

Cette extension conserve l'archive source et le pont Moodle. Le nouveau `A-Kristal-ScolQc` décrit distinctement les règles du bulletin (`knowledge-base/sources/assessment_semantics.json`) et les attentes de progression. Le bulletin unique québécois compte officiellement **trois étapes**; les **quatre étapes pédagogiques Ekole** sont une décision interne de découpage des parcours, sans correspondance automatique aux bulletins. La durée de chacune n’est pas fixée à quatre mois.
