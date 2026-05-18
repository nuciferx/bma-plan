
# RUN_SPRINT_A_SEMANTIC_TAG_FOUNDATION.md — Semantic Tag + Use Category Data Foundation Only

## Goal

Add `semanticTag` and `useCategory` to the existing object model so that future calculation, reporting, and Phase 2 manual review can depend on object meaning instead of object type strings or layer names.

This is **Sprint A of 3** in the Layer Model migration. Scope is intentionally narrow.

```text
Sprint A (this sprint) = data field + safe default + read/edit + save/load + minimal Properties UI
Sprint B (later)       = useCategory dropdown + XLSX use category summary + report wiring
Sprint C (later)       = Photoshop-like editable layer model + L0–L8 default set
```

Sprint A must NOT touch the layer model. Layers stay exactly as they are today.

This sprint is still **Phase 1 factual support only**.

Do not add legal checking, OCR, AI checker, FAR/OSR/setback logic, automatic pass/fail, Project PDF Save/Load, or layer rename/reorder.

-----

## Why Sprint A First

1. The current `.bmaplan` files in production (e.g. `SCR_Permit_Plan_Ele_Sec_29-01-2026.bmaplan`) must keep loading without data loss.
1. Layer model migration in one shot is too risky — if save/load breaks, real user files are at risk.
1. `semanticTag` is purely additive on the object model. It can ship without changing layer behavior.
1. Once `semanticTag` is shipped and stable, Sprint B and Sprint C can build on it safely.

-----

## Required Reading

Read first:

1. `AGENTS.md`
1. latest entry in `log.md`
1. `index.md`
1. `CURRENT_STATUS.md`
1. `FINAL_REPORT_FOR_CHATGPT.md`
1. `TEST_RESULT.md`
1. `UI_MANUAL_TEST.md`
1. `proto/ui.html`
1. `proto/server.py`
1. `proto/e2e_ui_test.py`

Also confirm that `SCR_Permit_Plan_Ele_Sec_29-01-2026.bmaplan` (or whatever real `.bmaplan` is in workspace) loads cleanly **before** any patch.

-----

## Scope

Allowed:

1. Add `semanticTag` field to object model (areas, openings, references, parcel/site, north arrow, road/frontage, labels, notes).
1. Add `useCategory` field to area-class objects only.
1. Infer safe default `semanticTag` from existing object type at runtime (mapping below).
1. Display `semanticTag` and `useCategory` in Properties panel (read-only or simple dropdown).
1. Allow user to change `semanticTag` and `useCategory` via dropdown.
1. Persist both fields in `.bmaplan` save/load.
1. Backward compat: load existing `.bmaplan` files that do not have these fields → infer at load time.
1. Add a single XLSX column for `semanticTag` and `useCategory` in existing audit/areas/openings sheets where safe (no schema rewrite, no new sheet).
1. Add e2e tests.
1. Update sprint output docs.

Forbidden:

- Changing layer names, layer order, or layer count
- Adding L0–L8 default layer set (that is Sprint C)
- Adding useCategory summary sheet (that is Sprint B)
- Adding new XLSX sheet
- Renaming or reordering existing XLSX sheets
- Touching measurement geometry / hit test / picker / drawing logic
- OCR, AI checker, legal rules, FAR/OSR/setback validation, K.1 generation
- Project PDF Save/Load
- Tool UI cleanup, font change, header/sidebar redesign — UI overhaul belongs to a separate sprint
- Any rewrite or relayout of `proto/ui.html` structure beyond the Properties panel section

-----

## Conceptual Model

### Object Field Additions

Every object that currently exists gains:

```json
{
  "id": "...",
  "...existing fields...": "...",
  "semanticTag": "<string from allowed set>",
  "useCategory": "<string from allowed set or null>"
}
```

`semanticTag` is required. If absent on load, infer from existing type.
`useCategory` is optional. Only meaningful for area-class objects.

### Allowed `semanticTag` Values (Sprint A set only)

Site:

```
site_boundary
parcel_side
north_arrow
road_line
frontage_line
```

