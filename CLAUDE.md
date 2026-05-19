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

Expected E2E success markers — **smoke (18):** `CACHE_OK`, `SETUP_OK`, `MAIN_UI_OK`, `VECTOR_OK`, `RECAL_OK`, `SITE_UI_OK`, `XLSX_OK`, `PROJECT_OK`, `RASTER_OK`, `WHEEL_OK`, `SNAP_OK`, `SELECT_OK`, `SETBACK_OK`, `EXT_MEASURE_OK`, `MENU_OK`, `PATH_GEOMETRY_OK`, `PHASE_I_A_OK`, `PHASE_I_B1_OK`. **full adds (3):** `ANNOT_OK`, `PERSIST_OK`, `REAL_OK`. Total full = 21 markers (as of 2026-05-14 Phase I-B1).

## Architecture (big picture)

```
Browser (proto/ui.html — single-file HTML + inline JS + Canvas)
    ↕ HTTP (JSON / JPEG)
FastAPI app (proto/server.py)
    ↕ PyMuPDF        — render / export / fallback analysis
    ↕ pypdfium2      — vector snap extraction
Uploaded PDF → per-case temp file via CASES[case_id]
```

~95% of the runtime lives in two files: `proto/server.py` (~1750 lines, all endpoints) and `proto/ui.html` (~4230 lines, all measurement geometry, tools, render, save/load — inline JS, no bundler). Static assets in `proto/static/css/app.css` and `proto/static/js/{semantic-meta,opening-parent}.js`.

**Size discipline (added 2026-05-19 after bloat audit):** `ui.html` started at ~1,700 lines (2026-05). As of 2026-05-19 it stands at ~4,230 lines / 432 KB / 360 KB inline JS / 483 functions. The single-file pattern is still valid by stack (no bundler), but mental + AI-tool load grows non-linearly past ~3,000 lines.

> **Consolidation trigger rule:** if `proto/ui.html` crosses **5,000 lines**, the next sprint MUST be a consolidation sprint that extracts one cohesive JS region to `static/js/<region>.js`, following the existing `semantic-meta.js` / `opening-parent.js` pattern. The `/bma-dev-loop` adds; this rule is the only counter-force. Verify with `wc -l proto/ui.html` before queuing the next feature sprint. Active queue holds BLOAT-2..5 sprint cards for status-bar / export-save / annotations / page-setup extraction — pick the topmost when the trigger fires.

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

## Claude Code skills & subagents (`.claude/`, project-level)

Project-scoped skills + subagents deployed to save tokens and standardize workflow (Pack A + C, 2026-05-13). Trigger by typing the phrase in any language OR `/skill-name` explicitly. Auto-trigger uses the skill `description` field — if it picks wrong, just say "use /xxx" and the choice is corrected.

### Skills (`/command` or auto-trigger)

#### General workflow

| Skill | Trigger phrases | When to use |
|---|---|---|
| `/bma-start` | "เริ่มงาน", "ค้างอะไรอยู่", "session start", "resume" | Session start — 1-page brief replacing the 5-doc READ_ORDER ritual |
| `/bma-check-forbidden` | "แตะ X ได้ไหม", "is X safe to edit" | BEFORE editing any forbidden surface (polyAreaM2 / pdfToC / RS / snap / .bmaplan / server core) |
| `/bma-e2e` | "run test", "run smoke", "เทสต์" | Before commit, after touching forbidden-trigger surfaces, or to verify baseline |
| `/bma-sprint-finalize` | "จบ sprint", "commit ได้", "sprint done" | End of sprint — generates all 7 mandatory outputs in one batch |
| `/bma-log-add` | "log ไว้", "บันทึก", "log this" | Mid-sprint note — appends one entry without rewriting 50KB `log.md` |
| `/bma-sprint-status` | "sprint ค้าง", "active sprints" | Sprint queue drill-down (lighter than `/bma-start`) |
| `/bma-housekeep` | "housekeeping", "เก็บกวาด", "audit files" | Monthly — root file count, sprint triage, date drift detection |

#### UI specialists (Pack D, 2026-05-14)

Designed to fix UI section-by-section without destabilizing the measurement core. Always start a UI sprint with `/bma-ui-scope`, end with `/bma-ui-regression`.

