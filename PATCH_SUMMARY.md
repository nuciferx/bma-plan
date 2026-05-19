# PATCH_SUMMARY.md — Latest Sprint

> Full patch history: [docs/archive/patch-history-2026-05-09.md](docs/archive/patch-history-2026-05-09.md)

---

# Latest: INV-2026-05-19-001b — ⌘K Command Palette (fuzzy page jump)

Branch: main
Date: 2026-05-19

## Outcome: PASS — py_compile PASS, smoke EXIT 0 (PHASE_INV_PALETTE_OK 10/10), full EXIT 0, JOURNEY_OK

## Summary

Additive ⌘K Command Palette for fuzzy page jump. A fixed-center modal (z-index 9500, above Zen Mode HUDs at 1500) opens on Ctrl+K/Cmd+K with a filter input that narrows pages by number, name, or Thai page-type tag. Keyboard navigation (ArrowDown/Up to move selection, Enter to jump and close, Esc to dismiss) is handled before the generic `inInput` guard so the palette input does not swallow nav keys. A mid-draw guard (`mPts.length===0`) prevents Ctrl+K from hijacking polygon construction. View menu item added. Composes cleanly with Zen Mode and the HT-7 scale gate. No schema, no server, purely transient UI state.

## Files Changed

| File | Change |
|---|---|
| `proto/static/css/app.css` | ~35 LOC — `.cmd-palette` fixed-center modal, input, results list, hint bar, color-coded tag chips |
| `proto/ui.html` | ~120 LOC — `togglePalette`, `closePalette`, `filterPalette`, `_palJumpToIdx`, `_palMoveSel`, `_palEsc`; Ctrl+K keybind; ArrowDown/Up/Enter/Esc palette handlers; View menu item; `#cmd-palette` DOM block |
| `proto/e2e_ui_test.py` | ~95 LOC — `_test_inv_palette` (10 sub-checks), `PHASE_INV_PALETTE_OK` marker |

## Source Files NOT Touched (Forbidden Surfaces)

- `polyAreaM2`, `polyMetrics`, `polySelfIntersects` — UNCHANGED
- `pdfToC`, `cToPdf`, `RS`, scale math — UNCHANGED
- `buildSnapIndex`, `snap` engine — UNCHANGED
- `proto/server.py` — UNCHANGED (no server edit in this sprint)
- `.bmaplan` schema version stays 1; palette is purely transient UI state

## Tests Run

```
python3.11 -m py_compile proto/server.py proto/e2e_ui_test.py  → PASS
python3.11 proto/e2e_ui_test.py smoke                          → EXIT 0 (PHASE_INV_PALETTE_OK 10/10; PHASE_INV_ZEN_OK 10/10; all pre-existing GREEN)
python3.11 proto/e2e_ui_test.py full                           → EXIT 0
bma-human-journey-tester                                       → JOURNEY_OK (45-page permit; 13/13 spec steps PASS; 0 JS errors; HT-Z-3 filed)
```

## Phase 1 Scope Check

- ✅ `polyAreaM2` / `polyMetrics` / `polySelfIntersects` — UNCHANGED
- ✅ `pdfToC` / `cToPdf` / `RS` / scale math — UNCHANGED
- ✅ `buildSnapIndex` / `snap` engine — UNCHANGED
- ✅ `proto/server.py` core endpoints — UNCHANGED
- ✅ `.bmaplan` schema — UNCHANGED (palette is transient; version stays 1)
- ✅ No legal / OCR / AI / Rule Engine / FAR-OSR pass-fail

---

# Previous: INV-2026-05-19-001a — Zen Mode + Sheet Minimap

Branch: main
Date: 2026-05-19

## Outcome: PASS — py_compile PASS, smoke PASS, pure cosmetic changes

## Summary

Pure CSS + DOM `display:none` ribbon cleanup with zero JS logic change. Hid the `#scale-badge` red pill from the ribbon (status bar Scale field already surfaces this state) and hid the `#active-layer-select` ribbon-group (Right panel Layers tab is the primary path; select element preserved in DOM for JS references). Rewrapped the `#btn-report` Review button in a proper `.rsection` + `.rlbl` + `.rrow` structure so it renders at the same 60px uniform height as all other ribbon groups. Reverted `body { font-size }` from 16px back to 14px after real-Chrome testing showed layout shifts.

## Files Changed

| File | Change |
|---|---|
| `proto/static/css/app.css` | `body { font-size: 16px }` → `14px` (1-line revert) |
| `proto/ui.html` | `#scale-badge` `display:none`; `.ribbon-group` wrapping `#active-layer-select` `display:none` + 2 `rdiv` dividers removed; `#btn-report` rewrapped in `.ribbon-group.rsection` with `.rlbl "📊 REVIEW"` + `.rrow` + leading `rdiv` |

## Source Files NOT Touched (Forbidden Surfaces)

- `polyAreaM2`, `polyMetrics`, `polySelfIntersects` — UNCHANGED
- `pdfToC`, `cToPdf`, `RS`, scale math — UNCHANGED
- `buildSnapIndex`, `snap` engine — UNCHANGED
- `proto/server.py` — UNCHANGED
- `.bmaplan` schema version stays 1; no schema fields changed

## Tests Run

```
python3.11 -m py_compile proto/server.py proto/e2e_ui_test.py  → PASS
python3.11 proto/e2e_ui_test.py smoke  → PASS (all 18 markers GREEN)
full not run: no forbidden-trigger surfaces touched
```

## Phase 1 Scope Check

- ✅ All forbidden surfaces — UNCHANGED
- ✅ `.bmaplan` schema — UNCHANGED (version stays 1)
- ✅ No legal / OCR / AI / Rule Engine / FAR-OSR pass-fail

<!-- older Previous (Page Setup trilogy + Settings v2) archived to docs/archive/patch-history-2026-05-09.md -->
