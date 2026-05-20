# FINAL_REPORT_FOR_CHATGPT.md — Sprint Outcome Report

> Full report history: [docs/archive/reports-2026-05-09.md](docs/archive/reports-2026-05-09.md)

---

# Latest: INV-2026-05-20-002/003/004 — Layer model rebuild L1+L2+L3 — PASS

**Date:** 2026-05-20
**Branch:** main

## Outcome

PASS. Full E2E EXIT 0, 100 _OK markers, 0 E2E_FAIL. Three-commit layer-model rebuild resolving a user-reported bug where measured objects on ผังบริเวณ (site plan) pages landed in the wrong layer and overlapped with no way to separate or toggle them. The page-scoped layer system is now the single authoritative source for render, hit-test, visibility, and lock — the legacy global `areaTypeLayer`/`layerVis`/`layerLock` maps are demoted to a non-authoritative synced mirror. All three new markers (INV_LAYER_L1_OK / L2_OK / L3_OK) GREEN. Forbidden-surface diff scan CLEAN. UI_REGRESSION_PASS.

## What was delivered

- `proto/ui.html` — L1 (`93c512f`): `validLayerSlugForPage()` slug-guarantee helper; `getObjectLayerSlug()` resolver (openings→deduction, refs/lines→reference_geometry); `_slugVisible`/`_slugLocked`/`_objLayerVisible`/`_objLayerLocked` helpers; render/hit/label/snap paths (`hitTest`, `hitTestAll`, `hitVertex`, `findNearest`, `drawRefLines`) repointed to page-scoped helpers.
- `proto/ui.html` — L2 (`1301a12`): `reassignSelectedObjectLayer()` function; "Layer" `<select>` dropdown in both right-panel and left-panel properties views (Bluebeam-style move-to-layer UX); `objLayerKey()` reports real slug.
- `proto/ui.html` — L3 (`2e6b2f9`): `_layerLockGateBeforeMode` + `toggleLayerLock` deselect repointed to `_slugLocked`/`getObjectLayerSlug`; global `layerVis`/`layerLock` demoted to non-authoritative mirror (toggles still write them for legacy compat; nothing reads them for behaviour).
- `proto/e2e_ui_test.py` — 3 new test functions (`_test_inv_layer_l1/l2/l3`) + 3 markers + HT8D5A repointed (restored to all:True).
- `UI_MANUAL_TEST.md` — new 5-check manual checklist for layer rebuild verification.

## What's next

- `INV-2026-05-20-001 Verify Scale tool` follow-on E: fold `verifyResult` into `phase1Warnings` + export note — recommended next sprint.
- `BUG-20260520-zen-exit-rp-restore` — still parked at `BUG_STOP_NEEDS_REPRO`; awaiting user repro steps.
- Optional: literal deletion of `layerVis`/`layerLock` write-mirror from call sites (zero behaviour gain, test-only churn — not urgent).

## Position in Plan

Phase 1 — Layer system correctness. This sprint closes the page-scoped layer migration (PAGE_SCOPED_LAYER_MODEL.md design doc). Sprint cards: `INV-2026-05-20-002` (L1), `INV-2026-05-20-003` (L2), `INV-2026-05-20-004` (L3) in PHASE_INDEX — mark done. No Phase 2 scope boundary crossed.

---

# Previous: INV-2026-05-20-001 — Verify Scale tool — PASS

**Date:** 2026-05-20
**Branch:** main

## Outcome

PASS. Full E2E GREEN. The Verify Scale feature (invent GO'd approach A) has been implemented: post-calibration second-reference cross-check with %dev band (green/yellow/red), measured/entered/area-impact display, and Accept / Re-calibrate / Average actions. New E2E marker `INV_VERIFY_SCALE_OK` = 9/9 all:True. All key baselines (ANNOT_OK, PERSIST_OK, REAL_OK, PROJECT_OK, XLSX_OK, PATH_GEOMETRY_OK) remain GREEN. Zero regression — the 5 pre-existing env-artifact markers are unchanged.

## What was delivered

- `proto/ui.html` (+82/−5) — `verifyScale()` stub replaced with real flow; 10 new functions; `calibPanelOk()` router added; `#verify-modal` HTML (inline-styled, no `app.css` edit); `cancelCalib` reset; `anyModal` guard extended.
- `proto/e2e_ui_test.py` (+124 lines) — `_test_verify_scale` 9 sub-checks + `INV_VERIFY_SCALE_OK` marker.
- Schema additive: `calibScale.verifyResult{pct, action, verifyPts_per_m, ts}` — rides on `pageStore.calibScale`, round-trips through existing save/load without schema version bump.

## What's next

Layer model rebuild L1+L2+L3 (this sprint — done). Next: Verify Scale follow-on E or BUG-20260520-zen-exit-rp-restore.

## Position in Plan

Phase 1 — Scale workflow. Verify Scale is the quality-assurance layer on top of the existing calibration flow. Sprint card: `INV-2026-05-20-001` in PHASE_INDEX (done). No Phase 2 scope boundary crossed.

---

<!-- Older reports archived to docs/archive/reports-2026-05-09.md -->
