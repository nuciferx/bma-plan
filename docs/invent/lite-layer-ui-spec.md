# Layer panel design-system spec for lite (sandbox-anchored)

**Idea ID:** `2026-05-23-11-15`
**Pipeline:** `/lite-invent`
**Started:** 2026-05-23
**Status:** invent-in-progress (Phase 3 FRAME complete; Phase 4 DIVERGE pending)
**Linked:** `2026-05-23-11-16` (CALIBRATE phase angle, absorbed)

---

## Phase 1 — PICK (done)

User picked `2026-05-23-11-15` and narrowed scope from "lite design-system spec (whole UI)" to "**layer panel only**, calibrate live `lite/ui-lite.html` against an existing sandbox spike".

User-supplied anchor (via Drive link 2026-05-23, MD5-equivalent to repo copy): **`lite/sandbox/invent-layer-dnd.html`** — the LDND drag-and-drop spike (Approach A + D, shipped to live as LDND-S1..S4 on 2026-05-23 in the same day, but with stripped-down CSS).

## Phase 2 — RESEARCH (done, verdict `PRIOR_ART_PARTIAL`)

`bma-researcher` (haiku) returned a 5-section report. Key conclusions:

- **UX pattern** (tree + drag-to-nest) is `PRIOR_ART_MATURE` — Figma/Photoshop lineage, well-established.
- **Design tokens / CSS custom properties** approach is `PRIOR_ART_MATURE` — W3C Design Tokens 2025.10 stable; lite already uses `:root { --var }`.
- **No off-the-shelf library** fits lite's no-build / no-bundler / no-framework constraint. Open Props could be CDN'd but adds dependency for marginal value over hand-rolled tokens.
- **GREENFIELD slice** that remains: the specific visual calibration of live lite → DnD spike, the safe merge workflow, and ongoing token discipline.

Researcher's recommendation: process-based (W3C-format token sheet + diff script + manual merge) over library import. Inline tokens in `:root` of `ui-lite.html`; optionally extract to `lite/static/css/design-tokens.css` if size cap requires.

Full report cached in conversation; not duplicated here.

## Phase 3 — FRAME (this section)

### Problem statement

The user is unsatisfied with the live lite layer panel's visual quality ("ยังไม่ถูกใจ ui"). The DnD spike (built during LDND invention pass, 2026-05-23) demonstrates a more polished aesthetic with stricter visual rhythm and richer affordances, but its CSS lives only in `lite/sandbox/invent-layer-dnd.html` and was not carried over when LDND shipped to `lite/ui-lite.html`. The result: live lite layer panel works functionally (drag-and-drop, sublayer tree, report variables all shipped this week) but looks visually cramped and unfinished compared to its own sandbox prototype.

This invention pass produces a **design-system spec** (token sheet + component rules) that converts the DnD spike's aesthetic into a portable set of CSS custom properties, plus a calibration plan to apply that spec to the live layer panel without breaking any of the shipped LDND/LST/LRV behavior.

### Visual gap table (anchor vs live)

