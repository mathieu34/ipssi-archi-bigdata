"""Génère J1_Retail_Intelligence/01_UC01_besoin_exploration/dictionnaire_KPI.xlsx (UC-01, Étape B).

Usage : .venv/bin/python sources/uc01_dictionnaire_kpi.py
Les faits cités (volumes, nulls, période) proviennent de preuves/controles_kpi.txt.
"""
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from chemins import UC01, UC01_PREUVES  # noqa: E402

OUT = UC01 / "dictionnaire_KPI.xlsx"

NAVY = "1B3350"
LIGHT = "EEF3F7"
STATUS_FILL = {"Calculable": "D9EFD9", "Calculable avec réserve": "FFF1CC", "Non calculable": "F8D7D7"}

# Période observée : data/ 2001-01-01 -> 2005-12-13, data_refresh/ 2005-12-13 -> 2005-12-31
PERIODE = ("Du 01/01/2001 au 31/12/2005 en chargeant data/ (jusqu'au 13/12/2005) ET data_refresh/ "
           "(13/12 au 31/12/2005)")
CA_DEF = ("net_paid = ext_sales_price - coupon_amt (vérifié sur 100 % des lignes) : montant payé après "
          "remises et coupons, hors taxes, hors frais de port (web).")

KPIS = [
    # id, nom, profils, questions, définition, formule, unité, périmètre, fréquence,
    # sources, données manquantes, limites, statut
    ["K01", "Chiffre d'affaires net (CA)",
     "Direction commerciale, Responsable de magasin", "Q1, Q2, Q3",
     "Montant total encaissé sur les ventes, après remises et coupons, hors taxes. "
     "Indicateur de base réutilisé par les autres KPI.",
     "CA = SUM(store_sales.ss_net_paid) + SUM(web_sales.ws_net_paid)",
     "Unité monétaire (devise non documentée)",
     "Magasin + web, tous produits. " + PERIODE,
     "Quotidienne (calcul), consultation mensuelle",
     "store_sales.ss_net_paid ; web_sales.ws_net_paid",
     "Retours non déduits (store_returns / web_returns hors périmètre). Devise non documentée.",
     "CA brut de retours : surestime le CA réellement conservé. " + CA_DEF +
     " Les 4 136 doublons (ticket, produit) en magasin et 4 076 en web sont des lignes distinctes "
     "(prix et quantités différents, Étape D) : elles sont toutes comptées.",
     "Calculable avec réserve"],

    ["K02", "CA par catégorie de produits",
     "Direction commerciale", "Q1",
     "Répartition du CA net entre les catégories de produits du catalogue.",
     "CA_cat = SUM(net_paid) des lignes de vente JOIN item ON item_sk = i_item_sk, GROUP BY i_category ; "
     "part_cat = CA_cat / CA total",
     "Unité monétaire et %",
     "Magasin + web, 9 catégories observées. " + PERIODE,
     "Mensuelle",
     "store_sales.ss_item_sk, ss_net_paid ; web_sales.ws_item_sk, ws_net_paid ; item.i_item_sk, i_category",
     "Aucune pour le calcul (0 orphelin, 0 catégorie nulle).",
     "item possède des dates de validité (i_rec_start_date / i_rec_end_date) : la catégorie retenue est celle "
     "de la ligne item jointe, pas forcément celle en vigueur au moment de la vente. Le CA ne dit rien de la marge.",
     "Calculable"],

    ["K03", "Part du CA par canal",
     "Direction commerciale", "Q2",
     "Poids du web et du magasin dans le CA total.",
     "part_web = SUM(ws_net_paid) / (SUM(ss_net_paid) + SUM(ws_net_paid)) ; part_magasin = 1 - part_web",
     "%",
     "Magasin + web. " + PERIODE,
     "Mensuelle",
     "store_sales.ss_net_paid ; web_sales.ws_net_paid",
     "Aucun canal catalogue dans le kit (pas de catalog_sales).",
     "Pour la vue « clients » de Q2 : ss_customer_sk et ws_bill_customer_sk pointent vers customer sans orphelin "
     "(Étape D) ; 14 916 clients achètent sur les deux canaux. Le CA web est hors frais de port.",
     "Calculable"],

    ["K04", "Nombre de transactions",
     "Direction commerciale, Responsable de magasin", "Q2, Q3",
     "Nombre de passages en caisse (magasin) ou de commandes (web). Une transaction regroupe plusieurs lignes de vente.",
     "Magasin : COUNT(DISTINCT ss_ticket_number) ; Web : COUNT(DISTINCT ws_order_number)",
     "Nombre de transactions",
     "Par canal, par magasin, par période. " + PERIODE,
     "Quotidienne",
     "store_sales.ss_ticket_number ; web_sales.ws_order_number",
     "Aucune (0 nul).",
     "Un ticket et une commande web ne sont pas la même notion : à comparer avec prudence. Ne pas compter les "
     "lignes (667 579 lignes magasin pour 89 100 tickets). Chaque ticket est rattaché à un seul magasin (vérifié).",
     "Calculable"],

    ["K05", "Panier moyen",
     "Direction commerciale, Responsable de magasin", "Q2, Q3",
     "Montant moyen dépensé par transaction.",
     "Panier moyen = K01 / K04 (calculé séparément par canal)",
     "Unité monétaire par transaction",
     "Par canal et par magasin. " + PERIODE,
     "Mensuelle",
     "store_sales.ss_net_paid, ss_ticket_number ; web_sales.ws_net_paid, ws_order_number",
     "Aucune pour le calcul.",
     "Mélanger magasin et web dans un seul panier moyen n'a pas de sens (notions de transaction différentes). "
     "Sensible aux très gros paniers : compléter avec la médiane.",
     "Calculable"],

    ["K06", "Quantités vendues",
     "Direction commerciale, Responsable de magasin", "Q1, Q3",
     "Nombre d'unités de produits vendues.",
     "SUM(ss_quantity) + SUM(ws_quantity)",
     "Unités",
     "Magasin + web, par produit / catégorie / magasin. " + PERIODE,
     "Quotidienne",
     "store_sales.ss_quantity ; web_sales.ws_quantity",
     "Unité de vente du produit (i_units) non exploitée : additionner des unités hétérogènes.",
     "Aucune quantité <= 0 observée. Retours non déduits.",
     "Calculable"],

    ["K07", "Taux de remise",
     "Direction commerciale", "Q1",
     "Part du prix catalogue abandonnée sous forme de remise.",
     "Taux = SUM(ext_discount_amt) / SUM(ext_list_price) (par canal)",
     "%",
     "Magasin + web. " + PERIODE,
     "Mensuelle",
     "store_sales.ss_ext_discount_amt, ss_ext_list_price ; web_sales.ws_ext_discount_amt, ws_ext_list_price",
     "Lien avec les promotions (ss_promo_sk) non exploité : table promotion hors périmètre.",
     "ext_discount_amt = ext_list_price - ext_sales_price (vérifié sur 100 % des lignes). Les coupons "
     "(coupon_amt) sont une réduction distincte, non incluse dans ce taux.",
     "Calculable"],

    ["K08", "Évolution du CA (N vs N-1)",
     "Direction commerciale, Responsable de magasin", "Q1, Q3",
     "Variation du CA d'une période par rapport à la même période de l'année précédente.",
     "Évol = (CA_période - CA_même période N-1) / CA_même période N-1 ; jointure date_dim sur sold_date_sk",
     "%",
     "Par mois, comparaisons possibles de 2002 à 2005. " + PERIODE,
     "Mensuelle",
     "store_sales / web_sales (sold_date_sk, net_paid) ; date_dim.d_date_sk, d_year, d_moy",
     "Pas de données avant 2001 : pas d'évolution calculable pour 2001.",
     "Sans data_refresh/, décembre 2005 s'arrête le 13 et la comparaison avec décembre 2004 est faussée. "
     "Une évolution "
     "ne dit rien de sa cause. Données synthétiques : saisonnalité non représentative.",
     "Calculable avec réserve"],

    ["K09", "CA par magasin et classement",
     "Responsable de magasin, Direction commerciale", "Q3",
     "CA net de chaque magasin et son rang dans le réseau.",
     "CA_mag = SUM(ss_net_paid) GROUP BY ss_store_sk ; rang = RANK() par CA_mag décroissant ; "
     "jointure store ON ss_store_sk = s_store_sk",
     "Unité monétaire, rang",
     "12 magasins, ventes magasin uniquement. " + PERIODE,
     "Mensuelle",
     "store_sales.ss_store_sk, ss_net_paid ; store.s_store_sk, s_store_name, s_floor_space",
     "Surface utilisable pour un CA/m² (s_floor_space) : qualité non vérifiée.",
     "Un magasin plus grand vend mécaniquement plus : compléter par K04, K05 et CA/m². s_closed_date_sk est "
     "renseignée pour les 12 magasins (1917 à 2141) et 5 magasins « fermés » avant 2001 vendent en 2001-2005 : "
     "colonne inutilisable pour exclure des magasins (voir inventaire_sources.xlsx).",
     "Calculable"],

    ["K10", "CA moyen par jour de la semaine",
     "Responsable de magasin", "Q4",
     "CA moyen réalisé un lundi, un mardi, etc.",
     "CA_jour = SUM(ss_net_paid) GROUP BY d_day_name / nombre de dates de ce jour dans la période "
     "(jointure date_dim ON ss_sold_date_sk = d_date_sk)",
     "Unité monétaire par jour",
     "Ventes magasin, par magasin ou réseau. " + PERIODE,
     "Hebdomadaire",
     "store_sales.ss_sold_date_sk, ss_net_paid, ss_store_sk ; date_dim.d_date_sk, d_day_name",
     "Horaires d'ouverture par jour non disponibles (s_hours est global).",
     "Diviser par le nombre de jours de chaque type, sinon un jour plus fréquent dans la période paraît meilleur. "
     "Les jours fériés ne peuvent pas être isolés : d_holiday vaut Y pour 100 % des jours (inutilisable). Données synthétiques : profil hebdomadaire possiblement uniforme.",
     "Calculable"],

    ["K11", "Nombre de produits en rupture",
     "Responsable des stocks", "Q5",
     "Nombre de couples (produit, entrepôt) dont le stock est à zéro au dernier relevé.",
     "COUNT(*) WHERE inv_quantity_on_hand = 0 AND inv_date_sk = MAX(inv_date_sk) ; détail par inv_warehouse_sk",
     "Nombre de couples (produit, entrepôt)",
     "5 entrepôts, relevé hebdomadaire de 90 000 couples. Dernier relevé complet : 26/12/2005 dans "
     "data_refresh/ (106 couples à 0, 31 vides).",
     "Hebdomadaire (rythme des relevés)",
     "inventory.inv_date_sk, inv_item_sk, inv_warehouse_sk, inv_quantity_on_hand ; item (libellés)",
     "Pas de stock magasin (inventory n'a pas de colonne magasin). 180 produits du stock sont absents de "
     "data/item et présents dans data_refresh/item.",
     "Une quantité vide (NULL) n'est pas une rupture : la compter à part. Une rupture ne dit pas s'il y a "
     "une demande pour ce produit (croiser avec K06). Relevé hebdomadaire : une rupture de quelques jours peut échapper. "
     "Le relevé du 12/12/2005 est réparti entre data/ (35 100 lignes) et data_refresh/ (54 900) : sans les deux "
     "dossiers, le « dernier relevé » est incomplet.",
     "Calculable avec réserve"],

    ["K12", "Stock disponible par entrepôt",
     "Responsable des stocks", "Q6",
     "Nombre total d'unités en stock dans chaque entrepôt au dernier relevé.",
     "SUM(inv_quantity_on_hand) WHERE inv_date_sk = MAX(inv_date_sk) GROUP BY inv_warehouse_sk",
     "Unités",
     "5 entrepôts, dernier relevé complet (26/12/2005, data_refresh/).",
     "Hebdomadaire",
     "inventory.inv_date_sk, inv_warehouse_sk, inv_quantity_on_hand ; warehouse.w_warehouse_sk, w_warehouse_name, "
     "w_warehouse_sq_ft",
     "Valeur du stock : nécessiterait un prix (i_current_price ou i_wholesale_cost), non retenu ici.",
     "Additionner des relevés de dates différentes n'a pas de sens (stock = photo, pas flux). Des unités de "
     "produits différents ne sont pas comparables. 31 quantités vides au dernier relevé ignorées par SUM. "
     "Répartition quasi uniforme (8,93 à 9,02 millions d'unités par entrepôt) : effet probable de la génération.",
     "Calculable"],
]

