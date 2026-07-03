# FINAL_REPORT_FOR_CHATGPT.md — Sprint Outcome Report

> Full report history: [docs/archive/reports-2026-05-09.md](docs/archive/reports-2026-05-09.md) · [docs/archive/reports-2026-07-02.md](docs/archive/reports-2026-07-02.md) · [docs/archive/reports-2026-07-03.md](docs/archive/reports-2026-07-03.md)

---

<!-- GEN:START gen_status_docs -->

# Latest: PROC-20260703-v2-u6-changelog — process / release-tooling

**Date:** 2026-07-03

V2 U6 automated half: scripts/gen_changelog.py (SHIPS.jsonl -> docs/CHANGELOG.md, GEN-marker idempotent) + docs/process/RELEASE_RITUAL.md separating automated preflight from human-gated tag/sandbox-test/build steps. Closes: V2-U6-tooling.

---

# Previous: PROC-20260703-v2-u2-impact-map — process / test-infra

**Date:** 2026-07-03

V2 U2 impact-map: --changed / --changed-against / --dry-run in run_all_tests.py — maps changed source globs to affected tests + always t0; unmapped/broad-blast-radius files widen to whole suite loudly (no silent under-select). Shared-harness refactor deferred. Closes: V2-U2-impact-map.

---

# PROC-20260703-v2-u3gen-u5-truth — process / docs-tooling

**Date:** 2026-07-03

V2 U3 generator (scripts/gen_status_docs.py: SHIPS.jsonl -> 4 derived docs via GEN markers, idempotent, replaces bma-sprint-writer ~200-260K tok/finalize) + U5 executable-truth gate (scripts/check_executable_truth.py 5 assertions, wired into run_all_tests preflight). Closes: V2-U3-generator, V2-U5.

---

# PROC-20260703-v2-u3ledger-u4-roadmap — process / docs-tooling

**Date:** 2026-07-03

V2 U3 ledger half (SHIPS.jsonl 16 entries + README) + U4 roadmap ACTIVE/DONE split (123 done rows -> ROADMAP_DONE.md, PHASE_INDEX 825->703) + scripts/reconcile_roadmap.py (flags un-moved/stale/dead-hash rows, exit-code gated). Closes: V2-U3-ledger, V2-U4.

---

# SLICE-20260703-report-edit-default-grid — report / ui (lite)

**Date:** 2026-07-03

Editable jspreadsheet grid promoted to default report view; classic contenteditable table kept as print-fallback (off-screen swap + @media-print force-classic), #re-toggle repurposed grid->classic. report-edit.js unchanged. Closes: NEXT_ACTIONS-item-8.

---

# PERF-20260703-worker-recycle-chh-probe — perf-probe / docs

**Date:** 2026-07-03

Production RSS re-probe of worker-recycle on the real 90.8MB CHH binder: recycleNow released ~1444MB (tree RSS 1796->352MB = -80.4%), reinit transparent 1.1s from local blob. Passes the >=50% bar.

---

# BUG-20260703-lite-cfss-undo-masters — measure / undo (lite)

**Date:** 2026-07-03

Undo/redo now covers the CFSS MASTERS registry: additive masters key in _docSnap via snapshotMasters/restoreMasters + pushUndo in promote/edit; old snapshots restore gracefully. Closes: BUG-20260703-lite-cfss-undo-masters.

---

# UX-20260703-quickwins-batch2 — ui (lite)

**Date:** 2026-07-03

UX quick-wins batch 2: F-4 HUD verified badge, F-5 mousedown hint, F-6 upload message, F-9 verify-scale in-app modal (no window.prompt), seeded-vars dim state, wizard Next gated at 0 tagged. Closes: F-4, F-5, F-6, F-9.

---

# INV-20260703-layer-linkage — measure+layer (lite)

**Date:** 2026-07-03

Layer<->measurement redesign B0-B5 (Approach B): object-agg.js tuple stream + I11 oracle, per-floor Summary, single engine, orphan-catId self-heal, move-to-layer UI, ref badges. H1/H2/H3/M4/M6 closed. Closes: H1, H2, H3, M4, M6.

---

# UX-20260703-quickwins-batch1 — ui (lite)

**Date:** 2026-07-03

UX quick-wins batch 1: F-7 modalOpen keydown guard (hotkey-leak class), F-1 dead Shift+D Path hotkey, F-2 F-key/Focus collision, F-3 Page Manager menu entry, cheatsheet corrections. Closes: F-1, F-2, F-3, F-7.

---

# BUG-20260703-lite-save-wipes-data — save/load (lite)

**Date:** 2026-07-03

CRASH: Ctrl+S wrote an empty .bmaplan + wiped the live session. projectToGlobals resolves content from live PS by identity; guard drives the REAL mi-save click path (closed the API-vs-click test gap). Closes: BUG-20260703-lite-save-wipes-data.

---

# GO-20260703-invariants-streaming-worker-recycle — test-infra + perf (lite)

**Date:** 2026-07-03

V2-U1 INVARIANTS.md registry + reconciled 16 stale rows; Range-streaming spike NOGO (worker heap survives destroy) -> RESHAPE to pdf.js worker-recycle build (explicit PDFWorker + lazy reinit).

