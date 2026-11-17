"""Génère J1_Retail_Intelligence/02_UC02_architecture/positionnement_composants.pdf (UC-02, Étape D).

Usage : .venv/bin/python sources/uc02_positionnement_composants.py
Produit aussi preuves/matrice_composants.csv. Constat machine : preuves/environnement_local.txt.
"""
import csv

from reportlab.graphics.shapes import Drawing, String
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import KeepTogether, PageBreak, Spacer

from chemins import UC02, UC02_PREUVES
from pdf_style import (BLUE, CELL, GREEN, GREY, H2, H3, LIGHT, NAVY, ORANGE, SUB, TEAL, TITLE, arrow, box,
                       build, p, table)

OUT = UC02 / "positionnement_composants.pdf"

story = [
    p("Retail Intelligence Platform", TITLE),
    p("UC-02 &ndash; Positionnement des composants technologiques", SUB),
    p("IPSSI &ndash; Mastère Développement, Data &amp; IA &ndash; TP Jour 1", SUB),
    Spacer(1, 8),
    table([
        ["Élément", "Valeur"],
        ["Livrable", "positionnement_composants.pdf (UC02_positionnement_composants, §5.2.17)"],
        ["Étape couverte", "Étape D &ndash; Positionner les composants technologiques (§5.2.13)"],
        ["Date / version", "16/11/2026 &ndash; v1"],
        ["Référence des statuts", "Tableau du §5.2.13 D du sujet et slide 51 du cours, repris sans modification"],
        ["Constat machine", "preuves/environnement_local.txt (relevé du 16/11/2026)"],
    ], [4, 13]),
    p("Règle appliquée : aucun composant facultatif n'est rendu obligatoire (HBase, Delta Lake), et aucun composant "
      "n'est présenté comme installé ou déployé s'il ne l'est pas. Les statuts ci-dessous sont ceux du référentiel ; "
      "la dernière colonne indique l'état réel au Jour 1."),

    p("1. Matrice de positionnement", H2),
]

MATRICE = [
    ["Composant", "Statut (référentiel)", "Rôle dans le parcours", "Rôle dans l'architecture Retail Intelligence",
     "Jour", "État au Jour 1"],
    ["Linux / Ubuntu", "Obligatoire", "Environnement de référence local", "Système hôte de tous les composants "
                                                                        "locaux", "J1", "Installé : Ubuntu 24.04.3 LTS sous WSL2"],
    ["Python", "Obligatoire", "Exploration, scripts, traitements", "Profilage et contrôles de l'UC-01 ; repli "
                                                                   "d'ingestion ; scripts de contrôle", "J1",
     "Installé et utilisé : Python 3.12, pandas, pyarrow ; profilage UC-01 et démonstration Bronze -> Silver -> "
     "Gold (preuves/demo_bronze_silver_gold/)"],
    ["Hadoop / HDFS", "Obligatoire (repli documenté)", "Stockage distribué local", "Stockage des zones Bronze, "
                                                                                   "Silver et Gold en local", "J2",
     "Non installé (prévu au Jour 2)"],
    ["Apache NiFi", "Obligatoire (repli documenté)", "Ingestion et orchestration des flux", "Flux F1 à F4 : dépôt "
                                                                                             "des lots en Bronze, "
                                                                                             "empreinte, manifeste",
     "J2", "Non installé (prévu au Jour 2)"],
    ["Apache Spark / PySpark", "Obligatoire", "Traitements distribués et transformations", "Bronze vers Silver "
                                                                                           "(typage, contrôles) ; "
                                                                                           "Silver vers Gold (F5) ; "
                                                                                           "Spark SQL (F6)", "J3",
     "Non installé (prévu au Jour 3)"],
    ["Parquet", "Format de référence", "Stockage analytique colonnaire", "Format des zones Silver et Gold", "J3",
     "Utilisé dans la démonstration locale (pyarrow) : Silver et Gold écrits en Parquet"],
    ["HBase", "Facultatif", "Approfondissement NoSQL", "Non retenu dans le socle (voir section 3)", "J3",
     "Non installé ; non requis"],
    ["PDGF", "Selon kit disponible", "Génération des données si le kit le permet", "Non utilisé : les données sont "
                                                                                   "fournies déjà générées",
     "-", "Outil de génération non communiqué (UC-01)"],
    ["Delta Lake", "Facultatif", "Approfondissement Lakehouse", "Évolution possible vers un Lakehouse "
                                                                "(comparaison_architectures.pdf)", "J3",
     "Non installé ; non requis"],
    ["ADLS Gen2", "Objectif obligatoire", "Déclinaison cloud de l'architecture", "Cible cloud des zones Bronze, "
                                                                                 "Silver, Gold (local_vers_azure.pdf)",
     "J4", "Conception logique uniquement"],
    ["Azure Data Factory", "Présentation / étude", "Orchestration et intégration cloud", "Alternative cloud à NiFi "
                                                                                         "pour les flux", "J4",
     "Étude uniquement"],
    ["Azure Synapse", "Présentation / étude", "Services analytiques cloud", "Spark et SQL en cloud pour F5 et F6",
     "J4", "Étude uniquement"],
]
story.append(table(MATRICE, [2.6, 2.4, 3, 4.3, 1.1, 3.6], size=7.3))
with open(UC02_PREUVES / "matrice_composants.csv", "w", newline="", encoding="utf-8") as fh:
    csv.writer(fh, delimiter=";").writerows(MATRICE)

