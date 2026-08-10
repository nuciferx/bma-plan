# patch-history archive — rotated out on 2026-08-10 (ค่ำ finalize)

> Archived from `PATCH_SUMMARY.md`'s "Previous" slot to make room for the 2026-08-10 (ค่ำ) PKG-PORTABLE + PM-REDESIGN-D + SHELL sprint.

---

# BUG-20260706-lite-layer-page-binding — active-layer-not-following-page + multi-site-page-tag (lite)

Date: 2026-07-06 · Area: layer / page-tagging (lite) · 1 commit, lite-only, proto untouched

Two user-reported field bugs fixed together, both traced to the page↔layer binding introduced by `INV-2026-07-04-001`. Bug 1 (`BUG-20260706-lite-active-layer-not-following-page`, BROKEN — data-correctness): `_lsSyncActiveCatToFolder` had no fallback for a folder never visited this session, so `state.activeCat` stayed on the previous folder's layer — measurements landed in the wrong floor's layer silently, confirmed by a user screenshot on page 29 (roof) still showing "ผังบริเวณ · ที่ดิน (ซ่อน)". Fixed with (a) fallback to the folder's first layer in model order, (b) a new `lsForeignDrawBlocked()` commit-path guard called from `finishDraft()` + the count tool, warning via `state.hintFlash` (the direct `#hint` write was found to be wiped by `draw()`→`updateHUD()` on the test's first run — caught and fixed same session). Bug 2 (`BUG-20260706-lite-multi-site-page-tag`, FRICTION): `_lsGoTo` always warped to `pages[0]`, so a 2-sheet site plan's second sheet was unreachable from the floor-rail/dropdown/search nav surface — correctly tagged and aggregated but never drawn. Fixed by making `_lsGoTo` page-aware (same folder re-selected steps to the next page and wraps; arriving from another folder goes to `pages[0]`) and the rail ◀/▶ stepping pages within a folder before crossing folders; counter now shows "ชั้น i/N · แผ่น i/N".

**Commits:** `ba109f0`

**Files touched:** `lite/static/js/layer-scope.js` (+96/-17), `lite/ui-lite.html` (+2 guard call lines, 1189/1200 cap), `lite/tests/test_layer_scope.py` (6→9 checks, +140 lines)

**Closes:** BUG-20260706-lite-active-layer-not-following-page, BUG-20260706-lite-multi-site-page-tag

---
