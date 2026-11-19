```python
from pyspark.sql import SparkSession

spark = (
    SparkSession.builder
    .appName("TP3-Retail-Intelligence")
    .master("local[*]")
    .getOrCreate()
)

print("Version Spark :", spark.version)
```









    Version Spark : 4.3.0



```python
import os
import sys

# Noms de colonnes TPCx-BB : sources/schema.py, a la racine du depot (deja utilise aux J1 et J2).
# Le notebook s'execute depuis J3_Retail_Intelligence/notebooks/ : on remonte de 2 niveaux.
sys.path.append(os.path.abspath(os.path.join("..", "..", "sources")))

from schema import COLUMNS

COLONNES_STORE_SALES = COLUMNS["store_sales"]
COLONNES_STORE = COLUMNS["store"]

print(len(COLONNES_STORE_SALES), "colonnes store_sales :", COLONNES_STORE_SALES)
print(len(COLONNES_STORE), "colonnes store :", COLONNES_STORE)
```

    23 colonnes store_sales : ['ss_sold_date_sk', 'ss_sold_time_sk', 'ss_item_sk', 'ss_customer_sk', 'ss_cdemo_sk', 'ss_hdemo_sk', 'ss_addr_sk', 'ss_store_sk', 'ss_promo_sk', 'ss_ticket_number', 'ss_quantity', 'ss_wholesale_cost', 'ss_list_price', 'ss_sales_price', 'ss_ext_discount_amt', 'ss_ext_sales_price', 'ss_ext_wholesale_cost', 'ss_ext_list_price', 'ss_ext_tax', 'ss_coupon_amt', 'ss_net_paid', 'ss_net_paid_inc_tax', 'ss_net_profit']
    29 colonnes store : ['s_store_sk', 's_store_id', 's_rec_start_date', 's_rec_end_date', 's_closed_date_sk', 's_store_name', 's_number_employees', 's_floor_space', 's_hours', 's_manager', 's_market_id', 's_geography_class', 's_market_desc', 's_market_manager', 's_division_id', 's_division_name', 's_company_id', 's_company_name', 's_street_number', 's_street_name', 's_street_type', 's_suite_number', 's_city', 's_county', 's_state', 's_zip', 's_country', 's_gmt_offset', 's_tax_precentage']



```python
import os

# A ADAPTER : dossier qui contient votre copie des donnees TPCx-BB
# (le dossier parent de data/ et data_refresh/), sans prefixe file://
DOSSIER_SOURCES = "/home/math34/tp_bigdata/extract/retail_project"

# Chemins locaux des fichiers (sans prefixe, pour os.path.getsize)
FICHIERS = {
    "store_sales":         f"{DOSSIER_SOURCES}/data/store_sales/store_sales.dat",          # Source 1 : ventes magasin
    "store_sales_refresh": f"{DOSSIER_SOURCES}/data_refresh/store_sales/store_sales.dat",  # Source 1 bis : lot data_refresh
    "store":               f"{DOSSIER_SOURCES}/data/store/store.dat",                      # Source 2 : magasins
}

# Les noms de colonnes viennent de la cellule precedente (COLUMNS de sources/schema.py)

def lire_dat(chemin, colonnes):
    """Lit un .dat TPCx-BB (separateur |, sans en-tete) et nomme les colonnes.
    Prefixe file:// obligatoire : sinon Spark cherche dans HDFS (cf. fiche environnement)."""
    df = (
        spark.read
        .option("header", False)
        .option("inferSchema", True)
        .option("sep", "|")
        .csv("file://" + chemin)
    )
    return df.toDF(*colonnes)
```


