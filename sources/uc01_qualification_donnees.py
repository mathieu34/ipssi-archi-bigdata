"""Génère J1_Retail_Intelligence/01_UC01_besoin_exploration/qualification_donnees.pdf (UC-01, Étape D).

Prérequis : profilage_sources.py et relations_qualite.py exécutés (CSV dans preuves/).
Usage : .venv/bin/python sources/uc01_qualification_donnees.py
"""
from pathlib import Path

import pandas as pd
from reportlab.graphics.shapes import Drawing
from reportlab.lib.units import cm
from reportlab.platypus import KeepTogether, PageBreak, Spacer

from chemins import UC01, UC01_PREUVES
from pdf_style import (BLUE, CELL, GREEN, GREY, H2, H3, LIGHT, SUB, TITLE, box, build, link, p,
                       table)

PREUVES = UC01_PREUVES
OUT = UC01 / "qualification_donnees.pdf"

rel = pd.read_csv(PREUVES / "relations.csv")


def n(x):
    return f"{int(x):,}".replace(",", " ")


story = [
    p("Retail Intelligence Platform", TITLE),
    p("UC-01 &ndash; Qualification des données et des relations possibles", SUB),
    p("IPSSI &ndash; Mastère Développement, Data &amp; IA &ndash; TP Jour 1", SUB),
    Spacer(1, 8),
    table([
        ["Élément", "Valeur"],
        ["Livrable", "qualification_donnees.pdf (livrable 5 du dossier UC-01, §5.1.17)"],
        ["Étapes couvertes", "Étape C (qualité des fichiers) et Étape D &ndash; Vérifier les relations possibles"],
        ["Date / version", "16/11/2026 &ndash; v1"],
        ["Données", "Archive retail_project.zip, dossiers data/ et data_refresh/ (36 fichiers, 0,96 Go)"],
        ["Preuves", "preuves/relations.csv, controles_relations.txt, controle_inventaire_complet.txt, "
                    "controle_store_fermeture.txt, inventaire_colonnes.csv ; scripts dans sources/"],
    ], [4, 13]),

    p("1. Méthode", H2),
    p("La qualité est évaluée selon cinq dimensions, mesurées par script sur la totalité des lignes "
      "(pas d'échantillonnage) :"),
    Spacer(1, 3),
    table([
        ["Dimension", "Question posée", "Mesure"],
        ["Complétude", "Les champs utiles sont-ils renseignés ?", "Nombre et % de valeurs vides par colonne"],
        ["Unicité", "La clé identifie-t-elle une seule ligne ?", "Doublons sur la clé simple ou composite"],
        ["Validité", "Les valeurs ont-elles le bon type et une plage plausible ?",
         "Type observé, min / max, valeurs négatives, formats de date"],
        ["Cohérence", "Les tables se rejoignent-elles et les règles métier sont-elles respectées ?",
         "Orphelins, cardinalité, formules de montants, ordre des dates"],
        ["Couverture", "Quelle période et quel périmètre sont couverts ?", "Dates min / max, répartition "
                                                                           "data/ et data_refresh/"],
    ], [3, 7, 7]),
    Spacer(1, 4),
    p("Pour chaque relation candidate (§4.3 du sujet), on vérifie : présence de la colonne des deux côtés, "
      "type, unicité de la clé parente, cardinalité, valeurs nulles et valeurs sans correspondance (orphelins). "
      "Une relation est dite <b>Vérifiée</b> si la clé parente est unique et qu'il n'y a aucun orphelin."),

    p("2. Synthèse de la qualité des tables du périmètre", H2),
    table([
        ["Table", "Lignes (data + refresh)", "Complétude", "Unicité", "Validité / cohérence", "Appréciation"],
        ["store_sales", "667 579 + 6 632", "0 nul sur les colonnes de mesure ; < 0,07 % sur 4 clés secondaires",
         "(ticket, produit) non unique : 4 136 cas, lignes distinctes", "Montants cohérents à 100 % ; 1 date, "
         "1 client, 1 magasin par ticket", "Bonne"],
        ["web_sales", "668 052 + 6 879", "0 nul sur les mesures ; < 0,08 % sur 11 clés secondaires",
         "(commande, produit) non unique : 4 076 cas, lignes distinctes", "Montants cohérents à 100 % ; 1 date, "
         "1 client par commande", "Bonne"],
        ["item", "17 820 + 180", "i_size 14 % vide, i_units 4,8 % ; i_rec_end_date 100 % vide",
         "i_item_sk unique", "9 catégories ; prix 0,10 à 99,98", "Bonne avec réserves"],
        ["store", "12", "s_rec_end_date 100 % vide", "s_store_sk unique",
         "s_closed_date_sk incohérente (1917 à 2141)", "Bonne avec réserves"],
        ["date_dim", "109 573", "0 nul", "d_date_sk unique", "1900-01-01 à 2199-12-31", "Bonne"],
        ["inventory", "23 255 100 + 234 900", "inv_quantity_on_hand : 5 999 vides (0,026 %)",
         "(date, produit, entrepôt) unique", "Quantités 0 à 1 000 ; relevés tous les 7 jours",
         "Bonne avec réserves"],
        ["warehouse", "5", "0 nul", "w_warehouse_sk unique", "-", "Bonne"],
    ], [2.3, 2.5, 3.6, 3, 3.6, 2]),
    Spacer(1, 3),
    p("Les autres tables (clients, retours, navigation, avis, promotions) sont qualifiées dans "
      "inventaire_sources.xlsx (onglets Fichiers et Anomalies).", CELL),
]

