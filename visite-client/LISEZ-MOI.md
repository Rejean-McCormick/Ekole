# Visite client d’Ekole

Une visite en 17 étapes dans les interfaces locales. Le fil conducteur est la division en 3e année, avec les invitations de Mila. La visite s’arrête sur chaque écran avec un sous-titre. **Espace** ou le bouton **Suivant** déclenche l’action suivante. Fermer l’onglet termine la visite.

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

- Côté élève, le choix d’un parcours, une leçon en six étapes, la manipulation des invitations de Mila, le bilan et un micro-monde.
- Côté enseignant, la banque de scénarios Kontexte, le brouillon et son aperçu, la revue d’une leçon, la correction d’une réponse Inkuisite, les prompts d’illustration et le tableau de couverture.
- Du même contenu, une fiche anglaise rendue par Spek et une exploration des liens entre notions dans Konstellation-Light.

## La revue pédagogique dans Ekole

La revue d’une **leçon** vérifie la version que l’élève verra. On lit les six étapes et on se demande si l’objectif correspond au cours, si les exemples sont justes, si le vocabulaire convient à l’âge et si l’activité permet de voir ce que l’élève a compris. On vérifie aussi que les corrigés et les notes de l’enseignant restent privés. Dans l’atelier, une personne confirme la révision exacte du brouillon. **Diffuser** est une action distincte qui rend la version relue accessible dans l’espace Élève local.

La revue d’une **réponse Inkuisite** se fait après un essai. Elle sert à lire la justification donnée par l’élève, appliquer le critère et lui faire une rétroaction. La visite montre les deux opérations.

## Vérification automatique

`npm run verifier` exécute la même visite sans fenêtre et envoie réellement **Espace** à chaque étape.
