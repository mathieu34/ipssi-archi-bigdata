"""Génère J1_Retail_Intelligence/02_UC02_architecture/comparaison_architectures.pdf (UC-02, Étapes A et B).

Usage : .venv/bin/python sources/uc02_comparaison_architectures.py
Produit aussi preuves/tableau_comparaison_architectures.csv (preuve §5.2.16).
Les constats chiffrés viennent des livrables et preuves de l'UC-01.
"""
import csv

from reportlab.graphics.shapes import Drawing, String
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import KeepTogether, PageBreak, Spacer

from chemins import UC02, UC02_PREUVES
from pdf_style import (BLUE, CELL, GREEN, GREY, H2, H3, LIGHT, NAVY, ORANGE, SUB, TITLE, box, build,
                       link, p, table)

OUT = UC02 / "comparaison_architectures.pdf"
UC02_PREUVES.mkdir(parents=True, exist_ok=True)

story = [
    p("Retail Intelligence Platform", TITLE),
    p("UC-02 &ndash; Contraintes et comparaison des architectures analytiques", SUB),
    p("IPSSI &ndash; Mastère Développement, Data &amp; IA &ndash; TP Jour 1", SUB),
    Spacer(1, 8),
    table([
        ["Élément", "Valeur"],
        ["Livrable", "comparaison_architectures.pdf (UC02_comparaison_architectures, §5.2.17)"],
        ["Étapes couvertes", "Étape A &ndash; Identifier les contraintes ; Étape B &ndash; Comparer les approches "
                             "(§5.2.13) ; questions de recul (§5.2.20)"],
        ["Date / version", "16/11/2026 &ndash; v1"],
        ["Entrées", "Livrables UC-01 (01_UC01_besoin_exploration/) : cadrage, questions, KPI, inventaire, "
                    "qualification, limites ; support de cours J1 (slides 16-20, 35-48)"],
        ["Nature", "Document de conception : aucune architecture n'est déployée à ce stade."],
    ], [4, 13]),

    p("1. Démarche", H2),
    p("Conformément au principe du cours (« une architecture est une réponse argumentée à un besoin ; la "
      "technologie ne doit pas être choisie avant d'avoir compris le problème »), le choix part des contraintes "
      "mesurées dans l'UC-01 (section 2), compare trois approches sur les mêmes critères (section 3), les confronte "
      "aux contraintes (section 4), puis retient une architecture et en expose les limites (section 5)."),
    Spacer(1, 3),
    p("Statuts utilisés (§4.2) : <b>Vérifié</b> (mesuré sur les fichiers), <b>Déduit</b>, <b>Hypothèse</b>, "
      "<b>Non disponible</b>, <b>À valider</b>."),

    # ------------------------------------------------------------------ Étape A
    p("2. Contraintes du projet issues de l'UC-01 (Étape A)", H2),
    table([
        ["Contrainte", "Constat (source UC-01)", "Statut", "Exigence pour l'architecture"],
        ["Formats", "34 fichiers .dat (23 dans data/, 11 dans data_refresh/) texte délimités par « | », sans en-tête, UTF-8 ; 2 CSV d'audit "
                    "multi-sections ; aucun JSON ni binaire (inventaire_sources.xlsx)", "Vérifié",
         "Imposer un schéma à la lecture ; conserver les fichiers d'origine intacts"],
        ["Volumes", "36 fichiers, 0,96 Go décompressés ; plus grosses tables : inventory 23,5 M lignes "
                    "(425 Mo), web_clickstreams 6,8 M (179 Mo), web_sales et store_sales 0,67 M chacune",
         "Vérifié", "Volume modeste aujourd'hui ; traitement distribué utile pour inventory et les clics, et "
                    "pour absorber la croissance"],
        ["Diversité des domaines", "23 tables, 12 domaines (ventes magasin et web, retours, produits, clients, "
                                   "magasins, stocks, navigation, avis, promotions, prix concurrents, temps)",
         "Vérifié", "Organisation par domaine ; référentiels partagés entre plusieurs faits"],
        ["Nature des données", "Majoritairement structurées (tables exportées en .dat) ; texte libre dans "
                               "product_reviews.pr_review_content (non structuré dans un fichier tabulaire) ; CSV "
                               "d'audit multi-sections (semi-structuré)", "Vérifié",
         "Supporter des données non strictement tabulaires sans les forcer dans un modèle relationnel"],
        ["Historisation", "data_refresh/ prolonge data/ par lots (nouvelles clés, ventes du 13 au 31/12/2005) ; "
                          "stock en photos hebdomadaires ; colonnes *_rec_end_date prévues mais vides",
         "Vérifié / Déduit", "Charger par lots sans écraser ; conserver chaque lot reçu ; garder l'historique "
                             "des relevés de stock"],
        ["Qualité", "Anomalies réelles : date de fermeture de magasin incohérente, retours 1 à 2 ans après la "
                    "vente, 118 retours > quantité vendue, 5 999 stocks vides, doublons (ticket, produit) "
                    "légitimes (qualification_donnees.pdf)", "Vérifié",
         "Une étape de contrôle explicite, avec mise à l'écart des lignes invalides et traçabilité des règles"],
        ["Usages analytiques", "12 KPI (dictionnaire_KPI.xlsx) agrégés par catégorie, canal, magasin, jour, "
                               "entrepôt ; exploration future des avis et des clics", "Vérifié",
         "Données modélisées pour la BI (faits / dimensions) et accès au détail pour l'exploration"],
        ["Sécurité et accès", "Données personnelles clients (nom, e-mail, date de naissance), fictives mais à "
                              "traiter comme réelles ; profils métier différents", "Vérifié",
         "Accès différenciés par zone et par profil ; masquage des données personnelles pour les métiers"],
        ["Évolution", "Données complémentaires possibles (JSON, journaux, météo, §3.6) ; déclinaison Azure au "
                      "Jour 4 ; besoin temps réel non exprimé", "Hypothèse",
         "Architecture ouverte à de nouveaux formats et transposable vers un stockage cloud"],
    ], [2.6, 6.4, 1.8, 6.2], size=7.5),
]

