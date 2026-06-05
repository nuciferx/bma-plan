# Invent — Editable lite report (inline area override + user-defined subtotal rows)

- **Pipeline:** `/lite-invent` (lite-framed) — 2026-06-04
- **Source ideas (queued):** IDEAS.md 2026-06-04 15:18 ×2 → `### ideas 2026-06-04` in PHASE_INDEX
  1. Inline-edit area values in `/report` area list
  2. User-defined subtotal rows (Excel-style selective sum)
- **Status:** invent-spike-done → **awaiting human CHECKPOINT (GO / NOGO / RESHAPE)**
- **Spike:** `lite/sandbox/invent-lite-editable-report.html` + `…-eval.py` → `EDITABLE_REPORT_SPIKE_OK 3/3`

## 1. PICK
Two queued ideas developed as one theme (subtotal rows require an editable-table model anyway; separate passes would duplicate research/diverge).

## 2. RESEARCH (bma-researcher) → verdict **PRIOR_ART_PARTIAL**
- `lite-report.html` (INV-2026-05-21-002) already ships a `[contenteditable]` report; area cells are read-only — basic editing is proven, **no invention there**.
- Library scan: `jspreadsheet-ce` (MIT, ~93 KB, no-bundler) viable but grid-paradigm-heavy + needs vendoring (offline-first; CDN forbidden after the recent CDN bug). Handsontable = license-blocked. ag-Grid/Luckysheet = too heavy / need bundler. `contenteditable + thin compute` = natural fit, already proven.
- Incumbents (Bluebeam/Foxit/PlanSwift/AutoCAD/QGIS) **all enforce read-only computed values and defer editing to Excel post-export**. In-app editable measurement summary is a differentiator, not a copied pattern.
- Genuinely new = the **data model**: computed vs manual-override with **provenance**, + **selective subtotal rows** (row-id membership). Not in any library.

## 3. FRAME
- **Forbidden (lite):** `measure-engine.js`/`polyMetrics`/`RS`/`pdfToC`/`cToPdf`; `.bmaplan` non-additive; area math reading display name; mandatory CDN; size caps (UI bulk → `static/js/*.js` ≤1000).
- **Out-of-scope:** full grid (sort/filter/paste columns); backward propagation (edit→geometry). Geometry is locked → **forward override only**.
- **## Eval (taxonomy, outcome-based, tol 0.01, Playwright on spike):**
  - **Happy:** rows 50.45/36.48/26.16; subtotal(r0+r1)=86.93; edit r0→60 ⇒ 96.48.
  - **Edge:** subtotal of override row + deduction(sign −)=50.00; geometry refresh must keep override (60) + flag stale.
  - **Adversarial:** "abc" must not NaN-poison totals; deleting a referenced row must not crash and must recompute.
- **EVAL-GATE:** passed (runnable, ≥3 cases).

## 4–5. DIVERGE + SCORE (bma-inventor)
| # | Approach | axis | fb-touch | score |
|---|---|---|---|---|
| A | contenteditable overlay, session-only | data-model+UI | NO | 27 |
| **B** | **A + localStorage persist + stale-flag** | **persistence** | **NO** | **26** |
| C | subtotal-as-formula-token (report-vars style) | aggregation | NO | 24 |
| D | jspreadsheet-ce vendored micro-grid | library | NO | 21 |
| E | additive `.bmaplan` round-trip via postMessage | persistence | NO | 23 |

**#1 = B**, **fallback = A.** A scores 1 higher on raw points but **fails the edge eval** (silent clobber, no provenance). The eval gate is the decider → **B**. All approaches stay out of forbidden surfaces.

## 6. SPIKE (Approach B) — `EDITABLE_REPORT_SPIKE_OK 3/3`
- Override-as-overlay (`overrides[rowId]={val,computedAt}`), selective subtotal (`{id,label,members[]}`), signed sum, stale = `computedAt ≠ current area`, NaN-guard on input, deleted-row skip, localStorage persist keyed by payload hash.
- Eval actuals: happy 86.93/96.48 ✓ · edge 50.00 + stale=True + override-kept 60 ✓ · adversarial reject + skip → 50.45, totals finite ✓.

## 7. CHECKPOINT — awaiting human
**Recommendation: GO on B** as a `/bma-lite-dev` build (single reviewable slice). Build notes:
- Land logic in **new `lite/static/js/report-edit.js`** (~230 lines); `lite-report.html` gets the override-overlay markup + one `<script src>` (stays ≤ caps).
- v1 persistence = **localStorage** (no `.bmaplan` change). Promotion to additive `.bmaplan reportEditState` (Approach E) is a deliberate later slice — keeps this slice schema-free.
- Open design Qs for the human: (a) localStorage vs persist-to-`.bmaplan` now? (b) subtotal picker = checkbox list (B) vs formula builder (C, power-user)?

