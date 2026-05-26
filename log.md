# BMA-Plan — Log (บันทึกเหตุการณ์)

> ไฟล์นี้บันทึกเฉพาะ 2 session ล่าสุด
> ประวัติเต็ม: [docs/archive/log-2026-05-09.md](docs/archive/log-2026-05-09.md) · [docs/archive/log-2026-05-14.md](docs/archive/log-2026-05-14.md) · [docs/archive/log-2026-05-15.md](docs/archive/log-2026-05-15.md) · [docs/archive/log-2026-05-18.md](docs/archive/log-2026-05-18.md) · [docs/archive/log-2026-05-19.md](docs/archive/log-2026-05-19.md) (BLOAT-1 + BLOAT-2 + 2026-05-19 bundle) · [docs/archive/log-2026-05-20.md](docs/archive/log-2026-05-20.md) (BLOAT-3 + BLOAT-4 + BLOAT-5 + BLOAT-FLAKE-1 + BUG-20260520-sel-midpan + INV-2026-05-20-001 + INV-2026-05-20-002/003/004) · [docs/archive/log-2026-05-21.md](docs/archive/log-2026-05-21.md) (BUG-20260521-lite-menu-clip + LITE-5 + LITE-SNAP/REVIEW/ANNOT/EXPORT/PAGESETUP + LITE-1..4 + LITE-0 + HT-ACC series) · [docs/archive/log-2026-05-22.md](docs/archive/log-2026-05-22.md) (LITE-REPORT INV-2026-05-21-002) · [docs/archive/log-2026-05-24.md](docs/archive/log-2026-05-24.md) (LITE-BUG-2-OPUS47-FINDINGS) · [docs/archive/log-2026-05-25.md](docs/archive/log-2026-05-25.md) (LOVS-1 + LPFL-1 + INV-2026-05-25-001 + Centerline Snap arc + SIM-2)
> อัปเดตทุกครั้งที่: แก้โค้ด / เพิ่มฟีเจอร์ / แก้บั๊ก / รันทดสอบ / ตัดสินใจสำคัญ

---

## 2026-05-26 — BUG-20260526-lite-stale-pf-folder-cleanup — PASS (branch: main)

**What changed:** แก้บั๊กที่ `seedPageFolders()` ใน `lite/static/js/page-folder-layers.js` ไม่เคยลบ PF folder เก่าที่หายออกไปจาก map — `removeFolder` ถูก import ที่ line 8 แต่ไม่เคยถูกเรียก. ผล: ทุกครั้งที่ user re-tag floor page ให้ไม่ใช่ floor, `PF_floor_N` folder + 3 seed layers ("GFA ชั้น N", "หักช่องลิฟต์", "หักช่องบันได") ค้างอยู่เป็น ghost row. Fix เพิ่ม `_pflFolderHasUserDrawnObjects(folderId)` + `_pflPrunePF(activeFolderIds)` internal helpers; `seedPageFolders` เรียก `_pflPrunePF` หลัง add/update loop (ก่อน LFOC-ORDER-A re-rank). Safety guard: folder ที่ยังมี user-drawn objects ในตัว (objects ที่ `catId` ตรงกับ descendant layer) จะไม่ถูก prune — ป้องกันลบงานผู้ใช้โดยไม่ตั้งใจ. Return shape เพิ่ม field `pruned` (additive, in-memory เท่านั้น, ไม่ serialize). Discovery ผ่าน `/bma-simulate` run `basement-order-exclude-stale-20260526T173000` (BUG-HYP-2: `stale_PF_floor_1_exists=true`, 3 lingering layers ยืนยัน CONFIRMED). BUG-HYP-1 (basement-before-floor order) was NOT a bug — `_rankPFFolder` ให้ B1=95, floor1=110 ถูกต้องตาม LFOC-ORDER-A design.

