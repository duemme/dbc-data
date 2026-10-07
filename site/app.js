// Dashboard tonno rosso: tutto il calcolo avviene nel browser a partire dal CSV.

const CSV_URL = "pescaTonnoRosso.csv";
const REPO_URL = "https://github.com/duemme/dbc-data";
// Link per le donazioni (es. https://paypal.me/nomeutente). Vuoto = pulsante nascosto.
const DONATE_URL = "https://paypal.me/MatteoMannini";
const FIRST_YEAR = 2021;
const ROWS_STEP = 50;

const I18N = {
  it: {
    brand: "Tonno rosso · pesca sportiva",
    donate: "Sostieni il progetto",
    title: "Quanti tonni rossi pescano i pescatori sportivi in Italia",
    lede: "Ogni cattura di tonno rosso della pesca sportiva e ricreativa, dal 2021 a oggi: data, peso, regione e zona di pesca. Dati ufficiali del Ministero (MASAF) ottenuti con richieste di accesso civico.",
    f_years: "Anni",
    f_region: "Regione",
    f_fao: "Zona FAO",
    all_regions: "Tutte le regioni",
    all_fao: "Tutte le zone",
    loading: "Caricamento dati…",
    error: "Non è stato possibile caricare i dati.",
    empty: "Nessuna cattura per i filtri scelti.",
    t_catches: "Catture",
    t_weight: "Peso totale",
    t_avg: "Peso medio",
    t_boats: "Barche",
    t_regions: "Regioni",
    t_catches_sub: (y) => (y === 1 ? "in 1 anno" : `in ${y} anni`),
    t_weight_sub: "tonnellate",
    t_avg_sub: "kg per esemplare",
    t_boats_sub: "con almeno una cattura",
    t_regions_sub: "con almeno una cattura",
    season_t: "Come procede la stagione",
    season_d: "Catture cumulate giorno per giorno, un anno per linea.",
    years_count_t: "Catture per anno",
    years_weight_t: "Peso totale per anno (tonnellate)",
    years_table_t: "Riepilogo per anno",
    regions_t: "Catture per regione",
    hist_t: "Quanto pesano i tonni pescati",
    hist_d: "Numero di catture per classe di peso (5 kg).",
    heat_t: "Catture per regione e anno",
    heat_d: "Più intenso è il colore, più sono le catture. Il trattino indica che non ci sono catture registrate.",
    data_t: "Tutte le catture",
    download: "Scarica CSV",
    more: "Mostra altre",
    c_year: "Anno",
    c_date: "Data",
    c_boat: "Barca",
    c_weight: "Peso (kg)",
    c_region: "Regione",
    c_fao: "Zona FAO",
    c_catches: "Catture",
    c_total: "Peso totale (kg)",
    c_avg: "Peso medio (kg)",
    c_boats: "Barche",
    u_catches: (n) => (n === 1 ? "cattura" : "catture"),
    u_kg: "kg",
    u_t: "t",
    h_weight: "kg",
    shown: (a, b) => `${a} di ${b} catture`,
    about_t: "Note sui dati",
    about_src: `Fonte: Ministero dell'agricoltura, della sovranità alimentare e delle foreste (MASAF), Direzione generale della pesca. Dati ottenuti con richieste di accesso civico da Matteo Mannini. Riguardano solo il contingente assegnato alla pesca sportiva e ricreativa (SPOR), non la pesca professionale.`,
    about_ids: "Il numero della barca è un identificativo anonimo assegnato ogni anno: non permette di seguire la stessa barca da un anno all'altro.",
    about_fix: "Correzioni rispetto ai file originali: nomi delle regioni uniformati; nel 2024 sette catture in Basilicata erano attribuite alla zona 37.2.1 (Adriatico), che non bagna la regione, e sono state riportate alla 37.2.2 (Ionio).",
    about_repo: `Dati, file originali e codice sono su <a href="${REPO_URL}">GitHub</a>.`,
    footer: "Progetto indipendente di data journalism. I dati sono pubblici e riutilizzabili citando la fonte.",
    fao: {
      "37.1.3": "37.1.3 · Ligure, Tirreno e Sardegna",
      "37.2.1": "37.2.1 · Adriatico",
      "37.2.2": "37.2.2 · Ionio",
    },
  },
  en: {
    brand: "Bluefin tuna · recreational fishing",
    donate: "Support the project",
    title: "How many bluefin tuna do recreational anglers catch in Italy",
    lede: "Every bluefin tuna caught by sport and recreational fishers since 2021: date, weight, region and fishing area. Official data from the Italian Ministry of Agriculture (MASAF), obtained through freedom of information requests.",
    f_years: "Years",
    f_region: "Region",
    f_fao: "FAO area",
    all_regions: "All regions",
    all_fao: "All areas",
    loading: "Loading data…",
    error: "The data could not be loaded.",
    empty: "No catches for the selected filters.",
    t_catches: "Catches",
    t_weight: "Total weight",
    t_avg: "Average weight",
    t_boats: "Boats",
    t_regions: "Regions",
    t_catches_sub: (y) => (y === 1 ? "in 1 year" : `in ${y} years`),
    t_weight_sub: "tonnes",
    t_avg_sub: "kg per fish",
    t_boats_sub: "with at least one catch",
    t_regions_sub: "with at least one catch",
    season_t: "How the season unfolds",
    season_d: "Cumulative catches day by day, one line per year.",
    years_count_t: "Catches per year",
    years_weight_t: "Total weight per year (tonnes)",
    years_table_t: "Summary by year",
    regions_t: "Catches by region",
    hist_t: "How much the fish weigh",
    hist_d: "Number of catches per weight class (5 kg).",
    heat_t: "Catches by region and year",
    heat_d: "The more intense the colour, the more catches. A dash means no catches were recorded.",
    data_t: "All catches",
    download: "Download CSV",
    more: "Show more",
    c_year: "Year",
    c_date: "Date",
    c_boat: "Boat",
    c_weight: "Weight (kg)",
    c_region: "Region",
    c_fao: "FAO area",
    c_catches: "Catches",
    c_total: "Total weight (kg)",
    c_avg: "Average weight (kg)",
    c_boats: "Boats",
    u_catches: (n) => (n === 1 ? "catch" : "catches"),
    u_kg: "kg",
    u_t: "t",
    h_weight: "kg",
    shown: (a, b) => `${a} of ${b} catches`,
    about_t: "About the data",
    about_src: `Source: Italian Ministry of Agriculture, Food Sovereignty and Forests (MASAF), Directorate-General for Fisheries. Data obtained through freedom of information requests (accesso civico) by Matteo Mannini. They cover only the quota assigned to sport and recreational fishing (SPOR), not commercial fishing.`,
    about_ids: "The boat number is an anonymous identifier assigned each year: it cannot be used to follow the same boat across years.",
    about_fix: "Corrections to the original files: region names standardised; in 2024 seven catches in Basilicata were assigned to area 37.2.1 (Adriatic), which does not border the region, and were moved to 37.2.2 (Ionian).",
    about_repo: `Data, original files and code are on <a href="${REPO_URL}">GitHub</a>.`,
    footer: "Independent data journalism project. The data are public and may be reused with attribution.",
    fao: {
      "37.1.3": "37.1.3 · Ligurian, Tyrrhenian & Sardinia",
      "37.2.1": "37.2.1 · Adriatic",
      "37.2.2": "37.2.2 · Ionian",
    },
  },
};

