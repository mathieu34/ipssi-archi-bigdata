"""Génère preuves/index_preuves.pdf pour l'UC-01 et l'UC-02.

Chaque preuve : titre, ce qu'elle démontre, fichier, origine, extrait lisible (consigne de Livrables_Jour_1.pdf :
« chaque preuve doit être lisible, porter un titre et être accompagnée d'une courte explication »).
Usage : .venv/bin/python sources/index_preuves.py
"""
import csv
from html import escape
from pathlib import Path

import pymupdf
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import KeepTogether, PageBreak, Preformatted, Spacer

from chemins import UC01, UC01_PREUVES, UC02, UC02_PREUVES
from pdf_style import CELL, H2, H3, SUB, TITLE, build, p, table

CODE = ParagraphStyle("code", fontName="Courier", fontSize=6.3, leading=7.6, leftIndent=4)


def excerpt_text(path, n=14, width=118, skip=0):
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()[skip:skip + n]
    out = [(l[:width] + " …") if len(l) > width else l for l in lines]
    return Preformatted("\n".join(out), CODE)


def excerpt_csv(path, n=6, maxcols=7, width=45, cols=None):
    with open(path, encoding="utf-8") as fh:
        sample = fh.read(4096)
        fh.seek(0)
        delim = ";" if sample.count(";") > sample.count(",") else ","
        rows = list(csv.reader(fh, delimiter=delim))
    total = len(rows) - 1
    if cols:
        idx = [rows[0].index(c) for c in cols]
        rows = [[r[i] for i in idx] for r in rows]
    rows = [[escape((c[:width] + "…") if len(c) > width else c) for c in r[:maxcols]] for r in rows[:n + 1]]
    ncol = len(rows[0])
    return [table(rows, [17 / ncol] * ncol, size=6),
            p(f"Extrait : {min(n, total)} lignes sur {total}" + (f", {maxcols} premières colonnes" if ncol == maxcols else ""), CELL)]


def entry(i, title, demontre, fichier, origine, extrait):
    head = table([["Ce que la preuve démontre", demontre], ["Fichier", fichier], ["Origine", origine]],
                 [4, 13], header=False, size=7.5)
    ex = extrait if isinstance(extrait, list) else [extrait]
    return [KeepTogether([p(f"P{i:02d} &ndash; {title}", H3), head, Spacer(1, 2)] + ex[:1]), *ex[1:], Spacer(1, 6)]


def make(uc, folder, out_name, intro, items, annexes):
    story = [p("Retail Intelligence Platform", TITLE), p(f"{uc} &ndash; Index des preuves", SUB), Spacer(1, 6),
             p(intro), Spacer(1, 4),
             table([["#", "Preuve", "Fichier"]] + [[f"P{i:02d}", t, f] for i, (t, _, f, _, _) in enumerate(items, 1)]
                   + [[f"A{j}", a[1], a[0].name] for j, a in enumerate(annexes, 1)], [1.2, 9.3, 6.5], size=7.5),
             PageBreak()]
    for i, (t, d, f, o, e) in enumerate(items, 1):
        story += entry(i, t, d, f, o, e)
    if annexes:
        story += [PageBreak(), p("Annexes : schémas", H2),
                  p("Les pages suivantes reproduisent les schémas cités ci-dessus, extraits des documents indiqués.")]
        for j, (src, titre, pages, expl) in enumerate(annexes, 1):
            story.append(p(f"<b>A{j} &ndash; {titre}</b> : {expl} (source : {src.name}, page(s) "
                           f"{', '.join(str(x + 1) for x in pages)})", CELL))
    tmp = folder / (out_name + ".tmp.pdf")
    build(tmp, story, f"{uc} - Index des preuves", f"Retail Intelligence Platform - {uc} Index des preuves")
    doc = pymupdf.open(tmp)
    for src, _, pages, _ in annexes:
        s = pymupdf.open(src)
        for pg in pages:
            doc.insert_pdf(s, from_page=pg, to_page=pg)
    doc.save(folder / out_name)
    tmp.unlink()
    print("Index généré :", folder / out_name)


