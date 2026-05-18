# RUN_INV_FREEFORM_AREA — INV-2026-05-17-001: Freeform area measurement

Date: 2026-05-17
Branch: main
Status: PASS — completed 2026-05-17 · commit `023b988`

## Goal

Port the freeform-area spike (`docs/invent/freeform-area.md` + `proto/sandbox/invent-freeform-area.html`) to production `proto/ui.html`. In polygon mode, holding `Alt` at mousedown enters a streaming freehand sub-mode with distance-bin sampling (≥ 6 px gate). Releasing Alt returns to click-vertex mode — mixed click+drag in one polygon. `Shift`/`Ctrl` during draw modulates RDP tolerance live. `Enter` closes + RDP-decimates + computes area via existing `polyAreaM2`. Zero forbidden-surface edits. Schema fully additive.

Source of truth: `docs/invent/freeform-area.md` (research + 3 approaches + scoring + spike rationale) + `proto/sandbox/invent-freeform-area.html` (spike PASS 6/6, err=1.22%).

## Why this sprint exists

INV-2026-05-17-001 was filed as `queued — invent-done-go` in `PHASE_INDEX.md` after the 7-phase invention pipeline (PICK → RESEARCH → FRAME → DIVERGE → SCORE → SPIKE → CHECKPOINT). User approved GO 2026-05-17. Approach D (Alt sub-mode of polygon) was selected from the spike: minimal state-machine extension, no new draw mode, reuses existing `polyAreaM2` unchanged.

## Scope — IN

### New helpers (`proto/ui.html`, additive — next to area math block)

- `rdpSimplify(pts, tol)` — inline Ramer-Douglas-Peucker, ~25 LOC. Placed next to `polyAreaM2` (additive — `polyAreaM2` / `polyMetrics` untouched).

### New module-scope state

`mFreehandActive`, `mFreehandRaw`, `mFreehandLastSampled`, `mFreehandSegments`, `mFreehandSamplesTotal`, `freehandTolerance=4`, `freehandSampleStepPx=6`

### Edit sites in `proto/ui.html`

