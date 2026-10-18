# FIT3179 Data Visualisation 2 — handover

Paste this whole file into a new chat as the first message.

---

## 1. Who and what

- **Student:** Isaac Yeak Sern Tan, Monash University **Malaysia**. Student ID appears as `35387742`.
- **Unit:** FIT3179 Data Visualisation, **Assignment 2** (DV2). DV1 scored **18.9 / 25**.
- **Assigned topic:** *Gardening — explore popular plants, seasonal planting or home gardening participation. Compare plant categories on trends over time. Investigate how gardening has grown as a recreational activity.*
- **Audience:** the average Malaysian (Monash Malaysia campus).
- **Hard deadline:** **Sunday 25 October 2026, 11:55 PM.**
- **Deliverable:** a single scrolling Vega-Lite page published on GitHub Pages, plus a **hand-drawn** A4 sketch as a PDF in the repo.

## 2. Where everything lives — read this first

| Thing | Location | Notes |
|---|---|---|
| **Source of truth** | `C:\Users\User\Documents\FIT3179-DV2` | 63 files. Reachable in a linked session at `$HOME/mnt/Documents/FIT3179-DV2` |
| GitHub repo | https://github.com/itan0041/fit3179-dv2 | **Not a git clone locally** — there is no `.git`. Uploads are drag-and-drop through the GitHub web UI |
| Live page | https://itan0041.github.io/fit3179-dv2/ | GitHub Pages |
| Sketch PDF (missing) | must become `sketch/sketch.pdf` in the repo | folder currently holds only a README |

**The cloud container does not persist between chats.** A new session starts with an empty workspace. There is no `/home/claude/project`. To work on the page you must either edit directly in `$HOME/mnt/Documents/FIT3179-DV2` with `device_bash`, or stage files into the container, work, and commit back.

**GitHub may be behind the Documents folder.** Documents is always the newer copy. Diff before assuming.

## 3. Permissions and constraints in force

- **Granted:** read and write to `C:\Users\User\Documents` through the device bridge. Appending and editing files is fine without asking each time.
- **DENIED — do not delete anything on the user's machine.** The user explicitly refused the delete-permission request for the Documents folder, and later restated "do not do any deletion." Do not call `device_request_delete_permission` again. If something must go, move it into a `_to_delete/` subfolder and say so.
- The container's network is **allow-listed**. `curl` to `itan0041.github.io` or any ordinary website is **refused by the proxy**. Package registries and GitHub work. Do not retry a blocked host — say it's blocked. Never disable TLS or unset `HTTPS_PROXY`.
- `WebFetch` / `WebSearch` do reach the public web; the shell does not.
- The device link drops sometimes. When the `mcp__remote-devices__*` tools vanish, keep working in the container and deliver with `SendUserFile` instead.

## 4. What the page is

Single scrolling page, 1180px content column, six sections, **fourteen figures**. Self-hosted Vega 6 / Vega-Lite v6 / vega-embed 7.3.0 — no CDN. Fonts are local `@fontsource-variable` woff2 files.

**Colour is semantic and fixed page-wide:** green = growing / land / production · terracotta = attention / search interest · blue = rainfall / water.

| § | Section | Figures |
|---|---|---|
| One · The spike | The year everybody wanted to grow something | 1 multi-line chart |
| Two · The ground | Attention is not the same as acreage | 2 slope graph · 3 bump chart · 4 indexed line chart |
| Three · The map | Where Malaysia's vegetables actually grow | 5 choropleth · 6 proportional symbol |
| Four · The mismatch | Searching for a garden, and having one, are different maps | 7 bivariate choropleth (+ 7b key) |
| Five · The shift | The growth went east. The losses went where the people are. | 8 spike map · 9 dumbbell ‖ 10 waffle |
| Six · The calendar | No spring, no autumn — here, the rain sets the calendar | 11 heatmap · 12 radial ‖ 13 dual-axis · 14 interval |

Only two rows are split two-up: 9+10 and 12+13. Everything else is full width.

**Advanced idioms: 12 of 14. The rubric needs 8.** There are four to spare, so simplifying a chart for clarity is affordable — this has already paid off twice.

Data sources: DOSM / MAFS / DOA crop area and production (data.gov.my), Google Trends, NASA POWER climatology.

## 5. State as of 18 October 2026

Everything below is **written to Documents and verified**. Whether it is on GitHub depends on whether the user has uploaded since.

Recent work, newest first:

- **Word cuts.** Figure notes went 600 → 474 words (−21%). The sentence *"Peninsular Malaysia and Borneo are drawn as two panels at the same map scale…"* had been repeated **verbatim four times** on Figures 5–8; it now appears once, on Figure 5. "Hover a line to pick it out" appeared three times; now once, on Figure 1. Page total is 2,124 words (1,728 excluding the footer).
- **Byline rule fixed.** The masthead's `border-top` was being clipped at the global 64ch measure, so the title block had no bottom edge above a full-width KPI grid. `.byline { max-width: none }`.
- **White space.** Every chart now fills **98–100%** of its panel, measured in a real browser. The big wins were axis domains drawn far past the data: Figure 1 ran to 100 when nothing passed 70 (now `[0, 75]`); Figure 4 had a hard `padding.right: 170` sitting on top of the space autosize already reserved for its end labels.
- **Section headers restructured.** Headline and subtitle run full width at the top; body text sits below in two balanced columns. This replaced a two-column layout with the headline on the left.
- **Figure 11 legend.** Six threshold breaks were rendering **one pixel apart**. Cut to four (`[150, 200, 250, 325]`, five colours).
- **MCO rule on Figure 1 was never drawing.** The annotation text was visible, the dashed vertical line it referred to was not.
- **Figure 4 was a connected scatterplot and the narrative under it was factually wrong.** It claimed 2024 had "more land and more tonnes than 2014". Production 2024 = 1,340,110 t against 2014's 1,452,846 t — **8 per cent BELOW**. Replaced with an indexed line chart (2014 = 100) with the gap tinted, which makes the divergence the point. The corrected callout is live.

