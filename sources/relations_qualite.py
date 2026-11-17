"""Vérification des relations entre tables et analyses ciblées (UC-01, Étape D).

Usage : .venv/bin/python sources/relations_qualite.py
Produit dans J1_Retail_Intelligence/01_UC01_besoin_exploration/preuves/ :
  relations.csv               une ligne par relation testée (enfant -> parent)
  controles_relations.txt     journal complet des contrôles et analyses ciblées
"""
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path.home() / "tp_bigdata"))
from schema import load  # noqa: E402
from chemins import UC01, UC01_PREUVES  # noqa: E402

PREUVES = UC01_PREUVES
out_lines = []


def log(*a):
    s = " ".join(str(x) for x in a)
    print(s, flush=True)
    out_lines.append(s)


_cache = {}


def T(table, folder="data"):
    """Table chargée (mise en cache)."""
    if (table, folder) not in _cache:
        _cache[(table, folder)] = load(table, folder=folder, low_memory=False)
    return _cache[(table, folder)]


def T_all(table):
    """data/ + data_refresh/ si le fichier existe."""
    try:
        return pd.concat([T(table), T(table, "data_refresh")], ignore_index=True)
    except FileNotFoundError:
        return T(table)


# (table enfant, colonne enfant, table parent, colonne parent, usage)
RELATIONS = [
    ("store_sales", "ss_sold_date_sk", "date_dim", "d_date_sk", "Q4, K08"),
    ("store_sales", "ss_sold_time_sk", "time_dim", "t_time_sk", "-"),
    ("store_sales", "ss_item_sk", "item", "i_item_sk", "Q1"),
    ("store_sales", "ss_customer_sk", "customer", "c_customer_sk", "hors périmètre"),
    ("store_sales", "ss_cdemo_sk", "customer_demographics", "cd_demo_sk", "hors périmètre"),
    ("store_sales", "ss_hdemo_sk", "household_demographics", "hd_demo_sk", "hors périmètre"),
    ("store_sales", "ss_addr_sk", "customer_address", "ca_address_sk", "hors périmètre"),
    ("store_sales", "ss_store_sk", "store", "s_store_sk", "Q3"),
    ("store_sales", "ss_promo_sk", "promotion", "p_promo_sk", "K07"),
    ("web_sales", "ws_sold_date_sk", "date_dim", "d_date_sk", "K08"),
    ("web_sales", "ws_ship_date_sk", "date_dim", "d_date_sk", "-"),
    ("web_sales", "ws_sold_time_sk", "time_dim", "t_time_sk", "-"),
    ("web_sales", "ws_item_sk", "item", "i_item_sk", "Q1"),
    ("web_sales", "ws_bill_customer_sk", "customer", "c_customer_sk", "Q2 (par client)"),
    ("web_sales", "ws_ship_customer_sk", "customer", "c_customer_sk", "-"),
    ("web_sales", "ws_bill_addr_sk", "customer_address", "ca_address_sk", "-"),
    ("web_sales", "ws_web_page_sk", "web_page", "wp_web_page_sk", "-"),
    ("web_sales", "ws_web_site_sk", "web_site", "web_site_sk", "-"),
    ("web_sales", "ws_ship_mode_sk", "ship_mode", "sm_ship_mode_sk", "-"),
    ("web_sales", "ws_warehouse_sk", "warehouse", "w_warehouse_sk", "Q6 (piste)"),
    ("web_sales", "ws_promo_sk", "promotion", "p_promo_sk", "K07"),
    ("store_returns", "sr_returned_date_sk", "date_dim", "d_date_sk", "hors périmètre"),
    ("store_returns", "sr_item_sk", "item", "i_item_sk", "hors périmètre"),
    ("store_returns", "sr_customer_sk", "customer", "c_customer_sk", "hors périmètre"),
    ("store_returns", "sr_store_sk", "store", "s_store_sk", "hors périmètre"),
    ("store_returns", "sr_reason_sk", "reason", "r_reason_sk", "hors périmètre"),
    ("web_returns", "wr_returned_date_sk", "date_dim", "d_date_sk", "hors périmètre"),
    ("web_returns", "wr_item_sk", "item", "i_item_sk", "hors périmètre"),
    ("web_returns", "wr_reason_sk", "reason", "r_reason_sk", "hors périmètre"),
    ("web_returns", "wr_web_page_sk", "web_page", "wp_web_page_sk", "hors périmètre"),
    ("inventory", "inv_date_sk", "date_dim", "d_date_sk", "Q5, Q6"),
    ("inventory", "inv_item_sk", "item", "i_item_sk", "Q5"),
    ("inventory", "inv_warehouse_sk", "warehouse", "w_warehouse_sk", "Q6"),
    ("web_clickstreams", "wcs_click_date_sk", "date_dim", "d_date_sk", "hors périmètre"),
    ("web_clickstreams", "wcs_item_sk", "item", "i_item_sk", "hors périmètre"),
    ("web_clickstreams", "wcs_web_page_sk", "web_page", "wp_web_page_sk", "hors périmètre"),
    ("web_clickstreams", "wcs_user_sk", "customer", "c_customer_sk", "hors périmètre"),
    ("web_clickstreams", "wcs_sales_sk", "web_sales", "ws_order_number", "hors périmètre"),
    ("product_reviews", "pr_item_sk", "item", "i_item_sk", "hors périmètre"),
    ("product_reviews", "pr_user_sk", "customer", "c_customer_sk", "hors périmètre"),
    ("product_reviews", "pr_order_sk", "web_sales", "ws_order_number", "hors périmètre"),
    ("customer", "c_current_cdemo_sk", "customer_demographics", "cd_demo_sk", "hors périmètre"),
    ("customer", "c_current_hdemo_sk", "household_demographics", "hd_demo_sk", "hors périmètre"),
    ("customer", "c_current_addr_sk", "customer_address", "ca_address_sk", "hors périmètre"),
    ("household_demographics", "hd_income_band_sk", "income_band", "ib_income_band_sk", "hors périmètre"),
    ("item_marketprices", "imp_item_sk", "item", "i_item_sk", "hors périmètre"),
    ("promotion", "p_item_sk", "item", "i_item_sk", "hors périmètre"),
]