| Skill | Trigger phrases | When to use |
|---|---|---|
| `/bma-ui-scope` | "UI sprint", "scope UI", "วางขอบเขต UI" | BEFORE any UI sprint — classifies which of 8 regions is touched (menu / ribbon / left-panel / right-panel / canvas-ui / summary-widget / status-bar / modal). Returns UI_SCOPE_OK / SPLIT_REQUIRED / BLOCKED |
| `/bma-ui-menu` | "menu bar", "dropdown", "เมนูบน" | Menu-bar sprint scope check — item count, handlers, shortcut conflicts, close behavior. Returns MENU_UI_PASS / MENU_UI_RISK / MENU_UI_FAIL |
| `/bma-ui-ribbon` | "ribbon", "toolbar", "แถบเครื่องมือ" | Ribbon-toolbar sprint scope check — grouping, tool mapping, active state, no fake buttons. Returns RIBBON_PASS / RIBBON_RISK / RIBBON_FAIL |
| `/bma-ui-panel` | "left panel", "right panel", "panel", "layers panel" | Left/right panel scope check — Sheets / Objects / Properties / Inspection / Layers / selected-object footer / scroll / selection sync. Returns PANEL_PASS / PANEL_RISK / PANEL_FAIL |
| `/bma-ui-canvas` | "canvas UI", "loupe", "พิกัด", "zoom badge" | Canvas-adjacent UI scope check (NOT geometry math) — coord display, zoom badge, loupe, cursor guide, snap indicator visuals. Returns CANVAS_UI_PASS / CANVAS_UI_RISK / CANVAS_UI_FAIL |
| `/bma-ui-status` | "status bar", "lbl-save", "lbl-scale" | Status-bar scope check — 7 labels (tool / scale / objects / warnings / layer / save / page) + reactive triggers. Returns STATUS_UI_PASS / STATUS_UI_RISK / STATUS_UI_FAIL |
| `/bma-ui-regression` | "ui regression", "เช็คหลังแก้ UI" | AFTER any UI change — runs py_compile + smoke + (conditional) full, scans diff for forbidden-surface touches. Returns UI_REGRESSION_PASS / UI_REGRESSION_FAIL |

#### Measure specialists (Pack E, 2026-05-14)

Designed to develop Measure features (geometry / path / shape / curve / UX / validation) without destabilizing the area-math contract. Always start a Measure sprint with `/bma-measure-scope`, end with `/bma-measure-regression`. Deliberately slim — 4 skills + 3 subagents — geometry/shape/curve are one skill (they share the path model), validation folds into the regression skill, snap-conflict review folds into the UX specialist.

| Skill | Trigger phrases | When to use |
|---|---|---|
| `/bma-measure-scope` | "measure sprint", "scope measure", "วางขอบเขต measure" | BEFORE any Measure sprint — classifies into 6 categories (ux / geometry-core / shape-generator / curve-ui / validation / export-impact). Returns MEASURE_SCOPE_OK / SPLIT_REQUIRED / BLOCKED |
| `/bma-measure-ux` | "measure interaction", "loupe", "undo จุด", "ล็อกมุม" | Measure interaction scope check — loupe, undo-point, Enter/Esc, Shift/Alt angle lock, preview, cursor guide. Never touches area math or coordinate conversion. Returns MEASURE_UX_PASS / RISK / FAIL |
| `/bma-measure-geometry` | "path geometry", "shape generator", "curve tool", "Bezier", "วาดเส้นโค้ง" | Path-geometry core + shape generators + curve/Bezier UI in one skill (`sub-area` field: core / generator / curve-ui). Never edits polyAreaM2 / pdfToC / cToPdf / RS. Returns MEASURE_GEOMETRY_PASS / RISK / FAIL |
| `/bma-measure-regression` | "measure regression", "เช็คหลังแก้ measure", "validate measure" | AFTER any Measure change — py_compile + smoke + (conditional) full + folded-in pre-export object-validation checklist. Returns MEASURE_REGRESSION_PASS / FAIL |

#### Autonomous loop (Pack F, 2026-05-14)

