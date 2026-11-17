"""Génère J1_Retail_Intelligence/02_UC02_architecture/architecture_cible.pdf (UC-02, Étape C).

Usage : .venv/bin/python sources/uc02_architecture_cible.py
Produit aussi preuves/zones_donnees.csv et preuves/modele_gold.csv (preuves §5.2.16).
"""
import csv

from reportlab.graphics.shapes import Drawing, String
from reportlab.lib.units import cm
from reportlab.platypus import KeepTogether, PageBreak, Spacer

from chemins import UC02, UC02_PREUVES
from pdf_style import (BLUE, CELL, GREEN, GREY, H2, H3, LIGHT, NAVY, ORANGE, SUB, TEAL, TITLE, arrow,
                       box, build, link, p, table)

OUT = UC02 / "architecture_cible.pdf"
UC02_PREUVES.mkdir(parents=True, exist_ok=True)


def save_csv(name, rows):
    with open(UC02_PREUVES / name, "w", newline="", encoding="utf-8") as fh:
        csv.writer(fh, delimiter=";").writerows(rows)


story = [
    p("Retail Intelligence Platform", TITLE),
    p("UC-02 &ndash; Architecture logique cible", SUB),
    p("IPSSI &ndash; Mastère Développement, Data &amp; IA &ndash; TP Jour 1", SUB),
    Spacer(1, 8),
    table([
        ["Élément", "Valeur"],
        ["Livrable", "architecture_cible.pdf (UC02_architecture_cible, §5.2.17)"],
        ["Étape couverte", "Étape C &ndash; Concevoir une architecture logique (§5.2.13) ; schéma attendu au §5.2.12"],
        ["Date / version", "16/11/2026 &ndash; v1"],
        ["Choix d'origine", "Data Lake en zones Bronze / Silver / Gold, Parquet, modèle en étoile en Gold "
                            "(comparaison_architectures.pdf, section 5)"],
        ["Nature", "Conception logique : rien n'est déployé au Jour 1. Stockage prévu : HDFS en local (Jour 2), "
                   "ADLS Gen2 en cible cloud (Jour 4)."],
    ], [4, 13]),
    p("1. Vue d'ensemble", H2),
    p("Le schéma présente les sept couches demandées (§5.2.13 C) de gauche à droite, avec sous chaque couche la "
      "principale règle de qualité ou de traçabilité, et en bas la supervision et la gouvernance qui s'appliquent "
      "à toutes les couches."),
    Spacer(1, 4),
]

# ------------------------------------------------------------------ schéma des couches
W, H = 17 * cm, 9.4 * cm
d = Drawing(W, H)
n, gap = 6, 12.4
bw = (W - gap * (n - 1)) / n
X = [i * (bw + gap) for i in range(n)]
HEAD = [["Sources"], ["Ingestion"], ["Stockage brut"], ["Préparation", "et contrôle"],
        ["Stockage", "analytique"], ["Exposition", "des indicateurs"]]
for x, lines in zip(X, HEAD):
    for k, t in enumerate(lines):
        d.add(String(x + bw / 2, H - 9 - k * 8, t, textAnchor="middle", fontSize=7, fontName="Helvetica-Bold",
                     fillColor=TEAL))
MAIN = [
    (["Sources", "TPCx-BB :", "data/ (23 tables)", "data_refresh/ (11)", ".dat « | », 0,96 Go", "",
      "Complémentaires :", "aucune fournie"], LIGHT),
    (["Ingestion", "NiFi (batch)", "dépôt par lot", "manifeste", "+ SHA-256", "", "repli documenté :", "script Python"],
     BLUE),
    (["Bronze", "brut immuable", "36 fichiers", "tels quels,", "par table et lot", "(CSV d'audit inclus)"], ORANGE),
    (["Silver", "Parquet typé", "nettoyé, contrôlé", "data + data_refresh", "fusionnés", "+ quarantaine"], ORANGE),
    (["Gold", "Parquet", "étoile :", "2 faits,", "5 dimensions", "+ agrégats KPI"], GREEN),
    (["Exposition", "KPI K01 à K12", "Spark SQL", "outil BI", "(à choisir)", "3 profils métier"], GREEN),
]
YM, HM = 118, 120
for x, (lines, fill) in zip(X, MAIN):
    box(d, x, YM, bw, HM, lines, fill=fill, size=6.8)
