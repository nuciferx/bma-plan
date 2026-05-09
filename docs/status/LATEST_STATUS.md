# LATEST_STATUS.md — BMA-Plan Current Feature State

Date: 2026-05-09

## Phase

Phase 1 = Raster PDF Measurement Assistant. No legal checker, OCR, AI, Rule Engine, FAR/OSR/pass-fail.

## Latest Sprint Results

| Sprint | Result |
|--------|--------|
| Left Properties Migration | PASS |
| Opening Parent Reassignment | PASS |
| Page Scales Audit | PASS |
| Report Target Summary XLSX | PASS |
| Export Metadata Columns XLSX | PASS |
| Measurement Profile Metadata Foundation | PASS |
| Right Panel Organization After Mockup V3 | PASS |
| Mockup V3 Scale + Page Workflow UI | PASS |

## Active Feature State

- **Workflow**: Open PDF → Set Scale → Page Setup → Measure → Review → Export (locked)
- **Left panel tabs**: Sheets / Objects / Properties — all 3 clickable via `setSidebarMode(mode)`
  - Sheets: page thumbnails, search, quick-tag bar, workflow card
  - Objects: flat list of all page objects; click → selects and auto-switches to Properties
  - Properties: full property editor for selected object, or placeholder
- **Auto-switch**: canvas click, obj-picker, Object Tree → auto-switches left panel to Properties
- **Right panel**: Layers-first with counts/controls; Legacy/Compatibility Properties+ObjectTree below
- **Status bar**: Tool, Scale, Objects, Warnings, Layer, Save, Page
- **5 measurement metadata fields** on all objects: measurementProfile, objectCategory, reportTarget, lawBasis, countingRule (derived from semanticTag via mapping tables)
- **Opening parent reassignment**: `rpSetOpeningParent(id)` with parentManual guard
- **XLSX export**: Page Scales (10 cols), Report Target Summary sheet, 5 metadata columns in 4 sheets
- **JSON/CSV export**: all 5 metadata fields per row

## Test Baseline (2026-05-09)

```
python -m py_compile proto/server.py proto/e2e_ui_test.py  → PASS
python proto/e2e_ui_test.py smoke                          → PASS
python proto/e2e_ui_test.py full                           → PASS
```

## Latest Commits

- proto: `e32122e` feat: wire left panel tabs with content switching and auto-Properties on selection
- root: `7005903` feat: left properties migration - left panel tab switching PASS