```python
# Lecture des sources
df_ventes = lire_dat(FICHIERS["store_sales"], COLONNES_STORE_SALES)
df_ventes_refresh = lire_dat(FICHIERS["store_sales_refresh"], COLONNES_STORE_SALES)
df_magasins = lire_dat(FICHIERS["store"], COLONNES_STORE)

# Inventaire : taille, nombre de lignes, nombre de colonnes
for cle, df in [("store_sales", df_ventes),
                ("store_sales_refresh", df_ventes_refresh),
                ("store", df_magasins)]:
    taille_mo = os.path.getsize(FICHIERS[cle]) / 1024**2
    print(f"{cle:20} | {taille_mo:6.2f} Mo | {df.count():>7} lignes | {len(df.columns)} colonnes")
```

    


    
                                                                                

    store_sales          |  88.47 Mo |  667579 lignes | 23 colonnes
    store_sales_refresh  |   0.88 Mo |    6632 lignes | 23 colonnes


    store                |   0.00 Mo |      12 lignes | 29 colonnes



```python
# Source 1 - store_sales : types observes (inferSchema) et echantillon
df_ventes.printSchema()
df_ventes.select("ss_sold_date_sk", "ss_store_sk", "ss_ticket_number", "ss_item_sk",
                 "ss_quantity", "ss_sales_price", "ss_net_paid").show(5)
```

    root
     |-- ss_sold_date_sk: integer (nullable = true)
     |-- ss_sold_time_sk: integer (nullable = true)
     |-- ss_item_sk: integer (nullable = true)
     |-- ss_customer_sk: integer (nullable = true)
     |-- ss_cdemo_sk: integer (nullable = true)
     |-- ss_hdemo_sk: integer (nullable = true)
     |-- ss_addr_sk: integer (nullable = true)
     |-- ss_store_sk: integer (nullable = true)
     |-- ss_promo_sk: integer (nullable = true)
     |-- ss_ticket_number: integer (nullable = true)
     |-- ss_quantity: integer (nullable = true)
     |-- ss_wholesale_cost: double (nullable = true)
     |-- ss_list_price: double (nullable = true)
     |-- ss_sales_price: double (nullable = true)
     |-- ss_ext_discount_amt: double (nullable = true)
     |-- ss_ext_sales_price: double (nullable = true)
     |-- ss_ext_wholesale_cost: double (nullable = true)
     |-- ss_ext_list_price: double (nullable = true)
     |-- ss_ext_tax: double (nullable = true)
     |-- ss_coupon_amt: double (nullable = true)
     |-- ss_net_paid: double (nullable = true)
     |-- ss_net_paid_inc_tax: double (nullable = true)
     |-- ss_net_profit: double (nullable = true)
    


    +---------------+-----------+----------------+----------+-----------+--------------+-----------+
    |ss_sold_date_sk|ss_store_sk|ss_ticket_number|ss_item_sk|ss_quantity|ss_sales_price|ss_net_paid|
    +---------------+-----------+----------------+----------+-----------+--------------+-----------+
    |          36890|         10|               0|     10001|         31|         23.08|     715.48|
    |          36890|         10|               0|     10000|         54|         83.34|    4500.36|
    |          36890|         10|               0|     15556|         39|         83.24|    2629.55|
    |          36890|          4|               1|      4597|         20|         133.4|     2668.0|
    |          36890|          4|               1|      3258|         76|         11.85|      900.6|
    +---------------+-----------+----------------+----------+-----------+--------------+-----------+
    only showing top 5 rows



