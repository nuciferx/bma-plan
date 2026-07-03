# FINAL_REPORT_FOR_CHATGPT.md — Sprint Outcome Report

> Full report history: [docs/archive/reports-2026-05-09.md](docs/archive/reports-2026-05-09.md) · [docs/archive/reports-2026-07-02.md](docs/archive/reports-2026-07-02.md) · [docs/archive/reports-2026-07-03.md](docs/archive/reports-2026-07-03.md)

---

# Latest: INV-20260703-layer-linkage (plan B complete) + UX-batch-1 + save-fix follow-up — PASS

**Date:** 2026-07-03
**Branch:** main

## Outcome

PASS. The layer↔measurement redesign that reached its human GO checkpoint earlier the same day (`INV-20260703-layer-linkage`, Approach B "one aggregation engine") shipped end-to-end across a staged B0→B5 rollout of 6 commits, plus a first UX quick-wins batch and the bug-archive follow-up bookkeeping for the same-day CRASH-tier save-wipe fix. **B0 (`edc89ae`):** NEW `lite/static/js/object-agg.js` — a single tuple-stream aggregation engine `{pg, catId, role, floorKey, area, counting}` plus a new I11 invariant oracle that proves any two consumers reducing the same partition cannot disagree, making the H2 "Summary vs. Review can disagree" finding structurally impossible rather than manually kept in sync. **B1-B2 (`6909486`, `00ab9b9`):** report-vars, Summary per-floor totals, layer-tree sums, and the Review-panel Section-3 rows all rerouted onto the same tuple stream — H2 closed for good, and M6 (root-unfiled layers silently uncounted) closed as a side effect. **B3 (`34594b7`):** `layer-system.js` self-heals orphaned `catId`s on both `removeLayer` and load, closing H3 (the crash-tier orphan bug). **B4 (`750d2f6`):** NEW `lite/static/js/layer-move.js` finally gives users a UI to move an object between layers — Properties select plus a context-menu entry, with CFSS shared-shape instances retargeting their master with a confirm — closing H1, the last of the 3 HIGH findings. **B5 (`3d3741e`):** a small clarity polish groups the report-vars operand dropdown into Σ-role vs. ▸-layer optgroups, closing M4. Bundled into the same session: **UX batch 1 (`34aefa3`)** — F-7 fixes the `modalOpen()` gap that let hotkeys leak into the Summary widget (the exact class of bug the UX review filed that same morning), F-1/F-2/F-3 fix a dead hotkey, a key collision, and Page Manager's discoverability, plus a cheatsheet accuracy pass; and the **save-fix bug-archive follow-up (`d40b20b`, already fixed and reported in the prior finalize)**, included here to close out the narrative arc. Every commit was independently verified pre-commit with its own guard test plus a `t0` measure-parity sweep; `MEASURE_PARITY_OK` confirmed green at B4. Zero `proto/` edits across the whole block.

## What was delivered

- `lite/static/js/object-agg.js` (NEW, B0) — single tuple-stream aggregation engine, closes H2 by construction via the I11 invariant oracle
- `lite/static/js/report-vars.js`, `layer-tree.js`, `overview-setup.js` (B1-B2) — Summary, per-floor totals, and Review-panel rows all reduce the same tuple stream
- `lite/static/js/layer-system.js` (B3) — `reassignObjectsOfLayer` + load-time `sweepOrphanCatIds`, closes H3
- `lite/static/js/layer-move.js` (NEW, 120 lines, B4) — move-object-to-layer UI, closes H1
- `lite/static/js/report-vars.js` operand dropdown Σ/▸ optgroups (B5) — closes M4
- `lite/ui-lite.html` (UX batch 1) — F-7 modal-detection fix, F-1/F-2/F-3 hotkey/discoverability fixes, cheatsheet corrections
- `lite/tests/test_save_clickpath.py`, `test_ux_quickwins.py`, `test_object_tuples.py`, `test_b1_role_reroute.py`, `test_b2_single_engine.py`, `test_b3_orphan_heal.py`, `test_b4_move_layer.py`, `test_b5_ref_badges.py` (all NEW)
- Shipped as commits `d40b20b` + `34aefa3` + `edc89ae` + `6909486` + `00ab9b9` + `34594b7` + `750d2f6` + `3d3741e` on `main`

