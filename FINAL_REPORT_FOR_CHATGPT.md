# FINAL_REPORT_FOR_CHATGPT.md — Sprint Outcome Report

> Full report history: [docs/archive/reports-2026-05-09.md](docs/archive/reports-2026-05-09.md) · [docs/archive/reports-2026-07-02.md](docs/archive/reports-2026-07-02.md)

---

# Latest: BUG-20260702-lite-pagerot-registration — PASS

**Date:** 2026-07-02
**Branch:** main

## Outcome

PASS. Fixed the top-priority BROKEN bug filed earlier today by the `AUDIT-20260702-infra-bundle` render-engine accuracy review (see Previous below). Manual page rotation (`pageRot`) rotated the PDF.js raster canvas but the coordinate contract `ptToScreen`/`screenToPt` ignored `pgRot` (`getRot()` was hardcoded to 0) — pre-existing geometry detached from the visible plan by up to a page diagonal (~84 m at 1:100 A1), geometry drawn while a page was rotated stored bound to the wrong feature (correct area value, wrong location — the classic "right value, wrong location" measurement bug), and `/export-pdf-overlay` never applied `pageRot` at all. Intrinsic PDF `/Rotate` was always correct — only manual rotate was broken. Fixed by commit `9f4b298` ("Fix A — proto-parity" over "Fix B — geometry-baking", per an Opus specialist patch plan): `getRot()` now returns the real per-page rotation; `ptToScreen`/`screenToPt` route through the vendored, parity-tested `pdfToC`/`cToPdf` rotation branches (net 0 lines, zero geometry mutation, no migration); `/export-pdf-overlay` now prerotates the raster and maps all coordinates through a new `_rp` helper. New guard test `LITE_PAGEROT_REG_OK` proven RED→GREEN; 42 distinct regression files green.

## What was delivered

- `lite/static/js/measure-engine.js` — `getRot()` host contract function now returns `pageRot[pg]||0`
- `lite/ui-lite.html` — `ptToScreen`/`screenToPt` rewired through vendored rotation-aware `pdfToC`/`cToPdf`, net 0 lines
- `lite/static/js/export-annotate.js` — export payload includes per-page rotation
- `lite/server_lite.py` — `/export-pdf-overlay` prerotates raster + maps coordinates via new `_rp` helper
- `lite/tests/test_pagerot_registration.py` (NEW) — `LITE_PAGEROT_REG_OK` guard test, RED→GREEN proven
- `docs/status/PHASE_INDEX.md` — row updated to ✅ done via the bug-report pipeline
- Shipped as commit `9f4b298` on `main`

## What's next

- **(1) `AUDIT-20260702-render-followups` bundle** — pdfjs-fail → JPEG fallback / pan double-buffer blanking / scanned-PDF detection messaging / memory-claim correction / real overlay-registration Playwright test (item (e) would add visual coverage for the combined `V.rot≠0` + `pgRot≠0` case, still only exact-inverse-tested).
- **(2) `AUDIT-20260702-s2-fitz-lock`** — per-case PyMuPDF lock needed before the overlay-render step of `/export-pdf-overlay` can safely move to a threadpool.
- **(3) Calibration multi-sample / Verify-Scale port to lite** — the 2026-07-02 Foxit comparison identified this as the single remaining accuracy gap vs. competitors.
- **(4) `ptToScreen`/`screenToPt` into the drift-lock parity fixture** — partially resolved by this fix (runtime now routes through the vendored kernel); remaining work is only adding the functions themselves to `test_measure_parity.py`.

## Position in Plan

Phase 1 — BMA-Plan Lite epic, measurement-accuracy hardening track, render-registration sub-track. This closes the top-priority BROKEN bug filed same-day by `AUDIT-20260702-infra-bundle`'s render-engine accuracy review, resolving the last real correctness gap left by the 2026-05-28 PDF.js render migration. No forbidden surface touched.

---

