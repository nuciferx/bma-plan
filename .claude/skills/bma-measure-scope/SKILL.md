---
name: bma-measure-scope
description: |
  Run BEFORE any BMA-Plan Measure sprint to classify what kind of measurement work it is and decide whether it is one sprint or must be split. Returns MEASURE_SCOPE_OK / SPLIT_REQUIRED / BLOCKED with forbidden surfaces, required tests, whether full E2E is required, and whether save/load/export compatibility is affected.

  Trigger phrases (Thai): "จะแก้ measure", "measure sprint", "scope measure", "เริ่มงาน measure", "วางขอบเขต measure", "จะทำเครื่องมือวัด"
  Trigger phrases (English): "measure sprint", "scope measure change", "what measure category", "plan measure feature"

  Do NOT use when: editing pure UI chrome (use /bma-ui-scope) or unsure if a surface is forbidden (use /bma-check-forbidden).
---

# /bma-measure-scope — Measure Sprint Scope Classifier

Goal: before any Measure sprint, lock down WHAT category of measurement work it is, so the sprint doesn't bleed into the area-math contract, coordinate conversion, or snap engine — and doesn't stack multiple categories into a mega-sprint.

## Measure Categories (canonical 6)

| Category | What it covers | Region skill | Specialist subagent |
|---|---|---|---|
| `ux` | loupe, undo-point while drawing, Enter finish, Esc cancel, Shift/Alt angle lock, preview distance, cursor guide | `/bma-measure-ux` | `bma-measure-ux-specialist` |
| `geometry-core` | `flattenPathToPoints`, `pathAreaM2`, `renderPath`, `objectAreaM2` path branch, line/cubic segment model | `/bma-measure-geometry` | `bma-path-geometry-reviewer` |
| `shape-generator` | `rectangleToPath`, `circleToPath`, `ellipseToPath`, `arcToCubic`, shape preview/render | `/bma-measure-geometry` | `bma-path-geometry-reviewer` |
| `curve-ui` | pen/curve tool, click=corner, click-drag=Bezier handles, Alt break handle, Shift lock 0/45/90, Enter close, Esc cancel, Ctrl+Z remove last point | `/bma-measure-geometry` | `bma-measure-ux-specialist` + `bma-path-geometry-reviewer` |
| `validation` | pre-review/export object checks — scale present, path closed, self-intersect, opening parent, semanticTag/reportTarget present, flatten tolerance, negative/zero area | `/bma-measure-regression` (checklist section) | `bma-measure-regression-guardian` |
| `export-impact` | any change that reaches XLSX rows, annotated PDF, or `.bmaplan` save shape | (split out) | `bma-measure-regression-guardian` |

## Steps

1. **Parse target** — user describes the measurement change (function, tool, behavior, bug).
2. **Map to category(ies)** above. If unsure, ask ONE clarifying question.
3. **Check forbidden bleed-through** — if the change requires touching any of:
   - `polyAreaM2`, `polyMetrics`, `polySelfIntersects` (area-math contract — add NEW fn next to them, never edit)
   - `pdfToC`, `cToPdf`, scale math, `RS`
   - `buildSnapIndex`, `snap` core
   - `.bmaplan` schema field rename/remove
   - `proto/server.py` core endpoints
   - `layer.name` / `layer.slug` for calculation

   → mark **BLOCKED** and route to `/bma-check-forbidden`.

4. **Count categories touched**:
   - 1 category → `MEASURE_SCOPE_OK`
   - `curve-ui` always implies a `geometry-core` dependency — require geometry core to be PASS first, but this is **sequencing**, not a split, if curve-ui is the only code being written this sprint.
   - 2+ unrelated categories → `SPLIT_REQUIRED` (one sprint per category)

5. **Decide test depth**:
   - `ux` only → `py_compile` + `smoke`
   - `geometry-core` / `shape-generator` / `curve-ui` → `py_compile` + `smoke` + **`full`** (render + path geometry are forbidden-trigger surfaces)
   - `validation` / `export-impact` → `py_compile` + `smoke` + **`full`** (XLSX / annotated PDF / save round-trip)

6. **Output exactly:**

   ```
   ### Measure Scope: <user target one-line>

   Verdict: 🟢 MEASURE_SCOPE_OK / 🟡 SPLIT_REQUIRED / 🔴 BLOCKED

   Category(ies): <list from table>

   Files likely touched:
   - proto/ui.html (geometry/UX inline JS — never polyAreaM2/pdfToC/cToPdf/RS/snap)
   - proto/static/js/*.js (if logic split out there)

   Forbidden surfaces crossed: <none / list>

   Tests required:
   - py_compile (always)
   - smoke (always for code change)
   - full (if geometry / shape / curve / validation / export-impact)

   full E2E required: <yes/no — reason>
   save/load/export compatibility affected: <yes/no — reason>

   Manual check required: <yes/no — what to verify in real Chrome>

   Recommended region skill: <one of the 4 measure skills>
   Recommended specialist: <subagent name>

   <if SPLIT_REQUIRED>Suggested split:
   - Sprint 1: <category A only>
   - Sprint 2: <category B only>
   </if>

   <if BLOCKED>Route to: /bma-check-forbidden — reason: <crossed surface>
   </if>
   ```

## Heuristics for ambiguous targets

- "loupe" / "undo point" / "Enter to finish" / "angle lock" / "cursor guide" → `ux`
- "flatten" / "pathArea" / "renderPath" / "segment model" → `geometry-core`
- "rectangle" / "circle" / "ellipse" / "arc" / "shape tool" → `shape-generator`
- "pen tool" / "Bezier" / "handle" / "curve drawing" → `curve-ui`
- "warn before export" / "unclosed" / "self-intersect" / "missing tag" → `validation`
- "XLSX" / "annotated PDF" / "save shape" / "report row" → `export-impact`

## Constraints

- Total output ≤30 lines.
- Always emit exactly ONE verdict marker.
- If user describes a pure area-math change (e.g. "change how polyAreaM2 sums"), refuse with: "This is the area-math contract — use /bma-check-forbidden. Add a NEW function instead of editing."
- Never propose code edits — this is a scope classifier, not a fixer.
