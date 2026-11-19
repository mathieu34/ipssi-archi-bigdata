# Format Parquet et comparaison des formats – TP Jour 3 (UC-06, étape 8)

## 1. Résultats écrits en Parquet, relus et vérifiés (§4.11.2)

Tous les jeux produits sont écrits en Parquet, puis **relus depuis le disque** pour être contrôlés :

| Jeu | Script | Contrôles après relecture | Preuve |
|---|---|---|---|
| `silver/store_sales`, `silver/store`, `silver/date_dim`, `silver/store_sales_rejets` | `nettoyage.py` | Lecture OK ; lignes relues = lignes écrites (674 211 / 12 / 109 573 / 0) ; schéma et types conservés | `preuves/silver_gold/silver_sortie.txt` |
| `gold/q3_ca_magasin_annee` | `transformations.py` | Lecture OK ; 60 lignes ; 60 couples (année, magasin) distincts ; CA total relu = CA total des ventes (1 162 073 847,88) | `preuves/silver_gold/gold_sortie.txt` |

Les points demandés par le sujet sont tous vérifiés : la lecture fonctionne, le schéma est conservé, le nombre de lignes est cohérent, les valeurs sont exploitables (sommes exactes au centime), et les répertoires de sortie sont identifiés (`data/silver/<jeu>`, `data/gold/<jeu>`).

L'écriture utilise le mode `overwrite`, **uniquement sur les répertoires de sortie dédiés au TP** (`data/silver`, `data/gold`). Ce mode n'est jamais appliqué aux sources (§4.11.2, encadré « Point de vigilance »).

## 2. Mesure comparative (§4.11.3)

**Méthode :** `scripts/comparaison_formats.py` écrit **le même jeu**, `silver/store_sales` (674 211 lignes, 24 colonnes, en 2 fichiers), dans les trois formats, puis relit chacun. Chaque lecture est chronométrée 3 fois, et la meilleure mesure est retenue. Les copies CSV et JSON sont écrites dans `data/test/formats/` (hors Git) et ne servent qu'à la mesure.

**Sortie :** `preuves/parquet/comparaison_formats_sortie.txt`.

| Mesure | Source `.dat` | CSV | JSON | **Parquet** |
|---|---|---|---|---|
| **Volume observé** | 89,4 Mo | 92,0 Mo | **353,0 Mo** | **40,1 Mo** |
| Volume par rapport au CSV | — | 1× | 3,8× | **0,44×** |
| Type relu de `ss_net_paid` | — | `string` | `double` | **`decimal(7,2)`** |
| Type relu de `ss_quantity` | — | `string` | `bigint` | **`int`** |
| Lecture complète (`count`) | — | 0,25 s | 0,75 s | **0,10 s** |
| Lecture d'une colonne (somme de `ss_net_paid`) | — | 0,36 s | 0,77 s | **0,13 s** |
| Somme de `ss_net_paid` relue | — | 1 162 073 847,88 | 1 162 073 847,88 | 1 162 073 847,88 |

**Contenu brut observé :**
- **CSV** : `36890,5087,3560,97616,…,2296.48,2457.23,696.26,data`. Une ligne de texte par vente, avec une ligne d'en-tête.
- **JSON** : `{"ss_sold_date_sk":36890,"ss_sold_time_sk":5087,"ss_item_sk":3560,…}`. Un objet par vente, avec **le nom de chaque colonne répété sur chaque ligne**.
- **Parquet** : fichier binaire, illisible dans un éditeur de texte.

## 3. Comparaison argumentée

| Critère | CSV | JSON | Parquet |
|---|---|---|---|
| **Organisation des données** | Texte, **par ligne** : une vente par ligne, valeurs séparées par un délimiteur | Texte, **par ligne** : un objet clé-valeur par vente ; supporte les structures imbriquées | Binaire, **par colonne** : les valeurs d'une même colonne sont stockées ensemble, en groupes de lignes, avec le schéma et des statistiques (min, max) dans le fichier |
| **Lisibilité** | Excellente : s'ouvre dans un éditeur ou un tableur | Bonne : lisible, mais verbeux | Nulle à l'œil nu : il faut un outil (Spark, pandas, DuckDB…) |
| **Gestion des types** | **Aucune** : tout est du texte. Il faut un schéma ou une inférence à chaque lecture (`string` relu ici) | **Partielle** : distingue nombres, textes et booléens, mais pas `decimal` ni `date`. Ici `ss_net_paid` est relu en `double`, avec un risque d'arrondi | **Complète** : le schéma est **inscrit dans le fichier**. On relit `decimal(7,2)`, `date` et `int` sans rien préciser |
| **Volume de stockage observé** | 92 Mo | 353 Mo, car les noms de colonnes sont répétés 674 211 fois | **40 Mo** : une colonne contient des valeurs semblables, donc elle se compresse bien |
| **Lecture sélective** | Non : pour lire une colonne, il faut lire toute la ligne | Non | **Oui** : Spark ne lit que les colonnes demandées et peut sauter des blocs grâce aux statistiques |
| **Usages adaptés** | Échanges simples, imports et exports vers des tableurs, petites données, sources brutes (nos `.dat`) | Données semi-structurées ou imbriquées, API, journaux d'événements | **Stockage analytique** : zones Silver et Gold, requêtes qui portent sur quelques colonnes de beaucoup de lignes |
| **Avantages** | Universel, simple, lisible | Flexible, auto-descriptif, gère l'imbrication | Compact, typé, rapide en lecture analytique |
| **Limites** | Pas de types, ambiguïtés sur le séparateur, les guillemets et l'encodage ; volumineux | Très volumineux, lent à lire, types approximatifs | Illisible sans outil ; peu adapté à la modification ligne par ligne ; **pas de transactions** (voir le §4) |

## 4. Ce que Parquet ne fournit pas

Parquet est un **format de fichier**, pas un **format de table transactionnel** (§4.11.3, encadré « Point de vigilance »). Un répertoire de fichiers Parquet ne garantit pas, à lui seul :
- l'**atomicité** des écritures. Si `overwrite` est interrompu, le répertoire peut rester à moitié écrit. Le marqueur `_SUCCESS` permet de le **détecter**, mais pas de revenir en arrière ;
- l'**isolation** : un lecteur qui lit pendant une écriture peut voir un état incomplet ;
- l'**historique des versions** (« voyage dans le temps ») et les mises à jour ou suppressions de lignes (`UPDATE`, `DELETE`, `MERGE`) ;
- le **contrôle de l'évolution du schéma** entre deux écritures.

Ces garanties sont apportées par des formats de table qui ajoutent un **journal de transactions** au-dessus des fichiers Parquet : Delta Lake, Apache Iceberg, Apache Hudi. Elles relèvent de la partie avancée facultative (§6). Les zones Silver et Gold de ce TP sont donc des **répertoires Parquet**, pas des tables ACID.

## 5. Limites de la mesure

- **Petit volume, une seule machine** : sur 674 211 lignes en mode local, les temps se comptent en dixièmes de seconde. L'ordre de grandeur est significatif, mais pas les valeurs exactes. Sur des milliards de lignes, l'écart entre la lecture en colonnes et la lecture en lignes serait bien plus marqué.
- **Lecture complète de Parquet** : le `count()` sur Parquet profite du nombre de lignes inscrit dans les métadonnées du fichier. Il n'a pas besoin de lire les données, ce qui explique en partie sa rapidité.
- **Cache du système** : les fichiers venaient d'être écrits et étaient probablement encore en mémoire. Les trois mesures retenues sont les meilleures sur 3 essais, pour limiter cet effet.
