# FINAL_REPORT_FOR_CHATGPT.md — Sprint Outcome Report

> Full report history: [docs/archive/reports-2026-05-09.md](docs/archive/reports-2026-05-09.md) · [docs/archive/reports-2026-07-02.md](docs/archive/reports-2026-07-02.md) · [docs/archive/reports-2026-07-03.md](docs/archive/reports-2026-07-03.md)

---

<!-- GEN:START gen_status_docs -->

# Latest: BUG-20260706-lite-layer-page-binding — PASS

**Date:** 2026-07-06
**Branch:** main

## Outcome

Two user-reported field bugs in `lite/`, both traced to the page↔layer binding introduced by `INV-2026-07-04-001`, fixed and shipped in one commit (`ba109f0`). Bug 1 was a silent data-correctness defect (BROKEN): the active draw layer did not follow the page when navigating to a folder never visited this session, so measurements could land in the wrong floor's layer with no warning — confirmed by a user screenshot on page 29. Bug 2 was a discoverability gap (FRICTION): a 2-sheet site plan's second sheet was unreachable from the new floor-rail/dropdown/search nav surface, so it was correctly tagged but never drawn, leaving the report showing only one sheet.

## What was delivered

- Active-layer fallback: entering a folder never visited this session now selects that folder's first layer (model order) instead of leaving the previous folder's category active
- New `lsForeignDrawBlocked()` commit-path guard on `finishDraft()` + the count tool, refusing a commit whose target layer doesn't match the current page's folder, with a 5s `state.hintFlash` warning
- `_lsGoTo` made page-aware: re-selecting the active folder steps to the next page within it (wrapping); arriving from another folder goes to `pages[0]`
- Floor-rail ◀/▶ now steps pages within a folder before crossing folders; counter shows "ชั้น i/N · แผ่น i/N"
- `test_layer_scope.py` expanded 6→9 checks; first run caught a real bug in the fix itself (hint write silently overwritten by `draw()`→`updateHUD()`), fixed same session

## What's next

User field re-test of `ba109f0` (active-layer follow + 2-sheet site plan) and the still-pending `e1c6a76` layer re-test; then `BUG-20260605-lite-load-color-null` (still NEEDS-REPRO), `INV-2026-05-25-001` centerline (awaiting user field data), and the lowest-priority `UX-20260703` export-entry consolidation.

## Position in Plan

Phase 1 (Raster PDF Measurement Assistant), `lite/` track. Bug-report intake/fix cycle (Pack I pattern) closing out a same-day field-report pair from the 2026-07-04 layer-panel ship. No proto work, no forbidden-surface touches. Next up: user field validation before further feature work.

---

# Previous: 2026-07-04 full-day block — 8 ships — layer/report/measure/render (lite)

**Date:** 2026-07-04

One-day block, 18 commits, lite-only, proto untouched. 2 invent→build arcs (layer-menu-ui-fix `c35c1a7`→`7600fde`+`e1c6a76` closing INV-2026-07-04-001, absorbing LFOC-1e; page-tagging-workflow `0a6677a`→`2df5d40` closing INV-2026-07-04-002, absorbing REVIEW S-10) both driven by Fable reviews and closed with opus first-stage review + Fable final GO. A 5-slice report-truth rework (`bb5090f`/`6ba7ea3`/`fc63e72`/`8362c3f`/`52725a1`) moved XLSX/grid/report onto the object-agg tuple stream, made the grid the single source of truth (classic table deleted), added 3 truthful export doors + Thai PDF-overlay labels, and a plan-image appendix with SVG overlays. A user field report ("pdf เปิดกลับข้าง") led to `BUG-20260704-lite-native-rotate` (`fbe28fb`) — PDF.js explicit-rotation viewport was silently overriding intrinsic `/Rotate`, a regression from the prior day's streaming work; fixed with a 2-line change, repro-first (6 checks RED pre-fix → 24/24 GREEN). A Fable snap review led to `SNAP-2026-07-04` (`cd6a960`/`23f3914`/`42a0767`) — snap-engine extraction + static-intersection cache, angle-lock composing with snap, and 5-type nearest-on-edge symmetry; centerline-unification and wall-trace were explicitly deferred per user choice. `SCALE-GATE` (`a5044aa`) added a second JIT gate refusing measurement on an unscaled page. Full lite suite 97/98 green (1 pre-existing test-side bug, not app). `ui-lite.html` net DOWN (1197→1188) across 6 feature ships thanks to 2 size-cap extractions.

## What was delivered

- Context-scoped layer panel (floor-rail + grouped search) replacing the flat 100-floor layer list
- Reworked page-tagging workflow: bulk apply, group-by-tag verify view, per-page JIT gate
- Truthful report/export pipeline: single tuple-stream source of truth, deduction sign shown, grid-only printing, plan-image appendix
- Fixed native page-rotation bug reported by the user in the field
- Extracted, faster snap engine with angle-lock composition and edge-symmetry toggle
- Second JIT gate blocking measurement before scale is set

