# RUN_MEASUREMENT_MAIN_UI.md — BMA-Plan Measurement Main UI Cleanup

## Goal

Improve the main measurement screen UI after the user clicks `เริ่มวัด`.

Project Setup UI has already been improved, but the normal measurement screen is still cluttered and still has duplicated/unclear layer controls.

This sprint focuses only on the measurement workspace UI.

## Product Goal Context

BMA-Plan Phase 1 must first help users produce usable work output:

1. open construction-plan PDF
2. setup project/page metadata
3. measure areas manually
4. save/reopen work
5. export Excel report
6. export annotated PDF

Legal/building-control skill is Phase 2 and must not be added in this sprint.

The measurement screen must be clean enough for real manual work.

## Current Problem From Screenshot

The current measurement screen has these UX problems:

1. Top toolbar is too crowded.
2. Layer controls appear in more than one place.
3. Right panel already has a full Layers panel, so top toolbar should not duplicate layer visibility/lock controls.
4. Active layer is not visually separated enough from layer management.
5. Scale warning exists but should be clearer and cleaner.
6. Left sidebar workflow is useful but needs cleaner visual hierarchy.
7. The UI still feels like a prototype instead of a focused measurement workspace.
8. Some buttons appear before they are useful or make the screen visually noisy.

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
9. `proto/e2e_ui_test.py`

## Scope

Do only main measurement UI cleanup.

Allowed work:

1. Improve layout and visual hierarchy of the measurement screen.
2. Reduce top toolbar clutter.
3. Remove duplicated top layer visibility/lock buttons if the right panel already manages layers.
4. Keep only one compact active-layer selector in the toolbar if needed.
5. Make the right sidebar the single main place for layer management.
6. Keep tabs:
   - Layers
   - Properties
   - Object Tree
7. Improve left sidebar readability:
   - Pages
   - Workflow checklist
8. Improve scale warning bar:
   - show warning clearly when no scale is set
   - show ready state only if scale is actually set
9. Improve selected/disabled tool visual state if safe.
10. Keep existing measurement behavior unchanged.

## Visual Design Direction

Follow the approved dark BMA-Plan UI direction:

- professional dark desktop app
- compact top header
- clean contextual measurement toolbar
- large central canvas
- left sidebar for pages and workflow
- right sidebar for layers/properties/object tree
- blue accent for active tool / active layer
- yellow/amber for scale warning
- green only for real ready/success states
- clear spacing and less clutter

Do not turn this into a website landing page.

This must still look like a working measurement/CAD/PDF tool.

## Main UI Requirements

### 1. Top Header

Keep these functions visible:

- BMA-Plan logo/name
- file status or filename
- Open PDF
- Open Project
- page navigation
- zoom controls
- Export report

Make it cleaner and less dense where possible.

Do not remove working functionality.

### 2. Context Measurement Toolbar

The drawing toolbar should contain measurement/drawing tools only:

- เลือก
- วาดพื้นที่
- วาดช่องเปิด
- เส้นอ้างอิง
- ป้ายกำกับ
- วัดระยะ
- Undo
- Redo
- Delete

Do not put full layer show/hide/lock controls here.

### 3. Active Layer Control

If active layer control is needed, keep only one compact dropdown:

```text
Layer: พื้นที่หลัก ▼

This control should set/select the active layer for new objects only.

It must not duplicate the full visibility/lock layer panel.

4. Right Sidebar

The right sidebar is the main layer control area.

Tabs:

Layers
Properties
Object Tree

Layer rows:

พื้นที่หลัก
พื้นที่ย่อย
ช่องว่าง
เส้นอ้างอิง
ป้าย

Each row should show:

color dot
layer name
eye icon for visibility
lock icon for lock state

Preserve existing layer visibility and lock behavior.

5. Left Sidebar

Left sidebar should show:

Pages / thumbnails
Workflow checklist:
เปิด PDF
ตั้ง Scale
วาดพื้นที่
วาดช่องเปิด
Export รายงาน

Improve spacing and readability.

Do not remove page thumbnails.

6. Scale Warning

When scale is missing, show a clear warning:

ยังไม่ได้ตั้ง Scale — ค่าพื้นที่ยังใช้จริงไม่ได้
กรุณาตั้ง Scale ก่อนวัดพื้นที่เพื่อให้ค่าพื้นที่ถูกต้อง
[ตั้ง Scale]

When scale is set, show ready state only if the app can reliably detect that scale is set:

พร้อมวัดพื้นที่ — Scale ถูกตั้งค่าแล้ว

Do not invent a ready state if the internal scale state is unknown.

7. Empty / Invalid State

If measurement screen is entered without a PDF, show a clear empty state or redirect back to Project Setup/Open PDF state.

Do not show a blank canvas with full tools if no file exists.

Behavior That Must Not Change

Do not break:

Project Setup UI
PDF upload
page thumbnails
start measuring transition
measurement canvas
manual scale
draw area
draw opening
reference line
overlapping picker
layer lock
layer visibility
properties panel
object tree
XLSX export
PDF annotation export
.bmaplan save/load
Forbidden

Do not add:

OCR
AI checker
legal rules
Rule Engine
FAR / OSR / setback logic
K.1 generation
Project PDF Save/Load
large backend rewrite
curved path
iPad/touch UI
new law-related UI

Do not perform a large redesign.

This is a focused cleanup sprint.

Acceptance Criteria

This sprint passes only if:

Main measurement screen is visually cleaner.
Duplicated layer controls are removed or reduced.
Right panel remains the main layer control.
Active layer is still clear.
Measurement toolbar remains usable.
Left sidebar remains usable.
Scale warning remains visible when scale is missing.
Scale ready state is shown only when truthful.
Project Setup UI still works.
Start Measuring still opens the measurement screen.
Manual scale still works.
Area drawing still works.
Opening drawing still works.
Overlapping picker still works.
Layer visibility still works.
Layer lock still works.
Properties panel still works.
Object tree still works.
XLSX export still works.
.bmaplan save/load does not regress.
py_compile, smoke, and full tests pass.
Scope grep finds no legal/OCR/AI/Rule Engine strings.
Manual UI Check

Run or document a browser check:

Open app.
Open PDF.
Confirm Project Setup screen appears.
Click เริ่มวัด.
Confirm main measurement screen appears.
Confirm toolbar is cleaner.
Confirm duplicated layer controls are not present.
Confirm right panel controls layers.
Confirm active layer control is compact and clear.
Confirm scale warning appears if scale is missing.
Set scale.
Draw area.
Draw opening.
Test overlapping picker.
Test layer visibility.
Test layer lock.
Test properties panel.
Test object tree.
Export XLSX.