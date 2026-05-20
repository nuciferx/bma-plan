# BMA-Plan — Log (บันทึกเหตุการณ์)

> ไฟล์นี้บันทึกเฉพาะ 2 session ล่าสุด
> ประวัติเต็ม: [docs/archive/log-2026-05-09.md](docs/archive/log-2026-05-09.md) · [docs/archive/log-2026-05-14.md](docs/archive/log-2026-05-14.md) · [docs/archive/log-2026-05-15.md](docs/archive/log-2026-05-15.md) · [docs/archive/log-2026-05-18.md](docs/archive/log-2026-05-18.md) · [docs/archive/log-2026-05-19.md](docs/archive/log-2026-05-19.md) (BLOAT-1 + BLOAT-2 + 2026-05-19 bundle) · [docs/archive/log-2026-05-20.md](docs/archive/log-2026-05-20.md) (BLOAT-3 + BLOAT-4 + BLOAT-5 + BLOAT-FLAKE-1 + BUG-20260520-sel-midpan + INV-2026-05-20-001 + INV-2026-05-20-002/003/004)
> อัปเดตทุกครั้งที่: แก้โค้ด / เพิ่มฟีเจอร์ / แก้บั๊ก / รันทดสอบ / ตัดสินใจสำคัญ

---

## 2026-05-20 — BUG-20260520-zen-exit-rp-restore — PASS (branch: main)

**What changed:** Defensive fix making the right panel always recoverable after Zen Mode exits. Three coordinated changes: (1) F11 keydown handler now calls `preventDefault()` unconditionally so the browser can never enter native fullscreen and leave `body.zen` stuck — Zen exit (`if(body.zen || ...)`) always works; entering Zen is still blocked mid-draw or when a modal is open. (2) F9/F10 keybindings added — F9 calls `toggleLeftPanel`, F10 calls `toggleRightPanel`; the restore tabs already advertised [F9]/[F10] labels but had no handler wired. (3) `proto/static/css/app.css`: dead sibling selector `#right-panel.collapsed~#workspace #rp-restore-tab` (workspace precedes panel in DOM so `~` never matched) replaced with `body:has(#right-panel.collapsed) #rp-restore-tab{display:flex}`; the existing attribute-based fallback `.canvas-wrap[data-right-collapsed="1"]` kept. New E2E test `_test_bug_zen_exit_rp_restore` + marker `BUG_20260520_ZEN_EXIT_RP_RESTORE_OK` (6 sub-checks).

**Why:** User-reported: after hiding L+R panels → F11 Zen → exit to normal, the restore tab (`#rp-restore-tab`) was gone and the right panel could not be re-shown. Headless repro (3 variants in `artifacts/repro_zen_exit_rp.py`) could not reproduce — tab returned to flex in Playwright. Lead hypothesis: real-browser native F11 fullscreen collides with the app F11 `!anyModal && !mPts.length` guard; when a modal is open or mid-draw, `preventDefault` was skipped, the browser entered native fullscreen, and `body.zen` desynced/stayed stuck causing `body.zen .panel-restore-tab{display:none}` to hide the tab permanently. Fix is defensive — recoverable regardless of exact trigger.

**Files touched:**
- `proto/ui.html`: F11 handler — unconditional `preventDefault()` + widened exit condition; F9→`toggleLeftPanel` + F10→`toggleRightPanel` added
- `proto/static/css/app.css`: `#right-panel.collapsed~#workspace #rp-restore-tab` dead rule replaced with `:has()` selector; zen/overview `display:none !important` overrides unchanged
- `proto/e2e_ui_test.py`: `_test_bug_zen_exit_rp_restore` (+6 sub-checks) + `BUG_20260520_ZEN_EXIT_RP_RESTORE_OK` marker wired into `main()`

**Tests:**
```
py_compile proto/server.py proto/e2e_ui_test.py                → PASS
proto/e2e_ui_test.py full                                       → EXIT 0 (101 _OK markers, 0 E2E_FAIL)
  NEW: BUG_20260520_ZEN_EXIT_RP_RESTORE_OK GREEN (6 sub-checks:
       inZen, zenExitedMidDraw, f10Toggled, tabVisibleWhenCollapsed,
       tabHiddenInZen, tabVisibleAfterZenExit)
  CACHE_OK / MAIN_UI_OK (cssLinkPresent + cssVarLoaded true) — CSS still serves
  All prior 100 markers retained. Zero regression.
```

**Phase 1 scope check:**
- ✅ `polyAreaM2` / `polyMetrics` / `polySelfIntersects` — UNCHANGED
- ✅ `pdfToC` / `cToPdf` / `RS` / scale math — UNCHANGED
- ✅ `buildSnapIndex` / `snap` engine — UNCHANGED
- ✅ `proto/server.py` — NOT TOUCHED
- ✅ `.bmaplan` schema — additive only (untouched; version stays 1)
- ✅ No legal / OCR / AI / Rule Engine / FAR-OSR pass-fail

**Known gaps / follow-ups:**
- Static CSS touched → `UI_MANUAL_TEST.md` updated with 5-check Zen exit / F9/F10 / restore-tab checklist.
- Headless repro could not reproduce the original trigger — fix is defensive. Real-browser manual test (checklist item 3: open modal then F11) is the only way to confirm the native-fullscreen desync path is closed.
- Commit: `9453777` on main.

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

<!-- BUG-20260520-zen-exit-rp-restore and INV-2026-05-20-002/003/004 Layer L1+L2+L3 are the 2 sessions kept in this file -->
<!-- INV-2026-05-20-001 Verify Scale + earlier 2026-05-20 entries archived to docs/archive/log-2026-05-20.md -->
<!-- BLOAT-2 and BLOAT-1 entries archived to docs/archive/log-2026-05-19.md -->
