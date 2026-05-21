# Invent: BMA-Plan Lite — standalone /lite/ folder build

- **idea_id**: `2026-05-21-09-25`
- **short-name**: `bma-plan-lite-standalone`
- **Status**: invent-in-progress (started 2026-05-21)
- **Tags**: bma-plan, ui, lite-version, standalone, focus-mode, p-med
- **Source**: user /idea 2026-05-21 09:25, after a full function-scope discussion
- **Predecessor**: `docs/invent/focus-mode-lite-spinoff.md` (invent-done-nogo — right UX target, wrong packaging: it proposed a feature-flag inside `proto/ui.html`; user wants a true sibling `/lite/` tree)

> **FRAME IS PRE-LOCKED.** The function scope below was decided with the user on 2026-05-21 (10-group walkthrough). This invent pass MUST NOT re-litigate scope. RESEARCH + DIVERGE + SPIKE focus exclusively on the OPEN questions: backend code policy, packaging, version-sync, count additive-ignore, dimension rendering, and a single-row-chrome mockup.

---

## Frame (LOCKED 2026-05-21)

### Problem
User loves the F11 / Focus-mode face of BMA-Plan and wants to ship it as a **separate, minimal product** — a `/lite/` folder that is a true sibling of `/proto/`, not a feature flag inside `proto/ui.html` (which is already ~4,230 lines and must not grow). Lite's default face = single-row top menu + full canvas + measurement parity for the common job ("measure 45 pages → export XLSX"), with a deliberately reduced tool/chrome surface.

### Constraints
- Separate `/lite/` tree — **never edit `proto/ui.html` / `proto/server.py` / `proto/static/*`**.
- Raster-PDF compatible (reuse the per-case render approach; no vector-only path).
- Phase 1 boundary — no legal / OCR / AI / FAR-OSR / verdict.
- `.bmaplan` schema **shared with proto** — files cross-open both ways (additive-only).
- Page-scoped layer model preserved (but surfaced as the unified "what am I measuring" picker).
- Python backend MANDATORY — PDF overlay + XLSX export need PyMuPDF + openpyxl; static-only is ruled out.

### Forbidden surfaces this idea must avoid
`polyAreaM2` / `polyMetrics` / `polySelfIntersects` / `pdfToC` / `cToPdf` / `RS` / `buildSnapIndex` / `snap` internals / `.bmaplan` field renames or removals — all in `proto/`. Lite must re-create or re-derive equivalent math in `/lite/` with **byte-identical `.bmaplan` output**, not edit proto's.

### Locked function scope (10 groups)
| Group | IN | CUT |
|---|---|---|
| Measure tools | Set Scale · Polygon · Distance · Path · Reference line · Count (generic) | Land/Building/Site-tools/North/Parking (polygon+label replaces) |
| Snap | Endpoint · Intersection · Nearest (3) | mid/center/perpendicular |
| Layer+Semantic | **unified** "what am I measuring" → drives grouping + show/hide | proto's 2-concept split |
| Pages | open · nav · persistence · rotate · exclude · ⌘K+F12 overview · Page Setup | — |
| Export | XLSX (details+summary) · PDF overlay · PDF+annotations | CSV · JSON |
| Save/Load | `.bmaplan` shared schema (cross-open) | separate format |
| Annotation | Text · Comment · Arrow · Highlight · Frames (rect/circle/cloud) | Sticky note |
| Review | Area totals · Per-page summary · Site metrics | Warnings panel |
| UI chrome | single-row zen-top-bar (INV-002 default) · full canvas · no persistent panels · Corner HUDs | left/right panel · ribbon · status bar |
| Dimension | right-click show/hide · constant-screen-size render | — |

Category → semanticTag map: อาคาร→`gross_floor_area`, ใช้สอย→`use_area`, ช่องว่าง→`deduction_opening`, ที่ดิน→`site_land_area`, footprint→`building_footprint`, ที่ว่าง→`legal_open_space` (+permeable/hardscape), จอดรถ→`parking_area`.

