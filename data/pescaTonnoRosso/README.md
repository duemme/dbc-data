# Dati Campagna Pesca Tonno rosso

Campagna di pesca del tonno rosso – anni dal 2021 al 2026 – contingente assegnato alla pesca sportiva/ricreativa (SPOR). Comprende le catture dichiarate e registrate dalle autorità italiane competenti.

## File

- [pescaTonnoRosso.csv](pescaTonnoRosso.csv)

## Note

Dati ricevuti a valle di una richiesta di accesso civico, fatta da [Matteo Mannini](https://twitter.com/ManniniMatteo).

Correzioni rispetto ai dati originali (vedi `script/uniforma.py`):

- `peso_kg` scritto senza zeri decimali superflui (es. `30.00` → `30`);
- 2024: le 7 catture in BASILICATA erano assegnate alla zona FAO 37.2.1 (Adriatico), che non bagna la regione; corrette in 37.2.2 (Ionio).

## Schema

| name | type | note |
| --- | --- | --- |
| identificativo_natante | integer |  |
| data_cattura | date |  |
| peso_kg | number |  |
| regione | string |  |
| zona_FAO | string |  |

## Risorse

- [Richiesta accesso civico 2021](risorse/accesso_civico_-_campagna_tonno_rosso.pdf)