| Property | Anchor (DnD spike) | Live (`ui-lite.html`) | Gap |
|---|---|---|---|
| `--bg` | `#1e1f23` (warm near-black) | `#0f1115` (cool near-black) | warmer hue +slight value |
| `--panel` | `#26282d` (warm dark gray) | `#161a22` (cool dark gray) | warmer hue |
| `--row` (chip bg) | `#2d3036` | — (no row-chip token) | NEW token needed |
| `--row-hover` | `#343841` | — (no token, css selector) | NEW token needed |
| `--row-active` | `#3a4150` | — (no token, css selector) | NEW token needed |
| `--line` (accent) | `#4aa3ff` | `#4c8dff` | near-equal (Δ ≤ 2 in each channel) |
| `--nest` (drop-into) | `#3b5b3b` (muted green inset) | — | NEW token (DnD affordance) |
| `--group` (auto-group) | `#2f6b3f` (darker green) | — | NEW token (DnD affordance) |
| `--txt` | `#e6e8ec` | `#e7ecf3` | near-equal |
| `--muted` | `#8b909a` | `#8b97a8` | near-equal |
| `--border` | `#3a3d44` | `#2a3140` | warmer, slightly lighter |
| panel width | 320px (fixed) | 190px (fixed in `#picker`) | +130px (significant) |
| row height | 30px (fixed scalar rhythm) | content-driven | NEW rule needed |
| row padding | `0 6px` | `6px 8px` (variable) | tighter horizontal, no vertical |
| row margin | `2px 0` | none | NEW (visual gap between rows) |
| row border-radius | `5px` | none (flat) | NEW (chip look) |
| indent step | `16px` per depth via `marginLeft` | 0 (flat list in current live) | NEW (hierarchical visual) |
| grip affordance | `⠿` 14px wide, `--muted` color | absent | NEW (DnD discovery cue) |
| color swatch | 14×14px, 3px border-radius, `1px solid #0006` | 12×12px, 3px border-radius | scale up +2px |
| eye / lock / del | 20px width, 12px font, opacity 0.85→1 hover | 10–18px mixed, smaller font | normalize to 20px chip |
| folder icon | 📂 / 📁 emoji per collapsed state | none | NEW (folder rows visually distinct) |
| collapse toggle | 13px `▸` / `▾` | small `▾` | size to 13px, consistent |
| panel border-radius | 8px (outer container) | none | NEW |
| panel border | `1px solid var(--border)` | none on `#picker` outer | NEW |

### Constraints

**Lite size caps (hard):**
- `lite/ui-lite.html` ≤ 1200 lines (currently **1138/1200** as of 2026-05-23 — only **62 lines** of headroom)
- `lite/static/js/*.js` ≤ 1000 lines each (`layer-panel.js`, `layer-tree.js`, `layer-dnd.js`, `layer-system.js` all need to fit)
- `lite/static/css/*.css` no formal cap, but new files preferred over bloating `ui-lite.html`

**Implication:** Most of the new CSS (estimated ~80–120 lines of selectors + ~30 lines of `:root` token block) cannot live in `ui-lite.html`. It must go in a new `lite/static/css/layer-panel.css` or `lite/static/css/design-tokens.css`.

**Vendoring contract (immutable):**
- Measure math is copied verbatim from `proto/ui.html`; drift-locked by `lite/tests/test_measure_parity.py`
- NO approach in this pass may touch measure math, RS, pdfToC/cToPdf, semanticTag derivation, `.bmaplan` rename
- Pure CSS / DOM-class changes only

**Behavioral preservation:**
- All LDND drag-and-drop ops (S1 grip drag, S3 auto-group-on-collision) MUST continue to work
- All LST tree ops (folder expand/collapse, indent, roll-up Σ) MUST continue to work
- All LRV report variable composer ops MUST continue to work
- Keyboard fallback (`Shift+↑/↓`, `→/←` per LDND-S2) MUST continue to work

### Forbidden surfaces

| Surface | Status |
|---|---|
| `lite/static/js/measure-engine.js` (vendored, drift-locked) | **DO NOT TOUCH** |
| `RS`, `pdfToC`, `cToPdf`, area math, semanticTag | **DO NOT TOUCH** |
| `.bmaplan` schema field rename | **DO NOT TOUCH** (additive new tokens are not schema) |
| `lite/server_lite.py` | **NO CHANGE NEEDED** (CSS-only feature) |
| `lite/lite-report.html` | **NO CHANGE** (out of scope: layer panel only) |
| `proto/ui.html`, `proto/server.py`, `proto/static/*` | **OUT OF SCOPE** (lite-only idea) |

### Success criteria

A future `/bma-lite-dev` integration sprint succeeds if, after merge:

