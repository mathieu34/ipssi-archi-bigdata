"""Démonstration locale Bronze -> Silver -> Gold (preuve de traitement réellement effectué, UC-02).

Ce n'est PAS l'architecture cible déployée : HDFS, NiFi et Spark ne sont pas installés au Jour 1.
La démonstration applique les règles de l'architecture (architecture_cible.pdf, gouvernance.pdf) avec le repli
documenté : système de fichiers local (même arborescence /datalake/...) et Python (pandas + pyarrow) à la place de
Spark. Périmètre : store_sales (data/ + data_refresh/), item (data/ + data_refresh/), date_dim.

Usage : .venv/bin/python sources/demo_bronze_silver_gold.py
Sorties : datalake_demo/ (non versionné) et preuves/demo_bronze_silver_gold/ de l'UC-02.
"""
import hashlib
import json
import shutil
import sys
import time
from datetime import date, datetime
from pathlib import Path

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

from chemins import DONNEES, PROJET, UC02_PREUVES  # noqa: E402
from schema import COLUMNS  # noqa: E402

SOURCE = DONNEES
LAKE = PROJET / "datalake_demo"
PREUVE = UC02_PREUVES / "demo_bronze_silver_gold"
TODAY = date.today().isoformat()
LOTS = ["data", "data_refresh"]
TABLES = {"store_sales": LOTS, "item": LOTS, "date_dim": ["data"]}
journal = []


def log(msg):
    line = f"{datetime.now():%H:%M:%S} {msg}"
    print(line, flush=True)
    journal.append(line)


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def read_dat(path, table):
    """Lecture typée : clés *_sk et entiers en Int64 (accepte le vide), texte en string."""
    df = pd.read_csv(path, sep="|", header=None, names=COLUMNS[table], index_col=False,
                     dtype=str, keep_default_na=False, na_values=[""])
    for c in df.columns:
        s = df[c]
        if c.endswith("_sk") or c in ("ss_ticket_number", "ss_quantity", "d_year", "d_moy", "d_dow"):
            df[c] = pd.to_numeric(s).astype("Int64")
        elif table == "store_sales":
            df[c] = pd.to_numeric(s).astype("float64")
    return df


# ------------------------------------------------------------------ 0. préparation
t0 = time.time()
if LAKE.exists():
    shutil.rmtree(LAKE)  # répertoire de démonstration généré par ce script uniquement
if PREUVE.exists():
    shutil.rmtree(PREUVE)
PREUVE.mkdir(parents=True)
log(f"Démonstration Bronze -> Silver -> Gold ; source {SOURCE} ; lac de démonstration {LAKE}")

# ------------------------------------------------------------------ 1. BRONZE : dépôt sans modification
log("=== 1. BRONZE : dépôt des fichiers d'origine, empreinte SHA-256, manifeste par lot")
for lot in LOTS:
    manifeste = {"lot": lot, "origine": "retail_project.zip (TPCx-BB, synthétique)", "date_ingestion": TODAY,
                 "schema": "schema.py (conforme à la spécification TPCx-BB v1.7.0, annexe B.2)", "fichiers": []}
    for table, lots in TABLES.items():
        if lot not in lots:
            continue
        src = SOURCE / lot / table / f"{table}.dat"
        dst_dir = LAKE / "bronze" / "tpcx_bb" / table / f"lot={lot}" / f"date_ingestion={TODAY}"
        dst_dir.mkdir(parents=True)
        dst = dst_dir / src.name
        shutil.copy2(src, dst)
        h_src, h_dst = sha256(src), sha256(dst)
        with open(dst, "rb") as fh:
            n = sum(1 for _ in fh)
        manifeste["fichiers"].append({"table": table, "fichier": src.name, "octets": dst.stat().st_size,
                                      "lignes": n, "champs_attendus": len(COLUMNS[table]), "sha256": h_dst})
        log(f"  {table} lot={lot} : {n} lignes, {dst.stat().st_size} octets, copie identique à la source : "
            f"{'oui' if h_src == h_dst else 'NON'}")
    mdir = LAKE / "bronze" / "_manifestes"
    mdir.mkdir(parents=True, exist_ok=True)
    (mdir / f"manifeste_lot={lot}.json").write_text(json.dumps(manifeste, indent=2, ensure_ascii=False),
                                                   encoding="utf-8")
    shutil.copy2(mdir / f"manifeste_lot={lot}.json", PREUVE / f"manifeste_lot={lot}.json")