const state = { lang: "it", years: new Set(), region: "", fao: "", rowsShown: ROWS_STEP };
let DATA = [];
let YEARS = [];

// ---------- utilità ----------

const store = {
  get(k) { try { return localStorage.getItem(k); } catch { return null; } },
  set(k, v) { try { localStorage.setItem(k, v); } catch { /* niente */ } },
};

const t = (k) => I18N[state.lang][k];
const locale = () => (state.lang === "it" ? "it-IT" : "en-GB");
const fmt = (n, digits = 0) =>
  new Intl.NumberFormat(locale(), { minimumFractionDigits: digits, maximumFractionDigits: digits }).format(n);
const fmtDay = (ms) =>
  new Intl.DateTimeFormat(locale(), { day: "numeric", month: "short", timeZone: "UTC" }).format(ms);
const fmtDate = (s) =>
  new Intl.DateTimeFormat(locale(), { day: "2-digit", month: "2-digit", year: "numeric", timeZone: "UTC" }).format(Date.parse(s));

const css = (name) => getComputedStyle(document.documentElement).getPropertyValue(name).trim();
const yearColor = (y) => css(`--series-${((y - FIRST_YEAR) % 8) + 1}`);
const titleCase = (s) => s.toLowerCase().replace(/(^|[\s-])\S/g, (m) => m.toUpperCase());
// giorno della stagione, sullo stesso anno fittizio per sovrapporre gli anni
const seasonDay = (s) => Date.UTC(2000, +s.slice(5, 7) - 1, +s.slice(8, 10));

