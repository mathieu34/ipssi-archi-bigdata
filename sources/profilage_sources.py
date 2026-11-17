"""Profilage de tous les fichiers du kit (UC-01, Étape C).

Usage : .venv/bin/python sources/profilage_sources.py
Produit dans J1_Retail_Intelligence/01_UC01_besoin_exploration/preuves/ :
  arborescence.txt          arborescence des données avec tailles
  inventaire_fichiers.csv   une ligne par fichier
  inventaire_colonnes.csv   une ligne par colonne de chaque fichier .dat
  apercus/*.txt             5 premières lignes brutes de chaque fichier
  profilage_log.txt         journal d'exécution
Noms de colonnes : schema.py (~/tp_bigdata), repris de la spécification TPCx-BB.
"""
import re
import sys
import time
from collections import Counter
from datetime import datetime
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path.home() / "tp_bigdata"))
from schema import COLUMNS  # noqa: E402
from chemins import UC01, UC01_PREUVES  # noqa: E402

BASE = Path.home() / "tp_bigdata" / "extract" / "retail_project"
PREUVES = UC01_PREUVES
APERCUS = PREUVES / "apercus"

# Clés à tester par table (simple ou composite)
KEYS = {
    "customer": ["c_customer_sk"], "customer_address": ["ca_address_sk"],
    "customer_demographics": ["cd_demo_sk"], "date_dim": ["d_date_sk"],
    "household_demographics": ["hd_demo_sk"], "income_band": ["ib_income_band_sk"],
    "inventory": ["inv_date_sk", "inv_item_sk", "inv_warehouse_sk"], "item": ["i_item_sk"],
    "item_marketprices": ["imp_sk"], "product_reviews": ["pr_review_sk"], "promotion": ["p_promo_sk"],
    "reason": ["r_reason_sk"], "ship_mode": ["sm_ship_mode_sk"], "store": ["s_store_sk"],
    "store_returns": ["sr_ticket_number", "sr_item_sk"],
    "store_sales": ["ss_ticket_number", "ss_item_sk"], "time_dim": ["t_time_sk"],
    "warehouse": ["w_warehouse_sk"], "web_clickstreams": None, "web_page": ["wp_web_page_sk"],
    "web_returns": ["wr_order_number", "wr_item_sk"],
    "web_sales": ["ws_order_number", "ws_item_sk"], "web_site": ["web_site_sk"],
}
# Colonne de date principale (pour la période couverte)
DATE_COL = {
    "inventory": "inv_date_sk", "store_sales": "ss_sold_date_sk", "web_sales": "ws_sold_date_sk",
    "store_returns": "sr_returned_date_sk", "web_returns": "wr_returned_date_sk",
    "web_clickstreams": "wcs_click_date_sk", "product_reviews": "pr_review_date",
}

RE_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
RE_TIME = re.compile(r"^\d{2}:\d{2}:\d{2}$")

log_lines = []


def log(*a):
    s = " ".join(str(x) for x in a)
    print(s, flush=True)
    log_lines.append(s)


def human(n):
    for u in ["o", "Ko", "Mo", "Go"]:
        if n < 1024:
            return f"{n:.1f} {u}" if u != "o" else f"{n} o"
        n /= 1024
    return f"{n:.1f} To"


def scan_raw(path):
    """Lignes, distribution du nombre de champs, lignes non UTF-8."""
    fields, n, bad = Counter(), 0, 0
    with open(path, "rb") as fh:
        for line in fh:
            n += 1
            fields[line.count(b"|") + 1] += 1
            try:
                line.decode("utf-8")
            except UnicodeDecodeError:
                bad += 1
    return n, fields, bad


def col_type(s):
    nn = s.dropna()
    if nn.empty:
        return "vide (100 % nul)", None
    if pd.api.types.is_integer_dtype(s):
        return "entier", None
    if pd.api.types.is_float_dtype(s):
        if (nn == nn.round()).all() and s.isna().any():
            return "entier (lu en décimal car valeurs nulles)", None
        return "décimal", None
    sample = nn.astype(str).head(2000)
    if sample.map(lambda v: bool(RE_DATE.match(v))).all():
        return "date AAAA-MM-JJ (texte)", None
    if sample.map(lambda v: bool(RE_TIME.match(v))).all():
        return "heure HH:MM:SS (texte)", None
    return "texte", int(nn.astype(str).str.len().max())


def tree():
    out = [f"{BASE}  (relevé le {datetime.now():%Y-%m-%d %H:%M})"]
    for top in sorted(p for p in BASE.iterdir() if p.is_dir()):
        files = sorted(top.rglob("*.*"))
        out.append(f"├── {top.name}/   ({len(files)} fichiers, {human(sum(f.stat().st_size for f in files))})")
        dirs = sorted(d for d in top.iterdir() if d.is_dir())
        for i, d in enumerate(dirs):
            last = i == len(dirs) - 1
            out.append(f"│   {'└──' if last else '├──'} {d.name}/")
            for f in sorted(d.iterdir()):
                out.append(f"│   {'    ' if last else '│   '}    {f.name}  ({human(f.stat().st_size)})")
    return "\n".join(out)


