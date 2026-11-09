# Visite client d’Ekole

Une visite en 12 étapes dans les interfaces locales. L’enseignant ouvre le jardinage et le jazz, puis un élève explore les mathématiques, les sciences et la lecture dans ces univers. La visite s’arrête sur chaque écran avec un sous-titre. **Espace** ou le bouton **Suivant** déclenche l’action suivante. Fermer l’onglet termine la visite.

## Installation sur Windows

1. Décompresse le ZIP dans **`C:\mycode`** en fusionnant ses dossiers `Ekole`, `Konstellation` et `Spek_Semantic-publishing` avec les dossiers existants. `README-OVERLAY.md` donne les sept destinations.
2. Vérifie que `C:\mycode\Ekole\ekole\activite_locale.py` se trouve à côté de `launcher.py`. Le dossier `visite-client` est dans cette même racine du moteur.
3. Double-clique sur **`C:\mycode\Ekole\ekole\visite-client\LANCER_VISITE.cmd`**. Le lanceur installe Playwright et Chromium au besoin. Node.js 20 ou plus récent et Python sont requis.
4. Garde la fenêtre Chromium de la visite au premier plan et appuie sur **Espace** pour avancer.

Si tu préfères installer les dépendances à la main, ouvre un terminal dans `C:\mycode\Ekole\ekole\visite-client`.

```bat
npm.cmd install
npx.cmd playwright install chromium
npm.cmd run visite
```

Sous Linux et macOS, les commandes équivalentes sont `npm install`, `npx playwright install chromium` et `npm run visite`. La compilation du catalogue se fait depuis `ekole-quebec` avec `./lancer-ekole-cumulatif.sh --verifier`.

La visite démarre ses propres serveurs locaux et utilise une base temporaire. Les validations et réponses montrées sont des exemples de démonstration. Elle réutilise un catalogue compilé compatible. Si ce catalogue manque, la visite compile le sien dans un dossier temporaire. Les dépôts restent en lecture seule durant la visite. La visite et le compilateur détectent la disposition du ZIP. Si tu as déplacé des dépôts, utilise les variables de chemins listées dans `README-OVERLAY.md`. `EKOLE_PYTHON` peut désigner l’exécutable Python à utiliser.

## Ce que voit le collaborateur

- L’enseignant ouvre des thèmes, choisit la palette pastel et prépare un prompt d’illustration.
- L’élève choisit son compagnon, manipule des groupes de semences et distingue une observation d’une explication au jardin.
- L’élève change d’univers et retrouve le jazz dans une activité de lecture. Spek présente une fiche de cours dans cet univers avec la palette de classe.
- L’enseignant retrouve la banque de questions pour intervenir sur un exercice au besoin.

## Vérification automatique

`npm run verifier` exécute la même visite sans fenêtre et envoie réellement **Espace** à chaque étape.
