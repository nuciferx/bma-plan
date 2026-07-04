# Invent: lite-layer-menu-ui-fix

- **idea_id**: `2026-07-04-08-59`
- **Status**: invent-done-go → **INV-2026-07-04-001** (queued in PHASE_INDEX active queue)
- **Raw idea** (verbatim): "ใน lite  แก้ไข ui ในส่วนของ เมนู layer"
- **Tags**: bma-plan, lite, ui, layer, p-med
- **Related prior work (in-repo)**:
  - `docs/invent/lite-page-folder-layers.md` — LPFL-1 page-folder layer tree (shipped LPFL-1a)
  - `docs/invent/lfoc-order-b-kind-folders.md` — LFOC ordering
  - `docs/invent/lite-layer-ui-spec.md`, `lite-layer-dnd.md`, `lite-sublayer-tree.md`, `layer-model-rebuild.md`
  - Queued sprints from /idea `2026-05-25-22-31`: **LFOC-1b** (folder-only mode), **LFOC-1c** (empty default folders), **LFOC-1d** (add-layer kind selector), **LFOC-1e** (click-to-warp), **LFLOOR-1b/1c/1d**
- **Runtime surfaces**: `lite/static/js/layer-panel.js` (165), `layer-system.js` (560), `layer-tree.js` (552), `layer-dnd.js` (562), `layer-move.js` (120), `layer-target-ui.js` (308), `page-folder-layers.js` (817)

## Frame

**Refinement (user, 2026-07-04 PICK):** "คิดใหม่ ทบทวน ในกรณีที่ 1 layer ต่อ 1 ชั้น ถ้ามี 100 ชั้น แย่แน่ ควรจะมีวิธีคิดใหม่เลยไหม จากของที่มีอยู่เดิม"

**Problem (draft):** lite's page-folder layer model creates one folder per page/floor, each holding its own layer set. A tall building (50–100 floors → 100+ pages) makes the layer panel an unmanageable wall of near-identical folders: scrolling, finding the active floor, and repeating the same layer setup per floor all degrade linearly with floor count. The user wants a fundamentally different organizing model, not incremental tweaks (explicitly NOT the queued LFOC-1b/1c/1d/1e cards — those stay queued as-is).

**Constraints**
- Raster PDF input; lite stack = no bundler, plain-globals modules; lite size caps (`ui-lite.html` ≤1200 lines, other runtime files ≤1000 — over cap → extract module first)
- Layers are **workflow-only**: calculation / totals / report never read layer name — they use role/semanticTag. Any new model must keep that separation.
- `.bmaplan` schema **additive only** — old v1 files (current `liteLayers` + page-folder data) must load losslessly; new fields optional.
- Vendored measure math untouched.

**Forbidden surfaces this idea must avoid**
`lite/static/js/measure-engine.js`, `RS`, `pdfToC`/`cToPdf`, area math, semanticTag derivation, non-additive `.bmaplan` changes.

**Out of scope**
- Queued LFOC-1b/1c/1d/1e + LFLOOR-1b/1c/1d stay queued as-is (incremental polish; this pass is the model rethink).
- Proto layer panel (proto keeps its page-scoped model).
- Any calculation/report change.

## Eval

Runnable in the sandbox spike (standalone HTML, harness prints per-case PASS/FAIL):

1. **happy — 100-floor scale test**: generate synthetic project: 100 floor pages × 6 layer kinds (~600 layer entities, 2 objects each). Grader: (a) panel initial render < 150 ms (perf.now), (b) DOM nodes in panel < 800 (bounded — virtualized or scoped, not 600 rows), (c) locate + toggle visibility of "ชั้น 57 → ผนัง" in ≤ 3 UI actions (scripted click count).
2. **edge — mixed floor kinds**: 3 basements (B3→B1 reverse), mezzanine between 12–13, roof, plus two floors whose layer names are identical. Grader: ordering follows kind-aware convention (B3,B2,B1,1,2,…,12,M,13,…,ROOF); the two same-named layers stay distinct entities (toggling one never affects the other); no object loses its layer assignment after reorder.
3. **adversarial — v1 round-trip**: load a real current-format `.bmaplan` (folder-per-floor data) into the new model, then save. Grader: every object keeps its layer assignment + visibility/lock state; saved JSON retains all v1 fields (additive check = deep-diff shows additions only); loading the saved file back into the OLD code path (simulated: v1 reader ignores unknown fields) still resolves every object's layer.

## Research

**Verdict: PRIOR_ART_PARTIAL** (bma-researcher, 2026-07-04)

