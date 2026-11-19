# Transformations – TP Jour 3 (UC-06, étape 5)

**Objectif :** préparer la réponse à la question Q3 du J1, « Quel magasin vend le plus ? ». La question décisionnelle est : classer les 12 magasins selon le CA net, **par année**, avec le nombre de transactions et le panier moyen.

**Traitement :** `scripts/transformations.py`. Il lit la **zone Silver**, c'est-à-dire les données nettoyées et écrites par `scripts/nettoyage.py` (règles R1 à R22, `docs/03_regles_nettoyage.md` et `docs/05_silver.md`).

**Sortie d'exécution :** `preuves/transformations/transformations_sortie.txt`.

## 1. Enchaînement

```
store_sales nettoyées (674 211 lignes, lots data + data_refresh)
   │
   ├─ Jointure 1 : + store     (ss_store_sk = s_store_sk)       → nom, ville, État du magasin
   ├─ Jointure 2 : + date_dim  (ss_sold_date_sk = d_date_sk)    → date réelle, année, mois
   │
   └─ Agrégation par magasin × année → CA net, transactions, panier moyen, rang
```

Les deux jointures sont des **jointures gauches**, encadrées par trois contrôles : le nombre de lignes avant, le nombre de lignes après, et le nombre de lignes non rapprochées. Le script s'arrête si le nombre de lignes change, car ce serait le signe d'une clé en double côté droit (§4.8.4).

## 2. Jointure 1 – ventes × magasins

| Élément (§4.8.3) | Valeur |
|---|---|
| **Sources** | `store_sales` (nettoyée) et `store` (nettoyée) |
| **Colonnes utilisées** | `store_sales.ss_store_sk` = `store.s_store_sk` |
| **Colonnes ajoutées** | `s_store_id`, `s_store_name`, `s_city`, `s_state` |
| **Nature de la relation** | Chaque vente est réalisée dans un magasin ; un magasin réalise de nombreuses ventes |
| **Cardinalité attendue** | **N:1**. Côté `store`, `s_store_sk` est unique (12/12, règle R17) |
| **Justification de la clé** | Même nom de concept dans la spécification TPCx-BB (clé étrangère `ss_store_sk` vers `s_store_sk`), mêmes valeurs (0 à 11 des deux côtés, étape 3), relation déjà vérifiée au J1 (0 orphelin). La relation ne repose donc pas sur la seule ressemblance des noms (§3.2) |
| **Lignes avant** | 674 211 |
| **Lignes après** | **674 211** (aucune ligne perdue ni dupliquée) |
| **Non rapprochées** | **0** |

## 3. Jointure 2 – ventes × calendrier

| Élément (§4.8.3) | Valeur |
|---|---|
| **Sources** | `store_sales` (enrichie par la jointure 1) et `date_dim` (nettoyée, 4 colonnes) |
| **Colonnes utilisées** | `store_sales.ss_sold_date_sk` = `date_dim.d_date_sk` |
| **Colonnes ajoutées** | `d_date`, `d_year`, `d_moy` |
| **Nature de la relation** | Chaque vente a lieu un jour donné ; un jour compte de nombreuses ventes |
| **Cardinalité attendue** | **N:1**. Côté `date_dim`, `d_date_sk` est unique (109 573/109 573, règle R21) |
| **Justification de la clé** | Clé étrangère de la spécification TPCx-BB. Les 1 826 jours de vente existent tous dans `date_dim` (exploration et règle R22). Relation déjà vérifiée au J1 (fiche Q4) |
| **Lignes avant** | 674 211 |
| **Lignes après** | **674 211** |
| **Non rapprochées** | **0** |

## 4. Contrôle préalable à l'agrégation : un ticket = un magasin et un jour

Le nombre de transactions se calcule en comptant les **tickets distincts** par magasin et par année. Ce calcul n'est juste que si un ticket appartient à **un seul magasin et un seul jour**. Sinon, le même ticket serait compté dans plusieurs groupes.

**Contrôle :** tickets rattachés à plusieurs magasins ou à plusieurs jours : **0**. Le comptage est donc fiable. Au total, la somme des transactions des 12 magasins sur 5 ans donne **90 000 tickets**, et chacun n'est compté qu'une fois.

