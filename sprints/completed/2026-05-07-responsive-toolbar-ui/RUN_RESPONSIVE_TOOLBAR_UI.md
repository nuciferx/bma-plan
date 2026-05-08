# RUN_RESPONSIVE_TOOLBAR_UI.md — BMA-Plan Responsive Measurement Toolbar

## Goal

Fix the main measurement toolbar so it works on MacBook-width screens and matches the approved clean BMA-Plan measurement UI direction.

Current issue:
- The measurement toolbar is too long and crowded.
- On MacBook screen width, tools overflow and become visually cramped.
- The toolbar does not match the approved first UI design where tools are grouped and balanced.
- Too many secondary tools are visible at once.

This sprint focuses only on responsive toolbar cleanup.

## Current Screenshot Problem

The highlighted toolbar currently contains too many items in one row:

- เลือก
- พื้นที่
- ช่องเปิด
- เส้นอ้างอิง
- ตั้ง Scale
- Layer selector
- ระยะ
- ระยะต่อเนื่อง
- ถึง Ref
- ถนน
- ที่จอด
- รถยนต์
- ฝังจาก
- แว่น
- size controls
- ล้าง

This is not usable on MacBook-sized screens.

## Product Direction

The toolbar should follow the approved design direction:

1. Top header = file/page/zoom/report actions.
2. Context toolbar = core measurement tools only.
3. Secondary tools = grouped under More menu or secondary dropdown.
4. Layer management = right panel.
5. Active layer = one compact dropdown only.
6. No duplicated layer controls.
7. No horizontal overflow.

## Required Reading

Read first:

1. `AGENTS.md`
2. latest entry in `log.md`
3. `FINAL_REPORT_FOR_CHATGPT.md`
4. `TEST_RESULT.md`
5. `UI_MANUAL_TEST.md`
6. `proto/ui.html`
7. `proto/e2e_ui_test.py`

## Scope

Do only toolbar responsive cleanup.

Allowed:

1. Reorganize measurement toolbar into groups.
2. Keep primary tools visible:
   - เลือก
   - วาดพื้นที่
   - ช่องเปิด
   - ตั้ง Scale
   - วัดระยะ
3. Move secondary tools into a `เพิ่มเติม` / More menu:
   - เส้นอ้างอิง
   - ระยะต่อเนื่อง
   - ถึง Ref
   - ถนน
   - ที่จอด
   - รถยนต์
   - ฝังจาก
   - แว่น
   - loupe size controls
   - ล้าง
4. Keep active layer as compact dropdown:
   - Layer: พื้นที่หลัก ▼
5. Add responsive CSS:
   - prevent horizontal overflow
   - allow wrapping only if visually clean, or use overflow menu
   - hide labels on narrow screens if safe
6. Preserve every existing tool function.
7. Preserve existing keyboard/mouse interactions.
8. Update tests for toolbar layout and hidden/more-menu tools.

## Forbidden

Do not add:

- OCR
- AI checker
- legal rules
- Rule Engine
- FAR / OSR / setback logic
- K.1 generation
- Project PDF Save/Load
- large backend rewrite
- new measurement algorithms
- curved path
- iPad/touch UI

Do not break:

- Project Setup UI
- PDF upload
- start measuring
- page navigation
- zoom
- manual scale
- draw area
- draw opening
- reference line
- distance measurement
- overlapping picker
- layer lock
- layer visibility
- properties panel
- object tree
- XLSX export
- `.bmaplan` save/load

## UX Requirements

### Toolbar Groups

Group tools logically:

Primary group:
- เลือก
- วาดพื้นที่
- ช่องเปิด
- ตั้ง Scale
- วัดระยะ

Secondary group under More:
- เส้นอ้างอิง
- ระยะต่อเนื่อง
- ถึง Ref
- ถนน
- ที่จอด
- รถยนต์
- ฝังจาก
- แว่น
- ล้าง

Edit group:
- Undo
- Redo
- Delete

Layer group:
- compact active layer dropdown only

### More Menu

Add a visible button:

```text
เพิ่มเติม ▾

Clicking it opens secondary tools.

The menu must be real, not fake.

Every moved tool must still call the same existing function as before.

Responsive Rules

At MacBook width, toolbar must not overflow horizontally.

Minimum requirements:

no clipped tools
no overlapping text
no toolbar pushing into right panel
primary tools remain visible
secondary tools accessible through More menu

Suggested CSS behavior:

use flex-wrap: nowrap
use min-width: 0
use overflow: hidden
use compact button class
use @media (max-width: 1280px) to hide nonessential labels or move to More
use @media (max-width: 1100px) for icon-only primary buttons if needed
Visual Requirement

Toolbar should look closer to the approved mockup:

fewer visible items
consistent button height
grouped sections with separators
less dense
no duplicated layer controls
active tool is clear
active layer is compact
Acceptance Criteria

This sprint passes only if:

Toolbar no longer overflows on MacBook-width viewport.
Primary tools remain visible.
Secondary tools are accessible through More menu.
Moved tools still work.
Active layer dropdown remains visible and compact.
No duplicated layer visibility/lock controls appear in toolbar.
Right panel remains the main layer management area.
Scale warning still works.
Project Setup still works.
Start Measuring still opens measurement screen.
Manual scale still works.
Draw area still works.
Draw opening still works.
Reference line still works.
Distance tool still works.
Overlapping picker still works.
Layer lock still works.
XLSX export still works.
py_compile, smoke, and full tests pass.
Scope grep finds no legal/OCR/AI/Rule Engine strings.
Manual UI Check

Run browser check at MacBook-like viewport:

Use viewport around:

width: 1440 or 1512
height: 900 or 982

Check:

Open app.
Open PDF.
Click เริ่มวัด.
Confirm toolbar fits width.
Confirm no horizontal overflow.
Confirm primary tools visible.
Open More menu.
Confirm secondary tools available.
Test at least:
เลือก
วาดพื้นที่
ช่องเปิด
ตั้ง Scale
วัดระยะ
เส้นอ้างอิง from More
Confirm right panel layer controls still work.
Export XLSX.