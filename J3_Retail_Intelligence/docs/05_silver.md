# Zone Silver – TP Jour 3 (UC-06, étape 6)

**Rôle de la zone :** contenir les données **nettoyées, typées et harmonisées**, proches des sources mais fiables (§2.6.3). Aucune agrégation n'est faite ici : la granularité d'origine est conservée.

**Production :** `scripts/nettoyage.py`. Le script applique les règles R1 à R22 (`docs/03_regles_nettoyage.md`), écrit chaque jeu, puis le **relit pour le contrôler**.

**Sortie d'exécution :** `preuves/silver_gold/silver_sortie.txt`.

## 1. Conventions

| Convention | Choix | Justification |
|---|---|---|
| **Emplacement** | `J3_Retail_Intelligence/data/silver/<nom_du_jeu>/` | Répertoire dédié au TP, distinct des sources (§1.10.1, §1.10.5) |
| **Nommage des jeux** | Nom de la table TPCx-BB d'origine (`store_sales`, `store`, `date_dim`) ; suffixe `_rejets` pour les lignes écartées | On retrouve la source d'un jeu à son nom ; les rejets sont rangés à côté de leur jeu |
| **Nommage des colonnes** | Noms de la spécification TPCx-BB, inchangés (`ss_`, `s_`, `d_`) ; colonnes ajoutées en minuscules ; colonnes techniques préfixées par `_` | Reste fidèle à la source ; distingue les colonnes métier des colonnes techniques |
| **Format** | **Parquet**, compression Snappy | Conserve les types (`decimal`, `date`), stockage en colonnes et compressé. Le CSV perdrait les types à la relecture |
| **Nombre de fichiers** | 1 à 2 fichiers par jeu (`coalesce`) | Évite le problème des « petits fichiers » : sans regroupement, `store_sales` sortait en 200 fichiers |
| **Mode d'écriture** | `overwrite` | La zone est entièrement régénérée à chaque exécution, dans un répertoire dédié au TP (§1.9.4, encadré « Point de vigilance ») |

## 2. Provenance

Chaque jeu Silver porte des **colonnes de provenance** (§3.3 et §4.9.2, « conserver la provenance ») :

| Colonne | Contenu | Présente dans |
|---|---|---|
| `lot_source` | `data` ou `data_refresh` : lot d'origine de **chaque ligne** | `store_sales`, `store_sales_rejets` |
| `_fichiers_source` | Fichier(s) `.dat` d'origine, relatifs au dossier des données TPCx-BB | Tous les jeux |
| `_date_traitement` | Date et heure de l'exécution du traitement | Tous les jeux |

## 3. Jeux produits

| Jeu | Contenu | Granularité | Lignes | Colonnes | Taille | Fichiers |
|---|---|---|---|---|---|---|
| `silver/store_sales` | Ventes magasin nettoyées, lots `data` et `data_refresh` réunis | Une ligne d'article d'un ticket | **674 211** | 26 (23 + 3 de provenance) | 40,1 Mo | 2 |
| `silver/store_sales_rejets` | Ventes écartées, avec le motif du rejet | Idem | **0** | 27 (+ `motif_rejet`) | moins de 0,01 Mo | 1 |
| `silver/store` | Référentiel des magasins nettoyé | Un magasin | **12** | 31 (29 + 2 de provenance) | 0,01 Mo | 1 |
| `silver/date_dim` | Calendrier réduit aux colonnes utiles | Un jour | **109 573** | 6 (4 + 2 de provenance) | 0,84 Mo | 1 |

**Comparaison des volumes :** les ventes passent de **89,4 Mo** en texte (`data` + `data_refresh`) à **40,1 Mo** en Parquet, alors que trois colonnes ont été ajoutées. La comparaison complète des formats sera faite à l'étape 8 (§4.11.3).

**Le jeu de rejets est vide, mais il est écrit quand même.** Il prouve que le contrôle a eu lieu. Il fixe aussi son schéma, pour qu'un prochain chargement qui produirait des rejets les range au même endroit.

## 4. Schémas et dictionnaire des colonnes

### `silver/store_sales`

