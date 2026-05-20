# Invent — Layer Model Rebuild (single source of truth)

- **Idea**: รื้อ Layer model ใหม่ให้เหลือระบบเดียว แก้ปัญหา object ผังบริเวณลง layer ผิด + ซ้อนทับ
- **Status**: invent-done-go (→ INV-2026-05-20-002 / -003 / -004)
- **Started**: 2026-05-20
- **Run mode**: THIN (light research · 2-3 data-model diverge · focus on spike)
- **Short-name**: layer-model-rebuild
- **Sandbox**: `proto/sandbox/invent-layer-model.html`

## Frame

**Problem.** Site-plan objects land in the wrong layer and overlap on canvas. Root cause = an unfinished migration: BMA-Plan runs **two competing layer systems** — a page-scoped one (`pageStore[n].layers[]`, `object.layerSlug/layerId`, used by right panel + export grouping) and a legacy global one (`areaTypeLayer(areaType)` + `layerVis/layerLock`, used by canvas render + visibility). Render still reads the global one, so the page-scoped `layerId` is effectively cosmetic.

**Key finding (changes the picture).** This is NOT greenfield. The target model is already **specified AND partially built**:
- `docs/design/PAGE_SCOPED_LAYER_MODEL.md` (LOCKED 2026-05-10) — target spec
- `docs/design/LAYER_MODEL_ALIGNMENT_AUDIT.md` (2026-05-10) — gap list G1–G8 + a 6-sprint implementation sequence

**Current vs audit (verified in code 2026-05-20):**

| Gap | Audit sprint | State today |
|---|---|---|
| G2/G3 Layer data model + `pageStore[n].layers[]` | RUN_PAGE_LAYER_INSTANCE_MODEL | ✅ DONE (`ensurePageLayers`/`_makePageLayers` L897–919) |
| G6 Presets by pageType | RUN_PAGE_TYPE_LAYER_PRESETS | ✅ DONE (`DEFAULT_LAYER_PRESETS` L867–896) |
| G4/G5 `layerId`/`pageIndex` on objects | RUN_OBJECT_LAYER_VALIDATION | ◑ PARTIAL (`assignDefaultObjectLayer` sets them, but derives slug from `areaType`, not active layer / not semanticTag) |
| **G1 global `layerVis`/`layerLock`** | RUN_LAYER_SCOPE_AUDIT | ❌ NOT done (still global L865) |
| **G7 active layer writes `layerId`** | RUN_LAYER_TOOL_AWARENESS | ❌ NOT done (site tools bypass; `getObjectLayerSlug` reads `areaType`) |
| **render reads page-scoped layer** | (implicit tail) | ❌ NOT done (`redraw` L1905 uses `areaTypeLayer`+global `layerVis`) ← the visible bug |
| G8 cross-page total by floor | RUN_AREA_SUMMARY_BY_TAG_AND_FLOOR | separate concern (out of scope here) |

So the user's "rebuild" = **finish the last mile of an existing, spec'd migration** (G1 + G7 + render switch), with the user's 4 decisions layered on (manual layer dropdown, per-page-type presets [already done], drop backward-compat, single system).

**Constraints.** raster-PDF safe · Phase 1 boundary · page-scoped layers · no area-math change (`polyAreaM2`/`polyMetrics` untouched) · `pdfToC`/`cToPdf`/`RS`/snap untouched. No `.bmaplan` migration needed (user dropped backward-compat).

**Success criteria.** site object → correct layer per page-type · user reassigns layer via dropdown · hide/lock/solo per layer works independently · render no longer collapses 7 site tags into one bucket · only ONE layer system remains (global `areaTypeLayer`+`layerVis`/`layerLock` deleted).

**Out of scope.** G8 floor totals · area math · export schema redesign.

## Research

### Verdict: PRIOR_ART_MATURE

The incumbent CAD layer model (AutoCAD 40-yr standard, affirmed by Bluebeam Revu, Illustrator) is **"object holds `layerId`; layer object owns `{visible, locked, color, order}`; render iterates objects and looks up the layer."** Mature, battle-tested, orthogonal to semantic meaning (user owns layer assignment; `semanticTag`-derived metadata is separate — confirms decoupling layer from semanticTag is correct).

- **No viable inline-JS library** — Paper.js/Konva are bundler/animation-oriented; Fabric keeps layerId only in metadata (no Layer model). Single-file vanilla constraint ⇒ build in-house (same as `polyAreaM2`, snap).
- **Competitor UX**: Bluebeam auto-assigns new markup to the active Markup Layer + allows reassign; layer panel = visibility (eye) + lock (padlock). Foxit locks on creation. User's chosen "manual pick/move via dropdown" = Bluebeam-ish, more flexible than Foxit/QGIS.
- **In-repo**: `PAGE_SCOPED_LAYER_MODEL.md` + `LAYER_MODEL_ALIGNMENT_AUDIT.md` already adopt exactly this pattern with a phased sprint sequence. Spec is complete; remaining work is implementation, not invention.

Sources: Bluebeam Revu layers docs · AutoCAD ByLayer/ByEntity · QGIS visibility presets · Fabric.js v6 layer management.

## Diverge / Score / Spike

**SKIPPED — per invent rule "PRIOR_ART_MATURE → skip phases 3–6."**

No data-model alternatives worth diverging on: the standard `object.layerId → layer{visible,locked,color,order}` model is proven, already spec'd in-repo, and ~half-implemented in the live code. A sandbox spike would add little value because (a) the data model already exists and works in `proto/ui.html`, and (b) the real risk lives in migrating the live `redraw()`/visibility paths — which a standalone sandbox cannot de-risk meaningfully. The honest move is a normal dev sprint following the audit's remaining steps, not a spike.

## Recommendation

**Adopt prior art** — promote to a normal dev sprint (`/bma-dev-loop`-ready) that finishes the existing migration. Scope = G1 (de-globalize `layerVis`/`layerLock`) + G7 (active-layer dropdown writes `layerId`, incl. site tools) + render switch (`redraw` reads page-scoped layer, delete `areaTypeLayer` global path). Use `LAYER_MODEL_ALIGNMENT_AUDIT.md` as the scope doc. Likely SPLIT into 2–3 sub-sprints (data/scope · tool-awareness+reassign UI · render+delete-legacy) since it touches render + panel + save.

## Decision

**GO** (2026-05-20) — promote to dev sprints. Verdict `INVENT_DONE_PRIOR_ART`: adopt the standard CAD layer model already spec'd in `LAYER_MODEL_ALIGNMENT_AUDIT.md`; the work is finishing the unfinished migration (G1 + G7 + render switch), not invention. Split into 3 sequential sub-sprints in PHASE_INDEX (chained via depends-on):

- **INV-2026-05-20-002** (L1) — de-globalize `layerVis`/`layerLock` → per-page; fix `getObjectLayerSlug` so site objects stop collapsing to a non-existent "sub_area" slug. `INV_LAYER_L1_OK`.
- **INV-2026-05-20-003** (L2) — active-layer dropdown writes `layerId` (incl. site tools) + selected-object "move to layer" reassign UI. `INV_LAYER_L2_OK`. depends-on L1.
- **INV-2026-05-20-004** (L3) — `redraw()`/visibility read page-scoped layer; delete legacy `areaTypeLayer` global path + global `layerVis`/`layerLock`. `INV_LAYER_L3_OK` + `/bma-ui-regression`. depends-on L2.

No spike artifact (`proto/sandbox/invent-layer-model.html` not created — MATURE skip). `/bma-dev-loop` picks up L1 when its turn comes (after the higher-priority queued items / per depends-on).

**Status**: invent-done-go