HEAD = ["ID", "Nom de l'indicateur", "Profil(s)", "Question(s)", "Définition métier", "Formule",
        "Unité", "Périmètre", "Fréquence de calcul", "Sources nécessaires (table.colonne)",
        "Données manquantes", "Limites d'interprétation", "Calculabilité"]
WIDTHS = [6, 24, 22, 11, 38, 46, 16, 32, 16, 42, 38, 52, 15]

COUVERTURE = [
    ["Question", "Profil", "Priorité", "KPI principal", "KPI complémentaires", "Couverture"],
    ["Q1 - CA total de chaque catégorie de produits", "Direction commerciale", "Indispensable", "K02",
     "K01, K06, K07, K08", "Couverte"],
    ["Q2 - Plus d'achats en magasin ou sur le web ?", "Direction commerciale", "Utile", "K03",
     "K04, K05", "Couverte (CA, transactions ; clients via customer, relation vérifiée)"],
    ["Q3 - Quel magasin vend le plus ?", "Responsable de magasin", "Indispensable", "K09",
     "K04, K05, K08", "Couverte"],
    ["Q4 - Jour de la semaine avec le plus de ventes", "Responsable de magasin", "Utile", "K10",
     "K04", "Couverte"],
    ["Q5 - Produits avec un stock à zéro", "Responsable des stocks", "Indispensable", "K11",
     "K06", "Couverte avec réserve (charger data/ et data_refresh/ : relevés et produits répartis)"],
    ["Q6 - Entrepôt avec le plus de stock", "Responsable des stocks", "Complémentaire", "K12",
     "-", "Couverte (en unités, pas en valeur)"],
]

