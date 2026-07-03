# PATCH_SUMMARY.md — Latest Sprint

> Full patch history: [docs/archive/patch-history-2026-05-09.md](docs/archive/patch-history-2026-05-09.md) · [docs/archive/patch-history-2026-07-02.md](docs/archive/patch-history-2026-07-02.md) · [docs/archive/patch-history-2026-07-03.md](docs/archive/patch-history-2026-07-03.md)

---

<!-- GEN:START gen_status_docs -->

# Latest: AUDIT-20260703-lfoc-order-b-verify

Date: 2026-07-03 · Area: layer / folders (lite)

LFOC-ORDER-B build audit: feature found fully landed (kind-aware PF folder ids + rank + seeds + Thai labels + 11-check guard already in tree); floorKey exact-inverse parity proven for 7 kind/tag pairs; zero code change - stale invent-done-go card closed.

**Commits:** —

**Files touched:** —

**Closes:** INV-2026-05-26-LFOC-ORDER-B

---

# Previous: TEST-20260526-wiz-followup-guard

Date: 2026-07-03 · Area: wizard / test (lite)

BUG-20260526-lite-wizard-followup: both fixes found already landed (dblclick lock gate; buildPicker after reseed) - added the missing guard test BUG_20260526_LITE_WIZ_FOLLOWUP_OK 4/4, RED-proven by temporary revert; card moved to done.

**Commits:**
- `71ba5be` — test(lite): guard for BUG-20260526-lite-wizard-followup — fixes already landed, marker was missing
- `2000a9a` — docs: BUG-20260526-lite-wizard-followup done -> ROADMAP_DONE (reconcile clean)

**Files touched:** `docs/status/PHASE_INDEX.md`, `docs/status/ROADMAP_DONE.md`, `lite/tests/test_wiz_followup.py`

**Closes:** BUG-20260526-lite-wizard-followup

---

# FIX-20260703-undo-layers-folders

Date: 2026-07-03 · Area: layer / undo (lite)

Undo/redo covers LAYERS+FOLDERS: additive _docSnap keys + in-place splice restore (CATS alias preserved); pushUndo at all UI entry points, seeding/load undo-silent; reconcile banner [ตามหน้า] now round-trips under Ctrl+Z. RED-proven.

**Commits:**
- `085ab60` — fix(lite): undo/redo now covers LAYERS + FOLDERS (layer-redesign follow-up)

**Files touched:** `lite/static/js/layer-dnd.js`, `lite/static/js/layer-panel.js`, `lite/static/js/layer-system.js`, `lite/static/js/layer-target-ui.js`, `lite/static/js/layer-tree.js`, `lite/tests/test_undo_layers.py`, `lite/ui-lite.html`

**Closes:** layer-redesign-followup-a, b4-undo-flag

---

# INV-20260703-layer-redesign

Date: 2026-07-03 · Area: layer / model + ux (lite)

Layer redesign A+B (user GO at invent checkpoint, spike 4/4): A-model layer.floorKey one-seam swap in objectTuples (precedence master->layer->page, additive persistence, old saves byte-identical) + B-ui layer-target-ui.js (draw-target chip, canvas tint, make-current marker, reconcile banner).

**Commits:**
- `76ee98c` — docs(invent): file INV-20260703-layer-redesign — research+diverge done, A+B recommended, spike next
- `f54bac3` — docs(invent): INV-20260703-layer-redesign spike PASS 4/4 — layer.floorKey one-seam swap proven safe
- `92174b6` — feat(lite): A-model — layer.floorKey one-seam swap in objectTuples (INV-20260703-layer-redesign)
- `20129af` — feat(lite): B-ui — draw-target chip + canvas tint + make-current marker + reconcile banner (INV-20260703-layer-redesign)

