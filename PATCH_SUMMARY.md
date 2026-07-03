# PATCH_SUMMARY.md — Latest Sprint

> Full patch history: [docs/archive/patch-history-2026-05-09.md](docs/archive/patch-history-2026-05-09.md) · [docs/archive/patch-history-2026-07-02.md](docs/archive/patch-history-2026-07-02.md) · [docs/archive/patch-history-2026-07-03.md](docs/archive/patch-history-2026-07-03.md)

---

# Latest: INV-20260703-layer-linkage (plan B complete) + UX-batch-1 + save-fix follow-up

Branch: main

Date: 2026-07-03

## Outcome: PASS — Layer↔measurement redesign plan B (one aggregation engine) shipped 100% across 7 commits: all 3 HIGH findings (H1 no-move-UI / H2 engine disagreement / H3 orphan catId) plus M4 and M6 closed; plus the CRASH-tier save-wipe fix now has its bug-archive follow-up recorded; plus a first batch of UX quick-wins (F-7/F-1/F-2/F-3 + cheatsheet truth pass). `d40b20b` (save-fix): `projectToGlobals(livePS)` resolves live content by identity; `LITE_SAVE_CLICKPATH_OK`. `34aefa3` (UX batch 1): F-7 modalOpen keydown guard, F-1 ⇧D Path hotkey wired, F-2 F-key/Focus fix, F-3 Page Manager menu entry, cheatsheet corrections; `test_ux_quickwins.py`. `edc89ae` (B0): NEW `lite/static/js/object-agg.js` — single tuple-stream aggregation engine `{pg, catId, role, floorKey, area, counting}`; I11 oracle `assertEnginesAgree`; `test_object_tuples.py` (`LITE_OBJECT_TUPLES_OK`). `6909486` (B1): report-vars + Summary per-floor gfa/ded/net on tuples via opt-in `{useLive:true}` (default path byte-identical); `test_b1_role_reroute.py`. `00ab9b9` (B2): layer-tree Σ + Review Section-3 rows reduce the same tuple stream; oracle proves `byFloorRole` partitions == `byRole` — the two-engine disagreement (H2) impossible by construction; root-unfiled layers (M6) now counted; `test_b2_single_engine.py`. `34594b7` (B3): `layer-system.js` `reassignObjectsOfLayer` on `removeLayer` + `sweepOrphanCatIds` load-time heal — orphaned catId silent-drop/crash (H3) closed; `test_b3_orphan_heal.py`. `750d2f6` (B4): NEW `lite/static/js/layer-move.js` (120 lines, DOM-injected) — move-object-to-layer via Properties select + context menu "ย้ายไปเลเยอร์ ▸"; CFSS instances retarget MASTER with confirm; H1 closed; `test_b4_move_layer.py`. Known flag: CFSS-master-only moves not undoable (pre-existing `_docSnap` gap, candidate follow-up). `3d3741e` (B5): report-vars.js operand dropdown groups Σ role-refs vs ▸ single-layer refs (two optgroups); display-only, persisted expr format unchanged; M4 closed; `test_b5_ref_badges.py`. Every commit verified independently pre-commit; latest verify (B5) plus a `t0` measure-parity sweep all green. No `proto/` E2E needed — zero `proto/` files touched (lite-only block; proto markers unaffected).

## Summary