P1 = UC01_PREUVES
make("UC-01", P1, "index_preuves.pdf",
     "Preuves de l'exploration et de la qualification des données (UC-01). Toutes ont été produites sur les fichiers "
     "réellement fournis (archive retail_project.zip, dossiers data/ et data_refresh/), par les scripts Python du "
     "dossier sources/ du dépôt. Les extraits ci-dessous sont copiés tels quels depuis les fichiers.",
     [
         ("Contenu de l'archive fournie", "L'archive contient 36 fichiers (24 dans data/, 12 dans data_refresh/) "
          "pour 1 033 993 587 octets ; c'est la liste de référence de l'inventaire.", "contenu_archive.txt",
          "Commande unzip -l retail_project.zip", excerpt_text(P1 / "contenu_archive.txt", 16)),
         ("Empreinte de l'archive", "Intégrité : toute ingestion future compare l'empreinte SHA-256 à cette valeur.",
          "checksum.txt", "Commande sha256sum", excerpt_text(P1 / "checksum.txt", 3)),
         ("Arborescence des données (capture)", "Organisation réelle des fichiers par dossier et par table, avec les "
          "tailles : format .dat, un dossier par table, deux lots.", "arborescence.txt", "profilage_sources.py",
          excerpt_text(P1 / "arborescence.txt", 22)),
         ("Aperçu de fichiers représentatifs", "Format observé : texte délimité par « | », sans ligne d'en-tête ; "
          "valeurs vides représentées par un champ vide.", "apercus/ (36 fichiers)", "profilage_sources.py "
          "(5 premières lignes brutes de chaque fichier)", excerpt_text(P1 / "apercus" / "data__store_sales.dat.txt", 4)),
         ("Inventaire des fichiers", "Pour chaque fichier : lignes, nombre de champs (100 % conformes), clé testée, "
          "doublons, période couverte, colonnes avec valeurs vides.", "inventaire_fichiers.csv",
          "profilage_sources.py", excerpt_csv(P1 / "inventaire_fichiers.csv", 8, cols=["dossier", "fichier", "lignes", "colonnes_attendues", "lignes_hors_format", "cle_testee", "cle_unique"])),
         ("Colonnes et types observés", "522 colonnes : type observé, nombre et % de valeurs vides, valeurs "
          "distinctes, min / max, exemple, unicité.", "inventaire_colonnes.csv", "profilage_sources.py",
          excerpt_csv(P1 / "inventaire_colonnes.csv", 8)),
         ("Conformité des en-têtes à la spécification", "Les noms et l'ordre des colonnes utilisés pour lire les "
          "fichiers sont identiques à la spécification TPCx-BB v1.7.0 (annexe B.2) pour les 23 tables.",
          "controle_schema_vs_specification.txt", "Comparaison automatique avec TPCX-BB_v1.7.0.pdf",
          excerpt_text(P1 / "controle_schema_vs_specification.txt", 20, skip=8)),
         ("Contrôles qui fondent les KPI", "Valeurs vides, période, formules de montants exactes à 100 %, "
          "transactions distinctes : justifie les formules du dictionnaire KPI.", "controles_kpi.txt",
          "controles_kpi.py", excerpt_text(P1 / "controles_kpi.txt", 26)),
         ("Relations entre les tables", "47 relations testées : types, valeurs vides, orphelins, cardinalité ; "
          "justifie les jointures des KPI.", "relations.csv", "relations_qualite.py",
          excerpt_csv(P1 / "relations.csv", 8)),
         ("Analyses de cohérence (doublons, retours, lots, clics)", "Doublons (transaction, produit) = lignes "
          "distinctes ; retours retrouvés à 99 % ; data_refresh/ sans recouvrement ; clics reliés aux commandes.",
          "controles_relations.txt", "relations_qualite.py",
          excerpt_text(P1 / "controles_relations.txt", 18, skip=50)),
         ("Relevés de stock complets", "Un relevé complet = 90 000 lignes ; le relevé du 12/12/2005 est réparti "
          "entre les deux lots ; dernier relevé complet : 26/12/2005.", "controle_inventaire_complet.txt",
          "Commande Python ponctuelle (en-tête du fichier)", excerpt_text(P1 / "controle_inventaire_complet.txt", 9)),
         ("Incohérence des dates de fermeture des magasins", "5 magasins « fermés » avant 2001 vendent en "
          "2001-2005 : colonne inutilisable.", "controle_store_fermeture.txt", "Commande Python ponctuelle",
          excerpt_text(P1 / "controle_store_fermeture.txt", 16)),
         ("Indicateurs calendaires", "d_holiday vaut Y pour 100 % des jours : impossible d'isoler les jours fériés.",
          "controle_date_dim.txt", "Commande cut | sort | uniq -c", excerpt_text(P1 / "controle_date_dim.txt", 6)),
         ("Journal du profilage", "Trace de l'exécution : chaque fichier lu, lignes, durée.", "profilage_log.txt",
          "profilage_sources.py", excerpt_text(P1 / "profilage_log.txt", 10)),
     ],
     [(P1 / "schema_fonctionnel.pdf", "Schéma fonctionnel des besoins",
       [0], "utilisateurs, questions, KPI, domaines et fichiers ; sources vérifiées et souhaitées distinguées")])

