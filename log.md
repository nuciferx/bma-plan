# BMA-Plan — Log (บันทึกเหตุการณ์)

> ไฟล์นี้บันทึกเฉพาะ 2 session ล่าสุด
> ประวัติเต็ม: [docs/archive/log-2026-05-09.md](docs/archive/log-2026-05-09.md)
> อัปเดตทุกครั้งที่: แก้โค้ด / เพิ่มฟีเจอร์ / แก้บั๊ก / รันทดสอบ / ตัดสินใจสำคัญ

---

## 2026-05-09

### [session] E2E Test Split Audit

**What changed:**
- Read proto/e2e_ui_test.py (1525 lines) in full.
- Mapped 17 test functions + 9 helper functions.
- Identified irreversible stateful pipeline: test functions share one page object; each
  depends on browser state produced by the previous test.
- Created `docs/design/E2E_TEST_SPLIT_AUDIT.md` with full structure map and risk analysis.
- Decision: AUDIT_ONLY_STOP — splitting test modules is not safe without weakening tests.
  Only helpers (~114 lines, 7.5%) are safely extractable, insufficient to justify refactor.

**Tests:** No code changes. Baseline from proto 9fa57a0 remains valid.

---

### [session] Frontend UI HTML Split

**What changed:**
- Extracted `<style>` block (307 lines) → `proto/static/css/app.css`.
- Extracted 6 semantic constants + 2 functions → `proto/static/js/semantic-meta.js`.
- Extracted 5 opening-parent functions → `proto/static/js/opening-parent.js`.
- Added StaticFiles mount to `proto/server.py` (guarded, 3 lines).
- `proto/ui.html`: 1437 → 1111 lines (-326 lines, -23%).

**Tests:** py_compile PASS · smoke PASS · full PASS (proto 9fa57a0)

---

### [session] Max Token Reduction / File Split

**What changed:**
- Created `proto/export/__init__.py`, `proto/export/semantic_metadata.py`, `proto/export/xlsx_helpers.py`.
- Moved SEMANTIC_*_MAPs, AREA_SEMANTIC_TAGS, _derive_measurement_meta, _get_meta → `export/semantic_metadata.py`.
- Moved _hex_to_rgb, _poly_area_pt2, _line_points, _line_length_pt, _nearest_on_segment, _object_points_for_ref_report, _distance_to_ref, _m2_to_rwu → `export/xlsx_helpers.py`.
- `proto/server.py` now imports all names back — behavior identical.
- Created `docs/design/RUNTIME_FILE_SPLIT_AUDIT.md` (file size + risk analysis).
- Created `docs/design/E2E_SPLIT_PLAN.md` (e2e test split plan, implementation deferred).
- Created `docs/status/READ_ORDER.md` (agent reading guide).
- Updated all status docs (CURRENT_STATUS.md, LATEST_STATUS.md, NEXT_ACTIONS.md, COMMIT_HISTORY.md, PATCH_SUMMARY.md, TEST_RESULT.md, FINAL_REPORT_FOR_CHATGPT.md).

**Tests:** py_compile PASS · smoke PASS · full PASS (proto fb89ecd)

---

### [session] Fast UI Testability Polish (Sprint B)

**What changed:**
- Sprint 1: Empty state card with action buttons + numbered workflow steps 1→6.
- Sprint 2: Topbar zone-a .sep separator between file group and workflow group.
- Sprint 3: Set Scale .scale-cta orange highlight when PDF open but scale not set.
- Sprint 4: `#lp-page-info` strip in sidebar showing page name · tag · scale state.
- Sprint 5: `aria-label` on toolbar groups for testability.
- Sprint 6: `buildLeftProperties()` grouped: Basic / Measurement / Metadata.
- Sprint 7: Right panel Layers title styled; compat note improved.
- Sprint 8: QA warnings grouped by severity: Error / Warning / Info.
- Sprint 9: `#export-readiness` summary bar in export panel.
- Sprint 10: `docs/process/QUICK_TEST_GUIDE.md` created.
- Added rightPanelCompatibilityVisible, rightPanelLayersFirst, leftPanelTabsOk assertions to E2E.

**Tests:** py_compile PASS · smoke PASS · full PASS

---

### [session] Token Reduction / Status File Split

**What changed:**
- Archived full log.md (1624 lines) → `docs/archive/log-2026-05-09.md`.
- Archived PATCH_SUMMARY, TEST_RESULT, FINAL_REPORT history → `docs/archive/`.
- Created 5 new small status files in `docs/status/`: LATEST_STATUS.md, NEXT_ACTIONS.md, TEST_BASELINE.md, COMMIT_HISTORY.md, KNOWN_ISSUES.md.
- Reduced log.md, CURRENT_STATUS.md, PATCH_SUMMARY.md, TEST_RESULT.md, FINAL_REPORT_FOR_CHATGPT.md to current-only.
- Updated index.md to prioritize small status files.
- Sprint card created at sprints/active/RUN_TOKEN_REDUCTION_FILE_SPLIT.md.

**Tests:** No source code changed — no tests required.

---

### [session] Left Properties Migration

**What changed:**
- `proto/ui.html`: added `data-mode` + `onclick="setSidebarMode('...')"` to 3 left-panel tab divs.
- `proto/ui.html`: added `#lp-objects-content` and `#lp-properties-content` hidden divs in HTML.
- `proto/ui.html`: added `lSidebarMode` global, `setSidebarMode(mode)`, `buildLeftObjects()`, `buildLeftProperties()` functions.
- `proto/ui.html`: `selectObjectFromTree`, `_initDrag`, `showObjPicker` row click — each now calls `setSidebarMode("properties")` to auto-switch on object selection.
- `proto/e2e_ui_test.py`: added `leftPanelTabsOk` IIFE to MAIN_UI_OK; added Python assertion.
- Sprint card moved to `sprints/completed/2026-05-09-left-properties-migration/`.

**Tests:** py_compile PASS · smoke PASS · full PASS

---

### [session] Opening Parent Reassignment

**What changed:**
- `linkOpeningParent` in `proto/ui.html`: added `parentManual` guard so manual assignments survive `ensureStoreObjectIds` → `linkOpeningsInStore` cycles.
- `buildRightPanel()` opening case: shows `<select id="rp-opening-parent">` when parentStatus ≠ "linked".
- Added `rpSetOpeningParent(id)` to `proto/ui.html`.
- Extended SELECT_OK in `proto/e2e_ui_test.py` to assert parentSelectVisible and parentReassigned.
- Sprint card moved to `sprints/completed/2026-05-09-opening-parent-reassignment/`.

**Tests:** py_compile PASS · smoke PASS · full PASS

---

> Earlier sessions (Page Scales Audit, Report Target Summary, Export Metadata Columns,
> Measurement Profile Metadata, Right Panel Organization, Mockup V3 UI, etc.)
> are in [docs/archive/log-2026-05-09.md](docs/archive/log-2026-05-09.md)
