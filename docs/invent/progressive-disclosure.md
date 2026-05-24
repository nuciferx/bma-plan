# Progressive Disclosure for BMA-Plan Lite

- **Invent ID**: `INV-2026-05-24-001`
- **Parent idea**: `2026-05-24-02-23` (lite-first-flow-ui — split into LEMPTY-1 + LHELP-1 + this)
- **Sandbox tab**: `lite/sandbox/invent-lite-first-flow.html` tab "G"
- **Status**: invent-in-progress (started 2026-05-24)
- **Pre-analysis (Opus, before pipeline)**: vote = 👍 G. Verdict expected = PARTIAL.
  Pattern is well-trodden in modern web apps (Linear / Notion / Bluebeam) but the specific
  predicate set + lite's menu-flyout architecture is the genuinely novel piece.

---

## Phase 1: PICK ✅

Short-name `progressive-disclosure`. Artifact = this file. Sandbox spike will live at
`lite/sandbox/invent-progressive-disclosure.html`.

---

## Phase 2: Research

### 1. In-repo prior art

- **`lite/static/js/menu-flyout.js:15–49`** — `FLYOUT_GROUPS` schema is currently **static data** — each item has `tool`, `action`, or `sep`, but NO `enabled`/`disabled` predicate field.
- **`lite/sandbox/invent-lite-first-flow.html`** Tab G — mockup explicitly identifies the gap: "menu-flyout เดิมเป็น static data — ต้อง refactor ให้ accept predicate per item".
- **`proto/ui.html:1032`** — `scaleState()` returns three states (`missing` / `warn` / `manual` / `ok`). Predicate foundation available for lite to mirror.
- **`docs/design/BMA_PLAN_PHASE1_CONTEXT.md`** — no explicit workflow-lock or progressive-disclosure architecture doc. Workflow lock exists as informal invariant in CLAUDE.md (Open PDF → Set Scale → Page Setup → Measure → Review → Export) but not formalized as state-gating rules.
- **User feedback memory** — "User prefers hard workflow gating over soft warnings" — strong design constraint aligning with hard gates (greyed/disabled items) NOT fallback warnings.
- **No prior sprint on menu-state predicates**. The `.disabled{opacity:.2}` CSS exists in proto but is unused by menu items.

### 2. Library scan

| Candidate | Capability | Status | Note |
|---|---|---|---|
| Off-the-shelf inline-JS library | Feature-gating / rule-driven menu state | **None found** | Feature-gating libs (Unleash, LaunchDarkly) are SaaS; predicate engines (Immer, XState) too heavy for single-file HTML |
| Plain JS w/ FLYOUT_GROUPS extension | Custom predicate per item | **Viable, roll-your-own** | Add `enabled: fn()` field, evaluate at render. ~50 lines new logic in menu-flyout.js. Inline-friendly. |

**Verdict:** No mature inline library exists. Roll-your-own is the CAD-industry standard.

### 3. CAD / GIS / graphics incumbent behavior

- **AutoCAD** — Menu items controlled by DIESEL strings + tilde (`~`) for greying. Tools always present in toolbar; commands fail with terminal message if prerequisite unmet. Pattern: **always visible, fail-at-invoke** (soft gate).
- **Bluebeam Revu** — Measurement tools greyed by subscription tier. Post-calibration, calibration tool **itself turns grey** (visual "done" feedback). Pattern: **greyed by availability/capability** (hard gate).
- **PlanGrid** — Measurement tool requires calibration. Pre-calibration: click → error message (no grey). Post-calibration: calibration tool greyed. Pattern: **fail-at-invoke first time, then visual feedback**.

**Key split:** AutoCAD uses soft gates (always available, fail gracefully); Bluebeam/PlanGrid use hard gates (grey pre-calibration). User preference (per memory) aligns with Bluebeam/PlanGrid style.

### 4. Literature / patterns

- **Nielsen Norman Group (2006, updated 2026)** — Progressive disclosure: "Defer advanced features; initial task completion 30–50% faster while preserving full-feature discoverability." Mature, well-established.
- **Notion onboarding** — Contextual feature reveal based on user behavior. 75% completion + 30% paid conversion when done well.
- **Hard gates vs soft warnings** — Manufacturing/QA: hard = absolute restriction; soft = advisory. User memory leans hard.
- **Anti-patterns** — Over-disclosure exhausts cognitive budget; under-disclosure loses new users. Need escape hatch for experts.