**Files touched:** `docs/invent/lite-layer-floorkey.md`, `docs/status/PHASE_INDEX.md`, `lite/sandbox/invent-layer-floorkey/mockup.html`, `lite/sandbox/invent-layer-floorkey/spike.js`, `lite/static/js/layer-target-ui.js`, `lite/static/js/object-agg.js`, `lite/static/js/page-folder-layers.js`, `lite/tests/test_layer_floorkey.py`, `lite/tests/test_layer_target_ui.py`, `lite/ui-lite.html`

**Closes:** P1-layer-floor-mismatch, P2-wrong-layer-draws, P3-role-layer-ambiguity

**Docs:** docs/invent/lite-layer-floorkey.md

---

# UX-20260703-quickwins-batch3

Date: 2026-07-03 · Area: ui (lite)

UX batch 3: F-8 (11 error messages gain Thai next-step) + annotate Shift-hotkeys x7 via guarded central keydown + Thai PM/wizard strings + NEW empty-state.js pre-open overlay + NEW page-scan-badge.js per-page scanned/fallback badge.

**Commits:**
- `fcf5b23` — feat(lite): UX batch 3 — F-8 actionable errors + annotate hotkeys + Thai PM/wizard + empty state + scanned badge (UX-20260703)

**Files touched:** `lite/static/js/cheatsheet.js`, `lite/static/js/empty-state.js`, `lite/static/js/export-annotate.js`, `lite/static/js/overview-setup.js`, `lite/static/js/page-manager-ui.js`, `lite/static/js/page-renderer.js`, `lite/static/js/page-scan-badge.js`, `lite/tests/test_ux_batch3.py`, `lite/ui-lite.html`

**Closes:** UX-F8, UX-COSMETIC-1-4

---

# PROC-20260703-probe-dblclick-rewrite

Date: 2026-07-03 · Area: test-infra (simulate)

LITE-BUG-DBLCLICK-OVER-POP probe rewritten mouse_sequence -> evaluate-only (modal/wizard-proof): injects state.draft [4 pts + 2 strays], synthetic dblclick on #cv, asserts 4-pt commit; validated live incl. old-bug emulation discriminating 3-pt.

**Commits:**
- `707ed8f` — chore(test-infra): LITE-BUG-DBLCLICK-OVER-POP probe rewritten mouse_sequence -> evaluate-only

**Files touched:** `.claude/skills/bma-simulate/regression_probes.json`

**Closes:** NEXT_ACTIONS-item-11

---

# PROC-20260703-v2-u6-changelog

Date: 2026-07-03 · Area: process / release-tooling

V2 U6 automated half: scripts/gen_changelog.py (SHIPS.jsonl -> docs/CHANGELOG.md, GEN-marker idempotent) + docs/process/RELEASE_RITUAL.md separating automated preflight from human-gated tag/sandbox-test/build steps.

**Commits:**
- `a42bde6` — chore(process): V2 U6 tooling — gen_changelog.py (SHIPS.jsonl -> docs/CHANGELOG.md) + RELEASE_RITUAL.md

**Files touched:** `docs/CHANGELOG.md`, `docs/process/RELEASE_RITUAL.md`, `scripts/gen_changelog.py`

**Closes:** V2-U6-tooling

**Docs:** docs/process/RELEASE_RITUAL.md

---

# PROC-20260703-v2-u2-impact-map

Date: 2026-07-03 · Area: process / test-infra

V2 U2 impact-map: --changed / --changed-against / --dry-run in run_all_tests.py — maps changed source globs to affected tests + always t0; unmapped/broad-blast-radius files widen to whole suite loudly (no silent under-select). Shared-harness refactor deferred.

**Commits:**
- `2df65d4` — chore(process): V2 U2 impact-map --changed mode in run_all_tests.py (dev-loop <1min)

**Files touched:** `lite/tests/run_all_tests.py`

**Closes:** V2-U2-impact-map

---

# PROC-20260703-v2-u3gen-u5-truth

Date: 2026-07-03 · Area: process / docs-tooling

