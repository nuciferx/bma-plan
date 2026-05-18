# RUN_GIT_BASELINE_AFTER_MOCKUP_V3_UI.md

## 0. Sprint Identity

Sprint Name:
- Git Baseline After Mockup V3 UI

Sprint Type:
- Git / Safety / Baseline / No Feature

Status:
- PENDING

Date:
- 2026-05-09

---

## 1. Current Condition

The latest BMA-Plan condition is PASS.

Verified latest state:

- Mockup V3 Scale + Page Workflow UI: PASS
- Main workflow is locked as:
  - Open PDF
  - Set Scale
  - Page Setup
  - Measure
  - Review
  - Export
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
- py_compile PASS
- smoke PASS
- full PASS
- Manual viewport checks PASS:
  - 1440x900
  - 1512x982
  - 1366x768

Known compatibility note:
- Existing Properties/Object Tree may remain below Layers in the right panel for compatibility.

---

## 2. Goal

Create a clean Git baseline commit for the current PASS condition after Mockup V3 Scale + Page Workflow UI.

This sprint must not change product behavior.

Goal:

```text
Lock the current passing UI workflow condition into Git before starting the next implementation sprint.
```

---

## 3. Main Rule

This is a baseline-only sprint.

Do not add features.

Do not improve UI.

Do not refactor.

Do not touch source unless needed only to verify state, and if source changes are detected, stop and report.

---

## 4. Product Scope Lock

BMA-Plan Phase 1 remains:

```text
Raster PDF Measurement Assistant
```

Forbidden:

```text
Legal Checker
OCR
AI Checker
Rule Engine
FAR / OSR / Setback Pass-Fail
K.1 Generator
Auto Boundary Detection
Draggable Workspace
Full Autosave Engine
Full Scale Manager
Copy Scale Features
Data Model Migration
Save/Load Migration
Export Model Migration
```

---

## 5. Files to Read First

Read:

```text
AGENTS.md
CURRENT_STATUS.md
index.md
log.md
PATCH_SUMMARY.md
TEST_RESULT.md
UI_MANUAL_TEST.md
FINAL_REPORT_FOR_CHATGPT.md
```

Optional source read-only inspection:

```text
proto/ui.html
proto/e2e_ui_test.py
```

---

## 6. Files Allowed to Edit

Normally none.

Allowed only if documenting baseline:

```text
PATCH_SUMMARY.md
TEST_RESULT.md
FINAL_REPORT_FOR_CHATGPT.md
CURRENT_STATUS.md
index.md
log.md
docs/process/SPRINT_INDEX.md
```

Do not edit runtime source in this sprint.

---

## 7. Files Forbidden to Edit

Do not edit:

