# RUN_RIGHT_PANEL_ORGANIZATION_AFTER_MOCKUP_V3.md

## 0. Sprint Identity

Sprint Name:
- Right Panel Organization After Mockup V3

Sprint Type:
- UI / Layout / Stabilization

Status:
- PENDING

Date:
- 2026-05-09

---

## 1. Current Condition

The latest verified UI condition is:

```text
Mockup V3 Scale + Page Workflow UI: PASS
```

Verified workflow:

```text
Open PDF → Set Scale → Page Setup → Measure → Review → Export
```

Current accepted UI state:

- Set Scale appears before Page Setup.
- Page Setup is the primary visible setup label.
- Left panel labels are:
  - Sheets
  - Objects
  - Properties
- Right panel is Layers-first.
- Status bar includes:
  - Tool
  - Scale
  - Objects
  - Warnings
  - Layer
  - Save
  - Page
- py_compile PASS.
- smoke PASS.
- full PASS.
- Manual viewport checks PASS at:
  - 1440x900
  - 1512x982
  - 1366x768

Known issue from latest status:

```text
Right panel still includes existing Properties/Object Tree below Layers as a known compatibility choice.
```

---

## 2. Goal

Safely organize the right panel so it is clearly Layers-first without breaking existing object/property behavior.

Main goal:

```text
Right panel should behave as the Layers workspace, while full object/page properties should belong to the left Properties tab or remain accessible without duplication confusion.
```

This sprint is a cleanup/stabilization sprint, not a new feature sprint.

---

## 3. Product Scope

BMA-Plan Phase 1 remains:

```text
Raster PDF Measurement Assistant
```

This sprint must not add:

```text
Legal Checker
OCR
AI Checker
Rule Engine
FAR / OSR / Setback Pass-Fail
K.1 Generator
Auto Boundary Detection
Full Autosave Engine
Full Scale Manager
Copy Scale Features
Draggable Workspace
Dockable Panel System
Data Model Migration
Save/Load Migration
Export Model Migration
```

---

## 4. Problem Statement

After the Mockup V3 workflow sprint, the right panel is now Layers-first, but existing Properties/Object Tree remain below Layers for compatibility.

This creates UI ambiguity:

- User expects the right panel to be only about Layers.
- Object Properties appearing below Layers duplicates the left Properties tab concept.
- Future workflow will be harder to stabilize if object details are split across both sides.

This sprint must reduce ambiguity without breaking existing behavior.

---

## 5. Scope

Allowed in this sprint:

```text
Right panel organization
Panel labels
Section visibility
Minor UI movement if safe
E2E assertions
Manual UI check
Docs/status update
```

Primary target:

```text
Right panel = Layers-first and clearly Layers-focused.
Left panel = Sheets / Objects / Properties.
```

Allowed implementation approaches:

### Option A — Safest

Keep legacy Properties/Object Tree below Layers, but visually label it as:

```text
Legacy / Compatibility
```

or collapse it by default if existing JS supports collapse safely.

### Option B — Preferred if low risk

Move full selected-object properties to the left `Properties` tab, while keeping a small selected object summary on the right only if necessary.

### Option C — Stop

If moving Properties or Object Tree requires broad JS/data-binding rewrites, stop and report. Do not force it.

---

## 6. Not Scope

Do not implement:

```text
Custom draggable workspace
Dock/undock panels
Save current workspace
Panel resize engine
New property editor model
New object tree model
New layer data model
Layer rename/reorder rewrite
Layer preset migration
Smart review engine
Export preview engine
Autosave/recovery
Backend changes
```

---

## 7. Files to Read First

Read before editing:

```text
AGENTS.md
CURRENT_STATUS.md
index.md
log.md
PATCH_SUMMARY.md
TEST_RESULT.md
UI_MANUAL_TEST.md
FINAL_REPORT_FOR_CHATGPT.md
docs/design/PAGE_LAYER_MEASUREMENT_MODEL.md
proto/ui.html
proto/e2e_ui_test.py
```

If available, read:

```text
bma-plan-mockup-v3.html
RUN_MOCKUP_V3_SCALE_PAGE_WORKFLOW_UI.md
```

---

## 8. Files Allowed to Edit

Source:

```text
proto/ui.html
proto/e2e_ui_test.py
```

Docs/status:

```text
PATCH_SUMMARY.md
TEST_RESULT.md
UI_MANUAL_TEST.md
FINAL_REPORT_FOR_CHATGPT.md
CURRENT_STATUS.md
index.md
log.md
```

Optional doc:

```text
docs/design/RIGHT_PANEL_ORGANIZATION.md
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
docs/references/
archive/references/
archive/user_projects/
```

Do not touch backend, save/load, export, or project data model.

---

## 10. UI Contract

### 10.1 Right Panel

Right panel must be clearly Layers-first.

It must show:

```text
Layers
Visible toggle
Lock toggle
Active layer
Layer color
Object count
```

It may show:

```text
Selected object mini-summary
```

Only if it does not duplicate full Properties.

It should not show full object/page property editing as the dominant right-panel content.

---

### 10.2 Left Panel

Left panel must continue to show:

```text
Sheets
Objects
Properties
```

Rules:

- Sheets = page list / floor / page type / scale status.
- Objects = measured objects on current page.
- Properties = selected object or selected page properties.

Do not break left panel tab labels.

---

### 10.3 Workflow

Main workflow must remain:

```text
Open PDF → Set Scale → Page Setup → Measure → Review → Export
```

Set Scale must remain before Page Setup.

---

### 10.4 Status Bar

Status bar must remain visible and include:

```text
Tool
Scale
Objects
Warnings
Layer
Save
Page
```

