# FIT3179 Data Visualisation 2 — Submission Notes

**Student:** Isaac Yeak Sern Tan
**Title:** Grow Where You Are — Malaysia's gardening decade
**Visualisation URL:** _(paste your GitHub Pages URL)_
**Sketch PDF URL:** _(paste the raw/blob URL of `sketch/sketch.pdf` in your repository)_
**Date:** October 2026

---

## 1. Domain, why and who

**Domain.** Gardening in Malaysia, approached through three angles the topic brief names: popular
plant categories, seasonal planting, and gardening as a recreational activity.

**Why.** Malaysians were told, repeatedly during the pandemic, that growing food at home was a
national good. Six years later nobody has checked what happened. The question matters beyond
nostalgia: Selangor and Kuala Lumpur hold 27.8 per cent of the country's population but 3.0 per
cent of its vegetable land, and Selangor alone gave up 55 per cent of that land in a decade. The
people with the least access to farmland are exactly the people living where farmland is
disappearing fastest. A reader deciding whether to start a balcony garden also faces a practical
obstacle: almost every gardening guide online is written for a four-season country, and none of its
timing advice applies here.

The visualisation answers three questions a general reader can act on: did the gardening boom last,
where does Malaysia's food actually grow, and when should I plant?

**Who.** A general Malaysian adult with no statistical training. The page assumes familiarity with
Malaysian state names and the monsoon, and nothing else. Search-interest indices and the
"2014 = 100" index are both explained in plain words where they first appear. No chart requires an
understanding of variance, significance or confidence.

---

## 2. What — the data

| Dataset | Author / publisher | Period | Role in the page |
|---|---|---|---|
| Crop Area and Production by State | Ministry of Agriculture and Food Security, Department of Agriculture, and Department of Statistics Malaysia, via data.gov.my | 2014–2024, updated 11 Oct 2026 | Planted area and production for nine crop categories by state. The backbone: figures 2–10. |
| Population Table: States | Department of Statistics Malaysia, via data.gov.my | 1970–2026 | Denominator for every per-capita measure. |
| Google Trends | Google | Jan 2014 – Sep 2026 | Search interest in Malaysia and worldwide: figures 1, 7, 12, 13. |
| NASA POWER climatology | NASA Langley Research Center | 2001–2025 | Monthly rainfall and temperature at each state capital: figures 11, 13, 14. |
| State boundary geodata | Department of Statistics Malaysia | — | Base geometry for all four maps. |

**Two independent sources are combined throughout**, and in several places three: figure 5 joins
crop records to population; figure 7 joins crop records, population and Google Trends; figure 13
joins Google Trends to NASA climatology.

**Creation process.** Crop and population data were taken from data.gov.my's published CSV and API.
Search data was retrieved from Google Trends for four Malaysian-language and English terms. Climate
data was requested from the NASA POWER climatology endpoint at the coordinates of each of the 16
state capitals. Raw downloads are preserved unmodified in `data/source/`. A short Python pipeline
(`tools/`) reshapes them into tidy, chart-ready tables; the boundary file is simplified to compact
TopoJSON with the `topojson` toolchain. No value was edited by hand.

**Join keys.** The three sources align cleanly because DOSM's `code_state` (1–16) matches Google
Trends' ISO subdivision codes (MY-01 to MY-16) exactly, and DOSM's state names match the crop file
exactly.

**Three corrections, and why they matter.** These were found by checking the data against its own
documentation rather than trusting the field descriptions:

1. The portal describes all production as metric tonnes, but flower production is reported in the
   hundreds of millions — stem counts, not weight. Flower production is excluded from every
   tonnage chart; flower area in hectares is kept.
2. The published methodology files coconut *within* industrial crops, so the nine categories
   overlap. Summing all nine would double-count, so every total uses a non-overlapping edible
   grouping.
3. NASA POWER uses a half-degree grid, so Kuala Lumpur and Putrajaya return identical readings.

**Two limits stated on the page.** Google Trends reports a relative index, not search counts, and
each query set is normalised separately. The crop data counts commercial agricultural
establishments, not home gardens — so the page never claims to measure household gardening
directly, and treats the search data and the crop data as two different things rather than as cause
and effect.

---

## 3. How — idioms and rationale

Colour is semantic and fixed across the whole page: **green** always means growing, land or
production; **terracotta** always means attention or search interest; **blue** always means
rainfall. A reader who learns the scheme in section one can read section six without relearning it.

