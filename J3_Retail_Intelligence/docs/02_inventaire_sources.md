# Inventaire technique des sources – TP Jour 3 (UC-06, étape 2)

**Question métier retenue :** Q3 du J1, « Quel magasin vend le plus ? » (`J1_Retail_Intelligence/01_UC01_besoin_exploration/questions_decisionnelles.pdf`). La question décisionnelle associée est : classer les 12 magasins selon le CA net, par année, avec le nombre de transactions et le panier moyen.

**Sources retenues :** `store_sales` (les ventes) et `store` (le référentiel des magasins), reliées par `ss_store_sk = s_store_sk`. Une **source d'enrichissement**, `date_dim` (le calendrier), s'y ajoute : elle fournit l'année demandée par Q3 (voir le §3).

**Méthode :** toutes les valeurs ci-dessous ont été mesurées avec PySpark dans `notebooks/exploration.ipynb`, cellules 4 à 8, avec leurs sorties conservées. Il y a deux exceptions, vérifiées au terminal : l'encodage et la fin de ligne (commande `file`), et la conversion des identifiants de date (lecture de `date_dim.dat`).

> **Pour reproduire :** les chemins sont relatifs au dossier des données TPCx-BB, ici `~/tp_bigdata/extract/retail_project/`. Adaptez la variable `DOSSIER_SOURCES` du notebook.

## 1. Tableau d'inventaire

| Information | Source 1 – `store_sales` | Source 2 – `store` |
|---|---|---|
| **Nom réel du fichier** | `store_sales.dat` | `store.dat` |
| **Emplacement** | `data/store_sales/` (lot initial) **et** `data_refresh/store_sales/` (lot complémentaire), même structure | `data/store/` uniquement (pas de lot `data_refresh`) |
| **Format** | Texte délimité par `\|`, **sans ligne d'en-tête**, ASCII, fins de ligne Windows (CRLF) | Idem |
| **Taille** | 88,47 Mo (`data`) + 0,88 Mo (`data_refresh`) | moins de 0,01 Mo (environ 3 Ko) |
| **Nombre de lignes** | 667 579 (`data`) + 6 632 (`data_refresh`) = **674 211** | **12** |
| **Nombre de colonnes** | 23 | 29 |
| **Colonnes principales (pour Q3)** | `ss_store_sk` (magasin), `ss_net_paid` (montant net payé), `ss_ticket_number` (ticket), `ss_sold_date_sk` (date), `ss_item_sk` (produit), `ss_quantity` | `s_store_sk` (identifiant technique), `s_store_id` (identifiant métier), `s_store_name`, `s_floor_space`, `s_city`, `s_state`, `s_closed_date_sk` |
| **Types observés** (`inferSchema`) | 11 colonnes `integer` : les identifiants `*_sk`, `ss_ticket_number` et `ss_quantity`. 12 colonnes `double` : les prix et montants | `integer` pour les identifiants, `s_floor_space`, `s_zip`, `s_gmt_offset`… ; `string` pour les libellés ; `date` pour `s_rec_start_date` ; **`string` pour `s_rec_end_date`** (colonne entièrement vide, voir les anomalies) |
| **Clé candidate** | **Aucune clé simple.** Le couple (`ss_ticket_number`, `ss_item_sk`) n'est **pas unique** : 663 443 couples distincts pour 667 579 lignes, soit 4 136 lignes qui répètent un couple | **`s_store_sk`** (12 valeurs distinctes pour 12 lignes) ; `s_store_id` est aussi unique (12/12) |
| **Granularité** | Une ligne = **une ligne d'article d'un ticket de caisse** (un produit acheté dans un ticket, avec sa quantité et ses montants). Un même produit peut apparaître sur plusieurs lignes du même ticket | Une ligne = **un magasin** (une seule version par magasin : `s_rec_end_date` est toujours vide) |
| **Anomalies identifiées** | Voir le §2 | Voir le §2 |

### Période couverte par `store_sales`

