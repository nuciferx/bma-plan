---
name: bma-ui-canvas
description: |
  Inspect and propose fixes for BMA-Plan canvas-adjacent UI only (NOT geometry math). Covers canvas top bar, coordinate display, zoom display, summary widget position, loupe visual, cursor guide. Returns CANVAS_UI_PASS / CANVAS_UI_RISK / CANVAS_UI_FAIL.

  Trigger phrases (Thai): "canvas UI", "loupe", "ขยาย", "พิกัด", "zoom badge", "cursor guide"
  Trigger phrases (English): "canvas UI", "loupe", "coordinate display", "zoom badge", "cursor guide"

  Do NOT use when: touching pdfToC / cToPdf / RS / snap / polyAreaM2 — use /bma-check-forbidden.
---

# /bma-ui-canvas — Canvas-Adjacent UI Inspector

Goal: scope canvas-overlay UI work strictly to visual overlays. **Never touch** geometry math, coordinate conversion, snap, or render pipeline internals.

## What "canvas-adjacent UI" means

Anything visually attached to or near the canvas that is NOT the geometry itself:
- Canvas top bar (filename / current page / zoom level / fit-to-window button)
- Coordinate display (current PDF coord or metric coord under cursor)
- Zoom badge / zoom percentage / zoom controls
- Summary widget position when docked over canvas
- Loupe (magnifier) visual styling — overlay box, border, zoom factor display
- Cursor guide lines (crosshair extending to canvas edge)
- Snap indicator visuals (markers showing endpoint / midpoint / center / nearest)
- Selection box / marquee visual
- In-progress measurement preview (dashed lines, area readout)

## Forbidden — defer to /bma-check-forbidden

- `pdfToC`, `cToPdf`, scale math, `RS`
- `buildSnapIndex`, `snap` engine logic
- `polyAreaM2`, `polyMetrics`, `polySelfIntersects`, `pathAreaM2`
- Render scale, PDF page render request shape
- Hit-test priority logic

## Checklist

1. **Canvas top bar** — filename + page badge + zoom value visible and accurate. Updates on page change / zoom change.
2. **Coordinate display** — shows current cursor coord. Format = metric when scale=manual, pt when scale=unknown. Updates on mousemove (throttled).
3. **Zoom display** — percentage matches actual canvas transform. Wheel-zoom updates badge instantly.
4. **Summary widget position** — non-overlapping with canvas drawing area by default; user can drag (per widget placement system); persists in `bmaPlan.widgetPlacement.v1`.
5. **Loupe visual** — when active, shows magnified region at cursor; clears on tool deactivate; no pixel leak / ghosting.
6. **Cursor guide** — horizontal + vertical line through cursor when applicable; hidden when measurement preview active.
7. **Snap indicator** — color/icon distinguishes endpoint / midpoint / center / nearest / intersection / perpendicular / close-polygon.

## Output

```
### Canvas UI Check: <target>

Verdict: 🟢 CANVAS_UI_PASS / 🟡 CANVAS_UI_RISK / 🔴 CANVAS_UI_FAIL

#### Visuals checked
- Top bar / page / zoom: ✅/❌
- Coordinate display: ✅/❌
- Zoom badge: ✅/❌
- Summary position: ✅/❌
- Loupe: ✅/❌
- Cursor guide: ✅/❌
- Snap indicator: ✅/❌

#### Recommended patch (if RISK/FAIL)
- File: proto/ui.html L<n>–<m> (DOM/CSS/visual JS only)
- Change: <one-line minimal>
- Forbidden surface crossed: <NONE — abort sprint if any>
- Test required: smoke (WHEEL_OK + SNAP_OK + MAIN_UI_OK must stay GREEN)
```

## Required tests

- `py_compile`
- `smoke` — `WHEEL_OK`, `SNAP_OK`, `MAIN_UI_OK`, `SELECT_OK` must all stay GREEN
- `UI_MANUAL_TEST.md` — manual visual verification at zoom 50% / 100% / 200% / 400%

## Constraints

- Output ≤30 lines.
- Defer deep inspection to `bma-canvas-ui-specialist` subagent.
- If patch unavoidably touches `pdfToC` / `cToPdf` / `snap` / `RS` → return `CANVAS_UI_FAIL` and route to `/bma-check-forbidden`.
