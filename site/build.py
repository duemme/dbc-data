"""Genera il sito statico: una pagina per lingua con testi e numeri già scritti
nell'HTML (per motori di ricerca, anteprime social e LLM), più sitemap,
llms.txt e immagini di anteprima.

Uso: python site/build.py <cartella_di_uscita>
"""

import csv
import html
import json
import shutil
import sys
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

BASE_URL = "https://duemme.github.io/dbc-data/"
REPO_URL = "https://github.com/duemme/dbc-data"
DONATE_URL = "https://paypal.me/MatteoMannini"
LICENSE_URL = "https://creativecommons.org/licenses/by/4.0/"
FIRST_YEAR = 2021

site = Path(__file__).resolve().parent
root = site.parent
csv_path = root / "data" / "pescaTonnoRosso" / "pescaTonnoRosso.csv"
out = Path(sys.argv[1]).resolve()

I18N = json.loads((site / "i18n.json").read_text(encoding="utf-8"))
TEMPLATE = (site / "template.html").read_text(encoding="utf-8")
CSV_URL = BASE_URL + "pescaTonnoRosso.csv"

# ---------- dati ----------

with csv_path.open(encoding="utf-8") as f:
    rows = [
        {
            "boat": r["identificativo_natante"],
            "date": r["data_cattura"],
            "year": int(r["data_cattura"][:4]),
            "kg": float(r["peso_kg"]),
            "region": r["regione"],
            "fao": r["zona_FAO"],
        }
        for r in csv.DictReader(f)
    ]

years = sorted({r["year"] for r in rows})
by_year = defaultdict(list)
for r in rows:
    by_year[r["year"]].append(r)

summary = [
    {
        "year": y,
        "n": len(v),
        "kg": sum(r["kg"] for r in v),
        "avg": sum(r["kg"] for r in v) / len(v),
        "boats": len({r["boat"] for r in v}),
    }
    for y, v in sorted(by_year.items())
]
total_kg = sum(r["kg"] for r in rows)
regions = Counter(r["region"] for r in rows)
top_region, top_n = regions.most_common(1)[0]
last, prev = summary[-1], summary[-2]
dates = sorted(r["date"] for r in rows)
today = date.today().isoformat()


def fmt(n, digits=0, lang="it"):
    s = f"{n:,.{digits}f}"
    if lang == "it":
        s = s.replace(",", "X").replace(".", ",").replace("X", ".")
    return s


def plural(forms, n):
    return (forms["one"] if n == 1 else forms["other"]).replace("{n}", str(n))


def title_case(s):
    return " ".join(w.capitalize() for w in s.split())


def esc(s):
    return html.escape(s, quote=True)


def fill(s, **kw):
    for k, v in kw.items():
        s = s.replace("{" + k + "}", str(v))
    return s


def page_url(lang):
    return BASE_URL + I18N[lang]["path"]


# ---------- pezzi di pagina ----------


def tiles_html(t, lang):
    boats = len({(r["year"], r["boat"]) for r in rows})
    items = [
        (t["t_catches"], fmt(len(rows), 0, lang), plural(t["t_catches_sub"], len(years)), True),
        (t["t_weight"], fmt(total_kg / 1000, 1, lang), t["t_weight_sub"], False),
        (t["t_avg"], fmt(total_kg / len(rows), 1, lang), t["t_avg_sub"], False),
        (t["t_boats"], fmt(boats, 0, lang), t["t_boats_sub"], False),
        (t["t_regions"], fmt(len(regions), 0, lang), t["t_regions_sub"], False),
    ]
    return "".join(
        f'<div class="tile{" hero" if hero else ""}"><div class="tile-label">{esc(label)}</div>'
        f'<div class="tile-value">{value}</div><div class="tile-sub">{esc(sub)}</div></div>'
        for label, value, sub, hero in items
    )


def years_table_html(t, lang):
    head = "".join(
        "<th" + (' class="num"' if c else "") + f">{esc(t[k])}</th>"
        for k, c in [("c_year", 0), ("c_catches", 1), ("c_total", 1), ("c_avg", 1), ("c_boats", 1)]
    )
    body = "".join(
        f'<tr><td><span class="key" style="background:var(--series-{(s["year"] - FIRST_YEAR) % 8 + 1})"></span>{s["year"]}</td>'
        f'<td class="num">{fmt(s["n"], 0, lang)}</td><td class="num">{fmt(s["kg"], 0, lang)}</td>'
        f'<td class="num">{fmt(s["avg"], 1, lang)}</td><td class="num">{fmt(s["boats"], 0, lang)}</td></tr>'
        for s in summary
    )
    return f"<thead><tr>{head}</tr></thead><tbody>{body}</tbody>"