`ss_sold_date_sk` est un identifiant de jour. Il a été converti en date grâce à `date_dim.dat`.

| Lot | `ss_sold_date_sk` min → max | Dates | Tickets communs avec l'autre lot |
|---|---|---|---|
| `data` | 36890 → 38697 | 01/01/2001 → 13/12/2005 | **0** |
| `data_refresh` | 38697 → 38715 | 13/12/2005 → 31/12/2005 | **0** |

**Conclusion :** `data_refresh` n'est pas une copie du lot initial. Il contient les **ventes des 18 derniers jours de 2005**, et la coupure entre les deux fichiers tombe au milieu de la journée du 13/12/2005. Sans ce lot, l'année 2005 serait incomplète. **Les deux lots seront donc réunis en Silver**, avec une colonne de provenance. Aucun ticket n'étant commun aux deux lots, cette réunion ne crée pas de doublon.

## 2. Premiers constats et anomalies

| # | Source | Constat | Statut | Suite |
|---|---|---|---|---|
| A1 | `store_sales` | 4 136 lignes répètent un couple (ticket, produit) | Mesuré | Étape 3 : regarder ces lignes. Au J1, elles avaient des prix et quantités différents, donc il s'agirait de lignes légitimes et non de doublons |
| A2 | `store_sales` | Ventes réparties sur deux fichiers (`data` et `data_refresh`) | Mesuré | Réunir les deux lots en Silver avec une colonne de provenance |
| A3 | Les deux | Pas d'en-tête : les noms de colonnes viennent de la spécification TPCx-BB (`tp_bigdata/schema.py`) | Mesuré | Nommer les colonnes explicitement à la lecture |
| A4 | Les deux | Fins de ligne Windows (CRLF) | Mesuré | Les types inférés pour la dernière colonne (`double`) montrent que Spark les gère. À surveiller si une colonne texte se trouve en dernière position |
| A5 | `store` | `s_rec_end_date` est vide sur les 12 lignes, d'où un type `string` inféré au lieu de `date` | Mesuré | Typer explicitement la colonne en `date` en Silver |
| A6 | `store` | `s_closed_date_sk` est **incohérent** : les valeurs vont de 6235 (27/01/1917) à 88139 (26/04/2141). Des magasins seraient « fermés » avant 2001 alors qu'ils vendent entre 2001 et 2005 | Mesuré (déjà relevé au J1) | Ne pas utiliser cette colonne pour exclure des magasins |
| A7 | `store` | `s_floor_space` vaut entre 5,7 et 8,9 millions, une valeur peu réaliste pour une surface de magasin | Mesuré ; l'unité n'est pas documentée | Ne pas calculer de CA au m² sans réserve |
| A8 | `store_sales` | `ss_ticket_number` commence à 0 | Mesuré | Valeur valide pour un identifiant technique : ce n'est pas une anomalie |
| A9 | Les deux | Valeurs manquantes, doublons stricts et valeurs atypiques | Mesuré à l'étape 3 | Voir la synthèse en fin de `notebooks/exploration.ipynb` (§4.6) |

## 3. Source d'enrichissement – `date_dim`

Les ventes ne portent qu'un identifiant de jour (`ss_sold_date_sk`). Pour calculer le CA **par année**, il faut la table calendrier `date_dim`. Elle a été inventoriée et contrôlée avant toute jointure (notebook, section « Source d'enrichissement »).

| Information | `date_dim` |
|---|---|
| **Nom réel du fichier** | `date_dim.dat` |
| **Emplacement** | `data/date_dim/` uniquement (pas de lot `data_refresh`) |
| **Format** | Identique aux autres sources : texte délimité par `\|`, sans en-tête |
| **Taille** | 14,68 Mo |
| **Nombre de lignes / colonnes** | 109 573 / 28 |
| **Colonnes utilisées** | `d_date_sk` (clé), `d_date` (date réelle), `d_year` (année), `d_moy` (mois) |
| **Types observés** | `d_date_sk`, `d_year`, `d_moy` : `integer` ; `d_date` : `date` |
| **Clé candidate** | `d_date_sk` : 109 573 valeurs distinctes pour 109 573 lignes, donc **unique** |
| **Granularité** | Une ligne = **un jour** du calendrier, du 01/01/1900 au 31/12/2199 |
| **Contrôles avant jointure** | Aucune valeur nulle sur les 4 colonnes utilisées ; `d_year` cohérent avec `d_date` (0 écart) ; **les 1 826 jours de vente existent tous dans `date_dim` (0 orphelin)** |
| **Anomalies** | Aucune sur les colonnes utilisées |

