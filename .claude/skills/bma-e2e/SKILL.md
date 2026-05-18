---
name: bma-e2e
description: |
  Run the BMA-Plan E2E test pipeline (py_compile + smoke + full) and return a concise marker summary. Delegates execution to bma-test-runner subagent (haiku) so the main thread doesn't pay token cost for raw log output. Use before/after edits to forbidden-trigger surfaces or before commit per AGENTS.md.

  Trigger phrases (Thai): "test", "รัน test", "run smoke", "run full", "เทสต์", "เทสได้มั้ย", "เช็คก่อน commit"
  Trigger phrases (English): "run e2e", "run tests", "run smoke", "run full", "test it"

  Do NOT use when: user just edited docs only (no source change → use no-test rationale instead, see /bma-sprint-finalize).
---

# /bma-e2e — E2E Test Runner

Goal: replace raw 2-3 minute test log dump with parsed marker summary.

## Inputs

Optional from user:
- `mode`: `smoke` (default) / `full` / `both` / `compile-only`
- `forbidden-trigger`: `yes` (force full) / `no` (default smoke)

## Steps

1. **Default mode logic** — if user didn't specify:
   - If git diff touches `polyAreaM2`/`pdfToC`/`cToPdf`/`RS`/snap/`server.py` core/export/save-load → mode = `full`
   - Else → mode = `smoke`

2. **Delegate** to `bma-test-runner` subagent with:
   - Mode
   - Test PDF path (auto-detect — `proto/test_plan_A1.pdf` for smoke; root real PDF for full)
   - Expected markers (16 for smoke, 19 for full)

3. **Show progress** — tell user "running <mode>... (~N seconds)" before delegating.

4. **After subagent returns**, format result:

   ```
   ## E2E Result: <PASS/FAIL>

   ### py_compile
   - proto/server.py: <PASS/FAIL>
   - proto/e2e_ui_test.py: <PASS/FAIL>

   ### Smoke (16 markers)
   ✅ CACHE_OK, SETUP_OK, MAIN_UI_OK, VECTOR_OK, RECAL_OK, SITE_UI_OK,
      XLSX_OK, PROJECT_OK, RASTER_OK, WHEEL_OK, SNAP_OK, SELECT_OK,
      SETBACK_OK, EXT_MEASURE_OK, MENU_OK, PATH_GEOMETRY_OK
   ❌ <any FAIL>

   ### Full (additional 3 markers, if mode=full or both)
   ✅ ANNOT_OK, PERSIST_OK, REAL_OK

   ### Duration: <Ns total>
   ### Log tail (if any FAIL): <last 10 lines around the failure>
   ```

5. **If FAIL**:
   - Quote the exact failure assertion line from log
   - Suggest: rerun with `--verbose` or check `/bma-check-forbidden` for the affected area
   - Do NOT auto-rerun or attempt fixes.

## Constraints

- Always use `python3.11` (not `python3` — project requires 3.11+ per CLAUDE.md).
- Always run `py_compile` first; abort smoke/full if compile fails.
- For `full`, ensure root real PDF (`20250616_RAMA4 APARTMENT PERMIT rev 1.pdf`) exists before running — abort with clear message if missing.
- Output ≤30 lines. Long logs belong to the subagent's parse, not the user.