# Previous: AUDIT-20260702-infra-bundle — PASS

**Date:** 2026-07-02
**Branch:** main

## Outcome

PASS. Same-day follow-on to the 2-bug 2026-07-02 measurement-accuracy audit (both bugs already shipped earlier today, see docs/archive/reports-2026-07-02.md). Three pieces batched into one docs update. **Sprint A (`9c4c36e`, AUDIT-20260702-runner-preflight):** NEW aggregate `lite/tests/run_all_tests.py` — discovers + runs every `test_*.py` with per-test timeout, summary table, `LITE_RUN_ALL_OK`/`FAIL`; PREFLIGHT fails fast on low disk (<2 GB, hardened after the 2026-07-02 ENOSPC incident) or missing dependencies. First full run: 60/60 PASS in 8.5 min. **Sprint B (`60d424a`, AUDIT-20260702-export-caps):** `/export-pdf-overlay` and `/export-xlsx` now validate payloads BEFORE rendering (5 caps, HTTP 400, no silent truncation, ≥10x realistic worst case; bonus fix for a latent 500). NEW `test_export_endpoints.py` (`LITE_EXPORT_ENDPOINTS_OK` 14/14) is the first real HTTP test of either export endpoint. **Review C (read-only, Opus agent):** render-engine coordinate contract verdict SOUND for the common case, but surfaces a real BROKEN bug (`BUG-20260702-lite-pagerot-registration` — manual page rotation desyncs stored geometry from the raster) plus a hardening bundle, both filed to `PHASE_INDEX.md` with zero code applied.

## What was delivered

- `lite/tests/run_all_tests.py` (NEW) — aggregate test runner with disk/dependency PREFLIGHT
- `lite/server_lite.py` — export payload validation caps on `/export-pdf-overlay` + `/export-xlsx`; `wb.save()` offloaded via `run_in_threadpool`
- `lite/tests/test_export_endpoints.py` (NEW) — first real HTTP tests of both export endpoints, `LITE_EXPORT_ENDPOINTS_OK` 14/14
- `docs/status/PHASE_INDEX.md` — `BUG-20260702-lite-pagerot-registration` (BROKEN) + `AUDIT-20260702-render-followups` (bundle) + `AUDIT-20260702-s2-fitz-lock` filed by Review C / Sprint B
- Shipped as commits `9c4c36e` + `60d424a` on `main`

## What's next

- **(1) `BUG-20260702-lite-pagerot-registration`** — manual page rotate desyncs stored geometry from the raster. **SHIPPED same-day — see Latest above.**
- **(2) `AUDIT-20260702-render-followups` bundle** — pdfjs-fail → JPEG fallback / pan double-buffer blanking / scanned-PDF detection messaging / memory-claim correction / real overlay-registration Playwright test.
- **(3) `AUDIT-20260702-s2-fitz-lock`** — per-case PyMuPDF lock needed before the overlay-render step of `/export-pdf-overlay` can safely move to a threadpool.
- Older queued audit follow-ons (calibration multi-sample, `ptToScreen`/`screenToPt` into the drift-lock set) remain queued.

## Position in Plan

Phase 1 — BMA-Plan Lite epic, measurement-accuracy hardening track, test/render infrastructure sub-track. Direct same-day follow-on to the 2-bug audit (arc-summary + cfss-summary, both shipped earlier 2026-07-02). No forbidden surface touched by Sprint A/B; Review C is read-only.

---

<!-- BUG-20260702-lite-cfss-summary + BUG-20260702-lite-arc-summary (2026-07-02) + SLICE report-edit-1 (2026-06-05) + BUG-20260526-lite-stale-pf-folder-cleanup + Centerline Snap arc (2026-05-25) archived to docs/archive/reports-2026-07-02.md on 2026-07-02 (BUG-20260702-lite-pagerot-registration sprint) -->
<!-- SIM-2 (2026-05-24) and older reports archived to docs/archive/reports-2026-05-09.md -->
