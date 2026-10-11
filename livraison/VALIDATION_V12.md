# Validation v12 — 9 octobre 2026

- 202 références distinctes; 200 cadres source-ancrés; deux dossiers pédagogiques complets absents (`qc-pri-fr-004`, `qc-pri-ma-005`).
- Sept scénarios v12 sur cinq Kristals pilotes, jamais certifiants. Vingt défis MiniLab v9 sur neuf moteurs conservés.
- Test JavaScript des représentations, répartitions (avec et sans reste), causalité, classifications et théâtre : réussi. Les tests comprennent des erreurs attendues.
- Huit tests Python v12 : compilation, traçabilité, sauvegarde et édition contrôlée, API Enseignant authentifiée, identifiants invalides : réussis.
- Suite Python héritée et v12 (hors test du pont Moodle) : **50 tests réussis**; **un module Moodle bloqué au chargement** par des `kristal.workspace.json` absents, préexistants; ne pas déclarer toute la suite verte.
- Export Élève : 26 fichiers publiés (dont 5 fichiers MicroMondes v12), sans source `evaluation/`, corrections ni dossier Enseignant; lien Konstellation localhost supprimé de l'export public.
- Réinstallation des 200 dossiers référentiels : 2 730 fichiers manquants restaurés sans remplacement; seconde exécution zéro nouveau fichier (vérification copie d'intégration).
- Intégrité des sources de navigation Core et du pont Moodle non modifiée par la v12 (cette livraison n'ajoute pas d'édition de ces fichiers historiques).
- Aucune image IA générée. Injection manuelle avec revue, texte alternatif et sha256. En absence d'image, prompt conceptuel affiché dans la vue Élève.
- Chromium système : lancement possible, mais navigation HTTP locale bloquée (`ERR_BLOCKED_BY_ADMINISTRATOR`). Pas de validation visuelle GUI revendiquée.

**État réel** : plate-forme candidate technique fonctionnelle pour prévisualisation locale, non prête pour homologation ni exploitation publique multiutilisateur. Les 195 plans non pilotes restent non revus.
