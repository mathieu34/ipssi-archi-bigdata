"""Génère J1_Retail_Intelligence/01_UC01_besoin_exploration/limites_hypotheses.pdf (UC-01, Étape E).

Usage : .venv/bin/python sources/uc01_limites_hypotheses.py
Chiffres : preuves/ (controles_kpi.txt, controles_relations.txt, controle_inventaire_complet.txt,
inventaire_fichiers.csv, inventaire_colonnes.csv).
"""
from pathlib import Path

from reportlab.platypus import KeepTogether, PageBreak, Spacer

from pdf_style import CELL, H2, H3, SUB, TITLE, build, p, table
from chemins import UC01, UC01_PREUVES  # noqa: E402

OUT = UC01 / "limites_hypotheses.pdf"

story = [
    p("Retail Intelligence Platform", TITLE),
    p("UC-01 &ndash; Limites, hypothèses et besoins non couverts", SUB),
    p("IPSSI &ndash; Mastère Développement, Data &amp; IA &ndash; TP Jour 1", SUB),
    Spacer(1, 8),
    table([
        ["Élément", "Valeur"],
        ["Livrable", "limites_hypotheses.pdf (livrable 6 du dossier UC-01, §5.1.17)"],
        ["Étape couverte", "Étape E &ndash; Formaliser les limites (§5.1.13) ; solutions de repli (§5.1.19) ; "
                           "questions de recul (§5.1.20)"],
        ["Date / version", "16/11/2026 &ndash; v1"],
        ["Documents liés", "inventaire_sources.xlsx, qualification_donnees.pdf, dictionnaire_KPI.xlsx"],
    ], [4, 13]),
    p("Ce document recense 15 limites (le sujet en demande au moins 5), dont les six points imposés par l'Étape E "
      "(L01 à L06), puis les hypothèses de travail, les points à valider et les besoins métier "
      "non couverts par les données."),

    p("1. Limites des données et des indicateurs", H2),
    p("1.1 Les six points imposés par l'Étape E", H3),
]

