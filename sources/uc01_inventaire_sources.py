"""Génère J1_Retail_Intelligence/01_UC01_besoin_exploration/inventaire_sources.xlsx (UC-01, Étape C).

Prérequis : avoir lancé profilage_sources.py (produit les CSV dans preuves/).
Usage : .venv/bin/python sources/uc01_inventaire_sources.py
"""
from pathlib import Path

import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from chemins import UC01, UC01_PREUVES  # noqa: E402

PREUVES = UC01_PREUVES
OUT = UC01 / "inventaire_sources.xlsx"

NAVY, LIGHT = "1B3350", "EEF3F7"
FILLS = {"Vérifié": "D9EFD9", "Déduit": "DDEBF7", "Hypothèse": "FFF1CC", "Non disponible": "F8D7D7",
         "À valider": "FCE4D6"}

files = pd.read_csv(PREUVES / "inventaire_fichiers.csv")
cols = pd.read_csv(PREUVES / "inventaire_colonnes.csv")
# colonne mixte (texte pour les CSV d'audit) : forcer le numérique pour les .dat
files["lignes_hors_format"] = pd.to_numeric(files.lignes_hors_format, errors="coerce")

from annotations_sources import ANNOT, AUDIT  # noqa: E402


def type_summary(df):
    s = df.type_observe.str.replace(r" \(.*\)", "", regex=True).value_counts()
    return ", ".join(f"{v} {k}" for k, v in s.items())


def fmt_int(x):
    return f"{int(x):,}".replace(",", " ") if pd.notna(x) else ""


# ------------------------------------------------------------------ onglet Fichiers
fich_rows = []
for r in files.itertuples():
    c = cols[(cols.dossier == r.dossier) & (cols.table == r.table)]
    if r.format == "csv":
        dom, role, anom, lim = AUDIT
        fich_rows.append([r.dossier, r.fichier, r.chemin, "CSV (séparateur « , »), en-tête puis sections",
                          r.taille, fmt_int(r.taille_octets), fmt_int(r.lignes), r.colonnes_observees,
                          "maxItems, realMaxItems, numCompetitors, minComPerITem, maxComPerItem, avgComPerItem, "
                          "itemsWithoutCompetitors, itemsNotHavingMinCompetitors",
                          "nombres (statistiques)", "aucune", anom, lim, dom, role, "Vérifié"])
        continue
    dom, role, anom, lim = ANNOT[r.table]
    if r.dossier == "data_refresh":
        lim = (lim + " " if lim else "") + "Fichier de data_refresh/ : complète data/ (voir onglet data_refresh)."
    key = r.cle_testee
    keytxt = (f"{key} : unique" if r.cle_unique == "oui"
              else f"{key} : NON unique ({fmt_int(r.cle_doublons)} doublons)" if r.cle_unique == "non"
              else "aucune clé unique identifiée")
    nulls = (f"{int(r.nb_colonnes_avec_nulls)} colonne(s) avec nulls" if r.nb_colonnes_avec_nulls else "aucun nul")
    if isinstance(r.colonnes_100pct_nulles, str):
        nulls += f" ; 100 % vide : {r.colonnes_100pct_nulles}"
    if r.doublons_lignes_completes:
        nulls += f" ; {fmt_int(r.doublons_lignes_completes)} doublons de ligne complète"
    period = f" Période : {r.date_min} -> {r.date_max}." if isinstance(r.date_min, str) else ""
    fich_rows.append([
        r.dossier, r.fichier, r.chemin, "Texte délimité « | », sans en-tête, UTF-8",
        r.taille, fmt_int(r.taille_octets), fmt_int(r.lignes),
        f"{int(r.colonnes_attendues)} (toutes les lignes conformes)" if r.lignes_hors_format == 0
        else f"{r.colonnes_observees} - attendu {r.colonnes_attendues}",
        ", ".join(c.colonne), type_summary(c), keytxt, f"{nulls}. {anom}{period}", lim, dom, role,
        "Vérifié",
    ])

