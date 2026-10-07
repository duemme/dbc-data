# /// script
# requires-python = ">=3.10"
# dependencies = ["pandas"]
# ///
"""Correzioni comuni a tutti gli anni, applicate ai CSV annuali e al file unico.

- peso_kg senza zeri decimali superflui (55, 30.5, 25.14)
- BASILICATA: la costa da cui si pesca è quella ionica, zona FAO 37.2.2
  (nel 2024 il MASAF l'aveva assegnata a 37.2.1, Adriatico)

Uso: uv run script/uniforma.py
"""

from decimal import Decimal
from pathlib import Path

import pandas as pd

out_dir = Path(__file__).resolve().parent.parent


def formatta_peso(valore: str) -> str:
    peso = Decimal(valore).normalize()
    return f"{peso:f}"


def uniforma(d: pd.DataFrame) -> pd.DataFrame:
    d["peso_kg"] = d["peso_kg"].map(formatta_peso)
    d.loc[(d["regione"] == "BASILICATA") & (d["zona_FAO"] == "37.2.1"), "zona_FAO"] = "37.2.2"
    return d


if __name__ == "__main__":
    for csv in sorted(out_dir.glob("pescaTonnoRosso*.csv")):
        d = pd.read_csv(csv, dtype=str)
        uniforma(d).to_csv(csv, index=False)
        print(f"{csv.name}: {len(d)} righe")
