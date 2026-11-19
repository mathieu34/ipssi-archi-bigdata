"""Nettoyage des sources store_sales, store et date_dim (TP Jour 3, UC-06, etape 4).

Applique les regles R1 a R22 de docs/03_regles_nettoyage.md et affiche un bilan :
nombre de lignes a chaque etape et nombre de rejets par motif.

Etape 6 (§4.9) : ecrit les jeux nettoyes dans la zone Silver (Parquet), puis les relit
pour controler presence, format, lisibilite, volumes et schema.
Documentation de la zone Silver : docs/05_silver.md

Execution (depuis la racine du depot, environnement virtuel active) :
    python J3_Retail_Intelligence/scripts/nettoyage.py
"""
import os

from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import DateType, DecimalType, IntegerType, StringType

# A ADAPTER : dossier qui contient data/ et data_refresh/ des donnees TPCx-BB.
# Peut aussi etre fourni par la variable d'environnement RETAIL_SOURCES.
DOSSIER_SOURCES = os.environ.get(
    "RETAIL_SOURCES", "/home/math34/tp_bigdata/extract/retail_project"
)

# Zone Silver : J3_Retail_Intelligence/data/silver (chemin calcule depuis ce script)
DOSSIER_SILVER = os.path.abspath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "silver")
)

MONTANT = DecimalType(7, 2)  # type TPC-DS des montants : exact au centime (R2)

# R1 + R2 : noms des colonnes (specification TPCx-BB) et types explicites
SCHEMA_VENTES = [
    ("ss_sold_date_sk", IntegerType()), ("ss_sold_time_sk", IntegerType()),
    ("ss_item_sk", IntegerType()), ("ss_customer_sk", IntegerType()),
    ("ss_cdemo_sk", IntegerType()), ("ss_hdemo_sk", IntegerType()),
    ("ss_addr_sk", IntegerType()), ("ss_store_sk", IntegerType()),
    ("ss_promo_sk", IntegerType()), ("ss_ticket_number", IntegerType()),
    ("ss_quantity", IntegerType()),
    ("ss_wholesale_cost", MONTANT), ("ss_list_price", MONTANT),
    ("ss_sales_price", MONTANT), ("ss_ext_discount_amt", MONTANT),
    ("ss_ext_sales_price", MONTANT), ("ss_ext_wholesale_cost", MONTANT),
    ("ss_ext_list_price", MONTANT), ("ss_ext_tax", MONTANT),
    ("ss_coupon_amt", MONTANT), ("ss_net_paid", MONTANT),
    ("ss_net_paid_inc_tax", MONTANT), ("ss_net_profit", MONTANT),
]
SCHEMA_MAGASINS = [
    ("s_store_sk", IntegerType()), ("s_store_id", StringType()),
    ("s_rec_start_date", DateType()), ("s_rec_end_date", DateType()),
    ("s_closed_date_sk", IntegerType()), ("s_store_name", StringType()),
    ("s_number_employees", IntegerType()), ("s_floor_space", IntegerType()),
    ("s_hours", StringType()), ("s_manager", StringType()),
    ("s_market_id", IntegerType()), ("s_geography_class", StringType()),
    ("s_market_desc", StringType()), ("s_market_manager", StringType()),
    ("s_division_id", IntegerType()), ("s_division_name", StringType()),
    ("s_company_id", IntegerType()), ("s_company_name", StringType()),
    # numero de rue et code postal : codes, pas des nombres (zeros initiaux a conserver)
    ("s_street_number", StringType()), ("s_street_name", StringType()),
    ("s_street_type", StringType()), ("s_suite_number", StringType()),
    ("s_city", StringType()), ("s_county", StringType()),
    ("s_state", StringType()), ("s_zip", StringType()),
    ("s_country", StringType()), ("s_gmt_offset", DecimalType(5, 2)),
    ("s_tax_precentage", DecimalType(5, 2)),
]
# date_dim : le fichier a 28 colonnes (R1), seules 4 sont gardees et typees (R20)
COLONNES_DATE_DIM = [
    "d_date_sk", "d_date_id", "d_date", "d_month_seq", "d_week_seq", "d_quarter_seq",
    "d_year", "d_dow", "d_moy", "d_dom", "d_qoy", "d_fy_year", "d_fy_quarter_seq",
    "d_fy_week_seq", "d_day_name", "d_quarter_name", "d_holiday", "d_weekend",
    "d_following_holiday", "d_first_dom", "d_last_dom", "d_same_day_ly",
    "d_same_day_lq", "d_current_day", "d_current_week", "d_current_month",
    "d_current_quarter", "d_current_year",
]
SCHEMA_DATES = [
    ("d_date_sk", IntegerType()), ("d_date", DateType()),
    ("d_year", IntegerType()), ("d_moy", IntegerType()),
]

