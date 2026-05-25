# Invent — Cross-floor shared shape (lift / pipe / stair shaft)

- **Started**: 2026-05-25 (post-LOVS-3 ship)
- **Idea source**: user 2026-05-25 — "แตกประเด็น จาก ช่องว่างในแต่ละชั้น เช่น ช่องท่อ ช่องลิฟ ปรกติ จะ เหมือนกันเกือบทุกชั้น ทำอย่างไรให้ไม่ต้องเขียนใหม่ในทุกๆหน้า ถ้ากรณี สเกล ไม่ตรงกันในแต่ละหน้าลองคิด"
- **IDEAS.md**: 2026-05-25 entry (status: `invent-in-progress`)
- **PHASE_INDEX**: Discovered backlog ideas 2026-05-25
- **Scope**: lite (NOT proto)
- **Short-name**: `cross-floor-shared-shape`

## Pre-frame (raw idea)

User's setup question: typical building has lift shaft / pipe shaft / stair shaft that occupy IDENTICAL positions on every floor (1, 2, 3, …, roof). In current lite workflow user must:
1. Draw the same lift polygon on floor 1 page
2. Switch to floor 2 page
3. Re-draw the SAME polygon (manual click → click → click)
4. Repeat 5+ times

If user later realizes "actually lift is 2.5m × 1.8m not 2.4m × 1.8m" → edit each floor manually.

Extra twist user identified: per-page scale can differ (floor 1 plan at 1:100, floor 2 at 1:150) — even if user could copy-paste, the raw pt coordinates wouldn't represent the same metric shape on a different-scale page.

## Frame

### Problem
For a typical mid-rise building (3-10 floors), elements like ลิฟต์ (lift shaft), ช่องท่อ (pipe shaft), บันได (stair shaft) occupy IDENTICAL footprint on EVERY floor plan. In lite today, user must redraw the same polygon N times (1 per floor page). Worse: when scale differs per page (floor 1 plan at 1:100, floor 2 at 1:150), copy-paste of PDF-point coordinates produces wrong-sized shape on the destination page.

### User pain (today)
- Draw lift on floor 1 → switch to floor 2 → redraw → switch to floor 3 → redraw → … (5-6× repetition for 5-story building)
- Realize lift is 2.5m not 2.4m → must edit each floor manually (forgets one = silent bug in GFA deduction)
- Different-scale floor pages → cannot copy-paste coordinates

### Constraints (must hold)
- **lite scope only** — proto untouched
- **`measure-engine.js` byte-identical to proto** (vendored, forbidden surface)
- **`.bmaplan` schema additive only** — old files must load + proto cross-open safe
- **`RS`, `pdfToC`/`cToPdf`, `polyAreaM2`, `polyMetrics`, `snap`** — forbidden surfaces
- **Raw-geometry contract preserved** — metric values always re-derived from current page scale, never cached as m or m²
- **Per-page scale** — different `pts_per_m` per page must work; shape's metric size stays constant
- **Page-scoped UI not assumed** — lite layers are global; new mechanism must work whether LPFL mode is on or off
- **No external library** (lite is bloat-conscious)

### Forbidden surfaces this idea must avoid
- `lite/static/js/measure-engine.js` (vendored math)
- `RS`, `pdfToC`, `cToPdf`, `polyAreaM2`, `polyMetrics`, `polySelfIntersects`, `snap` internals
- `.bmaplan` field rename/remove
- `semanticTag` resolution rules

