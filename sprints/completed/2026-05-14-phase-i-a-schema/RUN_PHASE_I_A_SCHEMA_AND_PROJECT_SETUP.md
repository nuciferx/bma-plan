# RUN_PHASE_I_A_SCHEMA_AND_PROJECT_SETUP — Phase I-A: Site Plan Schema + Project Setup

Date: 2026-05-14 (card created) · revised 2026-05-14 (markerType descoped → Phase I-B)
Branch: main
Status: PASS — completed 2026-05-14 · moved to sprints/completed/2026-05-14-phase-i-a-schema/

## Goal

Additive-only schema groundwork for Site Plan (ผังบริเวณ) measurement. Adds new **area** `semanticTag` enum values, `AREA_LABELS`, an optional `buildingHeight_m` object field, and Project Setup form fields — so later phases (I-B tools, I-C summary) have the data model to build on. **No new behavior, no calculation, no UI tools yet** — purely the schema + Project Setup form fields + backward-compat loader.

Source of truth: `docs/design/SITE_PLAN_MEASUREMENT_PLAN.md` §9, §10, §13 (Phase I-A), §16 (Q1–Q5 DECIDED 2026-05-13, reconciled 2026-05-14).

## Revision note — markerType descoped

`bma-explorer` found markers currently store `parkingType` (car/ev/disabled/...), not `markerType`. Adding `markerType` "properly" would mean either a forbidden `.bmaplan` field RENAME, or a non-trivial additive field + backfill design. Marker placement UI is already Phase I-B — so **all marker work (the `markerType` enum + `fire_escape`/`fire_elevator` etc.) moves to Phase I-B**, done there as a clean additive field with backward-compat backfill from `parkingType`. Phase I-A stays purely area-side and 100% additive.

## Scope — IN (additive only)

### 1. `semanticTag` enum additions
Add 7 area semanticTags across BOTH `proto/ui.html` (`SEMANTIC_TAG_LABELS`, ~L941) and `proto/static/js/semantic-meta.js` (all 5 maps: profile / category / reportTarget / lawBasis where applicable / countingRule):
`building_coverage`, `open_space`, `permeable_area`, `hardscape`, `softscape`, `parking_area_outdoor`, `internal_road`

### 2. `SEMANTIC_TAG_LABELS` enum-registry additions (`proto/ui.html` ~L941)
Register the 7 new semanticTags in `SEMANTIC_TAG_LABELS` (identity-string entries, matching the existing pattern — this map IS the semanticTag enum registry). `AREA_LABELS` (areaType-keyed legacy model) is intentionally NOT touched — semanticTag ≠ areaType.

### 3. Project Setup fields (`proto/ui.html` — Project Info form ~L350 + `projectInfo` object + `syncProjectInfoFromForm` ~L1520 + form-restore on load)
- `buildingClassification`: `"general" | "large" | "tall" | "extra_large"`
- `buildingUseType`: `"residential" | "residential_mixed" | "commercial" | "industrial" | "office" | "public" | "warehouse" | "hotel" | "hospital" | "shop_house" | "townhouse"`
- `userDefinedLimits`: `{ far_max, osr_min_pct, permeable_min_pct, setback_front_min_m, setback_side_min_m, setback_back_min_m }` — all numbers, user-entered (Q1=A)
- `zoneCode`: string label only — **no lookup, no Rule Engine** (Q1=A)
- `siteAccessRoadWidth_m`: number

### 4. Object field — `buildingHeight_m` (Q2=A)
Optional number on polygon objects (`finishCurrentArea` ~L1400). Field is added to the schema and preserved through save/load; **no write-UI in I-A** (the Properties-panel input arrives in I-B). Defaults to `null`/absent.

### 5. Backward compatibility (`applyLoadedProject` ~L1616 in `proto/ui.html`)
Old `.bmaplan` files (no new fields) must load without error — every new field is optional with a safe default via the existing `|| {}` / `|| []` / `?? null` pattern.

## Scope — OUT (later phases — do NOT do here)

- ❌ **`markerType` enum + all marker work** (`parking_disabled` / `parking_fire` / `parking_ambulance` / `entrance` / `aed` / `sign` / `tree` / `fire_escape` / `fire_elevator`) → **Phase I-B** — must be done as an additive new field with backfill from `parkingType`, NOT a rename
- ❌ Site Plan toolbar buttons / new area tools → Phase I-B
- ❌ Default-layer assignment per new semanticTag → Phase I-B
- ❌ `buildingHeight_m` write-UI (Properties panel input) → Phase I-B
- ❌ "วาดแล้วค่อยเลือกว่าเป็นอะไร" Properties-panel hierarchy UI → Phase I-B (see §10.4)
- ❌ Summary Widget "ผังบริเวณ" tab, BCR/OSR/FAR calculation → Phase I-C
- ❌ Reference compare "X / Y" display → Phase I-D
- ❌ Building-to-building distance / `wallEdges` / `wallType` → Phase I-E
- ❌ 2h rule → deferred (needs Phase H.0 — Q4)

## Hard Forbidden — must stay untouched

- `polyAreaM2`, `polyMetrics`, `polySelfIntersects`, `pdfToC`, `cToPdf`, `RS`, scale math, snap engine
- `proto/server.py`
- `.bmaplan` version stays `1` (additive optional fields ONLY — no rename, no removal)
- No calculation from `layer.name` / `layer.slug` — use `semanticTag`
- ❌ No FAR/OSR auto-judgment, no pass/fail, no verdict UI, no Rule Engine, no zone→limit lookup

## E2E Acceptance Criteria

| # | Test | Expect |
|---|------|--------|
| A | New `semanticTag` values assignable to a polygon + survive save → load round-trip | PASS |
| B | Project Setup fields (`buildingClassification`, `buildingUseType`, `userDefinedLimits`, `zoneCode`, `siteAccessRoadWidth_m`) save → load round-trip | PASS |
| C | `buildingHeight_m` on a polygon persists through save → load | PASS |
| D | Old `.bmaplan` (pre-Phase-I-A, missing all new fields) loads with no error, safe defaults | PASS |
| E | `SEMANTIC_TAG_LABELS` contains every new area semanticTag | PASS |
| F | `semantic-meta.js` maps resolve profile/category/reportTarget for every new semanticTag | PASS |
| — | All 19 existing markers still GREEN — no regression | PASS |

Suggested new marker: `PHASE_I_A_OK` covering A–F.

## Test Run (required — schema + save/load = forbidden-trigger surface)

```
python3.11 -m py_compile proto/server.py proto/e2e_ui_test.py
python3.11 proto/e2e_ui_test.py smoke
python3.11 proto/e2e_ui_test.py full
```
Note: host has no `python3.11` — `py -3.12` satisfies the "Python 3.11+" requirement (see CLAUDE.md).

## References

- `docs/design/SITE_PLAN_MEASUREMENT_PLAN.md` §9 (schema), §10 (mapping), §13 (phases), §16 (Q1–Q5 decisions)
- `docs/design/PAGE_SCOPED_LAYER_MODEL.md` — layer model (page-scoped)
- Phase I decisions: Q1=A, Q2=A, Q3=A, Q4=Defer, Q5=A+B (no link) — DECIDED 2026-05-13
