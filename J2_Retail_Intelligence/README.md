# J2 — Retail Intelligence Platform

Remise du TP Jour 2 (IPSSI, Mastère Développement, Data & IA) : UC-03 (Hadoop, HDFS, Data Lake) et UC-04
(ingestion avec Apache NiFi). Organisation : option 1 (« plusieurs fichiers ») du document « Livrables attendus –
Jour 2 ». Environnement : Ubuntu 24.04.3 LTS sous WSL2, Hadoop 3.5.0 (Java 17), NiFi 2.12.0 (Java 21),
HDFS en mode pseudo-distribué mono-nœud.

## Arborescence

```
J2_Retail_Intelligence/
├── UC03_Hadoop_HDFS.pdf
├── UC03_preuves/
│   ├── environnement/    version Hadoop, état des services, erreurs de démarrage
│   ├── hdfs/             commandes HDFS, dépôt, contrôles (présence, taille, permissions, checksum)
│   └── data_lake/        arborescence /retail-lake, schéma, inventaire des fichiers TPCx-BB
├── UC04_ingestion_NiFi.pdf
├── UC04_preuves/
│   ├── configuration/    environnement NiFi, propriétés GetFile / PutHDFS, export du flux
│   ├── execution/        flux démarré, compteurs / files, fichier présent dans /retail-lake/raw/nifi
│   ├── erreurs/          test d'erreur contrôlé, tableau des erreurs et corrections
│   └── provenance/       événements de provenance du FlowFile
├── README_Jour2.pdf      README de reproduction (versions, démarrage, chemins HDFS, paramètres NiFi, arrêt)
├── Complementaire/       (facultatif, créé seulement si une activité CO-xx est réalisée)
└── Avance/               (facultatif, créé seulement si un défi AV-xx est réalisé)
```

## Correspondance avec les livrables obligatoires

| N° | Livrable obligatoire | Emplacement | État |
|---|---|---|---|
| 1 | Fiche d'environnement technique | `UC03_Hadoop_HDFS.pdf` ; `UC03_preuves/environnement/`, `UC04_preuves/configuration/environnement_nifi.txt` | Rédigé dans UC03_Hadoop_HDFS.pdf, en relecture |
| 2 | Fiche de découverte Hadoop et HDFS | `UC03_Hadoop_HDFS.pdf` | Rédigé dans UC03_Hadoop_HDFS.pdf, en relecture |
| 3 | Inventaire des fichiers TPCx-BB | `UC03_Hadoop_HDFS.pdf` ; `UC03_preuves/data_lake/inventaire_fichiers_tpcxbb.md` | Rédigé dans UC03_Hadoop_HDFS.pdf, en relecture |
| 4 | Arborescence du Data Lake | `UC03_Hadoop_HDFS.pdf` ; `UC03_preuves/data_lake/` | Rédigé dans UC03_Hadoop_HDFS.pdf, en relecture |
| 5 | Commandes et résultats HDFS | `UC03_preuves/hdfs/` | Rédigé dans UC03_Hadoop_HDFS.pdf, en relecture |
| 6 | Preuves du dépôt et des contrôles de stockage | `UC03_preuves/hdfs/` | Rédigé dans UC03_Hadoop_HDFS.pdf, en relecture |
| 7 | Schéma du flux NiFi | `UC04_ingestion_NiFi.pdf` | Rédigé dans UC04_ingestion_NiFi.pdf (schéma section 3), en relecture |
| 8 | Configuration NiFi | `UC04_preuves/configuration/` | Fait : export `configuration/flux_uc04.json` + captures GetFile / PutHDFS |
| 9 | Preuves d'exécution et de dépôt | `UC04_preuves/execution/` | Fait : `execution/flux_execute.png`, `execution/02_verification_hdfs.txt` |
| 10 | Tableau des erreurs et des corrections | `UC04_preuves/erreurs/erreurs-corrections.md` | Fait : E1 à E3, D2, D3, tests TA et TB (`erreurs/erreurs-corrections.md`) |
| 11 | Documentation de la provenance | `UC04_ingestion_NiFi.pdf` ; `UC04_preuves/provenance/` | Fait : `provenance/provenance.md` + 3 captures |
| 12 | Script de repli | Sans objet tant que NiFi fonctionne | Sans objet : NiFi a fonctionné |
| 13 | README de reproduction | `README_Jour2.pdf` | Rédigé dans README_Jour2.pdf, en relecture |
| — | Questions de recul (14) | `UC04_ingestion_NiFi.pdf` (partie finale) | Rédigé dans UC04_ingestion_NiFi.pdf (section 10), en relecture |

Le tableau des erreurs couvre les deux UC : E1 (port 9000 du NameNode) concerne UC-03, sa preuve est donc dans
`UC03_preuves/environnement/`.

Aucun identifiant NiFi (utilisateur ou mot de passe générés) n'est versionné.
