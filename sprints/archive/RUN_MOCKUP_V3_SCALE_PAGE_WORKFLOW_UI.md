# RUN_MOCKUP_V3_SCALE_PAGE_WORKFLOW_UI.md

## 0. Sprint Identity

Sprint Name:
- Mockup V3 Scale + Page Workflow UI

Sprint Type:
- UI / Workflow / Phase 1 Stabilization

Status:
- PENDING

Mockup Reference:
- `bma-plan-mockup-v3.html`

Main Rule:
- Do not implement the full mockup in one sprint.
- Use mockup v3 only as a direction for menu/workspace structure.

---

## 1. Product Framework

BMA-Plan Phase 1 is:

```text
Raster PDF Measurement Assistant
```

It is not:

```text
Legal Checker
OCR System
AI Checker
Rule Engine
FAR / OSR / Setback Pass-Fail Validator
K.1 Generator
Auto Boundary Detection Tool
```

---

## 2. Main Workflow to Lock

The main workflow must be:

```text
Open PDF → Set Scale → Page Setup → Measure → Review → Export
```

Important rule:

```text
Set Scale must come before Page Setup.
```

Reason:
- Every PDF page may have a different scale.
- No reliable measurement can happen before scale is verified.
- Page Setup assigns page type / floor / label after the page and scale status are known.

---

## 3. Goal

Apply only the safe, Phase 1-compatible parts of `bma-plan-mockup-v3.html` into the current BMA-Plan UI.

This sprint must make the interface clearer by:

1. Making `Set Scale` easy to find.
2. Reordering the main workflow to:
   - Open PDF
   - Set Scale
   - Page Setup
   - Measure
   - Review
   - Export
3. Renaming/reframing `Project Setup` as `Page Setup` where appropriate.
4. Making the left panel structure clearer:
   - Sheets
   - Objects
   - Properties
5. Making the right panel Layers-first.
6. Adding or improving a status bar showing:
   - Scale status
   - Object count
   - Warning count
   - Active layer
   - Active tool
   - Saved / Unsaved status

---

## 4. Scope

Allowed in this sprint:

```text
UI labels
UI order
Menu visibility
Workflow wording
Panel labels
Status bar foundation
E2E UI assertions
Documentation update
```

Allowed visible menu/entry points:

```text
Open PDF
Open Project
Save
Recover Unsaved Project
Set Scale Current Page
Scale Status by Page
Reset Page Scale
Page Setup
Page Manager
Set Floor
Auto Name Pages
Measure
Review
Export
Workspace Reset
Help / Status
```

---

## 5. Not Scope

Do not implement these in this sprint:

```text
Full Scale Manager
Copy Scale to Selected Pages
Copy Scale to Similar Pages
Scale History
Full Page Manager
Full Autosave Engine
Full Recovery Engine
Draggable Workspace
Dockable Panel System
Save Current Workspace
Move Panel Left / Right
Collapse Panels
Summary Widget Full Logic
Export Review Engine
Export JSON
Export History
Large File Mode Engine
Performance Monitor
Developer Debug
Data Model Migration
Save/Load Migration
Server Rewrite
```

---

## 6. Forbidden Scope

Hard forbidden:

```text
Legal Checker
OCR
AI Checker
Rule Engine
FAR Pass/Fail
OSR Pass/Fail
Setback Pass/Fail
Parking Requirement Judgment
Generate ค.1
Auto Boundary Detection
PDF Vector Geometry Assumption
```

If any of these appear as new logic, stop immediately.

---

## 7. Files to Read First

Read these files before editing:

```text
AGENTS.md
CURRENT_STATUS.md
index.md
log.md
docs/design/PAGE_LAYER_MEASUREMENT_MODEL.md
bma-plan-mockup-v3.html
proto/ui.html
proto/e2e_ui_test.py
```

If `PRODUCT_FRAMEWORK.md` already exists, read it too.

---

## 8. Files Allowed to Edit

Source files:

```text
proto/ui.html
proto/e2e_ui_test.py
```

Documentation/status files:

```text
PATCH_SUMMARY.md
TEST_RESULT.md
UI_MANUAL_TEST.md
FINAL_REPORT_FOR_CHATGPT.md
CURRENT_STATUS.md
index.md
log.md
```

Optional doc to create if useful:

```text
docs/design/MOCKUP_V3_MENU_INVENTORY.md
```

---

## 9. Files Forbidden to Edit

Do not edit:

```text
proto/server.py
proto/requirements.txt
PDF files
XLSX files
.bmaplan files
artifacts/
archive/
manual_test_artifacts/ unless intentionally creating new UI screenshots
```

Do not touch backend/export/save-load unless tests prove unavoidable. If unavoidable, stop and report before editing.

---

## 10. UI Contract

### 10.1 Main Workflow

Visible workflow order must be:

```text
1. Open PDF
2. Set Scale
3. Page Setup
4. Measure
5. Review
6. Export
```

Rules:

