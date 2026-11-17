"""Génère J1_Retail_Intelligence/02_UC02_architecture/schema_flux.pdf (UC-02, Étape E).

Usage : .venv/bin/python sources/uc02_schema_flux.py
Produit aussi preuves/flux.csv (preuve §5.2.16). Valeurs de référence : preuves/valeurs_reference.txt.
"""
import csv

from reportlab.graphics.shapes import Drawing, String
from reportlab.lib.units import cm
from reportlab.platypus import KeepTogether, PageBreak, Spacer

from chemins import UC02, UC02_PREUVES
from pdf_style import (BLUE, CELL, GREEN, GREY, H2, H3, LIGHT, ORANGE, SUB, TEAL, TITLE, arrow, box, build,
                       link, p, table)

OUT = UC02 / "schema_flux.pdf"
UC02_PREUVES.mkdir(parents=True, exist_ok=True)

story = [
    p("Retail Intelligence Platform", TITLE),
    p("UC-02 &ndash; Schéma et description des flux de données", SUB),
    p("IPSSI &ndash; Mastère Développement, Data &amp; IA &ndash; TP Jour 1", SUB),
    Spacer(1, 8),
    table([
        ["Élément", "Valeur"],
        ["Livrable", "schema_flux.pdf (UC02_schema_flux, §5.2.17)"],
        ["Étape couverte", "Étape E &ndash; Décrire les flux de données (§5.2.13)"],
        ["Date / version", "16/11/2026 &ndash; v1"],
        ["Documents liés", "architecture_cible.pdf (couches, zones, règles Silver, modèle Gold) ; "
                           "positionnement_composants.pdf ; gouvernance.pdf"],
        ["Nature", "Conception logique : les flux ne sont pas encore implémentés (NiFi au Jour 2, Spark au Jour 3)."],
    ], [4, 13]),

    p("1. Principes retenus", H2),
    table([
        ["Principe", "Application"],
        ["Traitement par lots (batch)", "Les sources sont des fichiers livrés par lots (data/, puis data_refresh/) ; "
                                        "aucun besoin temps réel n'est exprimé (section 5)."],
        ["ELT", "Les fichiers sont d'abord déposés tels quels en Bronze, puis transformés dans la plateforme "
                "(Spark) : le brut reste disponible pour rejouer un traitement."],
        ["Un flux = un lot traçable", "Chaque exécution porte un identifiant de lot (data, data_refresh, puis "
                                      "les suivants) repris dans les chemins et dans les colonnes techniques."],
        ["Référentiels avant faits", "Les contrôles d'orphelins des faits supposent des référentiels à jour "
                                     "(section 4)."],
        ["Traitements rejouables", "Relancer un lot réécrit ses seules partitions, sans doublon (idempotence)."],
    ], [4.5, 12.5], size=8),

    p("2. Schéma des flux", H2),
    p("Une ligne par flux d'ingestion (F1 à F4), puis la construction du Gold (F5) et l'exposition (F6). Les "
      "cadres en pointillés indiquent un flux arrêté en Bronze dans cette version."),
    Spacer(1, 4),
]

# ------------------------------------------------------------------ schéma en couloirs
W, H = 17 * cm, 9.6 * cm
d = Drawing(W, H)
cols = ["Sources", "Ingestion", "Bronze", "Silver", "Gold", "Exposition"]
n, gap = 6, 14
bw = (W - 22 - gap * (n - 1)) / n
X = [22 + i * (bw + gap) for i in range(n)]
for x, t in zip(X, cols):
    d.add(String(x + bw / 2, H - 9, t, textAnchor="middle", fontSize=7.5, fontName="Helvetica-Bold", fillColor=TEAL))
ROWS = [
    ("F1", ["Ventes", "store_sales,", "web_sales"], True),
    ("F2", ["Référentiels", "item, store, date_dim,", "customer, warehouse"], True),
    ("F3", ["Stocks", "inventory"], True),
    ("F4", ["Hors périmètre", "retours, clics, avis…"], False),
]
rh, top = 42, H - 26
Y = [top - rh - i * (rh + 8) for i in range(len(ROWS))]
for (fid, src, full), y in zip(ROWS, Y):
    d.add(String(2, y + rh / 2 - 3, fid, fontSize=8, fontName="Helvetica-Bold", fillColor=TEAL))
    box(d, X[0], y, bw, rh, src, fill=LIGHT, size=6.3)
    box(d, X[1], y, bw, rh, ["NiFi", "dépôt + SHA-256", "manifeste"], fill=BLUE, size=6.3)
    box(d, X[2], y, bw, rh, [".dat d'origine", "lot=data", "lot=data_refresh"], fill=ORANGE, size=6.3)
    arrow(d, X[0] + bw, y + rh / 2, X[1])
    arrow(d, X[1] + bw, y + rh / 2, X[2])
    if full:
        sil = {"F1": ["Parquet ventes", "année / mois", "+ quarantaine"],
               "F2": ["Parquet", "référentiels", "nettoyés"],
               "F3": ["Parquet stock", "par relevé", "+ quarantaine"]}[fid]
        box(d, X[3], y, bw, rh, sil, fill=ORANGE, size=6.3)
        arrow(d, X[2] + bw, y + rh / 2, X[3])
    else:
        box(d, X[3], y, bw, rh, ["itération", "suivante"], fill=GREY, dashed=True, size=6.3)