def facts(t, lang):
    delta = (last["n"] - prev["n"]) / prev["n"] * 100
    return fill(
        t["facts"],
        last=last["year"],
        prev=prev["year"],
        n=fmt(len(rows), 0, lang),
        t=fmt(total_kg / 1000, 1, lang),
        avg=fmt(total_kg / len(rows), 1, lang),
        n_last=fmt(last["n"], 0, lang),
        delta=("+" if delta >= 0 else "−") + fmt(abs(delta), 1, lang) + "%",
        top_region=title_case(top_region),
        top_n=fmt(top_n, 0, lang),
    )


def jsonld(t, lang):
    data = {
        "@context": "https://schema.org",
        "@type": "Dataset",
        "name": fill(t["ds_name"], last=last["year"]),
        "description": fill(t["ds_description"], last=last["year"]),
        "url": page_url(lang),
        "sameAs": REPO_URL,
        "inLanguage": lang,
        "keywords": t["keywords"],
        "license": LICENSE_URL,
        "isAccessibleForFree": True,
        "creator": {
            "@type": "Person",
            "name": "Matteo Mannini",
            "url": "https://github.com/duemme",
            "sameAs": ["https://twitter.com/ManniniMatteo"],
        },
        "sourceOrganization": {
            "@type": "GovernmentOrganization",
            "name": "Ministero dell'agricoltura, della sovranità alimentare e delle foreste (MASAF)",
            "url": "https://www.masaf.gov.it/",
        },
        "temporalCoverage": f"{dates[0]}/{dates[-1]}",
        "spatialCoverage": {"@type": "Place", "name": "Italy", "address": {"@type": "PostalAddress", "addressCountry": "IT"}},
        "variableMeasured": [
            {"@type": "PropertyValue", "name": "identificativo_natante", "description": "Anonymous boat identifier assigned by the ministry; not guaranteed to be comparable across years"},
            {"@type": "PropertyValue", "name": "data_cattura", "description": "Catch date (YYYY-MM-DD)"},
            {"@type": "PropertyValue", "name": "peso_kg", "description": "Weight of the fish", "unitText": "kg"},
            {"@type": "PropertyValue", "name": "regione", "description": "Italian region of landing"},
            {"@type": "PropertyValue", "name": "zona_FAO", "description": "FAO major fishing area 37 division: 37.1.3, 37.2.1 or 37.2.2"},
        ],
        "measurementTechnique": "Catch declarations recorded by the competent Italian authorities for the recreational bluefin tuna quota (SPOR), obtained through freedom of information requests",
        "distribution": [
            {"@type": "DataDownload", "encodingFormat": "text/csv", "contentUrl": CSV_URL},
        ],
        "dateModified": today,
    }
    return json.dumps(data, ensure_ascii=False, indent=2).replace("</", "<\\/")


def build_page(lang):
    t = I18N[lang]
    other = "en" if lang == "it" else "it"
    last_year = last["year"]
    values = {
        "lang": lang,
        "base": '<base href="../">' if t["path"] else "",
        "page_title": esc(fill(t["page_title"], last=last_year)),
        "meta_description": esc(fill(t["meta_description"], last=last_year, n=fmt(len(rows), 0, lang), t=fmt(total_kg / 1000, 1, lang))),
        "og_title": esc(t["og_title"]),
        "og_locale": t["locale"].replace("-", "_"),
        "og_locale_alt": I18N[other]["locale"].replace("-", "_"),
        "og_image": BASE_URL + f"og-{lang}.png",
        "url": page_url(lang),
        "url_it": page_url("it"),
        "url_en": page_url("en"),
        "cur_it": 'aria-current="page"' if lang == "it" else "",
        "cur_en": 'aria-current="page"' if lang == "en" else "",
        "donate_url": DONATE_URL,
        "facts": esc(facts(t, lang)),
        "tiles": tiles_html(t, lang),
        "years_table": years_table_html(t, lang),
        "about_repo": fill(t["about_repo"], repo=REPO_URL, csv="pescaTonnoRosso.csv"),
        "about_license": t["about_license"],
        "jsonld": jsonld(t, lang),
        "i18n": json.dumps(t, ensure_ascii=False).replace("</", "<\\/"),
    }
    page = TEMPLATE
    for k, v in values.items():
        page = page.replace("{{" + k + "}}", str(v))
    # tutte le altre chiavi sono testi semplici del dizionario
    for k, v in t.items():
        if isinstance(v, str):
            page = page.replace("{{" + k + "}}", esc(v))
    if "{{" in page:
        missing = page[page.index("{{"):page.index("}}", page.index("{{")) + 2]
        sys.exit(f"Segnaposto non sostituito: {missing}")
    return page


# ---------- file di supporto ----------


