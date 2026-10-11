# Ekole OpsConsole 0.1

Console de pilotage **locale**, propre au dépôt Ekole. Prototype stdlib Python 3, sans dépendances Python externes.

## Démarrage

Depuis la racine du repo :

```powershell
.\scripts\START_EKOLE_OPSCONSOLE.bat
# ou
py -3 opsconsole\ekole_ops.py
```

L'interface s'ouvre sur `http://127.0.0.1:8766/`. Le portail est distinct sur `http://127.0.0.1:8765/`.

## Capacité et frontières

| Fonction | Mode |
|---|---|
| Santé du catalogue 202, état du site, nombre d'items | Inspection locale |
| Inspecteur par Kristal : contrat, fichiers, banque, liens | Lecture seule |
| `verify`, `build`, `moodle-plan`, `pages-zip` | CLI Ekole local préexistant |
| Démarrage/arrêt de la prévisualisation | Serveur local temporaire, lié à la console |
| Déploiement vers un répertoire statique local | Simulation obligatoire, confirmation exacte, sauvegardes par `tools/ekole.py` |
| Git local | Statut en lecture seule |
| Moodle, SemantiK, Konstellation, Médiathèque, GitHub / v10 | Information uniquement : aucun port d'écriture/call branché |

Le moteur exécute uniquement une **liste fixe** de commandes. Pas de terminal, pas d'exécution de scripts configurables, pas d'écriture Moodle/Git/GitHub/SSH, pas de suppression, pas d'élévation.

## Sécurité

- Écoute uniquement sur `127.0.0.1`, port 8766.
- Jeton CSRF éphémère par lancement et vérification Origin sur les requêtes de modification.
- CSP et réponses `no-store` ; aucun script externe chargé.
- Copie locale refusée vers Ekole, vers une racine de disque et vers un dépôt Git.
- Simulation autorisée avant application et délai maximal de 10 minutes ; empreinte du site inchangée exigée.
- L'export public interdit `.env`, secrets, fichiers `authoring/` et `evaluation/`.
- Les banques d'évaluation ne sont pas envoyées au navigateur : seuls les totaux et métadonnées d'inspection sont exposés.
- Les journaux stockent le nom et le résultat de l'action, pas les secrets ni la commande arbitraire.

## Contrôles

```powershell
py -3 opsconsole\ekole_ops.py --check
py -3 -m unittest discover -s opsconsole\tests -v
```

La commande `--check` est un prévol léger. Le bouton « Vérifier les 202 Kristals » exécute le validateur du dépôt, plus approfondi.

## Limites

- Prototype local testé principalement sous Python 3 dans un environnement Linux, à essayer sur Windows.
- Les 202 workspaces conservent leur statut éditorial : leur présence ne les qualifie pas comme états Kristal v9/v10 publiés.
- Pas de publication ou de restauration distante. Intégrations à développer sur contrats et approbations séparés.
