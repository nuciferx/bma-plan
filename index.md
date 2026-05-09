# BMA-Plan Index

> Updated: 2026-05-09  
> Current phase: Phase 1 = Raster PDF Measurement Assistant / Mini-CAD for Area Measurement

## Current Status

- [CURRENT_STATUS.md](CURRENT_STATUS.md)
- [FINAL_REPORT_FOR_CHATGPT.md](FINAL_REPORT_FOR_CHATGPT.md)
- [TEST_RESULT.md](TEST_RESULT.md)
- [PATCH_SUMMARY.md](PATCH_SUMMARY.md)
- [UI_MANUAL_TEST.md](UI_MANUAL_TEST.md)
- [log.md](log.md)

Latest condition:
- Right Panel Organization After Mockup V3: PASS
- Mockup V3 Scale + Page Workflow UI: PASS
- Primary workflow locked as `Open PDF -> Set Scale -> Page Setup -> Measure -> Review -> Export`
- Left panel labels: `Sheets / Objects / Properties`
- Right panel: Layers-first with layer counts and controls, with existing Properties/Object Tree kept below as labeled compatibility sections
- Status bar labels: `Tool`, `Scale`, `Objects`, `Warnings`, `Layer`, `Save`, `Page`
- Latest tests: `py_compile`, `smoke`, `full`, and manual viewport check PASS
- Latest architecture docs: [PAGE_LAYER_MEASUREMENT_MODEL.md](docs/design/PAGE_LAYER_MEASUREMENT_MODEL.md)

## Phase 1 Scope Warning

Phase 1 is not:
- legal checker
- OCR
- AI checker
- Rule Engine
- FAR / OSR / setback law validator
- K.1 generator
- Project PDF Save/Load

Phase 1 is only:
- open PDF
- set/verify scale
- draw area and opening
- manage layers and overlapping objects
- edit object properties and semantic metadata
- export auditable measurement data

Real PDFs may be raster/scanned images, so the product must not depend on PDF vector geometry.

## Source

- [proto/](proto/) - FastAPI backend, HTML canvas frontend, E2E tests, and requirements

Root repository note:
- `proto/` is a nested Git repository/gitlink to `https://github.com/nuciferx/bma-plan-proto.git`.
- Runtime source files stay in `proto/` and were not moved by housekeeping.

## Design Docs

- [docs/design/PAGE_LAYER_MEASUREMENT_MODEL.md](docs/design/PAGE_LAYER_MEASUREMENT_MODEL.md)
- [docs/design/BMA_PLAN_PHASE1_CONTEXT.md](docs/design/BMA_PLAN_PHASE1_CONTEXT.md)
- [docs/design/BMA_PLAN_V2_SCOPE.md](docs/design/BMA_PLAN_V2_SCOPE.md)
- [docs/design/DEVELOPMENT_PLAN.md](docs/design/DEVELOPMENT_PLAN.md)
- [docs/design/idea-cards.md](docs/design/idea-cards.md)
- [docs/design/bma-plan-mockup-v3.html](docs/design/bma-plan-mockup-v3.html) — UI mockup V3 reference
- [docs/design/bma-plan-mockup.html](docs/design/bma-plan-mockup.html) — UI mockup V1 reference

## Process Docs

- [docs/process/SPRINT_INDEX.md](docs/process/SPRINT_INDEX.md)
- [docs/process/FILE_STRUCTURE_PLAN.md](docs/process/FILE_STRUCTURE_PLAN.md)
- [docs/process/HOUSEKEEPING_REPORT.md](docs/process/HOUSEKEEPING_REPORT.md)
- [docs/process/DOCS_SUMMARY.md](docs/process/DOCS_SUMMARY.md)
- [docs/process/TASK_PACKET.md](docs/process/TASK_PACKET.md)
- [docs/process/REVIEW_RESULT.md](docs/process/REVIEW_RESULT.md)
- [docs/process/humancheck.md](docs/process/humancheck.md) — user manual review notes 2026-05-09

## Status Docs

- [docs/status/PHASE1_AUDIT.md](docs/status/PHASE1_AUDIT.md)
- [reports/archive/PROGRESS.md](reports/archive/PROGRESS.md)
- [reports/archive/HANDOFF.md](reports/archive/HANDOFF.md)
- [reports/archive/SESSION_CONTINUATION.md](reports/archive/SESSION_CONTINUATION.md)
- [reports/archive/UI_REGRESSION_REPORT.md](reports/archive/UI_REGRESSION_REPORT.md)