FICH_HEAD = ["Dossier", "1. Nom exact", "2. Chemin", "3. Format", "4. Taille", "Taille (octets)",
             "5. Nb lignes", "6. Nb colonnes", "7. Noms des colonnes", "8. Types observés",
             "9. Clé / identifiant potentiel", "10. Nulls et anomalies visibles",
             "11. Limites de compréhension", "Domaine", "Rôle métier", "Statut"]

# ------------------------------------------------------------------ onglet Domaines (§5.1.11 + §3.5)
data_tables = set(files[(files.dossier == "data") & (files.format == "dat")].table)
DOMAINES = [
    ["Ventes magasin", "store_sales", "Identifiants, date, produit, quantité, montant", "Tous présents",
     "Vérifié", "Q1, Q3, Q4"],
    ["Ventes web", "web_sales, web_site, ship_mode", "Identifiants, date, produit, client, montant",
     "Tous présents ; pas d'identifiant de ligne unique", "Vérifié", "Q1, Q2"],
    ["Retours", "store_returns, web_returns, reason", "Références, dates, quantités, motifs",
     "Tous présents ; dates de retour jusqu'en 2007-2008", "Vérifié", "Hors périmètre (itération 2)"],
    ["Produits", "item", "Identifiants, libellés, catégories, attributs", "Présents ; i_size 14 % vide",
     "Vérifié", "Q1, Q5"],
    ["Clients", "customer, customer_address, customer_demographics, household_demographics, income_band",
     "Identifiants et caractéristiques", "Présents ; nulls < 0,05 %", "Vérifié", "Hors périmètre"],
    ["Magasins", "store", "Identifiants, attributs géographiques", "Présents (ville, État, zip, fuseau)",
     "Vérifié", "Q3"],
    ["Stocks", "inventory, warehouse", "Produit, lieu, date, quantité",
     "Présents ; lieu = entrepôt (pas de stock magasin)", "Vérifié", "Q5, Q6"],
    ["Navigation", "web_clickstreams, web_page", "Nature des événements, dates, identifiants",
     "Date, heure, produit, page, utilisateur présents ; PAS de type d'événement (vue, panier...)",
     "Vérifié", "Hors périmètre"],
    ["Temps", "date_dim, time_dim", "Calendrier, heures", "1900-2199 ; 86 400 secondes", "Vérifié", "Q4, K08"],
    ["Promotions", "promotion", "Campagnes", "300 promotions", "Vérifié", "Hors périmètre"],
    ["Avis produits", "product_reviews", "Notes et verbatims", "Notes 1 à 5 + texte", "Vérifié", "Hors périmètre"],
    ["Prix concurrents", "item_marketprices (+ audit CSV)", "Comparaison tarifaire", "Présents", "Vérifié",
     "Hors périmètre"],
    ["Ventes catalogue (3e canal TPC-DS)", "catalog_sales, catalog_returns", "-",
     "Absents du kit : seuls magasin et web sont analysables", "Non disponible", "Q2 limitée à 2 canaux"],
    ["Données complémentaires (§3.6 : météo, logistique, événements...)", "-", "-",
     "Aucune fournie. test.csv à la racine du projet n'est pas une donnée du kit.", "Non disponible", "-"],
]

# ------------------------------------------------------------------ onglet data_refresh
ref = files[(files.dossier == "data_refresh") & (files.format == "dat")]
REF_HEAD = ["Table", "Lignes data/", "Lignes data_refresh/", "Clés de data_refresh déjà dans data/",
            "Période data/", "Période data_refresh/", "Lecture"]