# Gold et exposition couvrant F1 à F3
gy, gh = Y[2], Y[0] + rh - Y[2]
box(d, X[4], gy, bw, gh, ["Gold", "", "dim_* (F2)", "fait_ventes (F1)", "fait_stock (F3)", "", "agrégats KPI"],
    fill=GREEN, size=6.5)
box(d, X[5], gy, bw, gh, ["Exposition", "", "Spark SQL", "outil BI", "", "K01 à K12", "3 profils métier"],
    fill=GREEN, size=6.5)
for y in Y[:3]:
    arrow(d, X[3] + bw, y + rh / 2, X[4])
d.add(String(X[2] + bw + gap / 2, Y[0] + rh + 4, "Spark", textAnchor="middle", fontSize=6.5,
             fontName="Helvetica-Bold", fillColor=TEAL))
d.add(String(X[3] + bw + gap / 2, Y[0] + rh + 4, "F5", textAnchor="middle", fontSize=7, fontName="Helvetica-Bold",
             fillColor=TEAL))
arrow(d, X[4] + bw, gy + gh / 2, X[5], "F6")
story += [d, Spacer(1, 2),
          p("Ordre d'exécution : F2 (référentiels) puis F1 et F3 (faits), puis F5 (Gold) et F6 (exposition). "
            "F4 ne fait que déposer les fichiers en Bronze.", CELL)]

# ------------------------------------------------------------------ fiches flux (8 attributs)
story += [p("3. Description de chaque flux (8 attributs demandés)", H2),
          p("Volumes mesurés à l'UC-01 (inventaire_sources.xlsx, preuves/valeurs_reference.txt). Les processeurs "
            "NiFi cités sont indicatifs : le flux réel sera conçu au Jour 2.")]

ATTR = ["1. Source", "2. Format d'entrée", "3. Mécanisme d'ingestion", "4. Zone de destination",
        "5. Contrôles à effectuer", "6. Transformations envisagées", "7. Résultat attendu", "8. Consommateur final"]