# ------------------------------------------------------------------ Étape B : schémas
story.append(p("3. Les trois approches étudiées (Étape B)", H2))


def mini_flow(steps, fills):
    W, H = 17 * cm, 1.7 * cm
    d = Drawing(W, H)
    n = len(steps)
    gap = 10
    bw = (W - gap * (n - 1)) / n
    for i, (s, f) in enumerate(zip(steps, fills)):
        x = i * (bw + gap)
        box(d, x, 6, bw, H - 12, s, fill=f, size=7)
        if i:
            link(d, x - gap, H / 2, x, H / 2)
    return d


APPROCHES = [
    ("3.1 Architecture décisionnelle centrée sur un Data Warehouse",
     [["Sources", ".dat TPCx-BB"], ["ETL", "transformer avant"], ["Staging", "contrôles"],
      ["Data Warehouse", "modèle intégré"], ["BI", "KPI"]],
     [LIGHT, BLUE, ORANGE, ORANGE, GREEN],
     "Les données sont extraites, transformées puis chargées dans un entrepôt intégré, historisé et orienté "
     "sujet (slides 16-19). Seules les données transformées sont conservées dans la destination."),
    ("3.2 Architecture Data Lake organisée en zones",
     [["Sources", ".dat TPCx-BB"], ["Ingestion", "chargement brut"], ["Bronze", "données reçues"],
      ["Silver", "nettoyées, typées"], ["Gold", "données métier"]],
     [LIGHT, BLUE, ORANGE, ORANGE, GREEN],
     "Les données sont d'abord chargées telles quelles (ELT), puis préparées dans des zones successives "
     "(slides 39-41). Le schéma est appliqué à la lecture ; catalogue et gouvernance sont indispensables."),
    ("3.3 Architecture Data Lakehouse",
     [["Sources", ".dat TPCx-BB"], ["Ingestion", "chargement brut"], ["Stockage fichiers", "Parquet"],
      ["Couche de tables", "Delta / Iceberg / Hudi"], ["BI + data science", "mêmes tables"]],
     [LIGHT, BLUE, ORANGE, ORANGE, GREEN],
     "Un Data Lake auquel s'ajoute une couche de gestion de tables : schémas, transactions, versions "
     "(slides 45 et 48). Parquet seul ne fournit pas ces garanties."),
]
for title, steps, fills, txt in APPROCHES:
    story.append(KeepTogether([p(title, H3), p(txt), Spacer(1, 3), mini_flow(steps, fills), Spacer(1, 4)]))

