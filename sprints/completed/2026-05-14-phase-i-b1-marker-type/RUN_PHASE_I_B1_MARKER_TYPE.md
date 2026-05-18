# RUN_PHASE_I_B1_MARKER_TYPE — Phase I-B1: markerType Additive Field

Date: 2026-05-14 (card written retrospectively — sub-sprint from Phase I-B split)
Branch: main
Status: PASS — completed 2026-05-14

## Goal

เพิ่ม `markerType` เป็น additive field บน marker objects + `MARKER_TYPE_LABELS` registry 9 ประเภท + backfill loop ใน `applyLoadedProject` สำหรับ marker เก่า. ทำก่อนเพื่อปลดล็อก data model ให้ Phase I-B2 (toolbar) และ I-B3 (Properties panel) ต่อยอดได้. ไม่ rename `parkingType` (forbidden `.bmaplan` field rename).

## Background — Why I-B was split

`/bma-measure-scope` (หรือการวิเคราะห์ก่อน sprint) พบว่า Phase I-B ตาม `NEXT_ACTIONS.md` มีงาน 3 ประเภทที่ risk และ surface ต่างกัน:

- **I-B1** (data model only) — `markerType` additive field + backfill. Risk: ต่ำ. Surface: `proto/ui.html` (2 หน่วย) + `proto/e2e_ui_test.py`. ไม่ใช่ UI sprint. ทำก่อนได้ทันที.
- **I-B2** (UI — toolbar) — Ribbon group / Measure menu submenu. Risk: กลาง. ต้องผ่าน `/bma-ui-scope` ก่อน.
- **I-B3** (UI — Properties panel) — buildingHeight_m write-UI + "วาดแล้วค่อยเลือก" semanticTag selector. Risk: กลาง. ต้องผ่าน `/bma-ui-scope` ก่อน.

SPLIT ครั้งนี้ทำให้ I-B1 ไม่ต้องรอ UI scope approval + ลด blast radius ของ sprint แต่ละตัว.

## Scope — IN

### 1. `MARKER_TYPE_LABELS` registry (`proto/ui.html` — ถัดจาก `PARKING_LABELS`)

9 ประเภท:
- `parking` → "ที่จอดรถ"
- `parking_disabled` → "จอดผู้พิการ"
- `parking_fire` → "จอดรถดับเพลิง"
- `parking_ambulance` → "จอดรถพยาบาล"
- `entrance` → "ทางเข้า-ออก"
- `aed` → "เครื่อง AED"
- `sign` → "ป้าย"
- `fire_escape` → "ทางหนีไฟ"
- `fire_elevator` → "ลิฟต์ดับเพลิง"

### 2. `markerType` field ใน marker creation literal (`proto/ui.html`)

ใน `mousedown` handler (`mParking.push({...})`): เพิ่ม `markerType:"parking"` วางข้าง `parkingType:curParkingType` เดิม. ไม่ rename/remove `parkingType`.

### 3. Backfill loop ใน `applyLoadedProject` (`proto/ui.html`)

```js
// Backfill markerType for legacy markers
(store.parking || []).forEach(m => {
  if (!m.markerType) m.markerType = "parking";
});
```

Marker เก่าทุกตัวในไฟล์ `bmaplan` ก่อนหน้านี้เป็น parking marker — backfill เป็น `"parking"` ถูกต้อง.

### 4. E2E test (`proto/e2e_ui_test.py`)

เพิ่ม `_test_phase_i_b1_marker_type(page)`:
- **registryComplete**: `MARKER_TYPE_LABELS` มีครบ 9 ตัว, label ไม่ว่าง, `MARKER_TYPE_LABELS['fire_escape']` === "ทางหนีไฟ"
- **markerTypeRoundTrips**: สร้าง marker → save → load → `markerType` ยังอยู่, `parkingType` ไม่เปลี่ยน
- **backfillWorks**: `applyLoadedProject` กับ project เก่า (marker ไม่มี `markerType`) → `markerType` === `"parking"`, `parkingType` คงเดิม