# ------------------------------------------------------------------ 2. SILVER
log("=== 2. SILVER : typage, contrôles, quarantaine, colonnes de traçabilité, Parquet")


def bronze_files(table):
    return sorted((LAKE / "bronze" / "tpcx_bb" / table).glob("lot=*/date_ingestion=*/*.dat"))


def with_trace(df, path):
    lot = path.parent.parent.name.split("=", 1)[1]
    df["_lot"] = lot
    df["_fichier_source"] = str(path.relative_to(LAKE))
    df["_date_ingestion"] = TODAY
    df["_id_ligne"] = [f"{lot}:{path.stem}:{i + 1}" for i in range(len(df))]
    return df


def count_fields_ok(path, expected):
    with open(path, "rb") as fh:
        return [line.count(b"|") + 1 == expected for line in fh]


# date_dim
dd = pd.concat([with_trace(read_dat(p, "date_dim"), p) for p in bronze_files("date_dim")], ignore_index=True)
assert dd.d_date_sk.is_unique
dd["d_date"] = pd.to_datetime(dd["d_date"])
dd = dd.drop(columns=["d_holiday"])  # neutralisée : Y pour 100 % des jours (controle_date_dim.txt)
(LAKE / "silver" / "referentiels" / "date_dim").mkdir(parents=True)
dd.to_parquet(LAKE / "silver" / "referentiels" / "date_dim" / "part-0.parquet", index=False)
log(f"  date_dim : {len(dd)} lignes, clé unique, d_holiday écartée -> silver/referentiels/date_dim/")

# item : fusion des deux lots + rognage du texte
it = pd.concat([with_trace(read_dat(p, "item"), p) for p in bronze_files("item")], ignore_index=True)
q03 = it.i_item_sk.is_unique
avant = int((it["i_item_desc"].fillna("") != it["i_item_desc"].fillna("").str.strip()).sum())
it["i_item_desc"] = it["i_item_desc"].str.strip()
(LAKE / "silver" / "referentiels" / "item").mkdir(parents=True)
it.to_parquet(LAKE / "silver" / "referentiels" / "item" / "part-0.parquet", index=False)
log(f"  item : {len(it)} lignes (data + data_refresh), Q03 clé unique : {q03}, "
    f"{avant} descriptions rognées -> silver/referentiels/item/")

# store_sales : contrôles ligne à ligne
parts, rejets = [], []
for p in bronze_files("store_sales"):
    ok_fields = count_fields_ok(p, len(COLUMNS["store_sales"]))
    df = with_trace(read_dat(p, "store_sales"), p)
    motif = pd.Series("", index=df.index)
    motif[~pd.Series(ok_fields, index=df.index)] += "Q02 nb_champs;"
    motif[~df.ss_item_sk.isin(it.i_item_sk)] += "Q04 produit_inconnu;"
    motif[~df.ss_sold_date_sk.isin(dd.d_date_sk)] += "Q04 date_inconnue;"
    motif[(df.ss_quantity * df.ss_sales_price - df.ss_ext_sales_price).abs() > 0.011] += "Q05 ext_sales_price;"
    motif[(df.ss_ext_sales_price - df.ss_coupon_amt - df.ss_net_paid).abs() > 0.011] += "Q05 net_paid;"
    motif[~(df.ss_quantity > 0)] += "Q06 quantite;"
    bad = motif != ""
    rejets.append(df[bad].assign(_motif=motif[bad]))
    parts.append(df[~bad])
    log(f"  store_sales {p.parent.parent.name} : {len(df)} lignes lues, {int(bad.sum())} en quarantaine")
ss = pd.concat(parts, ignore_index=True)
qt = pd.concat(rejets, ignore_index=True)
ss["canal"] = "MAGASIN"
cal = dd.set_index("d_date_sk")[["d_year", "d_moy"]]
ss["annee"] = ss.ss_sold_date_sk.map(cal.d_year).astype("int32")
ss["mois"] = ss.ss_sold_date_sk.map(cal.d_moy).astype("int32")
out = LAKE / "silver" / "ventes" / "store_sales"
pq.write_to_dataset(pa.Table.from_pandas(ss, preserve_index=False), root_path=str(out),
                    partition_cols=["annee", "mois"])
(LAKE / "silver" / "_quarantaine" / "store_sales").mkdir(parents=True)
qt.to_parquet(LAKE / "silver" / "_quarantaine" / "store_sales" / "part-0.parquet", index=False)
nb_part = len(list(out.glob("annee=*/mois=*")))
log(f"  store_sales : {len(ss)} lignes valides écrites en Parquet partitionné ({nb_part} partitions annee/mois), "
    f"{len(qt)} en quarantaine ; doublons (ticket, produit) conservés : "
    f"{int(ss.duplicated(['ss_ticket_number', 'ss_item_sk']).sum())}")