CONTROLES = [
    ["Contrôle", "Résultat observé", "Statut", "Impact sur les KPI"],
    ["Lignes store_sales / web_sales", "667 579 / 668 052", "Vérifié", "Volume de calcul"],
    ["Valeurs nulles sur les colonnes de ventes utilisées", "0 dans les deux tables", "Vérifié",
     "K01 à K10 calculables sans traitement des nulls"],
    ["Période des ventes", "data/ : 2001-01-01 -> 2005-12-13 ; data_refresh/ : 2005-12-13 -> 2005-12-31 "
     "(transactions 89 100 à 89 999, aucune en commun avec data/)", "Vérifié",
     "Charger les deux dossiers pour une année 2005 complète (K08)"],
    ["ext_sales_price = quantity x sales_price", "100 % des lignes (tolérance 0,01)", "Vérifié", "Cohérence K01 / K06"],
    ["ext_discount_amt = ext_list_price - ext_sales_price", "100 % des lignes", "Vérifié", "Formule K07"],
    ["net_paid = ext_sales_price - coupon_amt", "100 % des lignes", "Vérifié", "Définition du CA (K01)"],
    ["Quantités <= 0 ou net_paid < 0", "0", "Vérifié", "Pas de retours mélangés aux ventes"],
    ["Transactions distinctes", "89 100 tickets magasin ; 89 100 commandes web", "Vérifié", "K04 ; égalité à "
     "noter (jeu synthétique)"],
    ["Doublons (transaction, produit)", "4 136 magasin ; 4 076 web ; 0 doublon de ligne complète", "Vérifié",
     "Lignes distinctes : même ticket, produit, date, heure, client, mais prix et quantités différents (Étape D) "
     "- toutes comptées dans K01"],
    ["Clés de vente sans correspondance (item, store, date_dim)", "0 orphelin", "Vérifié", "Jointures K02, K09, K10"],
    ["item : unicité de i_item_sk, catégories", "17 820 lignes, unique, 9 catégories, 0 nulle", "Vérifié", "K02"],
    ["store", "12 magasins, 12 s_store_id distincts", "Vérifié", "K09"],
    ["inventory : relevés", "23 255 100 lignes ; 259 dates, 1 relevé tous les 7 jours ; 5 entrepôts",
     "Vérifié", "K11, K12 : photo hebdomadaire"],
    ["inventory : quantités vides", "5 999 dans data/ ; 31 au dernier relevé complet", "Vérifié",
     "K11 : compter à part"],
    ["inventory : relevé du 2005-12-12", "Réparti : 35 100 lignes dans data/ + 54 900 dans data_refresh/ = 90 000 "
     "(18 000 produits x 5 entrepôts), aucun couple en double", "Vérifié", "K11, K12 : charger les deux dossiers"],
    ["inventory : dernier relevé complet (2005-12-26, data_refresh/)", "90 000 lignes ; 106 à 0 ; 31 vides ; "
     "1 ligne par (produit, entrepôt)", "Vérifié", "K11, K12 (preuve : controle_inventaire_complet.txt)"],
    ["inventory : produits absents de data/item", "180 (sk 17820 à 17999)", "Vérifié", "K11 : libellés manquants"],
    ["data_refresh/item contient ces 180 produits", "180 lignes, sk 17820 à 17999", "Vérifié",
     "data_refresh complète data (rôle exact : Déduit, à valider)"],
    ["Noms des colonnes", "Identiques à la spécification TPCx-BB v1.7.0, annexe B.2 (fichiers sans en-tête)", "Vérifié",
     "Toutes les formules"],
    ["Devise des montants", "Non documentée", "Non disponible", "Unité de K01, K02, K05, K09, K10"],
]


