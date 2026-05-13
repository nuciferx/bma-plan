# TEST_RESULT.md — Latest Test Result

> Full test history: [docs/archive/test-history-2026-05-09.md](docs/archive/test-history-2026-05-09.md)

---

# Latest: Phase H.1 Path Geometry Implementation

Branch: main

Date: 2026-05-13

## Result: PASS

## Commands

```bash
python3.11 -m py_compile proto/server.py proto/e2e_ui_test.py
python3.11 proto/e2e_ui_test.py smoke
python3.11 proto/e2e_ui_test.py full
```

## Smoke (16 markers)

| Marker | Result |
|--------|--------|
| CACHE_OK | PASS |
| SETUP_OK | PASS |
| MAIN_UI_OK | PASS |
| VECTOR_OK | PASS |
| RECAL_OK | PASS |
| SITE_UI_OK | PASS |
| XLSX_OK | PASS |
| PROJECT_OK | PASS |
| RASTER_OK | PASS |
| WHEEL_OK | PASS |
| SNAP_OK | PASS |
| SELECT_OK | PASS |
| SETBACK_OK | PASS |
| EXT_MEASURE_OK | PASS |
| MENU_OK | PASS |
| **PATH_GEOMETRY_OK** | **PASS** |

## Full (additional 3 markers)

| Marker | Result |
|--------|--------|
| ANNOT_OK | PASS |
| PERSIST_OK | PASS |
| REAL_OK | PASS |

## PATH_GEOMETRY_OK Detail

```
{
  pathRectMatchesPolygon: True,
  pathCircleWithinTolerance: True,  # numeric=39.09290 vs analytic=39.09768 → 0.012% error
  pathMixedStable: True,
  pathLegacyUnchanged: True,
  pathSaveRoundTrip: True,
  fnsExist: True,
  all: True
}
```

## Known Non-Fatal

- `WinError 10054` (ConnectionResetError) on uvicorn shutdown — does not affect test results.
