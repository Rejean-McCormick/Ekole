# Ékole : consolidation PRF-22 dans le dépôt

## Pourquoi dans Ékole

La banque PRF-22 est un artefact de **conception pédagogique**, pas un nouveau produit ni une nouvelle source d'exercices. Le code est versionné sous `outils/compositeur_prf22_v0_3/`, avec le compositeur existant. Le dossier `banques/prf22/candidats-v0_4/` conserve les 137 propositions préconstruites afin qu'elles soient inspectables et diffusables dans le même dépôt.

Les scripts à la racine sont des lanceurs de l'application Ékole :

| Lanceur | Fonction |
| --- | --- |
| `LANCER_COMPOSITEUR_PRF22.cmd` | Atelier existant, conservé |
| `LANCER_BANQUE_PRF22.cmd` | Explorer les 137 propositions versionnées |
| `GENERER_BANQUE_PRF22.cmd` | Créer une nouvelle génération sous `banques/prf22/generations/` (ignorée par Git) |
| `VERIFIER_BANQUE_PRF22.cmd` | Vérifier documents, empreintes, plans et tests |

**Aucune extraction dans un dossier de travail quelconque.** Installer depuis le ZIP avec le script autonome. Toutes les écritures du code et des données versionnables ciblent `C:\mycode\Ekole\ekole`. Les générations restent à l'intérieur du même dépôt, sans remplacer la banque courante. Ne pas promouvoir une banque issue de sources Kontexte modifiées sans revue de ses correspondances.

## Frontières et versions

- Format du document : `situation-orchestrable.design.v0.3.schema.json` (inchangé).
- Version de la banque : v0.4; paquet de consolidation : v0.5.
- Le profil `PRF-22` dans Arketype reste géré par son installateur antérieur. Ce pack ne modifie pas le Framework ni les 19 archétypes.
- Kontexte conserve les trames, exercices, objectifs et personnages de référence. Ékole stocke seulement les références et compositions candidates.
- Kompose/Orgo/Konnaxion n'obtiennent aucune autorisation, aucun projet, aucune donnée élève et aucune séance lors de l'installation ou de la génération.
- Une réussite aux tests structurels **ne qualifie pas** le contenu pédagogique.

## Git

`git status --short` dans Ékole révèle les fichiers ajoutés ou mis à jour. Après examen, `git add outils/compositeur_prf22_v0_3 banques/prf22 docs/PRF22_BANQUE_REPO.md LANCER_BANQUE_PRF22.cmd GENERER_BANQUE_PRF22.cmd VERIFIER_BANQUE_PRF22.cmd` puis commiter sur une branche dédiée.

`banques/prf22/generations/.gitignore` exclut les régénérations locales; la banque `candidats-v0_4/` peut être suivie par Git. Aucun commit, push ou création de branche n'est effectué par l'installateur.

## Qualité et sécurité

Toutes les propositions restent `candidates_non_qualifies`. La banque source s'appuie sur 26 activités et 25 objectifs distincts seulement; 53 propositions demandent une revue prioritaire. La cohérence structurelle n'est pas une preuve d'efficacité. Les contextes, représentations culturelles, tâches et critères doivent être contrôlés avant toute mise en œuvre.

L'installateur refuse d'écraser un fichier préexistant divergent. Seul le `Atelier_PRF22.pyw` identique à la v0.3 originale est mis à jour pour accepter l'ouverture directe des brouillons (un hash exact est exigé). Sauvegardes et retour arrière disponibles.


## Intégration v0.6 (novembre 2026)

- Nouvelle page enseignant : `/prf22/index.html` dans l'application Ékole existante, aucun deuxième serveur.
- Nouvelle bibliothèque versionnée : `banques/prf22/activites-proposees-v0_6.json` (propositions, non Kontexte).
- Lot enrichi `banques/prf22/candidats-v0_6/` sous empreintes SHA-256.
- Révisions isolées dans `banques/prf22/revisions-local/` avec statut `design_only`.
- `--edition` et session enseignant + CSRF + origine locale requis pour l'enregistrement.
- `GENERER_BANQUE_ENRICHIE_PRF22.cmd` crée un lot neuf sans modifier les lots versionnés.
- Aucune interface enfant, aucun World, aucune publication ni admission créée.
