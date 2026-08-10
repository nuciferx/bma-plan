# FINAL_REPORT_FOR_CHATGPT.md — Sprint Outcome Report

> Full report history: [docs/archive/reports-2026-05-09.md](docs/archive/reports-2026-05-09.md) · [docs/archive/reports-2026-07-02.md](docs/archive/reports-2026-07-02.md) · [docs/archive/reports-2026-07-03.md](docs/archive/reports-2026-07-03.md) · [docs/archive/reports-2026-07-04.md](docs/archive/reports-2026-07-04.md) · [docs/archive/reports-2026-07-06.md](docs/archive/reports-2026-07-06.md)

---

<!-- GEN:START gen_status_docs -->

# Latest: PKG-PORTABLE + PM-REDESIGN-D + SHELL — PASS

**Date:** 2026-08-10 (ค่ำ)
**Branch:** main

## Outcome

Evening batch closing both `/lite-invent` pipelines that halted at their human checkpoint earlier the same day — the user GO'd both ("go ทั้งสองตัว"). Zero-install portable build now exists and works. The Page Manager's most severe field-reported issue (silent data loss on click-outside) is fixed. The wizard's forced auto-open + global input hard-lock, the root mechanism behind `BUG-20260810`, is retired. A new bottom status bar and Photoshop-style floating layer panel ship as the first pieces of the approved Shell v2 mockup. Every code slice had a RED-first guard test; the full suite stayed green throughout (103/104 → 105/106, one pre-existing failure unchanged).

## What was delivered

- **PKG-PORTABLE** (`fc4a407`): `lite/build_portable.bat` → `dist-portable/BMA-Plan-Lite/` (Python 3.11.9 embed + deps + runtime, 115MB/3193 files), cold start 6.22s verified with sanitized PATH + `/health` 200; additive `BMA_LITE_NO_BROWSER` flag
- **PM-GUARD** (`c88a379`): single guarded close funnel — backdrop/Esc/X can no longer silently discard pending edits; in-shell delete confirm shows measurement count; fixes the user field report "เปิด page manager แล้วคลิกนอก = งานหาย"
- **TAG-JIT** (`b0a13bf`): tag banner now acts on the live current page instead of a stale closure reference
- **WIZ-UNLOCK** (`fb9b2af`, user-approved breaking-ish UX change): wizard auto-open + global keydown/mousedown hard-lock removed (`wiz-auto.js` 256→135 lines); F12 wizard is manual-only now; structurally closes `BUG-20260810`
- **SHELL** (`2b1887f`): NEW `status-bar.js` (7-cell bottom bar incl. restored snap indicator + current-floor net) and NEW `float-panel.js` (Photoshop-style draggable/collapsible layer panel wrapper)
- Ledger/roadmap closed (`d231be5`/`3534d35`/`f89659d`): both invents + both SHELL cards marked SHIPPED, `BUG-20260810` closed structurally, `TRUTH_CHECK_OK` 5/5

## What's next

**User manual-test list leads the queue** (things a machine cannot verify) — wizard no longer force-opens and F12 still works, ⇧F12 reaches Page Manager right after opening a file, editing-in-progress in Page Manager then clicking outside shows a warning instead of closing, page delete confirm shows the measurement count, the new status bar shows all 7 cells and hides on ⇧F, the floating layer panel drags/collapses/hides and its position survives reload, `dist-portable` on a genuinely clean Windows machine (7-point checklist), and this morning's tag/rotate → Save fixes hold. After that: `test_closing_dup_strip.py` investigation, the module-review top-10 leftovers, page-pipeline slice 3-4, จานสี (layer palette) needs-GO, the parked E (pywebview) ruling, and Page Hub long-term merge.

## Position in Plan

Phase 1 (Raster PDF Measurement Assistant), `lite/` track. This is the invention-loop's build-and-ship half of two same-day `/lite-invent` pipelines (`page-manager-redesign` approach D, `lite-zero-install-packaging` approach B) plus a `PRIOR_ART_MATURE` shell sprint that correctly skipped the full invent pipeline per rule. No proto work, no forbidden-surface touches, no `.bmaplan` schema change. Next up: the 8-item user manual-test list above — do not queue further feature work on this surface until it's walked.

---

# Previous: PM-META + PM-ID — PASS

**Date:** 2026-08-10
**Branch:** main

## Outcome

Fixed the actual root cause underneath the user symptom "เลเยอร์มั่ว การจัดการหน้ามั่ว" (layers/page management scrambled) in `lite/`. Two bugs: PM-META, where every Save/Apply/Merge silently reverted page tags/rotations/floor numbers/exclusions to their open-time state because `_pmCommit` sourced live content but stale meta snapshots — the reverted meta then fed layer-folder re-derivation, producing the "scrambled layers" the user saw with no error shown. PM-ID, where the page-identity mint counter didn't advance on load/seed, so reopening a `.bmaplan` with a duplicate page could re-mint a colliding id and overwrite another page's data. Both fixed with additive, in-place changes (net 0 lines in `ui-lite.html`) and proven with RED-before/GREEN-after guard tests.

## What was delivered

- `PageModel.prototype._liveMetaFor` (mirrors the existing `_liveContentFor`) so `projectToGlobals(livePS, liveMeta)` resolves meta from live state instead of stale open-time snapshots
- `adoptId()` now advances the `_idc` mint counter past every adopted `pg<N>` id at both call sites, closing the duplicate-id collision on reopen
- New guard markers `LITE_PM_META_LIVE_OK` (E21) and `LITE_PM_ID_SEED_OK` (E22), both proven RED pre-fix then GREEN post-fix
- Full regression: `test_page_manager.py` 23/23, `check_executable_truth.py` 5/5, full suite 101/102 (1 pre-existing failure confirmed via git-stash, not this sprint's regression)
- Sprint delegated end-to-end: Opus wrote a ready-to-build work order after a 35-module review; `lite-builder` (sonnet) implemented; orchestrator reviewed diffs and committed

## What's next

File `test_closing_dup_strip.py`'s pre-existing failure as its own known-issue investigation; then the "slice 3-4" follow-ups from the 2026-08-10 page-pipeline review (pageRot/`_scanned` remap by identity on reorder, PM-overlay canvas/pageCount sync, wizard thumbnails via `serverNum()`); the tag-jit banner wrong-page-write + bootstrap-flag fix; and the top-10 list from today's module review (layer role=gfa hardcode, mixed count/area category m² loss, CFSS freeze dropping catId, etc.).

## Position in Plan

Phase 1 (Raster PDF Measurement Assistant), `lite/` track. Root-cause fix closing out the second half of `BUG-20260703` (I5) plus `I9`, both surfaced by the same-day 35-module review. No proto work, no forbidden-surface touches, no `.bmaplan` schema change. Next up: file the pre-existing test failure, then continue the page-pipeline follow-up queue.

---

<!-- BUG-20260706-lite-layer-page-binding archived to docs/archive/reports-2026-07-06.md on 2026-08-10 (ค่ำ finalize: PKG-PORTABLE + PM-REDESIGN-D + SHELL, to keep root at Latest + 1 Previous) -->
<!-- 2026-07-04 full-day block — 8 ships archived to docs/archive/reports-2026-07-04.md on 2026-08-10 (PM-META + PM-ID sprint finalize, to keep root at Latest + 1 Previous) -->

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
