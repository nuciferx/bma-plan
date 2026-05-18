---
name: bma-measure-ux
description: |
  Scope and propose fixes for BMA-Plan Measure user-interaction only — loupe, undo-point while drawing, Enter to finish, Esc to cancel, Shift/Alt angle lock, preview distance while dragging, cursor guide. Never changes area math or coordinate conversion. Returns MEASURE_UX_PASS / MEASURE_UX_RISK / MEASURE_UX_FAIL with a minimal patch plan.

  Trigger phrases (Thai): "measure ux", "การวาดวัด", "loupe", "undo จุด", "กด Enter จบ", "Esc ยกเลิก", "ล็อกมุม", "เส้นนำเมาส์"
  Trigger phrases (English): "measure interaction", "drawing UX", "undo point", "angle lock", "Enter to finish", "preview distance", "cursor guide"

  Do NOT use when: touching path geometry / shape generators / Bezier math (use /bma-measure-geometry) or pure panel/menu chrome (use /bma-ui-*).
---

# /bma-measure-ux — Measure Interaction Inspector

Goal: improve how the user *interacts* with measurement tools without ever touching the numbers. This skill owns input handling and on-screen drawing feedback — not geometry, not area, not coordinate conversion.

## In scope

- **Loupe** — magnifier visibility, follow-cursor, zoom factor display, clamp inside viewport (do NOT touch what it renders from the canvas — that's render).
- **Undo-point while drawing** — `Ctrl+Z` / Backspace removes the last placed vertex of the in-progress path (NOT global document undo).
- **Enter to finish** — closes / commits the in-progress measurement.
- **Esc to cancel** — discards the in-progress measurement, restores prior tool state.
- **Shift / Alt angle lock** — Shift = ortho/45° constrain, Alt = handle-break (curve-ui handoff); the *constraint application* to the cursor point before it is committed.
- **Preview distance / area while dragging** — the live readout overlay shown during drawing.
- **Cursor guide** — crosshair / alignment guide through the cursor.
- **Tool state transitions** — entering/leaving a measure tool, what resets.

## NEVER touch (route elsewhere)

- `polyAreaM2`, `polyMetrics`, `polySelfIntersects`, `pathAreaM2`, `circleAreaM2` — area math.
- `pdfToC`, `cToPdf`, `RS`, scale math — coordinate conversion. The UX layer reads the *result* of these; it must not change them.
- `flattenPathToPoints`, `renderPath`, segment model — `/bma-measure-geometry`.
- `buildSnapIndex`, `snap` core — snap engine. (Snap *interaction conflicts* with Shift/Alt/loupe ARE in scope to diagnose, but the fix must be in the UX layer, never in snap internals.)
- Save / load / `.bmaplan` schema.

If a fix needs any of the above → STOP, emit `FORBIDDEN_ROUTE` in the verdict, route to `/bma-check-forbidden`.

## Checklist (run in order)

1. **Event wiring** — each interaction (loupe toggle, undo-point, Enter, Esc, Shift, Alt) maps to a real handler in `proto/ui.html`. Flag any `// TODO` / empty / `void 0`.
2. **Key conflict scan** — collect keys used (Enter, Esc, Ctrl+Z, Shift, Alt, Backspace). Cross-check with global keydown handlers — no double-binding, no swallowed default.
3. **State isolation** — undo-point affects only the in-progress path, not committed objects or global undo stack.
4. **Constraint correctness** — Shift/Alt modify the *candidate* cursor point only; verify the committed value still flows through the unchanged coordinate pipeline.
5. **Cleanup** — on Esc / tool change / page change, in-progress state, preview overlay, cursor guide, and loupe all clear.
6. **Throttle** — mousemove-driven feedback (preview, cursor guide, loupe) is rAF-throttled.

## Output

```
### Measure UX Check: <target>

Verdict: 🟢 MEASURE_UX_PASS / 🟡 MEASURE_UX_RISK / 🔴 MEASURE_UX_FAIL

#### Interaction inventory
| Interaction | Handler | Key/Event | Status |
|---|---|---|---|
| Loupe toggle | <fn> | <key> | ✅/⚠️/❌ |
| Undo point | <fn> | Ctrl+Z | ... |
| Enter finish | <fn> | Enter | ... |
| Esc cancel | <fn> | Esc | ... |
| Angle lock | <fn> | Shift/Alt | ... |
| Preview readout | <fn> | mousemove | ... |
| Cursor guide | <fn> | mousemove | ... |

#### Key conflicts
- <list or "none">

#### State isolation
- Undo-point touches in-progress path only: ✅/❌
- Constraints modify candidate point only (math pipeline unchanged): ✅/❌

#### Cleanup
- ✅/❌ on Esc   ✅/❌ on tool change   ✅/❌ on page change

#### Forbidden surface
- <none / FORBIDDEN_ROUTE — which surface>

#### Recommended minimal patches (if RISK/FAIL)
- proto/ui.html L<n>–<m> — <one-line, UX layer only>
- Test required: smoke (MENU_OK + MAIN_UI_OK + WHEEL_OK) + UI_MANUAL_TEST.md

#### Defer to subagent
- bma-measure-ux-specialist for deep event-wiring + snap-conflict map
```

## Constraints

- Output ≤30 lines.
- Never propose a patch that edits area math, coordinate conversion, snap internals, or geometry functions.
- Never auto-apply — propose only; caller (main agent) edits.
- Headless Chromium misses real input-timing bugs → any change requires `UI_MANUAL_TEST.md`.
