"""Génère J1_Retail_Intelligence/01_UC01_besoin_exploration/questions_decisionnelles.pdf (UC-01, Étape A).

Usage : .venv/bin/python sources/uc01_questions_decisionnelles.py
Faits chiffrés : voir preuves/controles_kpi.txt.
"""
from pathlib import Path

from reportlab.platypus import KeepTogether, PageBreak, Spacer

from pdf_style import CELL, H2, H3, SUB, TITLE, build, p, table
from chemins import UC01, UC01_PREUVES  # noqa: E402

OUT = UC01 / "questions_decisionnelles.pdf"

story = [
    p("Retail Intelligence Platform", TITLE),
    p("UC-01 &ndash; Matrice des utilisateurs et questions décisionnelles", SUB),
    p("IPSSI &ndash; Mastère Développement, Data &amp; IA &ndash; TP Jour 1", SUB),
    Spacer(1, 8),
    table([
        ["Élément", "Valeur"],
        ["Livrable", "questions_decisionnelles.pdf (livrable 2 du dossier UC-01, §5.1.17)"],
        ["Étape couverte", "Étape A &ndash; Comprendre les utilisateurs (§5.1.13), points 3 à 5"],
        ["Date / version", "16/11/2026 &ndash; v1"],
        ["Documents liés", "cadrage_metier.pdf (profils), dictionnaire_KPI.xlsx (KPI K01 à K12), "
                           "preuves/controles_kpi.txt (contrôles chiffrés)"],
    ], [4, 13]),

    p("1. Objet et méthode", H2),
    p("Ce document détaille les six questions métier retenues dans la fiche de cadrage. Pour chacune, il "
      "établit la chaîne complète : <b>profil &rarr; question &rarr; décision &rarr; indicateur &rarr; "
      "données</b>, et indique si les fichiers réellement fournis permettent d'y répondre."),
    Spacer(1, 4),
    p("Chaque question métier est reformulée en <b>question décisionnelle</b> : une formulation précise, "
      "mesurable, qui dit quel indicateur calculer, sur quel périmètre et à quel niveau de détail. "
      "Les statuts utilisés sont ceux du §4.2 du sujet : Vérifié, Déduit, Hypothèse, Non disponible, À valider."),

    p("2. Matrice de synthèse", H2),
    table([
        ["#", "Profil", "Question métier", "Décision permise", "Priorité", "KPI", "Couverture par les données"],
        ["Q1", "Direction commerciale", "Quel est le chiffre d'affaires total de chaque catégorie de produits ?",
         "Choisir les catégories à développer ou à réduire", "Indispensable", "K02", "Couverte"],
        ["Q2", "Direction commerciale", "Les clients achètent-ils plus en magasin ou sur le web ?",
         "Répartir le budget entre les deux canaux", "Utile", "K03", "Couverte (CA, transactions, clients)"],
        ["Q3", "Responsable de magasin", "Quel magasin vend le plus ?",
         "Identifier le magasin modèle et aider les moins performants", "Indispensable", "K09", "Couverte"],
        ["Q4", "Responsable de magasin", "Quel jour de la semaine y a-t-il le plus de ventes ?",
         "Prévoir plus de personnel ces jours-là", "Utile", "K10", "Couverte"],
        ["Q5", "Responsable des stocks", "Quels produits ont un stock à zéro ?",
         "Commander ces produits en urgence", "Indispensable", "K11", "Couverte avec réserve"],
        ["Q6", "Responsable des stocks", "Quel entrepôt contient le plus de stock ?",
         "Équilibrer le stock entre les entrepôts", "Complémentaire", "K12", "Couverte en unités"],
    ], [1.0, 2.3, 3.5, 3.2, 2.5, 1.0, 3.5]),
    Spacer(1, 3),
    p("Chaque profil a deux questions ; chaque question est reliée à une décision, une priorité et un KPI.", CELL),
    PageBreak(),
    p("3. Fiches détaillées par question", H2),
]

