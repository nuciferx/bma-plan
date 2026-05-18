# NEXT_ACTION.md

## Current Mode
Fast but guarded.

## Rule
Do the next safest action only.

## Decision Tree

1. If latest PASS state is not committed:
   - do Git baseline only
   - no code edit

2. If workspace has untracked housekeeping files:
   - do housekeeping only
   - no runtime code edit

3. If no active sprint card exists:
   - create the next sprint card only
   - no runtime code edit

4. If an active sprint card exists and explicitly allows code:
   - implement that sprint only
   - run required tests
   - update docs
   - commit if PASS

5. If tests fail:
   - stop
   - report exact failure
   - do not continue into another sprint

## Current Recommended Sprint
RUN_PHASE_I_A_SCHEMA_AND_PROJECT_SETUP.md

(Site Plan §16 Open Questions DECIDED on 2026-05-13 — Phase I-A unblocked. Sprint card to be created in `sprints/active/`. References: `docs/design/SITE_PLAN_MEASUREMENT_PLAN.md §13 Phase I-A`, `docs/design/SITE_PLAN_UI_MOCKUP.md §11`. Target E2E marker: `SITE_AREA_TYPES_OK`.)

## Hard Forbidden
- legal checker
- OCR
- AI checker
- Rule Engine
- FAR/OSR/setback pass-fail
- save/load migration without compatibility plan
- export model rewrite without sprint scope