## 5. Agrégation Q3 (§4.8.5)

| Élément | Définition |
|---|---|
| **Question métier** | J1, Q3 : « Quel magasin vend le plus ? » |
| **Granularité du résultat** | Une ligne = **un magasin × une année**, soit 12 × 5 = **60 lignes** (vérifié) |
| **Dimensions** | `annee` (`d_year`), magasin (`ss_store_sk`, `s_store_id`, `s_store_name`, `s_city`, `s_state`) |
| **`ca_net`** | `SUM(ss_net_paid)` : chiffre d'affaires net de coupons, hors taxes (choix fait au J1, KPI K01) |
| **`nb_transactions`** | `COUNT(DISTINCT ss_ticket_number)` : nombre de **tickets**, pas de lignes. Un ticket contient en moyenne 7,5 lignes d'articles : compter les lignes surestimerait les transactions et sous-estimerait le panier |
| **`panier_moyen`** | `ca_net / nb_transactions`, arrondi au centime |
| **`nb_lignes_vente`, `quantite_vendue`** | Indicateurs de contexte : nombre de lignes d'articles et quantité totale |
| **`rang_annee`** | Classement par `ca_net` décroissant **au sein de chaque année** (fonction de fenêtre `rank()`) |
| **Contrôle de cohérence** | La somme de `ca_net` sur les 60 lignes est égale à la somme de `ss_net_paid` sur les 674 211 ventes : **1 162 073 847,88**, avec un écart de **0,00** |

### Résultats

**Premier et dernier magasin, par année :**

| Année | 1er (CA net) | 12e (CA net) | Écart 1er / 12e |
|---|---|---|---|
| 2001 | Hillside (20 022 451) | Avalon (18 737 675) | 6,9 % |
| 2002 | Buffalo (20 039 676) | Williamstown (18 417 258) | 8,8 % |
| 2003 | Buffalo (20 387 490) | Bloomfield (18 600 271) | 9,6 % |
| 2004 | Buffalo (20 748 577) | Avalon (18 184 148) | 14,1 % |
| 2005 | Germantown (20 430 494) | Egypt (18 200 785) | 12,3 % |

**Sur les 5 ans cumulés**, c'est **Buffalo** (magasin 7, Lewisburg, KS) qui vend le plus : 99,9 M de CA net et 7 717 transactions. Il est 1er en 2002, 2003 et 2004. Le dernier est **Sherwood** (94,7 M). Le classement complet figure dans la sortie d'exécution.

**Réponse à Q3 :** Buffalo est le magasin qui vend le plus sur la période et la plupart des années. Mais **les écarts sont faibles** : 5,4 % entre le 1er et le dernier sur 5 ans, et le classement change d'une année à l'autre. Aucun magasin ne domine nettement.

### Limites d'interprétation

- **Données synthétiques (TPCx-BB)** : la répartition très homogène entre magasins (de 55 000 à 58 000 lignes chacun) est probablement un effet de la génération. Le classement ne doit pas être lu comme une réalité commerciale.
- **CA net de coupons, mais brut de retours** : les retours (`store_returns`) ne sont pas déduits, car ils sont hors du périmètre retenu au J1.
- **Pas de CA rapporté à la surface** : `s_floor_space` n'a pas d'unité fiable (règle R19). Le classement ne tient donc pas compte de la taille des magasins.
- **2005 complète uniquement grâce au lot `data_refresh`** (du 13/12 au 31/12/2005, règle R4).
- **Un panier moyen d'environ 13 000** paraît élevé pour un magasin réel : c'est encore un effet des données synthétiques (7,5 articles par ticket, environ 1 700 par ligne).

## 6. Suite

Le même script écrit l'agrégation Q3 dans la **zone Gold**, au format Parquet (`data/gold/q3_ca_magasin_annee`). Voir `docs/06_gold.md` (étape 7, §4.10).

Les ventes enrichies, c'est-à-dire avec le nom du magasin et l'année, restent un **intermédiaire en mémoire** : elles ne sont pas écrites. La zone Silver conserve les tables nettoyées **séparément**, et la jointure est refaite à chaque calcul Gold. Ce choix évite de dupliquer 40 Mo de ventes pour une jointure qui ne prend que quelques secondes.
