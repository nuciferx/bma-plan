# TEST_RESULT.md — Latest Test Result

> Full test history: [docs/archive/test-history-2026-05-09.md](docs/archive/test-history-2026-05-09.md)

---

# Latest: Widget / Menu Placement System

Date: 2026-05-11

## Result: PASS

Proto HEAD: (current working tree)

## Commands Run

```bash
python -m py_compile proto/server.py proto/e2e_ui_test.py  → PASS
python proto/e2e_ui_test.py smoke                          → PASS
python proto/e2e_ui_test.py full                           → PASS
```

## New Assertions (all True)

| Key | Check |
|-----|-------|
| `widgetPlacementRegistryExists` | `WIDGET_MENU_REGISTRY` non-empty array (>= 10 entries) |
| `widgetPlacementHelpersExist` | 9 helper functions defined |
| `widgetPlacementSearchBox` | `#wp-search` and `#wp-category` exist |
| `widgetPlacementListRendered` | `#wp-list` shows ≥ 5 `.wp-row` rows |
| `widgetPlacementKeyWritten` | `bmaPlan.widgetPlacement.v1` written after option change |
| `widgetVisibilityToggleWorks` | `.widget-hidden` toggles on `#widget-review-warnings` |
| `widgetOrderInputWorks` | `style.order` updates on order input change |
| `widgetRegionMoveWorks` | `#widget-review-warnings` moves to `#wp-right-zone` then returns to `#sidebar` |
| `widgetSizeClassApplies` | `.widget-size-collapsed` and `.widget-size-large` apply |
| `widgetPlacementResetWorks` | Reset restores defaults |
| `widgetPlacementMalformedJsonSafe` | Loader does not crash on bad JSON |
| `widgetLockedRespected` | Locked `currentPageLayers` ignores region-change attempt |
| `widgetLeftPanelScrollOk` | `.sidebar-scroll-body` still `overflow-y:auto` |
| `widgetRightPanelScrollOk` | `#rp-content` still `overflow-y:auto` |
| `widgetCurrentPageLayersVisible` | Current page layers panel not hidden |

## Existing Assertions

All existing assertions for inspection panel, page info, review warning, export ready, layers panel, scale badge, drawing, save/load, export, real-PDF round-trip, panel layout, and layout options remain PASS.

## Stop Conditions Triggered

None.