Building / Area:

```
gross_floor_area
floor_area
use_area
```

Deduction:

```
deduction_opening
void
```

Reference:

```
scale_line
reference_line
dimension_line
```

Annotation:

```
label
review_note
```

(Sprint B will expand the set. Do not add the rest now.)

### Allowed `useCategory` Values

```
residential
commercial
office
service
parking
mechanical
storage
circulation
common
other
```

For non-area objects: `useCategory = null`.

-----

## Default Mapping — Existing Type → semanticTag

This mapping must be applied at:

- object creation (new draws)
- project load (backward compat)
- export (if missing)

|Existing object type / role                  |Default semanticTag|Default useCategory      |
|---------------------------------------------|-------------------|-------------------------|
|area `base_area` / `poly` (main area polygon)|`gross_floor_area` |`null`                   |
|area `sub_area` (sub-room polygon)           |`use_area`         |`null` (user picks later)|
|opening / `deduction` polygon                |`deduction_opening`|`null`                   |
|reference line / `ref`                       |`reference_line`   |`null`                   |
|scale calibration line                       |`scale_line`       |`null`                   |
|distance measure line                        |`dimension_line`   |`null`                   |
|parcel / site polygon (`site` polygon)       |`site_boundary`    |`null`                   |
|parcel side metadata edge                    |`parcel_side`      |`null`                   |
|north arrow / orientation tool object        |`north_arrow`      |`null`                   |
|road / frontage line                         |`road_line`        |`null`                   |
|label / text object                          |`label`            |`null`                   |
|note / highlight                             |`review_note`      |`null`                   |

If a type is encountered that is not in this table, default `semanticTag` to whatever closest match exists, or `null`, and log a console warning. Do not crash.

-----

## UI Requirements (Properties Panel ONLY)

In the existing right-panel Properties section, when an object is selected, add two new rows **at the end** of the existing fields:

```text
Semantic Tag : [dropdown with allowed values for this object class]
Use Category : [dropdown — only enabled if semanticTag is in {gross_floor_area, floor_area, use_area}]
```

Rules:

- Do NOT remove or rearrange any existing Properties rows.
- Do NOT change the right panel layout, layer rows, or object tree.
- The dropdown for `semanticTag` should only show values valid for this object’s geometry class (e.g. don’t offer `north_arrow` for a polygon).
- Changing `semanticTag` or `useCategory` must call `pushUndo()` before mutation.
- After change, refresh report numbers if they depend on the new field, otherwise leave UI as-is.
- No icon changes, no color changes, no font changes in this sprint.

-----

## Save / Load Requirements

`.bmaplan` save:

- Persist `semanticTag` and `useCategory` on every object that has them.

`.bmaplan` load:

- If `semanticTag` missing → infer from existing type using the mapping table.
- If `useCategory` missing → set to `null`.
- Old `.bmaplan` files (including `SCR_Permit_Plan_Ele_Sec_29-01-2026.bmaplan`) must load without error.
- After load, every object in memory must have `semanticTag` defined.

Backward compat is the **single most important acceptance criterion** of this sprint.

-----

## XLSX Export Requirements (minimum only)

In existing sheets that already list per-object rows (e.g. `สรุปพื้นที่`, `Areas`, `Openings`, `Audit Log`), add **two new columns at the right end**:

```
| ...existing columns... | semanticTag | useCategory |
```

Do not:

- Add a new sheet
- Rename any existing sheet
- Remove or reorder any existing column
- Add useCategory summary table — that is Sprint B

If a sheet has no per-object rows (e.g. Cover, Page Scales), do not touch it.

-----

## Calculation Requirements

None. This sprint adds data fields only. Calculations, summaries, and warnings stay exactly as they are today.

If existing calculations happen to reference the new fields safely (e.g. counting `gross_floor_area` objects), that is allowed but optional.

Forbidden in this sprint:

- FAR/OSR/setback pass-fail
- automatic legal compliance
- new structured warnings keyed off semanticTag
- any change to existing warning behavior

-----

## Acceptance Criteria

This sprint passes only if all of these hold:

