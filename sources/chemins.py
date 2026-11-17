"""Chemins de la remise J1 (arborescence recommandée au §8.4 du sujet)."""
from pathlib import Path

PROJET = Path(__file__).resolve().parent.parent
REMISE = PROJET / "J1_Retail_Intelligence"

UC01 = REMISE / "01_UC01_besoin_exploration"
UC01_PREUVES = UC01 / "preuves"

UC02 = REMISE / "02_UC02_architecture"
UC02_PREUVES = UC02 / "preuves"