## What's next

- **(1)** UX quick-wins batch 2 — F-4 (visible scale-verified badge), F-5/F-6 (wizard/upload messaging), F-9 (replace `window.prompt()` in Verify Scale), plus seeded-vars red-error display and a wizard Next-button gate. In progress at the time of this write.
- **(2)** B4 CFSS-undo follow-up — CFSS-master-only layer moves are not undoable (pre-existing `_docSnap` gap surfaced by the new UI, not a new regression). Candidate follow-up sprint.
- **(3)** Production RSS re-probe of worker-recycle on the CHH binder — carried over, still open.
- **(4)** Workflow-redesign proposal — awaiting user GO.
- **(5)** V2 U3/U4 migration — `SHIPS.jsonl` ledger (U3) and roadmap split+reconcile tooling (U4).

## Position in Plan

Phase 1 — BMA-Plan Lite epic. This block is the direct completion of the layer↔measurement redesign Pack H's `INV-20260703-layer-linkage` investigation scoped and scored earlier the same day: rather than patch 3 HIGH findings independently, the winning approach (a single shared aggregation engine) closes all 3 with one mechanism, one of them (H2, dual-engine disagreement) closed structurally rather than by careful manual synchronization. The staged B0→B5 commit sequence — engine first, consumers rerouted one at a time behind opt-in flags, crash-tier bug closed, UI finally shipped, then a small polish — kept every step independently testable. UX batch 1 was bundled in because its lead item (F-7) was a direct low-risk follow-up to the UX review filed the same morning. No forbidden surface touched; zero `proto/` edits.

---

# Previous: UX-REVIEW-20260703 + BUG-20260703-lite-save-wipes-data — PASS

**Date:** 2026-07-03
**Branch:** main

## Outcome

PASS. Three pieces filed/shipped the same morning. **(1) CRASH fix — save wiped all data (`d40b20b`):** Ctrl+S wrote an empty `.bmaplan` and destroyed the in-memory session — the most severe defect class this project tracks, total silent data loss on the single most-used action in the app. Root cause: `pageMgr` seeded `PS_by_id` as empty `deepCopy` snapshots taken at upload time, never refreshed, then projected back over live `PS` right before save serialized it. 72 previously-green tests missed this because every existing save test drove the API/serialization path directly, never the real `mi-save` click. Fixed via a new `projectToGlobals(livePS)` resolver plus the same latent wipe on the Apply/merge path (a backwards commit-order bug, 2 sites). NEW guard `LITE_SAVE_CLICKPATH_OK` drives the real click and closes the click-path-vs-API-path testing gap; RED pre-fix (exact journey repro) → GREEN; regression 17/17. **(2) UX review filed (`UX-20260703-review-findings`):** a full journey (29 screenshots on the real 45-page permit) + static-code review surfaced 9 FRICTION findings (dead hotkey, key collisions, an undiscoverable Page Manager, invisible post-verify scale state, a silently mouse-blocking wizard, misleading upload messaging, a modal-detection gap that leaks hotkeys into open dialogs, raw error text, and a native `window.prompt()` in Verify Scale) plus 6 COSMETIC findings, with 3 GOODs explicitly pinned so future work doesn't regress them. This is the review methodology validating itself in the same session — the CRASH it surfaced was fixed same-morning. **(3) Layer↔measurement invent reached its human checkpoint (`INV-20260703-layer-linkage`):** an investigation mapped 8 concrete problems in the current layer/measurement data model (3 rated HIGH, all tracing to two independently-maintained rollup engines that can silently disagree), scored 5 candidate redesigns, and staged a rollout plan around the winning "one aggregation engine" approach. GO was received; the first build increment and a batch of UX quick-win fixes are in progress right now via two parallel builder subagents, not yet shipped as of this report. Lite suite regression green throughout; `MEASURE_PARITY_OK` intact. Zero `proto/` edits.

