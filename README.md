# Tonno rosso, pesca sportiva in Italia

Dati ufficiali sulle catture di tonno rosso della pesca sportiva e ricreativa in Italia (contingente SPOR), dal 2021, ottenuti dal MASAF con richieste di accesso civico.

**Dashboard:** https://duemme.github.io/dbc-data/

## Dataset

- [Dati Campagna Pesca Tonno rosso](data/pescaTonnoRosso/README.md)

## Dashboard

La dashboard è una pagina statica in [`site/`](site/), pubblicata su GitHub Pages da [`.github/workflows/pages.yml`](.github/workflows/pages.yml) a ogni push su `main` che modifica la pagina o `pescaTonnoRosso.csv`. Tutti i calcoli avvengono nel browser.

Per provarla in locale:

```sh
cp data/pescaTonnoRosso/pescaTonnoRosso.csv site/
python3 -m http.server -d site 8000
```