for i in range(n - 1):
    arrow(d, X[i] + bw, YM + HM / 2, X[i + 1])
    if i in (2, 3):  # traitements Spark : Bronze -> Silver, Silver -> Gold
        d.add(String(X[i] + bw + gap / 2, YM + HM + 3, "Spark", textAnchor="middle", fontSize=6.5,
                     fontName="Helvetica-Bold", fillColor=TEAL))
RULES = [["Origine documentée", "(nom, empreinte)"], ["Contrôle : nb fichiers,", "taille, empreinte"],
         ["Écriture unique,", "jamais modifié"], ["Nb champs, types,", "unicité, orphelins,", "règles métier"],
         ["Réconciliation", "des totaux Silver", "/ Gold, grain fixé"], ["Lecture seule,", "données clients", "masquées"]]
for x, lines in zip(X, RULES):
    box(d, x, 66, bw, 42, lines, fill=LIGHT, dashed=True, bold_first=False, size=6)
d.add(String(0, 112, "Règles de qualité et de traçabilité", fontSize=6, fillColor=TEAL, fontName="Helvetica-Oblique"))
box(d, 0, 12, W, 42, ["Supervision et gouvernance (toutes les couches)",
                      "Catalogue des tables et colonnes · manifestes de lots · journaux d'exécution NiFi / Spark · "
                      "rapport de contrôle par exécution",
                      "Droits par zone et par profil · protection des données personnelles · durées de conservation · "
                      "suivi des volumes et des coûts"], fill=GREY, size=6.5)
story += [d, Spacer(1, 2),
          p("Les flèches indiquent le sens des données. « Spark » désigne les traitements de préparation (Bronze vers "
            "Silver) et de modélisation (Silver vers Gold). Le détail des flux est dans schema_flux.pdf, celui des "
            "composants dans positionnement_composants.pdf.", CELL)]

# ------------------------------------------------------------------ rôle des couches
COUCHES = [
    ["Couche", "Rôle", "Contenu", "Format", "Composant (local / cloud)"],
    ["Sources", "Fournir les données", "Archive retail_project.zip : data/ et data_refresh/. Aucune donnée "
                                       "complémentaire fournie ; une zone séparée est prévue si besoin (§3.6).",
     ".dat, .csv", "Système de fichiers"],
    ["Ingestion", "Déposer chaque lot sans le modifier et en garder la trace", "Copie des fichiers, calcul de "
                                                                              "l'empreinte, manifeste du lot",
     "inchangé", "NiFi / Azure Data Factory (étude)"],
    ["Stockage brut (Bronze)", "Conserver les données reçues et leur provenance", "Les 36 fichiers, y compris les "
                                                                                  "domaines hors périmètre",
     ".dat, .csv", "HDFS / ADLS Gen2"],
    ["Préparation et contrôle (Silver)", "Typer, nettoyer, contrôler, harmoniser", "Tables du périmètre en Parquet, "
                                                                                    "quarantaine des lignes rejetées",
     "Parquet", "Spark / PySpark"],
    ["Stockage analytique (Gold)", "Organiser les données pour les KPI", "Modèle en étoile et agrégats",
     "Parquet", "Spark / PySpark ; HDFS / ADLS Gen2"],
    ["Exposition", "Mettre les indicateurs à disposition des métiers", "Requêtes et tableaux de bord K01 à K12",
     "-", "Spark SQL ; outil BI à choisir (Synapse en étude)"],
    ["Supervision et gouvernance", "Rendre la plateforme traçable, sûre et maîtrisée", "Catalogue, journaux, "
                                                                                       "droits, contrôles, coûts",
     "-", "Voir gouvernance.pdf"],
]
story += [p("2. Rôle de chaque couche", H2), table(COUCHES, [3.2, 3.6, 5.2, 1.6, 3.4], size=7.5)]

