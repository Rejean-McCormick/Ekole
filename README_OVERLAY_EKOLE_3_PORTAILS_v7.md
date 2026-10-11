# Ekole v7 : Core + Élève + Enseignant + intentions d'images

**Overlay** à extraire à la racine du repo qui contient déjà `site/`, `tools/`, `catalogue/`, `moodle/` et `opsconsole/`. Compatible avec la base actualisée et l'overlay des affectations v5/v6; inclut les fichiers racine Core requis pour rétablir la navigation adulte.

## Trois entrées

| Application | URL de travail | État |
|---|---|---|
| **Ekole Core** — navigation, organisation, catalogue et pages d'administration de démonstration | `http://127.0.0.1:8765/` | Restaurée au root avec menus ajoutés |
| **Ekole Élève** — découverte par année, activités, cartes locales et emplacements d'images | `http://127.0.0.1:8765/eleve/` | Nouvelle app enfant autonome |
| **Ekole Enseignant** — modules complets, corrections et prompts IA | `http://127.0.0.1:8766/` après démarrage dédié | Application distincte hors de `site/`, serveur local à session temporaire |

Double-cliquer `LANCER_EKOLE_3_APPS.bat` ou exécuter :

```powershell
cd "C:\mycode\Ekole"
py -3 tools\synchroniser_ekole_apps.py --root .
py -3 tools\ekole.py preview
# Autre PowerShell :
py -3 tools\serve_enseignant.py --open
```

Si le repo est plutôt `C:\mycode\Ekole\Ekole_Pack_v10_GitHub_Moodle_202`, lancer depuis cette racine réelle.

## Images IA : prompts prêts, images non générées

`visuels/INTENTIONS_IMAGES.json` porte 227 intentions : 202 vignettes par cours, 14 symboles de domaines, 6 années, 2 ateliers mathématiques, 1 accueil, 1 carte des notions et 1 visuel enseignant. Les métadonnées incluent `visual_id`, `placement`, `kind`, `source_ref`, `prompt_image`, `negative_constraints`, `aspect_ratio`, `palette`, `alt_fr_CA`, destination future, statut et validations. Ces prompts sont des **ébauches originales à réviser**, pas des garanties de précision des images.

La vue élève reçoit **seulement des descriptions d'emplacements**, sous `site/eleve/data/visuels_public.json`. Les prompts complets sont visibles dans la vue Enseignant (« Atelier d'images IA »). Pas de média fabriqué ni d'image publiée par ce patch. Les diagrammes mathématiques exigent une preuve déterministe : privilégier le dessin par SVG pour quantités exactes et fractions.

## Konstellation Light

Le lien **local indépendant** pointe vers `http://127.0.0.1:4177/`, conformément au README fourni de Konstellation Light. Ouvre sa démo s'il est lancé; ce n'est pas un lien vérifié vers la collection des 202 cours. La navigation locale « Avant / Après » demeure un schéma Ekole du graphe de préalables. Voir `docs/EKOLE_PORTAILS_ET_VISUELS_v7.md`.

## Export de la seule vue enfant (sans banque ni corrections)

```powershell
py -3 tools\export_ekole_eleve_v7.py --root . --out "C:\temp\ekole-eleve-public"
```

L'ancien export `tools/export_vue_enfant.py` de v6 doit être considéré **obsolète** et ne pas être utilisé avec v7 : il visait l'ancienne application Élève à la racine. Le nouvel export ne publie que neuf fichiers autorisés et laisse `site/data/cours/`, `enseignant-app/`, `visuels/INTENTIONS_IMAGES.json` et la configuration d'administration hors du paquet élève.

**ATTENTION** : la racine `site/` contient encore des cours avec corrections en JSON et le clone ancien `site/pour-les-grands/` si v6 a déjà été appliqué. Ne jamais exposer **la racine entière `site/`** sur Internet. Le port enseignant 8766 n'accepte que les connexions depuis la machine locale; sa session temporaire n'est pas une authentification scolaire multi-utilisateur.

Le patch ne modifie pas Moodle, l'OpsConsole, le Framework, les Kristals sources ni leurs identifiants. Les attributions de niveaux restent des propositions et quatre étapes pédagogiques Ekole restent distinctes des trois bulletins officiels.
