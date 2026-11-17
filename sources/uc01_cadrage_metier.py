"""Génère J1_Retail_Intelligence/01_UC01_besoin_exploration/cadrage_metier.pdf (UC-01, Étape A).

Usage : .venv/bin/python sources/uc01_cadrage_metier.py
Modifier le contenu directement dans ce fichier puis relancer.
"""
from pathlib import Path

from reportlab.platypus import KeepTogether, Spacer

from pdf_style import CELL, H2, H3, SUB, TITLE, build, p, table
from chemins import UC01, UC01_PREUVES  # noqa: E402

OUT = UC01 / "cadrage_metier.pdf"

story = []

# ---------------------------------------------------------------- en-tête
story += [
    p("Retail Intelligence Platform", TITLE),
    p("UC-01 &ndash; Fiche de cadrage métier (Étape A)", SUB),
    p("IPSSI &ndash; Mastère Développement, Data &amp; IA &ndash; TP Jour 1", SUB),
    Spacer(1, 8),
    table([
        ["Élément", "Valeur"],
        ["Livrable", "cadrage_metier.pdf (livrable 1 du dossier UC-01, §5.1.17)"],
        ["Étape couverte", "Étape A &ndash; Comprendre les utilisateurs (§5.1.13)"],
        ["Date", "16/11/2026"],
        ["Version", "v1 &ndash; brouillon de travail"],
        ["Documents liés", "questions_decisionnelles.pdf (détail des questions), "
                           "dictionnaire_KPI.xlsx (Étape B), inventaire_sources.xlsx (Étape C)"],
    ], [4, 13]),
]

# ---------------------------------------------------------------- 1. contexte
story += [
    p("1. Contexte et objectif", H2),
    p("Retail Intelligence est une enseigne de distribution vendant en magasin et sur le web. "
      "Les directions souhaitent des indicateurs fiables pour piloter les ventes, comparer les "
      "magasins et suivre les stocks. Les données proviennent de plusieurs systèmes (ventes, "
      "produits, magasins, stocks, clients, navigation web)."),
    Spacer(1, 4),
    p("Cette fiche formalise <b>qui</b> utilisera la plateforme, <b>quelles décisions</b> ces "
      "utilisateurs doivent prendre et <b>quelles questions</b> ils posent aux données. "
      "Elle ne décrit pas encore de solution technique : les choix d'architecture sont traités dans UC-02."),
    Spacer(1, 4),
    p("<b>Rappel :</b> le jeu de données TPCx-BB est synthétique. Les résultats obtenus servent "
      "de support pédagogique et ne représentent pas une entreprise réelle."),
]

# ---------------------------------------------------------------- 2. périmètre
story += [
    p("2. Périmètre retenu pour cette première itération", H2),
    table([
        ["Dans le périmètre", "Hors périmètre à ce stade (besoin noté, non traité)"],
        ["&bull; Ventes en magasin<br/>&bull; Ventes web<br/>&bull; Produits et catégories<br/>"
         "&bull; Magasins<br/>&bull; Calendrier (jours, mois)<br/>&bull; Stocks par entrepôt",
         "&bull; Retours produits (store_returns, web_returns)<br/>&bull; Caractérisation des clients "
         "(customer, demographics)<br/>&bull; Navigation web (web_clickstreams)<br/>&bull; Avis produits, "
         "promotions, prix concurrents<br/>&bull; Fichiers du dossier data_refresh/ (rôle à valider)"],
    ], [8.5, 8.5]),
    Spacer(1, 3),
    p("Les domaines hors périmètre sont présents dans l'archive mais ne sont pas nécessaires aux six "
      "questions prioritaires ci-dessous. Ils pourront être ajoutés dans une itération suivante.", CELL),
]