# ------------------------------------------------------------------ organisation des zones
story += [
    p("3. Organisation des zones", H2),
    p("La même arborescence est utilisée en local (HDFS) et dans le cloud (ADLS Gen2, un conteneur par zone), "
      "ce qui facilite la déclinaison du Jour 4."),
    Spacer(1, 3),
    table([
        ["Chemin", "Contenu"],
        ["/datalake/bronze/tpcx_bb/&lt;table&gt;/lot=&lt;data|data_refresh&gt;/date_ingestion=AAAA-MM-JJ/",
         "Fichier .dat d'origine, non modifié"],
        ["/datalake/bronze/tpcx_bb/_audit_generation/lot=.../", "item_marketprices_audit.csv (rapport du générateur, "
                                                                "pas une table)"],
        ["/datalake/bronze/_manifestes/", "Un manifeste par lot : fichiers, tailles, lignes, SHA-256, date"],
        ["/datalake/bronze/complementaire/&lt;source&gt;/", "Données complémentaires éventuelles, jamais mélangées "
                                                            "à TPCx-BB (vide aujourd'hui)"],
        ["/datalake/silver/&lt;domaine&gt;/&lt;table&gt;/annee=AAAA/mois=MM/", "Parquet typé et contrôlé ; "
                                                                              "partitionné par date pour les faits"],
        ["/datalake/silver/_quarantaine/&lt;table&gt;/", "Lignes rejetées avec motif"],
        ["/datalake/gold/dimensionnel/&lt;fait_ou_dim&gt;/", "Modèle en étoile"],
        ["/datalake/gold/kpi/&lt;indicateur&gt;/", "Agrégats prêts pour les tableaux de bord"],
        ["/datalake/_catalogue/ , /datalake/_journaux/", "Métadonnées et journaux d'exécution"],
    ], [8.6, 8.4], size=7.5),
]

ZONES = [
    ["Zone", "Rôle dans Retail Intelligence", "Entrée", "Sortie", "Règles"],
    ["Bronze", "Conserver chaque lot reçu, tel quel, avec sa provenance", "Archive retail_project.zip (36 fichiers)",
     ".dat et .csv d'origine, rangés par table et par lot", "Écriture unique ; aucune modification ; empreinte "
                                                             "SHA-256 comparée à checksum.txt ; accès équipe Data"],
    ["Silver", "Rendre les données fiables et homogènes", "Bronze, tables du périmètre : store_sales, web_sales, "
                                                          "inventory, item, store, date_dim, warehouse, customer",
     "Parquet typé, nettoyé, data et data_refresh fusionnés ; quarantaine", "Règles de la section 4 ; colonnes "
                                                                            "techniques de traçabilité ; accès équipe Data"],
    ["Gold", "Servir les 12 KPI et les 6 questions métier", "Silver", "Modèle en étoile + agrégats KPI",
     "Grain documenté ; réconciliation des totaux avec Silver ; données personnelles exclues ; lecture métier"],
]
story += [Spacer(1, 6), p("Synthèse des zones", H3), table(ZONES, [1.6, 3.6, 4, 3.8, 4], size=7.5)]
save_csv("zones_donnees.csv", ZONES)