# ------------------------------------------------------------------ 3. relations
story.append(p("3. Relations vérifiées", H2))
story.append(p("Résultats mesurés (relations.csv). « Orph. » = valeurs de l'enfant absentes du parent dans data/ ; "
               "« avec refresh » = parent complété par data_refresh/."))
story.append(Spacer(1, 3))

PERIM = rel[~rel.usage.str.contains("hors périmètre") | rel.enfant.str.startswith("inventory")]
OTHER = rel.drop(PERIM.index)


def rel_table(df):
    rows = [["Enfant", "Parent", "Types", "Nulls enfant", "Orph.", "Orph. + refresh", "Card.", "Statut"]]
    for r in df.itertuples():
        statut = r.statut.replace("Vérifié (avec data_refresh/)", "Vérifié avec refresh")
        rows.append([r.enfant, r.parent, f"{r.type_enfant} / {r.type_parent}", f"{n(r.nulls_enfant)} ({r.pct_nulls} %)",
                     n(r.orphelins), n(r.orphelins_avec_refresh), r.cardinalite, statut])
    return table(rows, [4.3, 3.9, 2.3, 2.0, 1.1, 1.2, 0.9, 1.3], size=6.8)


story += [p("3.1 Relations utilisées par les questions Q1 à Q6 et les KPI", H3), rel_table(PERIM),
          Spacer(1, 4),
          p(f"3.2 Autres relations testées : {len(OTHER)} relations des domaines hors périmètre (clients, retours, "
            "navigation, avis, promotions, prix concurrents), toutes sans orphelin ; détail dans "
            "preuves/relations.csv.", CELL), Spacer(1, 3),
          p("Lecture : toutes les relations testées sont sans orphelin, à une exception près : "
            "inventory.inv_item_sk a 232 380 lignes orphelines tant que seul data/item est chargé "
            "(180 produits), et 0 avec data_refresh/item. Les relations vers web_sales.ws_order_number sont "
            "marquées Hypothèse car ws_order_number n'est pas unique (une commande = plusieurs lignes) : "
            "voir 4.5.", CELL)]