ref_rows = []
for r in ref.itertuples():
    d = files[(files.dossier == "data") & (files.table == r.table) & (files.format == "dat")].iloc[0]
    if pd.notna(r.refresh_cles_deja_dans_data):
        reading = ("Nouvelles lignes uniquement (aucune clé commune)" if r.refresh_cles_deja_dans_data == 0
                   else f"{int(r.refresh_cles_deja_dans_data)} clés en commun : mises à jour ?")
    elif isinstance(r.date_min, str) and r.table in ("store_sales", "web_sales", "web_clickstreams", "inventory"):
        reading = "Prolonge la période de data/ (fin décembre 2005)"
    else:
        reading = "Retours dispersés sur toute la période"
    ref_rows.append([r.table, fmt_int(d.lignes), fmt_int(r.lignes),
                     fmt_int(r.refresh_cles_deja_dans_data) if pd.notna(r.refresh_cles_deja_dans_data) else "n/a",
                     f"{d.date_min} -> {d.date_max}" if isinstance(d.date_min, str) else "",
                     f"{r.date_min} -> {r.date_max}" if isinstance(r.date_min, str) else "", reading])

# ------------------------------------------------------------------ onglet Anomalies
ANOMALIES = [
    ["Structure", "Les 36 fichiers ont un nombre de champs constant, conforme au schéma ; 0 ligne non UTF-8",
     "Vérifié", "Lecture fiable avec schema.py"],
    ["Structure", "Fichiers .dat sans en-tête : noms et ordre des colonnes comparés à la spécification TPCx-BB "
                  "v1.7.0 (annexe B.2) : 23 tables sur 23 identiques", "Vérifié",
     "Lecture fiable ; preuve : controle_schema_vs_specification.txt"],
    ["Clés", "Aucun identifiant de ligne unique dans store_sales, web_sales et web_clickstreams (aucune colonne "
             "ni combinaison unique)", "Vérifié", "Générer une clé technique (id_ligne) en Silver"],
    ["Doublons", "Doublons sur (transaction, produit) : store_sales 4 136, web_sales 4 076, store_returns 158, "
                 "web_returns 150 ; aucune ligne entièrement identique", "Vérifié",
     "Signification à établir (Étape D) avant tout comptage"],
    ["Doublons", "web_clickstreams : 83 lignes entièrement identiques (data/), 1 (data_refresh/)", "Vérifié",
     "À dédoublonner ou à expliquer (2 clics la même seconde ?)"],
    ["Nulls", "web_clickstreams.wcs_sales_sk vide à 90,1 %, wcs_user_sk vide à 42,1 %", "Vérifié",
     "Normal si la plupart des clics ne mènent pas à un achat et si les visiteurs sont anonymes (Hypothèse)"],
    ["Nulls", "item.i_rec_end_date, store.s_rec_end_date, web_page.wp_rec_end_date, web_site.web_rec_end_date "
              "100 % vides", "Vérifié", "Pas d'historique de versions : chaque référence a une seule version"],
    ["Nulls", "inventory.inv_quantity_on_hand : 5 999 vides", "Vérifié", "Ne pas confondre vide et stock 0 (K11)"],
    ["Incohérence", "store.s_closed_date_sk renseignée pour les 12 magasins (1917 à 2141) ; 5 magasins « fermés » "
                    "avant 2001 vendent en 2001-2005", "Vérifié", "Colonne inutilisable pour filtrer les magasins "
                                                                  "(preuve : controle_store_fermeture.txt)"],
    ["Incohérence", "Retours jusqu'en 2007-11-14 (magasin) et 2008-03-18 (web) alors que les ventes s'arrêtent "
                    "au 2005-12-31", "Vérifié", "Délais de retour irréalistes : vérifier le lien retour-vente (Étape D)"],
    ["Incohérence", "date_dim.d_holiday = Y pour 100 % des jours ; d_following_holiday réparti ~50/50", "Vérifié",
     "Indicateurs de jours fériés inutilisables (preuve : controle_date_dim.txt)"],
    ["Valeur sentinelle", "household_demographics.hd_vehicle_count = -1", "Vérifié", "Signification inconnue"],
    ["Type", "Colonnes entières lues en décimal dès qu'elles contiennent un nul ; ca_zip / s_zip lus en entier "
             "par défaut (aucun code ne commence par 0 dans le brut)", "Vérifié",
     "Imposer les types au chargement (Silver) : clés en entier nullable, codes postaux en texte"],
    ["Texte", "14 864 avis contiennent des entités HTML (&amp;quot;, &amp;amp;...) ; 2 575 descriptions produit "
              "(i_item_desc) ont des espaces en début ou fin", "Vérifié", "Décoder et rogner en Silver"],
    ["Référentiel", "180 produits de inventory absents de data/item, présents dans data_refresh/item", "Vérifié",
     "Charger data/ et data_refresh/ ensemble pour les référentiels"],
    ["Couverture", "Ventes de data/ jusqu'au 2005-12-13, data_refresh/ du 2005-12-13 au 2005-12-31 ; le 13/12 est "
                   "réparti entre les deux sans transaction commune (data 0-89 099, refresh 89 100-89 999)", "Vérifié",
     "Pas de doublon : concaténer les deux dossiers (preuve : controles_relations.txt)"],
    ["Couverture", "Relevé de stock du 2005-12-12 réparti : 35 100 lignes dans data/, 54 900 dans data_refresh/ ; "
                   "relevés des 19/12 et 26/12 uniquement dans data_refresh/", "Vérifié",
     "Le dernier relevé complet est le 26/12/2005 (controle_inventaire_complet.txt)"],
    ["Fichier hors standard", "item_marketprices_audit.csv (data/ et data_refresh/) : rapport de génération",
     "À valider", "Ne pas charger comme une table"],
]