# R5 : champs obligatoires d'une vente pour Q3
CHAMPS_OBLIGATOIRES = ["ss_store_sk", "ss_ticket_number", "ss_item_sk",
                       "ss_sold_date_sk", "ss_quantity", "ss_net_paid"]
# R10 : periode couverte par les donnees (01/01/2001 -> 31/12/2005, cf. date_dim)
DATE_SK_MIN, DATE_SK_MAX = 36890, 38715
# R14 : tolerance d'arrondi sur les montants
TOLERANCE = 0.01


def chemin(table, lot="data"):
    # Prefixe file:// obligatoire : sinon Spark cherche dans HDFS (fs.defaultFS du J2)
    return f"file://{DOSSIER_SOURCES}/{lot}/{table}/{table}.dat"


def lire_brut(spark, table, colonnes, lot="data"):
    """R1 : lecture en texte brut (toutes colonnes string), colonnes nommees.
    colonnes : liste de noms, ou schema [(nom, type), ...]."""
    noms = [c if isinstance(c, str) else c[0] for c in colonnes]
    df = (spark.read.option("header", False).option("sep", "|")
          .csv(chemin(table, lot)))
    return df.toDF(*noms)


def typer(df_brut, schema, libelle):
    """R2 : conversion vers le schema explicite.
    R3 : compte, par colonne, les valeurs non nulles devenues nulles a la conversion.
    try_cast et non cast : en Spark 4 (mode ANSI par defaut), cast fait planter le
    traitement sur une valeur non convertible ; try_cast renvoie null, ce qui permet
    de reperer la ligne et de l'envoyer dans les rejets."""
    df_type = df_brut.select(
        *[F.col(nom).try_cast(type_).alias(nom) for nom, type_ in schema]
    )
    echecs = df_brut.select(*[
        F.sum((F.col(nom).isNotNull() & F.col(nom).try_cast(type_).isNull()).cast("int")).alias(nom)
        for nom, type_ in schema
    ]).first().asDict()
    colonnes_en_echec = {c: n for c, n in echecs.items() if n}
    print(f"[R3] {libelle} - conversions echouees : "
          f"{colonnes_en_echec if colonnes_en_echec else 'aucune'}")
    return df_type, colonnes_en_echec