# ---------------------------------------------------------------- 3. kit
story += [
    p("3. Kit de données utilisé (§3.4)", H2),
    table([
        ["Information", "Valeur constatée", "Statut"],
        ["Nom de l'archive", "retail_project.zip", "Vérifié"],
        ["Version", "Non communiquée", "Non disponible"],
        ["Provenance", "Archive fournie dans le cadre du TP ; source TPCx-BB annoncée par le sujet", "À valider"],
        ["Date de mise à disposition", "Non communiquée (horodatage des fichiers dans l'archive : 15/11/2026)",
         "Non disponible"],
        ["Source de distribution", "Non communiquée", "Non disponible"],
        ["Format des fichiers", ".dat texte délimité par « | », sans ligne d'en-tête ; 2 fichiers .csv "
         "(item_marketprices_audit.csv)", "Vérifié"],
        ["Volume total (décompressé)", "1 033 993 587 octets (environ 0,96 Go)", "Vérifié"],
        ["Nombre de fichiers", "36 fichiers : 24 dans data/ (23 tables), 12 dans data_refresh/", "Vérifié"],
        ["Empreinte SHA-256 de l'archive", "dc1634e95cb3192487cad0b935a4e8dbd9ae44ca9078ac0b28513575943ed86c",
         "Vérifié"],
        ["Outils de génération", "Non communiqués (PDGF non confirmé)", "Non disponible"],
    ], [4.2, 10.3, 2.5]),
    Spacer(1, 3),
    p("Preuves : preuves/contenu_archive.txt (listing unzip -l) et preuves/checksum.txt.", CELL),
]

# ---------------------------------------------------------------- 4. profils
story += [p("4. Profils utilisateurs retenus", H2),
          p("Trois profils sont retenus, chacun avec deux questions métier. Ils couvrent les trois "
            "domaines au cœur du pilotage commercial : produits et canaux, magasins, stocks.")]

PROFILS = [
    {
        "nom": "Profil 1 &ndash; Direction commerciale",
        "resp": "Définit la stratégie commerciale de l'enseigne : assortiment, répartition des efforts "
                "entre canaux de vente, objectifs de chiffre d'affaires.",
        "besoin": "Vision consolidée des ventes magasin et web, par catégorie de produits et par canal.",
        "freq": "Mensuelle, avec revue trimestrielle.",
        "qs": [
            ["Q1", "Quel est le chiffre d'affaires total de chaque catégorie de produits ?",
             "Choisir les catégories à développer ou à réduire", "Indispensable",
             "store_sales, web_sales, item"],
            ["Q2", "Les clients achètent-ils plus en magasin ou sur le web ?",
             "Répartir le budget entre les deux canaux", "Utile", "store_sales, web_sales"],
        ],
    },
    {
        "nom": "Profil 2 &ndash; Responsable de magasin",
        "resp": "Pilote l'activité d'un point de vente : chiffre d'affaires, organisation du personnel, "
                "comparaison avec les autres magasins du réseau.",
        "besoin": "Ventes de son magasin dans le temps et positionnement par rapport au réseau.",
        "freq": "Hebdomadaire.",
        "qs": [
            ["Q3", "Quel magasin vend le plus ?",
             "Identifier le magasin modèle et aider les moins performants", "Indispensable",
             "store_sales, store"],
            ["Q4", "Quel jour de la semaine y a-t-il le plus de ventes ?",
             "Prévoir plus de personnel ces jours-là", "Utile", "store_sales, date_dim"],
        ],
    },
    {
        "nom": "Profil 3 &ndash; Responsable des stocks",
        "resp": "Garantit la disponibilité des produits : suivi des niveaux de stock, déclenchement des "
                "réapprovisionnements, répartition entre entrepôts.",
        "besoin": "Niveau de stock par produit et par entrepôt à la date la plus récente.",
        "freq": "Quotidienne à hebdomadaire selon la fréquence des relevés d'inventaire (à vérifier).",
        "qs": [
            ["Q5", "Quels produits ont un stock à zéro ?", "Commander ces produits en urgence",
             "Indispensable", "inventory, item"],
            ["Q6", "Quel entrepôt contient le plus de stock ?", "Équilibrer le stock entre les entrepôts",
             "Complémentaire", "inventory, warehouse"],
        ],
    },
]

