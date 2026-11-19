# J3 — Retail Intelligence Platform

Remise du TP Jour 3 (IPSSI, Mastère Développement, Data & IA) : **UC-06**, transformation, qualité des données et Data Lakehouse avec Python, PySpark et Parquet. Organisation : option 1 (« plusieurs fichiers ») du document « Livrables attendus – Jour 3 ». Les parties facultatives (UC-05 NoSQL / HBase, partie avancée Lakehouse) ne sont pas réalisées.

**Question métier traitée** (J1, Q3) : « Quel magasin vend le plus ? », c'est-à-dire le classement des 12 magasins selon le CA net, par année, avec le nombre de transactions et le panier moyen.

## Arborescence

```
J3_Retail_Intelligence/
├── UC06_traitements_PySpark.pdf   document principal : parties 1 à 5 + annexes
├── README.md                      ce fichier (reproduction)
├── docs/                          sources du PDF, une fiche par étape
│   ├── 01_fiche_environnement.md
│   ├── 02_inventaire_sources.md
│   ├── 03_regles_nettoyage.md
│   ├── 04_transformations.md
│   ├── 05_silver.md
│   ├── 06_gold.md
│   ├── 07_formats_parquet.md
│   ├── 08_rapport_qualite.md
│   └── 09_questions_recul.md
├── notebooks/
│   └── exploration.ipynb          exploration des sources (étapes 2 et 3), avec ses sorties
├── scripts/
│   ├── nettoyage.py               sources -> Silver (règles R1 à R22)
│   ├── transformations.py         Silver -> Gold (jointures + agrégation Q3)
│   ├── comparaison_formats.py     CSV / JSON / Parquet
│   └── controles_qualite.py       32 contrôles sur Silver et Gold
├── data/
│   ├── silver/                    store_sales, store_sales_rejets, store, date_dim (Parquet)
│   └── gold/                      q3_ca_magasin_annee (Parquet)
└── preuves/                       sorties d'exécution, expliquées dans preuves/README.md
    ├── environnement/  exploration/  transformations/
    └── silver_gold/    parquet/      qualite/
```

Le dossier `data/parquet/` de l'arborescence recommandée n'existe pas séparément : **les zones Silver et Gold sont elles-mêmes au format Parquet**. Les copies CSV et JSON de la comparaison des formats sont écrites dans `data/test/` et ignorées par Git.

## Correspondance avec les livrables obligatoires

| N° | Livrable obligatoire | Emplacement | État |
|---|---|---|---|
| 1 | Fiche d'environnement technique | `docs/01_fiche_environnement.md` ; `preuves/environnement/` | Fait |
| 2 | Inventaire technique des sources | `docs/02_inventaire_sources.md` (`store_sales`, `store`, plus `date_dim` en enrichissement) | Fait |
| 3 | Notebook d'exploration | `notebooks/exploration.ipynb` ; export lisible dans `preuves/exploration/` | Fait |
| 4 | Règles de nettoyage | `docs/03_regles_nettoyage.md` (R1 à R22, avec test des règles) | Fait |
| 5 | Scripts de transformation | `scripts/nettoyage.py`, `scripts/transformations.py` ; `docs/04_transformations.md` | Fait |
| 6 | Jeux de données Silver | `data/silver/` ; `docs/05_silver.md` (conventions, provenance, dictionnaire) | Fait |
| 7 | Jeux de données Gold | `data/gold/q3_ca_magasin_annee` ; `docs/06_gold.md` | Fait |
| 8 | Résultat Parquet et comparaison des formats | `data/silver`, `data/gold` (écrits, relus, vérifiés) ; `docs/07_formats_parquet.md` ; `preuves/parquet/` | Fait |
| 9 | Rapport de contrôles qualité | `docs/08_rapport_qualite.md` ; `scripts/controles_qualite.py` ; `preuves/qualite/` | Fait : 32 contrôles, 31 OK, 1 à signaler, 0 anomalie |
| 10 | Documentation et preuves | ce README ; `preuves/README.md` ; `UC06_traitements_PySpark.pdf` | Fait |
| — | Questions de recul (§11) | `docs/09_questions_recul.md` | Fait |

## Reproduction

### Prérequis et versions observées

| Composant | Version |
|---|---|
| Système | Ubuntu 24.04.3 LTS sous WSL2 |
| Python | 3.12.3, environnement virtuel `.venv` à la racine du dépôt |
| PySpark | 4.3.0 (installé avec `pip`, Spark en mode local `local[*]`) |
| Java | OpenJDK 21 |
| Bibliothèques | `pip install pyspark jupyterlab ipykernel` |

