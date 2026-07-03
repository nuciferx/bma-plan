# patch-history-2026-07-03.md — Archived Patch Summaries

> Archived from root PATCH_SUMMARY.md on 2026-07-03 (BLOCK-20260703-clear-queue archived during the UX-REVIEW-20260703 + BUG-20260703-lite-save-wipes-data sprint block; GO-20260703-invariants-streaming-worker-recycle archived during the INV-20260703-layer-linkage plan-B-complete sprint block, both to keep root at Latest + 1 Previous).

---

# BLOCK-20260703-clear-queue — 5-ship "ทำทั้งหมด" session (fitz lock, render fallback+scan, V2 tiers/overlay-proof/streaming-research, Verify-Scale port, process docs)

Branch: main

Date: 2026-07-03

## Outcome: PASS — Five same-session ships clearing the entire remaining queue per user directive "ทำทั้งหมด" (2026-07-02 night → 2026-07-03). Ship 1 `AUDIT-20260702-s2-fitz-lock` (`d0a5dde`): per-case `threading.Lock` serializing all `fitz.Document` access, incl. moving `/export-pdf-overlay` render off the event loop; hammer-test guard `LITE_CASE_LOCK_OK`, zero 5xx across 96 concurrent requests. Ship 2 render-followups a+c (`aec375b`): raster fallback when PDF.js unavailable + scanned-page detection with capped re-render scale; `LITE_RENDER_FB_SCAN_OK` 6/6. Ship 3 (`13054b6`): tiered test runner (V2 blueprint U2), NEW pixel-level `LITE_OVERLAY_REG_OK` registration proof (max offset 0.50 px), and Range-streaming research HALTED at human checkpoint per Pack H. Ship 4 `ACC-20260703-verify-scale-port` (`bea2119`): Verify-Scale ported from proto, closing the last known accuracy gap vs. Foxit; `LITE_VERIFY_SCALE_OK` 7/7. Ship 5 (`16e6495`+`b676652`): `DEVELOPMENT_PILLARS.md` + `DEVELOPMENT_V2_BLUEPRINT.md` process docs. Full lite suite validated at 70/70 files green (grew 60→70 across the two days); `MEASURE_PARITY_OK` green throughout. Zero `proto/` edits. **Ship 3's Range-streaming checkpoint was cleared and resolved by `GO-20260703-invariants-streaming-worker-recycle`.**

## Summary