def dtype_label(s):
    nn = s.dropna()
    if pd.api.types.is_integer_dtype(s):
        return "entier"
    if pd.api.types.is_float_dtype(s) and (nn == nn.round()).all():
        return "entier (nulls)"
    return str(s.dtype)


def relations():
    rows = []
    log("=== 1. Relations enfant -> parent (data/ ; parent complété par data_refresh/ en 2e mesure) ===")
    for ct, cc, pt, pc, usage in RELATIONS:
        child, parent = T(ct)[cc], T(pt)[pc]
        parent_all = T_all(pt)[pc]
        nn = child.dropna()
        pset, pset_all = set(parent.dropna()), set(parent_all.dropna())
        orph = int((~nn.isin(pset)).sum())
        orph_all = int((~nn.isin(pset_all)).sum())
        per_parent = nn.value_counts()
        parent_unique = parent.is_unique
        card = ("N:1" if parent_unique else "N:N (parent non unique)")
        status = ("Vérifié" if orph == 0 and parent_unique
                  else "Vérifié (avec data_refresh/)" if orph_all == 0 and parent_unique
                  else "Hypothèse" if orph_all < len(nn) else "Non vérifiée (aucune correspondance)")
        rows.append({
            "enfant": f"{ct}.{cc}", "parent": f"{pt}.{pc}", "type_enfant": dtype_label(child),
            "type_parent": dtype_label(parent), "lignes_enfant": len(child), "nulls_enfant": int(child.isna().sum()),
            "pct_nulls": round(100 * child.isna().mean(), 3), "valeurs_distinctes": int(nn.nunique()),
            "parent_unique": "oui" if parent_unique else "non", "orphelins": orph,
            "orphelins_avec_refresh": orph_all, "pct_orphelins": round(100 * orph / len(nn), 3) if len(nn) else 0,
            "parents_utilises": f"{len(set(nn) & pset)}/{len(pset)}",
            "max_enfants_par_parent": int(per_parent.max()) if len(per_parent) else 0,
            "cardinalite": card, "statut": status, "usage": usage,
        })
        log(f"{ct}.{cc} -> {pt}.{pc} : nulls {rows[-1]['nulls_enfant']}, orphelins {orph} "
            f"(avec refresh {orph_all}), parents utilisés {rows[-1]['parents_utilises']}, {status}")
    pd.DataFrame(rows).to_csv(PREUVES / "relations.csv", index=False)