# ------------------------------------------------------------------ 3. GOLD
log("=== 3. GOLD : agrégat KPI K02 (CA net par catégorie et par année) et réconciliation")
silver = pd.read_parquet(out)
g = silver.merge(it[["i_item_sk", "i_category"]], left_on="ss_item_sk", right_on="i_item_sk", how="left")
kpi = (g.groupby(["annee", "i_category"], observed=True)
       .agg(ca_net=("ss_net_paid", "sum"), quantite=("ss_quantity", "sum"),
            nb_transactions=("ss_ticket_number", "nunique"), nb_lignes=("ss_net_paid", "size"))
       .reset_index().rename(columns={"i_category": "categorie"}))
kpi["annee"] = kpi["annee"].astype(int)
kpi["ca_net"] = kpi["ca_net"].round(2)
gdir = LAKE / "gold" / "kpi" / "k02_ca_categorie_annee"
gdir.mkdir(parents=True)
kpi.to_parquet(gdir / "part-0.parquet", index=False)
kpi.to_csv(PREUVE / "gold_k02_ca_categorie_annee.csv", index=False, sep=";", decimal=",")
shutil.copy2(gdir / "part-0.parquet", PREUVE / "gold_k02_ca_categorie_annee.parquet")

raw_total = sum(read_dat(p, "store_sales").ss_net_paid.sum() for p in bronze_files("store_sales"))
checks = {
    "Q10 lignes Bronze = Silver + quarantaine": (674211, len(silver) + len(qt)),
    "Q10 CA net Silver = somme Gold": (round(silver.ss_net_paid.sum(), 2), round(kpi.ca_net.sum(), 2)),
    "CA net Bronze (brut) = Silver + quarantaine": (round(raw_total, 2),
                                                    round(silver.ss_net_paid.sum() + qt.ss_net_paid.sum(), 2)),
    "Q11 tickets distincts = 90 000": (90000, silver.ss_ticket_number.nunique()),
    "jointure produit sans perte (catégorie vide)": (0, int(g.i_category.isna().sum())),
}
for k, (a, b) in checks.items():
    log(f"  {k} : {a} / {b} -> {'OK' if abs(float(a) - float(b)) < 0.01 else 'ÉCART'}")

# ------------------------------------------------------------------ 4. preuves
log("=== 4. Volumes : fichier texte .dat (Bronze) vs Parquet compressé (Silver)")
dat = sum(p.stat().st_size for p in bronze_files("store_sales"))
par = sum(p.stat().st_size for p in out.rglob("*.parquet"))
log(f"  store_sales : .dat {dat / 1e6:.1f} Mo -> Parquet {par / 1e6:.1f} Mo (rapport {dat / par:.1f})")
schema_txt = pq.read_schema(next(out.rglob("*.parquet")))
(PREUVE / "schema_parquet_silver_store_sales.txt").write_text(
    "# Schéma Parquet de silver/ventes/store_sales (types stockés dans le fichier)\n" + str(schema_txt) + "\n",
    encoding="utf-8")


def tree(root):
    lines = [f"{root.name}/"]
    for p in sorted(root.rglob("*")):
        rel = p.relative_to(root)
        if p.is_file() and p.suffix == ".parquet" and rel.parts[0] == "silver" and "annee=" in str(rel):
            if p.parent.name != "mois=1":
                continue  # une partition montrée par année
        depth = len(rel.parts)
        size = f"  ({p.stat().st_size / 1e6:.2f} Mo)" if p.is_file() else "/"
        if p.is_dir() and "mois=" in p.name and p.name != "mois=1":
            continue
        lines.append("    " * depth + p.name + size)
    return "\n".join(lines)


(PREUVE / "arborescence_datalake_demo.txt").write_text(
    "# Arborescence produite par la démonstration (une seule partition mois=1 affichée par année)\n"
    + tree(LAKE) + "\n", encoding="utf-8")
log(f"Terminé en {time.time() - t0:.0f} s")
(PREUVE / "journal_execution.txt").write_text(
    "# Journal d'exécution de sources/demo_bronze_silver_gold.py (démonstration locale, repli documenté :\n"
    "# système de fichiers local au lieu de HDFS, pandas + pyarrow au lieu de Spark)\n" + "\n".join(journal) + "\n",
    encoding="utf-8")