1. **Visual parity check (manual eyeball):** live `lite/ui-lite.html` layer panel, when opened in browser, looks visually equivalent to `lite/sandbox/invent-layer-dnd.html` on at least: panel width, row rhythm, color palette, grip/swatch/folder affordances.
2. **Behavioral regression check (automated):** `lite/tests/test_measure_parity.py` GREEN, `LITE_LDND_OK` GREEN, `LITE_LST_OK` GREEN, `LITE_LRV_OK` GREEN — all shipped tests pass without modification.
3. **Size-cap check:** `wc -l lite/ui-lite.html` < 1200; new CSS file (if created) < 1000 lines; no `.js` module exceeds 1000 lines.
4. **Token discipline check:** all new layer-panel CSS rules reference variables from `:root` or `lite/static/css/design-tokens.css` — no hard-coded color literals in selector bodies (manual grep).
5. **Cross-browser sanity:** opens in Chromium and Firefox without console errors; layer panel renders identically (modulo platform font hinting).

### Out of scope (explicit non-goals for this pass)

- Redesign of canvas, summary widget, status bar, modal dialogs, ribbon, menu bar
- Redesign of `lite-report.html`
- Touching proto in any way
- Changing measurement behavior, snap, or geometry
- Light-mode theme (lite is dark-only by design)
- Right-to-left layout
- Color-blind / accessibility audit (future sprint; track separately)
- Per-page-tab visual customization

### Open questions for Phase 4 DIVERGE (`bma-inventor`)

The translation/calibration strategy is not yet decided. Inventor must propose approaches across these axes:

1. **Token housing axis** — where do the new tokens live?
   - Inline in `ui-lite.html` `:root { --var }` (adds ~30 lines to ui-lite — risky given 62-line headroom)
   - New `lite/static/css/design-tokens.css` (clean, no headroom risk, but +1 file)
   - New `lite/static/css/layer-panel.css` (tokens + selectors together)

