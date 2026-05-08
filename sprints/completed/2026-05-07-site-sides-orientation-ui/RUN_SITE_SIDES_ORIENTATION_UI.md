# RUN_SITE_SIDES_ORIENTATION_UI.md — BMA-Plan Site Sides + Orientation + Tool UI Cleanup

## Goal

Add editable land-side metadata UI, add orientation / north-direction support, and clean up the measurement tool UI so it matches the approved design direction more closely.

This sprint combines 3 related needs:

1. Land parcel / site boundary sides already appear to have internal side definitions during parcel-frame creation, but there is no proper UI to inspect/edit them.
2. Site orientation / north direction is missing and must be added.
3. The tool UI and font styling should be improved to match the approved mockup direction and be easier to use.

This sprint is still Phase 1 factual support only.
Do not add legal checking.

---

## Product Goal Context

Phase 1 must help users produce usable work output:

1. open construction-plan PDF
2. setup project/page metadata
3. measure areas manually
4. define site/parcel facts
5. save/reopen work
6. export Excel report
7. export annotated PDF

Legal/building-control skill is Phase 2 and must not be added here.

---

## Current Problems

### A. Parcel side metadata has no editing UI

The code appears to already define sides of the land parcel when creating the parcel boundary/frame, but there is no proper UI for users to inspect or edit side labels/roles.

Need:
- editable side metadata
- visible menu / properties UI
- persistence in project state

### B. Orientation / north direction is missing

The app currently has no proper tool/UI for:
- north arrow
- site orientation
- road/front side orientation relationship

Need:
- a manual north-direction tool
- visible orientation state
- save/load support
- export/audit support if safe

### C. Tool UI is still not aligned enough with the approved design

Need:
- cleaner tool grouping
- less clutter
- font easier to read and closer to the design mockup
- no fake redesign, but clear usability improvement

---

## Required Reading

Read first:

1. `AGENTS.md`
2. latest entry in `log.md`
3. `index.md`
4. `CURRENT_STATUS.md` if it exists
5. `FINAL_REPORT_FOR_CHATGPT.md`
6. `TEST_RESULT.md`
7. `UI_MANUAL_TEST.md`
8. `proto/ui.html`
9. `proto/server.py`
10. `proto/e2e_ui_test.py`

---

## Scope

Do only the following:

1. Add UI to inspect/edit site boundary / parcel side definitions.
2. Add orientation / north direction support.
3. Add a visible menu or properties editor for parcel sides and site orientation.
4. Improve tool UI to be closer to the approved design.
5. Improve typography / font stack for usability.
6. Preserve all existing core workflows.

Do not add legal interpretation logic.

---

## Part 1 — Parcel Side Editing UI

### Requirement

If parcel boundary / site frame creation already stores per-side definitions internally, expose them in UI.

Users must be able to inspect and edit land-side data.

### Expected UI Behavior

When a parcel / site boundary object is selected, show a section in the Properties panel:

