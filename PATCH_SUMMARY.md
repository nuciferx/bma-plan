# PATCH_SUMMARY.md — Latest Sprint

> Full patch history: [docs/archive/patch-history-2026-05-09.md](docs/archive/patch-history-2026-05-09.md)

---

# Latest: BUG-20260526-lite-stale-pf-folder-cleanup

Branch: main

Date: 2026-05-26

## Outcome: PASS — Pruned stale PF_floor_N folders + seed layers in lite when their pages re-tagged (with user-object preservation guard). PF_CLEANUP_OK 4/4 + 5 regressions GREEN. Lite-only sprint; proto NOT TOUCHED.

## Summary

`seedPageFolders()` in `lite/static/js/page-folder-layers.js` never removed folders that disappeared from `folderPageMap`. `removeFolder` was imported at line 8 but never called anywhere in the file (grep-verified). Side effect: every time a user re-tagged a floor page to non-floor, the previous `PF_floor_N` folder + its 3 seed layers ("GFA ชั้น N", "หักช่องลิฟต์", "หักช่องบันได") lingered as ghost rows. Two internal helpers added: `_pflFolderHasUserDrawnObjects(folderId)` walks descendant layers and scans `PS[*].objects` for user-drawn objects; `_pflPrunePF(activeFolderIds)` reverse-walks FOLDERS of kind `page-folder`, skips `PF_excluded` and folders with user objects, then removes the rest. `PF_excluded` is never pruned even when empty. All changes are in the module only; `lite/ui-lite.html` untouched (cap 1200/1200).

## Files Changed

| File | Change |
|---|---|
| `lite/static/js/page-folder-layers.js` | +47/-2 (743→790 lines, ≤1000 cap) — added `_pflFolderHasUserDrawnObjects`, `_pflPrunePF`; wired into `seedPageFolders`; return shape adds `pruned` (in-memory only) |
| `lite/tests/test_pf_cleanup_on_exclude.py` | NEW 168 lines — 4-case Playwright marker `PF_CLEANUP_OK`: case A basic cleanup / case B safety preservation / case C idempotency / case D PF_excluded never pruned |
| `.claude/skills/bma-simulate/regression_probes.json` | setup_js for LITE-BUG-DBLCLICK-OVER-POP probe updated to call `_lwizAutoLiftLock()` + clear `ov.show` (partial workaround; full probe rewrite deferred to LITE-PROBE-DBLCLICK-REWRITE) |

## Source Files NOT Touched (Forbidden Surfaces)

- `proto/server.py` — NOT TOUCHED (lite-only sprint; zero proto/ edits)
- `polyAreaM2`, `polyMetrics`, `polySelfIntersects` — UNCHANGED
- `pdfToC`, `cToPdf`, `RS`, scale math — UNCHANGED
- `buildSnapIndex`, `snap` engine — UNCHANGED
- `.bmaplan` schema version stays 1; `pruned` return field is in-memory only, not serialized
- `lite/static/js/measure-engine.js` (drift-locked vendored copy) — UNCHANGED
- `lite/ui-lite.html` — UNCHANGED (at 1200/1200 cap)

## Tests Run

```
python -m py_compile lite/server_lite.py                   → OK
python lite/tests/test_pf_cleanup_on_exclude.py            → PF_CLEANUP_OK 4/4
python lite/tests/test_page_folder_model.py                → LITE_PAGE_FOLDER_MODEL_OK
python lite/tests/test_page_folder_persist.py              → LITE_PAGE_FOLDER_PERSIST_OK
python lite/tests/test_pf_kind_folders.py                  → LITE_PF_KIND_OK 11/11
python lite/tests/test_custom_layer_persist.py             → LITE_LAYER_PERSIST_OK
python lite/tests/test_tree_persist.py                     → LITE_TREE_PERSIST_OK
/bma-simulate verify re-run                                → PF cleanup VERIFIED PASS
                                                             (stale_PF_floor_1_exists=false;
                                                              dom_render_order=[PF_basement_1, PF_floor_2, PF_excluded])
Manual e2e verify_dblclick_manual.py                       → DBLCLICK_OK (objects=1, pts=4)

Proto py_compile + smoke + full NOT re-run (proto untouched; lite-only sprint).
Reference baseline: proto full E2E = 22 markers (PHASE_CENTERLINE_SNAP_OK 10/10, unchanged).
```