### Success criteria (for SPIKE)
1. Single-row chrome: top menu = exactly ONE row ≤44px at ≥1024×600; no second toolbar; canvas ≥95% (≈100% minus menu row in OS fullscreen).
2. Unified picker: choosing a category sets both the "layer" grouping and the `semanticTag`; show/hide by category declutters overlapping objects.
3. Dimension labels render at constant screen size (not world-scaled); right-click toggles per-object show/hide; small shapes don't get oversized text.
4. ⌘K + F12 overview navigate 45 pages with no persistent left panel.
5. (data) A `.bmaplan` written by the lite object model round-trips in proto byte-identically for shared object types; count objects are additive and proto-ignored.

### Out of scope (this pass)
- Re-deciding any of the 10 locked groups.
- Building the full `/lite/` app (this pass = research + chrome mockup + the backend/packaging decision, not implementation).
- Commercial gating, mobile, iPad.

---

## Research
_(bma-researcher, 2026-05-21 — verbatim)_

### Verdict: PRIOR_ART_PARTIAL — engineering/integration challenge, not math/algorithm. All 6 open questions have known solutions; none greenfield.

### 1. In-repo prior art
- `docs/invent/focus-mode-lite-spinoff.md` (invent-done-nogo) — feature-flag-inside-proto rejected by user; this idea = separate tree.
- `proto/BMA-Plan.spec` + `build.bat` — PyInstaller `--onedir`, single entry (`launch.py`), collects PyMuPDF/uvicorn/FastAPI. Multi-`.exe` needs manual spec edit (multiple Analysis/EXE sharing one COLLECT) — feasible.
- Extraction pattern proven: `semantic-meta.js` / `opening-parent.js` / `export-save.js` / `page-setup.js` extracted from ui.html, loaded via `<script src>`, no bundler. Lite could follow for shared measure math.
- Save/load `applyLoadedProject` (ui.html:3164): version check + warning-only pdfName mismatch; object arrays iterated by name with forEach → **unknown arrays (e.g. `counts`) are silently skipped, no crash.** BUT proto export does NOT iterate `counts` → lite count objects won't show in proto export unless proto explicitly reads them.
- RS reduce sprint blocked → **lite must use identical RS constant** or cross-open coords misalign.
- Page-scoped layer model reusable as-is for the unified picker.

### 2. Library scan
openpyxl (XLSX) viable · pymupdf (PDF) reuse · shapely NOT (15MB, polyAreaM2 is lighter hand-rolled) · pydantic viable for .bmaplan validation · fastapi/uvicorn mandatory both. **No shared "measure engine" package exists on PyPI — math is BMA-Plan-specific → copy or extract.**

### 3. CAD/GIS prior art
AutoCAD LT = runtime feature gate on one codebase (not separate build). Rhino + Grasshopper Player = separate deliverables, shared C++ engine. **QGIS + QGIS Server = closest precedent: shared geospatial lib, multiple entry points (desktop UI vs web server) via shared Python bindings.** Foxit/Bluebeam = multiple SKUs likely from one core + UI-level gates.

### 4. Algorithms
Shoelace/Green's theorem standard (proto already has it — lite must byte-match, not reinvent). Constant-screen-size labels = track devicePixelRatio + measure text screen-space + position world-space scaled 1/zoom; Bluebeam = world-space leader + screen-space text + collision declutter. Mockup files already demo it. PyInstaller multi-entry = manual .spec, standard.

### 5. Competitor UX
Bluebeam: separate Dimension/Length tools, on-canvas caption, right-click per-markup edit (font/size/leader/precision). Foxit: combined measure tool. Lite's right-click show/hide is simpler than a per-object editor.