Layer↔measurement redesign plan B ("one aggregation engine," the structural fix that won 25/30 at the `INV-20260703-layer-linkage` human GO checkpoint) shipped end-to-end across a staged B0→B5 rollout, bundled with a first UX quick-wins batch and the bug-archive follow-up bookkeeping for the same-day CRASH-tier save-wipe fix. **Save-fix follow-up (`d40b20b`, already fixed and recorded in the prior finalize):** Ctrl+S no longer wipes measurements — `projectToGlobals(livePS)` resolves live content by identity via `_initialIds`/`dupSrc`; guard `LITE_SAVE_CLICKPATH_OK`. **UX batch 1 (`34aefa3`):** F-7 `modalOpen()` keydown guard closes the hotkey-leak into Summary; F-1 dead ⇧D Path hotkey wired; F-2 F-key/Focus collision resolved; F-3 Page Manager gained a menu entry (was ⇧F12-only); cheatsheet corrected. Guard `test_ux_quickwins.py`. **B0 (`edc89ae`):** NEW `lite/static/js/object-agg.js` — the single tuple-stream aggregation engine: one generator emits `{pg, catId, role, floorKey, area, counting}` tuples for every measured object; NEW I11 invariant oracle `assertEnginesAgree` proves any two consumers reducing the same partition of the same tuple stream cannot disagree — making the H2 dual-engine-disagreement finding structurally impossible rather than patched case-by-case. Guard `test_object_tuples.py` (`LITE_OBJECT_TUPLES_OK`). **B1 (`6909486`):** `report-vars.js` + Summary per-floor `gfa`/`ded`/`net` rerouted onto the tuple engine behind an opt-in `{useLive:true}` flag — default path stays byte-identical. Guard `test_b1_role_reroute.py`. **B2 (`00ab9b9`):** layer-tree Σ totals and Review-panel Section-3 rows now reduce the SAME tuple stream as Summary; oracle check (c) proves `byFloorRole` partitions equal `byRole` partitions by construction — H2 closed for good; root-unfiled layers (M6) now counted where they previously silently dropped. Guard `test_b2_single_engine.py`. **B3 (`34594b7`):** `layer-system.js` gains `reassignObjectsOfLayer` on `removeLayer` plus a load-time `sweepOrphanCatIds` heal pass — closes H3 (deleted-category orphaned `catId` silently dropped objects from every total, crashed on one path). Guard `test_b3_orphan_heal.py`. **B4 (`750d2f6`):** NEW `lite/static/js/layer-move.js` (120 lines, DOM-injected — `ui-lite.html` itself untouched) — the move-object-to-layer UI closing H1: Properties-panel select + canvas context-menu "ย้ายไปเลเยอร์ ▸"; CFSS shared-shape instances retarget the MASTER with a confirm dialog. Guard `test_b4_move_layer.py`. Known flag carried forward: CFSS-master-only moves are not undoable (pre-existing `_docSnap` gap, candidate follow-up, not a new regression). **B5 (`3d3741e`):** report-vars.js operand dropdown now groups references into two optgroups — Σ role-refs vs ▸ single-layer refs — closing M4 (the two reference kinds were visually indistinguishable). Display-only; persisted expression format unchanged. **Tests:** every commit independently verified pre-commit (targeted suite + t0 measure-parity). Latest verify (B5): `test_b5_ref_badges` + `test_report_vars_ui` + `test_report_vars_rollup` + `test_b1_role_reroute` + `run_all_tests.py --tier t0` all green. No `proto/` E2E needed — zero `proto/` files touched this whole block.

## Files Changed

| File | Change |
|---|---|
| `lite/static/js/object-agg.js` | NEW (B0) — single tuple-stream aggregation engine `{pg, catId, role, floorKey, area, counting}` |
| `lite/static/js/report-vars.js` | (B1) per-floor gfa/ded/net on tuples via opt-in `{useLive:true}`; (B5) operand dropdown Σ/▸ optgroups |
| `lite/static/js/layer-tree.js` | (B2) Σ totals reduce the tuple stream |
| `lite/static/js/overview-setup.js` | (B2) Review-panel Section-3 rows reduce the tuple stream |
| `lite/static/js/layer-system.js` | (B3) `reassignObjectsOfLayer` on `removeLayer` + load-time `sweepOrphanCatIds` heal |
| `lite/static/js/layer-move.js` | NEW (B4, 120 lines) — move-object-to-layer via Properties select + context menu, CFSS master retarget with confirm |
| `lite/static/js/page-folder-layers.js`, `page-manager.js`, `page-manager-ui.js` | save-fix follow-up bookkeeping (piece 1, already shipped) |
| `lite/ui-lite.html` | UX batch 1 — F-7 modalOpen keydown guard, F-1 ⇧D Path hotkey, F-2 F-key/Focus fix, F-3 Page Manager menu entry, cheatsheet corrections |
| `lite/tests/test_save_clickpath.py`, `test_ux_quickwins.py`, `test_object_tuples.py`, `test_b1_role_reroute.py`, `test_b2_single_engine.py`, `test_b3_orphan_heal.py`, `test_b4_move_layer.py`, `test_b5_ref_badges.py` | all NEW (1 guard per piece) |
| `docs/status/PHASE_INDEX.md` | updated via the block's own commits — NOT touched by this docs-batching write per explicit instruction |

