# preuves (UC-02) — index des preuves

Preuves du dossier UC-02 (§5.2.16 du sujet). Les documents UC-02 sont des documents de **conception** :
aucune architecture n'est déployée au Jour 1. Les fichiers CSV reprennent les tableaux des PDF pour pouvoir
être relus ou réutilisés dans un tableur ; ils sont produits par les scripts de `sources/` (racine du projet).

**Point d'entrée : `index_preuves.pdf`** — titre, explication et extrait de chaque preuve, plus les schémas (architecture annotée, flux, cible Azure) en annexe.

## Preuves attendues par le sujet (§5.2.16)

| Preuve attendue | Fichier(s) | Produit par |
|---|---|---|
| Schéma d'architecture | `../architecture_cible.pdf` (section 1) | `uc02_architecture_cible.py` |
| Schéma des flux | `../schema_flux.pdf` (section 2), `flux.csv` | `uc02_schema_flux.py` |
| Tableau de comparaison des architectures | `tableau_comparaison_architectures.csv`, `../comparaison_architectures.pdf` | `uc02_comparaison_architectures.py` |
| Matrice de positionnement des composants | `matrice_composants.csv`, `../positionnement_composants.pdf` | `uc02_positionnement_composants.py` |
| Description des zones de données | `zones_donnees.csv`, `modele_gold.csv`, `../architecture_cible.pdf` (sections 3 à 5) | `uc02_architecture_cible.py` |
| Règles de gouvernance proposées | `regles_gouvernance.csv`, `regles_qualite.csv`, `../gouvernance.pdf` | `uc02_gouvernance.py` |
| Comparaison local / cloud | `comparaison_local_cloud.csv`, `../local_vers_azure.pdf` | `uc02_local_vers_azure.py` |

## Manipulation réellement effectuée : démonstration Bronze -> Silver -> Gold

Dossier `demo_bronze_silver_gold/`, produit par `sources/demo_bronze_silver_gold.py` sur store_sales, item et date_dim
(data/ + data_refresh/). Repli documenté : système de fichiers local (arborescence /datalake/… identique à la cible)
au lieu de HDFS, pandas + pyarrow au lieu de Spark. Ce n'est pas le déploiement de l'architecture cible.

| Fichier | Contenu |
|---|---|
| `journal_execution.txt` | Étapes, lignes lues / écrites / en quarantaine, réconciliations (toutes OK) |
| `arborescence_datalake_demo.txt` | Zones bronze / silver / gold réellement créées |
| `manifeste_lot=*.json` | Manifestes de lot (fichiers, lignes, SHA-256) |
| `schema_parquet_silver_store_sales.txt` | Types stockés dans le Parquet Silver |
| `gold_k02_ca_categorie_annee.csv` / `.parquet` | Résultat Gold : CA net par catégorie et par année |

## Mesures complémentaires

| Fichier | Contenu | Utilisé dans |
|---|---|---|
| `valeurs_reference.txt` | Lignes et transactions de `data/` + `data_refresh/` (674 211 / 674 931 lignes de ventes, 90 000 tickets et commandes, 23 490 000 lignes de stock = 261 relevés x 90 000) | Contrôles de réconciliation (schema_flux, gouvernance Q10-Q11, plan Azure) |
| `environnement_local.txt` | Système, versions, composants installés ou absents, mémoire, disque | positionnement_composants (état au Jour 1, contraintes), local_vers_azure |

Les preuves sur les données elles-mêmes (inventaire, qualité, relations) sont dans
`../../01_UC01_besoin_exploration/preuves/`.
