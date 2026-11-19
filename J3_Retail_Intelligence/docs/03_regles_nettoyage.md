# Règles de nettoyage – TP Jour 3 (UC-06, étape 4)

**Périmètre :** les sources `store_sales` (lots `data` et `data_refresh`) et `store`, retenues pour la question Q3 du J1, « Quel magasin vend le plus ? », ainsi que la source d'enrichissement `date_dim` (calendrier, pour l'année).

**Origine des anomalies :** inventaire (`docs/02_inventaire_sources.md`) et exploration (`notebooks/exploration.ipynb`, §4.6).

**Mise en œuvre :** `scripts/nettoyage.py`. Chaque règle porte un numéro (R1, R2…) repris dans les commentaires du script, et le script affiche le nombre de lignes concernées par chaque règle.

## Principes appliqués

- **Les fichiers sources ne sont jamais modifiés.** Le nettoyage produit de nouveaux jeux de données.
- **Aucune suppression silencieuse.** Une ligne écartée n'est pas effacée : elle va dans un **jeu de rejets**, avec le motif du rejet, et son nombre est affiché (§1.10.7 et §4.7.2 du sujet).
- **Une valeur surprenante n'est pas forcément une erreur.** Les montants à 0 et les marges négatives sont conservés quand ils s'expliquent par le métier (§4.7.2, encadré « Point de vigilance »).
- **Les règles sans effet aujourd'hui sont gardées.** Elles protègent les prochains chargements, par exemple un nouveau lot `data_refresh`.

## 1. Règles générales (les deux sources)

| N° | Anomalie | Règle | Action appliquée | Justification |
|---|---|---|---|---|
| R1 | **Pas de ligne d'en-tête** : Spark nomme les colonnes `_c0`, `_c1`… | Nommer les colonnes selon la spécification TPCx-BB (`COLUMNS` de `sources/schema.py`, à la racine du dépôt) | Colonnes renommées à la lecture | Sans noms explicites, les traitements seraient illisibles et fragiles |
| R2 | **Type incorrect** : les types inférés (`inferSchema`) ne sont qu'une proposition, et `s_rec_end_date` est inférée en `string` faute de valeur | Imposer un **schéma explicite** à la lecture : identifiants et quantités en `integer`, montants en `decimal(7,2)`, dates en `date`, libellés en `string` | Lecture avec un `StructType` défini dans le script, sans `inferSchema` | L'inférence ne vaut pas validation (§4.6.2). `decimal` évite les erreurs d'arrondi des `double` sur les montants, et le schéma devient identique à chaque exécution |
| R3 | **Échec de conversion** : une valeur non convertible devient `null` en silence (§4.7.3) | Comparer le nombre de valeurs nulles avant et après le typage, colonne par colonne | Contrôle affiché. Si une conversion crée des nulls, les lignes concernées vont dans les rejets | Vérifier que le typage n'a pas fait disparaître d'information |

## 2. Règles `store_sales` (ventes)

