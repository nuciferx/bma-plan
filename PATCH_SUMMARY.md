# PATCH_SUMMARY.md — Latest Sprint

> Full patch history: [docs/archive/patch-history-2026-05-09.md](docs/archive/patch-history-2026-05-09.md) · [docs/archive/patch-history-2026-07-02.md](docs/archive/patch-history-2026-07-02.md) · [docs/archive/patch-history-2026-07-03.md](docs/archive/patch-history-2026-07-03.md) · [docs/archive/patch-history-2026-07-04.md](docs/archive/patch-history-2026-07-04.md) · [docs/archive/patch-history-2026-07-06.md](docs/archive/patch-history-2026-07-06.md) · [docs/archive/patch-history-2026-08.md](docs/archive/patch-history-2026-08.md)

---

<!-- GEN:START gen_status_docs -->

# Latest: GOV-MAXLEN ratchet + extraction project-io.js + idea capture + Bluebeam research (lite + governance)

Branch: main

Date: 2026-08-10 (ดึก)

## Outcome: PASS — maxlen ratchet closes the "long line" size-cap gameability gap; ui-lite.html headroom restored via extraction (1191→1086) without raising the 1200 cap; new idea filed; Bluebeam-batch invent research HALTED at checkpoint

## Summary

User decided the file-size-limit question ("นับตัวอักษรดีไหม" → keep line caps, ADD an ESLint-style `max-len` pair) — `033ad5c` adds check-1b `maxlen-ratchet` to `scripts/check_executable_truth.py`: no file may hold more lines >300 chars than its frozen baseline (`ui-lite.html` 10, vendored `measure-engine.js` 11, everything else 0), baseline may move between files during extractions but the TOTAL may only decrease, RED-proven by planting a 320-char line then reverting. `df5a1f2` then extracted the `.bmaplan` save/load region out of `lite/ui-lite.html` (1191→1086) byte-verbatim into NEW `lite/static/js/project-io.js` (154 lines, header documents the globals contract), restoring headroom under the unmoved 1200-line cap — byte-identity proven programmatically, `cross-floor-shapes.js` monkey-patches verified still landing post-extraction. `ffc763f` files a new invent-queued idea (Track AI อ่านแบบแปลน). `2e8ba9e`+`5ad9e3d` complete `/lite-invent` Phase 2 (research→diverge→score) for a 4-candidate Bluebeam-batch, HALTED at the human checkpoint per Pack H. This finalize also closes a self-audit gap: the 6 mandatory docs below had stalled at the evening (`ค่ำ`) batch while `log.md`/`SHIPS.jsonl` stayed current and code work (the extraction) continued.

## Files Changed

| File | Change |
|---|---|
| `scripts/check_executable_truth.py` | NEW check-1b `maxlen-ratchet` — gate now 6 checks (was 5) |
| `lite/ui-lite.html` | 1191→1086 lines — `.bmaplan` save/load region extracted out, byte-verbatim |
| `lite/static/js/project-io.js` | NEW (154 lines) — `SEM_REV`/`annFwd`/`annRev`/`buildPageStore`/`#mi-save`/`#mi-load`/`loadProto`/`#file-bma` moved from `ui-lite.html` |
| `~/.claude/ideas/IDEAS.md` (outside repo) + Drive mirror | Track AI อ่านแบบแปลน idea appended |
| `docs/status/PHASE_INDEX.md` | +`invent-queued` idea entry (Track AI); Bluebeam-batch checkpoint recorded |
| `docs/invent/bluebeam-batch.md` | NEW — 4-candidate research+diverge+score, HALTED at human checkpoint |
| `docs/status/SHIPS.jsonl` | +`GOV-MAXLEN-EXTRACT-20260810` row (already current before this finalize) |
| `lite/out.txt` | Deleted (untracked scratch file, already recommended for deletion by same-day module review; disclosed, accepted) |

## Source Files NOT Touched (Forbidden Surfaces)

- `proto/server.py` — untouched
- `polyAreaM2`, `polyMetrics`, `polySelfIntersects` — untouched
- `pdfToC`, `cToPdf`, `RS`, scale math, snap engine — untouched
- `.bmaplan` schema version stays 1; no schema fields touched (the extraction moved code, not data shape)

## Tests Run

`node --check lite/static/js/project-io.js` → OK. Persist battery 7/7 (`test_cfss_persist`, `test_custom_layer_persist`, `test_page_folder_persist`, `test_report_vars_persist`, `test_tree_persist`, `test_save_clickpath`, `test_metamorphic_pages`). `python scripts/check_executable_truth.py` → `TRUTH_CHECK_OK` (6/6, gate grew by 1 check this batch). Full suite `python lite/tests/run_all_tests.py` → 105/106 in 16.6 min — sole failure `test_closing_dup_strip.py`, the already-confirmed pre-existing one, zero new failures. `maxlen-ratchet` itself RED-proven by temporarily planting a 320-char line (→ `TRUTH_CHECK_FAIL`) then reverting.