1. Every object in memory has a `semanticTag` after creation or load.
1. Every area-class object has `useCategory` field (may be null).
1. Properties panel shows both fields when an object is selected.
1. User can change both fields via dropdown.
1. `pushUndo()` is called before mutation.
1. Save → reload of `.bmaplan` preserves both fields exactly.
1. Loading the existing `SCR_Permit_Plan_Ele_Sec_29-01-2026.bmaplan` file (or current real `.bmaplan` in workspace) succeeds and every object gets a sensible default `semanticTag`.
1. XLSX export contains `semanticTag` and `useCategory` columns at the end of per-object sheets, without breaking any existing column.
1. No layer-related code is changed.
1. No measurement geometry or hit test changes.
1. `py_compile`, smoke, and full pass.
1. Scope grep finds no forbidden strings.
1. `MAIN_UI_OK`, `SITE_UI_OK`, `XLSX_OK`, `PROJECT_OK`, `SELECT_OK`, `ANNOT_OK`, `PERSIST_OK`, `REAL_OK` still pass.

-----

## Manual UI Check

Run or document:

1. Open app
1. Open PDF (use `proto/test_plan_A1.pdf` or sample)
1. Start Measuring
1. Set scale
1. Draw a base area polygon
1. Select it → confirm Properties panel shows `Semantic Tag = gross_floor_area`, `Use Category` enabled and empty
1. Change `Use Category` to `residential` → confirm reflected in panel
1. Draw a sub area → confirm `Semantic Tag = use_area`, `Use Category` empty
1. Draw an opening → confirm `Semantic Tag = deduction_opening`, `Use Category` disabled / null
1. Draw a reference line → confirm `Semantic Tag = reference_line`
1. Set north arrow → confirm `Semantic Tag = north_arrow`
1. Draw parcel boundary → confirm `Semantic Tag = site_boundary`
1. Save `.bmaplan`
1. Reload `.bmaplan`
1. Confirm every selected object still has the same `semanticTag` and `useCategory`
1. Open the existing real `.bmaplan` file in workspace → confirm it loads without error and every object has a default `semanticTag`
1. Export XLSX
1. Open XLSX → confirm `semanticTag` and `useCategory` columns appear at the end of per-object sheets, no existing columns lost

Update `UI_MANUAL_TEST.md`. Save screenshots to:

```
manual_test_artifacts/semantic_tag_foundation_YYYYMMDD/properties_panel.png
manual_test_artifacts/semantic_tag_foundation_YYYYMMDD/xlsx_columns.png
manual_test_artifacts/semantic_tag_foundation_YYYYMMDD/backward_compat_load.png
```

-----

## Automated Tests

Run:

```bash
python3 -m py_compile proto/server.py proto/e2e_ui_test.py
python3 proto/e2e_ui_test.py smoke
python3 proto/e2e_ui_test.py full
```

Allow fallback to `python` if environment requires.

Run scope grep:

```bash
rg -n "ZONE_RULES|runCheck|FAR|OSR|Rule Engine|OCR|AI checker|ข้อ 41|ข้อ 50|ผังเมือง|Project PDF Save/Load" proto/ui.html proto/server.py proto/e2e_ui_test.py
```

Expected: no matches.

Additional layer-safety grep — must find ZERO matches in this sprint’s diff:

```bash
rg -n "L0 |L1 |L2 |L3 |L4 |L5 |L6 |L7 |L8 |default layer set|layer rename|layer reorder|Photoshop" proto/ui.html proto/server.py
```

If any of these appear, you are doing Sprint C, not Sprint A. Stop.

-----

## Test Additions

Add or update e2e coverage:

1. After draw area → object has `semanticTag = gross_floor_area`
1. After draw sub area → `semanticTag = use_area`
1. After draw opening → `semanticTag = deduction_opening`
1. After draw reference → `semanticTag = reference_line`
1. After set north → object has `semanticTag = north_arrow`
1. After draw parcel → `semanticTag = site_boundary`
1. Properties panel `semanticTag` dropdown change persists in object state
1. Properties panel `useCategory` dropdown change persists for area
1. `.bmaplan` save/load roundtrip preserves both fields
1. Loading a stripped `.bmaplan` (without `semanticTag`) infers correct defaults
1. XLSX per-object sheets include both new columns
1. XLSX existing column count = old count + 2 for affected sheets