### 1. In-repo prior art
- `lite-page-folder-layers.md` (LPFL-1) — current folder-per-floor model; open Qs on cross-floor sharing
- `lite-sublayer-tree.md` (LST) — `parentId` tree + roll-up totals — spiked, user GO
- `lite-layer-dnd.md` (LDND) — DnD reorder/nest + auto-group — spiked, user GO
- `lfoc-order-b-kind-folders.md` — kind-aware composite folder IDs (`PF_basement_1`…) — rank function designed
- `layer-model-rebuild.md` — proto flat model (mature)
- Queued LFOC-1b/1c/1d/1e + LFLOOR-1b/1c/1d = incremental polish; **none address scalability**

### 2. Incumbents at scale — KEY CONSENSUS
All 5 incumbents **separate the FLOOR/LEVEL axis from the LAYER/TYPE axis — none nest layers under floor folders**:
| Tool | Pattern |
|---|---|
| AutoCAD | LAYERS ⊥ property/group FILTERS ⊥ LAYER STATES (visibility snapshots) |
| Revit | LEVELS (floor axis) ⊥ Categories (type axis) ⊥ View Templates (display presets) |
| QGIS | Layer groups (org only) ⊥ Map Themes (visibility presets) |
| Bluebeam | Flat markup layers + groups (org only) ⊥ Sheets as separate axis |
| PlanSwift/STACK | Sheet-first; trade/zone = **attribute**, not hierarchy |

### 3. JS/UX patterns
Virtualized lists (needed ≥1000 nodes; 600 is borderline), faceted filtering (2 orthogonal facets, AND across / OR within), CAD feature-tree expand/collapse, groups-vs-states orthogonality.

### 4. Literature
Two-level faceted hierarchy is the usable maximum; org structure ⊥ calculation model (never inherit role from parent folder).

### 5. Competitor measurement UX
Bluebeam: flat layers + page tag. Foxit: per-page markup layers. PlanSwift: duplicate sheet per trade rather than deep nesting. STACK: trade/zone attributes, not floor nesting.

**Gap:** not math — **UX integration**: FLOOR × LAYER as two independent axes (grid / facets / context-scoping) instead of the wall-of-folders. Reusable in-repo: LST tree, LFOC-ORDER-B rank, LRV registry pattern.

## Diverge

(bma-inventor, sonnet, 2026-07-04 — verbatim)