### Success criteria (spike must demonstrate)
1. **Cross-scale correctness** — master shape defined as 2.5m × 1.8m on a page at `pts_per_m=10` (visual size 25pt × 18pt). Place instance on second page with `pts_per_m=15` → instance renders 37.5pt × 27pt, but `polyAreaM2` of the instance still returns **4.50 m²** (= 2.5 × 1.8) regardless of which page.
2. **Master-edit propagation** — change master from 2.5×1.8 to 2.7×1.9 → all instances on all pages immediately reflect new size (re-render correct pt geometry per page scale)
3. **N-instance placement** — "place master on floors [2,3,4,5,roof]" creates 5 instances, each at the same offset relative to that page's origin (or user-specified per-page offset)
4. **Orphan safety** — delete master → instances either (a) freeze as standalone polys (no longer linked) or (b) deleted with confirm. No silent data loss.
5. **Save/load round-trip** — instances persist in `.bmaplan` as additive field, reload restores master + instance links

### Out of scope (this invention pass)
- Rotation / mirror of instances (translate-only for v1; rotation = follow-on if needed)
- Cross-PROJECT master (different .bmaplan files) — only within one project
- Master library / palette UI (could add later; v1 = ad-hoc "promote this polygon to master")
- Auto-place-on-all-floors with smart anchor detection (user picks floors manually)
- Symbol library import (DXF block import, etc.)

### Open design questions (for diverge)
- **How does user PROMOTE a regular polygon to master?** (right-click → "make cross-floor shared"? toolbar button? auto when on PF_floor_1?)
- **Where does instance live in data model?** (`PS[pg].objects[]` with `{kind:'instance', masterId, offset}` ? separate `INSTANCES[]` array?)
- **How does master live in data model?** (one of `PS[pg].objects[]` flagged as `isMaster:true` ? separate `MASTERS[]` array? part of LAYERS?)
- **Offset semantics** — relative to page origin? relative to a reference point user picks?
- **Master-on-page** — does master itself render as an instance on its source page, OR is master purely metadata + first instance is the source-page placement?
- **LPFL integration** — when LPFL mode is on + user picks floors via PF_floor_* folder picker, does that drive placement? Or independent UX?

## Research (bma-researcher, verdict: PRIOR_ART_PARTIAL)

### 1. In-repo prior art
- `docs/design/LITE_LAYER_ROADMAP.md` **LPFL-1** (just shipped 2026-05-25) — establishes `PS[n].scale.pts_per_m` per-page + page-scoped folder grouping. Foundation ready.
- `lite/static/js/measure-engine.js:40-46` — vendored from proto, byte-identical. `polyAreaM2(pts)` calls `scale.pts_per_m` per page; `arcSegmentAreaM2(...)` renders radius/chord as metric via page scale. **Re-derivation on every read** already enforced (raw-geometry contract).
- `lite/ui-lite.html:242,250,815` — `PS[n] = {objects:[], scale:{pts_per_m}|null, annotations:[]}`. Objects stored as raw `{x,y}` in PDF points. Scale per-page nullable (raster fallback). No inhibitor to per-page instance rendering.
- `docs/design/PAGE_SCOPED_LAYER_MODEL.md`, `docs/invent/layer-model-rebuild.md` — proto finished page-scoped layer rebuild; pattern works cross-page.

### 2. Library scan (inline-friendly, no bundler)
| lib | claim | lite-fit | note |
|---|---|---|---|
| native SVG `<use>/<symbol>` | symbol + instance native | ⭐ but canvas mismatch | lite uses Canvas — would need parallel SVG tree |
| paper.js | full vector, .clone(), groups | ❌ wrong-shape, 400KB, canvas-incompatible w/ lite geom |
| fabric.js | canvas objects, .clone() | ❌ 600KB, schema rewrite |
| D3-shape | SVG path generator | ❌ rendering-only |
| **vanilla `Map<masterId,master> + instance[]`** | roll-your-own | ⭐⭐ recommended ~100 LOC, fits lite arch |

**Recommendation: roll-your-own** (lite is bloat-conscious).