# ------------------------------------------------------------------ Silver : nettoyage
story += [
    p("4. Préparation et contrôle : règles de la zone Silver", H2),
    p("Les règles viennent directement des anomalies mesurées dans l'UC-01 (qualification_donnees.pdf, "
      "inventaire_sources.xlsx). Principes : le brut reste intact en Bronze, aucune correction n'est silencieuse, "
      "aucune valeur n'est inventée (§5.1.19)."),
    Spacer(1, 3),
    table([
        ["Action", "Règle", "Tables", "Constat UC-01 (Vérifié)"],
        ["Typer", "Clés *_sk en entier acceptant le vide ; dates texte en type date ; Y/N en booléen ; codes postaux "
                  "en texte", "Toutes", "Clés lues en décimal dès qu'un vide existe ; d_date et i_rec_start_date en texte"],
        ["Contrôler la structure", "Nombre de champs par ligne = schéma, sinon quarantaine", "Toutes",
         "100 % conforme aujourd'hui : la règle protège les prochains lots"],
        ["Fusionner les lots", "Concaténer data/ et data_refresh/ ; dédoublonner sur la clé si un recouvrement apparaît",
         "Ventes, stocks, item, customer", "Aucun recouvrement ; 180 produits et une partie des relevés de stock "
                                           "uniquement dans data_refresh/"],
        ["Décoder et rogner le texte", "Entités HTML converties en caractères ; espaces de début et fin supprimés",
         "item (et product_reviews plus tard)", "2 575 descriptions avec espaces ; 14 864 avis avec entités HTML"],
        ["Dédoublonner", "Supprimer les lignes entièrement identiques", "web_clickstreams (itération suivante)",
         "83 doublons complets (+1 dans data_refresh/)"],
        ["Ne PAS dédoublonner", "Garder les lignes (transaction, produit) répétées : ventes distinctes",
         "store_sales, web_sales", "Prix et quantités différents dans 4 038 et 3 991 groupes"],
        ["Neutraliser", "Valeur sentinelle remplacée par vide + indicateur « inconnu » ; colonne incohérente "
                        "écartée du modèle", "household_demographics, store, date_dim",
         "hd_vehicle_count = -1 ; s_closed_date_sk incohérente ; d_holiday = Y pour tous les jours"],
        ["Garder le vide", "Un stock vide reste vide (indicateur est_vide), jamais remplacé par 0", "inventory",
         "5 999 quantités vides dans data/"],
        ["Contrôler les relations", "Toute clé étrangère sans correspondance va en quarantaine", "Faits",
         "0 orphelin aujourd'hui (avec les deux dossiers item)"],
        ["Ajouter la traçabilité", "Colonnes _lot, _fichier_source, _date_ingestion, _id_ligne", "Toutes",
         "Pas de numéro de ligne dans les ventes"],
    ], [2.6, 5.4, 3.4, 5.6], size=7.3),
    Spacer(1, 3),
    p("Les règles sur les retours (118 retours supérieurs à la quantité vendue, délais de plus d'un an) seront "
      "ajoutées quand ce domaine entrera dans le périmètre.", CELL),
]

# ------------------------------------------------------------------ Gold : modèle
story += [p("5. Stockage analytique : modèle dimensionnel en Gold", H2),
          p("Modèle en étoile (slides 24-28) : deux tables de faits partagent les dimensions date et produit. Choix "
            "de l'étoile plutôt que du flocon : référentiels peu profonds, reporting simple pour des profils métier, "
            "moins de jointures.")]

W2, H2_ = 17 * cm, 8.8 * cm
d2 = Drawing(W2, H2_)
fw, fh, dw, dh = 104, 42, 100, 32
F = {"fait_ventes": (118, 112), "fait_stock": (262, 112)}
D = {"dim_date": (191, 205), "dim_produit": (191, 18), "dim_magasin": (0, 178), "dim_client": (0, 52),
     "dim_entrepot": (W2 - dw, 117)}
box(d2, *F["fait_ventes"], fw, fh, ["fait_ventes", "1 ligne = 1 ligne de vente", "magasin + web"], fill=BLUE, size=6.5)
box(d2, *F["fait_stock"], fw, fh, ["fait_stock", "1 ligne = produit x entrepôt", "x relevé hebdomadaire"],
    fill=BLUE, size=6.5)
for k, (x, y) in D.items():
    box(d2, x, y, dw, dh, k, fill=GREEN, size=7)


def mid(b, side, w, h):
    x, y = b
    return {"l": (x, y + h / 2), "r": (x + w, y + h / 2), "t": (x + w / 2, y + h), "b": (x + w / 2, y)}[side]


