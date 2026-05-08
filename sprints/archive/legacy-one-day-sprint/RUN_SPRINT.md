# RUN_SPRINT.md — BMA-Plan One-Day Sprint

## Goal

Finish the next practical BMA-Plan Phase 1 sprint with minimal token usage.

Main target:
1. Finish Sprint 1 stabilization.
2. Finish practical Sprint 2 raster UX.
3. Add minimal Sprint 3 audit/export foundation only if safe.

## Read First

Read these files before working:

1. AGENTS.md
2. log.md latest entry
3. index.md
4. BMA_PLAN_PHASE1_CONTEXT.md
5. proto/STATUS.md if available
6. PROGRESS.md if needed

## Hard Rules

Do not add:
- legal rules
- OCR
- AI checker
- Rule Engine
- Electron/native rewrite
- large architecture rewrite
- fake UI buttons
- vector-only PDF assumption

Preserve:
- CASES[case_id]
- raw geometry recalculation
- export/UI consistency
- scale confidence/source
- existing smoke/full test behavior

## Five-Agent Pipeline

Run this as an internal 5-agent workflow.

### AGENT 0 — Orchestrator

Create TASK_PACKET.md.

TASK_PACKET.md must include:
- exact tasks
- files to edit
- contracts to preserve
- acceptance criteria
- tests to run
- forbidden changes

Do not code.

### AGENT 1 — Coder

Read TASK_PACKET.md and implement minimal patch only.

Target files:
- proto/server.py
- proto/ui.html
- proto/e2e_ui_test.py
- index.md
- log.md
- PHASE1_AUDIT.md if needed

Do not edit unrelated files.

After coding, create:
- PATCH_SUMMARY.md
- PATCH.diff

### AGENT 2 — Reviewer + Tester

Review the patch and run tests.

Check:
- layer lock = visible but unselectable
- overlapping picker still works
- object tree reflects page/layer/object grouping
- properties panel edits real object data
- Finish / Cancel / Undo Point buttons work
- export uses same data as UI
- no legal/OCR/AI/rule engine added

Create:
- REVIEW_RESULT.md

### AGENT 3 — Docs + Second Code Check

Update docs and check scope again.

Create or update:
- PHASE1_AUDIT.md
- TEST_RESULT.md
- DOCS_SUMMARY.md
- index.md
- log.md

### AGENT 4 — Final Reporter

Create:
- FINAL_REPORT_FOR_CHATGPT.md

Report must include:
1. sprint goal
2. completed work
3. files changed
4. test results
5. manual test notes
6. regression risks
7. known remaining gaps
8. questions for ChatGPT review
9. recommended next sprint

## Target Tasks

Implement only what is safe:

Sprint 1:
- Create PHASE1_AUDIT.md
- Hide advanced tools such as law check, snap debug, setback panel
- Make locked layer visible but unselectable
- Add/improve object tree grouped by page/layer/object
- Add/improve properties panel for object code, name, type, gross/opening/net, color, label mode

Sprint 2:
- Add orthogonal mode toggle if safe
- Make reference line closer to first-class object if safe
- Add visible Finish / Cancel / Undo Point buttons on canvas

Minimal Sprint 3:
- Ensure measurable objects have object_id if safe
- Add minimal export audit trail if safe
- Do not expand into full legal/report engine

## Tests

Run:

```bash
python -m py_compile proto/server.py proto/e2e_ui_test.py
python proto/e2e_ui_test.py smoke