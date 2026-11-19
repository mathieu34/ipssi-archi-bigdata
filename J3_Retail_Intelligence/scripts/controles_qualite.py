"""Controles qualite des jeux produits (TP Jour 3, UC-06, etape 9, §4.12).

Controle les zones Silver et Gold (et non les sources) selon les familles du §4.12.2 :
completude, unicite, validite des types, coherence des valeurs, volumes,
cles candidates et integrite referentielle.

Chaque controle produit : famille, jeu, regle, resultat, statut.
  OK        : la regle est respectee
  ANOMALIE  : la regle n'est pas respectee (a corriger)
  A SIGNALER: ecart connu et documente, sans impact sur Q3 (limite a garder en tete)

Resultats : affiches, et ecrits dans preuves/qualite/resultats_controles.csv
Documentation : docs/08_rapport_qualite.md

Execution (apres nettoyage.py et transformations.py) :
    python J3_Retail_Intelligence/scripts/controles_qualite.py
"""
import csv
import os
import sys

from pyspark.sql import SparkSession
from pyspark.sql import functions as F

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from nettoyage import DOSSIER_SOURCES, SCHEMA_VENTES  # noqa: E402

RACINE_J3 = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
DOSSIER_SILVER = f"{RACINE_J3}/data/silver"
DOSSIER_GOLD = f"{RACINE_J3}/data/gold"
FICHIER_RESULTATS = f"{RACINE_J3}/preuves/qualite/resultats_controles.csv"

resultats = []


def controle(famille, jeu, regle, resultat, ok, signaler=False):
    statut = "OK" if ok else ("A SIGNALER" if signaler else "ANOMALIE")
    resultats.append({"id": f"C{len(resultats) + 1:02d}", "famille": famille, "jeu": jeu,
                      "regle": regle, "resultat": str(resultat), "statut": statut})