**Relation avec les ventes :** `ss_sold_date_sk = d_date_sk`, de type N:1 (plusieurs ventes par jour, un seul jour par vente). La jointure ne fera perdre aucune vente, ce qui confirme le constat du J1 (fiche Q4 de `questions_decisionnelles.pdf`).

**Répartition des ventes par année** (après jointure) : 2001 : 134 873 lignes, 2002 : 135 084, 2003 : 134 773, 2004 : 136 014, 2005 : 133 467. Chaque année est couverte du 1er janvier au 31 décembre.

## 4. Questions techniques (§4.5.2)

**1. Les fichiers sont-ils structurés, semi-structurés ou non structurés ?**
**Structurés.** Ce sont des fichiers texte tabulaires, avec un nombre fixe de colonnes par ligne (23 et 29), séparées par `|`. Le seul manque est l'absence d'en-tête : la structure est connue grâce à la spécification TPCx-BB, pas grâce au fichier lui-même.

**2. Les colonnes sont-elles correctement typées ?**
**En grande partie, oui.** L'inférence de Spark donne des types cohérents : entiers pour les identifiants et les quantités, décimaux pour les montants, texte pour les libellés. Deux réserves. D'abord, `s_rec_end_date` est inférée en `string` parce qu'elle est entièrement vide. Ensuite, les dates de vente sont stockées sous forme d'identifiants entiers (`ss_sold_date_sk`) et non de dates : il faut une jointure avec `date_dim` pour obtenir l'année. Comme le rappelle le sujet (§4.6.2), l'inférence ne vaut pas validation : les types seront fixés explicitement en Silver.

**3. Certaines colonnes contiennent-elles des valeurs nulles ?**
**Oui pour `s_rec_end_date`** (100 % vide, c'est-à-dire un magasin sans date de fin de validité). Le comptage de l'étape 3 (§4.6.2) a confirmé ce que montrait le J1 : aucune valeur nulle sur les colonnes utiles à Q3. Seuls quelques liens facultatifs de `store_sales` sont parfois nuls (`ss_cdemo_sk`, `ss_hdemo_sk`, `ss_addr_sk`, `ss_promo_sk`, moins de 0,1 % des lignes chacun).

**4. Les identifiants sont-ils uniques lorsque cela est attendu ?**
**Oui pour `store`** : `s_store_sk` et `s_store_id` sont uniques (12/12). **Pour `store_sales`**, aucune colonne seule n'est censée être unique, et même le couple (ticket, produit) ne l'est pas (4 136 répétitions). Les ventes n'ont donc pas de clé naturelle simple, ce qui sera pris en compte pour la détection des doublons.

**5. La granularité est-elle connue ?**
**Oui.** `store` : un magasin par ligne, une seule version. `store_sales` : une ligne d'article d'un ticket, sur la période du 01/01/2001 au 31/12/2005, lots `data` et `data_refresh` réunis.

**6. Les données sont-elles adaptées aux questions métier sélectionnées au Jour 1 ?**
**Oui, pour Q3.** Le CA net vient de `ss_net_paid`, le nombre de transactions de `ss_ticket_number` (en valeurs distinctes), et le magasin de `ss_store_sk`, relié à `s_store_sk`. L'année demande en plus la table `date_dim`, qui sera ajoutée comme source d'enrichissement. Il y a deux limites : 2005 n'est complète qu'avec le lot `data_refresh`, et le rapport du CA à la surface est fragile (A7).
