# Inventaire des fichiers TPCx-BB utilisés au Jour 2

Livrable obligatoire n° 3 (TP Jour 2, §8.2–8.3 et étape 4). Seuls les fichiers réellement inspectés et utilisés au
Jour 2 figurent ici. L'inventaire complet des 23 tables du jeu (dossiers `data/` et `data_refresh/`) a été produit
au Jour 1 : `J1_Retail_Intelligence/01_UC01_besoin_exploration/preuves/inventaire_fichiers.csv`.

## Provenance commune

| Élément | Valeur |
|---|---|
| Jeu de données | TPCx-BB (TPC Express Big Bench), données synthétiques fournies pour le module |
| Archive source | `retail_project.zip`, sha256 `dc1634e95cb3192487cad0b935a4e8dbd9ae44ca9078ac0b28513575943ed86c` (identique au Jour 1) |
| Extraction locale | `donnees/retail_project/` (copie de travail, exclue de Git ; l'archive n'est jamais modifiée) |
| Preuves | `00_source_archive.txt` (archive), `03_inspection.txt` (inspection des deux fichiers) |

## Matrice d'inventaire (§8.3)

| Fichier | Format | Taille | Lignes | Colonnes | Usage au Jour 2 | Observations |
|---|---|---|---|---|---|---|
| `store_sales.dat` | Texte délimité `\|`, sans en-tête | 92 764 700 octets (88,5 Mo) | 667 579 | 23 | UC-03 : dépôt manuel `hdfs dfs -put` | Table de faits des ventes en magasin ; voir limites ci-dessous |
| `store.dat` | Texte délimité `\|`, sans en-tête | 3 386 octets (3,3 Ko) | 12 | 29 | UC-04 : fichier de test du flux NiFi (petit fichier, consigne §12.3.5) | Dimension magasins ; voir limites ci-dessous |

## Fiches détaillées (§8.2)

### `store_sales.dat`

| Information | Relevé |
|---|---|
| Nom | `store_sales.dat` (table `store_sales`, ventes en magasin) |
| Chemin local | `donnees/retail_project/data/store_sales/store_sales.dat` |
| Chemin HDFS | `/retail-lake/raw/tpcxbb/initial/store_sales.dat` |
| Format | Texte ASCII, séparateur `\|`, pas de ligne d'en-tête, fins de ligne Windows (CRLF) |
| Taille | 92 764 700 octets ; sha256 `7e0a7f16b47483741754bb641c92601dd7384dacc8331d0bcfb8abac82ed3d2e` |
| Structure | 23 champs sur 100 % des lignes : `ss_sold_date_sk`, `ss_sold_time_sk`, `ss_item_sk`, `ss_customer_sk`, `ss_cdemo_sk`, `ss_hdemo_sk`, `ss_addr_sk`, `ss_store_sk`, `ss_promo_sk`, `ss_ticket_number`, `ss_quantity`, `ss_wholesale_cost`, `ss_list_price`, `ss_sales_price`, `ss_ext_discount_amt`, `ss_ext_sales_price`, `ss_ext_wholesale_cost`, `ss_ext_list_price`, `ss_ext_tax`, `ss_coupon_amt`, `ss_net_paid`, `ss_net_paid_inc_tax`, `ss_net_profit` |
| Types | Déduits de l'aperçu : 11 entiers (clés `*_sk`, `ss_ticket_number`, `ss_quantity`) puis 12 décimaux à 2 décimales (montants, dont `ss_net_profit` qui peut être négatif) |
| Volume | 667 579 lignes |
| Provenance | Archive `retail_project.zip`, dossier `data/` (lot initial) |
| Limites | Fichier sans en-tête : les noms de colonnes viennent de la spécification TPCx-BB (`sources/schema.py`), pas du fichier. Fins de ligne CRLF : le dernier champ contient un `\r` à retirer au Jour 3. Valeurs nulles (champ vide) dans 4 colonnes : `ss_cdemo_sk`, `ss_hdemo_sk`, `ss_addr_sk`, `ss_promo_sk`. Le couple `ss_ticket_number` + `ss_item_sk` n'est pas unique (4 136 doublons, constat J1). Dates (`ss_sold_date_sk`) de 2001-01-01 à 2005-12-13 |

### `store.dat`

| Information | Relevé |
|---|---|
| Nom | `store.dat` (table `store`, magasins) |
| Chemin local | `donnees/retail_project/data/store/store.dat` ; copie de travail déposée dans `/data/nifi/input` pour l'UC-04 |
| Chemin HDFS | `/retail-lake/raw/nifi/` (dépôt par le flux NiFi, UC-04) |
| Format | Texte ASCII, séparateur `\|`, pas de ligne d'en-tête, fins de ligne Windows (CRLF), lignes longues (303 caractères max.) |
| Taille | 3 386 octets ; sha256 `a936bc38692bdddc222cf86d08ed9d0feb761af26769212d789cf6729d1808ef` |
| Structure | 29 champs sur 100 % des lignes : `s_store_sk`, `s_store_id`, `s_rec_start_date`, `s_rec_end_date`, `s_closed_date_sk`, `s_store_name`, `s_number_employees`, `s_floor_space`, `s_hours`, `s_manager`, `s_market_id`, `s_geography_class`, `s_market_desc`, `s_market_manager`, `s_division_id`, `s_division_name`, `s_company_id`, `s_company_name`, `s_street_number`, `s_street_name`, `s_street_type`, `s_suite_number`, `s_city`, `s_county`, `s_state`, `s_zip`, `s_country`, `s_gmt_offset`, `s_tax_precentage` |
| Types | Déduits de l'aperçu : entiers (clés, effectifs, surface), dates `AAAA-MM-JJ` (`s_rec_start_date`), texte (noms, adresse, description), décimaux (`s_gmt_offset`, `s_tax_precentage`) |
| Volume | 12 lignes (12 magasins) |
| Provenance | Archive `retail_project.zip`, dossier `data/` (lot initial) |
| Limites | Sans en-tête (noms issus de la spécification). CRLF comme ci-dessus. `s_rec_end_date` vide sur toutes les lignes (100 % nulle, constat J1). Valeurs de remplissage synthétiques (`Unknown`, descriptions sans sens métier, codes comme `gcg5eGNxs` en suite). Le nom de colonne `s_tax_precentage` (faute d'orthographe) est celui de la spécification TPCx-BB, conservé tel quel |
