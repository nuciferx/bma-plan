# TASK_PACKET.md - Sprint 3A Duplicate Helper Cleanup

Date: 2026-05-06 16:52 +07:00

## Goal

Verify and keep `proto/ui.html` free of duplicate legacy helper declarations:
- `buildRows`
- `collectAreas`
- `phase1Warnings`

## Scope

Cleanup/verification only. Do not add features.

Forbidden:
- legal rules, OCR, AI checker, Rule Engine
- UI redesign
- export behavior changes
- measurement geometry changes
- backend case/session changes

## Acceptance

- Each target helper has exactly one active declaration.
- Existing picker, layer lock, properties, warning, and XLSX export behavior remains unchanged.
- `py_compile`, smoke, full pass.
- Scope grep finds no forbidden strings.

## Plan

1. Read `RUN_SPRINT_3A.md` and required context.
2. Search target helper declarations.
3. Patch `proto/ui.html` only if duplicates remain.
4. Run checks and regression tests.
5. Update pipeline docs and `log.md`.
