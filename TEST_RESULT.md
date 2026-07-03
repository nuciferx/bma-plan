# TEST_RESULT.md — Latest Test Result

> Full test history: [docs/archive/test-history-2026-05-09.md](docs/archive/test-history-2026-05-09.md) · [docs/archive/test-history-2026-07-02.md](docs/archive/test-history-2026-07-02.md) · [docs/archive/test-history-2026-07-03.md](docs/archive/test-history-2026-07-03.md)

---

# Latest: INV-20260703-layer-linkage (plan B complete) + UX-batch-1 + save-fix follow-up

Branch: main
Date: 2026-07-03

## Result: PASS (lite tests only — proto NOT TOUCHED)

## No Proto-Test Rationale

Per AGENTS.md §1: proto `py_compile + smoke + full` not re-run because this block made zero changes to `proto/` source files. Lite-only block (plan-B rollout B0-B5 + UX quick-wins batch 1 + save-fix bug-archive follow-up); no forbidden-trigger surface touched in proto. Reference baseline: proto full E2E = 22 _OK markers (`PHASE_CENTERLINE_SNAP_OK` 10/10, last run 2026-05-25, unchanged).

## Commands

```bash
python lite/tests/test_save_clickpath.py
python lite/tests/test_ux_quickwins.py
python lite/tests/test_object_tuples.py
python lite/tests/test_b1_role_reroute.py
python lite/tests/test_b2_single_engine.py
python lite/tests/test_b3_orphan_heal.py
python lite/tests/test_b4_move_layer.py
python lite/tests/test_b5_ref_badges.py
python lite/tests/run_all_tests.py --tier t0
```

## Lite — Results (8 new guard tests, one per commit, verified independently pre-commit)