The self-driving development loop. `docs/status/PHASE_INDEX.md` is the canonical roadmap. Run `/loop /bma-dev-loop` for continuous operation until the roadmap is exhausted or a stop-condition halts it.

| Skill | Trigger phrases | When to use |
|---|---|---|
| `/bma-human-test` | "human test", "เทสเหมือนคน", "journey test" | Realistic full-workflow user-journey test (open → measure every page → export → save → reopen) — delegates to `bma-human-journey-tester`, triages findings into `PHASE_INDEX.md`. Returns HUMAN_TEST_PASS / ISSUES / CRASH. This is the loop's "see problems" mechanism |
| `/bma-dev-loop` | "dev loop", "รันลูป", "ทำต่อจนจบแผน" | One iteration of the autonomous loop — PLAN→SCOPE→BUILD→TEST-M→TEST-H→LEARN→SHIP→LOOP. Full-auto: commits to `main`. Run via `/loop /bma-dev-loop`. Halts only on a stop-condition or roadmap exhaustion |

#### Sandbox / pre-release gate (Pack G, 2026-05-15)

Real customer / problematic PDFs live in `sandbox/`. Pack G runs every file through Tier-1 (open+render) + Tier-2 (journey round-trip) and files unique failure categories — including proposed NEW specialist skills/subagents — into `PHASE_INDEX.md`. Designed as the gate **before** distributing a build.

| Skill | Trigger phrases | When to use |
|---|---|---|
| `/bma-sandbox-test` | "sandbox test", "เทสไฟล์จริง", "ก่อนปล่อยรุ่น", "pre-release" | Pre-release / when new customer PDFs are dropped into `sandbox/`. Runs `bma-sandbox-journey-tester` per file + `bma-issue-triager` for categorisation + new-specialist proposals. Returns SANDBOX_TEST_PASS / ISSUES / CRASH |

#### Invention / R&D loop (Pack H, 2026-05-15)

Upstream of `/bma-dev-loop`. Raw ideas (from `/idea` or PHASE_INDEX `invent-queued`) need research + divergent thinking + spike before they become real sprints. Pack H runs a 7-phase pipeline (PICK → RESEARCH → FRAME → DIVERGE → SCORE → SPIKE → CHECKPOINT) and **always halts at the human checkpoint** — invention requires human risk-taking, unlike `/bma-dev-loop` which is full-auto. Vetted ideas (`invent-done-go`) get a sprint card written into PHASE_INDEX, then `/bma-dev-loop` picks them up.

| Skill | Trigger phrases | When to use |
|---|---|---|
| `/idea` | "idea", "ไอเดีย", "บันทึกไอเดีย", "เก็บไอเดียไว้" | Capture-only — appends verbatim raw idea to `~/.claude/ideas/IDEAS.md` (user-level, NOT in repo) AND mirrors a one-line `invent-queued` bullet into `PHASE_INDEX.md` Discovered backlog under `### ideas YYYY-MM-DD`. Returns `idea_id`. Does NOT run research/diverge/spike — that is `/bma-invent`'s job |
| `/bma-invent` | "invent", "ประดิษฐ์", "ลองคิดวิธีใหม่", "วิจัย + ออกแบบ" | One-shot invention pass on a single idea — useful when you want to deliberately think about one specific idea. Runs the 7-phase pipeline once and halts at checkpoint |
| `/bma-invent-loop` | "invent loop", "วิ่งลูปคิดวิธีใหม่", "loop ประดิษฐ์" | One iteration of the autonomous invention loop — picks next `invent-queued` idea, runs the 7 phases, halts at checkpoint for human GO/NOGO/RESHAPE. Run continuously via `/loop /bma-invent-loop` |

### Subagents (auto-delegated by main agent — usually no need to invoke directly)

#### General workflow

| Subagent | Model | Use |
|---|---|---|
| `bma-explorer` | haiku | Symbol lookup in `proto/ui.html` (~4230) + `proto/server.py` (~1750) — returns line ranges, never dumps whole files |
| `bma-sprint-writer` | sonnet | Batch-write the 7 sprint output files with consistent cross-links + Latest/Previous demotion |
| `bma-test-runner` | haiku | Run E2E and parse the 19 markers — keeps raw uvicorn/Playwright logs out of the main thread |
| `bma-doc-auditor` | sonnet | Quarterly doc drift scan (dates, duplicate facts, broken links, contradictions across status docs) |