```python
# Source 2 - store : types observes (inferSchema) et contenu (12 lignes, on peut tout afficher)
df_magasins.printSchema()
df_magasins.select("s_store_sk", "s_store_id", "s_store_name", "s_closed_date_sk",
                   "s_floor_space", "s_city", "s_state").show(truncate=False)
```

    root
     |-- s_store_sk: integer (nullable = true)
     |-- s_store_id: string (nullable = true)
     |-- s_rec_start_date: date (nullable = true)
     |-- s_rec_end_date: string (nullable = true)
     |-- s_closed_date_sk: integer (nullable = true)
     |-- s_store_name: string (nullable = true)
     |-- s_number_employees: integer (nullable = true)
     |-- s_floor_space: integer (nullable = true)
     |-- s_hours: string (nullable = true)
     |-- s_manager: string (nullable = true)
     |-- s_market_id: integer (nullable = true)
     |-- s_geography_class: string (nullable = true)
     |-- s_market_desc: string (nullable = true)
     |-- s_market_manager: string (nullable = true)
     |-- s_division_id: integer (nullable = true)
     |-- s_division_name: string (nullable = true)
     |-- s_company_id: integer (nullable = true)
     |-- s_company_name: string (nullable = true)
     |-- s_street_number: integer (nullable = true)
     |-- s_street_name: string (nullable = true)
     |-- s_street_type: string (nullable = true)
     |-- s_suite_number: string (nullable = true)
     |-- s_city: string (nullable = true)
     |-- s_county: string (nullable = true)
     |-- s_state: string (nullable = true)
     |-- s_zip: integer (nullable = true)
     |-- s_country: string (nullable = true)
     |-- s_gmt_offset: integer (nullable = true)
     |-- s_tax_precentage: double (nullable = true)
    
    +----------+----------------+------------+----------------+-------------+------------+-------+
    |s_store_sk|s_store_id      |s_store_name|s_closed_date_sk|s_floor_space|s_city      |s_state|
    +----------+----------------+------------+----------------+-------------+------------+-------+
    |0         |AAAAAAAAAAAAAAAA|Forest      |71238           |8891512      |Post Oak    |CO     |
    |1         |AAAAAAAAAAAAAAAB|Hillside    |18994           |8751339      |Jerusalem   |TN     |
    |2         |AAAAAAAAAAAAAAAC|Sherwood    |8900            |5913334      |Mount Vernon|CA     |
    |3         |AAAAAAAAAAAAAAAD|Pioneer     |69902           |5777026      |Austin      |TX     |
    |4         |AAAAAAAAAAAAAAAE|Elmwood     |79617           |7508523      |Lakeside    |KY     |
    |5         |AAAAAAAAAAAAAAAF|Egypt       |88139           |6942447      |Redland     |KY     |
    |6         |AAAAAAAAAAAAAAAG|Bloomfield  |15761           |8416754      |Union Hill  |IN     |
    |7         |AAAAAAAAAAAAAAAH|Buffalo     |71446           |8564004      |Lewisburg   |KS     |
    |8         |AAAAAAAAAAAAAAAI|Williamstown|50689           |8871354      |State Line  |TX     |
    |9         |AAAAAAAAAAAAAAAJ|Germantown  |25131           |6288915      |Pierce      |WV     |
    |10        |AAAAAAAAAAAAAAAK|Avalon      |6235            |6468537      |Cold Springs|TN     |
    |11        |AAAAAAAAAAAAAAAL|Bedford     |43634           |7039717      |Lyons       |KY     |
    +----------+----------------+------------+----------------+-------------+------------+-------+
    



```python
from pyspark.sql import functions as F

# data vs data_refresh : le lot refresh est-il une copie ou des ventes nouvelles ?
for nom, df in [("data", df_ventes), ("data_refresh", df_ventes_refresh)]:
    df.agg(
        F.min("ss_sold_date_sk").alias("date_min"),
        F.max("ss_sold_date_sk").alias("date_max"),
    ).withColumn("lot", F.lit(nom)).show()

tickets_communs = (
    df_ventes.select("ss_ticket_number").distinct()
    .join(df_ventes_refresh.select("ss_ticket_number").distinct(), on="ss_ticket_number")
    .count()
)
print("Tickets presents dans les deux lots :", tickets_communs)
```

    +--------+--------+----+
    |date_min|date_max| lot|
    +--------+--------+----+
    |   36890|   38697|data|
    +--------+--------+----+
    
    +--------+--------+------------+
    |date_min|date_max|         lot|
    +--------+--------+------------+
    |   38697|   38715|data_refresh|
    +--------+--------+------------+
    


    

    
                                                                                

    Tickets presents dans les deux lots : 0



