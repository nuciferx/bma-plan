# CHANGELOG — BMA-Plan lite

Generated from `docs/status/SHIPS.jsonl` by `scripts/gen_changelog.py` — do not
hand-edit the region between the GEN markers; append a ship line to the ledger
and re-run `python scripts/gen_changelog.py --write`. Anything above the START
marker is hand-written and preserved.

<!-- GEN:START gen_changelog -->

## 2026-07-03

- **TEST-20260526-wiz-followup-guard** _wizard / test (lite)_
  - BUG-20260526-lite-wizard-followup: both fixes found already landed (dblclick lock gate; buildPicker after reseed) - added the missing guard test BUG_20260526_LITE_WIZ_FOLLOWUP_OK 4/4, RED-proven by temporary revert; card moved to done.
  - commits `71ba5be`, `2000a9a` · guards BUG_20260526_LITE_WIZ_FOLLOWUP_OK · closes BUG-20260526-lite-wizard-followup
- **FIX-20260703-undo-layers-folders** _layer / undo (lite)_
  - Undo/redo covers LAYERS+FOLDERS: additive _docSnap keys + in-place splice restore (CATS alias preserved); pushUndo at all UI entry points, seeding/load undo-silent; reconcile banner [ตามหน้า] now round-trips under Ctrl+Z. RED-proven.
  - commits `085ab60` · guards LITE_UNDO_LAYERS_OK · closes layer-redesign-followup-a, b4-undo-flag
- **INV-20260703-layer-redesign** _layer / model + ux (lite)_
  - Layer redesign A+B (user GO at invent checkpoint, spike 4/4): A-model layer.floorKey one-seam swap in objectTuples (precedence master->layer->page, additive persistence, old saves byte-identical) + B-ui layer-target-ui.js (draw-target chip, canvas tint, make-current marker, reconcile banner).
  - commits `76ee98c`, `f54bac3`, `92174b6`, `20129af` · guards LITE_LAYER_FLOORKEY_OK, LITE_LAYER_TARGET_UI_OK · closes P1-layer-floor-mismatch, P2-wrong-layer-draws, P3-role-layer-ambiguity
- **UX-20260703-quickwins-batch3** _ui (lite)_
  - UX batch 3: F-8 (11 error messages gain Thai next-step) + annotate Shift-hotkeys x7 via guarded central keydown + Thai PM/wizard strings + NEW empty-state.js pre-open overlay + NEW page-scan-badge.js per-page scanned/fallback badge.
  - commits `fcf5b23` · guards LITE_UX_BATCH3_OK · closes UX-F8, UX-COSMETIC-1-4
- **PROC-20260703-probe-dblclick-rewrite** _test-infra (simulate)_
  - LITE-BUG-DBLCLICK-OVER-POP probe rewritten mouse_sequence -> evaluate-only (modal/wizard-proof): injects state.draft [4 pts + 2 strays], synthetic dblclick on #cv, asserts 4-pt commit; validated live incl. old-bug emulation discriminating 3-pt.
  - commits `707ed8f` · closes NEXT_ACTIONS-item-11
- **PROC-20260703-v2-u6-changelog** _process / release-tooling_
  - V2 U6 automated half: scripts/gen_changelog.py (SHIPS.jsonl -> docs/CHANGELOG.md, GEN-marker idempotent) + docs/process/RELEASE_RITUAL.md separating automated preflight from human-gated tag/sandbox-test/build steps.
  - commits `a42bde6` · closes V2-U6-tooling
- **PROC-20260703-v2-u2-impact-map** _process / test-infra_
  - V2 U2 impact-map: --changed / --changed-against / --dry-run in run_all_tests.py — maps changed source globs to affected tests + always t0; unmapped/broad-blast-radius files widen to whole suite loudly (no silent under-select). Shared-harness refactor deferred.
  - commits `2df65d4` · guards LITE_RUN_ALL_OK · closes V2-U2-impact-map
- **PROC-20260703-v2-u3gen-u5-truth** _process / docs-tooling_
  - V2 U3 generator (scripts/gen_status_docs.py: SHIPS.jsonl -> 4 derived docs via GEN markers, idempotent, replaces bma-sprint-writer ~200-260K tok/finalize) + U5 executable-truth gate (scripts/check_executable_truth.py 5 assertions, wired into run_all_tests preflight).
  - commits `ea03f53`, `770ee14` · guards TRUTH_CHECK_OK · closes V2-U3-generator, V2-U5