def main():
    spark = SparkSession.builder.appName("TP3-Qualite").master("local[*]").getOrCreate()
    spark.sparkContext.setLogLevel("ERROR")
    print("Version Spark :", spark.version, "\n")

    ventes = spark.read.parquet(f"file://{DOSSIER_SILVER}/store_sales").cache()
    rejets = spark.read.parquet(f"file://{DOSSIER_SILVER}/store_sales_rejets")
    magasins = spark.read.parquet(f"file://{DOSSIER_SILVER}/store").cache()
    dates = spark.read.parquet(f"file://{DOSSIER_SILVER}/date_dim").cache()
    gold = spark.read.parquet(f"file://{DOSSIER_GOLD}/q3_ca_magasin_annee").cache()
    nb_ventes = ventes.count()

    # ---------------- 1. Completude ----------------
    obligatoires = ["ss_store_sk", "ss_ticket_number", "ss_item_sk",
                    "ss_sold_date_sk", "ss_quantity", "ss_net_paid"]
    nuls = ventes.select([F.sum(F.col(c).isNull().cast("int")).alias(c) for c in obligatoires]).first()
    total_nuls = sum(nuls)
    controle("Completude", "silver/store_sales", "Champs obligatoires de Q3 non nuls (" + ", ".join(obligatoires) + ")",
             f"{total_nuls} valeur(s) nulle(s)", total_nuls == 0)

    facultatifs = ["ss_cdemo_sk", "ss_hdemo_sk", "ss_addr_sk", "ss_promo_sk"]
    nuls_fac = ventes.select([F.sum(F.col(c).isNull().cast("int")).alias(c) for c in facultatifs]).first().asDict()
    max_pct = max(nuls_fac.values()) / nb_ventes * 100
    controle("Completude", "silver/store_sales", "Liens facultatifs : taux de nulls < 1 % (regle R6 : conserves)",
             ", ".join(f"{c}={n}" for c, n in nuls_fac.items()) + f" (max {max_pct:.3f} %)", max_pct < 1)

    nuls_mag = magasins.select([F.sum(F.col(c).isNull().cast("int")).alias(c)
                                for c in ["s_store_sk", "s_store_id", "s_store_name", "s_city", "s_state"]]).first()
    controle("Completude", "silver/store", "Identifiant, nom et localisation renseignes",
             f"{sum(nuls_mag)} valeur(s) nulle(s)", sum(nuls_mag) == 0)

    nuls_gold = gold.select([F.sum(F.col(c).isNull().cast("int")).alias(c)
                             for c in ["annee", "ss_store_sk", "s_store_name", "ca_net",
                                       "nb_transactions", "panier_moyen", "rang_annee"]]).first()
    controle("Completude", "gold/q3_ca_magasin_annee", "Aucune valeur nulle sur les dimensions et mesures",
             f"{sum(nuls_gold)} valeur(s) nulle(s)", sum(nuls_gold) == 0)

    # ---------------- 2. Unicite / cles candidates ----------------
    def unicite(df, cles, jeu):
        n, d = df.count(), df.select(cles).distinct().count()
        controle("Unicite", jeu, f"Cle candidate ({', '.join(cles)}) unique", f"{d} distinct(s) / {n} ligne(s)", n == d)

    unicite(magasins, ["s_store_sk"], "silver/store")
    unicite(magasins, ["s_store_id"], "silver/store")
    unicite(dates, ["d_date_sk"], "silver/date_dim")
    unicite(gold, ["annee", "ss_store_sk"], "gold/q3_ca_magasin_annee")

    colonnes_donnees = [nom for nom, _ in SCHEMA_VENTES]
    doublons = nb_ventes - ventes.select(colonnes_donnees).distinct().count()
    controle("Unicite", "silver/store_sales", "Aucun doublon strict (23 colonnes identiques)",
             f"{doublons} doublon(s)", doublons == 0)

    tickets_ambigus = (ventes.groupBy("ss_ticket_number")
                       .agg(F.countDistinct("ss_store_sk").alias("m"), F.countDistinct("ss_sold_date_sk").alias("j"),
                            F.countDistinct("ss_sold_time_sk").alias("h"), F.countDistinct("ss_customer_sk").alias("c"))
                       .filter((F.col("m") > 1) | (F.col("j") > 1) | (F.col("h") > 1) | (F.col("c") > 1))
                       .count())
    controle("Unicite", "silver/store_sales",
             "Un ticket = un seul passage en caisse (1 magasin, 1 jour, 1 heure, 1 client)",
             f"{tickets_ambigus} ticket(s) ambigu(s)", tickets_ambigus == 0)

    # ---------------- 3. Validite des types ----------------
    attendus = {
        "silver/store_sales": (ventes, {"ss_store_sk": "int", "ss_ticket_number": "int", "ss_quantity": "int",
                                        "ss_sold_date_sk": "int", "ss_net_paid": "decimal(7,2)",
                                        "ss_ext_sales_price": "decimal(7,2)", "lot_source": "string"}),
        "silver/store": (magasins, {"s_store_sk": "int", "s_store_name": "string",
                                    "s_rec_start_date": "date", "s_rec_end_date": "date"}),
        "silver/date_dim": (dates, {"d_date_sk": "int", "d_date": "date", "d_year": "int"}),
        "gold/q3_ca_magasin_annee": (gold, {"annee": "int", "ca_net": "decimal(17,2)",
                                            "nb_transactions": "bigint", "panier_moyen": "decimal(18,2)",
                                            "rang_annee": "int"}),
    }
    for jeu, (df, types) in attendus.items():
        reels = dict(df.dtypes)
        ecarts = {c: reels.get(c) for c, t in types.items() if reels.get(c) != t}
        controle("Validite", jeu, "Types attendus : " + ", ".join(f"{c}={t}" for c, t in types.items()),
                 f"{len(ecarts)} ecart(s) {ecarts if ecarts else ''}".strip(), not ecarts)

    # ---------------- 4. Coherence des valeurs ----------------
    hors_domaine = ventes.filter((F.col("ss_quantity") < 1) | (F.col("ss_quantity") > 100)).count()
    controle("Coherence", "silver/store_sales", "ss_quantity entre 1 et 100", f"{hors_domaine} ligne(s) hors domaine",
             hors_domaine == 0)

    negatifs = ventes.filter(F.col("ss_net_paid") < 0).count()
    controle("Coherence", "silver/store_sales", "ss_net_paid >= 0", f"{negatifs} ligne(s) negative(s)", negatifs == 0)

    calc_ext = ventes.filter(F.abs(F.col("ss_ext_sales_price") - F.col("ss_quantity") * F.col("ss_sales_price")) > 0.01).count()
    controle("Coherence", "silver/store_sales", "ss_ext_sales_price = ss_quantity x ss_sales_price (+/- 0,01)",
             f"{calc_ext} ecart(s)", calc_ext == 0)

    calc_net = ventes.filter(F.abs(F.col("ss_net_paid") - (F.col("ss_ext_sales_price") - F.col("ss_coupon_amt"))) > 0.01).count()
    controle("Coherence", "silver/store_sales", "ss_net_paid = ss_ext_sales_price - ss_coupon_amt (+/- 0,01)",
             f"{calc_net} ecart(s)", calc_net == 0)

    periode = ventes.join(dates, ventes.ss_sold_date_sk == dates.d_date_sk) \
        .agg(F.min("d_date").alias("debut"), F.max("d_date").alias("fin")).first()
    controle("Coherence", "silver/store_sales", "Ventes comprises entre le 01/01/2001 et le 31/12/2005",
             f"du {periode['debut']} au {periode['fin']}",
             str(periode["debut"]) >= "2001-01-01" and str(periode["fin"]) <= "2005-12-31")

    panier_ecart = gold.filter(F.abs(F.col("panier_moyen") - F.col("ca_net") / F.col("nb_transactions")) > 0.01).count()
    controle("Coherence", "gold/q3_ca_magasin_annee", "panier_moyen = ca_net / nb_transactions (+/- 0,01)",
             f"{panier_ecart} ecart(s)", panier_ecart == 0)

    rangs_ko = gold.groupBy("annee").agg(F.min("rang_annee").alias("mn"), F.max("rang_annee").alias("mx"),
                                         F.count("*").alias("n")) \
        .filter((F.col("mn") != 1) | (F.col("mx") != 12) | (F.col("n") != 12)).count()
    controle("Coherence", "gold/q3_ca_magasin_annee", "Chaque annee : 12 magasins classes de 1 a 12",
             f"{rangs_ko} annee(s) incoherente(s)", rangs_ko == 0)

    fermes_avant = magasins.join(dates, magasins.s_closed_date_sk == dates.d_date_sk, "left") \
        .filter(F.col("d_date") < F.lit("2001-01-01")).count()
    controle("Coherence", "silver/store", "Aucun magasin ferme avant le debut de ses ventes (s_closed_date_sk)",
             f"{fermes_avant} magasin(s) 'fermes' avant 2001 mais avec des ventes 2001-2005 (regle R18)",
             fermes_avant == 0, signaler=True)

    # ---------------- 5. Volumes ----------------
    lignes_sources = sum(
        spark.read.text(f"file://{DOSSIER_SOURCES}/{lot}/store_sales/store_sales.dat").count()
        for lot in ("data", "data_refresh"))
    nb_rejets = rejets.count()
    controle("Volume", "silver/store_sales", "Lignes Silver + rejets = lignes des fichiers sources",
             f"{nb_ventes} + {nb_rejets} = {nb_ventes + nb_rejets} / sources : {lignes_sources}",
             nb_ventes + nb_rejets == lignes_sources)

    par_lot = {r["lot_source"]: r["count"] for r in ventes.groupBy("lot_source").count().collect()}
    controle("Volume", "silver/store_sales", "Les deux lots sont presents (data et data_refresh)",
             str(par_lot), set(par_lot) == {"data", "data_refresh"})

    controle("Volume", "silver/store", "12 magasins", f"{magasins.count()} ligne(s)", magasins.count() == 12)

    controle("Volume", "gold/q3_ca_magasin_annee", "12 magasins x 5 annees = 60 lignes",
             f"{gold.count()} ligne(s)", gold.count() == 60)

    annees_vol = {r["annee"]: r["n"] for r in gold.groupBy("annee").agg(F.sum("nb_lignes_vente").alias("n")).collect()}
    ecart_max = (max(annees_vol.values()) - min(annees_vol.values())) / min(annees_vol.values()) * 100
    controle("Volume", "gold/q3_ca_magasin_annee", "Volumes annuels comparables (ecart < 5 % : pas d'annee tronquee)",
             f"lignes de vente par annee {dict(sorted(annees_vol.items()))}, ecart max {ecart_max:.1f} %",
             ecart_max < 5)

    # ---------------- 6. Integrite referentielle ----------------
    orph_mag = ventes.join(magasins, ventes.ss_store_sk == magasins.s_store_sk, "left_anti").count()
    controle("Integrite", "silver/store_sales -> silver/store", "Tout ss_store_sk existe dans s_store_sk",
             f"{orph_mag} vente(s) orpheline(s)", orph_mag == 0)

    orph_date = ventes.join(dates, ventes.ss_sold_date_sk == dates.d_date_sk, "left_anti").count()
    controle("Integrite", "silver/store_sales -> silver/date_dim", "Tout ss_sold_date_sk existe dans d_date_sk",
             f"{orph_date} vente(s) orpheline(s)", orph_date == 0)

    orph_gold = gold.join(magasins, gold.ss_store_sk == magasins.s_store_sk, "left_anti").count()
    controle("Integrite", "gold -> silver/store", "Tout magasin du Gold existe dans store",
             f"{orph_gold} ligne(s) orpheline(s)", orph_gold == 0)

    # ---------------- 7. Coherence Gold / Silver (reconciliation) ----------------
    ca_silver = ventes.agg(F.sum("ss_net_paid")).first()[0]
    ca_gold = gold.agg(F.sum("ca_net")).first()[0]
    controle("Coherence", "gold <-> silver", "Somme ca_net (Gold) = somme ss_net_paid (Silver)",
             f"{ca_gold} / {ca_silver}", ca_gold == ca_silver)

    tickets_silver = ventes.select("ss_ticket_number").distinct().count()
    tickets_gold = gold.agg(F.sum("nb_transactions")).first()[0]
    controle("Coherence", "gold <-> silver", "Somme nb_transactions (Gold) = tickets distincts (Silver)",
             f"{tickets_gold} / {tickets_silver}", tickets_gold == tickets_silver)

    # ---------------- Bilan ----------------
    print(f"{'Id':4} | {'Statut':10} | {'Famille':10} | {'Jeu':36} | Regle -> Resultat")
    print("-" * 130)
    for r in resultats:
        print(f"{r['id']:4} | {r['statut']:10} | {r['famille']:10} | {r['jeu']:36} | {r['regle']} -> {r['resultat']}")
    bilan = {s: sum(r["statut"] == s for r in resultats) for s in ("OK", "A SIGNALER", "ANOMALIE")}
    print(f"\nBILAN : {len(resultats)} controles | " + " | ".join(f"{s} : {n}" for s, n in bilan.items()))

    os.makedirs(os.path.dirname(FICHIER_RESULTATS), exist_ok=True)
    with open(FICHIER_RESULTATS, "w", newline="", encoding="utf-8") as f:
        ecrivain = csv.DictWriter(f, fieldnames=["id", "famille", "jeu", "regle", "resultat", "statut"], delimiter=";")
        ecrivain.writeheader()
        ecrivain.writerows(resultats)
    print(f"Resultats ecrits dans : {os.path.relpath(FICHIER_RESULTATS, RACINE_J3)}")

    spark.stop()


if __name__ == "__main__":
    main()
