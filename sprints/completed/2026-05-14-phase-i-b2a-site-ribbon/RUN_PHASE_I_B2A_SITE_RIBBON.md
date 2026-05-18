# RUN_PHASE_I_B2A_SITE_RIBBON — Phase I-B2a: Site Plan Ribbon Group + Shared Handlers

Date: 2026-05-14
Branch: main
Status: PASS — completed 2026-05-14
Run by: Autonomous Dev Loop iteration 1 (supervised — user reviewed before unsupervised loop)

## Goal

เพิ่ม Site Plan ribbon group (`#ribbon-site`) ใน `proto/ui.html` — 7 area buttons + 8 marker buttons แสดงเฉพาะ page ที่ tag === "site". สร้าง handler functions `activateSiteAreaTool` / `setMarkerType` ที่ I-B2b (Measure menu submenu) จะ reuse. แก้ areaType↔semanticTag design wrinkle จาก Phase I-A: ribbon buttons ตั้งค่า `curSiteSemanticTag` override ที่ `finishCurrentArea` อ่านแล้ว consume-and-clear — ไม่ต้อง pollute `AREA_LABELS` legacy model.

## Background — Why I-B2 was split from I-B

Phase I-B2 ถูก `/bma-ui-scope` SPLIT เป็น:
- **I-B2a** (ribbon region) — ribbon DOM + handler logic. Sprint นี้.
- **I-B2b** (menu-bar region) — Measure menu submenu. ใช้ handlers จาก I-B2a โดยตรง.

One sprint = one UI region (UI sprint discipline Pack D).

## Scope — IN

### 1. State variables (`proto/ui.html`)

```js
let curSiteSemanticTag = null;  // consume-and-clear override (one click = one tagged polygon)
let curMarkerType = "parking";  // sticky (default = backward compat)
```

### 2. Ribbon DOM (`proto/ui.html` — inserted before `#status` span)

```html
<div class="ribbon-group" id="ribbon-site" style="display:none">
  <!-- 7 area buttons -->
  <button data-site-tag="building_coverage">พื้นที่อาคาร</button>
  <button data-site-tag="open_space">พื้นที่โล่ง</button>
  <button data-site-tag="permeable_area">พื้นที่ซึมน้ำ</button>
  <button data-site-tag="hardscape">พื้นผิวแข็ง</button>
  <button data-site-tag="softscape">พื้นที่สีเขียว</button>
  <button data-site-tag="parking_area_outdoor">ที่จอดรถ (กลางแจ้ง)</button>
  <button data-site-tag="internal_road">ถนนภายใน</button>
  <!-- 8 marker buttons -->
  <button data-marker-type="parking_disabled">จอดผู้พิการ</button>
  <button data-marker-type="parking_fire">จอดดับเพลิง</button>
  <button data-marker-type="parking_ambulance">จอดพยาบาล</button>
  <button data-marker-type="entrance">ทางเข้า-ออก</button>
  <button data-marker-type="aed">AED</button>
  <button data-marker-type="sign">ป้าย</button>
  <button data-marker-type="fire_escape">ทางหนีไฟ</button>
  <button data-marker-type="fire_elevator">ลิฟต์ดับเพลิง</button>
</div>
```

### 3. Handler functions (`proto/ui.html`)

- `activateSiteAreaTool(semanticTag)` — sets `curSiteSemanticTag` + enters area draw mode
- `setMarkerType(markerType)` — sets `curMarkerType` + enters parking/marker draw mode
- `updateSiteRibbon()` — shows/hides `#ribbon-site` based on `pageTags[curPage]==="site"`
- `updateSiteRibbonActive()` — active-state visual on the 15 buttons (matching curSiteSemanticTag / curMarkerType)

### 4. areaType↔semanticTag bridge (`proto/ui.html` — `finishCurrentArea`)

```js
// in finishCurrentArea poly literal:
semanticTag: curSiteSemanticTag || defaultSemanticTag(curAreaType),
// after push:
curSiteSemanticTag = null;  // consume-and-clear
```

### 5. Marker literal (`proto/ui.html`)

```js
// in mousedown handler (mParking.push):
markerType: curMarkerType || "parking",
```

(was hardcoded `"parking"` from I-B1; now reads the sticky state)

### 6. Hooks

- `activateAreaTool` → `+curSiteSemanticTag = null` (plain area tool clears the override)
- `setMode` → `+updateSiteRibbonActive()` call
- `updateBottomBar` → `+updateSiteRibbon()` call (runs per page change)

### 7. E2E test (`proto/e2e_ui_test.py`)

เพิ่ม `_test_phase_i_b2a_site_ribbon(page)` — 7 sub-checks:

