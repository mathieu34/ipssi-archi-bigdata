"""Génère J1_Retail_Intelligence/02_UC02_architecture/gouvernance.pdf (UC-02, Étape F).

Usage : .venv/bin/python sources/uc02_gouvernance.py
Produit aussi preuves/regles_gouvernance.csv et preuves/regles_qualite.csv.
"""
import csv

from reportlab.platypus import KeepTogether, PageBreak, Preformatted, Spacer
from reportlab.lib.styles import ParagraphStyle

from chemins import UC02, UC02_PREUVES
from pdf_style import CELL, H2, H3, SUB, TITLE, build, p, table

OUT = UC02 / "gouvernance.pdf"
CODE = ParagraphStyle("code", fontName="Courier", fontSize=7, leading=8.6, leftIndent=8)


def save_csv(name, rows):
    with open(UC02_PREUVES / name, "w", newline="", encoding="utf-8") as fh:
        csv.writer(fh, delimiter=";").writerows(rows)


story = [
    p("Retail Intelligence Platform", TITLE),
    p("UC-02 &ndash; Règles minimales de gouvernance", SUB),
    p("IPSSI &ndash; Mastère Développement, Data &amp; IA &ndash; TP Jour 1", SUB),
    Spacer(1, 8),
    table([
        ["Élément", "Valeur"],
        ["Livrable", "gouvernance.pdf (UC02_gouvernance, §5.2.17)"],
        ["Étape couverte", "Étape F &ndash; Définir les règles minimales de gouvernance (§5.2.13)"],
        ["Date / version", "16/11/2026 &ndash; v1"],
        ["Documents liés", "architecture_cible.pdf (zones, règles Silver), schema_flux.pdf (contrôles par flux), "
                           "local_vers_azure.pdf (identités, RBAC / ACL, secrets, coûts)"],
        ["Nature", "Règles de conception ; leur mise en œuvre commence au Jour 2."],
    ], [4, 13]),
    p("Le cours rappelle qu'un Data Lake sans qualité, catalogue, sécurité et gouvernance devient un « Data Swamp » "
      "(slide 39). Ce document fixe, pour chacun des sept points demandés, des règles vérifiables, leur mise en "
      "œuvre locale et cloud, et l'indicateur qui permet de les suivre."),

    p("1. Synthèse des sept règles", H2),
]
SYNTHESE = [
    ["Point (§5.2.13 F)", "Règle minimale", "Mise en œuvre locale", "Mise en œuvre Azure", "Indicateur de suivi"],
    ["Traçabilité de la provenance", "Toute donnée est reliée à son lot, son fichier source et sa date d'ingestion",
     "Manifeste par lot ; colonnes _lot, _fichier_source, _date_ingestion", "Mêmes colonnes ; manifestes dans le "
                                                                            "conteneur gouvernance",
     "% de lignes Silver / Gold sans provenance (cible 0)"],
    ["Documentation des fichiers et tables", "Aucune table n'est publiée sans fiche de catalogue",
     "Catalogue (fichier) repris de inventaire_sources.xlsx", "Catalogue équivalent (Microsoft Purview en option, "
                                                              "non requis)", "Nombre de tables sans fiche (cible 0)"],
    ["Contrôles de qualité", "Règles automatiques à chaque lot ; bloquantes ou signalées", "Scripts Python / Spark "
                                                                                            "(section 4)",
     "Mêmes traitements Spark", "Taux de rejet par table et par lot"],
    ["Gestion des accès", "Droits par zone et par profil, au plus juste", "Comptes et groupes Linux, droits HDFS",
     "Entra ID, RBAC, ACL", "Revue des droits à chaque nouveau profil"],
    ["Protection des données", "Données personnelles minimisées et cloisonnées", "Exclues du Gold ; Silver restreint",
     "Idem + chiffrement au repos du stockage", "Colonnes personnelles présentes en Gold (cible 0)"],
    ["Suivi des traitements", "Chaque exécution laisse un journal et un rapport de contrôle", "Journaux NiFi / Spark "
                                                                                             "dans _journaux/",
     "Azure Monitor (étude)", "Exécutions en échec, durée, lignes rejetées"],
    ["Maîtrise des coûts et des volumes", "Conservation, compression et partitionnement définis par zone",
     "Parquet compressé ; durées de conservation", "Niveaux d'accès, cycle de vie, budgets", "Volume par zone, "
                                                                                              "coût mensuel"],
]
story.append(table(SYNTHESE, [2.8, 3.6, 3.6, 3.4, 3.6], size=7.3))
save_csv("regles_gouvernance.csv", SYNTHESE)