-----

## Output Files

Update:

- `PATCH_SUMMARY.md`
- `TEST_RESULT.md`
- `UI_MANUAL_TEST.md`
- `FINAL_REPORT_FOR_CHATGPT.md`
- `CURRENT_STATUS.md`
- `index.md`
- `log.md`

Optional:

- `PATCH.diff`

-----

## PATCH_SUMMARY.md Format

```md
# PATCH_SUMMARY.md — Sprint A Semantic Tag Foundation

## Goal
Add semanticTag + useCategory data fields. No layer changes. No UI overhaul.

## Files Changed
- ...

## What Changed
- semanticTag field on all object types
- useCategory field on area-class objects
- Default mapping at create + load + export
- Properties panel dropdowns (added at end, no rearrangement)
- .bmaplan save/load includes new fields with backward compat
- XLSX per-object sheets get 2 new columns at end

## What Did Not Change
- Layer model (Sprint C)
- useCategory summary sheet (Sprint B)
- Tool UI / toolbar / header / sidebar layout (separate UI overhaul sprint)
- Measurement geometry / hit test / picker
- OCR / AI / legal rules / Rule Engine
- Project PDF Save/Load
- Existing XLSX sheets schema (only column addition at end)

## Tests Run
- py_compile:
- smoke:
- full:
- scope grep:
- layer-safety grep:
- backward compat load of real .bmaplan:

## Known Issues
- ...
```

-----

## TEST_RESULT.md Format

```md
# TEST_RESULT.md — Sprint A Semantic Tag Foundation

## Commands
\`\`\`bash
python3 -m py_compile proto/server.py proto/e2e_ui_test.py
python3 proto/e2e_ui_test.py smoke
python3 proto/e2e_ui_test.py full
rg -n "ZONE_RULES|runCheck|FAR|OSR|Rule Engine|OCR|AI checker|ข้อ 41|ข้อ 50|ผังเมือง|Project PDF Save/Load" proto/ui.html proto/server.py proto/e2e_ui_test.py
rg -n "L0 |L1 |L2 |L3 |L4 |L5 |L6 |L7 |L8 |default layer set|layer rename|layer reorder|Photoshop" proto/ui.html proto/server.py
\`\`\`

## Result
- py_compile:
- smoke:
- full:
- scope grep:
- layer-safety grep:

## Semantic Model Verification
- semanticTag default at create:
- semanticTag default at load (no field):
- useCategory editable for areas:
- useCategory disabled for non-area:
- save/load roundtrip:
- backward compat with real .bmaplan:
- XLSX columns added:

## Regression Confirmations
- Project Setup: 
- Measurement UI / MAIN_UI_OK:
- SITE_UI_OK:
- parcel side editor:
- north / orientation:
- draw area:
- draw opening:
- overlapping picker / SELECT_OK:
- layer visibility:
- layer lock:
- properties panel (existing rows):
- object tree:
- XLSX_OK:
- PROJECT_OK:
- ANNOT_OK:
- PERSIST_OK:
- REAL_OK:
```

-----

## FINAL_REPORT_FOR_CHATGPT.md Format