## Phase 1 Scope Check

- ✅ `polyAreaM2` / `polyMetrics` / `polySelfIntersects` unchanged
- ✅ `pdfToC` / `cToPdf` / `RS` / scale math unchanged
- ✅ `proto/server.py` core endpoints unchanged (proto NOT TOUCHED — lite-only sprint)
- ✅ `.bmaplan` schema additive only (return-value field `pruned` is in-memory, not serialized)
- ✅ No legal / OCR / AI / Rule Engine / FAR-OSR pass-fail
- ✅ `lite/static/js/measure-engine.js` UNCHANGED (drift-locked vendored copy)
- ✅ `lite/ui-lite.html` UNCHANGED (at 1200/1200 cap)

---

# Previous: Centerline Snap arc (invent 2026-05-24-22-14 → INV-002a proto → INV-002b lite → 2 post-ship bugfixes)

Branch: main

Date: 2026-05-25

## Outcome: PASS — Centerline snap shipped to proto (INV-002a, commit 6db0461) + lite (INV-002b, commit ad920c6); 2 user-reported lite bugs fixed same day (DPR coord mismatch ff3f9fe; button overlap 5783df4). PHASE_CENTERLINE_SNAP_OK 10/10 (maxDelta=0.140%), LITE_CENTERLINE_SNAP_OK 8/8 (maxDelta=0.1778%). All prior baseline markers GREEN. Zero server changes.

## Summary

User reported "วัดที่ดินเส้นปะได้ 3 ค่าต่างกัน" (SCR_ผังต่อโฉนด.pdf, thick dashed cadastral boundary). Correct measurement = stroke centerline. `/bma-invent` 7-phase pipeline (commit `0208314`) selected Approach A: click-time local-ROI Zhang-Suen thinning + post-draw PCA corner refinement. Spike pass 3 achieved maxDelta=0.185% PASS 4/4; user GO + requested lite vendor. INV-002a (proto): NEW `proto/static/js/centerline-snap.js` 208 LOC (Otsu + Zhang-Suen + ROI snap + PCA refine); `proto/ui.html` +15 lines net; E2E +162 lines; PHASE_CENTERLINE_SNAP_OK 10/10. INV-002b (lite): NEW `lite/static/js/centerline-snap.js` 306 LOC (Section A byte-identical to proto per drift-locked vendoring contract, Section B lite glue); `lite/ui-lite.html` +2 net lines (1197→1199 ≤ 1200 cap); LITE_CENTERLINE_SNAP_OK 8/8. Two user-reported bugs fixed same day: DPR coord mismatch (Windows 125/150% scaling → ROI read wrong canvas region → zero effect; fix: multiply CSS coords by dpr before algorithm, divide back after; also added missing `.active` CSS to make toggle visually distinguishable) and CL button overlapping zoom controls (moved from fixed position into `#hud-br` flex-column). Additive schema field: `obj.traceMode = "centerline-roi"` on corrected polygons (optional; legacy .bmaplan loads fine).

## Files Changed