### 3. CAD/GIS prior art
- **AutoCAD Block/BlockReference** — definition stored once in BLOCK_RECORD; BlockReference instances with insertionPoint + scale. **Master edit → all instances update.** ✅ Directly analogous
- **Revit Family/Instance** — master family + type/instance parameters, reference planes, parametric constraints drive geometry. ✅ Parametric approach for scale variance
- **Bluebeam Revu Tool Chest** — drag tool → places **fresh copy** (cold). ❌ No live link
- **Foxit PhantomPDF Stamps** — "Place on Multiple Pages" → independent copies. ❌ No retroactive update
- **QGIS Symbol Library** — symbols saved in .qml; placed features independent. ❌ No live update
- **ArcGIS Feature Templates** — defaults at creation only. ❌ No live link

**Gold standard = AutoCAD/Revit** (definition + instance reference with per-instance transform). Bluebeam/Foxit/QGIS all use cold copy-template.

### 4. Literature / standards
- **Master-slave / Template pattern** — software design, applied in CAD since AutoCAD 1988
- **Parametric Geometry in CAD Modeling** (Liu 2016) — geometry stored as constraints+parameters; scale invariance via metric storage + render-time scale application
- **SVG `<symbol>/<use>` + viewBox** (W3C 2022) — standard symbolic reuse with per-instance scaling
- **Figma Components & Instances** — main + unlimited instances; per-instance overrides break link on that property only

Key principle: store geometry in metric units, apply render scale dynamically.

### 5. Competitor UX
- **Bluebeam Revu** Tool Chest → fresh copy, no master/instance link
- **Foxit** stamps → batch place, no retroactive update
- **PlanGrid** annotations → cross-reference but independent
- **No raster-PDF tool ships live cross-page shape master/instance.** All use cold template-copy.

### Verdict: **PRIOR_ART_PARTIAL**