FLUX = [
    ("F1 &ndash; Ventes magasin et web", "Batch, par lot", [
        "store_sales.dat et web_sales.dat, dans data/ et data_refresh/ (674 211 et 674 931 lignes au total)",
        ".dat texte délimité « | », sans en-tête, UTF-8 ; 23 et 34 champs ; 93 Mo et 134 Mo (data/)",
        "NiFi : lecture du dossier du lot (ListFile / FetchFile), empreinte SHA-256 (CryptographicHashContent), "
        "dépôt (PutHDFS) avec l'attribut de lot ; manifeste du lot",
        "Bronze : bronze/tpcx_bb/store_sales|web_sales/lot=…/ ; puis Silver : silver/ventes/…/annee=/mois=/",
        "Ingestion : empreinte et nombre de fichiers attendus. Silver : nombre de champs, types, quantité &gt; 0, "
        "net_paid = ext_sales_price - coupon_amt, une seule date, un seul client et un seul magasin par ticket, "
        "clés présentes dans les référentiels (sinon quarantaine)",
        "Typage ; concaténation des lots ; ajout de _lot, _fichier_source, _date_ingestion, _id_ligne et canal ; "
        "PAS de dédoublonnage des lignes (transaction, produit)",
        "Parquet Silver partitionné par année et mois de vente ; alimente fait_ventes (F5)",
        "Direction commerciale (Q1, Q2) et responsables de magasin (Q3, Q4)"]),
    ("F2 &ndash; Référentiels", "Batch, par lot ; exécuté en premier", [
        "item (data/ + data_refresh/ : 17 820 + 180), store (12), date_dim (109 573), customer (99 000 + 1 000), "
        "warehouse (5)",
        ".dat texte délimité « | », sans en-tête",
        "NiFi, même chaîne que F1",
        "Bronze : bronze/tpcx_bb/&lt;table&gt;/lot=…/ ; puis Silver : silver/referentiels/&lt;table&gt;/",
        "Unicité des clés *_sk (vérifiée à l'UC-01), nombre de champs, types ; aucune clé commune entre lots "
        "(sinon règle de mise à jour)",
        "Fusion des deux fichiers item et customer ; rognage des espaces (i_item_desc) ; d_holiday et "
        "s_closed_date_sk écartés ; données personnelles conservées en Silver à accès restreint",
        "Parquet Silver par table ; alimente les dimensions dim_* (F5)",
        "Tous les profils, à travers les dimensions ; équipe Data"]),
    ("F3 &ndash; Stocks", "Batch, un lot par livraison de relevés", [
        "inventory.dat dans data/ et data_refresh/ (23 255 100 + 234 900 = 23 490 000 lignes)",
        ".dat texte délimité « | », 4 champs ; 425 Mo (data/)",
        "NiFi, même chaîne que F1",
        "Bronze : bronze/tpcx_bb/inventory/lot=…/ ; puis Silver : silver/stocks/inventory/releve=…/",
        "Unicité (date, produit, entrepôt) ; relevé complet = 90 000 lignes (18 000 produits x 5 entrepôts) ; "
        "total attendu = 261 relevés x 90 000 = 23 490 000 lignes ; produits et entrepôts présents dans les "
        "référentiels",
        "Typage ; regroupement par relevé quel que soit le lot d'origine (le relevé du 12/12/2005 est réparti "
        "entre les deux) ; ajout de est_vide (quantité vide, jamais remplacée par 0) et est_rupture",
        "Parquet Silver partitionné par relevé ; alimente fait_stock (F5)",
        "Responsable des stocks (Q5, Q6)"]),
    ("F4 &ndash; Domaines hors périmètre", "Batch, dépôt seul", [
        "store_returns, web_returns, reason, web_clickstreams, web_page, product_reviews, promotion, "
        "item_marketprices et son CSV d'audit, customer_address, customer_demographics, household_demographics, "
        "income_band, time_dim, ship_mode, web_site",
        ".dat (« | ») ; .csv multi-sections pour l'audit",
        "NiFi, même chaîne que F1",
        "Bronze uniquement (le CSV d'audit dans bronze/tpcx_bb/_audit_generation/)",
        "Empreinte, nombre de fichiers, nombre de champs par ligne",
        "Aucune dans cette version",
        "Données conservées et documentées pour les itérations suivantes (retours, navigation, avis)",
        "Équipe Data"]),
    ("F5 &ndash; Construction du Gold", "Batch, après F1 à F3", [
        "Tables Silver du périmètre",
        "Parquet typé",
        "Traitement Spark / PySpark (pas d'ingestion externe)",
        "Gold : gold/dimensionnel/ et gold/kpi/",
        "Réconciliation : somme de ca_net et nombre de lignes identiques entre Silver et Gold ; 90 000 tickets et "
        "90 000 commandes ; unicité de id_ligne ; nombre de lignes rattachées aux membres -1 / -2 ; jointures "
        "sans perte",
        "Construction des dimensions puis des faits ; union magasin + web avec la colonne canal ; "
        "id_transaction = canal + numéro ; calcul des agrégats K01 à K12",
        "Modèle en étoile (2 faits, 5 dimensions) et agrégats KPI en Parquet",
        "Flux F6"]),
    ("F6 &ndash; Exposition des indicateurs", "Batch, à la demande ou après F5", [
        "Tables Gold",
        "Parquet",
        "Lecture par Spark SQL, puis par l'outil BI retenu (à choisir ; Synapse en étude)",
        "Tableaux de bord et requêtes (pas de stockage supplémentaire)",
        "Droits en lecture seule ; date du dernier lot affichée ; contrôle de quelques valeurs de référence "
        "(nombre de transactions par canal)",
        "Filtres et agrégations à la demande ; aucune modification des données",
        "KPI K01 à K12 répondant aux questions Q1 à Q6",
        "Direction commerciale, responsables de magasin, responsable des stocks"]),
]
for title, mode, vals in FLUX:
    rows = [[f"<b>Mode</b>", mode]] + [[a, v] for a, v in zip(ATTR, vals)]
    story.append(KeepTogether([p(title, H3), table(rows, [4, 13], header=False, size=7.5), Spacer(1, 5)]))

