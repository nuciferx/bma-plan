---
name: bma-ui-regression
description: |
  Run AFTER any BMA-Plan UI change to verify it did not break the core measurement workflow. Validates Open PDF, Set Scale, Draw Area, Draw Opening, Save/Open Project, Export XLSX, Annotated PDF, menu dropdowns, path geometry marker. Returns UI_REGRESSION_PASS / UI_REGRESSION_FAIL.

  Trigger phrases (Thai): "regression UI", "เช็คหลังแก้ UI", "UI test", "regression test", "หลัง UI sprint"
  Trigger phrases (English): "ui regression", "post-ui check", "did ui break anything", "verify ui change"

  Do NOT use when: you have only modified .claude/ skills/agents/docs — those changes carry no app regression risk.
---

# /bma-ui-regression — Post-UI-Change Regression Check

Goal: after a UI sprint touches any region, confirm the measurement core, save/load, and export flows still work end-to-end. This is the gate before commit.

## When to run

Mandatory after any sprint that touched:
- `proto/ui.html` (any non-comment change)
- `proto/static/css/app.css`
- `proto/static/js/*.js`
- A menu/ribbon/panel/status DOM rewrite

Skip when only `.claude/`, `docs/`, or `sprints/` changed.

## Steps

1. **Delegate to `bma-ui-regression-guardian` subagent** with:
   - List of files changed (from `git diff --stat`)
   - UI region(s) touched (per `/bma-ui-scope` output)
   - Expected affected markers

2. **Subagent runs**:
   - `py_compile`
   - `smoke` E2E (16 markers)
   - `full` E2E (additional 3 markers) IF the touched region affects: export, save/load, rotation, real-PDF flow, menu/dropdown
   - Diff inspector: confirms no forbidden surface (`polyAreaM2`, `pdfToC`, `cToPdf`, `RS`, `buildSnapIndex`, `snap`, `.bmaplan` schema fields) was modified

3. **Required marker check** (smoke):
   - `CACHE_OK` — server cache
   - `SETUP_OK` — Open PDF + Set Scale path
   - `MAIN_UI_OK` — UI render
   - `VECTOR_OK` — vector snap
   - `RECAL_OK` — recalibration
   - `SITE_UI_OK` — site plan UI
   - `XLSX_OK` — XLSX export
   - `PROJECT_OK` — save/load round-trip
   - `RASTER_OK` — raster fallback
   - `WHEEL_OK` — wheel zoom
   - `SNAP_OK` — snap engine
   - `SELECT_OK` — selection / hit-test
   - `SETBACK_OK` — setback measurement
   - `EXT_MEASURE_OK` — external measurement
   - `MENU_OK` — menu dropdown flow
   - `PATH_GEOMETRY_OK` — Phase H.1 path geometry

4. **Required marker check** (full, if applicable):
   - `ANNOT_OK` — annotated PDF export
   - `PERSIST_OK` — multi-page persistence
   - `REAL_OK` — real permit PDF (45-page A1, rotation=90°)

## Output

```
### UI Regression: <sprint name>

Verdict: 🟢 UI_REGRESSION_PASS / 🔴 UI_REGRESSION_FAIL

#### Files changed
<git diff --stat output, short>

#### Forbidden surface scan
- ✅/❌ polyAreaM2 / polyMetrics / polySelfIntersects untouched
- ✅/❌ pdfToC / cToPdf / RS untouched
- ✅/❌ buildSnapIndex / snap untouched
- ✅/❌ .bmaplan schema fields untouched (additive-only OK)
- ✅/❌ proto/server.py core endpoints untouched

#### Smoke (16 markers)
<table — show only FAILs and missing markers; if all PASS write "all 16 ✅">

#### Full (3 markers — if applicable)
<same>

#### Manual check required
- ✅/❌ UI_MANUAL_TEST.md updated for this sprint
- ✅/❌ Verified in real Chrome (not just headless)

#### Verdict reasoning
<one paragraph>
```

## Constraints

- Output ≤40 lines.
- If FAIL: name the exact failing assertion, quote the log line, recommend rollback or surgical fix.
- Never auto-fix. Never commit. Verification only.
- If forbidden surface was crossed → automatic FAIL even if markers PASS — route to `/bma-check-forbidden`.