| # | Sub-check | What |
|---|-----------|------|
| ribbonSiteExists | `document.querySelector('#ribbon-site')` ≠ null | DOM group present |
| buttonsWired | `areaBtns:7, markerBtns:8` | correct button counts |
| hiddenOnPlan | `#ribbon-site` display=none on plan page | hide/show logic |
| shownOnSite | `#ribbon-site` visible on site page | hide/show logic |
| siteAreaToolSets | `activateSiteAreaTool('open_space')` → `curSiteSemanticTag==='open_space'` | handler wired |
| sitePolyGetsTag | draw poly after siteAreaTool → poly.semanticTag==='open_space'; `curSiteSemanticTag===null` | bridge + consume-and-clear |
| markerToolSets | `setMarkerType('entrance')` → `curMarkerType==='entrance'` | handler wired |

Marker: `PHASE_I_B2A_OK` (raises `AssertionError` on fail). Runs in smoke + full.

## Scope — OUT

- Phase I-B2b (Measure menu submenu) — next sprint; reuses `activateSiteAreaTool`/`setMarkerType` directly
- Phase I-B3 (Properties panel — buildingHeight_m write-UI + draw-then-classify) — queued
- Phase I-B4 (Site stepper widget) — queued
- Summary Widget "ผังบริเวณ" tab — Phase I-C
- `curSiteSemanticTag` stickiness (keep selected after draw) — FRICTION-level polish, deferred

## Hard Forbidden — must stay untouched

- `polyAreaM2`, `polyMetrics`, `polySelfIntersects`, `pdfToC`, `cToPdf`, `RS`, scale math, snap engine
- `proto/server.py` (ไม่แตะเลย)
- `.bmaplan` schema: `semanticTag` เป็น existing field, additive values only — ไม่ rename/remove, version ยัง 1
- No FAR/OSR auto-judgment, no pass/fail, no verdict UI, no Rule Engine

## E2E Acceptance Criteria

| # | Test | Expect |
|---|------|--------|
| ribbonSiteExists | DOM element `#ribbon-site` present | PASS |
| buttonsWired | areaBtns=7 (`data-site-tag`), markerBtns=8 (`data-marker-type`) | PASS |
| hiddenOnPlan | `#ribbon-site` hidden on plan page | PASS |
| shownOnSite | `#ribbon-site` visible on site page | PASS |
| siteAreaToolSets | `curSiteSemanticTag` set to 'open_space' after `activateSiteAreaTool('open_space')` | PASS |
| sitePolyGetsTag | drawn poly.semanticTag === 'open_space'; `curSiteSemanticTag` cleared after draw | PASS |
| markerToolSets | `curMarkerType` set to 'entrance' after `setMarkerType('entrance')` | PASS |
| — | All 18 existing smoke markers still GREEN — no regression | PASS |

## Test Run

```bash
py -3.12 -m py_compile proto/server.py proto/e2e_ui_test.py  → PASS
py -3.12 proto/e2e_ui_test.py smoke                          → PASS 19/19 markers GREEN
py -3.12 proto/e2e_ui_test.py full                           → PASS 22/22 markers GREEN
```

Note: เครื่องนี้ไม่มี `python3.11` (มี 3.12 + 3.14). `py -3.12` เข้าเกณฑ์ "Python 3.11+" ตาม CLAUDE.md.
One retry needed on smoke first run: `raw is not defined` error — fixed by using plain coords instead of Python helper inside `page.evaluate`.

PHASE_I_B2A_OK: all 7 sub-checks True. Debug output: `{areaBtns:7, markerBtns:8, newTag:'open_space'}`.
No regression: `MAIN_UI_OK.primaryToolCount` still 13; `MENU_OK.menuCounts.measure` still 22; `EXT_MEASURE_OK` parking summary intact.
Baseline (Phase I-B1): smoke 18/18 + full 21/21 GREEN (commit c38c3e6).

## Files Touched

| File | Change |
|---|---|
| `proto/ui.html` | +state `curSiteSemanticTag`/`curMarkerType`; ribbon DOM `#ribbon-site` (15 buttons); 4 new functions; bridge ใน `finishCurrentArea`; `curMarkerType` ใน marker literal; clear ใน `activateAreaTool`; hooks ใน `setMode`/`updateBottomBar` |
| `proto/e2e_ui_test.py` | เพิ่ม `_test_phase_i_b2a_site_ribbon(page)` + marker `PHASE_I_B2A_OK` (7 sub-checks) |
| 7 sprint output files | log.md, PATCH_SUMMARY.md, TEST_RESULT.md, FINAL_REPORT_FOR_CHATGPT.md, CURRENT_STATUS.md, docs/status/LATEST_STATUS.md, docs/status/NEXT_ACTIONS.md |
| `docs/status/PHASE_INDEX.md` | I-B2a → done; I-B2b topmost queued |
