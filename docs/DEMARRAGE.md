# Démarrer Ékole

Ékole Core fournit le portail, la vue élève et l’éditeur local. Choisissez le pack selon le cours visé. Pour une vue des outils qui interviennent avant ou après le moteur, ouvrez [L’écosystème Ékole](ECOSYSTEME.md).

## Choisir le pack

Placez le moteur `ekole` et le pack dans des dossiers frères. Les lanceurs attendent `ekole-quebec` pour [Ékole Québec](https://github.com/Rejean-McCormick/Ekole-Quebec/blob/main/README.md) et `ecole-pastorale` pour [Ékole Pastorale](https://github.com/Rejean-McCormick/Ekole-Pastorale/blob/main/README.md). Le moteur se lance avec Python 3.10 ou plus récent.

| Pack | Portail | Vue élève | Éditeur |
| --- | --- | --- | --- |
| Québec | `http://127.0.0.1:8765/` | `/eleve/` | Port 8766 |
| Pastorale | `http://127.0.0.1:8775/` | `/eleve/` | Port 8776 |

Utilisez le lanceur du pack pour obtenir ses ports et options par défaut. Le lien privé de l’éditeur est affiché dans le terminal. L’éditeur s’ouvre en lecture seule par défaut. Activez `--edition` seulement pour le travail d’édition local voulu.

## Vérifier ou lancer le moteur directement

Depuis le dépôt du moteur, vérifiez les manifestes sans lancer de serveur :

```sh
python launcher.py --contenu ../ekole-quebec --verifier
python launcher.py --contenu ../ecole-pastorale --verifier
```

Pour ouvrir uniquement le portail Québec :

```sh
python launcher.py --contenu ../ekole-quebec --sans-editeur
```

Si les deux packs sont présents, indiquez un chemin explicite. `--contenu auto` refuse de choisir entre eux. `--contenu none` démarre le moteur seul. Le moteur utilise 8765 et 8766 par défaut quand on le lance directement. Pour reproduire les ports Pastorale sans son lanceur, ajoutez `--port 8775 --port-editeur 8776`.

## Retrouver une fonction

- Pour visiter un exemple élève et enseignant, suivez [la visite de la division](../visite-client/LISEZ-MOI.md).
- Pour utiliser les brouillons, les activités locales ou les visuels, suivez [le guide auteur et publication](AUTEUR_ET_PUBLICATION.md).
- Pour préparer des situations, ouvrez [la banque PRF-22](../banques/prf22/README.md) sur le port enseignant.
- Pour reproduire une mission fictive, suivez [l’aperçu Tandem P1](TANDEM_EKOLE_ORGO_PREVIEW_P1.md) ou [le lot multicanal](architecture-collaborative/11_LOT_CODE_MULTICANAL_2026_11_11.md). Le premier ouvre un aperçu enseignant. Le second prépare un plan et des cartes pour revue.

Si le port enseignant 8766 est occupé, vérifiez notamment si l’[OpsConsole historique](../legacy/opsconsole/README.md) tourne déjà. Arrêtez le service concerné ou choisissez un autre port avec `--port-editeur`. Le service Core écoute sur la boucle locale. Une classe hébergée exige une infrastructure et des droits distincts, décrits dans la [recette collaborative](architecture-collaborative/09_FEUILLE_DE_ROUTE_ET_RECETTE.md).