## Source Files NOT Touched (Forbidden Surfaces)

- `proto/server.py` — NOT TOUCHED (lite-only block; zero proto/ edits)
- `polyAreaM2`, `polyMetrics`, `polySelfIntersects` — UNCHANGED
- `pdfToC`, `cToPdf`, `RS`, scale math — UNCHANGED
- `buildSnapIndex`, `snap` engine — UNCHANGED
- `lite/static/js/measure-engine.js` drift-locked vendored math — UNCHANGED; `MEASURE_PARITY_OK` verified green at B4
- `.bmaplan` schema version stays 1; all changes this block are additive (tuple engine is a pure read-side reduction, not a new persisted shape)

## Tests Run

Every commit independently verified pre-commit with its own targeted suite plus a `t0` measure-parity sweep. Latest verify (B5):
```
python lite/tests/test_b5_ref_badges.py       PASS
python lite/tests/test_report_vars_ui.py      PASS
python lite/tests/test_report_vars_rollup.py  PASS
python lite/tests/test_b1_role_reroute.py     PASS
python lite/tests/run_all_tests.py --tier t0  PASS
```
No `proto/` E2E run this block. Zero `proto/` files touched across the whole block (lite-only) — proto's 22-marker full-E2E baseline is unaffected by construction; this is the standing no-test rationale for the proto side, not an omission.

## Phase 1 Scope Check

- ✅ `polyAreaM2` / `polyMetrics` / `polySelfIntersects` unchanged
- ✅ `pdfToC` / `cToPdf` / `RS` / scale math unchanged
- ✅ `proto/server.py` core endpoints unchanged (proto NOT TOUCHED — lite-only block)
- ✅ `.bmaplan` schema version stays 1; all new fields/files this block are additive
- ✅ No legal / OCR / AI / Rule Engine / FAR-OSR pass-fail
- ✅ No forbidden surface touched

---

# Previous: UX-REVIEW-20260703 + BUG-20260703-lite-save-wipes-data — CRASH fix (Ctrl+S wiped all data) + full UI/UX journey review + layer↔measurement invent checkpoint

Branch: main

Date: 2026-07-03

## Outcome: PASS — CRASH-tier bug found and fixed (Ctrl+S wrote an empty `.bmaplan` and destroyed the in-memory session), a full UI/UX journey + static review filed 9 FRICTION + 6 COSMETIC findings (+3 GOODs pinned), and a layer↔measurement redesign investigation reached its human GO checkpoint. **(1) Save-wipe CRASH fix (`d40b20b`):** root cause was `pageMgr`'s `PS_by_id` snapshots taken (empty) at upload time, never refreshed, then projected back over live `PS` at save — so Ctrl+S always wrote the upload-time empty state. Fixed via new `projectToGlobals(livePS)` resolving content from live `PS` by identity, plus the same latent wipe fixed on the Apply/merge path (commit-order bug, 2 sites in `page-manager-ui.js`). NEW guard `LITE_SAVE_CLICKPATH_OK` drives the REAL `mi-save` click (closing the click-path-vs-API-path gap that let 72 prior green tests miss this) — proven RED (exact journey repro) → GREEN. Regression 17/17. **(2) UX review filed (`UX-20260703-review-findings`, `2249400`):** 29-screenshot journey review on the real 45-page permit + static inventory → 9 FRICTION (dead hotkey, key collisions, undiscoverable Page Manager, invisible verified state, silent mouse-block, misleading messaging, missed-modal hotkey leakage, raw errors, native prompt() in Verify Scale) + 6 COSMETIC + 3 GOODs pinned. **(3) Layer↔measurement invent checkpoint (`INV-20260703-layer-linkage`, `2249400`):** investigation mapped 8 problems (3 HIGH); Approach B "one aggregation engine" (`object-agg.js` tuple stream) scored 25/30 and won over 4 alternatives; fallback D recorded; staged B0-B5 rollout GO'd. B0 + UX quick-wins batch 1 (F-7/F-1/F-2/F-3 + cheatsheet pass) are being built right now by two parallel `lite-builder` subagents — in-progress, not shipped as of this write. Lite suite regression green throughout (`MEASURE_PARITY_OK` intact). Zero `proto/` edits.