# ------------------------------------------------------------------ 2 Traçabilité
story += [
    p("2. Traçabilité de la provenance", H2),
    p("Principe du cours : « une donnée transformée doit pouvoir être reliée à sa source, à ses règles de "
      "transformation et à ses contrôles » (slide 41). Trois mécanismes y répondent."),
    Spacer(1, 3),
    table([
        ["Mécanisme", "Contenu", "Où"],
        ["Manifeste de lot", "Identifiant du lot, origine, liste des fichiers, taille, nombre de lignes, empreinte "
                             "SHA-256, date de dépôt, version du schéma appliqué", "bronze/_manifestes/"],
        ["Colonnes techniques", "_lot, _fichier_source, _date_ingestion, _id_ligne (Silver) ; _lot conservé en Gold",
         "Chaque table Silver et Gold"],
        ["Journal d'exécution", "Traitement, lot, version du script, début / fin, lignes lues / écrites / rejetées, "
                                "résultat des contrôles", "_journaux/"],
    ], [3.2, 9.8, 4], size=7.8),
    Spacer(1, 4),
    p("Exemple de manifeste pour le lot data_refresh (valeurs réelles pour store_sales) :", CELL),
    Preformatted("""{
  "lot": "data_refresh",
  "origine": "retail_project.zip (TPCx-BB, synthétique) - version non communiquée",
  "empreinte_archive_sha256": "dc1634e95cb3192487cad0b935a4e8dbd9ae44ca9078ac0b28513575943ed86c",
  "date_ingestion": "AAAA-MM-JJ",
  "fichiers": [
    {"table": "store_sales", "fichier": "store_sales.dat", "octets": 922171,
     "lignes": 6632, "champs_attendus": 23, "sha256": "<calculé au dépôt>"}
  ],
  "schema": "schema.py (spécification TPCx-BB)"
}""", CODE),
    Spacer(1, 3),
    p("L'empreinte de l'archive est comparée à preuves/checksum.txt de l'UC-01 avant toute ingestion.", CELL),

    p("3. Documentation des fichiers et tables (catalogue)", H2),
    p("Le catalogue évite le Data Swamp : « comment comprendre un fichier déposé il y a six mois si personne n'a "
      "documenté sa provenance, son format, sa signification et ses transformations ? » (slide 44). Il est "
      "initialisé avec l'inventaire de l'UC-01 (36 fichiers, 522 colonnes)."),
    Spacer(1, 3),
    table([
        ["Champ de la fiche", "Exemple (fait_ventes)"],
        ["Nom, zone, chemin", "fait_ventes, Gold, gold/dimensionnel/fait_ventes/"],
        ["Description et grain", "Une ligne = une ligne de vente (magasin ou web)"],
        ["Propriétaire / responsable", "Équipe Data (technique) ; direction commerciale (métier)"],
        ["Sources et traitements", "silver/ventes/store_sales et web_sales ; traitement F5"],
        ["Colonnes : nom, type, définition, statut", "ca_net, décimal, net_paid (HT, après remises et coupons, "
                                                     "retours non déduits), Vérifié"],
        ["Classification", "Interne (aucune donnée personnelle directe)"],
        ["Qualité connue", "Doublons (transaction, produit) légitimes ; 0 orphelin"],
        ["Fraîcheur", "Dernier lot : data_refresh (ventes jusqu'au 31/12/2005)"],
    ], [5, 12], size=7.8),
    Spacer(1, 3),
    p("Convention de nommage : minuscules, sans accents ni espaces ; zone/domaine/table/partition ; préfixes fait_ "
      "et dim_ en Gold ; colonnes techniques préfixées par « _ ».", CELL),
]