Le détail est dans `docs/01_fiche_environnement.md`. HDFS (J2) n'est **pas nécessaire** : toutes les lectures se font sur le disque local.

### Emplacement des données

Les sources TPCx-BB (fichiers `.dat`, séparateur `|`, sans en-tête) **ne sont pas versionnées**. Les scripts les attendent dans un dossier qui contient `data/` et `data_refresh/` :

| Paramètre | Valeur par défaut | Comment le changer |
|---|---|---|
| Dossier des sources | `/home/math34/tp_bigdata/extract/retail_project` | Variable d'environnement `RETAIL_SOURCES`, ou constante `DOSSIER_SOURCES` de `scripts/nettoyage.py` |
| Sorties Silver et Gold | `J3_Retail_Intelligence/data/` | Calculé automatiquement à partir de l'emplacement des scripts |
| Notebook d'exploration | `DOSSIER_SOURCES`, plus `sys.path` vers le dossier qui contient `schema.py` | Cellules marquées « A ADAPTER » |

**Point d'attention :** si une configuration Hadoop est présente (`HADOOP_CONF_DIR`), Spark cherche les chemins sans préfixe dans HDFS. Les scripts utilisent donc toujours le préfixe `file://`.

### Ordre d'exécution

Depuis la racine du dépôt, avec l'environnement virtuel activé (`source .venv/bin/activate`) :

```bash
export RETAIL_SOURCES=/chemin/vers/retail_project      # si différent de la valeur par défaut

python J3_Retail_Intelligence/scripts/nettoyage.py            # 1. sources -> Silver   (environ 1 min)
python J3_Retail_Intelligence/scripts/transformations.py      # 2. Silver  -> Gold     (environ 30 s)
python J3_Retail_Intelligence/scripts/controles_qualite.py    # 3. contrôles qualité   (environ 1 min)
python J3_Retail_Intelligence/scripts/comparaison_formats.py  # 4. comparaison des formats (facultatif)
```

Les étapes 2 à 4 lisent ce que produit l'étape 1 : il faut les lancer dans cet ordre. Le notebook `notebooks/exploration.ipynb` est indépendant : il lit directement les sources.

### Sorties produites

| Sortie | Produite par | Contenu |
|---|---|---|
| `data/silver/store_sales` | `nettoyage.py` | 674 211 ventes nettoyées et typées, avec leur provenance |
| `data/silver/store_sales_rejets` | `nettoyage.py` | Ventes écartées, avec leur motif (0 aujourd'hui) |
| `data/silver/store`, `data/silver/date_dim` | `nettoyage.py` | Référentiels nettoyés |
| `data/gold/q3_ca_magasin_annee` | `transformations.py` | 60 lignes magasin × année : CA net, transactions, panier moyen, rang |
| `preuves/qualite/resultats_controles.csv` | `controles_qualite.py` | Résultats des 32 contrôles |

Les zones sont **régénérées entièrement** à chaque exécution (`overwrite`, sur des répertoires dédiés au TP). Les sources ne sont jamais modifiées.

### Contrôles disponibles

- **Pendant le nettoyage** : contrôles bloquants (unicité des clés `s_store_sk` et `d_date_sk`) et relecture de chaque jeu Silver écrit.
- **Pendant les transformations** : nombre de lignes avant et après chaque jointure, lignes non rapprochées, relecture du Gold et réconciliation du CA.
- **Après coup** : `controles_qualite.py`, 32 contrôles en 7 familles (voir `docs/08_rapport_qualite.md`).

### Limites connues

- Données **synthétiques** TPCx-BB : le classement des magasins ne reflète pas une réalité commerciale (écarts de 5 à 14 %).
- CA **brut de retours** (`store_returns` hors périmètre) et non rapporté à la surface (`s_floor_space` sans unité fiable).
- `s_closed_date_sk` est incohérent dans la source : la colonne est conservée mais jamais utilisée.
- Exécution en **mode local** sur une machine : ce n'est pas un traitement distribué sur cluster (§9.2).
- Zones Silver et Gold en **Parquet simple**, sans garanties transactionnelles (pas de Delta Lake, Iceberg ou Hudi).
- Le nom des fichiers Parquet (`part-…-<uuid>`) change à chaque exécution : la zone est régénérée, pas mise à jour.

Aucun mot de passe ni information sensible n'est versionné.
