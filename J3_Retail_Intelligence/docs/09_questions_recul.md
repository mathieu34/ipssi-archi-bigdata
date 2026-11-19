# Questions de recul – TP Jour 3 (§11)

Les réponses s'appuient sur ce qui a été réellement observé et fait dans ce TP.

**1. Pourquoi est-il nécessaire de vérifier les schémas avant de commencer les transformations ?**
Parce qu'un traitement repose sur des hypothèses implicites : noms, types, séparateur, présence d'un en-tête. Ici, les fichiers `.dat` n'ont **pas d'en-tête**. Sans vérification, Spark aurait nommé les colonnes `_c0` à `_c22`, et une erreur d'ordre aurait mis les quantités à la place des montants. L'inférence de types a aussi donné `string` pour `s_rec_end_date`, simplement parce que la colonne est vide. Vérifier le schéma, puis l'imposer explicitement (règle R2), garantit que chaque calcul porte sur la bonne colonne et le bon type.

**2. Quelle différence existe entre une donnée brute, une donnée Silver et une donnée Gold ?**
- La donnée **brute (Bronze)** est le fichier tel qu'il a été reçu (`store_sales.dat` : texte sans en-tête, deux lots séparés). On ne la modifie jamais.
- La donnée **Silver** est la même information, mais **fiabilisée** : colonnes nommées, types exacts, lots réunis avec leur provenance, règles de qualité appliquées. La granularité est inchangée (674 211 lignes de vente).
- La donnée **Gold** est **agrégée pour répondre à une question métier** : 60 lignes « magasin × année » avec le CA net, les transactions, le panier moyen et le rang, prêtes pour l'analyse.

**3. Pourquoi faut-il connaître la granularité d'une table avant de réaliser une agrégation ?**
Parce que le sens d'un comptage en dépend. Une ligne de `store_sales` est une **ligne d'article**, pas un ticket : un ticket compte 7,5 lignes en moyenne. Compter les lignes aurait donné 674 211 « transactions » au lieu de 90 000, et un panier moyen 7,5 fois trop petit. Il a fallu compter les **tickets distincts**, après avoir vérifié qu'un ticket appartient à un seul magasin et à un seul jour.

**4. Quels risques présente une jointure réalisée sur une clé supposée ?**
Si la clé n'est pas unique côté référentiel, la jointure **duplique** des lignes et gonfle les totaux. Si des valeurs n'existent pas de l'autre côté, une jointure interne **perd** des lignes en silence. Si les colonnes ne désignent pas le même concept, la jointure produit des associations **fausses**. Ici, chaque clé a été vérifiée avant de joindre (unicité de `s_store_sk` et de `d_date_sk`, 0 orphelin). Chaque jointure a aussi été encadrée par un comptage avant et après : 674 211 → 674 211.

**5. Pourquoi ne faut-il pas supprimer automatiquement les valeurs atypiques ?**
Parce qu'une valeur surprenante peut être un **cas métier réel**. Ici, 3 995 ventes ont un montant net de 0 : ce sont des articles gratuits ou couverts par un coupon. 74 % des lignes ont une marge négative : ce sont des ventes à perte. 4 082 couples (ticket, produit) sont répétés : ce sont des promotions différentes. Les supprimer aurait faussé le CA ou le nombre d'articles vendus. Une valeur n'est écartée que si elle est **impossible** au regard de sa définition (quantité ≤ 0, montant incohérent), et toujours dans un jeu de rejets, avec un motif.

**6. Quels contrôles permettent de vérifier la cohérence d'un jeu de données transformé ?**
- La **réconciliation des totaux** avec la source : CA du Gold = CA du Silver = 1 162 073 847,88 ; tickets : 90 000 = 90 000.
- La **conservation des volumes** : lignes Silver + rejets = lignes des fichiers sources.
- L'**unicité de la granularité** : 60 couples (année, magasin) pour 60 lignes.
- Les **règles de calcul** : panier = CA / transactions.
- L'**intégrité référentielle** : 0 orphelin.
- Les **domaines de valeurs** : quantités de 1 à 100, période 2001-2005.

Ces 32 contrôles sont dans `docs/08_rapport_qualite.md`.

**7. Pourquoi Parquet est-il adapté aux usages analytiques ?**
Parce qu'il stocke les données **par colonne** : une requête qui ne lit que `ss_net_paid` ne lit que cette colonne. Il **compresse** bien (40 Mo contre 92 Mo en CSV et 353 Mo en JSON pour les mêmes ventes). Il **conserve les types** (`decimal(7,2)`, `date`), ce qui rend les sommes exactes au centime et évite de redonner un schéma à chaque lecture.

**8. Pourquoi Parquet seul ne fournit-il pas les garanties d'une table transactionnelle Lakehouse ?**
Parce que c'est un format de **fichier**, pas de **table**. Un répertoire Parquet n'a pas de journal de transactions. Une écriture interrompue peut le laisser incomplet (le marqueur `_SUCCESS` permet seulement de le détecter). Un lecteur peut voir une écriture en cours. Il n'y a ni historique de versions, ni `UPDATE`, `DELETE` ou `MERGE` ligne à ligne, ni contrôle de l'évolution du schéma. Ces garanties ACID viennent de formats de table comme Delta Lake, Iceberg ou Hudi, qui ajoutent un journal au-dessus des fichiers Parquet.

**9. Dans quels cas une base NoSQL pourrait-elle compléter une architecture Data Lake ?**
Pour les **accès rapides à un enregistrement par sa clé**, que le Data Lake ne sait pas bien faire. Par exemple : afficher instantanément la fiche d'un produit, l'historique d'un client ou l'état du stock d'un article dans une application. Une base orientée colonnes comme HBase est adaptée à ces lectures et écritures unitaires à fort volume. Le Data Lake et Parquet restent adaptés aux **analyses de masse** (le CA de tous les magasins sur 5 ans). Les deux se complètent : le lac fournit l'historique analytique, la base NoSQL sert les accès opérationnels.

**10. Quelles limites des données TPCx-BB doivent être prises en compte lors de l'interprétation des résultats ?**
- Ce sont des données **synthétiques** : les 12 magasins ont des volumes presque identiques par construction, avec des écarts de CA de 5 à 14 %. Le classement de Q3 ne reflète aucune réalité commerciale.
- Certaines valeurs ne sont pas réalistes : panier moyen d'environ 13 000, 74 % de ventes à perte, surfaces de plusieurs millions sans unité, dates de fermeture de 1917 à 2141.
- Ce n'est pas un benchmark : aucun temps mesuré ici n'a de valeur de performance au sens TPC.
- Le périmètre est **partiel** : les retours ne sont pas déduits, et seules 3 tables sur plus de 20 sont utilisées.
