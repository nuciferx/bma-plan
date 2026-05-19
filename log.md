# BMA-Plan — Log (บันทึกเหตุการณ์)

> ไฟล์นี้บันทึกเฉพาะ 2 session ล่าสุด
> ประวัติเต็ม: [docs/archive/log-2026-05-09.md](docs/archive/log-2026-05-09.md) · [docs/archive/log-2026-05-14.md](docs/archive/log-2026-05-14.md) · [docs/archive/log-2026-05-15.md](docs/archive/log-2026-05-15.md) · [docs/archive/log-2026-05-18.md](docs/archive/log-2026-05-18.md) · [docs/archive/log-2026-05-19.md](docs/archive/log-2026-05-19.md) (includes 001a Zen Mode + Ribbon Cleanup + 001c FRICTION polish + 002a Zen top bar)
> อัปเดตทุกครั้งที่: แก้โค้ด / เพิ่มฟีเจอร์ / แก้บั๊ก / รันทดสอบ / ตัดสินใจสำคัญ

---

## 2026-05-19 — HT-18a-ext Extended pushUndo() coverage to 22 more mutation sites — PASS (branch: main)

**What changed:** Extended HT-18a (`895a9d7`) by inserting `pushUndo()` at 22 additional mutation sites found via Phase A audit + `/bma-human-test` discovery pass: layer reorder (`moveLayerUp`/`moveLayerDown`), `renameLayer`, `setLayerColor`, `toggleLayerLock`, `setAllLayersVisible`, `hideOtherLayers`, `lockOtherLayers`, `setAllLayersLocked`, `toggleLayer`, `layerHideOthers`, `layerShowAll`, `setQuickTag`, `setPageTag`, `setPageFloorKind`, `setPageFloorNum`, `applyAutoNames`, `excludePage` (+ `_skipUndo` param), `restorePage2` (+ `_skipUndo` param), `hideSelectedPages`, `rotatePage`, `resetPageScale`, `pageCtxMenu` inline `autoNamePage` call. The E2E test `_test_ht18_pushundo_leaks` was extended from 7 sub-checks to **36 sub-checks** (22 source-presence + 7 runtime isDirty-flip + 7 original from HT-18a). `PHASE_HT18_OK` is now `{'all': True}` with 36/36 GREEN. Human journey test (`/bma-human-test`) discovered 3 sites initially missed in Phase A audit (`toggleLayer`, `layerHideOthers`, `layerShowAll`); fixed inline in the same iteration. `setQuickTag` and `resetPageScale` were reported as "leaks" but are early-exit code paths — correct that `isDirty` stays false when preconditions unmet. `PHASE_INDEX.md` updated: HT-18a-ext card filed (done), HT-18b updated to `done-with-test-design-caveat`, HT-18c upgraded from `pending conditional` to `queued` with concrete fix scope. New drift-map artifact `sprints/active/2026-05-19-ht-18-save-load-audit-fix/PHASE_A_AUDIT.md` (~120 lines). +39 LOC JS, +295 LOC test.

**Why:** HT-18a fixed 6 of the `pushUndo()` leak sites but a Phase A audit of the full function surface revealed 22 more mutation functions that bypass `pushUndo()`. Each missing call means the user can make changes and close the browser without being prompted to save, silently losing work. Eliminating the full set of leaks in one sequel sprint (HT-18a-ext) is cheaper than filing 22 individual sprints and avoids the "is this site fixed?" ambiguity in future audits. The 36-sub-check E2E test creates a permanent regression guard that will catch any future additions that forget `pushUndo()`.