## Phase 1 Scope Check

- ✅ No legal checker / OCR / AI / rule engine / FAR-OSR-setback touched
- ✅ proto/ untouched
- ✅ No forbidden surface touched
- ✅ `.bmaplan` schema untouched — extraction moved code location only, not data shape

**Commits:** `033ad5c` (chore: GOV-MAXLEN ratchet), `df5a1f2` (refactor(lite): extract project-io.js), `ffc763f` (chore: idea capture — Track AI อ่านแบบแปลน), `2e8ba9e` + `5ad9e3d` (docs(invent): Bluebeam-batch research HALTED@checkpoint)

**Process note:** self-audit ("opus เราทำตามกฎไหม") found the 7-output discipline partially skipped — `log.md`/`SHIPS.jsonl` were kept current but the other 6 docs stalled at the evening batch while runtime-affecting code work (the extraction) continued. This finalize closes that gap. Lesson: a governance/refactor batch still triggers the full 7-output rule the moment it touches runtime code.

---

# Previous: PKG-PORTABLE + PM-REDESIGN-D + SHELL — evening ship batch (lite)

Branch: main

Date: 2026-08-10 (ค่ำ)

## Outcome: PASS — closed both /lite-invent pipelines HALTED at this morning's checkpoint (zero-install portable build + hardened Page Manager + new bottom-bar/floating-panel shell)

## Summary

Evening batch shipping the two invent pipelines that halted at their human checkpoint earlier the same day, after the user GO'd both ("go ทั้งสองตัว"). PKG-PORTABLE (`fc4a407`) ships a zero-install portable build (`lite/build_portable.bat` → `dist-portable/BMA-Plan-Lite/`, Python 3.11.9 embed + deps + runtime, 115MB/3193 files, cold start 6.22s verified) plus an additive `BMA_LITE_NO_BROWSER` launch flag. PM-REDESIGN approach D (3 commits, spike 14/14 PASS before build) hardens the Page Manager: PM-GUARD (`c88a379`) routes every close path through a single guarded funnel so pending edits can no longer be silently discarded by clicking outside — directly fixing the user field report "เปิด page manager แล้วคลิกนอก = งานหาย"; TAG-JIT (`b0a13bf`) fixes the tag banner acting on a stale closure page; WIZ-UNLOCK (`fb9b2af`, user-approved breaking-ish UX policy change) retires the wizard's forced auto-open and global input hard-lock, structurally closing `BUG-20260810`. SHELL (`2b1887f`, needs-GO sprint cards, `PRIOR_ART_MATURE` so full invent was correctly skipped per rule) adds a new 7-cell bottom status bar and a Photoshop-style floating layer panel. Every code slice had a RED-first guard test; suite went 103/104 (after WIZ-UNLOCK) → 105/106 (after SHELL), the one remaining failure being the already-known pre-existing `test_closing_dup_strip.py`.

## Files Changed

| File | Change |
|---|---|
| `lite/build_portable.bat` | NEW — produces `dist-portable/BMA-Plan-Lite/` zero-install build |
| `lite/launch_lite.py` | +additive `BMA_LITE_NO_BROWSER` flag |
| `lite/README.md` | +portable build section |
| `.gitignore` | +dist-portable output dir |
| `lite/static/js/page-manager-ui.js` | PM-GUARD — single `_pmTryClose()` funnel, in-shell pending-edit warning, in-shell delete confirm with measurement count, no-PDF hint |
| `lite/tests/test_pm_guarded_close.py` | NEW — `LITE_PM_GUARD_OK` RED 5/5 → GREEN 7/7 |
| `lite/static/js/tag-jit.js` | TAG-JIT — chips re-read `curPage` at click; banner hides + pending tool clears on `afterPage`; `__jitWrapped` set post-success + 5×200ms retry ladder |
| `lite/tests/test_tag_jit_banner_fix.py` | NEW — `LITE_TAG_JIT_BANNER_OK` RED 2/2 → GREEN |
| `lite/static/js/wiz-auto.js` | WIZ-UNLOCK — 256→135 lines; auto-open triggers + global keydown/mousedown hard-lock removed |
| `lite/tests/test_wiz_auto.py` | Rewritten to new no-lock contract, 8/8 |
| `lite/tests/test_bug_force_setup.py` | Rewritten to new no-lock contract, 8/8 (non-lock coverage kept verbatim) |
| `lite/static/js/status-bar.js` | NEW (210L) — 7-cell bottom bar: page/floor, scale state, tool, draw-target layer, snap indicator, dirty dot, current-floor net via `ObjectAgg.byFloorRole` |
| `lite/static/js/float-panel.js` | NEW (232L) — Photoshop-style `#picker` wrapper: drag/collapse/hide/dblclick-reset, position persisted |
| `lite/tests/test_status_bar.py` | NEW — `LITE_STATUS_BAR_OK` 6/6 |
| `lite/tests/test_float_panel.py` | NEW — `LITE_FLOAT_PANEL_OK` 7/7 |
| `lite/tests/INVARIANTS.md` | +I2 consumer registration for `_sbFloorNet` |
| `lite/tests/test_summary_arc_parity.py` | +arc-inclusive parity fixture (`sbOk`) |
| `lite/ui-lite.html` | +2 script tags only (1189→1191/1200) |
| `docs/status/PHASE_INDEX.md`, `docs/status/SHIPS.jsonl` | 3 new ship rows, `BUG-20260810` closed structurally, both invents + both SHELL cards marked SHIPPED |
| `docs/invent/page-manager-redesign.md`, `docs/invent/lite-zero-install-packaging.md` | +Decision sections |