```text
ข้อมูลด้านที่ดิน
- ด้านที่ 1
- ด้านที่ 2
- ด้านที่ 3
- ด้านที่ 4

For each side, provide editable fields such as:

ชื่อด้าน / Label
บทบาทของด้าน:
ด้านหน้า
ด้านหลัง
ด้านซ้าย
ด้านขวา
ด้านติดถนน
ด้านติดที่ดินข้างเคียง
อื่น ๆ
หมายเหตุ (optional)

If side order/orientation already exists internally, preserve it.

If side roles do not yet exist, add a safe minimal structure.

Suggested Data Shape

Use or extend existing project state safely.

Example conceptual structure:

{
  "parcelMeta": {
    "page": 1,
    "parcelId": "SITE-1",
    "sides": [
      { "index": 1, "label": "ด้านหน้า", "role": "front", "note": "ติดถนน" },
      { "index": 2, "label": "ด้านขวา", "role": "right", "note": "" },
      { "index": 3, "label": "ด้านหลัง", "role": "rear", "note": "" },
      { "index": 4, "label": "ด้านซ้าย", "role": "left", "note": "" }
    ]
  }
}

If parcel geometry can have more than 4 sides, support arbitrary side count.

Important

Do not fake this UI.
If side metadata does not exist yet, implement the smallest safe model so it can be edited and stored.

Part 2 — Orientation / North Direction
Requirement

Add a system for defining north direction manually.

Tool

Add a tool/menu item:

ตั้งทิศเหนือ

Suggested behavior:

click base point
click north-point direction
store vector
compute angle if safe
Optional Additional Site Orientation Support

If safe, also allow defining:

ด้านติดถนน / แนวหน้าแปลง

This may be:

a dedicated line tool
or a metadata assignment from a selected parcel side
Properties Panel

When north/orientation is selected or available, show:

page
angle
source = manual
status = verified
label = ทิศเหนือ
Suggested Data Shape
{
  "siteOrientation": {
    "1": {
      "north": {
        "x1": 0,
        "y1": 0,
        "x2": 0,
        "y2": 0,
        "angleDeg": 0,
        "source": "manual",
        "status": "verified"
      }
    }
  }
}
Canvas Overlay

Show a visible north arrow overlay:

N / ทิศเหนือ
clear but not noisy
separate from area/opening rendering
Warnings

If a page appears to be a site plan / parcel page and has no orientation, add warning if safe:

หน้าผังบริเวณยังไม่ได้ตั้งทิศเหนือ

Do not turn this into legal pass/fail.

Part 3 — Tool UI Cleanup
Goal

Make tool UI closer to the approved design.

Requirements
Tool group should be clearer and visually cleaner.
Keep primary tools visible and easy to use.
Keep secondary tools grouped cleanly if already supported.
Do not duplicate layer controls.
Maintain right panel as main layer management area.
Suggested Primary Tool Set

Keep clearly visible:

เลือก
วาดพื้นที่
วาดช่องเปิด
เส้นอ้างอิง
ตั้ง Scale
วัดระยะ
ตั้งทิศเหนือ
กรอบที่ดิน / ผังบริเวณ (if parcel/site tool exists)

If there are too many tools, keep primary tools visible and move less-used items to a More/เพิ่มเติม menu.

Active Layer

Keep compact:

Layer: พื้นที่หลัก ▼

Do not reintroduce duplicated layer visibility/lock controls in the toolbar.

Part 4 — Font / Typography Improvement
Goal

Use a cleaner, easier-to-read font stack closer to the approved design.

Requirement

Update font usage to be easier for Thai UI.

Use a safe modern font stack such as:

font-family:
  "Inter",
  "Noto Sans Thai",
  "Sarabun",
  system-ui,
  sans-serif;

If web font loading is unsafe or unavailable, use a safe local-first stack.

Typography Expectations
clearer Thai readability
cleaner label hierarchy
more consistent button/input text
improved sidebar/tool readability

Do not do a decorative redesign.

Save / Load Requirements

New state must persist safely in .bmaplan project state:

parcel side metadata
site orientation / north arrow
any related labels/notes if added

Do not implement Project PDF Save/Load in this sprint.

Export Requirements

If safe, include new factual data in export:

XLSX / Audit

Add to an existing audit sheet or a new sheet only if safe:

parcel side metadata
north angle / orientation status
front/road side status

Minimum acceptable:

enough data appears in audit output or warnings

Do not break existing export sheets.

Behavior That Must Not Change

Do not break:

Project Setup UI
PDF upload
page thumbnails
Start Measuring transition
measurement canvas
manual scale
draw area
draw opening
overlapping picker
layer visibility
layer lock
properties panel
object tree
XLSX export
annotated PDF export
.bmaplan save/load
Forbidden

Do not add:

OCR
AI checker
legal rules
automatic legal pass/fail
Rule Engine
FAR / OSR / setback logic
K.1 generation
Project PDF Save/Load
large backend rewrite
unrelated redesign

Do not introduce fake buttons.

Acceptance Criteria

This sprint passes only if:

Parcel/site sides can be inspected and edited in UI.
Side metadata is saved in project state.
North direction can be set manually.
North direction is visible on canvas.
Orientation state is saved/loaded.
Tool UI is cleaner and closer to the approved design.
Typography / font readability is improved.
Right panel remains the main layer management area.
Existing measurement workflow still works.
Existing exports still work.
py_compile, smoke, and full pass.
Scope grep finds no legal/OCR/AI/Rule Engine strings.
Manual UI Check

Run or document:

Open app
Open PDF
Start Measuring
Create/select parcel boundary or site frame
Confirm side metadata editor appears
Edit side labels/roles
Set north direction
Confirm north arrow visible
Save project
Reload project
Confirm side metadata restored
Confirm north direction restored
Draw area/opening
Export XLSX
Confirm no major regression

Update:

UI_MANUAL_TEST.md

Take screenshots if possible.

Tests

Run:

python3 -m py_compile proto/server.py proto/e2e_ui_test.py
python3 proto/e2e_ui_test.py smoke
python3 proto/e2e_ui_test.py full

If environment uses python, allow fallback.

Run scope grep:

rg -n "ZONE_RULES|runCheck|FAR|OSR|Rule Engine|OCR|AI checker|ข้อ 41|ข้อ 50|ผังเมือง" proto/ui.html proto/server.py

Expected:

no matches
Test Additions

If safe, add/update tests for:

parcel side editor exists when parcel/site boundary selected
side metadata can be updated
north tool exists
north orientation persists after save/load
toolbar still renders cleanly
right panel layer controls still work
Output Files

Update:

PATCH_SUMMARY.md
TEST_RESULT.md
UI_MANUAL_TEST.md
FINAL_REPORT_FOR_CHATGPT.md
log.md

Optional:

PATCH.diff
FINAL_REPORT_FOR_CHATGPT.md Format
# FINAL_REPORT_FOR_CHATGPT.md — Parcel Sides + Orientation + Tool UI Cleanup

## Goal
Add editable parcel side metadata UI, north/orientation support, and clean up tool UI/typography.

## Outcome
PASS/FAIL

## Files Changed
- ...

## Result
- Parcel side editor:
- Parcel side persistence:
- North/orientation tool:
- Canvas overlay:
- Save/load:
- Export/audit:
- Tool UI:
- Typography/font:

## Tests
- py_compile:
- smoke:
- full:
- scope grep:
- manual UI:

## Regression Status
- Project Setup:
- Start Measuring:
- set scale:
- draw area:
- draw opening:
- overlapping picker:
- layer visibility:
- layer lock:
- properties panel:
- object tree:
- XLSX export:
- annotated PDF:
- .bmaplan save/load:

## Known Remaining Gaps
- Real PDF multi-page stress test still needed.
- Save/Load hardening may still need dedicated sprint.
- Project PDF Save/Load still future work.
- Legal/building-control skill remains Phase 2.
Update log.md

Add a new entry:

### [time] Parcel sides + orientation + tool UI cleanup

**สิ่งที่ทำ:**
- ...

**เหตุผล:**
- ...

**ไฟล์ที่แตะ:**
- proto/ui.html
- proto/server.py (if needed)
- proto/e2e_ui_test.py
- PATCH_SUMMARY.md
- TEST_RESULT.md
- UI_MANUAL_TEST.md
- FINAL_REPORT_FOR_CHATGPT.md
- log.md

**ผลทดสอบ/ผลตรวจ:**
- py_compile:
- smoke:
- full:
- scope grep:
- manual UI:

**Known issues:**
- ...
Stop Conditions

Stop immediately if:

parcel side metadata cannot be stored safely
north/orientation breaks existing drawing workflow
save/load breaks
export breaks
full test fails
legal/OCR/AI/Rule Engine appears
change becomes a large redesign or rewrite
Final Instruction

Keep the patch focused.

Do not redesign the entire app.

Implement:

parcel side editing UI
north/orientation support
tool UI cleanup
font/typography improvement

while preserving the current measurement workflow.