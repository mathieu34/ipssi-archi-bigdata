# Rapport de contrôles qualité – TP Jour 3 (UC-06, étape 9)

**Objet :** vérifier que les jeux **produits**, c'est-à-dire la zone Silver et le jeu Gold Q3, sont cohérents et adaptés à leur usage (§4.12.1). Les contrôles portent sur les sorties du traitement, et non sur les sources, qui ont été explorées à l'étape 3.

**Traitement :** `scripts/controles_qualite.py`, exécuté après `nettoyage.py` et `transformations.py`.

**Preuves :** `preuves/qualite/controles_qualite_sortie.txt` (sortie complète) et `preuves/qualite/resultats_controles.csv` (tableau des résultats, réutilisable).

**Statuts :**
- **OK** : la règle est respectée ;
- **ANOMALIE** : la règle n'est pas respectée et il faut corriger ;
- **À SIGNALER** : un écart connu et documenté, sans impact sur Q3, qui reste une limite à garder en tête.

## 1. Bilan

| Contrôles | OK | À signaler | Anomalie |
|---|---|---|---|
| **32** | **31** | **1** | **0** |

Les 7 familles du §4.12.2 sont couvertes : complétude, unicité, validité des types, cohérence des valeurs, volumes, clés candidates et intégrité référentielle.

## 2. Résultats détaillés

### Complétude

| Id | Jeu | Règle | Résultat | Statut |
|---|---|---|---|---|
| C01 | silver/store_sales | Champs obligatoires de Q3 non nuls (magasin, ticket, produit, date, quantité, montant net) | 0 valeur nulle | OK |
| C02 | silver/store_sales | Liens facultatifs : moins de 1 % de nulls (conservés, R6) | `ss_cdemo_sk` 250, `ss_hdemo_sk` 308, `ss_addr_sk` 462, `ss_promo_sk` 159 (au plus 0,069 %) | OK |
| C03 | silver/store | Identifiant, nom et localisation renseignés | 0 valeur nulle | OK |
| C04 | gold | Aucune valeur nulle sur les dimensions et les mesures | 0 valeur nulle | OK |

### Unicité et clés candidates

| Id | Jeu | Règle | Résultat | Statut |
|---|---|---|---|---|
| C05 | silver/store | `s_store_sk` unique | 12 / 12 | OK |
| C06 | silver/store | `s_store_id` unique | 12 / 12 | OK |
| C07 | silver/date_dim | `d_date_sk` unique | 109 573 / 109 573 | OK |
| C08 | gold | Granularité (`annee`, `ss_store_sk`) unique | 60 / 60 | OK |
| C09 | silver/store_sales | Aucun doublon strict (23 colonnes identiques) | 0 | OK |
| C10 | silver/store_sales | Un ticket = un seul passage en caisse : 1 magasin, 1 jour, 1 heure, 1 client | 0 ticket ambigu | OK |

C10 va plus loin que le contrôle de l'étape 5 : il vérifie aussi l'**heure** et le **client**. Il confirme que `ss_ticket_number` identifie bien une transaction, ce qui valide le calcul de `nb_transactions`.

### Validité des types

| Id | Jeu | Types attendus | Résultat | Statut |
|---|---|---|---|---|
| C11 | silver/store_sales | identifiants `int`, montants `decimal(7,2)`, `lot_source` `string` | 0 écart | OK |
| C12 | silver/store | `s_store_sk` `int`, `s_store_name` `string`, dates de validité `date` | 0 écart | OK |
| C13 | silver/date_dim | `d_date_sk` et `d_year` `int`, `d_date` `date` | 0 écart | OK |
| C14 | gold | `annee` et `rang_annee` `int`, `ca_net` `decimal(17,2)`, `nb_transactions` `bigint`, `panier_moyen` `decimal(18,2)` | 0 écart | OK |

### Cohérence des valeurs

