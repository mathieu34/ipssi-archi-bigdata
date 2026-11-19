"""Transformations Silver -> Gold pour Q3 (TP Jour 3, UC-06, etapes 5 et 7).

Question metier (J1, Q3) : quel magasin vend le plus ?
Question decisionnelle : classement des 12 magasins selon le CA net, par annee,
complete par le nombre de transactions et le panier moyen.

1. Lit la zone Silver produite par scripts/nettoyage.py (a executer avant).
2. Jointure 1 : ventes + store    (ss_store_sk = s_store_sk)
3. Jointure 2 : ventes + date_dim (ss_sold_date_sk = d_date_sk)
4. Agregation : CA net, transactions, panier moyen et rang, par magasin et par annee.
5. Ecrit le resultat dans la zone Gold (Parquet), puis le relit et le controle.

Documentation : docs/04_transformations.md (etape 5), docs/06_gold.md (etape 7)

Execution (depuis la racine du depot, environnement virtuel active) :
    python J3_Retail_Intelligence/scripts/nettoyage.py        # Bronze -> Silver
    python J3_Retail_Intelligence/scripts/transformations.py  # Silver -> Gold
"""
import os

from pyspark.sql import SparkSession, Window
from pyspark.sql import functions as F

DOSSIER_DATA = os.path.abspath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
)
DOSSIER_SILVER = f"{DOSSIER_DATA}/silver"
DOSSIER_GOLD = f"{DOSSIER_DATA}/gold"
NOM_GOLD_Q3 = "q3_ca_magasin_annee"


def lire_silver(spark, nom):
    """Lecture d'un jeu Silver : le Parquet conserve les types, pas de schema a redonner."""
    return spark.read.parquet(f"file://{DOSSIER_SILVER}/{nom}")


def joindre_verifie(gauche, droite, condition, libelle, colonne_temoin):
    """Jointure gauche avec les controles du §4.8.3 :
    lignes avant / apres (la jointure ne doit ni perdre ni dupliquer de ligne)
    et nombre de lignes non rapprochees (colonne_temoin nulle apres jointure)."""
    avant = gauche.count()
    resultat = gauche.join(F.broadcast(droite), condition, "left")
    apres = resultat.count()
    non_rapprochees = resultat.filter(F.col(colonne_temoin).isNull()).count()
    print(f"[{libelle}] lignes avant : {avant} | apres : {apres} | "
          f"non rapprochees : {non_rapprochees}")
    if apres != avant:
        # Plus de lignes apres qu'avant = cle en double cote droit (§4.8.4)
        raise ValueError(f"{libelle} : le nombre de lignes a change ({avant} -> {apres})")
    return resultat


def enrichir(ventes, magasins, dates):
    """Jointures 1 et 2 : ajoute aux ventes le nom et la ville du magasin, et l'annee."""
    infos_magasins = magasins.select("s_store_sk", "s_store_id", "s_store_name",
                                     "s_city", "s_state")
    ventes_magasins = joindre_verifie(
        ventes, infos_magasins, ventes.ss_store_sk == infos_magasins.s_store_sk,
        "Jointure 1 ventes x store", "s_store_sk")

    # Seules les colonnes utiles sont jointes : les colonnes de provenance de store
    # et date_dim (_fichiers_source...) feraient doublon avec celles des ventes
    infos_dates = dates.select("d_date_sk", "d_date", "d_year", "d_moy")
    ventes_enrichies = joindre_verifie(
        ventes_magasins, infos_dates, ventes_magasins.ss_sold_date_sk == infos_dates.d_date_sk,
        "Jointure 2 ventes x date_dim", "d_date_sk")

    # Les cles de droite font doublon avec celles des ventes : on les retire
    return ventes_enrichies.drop("s_store_sk", "d_date_sk")


def verifier_tickets(ventes_enrichies):
    """Un ticket doit appartenir a un seul magasin et a un seul jour.
    Sinon, compter les tickets distincts par magasin et par annee les compterait
    plusieurs fois, et le nombre de transactions serait faux."""
    tickets_ambigus = (
        ventes_enrichies.groupBy("ss_ticket_number")
        .agg(F.countDistinct("ss_store_sk").alias("nb_magasins"),
             F.countDistinct("ss_sold_date_sk").alias("nb_jours"))
        .filter((F.col("nb_magasins") > 1) | (F.col("nb_jours") > 1))
        .count()
    )
    print(f"[Controle tickets] tickets rattaches a plusieurs magasins ou jours : {tickets_ambigus}")
    return tickets_ambigus


def agreger_q3(ventes_enrichies):
    """Agregation Q3. Granularite du resultat : une ligne = un magasin x une annee.
      ca_net          = somme de ss_net_paid (CA net apres coupons, hors taxes)
      nb_transactions = nombre de tickets distincts (et non nombre de lignes)
      panier_moyen    = ca_net / nb_transactions
      rang_annee      = classement par CA net decroissant au sein de chaque annee"""
    q3 = (
        ventes_enrichies
        .groupBy("d_year", "ss_store_sk", "s_store_id", "s_store_name", "s_city", "s_state")
        .agg(
            F.sum("ss_net_paid").alias("ca_net"),
            F.countDistinct("ss_ticket_number").alias("nb_transactions"),
            F.count("*").alias("nb_lignes_vente"),
            F.sum("ss_quantity").alias("quantite_vendue"),
        )
        .withColumn("panier_moyen", F.round(F.col("ca_net") / F.col("nb_transactions"), 2))
        .withColumn("rang_annee",
                    F.rank().over(Window.partitionBy("d_year").orderBy(F.desc("ca_net"))))
        .withColumnRenamed("d_year", "annee")
    )
    return q3