```text
Set Scale must appear before Page Setup.
Project Setup must not appear as the primary workflow label.
Page Setup means page type / floor / page label assignment.
```

---

### 10.2 Scale UI

Set Scale must be easy to find.

Allowed visible scale items:

```text
Set Scale Current Page
Scale Status by Page
Reset Page Scale
Show Scale Line
Scale Warning
```

Allowed only if real handler already exists:

```text
Verify Scale
Scale Manager
```

Must stay hidden or disabled with clear reason:

```text
Copy Scale to Selected Pages
Copy Scale to Similar Pages
Scale History
```

No fake active button.

---

### 10.3 Left Panel

Left panel must be structured as:

```text
Sheets
Objects
Properties
```

Meaning:

```text
Sheets = page list / floor / page type / scale status
Objects = measured objects on current page
Properties = selected object or selected page properties
```

---

### 10.4 Right Panel

Right panel must be Layers-first.

Right panel may show:

```text
Layers
Visible toggle
Lock toggle
Active layer
Layer color
Object count
Add layer
Rename layer
Delete empty layer
```

Avoid putting full object properties in the right panel.

If selected object summary already exists on right and moving it risks regression, keep it temporarily but mark as known issue in docs.

---

### 10.5 Status Bar

Status bar should show:

```text
Scale status
Object count
Warning count
Active layer
Active tool
Saved / Unsaved status
Current file/page
```

Important:

```text
Do not fake autosave.
```

If autosave logic does not exist, show only safe labels such as:

```text
Saved
Unsaved changes
Manual save required
```

Do not show:

```text
Autosaved just now
```

unless real autosave exists.

---

## 11. Data Contract

Do not change data model.

Must preserve:

```text
case_id isolation
PDF/page state
scale state
raw geometry
layer state
selected tool state
selected object state
save/load compatibility
export compatibility
```

No new required fields in saved project data.

---

## 12. Regression Contract

Must not break:

```text
App opens
PDF upload
Set scale
Draw area
Draw opening
Select object
Overlapping picker
Layer visibility
Layer lock
Save project
Load project
XLSX export
PDF/annotation export if already covered
```

---

## 13. Implementation Tasks

### Task 1 — Audit Current UI

- Locate current header/menu/ribbon/workflow markup in `proto/ui.html`.
- Locate current `Project Setup` and `Set Scale` labels.
- Locate current left/right panel markup.
- Locate status bar or equivalent status area.
- Locate E2E assertions in `proto/e2e_ui_test.py`.

---

### Task 2 — Apply Workflow Reorder

Change visible workflow order to:

```text
Open PDF → Set Scale → Page Setup → Measure → Review → Export
```

Requirements:

- Set Scale appears before Page Setup.
- Page Setup replaces Project Setup in primary workflow.
- Existing project setup logic may keep internal function names if renaming risks regression.

---

### Task 3 — Improve Scale Entry Point

Make scale accessible and obvious.

Minimum:

```text
Set Scale
Scale status
Current page scale state
```

Do not implement copy-scale or scale-history features in this sprint.

---

### Task 4 — Adjust Panel Labels

Left panel:

```text
Sheets
Objects
Properties
```

Right panel:

```text
Layers
```

Do not redesign panel logic deeply in this sprint.

---

### Task 5 — Add/Improve Status Bar

Add or adjust status labels:

```text
Scale
Objects
Warnings
Layer
Tool
Saved/Unsaved
Page
```

Use real state where available.

If real state is not available, use neutral placeholder only, not fake success.

---

### Task 6 — Hide or Disable Unsafe Mockup Items

From mockup v3, keep hidden or disabled:

```text
Copy Scale to Selected Pages
Copy Scale to Similar Pages
Scale History
Group Objects
Ungroup Objects
Export JSON
Export History
Large File Mode
Split PDF Suggestion
Performance Monitor
Developer Debug
Save Current Workspace
Move Panel Left
Move Panel Right
Collapse Panels
```

Disabled items must not look functional.

---

### Task 7 — Update E2E Tests

Add/update assertions:

```text
Set Scale visible
Set Scale appears before Page Setup
Page Setup visible
Project Setup not used as primary workflow label
Sheets visible
Objects visible
Properties visible
Layers visible
Status bar contains Scale
Status bar contains Tool or Active tool
No forbidden Phase 1 strings introduced as active features
```

Do not rewrite unrelated tests broadly.

---

### Task 8 — Run Tests

Run:

```bash
python -m py_compile proto/server.py proto/e2e_ui_test.py
python proto/e2e_ui_test.py smoke
python proto/e2e_ui_test.py full
```

If full test fails, stop and report root cause.

---

### Task 9 — Manual UI Check

Check these viewport sizes:

```text
1440 × 900
1512 × 982
1366 × 768
```

Checklist:

```text
Header/menu does not overflow
Ribbon does not overflow badly
Set Scale is visible
Page Setup is after Set Scale
Left panel tabs are readable
Right Layers panel is readable
Status bar is readable
Canvas remains usable
No fake active buttons visible
```