**Why:** ผู้ใช้รายงาน "layer กับ pagesetup น่าจะมีปัญหา กับชั้นใต้ดินใน layer" → `/bma-simulate` ยืนยัน stale PF folder หลัง exclude page. Stale folders ทำให้ UI layer panel เต็มด้วย ghost rows, catlist มี "ชั้น 1" ทั้งที่ page ถูก exclude แล้ว, และอาจ confuse summary/export ที่ iterate layers. Root cause ชัดเจน: `removeFolder` imported แต่ไม่เคย called ทุก sprint ที่ผ่านมาตั้งแต่ LPFL-1.

**Files touched:**
- `lite/static/js/page-folder-layers.js`: +47/-2 (743→790 lines, ≤1000 cap) — added `_pflFolderHasUserDrawnObjects`, `_pflPrunePF`, wired into `seedPageFolders`, return shape adds `pruned`
- `lite/tests/test_pf_cleanup_on_exclude.py`: NEW 168 lines — 4-case Playwright, marker `PF_CLEANUP_OK` (case A basic cleanup / case B safety preservation / case C idempotency / case D PF_excluded never pruned)
- `.claude/skills/bma-simulate/regression_probes.json`: setup_js for LITE-BUG-DBLCLICK-OVER-POP probe updated to call `_lwizAutoLiftLock()` + clear `ov.show` class (partial fix; full probe rewrite deferred to LITE-PROBE-DBLCLICK-REWRITE)

**Tests:**
```
python -m py_compile lite/server_lite.py          → OK
python lite/tests/test_pf_cleanup_on_exclude.py   → PF_CLEANUP_OK 4/4
python lite/tests/test_page_folder_model.py       → LITE_PAGE_FOLDER_MODEL_OK
python lite/tests/test_page_folder_persist.py     → LITE_PAGE_FOLDER_PERSIST_OK
python lite/tests/test_pf_kind_folders.py         → LITE_PF_KIND_OK 11/11
python lite/tests/test_custom_layer_persist.py    → LITE_LAYER_PERSIST_OK
python lite/tests/test_tree_persist.py            → LITE_TREE_PERSIST_OK
/bma-simulate verify re-run                       → PF cleanup VERIFIED PASS (stale_PF_floor_1_exists=false)
Manual e2e verify_dblclick_manual.py              → DBLCLICK_OK (objects=1, pts=4)
```

**Phase 1 scope check:**
- ✅ `polyAreaM2` / `polyMetrics` / `polySelfIntersects` unchanged
- ✅ `pdfToC` / `cToPdf` / `RS` / scale math unchanged
- ✅ `proto/server.py` core endpoints unchanged (proto NOT TOUCHED — lite-only sprint)
- ✅ `.bmaplan` schema additive only (return-value field `pruned` is in-memory, not serialized)
- ✅ No legal / OCR / AI / Rule Engine / FAR-OSR pass-fail
- ✅ `lite/static/js/measure-engine.js` UNCHANGED (drift-locked vendored copy)
- ✅ `lite/ui-lite.html` UNCHANGED (at 1200/1200 cap)

**Known gaps / follow-ups:**
- LITE-PROBE-DBLCLICK-REWRITE (medium priority): Rewrite `LITE-BUG-DBLCLICK-OVER-POP` probe from `mouse_sequence` to `evaluate`-only — directly inject `state.draft` points then dispatch synthetic dblclick event on `cv`. Makes probe robust against future UI workflow changes (wizard auto-open, modal overlays) that block real mouse events.

---

## 2026-05-25 (LOVS-1) — Lite Overview Setup wizard — DONE — branch: main

**Trigger**: user followed up on LPFL-1 — "ในหน้า overview ทำให้ setup page ได้ เหมือน sandbox [wizard-H]" → 1st spike `invent-overview-setup.html` (inline edit only) → user added "ทำ multi-select และทำ tab Number Floors + Review" → spike v2 (3-tab wizard + multi-select) → user `/goal ทำให้เรียบร้อย` → ship LOVS-1.