Marker ใหม่: `PHASE_I_B1_OK` (raise `AssertionError` ถ้า fail). รันใน smoke + full ทั้งคู่.

## Scope — OUT (later sprints)

- ❌ Site Plan toolbar buttons / Ribbon group สำหรับ 7 area type → **Phase I-B2** (UI sprint)
- ❌ buildingHeight_m write-UI (Properties panel input) → **Phase I-B3** (UI sprint)
- ❌ "วาดแล้วค่อยเลือกว่าเป็นอะไร" Properties-panel semanticTag selector → **Phase I-B3**
- ❌ เครื่องมือวาง marker type ใหม่ (parking_fire/entrance/aed/...) → **Phase I-B2** (ต้องมี toolbar ก่อน)
- ❌ Summary Widget "ผังบริเวณ" tab → **Phase I-C**

## Hard Forbidden — must stay untouched

- `polyAreaM2`, `polyMetrics`, `polySelfIntersects`, `pdfToC`, `cToPdf`, `RS`, scale math, snap engine
- `proto/server.py` (ไม่แตะเลย)
- `.bmaplan` schema: `markerType` เป็น additive new field ONLY — `parkingType` ห้าม rename/remove, version ยัง 1
- No FAR/OSR auto-judgment, no pass/fail, no verdict UI, no Rule Engine

## E2E Acceptance Criteria

| # | Test | Expect |
|---|------|--------|
| registryComplete | `MARKER_TYPE_LABELS` มี 9 entries; `MARKER_TYPE_LABELS['fire_escape']` === "ทางหนีไฟ"; ไม่มี label ว่าง | PASS |
| markerTypeRoundTrips | สร้าง marker → JSON round-trip → `markerType` ยังอยู่; `parkingType` ไม่เปลี่ยน; `EXT_MEASURE_OK` ยัง PASS | PASS |
| backfillWorks | `applyLoadedProject` กับ project เก่าที่ marker ไม่มี `markerType` → backfill เป็น `"parking"`; `parkingType` คงเดิม | PASS |
| — | All 17 existing smoke markers still GREEN — no regression | PASS |

## Test Run

```bash
py -3.12 -m py_compile proto/server.py proto/e2e_ui_test.py  → PASS
py -3.12 proto/e2e_ui_test.py smoke                          → PASS 18/18 markers GREEN
py -3.12 proto/e2e_ui_test.py full                           → PASS 21/21 markers GREEN
```

Note: เครื่องนี้ไม่มี `python3.11` (มี 3.12 + 3.14). `py -3.12` เข้าเกณฑ์ "Python 3.11+" ตาม CLAUDE.md.

PHASE_I_B1_OK: registryComplete=True, markerTypeRoundTrips=True, backfillWorks=True — all 3 sub-checks GREEN.
EXT_MEASURE_OK: ยืนยัน parking summary ปกติ — `parkingType` ไม่มี regression.
Baseline (Phase I-A): smoke 17/17 + full 20/20 GREEN (commit 984eb7e).

## Files Touched

| File | Change |
|---|---|
| `proto/ui.html` | เพิ่ม `MARKER_TYPE_LABELS` (9 entries) ถัดจาก `PARKING_LABELS`; เพิ่ม `markerType:"parking"` ใน `mParking.push({...})`; เพิ่ม backfill loop ใน `applyLoadedProject` |
| `proto/e2e_ui_test.py` | เพิ่ม `_test_phase_i_b1_marker_type(page)` + marker `PHASE_I_B1_OK` (3 sub-checks) |
| `CLAUDE.md` | อัปเดต Expected E2E success markers: smoke 18 (+ PHASE_I_B1_OK), full 21 (+ PHASE_I_B1_OK) |
| 7 sprint output files | log.md, PATCH_SUMMARY.md, TEST_RESULT.md, FINAL_REPORT_FOR_CHATGPT.md, CURRENT_STATUS.md, docs/status/LATEST_STATUS.md, docs/status/NEXT_ACTIONS.md |
