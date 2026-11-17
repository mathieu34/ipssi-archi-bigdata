"""Chemins de la remise J1 (arborescence recommandée au §8.4 du sujet)."""
import os
from pathlib import Path

PROJET = Path(__file__).resolve().parent.parent
REMISE = PROJET / "J1_Retail_Intelligence"

UC01 = REMISE / "01_UC01_besoin_exploration"
UC01_PREUVES = UC01 / "preuves"

UC02 = REMISE / "02_UC02_architecture"
UC02_PREUVES = UC02 / "preuves"

# Données brutes TPCx-BB : archive retail_project.zip décompressée dans donnees/retail_project/ (dossier exclu de Git),
# ou tout autre emplacement indiqué par la variable d'environnement RETAIL_DATA.
DONNEES = Path(os.environ.get("RETAIL_DATA", PROJET / "donnees" / "retail_project"))