Five same-session ships, run back-to-back overnight under a user directive to clear the entire remaining queue in one sitting. **Ship 1 — `AUDIT-20260702-s2-fitz-lock` (`d0a5dde`):** a per-case `threading.Lock` (`_case_lock`) in `lite/server_lite.py` now serializes all `fitz.Document` access — `/page` + `/thumb` (double-checked cache), `/pageinfo`, and the whole `/export-pdf-overlay` render path (now also moved off the event loop via `run_in_threadpool` around a new `_render_overlay` helper, completing the S2 threadpool goal deferred by `AUDIT-20260702-infra-bundle`), plus copy/close/swap critical sections of apply-page-mutations + merge-pages. Urgency raised by `PERF-20260702-lite-foxit-smoothness` Sprint 4's thumbnail warm making concurrent `/thumb`+`/page` traffic routine. NEW `lite/tests/test_case_lock.py` (`LITE_CASE_LOCK_OK`): 96-request 8-thread hammer + mid-flight doc-swap mutation + concurrent overlay export, zero 5xx — an honest hardening-hammer test, not a deterministic RED-before-fix proof (native races are probabilistic). Regression 9/9. **Ship 2 — render-followups (a)+(c) (`aec375b`):** (a) raster fallback — PDF.js unavailable no longer blanks the canvas; `loadPage` falls back to server JPEG (`/pageinfo`+`/page?rot`) drawn through the same view transform, with an `instanceof` guard keeping legacy shims safe; measurement stays fully functional. (c) scanned-page detection — an operator-list heuristic (free, post-render) flags image-only pages; re-render scale capped at `RS*4` (~432 DPI) with transform compensation so registration is bit-identical, saving only wasted re-raster CPU; one-time Thai hint. NEW `lite/tests/test_render_fallback_scanned.py` (`LITE_RENDER_FB_SCAN_OK`, 6 checks); 2 false alarms traced to the test harness itself and fixed there. Regression 8/8. **Ship 3 — V2 tiers + overlay proof + streaming research (`13054b6`):** (i) `run_all_tests.py --tier t0/t1/t2` (V2 blueprint U2) — `t0` measure-math-via-Node runs in 1.26 s, hitting the <5 s target; (ii) NEW `lite/tests/test_overlay_registration.py` (`LITE_OVERLAY_REG_OK`), built by a delegated agent and independently re-run — the first PIXEL-level raster↔overlay registration proof (max offset 0.50 px at zoom×2, 0.33 px at fit, 0.40 px at `pageRot=90°`, tolerance 4), the evidence the 2026-05-28 render-quality spike never produced; (iii) `docs/invent/lite-range-streaming.md` — Range-streaming research (`bma-researcher`): `PRIOR_ART_PARTIAL` verdict, key risks (PDF.js worker-heap bug #10730, untested `Blob.slice` transport, unknown customer-PDF linearization, `/raw` may already support Range), 5-step spike design + GO/NOGO criteria — **HALTED at the human checkpoint per Pack H, no code shipped for this piece by design.** **Ship 4 — `ACC-20260703-verify-scale-port` (`bea2119`):** Verify-Scale ported from proto's `INV-2026-05-20-001` — the single remaining accuracy gap vs. Foxit identified by the 2026-07-02 comparison. NEW `lite/static/js/verify-scale.js` (225 lines): 2-point verify capture reusing the calibration pipeline, %deviation banding (green/yellow/red), accept/recalibrate/average actions, additive `PS[pg].scale.verifyResult` riding the existing `calibScale` serialization. `lite/ui-lite.html` +3 net lines (menu item, `state.verifyMode` routing, `Shift+S`); `menu-flyout.js` +2 lines. Built by `lite-builder` subagent, independently verified. NEW `lite/tests/test_verify_scale.py` (`LITE_VERIFY_SCALE_OK`, 7 checks incl. save/load round-trip + average-re-derives-areas). **Ship 5 — process docs (`16e6495`+`b676652`):** `docs/process/DEVELOPMENT_PILLARS.md` (6-pillar doctrine + incident evidence + halt conditions) and `docs/process/DEVELOPMENT_V2_BLUEPRINT.md` (6 weaknesses → 6 structural upgrades + migration order + success bar); U2 migration step partially landed via Ship 3. **Final validation:** full lite suite — 70 files, 70/70 green — run in chunks (17+27+26) after background runs kept getting killed; `artifacts/run_all_tests_20260703_final.log` covers the first 17; `MEASURE_PARITY_OK` green throughout every ship; suite grew 60→70 files across the two days.

## Files Changed