def sitemap():
    links = "".join(
        f'\n    <xhtml:link rel="alternate" hreflang="{h}" href="{page_url(l)}"/>'
        for h, l in [("it", "it"), ("en", "en"), ("x-default", "en")]
    )
    urls = "".join(
        f"\n  <url>\n    <loc>{page_url(l)}</loc>\n    <lastmod>{today}</lastmod>{links}\n  </url>" for l in ["it", "en"]
    )
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">'
        f"{urls}\n</urlset>\n"
    )


def llms_txt():
    t = I18N["en"]
    table = "\n".join(
        f"| {s['year']} | {s['n']} | {s['kg']:.0f} | {s['avg']:.1f} | {s['boats']} |" for s in summary
    )
    by_region = "\n".join(f"| {title_case(r)} | {n} |" for r, n in regions.most_common())
    return f"""# {fill(t['ds_name'], last=last['year'])}

> {fill(t['ds_description'], last=last['year'])}

{facts(t, 'en')}

Dashboard: {page_url('en')} (English), {page_url('it')} (Italiano)
Data (CSV, UTF-8): {CSV_URL}
Source code and original files: {REPO_URL}
Licence: CC BY 4.0 ({LICENSE_URL}). Cite as: Matteo Mannini, MASAF data obtained through FOI requests, {page_url('en')}
Last updated: {today}

## Data dictionary

One row per fish caught.

- `identificativo_natante` (integer): anonymous boat identifier assigned by the ministry; not guaranteed to be comparable across years
- `data_cattura` (date, YYYY-MM-DD): catch date
- `peso_kg` (number): weight in kg
- `regione` (string, upper case Italian region name): region of landing
- `zona_FAO` (string): FAO area 37 division. 37.1.3 = Ligurian Sea, Tyrrhenian Sea and Sardinia; 37.2.1 = Adriatic Sea; 37.2.2 = Ionian Sea

## Catches by year

| Year | Catches | Total weight (kg) | Average weight (kg) | Boats |
|---|---|---|---|---|
{table}

## Catches by region, {years[0]}-{years[-1]}

| Region | Catches |
|---|---|
{by_region}

## Caveats

- Only catches declared and recorded by the competent Italian authorities under the sport and recreational quota (SPOR); undeclared catches and commercial fishing are not included.
- {t['about_fix']}
- Raw files are published as received from the ministry in `data/pescaTonnoRosso/grezzi/` of the repository.
"""


def og_image(lang, path):
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib non disponibile: immagini di anteprima saltate")
        return
    t = I18N[lang]
    colors = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#4a3aa7", "#e34948"]
    fig = plt.figure(figsize=(12, 6.3), dpi=100, facecolor="#fcfcfb")
    fig.text(0.05, 0.92, t["og_title"], fontsize=30, fontweight="bold", color="#0b0b0b", wrap=True, va="top")
    fig.text(0.05, 0.68, f"{fmt(len(rows), 0, lang)} {t['u_catches']['other']} · {fmt(total_kg / 1000, 1, lang)} t · {years[0]}–{years[-1]}", fontsize=20, color="#52514e")
    ax = fig.add_axes([0.05, 0.1, 0.9, 0.5], facecolor="#fcfcfb")
    xs = [s["year"] for s in summary]
    ns = [s["n"] for s in summary]
    bars = ax.bar([str(x) for x in xs], ns, color=[colors[(y - FIRST_YEAR) % 8] for y in xs], width=0.5)
    for b, n in zip(bars, ns):
        ax.text(b.get_x() + b.get_width() / 2, n + max(ns) * 0.02, fmt(n, 0, lang), ha="center", fontsize=16, color="#52514e")
    for s in ["top", "right", "left"]:
        ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color("#c3c2b7")
    ax.set_yticks([])
    ax.tick_params(axis="x", labelsize=16, colors="#52514e", length=0)
    fig.text(0.95, 0.03, BASE_URL.removeprefix("https://"), fontsize=14, color="#898781", ha="right")
    fig.savefig(path, facecolor=fig.get_facecolor())
    plt.close(fig)


# ---------- scrittura ----------

if out.exists():
    shutil.rmtree(out)
(out / "en").mkdir(parents=True)
(out / "index.html").write_text(build_page("it"), encoding="utf-8")
(out / "en" / "index.html").write_text(build_page("en"), encoding="utf-8")
for name in ["style.css", "app.js"]:
    shutil.copy(site / name, out / name)
shutil.copy(csv_path, out / "pescaTonnoRosso.csv")
(out / "sitemap.xml").write_text(sitemap(), encoding="utf-8")
(out / "llms.txt").write_text(llms_txt(), encoding="utf-8")
for lang in I18N:
    og_image(lang, out / f"og-{lang}.png")
print(f"Sito generato in {out}")