2. **Width strategy axis** — anchor uses 320px panel, live uses 190px `#picker`
   - Force 320px globally (changes layout — affects canvas width)
   - Keep 190px but tighten internal density (deviate from anchor's spacing rhythm)
   - Make it user-resizable / collapsible (new feature creep — out of scope?)

3. **Merge approach axis** — how to migrate live to new tokens
   - One-shot CSS replacement (high risk, single sprint, decisive)
   - Progressive (LCAL-S1 = colors only, LCAL-S2 = spacing, LCAL-S3 = affordances, LCAL-S4 = final cleanup)
   - Behind a feature flag (toggle: classic / new) — adds complexity, ~80% of the work, helpful for A/B comparison during review

4. **Affordance fidelity axis** — how closely to copy the DnD spike's affordances
   - 1:1 visual copy (grip + folder emoji + 14px swatch + 20px chip icons)
   - Tweaked subset (e.g., skip folder emoji, keep grip + larger swatch)
   - Minimal (just color/spacing rhythm; keep current icons as-is)

5. **Scope axis** — layer panel only, or also adjacent components that share visual idiom?
   - Strict: only `#picker` and its descendants
   - Broaden to: `#picker` + the right-side Σ overlay (which already shares color tokens via LRV)
   - Broaden to: all left-sidebar UI on the lite app

Inventor MUST produce at least 3 approaches that differ on at least 2 of these 5 axes each. Variants of the same axis (e.g., "320px vs 280px" both Width-strategy A) do not count as different.

---

## Phase 4 — DIVERGE (done — `bma-inventor` returned 5 approaches)

5 approaches differing across the 5 declared axes (token housing / width / merge / fidelity / scope):

| # | Approach | Token housing | Width | Merge | Fidelity | Scope |
|---|---|---|---|---|---|---|
| A | Inline one-shot | `:root` in `ui-lite.html` | force 320px | one-shot | 1:1 | `#picker` |
| B | Dedicated `layer-panel.css` | new `layer-panel.css` | 190px density-tight | one-shot extract | subset | `#picker` |
| C | Progressive LCAL-S1..S4 | split inline + new file | resize 190–380 | 4 sub-sprints | graduated | `#picker` + autogroup-bar |
| D | Feature-flag `body.lt-v2` | new `design-tokens.css` + `layer-panel.css` | force 320 under flag | flagged toggle | 1:1 under flag | `#picker` + `#sum` |
| E | Extract-and-supersede | new `layer-panel.css` (consolidated) | 240px midpoint | extract + remove JS-inject | minimal | `#picker` + DnD overlays |

**Inventor surfaced a 13th visual gap missed in FRAME:** `--line` naming inversion — anchor uses `--line` as accent blue (`#4aa3ff`); live uses `--line` as separator gray (`#2a3140`). Approach D resolves by keeping live's naming and re-mapping values (no token rename = no breakage).

**Tech-debt finding:** CSS for layer panel is split between `<style>` in `ui-lite.html` AND JS-injected `<style id="lt-dnd-style">` in `layer-dnd.js`. Approaches B, C-S4, and E explicitly consolidate this; A and D do not.

## Phase 5 — SCORE (done — `bma-inventor` 6-dimension scoring)

| Approach | Nov | Acc | UX | Fit | Bdy | Cost | **Total** |
|----------|-----|-----|----|-----|-----|------|-----------|
| A inline one-shot | 1 | 3 | 3 | 4 | 5 | 5 | 21 |
| B layer-panel.css | 1 | 3 | 3 | 5 | 5 | 4 | 21 |
| C progressive 4-sprint | 1 | 4 | 4 | 5 | 5 | 2 | 21 |
| **D feature-flag toggle** | **2** | **4** | **5** | **4** | **5** | **3** | **23** |
| E extract-and-supersede | 1 | 3 | 3 | 5 | 5 | 3 | 20 |

**Inventor's recommendation:** D (top) — strength = UX=5 (real-time A/B in browser without deploy). Fallback = B (cleanest, no flag complexity). **User accepted D 2026-05-23.**

**Risk of D:** `body.lt-v2` specificity doubling — if `layer-dnd.js` JS-inject styles are unscoped, they override the flagged colors. Ship sprint must migrate or scope them.

## Phase 6 — SPIKE (done — `lite/sandbox/invent-layer-ui-spec.html`)

Built 2026-05-23. ~330 lines. Self-contained — no imports from `lite/static/js/*`.

**What it demonstrates:**
- Topbar with toggle button `Toggle v1 ⇄ v2` + live indicator of which palette is active
- `#picker` with v1 styles (matches current live: 190px, no chip, no border) when `body.lt-v2` absent
- `#picker` with v2 styles (matches anchor DnD spike: 320px, row-chip 5px radius, 30px rhythm, grip `⠿`, folder icon, 14×14 swatch, 20px chip icons) when `body.lt-v2` present
- Smooth CSS transitions (0.18–0.22s) so the toggle feels demonstrative
- Side annotation panel listing all token + layout changes between v1 and v2, plus the 3 inventor-identified risks
- Mock canvas to the right to show that 320px panel still leaves working area
- 6 mock layers (1 folder + 5 layers) using realistic Thai BMA-Plan names

**Open question for human at checkpoint:**
1. When toggle ON, does the panel look ≈ identical to `invent-layer-dnd.html`?
2. When toggle OFF, does the panel look ≈ identical to current `ui-lite.html`?
3. Is the toggle UX understandable enough for real-user A/B preview?
4. Does 320px width feel visually right against a canvas to its right?

## Phase 7 — CHECKPOINT (done — **GO** 2026-05-23)

**User decision:** GO. Verified by side-by-side screenshots (sandbox spike v1/v2 + live lite v1/v2 with real 45-page RAMA4 permit PDF rendered behind the picker).

**Key observation that drove GO:** v2 picker is *wider* (320 vs 190 px) but **shorter vertically** because Thai layer names no longer wrap to 2-3 lines per row. Net screen area: ~117k px² (v2) vs ~123k px² (v1) — v2 uses *less* total screen real estate while improving readability ~3×. The "wide panel eats canvas" worry was misplaced.

### Sprint plan (built via `/bma-lite-dev`, one reviewable slice each)

**LCAL-S1** — design-token housing
- New file `lite/static/css/design-tokens.css` (~30 lines): `body.lt-v2 { --bg, --panel, --line, --accent, --ink, --muted, --row, --row-hover, --row-active, --nest, --group }` block.
- `lite/ui-lite.html` +1 line: `<link rel="stylesheet" href="static/css/design-tokens.css">` in `<head>`.
- Test: `body.classList.add("lt-v2")` in devtools console → page bg shifts warm. Smoke test `LITE_*` markers stay GREEN.

**LCAL-S2** — layer-panel selectors
- New file `lite/static/css/layer-panel.css` (~80 lines): all `body.lt-v2 #picker`, `body.lt-v2 #picker .h`, `body.lt-v2 #lt-autogroup-bar`, `body.lt-v2 #catlist`, `body.lt-v2 .cat`, `body.lt-v2 .cat .sw`, `body.lt-v2 .cat .eye`, `body.lt-v2 .cat .nm`, `body.lt-v2 .lt-grip` selectors.
- `lite/ui-lite.html` +1 line: second `<link>` for `layer-panel.css`.
- Test: devtools `body.classList.add("lt-v2")` + `buildPicker()` → layer panel visually matches anchor. Visual parity against `lite/sandbox/invent-layer-ui-spec.html` v2 mode.

**LCAL-S3** — toggle button + JS
- `lite/ui-lite.html` +~6 net lines: add small toggle button to `#picker .h` (next to the existing `+` / `📁+` buttons), inline `onclick=document.body.classList.toggle('lt-v2');buildPicker();`. Persist to `localStorage["bmaPlan.lite.layerSkin"]` so user choice survives reload.
- Test: full lite test suite GREEN. `LITE_LDND_OK`, `LITE_LST_OK`, `LITE_LRV_OK`, `LITE_REPORT_OK`, `MEASURE_PARITY_OK` all stay GREEN. Cap check: `wc -l lite/ui-lite.html` < 1200.
- Manual: open lite, load a PDF, toggle button → v2 appears. Reload page → toggle remembered.

**LCAL-S4** — flag → base (separate sprint, only after a real user run with v2 ON for ≥1 measurement session confirms "ถูกใจ")
- Move v2 token values into the base `:root` of `ui-lite.html`.
- Delete all `body.lt-v2` selectors from both CSS files (now base styles).
- Delete the toggle button + JS from `ui-lite.html`.
- Delete `bmaPlan.lite.layerSkin` localStorage key.
- Test: full lite suite GREEN. **Flag is a decision-making tool, not a permanent feature.**

### Forbidden surfaces (clean across all 4 slices)

| Surface | Touched? |
|---|---|
| `lite/static/js/measure-engine.js` (vendored, drift-locked) | NO |
| `RS`, `pdfToC`, `cToPdf`, area math, semanticTag | NO |
| `.bmaplan` schema field rename | NO (`bmaPlan.lite.layerSkin` localStorage is NOT in `.bmaplan` saves) |
| `lite/server_lite.py` | NO (CSS-only feature, no API change) |
| `lite/lite-report.html` | NO (out of scope) |
| `proto/*` | NO (lite-only idea) |
| `lite/static/js/layer-*.js` | NO (CSS migrates from JS-inject is LCAL-S4 follow-up at most — S1..S3 don't touch JS) |

### Acceptance for the dev loop

LCAL is considered DONE when:
1. Live lite layer panel in v2 mode is visually equivalent to `lite/sandbox/invent-layer-dnd.html` on width, row rhythm, color palette, grip/swatch/folder affordances.
2. All shipped `LITE_*` test markers stay GREEN.
3. `wc -l lite/ui-lite.html` < 1200.
4. New CSS files each < 1000 lines.
5. No hard-coded color literals in selector bodies (manual grep — must reference `--var` tokens).
6. User confirms v2 visually after one real measurement session.