fv, fs = F["fait_ventes"], F["fait_stock"]
for a, sa, b_, sb in [(fv, "l", D["dim_magasin"], "r"), (fv, "l", D["dim_client"], "r"), (fv, "t", D["dim_date"], "b"),
                      (fv, "b", D["dim_produit"], "t"), (fs, "t", D["dim_date"], "b"), (fs, "b", D["dim_produit"], "t"),
                      (fs, "r", D["dim_entrepot"], "l")]:
    link(d2, *mid(a, sa, fw, fh), *mid(b_, sb, dw, dh))
story += [Spacer(1, 4), d2,
          p("Non dessiné pour la lisibilité : fait_ventes est aussi relié à dim_entrepot pour les ventes web "
            "(ws_warehouse_sk).", CELL), Spacer(1, 4)]

GOLD = [
    ["Table", "Colonne Gold", "Source Silver (magasin / web)", "Remarque"],
    ["fait_ventes", "id_ligne", "_id_ligne", "Clé technique (pas de numéro de ligne dans la source)"],
    ["", "canal", "« MAGASIN » / « WEB »", "Permet Q2 et K03"],
    ["", "id_transaction", "canal + ss_ticket_number / ws_order_number", "Canal inclus : les numéros des deux canaux "
                                                                         "se recouvrent (0 à 89 999)"],
    ["", "date_key", "ss_sold_date_sk / ws_sold_date_sk", "vers dim_date"],
    ["", "produit_key", "ss_item_sk / ws_item_sk", "vers dim_produit"],
    ["", "magasin_key", "ss_store_sk / -1", "-1 = « non applicable » pour le web"],
    ["", "client_key", "ss_customer_sk / ws_bill_customer_sk", "vers dim_client"],
    ["", "entrepot_key", "-1 / ws_warehouse_sk (vide -> -2)", "-2 = « inconnu » (158 vides)"],
    ["", "quantite", "ss_quantity / ws_quantity", "K06"],
    ["", "montant_catalogue", "ss_ext_list_price / ws_ext_list_price", "Base du taux de remise (K07)"],
    ["", "remise", "ss_ext_discount_amt / ws_ext_discount_amt", "K07"],
    ["", "coupon", "ss_coupon_amt / ws_coupon_amt", "Réduction distincte de la remise"],
    ["", "ca_net", "ss_net_paid / ws_net_paid", "CA hors taxes, hors frais de port, retours non déduits (K01)"],
    ["fait_stock", "date_key, produit_key, entrepot_key", "inv_date_sk, inv_item_sk, inv_warehouse_sk",
     "Clé composite unique (vérifiée)"],
    ["", "quantite", "inv_quantity_on_hand", "Peut être vide"],
    ["", "est_vide, est_rupture", "quantité vide ; quantité = 0", "K11 ; une photo ne s'additionne pas dans le temps"],
    ["dim_date", "date_key, date, annee, trimestre, mois, jour_semaine, nom_jour, est_weekend",
     "d_date_sk, d_date, d_year, d_qoy, d_moy, d_dow, d_day_name, d_weekend", "d_holiday exclu (Y pour tous les jours)"],
    ["dim_produit", "produit_key, code, libelle, categorie, classe, marque, prix_courant",
     "i_item_sk, i_item_id, i_product_name, i_category, i_class, i_brand, i_current_price",
     "data/ + data_refresh/ (18 000 produits) ; libellés synthétiques illisibles"],
    ["dim_magasin", "magasin_key, nom, ville, etat, surface", "s_store_sk, s_store_name, s_city, s_state, s_floor_space",
     "s_closed_date_sk exclue (incohérente)"],
    ["dim_client", "client_key, annee_naissance, pays_naissance, client_prefere",
     "c_customer_sk, c_birth_year, c_birth_country, c_preferred_cust_flag",
     "Nom, e-mail, login exclus (minimisation des données personnelles)"],
    ["dim_entrepot", "entrepot_key, nom, etat, surface", "w_warehouse_sk, w_warehouse_name, w_state, w_warehouse_sq_ft",
     "5 entrepôts"],
    ["Toutes les dimensions", "Lignes -1 « Non applicable » et -2 « Inconnu »", "-", "Évite les clés vides dans les faits"],
]
story += [p("5.1 Colonnes du modèle et correspondance avec les sources", H3),
          table(GOLD, [2.3, 4.6, 5.2, 4.9], size=7)]