## Active Sprints

- [sprints/active/](sprints/active/)

No active run prompt was kept in this housekeeping pass. Next sprint should create a new focused runbook under `sprints/active/`.

## Completed Sprints

- [sprints/completed/2026-05-06-housekeeping-v1/](sprints/completed/2026-05-06-housekeeping-v1/)
- [sprints/completed/2026-05-06-project-setup-ui/](sprints/completed/2026-05-06-project-setup-ui/)
- [sprints/completed/2026-05-06-measurement-main-ui/](sprints/completed/2026-05-06-measurement-main-ui/)
- [sprints/completed/2026-05-07-responsive-toolbar-ui/](sprints/completed/2026-05-07-responsive-toolbar-ui/)
- [sprints/completed/2026-05-07-site-sides-orientation-ui/](sprints/completed/2026-05-07-site-sides-orientation-ui/)
- [sprints/completed/2026-05-07-sprint-3a-duplicate-helpers/](sprints/completed/2026-05-07-sprint-3a-duplicate-helpers/)
- [sprints/completed/2026-05-07-semantic-tag-foundation/](sprints/completed/2026-05-07-semantic-tag-foundation/)
- [sprints/completed/2026-05-07-update-agents-gtm-loop/](sprints/completed/2026-05-07-update-agents-gtm-loop/)
- [sprints/completed/2026-05-08-rollback-ui-pack1-targeted-fix/](sprints/completed/2026-05-08-rollback-ui-pack1-targeted-fix/)
- [sprints/completed/2026-05-08-page-layer-measurement-model/](sprints/completed/2026-05-08-page-layer-measurement-model/)

## Archived Sprints

- [sprints/archive/2026-05-08-ui-pack1-header-toolbar-superseded/](sprints/archive/2026-05-08-ui-pack1-header-toolbar-superseded/)
- [sprints/archive/legacy-one-day-sprint/](sprints/archive/legacy-one-day-sprint/)

## Reports

- [reports/latest/](reports/latest/) - reserved for future copied latest report sets
- [reports/archive/](reports/archive/) - old reports, handoffs, patches, and status docs

Latest report files remain in root:
- `FINAL_REPORT_FOR_CHATGPT.md`
- `TEST_RESULT.md`
- `PATCH_SUMMARY.md`
- `UI_MANUAL_TEST.md`

## Artifacts

- [artifacts/manual_test/](artifacts/manual_test/) - moved manual screenshots, downloaded XLSX, and `.bmaplan` roundtrip artifacts
- [artifacts/screenshots/](artifacts/screenshots/) - moved loose screenshots
- [artifacts/exports/](artifacts/exports/) - reserved for generated exports

`artifacts/` is ignored by Git and should not be staged unless explicitly requested.

## References And Archive

- [docs/references/](docs/references/) - reference PDFs/docs that should remain ignored unless explicitly approved
- [archive/references/](archive/references/) - large/private reference PDFs
- [archive/user_projects/](archive/user_projects/) - real/private `.bmaplan` files, ignored by Git
- [archive/old_docs/](archive/old_docs/) - old context notes, legacy source copies, patch scripts, assistant notes
- [sample_projects/](sample_projects/) - safe sample project files only; currently empty

Root exception:
- `20250616_RAMA4 APARTMENT PERMIT rev 1.pdf` remains in root because existing full E2E tests expect that path. It is ignored by Git and must not be staged.

## Current Sprint Roadmap

Recommended next sprint:
1. Git baseline commit for the current workflow UI/right-panel condition after review.
2. Dedicated left Properties migration sprint, if desired, to move the full object editor out of the right panel safely.
3. Stabilization sprint only if a concrete core workflow defect is reported.
4. Canvas Interaction UX as a narrow sprint if selection/pan/zoom issues are confirmed.
5. Measurement profile metadata implementation: add `measurementProfile`, `objectCategory`, `reportTarget`, `lawBasis`, and `countingRule` with backward-compatible normalization only.

Policy:
- no new feature until Git baseline and stabilization are confirmed
- one sprint = one branch = one problem
- do not start legal/OCR/AI/Rule Engine work before Phase 1 measurement stability is complete