## Summary

Three pieces filed/shipped the same morning. **(1) CRASH fix — save wiped all data (`d40b20b`):** Ctrl+S wrote an empty `.bmaplan` and destroyed the in-memory session. Root cause: `pageMgr` seeded `PS_by_id` as `deepCopy` snapshots of `PS` taken at upload time (empty at that point); all drawing thereafter mutated live `PS` only; `mi-save` → `_pmCommit` then projected those stale empty snapshots back over `PS` immediately before `buildPageStore()` serialized it. 72 green tests missed this because every existing save test called `buildPageStore()` directly (the API path), never the real `mi-save` click path. Fix: new `projectToGlobals(livePS)` resolves each page id's CONTENT from live `PS` by identity — baseline via `_initialIds`, duplicates via a new `dupSrc` map (deep-copy of the SOURCE page's live content), merges stay blank; `_pmCommit` passes `PS` through this resolver; model snapshots refreshed post-commit. The same latent wipe existed on the Apply/merge path (`_pmuiApplyChanges` + merge, `page-manager-ui.js`, 2 sites) — commit order was backwards (flush-then-commit); reordered to commit-with-pre-flush-baseline-THEN-flush. NEW guard `lite/tests/test_save_clickpath.py` (`LITE_SAVE_CLICKPATH_OK`) drives the REAL `mi-save` click via `URL.createObjectURL` interception — closing the exact click-path-vs-API-path gap that let 72 tests miss this. Proven RED pre-fix (polys 0, calib null — exact journey repro) → GREEN; 4 checks incl. dup-content-follows-identity. Regression 17/17 (metamorphic, page-manager suite, apply-mutations, all persist suites, arc/CFSS parities, `MEASURE_PARITY_OK`). **(2) UX review complete (`UX-20260703-review-findings`, `2249400`):** journey review on the real 45-page permit (29 screenshots in `artifacts/ux-review-20260703/`) + static inventory. 9 FRICTION: F-1 dead ⇧D hotkey, F-2 `F`/Focus collision, F-3 Page Manager undiscoverable (⇧F12-only), F-4 scale-verified state invisible post-modal, F-5 wizard blocks mouse silently, F-6 misleading "เปิด PDF ก่อน" during background upload, F-7 `modalOpen()` misses `#sum`/`#vs-modal`/cheatsheet → typing fires tool hotkeys, F-8 raw error messages, F-9 Verify Scale uses `window.prompt()`. 6 COSMETIC (annotate no hotkeys; Thai/English flips; stale cheatsheet; empty-state clutter; transient scanned notice; no fallback badge). 3 GOODs pinned (setup wizard, local-first save status, live measure feedback). Findings-filing only — no app code changed by the review itself. **(3) Layer↔measurement invent at checkpoint (`INV-20260703-layer-linkage`, `2249400`):** investigation mapped the model + 8 problems (3 HIGH: no move-between-layers UI; Summary-widget vs Review-panel dual aggregation engines can disagree on net area; orphaned `catId` silently drops objects / crashes). `bma-inventor` scored 5 approaches; Approach B "one aggregation engine" won 25/30 (`object-agg.js` tuple-stream generator, every consumer becomes a pure reduction, per-floor net becomes native, fully additive); fallback D (simple `floorKey` field) recorded. Staged B0-B5 rollout plan written. GO received at the human checkpoint. B0 (tuple generator + new `I11` invariant oracle) and a first UX quick-wins batch (F-7 modal-detection fix, F-1/F-2/F-3 hotkey/discoverability, cheatsheet accuracy pass) are being built right now by two `lite-builder` subagents in parallel — recorded as in-progress, not shipped in this docs-write's commit range.

## Files Changed

| File | Change |
|---|---|
| `lite/static/js/page-manager.js` | (1) — NEW `projectToGlobals(livePS)` resolves page content from live `PS` by identity at commit time |
| `lite/static/js/page-manager-ui.js` | (1) — Apply/merge commit-order fix (2 call sites) |
| `lite/tests/test_save_clickpath.py` | NEW (1) — `LITE_SAVE_CLICKPATH_OK`, drives the real `mi-save` click, 4 checks |
| `lite/ui-lite.html` | (1) — +4/− minor wiring for the click-path guard |
| `docs/status/PHASE_INDEX.md` | (1)+(2)+(3) — bug filed + `fixed_commit`; UX review + invent-checkpoint bundle filed — via the block's own commits, not this docs-batching write |
| `lite/tests/bug-archive.jsonl` | (1) — `BUG-20260703-lite-save-wipes-data` fixed_commit recorded — via the block's own commit, not this docs-batching write |
| `artifacts/ux-review-20260703/` | NEW (2) — 29 journey screenshots backing the UX review findings |