| Id | Jeu | Règle | Résultat | Statut |
|---|---|---|---|---|
| C15 | silver/store_sales | `ss_quantity` entre 1 et 100 | 0 hors domaine | OK |
| C16 | silver/store_sales | `ss_net_paid` ≥ 0 | 0 négatif | OK |
| C17 | silver/store_sales | `ss_ext_sales_price` = quantité × prix unitaire (à 0,01 près) | 0 écart | OK |
| C18 | silver/store_sales | `ss_net_paid` = `ss_ext_sales_price` − `ss_coupon_amt` (à 0,01 près) | 0 écart | OK |
| C19 | silver/store_sales | Ventes entre le 01/01/2001 et le 31/12/2005 | du 2001-01-01 au 2005-12-31 | OK |
| C20 | gold | `panier_moyen` = `ca_net` / `nb_transactions` | 0 écart | OK |
| C21 | gold | Chaque année : 12 magasins classés de 1 à 12 | 0 année incohérente | OK |
| C22 | silver/store | Aucun magasin « fermé » avant le début de ses ventes | **5 magasins** ont une date de fermeture antérieure à 2001 alors qu'ils vendent de 2001 à 2005 | **À SIGNALER** |
| C31 | gold ↔ silver | Somme de `ca_net` (Gold) = somme de `ss_net_paid` (Silver) | 1 162 073 847,88 des deux côtés | OK |
| C32 | gold ↔ silver | Somme de `nb_transactions` (Gold) = tickets distincts (Silver) | 90 000 des deux côtés | OK |

### Volumes

| Id | Jeu | Règle | Résultat | Statut |
|---|---|---|---|---|
| C23 | silver/store_sales | Lignes Silver + rejets = lignes des fichiers sources | 674 211 + 0 = 674 211, comme les sources | OK |
| C24 | silver/store_sales | Les deux lots sont présents | `data` 667 579, `data_refresh` 6 632 | OK |
| C25 | silver/store | 12 magasins | 12 | OK |
| C26 | gold | 12 magasins × 5 années | 60 lignes | OK |
| C27 | gold | Volumes annuels comparables (écart < 5 %, aucune année tronquée) | de 133 467 à 136 014 lignes par année, écart maximal de 1,9 % | OK |

C23 compte les lignes directement dans les fichiers sources (`spark.read.text`). Il prouve qu'**aucune ligne n'a été perdue** entre les sources et le Silver. C27 vérifie que 2005 n'est pas tronquée, ce qui serait le cas si le lot `data_refresh` avait été oublié.

### Intégrité référentielle

| Id | Relation | Règle | Résultat | Statut |
|---|---|---|---|---|
| C28 | silver/store_sales → silver/store | Tout `ss_store_sk` existe dans `s_store_sk` | 0 orphelin | OK |
| C29 | silver/store_sales → silver/date_dim | Tout `ss_sold_date_sk` existe dans `d_date_sk` | 0 orphelin | OK |
| C30 | gold → silver/store | Tout magasin du Gold existe dans `store` | 0 orphelin | OK |

## 3. Synthèse (§4.12.3)

**Règles respectées :** 31 contrôles sur 32. Les jeux Silver sont complets sur les champs utiles, sans doublon, correctement typés, cohérents dans leurs calculs et référentiellement intègres. Le jeu Gold est exactement **réconcilié** avec le Silver (même CA au centime, même nombre de tickets).

**Anomalies restantes :**
- **C22 – `s_closed_date_sk` incohérent** sur 5 magasins sur 12. C'est une anomalie **de la source**, connue depuis le J1 (règle R18). Elle n'est pas corrigeable sans information externe. **Elle n'a pas d'impact sur Q3**, car la colonne n'est jamais utilisée pour filtrer.
- **Anomalies non bloquantes documentées au nettoyage** : `s_floor_space` sans unité fiable (R19), 74 % de ventes à marge négative (R13). Elles sont hors du périmètre de Q3.

**Données mises à l'écart :** **aucune**. Le jeu `silver/store_sales_rejets` est vide : 0 ligne rejetée sur 674 211.

**Limites des contrôles :**
- Les contrôles vérifient la **cohérence interne** des données, pas leur **vérité** : sur des données synthétiques, il n'existe pas de référence externe (un CA comptable, par exemple) à laquelle se comparer.
- Les seuils retenus (moins de 1 % de nulls facultatifs, moins de 5 % d'écart de volume annuel, 0,01 de tolérance sur les montants) sont des choix raisonnés, pas des normes de l'entreprise. Ils seraient à valider avec le métier.
- Les contrôles portent sur les colonnes utiles à Q3. Les autres colonnes de `store_sales` (`ss_customer_sk`, `ss_item_sk`…) ne sont pas contrôlées en intégrité référentielle, car les tables `customer` et `item` n'ont pas été chargées.
- Les contrôles sont exécutés **après coup** par un script séparé : ils ne bloquent pas l'écriture. En production, ils seraient intégrés au pipeline et bloqueraient la publication du Gold en cas d'anomalie.

**Corrections éventuellement nécessaires :** aucune pour Q3. Pour un usage futur de la date de fermeture des magasins, il faudrait obtenir une source fiable.
