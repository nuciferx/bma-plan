# TEST_RESULT.md — Latest Test Result

> Full test history: [docs/archive/test-history-2026-05-09.md](docs/archive/test-history-2026-05-09.md) · [docs/archive/test-history-2026-07-02.md](docs/archive/test-history-2026-07-02.md) · [docs/archive/test-history-2026-07-03.md](docs/archive/test-history-2026-07-03.md) · [docs/archive/test-history-2026-07-04.md](docs/archive/test-history-2026-07-04.md) · [docs/archive/test-history-2026-07-06.md](docs/archive/test-history-2026-07-06.md) · [docs/archive/test-history-2026-08.md](docs/archive/test-history-2026-08.md)

---

<!-- GEN:START gen_status_docs -->

# Latest: GOV-MAXLEN ratchet + extraction project-io.js

Date: 2026-08-10 (ดึก) · Area: test-infra governance + size-cap extraction (lite)

_lite-only + governance-tooling, proto untouched. No forbidden surface (measure-engine/pdfToC/RS/snap untouched) — no proto E2E run._

| Slice | Check | RED (pre-fix) | GREEN (post-fix) |
|---|---|---|---|
| GOV-MAXLEN (`033ad5c`) | `scripts/check_executable_truth.py` check-1b `maxlen-ratchet` | planted a 320-char line → `TRUTH_CHECK_FAIL` | reverted → `TRUTH_CHECK_OK` (6/6, gate grew by 1) |
| Extraction (`df5a1f2`) | `node --check lite/static/js/project-io.js` | n/a (new file) | OK |
| Extraction (`df5a1f2`) | Persist battery (7 files) | — | 7/7 pass |
| Extraction (`df5a1f2`) | `cross-floor-shapes.js` wrapper landing check | — | `wrappersInstalled=True` |
| Extraction (`df5a1f2`) | Full suite `run_all_tests.py` | — | 105/106 in 16.6 min |

**Persist battery (7/7):** `test_cfss_persist`, `test_custom_layer_persist`, `test_page_folder_persist`, `test_report_vars_persist`, `test_tree_persist`, `test_save_clickpath`, `test_metamorphic_pages` — all green, proving the `.bmaplan` save/load region extracted byte-verbatim into `lite/static/js/project-io.js` behaves identically to the pre-extraction inline code.