#### UI specialists (Pack D, 2026-05-14)

| Subagent | Model | Use |
|---|---|---|
| `bma-menu-bar-specialist` | sonnet | Menu bar / dropdown deep inspection — selector map, handler map, shortcut conflicts, close-behavior gaps |
| `bma-ribbon-specialist` | sonnet | Ribbon toolbar deep inspection — button grouping, tool dispatch, active state, fake-button detection, overflow |
| `bma-left-panel-specialist` | haiku | Left panel deep inspection — Sheets / Objects / Properties / Inspection tabs + scroll + selection sync |
| `bma-right-panel-specialist` | haiku | Right panel deep inspection — page-scoped layers, active layer, lock/visible, selected-object footer, legacy compat |
| `bma-canvas-ui-specialist` | sonnet | Canvas overlay deep inspection — coord display, zoom badge, loupe, cursor guide, snap indicator (STRICTLY non-geometry) |
| `bma-summary-widget-specialist` | sonnet | Summary Widget 4 tabs (Area/Floor/Site/Warnings), drag/collapse/hide/show, data-source map |
| `bma-status-bar-specialist` | haiku | Status bar 7-label render + reactive trigger map, format check, TC-12-B1 investigation |
| `bma-ui-regression-guardian` | haiku | Post-UI-sprint regression gate — runs E2E, scans diff for forbidden surfaces, checks UI_MANUAL_TEST.md updated |

#### Measure specialists (Pack E, 2026-05-14)

| Subagent | Model | Use |
|---|---|---|
| `bma-path-geometry-reviewer` | sonnet | Deep path-geometry review — flattening, Bezier/cubic correctness, area-approximation accuracy, closed-path continuity, backward compat with legacy `poly.pts`. Read-only |
| `bma-measure-ux-specialist` | sonnet | Deep measure-interaction review — event wiring, key conflicts, state isolation, snap-conflict map (maps conflicts; never edits `snap` internals). Read-only |
| `bma-measure-regression-guardian` | haiku | Post-Measure-sprint regression gate — E2E markers (esp. `PATH_GEOMETRY_OK`), forbidden-surface diff scan, folded-in object-validation checklist |

#### Autonomous loop (Pack F, 2026-05-14)

| Subagent | Model | Use |
|---|---|---|
| `bma-human-journey-tester` | sonnet | Drives a realistic Playwright user journey on the real 45-page permit PDF — open → set scale → measure every page → export XLSX → save → reopen → verify round-trip. Reports CRASH / BROKEN / FRICTION / COSMETIC issues that marker-based E2E misses. Read-only on `proto/` — writes temp scripts to `artifacts/` only |

#### Sandbox / pre-release gate (Pack G, 2026-05-15)

| Subagent | Model | Use |
|---|---|---|
| `bma-sandbox-journey-tester` | sonnet | Drives one or more PDFs from `sandbox/` through BMA-Plan. Tier 1 = open + render every page (catches malloc / timeout / blank-page / rotation drift). Tier 2 = set-scale + draw + export + save + reopen round-trip (only if Tier 1 PASS). Reports per-file CRASH / BROKEN / FRICTION / COSMETIC. Read-only on `proto/` — writes per-file logs to `artifacts/sandbox-tests/<pdf-stem>/` only |
| `bma-issue-triager` | sonnet | Takes deduplicated findings from any journey source. Clusters by root cause; for each cluster checks existing `.claude/` coverage and either recommends "extend existing X" or drafts a **NEW skill/subagent spec** (name, model, trigger phrases, I/O contract, scope boundary). Outputs a paste-ready block for `PHASE_INDEX.md`. Never creates `.claude/` files itself — new specialists are created in a follow-up sprint |

#### Invention / R&D loop (Pack H, 2026-05-15)