| N° | Anomalie | Règle | Action appliquée | Justification |
|---|---|---|---|---|
| R4 | **Ventes réparties sur deux fichiers** (`data` : 667 579 lignes, `data_refresh` : 6 632 lignes) | Réunir les deux lots et ajouter une colonne `lot_source` (`data` ou `data_refresh`) | Union des deux lots, plus une colonne de provenance | `data_refresh` contient les ventes du 13/12 au 31/12/2005 : sans lui, 2005 est incomplète. Aucun ticket commun entre les deux lots, donc pas de doublon. La colonne garde la provenance (§3.3, §4.9.2) |
| R5 | **Valeur manquante sur un champ obligatoire** : magasin, ticket, produit, date, quantité ou montant net | Ces 6 champs (`ss_store_sk`, `ss_ticket_number`, `ss_item_sk`, `ss_sold_date_sk`, `ss_quantity`, `ss_net_paid`) doivent être renseignés | Une ligne où l'un d'eux manque va dans les rejets, avec le motif `champ_obligatoire_nul` | Sans magasin, date ou montant, une vente ne peut pas être prise en compte dans Q3. Constat de l'étape 3 : **0 ligne concernée** |
| R6 | **Valeur manquante sur un lien facultatif** : `ss_cdemo_sk` (250), `ss_hdemo_sk` (308), `ss_addr_sk` (462), `ss_promo_sk` (159) | Laisser la valeur nulle | **Conservée telle quelle** | Une vente sans profil client renseigné ou sans promotion reste une vente valide. Ces colonnes ne servent pas à Q3. Remplacer les nulls par une valeur inventée fausserait les données |
| R7 | **Doublon strict** : une ligne identique sur les 23 colonnes | Ne garder qu'un exemplaire | Lignes en trop retirées avec `dropDuplicates()` et comptées | Une ligne copiée deux fois compterait deux fois dans le CA. Constat de l'étape 3 : **0 doublon strict** |
| R8 | **Couple (ticket, produit) répété** : 4 082 couples | Ce n'est **pas** un doublon : les lignes diffèrent par la quantité, le prix et la promotion (exemple : ticket 44, produit 10003) | **Conservées** | Ce sont des lignes de ticket distinctes, par exemple un même article acheté sous deux promotions. Les supprimer ferait perdre du CA réel. Ce choix confirme celui du J1 |
| R9 | **Identifiant invalide** : un `ss_store_sk` absent de `store` (vente rattachée à un magasin inconnu) | Tout `ss_store_sk` doit exister dans `store.s_store_sk` | Une ligne orpheline va dans les rejets, avec le motif `magasin_inconnu` | Une vente sans magasin connu ne peut pas être classée dans Q3. Constat de l'étape 3 : les 12 valeurs (0 à 11) existent toutes, donc **0 ligne attendue** |
| R10 | **Date incohérente** : une vente hors de la période des données | `ss_sold_date_sk` doit être compris entre 36890 (01/01/2001) et 38715 (31/12/2005) | Une ligne hors période va dans les rejets, avec le motif `date_hors_periode` | Une vente datée hors de la période chargée serait le signe d'une erreur de saisie ou de lot. Constat de l'étape 2 : les valeurs vont de 36890 à 38715, donc **0 ligne attendue**. La conversion en vraie date se fera à l'étape 5, par jointure avec `date_dim` (§4.8) |
| R11 | **Valeur atypique** : quantité ≤ 0 ou montant net négatif | `ss_quantity` ≥ 1 et `ss_net_paid` ≥ 0 | Une ligne en écart va dans les rejets, avec le motif `valeur_hors_domaine` | Une quantité nulle ou négative n'a pas de sens pour une vente (les retours sont dans une autre table, `store_returns`). Constat de l'étape 3 : quantités de 1 à 100 et montants de 0 à 18 745, donc **0 ligne attendue** |
| R12 | **Valeur atypique** : `ss_net_paid = 0` (3 995 lignes) | Explication métier vérifiée : 3 361 articles à prix 0 (gratuits) et 634 lignes avec un coupon qui couvre tout le prix | **Conservées** | Ce sont des cas métier réels. Ils ne modifient pas le CA et comptent bien comme des articles vendus |
| R13 | **Valeur atypique** : marge négative (`ss_net_profit < 0`, 74 % des lignes) | Vente à perte : possible (promotion, déstockage) | **Conservées**, sans correction | Q3 porte sur le CA et non sur la marge. La proportion élevée est un effet probable de la génération synthétique, signalé comme limite |
| R14 | **Incohérence de calcul** : `ss_net_paid ≠ ss_ext_sales_price − ss_coupon_amt` | La règle de calcul TPC-DS doit être respectée, à 0,01 près | Une ligne incohérente va dans les rejets, avec le motif `montant_incoherent` | Elle garantit que `ss_net_paid` est un CA net fiable. Constat de l'étape 3 : **0 écart** |

## 3. Règles `store` (magasins)

| N° | Anomalie | Règle | Action appliquée | Justification |
|---|---|---|---|---|
| R15 | **Format de texte** : espaces parasites possibles dans les libellés | Supprimer les espaces de début et de fin (`trim`) des colonnes texte | Libellés harmonisés | Évite que « Forest » et « Forest␣ » soient vus comme deux magasins différents lors d'un regroupement (exemple du §4.7.3) |
| R16 | **Valeur manquante** : `s_rec_end_date` vide sur les 12 magasins | Une date de fin vide signifie « version toujours valide » | **Conservée nulle**, mais typée en `date` (R2) | C'est la convention des tables à historique : il y a une seule version par magasin, toujours active. Il ne faut pas inventer de date |
| R17 | **Identifiant** : `s_store_sk` doit être unique | Unicité de `s_store_sk` (clé de jointure de Q3) | Contrôle bloquant : si un doublon apparaît, le script s'arrête avec un message | Une clé en double dupliquerait les ventes lors de la jointure. Constat de l'étape 2 : 12 valeurs distinctes sur 12 |
| R18 | **Date incohérente** : `s_closed_date_sk` va de 1917 à 2141, et des magasins « fermés » avant 2001 vendent entre 2001 et 2005 | Colonne jugée **non fiable** | **Conservée telle quelle, mais jamais utilisée pour filtrer** des magasins ou des ventes | La corriger demanderait une information qu'on n'a pas. L'utiliser exclurait à tort des magasins actifs. Déjà relevé au J1 |
| R19 | **Valeur atypique** : `s_floor_space` entre 5,7 et 8,9 millions, unité inconnue | Colonne jugée **non interprétable** comme une surface en m² | **Conservée**, sans calcul de CA par surface | Diviser le CA par une surface d'unité inconnue produirait un indicateur faux. Signalé comme limite de Q3 |

## 3 bis. Règles `date_dim` (source d'enrichissement)

