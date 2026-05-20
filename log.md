# BMA-Plan — Log (บันทึกเหตุการณ์)

> ไฟล์นี้บันทึกเฉพาะ 2 session ล่าสุด
> ประวัติเต็ม: [docs/archive/log-2026-05-09.md](docs/archive/log-2026-05-09.md) · [docs/archive/log-2026-05-14.md](docs/archive/log-2026-05-14.md) · [docs/archive/log-2026-05-15.md](docs/archive/log-2026-05-15.md) · [docs/archive/log-2026-05-18.md](docs/archive/log-2026-05-18.md) · [docs/archive/log-2026-05-19.md](docs/archive/log-2026-05-19.md) (BLOAT-1 + BLOAT-2 + 2026-05-19 bundle) · [docs/archive/log-2026-05-20.md](docs/archive/log-2026-05-20.md) (BLOAT-3 + BLOAT-4 + BLOAT-5 + BLOAT-FLAKE-1 + BUG-20260520-sel-midpan + INV-2026-05-20-001)
> อัปเดตทุกครั้งที่: แก้โค้ด / เพิ่มฟีเจอร์ / แก้บั๊ก / รันทดสอบ / ตัดสินใจสำคัญ

---

## 2026-05-20 — INV-2026-05-20-002/003/004 Layer model rebuild L1+L2+L3 — PASS (branch: main)

**What changed:** Three-commit layer-model rebuild that makes the page-scoped layer system the single authoritative source for render, hit-test, visibility, and lock — replacing the old dual-system where global `areaTypeLayer` + `layerVis`/`layerLock` conflicted with `pageStore[n].layers`. L1 (`93c512f`): `validLayerSlugForPage()` guarantees an object's slug exists in its page preset (maps `land` → `site_boundary` on site pages, etc.); `getObjectLayerSlug()` resolves openings → deduction, refs/lines → reference_geometry; all render/hit/label/snap paths (`hitTest`, `hitTestAll`, `hitVertex`, `findNearest`, `drawRefLines`) now read the object's page-scoped layer via new `_slugVisible`/`_slugLocked`/`_objLayerVisible`/`_objLayerLocked` helpers instead of the global maps. L2 (`1301a12`): `reassignSelectedObjectLayer()` + "Layer" `<select>` dropdown in right+left properties panels (Bluebeam-style move-to-layer UX); `objLayerKey()` now reports the object's real slug. L3 (`2e6b2f9`): `_layerLockGateBeforeMode` + `toggleLayerLock` deselect repointed to page-scoped `_slugLocked`/`getObjectLayerSlug`; global `layerVis`/`layerLock` demoted to a non-authoritative synced mirror (toggles still write them for test/legacy compat, but nothing reads them for behaviour). `proto/e2e_ui_test.py` gained 3 new test functions (`_test_inv_layer_l1`, `_test_inv_layer_l2`, `_test_inv_layer_l3`) and 3 markers; existing HT8D5A lock test repointed to page-layer authority.

**Why:** User-reported bug on ผังบริเวณ (site plan) pages: measured objects went to the wrong layer and overlapped, couldn't be separated or toggled. Root cause was the incomplete page-scoped layer migration: two competing systems coexisted — the page-scoped `pageStore[n].layers` (authoritative by design) vs. the legacy global `areaTypeLayer`/`layerVis`/`layerLock` (still read by render/hit paths). Site plan objects with `areaType="room"` collapsed to slug `"sub_area"` which doesn't exist in the site page preset, producing `layerId = undefined` and complete overlap. The full rebuild closes this gap: one source of truth, zero phantom slugs.

**Files touched:**
- `proto/ui.html`: layer helpers (`validLayerSlugForPage`, `getObjectLayerSlug`, `_slugVisible`, `_slugLocked`, `_objLayerVisible`, `_objLayerLocked`); slug assignment at object creation; render/hit/label/lock-gate paths updated; `reassignSelectedObjectLayer` + Layer dropdown in properties panels; global `layerVis`/`layerLock` demoted to mirror role
- `proto/e2e_ui_test.py`: +3 test functions (`_test_inv_layer_l1/l2/l3`) + 3 markers (`INV_LAYER_L1_OK` / `INV_LAYER_L2_OK` / `INV_LAYER_L3_OK`) + HT8D5A repointed to page-layer authority

**Tests:**
```
py_compile proto/server.py proto/e2e_ui_test.py           → PASS
proto/e2e_ui_test.py full                                  → EXIT 0 (100 _OK markers, 0 E2E_FAIL)
  NEW: INV_LAYER_L1_OK GREEN — slug guarantee + render/hit authority
  NEW: INV_LAYER_L2_OK GREEN — reassign-layer UI + objLayerKey real slug
  NEW: INV_LAYER_L3_OK GREEN — page locked + global unlocked → app follows page
  HT8D5A all:True (lock test restored after repoint)
  Pre-existing cosmetic all:False markers (HT8C/HT8D1/HT10/HT12H/PHASE_I_D) — unchanged
  Zero regression introduced by this sprint.
```