| File | Change |
|---|---|
| `docs/invent/centerline-snap-dashed-boundary.md` | NEW — full 7-phase invent record (PICK→RESEARCH→FRAME→DIVERGE→SCORE→SPIKE→CHECKPOINT) |
| `proto/sandbox/invent-centerline-snap-dashed-boundary.html` | NEW — interactive spike, commit `0208314` |
| `proto/static/js/centerline-snap.js` | NEW 208 LOC — Otsu threshold + Zhang-Suen thinning + CL_snapCanvasToCenterline + CL_refineCornersOnSkeleton (IIFE, no CDN) |
| `proto/ui.html` | +15 lines net — script include, "⊙ CL" Helpers ribbon button, toggleCenterlineSnap() + state, area mousedown click-hook, finishCurrentArea refine call, PREFS.measure.centerlineSnap false, _applyCenterlineSnapPref() |
| `proto/e2e_ui_test.py` | +162 lines — _test_centerline_snap 10 sub-checks + PHASE_CENTERLINE_SNAP_OK |
| `lite/static/js/centerline-snap.js` | NEW 306 LOC — Section A: proto algo byte-identical (drift-locked); Section B: lite glue (CL_litePolyClick + CL_litePolyFinish + floating toggle + localStorage) |
| `lite/ui-lite.html` | +2 net lines (1197→1199, ≤1200 cap) — script include + poly click hook + finishDraft hook; DPR bugfix: dpr multiply/divide + inline .active CSS; button position bugfix: insertBefore #hud-br firstChild |
| `lite/tests/test_centerline_snap.py` | NEW 235 LOC — LITE_CENTERLINE_SNAP_OK Playwright; 6 sub-checks in 002b, expanded to 8 post-bugfix (dprBridge + activeCssRule) |
| `docs/status/PHASE_INDEX.md` | 002a + 002b sprint rows added, backlog flipped, commit hashes backfilled (commit `916d379`) |

## Source Files NOT Touched (Forbidden Surfaces)

- `proto/server.py` — NOT TOUCHED (zero server changes across entire arc; purely client-side feature)
- `polyAreaM2`, `polyMetrics`, `polySelfIntersects` — UNCHANGED (centerline snap is pre-processing, injects corrected pts before area math reads them; uses `getImageData` public API only)
- `pdfToC`, `cToPdf`, `RS`, scale math — UNCHANGED
- `buildSnapIndex`, `snap` engine — UNCHANGED (centerline snap fires only AFTER vector snap found no match)
- `.bmaplan` schema version stays 1; NEW additive `obj.traceMode` optional field only (absent = legacy behavior)
- `lite/static/js/measure-engine.js` (drift-locked vendored copy) — UNCHANGED

## Tests Run

```
python -m py_compile proto/server.py proto/e2e_ui_test.py  → PASS
python proto/e2e_ui_test.py smoke                          → 18/18 PASS
python proto/e2e_ui_test.py full                           → 21/21 PASS
  NEW: PHASE_CENTERLINE_SNAP_OK 10/10 (accuracy maxDelta=0.140%, target ≤0.5%)
  PROJECT_OK + PERSIST_OK confirm obj.traceMode additive field round-trips through save/load

python lite/tests/test_centerline_snap.py  → LITE_CENTERLINE_SNAP_OK 8/8 PASS
  accuracy maxDelta=0.1778% ≤0.5%; dprBridge + activeCssRule regression locks added post-bugfix
python lite/tests/test_measure_parity.py   → MEASURE_PARITY_OK GREEN (no regression)
wc -l lite/ui-lite.html                    → 1199 (≤1200 cap) PASS

TEST-H skipped per AGENTS.md rationale: feature defaults OFF, user must opt-in via Helpers ribbon;
existing journey tester does not toggle Helpers ribbon options; full E2E + 10/8-sub-check synthetic
proof = sufficient verification.

Commit trail: 0208314 (invent spike GO) → 6db0461 (INV-002a proto)
            → ad920c6 (INV-002b lite) → 916d379 (roadmap chore)
            → ff3f9fe (DPR bugfix) → 5783df4 (button position bugfix)
```

## Phase 1 Scope Check

- ✅ `polyAreaM2` / `polyMetrics` / `polySelfIntersects` — UNCHANGED
- ✅ `pdfToC` / `cToPdf` / `RS` / scale math — UNCHANGED
- ✅ `proto/server.py` — NOT TOUCHED
- ✅ `.bmaplan` schema — additive only (`obj.traceMode` optional; version stays 1)
- ✅ No legal / OCR / AI / Rule Engine / FAR-OSR pass-fail (centerline-of-stroke is geometry/snap, in-scope Phase 1)
- ✅ Lite-vendoring contract honored — `measure-engine.js` UNCHANGED; `centerline-snap.js` Section A byte-identical to proto
- ✅ Lite size cap — `ui-lite.html` 1199/1200 (1-line headroom); all `lite/static/js/*.js` ≤1000

---

<!-- SIM-2 (2026-05-24) and older entries archived to docs/archive/patch-history-2026-05-09.md -->
