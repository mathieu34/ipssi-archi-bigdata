# Fiche d'environnement – TP Jour 3 (UC-06)

Versions et paramètres **effectivement observés** sur le poste de travail le 18/11/2026.

## 1. Système et versions

| Composant | Version observée | Commande de vérification |
|---|---|---|
| Système | Ubuntu 24.04.3 LTS sous WSL2 (Windows) | `cat /etc/os-release` |
| Python | 3.12.3 | `python --version` |
| Environnement virtuel | `.venv` à la racine du dépôt (`ipssi-archi-bigdata/.venv`) | `which python` |
| PySpark / Spark | 4.3.0 | `python -c "import pyspark; print(pyspark.__version__)"` |
| Java | OpenJDK 21.0.13 | `java -version` |
| Hadoop (HDFS, installé au J2) | 3.5.0, avec Java 17 (défini dans `hadoop-env.sh`) | `hadoop version` |
| JupyterLab / ipykernel | 4.6.6 / 7.4.0 | `python -m pip show jupyterlab ipykernel` |
| pandas | 3.1.1 | `python -m pip show pandas` |

Spark a été installé avec `pip install pyspark`, sans installation séparée de Spark. Les variables `SPARK_HOME` et `JAVA_HOME` ne sont donc pas définies : Spark utilise le Java du système.

**Point d'attention :** PySpark 4.3.0 signale au démarrage qu'il ne supporte pas encore complètement pandas ≥ 3.0. Ce TP n'utilise pas les conversions vers pandas (`toPandas()`), donc ce message n'a pas d'impact.

## 2. Mode d'exécution

- **Spark en mode local** : `master("local[*]")`. Les traitements s'exécutent sur une seule machine et utilisent tous ses cœurs. Il n'y a pas de cluster Spark.
- Ce mode ne reproduit pas toutes les conditions d'un environnement distribué de production (cf. §1.4.1 du sujet).

## 3. Ressources disponibles

| Ressource | Valeur | Commande |
|---|---|---|
| Processeurs (cœurs logiques) | 16 | `nproc` |
| Mémoire vive allouée à WSL | 9,7 Gio, dont environ 4,7 Gio disponibles à l'observation | `free -h` |
| Swap | 4,0 Gio | `free -h` |

## 4. Interface de travail

- Notebooks Jupyter (`.ipynb`) exécutés dans **VS Code** (extension Jupyter, connexion WSL), avec le noyau Python du `.venv`.
- Scripts Python exécutés en ligne de commande (`python script.py`).

## 5. Données : stockage et chemins

> **Pour reproduire sur un autre poste :** les chemins ci-dessous sont ceux du poste de travail d'origine. Remplacez `/home/math34/tp_bigdata/extract` par le dossier qui contient votre copie des données TPCx-BB (le dossier parent de `retail_project/`). Gardez le préfixe `file://` : un chemin local s'écrit avec trois barres obliques, par exemple `file:///home/<utilisateur>/...`. Les chemins HDFS ne changent pas si les données ont été chargées comme au J2.

| Rôle | Chemin | Remarque |
|---|---|---|
| Sources TPCx-BB (lecture) | `file:///home/math34/tp_bigdata/extract/retail_project/data/` | Fichiers `.dat` : texte délimité par `\|`, sans ligne d'en-tête |
| Sources TPCx-BB, copie HDFS (J2) | `hdfs:///retail-lake/raw/tpcxbb/initial/` | HDFS pseudo-distribué local (`hdfs://localhost:9000`) ; à démarrer avec `start-dfs.sh` |
| Sorties du TP (Silver, Gold, Parquet) | `J3_Retail_Intelligence/data/` (à créer) | Répertoire dédié, distinct des sources |

**Point d'attention :** la variable `HADOOP_CONF_DIR=/opt/hadoop/etc/hadoop` (configuration du J2) fixe `fs.defaultFS = hdfs://localhost:9000`. Un chemin sans préfixe est donc cherché **dans HDFS**. Pour lire ou écrire sur le disque local, il faut toujours préfixer le chemin par `file://`.

Les fichiers sources ne sont jamais modifiés : toutes les écritures se font dans le répertoire de sortie dédié.

## 6. Preuves

La preuve de création de la session Spark et de lecture d'un fichier se trouve dans le notebook `preuves/environnement/TP3_Retail_Intelligence.ipynb`, qui est conservé avec les sorties de ses cellules. Le script de test `preuves/environnement/test_spark.py` (§1.4.1 du sujet) est rangé dans le même dossier :
- cellule 1 : création de la session Spark, qui affiche `Version Spark : 4.3.0` ;
- cellule 2 : lecture de `store_sales.dat`, qui affiche les 5 premières lignes.