## Source Files NOT Touched (Forbidden Surfaces)

- `proto/server.py` — NOT TOUCHED (lite-only block; zero proto/ edits)
- `polyAreaM2`, `polyMetrics`, `polySelfIntersects` — UNCHANGED
- `pdfToC`, `cToPdf`, `RS`, scale math — UNCHANGED
- `buildSnapIndex`, `snap` engine — UNCHANGED
- `lite/static/js/measure-engine.js` drift-locked vendored math — UNCHANGED
- `.bmaplan` schema version stays 1; save-fix changes commit-time resolution logic only, no new/renamed persisted fields
- Layer-linkage invent is HALTED at the human checkpoint per Pack H — B0/UX-quick-wins are a separate in-progress sprint, not part of this write's shipped commit range

## Tests Run

```
python lite/tests/test_save_clickpath.py   → LITE_SAVE_CLICKPATH_OK   PASS (NEW; RED pre-fix = exact journey repro; 4 checks)
```
Regression 17/17: metamorphic suite, page-manager suite, apply-mutations suite, all persist suites, arc-summary parity, CFSS-summary parity, `MEASURE_PARITY_OK` (drift-lock intact). UX review and invent checkpoint are findings/research work, no dedicated test marker, covered by the same regression run. B0 + UX quick-wins batch 1 are in-progress with two `lite-builder` subagents at time of write — not yet tested or shipped.

## Phase 1 Scope Check

- ✅ `polyAreaM2` / `polyMetrics` / `polySelfIntersects` unchanged
- ✅ `pdfToC` / `cToPdf` / `RS` / scale math unchanged
- ✅ `proto/server.py` core endpoints unchanged (proto NOT TOUCHED — lite-only block)
- ✅ `.bmaplan` schema version stays 1; no new/renamed fields
- ✅ No legal / OCR / AI / Rule Engine / FAR-OSR pass-fail
- ✅ No forbidden surface touched; layer-linkage invent correctly HALTED at the human checkpoint per Pack H

---

<!-- INV-20260703-layer-linkage (plan B complete) + UX-batch-1 + save-fix follow-up / UX-REVIEW-20260703 + BUG-20260703-lite-save-wipes-data are the 2 kept in this file -->
<!-- GO-20260703-invariants-streaming-worker-recycle archived to docs/archive/patch-history-2026-07-03.md on 2026-07-03 (INV-20260703-layer-linkage plan-B-complete sprint block) -->
<!-- BLOCK-20260703-clear-queue archived to docs/archive/patch-history-2026-07-03.md on 2026-07-03 (UX-REVIEW-20260703 + BUG-20260703-lite-save-wipes-data sprint block) -->
<!-- PERF-20260702-lite-foxit-smoothness archived to docs/archive/patch-history-2026-07-02.md on 2026-07-03 (GO-20260703-invariants-streaming-worker-recycle sprint block) -->
<!-- BUG-20260702-lite-pagerot-registration archived to docs/archive/patch-history-2026-07-02.md on 2026-07-03 (BLOCK-20260703-clear-queue session) -->
<!-- AUDIT-20260702-infra-bundle archived to docs/archive/patch-history-2026-07-02.md on 2026-07-02 (PERF-20260702-lite-foxit-smoothness sprint block) -->
<!-- BUG-20260702-lite-cfss-summary + BUG-20260702-lite-arc-summary (2026-07-02) + SLICE report-edit-1 (2026-06-05) + BUG-20260526-lite-stale-pf-folder-cleanup + Centerline Snap arc (2026-05-25) archived to docs/archive/patch-history-2026-07-02.md on 2026-07-02 (BUG-20260702-lite-pagerot-registration sprint) -->
<!-- SIM-2 (2026-05-24) and older entries archived to docs/archive/patch-history-2026-05-09.md -->