```text
proto/ui.html
proto/server.py
proto/e2e_ui_test.py
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

---

## 8. Git Safety Checks

Run:

```bash
git status --short
git diff --stat
git diff -- proto/ui.html proto/server.py proto/e2e_ui_test.py
```

Check unsafe files are not staged:

```bash
git diff --cached --name-only
```

Must not stage:

```text
PDF
XLSX
.bmaplan
.bmaplan.pdf
artifacts/
archive/
.env
tokens
credentials
keys
desktop.ini
```

---

## 9. Required Tests Before Commit

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

All must pass before baseline commit.

---

## 10. Commit Scope

Commit only safe files related to:

```text
Mockup V3 UI workflow change
test updates
status/report docs
sprint docs
```

Expected safe file types:

```text
.md
.html only if proto/ui.html already contains completed UI sprint changes
.py only if proto/e2e_ui_test.py already contains completed test updates
.gitignore if already intentionally updated
```

Do not commit generated artifacts unless explicitly required.

---

## 11. Suggested Commit Message

Use:

```bash
git add AGENTS.md README.md index.md CURRENT_STATUS.md PATCH_SUMMARY.md TEST_RESULT.md UI_MANUAL_TEST.md FINAL_REPORT_FOR_CHATGPT.md log.md docs/ sprints/ proto/ui.html proto/e2e_ui_test.py
git status --short
git commit -m "chore: baseline after mockup v3 workflow UI"
```

If `proto/` is a nested Git repo/submodule, handle it separately:

```bash
cd proto
git status --short
git diff --stat
python -m py_compile server.py e2e_ui_test.py
python e2e_ui_test.py smoke
python e2e_ui_test.py full
git add ui.html e2e_ui_test.py
git commit -m "ui: align workflow with mockup v3 scale-first flow"
cd ..
git status --short
git add proto CURRENT_STATUS.md PATCH_SUMMARY.md TEST_RESULT.md UI_MANUAL_TEST.md FINAL_REPORT_FOR_CHATGPT.md index.md log.md docs/ sprints/
git commit -m "chore: baseline after mockup v3 workflow UI"
```

Only use the nested repo path if `proto/` is actually a nested Git repository.

---

## 12. Acceptance Criteria

Pass only if:

```text
[ ] Current status says Mockup V3 Scale + Page Workflow UI PASS
[ ] py_compile PASS
[ ] smoke PASS
[ ] full PASS
[ ] git status reviewed
[ ] unsafe files not staged
[ ] generated/private files not committed
[ ] baseline commit created
[ ] commit hash recorded in log.md or final report
[ ] no new feature added
[ ] no source behavior changed during this baseline sprint
```

---

## 13. Stop Conditions

Stop immediately if:

```text
tests fail
Open PDF fails
Set Scale fails
Area/Opening drawing fails
export fails
save/load fails
unexpected source diff appears
unsafe files are staged
proto nested repo status is unclear
commit would include PDF/XLSX/.bmaplan/artifacts/archive
```

If stopped, report the exact reason and do not commit.

---

## 14. Final Report Format

At the end, report:

```text
Outcome: PASS / FAIL / PARTIAL

Baseline commit:
- root repo: <hash or not applicable>
- proto repo: <hash or not applicable>

Tests:
- py_compile: PASS/FAIL
- smoke: PASS/FAIL
- full: PASS/FAIL

Committed:
- ...

Not committed:
- ...

Known issues:
- ...

Next recommended sprint:
- Right-panel organization sprint
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

RUN_GIT_BASELINE_AFTER_MOCKUP_V3_UI.md

Goal:
Create a clean Git baseline commit for the current PASS condition after Mockup V3 Scale + Page Workflow UI.

Before doing anything, read:
- AGENTS.md
- CURRENT_STATUS.md
- index.md
- log.md
- PATCH_SUMMARY.md
- TEST_RESULT.md
- UI_MANUAL_TEST.md
- FINAL_REPORT_FOR_CHATGPT.md

Current verified condition:
- Mockup V3 Scale + Page Workflow UI: PASS
- Workflow: Open PDF -> Set Scale -> Page Setup -> Measure -> Review -> Export
- py_compile / smoke / full: PASS

Hard rules:
- Do not add features.
- Do not improve UI.
- Do not refactor.
- Do not edit runtime source unless only verifying state.
- Do not commit PDFs, XLSX, .bmaplan, artifacts, archive, references, secrets, or desktop.ini.
- If proto is a nested Git repo, handle proto commit separately and then commit the root gitlink/docs.

Run:
git status --short
git diff --stat
python -m py_compile proto/server.py proto/e2e_ui_test.py
python proto/e2e_ui_test.py smoke
python proto/e2e_ui_test.py full

If all tests pass, create a baseline commit.

Suggested commit message:
chore: baseline after mockup v3 workflow UI

After commit, update final report/log with commit hash and next recommended sprint.

If any test fails or unsafe files are staged, stop and report. Do not commit.
```

Alternative one-line command:

```bash
codex "Read RUN_GIT_BASELINE_AFTER_MOCKUP_V3_UI.md and execute it exactly. Create a safe Git baseline only. Do not add features."
```