# ------------------------------------------------------------------ écriture
thin = Side(style="thin", color="9AA9B8")


def write_sheet(ws, head, rows, widths, status_col=None, freeze="A2"):
    ws.append(head)
    for r in rows:
        ws.append(list(r))
    for i, w in enumerate(widths, 1):
        ws.column_dimensions[get_column_letter(i)].width = w
    for ri, row in enumerate(ws.iter_rows(), 1):
        for c in row:
            c.alignment = Alignment(wrap_text=True, vertical="top")
            c.border = Border(top=thin, bottom=thin, left=thin, right=thin)
            c.font = Font(name="Calibri", size=10)
            if ri == 1:
                c.fill = PatternFill("solid", fgColor=NAVY)
                c.font = Font(name="Calibri", size=10, bold=True, color="FFFFFF")
            elif ri % 2 == 1:
                c.fill = PatternFill("solid", fgColor=LIGHT)
        if ri > 1 and status_col:
            cell = row[status_col - 1]
            for k, color in FILLS.items():
                if str(cell.value).startswith(k):
                    cell.fill = PatternFill("solid", fgColor=color)
                    cell.font = Font(name="Calibri", size=10, bold=True)
    ws.freeze_panes = freeze
    ws.auto_filter.ref = ws.dimensions


wb = Workbook()
ws = wb.active
ws.title = "Lisez-moi"
tot = files.taille_octets.sum()
README = [
    ("inventaire_sources.xlsx - Retail Intelligence Platform", "t"),
    ("UC-01, Étape C - Examiner les données (§5.1.11 et §5.1.13). Version v1, 16/11/2026.", ""),
    ("", ""),
    ("Kit examiné", "h"),
    ("Archive retail_project.zip (SHA-256 dc1634e9...ed86c), version et provenance non communiquées.", ""),
    (f"36 fichiers, {fmt_int(tot)} octets décompressés : 24 dans data/ (23 tables .dat + 1 CSV d'audit), "
     "12 dans data_refresh/ (11 .dat + 1 CSV d'audit).", ""),
    ("Emplacement d'analyse : donnees/retail_project/ (archive décompressée, hors dépôt)", ""),
    ("", ""),
    ("Méthode", "h"),
    ("1. Lecture brute de chaque fichier : nombre de lignes, nombre de champs par ligne, encodage UTF-8.", ""),
    ("2. Chargement avec pandas (séparateur « | », sans en-tête, noms de colonnes de la spécification TPCx-BB).", ""),
    ("3. Par colonne : type observé, nulls, valeurs distinctes, min / max, exemple, unicité.", ""),
    ("4. Par fichier : test de la clé (simple ou composite), doublons, période couverte.", ""),
    ("Scripts : sources/profilage_sources.py (mesures) puis uc01_inventaire_sources.py (ce fichier).", ""),
    ("Preuves : preuves/arborescence.txt, apercus/, inventaire_fichiers.csv, inventaire_colonnes.csv, "
     "profilage_log.txt, controle_store_fermeture.txt.", ""),
    ("", ""),
    ("Onglets", "h"),
    ("Domaines : couverture des domaines demandés (§5.1.11) par les fichiers observés.", ""),
    ("Fichiers : les 11 informations demandées pour chacun des 36 fichiers.", ""),
    ("Colonnes : 522 colonnes avec type, nulls, distincts, min/max, exemple.", ""),
    ("data_refresh : comparaison des deux dossiers.", ""),
    ("Anomalies : constats de qualité et leur impact.", ""),
    ("", ""),
    ("Statuts (§4.2)", "h"),
    ("Vérifié = mesuré sur les fichiers ; Déduit = obtenu par analyse ; Hypothèse = à confirmer ; "
     "Non disponible = absent ; À valider = décision ou vérification à obtenir.", ""),
    ("Les noms de colonnes sont « Vérifiés » : les fichiers n'ont pas d'en-tête, mais noms et ordre sont identiques "
     "à la spécification TPCx-BB v1.7.0, annexe B.2 (controle_schema_vs_specification.txt).", ""),
]
for text, kind in README:
    ws.append([text])
    c = ws.cell(ws.max_row, 1)
    c.font = Font(name="Calibri", size=13 if kind == "t" else 10.5, bold=bool(kind),
                  color=NAVY if kind else "000000")
    c.alignment = Alignment(wrap_text=True, vertical="top")