LIM_IMPOSEES = [
    ["L01", "Une table présente ne garantit pas que ses champs soient renseignés",
     "item.i_size vide à 14 %, i_units à 4,8 % ; web_clickstreams.wcs_user_sk vide à 42,1 % ; "
     "i_rec_end_date, s_rec_end_date, wp_rec_end_date, web_rec_end_date vides à 100 % ; 5 999 quantités "
     "de stock vides.", "Vérifié",
     "Analyses par taille de produit ou par visiteur biaisées ; historique des référentiels inexistant.",
     "Mesurer le taux de remplissage avant chaque analyse ; afficher la part de valeurs inconnues."],
    ["L02", "Une vente magasin et une vente web ne sont pas modélisées de la même manière",
     "store_sales : 23 colonnes, 1 client, 1 magasin. web_sales : 34 colonnes, client facturé ET client livré, "
     "date d'expédition, frais de port, entrepôt, site, page.", "Vérifié",
     "Pas de « magasin » pour le web, pas d'« entrepôt » pour le magasin ; les montants web ont des frais de port.",
     "Comparer les canaux sur un socle commun (net_paid, quantité, transaction) ; documenter les écarts."],
    ["L03", "Vente, commande, ligne de vente et transaction ne sont pas interchangeables",
     "Une ligne = un produit dans une transaction : 667 579 lignes pour 89 100 tickets (magasin). Un même produit "
     "peut apparaître jusqu'à 4 fois dans un ticket (4 038 cas) avec des prix différents ; aucun numéro de ligne.",
     "Vérifié", "Compter des lignes au lieu de transactions multiplie le nombre de « ventes » par 7,5 environ.",
     "Transaction = COUNT(DISTINCT ss_ticket_number / ws_order_number) ; ne jamais dédoublonner les lignes."],
    ["L04", "Les clics web ne représentent pas automatiquement des ajouts au panier ou des achats",
     "Aucune colonne de type d'événement. 9,9 % des clics sont rattachés à une vente (wcs_sales_sk) ; "
     "42,1 % des clics n'ont pas d'utilisateur.", "Vérifié",
     "Impossible de mesurer un taux d'ajout au panier ou un tunnel de conversion détaillé.",
     "Se limiter à « clic avec / sans vente » ; demander un journal d'événements typés."],
    ["L05", "Les retours doivent être distingués des ventes",
     "Tables séparées (store_returns, web_returns). Délai médian retour - vente : 356 jours (magasin), 421 (web), "
     "jusqu'à 835 jours ; 118 retours dépassent la quantité vendue.", "Vérifié",
     "Le CA des KPI (net_paid) est brut de retours ; rattacher un retour au mois de la vente fausserait les tendances.",
     "Publier un CA brut et, dans une itération suivante, un CA net de retours daté à la date du retour."],
    ["L06", "Une corrélation entre deux indicateurs ne démontre pas une relation de causalité",
     "Ex. : un magasin avec plus de promotions et plus de CA ; un jour avec plus de ventes et plus de personnel.",
     "Déduit", "Les décisions Q2 (budget) et Q4 (personnel) pourraient reposer sur une fausse causalité.",
     "Présenter les KPI comme des constats ; tester une action (A/B, période témoin) avant de conclure."],
]
LIM_AUTRES = [
    ["L07", "Jeu de données synthétique",
     "89 100 tickets et 89 100 commandes exactement ; stock quasi identique dans les 5 entrepôts (8,93 à 9,02 M "
     "d'unités) ; délais de retour irréalistes ; dates de fermeture de magasins de 1917 à 2141.", "Vérifié",
     "Les tendances, saisonnalités et classements ne décrivent pas une entreprise réelle.",
     "Présenter les résultats comme pédagogiques ; valider la méthode, pas les chiffres."],
    ["L08", "Fichiers sans en-tête ni identifiant de ligne",
     "Fichiers sans en-tête (noms et ordre des colonnes vérifiés sur la spécification v1.7.0). Aucun identifiant de ligne unique dans "
     "store_sales, web_sales (couple transaction + produit non unique) ni web_clickstreams.", "Vérifié",
     "Impossible de désigner une ligne de vente ou un clic de façon unique.",
     "Cohérence contrôlée (montants à 100 %, 0 orphelin) ; clé technique à générer en zone Silver."],
    ["L09", "Version, provenance et outil de génération non communiqués", "Seuls le nom de l'archive et son "
     "empreinte SHA-256 sont connus.", "Non disponible", "Reproductibilité limitée ; impossible de régénérer le jeu.",
     "Obtenir l'information ; conserver l'empreinte comme référence."],
    ["L10", "Données réparties entre data/ et data_refresh/",
     "Ventes du 13/12 au 31/12/2005 et relevés de stock des 12/12 (partiel), 19/12 et 26/12 uniquement ou "
     "partiellement dans data_refresh/ ; 180 produits uniquement dans data_refresh/item.", "Vérifié",
     "Avec data/ seul : décembre 2005 tronqué, dernier relevé de stock incomplet, 232 380 lignes de stock orphelines.",
     "Toujours concaténer les deux dossiers (aucun recouvrement constaté)."],
    ["L11", "Devise et fiscalité non documentées", "Aucune colonne de devise ; adresses aux États-Unis "
     "(zip, fuseaux -5 à -10).", "Non disponible", "Unité des KPI monétaires inconnue ; CA hors taxes par choix.",
     "Indiquer « unité monétaire » ; hypothèse H07 à valider."],
    ["L12", "Stock suivi par entrepôt uniquement", "inventory : date, produit, entrepôt, quantité ; aucune "
     "colonne magasin.", "Vérifié", "Le responsable de magasin ne peut pas suivre son stock local.",
     "Besoin non couvert (voir section 4)."],
    ["L13", "Relevés de stock hebdomadaires", "1 relevé tous les 7 jours (259 dates dans data/, 3 dans "
     "data_refresh/).", "Vérifié", "Une rupture de quelques jours entre deux relevés n'est pas visible ; pas de "
                                    "mouvements d'entrée / sortie.", "Présenter K11 comme un état à date."],
    ["L14", "Colonne de fermeture des magasins incohérente", "5 magasins « fermés » avant 2001 vendent en "
     "2001-2005.", "Vérifié", "Filtrer sur s_closed_date_sk supprimerait 5 magasins actifs sur 12.",
     "Ne pas utiliser la colonne ; contrôle de cohérence en Silver."],
    ["L15", "Canaux et sources absents", "Pas de canal catalogue (catalog_sales) ; aucune donnée complémentaire "
     "(météo, logistique, fréquentation, effectifs).", "Non disponible",
     "Q2 limitée à 2 canaux ; Q4 ne permet pas de dimensionner le personnel.", "Voir section 4."],
]
HEAD = ["#", "Limite", "Constat (preuve)", "Statut", "Impact", "Traitement proposé"]
W = [0.9, 3, 4.6, 1.7, 3.4, 3.4]
story += [table([HEAD] + LIM_IMPOSEES, W, size=7.5), Spacer(1, 6),
          p("1.2 Autres limites constatées", H3), table([HEAD] + LIM_AUTRES, W, size=7.5)]