## What's next

User field re-test of everything shipped today; then centerline-snap robustness (`INV-2026-05-25-001`, awaiting field data), LFOC queue, a housekeeping pair (`test_closing_dup_strip` + `test_undo_layers` cp1252 crash), and the wall-trace-assist invent idea.

## Position in Plan

Phase 1 (Raster PDF Measurement Assistant), `lite/` track. This block continues the post-GO-20260703 cadence of Fable-reviewed invent→build cycles plus field-driven bugfixes; no proto work, no forbidden-surface touches. Next up per user: field validation pass before further feature work.

---

# AUDIT-20260703-roadmap-staleness — process / roadmap hygiene

**Date:** 2026-07-03

Full ACTIVE-row staleness audit after 2 stale cards in a row: found 3 more STALE-DONE (PERF-open-streaming status contradicted body; force-setup landed 32d5f38; probe-rewrite 707ed8f) + simulator idea superseded by Pack J; closed all + moved 4 tombstones; HK-1 *.gsheet gitignored; .git/refs desktop.ini removed (git log --all fixed). Root cause: fix commits carry card-id but docs follow-up commit sometimes never lands. Closes: PERF-20260702-open-streaming, BUG-20260526-lite-force-setup, LITE-PROBE-DBLCLICK-REWRITE, HK-1.

---

# AUDIT-20260703-lfoc-order-b-verify — layer / folders (lite)

**Date:** 2026-07-03

LFOC-ORDER-B build audit: feature found fully landed (kind-aware PF folder ids + rank + seeds + Thai labels + 11-check guard already in tree); floorKey exact-inverse parity proven for 7 kind/tag pairs; zero code change - stale invent-done-go card closed. Closes: INV-2026-05-26-LFOC-ORDER-B.

---

# TEST-20260526-wiz-followup-guard — wizard / test (lite)

**Date:** 2026-07-03

BUG-20260526-lite-wizard-followup: both fixes found already landed (dblclick lock gate; buildPicker after reseed) - added the missing guard test BUG_20260526_LITE_WIZ_FOLLOWUP_OK 4/4, RED-proven by temporary revert; card moved to done. Closes: BUG-20260526-lite-wizard-followup.

---

# FIX-20260703-undo-layers-folders — layer / undo (lite)

**Date:** 2026-07-03

Undo/redo covers LAYERS+FOLDERS: additive _docSnap keys + in-place splice restore (CATS alias preserved); pushUndo at all UI entry points, seeding/load undo-silent; reconcile banner [ตามหน้า] now round-trips under Ctrl+Z. RED-proven. Closes: layer-redesign-followup-a, b4-undo-flag.

---

# INV-20260703-layer-redesign — layer / model + ux (lite)

**Date:** 2026-07-03

Layer redesign A+B (user GO at invent checkpoint, spike 4/4): A-model layer.floorKey one-seam swap in objectTuples (precedence master->layer->page, additive persistence, old saves byte-identical) + B-ui layer-target-ui.js (draw-target chip, canvas tint, make-current marker, reconcile banner). Closes: P1-layer-floor-mismatch, P2-wrong-layer-draws, P3-role-layer-ambiguity.

---

# UX-20260703-quickwins-batch3 — ui (lite)

**Date:** 2026-07-03

UX batch 3: F-8 (11 error messages gain Thai next-step) + annotate Shift-hotkeys x7 via guarded central keydown + Thai PM/wizard strings + NEW empty-state.js pre-open overlay + NEW page-scan-badge.js per-page scanned/fallback badge. Closes: UX-F8, UX-COSMETIC-1-4.

---

# PROC-20260703-probe-dblclick-rewrite — test-infra (simulate)

**Date:** 2026-07-03

LITE-BUG-DBLCLICK-OVER-POP probe rewritten mouse_sequence -> evaluate-only (modal/wizard-proof): injects state.draft [4 pts + 2 strays], synthetic dblclick on #cv, asserts 4-pt commit; validated live incl. old-bug emulation discriminating 3-pt. Closes: NEXT_ACTIONS-item-11.

---

# PROC-20260703-v2-u6-changelog — process / release-tooling

**Date:** 2026-07-03

V2 U6 automated half: scripts/gen_changelog.py (SHIPS.jsonl -> docs/CHANGELOG.md, GEN-marker idempotent) + docs/process/RELEASE_RITUAL.md separating automated preflight from human-gated tag/sandbox-test/build steps. Closes: V2-U6-tooling.

---

# PROC-20260703-v2-u2-impact-map — process / test-infra

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
