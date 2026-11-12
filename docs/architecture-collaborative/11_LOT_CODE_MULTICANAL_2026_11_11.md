# Lot de code multicanal — 11 novembre 2026

Statut : **implémentation partielle testable**, pas déploiement scolaire.

Cette page prolonge l'architecture documentée dans les chapitres 00–10, en
conservant les autorités par domaine et en explicitant les limites prouvées.

## Composants réellement codés dans ce lot

| Propriétaire | Implémentation | Statut |
|---|---|---|
| Kontexte | Projection `kidaxion.print-cards/1` depuis les missions synthétiques sécurisées, sans fragments privés | Exécutable localement |
| Kompose | Suggestions déterministes et pseudonymisées de personnages-métiers, sans attribution réelle | Exécutable localement |
| Kamel | HTML de cartes en noir et blanc / couleur, QR informatif HTTPS facultatif | Exécutable localement |
| Orgo_Worlds | Six packs de revue supplémentaires; générateur basé sur l'adaptateur Kontexte et validé par l'injecteur Orgo | Synthétique seulement |
| Konnaxion | Visibilité restreinte des projets explicitement étiquetés `ekole.school`, de leurs ressources, messages, membres et tâches; garde-fous contre les tâches doublons | À qualifier dans Django réel |
| Konnaxion Web | Route `/kidaxion` : affiche les projets scolaires autorisés par le serveur, propose quatre messages normalisés | Préversion, ne montre pas encore les tâches Orgo |
| Kor | Projection pure d'une surface déjà autorisée en format jeunesse | Sans intégration Android active |
| Ékole | CLI d'assemblage, journal local SQLite de preuves, revue enseignante et portfolio candidat non publié | Démonstration locale, pas de registre scolaire homologué |

## Démonstration pédagogique locale

Depuis `C:\mycode\Ekole\ekole`, avec les autres dépôts installés :

```powershell
py tools\preparer_mission_collaborative.py --mission fete-sorciere `
  --kontexte C:\mycode\Ekole\Kontexte `
  --kompose C:\mycode\Ekole\Kompose `
  --kamel C:\mycode\Kamel\Kamel `
  --out C:\mycode\Ekole\Tandem_Local\preparation-fete
```

Produits : `plan-enseignant.json`, `cartes.json` et
`cartes-impression.html`. Les propositions de rôles ne sont créées que
lorsqu'un fichier de profils **pseudonymisés** est fourni à `--participants`.
Les fichiers de préparation n'ouvrent aucune séance ni autorisation d'élève.

La nouvelle page `Konnaxion/frontend/app/kidaxion/page.tsx` utilise les API
Konnaxion et leurs contrôles de projet ; elle ne communique pas avec un
éventuel dossier local SQLite d'Ékole ni avec un World Orgo actif.

## Séparation des responsabilités

- **Orgo** est l'autorité sur la réalisation opérationnelle des tâches.
- **Orgo_Worlds** est l'autorité sur ses Worlds et ses portées.
- **Konnaxion** conserve projets, équipes, messages, ressources et objets
  collaboratifs. Ses `ProjectTask` historiques ne doivent pas devenir une
  seconde exécution pour une aventure Ékole pilotée par Orgo.
- **Ékole** interprète les apprentissages ; une preuve enregistrée n'est pas
  automatiquement une compétence maîtrisée.
- **Kontexte** conserve les missions et personnages de référence.
- **Kompose** prépare, l'enseignant autorise. **Kor, Web, Kamel** projettent
  le même contexte sans créer de nouveaux droits.
- **Kamel** : un QR n'est jamais une clé de permission, ni un accusé de réussite.

## Blocages impératifs avant utilisation avec des élèves

1. Relier l'identité scolaire et les Worlds Orgo/Konnaxion à des sessions
   autorisées, avec contrôles serveur par classe, établissement et projet.
2. Qualifier les garde-fous Konnaxion dans son environnement Django avec
   base réelle, vérifier accès médias et routes de données complémentaires ;
   les contrôles de ce lot ne constituent pas un audit complet des données.
3. Faire passer l'injecteur Orgo de la **revue synthétique** à l'admission
   runtime via les contrôles existants ; ne pas activer les packs manuellement.
4. Lier les réceptions d'événements signés Orgo/Inkuisite/Konnaxion à une
   preuve Ékole authentifiée ; valider les objectifs et les décisions par
   un enseignant habilité.
5. Ajouter le vrai parcours des tâches Kidaxion (Web et Kor), le routage
   de QR authentifié, les notifications et le portfolio publié après revue.
6. Qualifier la confidentialité des enfants, la modération, les délais de
   conservation et les sauvegardes, selon les politiques de l'école.

## Tests de source

- `Kontexte` : `PYTHONPATH=src pytest -q`
- `Kompose` : `PYTHONPATH=src pytest -q tests`
- `Ékole` : `python -m unittest discover -s tests -p test_portfolio_ledger.py`,
  puis `-p test_preparer_mission_collaborative.py`
- `Kor` : `PYTHONPATH=src pytest -q tests/test_kidaxion_profile.py`
- `Kamel` : `python -m unittest tools/ekole/test_print_mission_cards.py`
- `Orgo_Worlds` : `python -m unittest tools/ekole/test_generate_review_worlds.py`
- `Konnaxion` : tests Django `backend/konnaxion/keenkonnect/test_school_access.py`
  dans l'environnement Python du dépôt, puis tests TypeScript/Next.js.

**Attention** : les scripts de test Python/Node qui fonctionnent sans la stack
Django ne prouvent ni la confidentialité réelle de la classe ni l'admission
Orgo. Les 55 liens curriculaires candidats demeurent non approuvés.