```md
# FINAL_REPORT_FOR_CHATGPT.md — Sprint A Semantic Tag Foundation

## Goal
Add semanticTag + useCategory data foundation. No layer changes.

## Outcome
PASS / FAIL

## Files Changed
- ...

## Model Result
- semanticTag field:
- useCategory field:
- Default mapping:
- Properties UI:
- Save/load:
- Backward compat:
- XLSX columns:

## Tests
- py_compile:
- smoke:
- full:
- scope grep:
- layer-safety grep:
- manual UI:

## Regression Status
- Project Setup:
- MAIN_UI_OK:
- SITE_UI_OK:
- parcel side editor:
- north/orientation:
- area drawing:
- opening drawing:
- layer visibility:
- layer lock:
- properties panel:
- object tree:
- XLSX_OK:
- PROJECT_OK / .bmaplan save/load:
- ANNOT_OK:
- PERSIST_OK:
- REAL_OK:

## Sprint Pipeline Status
- Sprint A (this) — semanticTag/useCategory foundation:
- Sprint B (next) — useCategory dropdown polish + XLSX use category summary: PENDING
- Sprint C (later) — Photoshop-like editable layer model: PENDING

## Known Remaining Gaps
- Layer model still hardcoded (intentional — Sprint C)
- Use category summary not yet in XLSX (intentional — Sprint B)
- UI overhaul (6 zones) not in scope here — separate sprint
- Project PDF Save/Load remains future work
- Legal/building-control skill remains Phase 2
```

-----

## log.md Entry

Add:

```md
### [time] Sprint A Semantic Tag Foundation
**สิ่งที่ทำ:**
- ...

**เหตุผล:**
- เพิ่ม semanticTag + useCategory เป็น data foundation ก่อนทำ Sprint B/C
- แยก data model migration ออกจาก layer migration เพื่อกัน .bmaplan ของจริงพัง
- เก็บ Properties panel เดิมไว้ ไม่ rearrange UI

**ไฟล์ที่แตะ:**
- proto/ui.html
- proto/server.py
- proto/e2e_ui_test.py
- PATCH_SUMMARY.md
- TEST_RESULT.md
- UI_MANUAL_TEST.md
- FINAL_REPORT_FOR_CHATGPT.md
- CURRENT_STATUS.md
- index.md
- log.md

**ผลทดสอบ/ผลตรวจ:**
- py_compile:
- smoke:
- full:
- scope grep:
- layer-safety grep:
- manual UI:
- backward compat load real .bmaplan:

**Known issues:**
- ...
```

-----

## Stop Conditions

Stop immediately if any of these happen:

- Loading `SCR_Permit_Plan_Ele_Sec_29-01-2026.bmaplan` (or current real workspace `.bmaplan`) fails or loses data
- `.bmaplan` save/load roundtrip changes geometry, layer, scale, or page metadata
- Existing XLSX sheets lose any column or row
- `MAIN_UI_OK` / `SITE_UI_OK` / `XLSX_OK` / `PROJECT_OK` / `SELECT_OK` regress
- Any layer-related code changes (rename, reorder, new default set, Photoshop-style refactor)
- Any UI layout change beyond adding 2 rows at the end of Properties panel
- Forbidden strings appear (legal, OCR, AI, Rule Engine, Project PDF Save/Load)
- Patch starts becoming a multi-file rewrite

If stopped, write a STOP report in `FINAL_REPORT_FOR_CHATGPT.md` explaining what was attempted and what blocked.

-----

## Final Instruction

Keep the patch surgical.

This sprint adds **two fields** to the object model. That is the entire feature.

UI overhaul is a separate sprint — do not start it here.

Layer model migration is Sprint C — do not start it here.

useCategory summary sheet is Sprint B — do not start it here.

Backward compat with existing `.bmaplan` is the highest priority. If in doubt, prefer to leave a field as `null` and infer at runtime rather than mutate stored data.

-----

## Run Command

PowerShell:

```powershell
cd "G:\drive\01 project\ai\bma-plan"
codex exec "Read RUN_SPRINT_A_SEMANTIC_TAG_FOUNDATION.md and execute it. Add semanticTag + useCategory data foundation only. Do not touch the layer model. Do not redesign UI. Preserve backward compatibility with existing .bmaplan files. Stop if full test fails or if real .bmaplan stops loading."
```

5-agent pipeline:

```powershell
codex exec "Read RUN_SPRINT_A_SEMANTIC_TAG_FOUNDATION.md and run the same 5-agent pipeline: plan, patch, review/test, docs/check, final report. Add semanticTag + useCategory data foundation only. Do not touch the layer model. Do not redesign UI. Preserve backward compatibility with existing .bmaplan files."
```



