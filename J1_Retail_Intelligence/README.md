# J1 — Retail Intelligence Platform

Remise du TP Jour 1 (IPSSI, Mastère Développement, Data & IA) : UC-01 et UC-02.
Arborescence recommandée au §8.4 du sujet. Jeu de données : archive `retail_project.zip` (TPCx-BB, synthétique).

## Contenu

| Dossier / fichier | Livrable du sujet | État |
|---|---|---|
| `01_UC01_besoin_exploration/cadrage_metier.pdf` | UC01_cadrage_metier | Fait |
| `01_UC01_besoin_exploration/questions_decisionnelles.pdf` | UC01_questions_decisionnelles | Fait |
| `01_UC01_besoin_exploration/dictionnaire_KPI.xlsx` | UC01_dictionnaire_KPI | Fait |
| `01_UC01_besoin_exploration/inventaire_sources.xlsx` | UC01_inventaire_sources | Fait |
| `01_UC01_besoin_exploration/qualification_donnees.pdf` | UC01_qualification_donnees | Fait |
| `01_UC01_besoin_exploration/limites_hypotheses.pdf` | UC01_limites_et_hypotheses | Fait |
| `01_UC01_besoin_exploration/preuves/` | UC01_preuves | Fait (index : `preuves/README.md`) |
| `02_UC02_architecture/comparaison_architectures.pdf` | UC02_comparaison_architectures | Fait |
| `02_UC02_architecture/architecture_cible.pdf` | UC02_architecture_cible | Fait |
| `02_UC02_architecture/schema_flux.pdf` | UC02_schema_flux | Fait |
| `02_UC02_architecture/positionnement_composants.pdf` | UC02_positionnement_composants | Fait |
| `02_UC02_architecture/gouvernance.pdf` | UC02_gouvernance | Fait |
| `02_UC02_architecture/local_vers_azure.pdf` | UC02_local_vers_azure | Fait |
| `02_UC02_architecture/preuves/` | UC02_preuves | Fait (index : `preuves/README.md`) |

Les dossiers `03_complementaire/`, `04_avance/` et `05_contribution_individuelle/` du §8.4 sont absents tant que
les activités correspondantes ne sont pas réalisées.

## Régénérer les documents

Les documents sont produits par les scripts Python de `../sources/` (dépendances dans `../.venv` :
pandas, reportlab, openpyxl). Les procédures complètes sont décrites dans `01_UC01_besoin_exploration/preuves/README.md` et `02_UC02_architecture/preuves/README.md`.

Les données ne sont pas dans le dépôt. Pour relancer les scripts d'analyse, décompresser l'archive
`retail_project.zip` dans `donnees/` à la racine du projet (on obtient `donnees/retail_project/data/` et
`donnees/retail_project/data_refresh/` ; ce dossier est exclu de Git), ou indiquer un autre emplacement avec la
variable d'environnement `RETAIL_DATA`. Les noms de colonnes sont fournis par `sources/schema.py`.

## Statuts utilisés (§4.2)

Vérifié, Déduit, Hypothèse, Non disponible, À valider. Aucune architecture n'est déployée au Jour 1 :
les documents UC-02 sont des documents de conception.