save_csv("modele_gold.csv", GOLD)

story += [
    Spacer(1, 5),
    p("5.2 Choix de modélisation", H3),
    table([
        ["Choix", "Justification"],
        ["Une seule table fait_ventes avec une colonne canal", "Q2 compare les canaux ; les mesures communes "
                                                               "(net_paid, quantité, remise) suivent les mêmes formules "
                                                               "dans les deux tables (vérifié à 100 %). Les colonnes propres "
                                                               "au web (frais de port, date d'expédition) restent en Silver."],
        ["Grain = ligne de vente", "C'est le grain réel des fichiers (UC-01) ; les transactions s'obtiennent par "
                                   "COUNT(DISTINCT id_transaction), jamais en comptant des lignes."],
        ["fait_stock séparé", "Grain et nature différents (photo hebdomadaire, non additive dans le temps)."],
        ["Agrégats KPI en plus de l'étoile", "Tableaux de bord rapides ; mais les mesures non additives (transactions, "
                                             "panier moyen, stock) sont recalculées depuis les faits, pas sommées entre "
                                             "agrégats."],
    ], [5, 12], size=7.5),
]

# ------------------------------------------------------------------ couverture des besoins
story += [
    p("6. Correspondance avec les besoins métier", H2),
    table([
        ["Question (UC-01)", "KPI", "Tables Gold utilisées"],
        ["Q1 CA par catégorie", "K02", "fait_ventes x dim_produit (categorie)"],
        ["Q2 Magasin ou web", "K03, K04, K05", "fait_ventes (canal) x dim_client"],
        ["Q3 Magasin le plus performant", "K09", "fait_ventes x dim_magasin (canal = MAGASIN)"],
        ["Q4 Jour de semaine le plus actif", "K10", "fait_ventes x dim_date (nom_jour)"],
        ["Q5 Produits en rupture", "K11", "fait_stock (dernier relevé complet, est_rupture) x dim_produit x dim_entrepot"],
        ["Q6 Stock par entrepôt", "K12", "fait_stock (dernier relevé complet) x dim_entrepot"],
    ], [4.5, 2.5, 10], size=7.5),
    p("Les six questions et les douze KPI sont servis par le Gold, sans retour aux fichiers bruts.", CELL),

    p("7. Hors périmètre de cette version et évolutions", H2),
    table([
        ["Élément", "Traitement aujourd'hui", "Évolution prévue"],
        ["Retours, clics, avis, promotions, prix concurrents", "Conservés en Bronze", "Silver puis fait_retours, "
                                                                                     "fait_clics en Gold"],
        ["Traitement en continu", "Non retenu (lots de fichiers statiques)", "Possible pour les clics si un flux "
                                                                            "en direct apparaît"],
        ["Couche de tables (Delta Lake)", "Non retenue (facultative)", "Si des mises à jour incrémentales fréquentes "
                                                                      "apparaissent"],
        ["Données complémentaires (§3.6)", "Zone bronze/complementaire/ prévue, vide", "Silver séparé, jointure "
                                                                                       "documentée avec TPCx-BB"],
    ], [5, 5.5, 6.5], size=7.5),

    p("8. Hypothèses et limites", H2),
    table([
        ["Point", "Statut"],
        ["L'outil de restitution BI n'est pas choisi (Synapse et Power BI sont des options d'étude)", "À valider"],
        ["Les libellés produit et marque sont des chaînes aléatoires : tableaux de bord peu lisibles sans "
         "correspondance externe", "Vérifié"],
        ["Le partitionnement par année et mois suppose que les analyses filtrent surtout par période", "Hypothèse"],
        ["Les volumes futurs ne sont pas connus ; la conception vaut pour le volume actuel et une croissance "
         "modérée", "Hypothèse"],
    ], [13.5, 3.5], size=7.5),
]

build(OUT, story, "UC02 - Architecture cible", "Retail Intelligence Platform - UC-02 Architecture cible")