ws.column_dimensions["A"].width = 125

write_sheet(wb.create_sheet("Domaines"),
            ["Domaine", "Tables observées", "Vérifications attendues (§5.1.11)", "Constat", "Statut",
             "Usage (questions)"], DOMAINES, [26, 34, 30, 50, 15, 22], status_col=5)
write_sheet(wb.create_sheet("Fichiers"), FICH_HEAD, fich_rows,
            [11, 26, 48, 22, 10, 14, 12, 18, 60, 24, 34, 60, 46, 16, 26, 18], status_col=16, freeze="C2")

col_out = cols.copy()
col_out["statut_nom"] = "Vérifié"
col_out = col_out[["dossier", "table", "position", "colonne", "type_observe", "longueur_max", "nb_nulls",
                   "pct_nulls", "nb_distincts", "min", "max", "exemple", "unique_non_nul", "statut_nom"]]
write_sheet(wb.create_sheet("Colonnes"),
            ["Dossier", "Table", "Pos.", "Colonne", "Type observé", "Long. max (texte)", "Nb nulls", "% nulls",
             "Nb distincts", "Min", "Max", "Exemple", "Unique et non nul", "Statut du nom"],
            col_out.astype(object).where(col_out.notna(), "").values.tolist(), [11, 22, 6, 26, 30, 10, 10, 9, 11, 11, 11, 34, 10, 11],
            freeze="E2")
write_sheet(wb.create_sheet("data_refresh"), REF_HEAD, ref_rows, [20, 14, 14, 18, 34, 34, 40])
write_sheet(wb.create_sheet("Anomalies"), ["Catégorie", "Constat", "Statut", "Impact / suite à donner"],
            ANOMALIES, [16, 70, 13, 60], status_col=3)

wb.save(OUT)
print(f"Excel généré : {OUT}")
