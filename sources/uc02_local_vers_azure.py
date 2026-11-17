"""Génère J1_Retail_Intelligence/02_UC02_architecture/local_vers_azure.pdf (UC-02, Étape G).

Usage : .venv/bin/python sources/uc02_local_vers_azure.py
Produit aussi preuves/comparaison_local_cloud.csv.
Conception logique : aucune ressource Azure n'est créée (CLI absente, abonnement non connu).
"""
import csv

from reportlab.graphics.shapes import Drawing, String
from reportlab.lib.units import cm
from reportlab.platypus import KeepTogether, PageBreak, Spacer

from chemins import UC02, UC02_PREUVES
from pdf_style import (BLUE, CELL, GREEN, GREY, H2, H3, LIGHT, NAVY, ORANGE, SUB, TEAL, TITLE, arrow, box,
                       build, link, p, table)

OUT = UC02 / "local_vers_azure.pdf"

story = [
    p("Retail Intelligence Platform", TITLE),
    p("UC-02 &ndash; De l'environnement local à la cible Azure", SUB),
    p("IPSSI &ndash; Mastère Développement, Data &amp; IA &ndash; TP Jour 1", SUB),
    Spacer(1, 8),
    table([
        ["Élément", "Valeur"],
        ["Livrable", "local_vers_azure.pdf (UC02_local_vers_azure, §5.2.17)"],
        ["Étape couverte", "Étape G &ndash; Comparer architecture locale et cloud (§5.2.13)"],
        ["Date / version", "16/11/2026 &ndash; v1"],
        ["Nature", "<b>Conception logique, non déployée.</b> Aucune ressource Azure n'a été créée : la CLI Azure "
                   "n'est pas installée et l'abonnement disponible n'est pas connu (preuves/environnement_local.txt). "
                   "La déclinaison réelle est prévue au Jour 4 (§5.2.19)."],
    ], [4, 13]),
    p("La même architecture logique (Data Lake en zones Bronze / Silver / Gold, Parquet, étoile en Gold) est "
      "déclinée deux fois. Seuls changent le stockage, l'orchestration, la sécurité et le modèle de coût ; "
      "l'arborescence des données et les règles restent identiques, ce qui rend le passage de l'un à l'autre "
      "progressif."),

    p("1. Deux déclinaisons de la même architecture", H2),
]
COMP = [
    ["Couche / sujet", "Environnement local (parcours)", "Cible cloud Azure", "Statut cloud"],
    ["Système", "Linux / Ubuntu 24.04 (WSL2)", "Services managés Azure", "-"],
    ["Ingestion", "Apache NiFi (repli : script Python)", "NiFi vers ADLS (processeur PutAzureDataLakeStorage) ou "
                                                         "Azure Data Factory", "ADF : étude"],
    ["Stockage des zones", "HDFS : /datalake/bronze|silver|gold/", "ADLS Gen2 : un conteneur par zone",
     "Objectif obligatoire (J4)"],
    ["Traitement", "Spark / PySpark en local", "Spark dans Azure Synapse (ou autre service Spark)", "Synapse : étude"],
    ["Format analytique", "Parquet", "Parquet (identique)", "-"],
    ["Exposition", "Spark SQL ; outil BI à choisir", "Synapse SQL (requêtes sur les fichiers) ; outil BI",
     "Étude"],
    ["Identités", "Comptes et groupes Linux", "Microsoft Entra ID (utilisateurs, groupes, identités managées)",
     "Conception"],
    ["Droits", "Permissions et ACL HDFS", "RBAC Azure + ACL POSIX d'ADLS Gen2", "Conception"],
    ["Secrets", "Fichiers de configuration locaux", "Azure Key Vault, identités managées", "Conception"],
    ["Supervision", "Journaux NiFi / Spark dans _journaux/", "Azure Monitor, journaux de diagnostic", "Étude"],
    ["Coûts", "Matériel local (7,5 Go de mémoire WSL, sous le minimum recommandé)", "Paiement à l'usage : stockage, "
                                                                                     "transactions, calcul",
     "Conception"],
    ["Montée en charge", "Limitée à la machine", "Ressources ajoutées à la demande", "-"],
]
story.append(table(COMP, [3, 4.8, 6, 3.2], size=7.5))
with open(UC02_PREUVES / "comparaison_local_cloud.csv", "w", newline="", encoding="utf-8") as fh:
    csv.writer(fh, delimiter=";").writerows(COMP)

# ------------------------------------------------------------------ schéma cible Azure
story += [p("2. Schéma de la cible Azure", H2),
          p("Vert : objectif obligatoire ou format de référence ; bleu : service étudié ; gris : services de "
            "sécurité, supervision et coûts communs à toute la plateforme.")]