```python
# Cles candidates : une cle est valable si son nombre de valeurs distinctes = nombre de lignes

# store : s_store_sk et s_store_id identifient-ils un magasin ?
nb_magasins = df_magasins.count()
print("store - lignes :", nb_magasins)
print("store - s_store_sk distincts :", df_magasins.select("s_store_sk").distinct().count())
print("store - s_store_id distincts :", df_magasins.select("s_store_id").distinct().count())

# store_sales : une ligne = un article d'un ticket ? on teste le couple (ticket, produit)
nb_ventes = df_ventes.count()
nb_couples = df_ventes.select("ss_ticket_number", "ss_item_sk").distinct().count()
print("\nstore_sales - lignes :", nb_ventes)
print("store_sales - couples (ss_ticket_number, ss_item_sk) distincts :", nb_couples)
print("store_sales - lignes en trop par rapport a ce couple :", nb_ventes - nb_couples)
```

    store - lignes : 12


    store - s_store_sk distincts : 12


    store - s_store_id distincts : 12


    
    store_sales - lignes : 667579
    store_sales - couples (ss_ticket_number, ss_item_sk) distincts : 663443
    store_sales - lignes en trop par rapport a ce couple : 4136


## Étape 3 – Exploration (§4.6) : valeurs manquantes, doublons, valeurs atypiques

Les ventes sont explorées sur les **deux lots réunis** (`data` + `data_refresh`), puisque l'inventaire a montré qu'ils sont complémentaires (0 ticket commun).


```python
# Ventes : les deux lots reunis
df_ventes_tout = df_ventes.unionByName(df_ventes_refresh)
print("store_sales (data + data_refresh) - lignes :", df_ventes_tout.count())

# Valeurs manquantes par colonne (meme principe que l'exemple du §4.6.2,
# mais calcule en une seule passe : une somme de 1 quand la valeur est nulle)
def compter_nulls(df):
    return df.agg(*[
        F.sum(F.col(c).isNull().cast("int")).alias(c) for c in df.columns
    ])

print("\nValeurs nulles - store_sales :")
nulls_ventes = compter_nulls(df_ventes_tout).first().asDict()
for colonne, nb in nulls_ventes.items():
    print(f"  {colonne:24} : {nb}")
```

    store_sales (data + data_refresh) - lignes : 674211
    
    Valeurs nulles - store_sales :


    

      ss_sold_date_sk          : 0
      ss_sold_time_sk          : 0
      ss_item_sk               : 0
      ss_customer_sk           : 0
      ss_cdemo_sk              : 250
      ss_hdemo_sk              : 308
      ss_addr_sk               : 462
      ss_store_sk              : 0
      ss_promo_sk              : 159
      ss_ticket_number         : 0
      ss_quantity              : 0
      ss_wholesale_cost        : 0
      ss_list_price            : 0
      ss_sales_price           : 0
      ss_ext_discount_amt      : 0
      ss_ext_sales_price       : 0
      ss_ext_wholesale_cost    : 0
      ss_ext_list_price        : 0
      ss_ext_tax               : 0
      ss_coupon_amt            : 0
      ss_net_paid              : 0
      ss_net_paid_inc_tax      : 0
      ss_net_profit            : 0


    
                                                                                


```python
print("Valeurs nulles - store :")
nulls_magasins = compter_nulls(df_magasins).first().asDict()
for colonne, nb in nulls_magasins.items():
    if nb > 0:
        print(f"  {colonne:20} : {nb} / {df_magasins.count()}")
print("(colonnes non affichees : 0 valeur nulle)")
```

    Valeurs nulles - store :




      s_rec_end_date       : 12 / 12
    (colonnes non affichees : 0 valeur nulle)