---

# DOCS-20260702-dev-pillars-blueprint — process / docs

**Date:** 2026-07-02

DEVELOPMENT_PILLARS.md (6-pillar doctrine) + DEVELOPMENT_V2_BLUEPRINT.md (6 evidenced weaknesses -> 6 upgrades U1-U6). Methodology docs, no runtime change.

---

# ACC-20260703-verify-scale-port — measure-ux / accuracy (lite)

**Date:** 2026-07-03

Verify-Scale ported from proto: 2nd-reference calibration cross-check -> %dev band + accept/recalibrate/average, additive scale.verifyResult. Closes the last accuracy gap vs Foxit. Closes: ACC-20260703-verify-scale-port.

---

# AUDIT-20260702-render-followups — render + test-infra (lite)

**Date:** 2026-07-03

Raster JPEG fallback + scanned-page detection (scale cap); V2 test-pyramid t0/t1/t2 tiers; first sub-pixel raster<->overlay registration proof (max 0.5 device px). Closes: AUDIT-20260702-render-followups.

---

# AUDIT-20260702-s2-fitz-lock — server perf (lite)

**Date:** 2026-07-02

Per-case fitz threading.Lock serializes all Document access (/page /thumb /pageinfo + overlay render moved off event loop). Hardening hammer: 96-req 8-thread + mid-flight swap, zero 5xx. Closes: AUDIT-20260702-s2-fitz-lock.

---

# PERF-20260702-lite-foxit-smoothness — perf (lite)

**Date:** 2026-07-02

Foxit-grade open smoothness (4 sprints): page-cache LRU, local-first open (paint before upload), worker warm-up + adjacent prefetch, sequential thumb warm. CHH heap 766->628MB; paint ~475ms.

---

# AUDIT-20260702-infra-bundle — test-infra + server (lite)

**Date:** 2026-07-02

Test-runner + preflight (run_all_tests.py, disk/dep checks) and export payload caps + first real HTTP tests of /export-xlsx and /export-pdf-overlay (400 on oversize, latent-500 fix). Closes: AUDIT-20260702-runner-preflight, AUDIT-20260702-export-caps.

---

# BUG-20260702-lite-pagerot-registration — measure-geometry / render (lite)

**Date:** 2026-07-02

Manual page rotate now registers geometry with the rotated raster + export: getRot reads pageRot, ptToScreen/screenToPt route through vendored pdfToC/cToPdf (net 0 lines), server prerotates overlay. Closes: BUG-20260702-lite-pagerot-registration.

---

# BUG-20260702-lite-cfss-summary — measure-geometry (lite)

**Date:** 2026-07-02

CFSS shared-shape instances now enter every rollup + export no longer crashes: promote captures catId/semanticTag, new rollupAreaM2/rollupCatId helpers rewire 6 rollup + 2 crash sites. Closes: BUG-20260702-lite-cfss-summary.

---

# BUG-20260702-lite-arc-summary — measure-geometry (lite)

**Date:** 2026-07-02

Arc-edge polygon areas entered all rollups arc-inclusive: swapped 6 rollup sites to polyMetricsAnyShape (labels were arc-correct, summaries silently under-counted). Closes: BUG-20260702-lite-arc-summary.

---

<!-- GEN:END -->


---

<!-- INV-20260703-layer-linkage (plan B complete) + UX-batch-1 + save-fix follow-up / UX-REVIEW-20260703 + BUG-20260703-lite-save-wipes-data are the 2 kept in this file -->
<!-- GO-20260703-invariants-streaming-worker-recycle archived to docs/archive/reports-2026-07-03.md on 2026-07-03 (INV-20260703-layer-linkage plan-B-complete sprint block) -->
<!-- BLOCK-20260703-clear-queue archived to docs/archive/reports-2026-07-03.md on 2026-07-03 (UX-REVIEW-20260703 + BUG-20260703-lite-save-wipes-data sprint block) -->
<!-- PERF-20260702-lite-foxit-smoothness archived to docs/archive/reports-2026-07-02.md on 2026-07-03 (GO-20260703-invariants-streaming-worker-recycle session) -->
<!-- BUG-20260702-lite-pagerot-registration archived to docs/archive/reports-2026-07-02.md on 2026-07-03 (BLOCK-20260703-clear-queue session) -->
<!-- AUDIT-20260702-infra-bundle archived to docs/archive/reports-2026-07-02.md on 2026-07-02 (PERF-20260702-lite-foxit-smoothness sprint block) -->
<!-- BUG-20260702-lite-cfss-summary + BUG-20260702-lite-arc-summary (2026-07-02) + SLICE report-edit-1 (2026-06-05) + BUG-20260526-lite-stale-pf-folder-cleanup + Centerline Snap arc (2026-05-25) archived to docs/archive/reports-2026-07-02.md on 2026-07-02 (BUG-20260702-lite-pagerot-registration sprint) -->
<!-- SIM-2 (2026-05-24) and older reports archived to docs/archive/reports-2026-05-09.md -->
