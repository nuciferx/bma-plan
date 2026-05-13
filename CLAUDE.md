# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this project is

BMA-Plan Phase 1 = Raster PDF Measurement Assistant. Mini-CAD for area measurement from raster/scanned construction PDFs. Concept = "CAD core + Foxit measurement behavior + Excel-style summary."

Phase 1 explicitly **excludes** (never add to this codebase): legal checker, OCR, AI, rule engine, FAR/OSR/setback law validation, K.1 generator, auto boundary detection, multi-user/SaaS. A document at `docs/design/BMA_PLAN_V2_SCOPE.md` describes an old "v2" with FAR/OSR/legal pass-fail — **that is not the current direction**; treat it as historical.

Real customer PDFs are usually raster/scanned. Code must not depend on PDF vector geometry being present (raster fallback path required).

**`AGENTS.md` is the authoritative operating manual.** It owns the GTM Infinite Loop, mandatory sprint outputs, hard rules, sprint backlog, and stop conditions. Read it before planning any non-trivial change. The reading order in `docs/status/READ_ORDER.md` is also authoritative for session start: `AGENTS.md → CURRENT_STATUS.md → docs/status/LATEST_STATUS.md → docs/status/NEXT_ACTIONS.md → docs/status/TEST_BASELINE.md`.

Respond to the user in Thai. Direct, practical, terse.

## Run / test

Entire runtime lives in `proto/`. No build step for dev work.

**Python 3.11+ required.** `proto/server.py` uses `dict | None` union syntax that fails on 3.9. Verify with `python3.11 --version`.

```bash
# Run app — picks free port from 8000, opens browser
python3.11 proto/launch.py

# Type-check
python3.11 -m py_compile proto/server.py proto/e2e_ui_test.py

# E2E (Playwright-driven; starts its own uvicorn on a free port)
python3.11 proto/e2e_ui_test.py smoke
python3.11 proto/e2e_ui_test.py full    # adds rotation, real-permit-PDF, multi-page persistence
```

`proto/requirements.txt` is incomplete. `aiofiles` (required by `StaticFiles`) and `python-multipart` (form parsing) are also needed — install with `pip install aiofiles python-multipart` if missing. **Listing `aiofiles` only as optional or omitting it is an anti-pattern** — see `docs/process/ANTI_PATTERNS.md` #3.

No pytest. Running one test = edit `main()` in `proto/e2e_ui_test.py` to call just one `_test_*` function, then run the file.

`full` is required (not just `smoke`) when touching: export (CSV/JSON/XLSX/PDF/PDF+annotations), rotation, save/load, real-permit-PDF flow, session isolation, scale/snap engine, layer system, annotation PDF.

Expected E2E success markers: `CACHE_OK`, `SETUP_OK`, `MAIN_UI_OK`, `VECTOR_OK`, `RECAL_OK`, `SITE_UI_OK`, `XLSX_OK`, `PROJECT_OK`, `RASTER_OK`, `WHEEL_OK`, `SNAP_OK`, `SELECT_OK`, `SETBACK_OK`, `EXT_MEASURE_OK`, `ANNOT_OK`, `PERSIST_OK`, `REAL_OK`, `MENU_OK`.

## Architecture (big picture)

```
Browser (proto/ui.html — single-file HTML + inline JS + Canvas)
    ↕ HTTP (JSON / JPEG)
FastAPI app (proto/server.py)
    ↕ PyMuPDF        — render / export / fallback analysis
    ↕ pypdfium2      — vector snap extraction
Uploaded PDF → per-case temp file via CASES[case_id]
```

~95% of the runtime lives in two files: `proto/server.py` (~1370 lines, all endpoints) and `proto/ui.html` (~1700 lines, all measurement geometry, tools, render, save/load — inline JS, no bundler). Static assets in `proto/static/css/app.css` and `proto/static/js/{semantic-meta,opening-parent}.js`.

### Non-negotiable invariants

- **Per-case isolation.** Backend never uses a global `SESSION`. Every endpoint takes `case_id`. Each case owns `doc`, `path`, `page_cache`, `image_cache`, `page_tags`, `project_info`. TTL prunes idle cases; cache size is bounded per case.

- **Raw-geometry contract.** Store raw PDF-coordinate geometry; re-derive metric values from the *current page scale* on every read. Never cache `m` or `m²`. Recalibration must update all downstream summaries and export rows immediately.

- **Scale states.** `manual` (user-calibrated) / `auto-unverified` (detected but unconfirmed) / `unknown` (raster fallback, measurements stay in `pt`/`pt²`). Never promote `auto-unverified` to confident metric output without explicit user verification.