| Subagent | Model | Use |
|---|---|---|
| `bma-researcher` | haiku | Phase 2 of the invent pipeline. Surveys prior art: in-repo prior work (sprints/plans/design docs), inline-JS library options, CAD/GIS/graphics incumbents (AutoCAD, Rhino, QGIS, Bluebeam, Foxit), literature/algorithms, competitor measurement UX. Returns a 5-section research block + verdict (`PRIOR_ART_MATURE` / `PRIOR_ART_PARTIAL` / `GREENFIELD`). Read-only |
| `bma-inventor` | sonnet | Phase 4-5 of the invent pipeline. Generates 3-5 genuinely different approaches on different axes (data-model / algorithm / UX / representation / integration / library use) — never variants of one another. Then scores them on 6 dimensions (novelty / accuracy / UX / model-fit / boundary / cost) and recommends the top one + a fallback for spike. Read-only |

#### Bug report intake (Pack I, 2026-05-19)

Upstream of `/bma-dev-loop`. A bug surfaced by the user (or as a structured finding from `/bma-human-test` / `/bma-sandbox-test`) doesn't need the full PLAN→SCOPE→BUILD→TEST→LEARN→SHIP loop hand-rolled — Pack I orchestrates it in one invocation. The new bug is always filed into `PHASE_INDEX.md` **before** any fix work starts, so even a stop-condition leaves a tracked sprint behind.

| Skill | Trigger phrases | When to use |
|---|---|---|
| `/bma-bug-report` | "แจ้งบั๊ก", "เจอบั๊ก", "มีบั๊ก", "bug report", "report a bug", "fix this bug" | User-surfaced bug, or a structured finding from a journey test that needs one-shot diagnose-fix-ship. Full-auto: triage → scope → specialist patch plan → fix → /bma-e2e → regression → /bma-sprint-finalize → commit to `main`. Halts on `BUG_STOP_*` (forbidden surface / regression / CRASH / design ambiguity / Phase 2 scope / needs-repro) — bug stays filed either way |

| Subagent | Model | Use |
|---|---|---|
| `bma-bug-triager` | sonnet | Single-bug router (not to be confused with `bma-issue-triager`, which clusters MANY findings + drafts NEW specialist specs). Takes one bug, returns severity + category (one of 15) + suspected file:line + recommended scope skill + recommended specialist subagent + recommended regression skill + acceptance criteria + E2E marker name + risk + adjacent forbidden surface. Read-only — never edits code, never writes to PHASE_INDEX, never invokes other skills. Special return codes: `BUG_TRIAGE_NEEDS_REPRO` / `BUG_TRIAGE_FORBIDDEN` / `BUG_TRIAGE_OUT_OF_SCOPE` |

### Invariants