---

### Task 10 — Update Documentation

Update:

```text
PATCH_SUMMARY.md
TEST_RESULT.md
UI_MANUAL_TEST.md
FINAL_REPORT_FOR_CHATGPT.md
CURRENT_STATUS.md
index.md
log.md
```

Each update must record:

```text
What changed
Why
Files touched
Tests run
PASS/FAIL
Known issues
Next action
```

---

## 14. Acceptance Criteria

Functional:

```text
[ ] Main workflow order is Open PDF → Set Scale → Page Setup → Measure → Review → Export
[ ] Set Scale is visible and before Page Setup
[ ] Page Setup is visible
[ ] Open PDF still works
[ ] Set Scale still works
[ ] Area drawing still works
[ ] Opening drawing still works
[ ] Export access remains visible
```

UI:

```text
[ ] Left panel labels are Sheets / Objects / Properties
[ ] Right panel is Layers-first
[ ] Status bar shows scale/object/warning/layer/tool/save-page info
[ ] No serious overflow at 1440, 1512, 1366 widths
```

Safety:

```text
[ ] No fake autosave
[ ] No fake draggable workspace
[ ] No fake copy-scale feature
[ ] No legal/OCR/AI/Rule Engine
[ ] No data model migration
[ ] No save/load migration
```

Tests:

```text
[ ] py_compile PASS
[ ] smoke PASS
[ ] full PASS
```

If any test fails, document exact failure and stop.

---

## 15. Stop Conditions

Stop immediately if:

```text
Open PDF breaks
Set Scale breaks
Area drawing breaks
Opening drawing breaks
Layer lock breaks
Export breaks
Save/load compatibility changes
Data model migration is needed
Backend edit is needed
UI overflow becomes worse than current baseline
Fake button is introduced
Legal/OCR/AI/Rule Engine appears
The work expands into full mockup v3 implementation
```

---

## 16. Final Report Format

At the end, report:

```text
Outcome: PASS / FAIL / PARTIAL

Changed:
- ...

Not changed:
- ...

Tests:
- py_compile: PASS/FAIL
- smoke: PASS/FAIL
- full: PASS/FAIL

Known issues:
- ...

Next recommended sprint:
- ...
```

---

# CODEX COMMAND

Use this command after saving this file in the project root:

```bash
codex
```

Then paste:

```text
You are working on BMA-Plan.

Read and follow this sprint card exactly:

RUN_MOCKUP_V3_SCALE_PAGE_WORKFLOW_UI.md

Before editing, read:
- AGENTS.md
- CURRENT_STATUS.md
- index.md
- log.md
- docs/design/PAGE_LAYER_MEASUREMENT_MODEL.md
- bma-plan-mockup-v3.html
- proto/ui.html
- proto/e2e_ui_test.py

Goal:
Apply only the safe parts of bma-plan-mockup-v3.html related to the Phase 1 UI workflow:
Open PDF → Set Scale → Page Setup → Measure → Review → Export.

Hard rules:
- Set Scale must appear before Page Setup.
- Page Setup replaces Project Setup as the primary workflow label.
- Left panel labels must become Sheets / Objects / Properties.
- Right panel must be Layers-first.
- Add or improve status bar labels for Scale, Objects, Warnings, Layer, Tool, and Saved/Unsaved state.
- Do not implement the full mockup.
- Do not implement draggable workspace.
- Do not implement full autosave/recovery.
- Do not implement full Scale Manager.
- Do not implement copy-scale features.
- Do not implement legal/OCR/AI/Rule Engine/FAR/OSR/setback pass-fail.

Allowed source files:
- proto/ui.html
- proto/e2e_ui_test.py

Allowed docs:
- PATCH_SUMMARY.md
- TEST_RESULT.md
- UI_MANUAL_TEST.md
- FINAL_REPORT_FOR_CHATGPT.md
- CURRENT_STATUS.md
- index.md
- log.md

Forbidden unless you stop and report first:
- proto/server.py
- proto/requirements.txt
- save/load model changes
- export model changes
- data migration
- PDFs
- XLSX
- .bmaplan
- artifacts/
- archive/

Required tests:
python -m py_compile proto/server.py proto/e2e_ui_test.py
python proto/e2e_ui_test.py smoke
python proto/e2e_ui_test.py full

Add/update E2E assertions for:
- Set Scale visible
- Set Scale appears before Page Setup
- Page Setup visible
- Project Setup not used as the primary workflow label
- Sheets / Objects / Properties visible
- Layers visible
- Status bar contains Scale
- Status bar contains active Tool or Tool
- forbidden Phase 1 features not introduced

If any core workflow breaks, rollback your change and report.

Do not continue beyond the sprint scope.
```

Alternative one-line command:

```bash
codex "Read RUN_MOCKUP_V3_SCALE_PAGE_WORKFLOW_UI.md and execute it exactly. Do not exceed scope. Run required tests and update docs."
```
