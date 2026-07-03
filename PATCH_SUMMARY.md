# PATCH_SUMMARY.md — Latest Sprint

> Full patch history: [docs/archive/patch-history-2026-05-09.md](docs/archive/patch-history-2026-05-09.md) · [docs/archive/patch-history-2026-07-02.md](docs/archive/patch-history-2026-07-02.md) · [docs/archive/patch-history-2026-07-03.md](docs/archive/patch-history-2026-07-03.md)

---

# Latest: UX-REVIEW-20260703 + BUG-20260703-lite-save-wipes-data — CRASH fix (Ctrl+S wiped all data) + full UI/UX journey review + layer↔measurement invent checkpoint

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

# Previous: GO-20260703-invariants-streaming-worker-recycle — V2-U1 invariant registry + Range-streaming spike (NOGO→RESHAPE) + worker-recycle build

Branch: main

Date: 2026-07-03

## Outcome: PASS — Continuation of the same-day "GO" loop block, resumed right after `BLOCK-20260703-clear-queue` closed and the Range-streaming human checkpoint was cleared. (1) V2-U1 invariant registry (`6d6e39b`): NEW `lite/tests/INVARIANTS.md` (10 invariants I1–I10 mapped to guard test + tier + mandatory SCOPE questions + new-object-kind fixture rule) + reconciled 16 stale `PHASE_INDEX.md` rows with real `fixed_commit` + closed the `ptToScreen` parity-fixture card with rationale (registered as invariant I7). (2) Range-streaming SPIKE (`9466fe4`+`f8c2981`), GO received: 5-step spike run for real on RAMA4 19MB + real CHH 95MB — streaming cut CHH RSS only 10% against a ≥50% GO bar (FAILS); pdf.js worker-heap bug #10730 CONFIRMED on 4.0.379 (the real memory ceiling is the WORKER heap, not the doc heap). VERDICT: NOGO on streaming-as-memory-fix, RESHAPE to worker-recycle — the spike prevented a doomed build sprint. (3) worker-recycle BUILT (`d52ddbb`), the RESHAPE: explicit `PDFWorker` ownership + cheap `_docSource` re-open handle + `recycleDocWorker()` with guards + transparent lazy reinit + hidden/idle/manual triggers; `LITE_WORKER_RECYCLE_OK` 7/7 (incl. zero-refetch-via-blob, heap-not-worse −0.8%); production RSS re-probe on CHH queued as honest follow-up. (4) Streaming-as-bandwidth card DEFERRED-until-remote-deployment (localhost bytes are free on the current desktop-only product). Lite suite now 72 files; `MEASURE_PARITY_OK` green throughout. Zero `proto/` edits.

## Summary