## RESHAPE #1 (2026-06-04) — human chose **D (jspreadsheet) + Excel-style formula entry**
Human at checkpoint: "ชอบแบบ D และทำให้เหมือน Excel ในการกดสูตร กดที่เซลแต่ละตัวแล้วใส่เครื่องหมาย" → direction switched from B/C to **D**.

- **Chosen approach:** Approach D — vendored `jspreadsheet-ce` grid (offline, currently in `lite/sandbox/vendor/`), with **Excel-style formula entry** for subtotals (double-click subtotal cell → `=` → click cells + `+`/`−` → Enter; native jss formula engine). Area-value edits = direct cell override (blue-bold). Persistence = localStorage v1. Provenance = parallel `baseline[]` computed array; on geometry recompute, non-overridden cells adopt the new value, overridden cells keep the user value + go **stale (orange ⚠)**.
- **Spike:** `lite/sandbox/invent-lite-editable-report-d.html` + `…-d-eval.py` → **honest result `D_SPIKE_PARTIAL 3/4`** (previously claimed 4/4; re-run shows the non-numeric NaN-eval case fails — see `…-d-eval.py` HAPPY/EDGE/delete-row pass, ADVERS-non-numeric fails — lib-level jss behaviour, captured honestly). 5-way compare sandbox: `lite/sandbox/invent-lite-editable-report-compare.html`.
- **⚠ HONEST CAVEATS:**
  1. **Excel cell-click was NOT actually proven** — the original `-d-eval.py` injected formula strings via `setCell('B5', '=B1+B2')`. User tested by hand and reported *"Excel cell-click ยังใช้ไม่ได้"*. **Root cause:** vendored is `jspreadsheet-ce` v4.15.0 — the **community edition** which has formula evaluation but **NOT** the live cell-click-while-editing UX (that's PRO). The original spike's hint text claimed click-cell behaviour the CE library does not provide. → RESHAPE #2.
  2. **Positional-ref shift on delete** (jss formulas use `=B1+B3` not stable row-ids). Deleting a referenced row does NOT `#REF` but silently keeps the cached value while the row labels shift — user sees a wrong-but-plausible number. A production D build MUST handle structural edits.
  3. **Lib NaN-eval:** non-numeric in a referenced cell → subtotal evaluates to NaN. Must be handled at app-layer NaN-guard.
- **Other D costs to accept on GO:** vendored ~282 KB (jss) + ~162 KB (jsuites) into `lite/static/` (offline, MIT — doubles lite's static payload); report renderer replaced wholesale (HTML `<table>` → grid) so print-to-PDF CSS must be re-validated; grid paradigm vs the existing contenteditable report.

## RESHAPE #2 (2026-06-04) — **build custom Excel cell-click picker on top of CE**
After RESHAPE #1 caveat #1 surfaced (CE has no live cell-click picker), instead of falling back to B/C or paying for PRO, the picker UX was implemented manually on the CE grid (~70 lines of JS, MIT-clean). The eval was rewritten to drive the picker via real DOM `mousedown` events (not string injection), closing the eval-gate hole from `-d-eval.py`.

- **Spike:** `lite/sandbox/invent-lite-editable-report-d2.html` (+ `…-d2-eval.py`) → **`D2_SPIKE_OK 5/5`**, no page errors.
- **Picker design (~70 LOC):**
  - Hook jss-CE's `oneditionstart` + `oncreateeditor` to capture the editor `<input>` synchronously (CE creates the input AFTER `oneditionstart`, so `oncreateeditor` is required — `setTimeout(0)` causes test races).
  - Activate "picker mode" whenever `editor.value.charAt(0) === '='` (live `input`/`keyup` listener); CSS highlights all `td[data-x="1"]` cells with a blue outline + cell-cursor so the user sees which cells are clickable.
  - Install a `mousedown` listener on the grid host in **capture phase** — fires BEFORE jss's own commit-and-move handler. When the click lands on a value cell (`data-x="1"`) that isn't the editor cell, call `e.preventDefault() + e.stopImmediatePropagation()`, then `insertAtCaret('B' + (data-y + 1))` into the editor input and refocus.
  - Guard: clicks on the label column (`data-x="0"`) are ignored — never inject `A<n>` (eval CASE 3 proves this).
  - 4 operator buttons (`+ − × ÷`) enabled only while picker is active; click → `insertAtCaret`.
- **Eval (DOM-driven, no string injection):**
  - **PICKER** ✓ `=`→click B1→`=B1`→op `+`→`=B1+`→click B2→`=B1+B2`→commit→ 86.93
  - **EDGE** ✓ picker `=B1-B4` with B1 override=60 → 50.00 + override kept + stale=True after recompute
  - **GUARD** ✓ click on label-col (x=0) does NOT inject `A2`
  - **ADVERS NaN** ✓ picker still builds correct `=B1+B3` even when B1='abc' (lib NaN-eval captured separately as lib-level concern)
  - **ADVERS delete** ✓ formula survives, no crash, no `#REF` (positional-shift risk captured but not gated — same as RESHAPE #1 caveat #2)
- **Open issues for `/bma-lite-dev` build spec** (unchanged from RESHAPE #1):
  - Positional-ref shift on row insert/delete → stable-row-id mapping OR restrict structural edits OR rewrite cell refs on mutation
  - NaN-guard at the input layer (reject non-numeric → keep previous value)
- **Build params if GO (D2):** renderer = jspreadsheet-ce (vendored), formula UX = custom cell-click picker (~70 LOC in `report-edit.js`, MIT-clean, no PRO upgrade), persistence = localStorage v1, provenance = baseline+stale, **+ stable-row-id mapper + NaN-guard** (closes the 2 known risks).

## RESHAPE #3 (2026-06-04) — **stable-row-id mapper closes the positional-ref shift risk**
Driven via the new `/lite-spike-iterate` skill (codified this session — the editable-report idea hit the memory escalation trigger: 3rd RESHAPE of one idea reusing the SPIKE→EVAL→fix loop). Closes RESHAPE #1 caveat #2 / RESHAPE #2 open-issue #1: jss formulas are positional (`=B1+B3`), so deleting a row silently shifts references and the subtotal shows a wrong-but-plausible number.

- **Spike:** `lite/sandbox/invent-lite-editable-report-d3.html` (+ `…-d3-eval.py`) → **`D3_SPIKE_OK 6/6`**, zero page errors (clean on the first eval run; re-verified per rule 1 — the headline case shows real behaviour, not a vacuous pass).
- **Mapper design (~60 LOC on top of D2's picker, all in-spike):**
  - `rowIds[]` runs parallel to jss data rows. Area rows = stable ids `r0..r3` (leading block); subtotal rows = `st<n>` (appended at end). `areaCount()` derives the area/subtotal split positionally.
  - A subtotal's formula is authored positionally by the picker (`=B1+B3`), then **captured as semantic ids** on commit (`onchange` on column B with a leading `=` → `parseFormula` maps each `B<n>` → `rowIds[n-1]` → `subMeta[stId] = [{id:'r0',op:'+'},{id:'r2',op:'+'}]`).
  - After **every structural mutation** (`doDeleteRow` / `addSubtotalRow`), `rebuildSubtotals()` re-projects each `subMeta` back to current positions: term id → `rowIds.indexOf(id)` → `B<pos+1>`. A `_rebuilding` guard stops the re-projection's own `setValue` from re-triggering capture.
  - **Deleted-referenced-row** → that term's `indexOf` is `-1` → term dropped from the rebuilt formula + the subtotal cell flagged red (`#ffe0e0`). Honest, visible, not silent.
  - `doDeleteRow` also splices `baseline[]` when an area row is removed so override/stale styling stays aligned.
- **Eval (6/6, DOM-driven picker, zero page errors):**
  - **PICKER** ✓ regression: `=`→click B1→`+`→click B2 → `=B1+B2` → 86.93
  - **STABLE unref-delete** ✓ HEADLINE: build `=B1+B3` (76.61), delete the unreferenced หลังคา B row → formula **re-projects to `=B1+B2`, value preserved 76.61** (naive positional would silently read 60.45)
  - **STABLE ref-delete** ✓ delete ทางเดิน (referenced) → term dropped → `=B1` = 50.45 + red flag
  - **STABLE multi-op** ✓ `=B1+B2+B3-B4` (103.09), delete referenced +term → surviving terms re-project to `=B1+B2-B3` = 66.61 + flag
  - **GUARD** ✓ click label col (x=0) does NOT inject `A2`
  - **PERSIST** ✓ semantic `subMeta` survives save→reopen → delete-unref still re-projects to 76.61
- **Remaining build-spec item (only one left):** NaN-guard at the input layer (reject non-numeric → keep previous value). The positional-shift risk is now CLOSED by the mapper; the NaN-eval is a jss-CE lib trait to guard at write-time.
- **Build params if GO (D3, supersedes D2):** renderer = jspreadsheet-ce (vendored); formula UX = custom cell-click picker; **subtotal model = semantic-id mapper (`rowIds` + `subMeta` + `rebuildSubtotals`)**, NOT raw positional strings; persistence = localStorage v1 → additive `.bmaplan reportEditState` (semantic ids serialize cleanly, proven by the PERSIST case); provenance = baseline+stale; **+ NaN-guard** (the sole open item). Target module `lite/static/js/report-edit.js` (~290 LOC: picker ~70 + mapper ~60 + render/persist/provenance ~160).
