# TEST_RESULT.md — Latest Test Result

> Full test history: [docs/archive/test-history-2026-05-09.md](docs/archive/test-history-2026-05-09.md)

---

# Latest: BUG-20260520-zen-exit-rp-restore — Zen Mode right-panel restore fix

Branch: main
Date: 2026-05-20

## Result: PASS — py_compile PASS; full EXIT 0; 101 _OK markers, 0 E2E_FAIL; NEW BUG_20260520_ZEN_EXIT_RP_RESTORE_OK GREEN (6 sub-checks); all prior 100 markers retained; zero regression.

## Commands

```bash
python3.11 -m py_compile proto/server.py proto/e2e_ui_test.py  # PASS
python3.11 proto/e2e_ui_test.py full                            # EXIT 0 — 101 _OK markers
```

## New Marker: BUG_20260520_ZEN_EXIT_RP_RESTORE_OK — 6 sub-checks

| Sub-check | Result | Description |
|---|---|---|
| inZen | PASS | `body.zen` class applied after F11 press; Zen Mode active |
| zenExitedMidDraw | PASS | F11 pressed while mid-draw (modal/draw guard) still exits Zen cleanly; `body.zen` removed |
| f10Toggled | PASS | F10 keypress calls `toggleRightPanel`; right panel collapses/restores |
| tabVisibleWhenCollapsed | PASS | `#rp-restore-tab` has `display:flex` when `#right-panel.collapsed` and not in Zen/Overview |
| tabHiddenInZen | PASS | `#rp-restore-tab` has `display:none` when `body.zen` active (`!important` override wins) |
| tabVisibleAfterZenExit | PASS | After Zen exit with right panel collapsed, `#rp-restore-tab` reappears |

## Static-Asset Safety

| Check | Result |
|---|---|
| NO_BOM on `proto/static/css/app.css` | PASS — no UTF-8 BOM |
| `CACHE_OK` | PASS |
| `MAIN_UI_OK` (`cssLinkPresent: true`, `cssVarLoaded: true`) | PASS |

## Key Baselines GREEN (101 total _OK markers)

| Marker | Result |
|---|---|
| ANNOT_OK | PASS |
| PERSIST_OK | PASS |
| REAL_OK | PASS |
| PROJECT_OK | PASS |
| XLSX_OK | PASS |
| PATH_GEOMETRY_OK | PASS |
| INV_VERIFY_SCALE_OK | PASS (9/9) |
| INV_LAYER_L1_OK / L2_OK / L3_OK | PASS |
| BUG_20260520_SEL_MIDPAN_OK | PASS |

Pre-existing cosmetic all:False markers (HT8C_OK, HT8D1_OK, HT10_OK, HT12H_OK, PHASE_I_D_OK) unchanged. Forbidden-surface diff scan CLEAN. UI_REGRESSION_PASS.

---

# Previous: INV-2026-05-20-002/003/004 — Layer model rebuild L1+L2+L3

Branch: main
Date: 2026-05-20

## Result: PASS — py_compile PASS; full EXIT 0; 100 _OK markers, 0 E2E_FAIL; NEW INV_LAYER_L1/L2/L3_OK GREEN; HT8D5A restored; zero regression.

## Commands

```bash
py_compile proto/server.py proto/e2e_ui_test.py  # PASS
proto/e2e_ui_test.py full                         # EXIT 0 — 100 _OK markers
```

## New Markers

| Marker | Result | Description |
|---|---|---|
| **INV_LAYER_L1_OK** | PASS | Slug guarantee (`validLayerSlugForPage`) + render/hit/label paths read page-scoped layer via `_slugVisible`/`_slugLocked`/`_objLayerVisible`/`_objLayerLocked`; global `areaTypeLayer` no longer used for behaviour |
| **INV_LAYER_L2_OK** | PASS | `reassignSelectedObjectLayer()` present; Layer `<select>` dropdown in properties panels; `objLayerKey()` reports real slug |
| **INV_LAYER_L3_OK** | PASS | Page locked + global unlocked → app follows page-scoped lock (authority proven); `_layerLockGateBeforeMode` + `toggleLayerLock` repointed to `_slugLocked`/`getObjectLayerSlug` |

## HT8D5A Lock Test

| Test | Before sprint | After sprint |
|---|---|---|
| HT8D5A | all:False (repointed to page layers — test needed update) | **all:True RESTORED** |

## Key Baselines GREEN (100 total _OK markers)

| Marker | Result |
|---|---|
| ANNOT_OK | PASS |
| PERSIST_OK | PASS |
| REAL_OK | PASS |
| PROJECT_OK | PASS |
| XLSX_OK | PASS |
| PATH_GEOMETRY_OK | PASS |
| INV_VERIFY_SCALE_OK | PASS (9/9) |
| BUG_20260520_SEL_MIDPAN_OK | PASS |

Pre-existing cosmetic all:False markers (HT8C_OK, HT8D1_OK, HT10_OK, HT12H_OK, PHASE_I_D_OK — left-panel/layout/compass, unrelated to layers) unchanged. Forbidden-surface diff scan CLEAN. UI_REGRESSION_PASS.

<!-- Older test results archived to docs/archive/test-history-2026-05-09.md -->

---

<!-- Older results archived to docs/archive/test-history-2026-05-09.md -->
