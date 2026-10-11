# Ekole v11 — Refonte fondamentale et progressive des Kristals

**Ce ZIP est un overlay cumulatif sur la v10**, à décompresser à la racine Ekole (même niveau que `site/`, `tools/`, `kristals/`, `enseignant-app/`). Il ne supprime pas le Core, les 202 références, Konstellation ni les ponts existants. Il n'impose aucun style graphique et ne fournit aucune image générée.

## Pourquoi cette version est différente

- **5 Kristals** (fractions, division, récit, enquête scientifique, théâtre) reçoivent chacun une conception approfondie de l'expérience : objectifs source, 4 moments pédagogiques, limitations des outils, remédiations, prompts conceptuels et guide de revue.
- **195 autres Kristals complets** : dossier individuel de revue heuristique, sans revendiquer une refonte achevée. **2 références sans dossier source** restent signalées (`qc-pri-fr-004`, `qc-pri-ma-005`).
- **20 scénarios MiniLab** : 18 hérités + 2 nouveaux entraînements de pratique non notée (récit, science) ; 9 moteurs conservés.
- **70 fichiers sources originaux des 5 pilotes** conservés dans `ressources_pilotes_originaux/` pour restaurer les seuls fichiers absents sans écraser une personnalisation. Ce sont des références, jamais une nouvelle version publiée.
- **10 compléments de guides** pour les 5 Kristals peuvent être ajoutés aux textes de cours existants par une commande explicite avec sauvegarde et contrôle d'empreinte. Tous les contrats, préalables et banques d'évaluation restent inchangés.

## Installation et essai (Windows)

1. **Sauvegarder / faire un commit Git**, puis extraire le ZIP à la racine du dépôt Ekole, en acceptant le remplacement des fichiers de l'overlay. Ne pas supprimer tes dossiers.
2. Si les cinq Kristals sources ne sont pas présents, restaurer uniquement leurs fichiers manquants :

```powershell
py -3 tools\installer_sources_pilotes_v11.py --root .       # simulation
py -3 tools\installer_sources_pilotes_v11.py --root . --apply
```

3. Synchroniser la projection Élève, puis relancer `LANCER_EKOLE_3_APPS.bat` :

```powershell
py -3 tools\synchroniser_ekole_apps.py --root .
```

4. Tester une fiche : `http://127.0.0.1:8765/eleve/?cours=qc-pri-ma-012`, puis `.../?cours=qc-pri-fr-008` et `.../?cours=qc-pri-ad-001`. La vue Enseignant locale nécessite sa session.

### Modifier également les guides pédagogiques *originaux*

Les compléments sont déjà disponibles dans les Kristals, sans modifier silencieusement les guides actuels. Pour **les fusionner réellement dans les deux modules source** des cinq Kristals, d'abord vérifier :

```powershell
py -3 tools\appliquer_revisions_guides_v11.py --root .
```

Puis seulement après lecture du résultat :

```powershell
py -3 tools\appliquer_revisions_guides_v11.py --root . --apply
```

L'outil ajoute au bas des guides les annexes thématiques, sans remplacer le texte précédent. Il conserve les originaux dans `sauvegardes_ekole_v11/`, ignore les fichiers personnels dont le SHA est différent et est réexécutable sans doublon. Ne pas publier le dossier de sauvegarde.

### Images conceptuelles

Les prompts n'indiquent **aucun style**. Si une image n'est pas disponible à `kristals/<id>/experience/images/<slot>.webp` (ou PNG/JPEG), le texte complet s'affiche directement dans le cours. Après ajout d'un fichier :

```powershell
py -3 tools\compiler_visuels_kristals.py --root .
```

**Aucune image n'a été créée ni incluse par cette v11.** Un diagramme de fraction dont les parts sont évaluées reste l'affaire de MiniLab/SVG.

### Tests

```powershell
py -3 -m unittest discover -s tests -p "test_refonte_kristals_v11.py"
py -3 tools\valider_mini_labs.py
```

## Ce qui reste à faire

L'architecture est prête pour une refonte **par lots pédagogiquement validés**, mais pas les 195 autres cours. Les placements scolaires restent des propositions, pas un alignement officiel. Les 20 défis ne sont pas des preuves de maîtrise. L'usage réel avec des enfants, la correction des interfaces, la vérification des contenus et la revue du programme demeurent nécessaires avant diffusion.

Voir `docs/PROTOCOLE_DE_REFONTE_V11.md` et `docs/CARNET_DE_REFONTE_202_v11.json`.