function el(tag, attrs = {}, text) {
  const node = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) node.setAttribute(k, v);
  if (text !== undefined) node.textContent = text;
  return node;
}

function plotStyle() {
  return {
    fontFamily: "system-ui, -apple-system, 'Segoe UI', sans-serif",
    fontSize: "12px",
    color: css("--text-muted"),
    background: "transparent",
    overflow: "visible",
  };
}

// barre al massimo 24px di spessore: il resto della banda resta vuoto
const bandPadding = (width, n) => Math.min(0.85, Math.max(0.2, 1 - 24 / (width / Math.max(n, 1))));

// ---------- dati ----------

async function load() {
  const rows = await d3.csv(CSV_URL, (d) => ({
    boat: +d.identificativo_natante,
    date: d.data_cattura,
    year: +d.data_cattura.slice(0, 4),
    kg: +d.peso_kg,
    region: d.regione,
    fao: d.zona_FAO,
  }));
  DATA = rows;
  YEARS = [...new Set(rows.map((d) => d.year))].sort();
  state.years = new Set(YEARS);
}

function filtered() {
  return DATA.filter(
    (d) =>
      state.years.has(d.year) &&
      (!state.region || d.region === state.region) &&
      (!state.fao || d.fao === state.fao),
  );
}

function summarizeYears(rows) {
  return d3
    .rollups(
      rows,
      (v) => ({
        n: v.length,
        kg: d3.sum(v, (d) => d.kg),
        avg: d3.mean(v, (d) => d.kg),
        boats: new Set(v.map((d) => d.boat)).size,
        regions: new Set(v.map((d) => d.region)).size,
      }),
      (d) => d.year,
    )
    .map(([year, s]) => ({ year, ...s }))
    .sort((a, b) => a.year - b.year);
}

// ---------- interfaccia ----------

function applyI18n() {
  document.documentElement.lang = state.lang;
  document.querySelectorAll("[data-i18n]").forEach((node) => {
    const v = t(node.dataset.i18n);
    if (typeof v !== "string") return;
    // i testi con link sono scritti da noi, non vengono dai dati
    if (v.includes("<a ")) node.innerHTML = v;
    else node.textContent = v;
  });
  document.querySelectorAll(".lang button").forEach((b) => b.setAttribute("aria-pressed", String(b.dataset.lang === state.lang)));
  document.title = state.lang === "it" ? "Tonno rosso, pesca sportiva" : "Bluefin tuna, recreational fishing";
  const donate = document.getElementById("donate");
  if (DONATE_URL) { donate.href = DONATE_URL; donate.hidden = false; }
}

