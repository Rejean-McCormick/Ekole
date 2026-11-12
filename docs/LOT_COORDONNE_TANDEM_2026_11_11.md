# Lot coordonné Ékole × Orgo × Kidaxion — 2026-11-11

Le portail enseignant affiche désormais tout aperçu local **synthétique, conforme au contrat fermé Ékole P1** de 1 à 50 tâches. La limitation de présentation à `fete-sorciere` et 11 tâches a été retirée. L'API `/api/tandem/preview.json` reste réservée à l'éditeur autorisé et un JSON de prévisualisation ne donne **aucun droit opérationnel**.

Le vérificateur `tools/verifier_ecosysteme_tandem.py` rapproche Kontexte, Kompose, Akor, Kolor, Orgo et Orgo_Worlds en mode **lecture seule et fixtures de démonstration**; exécuter avec Python 3 et Node.js. Résultat observé sur les snapshots : 17 missions (92 étapes), 38 rôles cohérents avec Kolor, 17 fixtures de revue Orgo valides et 7 intentions synthétiques conformes à Orgo_Worlds. Les 10 autres missions historiques ne satisfont pas encore les gardes structurées de prévisualisation. Les 52 nouvelles étapes n'ont toujours pas de `curriculum_ids`.

Ce lot ne crée ni World, ni séance, ni compte d'élève, ni interface Kidaxion. Pour la production : authentification élève/enseignant, permissions et releases réelles, approbation enseignante persistée, libération d'indices et EvidenceLog scolaire avec revue humaine restent à implémenter et à qualifier.

```powershell
cd C:\mycode\Ekole\ekole
python tools\verifier_ecosysteme_tandem.py
node --test tests\test_tandem_teacher_ui.cjs
```