**Full suite:** 105/106 (unchanged from the evening batch's final count) — sole failure `test_closing_dup_strip.py`, the already-confirmed pre-existing one (see the PM-META+PM-ID entry, archived to [docs/archive/test-history-2026-08.md](docs/archive/test-history-2026-08.md)). Zero new failures introduced by this batch.

`python scripts/check_executable_truth.py` → `TRUTH_CHECK_OK` (6/6) — the gate itself grew by one check in this batch (`maxlen-ratchet`), and that new check was proven RED-first before being confirmed GREEN, matching the project's own guard-test discipline applied to its own tooling.

**Disclosure (not a test failure, a process note):** the extraction builder subagent also deleted the untracked scratch file `lite/out.txt` (already recommended for deletion by the same-day module review) — accepted, no recovery needed, but it motivates a new builder-prompt rule that subagents must not delete files outside their allowed list (previously only git write operations were forbidden in subagent specs).

Commits: `033ad5c`, `df5a1f2`, `ffc763f` (idea capture, no test — see no-test rationale below), `2e8ba9e`, `5ad9e3d` (Bluebeam-batch research, no test — docs/research only). Closes: none (idea capture + invent research are not "closing" work); extends the truth-check gate and restores `ui-lite.html` line-cap headroom.

## No-Test Rationale (idea capture + Bluebeam research pieces)

Per AGENTS.md §1, the idea-capture commit (`ffc763f`) and the Bluebeam-batch research commits (`2e8ba9e`+`5ad9e3d`) are docs/research-only — no source code, UI, test code, or `.bmaplan` schema changed by either. `ffc763f` appends to `~/.claude/ideas/IDEAS.md` (outside the repo) and a one-line `invent-queued` bullet to `docs/status/PHASE_INDEX.md`. `2e8ba9e`/`5ad9e3d` write `docs/invent/bluebeam-batch.md` (research + diverge + score, HALTED at the human checkpoint per Pack H — no spike code was written, since the checkpoint precedes SPIKE for 3 of the 4 candidates and (a) Compare/Overlay is the only one needing SPIKE, not yet reached). Therefore `py_compile`/smoke/full were not run for these two pieces specifically; they are covered by the same full-suite 105/106 run reported above (run after all 5 commits, confirming zero regression from the docs-only pieces).

---

# Previous: PKG-PORTABLE + PM-REDESIGN-D + SHELL

Date: 2026-08-10 (ค่ำ) · Area: packaging + page-manager + shell UI (lite)

_lite-only, proto untouched. No forbidden surface (measure-engine/pdfToC/RS/snap untouched) — no proto E2E run. Every code slice had a RED-first guard test, and the full suite was re-run after each ship, showing a clean progression._

| Slice | Marker | RED (pre-fix) | GREEN (post-fix) |
|---|---|---|---|
| PM-GUARD (`c88a379`) | `LITE_PM_GUARD_OK` | 5/5 fail | 7/7 pass |
| TAG-JIT (`b0a13bf`) | `LITE_TAG_JIT_BANNER_OK` | 2/2 fail | pass |
| WIZ-UNLOCK (`fb9b2af`) | `test_wiz_auto.py` + `test_bug_force_setup.py` | rewritten to new no-lock contract (old lock-based checks retired, non-lock coverage kept) | 8/8 + 8/8 |
| SHELL status-bar (`2b1887f`) | `LITE_STATUS_BAR_OK` | RED-first | 6/6 pass |
| SHELL float-panel (`2b1887f`) | `LITE_FLOAT_PANEL_OK` | RED-first | 7/7 pass |

**Full suite progression this batch:** 103/104 (measured after WIZ-UNLOCK landed) → 105/106 (measured after SHELL landed). The suite is growing (2 new test files, `test_status_bar.py` + `test_float_panel.py`, on top of the 2 added by PM-GUARD/TAG-JIT) while staying at exactly one failing file throughout — `test_closing_dup_strip.py`, already confirmed **pre-existing** by the prior `PM-META + PM-ID` sprint's `git stash` verification against the unmodified tree (not a regression from this batch or any commit in it).

`python scripts/check_executable_truth.py` → `TRUTH_CHECK_OK` (5/5), confirmed after the ledger/roadmap close commit (`f89659d`).

**I2 invariant discipline note (SHELL):** `status-bar.js`'s new `_sbFloorNet` consumer of `ObjectAgg.byFloorRole` was registered in `lite/tests/INVARIANTS.md`'s I2 consumer list, and an arc-inclusive parity fixture was added to `test_summary_arc_parity.py` (`sbOk: True`) in the same commit — the standing rule from `INVARIANTS.md` for any new consumer of the tuple-aggregation engine.

**PKG-PORTABLE verification (not an automated test — a manual/scripted build-and-launch check):** `lite/build_portable.bat` build verified with sanitized PATH launch, cold start 6.22s, `/health` returning 200. Not part of `run_all_tests.py`; still outstanding is a user test on one genuinely clean Windows machine (7-point checklist communicated separately, not yet run).

Commits: `fc4a407`, `c88a379`, `b0a13bf`, `fb9b2af`, `2b1887f`, `d231be5`, `3534d35`, `f89659d`. Closes: BUG-20260810-lite-pagemgr-blocked (structurally), invent `page-manager-redesign` (SHIPPED), invent `lite-zero-install-packaging` (SHIPPED, approach B), sprint cards `SHELL-STATUS` + `SHELL-FLOAT`

---

<!-- PM-META + PM-ID (2026-08-10) archived to docs/archive/test-history-2026-08.md on 2026-08-10 (ดึก finalize: GOV-MAXLEN + extraction, to keep root at Latest + 1 Previous) -->
<!-- BUG-20260706-lite-layer-page-binding archived to docs/archive/test-history-2026-07-06.md on 2026-08-10 (ค่ำ finalize: PKG-PORTABLE + PM-REDESIGN-D + SHELL, to keep root at Latest + 1 Previous) -->
<!-- 2026-07-04 full-day block — 8 ships archived to docs/archive/test-history-2026-07-04.md on 2026-08-10 (PM-META + PM-ID sprint finalize, to keep root at Latest + 1 Previous) -->

# AUDIT-20260703-roadmap-staleness

Date: 2026-07-03 · Area: process / roadmap hygiene

_No guard markers — docs / process / research ship (no dedicated marker)._

Closes: PERF-20260702-open-streaming, BUG-20260526-lite-force-setup, LITE-PROBE-DBLCLICK-REWRITE, HK-1

---

# AUDIT-20260703-lfoc-order-b-verify

Date: 2026-07-03 · Area: layer / folders (lite)

_lite-only, proto untouched._

| Marker | Result |
|---|---|
| LITE_PF_KIND_OK | PASS |

Closes: INV-2026-05-26-LFOC-ORDER-B

---

# TEST-20260526-wiz-followup-guard

Date: 2026-07-03 · Area: wizard / test (lite)

_lite-only, proto untouched._

| Marker | Result |
|---|---|
| BUG_20260526_LITE_WIZ_FOLLOWUP_OK | PASS |

Closes: BUG-20260526-lite-wizard-followup

---

# FIX-20260703-undo-layers-folders

Date: 2026-07-03 · Area: layer / undo (lite)

_lite-only, proto untouched._

| Marker | Result |
|---|---|
| LITE_UNDO_LAYERS_OK | PASS |

Closes: layer-redesign-followup-a, b4-undo-flag

---

# INV-20260703-layer-redesign

Date: 2026-07-03 · Area: layer / model + ux (lite)

_lite-only, proto untouched._

| Marker | Result |
|---|---|
| LITE_LAYER_FLOORKEY_OK | PASS |
| LITE_LAYER_TARGET_UI_OK | PASS |

Closes: P1-layer-floor-mismatch, P2-wrong-layer-draws, P3-role-layer-ambiguity

---

# UX-20260703-quickwins-batch3

Date: 2026-07-03 · Area: ui (lite)

_lite-only, proto untouched._

| Marker | Result |
|---|---|
| LITE_UX_BATCH3_OK | PASS |

Closes: UX-F8, UX-COSMETIC-1-4

---

# PROC-20260703-probe-dblclick-rewrite

Date: 2026-07-03 · Area: test-infra (simulate)

_No guard markers — docs / process / research ship (no dedicated marker)._

Closes: NEXT_ACTIONS-item-11

---

# PROC-20260703-v2-u6-changelog

Date: 2026-07-03 · Area: process / release-tooling

_No guard markers — docs / process / research ship (no dedicated marker)._

Closes: V2-U6-tooling

---

# PROC-20260703-v2-u2-impact-map

Date: 2026-07-03 · Area: process / test-infra

| Marker | Result |
|---|---|
| LITE_RUN_ALL_OK | PASS |

Closes: V2-U2-impact-map

---

# PROC-20260703-v2-u3gen-u5-truth

Date: 2026-07-03 · Area: process / docs-tooling

| Marker | Result |
|---|---|
| TRUTH_CHECK_OK | PASS |

Closes: V2-U3-generator, V2-U5

---

# PROC-20260703-v2-u3ledger-u4-roadmap

Date: 2026-07-03 · Area: process / docs-tooling

_No guard markers — docs / process / research ship (no dedicated marker)._

Closes: V2-U3-ledger, V2-U4

---

# SLICE-20260703-report-edit-default-grid

Date: 2026-07-03 · Area: report / ui (lite)

_lite-only, proto untouched._

| Marker | Result |
|---|---|
| LITE_REPORT_DEFAULT_GRID_OK | PASS |

Closes: NEXT_ACTIONS-item-8

---

# PERF-20260703-worker-recycle-chh-probe

Date: 2026-07-03 · Area: perf-probe / docs

_No guard markers — docs / process / research ship (no dedicated marker)._

Closes: —

---

# BUG-20260703-lite-cfss-undo-masters

Date: 2026-07-03 · Area: measure / undo (lite)

_lite-only, proto untouched._

| Marker | Result |
|---|---|
| LITE_UNDO_MASTERS_OK | PASS |

Closes: BUG-20260703-lite-cfss-undo-masters

---

# UX-20260703-quickwins-batch2

Date: 2026-07-03 · Area: ui (lite)

_lite-only, proto untouched._

| Marker | Result |
|---|---|
| LITE_UX_BATCH2_OK | PASS |

Closes: F-4, F-5, F-6, F-9

---

# INV-20260703-layer-linkage

Date: 2026-07-03 · Area: measure+layer (lite)

_lite-only, proto untouched._

| Marker | Result |
|---|---|
| LITE_OBJECT_TUPLES_OK | PASS |
| LITE_B1_ROLE_REROUTE_OK | PASS |
| LITE_B2_SINGLE_ENGINE_OK | PASS |
| LITE_B3_ORPHAN_HEAL_OK | PASS |
| LITE_B4_MOVE_LAYER_OK | PASS |
| LITE_B5_REF_BADGES_OK | PASS |

Closes: H1, H2, H3, M4, M6

---

# UX-20260703-quickwins-batch1

Date: 2026-07-03 · Area: ui (lite)

_lite-only, proto untouched._

| Marker | Result |
|---|---|
| LITE_UX_QUICKWINS_OK | PASS |

Closes: F-1, F-2, F-3, F-7

---

# BUG-20260703-lite-save-wipes-data

Date: 2026-07-03 · Area: save/load (lite)

_lite-only, proto untouched._

| Marker | Result |
|---|---|
| LITE_SAVE_CLICKPATH_OK | PASS |

Closes: BUG-20260703-lite-save-wipes-data

---

# GO-20260703-invariants-streaming-worker-recycle

Date: 2026-07-03 · Area: test-infra + perf (lite)

_lite-only, proto untouched._

| Marker | Result |
|---|---|
| LITE_WORKER_RECYCLE_OK | PASS |

Closes: —

---

# DOCS-20260702-dev-pillars-blueprint

Date: 2026-07-02 · Area: process / docs

_No guard markers — docs / process / research ship (no dedicated marker)._

Closes: —

---

# ACC-20260703-verify-scale-port

Date: 2026-07-03 · Area: measure-ux / accuracy (lite)

_lite-only, proto untouched._

| Marker | Result |
|---|---|
| LITE_VERIFY_SCALE_OK | PASS |

Closes: ACC-20260703-verify-scale-port

---

# AUDIT-20260702-render-followups

Date: 2026-07-03 · Area: render + test-infra (lite)

_lite-only, proto untouched._

| Marker | Result |
|---|---|
| LITE_RENDER_FB_SCAN_OK | PASS |
| LITE_OVERLAY_REG_OK | PASS |

Closes: AUDIT-20260702-render-followups

---

# AUDIT-20260702-s2-fitz-lock

Date: 2026-07-02 · Area: server perf (lite)

_lite-only, proto untouched._

| Marker | Result |
|---|---|
| LITE_CASE_LOCK_OK | PASS |

Closes: AUDIT-20260702-s2-fitz-lock

---

# PERF-20260702-lite-foxit-smoothness

Date: 2026-07-02 · Area: perf (lite)

_lite-only, proto untouched._

| Marker | Result |
|---|---|
| LITE_PAGECACHE_LRU_OK | PASS |
| LITE_LOCAL_OPEN_OK | PASS |
| LITE_WARM_PREFETCH_OK | PASS |
| LITE_THUMB_WARM_OK | PASS |

Closes: —

---

# AUDIT-20260702-infra-bundle

Date: 2026-07-02 · Area: test-infra + server (lite)

_lite-only, proto untouched._

| Marker | Result |
|---|---|
| LITE_RUN_ALL_OK | PASS |
| LITE_EXPORT_ENDPOINTS_OK | PASS |

Closes: AUDIT-20260702-runner-preflight, AUDIT-20260702-export-caps

---

# BUG-20260702-lite-pagerot-registration

Date: 2026-07-02 · Area: measure-geometry / render (lite)

_lite-only, proto untouched._

| Marker | Result |
|---|---|
| LITE_PAGEROT_REG_OK | PASS |

Closes: BUG-20260702-lite-pagerot-registration

---

# BUG-20260702-lite-cfss-summary

Date: 2026-07-02 · Area: measure-geometry (lite)

_lite-only, proto untouched._

| Marker | Result |
|---|---|
| LITE_SUMMARY_CFSS_OK | PASS |

Closes: BUG-20260702-lite-cfss-summary

---

# BUG-20260702-lite-arc-summary

Date: 2026-07-02 · Area: measure-geometry (lite)

_lite-only, proto untouched._

| Marker | Result |
|---|---|
| LITE_SUMMARY_ARC_OK | PASS |

Closes: BUG-20260702-lite-arc-summary

---

<!-- GEN:END -->


---

<!-- INV-20260703-layer-linkage (plan B complete) + UX-batch-1 + save-fix follow-up / UX-REVIEW-20260703 + BUG-20260703-lite-save-wipes-data are the 2 kept in this file -->
<!-- GO-20260703-invariants-streaming-worker-recycle archived to docs/archive/test-history-2026-07-03.md on 2026-07-03 (INV-20260703-layer-linkage plan-B-complete sprint block) -->
<!-- BLOCK-20260703-clear-queue archived to docs/archive/test-history-2026-07-03.md on 2026-07-03 (UX-REVIEW-20260703 + BUG-20260703-lite-save-wipes-data sprint block) -->
<!-- PERF-20260702-lite-foxit-smoothness archived to docs/archive/test-history-2026-07-02.md on 2026-07-03 (GO-20260703-invariants-streaming-worker-recycle session) -->
<!-- BUG-20260702-lite-pagerot-registration archived to docs/archive/test-history-2026-07-02.md on 2026-07-03 (BLOCK-20260703-clear-queue session) -->
<!-- AUDIT-20260702-infra-bundle archived to docs/archive/test-history-2026-07-02.md on 2026-07-02 (PERF-20260702-lite-foxit-smoothness sprint block) -->
<!-- BUG-20260702-lite-cfss-summary + BUG-20260702-lite-arc-summary (2026-07-02) + SLICE report-edit-1 (2026-06-05) + BUG-20260526-lite-stale-pf-folder-cleanup + Centerline Snap arc (2026-05-25) archived to docs/archive/test-history-2026-07-02.md on 2026-07-02 (BUG-20260702-lite-pagerot-registration sprint) -->
<!-- SIM-2 (2026-05-24) and older test results archived to docs/archive/test-history-2026-05-09.md -->