W, H = 17 * cm, 10 * cm
d = Drawing(W, H)
box(d, 0, 150, 70, 60, ["Sources", "retail_project", ".dat (TPCx-BB)"], fill=LIGHT, size=6.8)
box(d, 84, 150, 78, 60, ["Ingestion", "NiFi ou", "Data Factory", "(étude)"], fill=BLUE, size=6.8)
# compte de stockage
sx, sy, sw, sh = 176, 98, 200, 168
box(d, sx, sy, sw, sh, [""], fill=LIGHT, size=6)
d.add(String(sx + sw / 2, sy + sh - 12, "Compte de stockage ADLS Gen2", textAnchor="middle", fontSize=7.5,
             fontName="Helvetica-Bold", fillColor=NAVY))
d.add(String(sx + sw / 2, sy + sh - 22, "StorageV2, espace de noms hiérarchique", textAnchor="middle", fontSize=6.3,
             fillColor=NAVY))
cw = (sw - 20) / 2
for i, (name, sub, fill) in enumerate([("bronze", "lots .dat d'origine", ORANGE), ("silver", "Parquet contrôlé", ORANGE),
                                       ("gold", "étoile + KPI", GREEN), ("gouvernance", "catalogue, manifestes, journaux", GREY)]):
    cx = sx + 6 + (i % 2) * (cw + 8)
    cy = sy + sh - 82 - (i // 2) * 62
    box(d, cx, cy, cw, 50, [f"conteneur {name}", sub], fill=fill, size=6.5)
box(d, 392, 180, 90, 46, ["Spark (Synapse)", "étude", "F5 : Silver -> Gold"], fill=BLUE, size=6.5)
box(d, 392, 118, 90, 46, ["Synapse SQL / BI", "étude", "F6 : KPI K01-K12"], fill=BLUE, size=6.5)
arrow(d, 70, 180, 84)
arrow(d, 162, 180, sx)
link(d, sx + sw, 203, 392, 203)
link(d, sx + sw, 141, 392, 141)
d.add(String(sx + sw / 2, sy - 10, "Même arborescence qu'en local : <zone>/<domaine>/<table>/<partition>/",
             textAnchor="middle", fontSize=6.3, fillColor=TEAL, fontName="Helvetica-Oblique"))
gw = (W - 3 * 8) / 4
for i, (a, b) in enumerate([("Microsoft Entra ID", "identités, groupes, identités managées"),
                            ("Azure Key Vault", "secrets, aucune clé dans le code"),
                            ("Azure Monitor", "journaux, alertes (étude)"),
                            ("Cost Management", "budgets, alertes de coût")]):
    box(d, i * (gw + 8), 8, gw, 40, [a, b], fill=GREY, size=6.5)
d.add(String(0, 56, "Services transverses", fontSize=6.5, fontName="Helvetica-Oblique", fillColor=NAVY))
story += [d]

# ------------------------------------------------------------------ 3 éléments ADLS
story += [
    p("3. Éléments de la cible cloud demandés (§5.2.13 G)", H2),
    p("3.1 Compte de stockage", H3),
    table([
        ["Paramètre", "Choix proposé", "Justification"],
        ["Type de compte", "StorageV2 (usage général v2)", "Type requis pour ADLS Gen2"],
        ["Espace de noms hiérarchique", "Activé", "C'est ce qui fait d'un compte de stockage un ADLS Gen2 : vrais "
                                                  "répertoires, renommage atomique, ACL POSIX"],
        ["Performance", "Standard", "Volume faible (environ 1 Go), accès par lots"],
        ["Redondance", "LRS en formation ; ZRS ou GRS en production", "Coût minimal pour un jeu synthétique ; "
                                                                      "résilience accrue pour des données réelles"],
        ["Région", "France Central (Hypothèse)", "Proximité ; données fictives mais habitude de localisation en UE"],
        ["Accès réseau", "Accès anonyme public désactivé ; TLS 1.2 minimum", "Aucune donnée ne doit être lisible "
                                                                             "sans authentification"],
        ["Nom", "Exemple : stretailintelj1 (3 à 24 caractères, minuscules et chiffres)", "Règle de nommage Azure "
                                                                                         "des comptes de stockage"],
    ], [3.6, 6, 7.4], size=7.5),
    Spacer(1, 4),
    p("3.2 Espace de stockage et conteneurs", H3),
    table([
        ["Conteneur", "Contenu", "Équivalent local"],
        ["bronze", "Lots .dat d'origine, CSV d'audit, manifestes (répertoire _manifestes/)", "/datalake/bronze/"],
        ["silver", "Parquet typé et contrôlé ; quarantaine (_quarantaine/)", "/datalake/silver/"],
        ["gold", "Modèle en étoile (dimensionnel/) et agrégats (kpi/)", "/datalake/gold/"],
        ["gouvernance", "Catalogue, journaux d'exécution", "/datalake/_catalogue/, /datalake/_journaux/"],
    ], [3, 9, 5], size=7.5),
    p("Un conteneur par zone permet d'attribuer les droits RBAC au niveau de la zone. Les noms de conteneur "
      "n'acceptent ni majuscules ni « _ » : d'où « gouvernance » plutôt que « _catalogue ».", CELL),
    Spacer(1, 4),
    p("3.3 Organisation des données", H3),
    table([
        ["Chemin local (HDFS)", "Chemin Azure (ABFS)"],
        ["hdfs:///datalake/bronze/tpcx_bb/store_sales/lot=data_refresh/…",
         "abfss://bronze@&lt;compte&gt;.dfs.core.windows.net/tpcx_bb/store_sales/lot=data_refresh/…"],
        ["hdfs:///datalake/silver/ventes/store_sales/annee=2005/mois=12/",
         "abfss://silver@&lt;compte&gt;.dfs.core.windows.net/ventes/store_sales/annee=2005/mois=12/"],
        ["hdfs:///datalake/gold/dimensionnel/fait_ventes/",
         "abfss://gold@&lt;compte&gt;.dfs.core.windows.net/dimensionnel/fait_ventes/"],
    ], [7.6, 9.4], size=7.3),
    p("Seul le préfixe change : les traitements Spark sont paramétrés par une racine de stockage, sans réécriture.",
      CELL),
]

story += [
    p("3.4 Gestion des identités et des accès", H3),
    table([
        ["Identité (Microsoft Entra ID)", "Type", "Usage"],
        ["grp-data-ingenierie", "Groupe d'utilisateurs", "Équipe Data : administration des données de toutes les zones"],
        ["grp-metier-ventes", "Groupe d'utilisateurs", "Direction commerciale, responsables de magasin : lecture Gold"],
        ["grp-metier-stocks", "Groupe d'utilisateurs", "Responsable des stocks : lecture Gold"],
        ["Identité managée du service d'ingestion (ADF ou NiFi via principal de service)", "Identité de service",
         "Écriture dans bronze"],
        ["Identité managée du service Spark", "Identité de service", "Lecture bronze, écriture silver et gold"],
    ], [6.4, 3.2, 7.4], size=7.5),
    p("Les droits sont attribués à des groupes, jamais à des personnes nommées ; les services utilisent des "
      "identités managées plutôt que des mots de passe ou des clés.", CELL),
    Spacer(1, 4),
    p("3.5 Permissions RBAC et ACL", H3),
    table([
        ["Niveau", "Attribution proposée"],
        ["RBAC sur le conteneur bronze", "Storage Blob Data Contributor : identité d'ingestion, grp-data-ingenierie ; "
                                         "Storage Blob Data Reader : identité Spark"],
        ["RBAC sur le conteneur silver", "Storage Blob Data Contributor : identité Spark, grp-data-ingenierie"],
        ["RBAC sur le conteneur gold", "Storage Blob Data Contributor : identité Spark, grp-data-ingenierie. "
                                       "Aucun rôle de données pour les groupes métier (voir ACL)"],
        ["RBAC sur le compte", "Storage Blob Data Owner : administrateur de la plateforme uniquement"],
        ["ACL POSIX sur gold", "grp-metier-ventes : lecture de dimensionnel/fait_ventes/, des dimensions et de kpi/ ; "
                               "grp-metier-stocks : lecture de dimensionnel/fait_stock/, des dimensions et de kpi/. "
                               "Droit d'exécution (x) sur chaque répertoire parent ; ACL par défaut pour que les "
                               "nouveaux fichiers héritent des droits"],
    ], [4.6, 12.4], size=7.5),
    p("Point d'attention : le RBAC est évalué avant les ACL. Si un rôle RBAC donne déjà l'accès aux données d'un "
      "conteneur, les ACL ne le restreignent pas. C'est pourquoi les groupes métier n'ont aucun rôle de données sur "
      "gold : leurs droits, plus fins (ventes ou stocks), passent uniquement par les ACL.", CELL),
    Spacer(1, 4),
    p("3.6 Sécurité des secrets", H3),
    table([
        ["Règle", "Mise en œuvre"],
        ["Aucun secret dans le code ni dans les flux NiFi", "Identités managées pour les services Azure ; Key Vault "
                                                            "pour les secrets restants"],
        ["Clés d'accès du compte non utilisées", "Désactiver l'autorisation par clé partagée si les outils le "
                                                 "permettent ; rotation sinon"],
        ["Accès temporaire", "Jetons SAS de courte durée, limités à un conteneur, uniquement si nécessaire"],
        ["Chiffrement", "Chiffrement au repos (activé par défaut sur Azure Storage) et en transit (HTTPS, TLS 1.2)"],
    ], [5.6, 11.4], size=7.5),
    Spacer(1, 4),
    p("3.7 Coûts et quotas", H3),
    table([
        ["Poste", "Mesure"],
        ["Stockage", "Volume actuel environ 1 Go par zone au plus : coût de stockage négligeable ; niveau Chaud pour "
                     "gold et silver"],
        ["Cycle de vie", "Règles de gestion du cycle de vie : lots bronze anciens vers le niveau Froid (Cool). Le niveau "
                         "Archive est déconseillé pour le Bronze, qui doit rester relisible pour rejouer un traitement"],
        ["Calcul", "Principal poste de coût : pools Spark à démarrage et arrêt automatiques, arrêtés hors traitement"],
        ["Transactions et sortie", "Éviter les petits fichiers (coût par opération) et les téléchargements massifs "
                                   "hors Azure"],
        ["Budgets", "Budget mensuel et alertes dans Cost Management"],
        ["Quotas", "Quotas de cœurs vCPU de l'abonnement (pools Spark) et limites du compte de stockage à vérifier ; "
                   "un abonnement étudiant a un crédit plafonné (À valider)"],
    ], [3.6, 13.4], size=7.5),
]

# ------------------------------------------------------------------ 4 plan / 5 statut
story += [
    p("4. Passage du local au cloud (plan pour le Jour 4)", H2),
    table([
        ["Étape", "Action", "Contrôle"],
        ["1", "Créer le compte de stockage (espace de noms hiérarchique activé) et les quatre conteneurs",
         "Propriétés du compte"],
        ["2", "Créer les groupes Entra ID et attribuer les rôles RBAC par conteneur, puis les ACL", "Test d'accès par "
                                                                                                  "profil"],
        ["3", "Déposer l'archive et les lots en Bronze (NiFi PutAzureDataLakeStorage, ou AzCopy en repli)",
         "Empreinte SHA-256 = checksum.txt"],
        ["4", "Pointer les traitements Spark sur la racine abfss:// et rejouer F1 à F5", "Règles Q01 à Q12"],
        ["5", "Comparer les résultats Gold cloud aux valeurs de référence locales", "674 211 / 674 931 lignes ; 90 000 "
                                                                                  "tickets et commandes ; 23 490 000 "
                                                                                  "lignes de stock"],
        ["6", "Mettre en place budget, alertes et règles de cycle de vie", "Alerte de test"],
    ], [1.2, 10.3, 5.5], size=7.5),

    p("5. Ce qui est déployé, étudié ou simulé", H2),
    table([
        ["Élément", "État au Jour 1"],
        ["Environnement local Linux / Python", "Réel : utilisé pour l'UC-01"],
        ["Démonstration Bronze -> Silver -> Gold (store_sales, item, date_dim)", "Réel, en local : système de "
                                                                                "fichiers au lieu de HDFS, pandas + "
                                                                                "pyarrow au lieu de Spark "
                                                                                "(preuves/demo_bronze_silver_gold/)"],
        ["HDFS, NiFi, Spark", "Conçus, non installés (Jours 2 et 3)"],
        ["Compte ADLS Gen2, conteneurs, RBAC, ACL, Key Vault", "Conception logique (ce document), non déployés"],
        ["Azure Data Factory, Synapse", "Étudiés et présentés, non déployés (non exigé)"],
    ], [7, 10], size=7.8),
    p("Conformément au §5.2.19, cette conception est une simulation : elle ne doit pas être présentée comme un "
      "déploiement réel.", CELL),

    p("6. Points à valider", H2),
    table([
        ["Point", "Statut"],
        ["Abonnement Azure disponible (étudiant, formation) et son plafond de crédit", "À valider"],
        ["Région de déploiement (France Central proposée)", "Hypothèse"],
        ["Outil d'ingestion cloud : NiFi conservé ou Azure Data Factory", "À valider (Jour 4)"],
        ["Outil de restitution BI", "À valider"],
    ], [13.5, 3.5], size=7.8),
]

build(OUT, story, "UC02 - Local vers Azure", "Retail Intelligence Platform - UC-02 Local vers Azure")