function buildFilters() {
  const chips = document.getElementById("f-years");
  chips.replaceChildren();
  for (const y of YEARS) {
    const b = el("button", { type: "button", class: "chip", "aria-pressed": String(state.years.has(y)) });
    const key = el("span", { class: "key" });
    key.style.background = yearColor(y);
    b.append(key, document.createTextNode(String(y)));
    b.addEventListener("click", () => {
      if (state.years.has(y)) {
        if (state.years.size === 1) return; // almeno un anno resta selezionato
        state.years.delete(y);
      } else state.years.add(y);
      b.setAttribute("aria-pressed", String(state.years.has(y)));
      state.rowsShown = ROWS_STEP;
      render();
    });
    chips.append(b);
  }

  const regionSel = document.getElementById("f-region");
  regionSel.replaceChildren(el("option", { value: "" }, t("all_regions")));
  for (const r of [...new Set(DATA.map((d) => d.region))].sort()) {
    regionSel.append(el("option", { value: r }, titleCase(r)));
  }
  regionSel.value = state.region;
  regionSel.onchange = () => { state.region = regionSel.value; state.rowsShown = ROWS_STEP; render(); };

  const faoSel = document.getElementById("f-fao");
  faoSel.replaceChildren(el("option", { value: "" }, t("all_fao")));
  for (const f of [...new Set(DATA.map((d) => d.fao))].sort()) {
    faoSel.append(el("option", { value: f }, t("fao")[f] ?? f));
  }
  faoSel.value = state.fao;
  faoSel.onchange = () => { state.fao = faoSel.value; state.rowsShown = ROWS_STEP; render(); };
}

function renderTiles(rows) {
  const tiles = document.getElementById("tiles");
  const kg = d3.sum(rows, (d) => d.kg);
  const boats = new Set(rows.map((d) => `${d.year}|${d.boat}`)).size;
  const regions = new Set(rows.map((d) => d.region)).size;
  const years = new Set(rows.map((d) => d.year)).size;
  const items = [
    { label: t("t_catches"), value: fmt(rows.length), sub: t("t_catches_sub")(years), hero: true },
    { label: t("t_weight"), value: fmt(kg / 1000, 1), sub: t("t_weight_sub") },
    { label: t("t_avg"), value: fmt(rows.length ? kg / rows.length : 0, 1), sub: t("t_avg_sub") },
    { label: t("t_boats"), value: fmt(boats), sub: t("t_boats_sub") },
    { label: t("t_regions"), value: fmt(regions), sub: t("t_regions_sub") },
  ];
  tiles.replaceChildren(
    ...items.map((it) => {
      const tile = el("div", { class: `tile${it.hero ? " hero" : ""}` });
      tile.append(el("div", { class: "tile-label" }, it.label), el("div", { class: "tile-value" }, it.value), el("div", { class: "tile-sub" }, it.sub));
      return tile;
    }),
  );
}

function renderSeason(rows) {
  const box = document.getElementById("c-season");
  const legend = document.getElementById("season-legend");
  const width = box.clientWidth;
  const years = [...new Set(rows.map((d) => d.year))].sort();

  legend.replaceChildren(
    ...years.map((y) => {
      const s = el("span");
      const k = el("i");
      k.style.background = yearColor(y);
      s.append(k, document.createTextNode(String(y)));
      return s;
    }),
  );

  const counts = d3.rollup(rows, (v) => v.length, (d) => d.year, (d) => seasonDay(d.date));
  const days = rows.map((d) => seasonDay(d.date));
  const start = d3.min(days);
  const end = d3.max(days);
  const grid = d3.utcDay.range(start, end + 86400000).map((d) => +d);
  const lastDay = new Map(years.map((y) => [y, d3.max(counts.get(y).keys())]));

  const points = [];
  const cross = grid.map((day) => ({ day, values: [] }));
  for (const y of years) {
    let cum = 0;
    grid.forEach((day, i) => {
      if (day > lastDay.get(y)) return;
      cum += counts.get(y).get(day) ?? 0;
      points.push({ year: y, day, cum });
      cross[i].values.push([y, cum]);
    });
  }
  const ends = years.map((y) => points.filter((p) => p.year === y).at(-1));

  const tipTitle = (d) =>
    [fmtDay(d.day), ...d.values.slice().sort((a, b) => b[1] - a[1]).map(([y, v]) => `${y}   ${fmt(v)} ${t("u_catches")(v)}`)].join("\n");

  const plot = Plot.plot({
    width,
    height: Math.max(260, Math.min(420, width * 0.5)),
    marginRight: 16,
    marginLeft: 44,
    style: plotStyle(),
    x: { type: "utc", tickFormat: fmtDay, ticks: width < 500 ? 4 : 8, label: null },
    y: { grid: true, label: null, tickFormat: (v) => fmt(v) },
    marks: [
      Plot.gridY({ stroke: css("--grid"), strokeOpacity: 1 }),
      Plot.ruleY([0], { stroke: css("--axis") }),
      Plot.lineY(points, { x: "day", y: "cum", z: "year", stroke: (d) => yearColor(d.year), strokeWidth: 2, curve: "step-after" }),
      Plot.dot(ends, { x: "day", y: "cum", fill: (d) => yearColor(d.year), r: 4, stroke: css("--surface-1"), strokeWidth: 2 }),
      Plot.ruleX(cross, Plot.pointerX({ x: "day", stroke: css("--axis") })),
      Plot.tip(cross, Plot.pointerX({ x: "day", title: tipTitle, frameAnchor: "top" })),
    ],
  });
  box.replaceChildren(plot);
}

