# PATCH_SUMMARY.md — Latest Sprint

> Full patch history: [docs/archive/patch-history-2026-05-09.md](docs/archive/patch-history-2026-05-09.md)

---

# Latest: INV-2026-05-19-001a — Zen Mode + Sheet Minimap

Branch: main
Date: 2026-05-19

## Outcome: PASS — py_compile PASS, smoke EXIT 0 (PHASE_INV_ZEN_OK 10/10), full EXIT 0, JOURNEY_OK

## Summary

Additive fullscreen-canvas Zen Mode. `body.zen` class toggle hides ribbon, left/right panels, status bar, and summary widget, expanding canvas to ~94% viewport height. Three corner HUDs (TL = scale + tool, TR = objects + layer, BL = save state) replace the hidden chrome. A lazy-loaded 5-column sheet minimap (IntersectionObserver, one thumb fetch per visible cell) provides page navigation without triggering concurrent render overload. F11 and Esc both exit Zen Mode. PREFS round-trip safe. Two pre-existing E2E baseline drifts from the ribbon-cleanup polish commit fixed in the test file.

## Files Changed

| File | Change |
|---|---|
| `proto/static/css/app.css` | ~50 LOC — `body.zen` chrome-hide rules, `.zen-hud-tl/tr/bl` styles, `.zen-minimap` grid, `.zen-onboarding-toast`, `.zen-exit-chip` |
| `proto/ui.html` | ~180 LOC — `PREFS.layout.zenMode/zenOnboarded`, `toggleZenMode`, `_zenBuildMinimapIfNeeded`, `_zenUpdateMinimapActive`, `_zenToggleMinimap`, `_zenSyncHud`, View menu item, F11/Esc handlers, HUD + minimap DOM, MutationObserver |
| `proto/e2e_ui_test.py` | ~110 LOC + 2-line fix — `_test_inv_zen_mode` (10 sub-checks), `PHASE_INV_ZEN_OK` marker, baseline drift fixes |

## Source Files NOT Touched (Forbidden Surfaces)

- `polyAreaM2`, `polyMetrics`, `polySelfIntersects` — UNCHANGED
- `pdfToC`, `cToPdf`, `RS`, scale math — UNCHANGED
- `buildSnapIndex`, `snap` engine — UNCHANGED
- `proto/server.py` — UNCHANGED (no server edit in this sprint)
- `.bmaplan` schema version stays 1; `PREFS.layout.zenMode/zenOnboarded` additive only

## Tests Run

```
python3.11 -m py_compile proto/server.py proto/e2e_ui_test.py  → PASS
python3.11 proto/e2e_ui_test.py smoke                          → EXIT 0 (PHASE_INV_ZEN_OK 10/10; all pre-existing GREEN)
python3.11 proto/e2e_ui_test.py full                           → EXIT 0
bma-human-journey-tester                                       → JOURNEY_OK (45-page permit; 0 CRASH/BROKEN; 2 FRICTION filed)
```

## Phase 1 Scope Check

- ✅ `polyAreaM2` / `polyMetrics` / `polySelfIntersects` — UNCHANGED
- ✅ `pdfToC` / `cToPdf` / `RS` / scale math — UNCHANGED
- ✅ `buildSnapIndex` / `snap` engine — UNCHANGED
- ✅ `proto/server.py` core endpoints — UNCHANGED
- ✅ `.bmaplan` schema — ADDITIVE only (PREFS layout fields; version stays 1)
- ✅ No legal / OCR / AI / Rule Engine / FAR-OSR pass-fail

---

# Previous: Ribbon Cleanup Polish — hide scale-badge + active-layer-select + Review rsection wrap + font revert

Branch: main
Date: 2026-05-19

## Outcome: PASS — py_compile PASS, smoke PASS, pure cosmetic changes

## Summary

Pure CSS + DOM `display:none` ribbon cleanup with zero JS logic change. Hid the `#scale-badge` red pill from the ribbon (status bar Scale field already surfaces this state) and hid the `#active-layer-select` ribbon-group (Right panel Layers tab is the primary path; select element preserved in DOM for JS references). Rewrapped the `#btn-report` Review button in a proper `.rsection` + `.rlbl` + `.rrow` structure so it renders at the same 60px uniform height as all other ribbon groups. Reverted `body { font-size }` from 16px back to 14px after real-Chrome testing showed layout shifts.

## Files Changed

| File | Change |
|---|---|
| `proto/static/css/app.css` | `body { font-size: 16px }` → `14px` (1-line revert) |
| `proto/ui.html` | `#scale-badge` `display:none`; `.ribbon-group` wrapping `#active-layer-select` `display:none` + 2 `rdiv` dividers removed; `#btn-report` rewrapped in `.ribbon-group.rsection` with `.rlbl "📊 REVIEW"` + `.rrow` + leading `rdiv` |

## Source Files NOT Touched (Forbidden Surfaces)

- `polyAreaM2`, `polyMetrics`, `polySelfIntersects` — UNCHANGED
- `pdfToC`, `cToPdf`, `RS`, scale math — UNCHANGED
- `buildSnapIndex`, `snap` engine — UNCHANGED
- `proto/server.py` — UNCHANGED
- `.bmaplan` schema version stays 1; no schema fields changed

## Tests Run

```
python3.11 -m py_compile proto/server.py proto/e2e_ui_test.py  → PASS
python3.11 proto/e2e_ui_test.py smoke  → PASS (all 18 markers GREEN)
full not run: no forbidden-trigger surfaces touched
```

## Phase 1 Scope Check

- ✅ All forbidden surfaces — UNCHANGED
- ✅ `.bmaplan` schema — UNCHANGED (version stays 1)
- ✅ No legal / OCR / AI / Rule Engine / FAR-OSR pass-fail

<!-- older Previous (Page Setup trilogy + Settings v2) archived to docs/archive/patch-history-2026-05-09.md -->