### Per-question answers
1. **Backend policy:** copy-fork NOT recommended (sync debt). Option C (shared `bma_measure_engine.py` package) viable but extracting it IS a proto edit (separate BLOAT sprint). **Option B (minimal new FastAPI implementing only lite's endpoints — `/upload`, `/page/{n}`, `/analyze`, `/export-xlsx`, PDF overlay — reusing PyMuPDF + identical coord logic) = lowest-risk.**
2. **Packaging:** PyInstaller `--onedir` + separate `lite_launch.py` entry, add to spec (proven, GitHub #6634). Web-only trivial. **Electron NOT recommended (150MB, no new value).** → `.exe` + optional web, not all-three.
3. **Version-sync:** shared package solves it (both `import bma_measure_engine`); else manual sync checklist + **contract test: `.bmaplan` fixtures + `test_measure_parity.py` pinning both to identical math.**
4. **Count additive-ignore:** **proto already tolerates unknown arrays — zero proto edit, zero risk.** Lite writes `store.counts=[...]`; proto ignores. (Caveat: proto export won't include them — fine, count=lite-only.)
5. **Dimension rendering:** MATURE. Canvas overlay + devicePixelRatio + world-space leader + screen-space text + `dimension.visible` toggle. Vanilla JS, no lib.
6. **Chrome mockup:** `invent-focus-mode-lite-spinoff.html` (736 LOC) + `mockup-spatial-sheet-map.html` = reusable SPIKE starting points.

### Recommendation for DIVERGE/SPIKE
Diverge on **backend code policy (Option B minimal-new vs Option C shared-package) + version-sync (vendored-copy+contract-test vs shared-import)**. Spike should deliver: chrome mockup (single-row + corner HUD + ⌘K/F12) AND a `.bmaplan` cross-open parity proof (lite object model writes → proto loads byte-identical for shared types + count ignored).

## Diverge
_(bma-inventor, 2026-05-21 — architecture axis only; UX is locked. 4 approaches.)_

**A — Vendored-copy + contract-test parity** (axis: packaging / zero-proto-edit)
`/lite/{server_lite.py, ui-lite.html, launch_lite.py}` + `tests/test_measure_parity.py`. server_lite.py = fresh ~400-line FastAPI (NOT derived), implements only lite endpoints (/upload, /page/{n}, /thumb, /export-xlsx, /project), uses PyMuPDF+openpyxl directly. JS math = vendored verbatim copy of the 9 functions (RS/pdfToC/cToPdf/polyAreaM2/polyMetrics/polySelfIntersects/pathAreaM2/objectAreaM2/flattenPathToPoints). Parity test pins numeric fixtures, runs BOTH proto+lite math, asserts byte-equal. **Proto edit: ZERO.** Drift cost: LOW→O(N) per math sprint (re-sync vendor copy). forbidden_touch: NO.

**B — JS-extract sprint + minimal server** (axis: integration). Extract the 9 functions out of ui.html into `proto/static/js/measure-engine.js`, both apps `<script src>` it = single source. **Proto edit: YES (edits ui.html — forbidden file).** Needs a prior extraction sprint passing full E2E. Lowest drift but expensive (2 sequential sprints). forbidden_touch: FLAGGED.

**C — Shared `bma_core/` Python package** (axis: monorepo). Move `proto/export/` → top-level `bma_core/`; proto+lite both import. **Proto edit: YES (server.py import block).** forbidden_touch: FLAGGED (minor — import lines, not endpoint).

**D — Single-process dual-mount FastAPI** (axis: zero-separate-server). `launch_all.py` imports `proto.server.app`, mounts `router_lite.py` (/lite/* additive routes); ALL measurement endpoints shared automatically; one exe, `/`=proto `/lite/`=lite. **Proto edit: ZERO (imports, not edits).** Cheapest (~50 lines). forbidden_touch: NO.

## Score
| approach | novelty | accuracy | UX | model-fit | boundary | cost | total |
|---|---|---|---|---|---|---|---|
| A vendored-copy + contract-test | 2 | 5 | 4 | 4 | 5 | 4 | **24** |
| B JS-extract + minimal server | 3 | 5 | 4 | 5 | 4 | 2 | 23 |
| C shared bma_core/ package | 3 | 5 | 4 | 5 | 4 | 2 | 23 |
| D single-process dual-mount | 2 | 5 | 5 | 5 | 5 | 5 | **27** |

## Recommendation
**Inventor's pick: D (27/30)** — zero proto edit, cheapest, strongest boundary; .bmaplan compat structurally guaranteed (same server functions). Fallback A (24/30) for full process isolation. B/C flagged for proto edits — not first-spike material.

### ⚠️ Phase 5 verification — RANKING OVERRIDE (orchestrator)
The inventor scored D's **model-fit=5**, but it scored fit-to-`.bmaplan`-compat, NOT fit-to-the-locked-FRAME's **separation requirement**. The frame mandates a *"true sibling, standalone, distributable independently"* tree — and this idea exists *because* the predecessor NOGO'd precisely on coupling-to-proto. **D achieves "zero proto edit" by tight runtime COUPLING** (`import proto.server.app`, one process): you cannot ship/distribute lite without proto. That directly contradicts the user's hard constraint. → **D is disqualified on FRAME-fit despite top engineering score.**

**Overridden recommendation: spike A (vendored-copy + contract-test).** A is the only approach that delivers a genuinely standalone `/lite/` (own server, own math copy, own process, independently packageable) while keeping `.bmaplan` parity enforced by a contract test — exactly the predecessor's missing piece. D remains documented as the "if you ever relax the separation requirement, this is cheaper" option, to be surfaced at the human checkpoint.

**Note on what is browser-spike-able:** the A-vs-D backend architecture cannot be proven by a no-server sandbox HTML. The SPIKE therefore validates the *chrome + dimension-rendering feasibility* (common to ALL approaches); the A-vs-D decision is surfaced to the human at CHECKPOINT as part of GO.

## Spike
_(2026-05-21 — `proto/sandbox/invent-bma-plan-lite-standalone.html`, browser-only, no server)_

**Scope:** chrome + dimension-rendering feasibility — the layer common to ALL backend approaches. The A-vs-D backend decision is NOT browser-spike-able and is deferred to the human checkpoint.

**Approach:** built the locked-scope lite shell from scratch (vanilla JS + Canvas, ~560 LOC). World→screen transform with zoom/pan; dimension labels drawn in screen space with devicePixelRatio-aware canvas; declutter via box-overlap test; right-click toggles `obj.dimVisible`. Verified with Playwright (Chromium, device_scale_factor=2) + screenshots in `artifacts/invent/bma-plan-lite-standalone/`.

**Outcome: PASS (6/6 browser-verifiable criteria).**
| # | criterion | result |
|---|---|---|
| 1 | single-row top menu ≤44px | **42px measured**, no second row ✅ |
| 2 | unified "กำลังวัดอะไร" picker = layer = semantic + per-category eye show/hide | ✅ (picks tool + sets category color/tag; eye toggles category visibility live) |
| 3 | dimension labels constant screen size + declutter + right-click show/hide | ✅ **proven: labels identical px at 91% vs 227% zoom** (not world-scaled); deduction label decluttered at fit, reappears zoomed-in; right-click toggle wired |
| 4 | corner HUDs (scale+tool / page n/N / category+save+zoom) | ✅ all 4 corners |
| 5 | ⌘K page search + F12 overview (45-page nav, no left panel) | ✅ both overlays + grouped overview (incl. excluded-pages group) |
| 6 | console clean | ✅ 0 errors/warnings |

**Known limitation (expected, mitigated):** a deliberately tiny 40×40px square's area label still overflows the shape at low zoom — this is the inherent "text bigger than shape" case the user flagged. Mitigations demonstrated: (a) right-click hides that object's dimensions, (b) declutter drops overlapping labels, (c) zooming in restores proportion (label px fixed, shape grows). A future polish option = auto-hide a shape's area label when shape screen-area < label box area.

**What the spike does NOT prove:** backend code-sharing (A vendored vs D dual-mount), PyInstaller multi-entry packaging, `.bmaplan` byte-parity round-trip, real raster PDF render — all are server-side and belong to the implementation sprint. Research already rates them PRIOR_ART_PARTIAL (known solutions).

Screenshots: `01-fit.png` `02-zoomed-in.png` `03-zoomed-out.png` `04-overview.png` `05-focus.png`.

## Decision

**Outcome: GO + Approach A** (vendored-copy + contract-test, true standalone) — 2026-05-21, human decision.

### Rationale
- Spike PASS 6/6 on browser-verifiable criteria; chrome + constant-screen-size dimension rendering (the user's flagged pain) demonstrably works.
- Approach A chosen over the higher-engineering-scored D because A delivers a **genuinely standalone `/lite/`** (own server, own vendored math, own process, independently packageable) — which is the entire reason the predecessor `focus-mode-lite-spinoff` was NOGO'd (it coupled to proto). D's "zero proto edit" came from runtime coupling (`import proto.server.app`), which fails the separation requirement.
- **Big-file performance check (user question):** per-page render speed is identical (both call the same PyMuPDF path); A is equal-or-better on footprint + memory headroom + malloc-resistance because a lite-only process doesn't load proto's full machinery. This reinforced A.

### Promoted to: INV-2026-05-21-001 (epic, see PHASE_INDEX). Decomposed into LITE-0..7 sub-sprints for `/bma-dev-loop`.