def main():
    t0 = time.time()
    APERCUS.mkdir(parents=True, exist_ok=True)
    (PREUVES / "arborescence.txt").write_text(tree() + "\n", encoding="utf-8")
    log(f"Profilage démarré {datetime.now():%Y-%m-%d %H:%M:%S} - base {BASE}")

    dd = pd.read_csv(BASE / "data/date_dim/date_dim.dat", sep="|", header=None,
                     names=COLUMNS["date_dim"], usecols=["d_date_sk", "d_date"], index_col=False)
    date_of = dict(zip(dd.d_date_sk, dd.d_date))
    data_keys = {}  # clés de data/ pour mesurer le recouvrement avec data_refresh/

    files_rows, cols_rows = [], []
    for path in sorted(BASE.rglob("*.*")):
        folder = path.relative_to(BASE).parts[0]
        table = path.parent.name
        rel = path.relative_to(BASE.parent)
        size = path.stat().st_size
        t1 = time.time()
        n, fields, bad = scan_raw(path)
        with open(path, encoding="utf-8", errors="replace") as fh:
            head = [next(fh, "") for _ in range(5)]
        (APERCUS / f"{folder}__{path.name}.txt").write_text(
            f"# {rel} - 5 premières lignes brutes\n" + "".join(head), encoding="utf-8")

        row = {
            "dossier": folder, "table": table, "fichier": path.name, "chemin": str(rel),
            "format": path.suffix.lstrip("."), "taille_octets": size, "taille": human(size),
            "lignes": n, "encodage_non_utf8": bad,
        }
        if path.suffix == ".csv":
            row.update({"separateur": ",", "entete": "oui (1re ligne) puis sections de listes",
                        "colonnes_observees": f"{len(head[0].split(','))} (ligne 1)",
                        "colonnes_attendues": "hors schéma TPCx-BB",
                        "lignes_hors_format": "structure multi-sections"})
            files_rows.append(row)
            log(f"{rel}: {n} lignes (csv) {time.time() - t1:.1f}s")
            continue

        names = COLUMNS[table]
        df = pd.read_csv(path, sep="|", header=None, names=names, index_col=False, low_memory=False)
        expected = len(names)
        row.update({
            "separateur": "|", "entete": "non",
            "colonnes_observees": ", ".join(f"{k} champs : {v} lignes" for k, v in fields.most_common()),
            "colonnes_attendues": expected,
            "lignes_hors_format": n - fields.get(expected, 0),
            "doublons_lignes_completes": int(df.duplicated().sum()),
        })
        key = KEYS.get(table)
        if key:
            dup = int(df.duplicated(key).sum())
            nulls = int(df[key].isna().any(axis=1).sum())
            row.update({"cle_testee": " + ".join(key), "cle_doublons": dup, "cle_nulls": nulls,
                        "cle_unique": "oui" if dup == 0 and nulls == 0 else "non"})
            if len(key) == 1:
                k = set(df[key[0]].dropna().astype("int64"))
                if folder == "data":
                    data_keys[table] = k
                elif table in data_keys:
                    row["refresh_cles_deja_dans_data"] = len(k & data_keys[table])
        else:
            row.update({"cle_testee": "aucune clé identifiée", "cle_unique": "non applicable"})
        dc = DATE_COL.get(table)
        if dc:
            s = df[dc].dropna()
            if dc.endswith("_sk"):
                lo, hi = int(s.min()), int(s.max())
                row.update({"date_min": f"{lo} ({date_of.get(lo, '?')})",
                            "date_max": f"{hi} ({date_of.get(hi, '?')})"})
            else:
                row.update({"date_min": s.min(), "date_max": s.max()})
        with_null, all_null = [], []
        for i, c in enumerate(names, 1):
            s = df[c]
            typ, maxlen = col_type(s)
            nnull = int(s.isna().sum())
            if nnull:
                with_null.append(c)
            if nnull == len(s):
                all_null.append(c)
            nn = s.dropna()
            is_num = pd.api.types.is_numeric_dtype(s) and not nn.empty
            cols_rows.append({
                "dossier": folder, "table": table, "position": i, "colonne": c, "type_observe": typ,
                "longueur_max": maxlen, "nb_nulls": nnull, "pct_nulls": round(100 * nnull / len(s), 3) if len(s) else 0,
                "nb_distincts": int(s.nunique()),
                "min": nn.min() if is_num else "", "max": nn.max() if is_num else "",
                "exemple": (str(nn.iloc[0])[:60] if not nn.empty else ""),
                "unique_non_nul": "oui" if nnull == 0 and s.is_unique else "non",
            })
        row.update({"nb_colonnes_avec_nulls": len(with_null), "colonnes_avec_nulls": ", ".join(with_null),
                    "colonnes_100pct_nulles": ", ".join(all_null)})
        files_rows.append(row)
        log(f"{rel}: {n} lignes, {expected} colonnes, {time.time() - t1:.1f}s")
        del df

    pd.DataFrame(files_rows).to_csv(PREUVES / "inventaire_fichiers.csv", index=False)
    pd.DataFrame(cols_rows).to_csv(PREUVES / "inventaire_colonnes.csv", index=False)
    log(f"Terminé en {time.time() - t0:.0f}s : {len(files_rows)} fichiers, {len(cols_rows)} colonnes")
    (PREUVES / "profilage_log.txt").write_text("\n".join(log_lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
