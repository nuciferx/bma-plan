# HOUSEKEEPING_REPORT.md

## Outcome
PASS

## What Was Organized
- Root folder reduced to current status/navigation files and top-level folders.
- Run prompts moved into `sprints/completed/` and `sprints/archive/`.
- Design/process/status docs moved into `docs/`.
- Old reports and handoffs moved into `reports/archive/`.
- Manual screenshots and generated manual-test outputs moved into `artifacts/manual_test/`.
- Loose screenshots moved into `artifacts/screenshots/`.
- Reference PDFs moved into `docs/references/` or `archive/references/`.
- Real/private `.bmaplan` moved into `archive/user_projects/`.
- Legacy notes, old source copies, assistant notes, and patch scripts moved into `archive/old_docs/`.
- `20250616_RAMA4 APARTMENT PERMIT rev 1.pdf` kept in root as an ignored E2E fixture path.

## Root Folder Before
- Many `RUN_*.md` prompt files in root
- Old reports and handoffs in root
- Manual test artifacts in `manual_test_artifacts/`
- Loose `pic/` screenshot folder
- Real PDF references in root
- Real `.bmaplan` in root
- Old context copies and patch scripts in root

## Root Folder After
- `AGENTS.md`
- `README.md`
- `index.md`
- `CURRENT_STATUS.md`
- `log.md`
- `FINAL_REPORT_FOR_CHATGPT.md`
- `TEST_RESULT.md`
- `PATCH_SUMMARY.md`
- `UI_MANUAL_TEST.md`
- `.gitignore`
- `.gitmodules`
- `proto/`
- `docs/`
- `sprints/`
- `reports/`
- `artifacts/`
- `sample_projects/`
- `archive/`

Root exception:
- `20250616_RAMA4 APARTMENT PERMIT rev 1.pdf` remains in root because existing full E2E tests expect that path. It is ignored by Git.

## Files Moved

| File | From | To | Reason |
|---|---|---|---|
| `RUN_HOUSEKEEPING.md` | root | `sprints/completed/2026-05-06-housekeeping-v1/` | Completed sprint prompt |
| `RUN_PROJECT_SETUP_UI.md` | root | `sprints/completed/2026-05-06-project-setup-ui/` | Completed sprint prompt |
| `RUN_MEASUREMENT_MAIN_UI.md` | root | `sprints/completed/2026-05-06-measurement-main-ui/` | Completed sprint prompt |
| `RUN_RESPONSIVE_TOOLBAR_UI.md` | root | `sprints/completed/2026-05-07-responsive-toolbar-ui/` | Completed sprint prompt |
| `RUN_SITE_SIDES_ORIENTATION_UI.md` | root | `sprints/completed/2026-05-07-site-sides-orientation-ui/` | Completed sprint prompt |
| `RUN_SPRINT_3A.md` | root | `sprints/completed/2026-05-07-sprint-3a-duplicate-helpers/` | Completed sprint prompt |
| `RUN_SPRINT_A_SEMANTIC_TAG_FOUNDATION.md` | root | `sprints/completed/2026-05-07-semantic-tag-foundation/` | Completed sprint prompt |
| `RUN_UPDATE_AGENTS_GTM_LOOP.md` | root | `sprints/completed/2026-05-07-update-agents-gtm-loop/` | Completed docs sprint prompt |
| `RUN_ROLLBACK_UI_PACK1_TARGETED_FIX.md` | root | `sprints/completed/2026-05-08-rollback-ui-pack1-targeted-fix/` | Completed restoration sprint prompt |
| `RUN_PAGE_LAYER_MEASUREMENT_MODEL.md` | root | `sprints/completed/2026-05-08-page-layer-measurement-model/` | Completed docs sprint prompt |
| `RUN_UI_PACK_1_HEADER_TOOLBAR.md` | root | `sprints/archive/2026-05-08-ui-pack1-header-toolbar-superseded/` | Superseded by rollback |
| `RUN_SPRINT.md` | root | `sprints/archive/legacy-one-day-sprint/` | Legacy generic prompt |
| Design docs | root | `docs/design/` | Durable design context |
| Process docs | root | `docs/process/` | Process/navigation docs |
| `PHASE1_AUDIT.md` | root | `docs/status/` | Durable audit/status doc |
| Old reports/handoffs | root | `reports/archive/` | Historical reports |
| Manual test artifacts | `manual_test_artifacts/` | `artifacts/manual_test/` | Generated artifacts |
| `pic/` contents | `pic/` | `artifacts/screenshots/` | Loose screenshot artifact |
| Reference PDFs | root | `docs/references/`, `archive/references/` | Reference material, ignored by Git |
| `20250616_RAMA4 APARTMENT PERMIT rev 1.pdf` | root | root | Kept to preserve full E2E test path; ignored by Git |
| `.bmaplan` | root | `archive/user_projects/` | Real/private project data, ignored by Git |
| Old notes/scripts | root | `archive/old_docs/` | Useful but non-current material |

## Files Kept in Root
- `AGENTS.md`
- `README.md`
- `index.md`
- `CURRENT_STATUS.md`
- `log.md`
- `FINAL_REPORT_FOR_CHATGPT.md`
- `TEST_RESULT.md`
- `PATCH_SUMMARY.md`
- `UI_MANUAL_TEST.md`
- `.gitignore`
- `.gitmodules`

## Files Not Moved
- `proto/` source folder and nested Git repo
- `.git/`
- `20250616_RAMA4 APARTMENT PERMIT rev 1.pdf` because current tests expect the root path
- environment-generated `desktop.ini` files; now ignored

## Git Safety
- `.gitignore` updated: yes, added `desktop.ini`
- unsafe files staged: no
- generated files staged: no
- secrets staged: no

## Known Issues
- `proto` remains a nested Git repository with pre-existing dirty/untracked state.
- `artifacts/`, PDFs, XLSX, `.bmaplan`, and archive user projects are intentionally ignored and should not be committed.
- Some Google Drive/Windows `desktop.ini` files may continue to appear locally but are ignored.
- One large PDF remains in root as an ignored test fixture path until tests/config are updated in a dedicated sprint.

## Next Recommended Action
- Git baseline commit for the housekeeping restructure after review.
- Stabilization sprint only if a concrete core workflow defect is reported.
- Canvas Interaction UX only if selection/pan/zoom workflow issues are confirmed.