### Open question the user has not answered

**Should the masthead title and subtitle be centred?** A peer suggested it. I rendered both and recommended **against**: the page has one left sight-line running all 13,296px, and centring breaks it at the top above a KPI grid pinned to both margins. The user has not replied. It is ~5 lines of CSS either way.

## 6. Outstanding work

1. **Hand-draw the A4 sketch** → scan → `sketch/sketch.pdf` → repo. **Rubric: 0 marks if made digitally; −3% if it doesn't match the page.** `SKETCH_BLUEPRINT.md` in the repo was rewritten on 17 Oct from the finished `index.html`, section for section. Draw from that file, not from memory.
2. **Upload the current Documents folder to GitHub** if not already done. `Ctrl+A` in the folder → drag onto the GitHub upload page → commit. Same-named files overwrite. **Then wait ten minutes** — GitHub Pages serves `max-age=600` and the user has twice thought a fix "didn't work" when it was just cached. Hard-refresh with `Ctrl+Shift+R`.
3. **Delete two dead files on GitHub:** `specs/01_search_ridgeline.json` and `specs/04_vegetable_connected_scatter.json`. Nothing references either. The user must do this themselves (trash icon on each file) — deletion on their machine is not permitted.
4. **Paste two URLs into `SUBMISSION.md`**: the Pages link and the GitHub link to `sketch/sketch.pdf`.
5. **AI-use acknowledgement** — the unit requires it on the submission. A stub exists in the footer; confirm it says what the unit asks for.

### Offered but never actioned

- "Industrial crops" is slate-blue in Figures 2 and 3, while blue means rainfall in Figures 11, 13 and 14. One colour, two meanings — this is the DV1 criticism in miniature. Worth 10 minutes.
- Standardise legend positions across figures.
- The DV1 marker specifically asked for an annotation on the waffle chart.

## 7. Technical landmines already hit — do not rediscover these

**Verification in a browser.** Playwright's CDN is blocked but **Chromium is pre-installed**. Check `ls /opt/pw-browsers` for the build number, then:

```js
chromium.launch({ executablePath: '/opt/pw-browsers/chromium-<N>/chrome-linux/chrome',
                  args: ['--no-sandbox'] })
```

Serve the folder with a tiny Node `http.createServer` (send `Cache-Control: no-store` or Chromium caches the spec JSONs) and measure with `getBoundingClientRect()`. **Parsing SVG `x`/`y` attributes is useless — Vega positions text with `transform`.** A whole afternoon went into that mistake.

Available space, measured: **1070px** for a full-width chart, **494px** per column in a two-up row. `.chart` has `overflow-x: auto`, so an oversized chart scrolls inside its panel rather than breaking the page.

**When hover-testing, `scrollIntoView` first.** Playwright's `mouse.move` uses viewport coordinates; a chart 2,000px down the page silently receives nothing and looks broken when it isn't.

**Vega-Lite gotchas banked so far:**

- A layer with its own inline `data` still inherits the top-level `encoding`. If the top level has `y: {field: 'smooth'}` and your one-row annotation has no `smooth` field, the mark **renders nothing, silently**. Set `'y': None` or give it a real field, and add `'transform': []` to block the top-level transform.
- A `point` selection param declared at the top level of a **layered** spec is instantiated once per layer → `Duplicate signal name: "hover_tuple"`. Put it on exactly one layer.
- `dy` is a **mark** property, not an encoding channel. Vega-Lite drops it with a warning you will miss.
- Vega-Lite **discards `gradientLength`** on a `threshold` scale — it draws a fixed ~200px banded key instead. `columnPadding` does nothing there either. The only lever is fewer breaks.
- `latitude2` without `longitude2` renders nothing.
- Inside an `hconcat`, the default `translate: [width/2, height/2]` resolves against the wrong view and clips the map. **Write the projection translate out in explicit pixels.** Both map panels share `MAP_SCALE = 3777` so a hectare covers the same pixels in Peninsular Malaysia and Borneo.
- Parse CSV numerics explicitly (`'k': 'number'`). A numeric column read as text sorts "0, 1, 10, 11" and turned the radial chart's rings into a starburst.
- `vega-embed` emits an empty `.vega-bindings` div for **every** chart. `.vega-bindings:empty { display: none }` or you get a row of grey pills.

**Rebuild pipeline.** Specs are generated, never hand-edited:

```
python3 tools/build_data.py     # raw -> tidy CSVs in data/
python3 tools/build_specs.py    # -> all 15 JSONs in specs/
node tools/render_specs.mjs     # -> qa/*.svg for headless inspection
node tools/validate_specs.mjs
```

Edit `tools/build_specs.py`, never `specs/*.json` — the next build overwrites them.

## 8. How the user wants to be worked with

- **Push back.** Start from doubt, not agreement. Lead with what's broken. No "great question", no flattery. Conclusion in the first sentence.
- **But** when they ask for help with a task, just do it — don't argue the task itself. Test them when they state an understanding or make a suggestion.
- **Don't rush them when they're clarifying.** They often think out loud across several messages.
- **Their mother is the comprehension test, and she has been right twice.** She flagged Figure 1 as overcomplicated (it was a ridgeline — replaced with a plain multi-line chart) and then questioned the connected scatterplot (which turned out to be hiding a factual error). When a chart needs explaining, simplify it. There are four spare advanced idioms to pay for it.
- They are not a developer. Give exact click-by-click steps for anything touching GitHub.
