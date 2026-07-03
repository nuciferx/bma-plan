# INV-20260703-layer-floorkey — layer.floorKey draw-target linkage (lite)

Pack H invention record. Upstream of `/bma-dev-loop`. Status: **CHECKPOINT — awaiting human GO/NOGO/RESHAPE.**
Spike artifacts: `lite/sandbox/invent-layer-floorkey/{spike.js, mockup.html}`. Live app untouched.

---

## 1. Frame (P1–P5)

The problem: in lite, an object's **floor bucket is decided purely by the page tag** (`floorKeyOfPage(pg)` in `object-agg.js`). A layer has no say. This breaks whenever the drawing on a sheet does not belong 1:1 to that sheet's floor.

- **P1 — Mezzanine-on-lower-sheet.** A mezzanine / โถงลอย is frequently drafted on the floor-1 sheet. Today every m² drawn there lands in `floor:1`, silently inflating floor 1 and zeroing the mezzanine floor. No way to say "this layer is floor 2 even though it's on the floor-1 page."
- **P2 — Re-tag lands objects on the wrong floor.** Tag a page floor 1, draw, later re-tag it floor 2 → all its objects jump floors with no warning and no audit trail.
- **P3 — Two floors on one sheet.** A stacked/typical-floor sheet showing two levels cannot split its area across two floor buckets at all.
- **P4 — Draw-target is invisible.** The user cannot see, before drawing, which floor the next object will be counted on. The only signal is the page tag, which lives in a different panel.
- **P5 — CFSS must stay per-instance.** Cross-floor shared shapes (a lift core repeated on every floor) must keep counting on each *instance's* page-floor. Any floor-linkage feature must not regress that.

Design target: let a **layer** optionally pin a floor, additively, without breaking the page-tag default or CFSS.

---

## 2. Research verdict summary — **PRIOR_ART_PARTIAL**

- **AutoCAD / Bluebeam pattern.** Both bind semantics to a *layer/space*, not to the sheet the geometry sits on. AutoCAD layer names encode floor by convention (e.g. `A-FLOR-02`); Revit levels bind elements to a level independent of the view they're drawn in. Bluebeam's measurement "layers/columns" let one PDF page contribute rows to arbitrary groups. So "the container carries the floor, the page is only a default" is a mature, well-trodden idea — not novel.
- **In-repo prior work.** `object-agg.js` already centralises every rollup on a single tuple stream `{pg,catId,role,floorKey,area,counting,count}` with a parity oracle (`assertEnginesAgree`). `floorKey` is *already a first-class field on every tuple* — it is simply always sourced from the page. This is the single seam the whole feature needs.
- **Gap (why PARTIAL not MATURE).** No inline-JS library gives us this for free — it is a 3-line change to one derivation function plus a persistence field plus UI. The reconcile-on-conflict UX (pin vs page) is the only genuinely bespoke bit, and even that mirrors Revit's "level moved" prompt.

---

## 3. The 5 approaches + scores

| # | Approach | Axis | Novelty | Accuracy | UX | Model-fit | Boundary | Cost | **Σ** |
|---|----------|------|:--:|:--:|:--:|:--:|:--:|:--:|:--:|
| **A** | `layer.floorKey` additive override in `floorKeyOfObject` | data-model | 3 | 5 | 3 | 5 | 4 | 3 | **23** |
| **B** | Draw-target chip + edge tint + ◉ make-current + reconcile banner | UX | 4 | 4 | 5 | 4 | 5 | 4 | **26** |
| C | Per-object `floorKey` field (object-level, not layer) | data-model | 3 | 4 | 2 | 2 | 4 | 3 | 18 |
| **D** | Split sheet into N virtual floor-regions (rubber-band a page area → floor) | representation | 5 | 4 | 3 | 3 | 4 | 2 | **24** |
| E | Floor = folder membership (drag layer into PF_floor_N folder = its floor) | integration | 2 | 4 | 4 | 4 | 5 | 3 | 22 |

**Recommendation: bundle A + B (data-model + its UX), D as fallback.**
- A alone is invisible; B alone has nothing to bind to. Together they are the minimum coherent feature.
- C (per-object floorKey) loses the "one place to set it" ergonomics and bloats `.bmaplan`.
- E (folder = floor) conflates the page-folder tree (already a fragile system, see `page-folder-layers.js` pruning logic) with metric semantics — the CLAUDE.md rule "calculation never reads folder/layer *name*" makes floorKey-via-folder-membership a smell.
- **D** is the strongest fallback: it solves P3 (two floors on one sheet) *geometrically* rather than per-layer, which is more precise for a genuinely split drawing — but it is a heavier build (new region model + hit-testing) and scores lower on cost/model-fit.

---

## 4. Spike results — 4 proofs, all PASS (honest)

`node lite/sandbox/invent-layer-floorkey/spike.js`. The harness COPIES the derivation from `object-agg.js` / `layer-system.js` / `cross-floor-shapes.js` and swaps only the floorKey deriver:

```
floorKeyOfObject(o, pg):
  if instance and master.floorKey && master.floorKey !== "multi": return master.floorKey
  layer = layerOf(rollupCatId(o))
  if layer.floorKey && layer.floorKey !== "multi": return layer.floorKey   // additive override
  return floorKeyOfPage(pg)                                                 // page-tag fallback
```

