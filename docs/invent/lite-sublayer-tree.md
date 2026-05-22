# Invent — Lite Sublayer Tree (A+B Hybrid)

- **idea_id**: `2026-05-22-23-15` (lite-sublayer-tree)
- **Pipeline**: `/lite-invent` (lite-framed invention pass)
- **Date**: 2026-05-22 → checkpoint GO 2026-05-23
- **Verbatim idea**: "พัฒนา layer ใน lite ทำให้เวลาเพิ่มเลเยอร์ เป็น sublayer แบบ tree"
- **Spike**: `lite/sandbox/invent-lite-sublayer-tree.html` (compares A–E + chosen hybrid F)
- **Checkpoint result**: **GO** — Approach **F (A+B Hybrid)** with roll-up + global layer scope
- **Build path**: `/bma-lite-dev` (one reviewable slice at a time; lite has no full-auto loop)

---

## 1. FRAME

**Problem.** Lite layers are a flat list (6-role model + custom layers, L1–L2c done). User wants to nest them as a tree — adding a layer can place it as a sublayer, Bluebeam/Photoshop style.

**Success criteria.**
- Tree UI: expand/collapse, nest/un-nest, arbitrary depth.
- A node can be a **folder** (organizational, no role, no objects) OR a **layer** (has role, holds objects).
- Child inherits **visibility + lock** from its parent (folder or layer), walking the parent chain.
- Child keeps its **own role / semanticTag** — never inherited. Area calc / deduction / export grouping unchanged.
- Folders show a **realtime roll-up total** (signed sum of all descendant layers' own areas; deductions subtract).
- `.bmaplan` round-trips; **proto cross-opens** lite tree files with identical area values.
- Old flat `.bmaplan` files load as all-root (backward compatible).

**Forbidden surfaces (lite frame).** `lite/static/js/measure-engine.js` (vendored, parity-locked), `RS`, `pdfToC`/`cToPdf`, area math. `.bmaplan` **additive only** — no renames/removals. proto cross-open parity must hold.

**Hard constraint (THE CRUX).** `semanticTag` is **role-derived** (`resolveSemanticTag` = `roleSemanticTag(layer.role)`). It must NEVER be inherited from a parent. A `ded` child under a `gfa` parent must still subtract correctly. The tree is for *organization + visibility/lock inheritance + roll-up display*; *calculation stays flat over roles*.

**Out of scope.** page-scoped layers (lite stays **global per project** — see decision below); drag-and-drop reorder (▲▼ + reparent action is enough for v1; drag = enhancement).

---

## 2. RESEARCH (delegated to `bma-researcher`, verdict `PRIOR_ART_PARTIAL`)

- **No layer-tree exists in BMA-Plan.** proto deliberately chose the flat CAD model (`PAGE_SCOPED_LAYER_MODEL.md` LOCKED); the layer-model-rebuild invent verdict was `PRIOR_ART_MATURE` for the flat model. `groupId` was reserved as a null placeholder in lite L1 but unused.
- **Standard data model = adjacency list** (`parentId` per node) — one additive `.bmaplan` field, proto ignores it, cross-open parity holds. Alternatives (nested-children array, materialized-path, closure-table) are heavier or break the flat-array persistence.
- **Incumbents (Bluebeam / QGIS / FreeCAD / Photoshop):** folder/group layers are **organizational only**; visibility + lock inherit from parent; **none roll up area/measurement totals to the parent.** → roll-up is a BMA-specific addition (chosen here because lite already sums per-layer).
- **The novel tension is BMA-specific:** child must keep its own role/semanticTag (not inherit parent's) or area calc breaks → warranted DIVERGE.
- Library: hand-rolled nested `<ul>` walk fits lite's no-bundler world better than any tree-view lib (TreeJS viable backup if drag-drop wanted later).

---

## 3. DIVERGE + SCORE (delegated to `bma-inventor`)

| # | Approach | Axis | Total | Forbidden |
|---|---|---|---|---|
| B | Group entity separate from layers (folder → layers, 1 level) | representation | 26 | NO |
| C | Role-bucket auto-grouping (no persisted parent) | UX / do-less | 25 | NO |
| A | `parentId` adjacency list (true layer-in-layer tree) | data-model | 24 | NO |
| E | subTag virtual grouping | representation | 24 | NO |
| D | Materialized-path string | data-model | 22 | NO |

All 5 preserve the crux (semanticTag stays role-derived) and are forbidden-surface-safe. `bma-inventor` recommended **B** (cheapest, `groupId` socket pre-drilled), fallback **C**.

---

## 4. CHECKPOINT decision — RESHAPE → **Approach F (A+B Hybrid)** — GO

User reshaped: "ชอบ A แต่ให้มี Group เหมือน B." → A's true `parentId` nesting **plus** B's separate folder entity, in one unified tree. Two further design decisions taken at the checkpoint:

1. **Roll-up totals: YES.** Folders show a realtime Σ of all descendant layers' own areas (ded subtracts). Layers show their own area only (no double-count). roll-up is computed live, **never persisted** (raw-geometry contract — never cache m²).
2. **Layer↔page scope: GLOBAL** (same as current lite, not page-scoped). The tree is global per project; objects bind to pages via `PS[page].objects[].catId`; the same tree shows on every page. Keeps lite slim (roadmap explicitly defers page-scoped).

### Model F (what gets built)

| Aspect | Decision |
|---|---|
| Node kinds | `folder` (in `liteGroups`, no role, no objects) + `layer` (in `LAYERS`, has role, holds objects) |
| Nesting | `parentId` on both → arbitrary depth. folder→folder, folder→layer, layer→sublayer all allowed |
| Visibility / lock | inherit down the parentId chain (hide folder → whole branch hidden) |
| semanticTag | **always role-derived per layer** — folders/parentId invisible to calc (CRUX preserved) |
| Roll-up | folder shows Σ of descendant layer own-areas (signed), realtime, not persisted |
| Schema (`.bmaplan`) | additive: `parentId` on each `liteLayers` item + new `liteGroups` array (folders carry their own `parentId`, `order`, `name`, `color`) |
| proto cross-open | proto ignores `parentId` + `liteGroups` → opens flat → identical area values |
| Backward compat | missing `parentId` = null = root; missing `liteGroups` = no folders |
| Reorder | reparent action + ▲▼ within siblings (drag-drop = later enhancement) |
| Delete folder | children's `parentId` move up to folder's parent (or null) |
| Delete layer with objects | reassign objects to default role layer (existing L2c-3 behavior) + reparent its sublayers |
| Size | ~300 LOC → tree render extracted to new `lite/static/js/layer-tree.js` (ui-lite.html stays under 1200) |
| Forbidden surface touch | **NO** |

---

## 5. Proposed slices (built via `/bma-lite-dev`, one reviewable slice each)

Smallest-safe-slice-first, mirroring the L2a→L2c discipline:

- **LST-1 — model + parentId (invisible refactor).** Add `parentId` to layers + `FOLDERS`/`liteGroups` model + tree accessors (`childrenOf`, `effVisible`, `effLock`, `rollup`) in `layer-system.js`. No UI yet. parity test stays green; export/.bmaplan byte-identical (no folders created yet). Marker `LITE_TREE_MODEL_OK`.
- **LST-2 — persistence (touches `.bmaplan`).** Save/load `parentId` + `liteGroups` additively. **Re-run `/bma-check-forbidden` (schema) + verify proto cross-open parity.** Backward-compat: old files load all-root. Marker `LITE_TREE_PERSIST_OK`.
- **LST-3 — tree panel UI.** Extract render to `static/js/layer-tree.js`: nested render, expand/collapse, nest/un-nest, reparent, ▲▼, folder CRUD, **folder roll-up Σ display**. Wire into `buildPicker()`. Marker `LITE_TREE_UI_OK`.

Sequencing rule: LST-1 must be PASS before LST-2; LST-2 before LST-3 (UI needs the model + persistence).

### Acceptance (whole feature)
- Draw gfa + nest a ded sublayer under it → deduction still subtracts; `areaByTag` signature unchanged vs flat baseline.
- Hide a folder → entire branch hidden on canvas; unhide restores.
- Folder Σ updates live when a descendant object's geometry/scale changes.
- Save → reopen in lite: tree intact. Save → open in **proto**: flat, identical area values.
- `lite/tests/test_measure_parity.py` → `MEASURE_PARITY_OK` on every slice.