def doublons():
    log("\n=== 2. Doublons (transaction, produit) dans les ventes ===")
    for t, tk, it in [("store_sales", "ss_ticket_number", "ss_item_sk"),
                      ("web_sales", "ws_order_number", "ws_item_sk")]:
        df = T(t)
        d = df[df.duplicated([tk, it], keep=False)]
        g = d.groupby([tk, it])
        sizes = g.size()
        log(f"{t}: {len(d)} lignes dans {len(sizes)} groupes (taille max {sizes.max()})")
        diff = {c: int((g[c].nunique(dropna=False) > 1).sum()) for c in df.columns if c not in (tk, it)}
        varying = {c: v for c, v in diff.items() if v}
        log("  colonnes qui diffèrent au sein des groupes (nb de groupes) :", varying)
        same = [c for c, v in diff.items() if v == 0]
        log("  colonnes identiques dans tous les groupes :", same)
        ex = d.sort_values([tk, it]).head(4)
        log("  exemple :\n" + ex.to_string(max_cols=12))
        # cohérence de la transaction
        per = df.groupby(tk).agg(**{f"n_{c}": (c, "nunique") for c in df.columns
                                    if c.endswith(("sold_date_sk", "customer_sk", "store_sk"))})
        for c in per.columns:
            log(f"  {t}: transactions avec plus d'une valeur de {c[2:]} : {int((per[c] > 1).sum())} / {len(per)}")


def retours():
    log("\n=== 3. Retours -> ventes ===")
    for rt, rk, ri, rd, rq, st, sk, si, sd, sq in [
        ("store_returns", "sr_ticket_number", "sr_item_sk", "sr_returned_date_sk", "sr_return_quantity",
         "store_sales", "ss_ticket_number", "ss_item_sk", "ss_sold_date_sk", "ss_quantity"),
        ("web_returns", "wr_order_number", "wr_item_sk", "wr_returned_date_sk", "wr_return_quantity",
         "web_sales", "ws_order_number", "ws_item_sk", "ws_sold_date_sk", "ws_quantity"),
    ]:
        r = T_all(rt)
        s = T_all(st)[[sk, si, sd, sq]].drop_duplicates([sk, si])
        m = r.merge(s, left_on=[rk, ri], right_on=[sk, si], how="left", indicator=True)
        found = (m._merge == "both").sum()
        log(f"{rt} (data + refresh, {len(r)} lignes) : retrouvés dans {st} sur (transaction, produit) : "
            f"{found} ({100 * found / len(r):.2f} %)")
        tk_only = r[rk].isin(set(T_all(st)[sk])).sum()
        log(f"  dont numéro de transaction seul présent dans les ventes : {tk_only} ({100 * tk_only / len(r):.2f} %)")
        mm = m[m._merge == "both"]
        if len(mm):
            delay = mm[rd] - mm[sd]
            log(f"  délai retour - vente (jours) : min {delay.min()}, médiane {delay.median()}, max {delay.max()}, "
                f"négatif {int((delay < 0).sum())}, > 365 j {int((delay > 365).sum())}")
            log(f"  quantité retournée > quantité vendue : {int((mm[rq] > mm[sq]).sum())}")