V2 U3 generator (scripts/gen_status_docs.py: SHIPS.jsonl -> 4 derived docs via GEN markers, idempotent, replaces bma-sprint-writer ~200-260K tok/finalize) + U5 executable-truth gate (scripts/check_executable_truth.py 5 assertions, wired into run_all_tests preflight).

**Commits:**
- `ea03f53` — chore(process): V2 U3 generator — SHIPS.jsonl → PATCH_SUMMARY/TEST_RESULT/FINAL_REPORT/LATEST_STATUS
- `770ee14` — chore(process): V2 U5 executable-truth gate wired into runner preflight

**Files touched:** `lite/tests/run_all_tests.py`, `scripts/check_executable_truth.py`, `scripts/gen_status_docs.py`, `scripts/gen_status_docs_README.md`

**Closes:** V2-U3-generator, V2-U5

**Docs:** scripts/gen_status_docs_README.md

---

# PROC-20260703-v2-u3ledger-u4-roadmap

Date: 2026-07-03 · Area: process / docs-tooling

V2 U3 ledger half (SHIPS.jsonl 16 entries + README) + U4 roadmap ACTIVE/DONE split (123 done rows -> ROADMAP_DONE.md, PHASE_INDEX 825->703) + scripts/reconcile_roadmap.py (flags un-moved/stale/dead-hash rows, exit-code gated).

**Commits:**
- `77a610f` — chore(process): V2 U3 SHIPS.jsonl ledger + U4 roadmap ACTIVE/DONE split + reconcile script

**Files touched:** `docs/status/PHASE_INDEX.md`, `docs/status/ROADMAP_DONE.md`, `docs/status/SHIPS.jsonl`, `docs/status/SHIPS_README.md`, `scripts/reconcile_roadmap.py`

**Closes:** V2-U3-ledger, V2-U4

**Docs:** docs/status/SHIPS_README.md

---

# SLICE-20260703-report-edit-default-grid

Date: 2026-07-03 · Area: report / ui (lite)

Editable jspreadsheet grid promoted to default report view; classic contenteditable table kept as print-fallback (off-screen swap + @media-print force-classic), #re-toggle repurposed grid->classic. report-edit.js unchanged.

**Commits:**
- `16698bb` — feat(lite): editable grid is default report view; classic as print-fallback toggle
- `99c37db` — chore(docs): NEXT_ACTIONS item 8 (report-edit default grid) shipped; item 9 re-scoped

**Files touched:** `docs/status/NEXT_ACTIONS.md`, `lite/lite-report.html`, `lite/tests/test_report_default_grid.py`

**Closes:** NEXT_ACTIONS-item-8

---

# PERF-20260703-worker-recycle-chh-probe

Date: 2026-07-03 · Area: perf-probe / docs

Production RSS re-probe of worker-recycle on the real 90.8MB CHH binder: recycleNow released ~1444MB (tree RSS 1796->352MB = -80.4%), reinit transparent 1.1s from local blob. Passes the >=50% bar.

**Commits:**
- `39de379` — chore(docs): record worker-recycle CHH production re-probe PASS (-80% tree RSS, reinit 1.1s)

**Files touched:** `docs/status/NEXT_ACTIONS.md`, `docs/status/PHASE_INDEX.md`

**Closes:** —

**Docs:** artifacts/perf/probe_worker_recycle_chh_20260703.txt

---

# BUG-20260703-lite-cfss-undo-masters

Date: 2026-07-03 · Area: measure / undo (lite)

Undo/redo now covers the CFSS MASTERS registry: additive masters key in _docSnap via snapshotMasters/restoreMasters + pushUndo in promote/edit; old snapshots restore gracefully.

**Commits:**
- `81c4325` — fix(lite): undo/redo now covers CFSS MASTERS registry (B4 follow-up)

**Files touched:** `lite/static/js/cross-floor-shapes.js`, `lite/tests/test_undo_masters.py`, `lite/ui-lite.html`