- Math solved (AutoCAD/Revit + lite's `getScaleForPage` already does metric storage)
- Data model proven (AutoCAD block + instance, 35 years old)
- **UX genuinely new in raster-PDF measurement space** — diverge on UX + placement algorithm + render integration
- No external library needed (~100 LOC roll-your-own)

## Diverge (bma-inventor)

### Approach A — Metric-master in MASTERS[] global  *(data-model axis)*
**Idea:** Top-level `MASTERS = {}` map keyed by UUID, alongside `PS[]`. Master stores geometry in **metric units (m)**. Instances in `PS[pg].objects[]` hold `{kind:'instance', masterId, offsetPt}`. On `draw()`, each instance resolves master, converts metric→pt via current page `pts_per_m`. polyAreaM2 receives resolved pts → unchanged.
**Pros:** No sync state machine; cross-scale math correct by construction; forbidden surface untouched.
**Cons:** Master editor needs separate canvas / numeric input UI.

### Approach B — Parametric template  *(representation axis)*
**Idea:** Master = `{width_m, height_m, unitPts:[{u,v}]}` (u,v ∈ [0,1]). Area computed by formula, not stored points.
**Pros:** Rotation easy. Clean for rect shafts. Native metric export.
**Cons:** Normalizing arbitrary irregular poly to unit-poly is fiddly.

### Approach C — Eager-copy + sync badge  *(sync-algorithm axis)*
**Idea:** No MASTERS global. Stamp `sharedId` UUID on polygon → walk other pages and copy full pt-array (scaled to target page). Edit master → manual "Sync now" walks all `{sharedId}` objects and overwrites. Blue badge=synced, red=stale.
**Pros:** Instance IS a plain polygon → existing draw/area/snap/export work with **zero changes**. Lowest impl risk.
**Cons:** Stale window between master edit and sync. N copies of pts.

### Approach D — LPFL-anchored auto-mirror  *(integration axis)*
**Idea:** Extends LPFL. Draw on `PF_floor_1` → prompt "Mirror to other floors?" → auto-place on selected `PF_floor_*` pages. Uses A's MASTERS underneath.
**Pros:** Deeply tied to floor taxonomy LPFL already knows. Auto-place on new floors.
**Cons:** Requires LPFL mode ON. Two subsystems coupled = fragility risk.

### Approach E — Shared-shape as a dedicated layer type  *(UX axis)*
**Idea:** Special `LAYERS[i] = {kind:'shared-template', metricObjects:[...]}`. Template objects ghost-render on every page; click to stamp.
**Pros:** Discoverability via existing layer panel.
**Cons:** Touching LAYERS type system risks breaking layer-system.js hide/lock/delete. Highest UI cost.

## Score

| approach | novelty | accuracy | UX | model-fit | boundary | cost | TOTAL | forbidden? |
|---|---|---|---|---|---|---|---|---|
| **A** metric-master global | 4 | 5 | 3 | 4 | 5 | 4 | **25** | NO |
| **B** parametric template | 4 | 5 | 3 | 3 | 5 | 3 | 23 | NO |
| **C** eager-copy + sync badge | 3 | 3 | 4 | 5 | 5 | 5 | **25** | NO |
| **D** LPFL-anchored mirror | 5 | 5 | 4 | 3 | 5 | 2 | 24 | NO |
| **E** template layer type | 4 | 5 | 4 | 2 | 5 | 2 | 22 | NO |

Tie at 25 between A (always-correct math) and C (zero existing-code-path changes) — real architectural trade-off.

## Recommendation

**Top: Approach A — Metric-master in `MASTERS[]` global (25/30)**
- Accuracy by construction — instances always recomputed from metric via current page scale (raw-geometry contract)
- `MASTERS{}` new global = clean + additive `.bmaplan` key
- ~120 LOC, single sprint: CRUD + instance resolver + wizard + save/load
- Math correctness is the differentiating factor over C (which has stale window)

**Fallback: Approach C — eager-copy + sync badge (25/30)**
- If A's master-editor UX proves too hard to build cleanly, fall back to C
- Instances are plain polygons → zero risk to draw/area/export
- Auto-trigger sync on master-close = closes stale window (accuracy effectively 5)

**Override notes:** No forbidden:YES approach ranked. All 5 spike-safe.

## Spike — Approach A (metric-master in MASTERS[] global)

**Sandbox:** `lite/sandbox/invent-cross-floor-shared-shape.html` (standalone, file:// run)

### Spike architecture
- `MASTERS = {[id]: {id, name, metricPts:[{x_m,y_m}], color}}` — global, metric-storage
- `PS[pg].objects[]` accepts new shape `{kind:'instance', masterId, offsetPt:{x,y}}` (additive)
- `resolveInstancePts(instance, pg)` — converts `master.metricPts × PS[pg].scale.pts_per_m + offset` → resolved pt array
- `objectAreaM2(obj, pg)` — dispatches by `kind`: instance → resolve + polyAreaPt2 / ppm² · poly → existing path
- Pull-on-draw (no cache, no sync state) — every `render()` re-resolves instances from current master + current page scale
- Orphan safety: delete master → walk all instances, freeze each as `kind:'poly'` with snapshot pts + `orphan:true` flag

### Acceptance results (5/5 PASS, verified by Playwright probe)

| # | Check | Result | Detail |
|---|---|---|---|
| C1 | Cross-scale correctness | ✅ PASS | 1 master 2.5×1.8 placed on 5 pages with `pts_per_m = {10, 15, 8, 12, 10}` → `objectAreaM2` returns **4.50 m² on every page** |
| C2 | Master-edit propagation | ✅ PASS | Edited master 2.5×1.8 → 2.7×1.9 → all 5 pages immediately show **5.13 m²** (no manual sync) |
| C3 | N-instance placement | ✅ PASS | "Place on all pages" creates 5 instances at one click |
| C4 | Orphan safety | ✅ PASS | Delete master → instances become `kind:'poly'` with `orphan:true` (red dashed render, polygon math still works, area frozen to last resolved value) |
| C5 | Save/load round-trip | ✅ PASS | Serialize `{masters, nextMasterIdN, PS}` → JSON → clear → reload → all 5 instance areas preserved bit-for-bit |

Zero JS errors. Spike screenshot: `artifacts/screenshots/cfss-04-after-edit.png` (1 master 2.7×1.9 = 5.13 m², 5 instances).

### Key technical findings
- **Pull-on-draw is architecturally clean** — eliminates sync state machine entirely. Master edit "propagates" because there's nothing to propagate; instances ARE the master at render-time.
- **`.bmaplan` impact is minimal** — new top-level key `masters: {}` (additive); `PS[pg].objects[]` accepts new `kind:'instance'` (additive). Old files load with empty MASTERS → no instances → behaves identically to today.
- **Math correctness mechanism**: `metricPts × ppm = pt`, then `polyAreaPt2 / ppm²` = m². Both factors of ppm cancel — area is determined ONLY by master's metric geometry, NEVER by the page it's drawn on. This is the core proof.
- **No external library needed** — full spike = ~330 LOC HTML+JS (single file).
- **LPFL integration is OPT-IN** (per Approach A scoring) — works without LPFL mode; works WITH LPFL via "place on all PF_floor_* pages" wizard variant (out of scope for spike, easy follow-on).

### Open production concerns (not blocking GO decision)
1. **Master editor UX**: spike uses simple numeric W×H inputs. Production may want a richer editor: click-to-draw rectangle in a dedicated "master canvas" panel, or right-click polygon → "promote to master" using its current bounding box → user adjusts metric dimensions. Decision deferred to sprint design.
2. **Where to place new instances**: spike places at fixed `{x:200, y:200}` per page (canvas center). Production needs UX: (a) auto-place at same offset as source-page placement, or (b) ghost-cursor preview + click to place per page.
3. **Master selection from existing polygon**: spike has user enter W×H manually. Production: "promote polygon" should compute W×H from polygon's bounding box (or polyAreaM2 if irregular).
4. **Folder/role for master**: should master live in a layer? Spike doesn't bind. Production: probably attach a `catId` to master (matches lite's role-derived semanticTag pipeline).
5. **Schema serialization**: spike persists everything in `serialize()`. Production: `.bmaplan` save/load adds `doc.masters = {}` + `kind:'instance'` round-trip via existing object loop in `loadProto()`.

### Approach C (fallback) — NOT spiked
Fallback was approach C (eager-copy + sync badge). Not needed — Approach A spike passed all 5 criteria cleanly. C remains documented as alternative if A's master-editor UX proves blocker at sprint time.

## Decision — **GO** (user 2026-05-25)

User decided GO at checkpoint after seeing 5/5 spike PASS + Playwright probe confirmation.

**Sprint card filed:** `INV-2026-05-25-CFSS` in `docs/status/PHASE_INDEX.md` active queue (status `queued`). Next `/bma-lite-dev` invocation can pick it up.

**Scope decision:** single sprint (~120 LOC + schema additive + UI). Not split — model + persist + UI form a single cohesive surface area smaller than LPFL-1 (which was 3 slices). Approach A spike covers all data-model + render logic; the sprint adds UI promotion flow + save/load wiring on top.

**Recommended worker:** `lite-builder` (sonnet) via `/bma-lite-dev`. Opus orchestrates spec + review.

**Pre-build checklist** (for the sprint):
1. `/bma-check-forbidden` on `.bmaplan` schema additive (`masters` new top-level key + `kind:'instance'` new object shape) — expected verdict 🟢 OK with WARN-additive
2. Read spike `lite/sandbox/invent-cross-floor-shared-shape.html` end-to-end for behavior contract
3. Decide master-editor UX during spec phase — options: (a) numeric W×H modal, (b) right-click "promote polygon" using bounding box, (c) draw-on-master-canvas. Recommend (b) for v1 — simplest, lowest UX risk, builds on existing polygon-draw flow
4. Cap watch: `ui-lite.html` at 1200/1200 — UI wiring MUST land in new `lite/static/js/cross-floor-shapes.js` (or via DOM injection from `page-folder-layers.js` bootstrap, same pattern as LOVS-1)