# ------------------------------------------------------------------ hypothèses
story += [
    p("2. Hypothèses de travail", H2),
    p("Propositions retenues pour avancer, à confirmer. Chacune indique ce qui la soutient et comment la vérifier."),
    Spacer(1, 3),
    table([
        ["#", "Hypothèse", "Éléments qui la soutiennent", "Statut", "Vérification proposée"],
        ["H01", "data_refresh/ est un chargement incrémental qui prolonge data/",
         "0 clé commune pour les référentiels ; transactions 89 100 à 89 999 à la suite de 0 à 89 099 ; "
         "période prolongée au 31/12/2005", "Déduit", "Confirmation à obtenir"],
        ["H02", "Les noms de colonnes de la spécification TPCx-BB correspondent aux fichiers",
         "Spécification TPCx-BB v1.7.0, annexe B.2 : 23 tables sur 23 identiques ; nombre de champs conforme sur "
         "100 % des lignes", "Vérifié", "Fait : controle_schema_vs_specification.txt"],
        ["H03", "Les lignes (transaction, produit) répétées sont des ventes distinctes",
         "Prix et quantités différents, même date / heure / client ; aucun doublon complet", "Déduit",
         "Demander s'il existe un numéro de ligne dans la source"],
        ["H04", "Le CA de référence est net_paid (après remises et coupons, hors taxes, retours non déduits)",
         "net_paid = ext_sales_price - coupon_amt vérifié à 100 %", "À valider",
         "Validation par la direction commerciale / le contrôle de gestion"],
        ["H05", "wcs_sales_sk désigne la commande web (ws_order_number)",
         "Correspondance (commande, produit) à 100 %, même date et même client", "Déduit",
         "Documentation du kit"],
        ["H06", "Un clic sans wcs_user_sk provient d'un visiteur anonyme", "42,1 % de clics sans utilisateur, "
         "aucun clic avec vente sans utilisateur", "Hypothèse", "Documentation du kit"],
        ["H07", "Les montants sont en dollars américains", "Adresses et fuseaux horaires des États-Unis",
         "Hypothèse", "À valider"],
        ["H08", "hd_vehicle_count = -1 signifie « inconnu »", "Valeur hors plage naturelle (0 à 4)",
         "Hypothèse", "Documentation du kit"],
        ["H09", "pr_order_sk (avis) désigne une commande web", "0 orphelin vers ws_order_number",
         "Hypothèse", "Contrôle produit / client sur les commandes jointes"],
    ], [1.1, 3.9, 5.2, 1.7, 5.1], size=7.5),

    p("3. Points à valider", H2),
    table([
        ["#", "Point", "Pourquoi"],
        ["V01", "Version, provenance, date et outil de génération du kit (PDGF ?)", "Non communiqués (L09)"],
        ["V02", "Rôle officiel de data_refresh/", "H01 repose sur une déduction"],
        ["V03", "Nature des fichiers item_marketprices_audit.csv", "Hors standard ; non chargés comme tables"],
        ["V04", "Définition du CA et devise (H04, H07)", "Conditionne l'unité et la valeur de 6 KPI"],
    ], [1.2, 9, 6.8]),

    p("4. Besoins métier non couverts et données complémentaires", H2),
    p("Application des solutions de repli du §5.1.19 : chaque besoin non couvert est conservé, avec les "
      "informations qui seraient nécessaires et la source à mobiliser. Aucune valeur n'est inventée."),
    Spacer(1, 3),
    table([
        ["Besoin", "Question concernée", "Information manquante", "Source ou collecte proposée"],
        ["Dimensionner le personnel selon l'affluence", "Q4", "Fréquentation par jour / heure, effectifs, "
                                                            "horaires par jour", "Compteurs d'entrée, SIRH, "
                                                                                 "planning"],
        ["Suivre le stock d'un magasin", "Q5 (magasin)", "Stock par magasin", "Logiciel de caisse / WMS magasin"],
        ["Quantité et délai de réapprovisionnement", "Q5", "Délais fournisseurs, quantités minimales",
         "ERP achats"],
        ["Valoriser le stock", "Q6", "Prix de revient à date", "ERP (coût moyen pondéré)"],
        ["Analyser le parcours web (panier, abandon)", "§2.2 navigation", "Type d'événement par clic",
         "Outil d'analytics web (journal d'événements)"],
        ["Comparer les trois canaux", "Q2", "Ventes catalogue", "Système de vente à distance"],
        ["CA net de retours dans la devise réelle", "Q1, Q3", "Devise, règles de comptabilisation des retours",
         "Contrôle de gestion"],
    ], [4.5, 2.6, 4.6, 5.3], size=7.5),

    p("5. Réponses aux questions de recul (§5.1.20)", H2),
]
RECUL = [
    ("1. Quels besoins métier sont réellement couverts par les données ?",
     "Les six questions retenues (Q1 à Q6) sont couvertes : CA par catégorie, par canal et par magasin, profil "
     "hebdomadaire, ruptures et répartition du stock par entrepôt. Sont aussi couvrables, hors périmètre : retours, "
     "profil des clients, avis, promotions, prix concurrents, et une analyse simple « clic avec / sans achat »."),
    ("2. Quels KPI ne peuvent pas être calculés de manière fiable ?",
     "Un CA net de retours fiable dans le temps (délais de retour irréalistes), un taux de conversion détaillé "
     "(pas de type d'événement), un CA au m² (s_floor_space non qualifié), le stock magasin, la valeur du stock à "
     "date. K08 n'est fiable sur décembre 2005 que si data_refresh/ est chargé ; K11 dépend du traitement des 31 "
     "quantités vides."),
    ("3. Quelle différence entre une donnée disponible et une donnée exploitable ?",
     "Disponible : le fichier et la colonne existent. Exploitable : la colonne est renseignée, son sens est connu, "
     "elle se joint aux autres tables et elle est cohérente. Exemples : s_closed_date_sk est disponible mais pas "
     "exploitable (incohérente) ; wcs_sales_sk n'est exploitable qu'après avoir établi qu'elle désigne une commande "
     "web ; i_rec_end_date est présente mais vide."),
    ("4. Quelles relations entre domaines restent à vérifier ?",
     "Toutes les relations du périmètre sont vérifiées (0 orphelin). Restent à confirmer : le sens de "
     "pr_order_sk (avis -> commande), la clé de ligne de vente (absence de numéro de ligne), et la signification "
     "des retours supérieurs à la quantité vendue."),
    ("5. Quelles limites du jeu synthétique prendre en compte ?",
     "Volumes et répartitions artificiellement réguliers (89 100 tickets et commandes, stock uniforme entre "
     "entrepôts), dates incohérentes (fermetures de magasins, retours tardifs), données personnelles fictives. "
     "Les chiffres servent à valider une méthode et une architecture, pas à prendre des décisions réelles."),
    ("6. Quelles données complémentaires seraient utiles à l'entreprise ?",
     "Fréquentation et effectifs des magasins, stock par magasin, journal d'événements web typés, coûts et délais "
     "fournisseurs, devise et règles comptables des retours, ventes catalogue (section 4)."),
]
for q, a in RECUL:
    story.append(KeepTogether([p(f"<b>{q}</b>"), p(a), Spacer(1, 4)]))

build(OUT, story, "UC01 - Limites et hypothèses", "Retail Intelligence Platform - UC-01 Limites et hypothèses")