**Closes:** BUG-20260703-lite-cfss-undo-masters

**Docs:** lite/tests/bug-archive.jsonl

---

# UX-20260703-quickwins-batch2

Date: 2026-07-03 · Area: ui (lite)

UX quick-wins batch 2: F-4 HUD verified badge, F-5 mousedown hint, F-6 upload message, F-9 verify-scale in-app modal (no window.prompt), seeded-vars dim state, wizard Next gated at 0 tagged.

**Commits:**
- `036a49d` — feat(lite): UX batch 2 — F-4/F-5/F-6/F-9 + seeded-vars wait-state + wizard Next gate (UX-20260703)

**Files touched:** `lite/static/js/export-annotate.js`, `lite/static/js/menu-flyout.js`, `lite/static/js/overview-setup.js`, `lite/static/js/page-renderer.js`, `lite/static/js/report-vars.js`, `lite/static/js/verify-scale.js`, `lite/static/js/wiz-auto.js`, `lite/tests/test_ux_batch2.py`, `lite/ui-lite.html`

**Closes:** F-4, F-5, F-6, F-9

---

# INV-20260703-layer-linkage

Date: 2026-07-03 · Area: measure+layer (lite)

Layer<->measurement redesign B0-B5 (Approach B): object-agg.js tuple stream + I11 oracle, per-floor Summary, single engine, orphan-catId self-heal, move-to-layer UI, ref badges. H1/H2/H3/M4/M6 closed.

**Commits:**
- `edc89ae` — feat(lite): B0 — object-tuple aggregation engine + I11 oracle (INV-20260703-layer-linkage)
- `6909486` — feat(lite): B1 — report-vars + Summary per-floor block on the tuple engine (INV-20260703)
- `00ab9b9` — feat(lite): B2 — single aggregation engine; Review/tree sums on tuples (INV-20260703)
- `34594b7` — feat(lite): B3 — orphan catId self-heal + catOf crash guards (INV-20260703, H3 closed)
- `750d2f6` — feat(lite): B4 — move-object-to-layer UI (INV-20260703, H1 closed)
- `3d3741e` — feat(lite): B5 — Σ/▸ ref badges in report-var editor (INV-20260703, M4 closed)

**Files touched:** `lite/static/js/export-annotate.js`, `lite/static/js/layer-move.js`, `lite/static/js/layer-system.js`, `lite/static/js/layer-tree.js`, `lite/static/js/object-agg.js`, `lite/static/js/overview-setup.js`, `lite/static/js/page-folder-layers.js`, `lite/static/js/report-vars.js`, `lite/tests/test_b1_role_reroute.py`, `lite/tests/test_b2_single_engine.py`, `lite/tests/test_b3_orphan_heal.py`, `lite/tests/test_b4_move_layer.py`, `lite/tests/test_b5_ref_badges.py`, `lite/tests/test_object_tuples.py`, `lite/ui-lite.html`

**Closes:** H1, H2, H3, M4, M6

---

# UX-20260703-quickwins-batch1

Date: 2026-07-03 · Area: ui (lite)

UX quick-wins batch 1: F-7 modalOpen keydown guard (hotkey-leak class), F-1 dead Shift+D Path hotkey, F-2 F-key/Focus collision, F-3 Page Manager menu entry, cheatsheet corrections.

**Commits:**
- `34aefa3` — feat(lite-ux): UX quick-wins batch 1 — F-7 hotkey leak + F-1/F-2/F-3 + cheatsheet truth (UX-20260703)

**Files touched:** `lite/static/js/cheatsheet.js`, `lite/tests/test_ux_quickwins.py`, `lite/ui-lite.html`

**Closes:** F-1, F-2, F-3, F-7

---

# BUG-20260703-lite-save-wipes-data

Date: 2026-07-03 · Area: save/load (lite)

CRASH: Ctrl+S wrote an empty .bmaplan + wiped the live session. projectToGlobals resolves content from live PS by identity; guard drives the REAL mi-save click path (closed the API-vs-click test gap).