function renderYearBars(summary) {
  const specs = [
    { id: "c-years-count", value: (d) => d.n, label: (d) => fmt(d.n), tip: (d) => `${d.year}\n${fmt(d.n)} ${t("u_catches")(d.n)}` },
    { id: "c-years-weight", value: (d) => d.kg / 1000, label: (d) => fmt(d.kg / 1000, 1), tip: (d) => `${d.year}\n${fmt(d.kg / 1000, 1)} ${t("u_t")}` },
  ];
  for (const s of specs) {
    const box = document.getElementById(s.id);
    const width = box.clientWidth;
    const plot = Plot.plot({
      width,
      height: 240,
      marginTop: 24,
      marginLeft: 40,
      style: plotStyle(),
      x: { type: "band", label: null, padding: bandPadding(width, summary.length), tickFormat: String },
      y: { grid: true, label: null, tickFormat: (v) => fmt(v) },
      marks: [
        Plot.gridY({ stroke: css("--grid"), strokeOpacity: 1 }),
        Plot.barY(summary, { x: "year", y: s.value, fill: (d) => yearColor(d.year), ry2: 4 }),
        Plot.ruleY([0], { stroke: css("--axis") }),
        Plot.text(summary, { x: "year", y: s.value, text: s.label, dy: -10, fill: css("--text-secondary"), fontSize: 12 }),
        Plot.tip(summary, Plot.pointerX({ x: "year", y: s.value, title: s.tip })),
      ],
    });
    box.replaceChildren(plot);
  }
}

function renderYearTable(summary) {
  const table = document.getElementById("t-years");
  const head = el("tr");
  [["c_year", ""], ["c_catches", "num"], ["c_total", "num"], ["c_avg", "num"], ["c_boats", "num"]].forEach(([k, c]) => head.append(el("th", c ? { class: c } : {}, t(k))));
  const body = summary.map((d) => {
    const tr = el("tr");
    const yearCell = el("td");
    const key = el("span", { class: "key" });
    key.style.background = yearColor(d.year);
    yearCell.append(key, document.createTextNode(String(d.year)));
    tr.append(yearCell, el("td", { class: "num" }, fmt(d.n)), el("td", { class: "num" }, fmt(d.kg)), el("td", { class: "num" }, fmt(d.avg, 1)), el("td", { class: "num" }, fmt(d.boats)));
    return tr;
  });
  const thead = el("thead");
  thead.append(head);
  const tbody = el("tbody");
  tbody.append(...body);
  table.replaceChildren(thead, tbody);
}