Continuation of the same-day "GO" loop block, resumed right after `BLOCK-20260703-clear-queue` closed and the Range-streaming human checkpoint was cleared. **(1) V2-U1 invariant registry (`6d6e39b`):** NEW `lite/tests/INVARIANTS.md` — canonical registry of 10 invariants (I1–I10), each mapped to its guard test + tier, plus the two mandatory SCOPE questions ("which invariants does this feature touch" / "does it create a new object kind") — the prevention mechanism `docs/process/DEVELOPMENT_V2_BLUEPRINT.md` U1 called for, born directly from the arc-summary/CFSS-summary postmortem. New-kind rule: fixtures added to I2/I4/I5 in the same sprint, no exceptions. Same commit reconciles 16 stale `PHASE_INDEX.md` rows (`lpm-1..9`, `cfss-guard`, `EVOLT-1..5`, `INV-2026-05-25-CFSS`) that claimed `queued` but were long since shipped — each now carries its real `fixed_commit`. The `ptToScreen`/`screenToPt` parity-fixture card is closed with a rationale instead of code: the behavioral lock already exists as invariant I7 (`LITE_PAGEROT_REG_OK`; runtime routes through the parity-tested `pdfToC`/`cToPdf` kernel since `9f4b298`). **(2) Range-streaming SPIKE (`9466fe4`+`f8c2981`), GO received via `/loop`:** the 5-step spike from `docs/invent/lite-range-streaming.md` was executed for real in `lite/sandbox/invent-range-streaming/` against RAMA4 (19 MB) and the real CHH binder (95 MB). Results: both customer PDFs are NON-linearized yet stream fine (20% bytes fetched — linearization concern moot); Starlette's `/raw` already serves `206 Partial Content`+`Content-Range` with zero backend work; streaming cut CHH's RSS only 10% (1675→1503 MB) against a ≥50% GO bar — **FAILS**; pdf.js worker-heap bug #10730 CONFIRMED on the pinned 4.0.379 build (`destroy()` frees the main doc heap 409→98 MB but the worker heap survives — the real ~1.5 GB ceiling); `PDFDataRangeTransport` over `Blob.slice` works mechanically but delivers no memory win. **VERDICT: NOGO on streaming-as-memory-fix, RESHAPE to worker-recycle** — the spike prevented a doomed build sprint. **(3) worker-recycle BUILT (`d52ddbb`), the RESHAPE:** `lite/static/js/page-renderer.js` gains explicit `PDFWorker` ownership (`_docWorker`, passed into `getDocument` from both `openLocal` and `/raw` paths) + a cheap `_docSource` re-open handle (retained local `File`/`Blob` = zero-network reinit, or `caseId` = one `/raw` refetch) + `recycleDocWorker()` (guards: recycle-in-progress / render-in-flight=SKIP / no source; preserves `pageDims`/`pageRot`/`_scanned`) + transparent lazy `_reinitDoc` on next `loadPage` + triggers (tab hidden ≥60s; idle ≥5min AND `pageCount>20`; manual `PageRenderer.recycleNow`). `_resetCache()` now also destroys the explicit worker on new-upload, closing a latent per-upload worker leak. `page-renderer.js` 790/1000 lines; `ui-lite.html` +1 call-site line (1170/1200). Built by `lite-builder`, independently verified. NEW `lite/tests/test_worker_recycle.py` (`LITE_WORKER_RECYCLE_OK`, 7 checks incl. zero-refetch-via-blob and heap-not-worse −0.8%). Honest scope: the full CHH RSS −50% acceptance bar was measured in the spike's pattern, not re-verified against this specific production build — a production re-probe is recorded as queued follow-up measurement, not assumed. Regression 6/6 + `--tier t0` green. **(4) Streaming-as-bandwidth card DEFERRED-until-remote-deployment** with a recorded rationale (เสา 1): all `/raw` byte transfer is localhost on the current desktop-only product (91 MB `/raw` = 498 ms measured), so the spike's 80% byte-count reduction has no user-facing benefit until a remote deployment target exists. **Suite validation:** lite test suite now 72 files; `MEASURE_PARITY_OK` green throughout every piece of this block.

## Files Changed

| File | Change |
|---|---|
| `lite/tests/INVARIANTS.md` | NEW (1) — 10 invariants I1–I10 mapped to guard test + tier, 2 mandatory SCOPE questions, new-object-kind fixture rule |
| `docs/status/PHASE_INDEX.md` | (1)+(2)+(4) — 16 stale rows reconciled with real `fixed_commit`; `ptToScreen` parity card closed with rationale (I7); streaming-spike verdict + worker-recycle GO + bandwidth-deferral recorded on the perf card — via the block's own commits, not this docs-batching write |
| `docs/invent/lite-range-streaming.md` | (2) — updated with the 5-step spike's real results, NOGO-as-memory-fix verdict, 2 proposed follow-on cards |
| `lite/sandbox/invent-range-streaming/` | NEW (2) — spike scripts + raw results (`s1_linearize.py`, `s2_range.py`, `spike.html`, `spike_run.py`, `results.json`, `results.md`) |
| `lite/static/js/page-renderer.js` | (3) — worker-recycle: `_docWorker` explicit ownership, `_docSource` re-open handle, `recycleDocWorker()` with guards, transparent lazy `_reinitDoc`, hidden/idle/manual triggers, `_resetCache()` destroys worker |
| `lite/ui-lite.html` | (3) — +1 line, single worker-recycle call-site (1170/1200 cap) |
| `lite/tests/test_worker_recycle.py` | NEW (3) — `LITE_WORKER_RECYCLE_OK`, 7 checks incl. zero-refetch-via-blob, heap-not-worse (−0.8%) |