```python
# Doublons stricts : lignes identiques sur les 23 colonnes
nb_total = df_ventes_tout.count()
nb_distinct = df_ventes_tout.distinct().count()
print("Doublons stricts (lignes 100 % identiques) :", nb_total - nb_distinct)

# Les 4 136 repetitions du couple (ticket, produit) vues a l'etape 2 : a quoi ressemblent-elles ?
couples_repetes = (
    df_ventes_tout.groupBy("ss_ticket_number", "ss_item_sk").count()
    .filter(F.col("count") > 1)
)
print("Couples (ticket, produit) presents plusieurs fois :", couples_repetes.count())

exemple = couples_repetes.orderBy("ss_ticket_number").first()
print("\nExemple : ticket", exemple["ss_ticket_number"], "- produit", exemple["ss_item_sk"])
(df_ventes_tout
 .filter((F.col("ss_ticket_number") == exemple["ss_ticket_number"])
         & (F.col("ss_item_sk") == exemple["ss_item_sk"]))
 .select("ss_ticket_number", "ss_item_sk", "ss_sold_time_sk", "ss_quantity",
         "ss_sales_price", "ss_net_paid", "ss_promo_sk")
 .show())
```

    

    

    
                                                                                

    Doublons stricts (lignes 100 % identiques) : 0


    Couples (ticket, produit) presents plusieurs fois : 4082


    
    Exemple : ticket 44 - produit 10003


    +----------------+----------+---------------+-----------+--------------+-----------+-----------+
    |ss_ticket_number|ss_item_sk|ss_sold_time_sk|ss_quantity|ss_sales_price|ss_net_paid|ss_promo_sk|
    +----------------+----------+---------------+-----------+--------------+-----------+-----------+
    |              44|     10003|          27946|         31|         53.16|    1647.96|        283|
    |              44|     10003|          27946|         46|           1.6|       5.89|         22|
    +----------------+----------+---------------+-----------+--------------+-----------+-----------+
    



```python
# Valeurs atypiques : statistiques des colonnes numeriques utiles a Q3
colonnes_mesures = ["ss_quantity", "ss_sales_price", "ss_ext_sales_price",
                    "ss_coupon_amt", "ss_net_paid", "ss_net_profit"]
df_ventes_tout.select(colonnes_mesures).summary("count", "min", "25%", "50%", "75%", "max").show()

# Valeurs a examiner : quantites nulles ou negatives, montants nets negatifs ou nuls
print("ss_quantity <= 0       :", df_ventes_tout.filter(F.col("ss_quantity") <= 0).count())
print("ss_net_paid < 0        :", df_ventes_tout.filter(F.col("ss_net_paid") < 0).count())
print("ss_net_paid = 0        :", df_ventes_tout.filter(F.col("ss_net_paid") == 0).count())
print("ss_net_profit < 0      :", df_ventes_tout.filter(F.col("ss_net_profit") < 0).count(),
      "(vente a perte : possible, pas forcement une erreur)")
```

    


    

    
                                                                                

    +-------+-----------+--------------+------------------+-------------+-----------+-------------+
    |summary|ss_quantity|ss_sales_price|ss_ext_sales_price|ss_coupon_amt|ss_net_paid|ss_net_profit|
    +-------+-----------+--------------+------------------+-------------+-----------+-------------+
    |  count|     674211|        674211|            674211|       674211|     674211|       674211|
    |    min|          1|           0.0|               0.0|          0.0|        0.0|      -9866.6|
    |    25%|         26|         10.24|             313.5|          0.0|     245.64|     -1462.37|
    |    50%|         51|         27.69|           1048.22|          0.0|      878.4|      -377.35|
    |    75%|         76|         56.77|            2674.2|          0.0|    2365.53|         5.82|
    |    max|        100|         199.3|           18745.0|     14371.66|    18745.0|       9134.0|
    +-------+-----------+--------------+------------------+-------------+-----------+-------------+
    


    ss_quantity <= 0       : 0


    ss_net_paid < 0        : 0


    ss_net_paid = 0        : 3995


    ss_net_profit < 0      : 500889 (vente a perte : possible, pas forcement une erreur)