function renderRegions(rows) {
  const box = document.getElementById("c-regions");
  const width = box.clientWidth;
  const data = d3
    .rollups(rows, (v) => ({ n: v.length, kg: d3.sum(v, (d) => d.kg) }), (d) => d.region)
    .map(([region, s]) => ({ region, name: titleCase(region), ...s }))
    .sort((a, b) => b.n - a.n);
  const plot = Plot.plot({
    width,
    height: data.length * 30 + 30,
    marginLeft: 150,
    marginRight: 48,
    style: plotStyle(),
    x: { axis: null },
    y: { domain: data.map((d) => d.name), label: null, tickSize: 0, padding: 0.3 },
    marks: [
      Plot.barX(data, { y: "name", x: "n", fill: css("--series-1"), rx2: 4 }),
      Plot.ruleX([0], { stroke: css("--axis") }),
      Plot.text(data, { y: "name", x: "n", text: (d) => fmt(d.n), dx: 6, textAnchor: "start", fill: css("--text-secondary"), fontSize: 12 }),
      Plot.tip(data, Plot.pointerY({ y: "name", x: "n", title: (d) => `${d.name}\n${fmt(d.n)} ${t("u_catches")(d.n)}\n${fmt(d.kg)} ${t("u_kg")}` })),
    ],
  });
  box.replaceChildren(plot);
}

function renderHist(rows) {
  const box = document.getElementById("c-hist");
  const width = box.clientWidth;
  const max = d3.max(rows, (d) => d.kg);
  const thresholds = d3.range(Math.floor(d3.min(rows, (d) => d.kg) / 5) * 5, max + 5, 5);
  const plot = Plot.plot({
    width,
    height: 260,
    marginLeft: 44,
    style: plotStyle(),
    x: { label: t("h_weight"), labelAnchor: "right", labelArrow: "none", tickFormat: (v) => fmt(v) },
    y: { grid: true, label: null, tickFormat: (v) => fmt(v) },
    marks: [
      Plot.gridY({ stroke: css("--grid"), strokeOpacity: 1 }),
      Plot.rectY(rows, Plot.binX({ y: "count", title: (v) => v }, {
        x: "kg",
        thresholds,
        fill: css("--series-1"),
        inset: 1,
        ry2: 4,
      })),
      Plot.ruleY([0], { stroke: css("--axis") }),
      Plot.tip(rows, Plot.pointerX(Plot.binX({ y: "count", title: (v) => {
        const lo = Math.floor(v[0].kg / 5) * 5;
        return `${fmt(lo)}–${fmt(lo + 5)} ${t("u_kg")}\n${fmt(v.length)} ${t("u_catches")(v.length)}`;
      } }, { x: "kg", thresholds }))),
    ],
  });
  box.replaceChildren(plot);
}

function renderHeat(rows) {
  const box = document.getElementById("c-heat");
  const width = box.clientWidth;
  const years = [...state.years].sort();
  const regions = d3
    .rollups(rows, (v) => v.length, (d) => d.region)
    .sort((a, b) => b[1] - a[1])
    .map(([r]) => r);
  const counts = d3.rollup(rows, (v) => v.length, (d) => d.region, (d) => d.year);
  const cells = regions.flatMap((r) => years.map((y) => ({ region: titleCase(r), year: y, n: counts.get(r)?.get(y) ?? 0 })));
  const maxN = d3.max(cells, (d) => d.n) || 1;
  const color = d3.scaleLinear([1, maxN], [css("--seq-lo"), css("--seq-hi")]).interpolate(d3.interpolateLab);
  const ink = (n) => {
    if (!n) return css("--text-muted");
    const c = d3.lab(color(n));
    return c.l > 60 ? "#0b0b0b" : "#ffffff";
  };
  const plot = Plot.plot({
    width,
    height: regions.length * 34 + 40,
    marginLeft: width < 500 ? 132 : 150,
    marginTop: 30,
    style: plotStyle(),
    x: { type: "band", axis: "top", label: null, tickSize: 0, domain: years, tickFormat: (y) => (width < 500 && years.length > 3 ? `'${String(y).slice(2)}` : String(y)) },
    y: { label: null, tickSize: 0, domain: regions.map(titleCase) },
    marks: [
      Plot.cell(cells, { x: "year", y: "region", fill: (d) => (d.n ? color(d.n) : css("--surface-2")), inset: 1, rx: 4 }),
      Plot.text(cells, { x: "year", y: "region", text: (d) => (d.n ? fmt(d.n) : "–"), fill: (d) => ink(d.n), fontSize: 12 }),
      Plot.tip(cells, Plot.pointer({ x: "year", y: "region", title: (d) => `${d.region} · ${d.year}\n${fmt(d.n)} ${t("u_catches")(d.n)}` })),
    ],
  });
  box.replaceChildren(plot);
}