- **RS = 1.5 is baked into coordinate math.** `RS` appears in `pdfToC()`, `cToPdf()`, and the E2E `raw()` helper. Reducing render scale changes setback distances and every coordinate-derived value. A prior `RUN_RENDER_SCALE_REDUCE` sprint was blocked for this reason — do not change `RS` without refactoring all coordinate-dependent code.

- **Workflow lock.** Open PDF → Set Scale → Page Setup → Measure → Review → Export. Status bar reflects this: Tool, Scale, Objects, Warnings, Layer, Save, Page.

- **Layer is for workflow only.** Layers are **page-scoped** (locked 2026-05-10 — `docs/design/PAGE_SCOPED_LAYER_MODEL.md`). Same layer name on different pages = two different `layer.id`s. **Calculation, deduction, totals, and export grouping never read `layer.name` or `layer.slug`** — they use `semanticTag` / `measurementProfile` / `reportTarget` (the 5 metadata fields on each object: `measurementProfile`, `objectCategory`, `reportTarget`, `lawBasis`, `countingRule`, all derived from `semanticTag`). Global `layerVis` / `layerLock` still exist in JS as a bridge during migration — do not extend them.

- **Hit priority for overlapping objects** (in canvas hit tests): selected vertex/edge → opening/deduction → room/sub area → base/GFA area. Locked layer = visible but not selectable. Picker popup appears when ≥2 objects overlap at click.

### Save / project format

`.bmaplan` JSON, `version: 1`. Holds `pageStore`, `pageRotations`, `pageTags`, `projectInfo`, `excludedPages`, per-page annotations. Load verifies `pdfName` matches before restoring (warning, not block, on mismatch — supports project merge).

Save uses File System Access API: `currentProjectHandle` (FileSystemFileHandle) + `isDirty` flag. Ctrl+S triggers `saveProject()`; if no handle, falls through to `saveProjectAs()` (`showSaveFilePicker`). Browser without FSAPI → `dlBlob()` download fallback. `isDirty` is set by `pushUndo()` / `restoreSnapshot()` / `clearMeasures()`, cleared by save/load.

Schema is **additive only.** New optional fields are fine; renaming or removing existing fields breaks user saves.

### Persistent state (localStorage)

| Key | Holds |
|---|---|
| `bmaPlan.recentProjects.v1` | Up to 10 recent `.bmaplan` filenames |
| `bmaPlan.uiLayoutOptions.v1` | UI Layout Options presets (Current Stable / Mockup V3 / Inspection Focus / Layer Focus / Compact) |
| `bmaPlan.widgetPlacement.v1` | Widget Menu Placement state — movable widgets: `workflow`, `reviewWarnings`, `exportReady`; locked widgets keep visibility/size only |

## Forbidden surfaces (never edit casually)

| Surface | File | Why |
|---|---|---|
| `polyAreaM2`, `polyMetrics`, `polySelfIntersects` | `proto/ui.html` | Area math contract — every measurement summary depends on it. Add new functions next to them (e.g. `circleAreaM2`, `pathAreaM2`) instead of editing. |
| `pdfToC`, `cToPdf`, scale math | `proto/ui.html` | Coordinate conversion contract — rotation, zoom, RS all depend on it. |
| `buildSnapIndex`, `snap` | `proto/ui.html` | CAD snap engine. Endpoint / midpoint / center / nearest / intersection / perpendicular / close-polygon. |
| Core upload/render/analyse endpoints | `proto/server.py` | Case isolation, validation, stale-response guards, render cache bounds. |
| `.bmaplan` schema fields | save/load in `proto/ui.html` | Backward compatibility for user saves. |
| `RS` constant + anything derived | `proto/ui.html` and E2E `raw()` helper | Reducing it breaks setback distances and coordinate-derived tests. |

## Anti-patterns (each has caused a real incident)

Full catalog in `docs/process/ANTI_PATTERNS.md` and `docs/process/TROUBLESHOOTING.md`. The headline traps:

- **Guarding `app.mount("/static", ...)` with `if _STATIC_DIR.exists():`** silently swallows the `RuntimeError` raised when `aiofiles` is missing. Result: every `/static/*` returns 404, UI loads unstyled, E2E may still pass off cached assets. Required pattern (from AGENTS.md §8):
  ```python
  from pathlib import Path
  _BASE_DIR = Path(__file__).resolve().parent
  _STATIC_DIR = _BASE_DIR / "static"
  print(f"[static] serving from: {_STATIC_DIR}")
  app.mount("/static", StaticFiles(directory=str(_STATIC_DIR)), name="static")
  ```

- **CWD-relative static paths** (`os.path.join(os.path.dirname(__file__), "static")` with bare `__file__`) break when the script is launched from a different directory. Always use `Path(__file__).resolve().parent`.