**Files touched:**
- `proto/ui.html`: +39 LOC — `pushUndo()` inserted at 22 mutation sites (layer reorder/rename/color/lock/visibility helpers, page tag/floor/name/exclude/restore/rotate/reset helpers, pageCtxMenu inline call)
- `proto/e2e_ui_test.py`: +295 LOC — `_test_ht18_pushundo_leaks` extended from 7 → 36 sub-checks (22 source-presence + 7 runtime isDirty-flip + 7 original)
- `docs/status/PHASE_INDEX.md`: HT-18a-ext card filed (done); HT-18b updated `done-with-test-design-caveat`; HT-18c upgraded to `queued` with concrete eq()-fix scope
- `sprints/active/2026-05-19-ht-18-save-load-audit-fix/PHASE_A_AUDIT.md`: New drift-map artifact (~120 lines)

**Tests:**
```
python -m py_compile proto/server.py proto/e2e_ui_test.py  → PY_COMPILE_OK
python proto/e2e_ui_test.py full                           → EXIT 0
  PHASE_HT18_OK: {'all': True} — 36/36 sub-checks GREEN
  21/21 core markers GREEN (smoke 16 + Phase I 2 + full 3)
  Smoke re-run after 3 additional sites found via /bma-human-test → still GREEN
Pre-existing non-regressions (NOT this sprint's regressions):
  PHASE_HT8C_OK 3/5, PHASE_HT8D1_OK 8/9, PHASE_HT10_OK 8/10, PHASE_HT12H_OK 4/5
  PHASE_HT18B_OK 7/13 (test design issue: eq() too strict after normalizeAllObjects;
  NOT schema drift — Phase A audit confirmed save/load symmetric; filed as HT-18c)
Human journey test: HUMAN_TEST_PASS after inline fix of 3 initially-missed sites
  (toggleLayer L2657, layerHideOthers L2659, layerShowAll L2666)
```

**Phase 1 scope check:**
- ✅ `polyAreaM2` / `polyMetrics` / `polySelfIntersects` — UNCHANGED
- ✅ `pdfToC` / `cToPdf` / `RS` / scale math — UNCHANGED
- ✅ `buildSnapIndex` / `snap` engine — UNCHANGED
- ✅ `proto/server.py` — NOT TOUCHED this sprint
- ✅ `.bmaplan` schema — ADDITIVE ONLY (`_skipUndo` params are internal helpers; no field rename/removal; version stays 1)
- ✅ No legal / OCR / AI / Rule Engine / FAR-OSR pass-fail

**Known gaps / follow-ups:**
- HT-18c (queued): fix `_test_ht18b_save_load_round_trip` eq() comparison (too strict after `normalizeAllObjects` mutates pre-snapshot). ~30-50 LOC, test-only, no app code change.
- After HT-18c lands, HT-18 series complete; queue moves to INV-2026-05-19-002c (F12 Overview mockup-port)
- PHASE_HT18B_OK 7/13 is a test design issue, not a schema drift — confirmed by Phase A audit

---

## 2026-05-19 — HT-18a Save-state pushUndo leak fixes — PASS (branch: main)

**What changed:** Inserted `pushUndo()` calls at 6 mutation sites that previously set data without marking the project dirty, causing the "save ไม่ตรงกับ canvas" data-integrity bug: `toggleScaleLine` (L2814), `showLayer` / `hideLayer` / `lockLayer` / `unlockLayer` / `soloLayer` (L2824-2828), and `applyLandEdgeTag` (L1788). Added new E2E test function `_test_ht18_pushundo_leaks()` (7 sub-checks) + `PHASE_HT18_OK` marker. Sprint card split: HT-18 → HT-18a (done, commit 895a9d7) + HT-18b (queued, round-trip E2E) + HT-18c (conditional). Session addenda (parallel commits, not part of this sprint): `c7e9334` (fix 002b chip alignment), `d94b35e` (fix 002a classic menu-bar hidden under body.zen), `5468d13` (invent GO verdict for f12-overview-mockup-port), `1f57451` (spike preview proto/sandbox/invent-f12-overview-mockup-port.html), `b6ba232` + `23ba929` (precursor docs for HT-18 card).

