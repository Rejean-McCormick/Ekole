# Validation inter-dépôts — Lot 4 (23 novembre 2026)

Ce document décrit **des vérifications locales**, pas une qualification de publication scolaire. Ne pas synchroniser des cours, illustrations, autorisations pédagogiques ou données élèves automatiquement.

## Dépôts frères attendus

Lancer les tests depuis `C:\mycode\Ekole\ekole` avec les dépôts voisins `ekole-quebec`, `Kontexte`, `ecole-pastorale`, `Inkuisite` et `Kamel`, selon les tests invoqués. Les scénarios Akor de bout en bout demandent aussi Orgo et Orgo_Worlds. L'absence d'un dépôt doit être interprétée comme **validation incomplète**, non comme une régression prouvée.

```powershell
cd C:\mycode\Ekole\ekole
python -m unittest discover -s tests -v
```

Vérifier en particulier `tests/test_personnages.py` : le catalogue `ekole.personnages/4` contient 3 040 ressources suivies et 304 illustrations libres. La réponse publique doit correspondre à `personnages.public_inventory` plutôt qu'au chiffre historique de 608. Aucun asset n'est ajouté ni supprimé par ce correctif.

## Décisions en suspens

La mission boulangerie de Kontexte contient `qc-pri-ma-006`, tandis que la correspondance `qc-pri-ma-008` a été proposée. **Aucune substitution n'est autorisée sans validation du responsable pédagogique.** Conserver les rapports d'Akor et les preuves de curriculum.
