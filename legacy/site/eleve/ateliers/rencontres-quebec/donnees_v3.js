window.EKOLE_HISTOIRE_V3 = {
  "format": "ekole.atelier-histoire-v3/3.0",
  "titre": "Rencontres et échanges entre populations",
  "objectif": "Comparer des situations de rencontre et d’échange entre populations.",
  "preuve": "Analyser une situation à partir de deux points de vue documentés.",
  "statut": "exploration_non_homologuee",
  "architecture": "Les assertions sont lues dans deux Kristals autonomes; le cours ne détient que sa sélection.",
  "dependances": [
    {
      "kristal": "societes-autochtones-quebec",
      "digest": "sha256:9e6a58efd15113c64d82b724c0e2e4a89a1aec2cca00bbf0e66f6544cc39865d"
    },
    {
      "kristal": "rencontres-coloniales-quebec",
      "digest": "sha256:cc6b2831d63e5922942dba101026eb3822ff4bc1fa5dfd36215f46e8d5ce46cb"
    }
  ],
  "categories": {
    "comprendre_les_societes": [
      "fait:peuples-avant",
      "fait:wendat-maisons",
      "fait:wendat-meres-clan",
      "fait:innus-saisons",
      "fait:v3-innu-outils",
      "fait:v3-wendat-gouvernance"
    ],
    "echanges_et_rencontres": [
      "fait:commerce-fourrures",
      "fait:commerce-participation",
      "fait:alliance-1603",
      "fait:v3-paix-rencontre"
    ],
    "diplomatie": [
      "fait:paix-date",
      "fait:kondiaronk",
      "fait:calliere",
      "fait:v3-paix-kondiaronk",
      "fait:v3-paix-texte"
    ],
    "transformations": [
      "fait:pouvoir-apres1760",
      "fait:wendat-1825",
      "fait:vie-aujourdhui",
      "fait:wendat-langue-vivante"
    ],
    "sources_et_points_de_vue": [
      "fait:traitement-sources",
      "fait:v3-paix-38-39",
      "fait:v3-innu-aine"
    ]
  },
  "faits": [
    {
      "id": "fait:peuples-avant",
      "enonce_fr": "Les peuples autochtones habitent le territoire de l’actuel Québec bien avant l’établissement colonial français de 1608.",
      "periode": "Avant l’implantation coloniale française dans la vallée du Saint-Laurent",
      "kristal": "societes-autochtones-quebec",
      "source_ids": [
        "src:quebec-nations",
        "src:pc-champlain"
      ],
      "limites": "Description générale; ne pas projeter les onze structures administratives actuelles sur 1500."
    },
    {
      "id": "fait:wendat-maisons",
      "enonce_fr": "Selon le Conseil de la Nation Wendat, des villages historiques wendat regroupaient plusieurs familles et clans dans des maisons longues.",
      "periode": "Organisations historiques — datation à préciser",
      "kristal": "societes-autochtones-quebec",
      "source_ids": [
        "src:wendat-histoire"
      ],
      "limites": "L’organisation et la taille des communautés ont changé dans le temps; ne pas généraliser à toutes les nations."
    },
    {
      "id": "fait:wendat-meres-clan",
      "enonce_fr": "Le Conseil de la Nation Wendat décrit une transmission traditionnelle de l’appartenance familiale par la lignée maternelle, avec des mères de clan jouant un rôle central.",
      "periode": "Organisations historiques — datation à préciser",
      "kristal": "societes-autochtones-quebec",
      "source_ids": [
        "src:wendat-histoire"
      ],
      "limites": "Ces rôles sont documentés pour la Nation Wendat; pas un système universel autochtone."
    },
    {
      "id": "fait:innus-saisons",
      "enonce_fr": "La ressource Nametau innu décrit, dans des contextes traditionnels, des déplacements de familles innues suivant les saisons et les ressources du Nitassinan.",
      "periode": "Organisations historiques — datation à préciser",
      "kristal": "societes-autochtones-quebec",
      "source_ids": [
        "src:nametau-territoire"
      ],
      "limites": "Il ne faut pas qualifier une nation entière de nomade éternellement; pratiques et modes de vie évoluent."
    },
    {
      "id": "fait:v3-innu-outils",
      "enonce_fr": "Nametau innu décrit la fabrication de canots à partir de bois de bouleau, d’écorce et de racines.",
      "periode": "Organisations historiques — datation à préciser",
      "kristal": "societes-autochtones-quebec",
      "source_ids": [
        "src:v3-nametau-materiel"
      ],
      "limites": "La source documente un procédé traditionnel, pas une obligation pour chaque personne."
    },
    {
      "id": "fait:v3-wendat-gouvernance",
      "enonce_fr": "La Nation Wendat décrit aujourd’hui un conseil d’élus composé d’un Grand Chef et de Chefs familiaux.",
      "periode": "Aujourd’hui",
      "kristal": "societes-autochtones-quebec",
      "source_ids": [
        "src:v3-wendat-histoire"
      ],
      "limites": "Cette organisation contemporaine ne décrit pas identiquement les conseils du XVIIe siècle."
    },
    {
      "id": "fait:commerce-fourrures",
      "enonce_fr": "Au début du XVIIe siècle, des commerçants français ont échangé des biens manufacturés avec des partenaires autochtones contre des fourrures.",
      "periode": "Début du XVIIe siècle — échanges et établissements",
      "kristal": "rencontres-coloniales-quebec",
      "source_ids": [
        "src:dnd-rencontres",
        "src:pc-champlain"
      ],
      "limites": "Les échanges ne décrivent ni tous les peuples ni des conditions immuables."
    },
    {
      "id": "fait:commerce-participation",
      "enonce_fr": "Des partenaires autochtones ont joué des rôles essentiels de fournisseurs et d’intermédiaires du commerce des fourrures en Nouvelle-France.",
      "periode": "Début du XVIIe siècle — échanges et établissements",
      "kristal": "rencontres-coloniales-quebec",
      "source_ids": [
        "src:pc-champlain"
      ],
      "limites": "Ne jamais cantonner tous les Autochtones à un rôle économique unique."
    },
    {
      "id": "fait:alliance-1603",
      "enonce_fr": "En 1603, à Tadoussac, des représentants français concluent des alliances avec des partenaires autochtones nommés dans les sources historiques.",
      "periode": "Début du XVIIe siècle — échanges et établissements",
      "kristal": "rencontres-coloniales-quebec",
      "source_ids": [
        "src:dnd-rencontres"
      ],
      "limites": "Les ethnonymes archivistiques exigent contextualisation et recoupement nation-spécifique."
    },
    {
      "id": "fait:v3-paix-rencontre",
      "enonce_fr": "Pointe-à-Callière présente la Grande Paix de Montréal comme une négociation entre plusieurs nations autochtones et des représentants français en août 1701.",
      "periode": "1701 — Grande Paix de Montréal",
      "kristal": "rencontres-coloniales-quebec",
      "source_ids": [
        "src:v3-pac-paix"
      ],
      "limites": "Chaque délégation conserve sa propre identité et ses intérêts."
    },
    {
      "id": "fait:paix-date",
      "enonce_fr": "La Grande Paix de Montréal a été conclue le 4 août 1701.",
      "periode": "1701 — Grande Paix de Montréal",
      "kristal": "rencontres-coloniales-quebec",
      "source_ids": [
        "src:pac-grande-paix",
        "src:pac-traite"
      ],
      "limites": "Une date ponctuelle ne qualifie pas à elle seule les conséquences du traité."
    },
    {
      "id": "fait:kondiaronk",
      "enonce_fr": "Kondiaronk, dirigeant wendat, a joué un rôle déterminant dans les négociations menant à la Grande Paix de Montréal.",
      "periode": "1701 — Grande Paix de Montréal",
      "kristal": "rencontres-coloniales-quebec",
      "source_ids": [
        "src:pc-kondiaronk",
        "src:pac-grande-paix"
      ],
      "limites": "Ne pas le présenter comme représentant de toutes les nations autochtones."
    },
    {
      "id": "fait:calliere",
      "enonce_fr": "Louis-Hector de Callière, gouverneur de la Nouvelle-France, a participé aux négociations conduisant à la Grande Paix de 1701.",
      "periode": "1701 — Grande Paix de Montréal",
      "kristal": "rencontres-coloniales-quebec",
      "source_ids": [
        "src:pac-grande-paix"
      ],
      "limites": "Rôle colonial précis; les autorités autochtones ne relèvent pas de son autorité politique interne."
    },
    {
      "id": "fait:v3-paix-kondiaronk",
      "enonce_fr": "Pointe-à-Callière souligne le rôle diplomatique du dirigeant wendat Kondiaronk dans les négociations de 1701.",
      "periode": "1701 — Grande Paix de Montréal",
      "kristal": "rencontres-coloniales-quebec",
      "source_ids": [
        "src:v3-pac-paix"
      ],
      "limites": "Ne pas attribuer toutes les décisions d’un traité à un seul acteur."
    },
    {
      "id": "fait:v3-paix-texte",
      "enonce_fr": "Une transcription du traité de 1701 conserve les paroles attribuées à plusieurs délégations.",
      "periode": "1701 — Grande Paix de Montréal",
      "kristal": "rencontres-coloniales-quebec",
      "source_ids": [
        "src:v3-pac-traite"
      ],
      "limites": "La transcription passe par une conservation et une écriture coloniales; ce n’est pas une parole directe enregistrée."
    },
    {
      "id": "fait:pouvoir-apres1760",
      "enonce_fr": "Après 1760, la Nouvelle-France passe sous autorité britannique et de nouveaux acteurs britanniques prennent place dans le commerce des fourrures.",
      "periode": "Après 1760 — changement de régime et revendications",
      "kristal": "rencontres-coloniales-quebec",
      "source_ids": [
        "src:pc-apres1760"
      ],
      "limites": "Ce changement de gouvernement colonial ne signifie pas que les nations autochtones disparaissent ou acceptent les mêmes autorités."
    },
    {
      "id": "fait:wendat-1825",
      "enonce_fr": "En 1825, des chefs de la Nation Wendat ont présenté des revendications territoriales au roi George IV en Grande-Bretagne.",
      "periode": "Après 1760 — changement de régime et revendications",
      "kristal": "rencontres-coloniales-quebec",
      "source_ids": [
        "src:wendat-archives"
      ],
      "limites": "Exemple d’action politique wendat, pas de consentement à la dépossession."
    },
    {
      "id": "fait:vie-aujourdhui",
      "enonce_fr": "Les nations autochtones sont des peuples vivants aujourd’hui, avec leurs langues, leurs cultures et leurs institutions distinctes.",
      "periode": "Aujourd’hui",
      "kristal": "societes-autochtones-quebec",
      "source_ids": [
        "src:quebec-nations"
      ],
      "limites": "Ne pas raconter ces peuples seulement au passé."
    },
    {
      "id": "fait:wendat-langue-vivante",
      "enonce_fr": "La Nation Wendat décrit des efforts contemporains pour revitaliser et transmettre sa langue.",
      "periode": "Aujourd’hui",
      "kristal": "societes-autochtones-quebec",
      "source_ids": [
        "src:wendat-histoire-2026"
      ],
      "limites": "La transmission et la vitalité changent avec le temps; ne pas dire que tous les locuteurs ont la même expérience."
    },
    {
      "id": "fait:traitement-sources",
      "enonce_fr": "Le traité conservé est un document historique dont les mots et les perspectives doivent être contextualisés.",
      "periode": "1701 — Grande Paix de Montréal",
      "kristal": "rencontres-coloniales-quebec",
      "source_ids": [
        "src:pac-traite",
        "src:quebec-ccq"
      ],
      "limites": "Ne pas présenter la transcription coloniale comme témoignage autochtone direct ou comme texte neutre."
    },
    {
      "id": "fait:v3-paix-38-39",
      "enonce_fr": "Des publications de Pointe-à-Callière ne donnent pas toutes le même nombre de nations participantes : des pages indiquent 38 et d’autres 39.",
      "periode": "1701 — Grande Paix de Montréal",
      "kristal": "rencontres-coloniales-quebec",
      "source_ids": [
        "src:v3-pac-325"
      ],
      "limites": "Il faut examiner les catégories et conventions de dénombrement avant de fixer un chiffre; aucune correction automatique."
    },
    {
      "id": "fait:v3-innu-aine",
      "enonce_fr": "Nametau innu met en scène et documente la transmission de connaissances entre des aînés et des enfants.",
      "periode": "Aujourd’hui",
      "kristal": "societes-autochtones-quebec",
      "source_ids": [
        "src:v3-nametau-visite"
      ],
      "limites": "La visite est un parcours documentaire et éducatif; pas un inventaire de toutes les familles innues."
    }
  ],
  "activites": [
    {
      "id": "v3:carte:fait:peuples-avant",
      "type": "choix_attestation",
      "categorie": "comprendre_les_societes",
      "question": "Quelle fiche du corpus documente cette information ?",
      "indice": "Les peuples autochtones habitent le territoire de l’actuel Québec bien avant l’établissement colonial français de 1608.",
      "contexte": "Avant l’implantation coloniale française dans la vallée du Saint-Laurent",
      "options": [
        {
          "id": "fait:peuples-avant",
          "label": "Les peuples autochtones habitent le territoire de l’actuel Québec bien avant l’établissement colonial français de 1608."
        },
        {
          "id": "fait:commerce-fourrures",
          "label": "Au début du XVIIe siècle, des commerçants français ont échangé des biens manufacturés avec des partenaires autochtones contre des fourrures."
        },
        {
          "id": "fait:commerce-participation",
          "label": "Des partenaires autochtones ont joué des rôles essentiels de fournisseurs et d’intermédiaires du commerce des fourrures en Nouvelle-France."
        }
      ],
      "correct_id": "fait:peuples-avant",
      "reponse_courte": "Cette fiche est bien documentée pour la période indiquée.",
      "reponse_longue": "Les peuples autochtones habitent le territoire de l’actuel Québec bien avant l’établissement colonial français de 1608. Description générale; ne pas projeter les onze structures administratives actuelles sur 1500. Source(s) : Gouvernement du Québec — Les 11 nations autochtones du Québec, Parcs Canada — Samuel de Champlain, premier Français à Chambly.",
      "source_ids": [
        "src:quebec-nations",
        "src:pc-champlain"
      ],
      "proprietaire": "societes-autochtones-quebec",
      "prealables": [
        "notion:source-historique",
        "notion:periode-historique"
      ],
      "attention": "Les autres fiches peuvent être vraies; elles ne répondent simplement pas au repère choisi."
    },
    {
      "id": "v3:carte:fait:wendat-maisons",
      "type": "choix_attestation",
      "categorie": "comprendre_les_societes",
      "question": "Quelle fiche du corpus documente cette information ?",
      "indice": "Selon le Conseil de la Nation Wendat, des villages historiques wendat regroupaient plusieurs familles et clans dans des maisons longues.",
      "contexte": "Organisations historiques — datation à préciser",
      "options": [
        {
          "id": "fait:commerce-fourrures",
          "label": "Au début du XVIIe siècle, des commerçants français ont échangé des biens manufacturés avec des partenaires autochtones contre des fourrures."
        },
        {
          "id": "fait:commerce-participation",
          "label": "Des partenaires autochtones ont joué des rôles essentiels de fournisseurs et d’intermédiaires du commerce des fourrures en Nouvelle-France."
        },
        {
          "id": "fait:wendat-maisons",
          "label": "Selon le Conseil de la Nation Wendat, des villages historiques wendat regroupaient plusieurs familles et clans dans des maisons longues."
        }
      ],
      "correct_id": "fait:wendat-maisons",
      "reponse_courte": "Cette fiche est bien documentée pour la période indiquée.",
      "reponse_longue": "Selon le Conseil de la Nation Wendat, des villages historiques wendat regroupaient plusieurs familles et clans dans des maisons longues. L’organisation et la taille des communautés ont changé dans le temps; ne pas généraliser à toutes les nations. Source(s) : Conseil de la Nation Wendat — Histoire et culture.",
      "source_ids": [
        "src:wendat-histoire"
      ],
      "proprietaire": "societes-autochtones-quebec",
      "prealables": [
        "notion:source-historique",
        "notion:periode-historique"
      ],
      "attention": "Les autres fiches peuvent être vraies; elles ne répondent simplement pas au repère choisi."
    },
    {
      "id": "v3:carte:fait:wendat-meres-clan",
      "type": "choix_attestation",
      "categorie": "comprendre_les_societes",
      "question": "Quelle fiche du corpus documente cette information ?",
      "indice": "Le Conseil de la Nation Wendat décrit une transmission traditionnelle de l’appartenance familiale par la lignée maternelle, avec des mères de clan jouant un rôle central.",
      "contexte": "Organisations historiques — datation à préciser",
      "options": [
        {
          "id": "fait:commerce-participation",
          "label": "Des partenaires autochtones ont joué des rôles essentiels de fournisseurs et d’intermédiaires du commerce des fourrures en Nouvelle-France."
        },
        {
          "id": "fait:wendat-meres-clan",
          "label": "Le Conseil de la Nation Wendat décrit une transmission traditionnelle de l’appartenance familiale par la lignée maternelle, avec des mères de clan jouant un rôle central."
        },
        {
          "id": "fait:commerce-fourrures",
          "label": "Au début du XVIIe siècle, des commerçants français ont échangé des biens manufacturés avec des partenaires autochtones contre des fourrures."
        }
      ],
      "correct_id": "fait:wendat-meres-clan",
      "reponse_courte": "Cette fiche est bien documentée pour la période indiquée.",
      "reponse_longue": "Le Conseil de la Nation Wendat décrit une transmission traditionnelle de l’appartenance familiale par la lignée maternelle, avec des mères de clan jouant un rôle central. Ces rôles sont documentés pour la Nation Wendat; pas un système universel autochtone. Source(s) : Conseil de la Nation Wendat — Histoire et culture.",
      "source_ids": [
        "src:wendat-histoire"
      ],
      "proprietaire": "societes-autochtones-quebec",
      "prealables": [
        "notion:source-historique",
        "notion:periode-historique"
      ],
      "attention": "Les autres fiches peuvent être vraies; elles ne répondent simplement pas au repère choisi."
    },
    {
      "id": "v3:carte:fait:innus-saisons",
      "type": "choix_attestation",
      "categorie": "comprendre_les_societes",
      "question": "Quelle fiche du corpus documente cette information ?",
      "indice": "La ressource Nametau innu décrit, dans des contextes traditionnels, des déplacements de familles innues suivant les saisons et les ressources du Nitassinan.",
      "contexte": "Organisations historiques — datation à préciser",
      "options": [
        {
          "id": "fait:innus-saisons",
          "label": "La ressource Nametau innu décrit, dans des contextes traditionnels, des déplacements de familles innues suivant les saisons et les ressources du Nitassinan."
        },
        {
          "id": "fait:commerce-fourrures",
          "label": "Au début du XVIIe siècle, des commerçants français ont échangé des biens manufacturés avec des partenaires autochtones contre des fourrures."
        },
        {
          "id": "fait:commerce-participation",
          "label": "Des partenaires autochtones ont joué des rôles essentiels de fournisseurs et d’intermédiaires du commerce des fourrures en Nouvelle-France."
        }
      ],
      "correct_id": "fait:innus-saisons",
      "reponse_courte": "Cette fiche est bien documentée pour la période indiquée.",
      "reponse_longue": "La ressource Nametau innu décrit, dans des contextes traditionnels, des déplacements de familles innues suivant les saisons et les ressources du Nitassinan. Il ne faut pas qualifier une nation entière de nomade éternellement; pratiques et modes de vie évoluent. Source(s) : Nametau innu — Territoire et cycle de vie traditionnels (point de vue scientifique).",
      "source_ids": [
        "src:nametau-territoire"
      ],
      "proprietaire": "societes-autochtones-quebec",
      "prealables": [
        "notion:source-historique",
        "notion:periode-historique"
      ],
      "attention": "Les autres fiches peuvent être vraies; elles ne répondent simplement pas au repère choisi."
    },
    {
      "id": "v3:carte:fait:v3-innu-outils",
      "type": "choix_attestation",
      "categorie": "comprendre_les_societes",
      "question": "Quelle fiche du corpus documente cette information ?",
      "indice": "Nametau innu décrit la fabrication de canots à partir de bois de bouleau, d’écorce et de racines.",
      "contexte": "Organisations historiques — datation à préciser",
      "options": [
        {
          "id": "fait:commerce-fourrures",
          "label": "Au début du XVIIe siècle, des commerçants français ont échangé des biens manufacturés avec des partenaires autochtones contre des fourrures."
        },
        {
          "id": "fait:commerce-participation",
          "label": "Des partenaires autochtones ont joué des rôles essentiels de fournisseurs et d’intermédiaires du commerce des fourrures en Nouvelle-France."
        },
        {
          "id": "fait:v3-innu-outils",
          "label": "Nametau innu décrit la fabrication de canots à partir de bois de bouleau, d’écorce et de racines."
        }
      ],
      "correct_id": "fait:v3-innu-outils",
      "reponse_courte": "Cette fiche est bien documentée pour la période indiquée.",
      "reponse_longue": "Nametau innu décrit la fabrication de canots à partir de bois de bouleau, d’écorce et de racines. La source documente un procédé traditionnel, pas une obligation pour chaque personne. Source(s) : Nametau innu — La culture matérielle.",
      "source_ids": [
        "src:v3-nametau-materiel"
      ],
      "proprietaire": "societes-autochtones-quebec",
      "prealables": [
        "notion:source-historique",
        "notion:periode-historique"
      ],
      "attention": "Les autres fiches peuvent être vraies; elles ne répondent simplement pas au repère choisi."
    },
    {
      "id": "v3:carte:fait:v3-wendat-gouvernance",
      "type": "choix_attestation",
      "categorie": "comprendre_les_societes",
      "question": "Quelle fiche du corpus documente cette information ?",
      "indice": "La Nation Wendat décrit aujourd’hui un conseil d’élus composé d’un Grand Chef et de Chefs familiaux.",
      "contexte": "Aujourd’hui",
      "options": [
        {
          "id": "fait:commerce-participation",
          "label": "Des partenaires autochtones ont joué des rôles essentiels de fournisseurs et d’intermédiaires du commerce des fourrures en Nouvelle-France."
        },
        {
          "id": "fait:v3-wendat-gouvernance",
          "label": "La Nation Wendat décrit aujourd’hui un conseil d’élus composé d’un Grand Chef et de Chefs familiaux."
        },
        {
          "id": "fait:commerce-fourrures",
          "label": "Au début du XVIIe siècle, des commerçants français ont échangé des biens manufacturés avec des partenaires autochtones contre des fourrures."
        }
      ],
      "correct_id": "fait:v3-wendat-gouvernance",
      "reponse_courte": "Cette fiche est bien documentée pour la période indiquée.",
      "reponse_longue": "La Nation Wendat décrit aujourd’hui un conseil d’élus composé d’un Grand Chef et de Chefs familiaux. Cette organisation contemporaine ne décrit pas identiquement les conseils du XVIIe siècle. Source(s) : Nation Wendat — Histoire & culture.",
      "source_ids": [
        "src:v3-wendat-histoire"
      ],
      "proprietaire": "societes-autochtones-quebec",
      "prealables": [
        "notion:source-historique",
        "notion:periode-historique"
      ],
      "attention": "Les autres fiches peuvent être vraies; elles ne répondent simplement pas au repère choisi."
    },
    {
      "id": "v3:carte:fait:commerce-fourrures",
      "type": "choix_attestation",
      "categorie": "echanges_et_rencontres",
      "question": "Quelle fiche du corpus documente cette information ?",
      "indice": "Au début du XVIIe siècle, des commerçants français ont échangé des biens manufacturés avec des partenaires autochtones contre des fourrures.",
      "contexte": "Début du XVIIe siècle — échanges et établissements",
      "options": [
        {
          "id": "fait:commerce-fourrures",
          "label": "Au début du XVIIe siècle, des commerçants français ont échangé des biens manufacturés avec des partenaires autochtones contre des fourrures."
        },
        {
          "id": "fait:peuples-avant",
          "label": "Les peuples autochtones habitent le territoire de l’actuel Québec bien avant l’établissement colonial français de 1608."
        },
        {
          "id": "fait:wendat-maisons",
          "label": "Selon le Conseil de la Nation Wendat, des villages historiques wendat regroupaient plusieurs familles et clans dans des maisons longues."
        }
      ],
      "correct_id": "fait:commerce-fourrures",
      "reponse_courte": "Cette fiche est bien documentée pour la période indiquée.",
      "reponse_longue": "Au début du XVIIe siècle, des commerçants français ont échangé des biens manufacturés avec des partenaires autochtones contre des fourrures. Les échanges ne décrivent ni tous les peuples ni des conditions immuables. Source(s) : Gouvernement du Canada — L’arrivée des Européens : guerres du XVIIe siècle, Parcs Canada — Samuel de Champlain, premier Français à Chambly.",
      "source_ids": [
        "src:dnd-rencontres",
        "src:pc-champlain"
      ],
      "proprietaire": "rencontres-coloniales-quebec",
      "prealables": [
        "notion:source-historique",
        "notion:periode-historique"
      ],
      "attention": "Les autres fiches peuvent être vraies; elles ne répondent simplement pas au repère choisi."
    },
    {
      "id": "v3:carte:fait:commerce-participation",
      "type": "choix_attestation",
      "categorie": "echanges_et_rencontres",
      "question": "Quelle fiche du corpus documente cette information ?",
      "indice": "Des partenaires autochtones ont joué des rôles essentiels de fournisseurs et d’intermédiaires du commerce des fourrures en Nouvelle-France.",
      "contexte": "Début du XVIIe siècle — échanges et établissements",
      "options": [
        {
          "id": "fait:peuples-avant",
          "label": "Les peuples autochtones habitent le territoire de l’actuel Québec bien avant l’établissement colonial français de 1608."
        },
        {
          "id": "fait:wendat-maisons",
          "label": "Selon le Conseil de la Nation Wendat, des villages historiques wendat regroupaient plusieurs familles et clans dans des maisons longues."
        },
        {
          "id": "fait:commerce-participation",
          "label": "Des partenaires autochtones ont joué des rôles essentiels de fournisseurs et d’intermédiaires du commerce des fourrures en Nouvelle-France."
        }
      ],
      "correct_id": "fait:commerce-participation",
      "reponse_courte": "Cette fiche est bien documentée pour la période indiquée.",
      "reponse_longue": "Des partenaires autochtones ont joué des rôles essentiels de fournisseurs et d’intermédiaires du commerce des fourrures en Nouvelle-France. Ne jamais cantonner tous les Autochtones à un rôle économique unique. Source(s) : Parcs Canada — Samuel de Champlain, premier Français à Chambly.",
      "source_ids": [
        "src:pc-champlain"
      ],
      "proprietaire": "rencontres-coloniales-quebec",
      "prealables": [
        "notion:source-historique",
        "notion:periode-historique"
      ],
      "attention": "Les autres fiches peuvent être vraies; elles ne répondent simplement pas au repère choisi."
    },
    {
      "id": "v3:carte:fait:alliance-1603",
      "type": "choix_attestation",
      "categorie": "echanges_et_rencontres",
      "question": "Quelle fiche du corpus documente cette information ?",
      "indice": "En 1603, à Tadoussac, des représentants français concluent des alliances avec des partenaires autochtones nommés dans les sources historiques.",
      "contexte": "Début du XVIIe siècle — échanges et établissements",
      "options": [
        {
          "id": "fait:wendat-maisons",
          "label": "Selon le Conseil de la Nation Wendat, des villages historiques wendat regroupaient plusieurs familles et clans dans des maisons longues."
        },
        {
          "id": "fait:alliance-1603",
          "label": "En 1603, à Tadoussac, des représentants français concluent des alliances avec des partenaires autochtones nommés dans les sources historiques."
        },
        {
          "id": "fait:peuples-avant",
          "label": "Les peuples autochtones habitent le territoire de l’actuel Québec bien avant l’établissement colonial français de 1608."
        }
      ],
      "correct_id": "fait:alliance-1603",
      "reponse_courte": "Cette fiche est bien documentée pour la période indiquée.",
      "reponse_longue": "En 1603, à Tadoussac, des représentants français concluent des alliances avec des partenaires autochtones nommés dans les sources historiques. Les ethnonymes archivistiques exigent contextualisation et recoupement nation-spécifique. Source(s) : Gouvernement du Canada — L’arrivée des Européens : guerres du XVIIe siècle.",
      "source_ids": [
        "src:dnd-rencontres"
      ],
      "proprietaire": "rencontres-coloniales-quebec",
      "prealables": [
        "notion:source-historique",
        "notion:periode-historique"
      ],
      "attention": "Les autres fiches peuvent être vraies; elles ne répondent simplement pas au repère choisi."
    },
    {
      "id": "v3:carte:fait:v3-paix-rencontre",
      "type": "choix_attestation",
      "categorie": "echanges_et_rencontres",
      "question": "Quelle fiche du corpus documente cette information ?",
      "indice": "Pointe-à-Callière présente la Grande Paix de Montréal comme une négociation entre plusieurs nations autochtones et des représentants français en août 1701.",
      "contexte": "1701 — Grande Paix de Montréal",
      "options": [
        {
          "id": "fait:v3-paix-rencontre",
          "label": "Pointe-à-Callière présente la Grande Paix de Montréal comme une négociation entre plusieurs nations autochtones et des représentants français en août 1701."
        },
        {
          "id": "fait:peuples-avant",
          "label": "Les peuples autochtones habitent le territoire de l’actuel Québec bien avant l’établissement colonial français de 1608."
        },
        {
          "id": "fait:wendat-maisons",
          "label": "Selon le Conseil de la Nation Wendat, des villages historiques wendat regroupaient plusieurs familles et clans dans des maisons longues."
        }
      ],
      "correct_id": "fait:v3-paix-rencontre",
      "reponse_courte": "Cette fiche est bien documentée pour la période indiquée.",
      "reponse_longue": "Pointe-à-Callière présente la Grande Paix de Montréal comme une négociation entre plusieurs nations autochtones et des représentants français en août 1701. Chaque délégation conserve sa propre identité et ses intérêts. Source(s) : Pointe-à-Callière — La Grande Paix de Montréal.",
      "source_ids": [
        "src:v3-pac-paix"
      ],
      "proprietaire": "rencontres-coloniales-quebec",
      "prealables": [
        "notion:source-historique",
        "notion:periode-historique"
      ],
      "attention": "Les autres fiches peuvent être vraies; elles ne répondent simplement pas au repère choisi."
    },
    {
      "id": "v3:carte:fait:paix-date",
      "type": "choix_attestation",
      "categorie": "diplomatie",
      "question": "Quelle fiche du corpus documente cette information ?",
      "indice": "La Grande Paix de Montréal a été conclue le 4 août 1701.",
      "contexte": "1701 — Grande Paix de Montréal",
      "options": [
        {
          "id": "fait:peuples-avant",
          "label": "Les peuples autochtones habitent le territoire de l’actuel Québec bien avant l’établissement colonial français de 1608."
        },
        {
          "id": "fait:wendat-maisons",
          "label": "Selon le Conseil de la Nation Wendat, des villages historiques wendat regroupaient plusieurs familles et clans dans des maisons longues."
        },
        {
          "id": "fait:paix-date",
          "label": "La Grande Paix de Montréal a été conclue le 4 août 1701."
        }
      ],
      "correct_id": "fait:paix-date",
      "reponse_courte": "Cette fiche est bien documentée pour la période indiquée.",
      "reponse_longue": "La Grande Paix de Montréal a été conclue le 4 août 1701. Une date ponctuelle ne qualifie pas à elle seule les conséquences du traité. Source(s) : Pointe-à-Callière — La Grande Paix de Montréal, Pointe-à-Callière — Le traité de la Grande Paix de Montréal (transcription).",
      "source_ids": [
        "src:pac-grande-paix",
        "src:pac-traite"
      ],
      "proprietaire": "rencontres-coloniales-quebec",
      "prealables": [
        "notion:source-historique",
        "notion:periode-historique"
      ],
      "attention": "Les autres fiches peuvent être vraies; elles ne répondent simplement pas au repère choisi."
    },
    {
      "id": "v3:carte:fait:kondiaronk",
      "type": "choix_attestation",
      "categorie": "diplomatie",
      "question": "Quelle fiche du corpus documente cette information ?",
      "indice": "Kondiaronk, dirigeant wendat, a joué un rôle déterminant dans les négociations menant à la Grande Paix de Montréal.",
      "contexte": "1701 — Grande Paix de Montréal",
      "options": [
        {
          "id": "fait:wendat-maisons",
          "label": "Selon le Conseil de la Nation Wendat, des villages historiques wendat regroupaient plusieurs familles et clans dans des maisons longues."
        },
        {
          "id": "fait:kondiaronk",
          "label": "Kondiaronk, dirigeant wendat, a joué un rôle déterminant dans les négociations menant à la Grande Paix de Montréal."
        },
        {
          "id": "fait:peuples-avant",
          "label": "Les peuples autochtones habitent le territoire de l’actuel Québec bien avant l’établissement colonial français de 1608."
        }
      ],
      "correct_id": "fait:kondiaronk",
      "reponse_courte": "Cette fiche est bien documentée pour la période indiquée.",
      "reponse_longue": "Kondiaronk, dirigeant wendat, a joué un rôle déterminant dans les négociations menant à la Grande Paix de Montréal. Ne pas le présenter comme représentant de toutes les nations autochtones. Source(s) : Parcs Canada — Kondiaronk, Pointe-à-Callière — La Grande Paix de Montréal.",
      "source_ids": [
        "src:pc-kondiaronk",
        "src:pac-grande-paix"
      ],
      "proprietaire": "rencontres-coloniales-quebec",
      "prealables": [
        "notion:source-historique",
        "notion:periode-historique"
      ],
      "attention": "Les autres fiches peuvent être vraies; elles ne répondent simplement pas au repère choisi."
    },
    {
      "id": "v3:carte:fait:calliere",
      "type": "choix_attestation",
      "categorie": "diplomatie",
      "question": "Quelle fiche du corpus documente cette information ?",
      "indice": "Louis-Hector de Callière, gouverneur de la Nouvelle-France, a participé aux négociations conduisant à la Grande Paix de 1701.",
      "contexte": "1701 — Grande Paix de Montréal",
      "options": [
        {
          "id": "fait:calliere",
          "label": "Louis-Hector de Callière, gouverneur de la Nouvelle-France, a participé aux négociations conduisant à la Grande Paix de 1701."
        },
        {
          "id": "fait:peuples-avant",
          "label": "Les peuples autochtones habitent le territoire de l’actuel Québec bien avant l’établissement colonial français de 1608."
        },
        {
          "id": "fait:wendat-maisons",
          "label": "Selon le Conseil de la Nation Wendat, des villages historiques wendat regroupaient plusieurs familles et clans dans des maisons longues."
        }
      ],
      "correct_id": "fait:calliere",
      "reponse_courte": "Cette fiche est bien documentée pour la période indiquée.",
      "reponse_longue": "Louis-Hector de Callière, gouverneur de la Nouvelle-France, a participé aux négociations conduisant à la Grande Paix de 1701. Rôle colonial précis; les autorités autochtones ne relèvent pas de son autorité politique interne. Source(s) : Pointe-à-Callière — La Grande Paix de Montréal.",
      "source_ids": [
        "src:pac-grande-paix"
      ],
      "proprietaire": "rencontres-coloniales-quebec",
      "prealables": [
        "notion:source-historique",
        "notion:periode-historique"
      ],
      "attention": "Les autres fiches peuvent être vraies; elles ne répondent simplement pas au repère choisi."
    },
    {
      "id": "v3:carte:fait:v3-paix-kondiaronk",
      "type": "choix_attestation",
      "categorie": "diplomatie",
      "question": "Quelle fiche du corpus documente cette information ?",
      "indice": "Pointe-à-Callière souligne le rôle diplomatique du dirigeant wendat Kondiaronk dans les négociations de 1701.",
      "contexte": "1701 — Grande Paix de Montréal",
      "options": [
        {
          "id": "fait:peuples-avant",
          "label": "Les peuples autochtones habitent le territoire de l’actuel Québec bien avant l’établissement colonial français de 1608."
        },
        {
          "id": "fait:wendat-maisons",
          "label": "Selon le Conseil de la Nation Wendat, des villages historiques wendat regroupaient plusieurs familles et clans dans des maisons longues."
        },
        {
          "id": "fait:v3-paix-kondiaronk",
          "label": "Pointe-à-Callière souligne le rôle diplomatique du dirigeant wendat Kondiaronk dans les négociations de 1701."
        }
      ],
      "correct_id": "fait:v3-paix-kondiaronk",
      "reponse_courte": "Cette fiche est bien documentée pour la période indiquée.",
      "reponse_longue": "Pointe-à-Callière souligne le rôle diplomatique du dirigeant wendat Kondiaronk dans les négociations de 1701. Ne pas attribuer toutes les décisions d’un traité à un seul acteur. Source(s) : Pointe-à-Callière — La Grande Paix de Montréal.",
      "source_ids": [
        "src:v3-pac-paix"
      ],
      "proprietaire": "rencontres-coloniales-quebec",
      "prealables": [
        "notion:source-historique",
        "notion:periode-historique"
      ],
      "attention": "Les autres fiches peuvent être vraies; elles ne répondent simplement pas au repère choisi."
    },
    {
      "id": "v3:carte:fait:v3-paix-texte",
      "type": "choix_attestation",
      "categorie": "diplomatie",
      "question": "Quelle fiche du corpus documente cette information ?",
      "indice": "Une transcription du traité de 1701 conserve les paroles attribuées à plusieurs délégations.",
      "contexte": "1701 — Grande Paix de Montréal",
      "options": [
        {
          "id": "fait:wendat-maisons",
          "label": "Selon le Conseil de la Nation Wendat, des villages historiques wendat regroupaient plusieurs familles et clans dans des maisons longues."
        },
        {
          "id": "fait:v3-paix-texte",
          "label": "Une transcription du traité de 1701 conserve les paroles attribuées à plusieurs délégations."
        },
        {
          "id": "fait:peuples-avant",
          "label": "Les peuples autochtones habitent le territoire de l’actuel Québec bien avant l’établissement colonial français de 1608."
        }
      ],
      "correct_id": "fait:v3-paix-texte",
      "reponse_courte": "Cette fiche est bien documentée pour la période indiquée.",
      "reponse_longue": "Une transcription du traité de 1701 conserve les paroles attribuées à plusieurs délégations. La transcription passe par une conservation et une écriture coloniales; ce n’est pas une parole directe enregistrée. Source(s) : Pointe-à-Callière — Transcription de la Grande Paix de Montréal.",
      "source_ids": [
        "src:v3-pac-traite"
      ],
      "proprietaire": "rencontres-coloniales-quebec",
      "prealables": [
        "notion:source-historique",
        "notion:periode-historique"
      ],
      "attention": "Les autres fiches peuvent être vraies; elles ne répondent simplement pas au repère choisi."
    },
    {
      "id": "v3:carte:fait:pouvoir-apres1760",
      "type": "choix_attestation",
      "categorie": "transformations",
      "question": "Quelle fiche du corpus documente cette information ?",
      "indice": "Après 1760, la Nouvelle-France passe sous autorité britannique et de nouveaux acteurs britanniques prennent place dans le commerce des fourrures.",
      "contexte": "Après 1760 — changement de régime et revendications",
      "options": [
        {
          "id": "fait:pouvoir-apres1760",
          "label": "Après 1760, la Nouvelle-France passe sous autorité britannique et de nouveaux acteurs britanniques prennent place dans le commerce des fourrures."
        },
        {
          "id": "fait:peuples-avant",
          "label": "Les peuples autochtones habitent le territoire de l’actuel Québec bien avant l’établissement colonial français de 1608."
        },
        {
          "id": "fait:wendat-maisons",
          "label": "Selon le Conseil de la Nation Wendat, des villages historiques wendat regroupaient plusieurs familles et clans dans des maisons longues."
        }
      ],
      "correct_id": "fait:pouvoir-apres1760",
      "reponse_courte": "Cette fiche est bien documentée pour la période indiquée.",
      "reponse_longue": "Après 1760, la Nouvelle-France passe sous autorité britannique et de nouveaux acteurs britanniques prennent place dans le commerce des fourrures. Ce changement de gouvernement colonial ne signifie pas que les nations autochtones disparaissent ou acceptent les mêmes autorités. Source(s) : Parcs Canada — Une histoire tapissée de fourrures (Lachine).",
      "source_ids": [
        "src:pc-apres1760"
      ],
      "proprietaire": "rencontres-coloniales-quebec",
      "prealables": [
        "notion:source-historique",
        "notion:periode-historique"
      ],
      "attention": "Les autres fiches peuvent être vraies; elles ne répondent simplement pas au repère choisi."
    },
    {
      "id": "v3:carte:fait:wendat-1825",
      "type": "choix_attestation",
      "categorie": "transformations",
      "question": "Quelle fiche du corpus documente cette information ?",
      "indice": "En 1825, des chefs de la Nation Wendat ont présenté des revendications territoriales au roi George IV en Grande-Bretagne.",
      "contexte": "Après 1760 — changement de régime et revendications",
      "options": [
        {
          "id": "fait:peuples-avant",
          "label": "Les peuples autochtones habitent le territoire de l’actuel Québec bien avant l’établissement colonial français de 1608."
        },
        {
          "id": "fait:wendat-maisons",
          "label": "Selon le Conseil de la Nation Wendat, des villages historiques wendat regroupaient plusieurs familles et clans dans des maisons longues."
        },
        {
          "id": "fait:wendat-1825",
          "label": "En 1825, des chefs de la Nation Wendat ont présenté des revendications territoriales au roi George IV en Grande-Bretagne."
        }
      ],
      "correct_id": "fait:wendat-1825",
      "reponse_courte": "Cette fiche est bien documentée pour la période indiquée.",
      "reponse_longue": "En 1825, des chefs de la Nation Wendat ont présenté des revendications territoriales au roi George IV en Grande-Bretagne. Exemple d’action politique wendat, pas de consentement à la dépossession. Source(s) : Conseil de la Nation Wendat — Centre d’archives.",
      "source_ids": [
        "src:wendat-archives"
      ],
      "proprietaire": "rencontres-coloniales-quebec",
      "prealables": [
        "notion:source-historique",
        "notion:periode-historique"
      ],
      "attention": "Les autres fiches peuvent être vraies; elles ne répondent simplement pas au repère choisi."
    },
    {
      "id": "v3:carte:fait:vie-aujourdhui",
      "type": "choix_attestation",
      "categorie": "transformations",
      "question": "Quelle fiche du corpus documente cette information ?",
      "indice": "Les nations autochtones sont des peuples vivants aujourd’hui, avec leurs langues, leurs cultures et leurs institutions distinctes.",
      "contexte": "Aujourd’hui",
      "options": [
        {
          "id": "fait:wendat-maisons",
          "label": "Selon le Conseil de la Nation Wendat, des villages historiques wendat regroupaient plusieurs familles et clans dans des maisons longues."
        },
        {
          "id": "fait:vie-aujourdhui",
          "label": "Les nations autochtones sont des peuples vivants aujourd’hui, avec leurs langues, leurs cultures et leurs institutions distinctes."
        },
        {
          "id": "fait:peuples-avant",
          "label": "Les peuples autochtones habitent le territoire de l’actuel Québec bien avant l’établissement colonial français de 1608."
        }
      ],
      "correct_id": "fait:vie-aujourdhui",
      "reponse_courte": "Cette fiche est bien documentée pour la période indiquée.",
      "reponse_longue": "Les nations autochtones sont des peuples vivants aujourd’hui, avec leurs langues, leurs cultures et leurs institutions distinctes. Ne pas raconter ces peuples seulement au passé. Source(s) : Gouvernement du Québec — Les 11 nations autochtones du Québec.",
      "source_ids": [
        "src:quebec-nations"
      ],
      "proprietaire": "societes-autochtones-quebec",
      "prealables": [
        "notion:source-historique",
        "notion:periode-historique"
      ],
      "attention": "Les autres fiches peuvent être vraies; elles ne répondent simplement pas au repère choisi."
    },
    {
      "id": "v3:carte:fait:wendat-langue-vivante",
      "type": "choix_attestation",
      "categorie": "transformations",
      "question": "Quelle fiche du corpus documente cette information ?",
      "indice": "La Nation Wendat décrit des efforts contemporains pour revitaliser et transmettre sa langue.",
      "contexte": "Aujourd’hui",
      "options": [
        {
          "id": "fait:wendat-langue-vivante",
          "label": "La Nation Wendat décrit des efforts contemporains pour revitaliser et transmettre sa langue."
        },
        {
          "id": "fait:peuples-avant",
          "label": "Les peuples autochtones habitent le territoire de l’actuel Québec bien avant l’établissement colonial français de 1608."
        },
        {
          "id": "fait:wendat-maisons",
          "label": "Selon le Conseil de la Nation Wendat, des villages historiques wendat regroupaient plusieurs familles et clans dans des maisons longues."
        }
      ],
      "correct_id": "fait:wendat-langue-vivante",
      "reponse_courte": "Cette fiche est bien documentée pour la période indiquée.",
      "reponse_longue": "La Nation Wendat décrit des efforts contemporains pour revitaliser et transmettre sa langue. La transmission et la vitalité changent avec le temps; ne pas dire que tous les locuteurs ont la même expérience. Source(s) : Nation Wendat — Histoire et culture (rôles, langue, maison longue, famille).",
      "source_ids": [
        "src:wendat-histoire-2026"
      ],
      "proprietaire": "societes-autochtones-quebec",
      "prealables": [
        "notion:source-historique",
        "notion:periode-historique"
      ],
      "attention": "Les autres fiches peuvent être vraies; elles ne répondent simplement pas au repère choisi."
    },
    {
      "id": "v3:carte:fait:traitement-sources",
      "type": "choix_attestation",
      "categorie": "sources_et_points_de_vue",
      "question": "Quelle fiche du corpus documente cette information ?",
      "indice": "Le traité conservé est un document historique dont les mots et les perspectives doivent être contextualisés.",
      "contexte": "1701 — Grande Paix de Montréal",
      "options": [
        {
          "id": "fait:peuples-avant",
          "label": "Les peuples autochtones habitent le territoire de l’actuel Québec bien avant l’établissement colonial français de 1608."
        },
        {
          "id": "fait:wendat-maisons",
          "label": "Selon le Conseil de la Nation Wendat, des villages historiques wendat regroupaient plusieurs familles et clans dans des maisons longues."
        },
        {
          "id": "fait:traitement-sources",
          "label": "Le traité conservé est un document historique dont les mots et les perspectives doivent être contextualisés."
        }
      ],
      "correct_id": "fait:traitement-sources",
      "reponse_courte": "Cette fiche est bien documentée pour la période indiquée.",
      "reponse_longue": "Le traité conservé est un document historique dont les mots et les perspectives doivent être contextualisés. Ne pas présenter la transcription coloniale comme témoignage autochtone direct ou comme texte neutre. Source(s) : Pointe-à-Callière — Le traité de la Grande Paix de Montréal (transcription), Gouvernement du Québec — Culture et citoyenneté québécoise au primaire.",
      "source_ids": [
        "src:pac-traite",
        "src:quebec-ccq"
      ],
      "proprietaire": "rencontres-coloniales-quebec",
      "prealables": [
        "notion:source-historique",
        "notion:periode-historique"
      ],
      "attention": "Les autres fiches peuvent être vraies; elles ne répondent simplement pas au repère choisi."
    },
    {
      "id": "v3:carte:fait:v3-innu-aine",
      "type": "choix_attestation",
      "categorie": "sources_et_points_de_vue",
      "question": "Quelle fiche du corpus documente cette information ?",
      "indice": "Nametau innu met en scène et documente la transmission de connaissances entre des aînés et des enfants.",
      "contexte": "Aujourd’hui",
      "options": [
        {
          "id": "fait:wendat-maisons",
          "label": "Selon le Conseil de la Nation Wendat, des villages historiques wendat regroupaient plusieurs familles et clans dans des maisons longues."
        },
        {
          "id": "fait:v3-innu-aine",
          "label": "Nametau innu met en scène et documente la transmission de connaissances entre des aînés et des enfants."
        },
        {
          "id": "fait:peuples-avant",
          "label": "Les peuples autochtones habitent le territoire de l’actuel Québec bien avant l’établissement colonial français de 1608."
        }
      ],
      "correct_id": "fait:v3-innu-aine",
      "reponse_courte": "Cette fiche est bien documentée pour la période indiquée.",
      "reponse_longue": "Nametau innu met en scène et documente la transmission de connaissances entre des aînés et des enfants. La visite est un parcours documentaire et éducatif; pas un inventaire de toutes les familles innues. Source(s) : Nametau innu — Visite guidée.",
      "source_ids": [
        "src:v3-nametau-visite"
      ],
      "proprietaire": "societes-autochtones-quebec",
      "prealables": [
        "notion:source-historique",
        "notion:periode-historique"
      ],
      "attention": "Les autres fiches peuvent être vraies; elles ne répondent simplement pas au repère choisi."
    },
    {
      "id": "v3:relation:relation:v3-wendat-representer",
      "type": "choix_role",
      "categorie": "roles_et_taches",
      "question": "Dans les fiches sourcées, quel rôle est associé à cette tâche ?",
      "indice": "Délibérer et représenter des membres",
      "contexte": "Aujourd’hui",
      "options": [
        {
          "id": "relation:v3-wendat-representer",
          "label": "Membre élu du Conseil wendat"
        },
        {
          "id": "relation:innus-ainés",
          "label": "Aînées et aînés transmettant des récits dans les campements d’été"
        },
        {
          "id": "relation:innus-outils",
          "label": "Personnes qui fabriquent ou réparent outils et moyens de transport"
        }
      ],
      "correct_id": "relation:v3-wendat-representer",
      "reponse_courte": "Le lien rôle–tâche est documenté dans ce contexte.",
      "reponse_longue": "La Nation Wendat décrit aujourd’hui un conseil d’élus composé d’un Grand Chef et de Chefs familiaux. Cette organisation contemporaine ne décrit pas identiquement les conseils du XVIIe siècle.",
      "source_ids": [],
      "proprietaire": "societes-autochtones-quebec",
      "prealables": [
        "notion:role",
        "notion:tache",
        "notion:periode-historique"
      ],
      "attention": "Choisir une autre fiche ne démontre pas que cet autre rôle était historiquement impossible."
    },
    {
      "id": "v3:relation:relation:v3-innu-transmission",
      "type": "choix_role",
      "categorie": "roles_et_taches",
      "question": "Dans les fiches sourcées, quel rôle est associé à cette tâche ?",
      "indice": "Transmettre des connaissances",
      "contexte": "Aujourd’hui",
      "options": [
        {
          "id": "relation:innus-ainés",
          "label": "Aînées et aînés transmettant des récits dans les campements d’été"
        },
        {
          "id": "relation:innus-outils",
          "label": "Personnes qui fabriquent ou réparent outils et moyens de transport"
        },
        {
          "id": "relation:v3-innu-transmission",
          "label": "Adulte qui transmet des savoirs"
        }
      ],
      "correct_id": "relation:v3-innu-transmission",
      "reponse_courte": "Le lien rôle–tâche est documenté dans ce contexte.",
      "reponse_longue": "Nametau innu met en scène et documente la transmission de connaissances entre des aînés et des enfants. La visite est un parcours documentaire et éducatif; pas un inventaire de toutes les familles innues.",
      "source_ids": [],
      "proprietaire": "societes-autochtones-quebec",
      "prealables": [
        "notion:role",
        "notion:tache",
        "notion:periode-historique"
      ],
      "attention": "Choisir une autre fiche ne démontre pas que cet autre rôle était historiquement impossible."
    },
    {
      "id": "v3:relation:relation:v3-innu-canoe",
      "type": "choix_role",
      "categorie": "roles_et_taches",
      "question": "Dans les fiches sourcées, quel rôle est associé à cette tâche ?",
      "indice": "Fabriquer et entretenir des canots",
      "contexte": "Organisations historiques — datation à préciser",
      "options": [
        {
          "id": "relation:innus-outils",
          "label": "Personnes qui fabriquent ou réparent outils et moyens de transport"
        },
        {
          "id": "relation:v3-innu-canoe",
          "label": "Artisane ou artisan innu"
        },
        {
          "id": "relation:innus-ainés",
          "label": "Aînées et aînés transmettant des récits dans les campements d’été"
        }
      ],
      "correct_id": "relation:v3-innu-canoe",
      "reponse_courte": "Le lien rôle–tâche est documenté dans ce contexte.",
      "reponse_longue": "Nametau innu décrit la fabrication de canots à partir de bois de bouleau, d’écorce et de racines. La source documente un procédé traditionnel, pas une obligation pour chaque personne.",
      "source_ids": [],
      "proprietaire": "societes-autochtones-quebec",
      "prealables": [
        "notion:role",
        "notion:tache",
        "notion:periode-historique"
      ],
      "attention": "Choisir une autre fiche ne démontre pas que cet autre rôle était historiquement impossible."
    },
    {
      "id": "v3:relation:relation:v3-wendat-diplomatie",
      "type": "choix_role",
      "categorie": "roles_et_taches",
      "question": "Dans les fiches sourcées, quel rôle est associé à cette tâche ?",
      "indice": "Négocier une entente de paix",
      "contexte": "1701 — Grande Paix de Montréal",
      "options": [
        {
          "id": "relation:v3-wendat-diplomatie",
          "label": "Diplomate wendat dans une négociation historique"
        },
        {
          "id": "relation:innus-ainés",
          "label": "Aînées et aînés transmettant des récits dans les campements d’été"
        },
        {
          "id": "relation:innus-outils",
          "label": "Personnes qui fabriquent ou réparent outils et moyens de transport"
        }
      ],
      "correct_id": "relation:v3-wendat-diplomatie",
      "reponse_courte": "Le lien rôle–tâche est documenté dans ce contexte.",
      "reponse_longue": "Pointe-à-Callière souligne le rôle diplomatique du dirigeant wendat Kondiaronk dans les négociations de 1701. Ne pas attribuer toutes les décisions d’un traité à un seul acteur.",
      "source_ids": [],
      "proprietaire": "rencontres-coloniales-quebec",
      "prealables": [
        "notion:role",
        "notion:tache",
        "notion:periode-historique"
      ],
      "attention": "Choisir une autre fiche ne démontre pas que cet autre rôle était historiquement impossible."
    },
    {
      "id": "v3:relation:relation:v3-delegation-paix",
      "type": "choix_role",
      "categorie": "roles_et_taches",
      "question": "Dans les fiches sourcées, quel rôle est associé à cette tâche ?",
      "indice": "Exprimer un engagement dans une négociation",
      "contexte": "1701 — Grande Paix de Montréal",
      "options": [
        {
          "id": "relation:innus-ainés",
          "label": "Aînées et aînés transmettant des récits dans les campements d’été"
        },
        {
          "id": "relation:innus-outils",
          "label": "Personnes qui fabriquent ou réparent outils et moyens de transport"
        },
        {
          "id": "relation:v3-delegation-paix",
          "label": "Déléguées et délégués de nations réunies"
        }
      ],
      "correct_id": "relation:v3-delegation-paix",
      "reponse_courte": "Le lien rôle–tâche est documenté dans ce contexte.",
      "reponse_longue": "Une transcription du traité de 1701 conserve les paroles attribuées à plusieurs délégations. La transcription passe par une conservation et une écriture coloniales; ce n’est pas une parole directe enregistrée.",
      "source_ids": [],
      "proprietaire": "rencontres-coloniales-quebec",
      "prealables": [
        "notion:role",
        "notion:tache",
        "notion:periode-historique"
      ],
      "attention": "Choisir une autre fiche ne démontre pas que cet autre rôle était historiquement impossible."
    }
  ],
  "sources": [
    {
      "id": "src:nametau-cycle-2026",
      "title": "Nametau innu — Territoire et cycle de vie traditionnels, point de vue scientifique",
      "locator": "https://www.nametauinnu.ca/fr/accueil/science/outil/cycle.html",
      "proprietaire": "societes-autochtones-quebec"
    },
    {
      "id": "src:nametau-temoignage",
      "title": "Nametau innu — Grand-mère : contexte social (paroles et témoignages)",
      "locator": "https://www.nametauinnu.ca/fr/culture/ouverture/detail/58/152.html",
      "proprietaire": "societes-autochtones-quebec"
    },
    {
      "id": "src:nametau-territoire",
      "title": "Nametau innu — Territoire et cycle de vie traditionnels (point de vue scientifique)",
      "locator": "https://www.nametauinnu.ca/fr/accueil/science/outil/cycle.html",
      "proprietaire": "societes-autochtones-quebec"
    },
    {
      "id": "src:pac-texte-1701",
      "title": "Pointe-à-Callière — Transcription du traité de la Grande Paix de Montréal",
      "locator": "https://pacmusee.qc.ca/fr/traite-grande-paix-montreal/",
      "proprietaire": "societes-autochtones-quebec"
    },
    {
      "id": "src:pc-champlain",
      "title": "Parcs Canada — Samuel de Champlain, premier Français à Chambly",
      "locator": "https://parcs.canada.ca/lhn-nhs/qc/fortchambly/culture/histoire-history/site/samuel-de-champlain",
      "proprietaire": "societes-autochtones-quebec"
    },
    {
      "id": "src:quebec-nations",
      "title": "Gouvernement du Québec — Les 11 nations autochtones du Québec",
      "locator": "https://www.quebec.ca/gouvernement/portrait-quebec/premieres-nations-inuits/profil-des-nations/a-propos-nations",
      "proprietaire": "societes-autochtones-quebec"
    },
    {
      "id": "src:v3-nametau-intro",
      "title": "Nametau innu — Mémoire et connaissance du Nitassinan",
      "locator": "https://www.nametauinnu.ca/fr/accueil.html",
      "proprietaire": "societes-autochtones-quebec"
    },
    {
      "id": "src:v3-nametau-materiel",
      "title": "Nametau innu — La culture matérielle",
      "locator": "https://www.nametauinnu.ca/fr/accueil/science/outil.html",
      "proprietaire": "societes-autochtones-quebec"
    },
    {
      "id": "src:v3-nametau-visite",
      "title": "Nametau innu — Visite guidée",
      "locator": "https://www.nametauinnu.ca/fr/visite.html",
      "proprietaire": "societes-autochtones-quebec"
    },
    {
      "id": "src:v3-wendat-histoire",
      "title": "Nation Wendat — Histoire & culture",
      "locator": "https://www.wendake.ca/histoire-et-culture",
      "proprietaire": "societes-autochtones-quebec"
    },
    {
      "id": "src:wendat-conseil-2026",
      "title": "Nation Wendat — Grand Chef et Chefs (mandat, élus, redevabilité)",
      "locator": "https://www.wendake.ca/grand-chef-et-chefs-familiaux",
      "proprietaire": "societes-autochtones-quebec"
    },
    {
      "id": "src:wendat-gouvernance",
      "title": "Conseil de la Nation Wendat — Grand Chef et Chefs familiaux",
      "locator": "https://www.wendake.ca/grand-chef-et-chefs-familiaux",
      "proprietaire": "societes-autochtones-quebec"
    },
    {
      "id": "src:wendat-histoire",
      "title": "Conseil de la Nation Wendat — Histoire et culture",
      "locator": "https://www.wendake.ca/histoire-et-culture",
      "proprietaire": "societes-autochtones-quebec"
    },
    {
      "id": "src:wendat-histoire-2026",
      "title": "Nation Wendat — Histoire et culture (rôles, langue, maison longue, famille)",
      "locator": "https://www.wendake.ca/histoire-et-culture",
      "proprietaire": "societes-autochtones-quebec"
    },
    {
      "id": "src:dnd-rencontres",
      "title": "Gouvernement du Canada — L’arrivée des Européens : guerres du XVIIe siècle",
      "locator": "https://www.canada.ca/fr/ministere-defense-nationale/services/histoire-militaire/histoire-patrimoine/ouvrages-grand-public/autochtones-militaire-canadienne/arrivee-europeens-guerres-XVIIe-siecle.html",
      "proprietaire": "rencontres-coloniales-quebec"
    },
    {
      "id": "src:pac-contexte-1701",
      "title": "Pointe-à-Callière — La Grande Paix de Montréal : contextualisation",
      "locator": "https://pacmusee.qc.ca/fr/histoires-de-montreal/article/la-grande-paix-de-montreal/",
      "proprietaire": "rencontres-coloniales-quebec"
    },
    {
      "id": "src:pac-grande-paix",
      "title": "Pointe-à-Callière — La Grande Paix de Montréal",
      "locator": "https://pacmusee.qc.ca/fr/histoires-de-montreal/article/la-grande-paix-de-montreal/",
      "proprietaire": "rencontres-coloniales-quebec"
    },
    {
      "id": "src:pac-texte-1701",
      "title": "Pointe-à-Callière — Transcription du traité de la Grande Paix de Montréal",
      "locator": "https://pacmusee.qc.ca/fr/traite-grande-paix-montreal/",
      "proprietaire": "rencontres-coloniales-quebec"
    },
    {
      "id": "src:pac-traite",
      "title": "Pointe-à-Callière — Le traité de la Grande Paix de Montréal (transcription)",
      "locator": "https://pacmusee.qc.ca/fr/traite-grande-paix-montreal/",
      "proprietaire": "rencontres-coloniales-quebec"
    },
    {
      "id": "src:pc-apres1760",
      "title": "Parcs Canada — Une histoire tapissée de fourrures (Lachine)",
      "locator": "https://parcs.canada.ca/lhn-nhs/qc/lachine/culture/histoire-history/site/trappe-trapping",
      "proprietaire": "rencontres-coloniales-quebec"
    },
    {
      "id": "src:pc-champlain",
      "title": "Parcs Canada — Samuel de Champlain, premier Français à Chambly",
      "locator": "https://parcs.canada.ca/lhn-nhs/qc/fortchambly/culture/histoire-history/site/samuel-de-champlain",
      "proprietaire": "rencontres-coloniales-quebec"
    },
    {
      "id": "src:pc-kondiaronk",
      "title": "Parcs Canada — Kondiaronk",
      "locator": "https://www.pc.gc.ca/apps/dfhd/page_nhs_fra.aspx?i=69214&id=1938",
      "proprietaire": "rencontres-coloniales-quebec"
    },
    {
      "id": "src:pc-mikmaq",
      "title": "Parcs Canada — L’alliance entre les Mi’kmaq et les Français au XVIIIe siècle",
      "locator": "https://www.canada.ca/fr/parcs-canada/nouvelles/2019/08/lalliance-entre-les-mikmaq-et-les-francais-au-xviiiesiecle.html",
      "proprietaire": "rencontres-coloniales-quebec"
    },
    {
      "id": "src:pc-pensionnats",
      "title": "Parcs Canada — Le système de pensionnats autochtones",
      "locator": "https://www.canada.ca/fr/parcs-canada/nouvelles/2020/09/le-systeme-de-pensionnats-autochtones.html",
      "proprietaire": "rencontres-coloniales-quebec"
    },
    {
      "id": "src:quebec-ccq",
      "title": "Gouvernement du Québec — Culture et citoyenneté québécoise au primaire",
      "locator": "https://www.quebec.ca/education/prescolaire-primaire-et-secondaire/programmes-formations-evaluation/programme-formation-ecole-quebecoise/primaire/culture-citoyennete-quebecoise",
      "proprietaire": "rencontres-coloniales-quebec"
    },
    {
      "id": "src:v3-pac-325",
      "title": "Pointe-à-Callière — 325e anniversaire de la Grande Paix",
      "locator": "https://pacmusee.qc.ca/fr/medias/communiques-de-presse/communique-presse-grande-paix-montreal-1701/",
      "proprietaire": "rencontres-coloniales-quebec"
    },
    {
      "id": "src:v3-pac-paix",
      "title": "Pointe-à-Callière — La Grande Paix de Montréal",
      "locator": "https://pacmusee.qc.ca/fr/histoires-de-montreal/article/la-grande-paix-de-montreal/",
      "proprietaire": "rencontres-coloniales-quebec"
    },
    {
      "id": "src:v3-pac-traite",
      "title": "Pointe-à-Callière — Transcription de la Grande Paix de Montréal",
      "locator": "https://pacmusee.qc.ca/fr/traite-grande-paix-montreal/",
      "proprietaire": "rencontres-coloniales-quebec"
    },
    {
      "id": "src:wendat-archives",
      "title": "Conseil de la Nation Wendat — Centre d’archives",
      "locator": "https://www.wendake.ca/etablissements/centre-darchives",
      "proprietaire": "rencontres-coloniales-quebec"
    }
  ],
  "images": [
    {
      "id": "visuel:territoires-presences",
      "moment": "Découvrir",
      "titre": "Territoires habités",
      "concept_prompt": "Représenter plusieurs lieux habités et plusieurs communautés autochtones distinctes sur le territoire de l’actuel Québec avant les établissements coloniaux français. Mettre en évidence l’ancienneté de la présence, la pluralité des nations et leurs relations avec le territoire. Éviter une carte qui prétend délimiter exactement tous les droits territoriaux ou des costumes attribués à une nation sans source. Aucun texte ni réponse.",
      "expected_path": "assets/territoires-presences.webp",
      "alt_fr": "Territoires habités",
      "contraintes": "aucune carte historique factuelle sans données géographiques validées",
      "statut": "description_sans_image"
    },
    {
      "id": "visuel:echanges-et-ressources",
      "moment": "Essayer",
      "titre": "Échange de ressources",
      "concept_prompt": "Représenter une situation historique d’échange entre des partenaires autochtones et des commerçants français, où les fourrures et des objets manufacturés sont des ressources présentes. Rendre visibles les acteurs et la circulation des biens sans hiérarchie implicite. Éviter d’affirmer qu’une transaction unique décrit toutes les relations. Aucun mot ni quantité évaluée.",
      "expected_path": "assets/echanges-et-ressources.webp",
      "alt_fr": "Échange de ressources",
      "contraintes": "les quantités et la validation d’échanges appartiennent au MiniLab",
      "statut": "description_sans_image"
    },
    {
      "id": "visuel:diplomatie-1701",
      "moment": "Comparer",
      "titre": "Négociations entre délégations",
      "concept_prompt": "Illustrer une réunion diplomatique rassemblant des représentants de plusieurs nations autochtones distinctes et des autorités françaises autour d’une négociation en 1701 à Montréal. Montrer la pluralité des interlocuteurs et le rôle des paroles et des accords. Éviter les reproductions supposées exactes de personnes, objets cérémoniels ou symboles sacrés sans sources. Sans texte et sans réponses visibles.",
      "expected_path": "assets/diplomatie-1701.webp",
      "alt_fr": "Négociations entre délégations",
      "contraintes": "toute image présentée comme document historique doit avoir provenance et révision",
      "statut": "description_sans_image"
    },
    {
      "id": "visuel:sources-et-voix",
      "moment": "Enquêter",
      "titre": "Des documents et leurs perspectives",
      "concept_prompt": "Représenter deux documents historiques étudiés côte à côte, avec des repères indiquant qu’ils proviennent d’époques ou d’auteurs différents, et des espaces libres pour questionner ce qu’ils montrent et ce qui manque. Ne pas simuler une citation autochtone ni inventer des mots d’archives. Sans texte dans l’image.",
      "expected_path": "assets/sources-et-voix.webp",
      "alt_fr": "Des documents et leurs perspectives",
      "contraintes": "les deux sources réelles sont consultables séparément",
      "statut": "description_sans_image"
    },
    {
      "id": "visuel:aujourdhui-nations",
      "moment": "Découvrir",
      "titre": "Les nations aujourd’hui",
      "concept_prompt": "Représenter la vie contemporaine et la diversité de plusieurs communautés autochtones du Québec, en mettant en évidence qu’elles existent aujourd’hui et évoluent. Ne pas mettre toutes les nations dans une seule représentation culturelle; éviter les traits génériques et les vêtements dits « traditionnels » imposés. Sans texte.",
      "expected_path": "assets/aujourdhui-nations.webp",
      "alt_fr": "Les nations aujourd’hui",
      "contraintes": "à soumettre à des représentantes et représentants des nations avant diffusion",
      "statut": "description_sans_image"
    },
    {
      "id": "visuel:transitions-droits",
      "moment": "Explorer",
      "titre": "Des régimes et des droits",
      "concept_prompt": "Représenter une continuité de sociétés autochtones à travers des changements d’autorités coloniales et des démarches de défense de leur territoire. Faire comprendre que changer de régime politique ne fait pas disparaître les nations et que leurs représentants prennent des initiatives. Ne pas imposer une carte de propriété, une frontière non documentée ou des vêtements identitaires fictifs. Ne pas représenter la souffrance d’enfants ni des pensionnats. Aucun texte et aucune réponse.",
      "expected_path": "assets/transitions-droits.webp",
      "alt_fr": "Sociétés vivantes et changements politiques",
      "contraintes": "pas de reconstitution historique présentée comme document authentique",
      "statut": "description_sans_image"
    },
    {
      "id": "visuel:roles-taches-ressources",
      "moment": "Exploration des sources et relations",
      "titre": "Relier le travail, le rôle et la ressource",
      "concept_prompt": "Représenter trois catégories reconnaissables dans une scène pédagogique : une personne exerçant un rôle, une action accomplie et une ressource utilisée. Prévoir des zones distinctes où l’interface pourra superposer des étiquettes exactes générées par le moteur. Les exemples spécifiques à une nation doivent être référencés dans le corpus du cours. Ne pas attribuer d’objets ou vêtements culturellement précis sans documentation. Ne pas afficher de solution.",
      "expected_path": "assets/roles-taches-ressources.webp",
      "alt_fr": "Schéma général des liens entre rôle, action et ressource.",
      "contraintes": "aucune image historique présentée comme preuve sans vérification",
      "statut": "description_sans_image",
      "source_fact_ids": [],
      "media_role": "contexte_conceptuel_non_evaluatif"
    },
    {
      "id": "visuel:wendat-conseil-actuel",
      "moment": "Exploration des sources et relations",
      "titre": "Des responsabilités de gouvernance contemporaines",
      "concept_prompt": "Représenter la notion de conseil d’élus, de représentation des membres, de discussion et de services collectifs dans le contexte contemporain de la Nation Wendat. Les éléments institutionnels doivent être génériques tant qu’aucune référence visuelle validée par la Nation n’est fournie. Ne pas simuler un portrait d’une personne réelle ni inventer de symboles sacrés. Prévoir des emplacements libres pour les étiquettes interactives.",
      "expected_path": "assets/wendat-conseil-actuel.webp",
      "alt_fr": "Concept d’un conseil actuel représentant une communauté.",
      "contraintes": "aucune image historique présentée comme preuve sans vérification",
      "statut": "description_sans_image",
      "source_fact_ids": [],
      "media_role": "contexte_conceptuel_non_evaluatif"
    },
    {
      "id": "visuel:innus-recits",
      "moment": "Exploration des sources et relations",
      "titre": "Transmission intergénérationnelle de récits",
      "concept_prompt": "Faire comprendre que des personnes de différentes générations peuvent transmettre des récits et des connaissances lors de rassemblements saisonniers décrits dans une source innue. Ne pas suggérer que toutes les familles et toutes les époques suivent la même pratique. Ne pas imaginer des motifs culturels, des vêtements traditionnels spécifiques ou des cérémonies sans document de référence autorisé. L’espace doit permettre l’ajout de mots-clés séparés par Ekole.",
      "expected_path": "assets/innus-recits.webp",
      "alt_fr": "Situation conceptuelle de transmission de savoirs entre générations.",
      "contraintes": "aucune image historique présentée comme preuve sans vérification",
      "statut": "description_sans_image",
      "source_fact_ids": [],
      "media_role": "contexte_conceptuel_non_evaluatif"
    },
    {
      "id": "visuel:innus-ressources",
      "moment": "Exploration des sources et relations",
      "titre": "Tâches saisonnières et ressources",
      "concept_prompt": "Décrire la relation entre une saison, une activité d’entretien d’outils, une activité de pêche et les ressources environnementales dans la ressource Nametau innu. Préparer trois zones d’observation distinctes, sans transformer le montage en une chronologie universelle ni prétendre restituer une scène historique exacte. Ne pas afficher de données de capture ou de droits non documentés.",
      "expected_path": "assets/innus-ressources.webp",
      "alt_fr": "Concept de trois activités et ressources saisonnières documentées.",
      "contraintes": "aucune image historique présentée comme preuve sans vérification",
      "statut": "description_sans_image",
      "source_fact_ids": [],
      "media_role": "contexte_conceptuel_non_evaluatif"
    },
    {
      "id": "visuel:traite-1701-sources",
      "moment": "Exploration des sources et relations",
      "titre": "Traité et provenance des paroles",
      "concept_prompt": "Illustrer la différence conceptuelle entre une rencontre diplomatique de plusieurs délégations et un document colonial qui en conserve une transcription. Montrer la relation entre événement, source et interprétation, sans reproduire de signatures, wampums, emblèmes ou symboles historiques spécifiques sans droits et validation. Ne présenter aucune parole inventée comme citation authentique.",
      "expected_path": "assets/traite-1701-sources.webp",
      "alt_fr": "Schéma des liens entre négociations de 1701 et document historique.",
      "contraintes": "aucune image historique présentée comme preuve sans vérification",
      "statut": "description_sans_image",
      "source_fact_ids": [],
      "media_role": "contexte_conceptuel_non_evaluatif"
    },
    {
      "id": "visuel:comparaison-temporelle",
      "moment": "Exploration des sources et relations",
      "titre": "Lire une même société à plusieurs époques",
      "concept_prompt": "Représenter une comparaison en colonnes : pratiques historiquement décrites, événements coloniaux, responsabilités institutionnelles contemporaines. Les colonnes ne doivent pas suggérer que l’une remplace totalement l’autre ni que les nations auraient cessé d’exister. Aucun repère de date ou carte non sourcé; l’interface superposera la chronologie validée.",
      "expected_path": "assets/comparaison-temporelle.webp",
      "alt_fr": "Comparaison conceptuelle entre périodes sans effacer les continuités.",
      "contraintes": "aucune image historique présentée comme preuve sans vérification",
      "statut": "description_sans_image",
      "source_fact_ids": [],
      "media_role": "contexte_conceptuel_non_evaluatif"
    },
    {
      "id": "visuel:relations-reciproques",
      "moment": "Exploration des sources et relations",
      "titre": "Relations multiples entre organisations",
      "concept_prompt": "Représenter un réseau de plusieurs communautés et institutions reliées par des échanges, négociations, alliances et désaccords, sans hiérarchie implicite et sans associer une nation à un cliché visuel. Les étiquettes, noms et directions de relations doivent provenir du graphe plutôt que de l’image, qui ne doit pas imposer d’affirmations historiques précises.",
      "expected_path": "assets/relations-reciproques.webp",
      "alt_fr": "Réseau conceptuel de relations multiples entre organisations.",
      "contraintes": "aucune image historique présentée comme preuve sans vérification",
      "statut": "description_sans_image",
      "source_fact_ids": [],
      "media_role": "contexte_conceptuel_non_evaluatif"
    }
  ],
  "limites": [
    "Aucune approbation culturelle ou pédagogique présumée.",
    "Entraînement ≠ preuve de maîtrise.",
    "Une absence dans le corpus ne démontre pas une négation historique."
  ]
};