## Source Files NOT Touched (Forbidden Surfaces)

- `proto/server.py` — NOT TOUCHED (lite-only block; zero proto/ edits)
- `polyAreaM2`, `polyMetrics`, `polySelfIntersects` — UNCHANGED
- `pdfToC`, `cToPdf`, `RS`, scale math — UNCHANGED
- `buildSnapIndex`, `snap` engine — UNCHANGED
- `lite/static/js/measure-engine.js` drift-locked vendored math — UNCHANGED
- `.bmaplan` schema version stays 1; no schema fields touched this block (invariants doc, spike research, worker lifecycle management — no persisted-state change)
- Range-streaming spike ran isolated in `lite/sandbox/`, not against the live page-renderer buffer-ownership contract, until the RESHAPE was independently built + guarded by its own test

## Tests Run

```
python lite/tests/test_worker_recycle.py       → LITE_WORKER_RECYCLE_OK   PASS (NEW, 7/7 checks)
python lite/tests/run_all_tests.py --tier t0   → PASS (measure-math tier, <5s target)
python lite/tests/test_measure_parity.py       → MEASURE_PARITY_OK        PASS (drift-lock intact)
```

Regression 6/6 targeted at-risk files green + `run_all_tests.py --tier t0` green. `MEASURE_PARITY_OK` green throughout — zero vendored-math touch across all 4 pieces of this block. Lite suite now 72 test files. Proto E2E n/a (lite-only block; zero `proto/` edits).

## Phase 1 Scope Check

- ✅ `polyAreaM2` / `polyMetrics` / `polySelfIntersects` unchanged
- ✅ `pdfToC` / `cToPdf` / `RS` / scale math unchanged
- ✅ `proto/server.py` core endpoints unchanged (proto NOT TOUCHED — lite-only block)
- ✅ `.bmaplan` schema version stays 1; no fields touched this block
- ✅ No legal / OCR / AI / Rule Engine / FAR-OSR pass-fail
- ✅ No forbidden surface touched; spike isolated in `lite/sandbox/`, RESHAPE independently built + guarded
- ✅ `lite/ui-lite.html` stays under 1200-line cap (1170/1200); `page-renderer.js` stays under 1000-line cap (790/1000)

---

<!-- UX-REVIEW-20260703 + BUG-20260703-lite-save-wipes-data / GO-20260703-invariants-streaming-worker-recycle are the 2 kept in this file -->
<!-- BLOCK-20260703-clear-queue archived to docs/archive/patch-history-2026-07-03.md on 2026-07-03 (UX-REVIEW-20260703 + BUG-20260703-lite-save-wipes-data sprint block) -->
<!-- PERF-20260702-lite-foxit-smoothness archived to docs/archive/patch-history-2026-07-02.md on 2026-07-03 (GO-20260703-invariants-streaming-worker-recycle sprint block) -->
<!-- BUG-20260702-lite-pagerot-registration archived to docs/archive/patch-history-2026-07-02.md on 2026-07-03 (BLOCK-20260703-clear-queue session) -->
<!-- AUDIT-20260702-infra-bundle archived to docs/archive/patch-history-2026-07-02.md on 2026-07-02 (PERF-20260702-lite-foxit-smoothness sprint block) -->
<!-- BUG-20260702-lite-cfss-summary + BUG-20260702-lite-arc-summary (2026-07-02) + SLICE report-edit-1 (2026-06-05) + BUG-20260526-lite-stale-pf-folder-cleanup + Centerline Snap arc (2026-05-25) archived to docs/archive/patch-history-2026-07-02.md on 2026-07-02 (BUG-20260702-lite-pagerot-registration sprint) -->
<!-- SIM-2 (2026-05-24) and older entries archived to docs/archive/patch-history-2026-05-09.md -->