QUESTIONS = [
    {
        "id": "Q1", "titre": "CA par catégorie de produits",
        "rows": [
            ["Profil", "Direction commerciale"],
            ["Question métier", "Quel est le chiffre d'affaires total de chaque catégorie de produits ?"],
            ["Question décisionnelle", "Quel est le CA net (K01) de chaque catégorie i_category, magasin et web "
                                       "confondus, par année, et quelle part du CA total représente-t-elle ?"],
            ["Décision permise", "Choisir les catégories à développer (plus de références, plus de mise en avant) "
                                 "ou à réduire."],
            ["Priorité", "<b>Indispensable</b> : l'assortiment est le premier levier de la direction commerciale."],
            ["KPI", "K02 (principal) ; K01, K06, K07, K08 (complément)"],
            ["Tables et colonnes", "store_sales (ss_item_sk, ss_net_paid, ss_sold_date_sk) ; web_sales (ws_item_sk, "
                                   "ws_net_paid, ws_sold_date_sk) ; item (i_item_sk, i_category)"],
            ["Jointures", "ss_item_sk = i_item_sk et ws_item_sk = i_item_sk : relation N:1, 0 orphelin, "
                          "i_item_sk unique &ndash; <b>Vérifié</b>"],
            ["Données", "Présentes, 0 valeur nulle sur les colonnes utilisées, 9 catégories &ndash; <b>Vérifié</b>"],
            ["Points d'attention", "item a des dates de validité (i_rec_start_date / i_rec_end_date) : une "
                                   "référence peut avoir changé de catégorie (colonne de fin vide : une seule version "
                                   "observée). CA brut de retours. Les doublons (ticket, produit) sont des lignes "
                                   "distinctes (prix et quantités différents) : à conserver."],
            ["Ce que la réponse ne dit pas", "La rentabilité d'une catégorie (marge non incluse) ni la raison "
                                             "de son succès."],
        ],
    },
    {
        "id": "Q2", "titre": "Magasin ou web",
        "rows": [
            ["Profil", "Direction commerciale"],
            ["Question métier", "Les clients achètent-ils plus en magasin ou sur le web ?"],
            ["Question décisionnelle", "Quelle part du CA net et du nombre de transactions est réalisée sur le "
                                       "web et en magasin, par année, et quel est le panier moyen de chaque canal ?"],
            ["Décision permise", "Répartir le budget (marketing, investissements) entre les deux canaux."],
            ["Priorité", "<b>Utile</b> : oriente le budget, mais ne conditionne pas le pilotage quotidien."],
            ["KPI", "K03 (principal) ; K04, K05 (complément)"],
            ["Tables et colonnes", "store_sales (ss_net_paid, ss_ticket_number) ; web_sales (ws_net_paid, "
                                   "ws_order_number)"],
            ["Jointures", "Aucune : les deux tables sont agrégées séparément puis comparées."],
            ["Données", "Présentes, 0 valeur nulle &ndash; <b>Vérifié</b>. 89 100 tickets et 89 100 commandes "
                        "(égalité exacte, effet probable de la génération synthétique)."],
            ["Points d'attention", "Un ticket de caisse et une commande web ne sont pas la même notion. La question "
                                   "parle de « clients » : ss_customer_sk et ws_bill_customer_sk pointent tous deux "
                                   "vers customer sans orphelin (<b>Vérifié</b>, Étape D) ; 37 336 clients magasin, "
                                   "37 367 clients web, dont 14 916 achètent sur les deux canaux."],
            ["Ce que la réponse ne dit pas", "L'effet qu'aurait un changement de budget (corrélation n'est pas "
                                             "causalité)."],
        ],
    },
    {
        "id": "Q3", "titre": "Magasin le plus performant",
        "rows": [
            ["Profil", "Responsable de magasin"],
            ["Question métier", "Quel magasin vend le plus ?"],
            ["Question décisionnelle", "Quel est le classement des 12 magasins selon le CA net, par année, "
                                       "complété par le nombre de transactions et le panier moyen ?"],
            ["Décision permise", "Identifier le magasin modèle et accompagner les moins performants."],
            ["Priorité", "<b>Indispensable</b> : base de la comparaison entre magasins demandée par la direction."],
            ["KPI", "K09 (principal) ; K04, K05, K08 (complément)"],
            ["Tables et colonnes", "store_sales (ss_store_sk, ss_net_paid, ss_ticket_number) ; store (s_store_sk, "
                                   "s_store_name, s_floor_space, s_closed_date_sk)"],
            ["Jointures", "ss_store_sk = s_store_sk : N:1, 0 orphelin, 12 magasins, s_store_id unique &ndash; "
                          "<b>Vérifié</b>"],
            ["Données", "Présentes, 0 valeur nulle &ndash; <b>Vérifié</b>"],
            ["Points d'attention", "« Vend le plus » est interprété comme le CA (choix à valider ; la quantité "
                                   "K06 est l'alternative). Un grand magasin vend mécaniquement plus : rapporter "
                                   "à la surface (s_floor_space, qualité non vérifiée). La date de fermeture "
                                   "(s_closed_date_sk) est incohérente (5 magasins « fermés » avant 2001 vendent "
                                   "en 2001-2005) : ne pas l'utiliser pour exclure des magasins."],
            ["Ce que la réponse ne dit pas", "Pourquoi un magasin performe (emplacement, équipe, clientèle)."],
        ],
    },
    {
        "id": "Q4", "titre": "Jour de la semaine le plus actif",
        "rows": [
            ["Profil", "Responsable de magasin"],
            ["Question métier", "Quel jour de la semaine y a-t-il le plus de ventes ?"],
            ["Question décisionnelle", "Pour un magasin donné, quel jour de la semaine (d_day_name) présente le CA "
                                       "net moyen par jour le plus élevé ?"],
            ["Décision permise", "Prévoir plus de personnel ces jours-là."],
            ["Priorité", "<b>Utile</b> : améliore l'organisation, sans être un indicateur de pilotage central."],
            ["KPI", "K10 (principal) ; K04 (complément)"],
            ["Tables et colonnes", "store_sales (ss_sold_date_sk, ss_store_sk, ss_net_paid) ; date_dim (d_date_sk, "
                                   "d_day_name)"],
            ["Jointures", "ss_sold_date_sk = d_date_sk : N:1, 0 orphelin &ndash; <b>Vérifié</b>"],
            ["Données", "Présentes, 0 valeur nulle &ndash; <b>Vérifié</b>"],
            ["Points d'attention", "Diviser par le nombre de lundis, mardis, etc. de la période, sinon le résultat "
                                   "est biaisé. Jours fériés impossibles à isoler (d_holiday = Y pour tous les jours). Profil hebdomadaire possiblement uniforme "
                                   "(données synthétiques)."],
            ["Ce que la réponse ne dit pas", "Le nombre de personnes nécessaires : pas de données de fréquentation "
                                             "ni d'effectifs (Non disponible)."],
        ],
    },
    {
        "id": "Q5", "titre": "Produits en rupture",
        "rows": [
            ["Profil", "Responsable des stocks"],
            ["Question métier", "Quels produits ont un stock à zéro ?"],
            ["Question décisionnelle", "Au dernier relevé d'inventaire, quels couples (produit, entrepôt) ont "
                                       "inv_quantity_on_hand = 0 ?"],
            ["Décision permise", "Commander ces produits en urgence."],
            ["Priorité", "<b>Indispensable</b> : une rupture fait perdre des ventes immédiatement."],
            ["KPI", "K11 (principal) ; K06 (complément : le produit se vend-il ?)"],
            ["Tables et colonnes", "inventory (inv_date_sk, inv_item_sk, inv_warehouse_sk, inv_quantity_on_hand) ; "
                                   "item (i_item_sk, i_product_name)"],
            ["Jointures", "inv_item_sk = i_item_sk : 180 produits du stock absents de data/item, présents dans "
                          "data_refresh/item &ndash; <b>Vérifié</b>. Il faut donc charger les deux fichiers item."],
            ["Données", "Relevé hebdomadaire de 90 000 couples (18 000 produits x 5 entrepôts). Dernier relevé "
                        "complet le 26/12/2005, dans data_refresh/ : 106 couples à 0, 31 quantités vides &ndash; "
                        "<b>Vérifié</b>"],
            ["Points d'attention", "Le relevé du 12/12/2005 est réparti entre data/ (35 100 lignes) et data_refresh/ "
                                   "(54 900) : charger les deux dossiers, sinon le dernier relevé est incomplet. "
                                   "Une quantité vide n'est pas une rupture : la compter à part. Stock suivi par "
                                   "entrepôt uniquement, pas par magasin (<b>Déduit</b> : pas de colonne magasin). "
                                   "Une rupture de quelques jours entre deux relevés peut échapper."],
            ["Ce que la réponse ne dit pas", "La quantité à commander ni le délai fournisseur (Non disponible)."],
        ],
    },
    {
        "id": "Q6", "titre": "Répartition du stock entre entrepôts",
        "rows": [
            ["Profil", "Responsable des stocks"],
            ["Question métier", "Quel entrepôt contient le plus de stock ?"],
            ["Question décisionnelle", "Au dernier relevé, combien d'unités détient chacun des 5 entrepôts, et "
                                       "quelle part du stock total cela représente-t-il ?"],
            ["Décision permise", "Équilibrer le stock entre les entrepôts."],
            ["Priorité", "<b>Complémentaire</b> : utile à l'optimisation, moins urgent que les ruptures (Q5)."],
            ["KPI", "K12"],
            ["Tables et colonnes", "inventory (inv_date_sk, inv_warehouse_sk, inv_quantity_on_hand) ; warehouse "
                                   "(w_warehouse_sk, w_warehouse_name, w_warehouse_sq_ft)"],
            ["Jointures", "inv_warehouse_sk = w_warehouse_sk : valeurs 0 à 4 des deux côtés, 0 orphelin, N:1 "
                          "&ndash; <b>Vérifié</b> (Étape D)"],
            ["Données", "Présentes ; au 26/12/2005 (dernier relevé complet) les 5 entrepôts détiennent entre "
                        "8,93 et 9,02 millions d'unités &ndash; <b>Vérifié</b>"],
            ["Points d'attention", "Stock en unités, pas en valeur. Ne jamais additionner des relevés de dates "
                                   "différentes. Répartition quasi uniforme (effet probable de la génération "
                                   "synthétique). Piste : web_sales.ws_warehouse_sk (relation vérifiée, 0 orphelin) "
                                   "pour mesurer la demande servie par chaque entrepôt."],
            ["Ce que la réponse ne dit pas", "Si l'entrepôt le plus rempli est sur-stocké : il faudrait le comparer à "
                                             "sa capacité et à sa demande."],
        ],
    },
]