# ------------------------------------------------------------------ 4 Qualité
QUALITE = [
    ["ID", "Règle", "Zone / flux", "Type", "Seuil", "Effet"],
    ["Q01", "Empreinte de l'archive = checksum.txt", "Ingestion", "Intégrité", "Égalité", "Bloquant"],
    ["Q02", "Nombre de champs par ligne = schéma (23, 34, 4…)", "Silver, F1-F3", "Validité", "100 % des lignes",
     "Ligne en quarantaine ; fichier bloqué si 0 % conforme"],
    ["Q03", "Clé primaire unique (*_sk ; (date, produit, entrepôt) pour le stock)", "Silver, F2-F3", "Unicité",
     "0 doublon", "Bloquant"],
    ["Q04", "Clés étrangères présentes dans les référentiels", "Silver, F1-F3", "Intégrité", "0 orphelin",
     "Ligne en quarantaine"],
    ["Q05", "net_paid = ext_sales_price - coupon_amt ; ext_sales_price = quantity x sales_price", "Silver, F1",
     "Cohérence", "Écart &lt;= 0,01", "Bloquant si l'écart est généralisé"],
    ["Q06", "quantity &gt; 0 dans les ventes", "Silver, F1", "Validité", "100 %", "Ligne en quarantaine"],
    ["Q07", "Une seule date, un seul client, un seul magasin par transaction", "Silver, F1", "Cohérence", "100 %",
     "Signalé"],
    ["Q08", "Relevé de stock complet = 90 000 lignes", "Silver, F3", "Complétude", "Égalité", "Bloquant pour le relevé"],
    ["Q09", "Quantité de stock vide comptée à part, jamais remplacée par 0", "Silver, F3", "Exactitude", "-",
     "Règle de transformation"],
    ["Q10", "Somme de ca_net et nombre de lignes identiques entre Silver et Gold", "Gold, F5", "Réconciliation",
     "Égalité", "Bloquant"],
    ["Q11", "Transactions distinctes : 90 000 tickets, 90 000 commandes (lots actuels)", "Gold, F5", "Réconciliation",
     "Égalité", "Signalé si nouveau lot"],
    ["Q12", "Aucune colonne personnelle (nom, e-mail, login) en Gold", "Gold, F5", "Conformité", "0 colonne",
     "Bloquant"],
]
story += [p("4. Contrôles de qualité", H2),
          p("Les règles reprennent les contrôles exécutés à l'UC-01 (preuves/controles_*.txt) : elles ont déjà été "
            "testées sur les données réelles. Dimensions de qualité du cours (slide 33) : complétude, validité, "
            "cohérence, unicité, exactitude, fraîcheur, intégrité."),
          Spacer(1, 3), table(QUALITE, [1, 6, 2.4, 2.1, 2.2, 3.3], size=7.3),
          p("Les lignes en quarantaine sont conservées avec leur motif (silver/_quarantaine/) ; un taux de rejet "
            "anormal est signalé dans le rapport du lot.", CELL)]
save_csv("regles_qualite.csv", [[c.replace("&lt;", "<").replace("&gt;", ">") for c in r] for r in QUALITE])

# ------------------------------------------------------------------ 5 Accès
story += [
    p("5. Gestion des accès", H2),
    p("Principe du moindre privilège : chaque profil n'accède qu'aux zones nécessaires à son rôle."),
    Spacer(1, 3),
    table([
        ["Profil", "Bronze", "Silver", "Gold", "Gouvernance (catalogue, journaux)"],
        ["Équipe Data (ingénierie)", "Lecture / écriture", "Lecture / écriture", "Lecture / écriture", "Lecture / écriture"],
        ["Traitements automatiques (NiFi, Spark)", "Écriture (ingestion), lecture", "Lecture / écriture",
         "Écriture", "Écriture des journaux"],
        ["Direction commerciale", "Aucun", "Aucun", "Lecture (ventes, KPI)", "Lecture du catalogue"],
        ["Responsable de magasin", "Aucun", "Aucun", "Lecture (ventes, KPI)", "Lecture du catalogue"],
        ["Responsable des stocks", "Aucun", "Aucun", "Lecture (stocks, KPI)", "Lecture du catalogue"],
    ], [4.4, 2.8, 2.8, 3.4, 3.6], size=7.5),
    p("Restriction par magasin (un responsable ne voit que son établissement) : envisageable en filtrant le Gold "
      "par magasin_key ; non retenue dans cette version (À valider avec le métier).", CELL),

    p("6. Protection des données", H2),
    table([
        ["Donnée", "Classification", "Mesure"],
        ["customer : c_first_name, c_last_name, c_email_address, c_login, c_birth_day/month",
         "Personnelle (fictive, traitée comme réelle)", "Conservée en Bronze et Silver à accès restreint ; exclue du "
                                                        "Gold (minimisation)"],
        ["customer_address : rue, numéro, code postal", "Personnelle", "Bronze uniquement dans cette version"],
        ["c_customer_sk", "Identifiant technique (pseudonyme)", "Seule clé client exposée en Gold"],
        ["Ventes, stocks, référentiels produit / magasin", "Interne", "Lecture métier en Gold"],
        ["Empreintes, journaux, catalogue", "Interne", "Équipe Data"],
    ], [6.2, 4, 6.8], size=7.5),
    p("Autres mesures : pas de copie de données personnelles hors de la plateforme (exports, postes de travail) ; "
      "chiffrement au repos et en transit dans la cible cloud ; durée de conservation définie (section 8).", CELL),
]