**Commits:**
- `d40b20b` — fix(BUG-20260703-lite-save-wipes-data): save no longer wipes all measurements

**Files touched:** `docs/status/PHASE_INDEX.md`, `lite/static/js/page-manager-ui.js`, `lite/static/js/page-manager.js`, `lite/tests/bug-archive.jsonl`, `lite/tests/test_save_clickpath.py`, `lite/ui-lite.html`

**Closes:** BUG-20260703-lite-save-wipes-data

**Docs:** lite/tests/bug-archive.jsonl

---

# GO-20260703-invariants-streaming-worker-recycle

Date: 2026-07-03 · Area: test-infra + perf (lite)

V2-U1 INVARIANTS.md registry + reconciled 16 stale rows; Range-streaming spike NOGO (worker heap survives destroy) -> RESHAPE to pdf.js worker-recycle build (explicit PDFWorker + lazy reinit).

**Commits:**
- `6d6e39b` — chore: V2-U1 invariant registry + PHASE_INDEX reconcile (16 stale rows)
- `9466fe4` — invent(lite): Range-streaming spike complete — NOGO on memory, RESHAPE to worker-recycle
- `f8c2981` — chore: PHASE_INDEX — record streaming spike verdict on the perf card
- `d52ddbb` — perf(lite): pdf.js worker-recycle — reclaim the worker heap (RESHAPE from streaming spike)

**Files touched:** `docs/invent/lite-range-streaming.md`, `docs/status/PHASE_INDEX.md`, `lite/sandbox/invent-range-streaming/results.json`, `lite/sandbox/invent-range-streaming/results.md`, `lite/sandbox/invent-range-streaming/s1_linearize.py`, `lite/sandbox/invent-range-streaming/s2_range.py`, `lite/sandbox/invent-range-streaming/spike.html`, `lite/sandbox/invent-range-streaming/spike_run.py`, `lite/static/js/page-renderer.js`, `lite/tests/INVARIANTS.md`, `lite/tests/test_worker_recycle.py`, `lite/ui-lite.html`

**Closes:** —

**Docs:** lite/tests/INVARIANTS.md,docs/invent/lite-range-streaming.md

---

# DOCS-20260702-dev-pillars-blueprint

Date: 2026-07-02 · Area: process / docs

DEVELOPMENT_PILLARS.md (6-pillar doctrine) + DEVELOPMENT_V2_BLUEPRINT.md (6 evidenced weaknesses -> 6 upgrades U1-U6). Methodology docs, no runtime change.

**Commits:**
- `16e6495` — docs(process): DEVELOPMENT_PILLARS.md — 6-pillar development doctrine
- `b676652` — docs(process): DEVELOPMENT_V2_BLUEPRINT — next-gen methodology from honest self-critique

**Files touched:** `docs/process/DEVELOPMENT_PILLARS.md`, `docs/process/DEVELOPMENT_V2_BLUEPRINT.md`

**Closes:** —

**Docs:** docs/process/DEVELOPMENT_PILLARS.md,docs/process/DEVELOPMENT_V2_BLUEPRINT.md

---

# ACC-20260703-verify-scale-port

Date: 2026-07-03 · Area: measure-ux / accuracy (lite)

Verify-Scale ported from proto: 2nd-reference calibration cross-check -> %dev band + accept/recalibrate/average, additive scale.verifyResult. Closes the last accuracy gap vs Foxit.

**Commits:**
- `bea2119` — feat(lite): Verify-Scale port — 2nd-reference calibration cross-check (accuracy gap vs Foxit closed)

**Files touched:** `lite/static/js/menu-flyout.js`, `lite/static/js/verify-scale.js`, `lite/tests/test_verify_scale.py`, `lite/ui-lite.html`

**Closes:** ACC-20260703-verify-scale-port

---

# AUDIT-20260702-render-followups