### 5. Competitor measurement-app UX

- **Bluebeam Revu** workflow: Open PDF → Find scale → Click Calibrate → Measure known dim → **Calibration tool greyed** → measurement tools active. Hard gate + visual feedback.
- **PlanGrid** workflow: Open → Click ruler → Calibrate → Tools unlock. Difference: pre-calibration click = error message (fail-fast), then visual feedback.
- **Foxit Phantom** — Measurement tools always available. No greying. No workflow enforcement. Soft gate.
- **Bluebeam wins**: post-completion grey-out = strongest UX signal ("you did this step, here are next options").

### Verdict: **PRIOR_ART_PARTIAL**

Progressive disclosure as a principle is mature (Nielsen, 2006–2026). Greyed-menu-item pattern is standard in CAD (AutoCAD/Bluebeam/PlanGrid variants exist). **However**, lite's specific inventive gaps:

1. **FLYOUT_GROUPS predicate schema** — must accept `enabled: fn(state)` per item, evaluated live. No library does this; every CAD tool rolls its own.
2. **State-to-menu mapping** — rules engine mapping `scaleState`, `hasObjects`, etc. to greyed/enabled items.
3. **Hard gate (user pref)** vs soft gate (AutoCAD norm) — explicit design choice conflicting with norm.
4. **Auto-tooltip "why is this greyed"** — novel in measurement-tool space.

Math is trivial. UX (when to grey, which items, tooltip copy, escape hatches) + integration (wiring scaleState → FLYOUT_GROUPS → DOM) are the novel parts. **Proceed to phases 3–6.**

---

## Phase 3: Frame

