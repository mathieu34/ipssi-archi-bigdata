# Preuves d'exécution – Jour 3 (UC-06)

Toutes les preuves ci-dessous ont été produites par une **exécution réelle** des scripts et notebooks du dossier, le 18/11/2026 : Spark 4.3.0 en mode local sur WSL2 Ubuntu 24.04, données TPCx-BB lues depuis le disque local. Les sorties texte sont celles des scripts, sans retouche. Seuls les messages techniques de Spark (warnings, barres de progression) ont été écartés.

## environnement/

| Fichier | Ce qu'il prouve |
|---|---|
| `versions.txt` | Versions réellement observées : Ubuntu 24.04.3, Python 3.12.3, Java 21, PySpark 4.3.0, Hadoop 3.5.0, 16 cœurs, 9,7 Gio de RAM |
| `test_spark.py` | Premier programme de test du sujet (§1.4.1) : création d'une session Spark et affichage d'un petit DataFrame |
| `TP3_Retail_Intelligence.ipynb` | Notebook de prise en main, avec ses sorties. Il montre la **création de la session Spark** (`Version Spark : 4.3.0`), la lecture d'un fichier source en **local** (`file://`) et depuis **HDFS** (`hdfs:///retail-lake/...`, copie du J2), l'affichage d'un schéma, et un **test d'écriture puis de relecture** dans un répertoire dédié (10 lignes relues) |

## exploration/

| Fichier | Ce qu'il prouve |
|---|---|
| `exploration_resultats.md` | Export lisible de `notebooks/exploration.ipynb` avec ses sorties : schémas, échantillons, volumes (667 579 + 6 632 ventes, 12 magasins, 109 573 jours), valeurs manquantes par colonne, doublons (0 strict, 4 082 couples ticket-produit légitimes), valeurs atypiques, cohérence des montants, couverture du calendrier (0 jour orphelin). Les réponses aux questions du §4.6.3 sont en fin de document |

## transformations/

| Fichier | Ce qu'il prouve |
|---|---|
| `nettoyage_sortie.txt` | Exécution de `scripts/nettoyage.py` : règles R1 à R22 appliquées, 0 conversion échouée, 0 doublon, **0 rejet**, schémas typés obtenus (identique à `silver_gold/silver_sortie.txt`, le même script écrivant aussi la zone Silver) |
| `transformations_sortie.txt` | Exécution de `scripts/transformations.py` : **jointures vérifiées** (674 211 lignes avant et après, 0 non rapprochée), contrôle « un ticket = un magasin et un jour », **agrégation Q3** (60 lignes, CA total réconcilié au centime) et classements |

## silver_gold/

| Fichier | Ce qu'il prouve |
|---|---|
| `silver_sortie.txt` | Production de la **zone Silver** : 4 jeux écrits en Parquet puis **relus et contrôlés** (lignes relues = attendues, schéma conservé) : `store_sales` 674 211, `store_sales_rejets` 0, `store` 12, `date_dim` 109 573 |
| `gold_sortie.txt` | Production du **jeu Gold** `q3_ca_magasin_annee` à partir du Silver : écrit en Parquet, relu, 60 lignes, 60 couples (année, magasin) uniques, CA relu = CA des ventes ; schéma et contenu 2005 affichés |

## parquet/

| Fichier | Ce qu'il prouve |
|---|---|
| `comparaison_formats_sortie.txt` | Le même jeu (674 211 ventes) écrit en CSV, JSON et Parquet puis relu : **volumes observés** (92 / 353 / 40 Mo), types relus (`string` / `double` / `decimal(7,2)`), temps de lecture, sommes identiques. Les écritures et relectures Parquet des zones Silver et Gold sont prouvées dans `silver_gold/` |

## qualite/

| Fichier | Ce qu'il prouve |
|---|---|
| `controles_qualite_sortie.txt` | Exécution de `scripts/controles_qualite.py` : **32 contrôles** (complétude, unicité, validité, cohérence, volumes, intégrité référentielle), dont **31 OK, 1 à signaler** (`s_closed_date_sk`, déjà connu), **0 anomalie** |
| `resultats_controles.csv` | Les mêmes résultats sous forme de tableau (séparateur `;`), réutilisable : identifiant, famille, jeu, règle, résultat, statut |