- `/bma-sprint-finalize` maintains 7 files: `log.md`, `PATCH_SUMMARY.md`, `TEST_RESULT.md`, `FINAL_REPORT_FOR_CHATGPT.md`, `CURRENT_STATUS.md`, `docs/status/LATEST_STATUS.md`, `docs/status/NEXT_ACTIONS.md`. Do not skip — drift between these is the most common housekeeping bug.
- `bma-explorer` has a region map embedded for both runtime files. When asked "where is X", delegate instead of reading the whole file.
- Skills auto-load on session start from `.claude/skills/<name>/SKILL.md`. New skills require a session restart.
- `.claude/settings.local.json` stays gitignored (user-specific). Everything else under `.claude/` is tracked.
- UI sprint discipline (Pack D): every UI sprint starts with `/bma-ui-scope` and ends with `/bma-ui-regression`. Each `bma-ui-*` skill is region-scoped — touching a different region in the same sprint requires SPLIT_REQUIRED verdict. UI specialists are read-only inspectors that return patch plans; the main agent applies edits.
- Measure sprint discipline (Pack E): every Measure sprint starts with `/bma-measure-scope` and ends with `/bma-measure-regression`. `/bma-measure-geometry` covers geometry core + shape generators + curve UI in one skill via a `sub-area` field — `curve-ui` work requires geometry `core` to be PASS first (sequencing, not a split). Measure skills + subagents never edit `polyAreaM2` / `polyMetrics` / `polySelfIntersects` / `pdfToC` / `cToPdf` / `RS` / `snap` internals — they add new functions next to them or route to `/bma-check-forbidden`. Specialists are read-only; the main agent applies edits.
- Autonomous Dev Loop (Pack F): `docs/status/PHASE_INDEX.md` is the canonical phase/sprint roadmap — `/bma-dev-loop` reads the next `queued` sprint from it and writes status back every iteration. The loop is full-auto (commits to `main` without per-sprint review) but every commit still passes `py_compile + smoke + full` first, and it halts on any of 6 stop-conditions (BLOCKED forbidden surface / marker regression / human-test CRASH / design ambiguity / Phase 1 scope boundary / roadmap exhausted). `/bma-human-test` is the "see problems" mechanism — `bma-human-journey-tester` walks the full workflow like a real user (open → measure every page → export → save → reopen) and files discovered issues back into `PHASE_INDEX.md` as new sprints, so the loop self-extends. Run continuously with `/loop /bma-dev-loop`.
- Sandbox / pre-release gate (Pack G): `sandbox/` (gitignored) holds real customer / problematic PDFs. `/bma-sandbox-test` runs every file through `bma-sandbox-journey-tester` (Tier 1 open+render → Tier 2 journey round-trip) and `bma-issue-triager` (root-cause cluster + existing-coverage check + new-specialist spec draft). All findings — including drafts of NEW skill/subagent specs — are filed into the `PHASE_INDEX.md` Discovered backlog under a `### sandbox YYYY-MM-DD` sub-block. **Propose-first, never auto-create:** new specialist files are created in a follow-up sprint by `/bma-dev-loop`, not by this pack, so each gets normal sprint discipline. `/bma-sandbox-test` is required to return `SANDBOX_TEST_PASS` (or ISSUES with all CRASH resolved) before any user-visible release / build hand-off.
- Bug report intake (Pack I): one-shot orchestrator for a single user-surfaced bug. `/bma-bug-report` always (1) files the bug into `PHASE_INDEX.md` **before** any fix work starts so a stop-condition never loses the bug, (2) delegates triage to `bma-bug-triager` (sonnet, one bug → one routing block), (3) chains the existing scope/specialist/regression skills already in Packs D–E, (4) reuses `/bma-sprint-finalize` for the 7 mandatory outputs, (5) commits to `main`. Full-auto by default but halts on `BUG_STOP_BLOCKED` / `BUG_STOP_REGRESSION` / `BUG_STOP_CRASH` / `BUG_STOP_DESIGN` / `BUG_STOP_SCOPE` / `BUG_STOP_NEEDS_REPRO`. **Pack I never adds new code paths** — it only orchestrates existing skills/subagents. Distinction from `bma-issue-triager` (Pack G): that one digests *many* findings from a journey and drafts NEW specialist specs; `bma-bug-triager` (Pack I) routes *one* bug into the *existing* specialist roster.
- Invention / R&D loop (Pack H): upstream of `/bma-dev-loop`. Raw ideas (status `invent-queued`) become vetted sprint cards (status `invent-done-go`) only after passing the 7-phase pipeline: **PICK → RESEARCH (`bma-researcher`, haiku) → FRAME → DIVERGE (`bma-inventor`, sonnet, 3-5 approaches on different axes) → SCORE (6-dim) → SPIKE (in `proto/sandbox/invent-<name>.html`, never in `proto/ui.html`) → CHECKPOINT (human decides GO / NOGO / RESHAPE)**. Two key differences from `/bma-dev-loop`: (1) every iteration halts at the human checkpoint — invention requires human risk-taking, the loop never auto-promotes; (2) commits are restricted to `docs/invent/`, `proto/sandbox/`, and `PHASE_INDEX.md` — invention NEVER touches the live app (`proto/ui.html` / `proto/server.py`). Research-first is non-negotiable: cheap haiku research often reveals a viable inline-JS library (e.g. flatten-js, paper.js) that turns a "novel invention" into a regular sprint (`PRIOR_ART_MATURE` → skip diverge/spike → write standard sprint card). The dev loop reads only `invent-done-go` items; raw `invent-queued` ideas are NOT eligible for `/bma-dev-loop`. Run via `/loop /bma-invent-loop` for continuous invention across the whole idea backlog.

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
.claude/              # tracked: skills/, agents/. Ignored: settings.local.json
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