def style_sheet(ws, widths, status_col=None):
    thin = Side(style="thin", color="9AA9B8")
    for i, w in enumerate(widths, 1):
        ws.column_dimensions[get_column_letter(i)].width = w
    for r, row in enumerate(ws.iter_rows(), 1):
        for c in row:
            c.alignment = Alignment(wrap_text=True, vertical="top")
            c.border = Border(top=thin, bottom=thin, left=thin, right=thin)
            c.font = Font(name="Calibri", size=10)
            if r == 1:
                c.fill = PatternFill("solid", fgColor=NAVY)
                c.font = Font(name="Calibri", size=10, bold=True, color="FFFFFF")
            elif r % 2 == 1:
                c.fill = PatternFill("solid", fgColor=LIGHT)
        if r > 1 and status_col:
            cell = row[status_col - 1]
            for k, color in STATUS_FILL.items():
                if cell.value == k:
                    cell.fill = PatternFill("solid", fgColor=color)
                    cell.font = Font(name="Calibri", size=10, bold=True)
    ws.freeze_panes = "B2" if ws.title == "Dictionnaire_KPI" else "A2"
    ws.auto_filter.ref = ws.dimensions


wb = Workbook()

# --- Lisez-moi
ws = wb.active
ws.title = "Lisez-moi"
readme = [
    ("dictionnaire_KPI.xlsx - Retail Intelligence Platform", True),
    ("UC-01, Étape B - Définir les indicateurs (§5.1.13). Version v1, 16/11/2026.", False),
    ("", False),
    ("Objet", True),
    ("Dictionnaire initial des 12 indicateurs nécessaires aux 6 questions de la fiche de cadrage "
     "(cadrage_metier.pdf). Chaque KPI donne les 9 attributs demandés : nom, définition, formule, unité, "
     "périmètre, fréquence, sources, données manquantes, limites.", False),
    ("", False),
    ("Onglets", True),
    ("Dictionnaire_KPI : une ligne par indicateur.", False),
    ("Couverture_questions : quel KPI répond à quelle question métier.", False),
    ("Controles : faits mesurés sur les fichiers pour fonder les formules (preuve : preuves/controles_kpi.txt).",
     False),
    ("", False),
    ("Conventions", True),
    ("CA = montant net payé (net_paid) : après remises et coupons, hors taxes, hors frais de port, retours non déduits.",
     False),
    ("Calculabilité : Calculable / Calculable avec réserve (calcul possible, limite à signaler) / Non calculable.",
     False),
    ("Statuts des contrôles : Vérifié, Déduit, Hypothèse, Non disponible, À valider (§4.2 du sujet).", False),
    ("Source : archive retail_project.zip, dossier data/ (sauf mention data_refresh/). Jeu synthétique TPCx-BB.",
     False),
]
for text, bold in readme:
    ws.append([text])
    ws.cell(ws.max_row, 1).font = Font(name="Calibri", size=13 if ws.max_row == 1 else 10.5, bold=bold,
                                       color=NAVY if bold else "000000")
    ws.cell(ws.max_row, 1).alignment = Alignment(wrap_text=True, vertical="top")
ws.column_dimensions["A"].width = 120

# --- Dictionnaire
ws = wb.create_sheet("Dictionnaire_KPI")
ws.append(HEAD)
for k in KPIS:
    ws.append(k)
style_sheet(ws, WIDTHS, status_col=len(HEAD))

# --- Couverture
ws = wb.create_sheet("Couverture_questions")
for r in COUVERTURE:
    ws.append(r)
style_sheet(ws, [44, 24, 15, 14, 20, 50])

# --- Contrôles
ws = wb.create_sheet("Controles")
for r in CONTROLES:
    ws.append(r)
style_sheet(ws, [48, 52, 15, 44])

wb.save(OUT)
print(f"Excel généré : {OUT}")