## Source Files NOT Touched (Forbidden Surfaces)

- `proto/server.py` — untouched, lite-only batch
- `polyAreaM2`, `polyMetrics`, `polySelfIntersects` — untouched
- `pdfToC`, `cToPdf`, `RS`, scale math, snap engine — untouched
- `.bmaplan` schema version stays 1; no schema fields touched

## Tests Run

Every code slice had a RED-first guard test: `LITE_PM_GUARD_OK` RED 5/5 → GREEN 7/7, `LITE_TAG_JIT_BANNER_OK` RED 2/2 → GREEN, `test_wiz_auto.py` 8/8 + `test_bug_force_setup.py` 8/8 (rewritten to the new no-lock contract), `LITE_STATUS_BAR_OK` 6/6, `LITE_FLOAT_PANEL_OK` 7/7. Full suite progression: 103/104 (after WIZ-UNLOCK) → 105/106 (after SHELL) — sole failure throughout is `test_closing_dup_strip.py`, already confirmed pre-existing by the prior PM-META+PM-ID sprint's `git stash` verification, unrelated to this batch. `python scripts/check_executable_truth.py` → `TRUTH_CHECK_OK` (5/5).

## Phase 1 Scope Check

- ✅ No legal checker / OCR / AI / rule engine / FAR-OSR-setback touched
- ✅ proto/ untouched, lite-only
- ✅ No forbidden surface touched
- ✅ `.bmaplan` schema untouched (additive-only rule not exercised — no new fields this batch)

**Commits:** `fc4a407` (feat: PKG-PORTABLE), `c88a379` (feat: PM-GUARD), `b0a13bf` (fix: TAG-JIT), `fb9b2af` (feat!: WIZ-UNLOCK), `2b1887f` (feat: SHELL status-bar+float-panel), `d231be5`+`3534d35`+`f89659d` (docs: GO both invents + ledger/roadmap close)

**Closes:** BUG-20260810-lite-pagemgr-blocked (structurally, via WIZ-UNLOCK), invent `page-manager-redesign` (SHIPPED), invent `lite-zero-install-packaging` (SHIPPED, approach B), sprint cards `SHELL-STATUS` + `SHELL-FLOAT`

---

<!-- PM-META + PM-ID (2026-08-10) archived to docs/archive/patch-history-2026-08.md on 2026-08-10 (ดึก finalize: GOV-MAXLEN + extraction, to keep root at Latest + 1 Previous) -->
<!-- BUG-20260706-lite-layer-page-binding archived to docs/archive/patch-history-2026-07-06.md on 2026-08-10 (ค่ำ finalize: PKG-PORTABLE + PM-REDESIGN-D + SHELL, to keep root at Latest + 1 Previous) -->
<!-- 2026-07-04 full-day block — 8 ships archived to docs/archive/patch-history-2026-07-04.md on 2026-08-10 (PM-META + PM-ID sprint finalize, to keep root at Latest + 1 Previous) -->

# AUDIT-20260703-roadmap-staleness

Date: 2026-07-03 · Area: process / roadmap hygiene

Full ACTIVE-row staleness audit after 2 stale cards in a row: found 3 more STALE-DONE (PERF-open-streaming status contradicted body; force-setup landed 32d5f38; probe-rewrite 707ed8f) + simulator idea superseded by Pack J; closed all + moved 4 tombstones; HK-1 *.gsheet gitignored; .git/refs desktop.ini removed (git log --all fixed). Root cause: fix commits carry card-id but docs follow-up commit sometimes never lands.

**Commits:** —

**Files touched:** —

**Closes:** PERF-20260702-open-streaming, BUG-20260526-lite-force-setup, LITE-PROBE-DBLCLICK-REWRITE, HK-1

---

# AUDIT-20260703-lfoc-order-b-verify

Date: 2026-07-03 · Area: layer / folders (lite)

LFOC-ORDER-B build audit: feature found fully landed (kind-aware PF folder ids + rank + seeds + Thai labels + 11-check guard already in tree); floorKey exact-inverse parity proven for 7 kind/tag pairs; zero code change - stale invent-done-go card closed.

**Commits:** —

**Files touched:** —

**Closes:** INV-2026-05-26-LFOC-ORDER-B

---

# TEST-20260526-wiz-followup-guard

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