```python
# Coherence des montants (specification TPC-DS) :
#   ss_ext_sales_price = ss_quantity * ss_sales_price
#   ss_net_paid        = ss_ext_sales_price - ss_coupon_amt
# Tolerance de 1 centime pour les arrondis
TOLERANCE = 0.01
incoherent_ext = df_ventes_tout.filter(
    F.abs(F.col("ss_ext_sales_price") - F.col("ss_quantity") * F.col("ss_sales_price")) > TOLERANCE
).count()
incoherent_net = df_ventes_tout.filter(
    F.abs(F.col("ss_net_paid") - (F.col("ss_ext_sales_price") - F.col("ss_coupon_amt"))) > TOLERANCE
).count()
print("ext_sales_price != quantite x prix unitaire  :", incoherent_ext)
print("net_paid != ext_sales_price - coupon         :", incoherent_net)

# Magasins presents dans les ventes : valeurs de ss_store_sk
print("\nValeurs distinctes de ss_store_sk :")
df_ventes_tout.groupBy("ss_store_sk").count().orderBy("ss_store_sk").show(20)
```

    ext_sales_price != quantite x prix unitaire  : 0
    net_paid != ext_sales_price - coupon         : 0
    
    Valeurs distinctes de ss_store_sk :


    +-----------+-----+
    |ss_store_sk|count|
    +-----------+-----+
    |          0|56607|
    |          1|56248|
    |          2|55055|
    |          3|55970|
    |          4|56800|
    |          5|55773|
    |          6|55108|
    |          7|58159|
    |          8|56185|
    |          9|56590|
    |         10|55747|
    |         11|55969|
    +-----------+-----+
    



```python
# Pourquoi certaines ventes ont un montant net de 0 ?
ventes_nulles = df_ventes_tout.filter(F.col("ss_net_paid") == 0)
print("ss_net_paid = 0                      :", ventes_nulles.count())
print("  dont prix unitaire = 0             :", ventes_nulles.filter(F.col("ss_sales_price") == 0).count())
print("  dont coupon qui couvre tout le prix :", ventes_nulles.filter(
    (F.col("ss_sales_price") > 0) & (F.col("ss_coupon_amt") >= F.col("ss_ext_sales_price"))).count())
```

    ss_net_paid = 0                      : 3995


      dont prix unitaire = 0             : 3361


      dont coupon qui couvre tout le prix : 634


## Synthèse de l'exploration et réponses aux questions techniques (§4.6.3)

**Constats chiffrés** (`store_sales`, lots `data` + `data_refresh` = 674 211 lignes ; `store` = 12 lignes)

| Contrôle | Résultat | Interprétation |
|---|---|---|
| Valeurs nulles `store_sales` | 0 sur les colonnes utiles à Q3 (`ss_store_sk`, `ss_net_paid`, `ss_ticket_number`, `ss_sold_date_sk`). Nulles seulement sur `ss_cdemo_sk` (250), `ss_hdemo_sk` (308), `ss_addr_sk` (462), `ss_promo_sk` (159) | Liens facultatifs : une vente sans profil client renseigné, ou sans promotion. Aucun impact sur Q3 |
| Valeurs nulles `store` | `s_rec_end_date` : 12/12 | Une seule version par magasin, toujours valide. Ce n'est pas une erreur |
| Doublons stricts (23 colonnes identiques) | **0** | Aucune ligne copiée par erreur |
| Couple (ticket, produit) répété | 4 082 couples | Lignes **distinctes** : même ticket, même produit et même heure, mais quantité, prix et **promotion** différents (exemple : ticket 44). Ce sont des lignes légitimes, à **conserver** |
| `ss_quantity` | de 1 à 100, aucune valeur ≤ 0 | Cohérent |
| `ss_net_paid` | de 0 à 18 745, aucune valeur < 0 ; **3 995 lignes à 0** | 3 361 lignes avec un prix unitaire de 0 (article gratuit) et 634 lignes où le coupon couvre tout le prix. Ce sont des cas métier possibles, à **conserver** : ils ne font pas varier le CA |
| `ss_net_profit` | 500 889 lignes négatives (74 %) | Ventes à perte, très fréquentes : effet probable de la génération synthétique. Hors du périmètre de Q3, qui porte sur le CA et non sur la marge |
| Cohérence des calculs | `ext_sales_price = quantité × prix` : 0 écart ; `net_paid = ext_sales_price − coupon` : 0 écart | Montants fiables : `ss_net_paid` peut servir de CA net |
| Magasins dans les ventes | `ss_store_sk` de 0 à 11 : 12 valeurs, entre 55 000 et 58 000 lignes chacune | Les 12 magasins de `store` vendent tous. Les volumes sont très homogènes (effet synthétique probable) |