for q in QUESTIONS:
    story.append(KeepTogether([p(f"{q['id']} &ndash; {q['titre']}", H3),
                               table(q["rows"], [4.2, 12.8], header=False), Spacer(1, 6)]))

story += [
    p("4. Questions initiales du sujet (§2.2) : ce qui est retenu, couvert ou reporté", H2),
    p("Le sujet propose huit questions de départ. Le tableau distingue ce que l'entreprise souhaite analyser "
      "de ce que cette itération traite."),
    Spacer(1, 3),
    table([
        ["Question du §2.2", "Traitement", "Données correspondantes", "Statut"],
        ["Quels produits génèrent le plus de ventes ?", "Retenue (Q1, au niveau catégorie ; détail produit "
                                                       "possible avec K02)", "store_sales, web_sales, item", "Vérifié"],
        ["Comment évoluent les ventes dans le temps ?", "Couverte par K08 (évolution N vs N-1)",
         "ventes + date_dim", "Vérifié"],
        ["Quels magasins présentent les meilleures performances ?", "Retenue (Q3)", "store_sales, store", "Vérifié"],
        ["Quels sont les volumes de ventes par canal ?", "Retenue (Q2)", "store_sales, web_sales", "Vérifié"],
        ["Peut-on analyser les niveaux de stock ?", "Retenue (Q5, Q6), par entrepôt uniquement",
         "inventory, warehouse", "Vérifié"],
        ["Quels produits font l'objet de retours ?", "Reportée à une itération suivante",
         "store_returns, web_returns, reason (fichiers présents, non analysés)", "À valider"],
        ["Quelles informations caractérisent les clients ?", "Reportée",
         "customer, customer_address, customer_demographics, household_demographics (présents, non analysés)",
         "À valider"],
        ["Les données de navigation permettent-elles d'étudier les visiteurs ?", "Reportée ; un clic n'est pas "
                                                                               "un achat",
         "web_clickstreams, web_page (présents ; lien clic-vente via wcs_sales_sk : Hypothèse)", "Hypothèse"],
    ], [4.6, 4.4, 5.6, 2.4]),

    p("5. Contrôles de validation (§5.1.15)", H2),
    table([
        ["Contrôle", "Résultat"],
        ["Chaque profil utilisateur possède des besoins identifiés", "Oui : 3 profils, 2 questions chacun"],
        ["Chaque question métier est associée à une décision", "Oui : Q1 à Q6"],
        ["Chaque question a une priorité", "Oui : 3 indispensables, 2 utiles, 1 complémentaire"],
        ["Chaque KPI cité possède une formule et un périmètre", "Oui : voir dictionnaire_KPI.xlsx"],
        ["Chaque source annoncée comme disponible a été observée", "Oui : présence dans l'archive et contrôles "
                                                                   "chiffrés (controles_kpi.txt)"],
        ["Les relations proposées sont justifiées", "Oui pour Q1 à Q6 (0 orphelin mesuré, voir "
                                                    "qualification_donnees.pdf)"],
    ], [8.5, 8.5]),
]

build(OUT, story, "UC01 - Questions décisionnelles",
      "Retail Intelligence Platform - UC-01 Questions décisionnelles")
