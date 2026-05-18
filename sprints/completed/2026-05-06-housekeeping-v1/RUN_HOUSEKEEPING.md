# RUN_HOUSEKEEPING.md — BMA-Plan Project Housekeeping + Index Cleanup

## Goal

จัดระเบียบไฟล์โปรเจกต์ BMA-Plan ให้ชัดเจน อ่านต่อได้ง่าย และไม่หลงไฟล์ ก่อนเริ่ม Sprint ถัดไป

งานนี้เป็น documentation / housekeeping sprint เท่านั้น

## Main Objectives

1. ตรวจไฟล์ทั้งหมดใน project root
2. แยกไฟล์ที่จำเป็นกับไฟล์ artifact ชั่วคราว
3. อัปเดต `index.md` ให้ตรงกับสถานะล่าสุด
4. สร้าง `CURRENT_STATUS.md`
5. สร้าง `SPRINT_INDEX.md`
6. เสนอแผนจัด folder structure ที่ชัดเจน
7. ห้ามแก้ source code
8. ห้ามลบไฟล์
9. ห้ามย้ายไฟล์จริง ถ้าไม่มั่นใจ ให้เสนอแผนก่อน

## Required Reading

Read these files first:

1. `AGENTS.md`
2. latest entry in `log.md`
3. `index.md`
4. `FINAL_REPORT_FOR_CHATGPT.md`
5. `TEST_RESULT.md`
6. `PATCH_SUMMARY.md`
7. `UI_MANUAL_TEST.md`
8. `PHASE1_AUDIT.md`
9. `DOCS_SUMMARY.md`
10. `BMA_PLAN_PHASE1_CONTEXT.md`

## Current Known Context

Current project direction:

- Phase 1 = Raster PDF Measurement Assistant
- Not legal checker
- No OCR
- No AI checker
- No Rule Engine
- Main goal = open PDF, set scale, draw area/opening, select overlapping objects, edit properties, export audit reports

Recent completed work:

- Overlapping picker fixed and manual UI test passed
- Layer lock passed
- Properties panel passed
- XLSX export passed
- Sprint 3A duplicate helper cleanup verification passed
- `buildRows`, `collectAreas`, and `phase1Warnings` each have only one declaration
- `py_compile`, `smoke`, and `full` tests passed
- Scope grep found no law/OCR/AI/Rule Engine strings

## Scope

Do only documentation and file organization planning.

Allowed work:

1. Update `index.md`
2. Create `CURRENT_STATUS.md`
3. Create `SPRINT_INDEX.md`
4. Create `FILE_STRUCTURE_PLAN.md`
5. Update `log.md`
6. Create `HOUSEKEEPING_REPORT.md`

Do not edit:

- `proto/server.py`
- `proto/ui.html`
- `proto/e2e_ui_test.py`
- runtime source code
- test logic
- export logic
- measurement logic

Do not move files unless explicitly safe and reversible.

If moving files is needed, do not move them yet. Instead, write a proposed move plan in `FILE_STRUCTURE_PLAN.md`.

## File Classification Task

Inspect project root and classify files into these groups:

### A. Core Project Files

Required to understand and continue the project.

Examples:

- `index.md`
- `CURRENT_STATUS.md`
- `AGENTS.md`
- `BMA_PLAN_PHASE1_CONTEXT.md`
- `log.md`
- `proto/`

### B. Current Sprint Artifacts

Latest active pipeline outputs.

Examples:

- `TASK_PACKET.md`
- `PATCH_SUMMARY.md`
- `REVIEW_RESULT.md`
- `TEST_RESULT.md`
- `DOCS_SUMMARY.md`
- `FINAL_REPORT_FOR_CHATGPT.md`
- `UI_MANUAL_TEST.md`

### C. Sprint Prompt Files

Files used to run agent/codex sprint.

Examples:

- `RUN_SPRINT.md`
- `RUN_SPRINT_3A.md`
- future `RUN_SPRINT_3B.md`

### D. Historical / Archive Candidates

Files that are useful but should not stay mixed in root forever.

Examples:

- old patch scripts
- old context copies
- old reports
- old handoff files
- manual test artifacts from past runs

### E. Source / Runtime Files

Implementation files.

Examples:

- `proto/server.py`
- `proto/ui.html`
- `proto/e2e_ui_test.py`
- `proto/requirements.txt`
- `proto/STATUS.md`

## Required Output: index.md

Update `index.md` so it includes:

1. Current project purpose
2. Current phase
3. Current status
4. Latest completed sprint
5. Latest passing tests
6. Important files and their purpose
7. Current sprint roadmap
8. Next recommended sprint
9. File organization notes
10. Clear warning that Phase 1 is not legal/OCR/AI/Rule Engine

`index.md` must clearly show:

```text
Current latest status:
- Overlapping picker: PASS
- UI manual picker test: PASS
- Sprint 3A duplicate helper verification: PASS
- py_compile / smoke / full: PASS
- Next recommended sprint: Start/Open File UI or Sprint 3B Page Scales audit