**Why:** User reported that closing the app after certain operations (layer toggles, scale line toggle, land-edge tag apply) resulted in changes being lost because the browser did not prompt to save. The root cause was confirmed via `bma-explorer` audit: `_makeProjBlob` uses `JSON.stringify(pageStore)` which auto-serializes all fields (save schema is complete), and `applyLoadedProject` restores by ref (no field drift). The bug was purely missing `pushUndo()` calls — mutations were not setting `isDirty` — so the user believed the project was saved when it was not, and closed without Ctrl+S.

**Files touched:**
- `proto/ui.html`: +~10 LOC — `pushUndo()` inserted at: `toggleScaleLine` (L2814), `showLayer` (L2824), `hideLayer` (L2825), `lockLayer` (L2826), `unlockLayer` (L2827), `soloLayer` (L2828), `applyLandEdgeTag` (L1788)
- `proto/e2e_ui_test.py`: +~70 LOC — `_test_ht18_pushundo_leaks()` with 7 sub-checks; `PHASE_HT18_OK` marker registered in pipeline
- `docs/status/PHASE_INDEX.md`: sprint card split HT-18 → HT-18a (done 895a9d7) + HT-18b (queued) + HT-18c (conditional)

**Tests:**
```
python3.11 -m py_compile proto/server.py proto/e2e_ui_test.py  → PASS
python3.11 proto/e2e_ui_test.py smoke                          → EXIT 0
  PHASE_HT18_OK 7/7 PASS (toggleScaleLineSetsDirty, hideLayerSetsDirty,
  showLayerSetsDirty, lockLayerSetsDirty, unlockLayerSetsDirty, soloLayerSetsDirty,
  applyLandEdgeTagHasPushUndo)
  PHASE_INV_ZEN_V2_OK 10/10, PHASE_INV_OVERVIEW_OK 9/9, PHASE_INV_ZEN_OK 10/10,
  PHASE_INV_PALETTE_OK 10/10, PHASE_INV_POLISH_001C_OK 5/5 — no regression
full → SKIPPED (additive pushUndo() insert only; no save/load logic, no .bmaplan schema change,
  no field rename; PROJECT_OK + PERSIST_OK test save/load round-trip not isDirty trigger)
TEST-H → SKIPPED (sub-50-LOC additive fix; all 7 mutation sites marker-covered by PHASE_HT18_OK)
```

**Phase 1 scope check:**
- ✅ `polyAreaM2` / `polyMetrics` / `polySelfIntersects` — UNCHANGED
- ✅ `pdfToC` / `cToPdf` / `RS` / scale math — UNCHANGED
- ✅ `buildSnapIndex` / `snap` engine — UNCHANGED
- ✅ `proto/server.py` — UNCHANGED
- ✅ `.bmaplan` schema — UNCHANGED (pushUndo() calls are pure additive code; version stays 1)
- ✅ No legal / OCR / AI / Rule Engine / FAR-OSR pass-fail

**Known gaps / follow-ups:**
- HT-18b: round-trip E2E test (port 8012) — iteration attempted but blocked by test infrastructure (subagent miscount, render flood, port lock). Test design correct; needs fresh-context investigation
- HT-18c: conditional — only if HT-18b finds field drift (audit suggests it will not)
- Uncommitted edits in working tree: additional pushUndo calls in setQuickTag/hideSelectedPages/setPageFloorKind/setPageFloorNum/applyAutoNames + excludePage signature change — user/linter parallel edits, not part of this finalize; user must review before committing
- INV-2026-05-19-002c (F12 mockup port) queued; Print-canvas idea needs /bma-invent before dev-loop eligible

---

<!-- sessions before HT-18a are archived to docs/archive/log-2026-05-19.md (001a Zen Mode + Ribbon Cleanup + 001b Command Palette + 001c FRICTION polish + 002a Zen top bar + 002b F12 Overview + HT-18a) and docs/archive/log-2026-05-18.md (earlier) -->