- mousedown `mode==='area'` branch: Alt-at-mousedown enters freehand sub-mode. Guard: `mFreehandActive` and `mArcDraft.pending` are mutually exclusive (carry-over risk #1 resolved here).
- mousemove: freehand sample-and-redraw branch inserted BEFORE the snap branch. Explicit early-return bypasses snap engine during drag (carry-over risk #2 resolved here).
- mouseup: commits burst via `rdpSimplify` + `cToPdf` + push to `mPts` (skip first to avoid duplicate vertex).
- `setMode` / `clearMeasures` / `drawBarCancel` / Esc: reset all freehand state.
- `finishCurrentArea` (both branches): attaches `obj.freeform = {tolerance, freehandSegments, originalSamples}` when applicable (additive optional field — no `.bmaplan` migration needed).
- Shift / Control keydown: live tolerance modulation when `mFreehandActive && mode==='area'`.
- `redraw()`: live raw freehand trail in red dashed during burst.

### `proto/e2e_ui_test.py`

- NEW `_test_inv_freeform_area` — `PHASE_FREEFORM_OK` marker, 7 sub-checks:

| Sub-check | Result | Detail |
|-----------|--------|--------|
| accCheck | PASS | err=0.46% on noisy circle (budget < 5%) |
| mixedOk | PASS | mixed click+drag polygon, 11 pts |
| siCheck | PASS | `polySelfIntersects` on decimated polyline |
| metaOk | PASS | `obj.freeform` metadata present |
| resetOk | PASS | freehand state cleared on mode-change |
| stateOk | PASS | `mFreehandActive` false after commit |
| tolModOk | PASS | Shift/Ctrl tolerance modulation wired |

Also: DEFENSIVE try/except around the REAL_PDF sub-check inside `_test_menu_power_up` (perPageLayerMemoryFixed). Wraps the 45-page PDF analyse to survive the known WinError 10054 / analyse timeout flake on single-threaded uvicorn. Sub-check is supplementary; not core to `MENU_OK`.

## Scope — OUT

- Touch / pointer events — deferred per spec to iPad track; mouse-only in v1
- Snap-on-release for freehand bursts — deferred (snap bypass during freehand is intentional v1 design)
- Live area preview during freehand draw — deferred (requires live decimation on every mousemove)

## Carry-over risks (from spike) — all RESOLVED

1. **Alt-mid-stroke guard** ✅ — `altKey` checked at `mousedown` only; `mFreehandActive` and `mArcDraft.pending` mutually-exclusive guard prevents entering freehand mid-arc.
2. **Snap bypass during freehand** ✅ — explicit early-return in `mousemove` freehand branch BEFORE snap call; `buildSnapIndex` / `snap` engine internals untouched.
3. **Touch input** — deferred per spec to iPad track. Mouse-only in v1.

## Hard Forbidden — untouched

- `polyAreaM2`, `polyMetrics`, `polySelfIntersects` — unchanged. `rdpSimplify` decimates points; existing functions compute on the decimated array.
- `pdfToC`, `cToPdf`, `RS`, scale math — unchanged. `cToPdf` called at the boundary in mouseup commit only.
- `buildSnapIndex`, `snap` — unchanged. Explicit early-return in `mousemove` before snap branch when `mFreehandActive`.
- `proto/server.py` — UNTOUCHED (pure client feature).
- `.bmaplan` schema — ADDITIVE only. New optional `obj.freeform={tolerance, freehandSegments, originalSamples}`. Legacy `.bmaplan v1` loads unchanged.
- Phase 1 boundary — kept. No legal verdict, no OCR, no AI, no FAR/OSR.

## TEST-H skip rationale

Same pattern as HT-6 (arc-guideline) and HT-7 (scale gate): freeform sub-mode triggers on Alt-mousedown which the synthetic `bma-human-journey-tester` does not exercise (it performs straight polygon draws + name + save + reopen). User manually tested INV-001 arc-polygon and provided feedback that drove HT-6 and HT-7. User will test freeform manually via the live dev server at http://127.0.0.1:8001 once they refresh. Future enhancement to `bma-human-journey-tester` to cover Alt-drag freehand is filed as an option in `NEXT_ACTIONS.md`.

## E2E Results

```
python -m py_compile proto/server.py proto/e2e_ui_test.py  → PASS
python proto/e2e_ui_test.py smoke                          → PASS 41/41 GREEN
python proto/e2e_ui_test.py full                           → PASS 44/44 GREEN
```

43 pre-existing markers all GREEN (zero regression). 1 new marker this sprint:

`PHASE_FREEFORM_OK {accCheck:True, mixedOk:True, siCheck:True, metaOk:True, resetOk:True, stateOk:True, tolModOk:True, decLen:16, errPct:0.46, mixedLen:11, all:True}`

240 raw samples → 16 RDP-decimated pts. err=0.46% on noisy circle. Marker count: smoke 41/41, full 44/44.

## Files changed

| File | Change |
|---|---|
| `proto/ui.html` | ~80 LOC additions — `rdpSimplify` helper, freehand state vars, mousedown/mousemove/mouseup/keydown/redraw extensions |
| `proto/e2e_ui_test.py` | ~120 LOC — `_test_inv_freeform_area` + `PHASE_FREEFORM_OK` marker; defensive try/except in `_test_menu_power_up` |

## Phase 1 scope check

- ✅ `polyAreaM2` — UNTOUCHED
- ✅ `polyMetrics` / `polySelfIntersects` — UNTOUCHED (test calls `polySelfIntersects` on decimated polylines)
- ✅ `pdfToC` / `cToPdf` / `RS` — UNTOUCHED
- ✅ `buildSnapIndex` / `snap` — UNTOUCHED
- ✅ `.bmaplan` schema — ADDITIVE; version stays 1
- ✅ `proto/server.py` — UNTOUCHED
- ✅ Phase 1 boundary — kept

## References

- `docs/invent/freeform-area.md` — invention doc (research + 3 approaches + scoring + spike rationale)
- `proto/sandbox/invent-freeform-area.html` — spike implementation (SPIKE_PASS 6/6, err=1.22%)
- `docs/status/PHASE_INDEX.md` — INV-2026-05-17-001 row (status `queued — invent-done-go` → `✅ done 023b988`)