# ------------------------------------------------------------------ 4. analyses ciblées
story.append(p("4. Analyses ciblées", H2))
ANALYSES = [
    ("4.1 Grain des tables de vente et doublons (transaction, produit)", [
        ["Constat", "store_sales : 8 174 lignes réparties en 4 038 groupes ayant le même (ss_ticket_number, "
                    "ss_item_sk), jusqu'à 4 lignes par groupe. web_sales : 8 067 lignes, 3 991 groupes."],
        ["Analyse", "Dans chaque groupe, date, heure, client, adresse et magasin sont identiques ; quantité, prix, "
                    "remise et montant diffèrent dans presque tous les groupes. Aucune ligne n'est un doublon complet."],
        ["Conclusion", "<b>Déduit</b> : ce sont des lignes de vente distinctes (même produit passé plusieurs fois "
                       "sur un ticket, à des prix différents), pas des copies. Il manque un numéro de ligne : la clé "
                       "naturelle d'une ligne de vente n'existe pas dans les fichiers."],
        ["Décision", "Conserver toutes les lignes. Le grain des tables de vente est la ligne de vente. Une "
                     "transaction = un ss_ticket_number (magasin) ou un ws_order_number (web)."],
    ]),
    ("4.2 Cohérence des transactions", [
        ["Constat", "Sur 89 100 tickets : 0 ticket avec plusieurs dates, 0 avec plusieurs clients, 0 avec plusieurs "
                    "magasins. Sur 89 100 commandes web : 0 avec plusieurs dates ou plusieurs clients."],
        ["Conclusion", "<b>Vérifié</b> : un ticket ou une commande est une entité cohérente ; K04 et K05 peuvent "
                       "être calculés de façon fiable."],
    ]),
    ("4.3 Retours et ventes", [
        ["Constat", "store_returns : 98,94 % des retours retrouvent leur vente sur (ticket, produit), 100 % sur le "
                    "seul ticket. web_returns : 99,05 % et 100 %."],
        ["Délais", "Délai retour - vente : médiane 356 jours (magasin) et 421 jours (web), maximum 715 et 835 jours, "
                   "aucun délai négatif. 64 retours magasin et 54 retours web dépassent la quantité vendue."],
        ["Conclusion", "<b>Vérifié</b> : la relation retour -> vente existe sur (transaction, produit). Les délais "
                       "sont irréalistes pour un commerce (jeu synthétique) : les retours ne doivent pas être "
                       "rattachés au mois de la vente sans précaution. Domaine hors périmètre de cette itération."],
    ]),
    ("4.4 data/ et data_refresh/", [
        ["Référentiels", "customer, customer_address, item, item_marketprices, product_reviews : 0 clé commune "
                         "avec data/ (que des nouvelles lignes)."],
        ["Ventes", "Transactions 0 à 89 099 dans data/, 89 100 à 89 999 dans data_refresh/ : aucune en commun. "
                   "Le 13/12/2005 est réparti (285 lignes magasin dans data/, 96 dans data_refresh/), sans ligne "
                   "identique."],
        ["Stocks", "Un relevé complet compte 90 000 lignes (18 000 produits x 5 entrepôts). Le relevé du 12/12/2005 "
                   "est réparti (35 100 + 54 900, aucun couple commun) ; ceux du 19/12 et du 26/12 ne sont que dans "
                   "data_refresh/."],
        ["Conclusion", "<b>Déduit</b> : data_refresh/ est un chargement incrémental qui prolonge data/ jusqu'au "
                       "31/12/2005. Il faut concaténer les deux dossiers ; aucun dédoublonnage n'est nécessaire."],
    ]),
    ("4.5 Clics web et ventes", [
        ["Constat", "9,9 % des clics (668 052 sur 6 770 550) ont un wcs_sales_sk. Ce nombre est exactement celui des "
                    "lignes de web_sales."],
        ["Analyse", "(wcs_sales_sk, wcs_item_sk) correspond à (ws_order_number, ws_item_sk) pour 100 % de ces clics ; "
                    "même date et même client dans 100 % des cas."],
        ["Conclusion", "<b>Vérifié</b> sur la clé composite : wcs_sales_sk désigne la commande web. Les 90,1 % "
                       "restants sont des clics sans achat. Aucune colonne ne donne le type d'événement (vue, panier)."],
    ]),
    ("4.6 Stocks et entrepôts", [
        ["Constat", "w_warehouse_sk, inv_warehouse_sk et ws_warehouse_sk prennent les mêmes valeurs 0 à 4."],
        ["Conclusion", "<b>Vérifié</b> : relation inventory -> warehouse N:1 sans orphelin. Pas de colonne magasin "
                       "dans inventory : le stock en magasin n'est pas disponible (<b>Non disponible</b>)."],
    ]),
    ("4.7 Clients des deux canaux", [
        ["Constat", "37 336 clients magasin, 37 367 clients web, 14 916 communs, sur 99 000 clients du référentiel."],
        ["Conclusion", "<b>Vérifié</b> : ss_customer_sk et ws_bill_customer_sk désignent le même référentiel "
                       "customer. La question Q2 peut être traitée par client."],
    ]),
    ("4.8 Date de fermeture des magasins", [
        ["Constat", "s_closed_date_sk est renseignée pour les 12 magasins, de 1917 à 2141. 5 magasins « fermés » "
                    "avant 2001 réalisent entre 54 574 et 56 040 lignes de vente en 2001-2005."],
        ["Conclusion", "<b>Vérifié</b> : colonne incohérente avec les ventes, inutilisable pour filtrer les magasins."],
    ]),
]
for title, rows in ANALYSES:
    story.append(KeepTogether([p(title, H3), table(rows, [3, 14], header=False), Spacer(1, 4)]))

# ------------------------------------------------------------------ 5. schéma relationnel
story += [p("5. Modèle relationnel observé (périmètre)", H2),
          p("Tables de faits au centre, référentiels autour. Traits pleins : relations vérifiées (0 orphelin). "
            "Cadres gris pointillés : tables présentes mais hors périmètre. Chaque relation est N:1 (plusieurs "
            "lignes de faits pour une ligne de référentiel).")]