COMPARAISON = [
    ["Critère", "Data Warehouse", "Data Lake en zones", "Data Lakehouse"],
    ["Principe", "ETL vers un entrepôt intégré, historisé, orienté sujet ; schéma défini à l'écriture",
     "ELT : conservation des données reçues, préparation par zones ; schéma à la lecture",
     "Stockage de type lac + couche de tables transactionnelle"],
    ["Types de données adaptés", "Structurées", "Structurées, semi-structurées, non structurées",
     "Toutes, exposées sous forme de tables gérées"],
    ["Principaux avantages", "Modèle maîtrisé et stable ; KPI cohérents ; requêtes BI simples",
     "Données sources conservées ; formats variés ; évolutif ; exploration possible",
     "Fiabilité proche d'un DW (transactions, évolution de schéma, versions) sur un stockage flexible"],
    ["Limites", "Rigide face à de nouvelles sources ; intégration longue ; brut non conservé ; texte et "
                "semi-structuré mal gérés",
     "Risque de Data Swamp sans catalogue ni contrôles ; pas de transactions sur des fichiers Parquet seuls",
     "Complexité accrue ; dépend d'une technologie de tables (Delta Lake facultatif dans le parcours)"],
    ["Usages permis", "Reporting, tableaux de bord, analyse OLAP", "BI, exploration, data science, "
                                                                    "retraitements depuis le brut",
     "BI et data science sur les mêmes tables ; mises à jour incrémentales fiables"],
    ["Contraintes de gouvernance", "Règles d'intégration et de qualité en amont du chargement",
     "Catalogue, métadonnées, zones, droits par zone, traçabilité indispensables à grande échelle",
     "Celles du Data Lake + gestion des versions et des schémas de tables"],
    ["Pertinence pour Retail Intelligence", "Partielle : couvre les 12 KPI mais ne conserve ni le brut ni "
                                            "les lots data_refresh/, et gère mal avis et clics",
     "Forte : couvre les contraintes mesurées ; cohérente avec HDFS / ADLS, Spark et Parquet du parcours",
     "Forte à terme, mais repose sur un composant facultatif ; non nécessaire au socle"],
]
story += [p("3.4 Tableau comparatif", H3), table(COMPARAISON, [3, 4.5, 4.9, 4.6], size=7.5)]
with open(UC02_PREUVES / "tableau_comparaison_architectures.csv", "w", newline="", encoding="utf-8") as fh:
    csv.writer(fh, delimiter=";").writerows(
        [[c.replace("&ndash;", "-") for c in r] for r in COMPARAISON])

