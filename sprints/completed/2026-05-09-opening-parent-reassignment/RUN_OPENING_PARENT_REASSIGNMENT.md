# RUN_OPENING_PARENT_REASSIGNMENT.md

## 0. Sprint Identity

Sprint Name: Opening Parent Reassignment
Sprint Type: Implementation / UI Feature
Status: PASS
Date: 2026-05-09

---

## 1. Current Condition

Baseline PASS after commits 94529c5 (proto) / fc5134c (root).

Existing opening parent state:
- `linkOpeningParent(op, polys)` auto-links when exactly 1 poly geometrically contains the opening.
- parentStatus can be: "linked", "ambiguous" (multiple candidates), "unlinked" (no candidates).
- The right panel Properties section for a selected opening shows Parent as a static `<div>` text only.
- No UI exists to manually override parentId.
- Unlinked openings cause a warning in currentWarningCount() and appear as `unlinkedWarnings: 1` in tests.

---

## 2. Goal

When an opening's parentStatus is "ambiguous" or "unlinked", show a `<select>` dropdown in the
right panel Properties section listing all closed polys on the page. Selecting a poly immediately
sets op.parentId, re-runs linkOpeningParent to confirm the link, updates the warning count, and
redraws.

When parentStatus is "linked", keep the existing read-only display (parent name).

---

## 3. Approach

- In `buildRightPanel()`, for a selected opening, replace the static parent `<div>` with:
  - A `<select id="rp-opening-parent">` when parentStatus is "ambiguous" or "unlinked".
  - A `<div>` (existing read-only display) when parentStatus is "linked".
- Add `rpSetOpeningParent(id)` function: sets op.parentId, re-runs linkOpeningParent, pushes undo,
  saves current page, updates summary, redraws, rebuilds right panel.
- The select lists all closed polys with their display names; value is poly.id.
  First option is "— เลือก parent —" with empty value.
- E2E: extend SELECT_OK test to verify that after manual parent assignment, parentId is set and
  warning count drops (or parentStatus becomes "linked").

---

## 4. Files Allowed

- `proto/ui.html` — update buildRightPanel opening case, add rpSetOpeningParent
- `proto/e2e_ui_test.py` — extend SELECT_OK parentReassign assertion

## 5. Files Forbidden

- `proto/server.py`
- `proto/requirements.txt`
- Legal/OCR/AI/Rule Engine logic

---

## 6. Acceptance Criteria

- [x] When opening parentStatus == "linked": right panel shows read-only parent name (unchanged)
- [x] When opening parentStatus == "ambiguous" or "unlinked": right panel shows `<select id="rp-opening-parent">` with all closed polys as options
- [x] Selecting a poly from the dropdown calls rpSetOpeningParent(id) and sets op.parentId
- [x] After assignment, parentStatus becomes "linked" and right panel re-renders as read-only display
- [x] undo captures the parent assignment
- [x] E2E SELECT_OK includes parentSelectVisible: True, parentReassigned: True
- [x] py_compile PASS
- [x] smoke PASS
- [x] full PASS

---

## 7. Stop Conditions

- Parent geometry validation logic needed
- Broad restructure of linkOpeningParent required
- Tests fail outside parent reassignment flow
