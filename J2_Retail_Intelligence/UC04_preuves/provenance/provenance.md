# Provenance du FlowFile déposé par le flux NiFi

Livrable obligatoire n° 11 (TP Jour 2, étape 11). Source : interface NiFi, menu **Data Provenance**, événement
SEND du premier dépôt réussi (17/11/2026), puis **Show lineage**. Captures : `evenement_send.png`,
`evenement_send_suite.png`, `lignee.png`.

## Identité du FlowFile

| Information | Valeur relevée |
|---|---|
| FlowFile UUID | `554f376f-d2be-4840-a0da-273d00cad998` |
| Nom du fichier | `store.dat` |
| Taille | 3,31 Ko (3 386 octets) |
| Flux | Process Group `UC04_ingestion_tpcxbb` : GetFile → PutHDFS |

## Événements observés (graphe de lignée)

| Ordre | Événement | Composant | Signification | Heure |
|---|---|---|---|---|
| 1 | `RECEIVE` | GetFile | Le fichier entre dans NiFi depuis `/data/nifi/input/store.dat` : création du FlowFile | ≈ 17:54:43,9 (déduite : heure du SEND moins la durée de lignée de 0,884 s) |
| 2 | `SEND` | PutHDFS (`ea5c6f48-01a1-1000-9420-951fd95eeaeb`) | Le contenu est envoyé vers HDFS. Transit URI : `hdfs://localhost:9000/retail-lake/raw/nifi/store.dat` ; durée de l'envoi : 0,763 s | 17:54:44,783 CET |
| 3 | `ATTRIBUTES_MODIFIED` | PutHDFS | PutHDFS ajoute au FlowFile des attributs décrivant le fichier écrit (emplacement HDFS) | Juste après le SEND |
| 4 | `DROP` | PutHDFS | Fin de vie du FlowFile : la relation `success` est en *auto-terminate* | Juste après |

Le FlowFile n'a ni parent ni enfant (`Parent FlowFiles (0)`, `Child FlowFiles (0)`) : il n'a été ni découpé ni
fusionné, son parcours est linéaire.

## Recoupements avec les autres preuves

| Information de provenance | Confirmée par |
|---|---|
| Écriture à 17:54:44 | `hdfs dfs -stat` : `modified=2026-11-17 17:54:44` (`execution/02_verification_hdfs.txt`) |
| Destination `/retail-lake/raw/nifi/store.dat` | `hdfs dfs -ls /retail-lake/raw/nifi` (même fichier) |
| Taille 3,31 Ko | 3 386 octets dans HDFS ; SHA-256 identique à l'original |
| Composant `ea5c6f48-…` = PutHDFS | Même identifiant dans le journal NiFi (démarrage de PutHDFS à 17:54:41) |
| Un FlowFile distinct par passage | Le doublon du test B a un autre UUID (`50fa9dd0-fdf4-4e55-bd05-c85e60b39f12`) et finit en `failure`, sans événement SEND |

## Ce que la provenance permet de reconstituer

À partir du seul nom `store.dat`, la provenance répond aux questions d'un audit :

- **d'où vient la donnée** : RECEIVE par GetFile, depuis le dossier `/data/nifi/input` ;
- **où elle est allée** : SEND vers `hdfs://localhost:9000/retail-lake/raw/nifi/store.dat` ;
- **quand** : 17/11/2026 à 17:54:44 ;
- **par quel composant** : PutHDFS, identifié par son UUID ;
- **ce qu'elle est devenue dans NiFi** : DROP après succès, donc aucun FlowFile oublié dans une file.

Combinée à l'empreinte SHA-256 relevée avant et après le dépôt, elle prouve que le fichier présent dans HDFS est
bien celui qui a été lu dans le dossier d'entrée, et qu'il n'a pas été modifié en chemin.

## Limite

Le dépôt de provenance de NiFi est conservé pour une durée et une taille limitées (paramètres
`nifi.provenance.repository.max.storage.time` et `max.storage.size` de `nifi.properties`, ici **30 jours** et **10 Go**). Pour une traçabilité
durable, ces informations doivent être recopiées dans un journal d'ingestion (zone `/retail-lake/logs`), ce qui
est prévu avec les colonnes techniques de provenance du Jour 3.
