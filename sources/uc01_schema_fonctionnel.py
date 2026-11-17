"""Génère J1_Retail_Intelligence/01_UC01_besoin_exploration/preuves/schema_fonctionnel.pdf (UC-01, §5.1.12).

Représente : utilisateurs -> questions -> indicateurs -> domaines -> fichiers observés,
en distinguant les sources vérifiées des sources souhaitées / absentes.
Usage : .venv/bin/python sources/uc01_schema_fonctionnel.py
"""
from pathlib import Path

from reportlab.graphics.shapes import Drawing, String
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import cm
from reportlab.platypus import Spacer

from pdf_style import BLUE, CELL, GREEN, GREY, LIGHT, NAVY, ORANGE, SUB, TITLE, box, build, link, p
from chemins import UC01, UC01_PREUVES  # noqa: E402

OUT = UC01_PREUVES / "schema_fonctionnel.pdf"

PAGE = landscape(A4)
W, H = PAGE[0] - 4 * cm, 14.2 * cm
d = Drawing(W, H)

COLS = ["Utilisateurs", "Questions décisionnelles", "Indicateurs", "Domaines", "Fichiers / tables"]
cw = [88, 150, 112, 86, 150]
gap = (W - sum(cw)) / 4
X = [sum(cw[:i]) + i * gap for i in range(5)]
for x, w, t in zip(X, cw, COLS):
    d.add(String(x + w / 2, H - 10, t, textAnchor="middle", fontSize=9, fontName="Helvetica-Bold", fillColor=NAVY))


def column(i, items, h, top=H - 26, bottom=8, fill=LIGHT):
    """Répartit verticalement les boîtes d'une colonne ; renvoie {clé: (x, y, w, h)}."""
    n = len(items)
    step = (top - bottom - h) / max(n - 1, 1)
    out = {}
    for k, (key, lines, f, dashed) in enumerate(items):
        y = top - h - k * step
        box(d, X[i], y, cw[i], h, lines, fill=f or fill, dashed=dashed, size=6.6)
        out[key] = (X[i], y, cw[i], h)
    return out


U = column(0, [
    ("DC", ["Direction", "commerciale"], BLUE, False),
    ("RM", ["Responsable", "de magasin"], BLUE, False),
    ("RS", ["Responsable", "des stocks"], BLUE, False),
], 34, top=H - 60, bottom=60)
Q = column(1, [
    ("Q1", ["Q1 CA par catégorie", "Indispensable"], None, False),
    ("Q2", ["Q2 Magasin ou web ?", "Utile"], None, False),
    ("Q3", ["Q3 Magasin le plus performant", "Indispensable"], None, False),
    ("Q4", ["Q4 Jour de semaine le plus actif", "Utile"], None, False),
    ("Q5", ["Q5 Produits en rupture", "Indispensable"], None, False),
    ("Q6", ["Q6 Stock par entrepôt", "Complémentaire"], None, False),
], 26)
K = column(2, [
    ("K02", ["K02 CA par catégorie", "+ K01, K06, K07, K08"], None, False),
    ("K03", ["K03 Part du CA par canal", "+ K04, K05"], None, False),
    ("K09", ["K09 CA par magasin", "+ K04, K05, K08"], None, False),
    ("K10", ["K10 CA moyen / jour sem."], None, False),
    ("K11", ["K11 Couples en rupture"], None, False),
    ("K12", ["K12 Stock par entrepôt"], None, False),
], 26)
D = column(3, [
    ("VM", ["Ventes magasin"], GREEN, False),
    ("VW", ["Ventes web"], GREEN, False),
    ("PR", ["Produits"], GREEN, False),
    ("MA", ["Magasins"], GREEN, False),
    ("TE", ["Temps"], GREEN, False),
    ("ST", ["Stocks"], GREEN, False),
    ("SM", ["Stock magasin", "souhaité"], ORANGE, True),
    ("AF", ["Affluence / effectifs", "souhaité"], ORANGE, True),
], 22)
F = column(4, [
    ("f_ss", ["store_sales.dat", "data/ + data_refresh/"], GREEN, False),
    ("f_ws", ["web_sales.dat", "data/ + data_refresh/"], GREEN, False),
    ("f_it", ["item.dat", "data/ + data_refresh/"], GREEN, False),
    ("f_st", ["store.dat", "data/"], GREEN, False),
    ("f_dd", ["date_dim.dat", "data/"], GREEN, False),
    ("f_in", ["inventory.dat + warehouse.dat", "data/ + data_refresh/"], GREEN, False),
    ("f_na", ["Aucun fichier", "Non disponible"], GREY, True),
], 22)


def r(b):
    x, y, w, h = b
    return x + w, y + h / 2


def l(b):
    x, y, w, h = b
    return x, y + h / 2


for a, b in [("DC", "Q1"), ("DC", "Q2"), ("RM", "Q3"), ("RM", "Q4"), ("RS", "Q5"), ("RS", "Q6")]:
    link(d, *r(U[a]), *l(Q[b]))
for a, b in [("Q1", "K02"), ("Q2", "K03"), ("Q3", "K09"), ("Q4", "K10"), ("Q5", "K11"), ("Q6", "K12")]:
    link(d, *r(Q[a]), *l(K[b]))
for a, b in [("K02", "VM"), ("K02", "VW"), ("K02", "PR"), ("K03", "VM"), ("K03", "VW"), ("K09", "VM"),
             ("K09", "MA"), ("K10", "VM"), ("K10", "TE"), ("K11", "ST"), ("K11", "PR"), ("K12", "ST")]:
    link(d, *r(K[a]), *l(D[b]))
link(d, *r(K["K11"]), *l(D["SM"]), dashed=True)
link(d, *r(K["K10"]), *l(D["AF"]), dashed=True)
for a, b in [("VM", "f_ss"), ("VW", "f_ws"), ("PR", "f_it"), ("MA", "f_st"), ("TE", "f_dd"), ("ST", "f_in")]:
    link(d, *r(D[a]), *l(F[b]))
link(d, *r(D["SM"]), *l(F["f_na"]), dashed=True)
link(d, *r(D["AF"]), *l(F["f_na"]), dashed=True)

story = [
    p("Retail Intelligence Platform &ndash; Schéma fonctionnel UC-01", TITLE),
    p("Des utilisateurs métier aux fichiers réellement observés (§5.1.12)", SUB),
    Spacer(1, 6),
    d,
    Spacer(1, 4),
    p("<b>Légende</b> : cadres verts à trait plein = domaines et fichiers <b>vérifiés</b> (présents, profilés, "
      "relations sans orphelin). Cadres orange / gris en pointillés = sources <b>souhaitées</b> mais absentes du kit "
      "(statut Non disponible). Les domaines présents mais hors périmètre (retours, clients, navigation, avis, "
      "promotions, prix concurrents) sont listés dans inventaire_sources.xlsx.", CELL),
]
build(OUT, story, "UC01 - Schéma fonctionnel", "Retail Intelligence Platform - UC-01 Schéma fonctionnel (preuve)",
      pagesize=PAGE)