P2 = UC02_PREUVES
D = P2 / "demo_bronze_silver_gold"
make("UC-02", P2, "index_preuves.pdf",
     "Preuves de l'UC-02. Au Jour 1, l'architecture est conçue mais pas déployée : HDFS, NiFi et Spark ne sont pas "
     "installés (P01). Les manipulations réellement effectuées sont le profilage de l'UC-01 et une démonstration "
     "locale Bronze -> Silver -> Gold (P02 à P06), réalisée avec le repli documenté : système de fichiers local au lieu "
     "de HDFS, Python (pandas + pyarrow) au lieu de Spark. Elle n'est pas présentée comme le déploiement de "
     "l'architecture cible.",
     [
         ("État réel de l'environnement local (capture)", "Composants réellement installés ou absents au Jour 1, "
          "mémoire et disque : rien n'est présenté comme installé s'il ne l'est pas.", "environnement_local.txt",
          "Commandes lsb_release, command -v, free, df", excerpt_text(P2 / "environnement_local.txt", 14)),
         ("Traitement réalisé : démonstration Bronze -> Silver -> Gold", "Exécution réelle : dépôt Bronze avec "
          "empreinte, contrôles Silver (Q02 à Q06), Parquet partitionné, agrégat Gold et réconciliations toutes OK.",
          "demo_bronze_silver_gold/journal_execution.txt", "demo_bronze_silver_gold.py",
          excerpt_text(D / "journal_execution.txt", 30, width=125)),
         ("Exemple de stockage organisé en zones", "Arborescence réellement produite : bronze (fichiers d'origine "
          "par table et par lot), silver (Parquet, quarantaine), gold (KPI).",
          "demo_bronze_silver_gold/arborescence_datalake_demo.txt", "demo_bronze_silver_gold.py",
          excerpt_text(D / "arborescence_datalake_demo.txt", 50)),
         ("Traçabilité : manifeste de lot", "Règle de gouvernance mise en œuvre : chaque lot déposé a son manifeste "
          "(fichiers, tailles, lignes, SHA-256, date).", "demo_bronze_silver_gold/manifeste_lot=data_refresh.json",
          "demo_bronze_silver_gold.py", excerpt_text(D / "manifeste_lot=data_refresh.json", 24)),
         ("Types stockés dans le Parquet Silver", "Contrairement au .dat, le Parquet porte le schéma : clés entières, "
          "montants décimaux, colonnes de traçabilité _lot, _fichier_source, _id_ligne.",
          "demo_bronze_silver_gold/schema_parquet_silver_store_sales.txt", "pyarrow",
          excerpt_text(D / "schema_parquet_silver_store_sales.txt", 34)),
         ("Résultat Gold : KPI K02 (CA net par catégorie et par année)", "Fichier analytique réellement produit "
          "(aussi en Parquet) ; la somme du CA est réconciliée avec Silver et Bronze.",
          "demo_bronze_silver_gold/gold_k02_ca_categorie_annee.csv (+ .parquet)", "demo_bronze_silver_gold.py",
          excerpt_csv(D / "gold_k02_ca_categorie_annee.csv", 9)),
         ("Valeurs de référence pour la réconciliation", "Lignes et transactions attendues (data/ + data_refresh/) "
          "utilisées par les contrôles des flux.", "valeurs_reference.txt", "Commandes wc -l, cut, sort -u",
          excerpt_text(P2 / "valeurs_reference.txt", 10)),
         ("Tableau de comparaison des architectures", "Les 7 critères demandés pour DW, Data Lake et Lakehouse.",
          "tableau_comparaison_architectures.csv", "uc02_comparaison_architectures.py",
          excerpt_csv(P2 / "tableau_comparaison_architectures.csv", 8, 4, 70)),
         ("Description des zones et du modèle Gold", "Rôle, entrées, sorties et règles de Bronze, Silver, Gold ; "
          "colonnes Gold et correspondance avec les sources.", "zones_donnees.csv, modele_gold.csv",
          "uc02_architecture_cible.py", excerpt_csv(P2 / "zones_donnees.csv", 3, 5, 70)),
         ("Description des flux", "Les 6 flux avec les 8 attributs demandés.", "flux.csv", "uc02_schema_flux.py",
          excerpt_csv(P2 / "flux.csv", 6, 5, 50)),
         ("Matrice de positionnement des composants", "Statut du référentiel et état réel au Jour 1 de chaque "
          "composant.", "matrice_composants.csv", "uc02_positionnement_composants.py",
          excerpt_csv(P2 / "matrice_composants.csv", 12, 6, 45)),
         ("Règles de gouvernance et de qualité", "Les 7 règles minimales et les 12 contrôles de qualité Q01 à Q12.",
          "regles_gouvernance.csv, regles_qualite.csv", "uc02_gouvernance.py",
          excerpt_csv(P2 / "regles_qualite.csv", 12, 6, 50)),
         ("Correspondance local / Azure", "Chaque couche en local et dans la cible Azure (ADLS Gen2), avec son "
          "statut (conception, étude).", "comparaison_local_cloud.csv", "uc02_local_vers_azure.py",
          excerpt_csv(P2 / "comparaison_local_cloud.csv", 12, 4, 60)),
     ],
     [(UC02 / "architecture_cible.pdf", "Schéma d'architecture annoté", [0],
       "couches, zones, règles de qualité et de traçabilité sous chaque couche, gouvernance"),
      (UC02 / "schema_flux.pdf", "Schéma des flux", [0], "flux F1 à F6, de la source à l'exposition"),
      (UC02 / "local_vers_azure.pdf", "Schéma de la cible Azure", [1], "compte ADLS Gen2, conteneurs, services")])
