# RUN_UPDATE_AGENTS_GTM_LOOP.md — Add GTM Infinite Loop to Agent Protocol

## Goal

Update AGENTS.md to include the GTM Infinite Loop as the mandatory operating method for all BMA-Plan agents.

The loop is:

1. Understanding Condition
2. Restoration
3. Defect Factors Analysis
4. Eliminating Factors of Defect
5. Setting Condition
6. Condition Kaizen
7. Condition Management

This must guide every future sprint and every agent role.

## Scope

Documentation only.

Do:
1. Read AGENTS.md.
2. Add a new section: `BMA-Plan Agent Operating Loop — GTM Infinite Loop`.
3. Explain each of the 7 steps in the context of BMA-Plan.
4. Map the 7 steps to Agent 0–4 roles.
5. Add mandatory sprint outputs.
6. Add Phase 1 / Phase 2 rule:
   - Phase 1 = usable measurement/output workflow
   - Phase 2 = legal/building-control skill
7. Update log.md.
8. Update CURRENT_STATUS.md or index.md only if needed to mention the new agent operating loop.

Do not:
- edit source code
- edit proto/ui.html
- edit proto/server.py
- edit proto/e2e_ui_test.py
- add features
- move files
- delete files

## Required Reading

Read:
- AGENTS.md
- CURRENT_STATUS.md if exists
- index.md
- log.md latest entry
- FINAL_REPORT_FOR_CHATGPT.md

## Content Requirements

The new AGENTS.md section must include:

### 1. Understanding Condition
Agent must understand current status, scope, files, test state, defect/gap, and stop conditions before patching.

### 2. Restoration
Agent must restore broken core workflow before adding improvements.

Core workflow:
- app opens
- PDF upload
- Project Setup
- Start Measuring
- set scale
- draw area/opening
- overlapping picker
- layer lock/visibility
- save/load
- XLSX export

### 3. Defect Factors Analysis
Agent must identify the defect factor:
- layout/responsive issue
- event lifecycle issue
- duplicated state
- missing serialization field
- missing regression test
- unclear UX flow
- export mismatch
- stale documentation
- scope leakage
- environment mismatch

### 4. Eliminating Factors of Defect
Agent must fix root cause and add regression guard where possible.

### 5. Setting Condition
Agent must update reports/docs/tests to lock the new standard.

### 6. Condition Kaizen
Agent may improve UX/code/docs only within sprint scope.

### 7. Condition Management
Agent must update log/report/status and clearly mark PASS/FAIL, known gaps, and next action.

## Agent Role Mapping

Add mapping:

- Agent 0 = Planner / Orchestrator
- Agent 1 = Coder
- Agent 2 = Reviewer / Tester
- Agent 3 = Docs / Condition Setting
- Agent 4 = Final Reporter / Condition Management

## Phase Rule

Add:

Phase 1:
- produce usable outputs first:
  - PDF measurement
  - project setup
  - save/reopen
  - Excel export
  - annotated PDF export

Phase 2:
- legal/building-control skill
- manual review support only
- not automatic legal pass/fail

Legal skill must separate:
1. facts
2. law sources/effective dates
3. exceptions/transitional provisions
4. guidelines/circulars/case discussions
5. human judgment notes

## Tests

No app tests are required because this is documentation only.

But verify:
- AGENTS.md updated
- log.md updated
- no source code changed

## Output

Update:
- AGENTS.md
- log.md
- PATCH_SUMMARY.md
- FINAL_REPORT_FOR_CHATGPT.md

Optional:
- CURRENT_STATUS.md
- index.md

## Acceptance Criteria

Pass only if:
1. AGENTS.md contains the GTM Infinite Loop section.
2. Each of 7 steps is explained for BMA-Plan.
3. Agent 0–4 role mapping is added.
4. Phase 1 / Phase 2 rule is added.
5. Legal skill is clearly manual review support, not automatic pass/fail.
6. No source code is changed.
7. log.md is updated.

## Stop Conditions

Stop if:
- source code changes are required
- the update becomes a product feature sprint
- legal automation/pass-fail language is introduced