function renderRows(rows) {
  const table = document.getElementById("t-rows");
  const sorted = rows.slice().sort((a, b) => (a.date < b.date ? 1 : a.date > b.date ? -1 : 0));
  const shown = sorted.slice(0, state.rowsShown);
  const head = el("tr");
  [["c_date", ""], ["c_boat", "num"], ["c_weight", "num"], ["c_region", ""], ["c_fao", ""]].forEach(([k, c]) => head.append(el("th", c ? { class: c } : {}, t(k))));
  const thead = el("thead");
  thead.append(head);
  const tbody = el("tbody");
  for (const d of shown) {
    const tr = el("tr");
    tr.append(
      el("td", {}, fmtDate(d.date)),
      el("td", { class: "num" }, String(d.boat)),
      el("td", { class: "num" }, fmt(d.kg, d.kg % 1 ? 1 : 0)),
      el("td", {}, titleCase(d.region)),
      el("td", {}, d.fao),
    );
    tbody.append(tr);
  }
  const caption = el("caption", {}, t("shown")(fmt(shown.length), fmt(rows.length)));
  caption.style.cssText = "caption-side: bottom; text-align: left; padding-top: 8px; font-size: 13px; color: var(--text-muted)";
  table.replaceChildren(caption, thead, tbody);

  const more = document.getElementById("more");
  more.hidden = shown.length >= rows.length;
  more.onclick = () => { state.rowsShown += ROWS_STEP * 2; renderRows(filtered()); };

  document.getElementById("download").onclick = () => {
    const csv = d3.csvFormat(
      sorted.map((d) => ({ identificativo_natante: d.boat, data_cattura: d.date, peso_kg: d.kg, regione: d.region, zona_FAO: d.fao })),
    );
    const a = el("a", { href: URL.createObjectURL(new Blob([csv], { type: "text/csv" })), download: "tonno-rosso-catture.csv" });
    document.body.append(a);
    a.click();
    a.remove();
  };
}

function render() {
  const rows = filtered();
  const status = document.getElementById("status");
  const content = document.getElementById("content");
  if (!rows.length) {
    status.textContent = t("empty");
    status.hidden = false;
    content.hidden = true;
    return;
  }
  status.hidden = true;
  content.hidden = false;
  const summary = summarizeYears(rows);
  renderTiles(rows);
  renderSeason(rows);
  renderYearBars(summary);
  renderYearTable(summary);
  renderRegions(rows);
  renderHist(rows);
  renderHeat(rows);
  renderRows(rows);
}

async function main() {
  const saved = store.get("lang");
  state.lang = saved === "it" || saved === "en" ? saved : navigator.language?.startsWith("it") ? "it" : "en";
  applyI18n();

  document.querySelectorAll(".lang button").forEach((b) =>
    b.addEventListener("click", () => {
      state.lang = b.dataset.lang;
      store.set("lang", state.lang);
      applyI18n();
      if (DATA.length) { buildFilters(); render(); }
    }),
  );

  try {
    await load();
  } catch (e) {
    document.getElementById("status").textContent = t("error");
    console.error(e);
    return;
  }
  buildFilters();
  render();

  // ridisegna quando cambia la larghezza o il tema chiaro/scuro
  let lastWidth = document.querySelector("main").clientWidth;
  new ResizeObserver(() => {
    const w = document.querySelector("main").clientWidth;
    if (w !== lastWidth) { lastWidth = w; render(); }
  }).observe(document.querySelector("main"));
  matchMedia("(prefers-color-scheme: dark)").addEventListener("change", () => { buildFilters(); render(); });
}

main();