## What was delivered

- `lite/static/js/page-manager.js` — NEW `projectToGlobals(livePS)`, resolves page content from live `PS` by identity at commit time
- `lite/static/js/page-manager-ui.js` — Apply/merge commit-order fix (2 sites), closing the same latent save-wipe on that path
- `lite/tests/test_save_clickpath.py` (NEW, 190 lines) — `LITE_SAVE_CLICKPATH_OK`, drives the real `mi-save` click via `URL.createObjectURL` interception
- `artifacts/ux-review-20260703/` (NEW) — 29 journey screenshots backing the filed UX findings
- `docs/status/PHASE_INDEX.md` — bug filed + fixed; UX review bundle + layer-linkage invent checkpoint filed
- Shipped as commits `d40b20b` + `912c3e2` + `2249400` on `main`

## What's next

- **(1)** Verify + commit the two in-flight builder sprints: B0 (tuple-stream aggregation engine + `I11` invariant oracle) and UX quick-wins batch 1 (F-7/F-1/F-2/F-3 + cheatsheet accuracy pass).
- **(2)** B1-B2 — reroute the existing summary/review/export consumers onto the new tuple-stream aggregation engine once B0 lands.
- **(3)** UX quick-wins batch 2 — F-4 (visible scale-verified badge), F-5/F-6 (wizard/upload messaging), F-9 (replace `window.prompt()` in Verify Scale), plus summary seeded-vars red-error display and a wizard Next-button gate.
- **(4)** Production RSS re-probe of worker-recycle on the CHH binder (carried over, still open).
- **(5)** V2 migration continuation — `SHIPS.jsonl` ledger (U3) and roadmap split+reconcile tooling (U4).

## Position in Plan

Phase 1 — BMA-Plan Lite epic. A CRASH-tier bug on the core save path was found and fixed the same morning a broader UI/UX health review was run — direct validation of why the review methodology exists. The layer↔measurement redesign is upstream R&D discipline (Pack H): rather than patching 8 symptom-level problems ad hoc, the investigation found and scored a structural root-cause fix before committing build time, and correctly halted at the human GO checkpoint rather than auto-promoting. No forbidden surface touched.

---

<!-- INV-20260703-layer-linkage (plan B complete) + UX-batch-1 + save-fix follow-up / UX-REVIEW-20260703 + BUG-20260703-lite-save-wipes-data are the 2 kept in this file -->
<!-- GO-20260703-invariants-streaming-worker-recycle archived to docs/archive/reports-2026-07-03.md on 2026-07-03 (INV-20260703-layer-linkage plan-B-complete sprint block) -->
<!-- BLOCK-20260703-clear-queue archived to docs/archive/reports-2026-07-03.md on 2026-07-03 (UX-REVIEW-20260703 + BUG-20260703-lite-save-wipes-data sprint block) -->
<!-- PERF-20260702-lite-foxit-smoothness archived to docs/archive/reports-2026-07-02.md on 2026-07-03 (GO-20260703-invariants-streaming-worker-recycle session) -->
<!-- BUG-20260702-lite-pagerot-registration archived to docs/archive/reports-2026-07-02.md on 2026-07-03 (BLOCK-20260703-clear-queue session) -->
<!-- AUDIT-20260702-infra-bundle archived to docs/archive/reports-2026-07-02.md on 2026-07-02 (PERF-20260702-lite-foxit-smoothness sprint block) -->
<!-- BUG-20260702-lite-cfss-summary + BUG-20260702-lite-arc-summary (2026-07-02) + SLICE report-edit-1 (2026-06-05) + BUG-20260526-lite-stale-pf-folder-cleanup + Centerline Snap arc (2026-05-25) archived to docs/archive/reports-2026-07-02.md on 2026-07-02 (BUG-20260702-lite-pagerot-registration sprint) -->
<!-- SIM-2 (2026-05-24) and older reports archived to docs/archive/reports-2026-05-09.md -->