- **PROC-20260703-v2-u3ledger-u4-roadmap** _process / docs-tooling_
  - V2 U3 ledger half (SHIPS.jsonl 16 entries + README) + U4 roadmap ACTIVE/DONE split (123 done rows -> ROADMAP_DONE.md, PHASE_INDEX 825->703) + scripts/reconcile_roadmap.py (flags un-moved/stale/dead-hash rows, exit-code gated).
  - commits `77a610f` · closes V2-U3-ledger, V2-U4
- **SLICE-20260703-report-edit-default-grid** _report / ui (lite)_
  - Editable jspreadsheet grid promoted to default report view; classic contenteditable table kept as print-fallback (off-screen swap + @media-print force-classic), #re-toggle repurposed grid->classic. report-edit.js unchanged.
  - commits `16698bb`, `99c37db` · guards LITE_REPORT_DEFAULT_GRID_OK · closes NEXT_ACTIONS-item-8
- **PERF-20260703-worker-recycle-chh-probe** _perf-probe / docs_
  - Production RSS re-probe of worker-recycle on the real 90.8MB CHH binder: recycleNow released ~1444MB (tree RSS 1796->352MB = -80.4%), reinit transparent 1.1s from local blob. Passes the >=50% bar.
  - commits `39de379`
- **BUG-20260703-lite-cfss-undo-masters** _measure / undo (lite)_
  - Undo/redo now covers the CFSS MASTERS registry: additive masters key in _docSnap via snapshotMasters/restoreMasters + pushUndo in promote/edit; old snapshots restore gracefully.
  - commits `81c4325` · guards LITE_UNDO_MASTERS_OK · closes BUG-20260703-lite-cfss-undo-masters
- **UX-20260703-quickwins-batch2** _ui (lite)_
  - UX quick-wins batch 2: F-4 HUD verified badge, F-5 mousedown hint, F-6 upload message, F-9 verify-scale in-app modal (no window.prompt), seeded-vars dim state, wizard Next gated at 0 tagged.
  - commits `036a49d` · guards LITE_UX_BATCH2_OK · closes F-4, F-5, F-6, F-9
- **INV-20260703-layer-linkage** _measure+layer (lite)_
  - Layer<->measurement redesign B0-B5 (Approach B): object-agg.js tuple stream + I11 oracle, per-floor Summary, single engine, orphan-catId self-heal, move-to-layer UI, ref badges. H1/H2/H3/M4/M6 closed.
  - commits `edc89ae`, `6909486`, `00ab9b9`, `34594b7`, `750d2f6`, `3d3741e` · guards LITE_OBJECT_TUPLES_OK, LITE_B1_ROLE_REROUTE_OK, LITE_B2_SINGLE_ENGINE_OK, LITE_B3_ORPHAN_HEAL_OK, LITE_B4_MOVE_LAYER_OK, LITE_B5_REF_BADGES_OK · closes H1, H2, H3, M4, M6
- **UX-20260703-quickwins-batch1** _ui (lite)_
  - UX quick-wins batch 1: F-7 modalOpen keydown guard (hotkey-leak class), F-1 dead Shift+D Path hotkey, F-2 F-key/Focus collision, F-3 Page Manager menu entry, cheatsheet corrections.
  - commits `34aefa3` · guards LITE_UX_QUICKWINS_OK · closes F-1, F-2, F-3, F-7
- **BUG-20260703-lite-save-wipes-data** _save/load (lite)_
  - CRASH: Ctrl+S wrote an empty .bmaplan + wiped the live session. projectToGlobals resolves content from live PS by identity; guard drives the REAL mi-save click path (closed the API-vs-click test gap).
  - commits `d40b20b` · guards LITE_SAVE_CLICKPATH_OK · closes BUG-20260703-lite-save-wipes-data
- **GO-20260703-invariants-streaming-worker-recycle** _test-infra + perf (lite)_
  - V2-U1 INVARIANTS.md registry + reconciled 16 stale rows; Range-streaming spike NOGO (worker heap survives destroy) -> RESHAPE to pdf.js worker-recycle build (explicit PDFWorker + lazy reinit).
  - commits `6d6e39b`, `9466fe4`, `f8c2981`, `d52ddbb` · guards LITE_WORKER_RECYCLE_OK
