// Dashboard tonno rosso: tutto il calcolo avviene nel browser a partire dal CSV.

const CSV_URL = "pescaTonnoRosso.csv";
const FIRST_YEAR = 2021;
const ROWS_STEP = 50;

// testi della lingua della pagina, scritti nell'HTML da build.py
const I18N = JSON.parse(document.getElementById("i18n").textContent);

const state = { lang: document.documentElement.lang, years: new Set(), region: "", fao: "", rowsShown: ROWS_STEP };
let DATA = [];
let YEARS = [];

// ---------- utilità ----------

const t = (k) => I18N[k];
const plural = (k, n) => (n === 1 ? I18N[k].one : I18N[k].other).replace("{n}", n);
const locale = () => I18N.locale;
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
    { label: t("t_catches"), value: fmt(rows.length), sub: plural("t_catches_sub", years), hero: true },
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
    [fmtDay(d.day), ...d.values.slice().sort((a, b) => b[1] - a[1]).map(([y, v]) => `${y}   ${fmt(v)} ${plural("u_catches", v)}`)].join("\n");

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
    { id: "c-years-count", value: (d) => d.n, label: (d) => fmt(d.n), tip: (d) => `${d.year}\n${fmt(d.n)} ${plural("u_catches", d.n)}` },
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
      Plot.tip(data, Plot.pointerY({ y: "name", x: "n", title: (d) => `${d.name}\n${fmt(d.n)} ${plural("u_catches", d.n)}\n${fmt(d.kg)} ${t("u_kg")}` })),
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
        return `${fmt(lo)}–${fmt(lo + 5)} ${t("u_kg")}\n${fmt(v.length)} ${plural("u_catches", v.length)}`;
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
      Plot.tip(cells, Plot.pointer({ x: "year", y: "region", title: (d) => `${d.region} · ${d.year}\n${fmt(d.n)} ${plural("u_catches", d.n)}` })),
    ],
  });
  box.replaceChildren(plot);

  // scala dei colori: in tema scuro va dal più scuro al più chiaro, quindi va sempre mostrata
  const legend = document.getElementById("heat-legend");
  const bar = el("span", { class: "scale-bar" });
  bar.style.background = `linear-gradient(to right, ${d3.range(0, 1.01, 0.25).map((k) => color(1 + k * (maxN - 1))).join(", ")})`;
  legend.replaceChildren(el("span", {}, fmt(1)), bar, el("span", {}, `${fmt(maxN)} ${plural("u_catches", maxN)}`));
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
  const caption = el("caption", {}, t("shown").replace("{a}", fmt(shown.length)).replace("{b}", fmt(rows.length)));
  caption.style.cssText = "caption-side: bottom; text-align: left; padding-top: 8px; font-size: 13px; color: var(--text-muted)";
  table.replaceChildren(caption, thead, tbody);

  const more = document.getElementById("more");
  more.hidden = shown.length >= rows.length;
  more.onclick = () => { state.rowsShown += ROWS_STEP * 2; renderRows(filtered()); };

  document.getElementById("download").onclick = (e) => {
    e.preventDefault();
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
  try {
    await load();
  } catch (e) {
    const status = document.getElementById("status");
    status.textContent = t("error");
    status.hidden = false;
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