| Colonne | Type | Description |
|---|---|---|
| `ss_sold_date_sk` | integer | Jour de la vente, clé vers `date_dim.d_date_sk` |
| `ss_sold_time_sk` | integer | Heure de la vente, clé vers `time_dim` (non utilisée) |
| `ss_item_sk` | integer | Produit vendu, clé vers `item` (non utilisée) |
| `ss_customer_sk` | integer | Client, clé vers `customer` (non utilisée) |
| `ss_cdemo_sk`, `ss_hdemo_sk`, `ss_addr_sk` | integer | Profil démographique, foyer et adresse du client. **Peuvent être nuls** (règle R6) |
| `ss_store_sk` | integer | Magasin, clé vers `store.s_store_sk`. Obligatoire |
| `ss_promo_sk` | integer | Promotion appliquée. **Peut être nul** = pas de promotion (R6) |
| `ss_ticket_number` | integer | Numéro de ticket : un passage en caisse. Unique sur toute la base, chaque ticket appartenant à un seul magasin et à un seul jour (contrôle de l'étape 5) |
| `ss_quantity` | integer | Quantité vendue, de 1 à 100 (R11) |
| `ss_wholesale_cost`, `ss_list_price`, `ss_sales_price` | decimal(7,2) | Coût d'achat unitaire, prix catalogue unitaire, prix de vente unitaire |
| `ss_ext_discount_amt` | decimal(7,2) | Remise totale de la ligne |
| `ss_ext_sales_price` | decimal(7,2) | Montant de la ligne : quantité × prix de vente |
| `ss_ext_wholesale_cost`, `ss_ext_list_price` | decimal(7,2) | Coût d'achat et prix catalogue de la ligne |
| `ss_ext_tax` | decimal(7,2) | Taxe de la ligne |
| `ss_coupon_amt` | decimal(7,2) | Montant du coupon de réduction |
| **`ss_net_paid`** | decimal(7,2) | **Montant net payé = `ss_ext_sales_price` − `ss_coupon_amt`**. Il sert de **CA net** pour Q3 (contrôlé par R14) |
| `ss_net_paid_inc_tax` | decimal(7,2) | Montant net payé, taxes comprises |
| `ss_net_profit` | decimal(7,2) | Marge nette de la ligne. **Peut être négative** (R13) |
| `lot_source` | string | Lot d'origine : `data` (667 579 lignes) ou `data_refresh` (6 632 lignes) |
| `_fichiers_source`, `_date_traitement` | string, timestamp | Provenance (§2) |

### `silver/store` (colonnes principales)

| Colonne | Type | Description |
|---|---|---|
| `s_store_sk` | integer | Clé technique du magasin, **unique** (R17) |
| `s_store_id` | string | Clé métier du magasin (16 caractères) |
| `s_store_name` | string | Nom du magasin (Forest, Buffalo…), sans espaces parasites (R15) |
| `s_city`, `s_county`, `s_state`, `s_zip`, `s_country` | string | Localisation. `s_zip` est en texte pour conserver d'éventuels zéros initiaux |
| `s_rec_start_date` | date | Début de validité de la fiche |
| `s_rec_end_date` | date | Fin de validité. **Toujours nulle** = fiche toujours valide (R16) |
| `s_closed_date_sk` | integer | Date de fermeture. **Non fiable**, à ne pas utiliser (R18) |
| `s_floor_space` | integer | Surface, **unité inconnue**, à ne pas utiliser en ratio (R19) |
| `s_number_employees`, `s_market_id`, `s_division_id`, `s_company_id`… | integer, string | Autres informations descriptives, conservées telles quelles |
| `_fichiers_source`, `_date_traitement` | string, timestamp | Provenance |

### `silver/date_dim`

| Colonne | Type | Description |
|---|---|---|
| `d_date_sk` | integer | Clé du jour, **unique** (R21) |
| `d_date` | date | Date réelle |
| `d_year` | integer | Année |
| `d_moy` | integer | Mois de l'année (1 à 12) |
| `_fichiers_source`, `_date_traitement` | string, timestamp | Provenance |

### `silver/store_sales_rejets`

Même schéma que `silver/store_sales`, avec une colonne de plus : `motif_rejet` (string). Elle liste, séparés par des virgules, les motifs `conversion_echouee`, `champ_obligatoire_nul`, `magasin_inconnu`, `date_hors_periode`, `valeur_hors_domaine`, `montant_incoherent` et `date_inconnue`.

## 5. Contrôles après écriture (§4.9.3)

Chaque jeu est **relu depuis le disque** juste après son écriture :

| Contrôle | Méthode | Résultat |
|---|---|---|
| **Présence des fichiers** | Fichiers `.parquet` présents dans le répertoire (plus le marqueur `_SUCCESS`) | OK pour les 4 jeux |
| **Format** | Relecture avec `spark.read.parquet` | OK |
| **Lisibilité** | La relecture et le comptage fonctionnent | OK |
| **Nombre de lignes** | Lignes relues = lignes attendues (674 211 / 0 / 12 / 109 573) | OK pour les 4 jeux |
| **Schéma** | Colonnes relues = colonnes écrites, dans le même ordre ; types `decimal(7,2)` et `date` conservés | OK |
| **Cohérence** | Le volume de `store_sales` est égal à celui des sources (667 579 + 6 632), 0 rejet | OK |

Le script **s'arrête avec une erreur** si l'un de ces contrôles échoue.

## 6. Limites

- Silver en **Parquet simple** : il n'y a pas de garantie transactionnelle. Une écriture interrompue en mode `overwrite` peut laisser un répertoire incomplet. Le marqueur `_SUCCESS` permet de le détecter, mais pas de revenir à la version précédente (§4.11.3, encadré « Point de vigilance », et partie avancée §6.2).
- La zone est **régénérée en entier** à chaque exécution : il n'y a pas de traitement incrémental (§6.5).
