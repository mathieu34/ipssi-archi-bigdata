"""Contrôles sur les données qui servent à définir les KPI (UC-01, Étape B).

Usage : .venv/bin/python sources/controles_kpi.py > J1_Retail_Intelligence/01_UC01_besoin_exploration/preuves/controles_kpi.txt
S'appuie sur schema.py du dossier ~/tp_bigdata (noms de colonnes TPCx-BB, fichiers sans en-tête).
"""
import sys
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path.home() / "tp_bigdata"))
from schema import load  # noqa: E402

TOL = 0.011  # tolérance d'arrondi au centime


def ok_ratio(a, b):
    return f"{((a - b).abs() < TOL).mean():.4%}"


print(f"Contrôles KPI - exécuté le {datetime.now():%Y-%m-%d %H:%M}")
print("Source : ~/tp_bigdata/extract/retail_project/data/\n")

dd = load("date_dim", usecols=["d_date_sk", "d_date"])
date_of = dict(zip(dd.d_date_sk, dd.d_date))

for chan, t, p, ticket, store_col in [
    ("MAGASIN", "store_sales", "ss", "ss_ticket_number", "ss_store_sk"),
    ("WEB", "web_sales", "ws", "ws_order_number", None),
]:
    df = load(t)
    print(f"=== {t} ({chan}) ===")
    print("lignes :", len(df))
    cols = [f"{p}_sold_date_sk", f"{p}_item_sk", ticket, f"{p}_quantity", f"{p}_sales_price",
            f"{p}_ext_sales_price", f"{p}_ext_list_price", f"{p}_ext_discount_amt",
            f"{p}_coupon_amt", f"{p}_net_paid"] + ([store_col] if store_col else [])
    print("valeurs nulles par colonne :")
    print(df[cols].isna().sum().to_string())
    print("transactions distinctes (", ticket, ") :", df[ticket].nunique())
    dmin, dmax = df[f"{p}_sold_date_sk"].min(), df[f"{p}_sold_date_sk"].max()
    print(f"période : {dmin} ({date_of.get(dmin)}) -> {dmax} ({date_of.get(dmax)})")
    print("ext_sales_price = quantity * sales_price :",
          ok_ratio(df[f"{p}_quantity"] * df[f"{p}_sales_price"], df[f"{p}_ext_sales_price"]))
    print("ext_discount_amt = ext_list_price - ext_sales_price :",
          ok_ratio(df[f"{p}_ext_list_price"] - df[f"{p}_ext_sales_price"], df[f"{p}_ext_discount_amt"]))
    print("net_paid = ext_sales_price - coupon_amt :",
          ok_ratio(df[f"{p}_ext_sales_price"] - df[f"{p}_coupon_amt"], df[f"{p}_net_paid"]))
    print("quantités <= 0 :", (df[f"{p}_quantity"] <= 0).sum(),
          "| net_paid < 0 :", (df[f"{p}_net_paid"] < 0).sum())
    print("doublons (transaction, produit) :", df.duplicated([ticket, f"{p}_item_sk"]).sum(),
          "| doublons de ligne complète :", df.duplicated().sum())
    if store_col:
        print("magasins distincts :", df[store_col].nunique(),
              "| tickets rattachés à plusieurs magasins :",
              (df.groupby(ticket)[store_col].nunique() > 1).sum())
    print()

print("=== Correspondance des clés (orphelins) ===")
it = load("item", usecols=["i_item_sk", "i_category"])
st = load("store", usecols=["s_store_sk", "s_store_id"])
ss = load("store_sales", usecols=["ss_item_sk", "ss_store_sk", "ss_sold_date_sk"])
ws = load("web_sales", usecols=["ws_item_sk", "ws_sold_date_sk"])
print("store_sales.ss_item_sk absent de item :", (~ss.ss_item_sk.isin(it.i_item_sk)).sum())
print("store_sales.ss_store_sk absent de store :", (~ss.ss_store_sk.isin(st.s_store_sk)).sum())
print("store_sales.ss_sold_date_sk absent de date_dim :", (~ss.ss_sold_date_sk.isin(dd.d_date_sk)).sum())
print("web_sales.ws_item_sk absent de item :", (~ws.ws_item_sk.isin(it.i_item_sk)).sum())
print("web_sales.ws_sold_date_sk absent de date_dim :", (~ws.ws_sold_date_sk.isin(dd.d_date_sk)).sum())
print()

print("=== item / store ===")
print("item : lignes", len(it), "| i_item_sk unique :", it.i_item_sk.is_unique,
      "| i_category nulle :", it.i_category.isna().sum(), "| catégories distinctes :", it.i_category.nunique())
print("store : lignes", len(st), "| s_store_id distincts :", st.s_store_id.nunique())
print()

print("=== inventory ===")
inv = load("inventory")
wh = load("warehouse", usecols=["w_warehouse_sk"])
print("lignes :", len(inv))
print("valeurs nulles :")
print(inv.isna().sum().to_string())
ds = np.sort(inv.inv_date_sk.unique())
print("dates de relevé distinctes :", len(ds), f"| {ds[0]} ({date_of.get(ds[0])}) -> {ds[-1]} ({date_of.get(ds[-1])})")
print("écart entre relevés (jours) :", pd.Series(np.diff(ds)).value_counts().to_dict())
print("entrepôts dans inventory :", inv.inv_warehouse_sk.nunique(), "| lignes de warehouse :", len(wh))
print("quantité min / max :", inv.inv_quantity_on_hand.min(), "/", inv.inv_quantity_on_hand.max())
last = inv[inv.inv_date_sk == ds[-1]]
print(f"dernier relevé ({date_of.get(ds[-1])}) : lignes {len(last)}",
      "| quantité = 0 :", (last.inv_quantity_on_hand == 0).sum(),
      "| quantité nulle (vide) :", last.inv_quantity_on_hand.isna().sum(),
      "| produits distincts :", last.inv_item_sk.nunique())
orph = last[~last.inv_item_sk.isin(it.i_item_sk)]
print("dernier relevé : lignes dont inv_item_sk est absent de item :", len(orph),
      "| produits concernés :", orph.inv_item_sk.nunique(),
      "| dont quantité = 0 :", (orph.inv_quantity_on_hand == 0).sum())
print("item_sk min/max : item", it.i_item_sk.min(), "/", it.i_item_sk.max(),
      "| inventory", inv.inv_item_sk.min(), "/", inv.inv_item_sk.max())
print("lignes par (produit, entrepôt) au dernier relevé - max :",
      last.groupby(["inv_item_sk", "inv_warehouse_sk"]).size().max())
