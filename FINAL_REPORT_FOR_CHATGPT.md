# FINAL_REPORT_FOR_CHATGPT.md — Sprint Outcome Report

> Full report history: [docs/archive/reports-2026-05-09.md](docs/archive/reports-2026-05-09.md) · [docs/archive/reports-2026-07-02.md](docs/archive/reports-2026-07-02.md)

---

# Latest: BUG-20260702-lite-arc-summary — PASS

**Date:** 2026-07-02
**Branch:** main

## Outcome

PASS. Fixed a silent measurement-accuracy bug: arc-edge polygon areas were correct on the per-object canvas label but wrong in EVERY downstream rollup — summary panel, XLSX export, annotated-PDF overlay, report, layer totals, and site-setup rollup all under-counted curved rooms because 6 call sites dropped `o.edges` when calling the area function. Fixed by swapping all 6 sites to the arc-aware `polyMetricsAnyShape`. A new guard test proves the bug was real (RED on pre-fix code) and that the fix is complete (GREEN post-fix, all 6 consumers now agree with the canvas label). Zero edits to the drift-locked vendored geometry engine; non-arc measurements are byte-identical to before. Bug 1 of 2 from the 2026-07-02 measurement-accuracy audit — bug 2 (CFSS shared-shape instances excluded from totals) is queued next.

## What was delivered

- `lite/ui-lite.html:1049`, `lite/static/js/export-annotate.js:14/27/58`, `lite/static/js/layer-tree.js:62`, `lite/static/js/overview-setup.js:642` — 6 callee swaps: `polyMetrics({pts:o.pts})` → `polyMetricsAnyShape(o,pg)`
- `lite/tests/test_summary_arc_parity.py` (NEW) — `LITE_SUMMARY_ARC_OK` guard test, independent closed-form fixture, proven RED→GREEN across the fix
- `lite/tests/bug-archive.jsonl` — entry appended (fixed_commit `e5264e2`, status `fixed`) via the bug-report pipeline
- `docs/status/PHASE_INDEX.md` — row updated to ✅ done via the bug-report pipeline
- Shipped as commit `e5264e2` on `main`

## What's next

- **(1)** `BUG-20260702-lite-cfss-summary` — CFSS shared-shape instances have no `.pts` of their own, so `computeSummary` skips them entirely; promoting a shared shape removes its source polygon from totals with no replacement. Runs next via `/bma-bug-report`.
- **(2)** File the remaining 2026-07-02 measurement-accuracy audit findings as queued cards: calibration single-sample risk, export payload size stress-testing, `ptToScreen` outside the drift-lock contract, no all-tests runner for lite.

## Position in Plan

Phase 1 — BMA-Plan Lite epic, measurement-accuracy hardening track. Part of a 2-bug audit initiated 2026-07-02; this is bug 1 of 2. Bug-report pipeline (triage → specialist review widened scope from 4 to 6 sites → fix → regression → this write-up) ran end-to-end without a stop-condition. No forbidden surface touched; no Phase 2 scope crossed.

---

# Previous: SLICE report-edit-1 — Editable lite report — PASS

**Date:** 2026-06-05
**Branch:** main

## Outcome

PASS. The lite report is now editable. Users can enter custom subtotals using Excel-style formulas (=B1+B2), click area cells to inject row references while typing, and override computed values — overridden cells are flagged orange when the underlying geometry changes. Deleting a row that a formula references drops that term and raises a red flag instead of silently producing the wrong number. All 7 test cases pass. Zero proto/ edits; all forbidden surfaces untouched.

## What was delivered

- `lite/static/js/report-edit.js` (NEW 404 LOC) — custom formula picker, stable-row-id subtotal mapper, render/persist/provenance, NaN-guard
- `lite/lite-report.html` (+46) — override-overlay toggle markup, grid mount, 4 vendor tags
- `lite/static/js/vendor/jspreadsheet.min.{js,css}` + `jsuites.min.{js,css}` (NEW ~440 KB, MIT, offline-vendored)
- `lite/tests/test_report_edit.py` (NEW 245 LOC) — LITE_REPORT_EDIT_OK 7/7
- `docs/invent/lite-editable-report.md` (NEW) — full invent record with 3 RESHAPE sections
- `.claude/skills/lite-spike-iterate/SKILL.md` (NEW) — SPIKE→EVAL→fix loop skill
- `docs/status/PHASE_INDEX.md` (+11) — 2 idea entries under ### ideas 2026-06-04
- `lite/sandbox/invent-lite-editable-report*` (NEW spike artifacts for reproducibility)

## What's next

- **(1)** Wire report-edit into the production lite report flow (currently behind `#re-toggle` dev gate)
- **(2)** Promote persistence from localStorage v1 to additive `.bmaplan reportEditState` (Approach E; semantic ids proven to serialize cleanly by the PERSIST eval case)
- **(3)** Re-validate print-to-PDF CSS for the jss grid renderer (`@page` rules applied to HTML `<table>` may not translate to jss grid without a dedicated print sprint)

## Position in Plan

Phase 1 — BMA-Plan Lite epic, report sub-system. This sprint completes the BUILD phase of the invent pipeline started 2026-06-04 (ideas: inline-edit area values + Excel-style user-defined subtotal rows). Invent went through 3 RESHAPE rounds before arriving at Approach D3. The editable report feature is behind a dev gate; the next sprint wires it to production. LITE-7 (PyInstaller .exe) remains the only deferred epic item.

---

<!-- BUG-20260526-lite-stale-pf-folder-cleanup + Centerline Snap arc (2026-05-25) archived to docs/archive/reports-2026-07-02.md on 2026-07-02 (BUG-20260702-lite-arc-summary sprint) -->
<!-- SIM-2 (2026-05-24) and older reports archived to docs/archive/reports-2026-05-09.md -->