| Proof | What it proves | Key numbers | Result |
|---|---|---|---|
| **1. Legacy parity** | No `layer.floorKey` anywhere → old vs new are byte/number-identical. 3 pages, 2 floors, default+custom layers, poly+ded+CFSS master/instances+count. | tuples 8==8; byFloor `floor:1=195.00/1  floor:2=230.00` identical; byRole `gfa=410 ded=15 count=/1`; grand total **425==425**; tupleStream/byRole/byFloor/byFloorRole all `equal:true`; oracle old.ok & new.ok. | **PASS** |
| **2. Re-tag follows layer** | Custom layer pinned `floor:1`; re-tag its page floor1→floor2 → pinned objects stay, default follows page, divergence detected, total unchanged. | before `floor:1=120.00`; after `floor:1=80.00  floor:2=40.00`; total **120==120**; divergence = exactly 1 row `{L1, layerFloorKey:floor:1, pageFloorKey:floor:2}`; oracle.ok. | **PASS** |
| **3. Two gfa layers, diff floors, same page** | Layer A `floor:1`, layer B `floor:2`, both on ONE page → distinct buckets, sum == byRole. | `floor:1.gfa=60.00  floor:2.gfa=90.00`; sum **150 == byRole.gfa 150**; single page confirmed; oracle.ok. | **PASS** |
| **4. CFSS master `floorKey:"multi"`** | Master multi + instances on 2 pages of different floors → per-floor totals follow the instance's page, identical to today. | `floor:1.gfa=25.00  floor:2.gfa=25.00`; identical to deriveOld = true; oracle old.ok & new.ok. | **PASS** |

Oracle used: the self-contained **(b)** total-partition (Σtuple == ΣbyRole == ΣbyFloor) and **(c)** floorRole-partition (Σ over floors of `byFloorRole` == `byRole` per role) checks from `assertEnginesAgree`. The **(a)** check (vs `computeSummary()`) has no Node equivalent, but (c) is the stronger structural guarantee here because `byFloorRole` is exactly what the new per-floor UI reads.

---

## 5. Migration notes

- **Field is additive.** `layer.floorKey` absent → `floorKeyOfObject` returns `floorKeyOfPage(pg)` = today. Proof 1 is the byte-identical guarantee. Old `.bmaplan` files load with no `floorKey` on any layer and produce the exact same numbers. Persist as an **optional** field on the layer entry (additive-only, per the `.bmaplan` schema rule).
- **`byRole` and grand totals are floorKey-invariant by construction** (they never read `floorKey`). So the override can only *redistribute* area across floors — it can never change a role total or the project total. This is the mathematical "no double-count" guarantee (proof 2 total 120==120, proof 3 sum==byRole).
- **CFSS unchanged.** A master with no `floorKey` (or `"multi"`) keeps per-instance-page behaviour (proof 4). A concrete `master.floorKey` would pin all instances — an opt-in escape hatch, off by default.
- **`"multi"` sentinel** is the explicit cross-floor marker; treat it identically to "absent" in the deriver so existing masters need no rewrite.

---

## 6. Surprising findings in `object-agg.js` that shape the design

1. **`floorKey` is already on every tuple** — only ever fed from the page. The feature is a one-seam change (`floorKeyOfObject` replaces the inline `floorKeyOfPage(pg)` call inside `objectTuples`), not a new engine.
2. **`byFloorRole` silently drops tuples with `floorKey===""`** (untagged/non-floor page) — but keeps `byRole`. Consequence for the new model: an object whose **layer** carries a floorKey while sitting on an **untagged** page (page → `""`) now *gains* a real bucket and **appears in `byFloorRole` where it previously vanished**. This is a net semantic gain (layer.floorKey rescues untagged-page objects into a floor), and it does **not** touch `byRole` or the grand total — but it means `byFloorRole` coverage can *increase* after adoption. Worth a one-line note in the sprint card.
3. **Excluded-page asymmetry is orthogonal.** `objectTuples` skips `excluded[]`; `computeSummary` does not (documented B0/B1 gap). The floorKey change does not interact with it — do not try to fix both in one sprint.
4. **Counting markers also carry floorKey** and land in `byFloorRole` under the `count` role. `layer.floorKey` therefore applies to count layers too — consistent, no special-case needed.

---

## 7. OPEN CHECKPOINT QUESTION (human decides)

> The spike proves Approach **A** (`layer.floorKey ?? page`) is a safe, additive, parity-preserving one-seam change, and mockup **B** shows the draw-target chip + edge tint + ◉ make-current + reconcile banner that makes it usable. All 4 proofs pass; `byRole`/totals are provably invariant.
>
> **Choose one:**
> - **GO A+B** — write the sprint card: persist `layer.floorKey` (additive), reroute `objectTuples` through `floorKeyOfObject`, add the chip/tint/make-current UI + reconcile banner sourced from `detectDivergence()`. *(recommended — Σ 23+26, minimum coherent feature)*
> - **GO B-only** — ship the draw-target chip + edge tint as pure UX now (no data-model change, chip just displays `floorKeyOfPage`), defer the pin/override. Lower risk, solves P4 only, leaves P1–P3 open.
> - **RESHAPE to D** — if the real need is *two floors on one physical sheet* precisely, prefer the virtual floor-region approach (rubber-band a page area → floor). Heavier build; revisit research on region hit-testing first.
> - **NOGO** — page-tag-only floor assignment is acceptable; close the idea.
