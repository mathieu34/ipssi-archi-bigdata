# Zone Gold – TP Jour 3 (UC-06, étape 7)

**Rôle de la zone :** contenir des données **préparées pour répondre à une question métier**, sous forme d'indicateurs agrégés, prêtes pour l'analyse et la restitution du Jour 4 (§2.6.3, §4.10.1).

**Production :** `scripts/transformations.py`. Le script lit la zone Silver, fait les jointures et l'agrégation (`docs/04_transformations.md`), écrit le jeu Gold, puis le **relit pour le contrôler**.

**Sortie d'exécution :** `preuves/silver_gold/gold_sortie.txt`.

## 1. Chaîne de production

```
Sources TPCx-BB (.dat)          Silver (Parquet)                    Gold (Parquet)
─────────────────────          ────────────────                    ──────────────
store_sales  data + refresh ─┐
store                       ─┼─ nettoyage.py ─▶ silver/store_sales ─┐
date_dim                    ─┘   (R1 à R22)     silver/store        ─┼─ transformations.py ─▶ gold/q3_ca_magasin_annee
                                                silver/date_dim     ─┘   (2 jointures + agrégation)
```

Le Gold est calculé **uniquement à partir du Silver**, jamais directement depuis les sources. Le résultat est identique à celui calculé en mémoire à l'étape 5 (même CA total au centime et même classement), ce qui confirme que l'écriture et la relecture du Silver n'ont rien perdu.

## 2. Fiche du jeu Gold (§4.10.2)

| Élément | Description |
|---|---|
| **Nom** | `gold/q3_ca_magasin_annee` : synthèse des ventes par magasin et par année |
| **Finalité métier** | Répondre à **Q3 du J1** : « Quel magasin vend le plus ? ». Le jeu permet au responsable de magasin et à la direction d'**identifier le magasin modèle et d'accompagner les moins performants** (décision définie au J1) |
| **Sources** | `silver/store_sales` (ventes nettoyées, lots `data` et `data_refresh`), `silver/store` (noms et localisation), `silver/date_dim` (année) |
| **Granularité** | Une ligne = **un magasin × une année**. 12 magasins × 5 années (2001 à 2005) = **60 lignes** |
| **Dimensions** | `annee` ; magasin : `ss_store_sk`, `s_store_id`, `s_store_name`, `s_city`, `s_state` |
| **Mesures** | `ca_net`, `nb_transactions`, `panier_moyen`, `nb_lignes_vente`, `quantite_vendue` |
| **Indicateur de classement** | `rang_annee` |
| **Usage** | Analyse descriptive et restitution au Jour 4 : classement annuel, évolution d'un magasin dans le temps, comparaison entre magasins |
| **Format** | Parquet, 1 fichier (environ 7 Ko), trié par année puis par rang |

## 3. Colonnes et règles de calcul

| Colonne | Type | Règle de calcul |
|---|---|---|
| `annee` | integer | `date_dim.d_year` du jour de la vente (jointure `ss_sold_date_sk = d_date_sk`) |
| `rang_annee` | integer | Rang du magasin dans l'année, par `ca_net` décroissant : `rank() over (partition by annee order by ca_net desc)`. 1 = le magasin qui vend le plus. En cas d'égalité, deux magasins auraient le même rang |
| `ss_store_sk` | integer | Clé technique du magasin |
| `s_store_id`, `s_store_name`, `s_city`, `s_state` | string | Identifiant métier, nom et localisation du magasin (jointure avec `store`) |
| **`ca_net`** | decimal(17,2) | **`SUM(ss_net_paid)`** : chiffre d'affaires net de coupons, hors taxes (KPI K01 du J1) |
| **`nb_transactions`** | long | **`COUNT(DISTINCT ss_ticket_number)`** : nombre de tickets (passages en caisse), et non de lignes. Valable parce que chaque ticket appartient à un seul magasin et à un seul jour (contrôle de l'étape 5 : 0 exception) |
| **`panier_moyen`** | decimal(18,2) | **`ca_net / nb_transactions`**, arrondi au centime |
| `nb_lignes_vente` | long | `COUNT(*)` : nombre de lignes d'articles (indicateur de contexte) |
| `quantite_vendue` | long | `SUM(ss_quantity)` : nombre d'unités vendues (indicateur de contexte, KPI K06 du J1) |
| `_sources`, `_date_traitement` | string, timestamp | Provenance : jeux Silver utilisés, et date et heure du calcul |

Les montants restent en **`decimal`** de bout en bout. Les sommes sont exactes au centime, sans erreur d'arrondi, ce qui ne serait pas garanti avec des `double`.

## 4. Contrôles après écriture

| Contrôle | Résultat |
|---|---|
| Fichier présent et relisible en Parquet | OK |
| Nombre de lignes relues | **60** (attendu : 12 × 5) |
| Unicité de la granularité : couples (`annee`, `ss_store_sk`) distincts | **60**, aucun doublon |
| Cohérence avec le Silver : somme de `ca_net` = somme de `ss_net_paid` sur toutes les ventes | **1 162 073 847,88** des deux côtés |
| Schéma relu | Types conservés (`decimal`, `integer`, `long`, `string`, `timestamp`) |

Le script **s'arrête avec une erreur** si l'un de ces contrôles échoue.

## 5. Résultat

| Année | 1er | 2e | 3e | 12e |
|---|---|---|---|---|
| 2001 | Hillside | Bloomfield | Buffalo | Avalon |
| 2002 | Buffalo | Avalon | Bloomfield | Williamstown |
| 2003 | Buffalo | Forest | Williamstown | Bloomfield |
| 2004 | Buffalo | Williamstown | Pioneer | Avalon |
| 2005 | Germantown | Forest | Hillside | Egypt |

**Lecture :** **Buffalo** (Lewisburg, KS) est premier 3 années sur 5 (2002 à 2004), et premier sur la période cumulée. Ce cumul se calcule en additionnant les 5 lignes de chaque magasin dans ce jeu Gold.

En revanche, les écarts sont **faibles** : entre 6,9 % et 14,1 % d'écart entre le premier et le dernier selon l'année. Le classement est aussi **instable** : Buffalo passe 8e en 2005, Avalon est 2e en 2002 et dernier en 2001 et 2004.

## 6. Limites d'interprétation

- **Données synthétiques TPCx-BB** : les magasins ont des volumes très proches par construction. Les écarts de classement sont faibles et ne doivent pas être lus comme une performance commerciale réelle.
- **CA net de coupons, mais brut de retours** : `store_returns` n'est pas déduit, car hors du périmètre du J1. Un magasin qui a beaucoup de retours pourrait être surclassé.
- **Pas de rapport à la taille du magasin** : `s_floor_space` n'a pas d'unité fiable (R19), et le nombre d'employés n'a pas été vérifié. Un grand magasin vend mécaniquement plus.
- **2005 est complète uniquement grâce au lot `data_refresh`** (du 13/12 au 31/12/2005). Sans ce lot, le CA 2005 serait sous-estimé pour tous les magasins.
- **Le panier moyen est élevé** (environ 13 000) : 7,5 articles par ticket à environ 1 700 la ligne. C'est un trait des données synthétiques, pas une erreur de calcul.
- **Le jeu ne dit pas pourquoi** un magasin vend plus (emplacement, équipe, clientèle) : il ne fait que décrire.
