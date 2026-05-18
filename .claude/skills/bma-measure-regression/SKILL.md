---
name: bma-measure-regression
description: |
  Run AFTER any BMA-Plan Measure change to verify it did not break area math, path geometry, the measurement workflow, save/load, or export. Also folds in the pre-export object-validation checklist (scale present, path closed, self-intersection, opening parent, semanticTag/reportTarget present, flatten tolerance, negative/zero area). Returns MEASURE_REGRESSION_PASS / MEASURE_REGRESSION_FAIL.

  Trigger phrases (Thai): "regression measure", "เช็คหลังแก้ measure", "measure test", "หลัง measure sprint", "วัดยังถูกไหม", "validate measure"
  Trigger phrases (English): "measure regression", "post-measure check", "did measure break anything", "verify measure change", "validate measurement objects"

  Do NOT use when: you only modified .claude/ skills/agents/docs (no app regression risk), or for UI-only changes (use /bma-ui-regression).
---

# /bma-measure-regression — Post-Measure-Change Regression + Validation Gate

Goal: after a Measure sprint touches geometry, shape, curve, or UX code, confirm the area-math contract, path geometry, workflow, save/load, and export all still hold. This is the gate before commit. The pre-export **object-validation** checklist lives here too — it was not large enough to justify a separate skill.

## When to run

Mandatory after any sprint that touched:
- `proto/ui.html` measurement code (geometry / shape / curve / measure-UX)
- `proto/static/js/*.js` measurement logic

Skip when only `.claude/`, `docs/`, or `sprints/` changed.

## Steps

1. **Delegate to `bma-measure-regression-guardian` subagent** with:
   - Files changed (`git diff --stat`)
   - Measure category touched (per `/bma-measure-scope` output)
   - Whether `full` is required (geometry / shape / curve / export-impact → yes)

2. **Subagent runs** (`python3.11`; if absent on host, `py -3.12` satisfies the "Python 3.11+" requirement):
   - `py_compile`
   - `smoke` E2E (16 markers)
   - `full` E2E (3 extra markers) — required if the change touched geometry / shape / curve / save / export / rotation / real-PDF
   - Diff inspector: confirm NO forbidden surface modified — `polyAreaM2`, `polyMetrics`, `polySelfIntersects`, `pdfToC`, `cToPdf`, `RS`, `buildSnapIndex`, `snap`, `.bmaplan` schema field rename/remove

3. **Regression assertions** (must ALL hold):
   - Old polygon (`poly.pts`) area unchanged vs baseline
   - `PATH_GEOMETRY_OK` marker still GREEN
   - Set Scale works · Area works · Opening works · Land works · Dimension works
   - Save / Open `.bmaplan` round-trip works
   - Export XLSX works · Annotated PDF export works
   - Real 45-page PDF still passes (`REAL_OK`) if `full` was required

4. **Object-validation checklist** (folded-in — run against a representative project state):
   - Page has a scale (`manual` or explicitly verified) before metric output
   - Every area / path object is closed
   - No self-intersection (`polySelfIntersects` reports clean)
   - Every opening has a parent
   - `semanticTag` present on every object
   - `reportTarget` present (derived from `semanticTag`)
   - Path flatten tolerance within bounds
   - No negative / zero area objects without an explicit warning

## Markers

- Smoke (16): `CACHE_OK`, `SETUP_OK`, `MAIN_UI_OK`, `VECTOR_OK`, `RECAL_OK`, `SITE_UI_OK`, `XLSX_OK`, `PROJECT_OK`, `RASTER_OK`, `WHEEL_OK`, `SNAP_OK`, `SELECT_OK`, `SETBACK_OK`, `EXT_MEASURE_OK`, `MENU_OK`, `PATH_GEOMETRY_OK`
- Full extra (3): `ANNOT_OK`, `PERSIST_OK`, `REAL_OK`

## Output

```
### Measure Regression: <sprint name>

Verdict: 🟢 MEASURE_REGRESSION_PASS / 🔴 MEASURE_REGRESSION_FAIL

#### Files changed (git diff --stat)
<short table>

#### Forbidden surface scan
- ✅/❌ polyAreaM2 / polyMetrics / polySelfIntersects untouched
- ✅/❌ pdfToC / cToPdf / RS untouched
- ✅/❌ buildSnapIndex / snap untouched
- ✅/❌ .bmaplan schema fields untouched (additive OK)

#### Tests
- py_compile: PASS/FAIL
- smoke (16): all ✅ or list FAILs
- full (3): all ✅ or list FAILs / N/A

#### Regression assertions
- Old polygon area unchanged: ✅/❌
- Workflow (Scale/Area/Opening/Land/Dimension): ✅/❌
- Save/Open round-trip: ✅/❌
- Export XLSX + Annotated PDF: ✅/❌

#### Object-validation checklist
- scale present ✅/❌ · closed ✅/❌ · no self-intersect ✅/❌ · opening parent ✅/❌
- semanticTag ✅/❌ · reportTarget ✅/❌ · flatten tolerance ✅/❌ · no silent neg/zero area ✅/❌

#### Verdict reasoning
<one paragraph — name the failing assertion + quote log line if FAIL>
```

## Constraints

- Output ≤45 lines.
- If any forbidden surface was modified → `MEASURE_REGRESSION_FAIL` regardless of marker state; route to `/bma-check-forbidden`.
- If `PATH_GEOMETRY_OK` or old-polygon-area assertion fails → `FAIL`, recommend rollback or surgical fix.
- Never auto-fix. Never commit. Verification only.
- A geometry/shape/curve sprint that skipped `full` → `FAIL` (insufficient coverage).
