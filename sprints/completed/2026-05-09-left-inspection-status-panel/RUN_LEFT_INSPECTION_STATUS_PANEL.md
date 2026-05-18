# RUN_LEFT_INSPECTION_STATUS_PANEL.md

Date: 2026-05-09
Status: IN PROGRESS

## Goal

Add a fixed Left Inspection Status Panel to the left panel sidebar.
Users always know current context, workflow progress, page/floor status,
measurement summary, and next recommended action.

## Scope

Files to edit:
- proto/ui.html (HTML + JS)
- proto/static/css/app.css (CSS classes)
- proto/e2e_ui_test.py (new assertions)

Files NOT to touch:
- proto/server.py
- export/
- save/load format

## Phase 1 Scope Check

- [ ] No legal checker, OCR, AI, Rule Engine
- [ ] No drag handlers, no position save, no workspace preset
- [ ] No autosave engine
- [ ] No save/load format changes
- [ ] No export rewrite
- [ ] Uses existing helpers only

## Acceptance Criteria

- Panel is visible in left sidebar above mode tabs
- Panel shows: file name, page, scale, tool, layer
- Panel shows workflow steps with status markers
- Panel shows per-page stats (pages with scale, with objects)
- Panel shows measurement summary (total objects, gross, net, land, parking)
- Panel shows warnings and next recommended action
- Panel is collapsible
- Tabs (Sheets/Objects/Properties) still switch correctly
- Drawing, selecting, export unchanged
- py_compile PASS + smoke PASS + full PASS

## Stop Conditions

- Left panel tabs break
- Drawing breaks
- Export breaks
- Widget uses drag behavior
- Legal/OCR/AI/Rule Engine appears
- Tests fail outside local UI scope
