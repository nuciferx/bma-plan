# KNOWN_ISSUES.md — BMA-Plan Known Issues

Date: 2026-05-09

## Active Non-Blocking Issues

| Issue | Severity | Notes |
|-------|----------|-------|
| WinError 10054 (ConnectionResetError) on uvicorn shutdown | Low | Non-fatal, appears after test suite, does not affect results |
| `? proto` in root git status --short | Low | Proto has internal untracked files (BMA-Plan.spec, build/, dist/, etc.) that are not staged; root submodule tracking works correctly |

## Design Limitations (By Intent)

| Limitation | Reason |
|------------|--------|
| lawBasis is null for most object types | Only meaningful for gross_floor_area, floor_area, legal_open_space, site_land_area — by design |
| Right panel still has Legacy/Compatibility Properties+ObjectTree | Intentional backward-compat label; future sprint may collapse these |
| Opening parent auto-link re-runs on saveCurrentPage | By design; parentManual flag now guards against overwriting manual assignments |

## Deferred Work

- Full scale record: calibration endpoint point1/point2 not yet stored in XLSX
- Manual opening parent reassignment further UX improvements
- Parking-specific sub-rows in สรุปตาม Report Target
- Reference arcs/circles (curved path — Sprint 5)
- iPad touch UX (Sprint 6)
- Moving full property editor out of right panel into left panel Properties tab (left tab now shows full editor, but right panel compat section remains)

## Phase 1 Scope Boundary (Permanent)

Never implement in Phase 1:
- Legal checker, OCR, AI checker, Rule Engine
- FAR/OSR/setback validation, K.1 generator
- Auto boundary detection, draggable workspace
- Full autosave engine, large file mode engine
