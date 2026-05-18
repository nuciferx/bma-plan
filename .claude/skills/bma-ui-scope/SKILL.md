---
name: bma-ui-scope
description: |
  Run BEFORE any BMA-Plan UI sprint to classify which UI region is being changed and decide whether the work is one sprint or must be split. Returns UI_SCOPE_OK / SPLIT_REQUIRED / BLOCKED with files likely touched, forbidden areas crossed, tests required, and manual-check requirement.

  Trigger phrases (Thai): "จะแก้ UI", "UI sprint", "scope UI", "แก้ฝั่งหน้า", "เริ่ม UI", "วางขอบเขต UI"
  Trigger phrases (English): "UI sprint", "scope UI change", "what UI region", "plan UI fix"

  Do NOT use when: editing measurement math, coordinate math, save/load, or server endpoints — use /bma-check-forbidden instead.
---

# /bma-ui-scope — UI Region Scope Classifier

Goal: before any UI sprint, lock down WHICH UI region is being changed so the work doesn't cross-contaminate measurement core or stack into a multi-region mega-sprint.

## UI Regions (canonical 8)

| Region | DOM anchor (approx) | Specialist subagent |
|---|---|---|
| `menu-bar` | `#top-bar`, `#top-menu-*` | `bma-menu-bar-specialist` |
| `ribbon` | `#ribbon`, `.tool-btn` group | `bma-ribbon-specialist` |
| `left-panel` | `#left-panel` (Sheets / Objects / Properties / Inspection) | `bma-left-panel-specialist` |
| `right-panel` | `#right-panel` (Layers + Legacy Properties + ObjectTree) | `bma-right-panel-specialist` |
| `canvas-ui` | overlays above `<canvas>` — coord display, zoom badge, loupe, cursor guide | `bma-canvas-ui-specialist` |
| `summary-widget` | `#summary-widget` 4 tabs (Area / Floor / Site / Warnings) | `bma-summary-widget-specialist` |
| `status-bar` | `#status-bar`, `lbl-tool` / `lbl-scale` / `lbl-objects` / `lbl-warnings` / `lbl-layer` / `lbl-save-state` / `lbl-page` | `bma-status-bar-specialist` |
| `modal/dialog` | `#dlg-*`, `#modal-*` | (no dedicated agent — use bma-explorer) |

## Steps

1. **Parse target** — user describes the UI change (selector, behavior, screenshot, complaint).
2. **Map to region(s)** above. If unsure, ask ONE clarifying question.
3. **Check forbidden bleed-through** — if the change requires touching any of:
   - `polyAreaM2`, `polyMetrics`, `polySelfIntersects`, `circleAreaM2`, `pathAreaM2`
   - `pdfToC`, `cToPdf`, `RS`, scale math
   - `buildSnapIndex`, `snap`
   - `.bmaplan` schema field rename/remove
   - `proto/server.py` core endpoints (`/upload`, `/page/{n}`, `/analyse`, export)
   - `layer.name` / `layer.slug` for calculation (Page-Scoped Layer Model)

   → mark as **BLOCKED** and route to `/bma-check-forbidden`.

4. **Count regions touched**:
   - 1 region → `UI_SCOPE_OK`
   - 2+ regions → `SPLIT_REQUIRED` (recommend one sprint per region)

5. **Output exactly:**

   ```
   ### UI Scope: <user target one-line>

   Verdict: 🟢 UI_SCOPE_OK / 🟡 SPLIT_REQUIRED / 🔴 BLOCKED

   Region(s): <list from table>

   Files likely touched:
   - proto/ui.html (DOM + inline JS only — never geometry math)
   - proto/static/css/app.css (if styling)
   - proto/static/js/{semantic-meta,opening-parent}.js (if logic)

   Forbidden areas crossed: <none / list>

   Tests required:
   - py_compile (always)
   - smoke (if proto/ui.html or static touched)
   - full (if menu/save/export/rotation/real-PDF flow touched)
   - UI_MANUAL_TEST.md (always — UI changes per AGENTS §8)

   Manual check required: <yes/no — describe what to verify in real browser>

   Recommended specialist: <subagent name from table>

   <if SPLIT_REQUIRED>Suggested split:
   - Sprint 1: <region A only>
   - Sprint 2: <region B only>
   </if>

   <if BLOCKED>Route to: /bma-check-forbidden — reason: <crossed surface>
   </if>
   ```

## Heuristics for ambiguous targets

- "topbar" / "menu" / "dropdown" → `menu-bar`
- "toolbar" / "ribbon" / "tool button" → `ribbon`
- "sheets list" / "object tree" / "properties editor" / "inspection" → `left-panel`
- "layers" / "active layer" / "layer count" / "selected object footer" → `right-panel`
- "coordinate display" / "zoom" / "loupe" / "cursor guide" → `canvas-ui`
- "summary" / "BCR" / "OSR" / "report tabs" → `summary-widget`
- "status" / "save state label" / "scale label" / "warnings label" → `status-bar`
- "modal" / "dialog" / "popup" / "calibration window" → `modal/dialog`

## Constraints

- Total output ≤30 lines.
- Always emit exactly ONE verdict marker.
- If user describes a measurement bug masquerading as a UI bug (e.g. "area shows wrong number"), refuse with: "This is measurement core, not UI — use /bma-check-forbidden."
- Never propose code edits — this is a scope classifier, not a fixer.