- **UTF-8 BOM in `proto/static/css/app.css`** makes some browsers fail to parse the first rule (the file loads HTTP 200 but no styles apply). Verify with `python -c "open('proto/static/css/app.css','rb').read(3)==b'\\xef\\xbb\\xbf'"`.

- **E2E pass ≠ browser renders correctly.** Headless Chromium can use cached CSS. Any static-touching sprint also requires `UI_MANUAL_TEST.md`.

- **Calculating from layer name** (`layer.name === "พื้นที่อาคาร"` → count as building area). Forbidden by the Page-Scoped Layer Model. Always use `semanticTag` / `measurementProfile` / `reportTarget`.

- **Progressive PDF rendering** (preview-then-full) is *not* a free perf win. A prior `RUN_PROGRESSIVE_PREVIEW_AND_BACKGROUND_FULL_RENDER` sprint was blocked: server has to render 2× plus all thumbnails concurrently and hits `malloc failed` on real PDFs. The JPEG encode in `/page/{n}` is 93% of render time — see the `[BMA_PAGE_RENDER_PERF]` log line for per-request `session/cache/get_pixmap/encode/bytes/total` breakdown.

## Document discipline (mandatory per sprint)

AGENTS.md §1 "Mandatory Sprint Outputs" — every sprint, **including docs-only ones**, must update:

- `log.md` — session log entry: date, what changed, why, files touched, tests run, known gaps. Mandatory for **every** activity including reads/analysis with no code change (include rationale). Only the last ~2 sessions live in root `log.md`; older sessions are archived under `docs/archive/`.
- `PATCH_SUMMARY.md` — what changed
- `TEST_RESULT.md` — test commands + results, or explicit "no-test rationale" for docs-only
- `FINAL_REPORT_FOR_CHATGPT.md` — sprint outcome
- `UI_MANUAL_TEST.md` — additionally when UI/UX changes; AGENTS §8 also lists static-asset E2E assertions

After each sprint, also refresh: `CURRENT_STATUS.md` (one-line state), `docs/status/{LATEST_STATUS,NEXT_ACTIONS,KNOWN_ISSUES,COMMIT_HISTORY,TEST_BASELINE}.md`, and the sprint card in `sprints/completed/YYYY-MM-DD-short-name/`.

One sprint = one problem. Commits must pass `py_compile + smoke` before merge, and `full` if any forbidden-trigger surface (export, rotation, save/load, real-PDF, snap, layer) was touched.

## Repository layout

```
proto/                # entire runtime (FastAPI + HTML/JS + tests + spec)
docs/
  design/             # architecture + scope (READ ME: PHASE1_CONTEXT, PAGE_SCOPED_LAYER_MODEL)
  process/            # anti-patterns, troubleshooting, sprint index, quick test guide
  status/             # LATEST_STATUS, NEXT_ACTIONS, KNOWN_ISSUES, READ_ORDER, TEST_BASELINE
  references/         # gitignored — large reference PDFs
  archive/            # historical logs
sprints/
  active/             # current/next sprint cards
  completed/YYYY-MM-DD-name/RUN_*.md
  archive/            # superseded
plans/                # cross-sprint planning docs
artifacts/            # gitignored — generated test outputs, screenshots, downloads
archive/old_docs/     # historical context (includes the original CLAUDE.md predecessor)
```

`proto/` was a git submodule pointing to `https://github.com/nuciferx/bma-plan-proto.git` until 2026-05-12, when it was absorbed into this repo as a regular directory. The proto remote is now an archive. Older design/status docs may still describe the submodule layout — treat those mentions as historical.

PyInstaller outputs (`proto/build/`, `proto/dist/`, `proto/dist2/`, `proto/export/`) and server logs are gitignored at the proto/ level. Rebuild via `proto/build.bat` or `BMA-Plan.spec` if a binary is needed.

Root must stay small. Files allowed at root: `AGENTS.md`, `CLAUDE.md`, `README.md`, `index.md`, `CURRENT_STATUS.md`, `log.md`, `FINAL_REPORT_FOR_CHATGPT.md`, `TEST_RESULT.md`, `PATCH_SUMMARY.md`, `UI_MANUAL_TEST.md`, `NEXT_ACTION.md`, `.gitignore`. Anything else generally goes into `docs/`, `sprints/`, `plans/`, or `archive/`.

## Test PDFs

- `proto/test_plan_A1.pdf` — small fixture used by `smoke`
- `20250616_RAMA4 APARTMENT PERMIT rev 1.pdf` (root) — real 45-page A1 permit with rotation=90°, used by `full` for navigation / rotation / multi-page persistence

The real PDF must live at repo root because `proto/e2e_ui_test.py` resolves it relative to `proto/`'s parent. It is gitignored.