### A — Layer-type-once + floor-as-facet   (axis: data-model)
mechanism: LAYERS becomes global/project-wide (~6-10 type entities: gfa/ded-lift/ded-stair/wall/opening/site — not one set per floor). `PF_*` folders stop owning layer copies; they become pure floor-index metadata (page range/tag/kind), i.e. FLOOR is a facet value, LAYER-TYPE is the only tree axis. Objects already carry `catId`+`page`; per-floor visibility divergence handled by new sparse `layer.floorOverrides = {page:{vis,lock}}` (default = layer's global state).
v1 migration: hardest of the five — each existing distinct per-floor layer (e.g. "ผนัง ชั้น 12") must be aliased into its type-bucket + any non-default vis/lock captured as a `floorOverrides` entry. Additive only (old fields kept, nothing renamed), but the collapse logic itself is new code with real data-loss risk if an override is missed.
size cost: ~350-450 LOC across layer-system.js/page-folder-layers.js/layer-tree.js + a migration adapter.
riskiest Eval case: **3 (v1 round-trip)** — the whole model inverts the existing per-floor-copy assumption; losslessness depends entirely on the migration adapter being complete.

### B — Context-scoped panel + global floor search   (axis: UX)
mechanism: zero data change. Panel renders **only the active page's `PF_*` folder** by default (its ~6-10 layers) instead of all 100 folders; a collapsed floor-rail/dropdown lists floor labels for jump-nav; a search box ("57" or "ผนัง") queries across all floors and expands+scrolls to the hit. FLOOR = context switch (like current page-nav tab), LAYER-TYPE = nested exactly as today under the active folder.
v1 migration: **none** — pure render-layer change on top of unmodified `FOLDERS`/`liteLayers`.
size cost: ~150-220 LOC in `layer-panel.js`/`layer-tree.js` (floor-rail + search index), `layer-system.js` untouched.
riskiest Eval case: **1 (100-floor perf/actions)** — DOM-bound is easy (1 folder rendered), but the floor-rail itself must stay collapsed/virtualized too, and the "≤3 actions" grader lives or dies on search-jump correctness.

### C — Floor-template + lazy instantiation   (axis: algorithm)
mechanism: reuses existing `pageFloorKind` template (normal/basement/mezz/mech/roof) but stops eager-seeding all 100 folders' layers at project setup. `_seedBaseLayers` fires only on first object-draw or first panel-expand of that floor; panel shows lightweight stub rows (id+label+kind, no children) until materialized, then caches.
v1 migration: old saves already have everything eagerly materialized — treat as `folder.materialized=true` (new flag, default true for legacy), only NEW floors take the lazy path. Fully additive.
size cost: ~180-250 LOC (materialization gate + stub renderer).
riskiest Eval case: **2 (mixed floor kinds)** — stub list must still sort by the LFOC-ORDER-B kind-aware rank *before* children exist; a lazy-materialize bug could reorder or drop the rank on first expand.

### D — Virtualized flat list + 2-facet filter chips   (axis: representation)
mechanism: flattens every (floor, layer-kind) pair into one array (~600 rows, underlying `FOLDERS`/`LAYERS` unchanged) and renders it through a hand-rolled windowed scroller (no lib) showing ~20 DOM rows regardless of total count. Two facet-chip groups — Floor (multiselect B3..Roof) and Layer-kind (gfa/ded/wall/...) — AND across facets, OR within one. FLOOR and LAYER-TYPE are pure orthogonal filters, nesting is gone.
v1 migration: **none** — reads existing model as-is, flattens only at render time.
size cost: ~300 LOC — virtualization/windowing hand-rolled is the fiddliest code of the five.
riskiest Eval case: **1(b) DOM-node bound** — an off-by-one in the windowing math fails the `<800 nodes` grader outright; highest implementation-bug risk.

### E — Visibility-state presets ("Themes")   (axis: integration)
mechanism: tree/folders/layers stay **exactly as today** — zero change to `FOLDERS`/`LAYERS`/`PF_*`. New additive top-level array `liteLayerStates: [{id, name, visMap, lockMap}]` (AutoCAD Layer States / QGIS Map Themes pattern) — a saved snapshot the user applies from a small dropdown ("เฉพาะชั้น 57", "โครงสร้างทั้งหมด") to flip many layers' visibility/lock in one action.
v1 migration: fully additive, empty array if absent.
size cost: ~150 LOC (preset CRUD + apply fn + dropdown).
riskiest Eval case: **1(b) DOM-node bound — genuinely fails standalone.** This approach never reduces panel row count; it only adds a shortcut layer on top of the existing wall-of-folders. Flagging honestly: E is not viable as the sole fix, only as a phase-2 complement to B or D.

All 5: forbidden-surface touch = NO (none edit `measure-engine.js`/RS/pdfToC/cToPdf/area math/semanticTag derivation).

## Score

| approach | novelty | accuracy(state-fidelity) | UX | model-fit | boundary | cost | total |
|---|---|---|---|---|---|---|---|
| A type-once+facet | 4 | 3 | 5 | 3 | 5 | 2 | 22 |
| B context-scoped+search | 3 | 5 | 4 | 5 | 5 | 4 | **26** |
| C lazy template | 3 | 4 | 3 | 4 | 5 | 3 | 22 |
| D virtualized+facets | 4 | 5 | 4 | 4 | 5 | 2 | 24 |
| E visibility presets | 3 | 5 | 3 | 5 | 5 | 5 | **26** |

Rationales (non-obvious cells):
- A model-fit=3: ripples across nearly every layer file (layer-system/page-folder-layers/layer-tree/layer-dnd/layer-move/layer-target-ui) even though calc itself is untouched.
- A accuracy=3: sparse `floorOverrides` is a new indirection layer — real risk of silently losing a per-floor vis/lock override during migration.
- B UX=4 not 5: search-jump is fast but users who want to eyeball 2 floors' layers side-by-side lose that at-a-glance view.
- C UX=3: stub rows still number 100 in the accordion by default — helps perf, not directly the "3 actions" criterion unless paired with B's search.
- D cost=2: hand-rolled windowed scroll (no virtualization lib allowed by size caps) is genuinely fiddly and easy to get subtly wrong.
- E UX=3 + explicit caveat: high score elsewhere is real, but standalone it does not solve the row-count problem — see riskiest-case note above.
- **B and E tie at 26** — but E fails Eval case 1(b) standalone (doesn't touch panel row count), so the tie is not a real dead-heat: B is Eval-viable alone, E is not.

## Recommendation

**Spike B (context-scoped panel + global floor search) first.** Zero schema change (Eval case 3 trivially passes), directly attacks Eval case 1's action-count and DOM-node-bound criteria, and carries none of A's migration-loss risk. **Fallback: D (virtualized flat list + facets)** if B's search-jump UX feels too indirect for users who want to compare multiple floors' layers at once during the spike review. Treat **E as a phase-2 add-on to layer B or D**, never as its own spike target — it fails the core Eval on DOM-node count by design. **A is the "big bet"** long-term architecture (best UX ceiling, matches the incumbent consensus most closely) but too costly/risky for the first of only 3 spike attempts; revisit only if both B and D fail their spikes.

**Phase-5 gate check (orchestrator, Fable):** no approach touches a forbidden surface; none cross Phase 1 boundary → top rank stands, no override needed.

## Spike

- **Approach attempted:** B (context-scoped panel + floor-rail + global search) — first and only attempt needed
- **Artifacts:** `lite/sandbox/invent-lite-layer-menu-ui-fix.html` (standalone, file://, in-page eval harness) + `invent-lite-layer-menu-ui-fix-eval.py` (Playwright driver) + logs/screenshot in `artifacts/invent/lite-layer-menu-ui-fix/` (gitignored)
- **Builder:** sonnet · **First-stage review:** opus (rerun + adversarial verify) · **Final:** Fable

### Eval results (builder run; opus rerun reproduced 3/3)

| Case | Metric | Actual | Expected | Verdict |
|---|---|---|---|---|
| 1 happy (100 fl × 6 layers) | render time | 0.40 ms (rerun 0.20) | < 150 ms | PASS |
| | DOM nodes in panel | 25 | < 800 | PASS |
| | actions to toggle ชั้น57→ผนัง | 3 real DOM events | ≤ 3 | PASS |
| 2 edge (mixed kinds) | rail order after reverse+re-rank | B3,B2,B1,1…12,M,13…ROOF | kind-aware | PASS |
| | same-name "ผนัง" ×2 floors | distinct ids, isolated toggles | isolated | PASS |
| | orphans after reorder | 0/240 | 0 | PASS |
| 3 adversarial (v1 round-trip) | deep-diff load→save | 0 add / 0 rm / 0 chg | additions-only | PASS |
| | v1-reader resolution | 0 orphans | lossless | PASS |

- **Real bug caught by the eval (spike's purpose):** per-floor-local `layer.order` reshuffled layers across floors via global `layersInOrder()` sort → 138 spurious round-trip diffs. Root-cause-fixed to globally-monotonic order matching real `addLayer()` maxOrder+1 convention.

### Opus first-stage review — CONFIRM-WITH-CONCERNS

Verified: field shapes verbatim vs `ui-lite.html` L970-1020; v1 truly never persists vis/lock (case-3 vis/lock grader vacuous-but-honest); order-bug fix real, not grader-papered; interactions via real DOM events; total-document DOM @100 floors = 148 nodes → rail-scoping non-issue.

Concerns for integration stage (not model flaws):
1. Search caps at 30 results — searching a common layer name ("ผนัง") returns 30/100 floors; eval never exercised the cap. Real build needs cap UX (count badge / group-by-floor).
2. Spike is clean-room — not wired into real `layer-panel.js`/`layer-tree.js`; the 25-node win is proven in isolation only. Integration testing mandatory in the build sprint.
3. Round-trip losslessness effectively proven for liteLayers/liteGroups; pageStore passes through by reference (fine — B never touches it).

**Fable final verdict:** eval green + adversarially reproduced; concerns are build-sprint checklist items, not blockers → recommend **GO**, sprint card must carry the 3 concerns as acceptance criteria.

**User checkpoint question (2026-07-04):** "หน้าที่เลือกต้องเชื่อมกับหน้า pdf ที่กำหนดไว้ คิดตรงนี้หรือไม่" → answered: yes by design — `PF_*.pages` (Page Setup binding) IS the link; "active floor" is derived from the PDF page shown on canvas. Must be **bidirectional**: (1) PDF page change → panel context switches to that floor's folder; (2) rail/search jump → canvas navigates to the bound PDF page (subsumes queued LFOC-1e click-to-warp). NOT proven in the clean-room spike (no PDF canvas) → promoted to acceptance criterion #1 of the build sprint.

## Decision

**GO** — user, 2026-07-04 at checkpoint. Additional decisions made at checkpoint:
- **Proportions: P2 Balanced 260px** — chosen from 3 live-switchable presets added to the spike on user request (P1 Compact 190 = live today, P2 Balanced 260, P3 Anchor 320 = full DnD-spike spec). Eval re-passed 9/9 under every preset; screenshots in `artifacts/invent/lite-layer-menu-ui-fix/proportion-p{1,2,3}.png`. P2's `--p-*` token values in the spike are the build reference. This also answers the width question left open by the stalled `lite-layer-ui-spec.md` pass (190 vs 320 → 260 for the layer panel).
- **Bidirectional PDF-page binding** is acceptance criterion #1 (user's explicit requirement) — subsumes queued LFOC-1e.
- Sprint card: **INV-2026-07-04-001** (status queued, scope skill `/bma-lite-dev`) in PHASE_INDEX active queue, carrying opus's 3 concerns as acceptance criteria.
- Approach E (visibility presets) recorded as a phase-2 candidate, separate sprint.

**Model ladder used (per user rule 2026-07-04):** haiku research → sonnet diverge/spike-build → opus first-stage adversarial review → Fable frame/final verdict → human GO.