Date: 2026-07-03 · Area: render + test-infra (lite)

Raster JPEG fallback + scanned-page detection (scale cap); V2 test-pyramid t0/t1/t2 tiers; first sub-pixel raster<->overlay registration proof (max 0.5 device px).

**Commits:**
- `aec375b` — feat(lite-render): raster fallback + scanned-page detection with capped re-render (render-followups a+c)
- `13054b6` — feat(lite-tests): V2 test-pyramid tiers + overlay-registration pixel proof + streaming research

**Files touched:** `docs/invent/lite-range-streaming.md`, `docs/status/PHASE_INDEX.md`, `lite/static/js/page-renderer.js`, `lite/tests/run_all_tests.py`, `lite/tests/test_overlay_registration.py`, `lite/tests/test_render_fallback_scanned.py`

**Closes:** AUDIT-20260702-render-followups

**Docs:** docs/invent/lite-range-streaming.md

---

# AUDIT-20260702-s2-fitz-lock

Date: 2026-07-02 · Area: server perf (lite)

Per-case fitz threading.Lock serializes all Document access (/page /thumb /pageinfo + overlay render moved off event loop). Hardening hammer: 96-req 8-thread + mid-flight swap, zero 5xx.

**Commits:**
- `d0a5dde` — fix(lite-server): per-case fitz lock — serialize all Document access (AUDIT-20260702-s2-fitz-lock)

**Files touched:** `lite/server_lite.py`, `lite/tests/test_case_lock.py`

**Closes:** AUDIT-20260702-s2-fitz-lock

---

# PERF-20260702-lite-foxit-smoothness

Date: 2026-07-02 · Area: perf (lite)

Foxit-grade open smoothness (4 sprints): page-cache LRU, local-first open (paint before upload), worker warm-up + adjacent prefetch, sequential thumb warm. CHH heap 766->628MB; paint ~475ms.

**Commits:**
- `ae0f168` — perf(lite): LRU eviction for PDFPageProxy page cache (PERF-20260702 companion 1)
- `3ec9239` — perf(lite): local-first open — first paint no longer waits for upload (PERF-20260702 companion 2)
- `e0fb856` — perf(lite): pdf.js worker warm-up at idle + adjacent-page prefetch (PERF-20260702 companions 3-4)
- `a0c1152` — perf(lite): sequential thumbnail warm after upload (PERF-20260702 companion 6)

**Files touched:** `lite/static/js/page-renderer.js`, `lite/tests/test_local_open.py`, `lite/tests/test_pagecache_lru.py`, `lite/tests/test_thumb_warm.py`, `lite/tests/test_warm_prefetch.py`, `lite/ui-lite.html`

**Closes:** —

**Docs:** artifacts/perf/probe_results_20260702.txt

---

# AUDIT-20260702-infra-bundle

Date: 2026-07-02 · Area: test-infra + server (lite)

Test-runner + preflight (run_all_tests.py, disk/dep checks) and export payload caps + first real HTTP tests of /export-xlsx and /export-pdf-overlay (400 on oversize, latent-500 fix).

**Commits:**
- `9c4c36e` — feat(lite-tests): all-tests runner + free-space preflight (AUDIT-20260702-runner-preflight)
- `60d424a` — feat(lite-server): export payload caps + real export endpoint tests (AUDIT-20260702-export-caps)

**Files touched:** `lite/server_lite.py`, `lite/tests/run_all_tests.py`, `lite/tests/test_export_endpoints.py`

**Closes:** AUDIT-20260702-runner-preflight, AUDIT-20260702-export-caps

---

# BUG-20260702-lite-pagerot-registration

Date: 2026-07-02 · Area: measure-geometry / render (lite)

Manual page rotate now registers geometry with the rotated raster + export: getRot reads pageRot, ptToScreen/screenToPt route through vendored pdfToC/cToPdf (net 0 lines), server prerotates overlay.

