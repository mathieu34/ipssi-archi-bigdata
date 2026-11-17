# preuves (UC-01) — index des preuves

Preuves du dossier UC-01 (§5.1.16 du sujet). Chaque fichier est produit par une commande ou un script
rejouable ; les scripts sont dans `sources/` (à la racine du projet).

Données examinées : `~/tp_bigdata/extract/retail_project/` (archive `retail_project.zip`, dossiers `data/` et
`data_refresh/`). Jeu synthétique TPCx-BB.

**Point d'entrée : `index_preuves.pdf`** — pour chaque preuve, un titre, ce qu'elle démontre, son origine et un extrait lisible (généré par `index_preuves.py`).

## Preuves attendues par le sujet (§5.1.16)

| Preuve attendue | Fichier(s) | Produit par |
|---|---|---|
| Capture de l'arborescence des données | `arborescence.txt`, `contenu_archive.txt` | `profilage_sources.py`, `unzip -l` |
| Extrait d'inventaire des fichiers | `inventaire_fichiers.csv` (36 fichiers) | `profilage_sources.py` |
| Aperçu de fichiers représentatifs | `apercus/` (5 premières lignes brutes de chaque fichier) | `profilage_sources.py` |
| Tableau des colonnes et des types | `inventaire_colonnes.csv` (522 colonnes) | `profilage_sources.py` |
| Résultats de contrôles simples | `controles_kpi.txt`, `controles_relations.txt`, `relations.csv`, `controle_inventaire_complet.txt`, `controle_store_fermeture.txt`, `controle_date_dim.txt`, `controle_schema_vs_specification.txt`, `profilage_log.txt` | `controles_kpi.py`, `relations_qualite.py`, commandes ad hoc (en-tête de chaque fichier) |
| Schéma des besoins métier | `schema_fonctionnel.pdf` | `uc01_schema_fonctionnel.py` |
| Dictionnaire de KPI | `../dictionnaire_KPI.xlsx` | `uc01_dictionnaire_kpi.py` |

## Intégrité de l'archive

`checksum.txt` contient l'empreinte SHA-256 de `retail_project.zip`. La comparer avant toute nouvelle analyse :

```bash
sha256sum ~/tp_bigdata/raw/retail_project.zip
```

## Quel livrable s'appuie sur quelle preuve

| Livrable | Preuves |
|---|---|
| `cadrage_metier.pdf` | `contenu_archive.txt`, `checksum.txt` |
| `questions_decisionnelles.pdf` | `controles_kpi.txt`, `controles_relations.txt`, `schema_fonctionnel.pdf` |
| `dictionnaire_KPI.xlsx` | `controles_kpi.txt`, `controle_inventaire_complet.txt` |
| `inventaire_sources.xlsx` | `inventaire_fichiers.csv`, `inventaire_colonnes.csv`, `apercus/`, `arborescence.txt`, `controle_store_fermeture.txt` |
| `qualification_donnees.pdf` | `relations.csv`, `controles_relations.txt`, `controle_inventaire_complet.txt` |
| `limites_hypotheses.pdf` | toutes les preuves ci-dessus |

## Rejouer l'ensemble

Depuis la racine du projet (`~/projets/ipssi-archi-bigdata`) :

```bash
cd sources
../.venv/bin/python profilage_sources.py          # ~40 s : inventaire, colonnes, aperçus, arborescence
../.venv/bin/python controles_kpi.py > ../J1_Retail_Intelligence/01_UC01_besoin_exploration/preuves/controles_kpi.txt
../.venv/bin/python relations_qualite.py          # relations.csv, controles_relations.txt
for s in uc01_cadrage_metier uc01_questions_decisionnelles uc01_dictionnaire_kpi uc01_inventaire_sources \
         uc01_qualification_donnees uc01_limites_hypotheses uc01_schema_fonctionnel; do
  ../.venv/bin/python $s.py
done
```

Remarques :
- `controles_kpi.txt` se termine par un contrôle de `data_refresh/item` ajouté à la main (commande indiquée dans le fichier) ;
  relancer `controles_kpi.py` seul ne régénère pas cette partie.
- `controle_inventaire_complet.txt` et `controle_store_fermeture.txt` viennent de commandes ponctuelles dont la logique est
  décrite en tête de fichier.
- Dépendances Python (dans `.venv`) : pandas, reportlab, openpyxl.