| File | Change |
|---|---|
| `lite/server_lite.py` | Ship 1 — `_case_lock` wraps all `fitz.Document` access incl. `/export-pdf-overlay` via new `_render_overlay` + `run_in_threadpool` |
| `lite/tests/test_case_lock.py` | NEW (Ship 1) — `LITE_CASE_LOCK_OK`, 96-request 8-thread hammer, zero 5xx |
| `lite/ui-lite.html` | Ship 2 — `loadPage()` raster fallback to server JPEG; Ship 4 — +3 net lines (Verify Scale menu item, verify-mode routing, `Shift+S`) |
| render module (page-renderer) | Ship 2 — scanned-page heuristic + `RS*4` capped re-render scale + transform compensation |
| `lite/tests/test_render_fallback_scanned.py` | NEW (Ship 2) — `LITE_RENDER_FB_SCAN_OK`, 6 checks |
| `lite/tests/run_all_tests.py` | Ship 3 — `--tier t0/t1/t2` flag (V2 blueprint U2) |
| `lite/tests/test_overlay_registration.py` | NEW (Ship 3) — `LITE_OVERLAY_REG_OK`, pixel-level registration proof |
| `docs/invent/lite-range-streaming.md` | NEW (Ship 3) — Range-streaming research, HALTED at human checkpoint |
| `lite/static/js/verify-scale.js` | NEW (Ship 4) — 225 lines, ported from proto `INV-2026-05-20-001` |
| `lite/static/js/menu-flyout.js` | Ship 4 — +2 lines, picks up new menu item |
| `lite/tests/test_verify_scale.py` | NEW (Ship 4) — `LITE_VERIFY_SCALE_OK`, 7 checks |
| `docs/process/DEVELOPMENT_PILLARS.md` | NEW (Ship 5) — 6-pillar doctrine |
| `docs/process/DEVELOPMENT_V2_BLUEPRINT.md` | NEW (Ship 5) — 6 weaknesses → 6 upgrades + migration order |

## Source Files NOT Touched (Forbidden Surfaces)

- `proto/server.py` — NOT TOUCHED (lite-only block; zero proto/ edits)
- `polyAreaM2`, `polyMetrics`, `polySelfIntersects` — UNCHANGED
- `pdfToC`, `cToPdf`, `RS`, scale math — UNCHANGED
- `buildSnapIndex`, `snap` engine — UNCHANGED
- `lite/static/js/measure-engine.js` drift-locked vendored math — UNCHANGED across all 5 ships
- `.bmaplan` schema version stays 1; only additive field this block is `PS[pg].scale.verifyResult` (Ship 4, mirrors proto's already-shipped equivalent)
- `docs/status/PHASE_INDEX.md` / `lite/tests/bug-archive.jsonl` — deliberately NOT touched by this docs-batching write

## Tests Run

```
python lite/tests/test_case_lock.py               → LITE_CASE_LOCK_OK          PASS (NEW; hardening hammer, not deterministic RED proof)
python lite/tests/test_render_fallback_scanned.py → LITE_RENDER_FB_SCAN_OK     PASS (NEW, 6 checks)
python lite/tests/run_all_tests.py --tier t0       → t0 in 1.26s (<5s target)  PASS
python lite/tests/test_overlay_registration.py    → LITE_OVERLAY_REG_OK       PASS (NEW, pixel-level proof)
python lite/tests/test_verify_scale.py            → LITE_VERIFY_SCALE_OK      PASS (NEW, 7 checks)
python lite/tests/run_all_tests.py                → 70/70 files green (chunked: 17 + 27 + 26)
```

`MEASURE_PARITY_OK` green throughout every ship — zero vendored-math touch. Lite suite grew 60→70 files across 2026-07-02 → 2026-07-03. Proto E2E n/a (lite-only block; zero `proto/` edits).

## Phase 1 Scope Check

- ✅ `polyAreaM2` / `polyMetrics` / `polySelfIntersects` unchanged
- ✅ `pdfToC` / `cToPdf` / `RS` / scale math unchanged
- ✅ `proto/server.py` core endpoints unchanged (proto NOT TOUCHED — lite-only block)
- ✅ `.bmaplan` schema version stays 1; only additive field is Ship 4's `verifyResult`
- ✅ No legal / OCR / AI / Rule Engine / FAR-OSR pass-fail
- ✅ No forbidden surface touched — Ship 3's Range-streaming (the one piece that would touch the page-renderer's buffer-ownership contract) correctly HALTED at the human checkpoint rather than shipped
- ✅ `lite/ui-lite.html` stays under 1200-line cap (1170/1200 after Ship 4)

---

# GO-20260703-invariants-streaming-worker-recycle — V2-U1 invariant registry + Range-streaming spike (NOGO→RESHAPE) + worker-recycle build

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