| # | Idiom | Why this idiom | Reader's task |
|---|---|---|---|
| 1 | Multi-line chart | Deliberately the simplest idiom on the page. An earlier ridgeline scaled each row to its own peak, which hid a five-fold difference in volume and tested poorly with a non-technical reader. One shared 0–100 scale is honest about relative volume and needs no explaining. | Compare the rise and fall of four terms at a glance |
| 2 | Slope graph | Reduces eleven years to the only comparison the section needs: where each category started and ended | See winners and losers in one read |
| 3 | Bump chart | Recovers the year-by-year movement the slope graph deliberately discards | Follow one category's fortunes over time |
| 4 | Indexed line chart | Two lines on one index (2014 = 100) with the gap between them tinted. Replaced a connected scatterplot: the loop shape made the path legible but buried the finding, which is that the two measures have not recovered together. Planted area is back above its 2014 level and production is still 8 per cent below it. | Read the divergence directly |
| 5 | Choropleth map | Per-capita rates are a ratio, correctly encoded by colour over an area | Find states with land relative to population |
| 6 | Proportional symbol map | Raw tonnage is a magnitude, correctly encoded by area, not by shading | Judge absolute scale of output |
| 7 | Bivariate choropleth map | Two variables on one geography answers the mismatch question directly, instead of asking the reader to hold two maps in memory | Spot where interest and growing diverge |
| 8 | Spike map | Signed change reads naturally as direction and length; a diverging choropleth would hide magnitude in small states | Compare gains and losses geographically |
| 9 | Dumbbell chart | Gives the spike map's values an exact, sortable reading | Read precise start and end values |
| 10 | Waffle chart | Makes "a third of the country's vegetables" a countable quantity rather than an abstract percentage | Grasp concentration intuitively |
| 11 | Heatmap | 16 states × 12 months is a dense matrix; colour is the only encoding that fits it on one screen | Find any state's wet and dry months |
| 12 | Radial chart | A year is a cycle, and a cyclical layout makes December adjacent to January, which a linear axis cannot | Compare two seasonal shapes |
| 13 | Dual-axis chart | Puts two differently scaled quantities against the same months to test one specific claim | Check whether interest tracks rain |
| 14 | Interval chart | A planting window is a span, not a magnitude, so it is encoded as an interval | Find their own state's window |

**Interactivity.** Every chart carries informative tooltips giving the underlying values and units.
The slope graph (2) has a radio control switching between planted area and production, letting the
reader test whether land and output tell the same story. Interactivity is not added where it would
not earn its place.

**Special features and custom-built elements.**

- **The radial chart is built from scratch.** Vega-Lite has no polar line mark, so polar
  coordinates, grid rings, spokes and ring labels are computed in Python and rendered as Cartesian
  line, rule and text layers.
- **Two-panel cartography at a shared scale.** Malaysia spans the South China Sea, so a single
  fitted frame wastes half its canvas and shrinks the peninsular states past legibility. Each map
  is split into Peninsular Malaysia and Malaysian Borneo, both pinned to the same Mercator scale
  with explicit pixel translations, so areas remain comparable between panels. Mercator is
  appropriate because the entire country lies within eight degrees of the equator.
- **A bivariate colour key** built as its own small Vega-Lite specification, with a 3 × 3 matrix
  classified by tertiles on each axis.
- **Self-hosted rendering.** The Vega libraries and both typefaces ship with the page; nothing
  loads from a CDN, so the page renders identically offline.
- **A reproducible pipeline.** Five scripts rebuild every data file and every specification from
  the unmodified raw downloads, and a validation script compiles all 14 specifications and fails on
  any error.

**Design decisions addressing feedback on Data Visualisation 1.** Colour is now semantic and never
reused for a different attribute between charts; charts are sized larger; legend titles are written
out in full with no abbreviations; annotations are placed both inside the charts and in the prose
beside them; and the layout is a single 12-column grid so panel edges share vertical sight lines.

---

## 4. Acknowledgement of generative AI

Anthropic's Claude was used to assist with locating and retrieving the source datasets, writing the
Python data-preparation scripts and the Vega-Lite specifications, drafting and editing the narrative
text, and reviewing the page layout. All data is unmodified public data from the sources listed
above. The analysis, interpretation and final design decisions are my own.