# ------------------------------------------------------------------ 4. Confrontation
story += [
    p("4. Confrontation aux contraintes de Retail Intelligence", H2),
    p("Chaque approche est évaluée face aux contraintes de la section 2 : <b>++</b> répond pleinement, "
      "<b>+</b> répond avec des efforts, <b>-</b> répond mal."),
    Spacer(1, 3),
    table([
        ["Contrainte", "DW", "Lake", "Lakehouse", "Justification"],
        ["Formats .dat sans en-tête", "+", "++", "++", "DW : schéma imposé à l'ETL ; Lake / Lakehouse : brut conservé, "
                                                        "schéma appliqué à la lecture"],
        ["Volumes (0,96 Go, croissance)", "+", "++", "++", "Stockage et calcul distribués pour Lake et Lakehouse"],
        ["Texte libre (avis), CSV d'audit", "-", "++", "+", "Le DW n'a pas vocation à stocker du texte libre ; le Lake "
                                                            "garde tout en Bronze"],
        ["Historisation par lots (data_refresh/)", "+", "++", "++", "Chaque lot reçu est conservé en Bronze ; le "
                                                                   "Lakehouse ajoute des mises à jour fiables"],
        ["Qualité et traçabilité", "++", "+", "++", "Le DW contrôle avant chargement ; le Lake exige une zone Silver "
                                                    "et un catalogue rigoureux"],
        ["12 KPI pour les métiers", "++", "+", "++", "Le Lake doit ajouter un modèle dimensionnel en Gold pour égaler le DW"],
        ["Sécurité par profil", "+", "+", "+", "Possible partout ; à concevoir explicitement (gouvernance.pdf)"],
        ["Évolution (nouvelles sources, Azure)", "-", "++", "++", "ADLS Gen2 est un stockage de type lac"],
        ["Composants du socle (HDFS, NiFi, Spark, Parquet)", "+", "++", "+", "Le Lakehouse impose Delta Lake, "
                                                                            "facultatif dans le parcours"],
    ], [4.2, 1.1, 1.2, 1.9, 8.6], size=7.5),

    # ------------------------------------------------------------------ 5. Choix
    p("5. Choix retenu et justification", H2),
    p("<b>Architecture retenue : Data Lake organisé en zones Bronze / Silver / Gold, avec des fichiers Parquet en "
      "Silver et Gold et un modèle dimensionnel en étoile en Gold, qui joue le rôle de Data Mart.</b>"),
    Spacer(1, 3),
    table([
        ["Argument", "Lien avec les contraintes et le cours"],
        ["Conserver les données reçues", "Les lots data/ et data_refresh/ et les anomalies constatées doivent "
                                         "pouvoir être rejoués et audités (zone Bronze, slide 40)."],
        ["Contrôler avant d'exposer", "Les anomalies de l'UC-01 deviennent des règles de la zone Silver "
                                      "(slide 21 : zone de préparation et contrôles)."],
        ["Garder la simplicité de la BI", "Le Gold en étoile (fait_ventes au grain de la ligne de vente, fait_stock "
                                          "au relevé hebdomadaire) offre la lisibilité d'un DW pour les 12 KPI "
                                          "(slides 24-28). Le Lake complète le DW plutôt qu'il ne le remplace "
                                          "(slide 42)."],
        ["Respecter le socle du parcours", "HDFS (puis ADLS Gen2), NiFi, Spark et Parquet suffisent ; aucun "
                                           "composant facultatif n'est rendu obligatoire (slide 51)."],
        ["Préparer le cloud", "Les zones se transposent en conteneurs ADLS Gen2 au Jour 4 (local_vers_azure.pdf)."],
    ], [4.2, 12.8], size=8),
    Spacer(1, 5),
    p("Pourquoi pas les deux autres approches ?", H3),
    table([
        ["Approche écartée", "Raison", "Statut"],
        ["Data Warehouse seul", "Perte des données brutes et des lots ; avis et clics hors modèle ; rigidité face "
                                "aux sources complémentaires annoncées (§3.6)", "Déduit"],
        ["Lakehouse dès maintenant", "Les garanties transactionnelles ne sont pas exigées par un chargement par "
                                     "lots de fichiers statiques ; Delta Lake est facultatif. Il reste l'évolution "
                                     "naturelle si des mises à jour incrémentales fréquentes apparaissent.",
         "Déduit"],
    ], [4, 10.8, 2.2], size=8),
    Spacer(1, 5),
    p("Limites du choix et mesures associées", H3),
    table([
        ["Risque", "Mesure prévue (détaillée dans gouvernance.pdf)"],
        ["Data Swamp : fichiers déposés mais incompréhensibles", "Catalogue repris de inventaire_sources.xlsx, "
                                                                 "nommage normalisé, manifeste par lot"],
        ["Pas de transactions sur des fichiers Parquet", "Écriture par lot complet et par partition, traitements "
                                                         "rejouables (idempotents), Delta Lake en option"],
        ["Duplication du stockage entre zones", "Durées de conservation par zone, compression Parquet"],
        ["Données personnelles présentes en Bronze et Silver", "Accès restreint à l'équipe Data, masquage en Gold"],
    ], [6, 11], size=8),

    # ------------------------------------------------------------------ 6. Recul
    p("6. Réponses aux questions de recul (§5.2.20)", H2),
]
RECUL = [
    ("1. Pourquoi une architecture Data Lake peut-elle compléter un Data Warehouse ?",
     "Le DW sert un reporting stable sur des données structurées et intégrées. Le Data Lake conserve en plus ce que "
     "le DW ne stocke pas : données brutes, formats variés (texte des avis), historique des lots reçus. Ici, le "
     "Gold en étoile reprend le rôle du DW, et Bronze / Silver apportent conservation et préparation."),
    ("2. Dans quels cas une architecture Lakehouse peut-elle être pertinente ?",
     "Quand il faut des mises à jour fiables sur le lac : corrections de lignes, chargements incrémentaux "
     "fréquents, lectures concurrentes, retour à une version antérieure, évolution de schéma maîtrisée. Ce serait "
     "le cas si data_refresh/ devenait un flux quotidien avec corrections de lignes existantes."),
    ("3. Pourquoi conserver les données brutes ?",
     "Pour rejouer un traitement après correction d'une règle, auditer un résultat, et traiter plus tard des "
     "données aujourd'hui hors périmètre (retours, clics, avis). L'UC-01 l'a montré : le dernier relevé de stock "
     "n'est complet qu'en combinant deux lots ; sans le brut de chaque lot, l'erreur serait irrécupérable."),
    ("4. Pourquoi organiser les données en zones ?",
     "Pour séparer les responsabilités : conserver (Bronze), fiabiliser (Silver), exposer (Gold). Chaque zone a "
     "ses droits, ses règles de qualité et sa durée de conservation, et une donnée Gold peut être reliée à sa "
     "source et à ses transformations (slide 41)."),
    ("5. Quelles garanties ne sont pas apportées par le seul stockage de fichiers Parquet ?",
     "Parquet apporte un stockage colonnaire, typé et compressé, mais pas de transactions ACID, pas d'historique "
     "de versions, pas de gestion de l'évolution de schéma au niveau d'une table ni de protection contre deux "
     "écritures concurrentes. Ces garanties viennent d'une couche de tables (Delta, Iceberg, Hudi)."),
    ("6. Quels risques apparaissent lorsque la gouvernance est insuffisante ?",
     "Data Swamp (fichiers incompréhensibles), KPI contradictoires faute de définition partagée (par exemple un CA "
     "brut ou net de retours), fuite de données personnelles, résultats non reproductibles, coûts de stockage "
     "incontrôlés par duplication entre zones."),
    ("7. Quels composants sont indispensables au socle et lesquels relèvent de l'approfondissement ?",
     "Socle : Linux / Ubuntu, Python, Hadoop / HDFS, NiFi, Spark / PySpark, Parquet, et ADLS Gen2 comme objectif "
     "cloud. Étude : Azure Data Factory, Synapse. Approfondissement facultatif : HBase, Delta Lake. PDGF dépend "
     "du kit (outil de génération non communiqué). Détail dans positionnement_composants.pdf."),
]
for q, a in RECUL:
    story.append(KeepTogether([p(f"<b>{q}</b>"), p(a), Spacer(1, 4)]))

story += [
    p("7. Hypothèses et points à valider", H2),
    table([
        ["Point", "Statut"],
        ["Aucun besoin temps réel n'est exprimé : traitements en batch", "Hypothèse"],
        ["Volumes futurs inconnus : le dimensionnement repose sur la croissance attendue d'un jeu Big Data",
         "Hypothèse"],
        ["Les données complémentaires du §3.6 pourraient arriver en JSON ou en journaux", "Hypothèse"],
        ["Rôle officiel de data_refresh/ (chargement incrémental déduit à l'UC-01)", "À valider"],
    ], [13, 4], size=8),
]

build(OUT, story, "UC02 - Comparaison des architectures",
      "Retail Intelligence Platform - UC-02 Comparaison des architectures")