**1. Quelles colonnes sont numériques ?**
Dans `store_sales`, toutes les colonnes : 11 entiers (identifiants `*_sk`, `ss_ticket_number`, `ss_quantity`) et 12 décimaux (prix, montants, taxes, marges). Dans `store` : les identifiants, `s_number_employees`, `s_floor_space`, `s_market_id`, `s_division_id`, `s_company_id`, `s_street_number`, `s_zip`, `s_gmt_offset` et `s_tax_precentage`. Certaines sont des codes et non des mesures (`s_zip`, `*_id`) : il ne faut pas les additionner.

**2. Quelles colonnes représentent des dates ?**
`ss_sold_date_sk` et `s_closed_date_sk` sont des identifiants de jour, à convertir avec `date_dim`. `ss_sold_time_sk` est un identifiant d'heure (table `time_dim`). Les vraies colonnes de date sont `s_rec_start_date` (type `date`) et `s_rec_end_date` (vide, inférée en `string`).

**3. Quelles colonnes sont des identifiants ?**
Toutes les colonnes `*_sk` (clés techniques), `s_store_id` (clé métier du magasin) et `ss_ticket_number` (numéro de ticket). La clé de `store` est `s_store_sk`. `store_sales` n'a pas de clé simple.

**4. Quels champs présentent des valeurs manquantes ?**
`ss_cdemo_sk`, `ss_hdemo_sk`, `ss_addr_sk` et `ss_promo_sk` (moins de 0,1 % des lignes chacun), ainsi que `s_rec_end_date` (100 %). Aucun de ces champs n'est utilisé pour Q3.

**5. Existe-t-il des doublons ?**
Il n'y a **aucun doublon strict**. Les 4 082 couples (ticket, produit) répétés correspondent à des lignes différentes (autre promotion, autre prix, autre quantité). Ce ne sont donc pas des doublons au sens métier, et ils sont conservés.

**6. Certaines valeurs sont-elles incohérentes au regard de leur signification ?**
Dans `store` : `s_closed_date_sk` (dates de fermeture de 1917 à 2141, alors que tous les magasins vendent entre 2001 et 2005) et `s_floor_space` (surfaces de plusieurs millions, sans unité connue). Dans `store_sales`, les montants sont cohérents entre eux. Les montants nets à 0 et les marges négatives s'expliquent métier et ne sont pas des erreurs.

## Source d'enrichissement – `date_dim` (calendrier)

Q3 demande le CA **par année**. Or les ventes ne portent qu'un identifiant de jour (`ss_sold_date_sk`). La table `date_dim` donne la date réelle et l'année de chaque identifiant. Avant de l'utiliser en jointure, on la vérifie (§3.1, §4.8.3).


```python
# Inventaire de date_dim : taille, volume, schema, echantillon
FICHIERS["date_dim"] = f"{DOSSIER_SOURCES}/data/date_dim/date_dim.dat"  # pas de lot data_refresh
df_dates = lire_dat(FICHIERS["date_dim"], COLUMNS["date_dim"])

print(f"date_dim | {os.path.getsize(FICHIERS['date_dim']) / 1024**2:.2f} Mo | "
      f"{df_dates.count()} lignes | {len(df_dates.columns)} colonnes")
df_dates.select("d_date_sk", "d_date", "d_year", "d_moy", "d_dom", "d_day_name").printSchema()
df_dates.select("d_date_sk", "d_date", "d_year", "d_moy", "d_dom", "d_day_name").show(3)
df_dates.agg(F.min("d_date").alias("date_min"), F.max("d_date").alias("date_max")).show()
```

    date_dim | 14.68 Mo | 109573 lignes | 28 colonnes
    root
     |-- d_date_sk: integer (nullable = true)
     |-- d_date: date (nullable = true)
     |-- d_year: integer (nullable = true)
     |-- d_moy: integer (nullable = true)
     |-- d_dom: integer (nullable = true)
     |-- d_day_name: string (nullable = true)
    
    +---------+----------+------+-----+-----+----------+
    |d_date_sk|    d_date|d_year|d_moy|d_dom|d_day_name|
    +---------+----------+------+-----+-----+----------+
    |        0|1900-01-01|  1900|    1|    1|    Monday|
    |        1|1900-01-02|  1900|    1|    2|   Tuesday|
    |        2|1900-01-03|  1900|    1|    3| Wednesday|
    +---------+----------+------+-----+-----+----------+
    only showing top 3 rows


    +----------+----------+
    |  date_min|  date_max|
    +----------+----------+
    |1900-01-01|2199-12-31|
    +----------+----------+
    