def nettoyer(spark, verbeux=True):
    """Applique les regles R1 a R22.
    Retourne (ventes_propres, ventes_rejetees, magasins_propres, dates_propres)."""
    def log(*args):
        if verbeux:
            print(*args)

    # ---------- store ----------
    magasins_brut = lire_brut(spark, "store", SCHEMA_MAGASINS)
    magasins, echecs_magasins = typer(magasins_brut, SCHEMA_MAGASINS, "store")
    if echecs_magasins:
        raise ValueError(f"store : conversions echouees {echecs_magasins}")

    # R15 : trim des colonnes texte
    magasins = magasins.select(*[
        F.trim(F.col(nom)).alias(nom) if isinstance(type_, StringType) else F.col(nom)
        for nom, type_ in SCHEMA_MAGASINS
    ])
    # R16 : s_rec_end_date reste nulle (version toujours valide), typee en date par R2
    # R18, R19 : s_closed_date_sk et s_floor_space conserves, jamais utilises pour filtrer

    # R17 : unicite de la cle de jointure (controle bloquant)
    nb_magasins = magasins.count()
    nb_cles = magasins.select("s_store_sk").distinct().count()
    log(f"[R17] store - {nb_magasins} lignes, {nb_cles} s_store_sk distincts")
    if nb_cles != nb_magasins:
        raise ValueError("store : s_store_sk n'est pas unique, jointure impossible")

    # ---------- date_dim ----------
    # R20 : on ne garde que les 4 colonnes utiles, typees explicitement (R2, R3)
    dates_brut = lire_brut(spark, "date_dim", COLONNES_DATE_DIM)
    dates, echecs_dates = typer(dates_brut.select([n for n, _ in SCHEMA_DATES]),
                                SCHEMA_DATES, "date_dim")
    if echecs_dates:
        raise ValueError(f"date_dim : conversions echouees {echecs_dates}")
    dates = dates.cache()

    # R21 : unicite de la cle de jointure (controle bloquant, comme R17)
    nb_jours = dates.count()
    nb_cles_dates = dates.select("d_date_sk").distinct().count()
    log(f"[R21] date_dim - {nb_jours} lignes, {nb_cles_dates} d_date_sk distincts")
    if nb_cles_dates != nb_jours:
        raise ValueError("date_dim : d_date_sk n'est pas unique, jointure impossible")

    # ---------- store_sales ----------
    # R4 : union des deux lots, avec la provenance
    lots = []
    for lot in ["data", "data_refresh"]:
        brut = lire_brut(spark, "store_sales", SCHEMA_VENTES, lot)
        lots.append(brut.withColumn("lot_source", F.lit(lot)))
        log(f"[R4] store_sales {lot:12} : {brut.count()} lignes")
    ventes_brut = lots[0].unionByName(lots[1])

    # R2 + R3 : typage, avec reperage des lignes dont une conversion echoue
    schema_avec_lot = SCHEMA_VENTES + [("lot_source", StringType())]
    echec_conversion = F.lit(False)
    for nom, type_ in SCHEMA_VENTES:
        echec_conversion = echec_conversion | (
            F.col(nom).isNotNull() & F.col(nom).try_cast(type_).isNull())
    ventes_brut = ventes_brut.withColumn("_echec_conversion", echec_conversion)
    typer(ventes_brut.drop("_echec_conversion"), schema_avec_lot, "store_sales")
    ventes = ventes_brut.select(
        *[F.col(nom).try_cast(type_).alias(nom) for nom, type_ in schema_avec_lot],
        "_echec_conversion",
    ).cache()
    nb_union = ventes.count()
    log(f"[R4] store_sales apres union : {nb_union} lignes")

    # R7 : doublons stricts sur les 23 colonnes de donnees (hors provenance)
    colonnes_donnees = [nom for nom, _ in SCHEMA_VENTES]
    ventes = ventes.dropDuplicates(colonnes_donnees)
    nb_dedup = ventes.count()
    log(f"[R7] doublons stricts retires : {nb_union - nb_dedup}")
    # R6, R8, R12, R13 : conservations (aucune action sur les donnees)

    # R9 : magasin connu (jointure sur les cles de store)
    cles_magasins = magasins.select(F.col("s_store_sk").alias("_cle_magasin"))
    ventes = ventes.join(F.broadcast(cles_magasins),
                         ventes.ss_store_sk == cles_magasins._cle_magasin, "left")

    # R22 : jour de vente connu du calendrier (meme principe que R9)
    cles_dates = dates.select(F.col("d_date_sk").alias("_cle_date"))
    ventes = ventes.join(F.broadcast(cles_dates),
                         ventes.ss_sold_date_sk == cles_dates._cle_date, "left")

    # R5, R9, R10, R11, R14, R22 + R3 : un motif par regle non respectee
    obligatoire_nul = F.lit(False)
    for c in CHAMPS_OBLIGATOIRES:
        obligatoire_nul = obligatoire_nul | F.col(c).isNull()
    motifs = [
        F.when(F.col("_echec_conversion"), F.lit("conversion_echouee")),            # R3
        F.when(obligatoire_nul, F.lit("champ_obligatoire_nul")),                    # R5
        F.when(F.col("ss_store_sk").isNotNull() & F.col("_cle_magasin").isNull(),
               F.lit("magasin_inconnu")),                                           # R9
        F.when(~F.col("ss_sold_date_sk").between(DATE_SK_MIN, DATE_SK_MAX),
               F.lit("date_hors_periode")),                                         # R10
        F.when((F.col("ss_quantity") < 1) | (F.col("ss_net_paid") < 0),
               F.lit("valeur_hors_domaine")),                                       # R11
        F.when(F.abs(F.col("ss_net_paid")
                     - (F.col("ss_ext_sales_price") - F.col("ss_coupon_amt"))) > TOLERANCE,
               F.lit("montant_incoherent")),                                        # R14
        F.when(F.col("ss_sold_date_sk").isNotNull() & F.col("_cle_date").isNull(),
               F.lit("date_inconnue")),                                             # R22
    ]
    ventes = (ventes.withColumn("motif_rejet", F.concat_ws(",", *motifs))
              .drop("_cle_magasin", "_cle_date", "_echec_conversion")
              .cache())

    ventes_propres = ventes.filter(F.col("motif_rejet") == "").drop("motif_rejet")
    ventes_rejetees = ventes.filter(F.col("motif_rejet") != "")

    return ventes_propres, ventes_rejetees, magasins, dates