| N° | Anomalie | Règle | Action appliquée | Justification |
|---|---|---|---|---|
| R20 | **Table trop large pour le besoin** : 28 colonnes, dont 4 seulement sont utiles à Q3 | Ne garder que `d_date_sk`, `d_date`, `d_year` et `d_moy`, avec un schéma explicite (R2) | Sélection des 4 colonnes | Alléger la jointure et éviter d'importer dans les ventes des colonnes non contrôlées |
| R21 | **Identifiant** : `d_date_sk` doit être unique | Unicité de `d_date_sk` | Contrôle bloquant, comme R17 : le script s'arrête si la clé est en double | Une clé en double dupliquerait des ventes lors de la jointure et gonflerait le CA. Constat : 109 573 valeurs distinctes sur 109 573 lignes |
| R22 | **Jour de vente absent du calendrier** : une vente dont le `ss_sold_date_sk` n'existe pas dans `date_dim` perdrait son année | Tout `ss_sold_date_sk` doit exister dans `date_dim` | Une vente orpheline va dans les rejets, avec le motif `date_inconnue`, même principe que R9 | Une vente sans année ne peut pas entrer dans le CA annuel de Q3. Constat : 1 826 jours de vente, **0 orphelin** |

## 4. Ordre d'application

1. **Lecture** avec noms de colonnes et schéma explicites (R1, R2), puis contrôle des conversions (R3).
2. **`store`** : `trim` (R15), contrôle d'unicité de la clé (R17).
3. **`date_dim`** : sélection des colonnes utiles (R20), contrôle d'unicité de la clé (R21).
4. **`store_sales`** : union des lots avec provenance (R4), puis suppression des doublons stricts (R7).
5. **Validation des ventes** (R5, R9, R10, R11, R14, R22) : chaque ligne reçoit un **motif de rejet** ou rien. Les lignes sans motif forment le jeu nettoyé, les autres le jeu de rejets.
6. **Bilan** : nombre de lignes à chaque étape, puis par motif de rejet.

Les règles R6, R8, R12, R13, R16, R18 et R19 sont des **décisions de conservation** : elles ne transforment pas les données, mais elles sont documentées pour justifier pourquoi rien n'est fait.

Le jeu nettoyé et le jeu de rejets seront écrits dans la zone Silver à l'étape 6 (§4.9).

## 5. Résultats mesurés

Sortie complète : `preuves/transformations/nettoyage_sortie.txt`.

| Étape | Résultat |
|---|---|
| R3 – conversions échouées (`store`, `date_dim` et `store_sales`) | **0** |
| R17 – unicité de `s_store_sk` | 12 lignes, 12 clés distinctes : OK |
| R20, R21 – `date_dim` réduit à 4 colonnes, unicité de `d_date_sk` | 109 573 lignes, 109 573 clés distinctes : OK |
| R4 – union des lots | 667 579 (`data`) + 6 632 (`data_refresh`) = **674 211** lignes |
| R7 – doublons stricts retirés | **0** |
| R5, R9, R10, R11, R14, R22 – lignes rejetées | **0** |
| **Bilan** | `store` : **12** magasins conservés ; `date_dim` : **109 573** jours (4 colonnes) ; `store_sales` : **674 211** lignes conservées, **0** rejet |
| Schéma obtenu | Identifiants et quantités en `integer`, montants en `decimal(7,2)`, `s_rec_start_date`, `s_rec_end_date` et `d_date` en `date`, plus la colonne `lot_source` |

**Interprétation :** les sources sont de bonne qualité sur le périmètre de Q3, ce qui est cohérent avec les constats de l'exploration. Le nettoyage consiste surtout à **fiabiliser la structure** (noms, types exacts, provenance) et à **documenter les décisions de conservation** (R6, R8, R12, R13, R16, R18, R19). Il n'y a pas de lignes à exclure.

### Vérification que les règles fonctionnent

Un résultat de « 0 rejet » ne prouve rien si les règles ne se déclenchent jamais. Le script a donc été exécuté sur un **jeu de test construit à la main** : 3 lignes réelles, plus 8 lignes contenant chacune une erreur volontaire, et un calendrier auquel il manque un jour. Résultat : 3 lignes conservées, 1 doublon retiré, et 7 lignes rejetées avec le bon motif.

| Erreur injectée | Motif obtenu |
|---|---|
| Copie exacte d'une ligne | retirée par R7 (doublon strict) |
| `ss_store_sk` = 99 | `magasin_inconnu` (R9) |
| `ss_sold_date_sk` = 30000 | `date_hors_periode` (R10) |
| `ss_quantity` = 0 | `valeur_hors_domaine` (R11) |
| `ss_net_paid` faux | `montant_incoherent` (R14) |
| `ss_store_sk` vide | `champ_obligatoire_nul` (R5) |
| `ss_quantity` = `abc` | `conversion_echouee` et `champ_obligatoire_nul` (R3 puis R5) |
| Vente datée d'un jour retiré du calendrier de test | `date_inconnue` (R22) |

**Problème trouvé et corrigé grâce à ce test :** Spark 4 active par défaut le mode ANSI. Dans ce mode, `cast` **fait planter** le traitement sur une valeur non convertible au lieu de renvoyer `null`. Le script utilise donc `try_cast`, qui renvoie `null` et permet de diriger la ligne vers les rejets (R3).
