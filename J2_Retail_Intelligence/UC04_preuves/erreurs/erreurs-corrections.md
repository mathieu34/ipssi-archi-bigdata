# Erreurs rencontrées et corrections — Jour 2

Tableau des erreurs et des corrections (livrable obligatoire n° 10 ; TP Jour 2, §12.6 et §18). Environnement : Ubuntu 24.04.3 LTS
sous WSL2 (Windows 11), Hadoop 3.5.0 (Java 17), NiFi 2.12.0 (Java 21), mode pseudo-distribué mono-nœud.

| # | Date | Composant | Symptôme | Cause identifiée | Correction appliquée | Vérification | Preuve |
|---|---|---|---|---|---|---|---|
| E1 | 2026-11-17 14:55 | HDFS (NameNode) | NameNode absent de `jps` ; `hdfs dfsadmin -report` : « RPC response has invalid length of -16777216 » | Journal du NameNode : `BindException: Address already in use` sur `localhost:9000`. `ss -ltnp` : port 9000 tenu par un noyau Jupyter lancé par VS Code | Arrêt du noyau Jupyter, puis `hdfs --daemon start namenode` (sans reformatage) | `jps` : NameNode, DataNode, SecondaryNameNode ; rapport : `Live datanodes (1)` | `UC03_preuves/environnement/erreur_port_9000_namenode.txt` |
| E2 | 2026-11-17 | NiFi (PutHDFS) | Processeur PutHDFS introuvable dans « Add Processor » | Depuis NiFi 2.0, les processeurs Hadoop ne sont plus inclus dans la distribution standard `nifi-2.12.0-bin.zip` | Téléchargement de `nifi-hadoop-nar-2.12.0.nar` et `nifi-hadoop-libraries-nar-2.12.0.nar` depuis Maven Central dans `/opt/nifi/lib`, puis redémarrage de NiFi | Fichiers présents ; SHA-1 identiques à ceux publiés par Maven Central | `UC04_preuves/erreurs/nifi_modules_hadoop.txt` |
| D2 | 2026-11-17 16:10 | Commandes de preuve (shell) | `hdfs: command not found` lors de l'exécution des commandes de preuve UC-03 | Shell non interactif : les variables Hadoop (`PATH`) sont déclarées dans `~/.bashrc`, qui n'est pas chargé | Export explicite de `HADOOP_HOME`, `JAVA_HOME` et `PATH` avant les commandes ; preuve régénérée | `hdfs/01_decouverte_hdfs.txt` complet | `UC03_preuves/hdfs/01_decouverte_hdfs.txt` |
| D3 | 2026-11-17 16:11 | HDFS (`hdfs dfs -stat`) | Accents remplacés par `??` dans la sortie de `-stat` | Le format est affiché par Java, dont l'encodage n'est pas UTF-8 | Libellés du format en ASCII ; commande relancée et sa ligne remplacée dans la preuve | Sortie lisible | `UC03_preuves/hdfs/05_verification.txt` |
| E3 | 2026-11-17 15:20 | NiFi (interface web) | `nifi.sh status` : UP, mais Chrome (Windows) → `https://localhost:8443/nifi` : ERR_CONNECTION_REFUSED | NiFi écoutait sur `[::ffff:127.0.0.1]:8443` (socket IPv6), non relayé par WSL2 vers Windows ; les services en IPv4 (interface HDFS 9870) étaient accessibles | Ajout de `java.arg.preferIPv4=-Djava.net.preferIPv4Stack=true` dans `/opt/nifi/conf/bootstrap.conf` (original sauvegardé en `bootstrap.conf.orig`), puis redémarrage. NiFi reste limité à localhost | `ss -ltn` : `127.0.0.1:8443` ; `Test-NetConnection localhost -Port 8443` depuis Windows : `True` | `UC04_preuves/erreurs/erreur_acces_interface_nifi.txt` |

## Tests d'erreur contrôlés (TP Jour 2, étape 10)

Erreurs **provoquées volontairement** après la réussite du transfert, pour vérifier que le flux les rend
identifiables. Elles ne sont pas des incidents.

| # | Date | Erreur provoquée | Comportement observé | Diagnostic | Correction / issue | Preuve |
|---|---|---|---|---|---|---|
| TA | 2026-11-18 | GetFile : Input Directory = `/data/nifi/input_inexistant` (processeur arrêté) | GetFile devient invalide (⚠️) et ne peut pas être démarré : « 'Input Directory' validated against '/data/nifi/input_inexistant' is invalid because Directory does not exist » | Erreur de **configuration**, détectée par NiFi avant toute exécution | Valeur rétablie à `/data/nifi/input` : processeur de nouveau valide (Stopped) | `testA_dossier_inexistant.png`, `testA_corrige.png` |
| TB | 2026-11-18 09:25 | Nouvel envoi de `store.dat`, déjà présent dans `/retail-lake/raw/nifi` (LogAttribute arrêté pour garder le FlowFile visible) | Bulletin WARNING sur PutHDFS : « penalizing … and routing to failure because file with same name already exists » ; file `failure` : 1 FlowFile (3 386 octets) ; rien écrit dans HDFS | **Doublon** bloqué par `Conflict Resolution Strategy = fail` : erreur d'exécution identifiable, sans perte (FlowFile conservé avec son contenu, UUID `50fa9dd0-…`) | LogAttribute redémarré : attributs du FlowFile écrits dans le journal. HDFS : un seul `store.dat`, date (17/11 17:54) et SHA-256 inchangés | `testB_doublon_failure.png`, `testB_flowfile_details.png`, `03_test_erreur.txt` |

## Mesure préventive

| Date | Composant | Constat | Mesure | Vérification |
|---|---|---|---|---|
| 2026-11-17 | WSL2 (mémoire) | 7,5 Go alloués à WSL, sous les 8 Go minimum recommandés (TP Jour 1, §3.2) pour faire tourner HDFS et NiFi ensemble | Fichier `C:\Users\<utilisateur>\.wslconfig` : `memory=10GB`, `swap=4GB`, puis `wsl --shutdown` | `free -h` : 9,7 Gi de mémoire, 4 Gi de swap |

## Enseignements

- Démarrer HDFS **avant** d'ouvrir un notebook dans VS Code, pour éviter qu'un noyau Jupyter prenne le port 9000.
- Ne jamais relancer `hdfs namenode -format` pour corriger un problème de démarrage : E1 a été résolu sans reformatage.
- Avec NiFi 2.x, prévoir l'ajout des modules Hadoop avant de construire un flux vers HDFS.
- Sous WSL2, vérifier qu'un service est joignable **depuis Windows** (`Test-NetConnection`), et pas seulement depuis Linux.
- `Conflict Resolution Strategy = fail` empêche un second dépôt d'écraser le premier : le doublon est isolé dans
  `failure` au lieu d'être écrit (`replace`) ou perdu sans trace (`ignore`).