for pr in PROFILS:
    block = [
        p(pr["nom"], H3),
        table([
            ["Responsabilités", pr["resp"]],
            ["Besoin principal", pr["besoin"]],
            ["Fréquence de consultation", pr["freq"]],
        ], [4.2, 12.8], header=False),
        Spacer(1, 4),
        table([["#", "Question métier", "Décision permise", "Priorité", "Tables pressenties"]] + pr["qs"],
              [1, 5.4, 4.4, 2.7, 3.5]),
    ]
    story.append(KeepTogether(block))

# ---------------------------------------------------------------- 5. synthèse
story += [
    p("5. Synthèse des priorités", H2),
    table([
        ["Priorité", "Questions", "Signification"],
        ["Indispensable", "Q1, Q3, Q5", "Nécessaire au pilotage dès la première version de la plateforme"],
        ["Utile", "Q2, Q4", "Apporte une aide à la décision importante, peut suivre la première version"],
        ["Complémentaire", "Q6", "Enrichit l'analyse, sans bloquer les décisions principales"],
    ], [3.2, 3, 10.8]),
]

# ---------------------------------------------------------------- 6. profils non retenus
story += [
    p("6. Autres profils identifiés (non détaillés dans cette itération)", H2),
    table([
        ["Profil", "Besoin pressenti", "Raison du report"],
        ["Direction générale", "Vision consolidée de l'activité", "Besoin largement couvert par Q1 à Q3 "
                                                                 "agrégés ; à détailler plus tard"],
        ["Contrôleur de gestion", "Marges, taux de remise, comparaisons de périodes",
         "Dépend des définitions de KPI de l'Étape B (montants net / brut, remises)"],
        ["Équipe Data", "Qualité, intégration et mise à disposition des données",
         "Profil fournisseur de la plateforme ; ses besoins sont traités dans UC-02 (gouvernance)"],
    ], [3.8, 5.6, 7.6]),
]

# ---------------------------------------------------------------- 7. statuts / points à valider
story += [
    p("7. Niveau de certitude et points à valider", H2),
    p("Les statuts suivent le §4.2 du sujet : Vérifié, Déduit, Hypothèse, Non disponible, À valider."),
    Spacer(1, 3),
    table([
        ["Point", "Statut"],
        ["Les 7 tables citées (store_sales, web_sales, item, store, date_dim, inventory, warehouse) "
         "sont présentes dans data/", "Vérifié"],
        ["Toutes leurs lignes ont le nombre de champs attendu (23, 34, 22, 29, 28, 4, 14)", "Vérifié"],
        ["Noms et ordre des colonnes (fichiers sans en-tête) conformes à la spécification TPCx-BB v1.7.0, annexe B.2 (23 tables sur 23 identiques, preuve : controle_schema_vs_specification.txt)",
         "Vérifié"],
        ["Les jointures ventes / produits / magasins / dates / entrepôts fonctionnent sur les clés _sk",
         "Vérifié (Étape D : 0 orphelin)"],
        ["Les stocks (inventory) sont relevés par entrepôt et non par magasin", "Déduit (colonne "
         "inv_warehouse_sk, pas de colonne magasin)"],
        ["data_refresh/ complète data/ : data_refresh/item contient exactement les 180 produits "
         "(i_item_sk 17820 à 17999) présents dans inventory mais absents de data/item", "Déduit"],
        ["Rôle exact de data_refresh/ (chargement incrémental ?) et du fichier "
         "item_marketprices_audit.csv (absent du standard TPCx-BB)", "À valider"],
        ["Chiffre d'affaires = net_paid (après remises et coupons, hors taxes, retours non déduits), "
         "formule vérifiée sur 100 % des lignes ; voir dictionnaire_KPI.xlsx",
         "À valider (choix métier)"],
    ], [12.5, 4.5]),
]

build(OUT, story, "UC01 - Cadrage métier", "Retail Intelligence Platform - UC-01 Cadrage métier")
