---
name: bma-ui-ribbon
description: |
  Inspect and propose fixes for the BMA-Plan ribbon toolbar only. Verifies button grouping, tool mapping, active-tool state, no fake/placeholder buttons, responsive overflow. Returns RIBBON_PASS / RIBBON_RISK / RIBBON_FAIL with minimal patch plan.

  Trigger phrases (Thai): "ribbon", "toolbar", "แถบเครื่องมือ", "ปุ่ม tool", "active tool"
  Trigger phrases (English): "ribbon toolbar", "tool button", "active tool state", "ribbon overflow"

  Do NOT use when: working on menu bar (use /bma-ui-menu) or canvas-adjacent UI (use /bma-ui-canvas).
---

# /bma-ui-ribbon — Ribbon Toolbar Inspector

Goal: scope ribbon work strictly to ribbon surfaces. No geometry, no measurement, no save/load.

## Checklist (run in order)

1. **Button grouping** — verify groups match `SITE_PLAN_UI_MOCKUP.md`:
   - Draw group (rect / polygon / circle / ellipse / arc / opening)
   - Annotation group (marker / text / dimension)
   - Edit group (select / move / delete / undo / redo)
   - View group (zoom / pan / rotate / fit)
   - Layer group (active layer / lock / visibility)
   Flag any button outside these groups.
2. **Tool mapping** — every button has a `data-tool` attribute mapped to a valid `setTool(...)` argument. Cross-check the canonical tool list from `proto/ui.html` state region.
3. **Active tool state** — exactly ONE button has the `.active` class at any time. Switching tools toggles correctly. Tool state syncs with status-bar `lbl-tool`.
4. **No fake buttons** — every button calls a real handler. Flag any with `onclick="void 0"`, `// TODO`, or alert('coming soon'). Phase 1 forbids fake UI.
5. **Responsive overflow** — at narrow width, ribbon must overflow gracefully (horizontal scroll or "more" dropdown). Test at 1024px, 1280px, 1440px.

## Output

```
### Ribbon UI Check: <target>

Verdict: 🟢 RIBBON_PASS / 🟡 RIBBON_RISK / 🔴 RIBBON_FAIL

#### Inventory
- Total buttons: N
- Groups: <list>
- Buttons missing data-tool: <list or "none">
- Buttons with no handler (fake): <list or "none">
- Active-state bugs: <list or "none">

#### Overflow behavior
- ✅/❌ @1024px
- ✅/❌ @1280px
- ✅/❌ @1440px

#### Recommended patch (if RISK/FAIL)
- File: proto/ui.html L<n>–<m>
- Change: <one-line minimal>
- Forbidden surface: <none>
- Test required: smoke (verifies tool switch flow)
```

## Forbidden cross-contamination

- ❌ Never edit `setTool()` body itself if it touches snap, coordinate math, or RS.
- ❌ Never add a ribbon button that maps to a Phase 1-forbidden feature (auto boundary, legal check, OCR).
- ✅ OK: re-group buttons, fix active-state CSS, add tooltip, fix overflow.

## Required tests

- `py_compile`
- `smoke` — verifies tool dispatch
- `UI_MANUAL_TEST.md` — manual verify at 3 viewport widths

## Constraints

- Output ≤30 lines.
- Defer deep inspection to `bma-ribbon-specialist` subagent.
- Propose patches only — never auto-apply.
