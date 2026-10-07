# /// script
# requires-python = ">=3.10"
# dependencies = ["pandas", "xlrd"]
# ///
"""Normalizza i dati grezzi 2026 e li aggiunge al file unico.

Uso: uv run script/normalize_2026.py [percorso/file.xls]
"""

import sys
from pathlib import Path

import pandas as pd

from uniforma import uniforma

folder = Path(__file__).resolve().parent
out_dir = folder.parent

nomeFile = Path(sys.argv[1]) if len(sys.argv) > 1 else out_dir / "grezzi" / "BFT_SPORT_2026.xls"

REGIONI = {
    "ABRUZZO", "BASILICATA", "CALABRIA", "CAMPANIA", "EMILIA ROMAGNA",
    "FRIULI VENEZIA GIULIA", "LAZIO", "LIGURIA", "MARCHE", "MOLISE",
    "PUGLIA", "SARDEGNA", "SICILIA", "TOSCANA", "VENETO",
}

# varianti già incontrate negli anni precedenti
ALIAS = {
    "CAMPOBASSO": "MOLISE",
    "VENEZIA": "VENETO",
    "FRIULI VENETO GIULIA": "FRIULI VENEZIA GIULIA",
    "FRIULI-VENEZIA GIULIA": "FRIULI VENEZIA GIULIA",
    "EMILIA-ROMAGNA": "EMILIA ROMAGNA",
}

d = pd.read_excel(nomeFile, usecols=range(5)).dropna(how="all")
d.columns = ["data_cattura", "identificativo_natante", "peso_kg", "regione", "zona_FAO"]

d["regione"] = d["regione"].str.strip().str.upper().str.split().str.join(" ")
d["regione"] = d["regione"].replace(ALIAS)
sconosciute = set(d["regione"]) - REGIONI
if sconosciute:
    sys.exit(f"Regioni non riconosciute, aggiungerle ad ALIAS: {sorted(sconosciute)}")

d["zona_FAO"] = d["zona_FAO"].astype(str).str.strip()
d["identificativo_natante"] = d["identificativo_natante"].astype(int)
d["peso_kg"] = d["peso_kg"].astype(float)
d["data_cattura"] = pd.to_datetime(d["data_cattura"]).dt.strftime("%Y-%m-%d")

d = d[["identificativo_natante", "data_cattura", "peso_kg", "regione", "zona_FAO"]]
d = uniforma(d.astype(str))
d = d.sort_values(["data_cattura", "regione"], kind="stable")
d.to_csv(out_dir / "pescaTonnoRosso_2026.csv", index=False)

# unisci i file: le righe 2026 vengono dopo tutte le precedenti
unico = out_dir / "pescaTonnoRosso.csv"
precedenti = pd.read_csv(unico, dtype=str)
precedenti = precedenti[~precedenti["data_cattura"].str.startswith("2026")]
precedenti.to_csv(unico, index=False)
d.to_csv(unico, mode="a", header=False, index=False)

print(f"{len(d)} catture 2026 normalizzate")
