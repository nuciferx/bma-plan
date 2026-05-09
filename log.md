# BMA-Plan — Log (บันทึกเหตุการณ์)

> ไฟล์นี้บันทึกเฉพาะ 2 session ล่าสุด
> ประวัติเต็ม: [docs/archive/log-2026-05-09.md](docs/archive/log-2026-05-09.md)
> อัปเดตทุกครั้งที่: แก้โค้ด / เพิ่มฟีเจอร์ / แก้บั๊ก / รันทดสอบ / ตัดสินใจสำคัญ

---

## 2026-05-09

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
