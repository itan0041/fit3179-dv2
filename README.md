# Grow Where You Are

**Malaysia's gardening decade, 2014–2026.** An interactive single-page data visualisation built
with Vega-Lite for FIT3179 Data Visualisation 2, Monash University Malaysia.

**Live page:** _(add your GitHub Pages URL here once published)_
**Sketch:** [`sketch/sketch.pdf`](sketch/sketch.pdf)
**Author:** Isaac Yeak Sern Tan · October 2026

---

## The question

In 2020 Malaysians searched for ways to grow food at home like never before. Did anything on the
ground actually change?

Three independent sources are read against each other to answer it: monthly search interest,
eleven years of state-level crop records, and a 25-year rainfall climatology. The short answer is
that the attention and the acreage moved on completely different rhythms — the search boom faded
below its 2014 level, while commercial vegetable land quietly reached an eleven-year high in 2024.

## Data sources

| Source | What it provides | Period | Retrieved |
|---|---|---|---|
| [Crop Area and Production by State](https://data.gov.my/data-catalogue/crops_state) — MAFS, DOA & DOSM via data.gov.my | Planted area and production for nine crop categories, by state | 2014–2024 | 12 Oct 2026 |
| [Population Table: States](https://data.gov.my/data-catalogue/population_state) — DOSM via data.gov.my | State population, used for per-capita measures | 1970–2026 | 12 Oct 2026 |
| [Google Trends](https://trends.google.com/trends/) | Monthly relative search interest, Malaysia and worldwide | Jan 2014 – Sep 2026 | 12 Oct 2026 |
| [NASA POWER](https://power.larc.nasa.gov/) | Monthly rainfall, temperature and solar climatology at each state capital | 2001–2025 | 12 Oct 2026 |
| [DOSM open geodata](https://github.com/dosm-malaysia/data-open) | Official boundaries for all 16 states and federal territories | — | 12 Oct 2026 |

Raw downloads are kept unmodified in [`data/source/`](data/source/) so every published figure can
be traced back to its origin.

## Three corrections made to the source data

These are documented in the page footer as well, because they change what the charts can honestly
claim.

1. **Flower production is not measured in tonnes.** The portal describes every production figure as
   metric tonnes, but the flower series reports values in the hundreds of millions — stem counts,
   not weight. Flower production is set to null throughout; flower *area*, in hectares, is reliable
   and is used.
2. **Coconut is a subset of industrial crops.** The published methodology files coconut under
   industrial crops, so the nine categories overlap and must never be summed. All totals use a
   non-overlapping "edible garden" grouping: vegetables, fruits, herbs, spices and cash crops.
3. **NASA POWER works on a half-degree grid**, so Kuala Lumpur and Putrajaya fall in the same cell
   and return identical climate readings.

Two further cautions apply to the search data. Google Trends reports a relative index, not a count
of searches, and each query set is normalised independently. 2026 covers January to September only,
so wherever years are compared, every year uses January to September.

## Charts

Fourteen charts, four of them maps. Every specification is a readable JSON file in
[`specs/`](specs/).

| # | Idiom | Question it answers |
|---|---|---|
| 1 | Multi-line chart | How did interest in four gardening terms move, month by month? |
| 2 | Slope graph | Which crop categories gained or lost land over the decade? |
| 3 | Bump chart | How did the categories rank against each other, year by year? |
| 4 | Indexed line chart | Did vegetable area and production recover together? |
| 5 | **Choropleth map** | Where is there vegetable land per head of population? |
| 6 | **Proportional symbol map** | Where is the raw tonnage produced? |
| 7 | **Bivariate choropleth map** | Where do searching and growing agree, and where not? |
| 8 | **Spike map** | Which states gained and lost vegetable land since 2014? |
| 9 | Dumbbell chart | Where did each state start and finish? |
| 10 | Waffle chart | How concentrated is national vegetable land? |
| 11 | Heatmap | How does rainfall vary by state and month? |
| 12 | Radial chart (custom-built) | How does Malaysia's gardening year differ from the world's? |
| 13 | Dual-axis chart | Does interest track the rain? |
| 14 | Interval chart | When is each state's driest planting window? |

**Custom-built element.** Vega-Lite has no polar line mark, so the radial chart (12) is drawn from
polar coordinates computed in Python (`tools/build_derived.py`) and rendered as Cartesian line,
rule and text layers, including hand-built grid rings, spokes and ring labels.

**Cartography.** Malaysia straddles the South China Sea, so a single fitted frame wastes about half
its canvas on open water. Each map is therefore drawn as two panels — Peninsular Malaysia and
Malaysian Borneo — pinned to the *same* Mercator scale and explicit pixel translations, so a
hectare covers the same number of pixels in both panels. Mercator is appropriate here because the
whole country lies within eight degrees of the equator, where its area distortion is negligible.

## Repository layout

```
index.html              the page
css/style.css           layout, type scale and colour tokens
css/fonts/              Fraunces and Inter, self-hosted as variable WOFF2
js/app.js               loads each spec and applies the shared Vega-Lite theme
js/vendor/              Vega 6, Vega-Lite 6 and vega-embed, self-hosted
specs/*.json            one human-readable Vega-Lite specification per chart
data/*.csv|json         tidy, chart-ready data
data/source/            unmodified raw downloads
tools/                  the build pipeline (see below)
sketch/sketch.pdf       the hand-drawn sketch
```

Nothing is loaded from a CDN. The fonts and the Vega libraries ship with the page, so it renders
identically offline and does not depend on a third-party host staying up.

## Rebuilding the data

```bash
python3 tools/build_data.py      # tidy the raw sources into chart-ready tables
node    tools/make_topojson.mjs  # simplify DOSM boundaries into compact TopoJSON
python3 tools/build_derived.py   # centroids, bivariate classes, waffle, polar coordinates
python3 tools/build_specs.py     # write every Vega-Lite specification
node    tools/validate_specs.mjs # compile every spec and fail on errors
node    tools/render_specs.mjs   # render every spec to SVG for visual checking
```

## Running locally

The page fetches its data with `fetch()`, which browsers block over `file://`. Serve it over HTTP:

```bash
python3 -m http.server 8000
# then open http://localhost:8000
```

## Use of generative artificial intelligence

Anthropic's Claude was used to assist with locating and retrieving the source datasets, writing the
Python data-preparation scripts and the Vega-Lite specifications, drafting and editing the
narrative text, and reviewing the page layout. All data is unmodified public data from the sources
listed above. The analysis, interpretation and final design decisions are the author's own.

## Licence

Text and figures are released under
[Creative Commons Attribution 4.0](https://creativecommons.org/licenses/by/4.0/). The underlying
data remains subject to the terms of its original publishers.
