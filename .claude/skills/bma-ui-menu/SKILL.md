---
name: bma-ui-menu
description: |
  Inspect and propose fixes for the BMA-Plan menu bar and dropdowns only. Verifies item count, dropdown items, action mapping, shortcut conflicts, disabled/placeholder items, click-outside / Esc close behavior. Returns MENU_UI_PASS / MENU_UI_RISK / MENU_UI_FAIL with a minimal patch plan.

  Trigger phrases (Thai): "เมนูบาร์", "menu bar", "dropdown", "เมนูบน", "ลูกศรเมนู", "menu ไม่ทำงาน"
  Trigger phrases (English): "menu bar", "top menu", "dropdown menu", "menu shortcut", "menu item missing"

  Do NOT use when: working on ribbon toolbar (use /bma-ui-ribbon) or status bar (use /bma-ui-status).
---

# /bma-ui-menu — Menu Bar Inspector

Goal: scope menu-bar UI work strictly to menu-bar surfaces. Never touch geometry, save/load, or export logic.

## Checklist (run in order)

1. **Menu item count** — current count of top-level menus (File / Edit / View / Tool / Layer / Page / Help, etc.). Match against `SITE_PLAN_UI_MOCKUP.md` expected count.
2. **Dropdown items** — for each dropdown, list items + their action handler binding.
3. **Action mapping** — every menu item must call an existing function in `proto/ui.html`. Flag any item whose handler is `// TODO`, `void 0`, or empty.
4. **Shortcut conflicts** — collect all `data-shortcut` attributes; verify no two menu items share the same keystroke. Cross-check with global keydown handlers (Ctrl+S, Ctrl+Z, etc.).
5. **Disabled / placeholder items** — list any items rendered grey or with `disabled` attribute. Confirm each has a documented reason (Phase 1 scope deferral, etc.) — otherwise flag as RISK.
6. **Click-outside / Esc close** — verify dropdowns close on:
   - click outside the menu DOM subtree
   - pressing `Escape`
   - selecting an item
   - opening a different top-level menu

## Output

```
### Menu UI Check: <target>

Verdict: 🟢 MENU_UI_PASS / 🟡 MENU_UI_RISK / 🔴 MENU_UI_FAIL

#### Inventory
- Top-level menus: N (<list>)
- Total dropdown items: M
- Items with missing handler: <list or "none">
- Items disabled without reason: <list or "none">

#### Shortcut conflicts
- <conflict list or "none">

#### Close behavior
- ✅/❌ click-outside
- ✅/❌ Escape
- ✅/❌ item-select
- ✅/❌ open-another-menu

#### Recommended patch (if RISK/FAIL)
- File: proto/ui.html L<n>–<m>
- Change: <one-line minimal>
- Forbidden surface: <none / which>
- Test required: smoke + MENU_OK marker
```

## Forbidden cross-contamination

- ❌ Never edit menu handlers that call `polyAreaM2` / `pdfToC` / `cToPdf` / `RS` / `snap` internals.
- ❌ Never change `.bmaplan` save fields from a menu sprint.
- ❌ Never reroute Export menu items to a different endpoint.
- ✅ OK: re-wire a menu item's `onclick`, add a new shortcut, fix dropdown close, add a tooltip.

## Required tests after change

- `py_compile`
- `smoke` — must keep `MENU_OK` marker GREEN
- `UI_MANUAL_TEST.md` — manually verify dropdown close behavior in real browser (headless Chromium has caught dropdown bugs that work on real Chrome)

## Constraints

- Output ≤30 lines.
- Defer to `bma-menu-bar-specialist` subagent for deep inspection of selectors + handler mapping when needed.
- Never auto-apply patches — propose only.