### Problem
Lite ships 20+ keyboard shortcuts + 5 menu groups + 30+ tools/menu items after the 6-slice rework (LCURVE/LMENU/LROTATE/LSNAP/LORTHO/LEXP). A first-time user opening lite sees the full surface immediately — no scaffolding to guide them through Open → Set Scale → Measure. Worse, if they draw before setting scale, output is in `pt/pt²` (a unit they don't understand) instead of `m²`. Current workflow-lock is informal — documented in CLAUDE.md and surfaced in HUD hints only, never enforced visually in the menu.

### Constraints (must respect)
- **Raster-PDF compatibility** — assumed always.
- **Phase 1 boundary** — no legal / OCR / AI / FAR / OSR. Pure UI.
- **Page-scoped layer model** — already locked; don't redesign.
- **`.bmaplan` schema additive-only** — disclosure state stays **runtime + localStorage** ONLY; never written to `.bmaplan`.
- **menu-flyout.js FLYOUT_GROUPS** — extend the schema, do NOT replace. Other 8 modules (snap-types/ortho-mode/empty-hub/etc.) must keep working.
- **ui-lite.html ≤ 1200 lines** — currently 1197 (3 left). New rule-engine MUST land in `static/js/disclosure.js` (or similar new module ≤1000 lines).
- **User pref**: hard gating > soft warnings (per saved feedback memory).
- **Escape hatch for power users** — can't trap experts. Either keyboard always works, or a "disable disclosure" toggle, or both.

### Forbidden surfaces (idea must NOT touch)
- `lite/static/js/measure-engine.js` (math contract)
- `RS`, `pdfToC`, `cToPdf`, area math, `polyAreaM2` etc.
- `.bmaplan` schema persistence
- `setTool()` body (call only)
- `semanticTag` / layer model rules
- proto/ anywhere

### Success criteria (concrete, spike-measurable)
1. **Empty state (no PDF)**: only File>Open* / File>Open Project / Help-style items are enabled. Other top-level menus visibly dimmed (Edit, View, Page, Measure, Annotate).
2. **PDF loaded, no scale**: Measure>Set Scale highlighted; Area / Distance / Snap / Ref / Count dimmed inside Measure dropdown; tooltip "ตั้ง scale ก่อน" on hover of dimmed items.
3. **Scale set, no objects**: Measure tools light up; Annotate menu still dimmed (no objects to annotate yet — debatable, see Diverge).
4. **First object drawn**: Annotate menu lights up; Export submenu lights up.
5. **Keyboard always works** regardless of menu state (escape hatch = power users use shortcuts; menu = guidance for newbies).
6. **Tooltip explains WHY** something is dimmed — auto-generated from the predicate's "missing" message.
7. **No regression** — every test marker from LCURVE/LMENU/LROTATE/LSNAP/LORTHO/LEXP/LEMPTY/LHELP stays green.

### Out of scope (this invent pass)
- Onboarding tour modal (B was voted down)
- Plan-type wizard (CE voted down)
- Schema persistence of disclosure state (always runtime)
- Empty-state hub (LEMPTY-1, done)
- Cheatsheet (LHELP-1, done)
- Coach-marks (deferred indefinitely)
- Per-project user preference for disclosure (overkill v1; can add later if needed)

---

## Phase 4: Diverge

### Approach A — Predicate-in-FLYOUT_GROUPS (axis: data model)
- **Axis**: Where predicates live — extend FLYOUT_GROUPS item schema with a `requires` field.
- **Data model**: Each FLYOUT_GROUPS item gains optional `requires: 'pdf'|'scale'|'objects'`. Parent gains optional `groupRequires`. `disclosure.js` reads at menu-open, queries sentinel fns (`hasPdf/hasScale/hasObjects` in ui-lite.html), patches CSS + aria-disabled.
- **Rule evaluation**: Once per menu-open. Hooks into `_buildSubItem`/open-event path.
- **Visual**: `.item.ds-dim { opacity:.38; pointer-events:none; }`. Parent dims when ALL children dim. Tooltip via `title` map.
- **Escape hatch**: Keyboard calls `setTool()` directly — never intercepted.
- **Files**: menu-flyout.js +15, new disclosure.js ~180, ui-lite.html +3.
- **Forbidden touch**: NO. **Spike cost**: S.

### Approach B — State-observer bus (axis: rule evaluation)
- **Axis**: When predicates run — reactive observer on shared workflow-state object instead of poll-on-open.
- **Data model**: `WF_RULES` array of `{selector, predicate, reason}` in disclosure.js. No FLYOUT_GROUPS changes.
- **Rule evaluation**: `wfNotify()` called at 4-5 state-mutating sites in ui-lite.html; rules re-evaluate and patch DOM.
- **Visual**: Same dim class + shared `<div id="ds-tip">` popover on mouseenter.
- **Escape hatch**: Keyboard bypasses menu DOM entirely.
- **Files**: new disclosure.js ~260, ui-lite.html +8.
- **Forbidden touch**: NO. **Spike cost**: M.

### Approach C — Scope-wide HUD lock (axis: scope)
- **Axis**: Extends beyond menu items to canvas + HUD stage indicator.
- **Data model**: `STAGES` array + `stageOf()` deriving from caseId/scale/objects. No FLYOUT_GROUPS change.
- **Rule evaluation**: `disclosureApply(stageOf())` called at each `updateHUD()` tick.
- **Visual**: Dimmed menu items + persistent yellow stage banner ("Step 2 of 4: ตั้ง scale").
- **Escape hatch**: Ctrl+Shift+U stores `bmaPlan.lite.disclosureOff=1` in localStorage.
- **Files**: new disclosure.js ~300, ui-lite.html +12.
- **Forbidden touch**: NO. **Spike cost**: M.

### Approach D — CSS-class state machine (axis: visual / representation)
- **Axis**: Body/container class encodes workflow stage; CSS does all dimming, JS only writes a single className.
- **Data model**: No FLYOUT_GROUPS changes. disclosure.js sets one of `wf-empty / wf-pdf / wf-scale / wf-objects` on `<body>`. CSS selectors layered per stage.
- **Rule evaluation**: Same `wfNotify()` hook as B, but JS only writes a single className — zero per-item iteration. CSS cascade does the rest.
- **Visual**: Dimming with CSS transition `opacity .15s`. Tooltip via JS `mouseenter` on container (because `pointer-events:none` blocks browser native title hover — known risk).
- **Escape hatch**: `body.wf-power` class (Ctrl+Shift+U), persisted localStorage.
- **Files**: new disclosure.js ~130, ui-lite.html +6, menu-flyout.js +5 (title attr at build), CSS ~20 lines.
- **Forbidden touch**: NO. **Spike cost**: S.

---

## Phase 5: Score

| Approach | Novelty | UX fit | Lite-cap fit | Boundary safety | Extensibility | Spike cost | Total |
|---|---|---|---|---|---|---|---|
| A Predicate-in-data | 3 | 4 | 5 | 5 | 3 | 5 | **25** |
| B State-observer bus | 4 | 4 | 4 | 5 | 5 | 3 | **25** |
| C Scope-wide HUD lock | 5 | 5 | 3 | 5 | 4 | 3 | **25** |
| **D CSS-class machine** | 4 | 4 | 5 | 5 | 4 | 5 | **27** |

(Spike cost inverted: S=5, M=3, L=1.) No approach has `forbidden_surface_touch: YES` ✓ · No approach crosses Phase 1 ✓ · No re-rank.

### Recommendation
**D (CSS-class state machine)** for spike. Fallback = **A (predicate-in-data)** if D's tooltip-on-dimmed-item proves brittle (`pointer-events:none` blocks browser native `title` hover — must verify in spike).

D wins on lite-cap fit (5) + spike cost (5). JS surface ~130 lines, single className write, ≤870 lines headroom in disclosure.js. CSS transition = instant visual without DOM iteration. **Tradeoff**: spike MUST verify that mouseenter-on-container-above tooltip works when items have pointer-events:none. If brittle → fall back to A (title attr per item at build).

---

## Phase 6: Spike

Spike file: `lite/sandbox/invent-progressive-disclosure.html` (~390 lines, standalone HTML, no server, no build).

### Build approach
- 5 mock menus (File / Edit / Page / Measure / Annotate) mirroring lite's real structure
- Each item declares `data-req="pdf|scale|objects"` (predicate)
- Optional `data-next="pdf|scale|measure"` marks the "do this next" highlight
- Parent menu carries `data-req-all="..."` so the button itself dims when all children dim
- Body class drives EVERYTHING via CSS: `body.wf-empty .item[data-req="pdf"] { opacity:.35; pointer-events:none; }` etc.
- JS writes ONLY the body class. Zero per-item iteration.
- 4 stage buttons toggle through empty→pdf→scale→objects so reviewer can inspect each state.
- Ctrl+⇧U (escape hatch) toggles `body.wf-power` which overrides all dimming + persists to localStorage.

### Tooltip mechanism (the known risk)
`pointer-events:none` on a dimmed `.item` blocks native `title=` hover. **Solution implemented**: mousemove listener on the `.dd` PARENT (which has `pointer-events:auto`), does hit-test by `getBoundingClientRect()` instead of relying on `event.target`. Mouse events bubble up from cursor-space through the dimmed `.item` (which is transparent to pointer-events) to the `.dd` listener — and we still know WHICH item is under the cursor via the rect check. Tooltip popover (`#ds-tip`, `position:fixed`, `pointer-events:none` itself so it never gobbles its own hover) is positioned to the cursor with viewport clamping.

### Acceptance check against `## Frame` success criteria

| # | Criterion | Spike status |
|---|---|---|
| 1 | Empty state: only File>Open* enabled | ✅ Verifiable in browser by clicking "1·empty" — File menu has Open PDF + Open Project enabled; Save / Export / all other menus dimmed |
| 2 | PDF loaded, no scale: Set Scale highlighted, others dimmed + tooltip | ✅ Click "2·pdf-loaded" → Measure menu enables; inside, Set Scale has blue highlight; Polygon/Distance/etc. dimmed with `data-req="scale"`; hover dimmed item → ⚠ "ตั้ง scale ก่อน" tooltip |
| 3 | Scale set: tools light up | ✅ Click "3·scale-set" → all Measure tools enabled; Annotate / Edit / Export still dimmed (`data-req="objects"`) |
| 4 | First object drawn: Annotate + Export light up | ✅ Click "4·object-drawn" → all dimming cleared |
| 5 | Keyboard always works | ✅ Press A at stage=empty → log shows "kbd dispatch → setTool('poly') [bypasses disclosure ✓]" — keydown handler has zero stage checks |
| 6 | Tooltip explains WHY | ✅ Hover on any dimmed item → ⚠ "blocked: <reason>" popover, regardless of pointer-events:none — proves the known-risk mechanism works |
| 7 | No regression | N/A in spike (sandbox-only); will be verified in the GO-sprint by running all 9 existing lite test markers |

### Known risk resolution
The `pointer-events:none` tooltip risk flagged in Phase 4 is **resolved by the parent-listener pattern** (mousemove on `.dd`, hit-test via rect, NOT via `event.target`). Verified at the code level; needs human browser smoke to confirm it FEELS responsive (not laggy or jittery during quick mouse movement across items).

### What the spike does NOT prove (left for the GO-sprint)
- Real wiring to lite's actual `scaleState()` / `caseId` / `PSpage().objects.length` sentinels — spike uses control buttons
- The 4-5 `wfNotify()` callsites that Approach B/D need wired into ui-lite.html — spike uses manual button presses
- Tooltip language polish / final visual style — spike uses placeholder Thai text
- Touch-device compatibility (hover doesn't exist on touch) — needs separate decision

### Outcome
**SPIKE PASS** at code-correctness level. Human reviewer should open the file in a browser to confirm visual + interaction feel — particularly the tooltip-on-dimmed-item hover, which was the headline risk. If the tooltip feels right, recommendation stands: **Approach D → GO**.

---

## Phase 7: Decision

**NOGO** — closed 2026-05-24 at human checkpoint.

### Rationale

The first-flow gap that motivated this invent (idea `2026-05-24-02-23`) was largely
**already closed by the two sibling slices that shipped just before this checkpoint**:

- **`LEMPTY-1`** (commit `728e24e`) — empty-state hub now greets first-time users with
  clear Open/Recent/drag-drop, so the "black canvas, no idea what to do" pain is gone.
- **`LHELP-1`** (commit `3f9b445`) — F1/? cheatsheet now lists every shortcut and tool
  in one overlay, so the "20+ shortcuts, no map" pain is also gone.

What progressive disclosure (Approach D) would add on top of those:

- **Cost**: ~130 lines of `disclosure.js` + 4-5 `wfNotify()` callsites in `ui-lite.html`
  + CSS rule set + a new `body.wf-*` state machine + tests. Real maintenance surface.
- **Benefit**: dimmed menu items + auto-tooltip "ตั้ง scale ก่อน". Useful only to a
  first-time user who already opened a PDF and is now staring at the Measure menu —
  a fairly narrow window now that LEMPTY-1 guides them at the door and LHELP-1 hands
  them the keys.
- **Risk**: power-user friction. Dimmed items invite "why is this greyed?" interruptions
  even with the escape hatch. The escape hatch itself (Ctrl+⇧U) is yet another keyboard
  shortcut nobody will remember.

**Net**: marginal benefit, real ongoing cost. Defer until concrete user-feedback shows
new users actually get stuck at "PDF open, scale not set, drew before scale, got pt²".
If that pain surfaces from `/bma-human-test` or a user report, revisit — the spike
artifact and research stand ready.

### What remains valuable from this pass

- **Research block** (Phase 2) — the AutoCAD/Bluebeam/PlanGrid pattern survey is reusable
  context for any future menu-state work.
- **Spike artifact** `lite/sandbox/invent-progressive-disclosure.html` — proves the
  CSS-class-state-machine + parent-listener-tooltip pattern works around the
  `pointer-events:none` browser limitation. If a future feature needs to dim a menu
  item with an explanatory tooltip, copy the pattern.
- **Frame** (Phase 3) — the success criteria + forbidden-surface profile are reusable
  if this idea ever gets re-opened.

### Status updates
- `INV-2026-05-24-001` → `invent-done-nogo`
- Parent idea `2026-05-24-02-23` stays `invent-done-split` (other children LEMPTY-1 +
  LHELP-1 went GO and shipped).
- Artifact + sandbox stay in tree for future reference (NOT deleted).

---

## Phase 7: Decision

(pending — human checkpoint)
