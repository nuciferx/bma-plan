---
name: bma-ui-panel
description: |
  Inspect and propose fixes for BMA-Plan left and right panels only. Verifies Sheets tab, Objects tab, Properties tab, right-panel Layers, selected-object footer, scroll behavior, selection sync. Returns PANEL_PASS / PANEL_RISK / PANEL_FAIL with minimal patch plan.

  Trigger phrases (Thai): "left panel", "right panel", "ฝั่งซ้าย", "ฝั่งขวา", "panel", "Sheets tab", "layers panel"
  Trigger phrases (English): "left panel", "right panel", "Sheets tab", "Objects tab", "Properties tab", "layers panel"

  Do NOT use when: working on summary widget (use bma-summary-widget-specialist) or ribbon (use /bma-ui-ribbon).
---

# /bma-ui-panel — Left/Right Panel Inspector

Goal: scope panel work strictly to left/right panel surfaces. Never touch measurement math, layer scope rules, or page-scoped layer ID logic.

## Left Panel Checklist

1. **Sheets tab** — page list, current-page highlight, page-type badge (site/plan/elev/section), navigation works.
2. **Objects tab** — flat object list for current page, semanticTag badge, count matches page state, click → select object on canvas.
3. **Properties tab** — full property editor for selected object (5 metadata fields + geometry summary). Disabled state when nothing selected.
4. **Inspection panel** — workflow steps, per-page stats, measurement summary, warnings, next action.
5. **Scroll** — each tab body scrolls independently; tab header stays sticky; no double scrollbar.

## Right Panel Checklist

1. **Page-scoped layers list** — driven by `getCurrentPageLayers()`; live object count per layer; visible/locked toggles.
2. **Active layer** — exactly ONE layer highlighted; syncs with `lbl-layer` status bar; clicking activates.
3. **Lock / visible** — toggles affect canvas hit-test (locked = visible-not-selectable) and render visibility.
4. **Selected object footer** — shows selected object's `semanticTag`, `measurementProfile`, layer name, area/length, parent (if opening).
5. **Legacy Properties + ObjectTree** — still present below layers (per CLAUDE.md intentional compat); flag if accidentally hidden.

## Selection sync (cross-panel invariant)

- Canvas select → left Objects tab highlights → Properties tab populates → right panel selected-object footer updates
- Left Objects click → canvas highlights → right footer updates
- Verify both directions.

## Output

```
### Panel UI Check: <target>

Verdict: 🟢 PANEL_PASS / 🟡 PANEL_RISK / 🔴 PANEL_FAIL

Side: left / right / both

#### Left findings
- Sheets: ✅/❌
- Objects: ✅/❌
- Properties: ✅/❌
- Inspection: ✅/❌
- Scroll: ✅/❌

#### Right findings
- Page-scoped layers: ✅/❌
- Active layer: ✅/❌
- Lock/visible: ✅/❌
- Selected footer: ✅/❌
- Legacy compat: ✅/❌

#### Selection sync
- Canvas → Left → Right: ✅/❌
- Left → Canvas → Right: ✅/❌

#### Recommended patch (if RISK/FAIL)
- File: proto/ui.html L<n>–<m>
- Change: <one-line>
- Forbidden surface: <none / layer name calc?>
- Test required: smoke + SELECT_OK
```

## Forbidden cross-contamination

- ❌ Never calculate from `layer.name` / `layer.slug` (Page-Scoped Layer Model).
- ❌ Never compare `layer.id` across pages (page-scoped IDs).
- ❌ Never extend `layerVis` / `layerLock` globals — they are bridge-only.
- ❌ Never modify `validateObjectLayerScope()`.
- ✅ OK: re-style panels, fix scroll, add tab, fix selection sync UI, fix active-layer highlight.

## Required tests

- `py_compile`
- `smoke` — must keep `SELECT_OK` + `MAIN_UI_OK`
- `UI_MANUAL_TEST.md` — manual selection sync in real browser

## Constraints

- Output ≤30 lines.
- Defer left-side details to `bma-left-panel-specialist`, right-side to `bma-right-panel-specialist`.
- Propose only — never auto-apply.