with open(UC02_PREUVES / "flux.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh, delimiter=";")
    w.writerow(["Flux", "Mode"] + ATTR)
    for title, mode, vals in FLUX:
        w.writerow([title.replace("&ndash;", "-"), mode] + [v.replace("&gt;", ">").replace("&lt;", "<") for v in vals])

# ------------------------------------------------------------------ ordonnancement et reprise
story += [
    p("4. Ordonnancement, contrôles bloquants et reprise sur erreur", H2),
    table([
        ["Étape", "Dépend de", "Contrôle bloquant (le lot n'est pas publié)", "Contrôle non bloquant (signalé)"],
        ["F2 Référentiels", "Dépôt Bronze", "Empreinte différente ; clé *_sk en double", "Texte rogné, colonnes écartées"],
        ["F1 Ventes", "F2", "Nombre de champs incorrect sur tout le fichier ; formule net_paid fausse",
         "Lignes orphelines ou invalides mises en quarantaine"],
        ["F3 Stocks", "F2", "Relevé incomplet (différent de 90 000 lignes) ; clé composite en double",
         "Quantités vides (comptées à part)"],
        ["F5 Gold", "F1, F2, F3", "Écart de réconciliation Silver / Gold", "Part de membres -2 « inconnu » en hausse"],
        ["F6 Exposition", "F5", "-", "Date du dernier lot ancienne"],
    ], [3, 2.2, 6.2, 5.6], size=7.5),
    Spacer(1, 4),
    p("<b>Reprise :</b> chaque lot est rejoué depuis Bronze (jamais modifié). Le traitement réécrit uniquement les "
      "partitions du lot concerné, ce qui évite les doublons. Les lignes en quarantaine sont conservées avec leur "
      "motif pour analyse. Le journal d'exécution (lot, durée, lignes lues / écrites / rejetées) est conservé dans "
      "_journaux/."),

    p("5. Batch ou continu ?", H2),
    table([
        ["Flux", "Mode retenu", "Justification", "Continu envisageable ?"],
        ["F1 Ventes", "Batch", "Fichiers livrés par lots ; KPI consultés à la semaine ou au mois",
         "Oui en production (tickets de caisse au fil de l'eau), sans besoin exprimé aujourd'hui"],
        ["F2 Référentiels", "Batch", "Changements rares (12 magasins, 5 entrepôts)", "Non utile"],
        ["F3 Stocks", "Batch", "Relevés hebdomadaires par nature", "Non : la source est une photo hebdomadaire"],
        ["F4 Clics (web_clickstreams)", "Batch (dépôt)", "Fichier historique, hors périmètre",
         "Oui si un flux de clics en direct apparaît (NiFi + Spark Structured Streaming, à étudier)"],
        ["F5, F6", "Batch", "Dépendent de lots complets", "Non"],
    ], [3.2, 2.2, 5.6, 6], size=7.5),
    p("Conclusion : tous les flux sont traités en batch. Le continu n'est pas justifié par un besoin métier "
      "actuel ; il reste une évolution possible pour les ventes et les clics.", CELL),

    p("6. Volumétrie des flux", H2),
    table([
        ["Flux", "Fichiers", "Lignes (data/ + data_refresh/)", "Taille (data/ + data_refresh/)"],
        ["F1", "4", "674 211 (magasin) ; 674 931 (web)", "229 Mo"],
        ["F2", "7", "17 820 + 180 (item) ; 99 000 + 1 000 (customer) ; 109 573 (date_dim) ; 12 ; 5", "36 Mo"],
        ["F3", "2", "23 490 000", "429 Mo"],
        ["F4", "23", "dont 6 839 538 clics (6 770 550 + 68 988)", "340 Mo"],
        ["Total", "36", "-", "1 034 Mo (0,96 Go en unités binaires)"],
    ], [1.5, 1.8, 8.7, 5], size=7.5),
    p("Tailles arrondies au Mo (10<super>6</super> octets) à partir de inventaire_fichiers.csv.", CELL),

    p("7. Hypothèses", H2),
    table([
        ["Point", "Statut"],
        ["Les futurs lots arriveront sous la même forme que data_refresh/ (mêmes fichiers, nouvelles clés)", "Hypothèse"],
        ["Les processeurs NiFi cités conviennent ; la conception détaillée est faite au Jour 2", "Hypothèse"],
        ["Si NiFi ou HDFS ne peuvent pas être installés, un script Python de dépôt documenté sert de repli "
         "(slide 51 : « obligatoire, avec repli documenté »)", "Déduit"],
    ], [13.5, 3.5], size=7.5),
]

build(OUT, story, "UC02 - Schéma des flux", "Retail Intelligence Platform - UC-02 Schéma des flux")
