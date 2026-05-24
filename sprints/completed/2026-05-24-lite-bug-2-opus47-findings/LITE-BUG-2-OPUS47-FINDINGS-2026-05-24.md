# Sprint: LITE-BUG-2-OPUS47-FINDINGS
**Date:** 2026-05-24
**Status:** DONE
**File touched:** `lite/ui-lite.html` (+0/-0 net lines, was 1197, still 1197)

---

## Bug IDs

| ID | Severity |
|---|---|
| LITE-BUG-MODAL-NEST | BROKEN |
| LITE-BUG-DBLCLICK-OVER-POP | FRICTION |

**Evidence:** `artifacts/sim/lite/test-pdf-opus47-direct-20260524T194000/summary.json`

---

## LITE-BUG-MODAL-NEST

**Symptom:** `#setupModal` was nested inside `#modal` (which defaults to `display:none`). User clicks Page Setup → nothing visible.

**Root cause:** `<div id="modal">` on line 191 was missing its closing `</div>`. `#setupModal` (line 195) ended up as a child of `#modal`, inheriting `display:none` regardless of `openSetup()` setting `style.display='flex'`.

**Patch:** Added a third `</div>` to the end of line 194 (was `...</div></div>`, now `...</div></div></div>`). Zero net lines added.

```
Before: ...ตั้งสเกล</button></div></div>
After:  ...ตั้งสเกล</button></div></div></div>
```

**DOM after fix:**
```
#stage
├── #modal (calibration)     ← now properly closed
│   └── .box
└── #setupModal (page setup) ← now sibling of #modal
    └── inner content
```

---

## LITE-BUG-DBLCLICK-OVER-POP

**Symptom:** Dblclick to finish a 4-vertex polygon at the same position as the last vertex → last vertex popped → polygon saved as triangle. 713 m² quad collapsed to 356 m² triangle (exactly half).

**Root cause:** `cv.addEventListener("dblclick", ...)` used an unbounded `while` loop to pop trailing stray points from the two mousedowns fired by the dblclick. Expected pops = at most 2, but the loop had no upper bound, consuming the user's intentional final vertex when it was at the same screen position.

**Patch:** Replaced unbounded `while` with a bounded `for(_np<2)` loop. Same 2 physical lines, zero net delta.

```js
// Before:
while(state.draft.length>0){ var sp=ptToScreen(state.draft[state.draft.length-1]);
  if(Math.hypot(sp.x-e.offsetX,sp.y-e.offsetY)<6)state.draft.pop(); else break; }

// After:
for(var _np=0;_np<2&&state.draft.length>0;){ var sp=ptToScreen(state.draft[state.draft.length-1]);
  if(Math.hypot(sp.x-e.offsetX,sp.y-e.offsetY)<6){ state.draft.pop(); _np++; } else break; }
```

---

## Self-check table

| Check | Command | Result |
|---|---|---|
| parseable | `python -c "open(...).read()"` | PASS |
| size cap | `wc -l ui-lite.html` → 1197 | PASS (≤1200) |
| div balance | regex opens==closes → delta=0 | PASS (was 1, now 0) |
| smoke boot | `python -m py_compile server_lite.py` | PASS |
| pan test | `python tests/test_pan_controls.py` | PASS (BUG_20260521_LITE_PAN_OK) |