- **ACC-20260703-verify-scale-port** _measure-ux / accuracy (lite)_
  - Verify-Scale ported from proto: 2nd-reference calibration cross-check -> %dev band + accept/recalibrate/average, additive scale.verifyResult. Closes the last accuracy gap vs Foxit.
  - commits `bea2119` · guards LITE_VERIFY_SCALE_OK · closes ACC-20260703-verify-scale-port
- **AUDIT-20260702-render-followups** _render + test-infra (lite)_
  - Raster JPEG fallback + scanned-page detection (scale cap); V2 test-pyramid t0/t1/t2 tiers; first sub-pixel raster<->overlay registration proof (max 0.5 device px).
  - commits `aec375b`, `13054b6` · guards LITE_RENDER_FB_SCAN_OK, LITE_OVERLAY_REG_OK · closes AUDIT-20260702-render-followups

## 2026-07-02

- **DOCS-20260702-dev-pillars-blueprint** _process / docs_
  - DEVELOPMENT_PILLARS.md (6-pillar doctrine) + DEVELOPMENT_V2_BLUEPRINT.md (6 evidenced weaknesses -> 6 upgrades U1-U6). Methodology docs, no runtime change.
  - commits `16e6495`, `b676652`
- **AUDIT-20260702-s2-fitz-lock** _server perf (lite)_
  - Per-case fitz threading.Lock serializes all Document access (/page /thumb /pageinfo + overlay render moved off event loop). Hardening hammer: 96-req 8-thread + mid-flight swap, zero 5xx.
  - commits `d0a5dde` · guards LITE_CASE_LOCK_OK · closes AUDIT-20260702-s2-fitz-lock
- **PERF-20260702-lite-foxit-smoothness** _perf (lite)_
  - Foxit-grade open smoothness (4 sprints): page-cache LRU, local-first open (paint before upload), worker warm-up + adjacent prefetch, sequential thumb warm. CHH heap 766->628MB; paint ~475ms.
  - commits `ae0f168`, `3ec9239`, `e0fb856`, `a0c1152` · guards LITE_PAGECACHE_LRU_OK, LITE_LOCAL_OPEN_OK, LITE_WARM_PREFETCH_OK, LITE_THUMB_WARM_OK
- **AUDIT-20260702-infra-bundle** _test-infra + server (lite)_
  - Test-runner + preflight (run_all_tests.py, disk/dep checks) and export payload caps + first real HTTP tests of /export-xlsx and /export-pdf-overlay (400 on oversize, latent-500 fix).
  - commits `9c4c36e`, `60d424a` · guards LITE_RUN_ALL_OK, LITE_EXPORT_ENDPOINTS_OK · closes AUDIT-20260702-runner-preflight, AUDIT-20260702-export-caps
- **BUG-20260702-lite-pagerot-registration** _measure-geometry / render (lite)_
  - Manual page rotate now registers geometry with the rotated raster + export: getRot reads pageRot, ptToScreen/screenToPt route through vendored pdfToC/cToPdf (net 0 lines), server prerotates overlay.
  - commits `9f4b298` · guards LITE_PAGEROT_REG_OK · closes BUG-20260702-lite-pagerot-registration
- **BUG-20260702-lite-cfss-summary** _measure-geometry (lite)_
  - CFSS shared-shape instances now enter every rollup + export no longer crashes: promote captures catId/semanticTag, new rollupAreaM2/rollupCatId helpers rewire 6 rollup + 2 crash sites.
  - commits `02e35af` · guards LITE_SUMMARY_CFSS_OK · closes BUG-20260702-lite-cfss-summary
- **BUG-20260702-lite-arc-summary** _measure-geometry (lite)_
  - Arc-edge polygon areas entered all rollups arc-inclusive: swapped 6 rollup sites to polyMetricsAnyShape (labels were arc-correct, summaries silently under-counted).
  - commits `e5264e2` · guards LITE_SUMMARY_ARC_OK · closes BUG-20260702-lite-arc-summary

<!-- GEN:END -->