**Phase 1 scope check:**
- ✅ `polyAreaM2` / `polyMetrics` / `polySelfIntersects` — UNCHANGED
- ✅ `pdfToC` / `cToPdf` / `RS` / scale math — UNCHANGED
- ✅ `buildSnapIndex` / `snap` engine — UNCHANGED
- ✅ `proto/server.py` — NOT TOUCHED
- ✅ `.bmaplan` schema — additive only (`layerSlug`/`layerId` already existed; no renames; version stays 1)
- ✅ No legal / OCR / AI / Rule Engine / FAR-OSR pass-fail

**Known gaps / follow-ups:**
- Literal deletion of `layerVis`/`layerLock` identifiers from call sites — deferred (test-only churn, zero behaviour gain; mirror write retained for legacy compat).
- Active-layer-at-creation routing (L1 default mapping + L2 reassign already cover user need) — deferred.
- `UI_MANUAL_TEST.md` updated with 5-check layer-rebuild manual checklist.
- Commits: `93c512f` (L1), `1301a12` (L2), `2e6b2f9` (L3). PHASE_INDEX rows INV-2026-05-20-002/003/004 → mark done.

---

## 2026-05-20 — INV-2026-05-20-001 Verify Scale tool — PASS (branch: main)

**What changed:** Replaced the `verifyScale()` stub with a real second-reference cross-check flow: Scale-menu "Verify Scale" reuses the existing 2-point calibration draw, then `verifyFinish()` computes `%dev = 100·|d_meas−d_enter|/d_enter` and shows `#verify-modal` with a color-coded confidence band (green <0.5% / yellow <2% / red ≥2%) plus measured distance, entered distance, area-impact estimate (≈2×%dev), and three action buttons: Accept / Re-calibrate / Average. A `calibPanelOk()` router was added so the calib panel OK button routes to `verifyFinish()` in verify mode and to `finishCalib()` otherwise — `finishCalib()` body unchanged. Schema additive: `calibScale.verifyResult{pct, action, verifyPts_per_m, ts}` round-trips through existing save/load automatically.

**Why:** Calibration-by-single-reference gives no quality signal — a mis-click or misread dimension passes silently. Verify Scale closes this gap with a second known dimension and a numeric %dev band (green/yellow/red), giving three actionable recovery paths. Approach A from the invent pipeline GO verdict (spike 10/10 in `proto/sandbox/invent-verify-scale.html`).

**Files touched:**
- `proto/ui.html`: +82/−5 — calib panel h3 id + OK→`calibPanelOk`; `#verify-modal` HTML block; 10 new fns (`verifyScale`, `verifyFinish`, `openVerifyModal`, `_verifyBand`, `_verifyWriteResult`, `_afterVerifyScaleChange`, `verifyAccept`, `verifyRecalibrate`, `verifyAverage`, `closeVerifyModal`); `cancelCalib` reset; `anyModal` guard extended
- `proto/e2e_ui_test.py`: +124 lines — `_test_verify_scale` (9 sub-checks) + `INV_VERIFY_SCALE_OK` marker wired into `main()`

**Tests:**
```
py_compile proto/server.py proto/e2e_ui_test.py           → PASS
proto/e2e_ui_test.py full                                  → EXIT 0
  NEW: INV_VERIFY_SCALE_OK = 9/9 all:True
  ANNOT_OK / PERSIST_OK / REAL_OK / PROJECT_OK / XLSX_OK / PATH_GEOMETRY_OK — GREEN
  Pre-existing 5 env-artifact markers unchanged. Zero regression.
```

**Phase 1 scope check:**
- ✅ `polyAreaM2` / `polyMetrics` / `polySelfIntersects` — UNCHANGED
- ✅ `pdfToC` / `cToPdf` / `RS` / scale math — UNCHANGED
- ✅ `buildSnapIndex` / `snap` engine — UNCHANGED
- ✅ `proto/server.py` — NOT TOUCHED
- ✅ `.bmaplan` schema — additive only (`calibScale.verifyResult` optional field; version stays 1)
- ✅ `finishCalib()` — UNCHANGED (`calibPanelOk` wrapper routes to it)
- ✅ No legal / OCR / AI / Rule Engine / FAR-OSR pass-fail

**Known gaps / follow-ups:**
- Follow-on E (fold verifyResult into phase1Warnings + export note) — deferred.
- Follow-on D (live canvas badge showing %dev) — deferred.
- Follow-on C (dual-axis H/V stretch detector) — deferred.
- `BUG-20260520-zen-exit-rp-restore` parked at `BUG_STOP_NEEDS_REPRO`.

---

<!-- INV-2026-05-20-002/003/004 Layer L1+L2+L3 and INV-2026-05-20-001 Verify Scale are the 2 sessions kept in this file -->
<!-- BUG-20260520-sel-midpan, BLOAT-FLAKE-1, BLOAT-5, BLOAT-4, BLOAT-3 archived to docs/archive/log-2026-05-20.md -->
<!-- BLOAT-2 and BLOAT-1 entries archived to docs/archive/log-2026-05-19.md -->
