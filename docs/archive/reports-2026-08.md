# Reports History — 2026-08

Archived entries superseded out of `FINAL_REPORT_FOR_CHATGPT.md`'s Latest + 1 Previous window.

---

# PM-META + PM-ID — PASS

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
