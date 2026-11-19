"""Comparaison des formats CSV, JSON et Parquet (TP Jour 3, UC-06, etape 8, §4.11.3).

Ecrit le meme jeu (silver/store_sales, 674 211 lignes) en CSV, JSON et Parquet,
puis compare pour chaque format :
  - le volume de stockage observe ;
  - la conservation des types a la relecture ;
  - le temps de lecture complete (count) ;
  - le temps de lecture d'une seule colonne (somme de ss_net_paid), pour mettre en
    evidence la lecture selective permise par le stockage en colonnes.

Les copies CSV et JSON sont ecrites dans data/test/formats (ignore par Git) :
elles ne servent qu'a la mesure. Documentation : docs/07_formats_parquet.md

Execution (apres nettoyage.py) :
    python J3_Retail_Intelligence/scripts/comparaison_formats.py
"""
import os
import sys
import time

from pyspark.sql import SparkSession
from pyspark.sql import functions as F

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from nettoyage import DOSSIER_SOURCES  # noqa: E402  (meme chemin des sources que le nettoyage)

DOSSIER_DATA = os.path.abspath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
)
SILVER_VENTES = f"{DOSSIER_DATA}/silver/store_sales"
DOSSIER_TEST = f"{DOSSIER_DATA}/test/formats"
REPETITIONS = 3  # chaque lecture est chronometree 3 fois, on garde la meilleure


def taille_mo(dossier):
    return sum(os.path.getsize(os.path.join(dossier, f)) for f in os.listdir(dossier)
               if not f.startswith((".", "_"))) / 1024**2


def chrono(action):
    meilleur = None
    for _ in range(REPETITIONS):
        debut = time.perf_counter()
        resultat = action()
        duree = time.perf_counter() - debut
        meilleur = duree if meilleur is None else min(meilleur, duree)
    return resultat, meilleur


def main():
    spark = (SparkSession.builder.appName("TP3-Formats").master("local[*]").getOrCreate())
    spark.sparkContext.setLogLevel("ERROR")
    print("Version Spark :", spark.version, "\n")

    ventes = spark.read.parquet(f"file://{SILVER_VENTES}").drop("_fichiers_source", "_date_traitement")
    nb = ventes.count()
    print(f"Jeu compare : silver/store_sales, {nb} lignes, {len(ventes.columns)} colonnes\n")

    # Ecriture du meme jeu dans les trois formats (2 fichiers chacun, comme le Silver)
    chemins = {
        "CSV": f"{DOSSIER_TEST}/store_sales_csv",
        "JSON": f"{DOSSIER_TEST}/store_sales_json",
        "Parquet": f"{DOSSIER_TEST}/store_sales_parquet",
    }
    ventes.coalesce(2).write.mode("overwrite").option("header", True).csv(f"file://{chemins['CSV']}")
    ventes.coalesce(2).write.mode("overwrite").json(f"file://{chemins['JSON']}")
    ventes.coalesce(2).write.mode("overwrite").parquet(f"file://{chemins['Parquet']}")

    lecteurs = {
        # CSV relu sans inferSchema : c'est ce que voit un outil qui ne connait pas le schema
        "CSV": lambda: spark.read.option("header", True).csv(f"file://{chemins['CSV']}"),
        "JSON": lambda: spark.read.json(f"file://{chemins['JSON']}"),
        "Parquet": lambda: spark.read.parquet(f"file://{chemins['Parquet']}"),
    }

    fichiers_dat = [f"{DOSSIER_SOURCES}/{lot}/store_sales/store_sales.dat" for lot in ("data", "data_refresh")]
    if all(os.path.exists(f) for f in fichiers_dat):
        taille_dat = sum(os.path.getsize(f) for f in fichiers_dat) / 1024**2
        print(f"Reference : fichiers sources .dat (texte delimite par |, sans en-tete) : {taille_dat:.2f} Mo\n")

    print(f"{'Format':8} | {'Taille':>9} | {'Lignes relues':>13} | {'Lecture complete':>16} | "
          f"{'Lecture 1 colonne':>17} | Type relu de ss_net_paid / ss_quantity")
    print("-" * 118)
    for fmt, lire in lecteurs.items():
        df = lire()
        types = dict(df.dtypes)
        nb_relu, t_complet = chrono(lambda: lire().count())
        _, t_colonne = chrono(lambda: lire().agg(F.sum(F.col("ss_net_paid").cast("decimal(17,2)"))).first())
        print(f"{fmt:8} | {taille_mo(chemins[fmt]):6.2f} Mo | {nb_relu:>13} | {t_complet:13.2f} s | "
              f"{t_colonne:14.2f} s | {types['ss_net_paid']} / {types['ss_quantity']}")

    print("\nSomme de ss_net_paid relue dans chaque format (controle d'exactitude) :")
    for fmt, lire in lecteurs.items():
        total = lire().agg(F.sum(F.col("ss_net_paid").cast("decimal(17,2)"))).first()[0]
        print(f"  {fmt:8} : {total}")

    print("\nApercu du contenu brut (debut du premier fichier) :")
    for fmt in ["CSV", "JSON"]:
        fichier = sorted(f for f in os.listdir(chemins[fmt]) if f.startswith("part-"))[0]
        with open(os.path.join(chemins[fmt], fichier), encoding="utf-8") as f:
            print(f"  {fmt} : {f.readline().strip()[:150]}")
            print(f"  {' ' * len(fmt)}   {f.readline().strip()[:150]}")
    print("  Parquet : fichier binaire (non lisible dans un editeur de texte)")

    spark.stop()


if __name__ == "__main__":
    main()
