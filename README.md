# Tonno rosso, pesca sportiva in Italia

Dati ufficiali sulle catture di tonno rosso della pesca sportiva e ricreativa in Italia (contingente SPOR) dichiarate e registrate dalle autorità italiane competenti, dal 2021, ottenuti dal MASAF con richieste di accesso civico.

**Dashboard:** https://duemme.github.io/dbc-data/ (italiano) · https://duemme.github.io/dbc-data/en/ (English)

**Licenza:** [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.it), citando «Matteo Mannini, dati MASAF ottenuti con accesso civico».

## Dataset

- [Dati Campagna Pesca Tonno rosso](data/pescaTonnoRosso/README.md)

## Dashboard

La dashboard è statica e viene pubblicata su GitHub Pages da [`.github/workflows/pages.yml`](.github/workflows/pages.yml) a ogni push su `main` che modifica `site/` o `pescaTonnoRosso.csv`.

[`site/build.py`](site/build.py) genera una pagina per lingua a partire da `template.html` e `i18n.json`, con testi, numeri principali e metadati (schema.org Dataset, Open Graph, hreflang) già scritti nell'HTML, più `sitemap.xml`, `llms.txt` e le immagini di anteprima. I grafici e i filtri sono calcolati nel browser da `app.js`.

Per provarla in locale:

```sh
pip install matplotlib
python3 site/build.py _site
python3 -m http.server -d _site 8000
```