def main():
    spark = (SparkSession.builder
             .appName("TP3-Transformations")
             .master("local[*]")
             .getOrCreate())
    spark.sparkContext.setLogLevel("ERROR")
    print("Version Spark :", spark.version, "\n")

    print(f"===== 1. Lecture de la zone Silver : {DOSSIER_SILVER} =====")
    ventes = lire_silver(spark, "store_sales")
    magasins = lire_silver(spark, "store")
    dates = lire_silver(spark, "date_dim")
    print(f"ventes : {ventes.count()} | magasins : {magasins.count()} | jours : {dates.count()}")

    print("\n===== 2. Jointures (§4.8.3) =====")
    ventes_enrichies = enrichir(ventes, magasins, dates).cache()
    verifier_tickets(ventes_enrichies)
    print("\nEchantillon des ventes enrichies :")
    ventes_enrichies.select("ss_ticket_number", "ss_store_sk", "s_store_name", "s_city",
                            "d_date", "d_year", "ss_net_paid", "lot_source").show(5)

    print("===== 3. Agregation Q3 (§4.8.5) : CA net par magasin et par annee =====")
    q3 = agreger_q3(ventes_enrichies).cache()
    print(f"Lignes du resultat : {q3.count()} (attendu : 12 magasins x 5 annees = 60)")

    print("\nControle de coherence : total du CA net")
    total_ventes = ventes_enrichies.agg(F.sum("ss_net_paid")).first()[0]
    total_q3 = q3.agg(F.sum("ca_net")).first()[0]
    print(f"  somme ventes : {total_ventes} | somme agregat : {total_q3} | "
          f"ecart : {total_ventes - total_q3}")

    print("\nClassement par annee (top 3 et dernier) :")
    dernier_rang = q3.groupBy("annee").agg(F.max("rang_annee").alias("dernier"))
    (q3.join(dernier_rang, "annee")
       .filter((F.col("rang_annee") <= 3) | (F.col("rang_annee") == F.col("dernier")))
       .select("annee", "rang_annee", "s_store_name", "ca_net", "nb_transactions", "panier_moyen")
       .orderBy("annee", "rang_annee")
       .show(30, truncate=False))

    print("Synthese 2001-2005 (toutes annees confondues) :")
    (q3.groupBy("ss_store_sk", "s_store_name")
       .agg(F.sum("ca_net").alias("ca_net_5_ans"),
            F.sum("nb_transactions").alias("nb_transactions_5_ans"))
       .withColumn("panier_moyen", F.round(F.col("ca_net_5_ans") / F.col("nb_transactions_5_ans"), 2))
       .withColumn("rang", F.rank().over(Window.orderBy(F.desc("ca_net_5_ans"))))
       .orderBy("rang")
       .show(truncate=False))

    print("Ecart entre le 1er et le dernier magasin, par annee :")
    (q3.groupBy("annee")
       .agg(F.max("ca_net").alias("ca_max"), F.min("ca_net").alias("ca_min"))
       .withColumn("ecart_pct", F.round((F.col("ca_max") - F.col("ca_min")) / F.col("ca_min") * 100, 2))
       .orderBy("annee")
       .show())

    ecrire_gold(spark, q3, total_ventes)

    spark.stop()


def ecrire_gold(spark, q3, total_ventes):
    """Etape 7 (§4.10) : ecriture du jeu Gold Q3 en Parquet, puis relecture et controles."""
    chemin_gold = f"file://{DOSSIER_GOLD}/{NOM_GOLD_Q3}"
    print(f"===== 4. Zone Gold : {DOSSIER_GOLD}/{NOM_GOLD_Q3} =====")

    gold = (q3
            .select("annee", "rang_annee", "ss_store_sk", "s_store_id", "s_store_name",
                    "s_city", "s_state", "ca_net", "nb_transactions", "panier_moyen",
                    "nb_lignes_vente", "quantite_vendue")
            .withColumn("_sources", F.lit("silver/store_sales + silver/store + silver/date_dim"))
            .withColumn("_date_traitement", F.current_timestamp())
            .orderBy("annee", "rang_annee"))

    # 60 lignes : un seul fichier ; overwrite sur un repertoire dedie au TP
    gold.coalesce(1).write.mode("overwrite").parquet(chemin_gold)

    relu = spark.read.parquet(chemin_gold)
    nb_lignes = relu.count()
    total_relu = relu.agg(F.sum("ca_net")).first()[0]
    cles_uniques = relu.select("annee", "ss_store_sk").distinct().count()
    print(f"[Gold] lignes relues : {nb_lignes} (attendu 60) | "
          f"couples (annee, magasin) distincts : {cles_uniques} | "
          f"CA total relu : {total_relu} (attendu {total_ventes})")
    if nb_lignes != 60 or cles_uniques != 60 or total_relu != total_ventes:
        raise ValueError("Gold : controle apres ecriture en echec")
    print("[Gold] controle apres ecriture : OK\n")

    print("Schema relu du jeu Gold :")
    relu.printSchema()
    print("Contenu (annee 2005) :")
    relu.filter(F.col("annee") == 2005).drop("_sources", "_date_traitement").show(truncate=False)


if __name__ == "__main__":
    main()