def refresh():
    log("\n=== 4. data/ vs data_refresh/ ===")
    for t, tk, dc in [("store_sales", "ss_ticket_number", "ss_sold_date_sk"),
                      ("web_sales", "ws_order_number", "ws_sold_date_sk")]:
        a, b = T(t), T(t, "data_refresh")
        common = set(a[tk]) & set(b[tk])
        log(f"{t}: transactions communes aux deux dossiers : {len(common)}")
        log(f"  lignes du 13/12/2005 (38697) : data {int((a[dc] == 38697).sum())}, refresh {int((b[dc] == 38697).sum())}")
        both = pd.concat([a, b])
        log(f"  lignes entièrement identiques entre data et refresh : {int(both.duplicated().sum()) - int(a.duplicated().sum()) - int(b.duplicated().sum())}")
        log(f"  numéros de transaction : data {a[tk].min()}-{a[tk].max()}, refresh {b[tk].min()}-{b[tk].max()}")
    a, b = T("inventory"), T("inventory", "data_refresh")
    log(f"inventory: dates refresh {sorted(b.inv_date_sk.unique())} ; lignes du relevé 38696 : data "
        f"{int((a.inv_date_sk == 38696).sum())}, refresh {int((b.inv_date_sk == 38696).sum())}")
    k = ["inv_date_sk", "inv_item_sk", "inv_warehouse_sk"]
    m = a[a.inv_date_sk == 38696].merge(b[b.inv_date_sk == 38696], on=k, suffixes=("_d", "_r"))
    log(f"  relevé 38696 présent dans les deux : {len(m)} couples communs, quantités différentes : "
        f"{int((m.inv_quantity_on_hand_d.fillna(-1) != m.inv_quantity_on_hand_r.fillna(-1)).sum())}")


def clics():
    log("\n=== 5. Clics -> ventes web ===")
    c = T("web_clickstreams")
    ws = T("web_sales")
    nn = c[c.wcs_sales_sk.notna()]
    log(f"clics avec wcs_sales_sk : {len(nn)} / {len(c)} ({100 * len(nn) / len(c):.1f} %)")
    m = nn.merge(ws[["ws_order_number", "ws_item_sk", "ws_sold_date_sk", "ws_bill_customer_sk"]],
                 left_on=["wcs_sales_sk", "wcs_item_sk"], right_on=["ws_order_number", "ws_item_sk"], how="left")
    ok = m.ws_order_number.notna()
    log(f"  correspondance (wcs_sales_sk, wcs_item_sk) = (ws_order_number, ws_item_sk) : {int(ok.sum())} / {len(m)}")
    mm = m[ok]
    log(f"  même date clic / vente : {(mm.wcs_click_date_sk == mm.ws_sold_date_sk).mean():.2%} ; "
        f"même client (wcs_user_sk = ws_bill_customer_sk) : {(mm.wcs_user_sk == mm.ws_bill_customer_sk).mean():.2%}")
    log(f"  clics avec vente mais sans utilisateur : {int(nn.wcs_user_sk.isna().sum())}")


def entrepots():
    log("\n=== 6. Entrepôts ===")
    inv, wh = T("inventory"), T("warehouse")
    log("w_warehouse_sk :", sorted(wh.w_warehouse_sk), "| inv_warehouse_sk :", sorted(inv.inv_warehouse_sk.unique()))
    log("ws_warehouse_sk :", sorted(T("web_sales").ws_warehouse_sk.dropna().astype(int).unique()))


def clients_canaux():
    log("\n=== 7. Clients communs aux deux canaux (Q2 par client) ===")
    a = set(T("store_sales").ss_customer_sk.dropna())
    b = set(T("web_sales").ws_bill_customer_sk.dropna())
    log(f"clients magasin {len(a)}, clients web {len(b)}, communs {len(a & b)}, "
        f"clients référentiel {len(T('customer'))}")


if __name__ == "__main__":
    log(f"Contrôles des relations - {datetime.now():%Y-%m-%d %H:%M} - source ~/tp_bigdata/extract/retail_project")
    relations()
    doublons()
    retours()
    refresh()
    clics()
    entrepots()
    clients_canaux()
    (PREUVES / "controles_relations.txt").write_text("\n".join(out_lines) + "\n", encoding="utf-8")