def ajouter_provenance(df, fichiers_source):
    """Provenance (§3.3, §4.9.2) : fichier(s) d'origine et horodatage du traitement."""
    return (df.withColumn("_fichiers_source", F.lit(fichiers_source))
              .withColumn("_date_traitement", F.current_timestamp()))


def ecrire_silver(spark, jeux):
    """Ecrit chaque jeu en Parquet dans data/silver/<nom>, puis le relit et le controle.
    jeux : liste de (nom, DataFrame, nombre de lignes attendu, nombre de fichiers).
    coalesce : sans lui, le dropDuplicates (R7) laisse 200 partitions, donc 200 petits
    fichiers. On vise des fichiers de quelques dizaines de Mo au plus."""
    print(f"\n===== ZONE SILVER : {DOSSIER_SILVER} =====")
    for nom, df, attendu, nb_fichiers in jeux:
        chemin_sortie = f"file://{DOSSIER_SILVER}/{nom}"
        # overwrite : repertoire dedie au TP, regenere a chaque execution (§1.9.4)
        df.coalesce(nb_fichiers).write.mode("overwrite").parquet(chemin_sortie)

        relu = spark.read.parquet(chemin_sortie)                       # lisibilite + format
        nb_relu = relu.count()                                         # volume
        fichiers = [f for f in os.listdir(f"{DOSSIER_SILVER}/{nom}") if f.endswith(".parquet")]
        taille = sum(os.path.getsize(f"{DOSSIER_SILVER}/{nom}/{f}") for f in fichiers)
        schema_ok = [c.name for c in relu.schema] == df.columns        # schema conserve
        statut = "OK" if (nb_relu == attendu and schema_ok and fichiers) else "ECART"
        print(f"[Silver] {nom:18} | {len(fichiers)} fichier(s) parquet | {taille / 1024**2:6.2f} Mo | "
              f"{nb_relu:>7} lignes relues / {attendu} attendues | schema conserve : {schema_ok} | {statut}")
        if statut != "OK":
            raise ValueError(f"Silver {nom} : controle apres ecriture en echec")


def main():
    spark = (SparkSession.builder
             .appName("TP3-Nettoyage")
             .master("local[*]")
             .getOrCreate())
    spark.sparkContext.setLogLevel("ERROR")
    print("Version Spark :", spark.version)
    print("Sources :", DOSSIER_SOURCES, "\n")

    ventes_propres, ventes_rejetees, magasins, dates = nettoyer(spark)

    nb_propres = ventes_propres.count()
    nb_rejets = ventes_rejetees.count()
    print("\n===== BILAN =====")
    print(f"store       : {magasins.count()} magasins conserves")
    print(f"date_dim    : {dates.count()} jours conserves ({len(dates.columns)} colonnes)")
    print(f"store_sales : {nb_propres} lignes conservees, {nb_rejets} lignes rejetees")
    print("\nRejets par motif :")
    if nb_rejets:
        ventes_rejetees.groupBy("motif_rejet").count().show(truncate=False)
    else:
        print("  aucun")
    print("Lignes conservees par lot :")
    ventes_propres.groupBy("lot_source").count().orderBy("lot_source").show()

    print("Schema des ventes nettoyees :")
    ventes_propres.printSchema()
    print("Schema des magasins nettoyes :")
    magasins.printSchema()
    print("Schema du calendrier nettoye :")
    dates.printSchema()

    # ---------- Etape 6 : ecriture et controle de la zone Silver ----------
    fichiers_ventes = "data/store_sales/store_sales.dat + data_refresh/store_sales/store_sales.dat"
    ecrire_silver(spark, [
        ("store_sales", ajouter_provenance(ventes_propres, fichiers_ventes), nb_propres, 2),
        ("store_sales_rejets", ajouter_provenance(ventes_rejetees, fichiers_ventes), nb_rejets, 1),
        ("store", ajouter_provenance(magasins, "data/store/store.dat"), magasins.count(), 1),
        ("date_dim", ajouter_provenance(dates, "data/date_dim/date_dim.dat"), dates.count(), 1),
    ])

    print("\nSchema relu de silver/store_sales :")
    spark.read.parquet(f"file://{DOSSIER_SILVER}/store_sales").printSchema()

    spark.stop()


if __name__ == "__main__":
    main()