# ------------------------------------------------------------------ schéma
story += [p("2. Placement des composants dans l'architecture", H2),
          p("Couleur = statut du référentiel. Vert : obligatoire ou format de référence ; bleu : présentation / "
            "étude ; gris pointillé : facultatif ou selon kit. La ligne du bas donne l'équivalent cloud.")]
W, H = 17 * cm, 9.2 * cm
d = Drawing(W, H)
n, gap = 5, 14
bw = (W - gap * (n - 1)) / n
X = [i * (bw + gap) for i in range(n)]
for x, t in zip(X, ["Ingestion", "Stockage", "Traitement", "Format", "Exposition"]):
    d.add(String(x + bw / 2, H - 9, t, textAnchor="middle", fontSize=7.5, fontName="Helvetica-Bold", fillColor=TEAL))
d.add(String(0, H - 24, "Local", fontSize=7, fontName="Helvetica-Oblique", fillColor=NAVY))
LOCAL = [(["Apache NiFi", "obligatoire"], GREEN, False), (["Hadoop / HDFS", "obligatoire"], GREEN, False),
         (["Spark / PySpark", "obligatoire"], GREEN, False), (["Parquet", "référence"], GREEN, False),
         (["Spark SQL", "+ outil BI à choisir"], GREEN, False)]
y1 = H - 70
for x, (lines, fill, dash) in zip(X, LOCAL):
    box(d, x, y1, bw, 40, lines, fill=fill, dashed=dash, size=7)
for i in range(n - 1):
    arrow(d, X[i] + bw, y1 + 20, X[i + 1])
OPT = [None, (["HBase", "facultatif"], GREY, True), (["Delta Lake", "facultatif"], GREY, True),
       (["PDGF", "selon kit (amont)"], GREY, True), None]
y2 = y1 - 52
for x, o in zip(X, OPT):
    if o:
        box(d, x, y2, bw, 36, o[0], fill=o[1], dashed=o[2], size=7)
d.add(String(0, y2 - 18, "Cloud (Jour 4)", fontSize=7, fontName="Helvetica-Oblique", fillColor=NAVY))
CLOUD = [(["Azure Data Factory", "étude"], BLUE, False), (["ADLS Gen2", "objectif obligatoire"], GREEN, False),
         (["Spark (Synapse)", "étude"], BLUE, False), (["Parquet", "référence"], GREEN, False),
         (["Synapse SQL", "étude"], BLUE, False)]
y3 = y2 - 70
for x, (lines, fill, dash) in zip(X, CLOUD):
    box(d, x, y3, bw, 40, lines, fill=fill, dashed=dash, size=7)
box(d, 0, 4, W, 22, ["Socle commun : Linux / Ubuntu (obligatoire) et Python (obligatoire) pour l'exploration, les "
                     "scripts de contrôle et le repli d'ingestion"], fill=LIGHT, bold_first=False, size=7)
story += [d]