| Test | Marker | Result |
|---|---|---|
| test_save_clickpath.py | LITE_SAVE_CLICKPATH_OK | PASS (already reported in the prior finalize; carried here for the closed arc's completeness) |
| test_ux_quickwins.py | (UX batch 1 guard) | PASS — F-7 modalOpen keydown guard, F-1 ⇧D Path hotkey, F-2 F-key/Focus fix, F-3 Page Manager menu entry, cheatsheet corrections all verified |
| test_object_tuples.py | LITE_OBJECT_TUPLES_OK | PASS (NEW, B0) — single tuple-stream aggregation engine + I11 oracle `assertEnginesAgree` |
| test_b1_role_reroute.py | (B1 guard) | PASS — report-vars + Summary per-floor gfa/ded/net on tuples via opt-in `{useLive:true}`; default path byte-identical |
| test_b2_single_engine.py | (B2 guard) | PASS — layer-tree Σ + Review Section-3 rows reduce the same tuple stream; oracle (c) proves `byFloorRole` partitions == `byRole`; M6 root-unfiled layers now counted |
| test_b3_orphan_heal.py | (B3 guard) | PASS — `reassignObjectsOfLayer` on `removeLayer` + `sweepOrphanCatIds` load-time heal; H3 closed |
| test_b4_move_layer.py | (B4 guard) | PASS — move-object-to-layer via Properties select + context menu; CFSS master retarget with confirm; H1 closed |
| test_b5_ref_badges.py | (B5 guard) | PASS — report-vars operand dropdown Σ/▸ optgroups; M4 closed |
| run_all_tests.py --tier t0 | — | PASS (measure-math tier, <5s target) |

Every commit was independently verified pre-commit with its own targeted suite plus a `t0` measure-parity sweep. Latest verify (B5): `test_b5_ref_badges.py` + `test_report_vars_ui.py` + `test_report_vars_rollup.py` + `test_b1_role_reroute.py` + `run_all_tests.py --tier t0` — all green. `MEASURE_PARITY_OK` verified green at B4 — the natural checkpoint for a block this heavy on layer/aggregation plumbing — confirming `measure-engine.js` vendored math stayed untouched throughout.

## Plan-B closure — what each finding's guard proves

- **H1 (no move-between-layers UI):** `test_b4_move_layer.py` exercises the Properties-select and context-menu move paths, incl. CFSS master retarget-with-confirm.
- **H2 (dual aggregation engines can disagree):** `test_object_tuples.py`'s I11 oracle + `test_b2_single_engine.py`'s partition-equality check (c) prove structurally, not just empirically, that Summary and Review cannot disagree once both reduce the same tuple stream.
- **H3 (orphaned catId silently drops objects / crashes):** `test_b3_orphan_heal.py` exercises both the `removeLayer` reassignment path and the load-time `sweepOrphanCatIds` heal.
- **M4 (Σ vs ▸ refs visually indistinguishable):** `test_b5_ref_badges.py`.
- **M6 (root-unfiled layers uncounted):** covered by `test_b2_single_engine.py`.

## In-progress work not covered by this test result

UX quick-wins batch 2 (F-4/F-5/F-6/F-9 + seeded-vars red-error display + wizard Next-button gate) is in progress at the time of this write and will get its own `TEST_RESULT.md` update when it lands.

## Reference Baseline (proto, unchanged this block)

```
python3.11 proto/e2e_ui_test.py full → PASS 22 markers (PHASE_CENTERLINE_SNAP_OK 10/10), last run 2026-05-25.
```

---

# Previous: UX-REVIEW-20260703 + BUG-20260703-lite-save-wipes-data — CRASH fix (Ctrl+S wiped all data) + full UI/UX journey review + layer↔measurement invent checkpoint

Branch: main
Date: 2026-07-03

## Result: PASS (lite tests only — proto NOT TOUCHED)

## No Proto-Test Rationale

Per AGENTS.md §1: proto `py_compile + smoke + full` not re-run because this block made zero changes to `proto/` source files. Lite-only block (save-wipe CRASH fix + UX review + invent checkpoint); no forbidden-trigger surface touched in proto. Reference baseline: proto full E2E = 22 _OK markers (`PHASE_CENTERLINE_SNAP_OK` 10/10, last run 2026-05-25, unchanged).

## Commands

```bash
python lite/tests/test_save_clickpath.py
```

## Lite — Results (1 new guard test + 17-file targeted regression, all exit 0)

| Test | Marker | Result |
|---|---|---|
| test_save_clickpath.py | LITE_SAVE_CLICKPATH_OK (NEW) | PASS (4 checks: real `mi-save` click driven via `URL.createObjectURL` interception, polys/calib survive save, duplicate-page content follows identity not position, Apply/merge commit-order also verified. RED pre-fix = exact journey repro: polys 0, calib null) |

Regression: 17/17 targeted at-risk files green — metamorphic suite, page-manager suite, apply-mutations suite, all persist suites, arc-summary parity, CFSS-summary parity, `MEASURE_PARITY_OK` (drift-lock intact — confirms `measure-engine.js` vendored math untouched). The UX review (`UX-20260703-review-findings`) and the layer-linkage invent checkpoint (`INV-20260703-layer-linkage`) are findings-filing / research work, not app-code changes, and carry no dedicated test marker — covered by the same regression context rather than a standalone guard.

## Save-wipe CRASH — the click-path-vs-API-path gap

72 previously-green tests missed this CRASH-tier bug because every existing save test called `buildPageStore()` directly (the API/serialization path) rather than driving the real `mi-save` button click a user actually triggers. `test_save_clickpath.py` closes that specific gap by intercepting `URL.createObjectURL` to capture the blob the real click handler produces. This is recorded here as a testing-methodology lesson, not yet promoted into `lite/tests/INVARIANTS.md` (that file was explicitly out of scope for this docs-batching write while two `lite-builder` subagents are actively editing `lite/`).

## In-progress work not covered by this test result

B0 (tuple-stream aggregation engine + new `I11` invariant oracle) and UX quick-wins batch 1 (F-7/F-1/F-2/F-3 + cheatsheet accuracy pass) are being built right now by two `lite-builder` subagents in parallel. No test results are recorded for either here — they are unshipped as of this write and will get their own `TEST_RESULT.md` update when they land.

## Reference Baseline (proto, unchanged this block)

```
python3.11 proto/e2e_ui_test.py full → PASS 22 markers (PHASE_CENTERLINE_SNAP_OK 10/10), last run 2026-05-25.
```

---

<!-- INV-20260703-layer-linkage (plan B complete) + UX-batch-1 + save-fix follow-up / UX-REVIEW-20260703 + BUG-20260703-lite-save-wipes-data are the 2 kept in this file -->
<!-- GO-20260703-invariants-streaming-worker-recycle archived to docs/archive/test-history-2026-07-03.md on 2026-07-03 (INV-20260703-layer-linkage plan-B-complete sprint block) -->
<!-- BLOCK-20260703-clear-queue archived to docs/archive/test-history-2026-07-03.md on 2026-07-03 (UX-REVIEW-20260703 + BUG-20260703-lite-save-wipes-data sprint block) -->
<!-- PERF-20260702-lite-foxit-smoothness archived to docs/archive/test-history-2026-07-02.md on 2026-07-03 (GO-20260703-invariants-streaming-worker-recycle session) -->
<!-- BUG-20260702-lite-pagerot-registration archived to docs/archive/test-history-2026-07-02.md on 2026-07-03 (BLOCK-20260703-clear-queue session) -->
<!-- AUDIT-20260702-infra-bundle archived to docs/archive/test-history-2026-07-02.md on 2026-07-02 (PERF-20260702-lite-foxit-smoothness sprint block) -->
<!-- BUG-20260702-lite-cfss-summary + BUG-20260702-lite-arc-summary (2026-07-02) + SLICE report-edit-1 (2026-06-05) + BUG-20260526-lite-stale-pf-folder-cleanup + Centerline Snap arc (2026-05-25) archived to docs/archive/test-history-2026-07-02.md on 2026-07-02 (BUG-20260702-lite-pagerot-registration sprint) -->
<!-- SIM-2 (2026-05-24) and older test results archived to docs/archive/test-history-2026-05-09.md -->