```python
# Controles avant jointure
colonnes_utiles = ["d_date_sk", "d_date", "d_year", "d_moy"]

# 1. Cle unique ?
print("d_date_sk distincts :", df_dates.select("d_date_sk").distinct().count(), "/", df_dates.count())

# 2. Valeurs nulles sur les colonnes utilisees ?
print("Valeurs nulles :", compter_nulls(df_dates.select(colonnes_utiles)).first().asDict())

# 3. Coherence : l'annee de d_year est-elle celle de d_date ?
print("d_year different de l'annee de d_date :",
      df_dates.filter(F.col("d_year") != F.year("d_date")).count())

# 4. Couverture : chaque jour de vente existe-t-il dans date_dim ? (anti-jointure)
jours_ventes = df_ventes_tout.select("ss_sold_date_sk").distinct()
jours_orphelins = jours_ventes.join(df_dates, jours_ventes.ss_sold_date_sk == df_dates.d_date_sk, "left_anti")
print("Jours de vente distincts :", jours_ventes.count())
print("Jours de vente absents de date_dim :", jours_orphelins.count())

# 5. Annees couvertes par les ventes
(df_ventes_tout.join(df_dates, df_ventes_tout.ss_sold_date_sk == df_dates.d_date_sk)
 .groupBy("d_year").agg(F.count("*").alias("lignes_vente"),
                        F.min("d_date").alias("premier_jour"),
                        F.max("d_date").alias("dernier_jour"))
 .orderBy("d_year").show())
```

    d_date_sk distincts : 109573 / 109573


    Valeurs nulles : {'d_date_sk': 0, 'd_date': 0, 'd_year': 0, 'd_moy': 0}
    d_year different de l'annee de d_date : 0


    Jours de vente distincts : 1826


    Jours de vente absents de date_dim : 0


    +------+------------+------------+------------+
    |d_year|lignes_vente|premier_jour|dernier_jour|
    +------+------------+------------+------------+
    |  2001|      134873|  2001-01-01|  2001-12-31|
    |  2002|      135084|  2002-01-01|  2002-12-31|
    |  2003|      134773|  2003-01-01|  2003-12-31|
    |  2004|      136014|  2004-01-01|  2004-12-31|
    |  2005|      133467|  2005-01-01|  2005-12-31|
    +------+------------+------------+------------+
    


**Conclusion `date_dim`** : la table est utilisable en jointure.
- Calendrier de 109 573 jours (1900 → 2199), **un jour par ligne**. La clé `d_date_sk` est unique.
- Aucune valeur nulle sur `d_date_sk`, `d_date`, `d_year` et `d_moy`. `d_year` est cohérent avec `d_date`.
- Les **1 826 jours** de vente (du 01/01/2001 au 31/12/2005, soit tous les jours des 5 années) existent tous dans `date_dim` : **0 orphelin**. La jointure `ss_sold_date_sk = d_date_sk` (relation N:1) ne fera perdre aucune vente. Cela confirme le constat du J1.
- Volumes par année très proches (de 133 467 à 136 014 lignes) : **2005 n'est complète qu'avec le lot `data_refresh`**.