**What shipped (1 atomic slice)**:
- NEW `lite/static/js/overview-setup.js` (668/900) — 3-tab wizard wraps live `openOv()`:
  - **Step 1 Classify**: tile grid with inline tag-chip cycle + floor-input + **multi-select** (shift+click range / ctrl+click toggle / drag-rectangle box-select / Ctrl+A) → bulk-bar applies tag to all / exclude-toggle. Right-click context menu (multi-select aware). Keyboard 1-6 (bulk if multi), 0 clear, ←→ focus (Shift extends), Enter navigate, X exclude.
  - **Step 2 Number Floors**: floor pages as draggable HTML5 chips → swap floor# on drop. Sequential auto-assigns 1→N (last = `roof` if ≥4 floors). clear.
  - **Step 3 Review**: mock BCR/FAR/OSR report + traceability + warnings.
- EDIT `lite/static/js/page-folder-layers.js` (547 → 557) — 9-line IIFE injects `<script src="static/js/overview-setup.js">` into `document.head` (idempotent via `#__lovs_script__` guard).
- NEW `lite/tests/test_overview_setup.py` — 8 sub-checks Playwright, marker `LITE_OVERVIEW_SETUP_OK`.

**Tests run** (all GREEN):
- `LITE_OVERVIEW_SETUP_OK` 8/8
- `LITE_PAGE_FOLDER_UI_OK` 7/7
- `LITE_PAGE_FOLDER_MODEL_OK` 12/12
- `LITE_PAGE_FOLDER_PERSIST_OK` 6/6
- `LITE_TREE_UI_OK` 9/9
- `LITE_LAYER_DND_OK` 4/4
- `MEASURE_PARITY_OK`

**Forbidden surfaces**: NONE touched (measure-engine.js, RS, pdfToC, cToPdf, area math, semanticTag, snap, .bmaplan schema, layer-system/tree/panel/dnd internals — all UNTOUCHED).

**Size discipline**: `ui-lite.html` STAYED at 1200/1200 (UNTOUCHED). `page-folder-layers.js` 547 → 557 (still <1000). New module 668/900. Cap held cleanly.

**Files**:
- NEW `lite/static/js/overview-setup.js` (668)
- NEW `lite/tests/test_overview_setup.py` (469)
- NEW `lite/sandbox/invent-overview-setup.html` (calibrated spike, 2 iterations — kept as design ref)
- MODIFIED `lite/static/js/page-folder-layers.js` (+9 lines IIFE)
- MODIFIED `lite/sandbox/invent-page-folder-layers.html` (earlier rewrite — workbench loading live modules; kept as canonical LPFL workbench)
- UPDATED `docs/design/LITE_LAYER_ROADMAP.md` (LOVS section)
- UPDATED `docs/status/PHASE_INDEX.md` (LOVS-1 marked done)
- UPDATED `log.md` (this entry)

**Known gaps / follow-ups:**
- none

---

<!-- BUG-20260526-lite-stale-pf-folder-cleanup + LOVS-1 are the 2 sessions kept in this file -->
<!-- LPFL-1 + INV-2026-05-25-001 + Centerline Snap arc + SIM-2 archived to docs/archive/log-2026-05-25.md on 2026-05-26 -->
<!-- LITE-BUG-2-OPUS47-FINDINGS (2026-05-24) archived to docs/archive/log-2026-05-24.md on 2026-05-25 (Centerline Snap sprint) -->
<!-- LITE-REPORT (INV-2026-05-21-002, 2026-05-22) archived to docs/archive/log-2026-05-22.md on 2026-05-24 (SIM-2 sprint) -->
<!-- BUG-20260521-lite-pan-controls archived to docs/archive/log-2026-05-21.md on 2026-05-24 (LITE-BUG-2 sprint) -->
<!-- BUG-20260521-lite-menu-clip + LITE-5 + LITE-SNAP/REVIEW/ANNOT/EXPORT/PAGESETUP + LITE-1..4 + LITE-0 + HT-ACC series archived to docs/archive/log-2026-05-21.md -->
<!-- Earlier 2026-05-20 entries archived to docs/archive/log-2026-05-20.md -->
<!-- BLOAT-2 and BLOAT-1 entries archived to docs/archive/log-2026-05-19.md -->