**Commits:**
- `9f4b298` — fix(BUG-20260702-lite-pagerot-registration): geometry now registers with rotated raster

**Files touched:** `lite/server_lite.py`, `lite/static/js/export-annotate.js`, `lite/tests/test_pagerot_registration.py`, `lite/ui-lite.html`

**Closes:** BUG-20260702-lite-pagerot-registration

**Docs:** lite/tests/bug-archive.jsonl

---

# BUG-20260702-lite-cfss-summary

Date: 2026-07-02 · Area: measure-geometry (lite)

CFSS shared-shape instances now enter every rollup + export no longer crashes: promote captures catId/semanticTag, new rollupAreaM2/rollupCatId helpers rewire 6 rollup + 2 crash sites.

**Commits:**
- `02e35af` — fix(BUG-20260702-lite-cfss-summary): CFSS instances enter all rollups + export no longer crashes

**Files touched:** `lite/static/js/cross-floor-shapes.js`, `lite/static/js/export-annotate.js`, `lite/static/js/layer-tree.js`, `lite/static/js/overview-setup.js`, `lite/tests/test_summary_cfss_parity.py`, `lite/ui-lite.html`

**Closes:** BUG-20260702-lite-cfss-summary

**Docs:** lite/tests/bug-archive.jsonl

---

# BUG-20260702-lite-arc-summary

Date: 2026-07-02 · Area: measure-geometry (lite)

Arc-edge polygon areas entered all rollups arc-inclusive: swapped 6 rollup sites to polyMetricsAnyShape (labels were arc-correct, summaries silently under-counted).

**Commits:**
- `e5264e2` — fix(BUG-20260702-lite-arc-summary): arc-edge areas now enter all rollups arc-inclusive

**Files touched:** `lite/static/js/export-annotate.js`, `lite/static/js/layer-tree.js`, `lite/static/js/overview-setup.js`, `lite/tests/test_summary_arc_parity.py`, `lite/ui-lite.html`

**Closes:** BUG-20260702-lite-arc-summary

**Docs:** lite/tests/bug-archive.jsonl

---

<!-- GEN:END -->


---

<!-- INV-20260703-layer-linkage (plan B complete) + UX-batch-1 + save-fix follow-up / UX-REVIEW-20260703 + BUG-20260703-lite-save-wipes-data are the 2 kept in this file -->
<!-- GO-20260703-invariants-streaming-worker-recycle archived to docs/archive/patch-history-2026-07-03.md on 2026-07-03 (INV-20260703-layer-linkage plan-B-complete sprint block) -->
<!-- BLOCK-20260703-clear-queue archived to docs/archive/patch-history-2026-07-03.md on 2026-07-03 (UX-REVIEW-20260703 + BUG-20260703-lite-save-wipes-data sprint block) -->
<!-- PERF-20260702-lite-foxit-smoothness archived to docs/archive/patch-history-2026-07-02.md on 2026-07-03 (GO-20260703-invariants-streaming-worker-recycle sprint block) -->
<!-- BUG-20260702-lite-pagerot-registration archived to docs/archive/patch-history-2026-07-02.md on 2026-07-03 (BLOCK-20260703-clear-queue session) -->
<!-- AUDIT-20260702-infra-bundle archived to docs/archive/patch-history-2026-07-02.md on 2026-07-02 (PERF-20260702-lite-foxit-smoothness sprint block) -->
<!-- BUG-20260702-lite-cfss-summary + BUG-20260702-lite-arc-summary (2026-07-02) + SLICE report-edit-1 (2026-06-05) + BUG-20260526-lite-stale-pf-folder-cleanup + Centerline Snap arc (2026-05-25) archived to docs/archive/patch-history-2026-07-02.md on 2026-07-02 (BUG-20260702-lite-pagerot-registration sprint) -->
<!-- SIM-2 (2026-05-24) and older entries archived to docs/archive/patch-history-2026-05-09.md -->
