---
name: bma-ui-status
description: |
  Inspect and propose fixes for BMA-Plan status bar only. Verifies tool, scale, objects, warnings, layer, save state, page label. Returns STATUS_UI_PASS / STATUS_UI_RISK / STATUS_UI_FAIL with minimal patch plan.

  Trigger phrases (Thai): "status bar", "แถบสถานะ", "lbl-save", "lbl-scale", "save state label"
  Trigger phrases (English): "status bar", "lbl-save-state", "lbl-tool", "lbl-scale", "lbl-warnings"

  Do NOT use when: changing scale math, layer model rules — use /bma-check-forbidden.
---

# /bma-ui-status — Status Bar Inspector

Goal: scope status-bar work strictly to the seven status fields. Read-only with respect to scale math, layer model, and warning rules.

## The 7 status fields (canonical order)

| Field | Element ID | Source of truth |
|---|---|---|
| Tool | `lbl-tool` | current `tool` state |
| Scale | `lbl-scale` | `pageScales[currentPage]` (manual / auto-unverified / unknown) |
| Objects | `lbl-objects` | `getCurrentPageObjects().length` |
| Warnings | `lbl-warnings` | `warnings` for current page |
| Layer | `lbl-layer` | active layer name for current page |
| Save state | `lbl-save-state` | `isDirty` + `currentProjectHandle` |
| Page | `lbl-page` | `currentPage / pageCount` |

## Checklist

1. **All 7 fields present** in DOM and visible.
2. **Order matches table** above — left to right.
3. **Each field updates reactively**:
   - Tool change → `lbl-tool` updates
   - `setPageScale()` → `lbl-scale` updates
   - Object add/remove → `lbl-objects` updates
   - Warning add → `lbl-warnings` updates
   - Layer activate → `lbl-layer` updates
   - `pushUndo()` / save / load → `lbl-save-state` updates (KNOWN BUG TC-12-B1: first push without prior save still shows wrong text)
   - Page change → `lbl-page` updates
4. **Format**:
   - Scale: "1:100" or "auto" or "—" (never raw number)
   - Save state: "Saved" / "Unsaved changes" / "Manual save required" (per FSAPI handle state)
   - Page: "N / M"
5. **No empty fields** — show "—" placeholder, never blank.

## Known issue

**TC-12-B1 (MINOR)** — `lbl-save-state` stays "Manual save required" instead of "Unsaved changes" after first `pushUndo()` when no prior save exists. Cosmetic. See `KNOWN_ISSUES.md`. A fix here is a candidate sprint.

## Output

```
### Status Bar Check: <target>

Verdict: 🟢 STATUS_UI_PASS / 🟡 STATUS_UI_RISK / 🔴 STATUS_UI_FAIL

#### Field state
- lbl-tool: ✅/❌
- lbl-scale: ✅/❌
- lbl-objects: ✅/❌
- lbl-warnings: ✅/❌
- lbl-layer: ✅/❌
- lbl-save-state: ✅/❌ (TC-12-B1 known)
- lbl-page: ✅/❌

#### Reactive update
- <list any field that does not update on the right trigger>

#### Recommended patch (if RISK/FAIL)
- File: proto/ui.html L<n>–<m> (label render only)
- Change: <one-line>
- Forbidden surface: <none>
- Test required: smoke + relevant marker (SETUP_OK / PROJECT_OK / MAIN_UI_OK)
```

## Forbidden cross-contamination

- ❌ Never modify `pageScales` state from a status-bar sprint — only read it.
- ❌ Never change `isDirty` semantics — only mirror.
- ❌ Never derive layer label from anything except `getCurrentPageLayers()`.
- ✅ OK: relabel, reformat, add tooltip, fix update trigger wiring (call site only).

## Required tests

- `py_compile`
- `smoke` — `SETUP_OK`, `MAIN_UI_OK`, `PROJECT_OK` must stay GREEN
- `UI_MANUAL_TEST.md` — verify each field updates on its trigger

## Constraints

- Output ≤30 lines.
- Defer deep inspection to `bma-status-bar-specialist` subagent.
- Propose only.