# ------------------------------------------------------------------ 7 Suivi
story += [
    p("7. Suivi des traitements", H2),
    table([
        ["Élément suivi", "Contenu", "Usage"],
        ["Journal d'exécution", "Traitement, lot, version du script, début / fin, statut", "Diagnostic, reprise"],
        ["Rapport de contrôle", "Résultat des règles Q01 à Q12, lignes lues / écrites / rejetées",
         "Décision de publier ou non le lot"],
        ["Historique des lots", "Liste des lots ingérés et leur statut (publié, bloqué, rejoué)", "Fraîcheur des KPI"],
        ["Alertes", "Contrôle bloquant en échec, taux de rejet anormal, traitement trop long", "Intervention de "
                                                                                              "l'équipe Data"],
    ], [3.6, 7.8, 5.6], size=7.8),
    p("Le journal de profilage de l'UC-01 (preuves/profilage_log.txt) est un premier exemple de ce format.", CELL),

    p("8. Maîtrise des coûts et des volumes", H2),
    table([
        ["Levier", "Règle", "Effet attendu"],
        ["Durée de conservation", "Bronze : tous les lots tant qu'ils peuvent servir à rejouer ; Silver et Gold : "
                                  "reconstructibles, donc remplaçables ; journaux : durée limitée",
         "Éviter l'accumulation sans valeur"],
        ["Format", "Parquet compressé en Silver et Gold", "Volume réduit, lectures plus rapides"],
        ["Partitionnement", "Ventes par année / mois, stocks par relevé", "Ne lire que les partitions utiles"],
        ["Petits fichiers", "Regrouper les écritures (taille de fichier raisonnable)", "Éviter la surcharge du "
                                                                                       "stockage distribué"],
        ["Duplication", "Une seule copie par zone ; pas d'extraction parallèle non documentée",
         "Volume total maîtrisé (environ 1 Go de brut aujourd'hui)"],
        ["Cloud", "Niveaux d'accès, règles de cycle de vie, budgets et alertes", "Voir local_vers_azure.pdf"],
    ], [3.2, 8.6, 5.2], size=7.8),

    p("9. Rôles et responsabilités", H2),
    table([
        ["Rôle", "Responsabilités de gouvernance"],
        ["Équipe Data", "Catalogue, règles de qualité, traitements, journaux, gestion technique des droits"],
        ["Responsables métier (direction commerciale, magasins, stocks)", "Définition des KPI, validation des "
                                                                          "règles métier, demande d'accès"],
        ["Commanditaire du projet", "Validation des points « À valider » (provenance du kit, rôle de "
                                      "data_refresh/, devise)"],
    ], [6, 11], size=7.8),

    p("10. Risques en l'absence de gouvernance", H2),
    table([
        ["Risque", "Règle qui le prévient"],
        ["Data Swamp : fichiers incompréhensibles", "Catalogue (§3), nommage, manifestes (§2)"],
        ["KPI contradictoires (ex. CA brut ou net de retours)", "Définitions du dictionnaire KPI dans le catalogue"],
        ["Erreur silencieuse (ex. relevé de stock incomplet)", "Contrôles bloquants Q08, Q10"],
        ["Fuite de données personnelles", "Accès par zone (§5), exclusion du Gold (§6), Q12"],
        ["Résultats non reproductibles", "Bronze immuable, journaux, versions des scripts"],
        ["Coûts incontrôlés", "Conservation, compression, partitionnement, budgets (§8)"],
    ], [7, 10], size=7.8),
]

build(OUT, story, "UC02 - Gouvernance", "Retail Intelligence Platform - UC-02 Gouvernance")