W, H = 17 * cm, 12 * cm
d = Drawing(W, H)
bw, bh = 120, 34
XL, XC, XR = 10, W / 2 - bw / 2, W - 10 - bw
YT, YM, YB = 215, 120, 25
FACTS = {"store_sales": (XL, YM), "web_sales": (XC, YM), "inventory": (XR, YM)}
DIMS = {"store": (XL, YT), "date_dim": (XC, YT), "warehouse": (XR, YT),
        "customer": (XL, YB), "item": (XC, YB)}
SUB_LBL = {"store_sales": "fait - ligne de vente", "web_sales": "fait - ligne de vente",
           "inventory": "fait - relevé hebdomadaire", "item": "data/ + data_refresh/"}
for k, (x, y) in FACTS.items():
    box(d, x, y, bw, bh, [k, SUB_LBL[k]], fill=BLUE)
for k, (x, y) in DIMS.items():
    box(d, x, y, bw, bh, [k, SUB_LBL.get(k, "référentiel")], fill=GREEN)


def top(pt):
    return pt[0] + bw / 2, pt[1] + bh


def bottom(pt):
    return pt[0] + bw / 2, pt[1]


for f_, d_ in [("store_sales", "store"), ("store_sales", "date_dim"), ("web_sales", "date_dim"),
               ("inventory", "date_dim"), ("inventory", "warehouse")]:
    link(d, *top(FACTS[f_]), *bottom(DIMS[d_]))
for f_, d_ in [("store_sales", "customer"), ("web_sales", "customer"), ("store_sales", "item"),
               ("web_sales", "item"), ("inventory", "item")]:
    link(d, *bottom(FACTS[f_]), *top(DIMS[d_]))
# tables présentes hors périmètre (sans lien dessiné)
gw = (W - 20 - 3 * 8) / 4
for i, (a, b) in enumerate([("store_returns", "-> store_sales (98,9 %)"), ("web_returns", "-> web_sales (99,1 %)"),
                            ("web_clickstreams", "-> web_sales (9,9 % des clics)"),
                            ("customer_demographics, ...", "-> customer")]):
    box(d, 10 + i * (gw + 8), H - 32, gw, 26, [a, b], fill=GREY, dashed=True, size=6.5)
story.append(d)
story.append(p("Bandeau gris : tables présentes, relations vérifiées, hors périmètre de cette itération.", CELL))
story.append(Spacer(1, 4))
story.append(table([
    ["Fait", "Référentiel", "Jointure (enfant = parent)", "Cardinalité", "Statut"],
    ["store_sales", "date_dim / store / item / customer", "ss_sold_date_sk = d_date_sk ; ss_store_sk = s_store_sk ; "
     "ss_item_sk = i_item_sk ; ss_customer_sk = c_customer_sk", "N:1", "Vérifié"],
    ["web_sales", "date_dim / item / customer", "ws_sold_date_sk = d_date_sk ; ws_item_sk = i_item_sk ; "
     "ws_bill_customer_sk = c_customer_sk", "N:1", "Vérifié"],
    ["inventory", "date_dim / item / warehouse", "inv_date_sk = d_date_sk ; inv_item_sk = i_item_sk (data/ + "
     "data_refresh/) ; inv_warehouse_sk = w_warehouse_sk", "N:1", "Vérifié"],
], [2.3, 3.7, 7.6, 1.7, 1.7]))

# ------------------------------------------------------------------ 6. à confirmer
story += [
    p("6. Relations et points restant à confirmer", H2),
    table([
        ["Point", "Statut", "Action proposée"],
        ["product_reviews.pr_order_sk -> web_sales.ws_order_number : 0 orphelin, mais signification non "
         "documentée (commande web ou tout canal ?)", "Hypothèse", "Vérifier la cohérence produit / client "
                                                                   "avant usage"],
        ["Pas d'identifiant de ligne unique dans store_sales, web_sales et web_clickstreams",
         "Vérifié", "Générer une clé technique (id_ligne) en Silver"],
        ["Délais de retour de 1 à 2 ans et retours supérieurs à la quantité vendue (118 cas)", "Vérifié (anomalie)",
         "Signaler comme limite du jeu synthétique ; contrôle de qualité en Silver"],
        ["Noms et ordre des colonnes (fichiers sans en-tête)", "Vérifié",
         "Identiques à la spécification TPCx-BB v1.7.0, annexe B.2 (23 tables sur 23)"],
        ["Signification de hd_vehicle_count = -1", "Hypothèse (valeur inconnue)", "À valider"],
        ["Rôle des fichiers item_marketprices_audit.csv", "À valider", "Ne pas charger comme table"],
    ], [8.5, 3, 5.5]),
]

build(OUT, story, "UC01 - Qualification des données", "Retail Intelligence Platform - UC-01 Qualification des données")