Do not fake autosave.

---

## 11. Data Contract

No data model changes.

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
Annotated PDF export if covered
```

---

## 13. Implementation Tasks

### Task 1 — Audit Current Right Panel

Inspect `proto/ui.html` and document:

- Current Layers section.
- Current Properties section under right panel.
- Current Object Tree section under right panel.
- Any JS IDs/classes/event handlers that depend on these locations.

### Task 2 — Choose Safe Strategy

Choose one:

```text
A. Collapse/label legacy right-panel Properties/Object Tree
B. Move full Properties to left Properties tab
C. Stop and report if movement is too risky
```

Do not guess. Prefer A if B requires broad rewrite.

### Task 3 — Apply Minimal UI Change

Implement only the chosen safe strategy.

Minimum acceptable improvement:

- Right panel header and first visible section are Layers.
- Any legacy Properties/Object Tree below Layers is clearly marked or collapsed.
- User cannot confuse right panel as full property editor.

### Task 4 — Preserve Interaction

Verify:

- Layer visibility toggle still works.
- Layer lock toggle still works.
- Active layer display still works.
- Object selection still shows usable properties somewhere.
- Existing object tree behavior still works if retained.

### Task 5 — Update E2E Tests

Add/update assertions:

```text
Right panel Layers visible
Layers appears before any Properties/Object Tree section in right panel
Left panel has Sheets / Objects / Properties
Workflow order still Open PDF -> Set Scale -> Page Setup -> Measure -> Review -> Export
Set Scale before Page Setup
Status bar contains Tool / Scale / Layer
Layer lock behavior still covered
```

### Task 6 — Run Tests

Run:

```bash
python -m py_compile proto/server.py proto/e2e_ui_test.py
python proto/e2e_ui_test.py smoke
python proto/e2e_ui_test.py full
```

If on PowerShell and encoding is needed:

```powershell
$env:PYTHONIOENCODING='utf-8'; python proto/e2e_ui_test.py smoke
$env:PYTHONIOENCODING='utf-8'; python proto/e2e_ui_test.py full
```

### Task 7 — Manual UI Check

Check viewport sizes:

```text
1440 × 900
1512 × 982
1366 × 768
```

Checklist:

```text
Right panel is clearly Layers-first
Left tabs are readable
Status bar readable
No right-panel overflow
Object selection still displays properties somewhere
Layer toggle and lock still usable
Canvas remains usable
No fake buttons added
```

### Task 8 — Update Docs

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

Record:

```text
What changed
Why
Chosen strategy A/B/C
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
[ ] Right panel is clearly Layers-first.
[ ] Layers section appears before any right-panel property/object-tree section.
[ ] Left panel still shows Sheets / Objects / Properties.
[ ] Object properties remain accessible somewhere.
[ ] Layer visibility still works.
[ ] Layer lock still works.
[ ] Active layer still works.
```

Workflow:

```text
[ ] Workflow remains Open PDF → Set Scale → Page Setup → Measure → Review → Export.
[ ] Set Scale remains before Page Setup.
```

Safety:

```text
[ ] No backend changes.
[ ] No data model changes.
[ ] No save/load migration.
[ ] No export model changes.
[ ] No legal/OCR/AI/Rule Engine.
[ ] No fake draggable workspace.
```

Tests:

```text
[ ] py_compile PASS.
[ ] smoke PASS.
[ ] full PASS.
```

---

## 15. Stop Conditions

Stop immediately if:

```text
Moving properties requires broad JS rewrite
Object selection breaks
Layer lock breaks
Layer visibility breaks
Save/load behavior changes
Export behavior changes
Data model migration is needed
Backend edit is needed
UI overflow becomes worse
Fake buttons are introduced
Legal/OCR/AI/Rule Engine appears
```

If stopped, report exact reason and do not continue.

---

## 16. Final Report Format

Report:

```text
Outcome: PASS / FAIL / PARTIAL

Chosen strategy:
- A / B / C

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
- Measurement profile metadata implementation
```

---

# CODEX COMMAND

Use:

```bash
codex
```

Paste:

```text
You are working on BMA-Plan.

Read and follow this sprint card exactly:

RUN_RIGHT_PANEL_ORGANIZATION_AFTER_MOCKUP_V3.md

Goal:
Safely organize the right panel after Mockup V3 UI so it is clearly Layers-first, while keeping object properties accessible and not breaking existing behavior.

Before editing, read:
- AGENTS.md
- CURRENT_STATUS.md
- index.md
- log.md
- PATCH_SUMMARY.md
- TEST_RESULT.md
- UI_MANUAL_TEST.md
- FINAL_REPORT_FOR_CHATGPT.md
- docs/design/PAGE_LAYER_MEASUREMENT_MODEL.md
- proto/ui.html
- proto/e2e_ui_test.py

Hard rules:
- Do not add features.
- Do not implement draggable workspace.
- Do not change backend.
- Do not change data model.
- Do not change save/load/export models.
- Do not add legal/OCR/AI/Rule Engine.
- Keep workflow: Open PDF -> Set Scale -> Page Setup -> Measure -> Review -> Export.
- Keep Set Scale before Page Setup.
- Keep left panel labels: Sheets / Objects / Properties.
- Make right panel clearly Layers-first.

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
- docs/design/RIGHT_PANEL_ORGANIZATION.md

Required tests:
python -m py_compile proto/server.py proto/e2e_ui_test.py
python proto/e2e_ui_test.py smoke
python proto/e2e_ui_test.py full

If moving Properties/Object Tree requires broad JS rewrite, stop and report instead of forcing it.

Do not continue beyond this sprint scope.
```