# ------------------------------------------------------------------ justification
story += [
    p("3. Justification des choix", H2),
    p("3.1 Composants du socle", H3),
    table([
        ["Composant", "Pourquoi dans cette architecture (lien avec les contraintes de l'UC-01)"],
        ["NiFi", "Dépôt de lots sans modification, calcul d'empreinte et traçabilité de la provenance : exigences "
                 "« conserver chaque lot reçu » et « traçabilité »."],
        ["HDFS", "Stockage distribué des zones ; la plus grosse table (inventory, 23,5 M lignes) et la croissance "
                 "attendue justifient la répartition sur plusieurs nœuds ; arborescence identique à ADLS Gen2."],
        ["Spark / PySpark", "Typage, contrôles et jointures sur des millions de lignes (inventory, clics) ; "
                            "lecture et écriture natives de Parquet ; Spark SQL pour l'exposition."],
        ["Parquet", "Types stockés dans le fichier (le .dat n'en a aucun), lecture par colonnes pour les KPI, "
                    "compression."],
        ["Python", "Déjà utilisé pour tout le profilage et les contrôles de l'UC-01 ; ces scripts deviennent les "
                   "contrôles automatiques de la zone Silver."],
    ], [3, 14], size=7.8),
    Spacer(1, 4),
    p("3.2 Composants facultatifs ou selon kit : pourquoi ils ne sont pas dans le socle", H3),
    table([
        ["Composant", "Raison de ne pas l'inclure", "Quand l'envisager"],
        ["HBase", "Aucune question métier n'exige un accès unitaire par clé en temps réel ; les KPI sont des "
                  "agrégats", "Consultation instantanée d'une fiche client ou d'un stock produit par une application"],
        ["Delta Lake", "Le chargement par lots de fichiers statiques n'exige pas de transactions ; Parquet suffit",
         "Corrections de lignes existantes, chargements incrémentaux fréquents, besoin d'historique de versions"],
        ["PDGF", "Les données sont fournies déjà générées ; l'outil de génération n'est pas communiqué",
         "Si le kit le fournit : générer des volumes plus grands pour tester la montée en charge"],
    ], [2.5, 7, 7.5], size=7.8),
    Spacer(1, 4),
    p("3.3 Composants cloud étudiés (Jour 4)", H3),
    p("ADLS Gen2 est l'objectif obligatoire de la déclinaison cloud ; Azure Data Factory et Synapse sont présentés "
      "et étudiés comme équivalents cloud de NiFi et de Spark / Spark SQL, sans déploiement exigé au Jour 1 "
      "(détail : local_vers_azure.pdf)."),
    p("4. Contraintes de l'environnement local et solutions de repli", H2),
    table([
        ["Constat (preuves/environnement_local.txt)", "Statut", "Conséquence", "Mesure proposée"],
        ["Mémoire allouée à WSL : 7,5 Go (3,3 Go disponibles au relevé)", "Vérifié",
         "Inférieure aux 8 Go minimum recommandés (§3.2) ; HDFS, NiFi et Spark ensemble risquent de saturer",
         "Augmenter la mémoire WSL (fichier .wslconfig côté Windows) ; démarrer les services un par un ; Spark en "
         "mode local avec mémoire limitée"],
        ["Java absent", "Vérifié", "Prérequis de Hadoop, NiFi et Spark", "Installer un JDK compatible au Jour 2"],
        ["Hadoop, NiFi, Spark absents", "Vérifié", "Attendu : installation prévue aux Jours 2 et 3",
         "Suivre la progression du module"],
        ["Disque : 948 Go libres", "Vérifié", "Largement suffisant (données : 1 Go, plus les copies par zone)", "-"],
        ["CLI Azure absente ; abonnement non connu", "Vérifié / À valider", "Pas de déploiement cloud possible "
                                                                             "aujourd'hui", "Conception logique au "
                                                                                            "Jour 1 ; accès à "
                                                                                            "confirmer"],
    ], [4.4, 1.9, 5, 5.7], size=7.5),
    Spacer(1, 5),
    table([
        ["Composant", "Repli si l'installation échoue (slide 51 : « obligatoire, avec repli documenté »)"],
        ["Hadoop / HDFS", "Système de fichiers local avec exactement la même arborescence /datalake/… ; le passage à "
                          "HDFS ou ADLS ne change que le préfixe des chemins. Déjà mis en œuvre dans la démonstration "
                          "Bronze -> Silver -> Gold (datalake_demo/)"],
        ["Apache NiFi", "Script Python de dépôt : copie du lot, calcul SHA-256, écriture du manifeste (mêmes règles "
                        "que le flux NiFi)"],
        ["Spark / PySpark", "Aucun repli prévu par le référentiel (obligatoire) ; PySpark peut s'exécuter en mode "
                            "local sur une seule machine"],
    ], [3.2, 13.8], size=7.8),
    p("Un repli doit être documenté comme tel dans les preuves : il ne doit pas être présenté comme le composant "
      "obligatoire qu'il remplace.", CELL),

    p("5. Synthèse par statut", H2),
    table([
        ["Statut", "Composants"],
        ["Obligatoire", "Linux / Ubuntu, Python, Hadoop / HDFS, Apache NiFi, Apache Spark / PySpark"],
        ["Format de référence", "Parquet"],
        ["Objectif obligatoire (cloud, Jour 4)", "ADLS Gen2"],
        ["Présentation / étude", "Azure Data Factory, Azure Synapse"],
        ["Facultatif", "HBase, Delta Lake"],
        ["Selon kit disponible", "PDGF"],
    ], [5, 12], size=8),
]

build(OUT, story, "UC02 - Positionnement des composants",
      "Retail Intelligence Platform - UC-02 Positionnement des composants")
