# FINAL_REPORT_FOR_CHATGPT.md — Sprint Outcome Report

> Full report history: [docs/archive/reports-2026-05-09.md](docs/archive/reports-2026-05-09.md)

---

# Latest: BUG-20260520-zen-exit-rp-restore — Zen Mode right-panel restore fix — PASS

**Date:** 2026-05-20
**Branch:** main

## Outcome

PASS. Full E2E EXIT 0, 101 _OK markers, 0 E2E_FAIL. A user-reported bug where the right-panel restore tab vanished after Zen Mode exit has been fixed defensively: F11 now always prevents native fullscreen, F9/F10 provide keyboard recovery for both panels, and the restore-tab CSS selector was corrected from a dead sibling combinator to a `:has()` rule. The original trigger (native-fullscreen desync leaving `body.zen` stuck) could not be reproduced headlessly but is now blocked by the unconditional `preventDefault()`. New E2E marker `BUG_20260520_ZEN_EXIT_RP_RESTORE_OK` GREEN (6 sub-checks). Static-asset safety confirmed: NO_BOM, CACHE_OK, MAIN_UI_OK. Forbidden-surface diff scan CLEAN. UI_REGRESSION_PASS.

## What was delivered

- `proto/ui.html` — F11 keydown handler: unconditional `preventDefault()` (browser can no longer enter native fullscreen and desync `body.zen`); exit condition widened to `body.zen || (!anyModal && !mPts.length)` so stuck Zen always exits; F9→`toggleLeftPanel` and F10→`toggleRightPanel` keybindings added (restore tabs already showed [F9]/[F10] labels but had no handler).
- `proto/static/css/app.css` — dead `#right-panel.collapsed~#workspace #rp-restore-tab` selector (sibling combinator never matched, DOM order wrong) replaced with `body:has(#right-panel.collapsed) #rp-restore-tab{display:flex}`; existing `.canvas-wrap[data-right-collapsed="1"]` attribute fallback kept; zen/overview `display:none !important` overrides unchanged.
- `proto/e2e_ui_test.py` — `_test_bug_zen_exit_rp_restore` (6 sub-checks: inZen, zenExitedMidDraw, f10Toggled, tabVisibleWhenCollapsed, tabHiddenInZen, tabVisibleAfterZenExit) + `BUG_20260520_ZEN_EXIT_RP_RESTORE_OK` marker.
- `UI_MANUAL_TEST.md` — 5-check Zen exit / F9/F10 / restore-tab manual checklist added (static CSS touched → required per AGENTS.md §8 anti-pattern).
- Commit: `9453777` on main.

## What's next

- Pick from Discovered backlog or invent queue: BMA-Plan Lite (focus-mode lite spinoff), comment/annotation redesign, or mobile port.
- Run `/bma-human-test` for fresh findings from the real 45-page permit PDF.
- Verify Scale follow-on E (fold `verifyResult` into `phase1Warnings` + export note) — still recommended.

## Position in Plan

Phase 1 — UI reliability. This sprint closes the Zen Mode / panel-restore usability gap filed as `BUG-20260520-zen-exit-rp-restore` in PHASE_INDEX. No Phase 2 scope boundary crossed.

---

# Previous: INV-2026-05-20-002/003/004 — Layer model rebuild L1+L2+L3 — PASS

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

<!-- Older reports archived to docs/archive/reports-2026-05-09.md -->
