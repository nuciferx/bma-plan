# Patch History — 2026-08

Archived entries superseded out of `PATCH_SUMMARY.md`'s Latest + 1 Previous window.

---

# PM-META + PM-ID — page-meta/globals live-sync fix + duplicate-id mint-counter fix (lite)

Branch: main

Date: 2026-08-10

## Outcome: PASS — 2 root-cause bugs fixed underneath the user symptom "เลเยอร์มั่ว การจัดการหน้ามั่ว"

## Summary

PM-META (I5, second half of BUG-20260703): `_pmCommit` called `projectToGlobals(PS)` with live content but page meta (tags/rotations/floor numbers/exclusions) still came from `meta_by_id` snapshots taken at open-time — every Save/Apply/Merge silently reverted all meta edits made since open, then `reseedActivePageFolders()` re-derived layer folders from the reverted data, producing the visible "layers scrambled" symptom. Fixed with a new `PageModel.prototype._liveMetaFor` (mirror of `_liveContentFor`) so `projectToGlobals(livePS, liveMeta)` resolves and refreshes meta from live state; `ui-lite.html:424` now passes live meta dicts (in-place edit, net 0 lines). PM-ID (I9): the `_idc` mint counter reset to 0 each session but `load()`/`seedFromGlobals()` adopted existing `pageIdentities` without advancing it, so reopening a `.bmaplan` with a duplicate page could re-mint `pg0` and overwrite page 1's data. Fixed by advancing `_idc` past adopted `pg<N>` ids at both adopt sites. Both proven RED before fix, GREEN after (new markers `LITE_PM_META_LIVE_OK`, `LITE_PM_ID_SEED_OK`).

## Files Changed

| File | Change |
|---|---|
| `lite/static/js/page-manager.js` | 533→565 lines: `_liveMetaFor` + `projectToGlobals(livePS, liveMeta)`, `adoptId()` advances `_idc` past adopted ids |
| `lite/ui-lite.html` | net 0 lines — line 424 passes live meta dicts into `_pmCommit` |
| `lite/tests/page_manager_eval.js` | 743→821 lines — new E21 (`LITE_PM_META_LIVE_OK`), E22 (`LITE_PM_ID_SEED_OK`) |
| `docs/status/PHASE_INDEX.md` | −2 rows (2 shipped items reconciled out) |
| `docs/status/ROADMAP_DONE.md` | +2 rows |
| `sprints/completed/2026-08-10-page-meta-identity/RUN_PAGE_META_IDENTITY.md` | sprint card / work order (Opus-authored after 35-module review) |

## Source Files NOT Touched (Forbidden Surfaces)

- `proto/server.py` — untouched, lite-only sprint
- `polyAreaM2`, `polyMetrics`, `polySelfIntersects` — untouched
- `pdfToC`, `cToPdf`, `RS`, scale math, snap engine — untouched
- `.bmaplan` schema version stays 1; `liveMeta` is an in-memory arg only, not a persisted field

## Tests Run

Guard tests proven RED before fix then GREEN after — E21 `LITE_PM_META_LIVE_OK`, E22 `LITE_PM_ID_SEED_OK`. `python lite/tests/test_page_manager.py` → 23/23 `LITE_PAGE_MANAGER_OK`. `python scripts/check_executable_truth.py` → `TRUTH_CHECK_OK` (5/5). Full suite `python lite/tests/run_all_tests.py` → 101/102 in 15.9 min; sole failure `test_closing_dup_strip.py` (`LITE_CLOSING_DUP_STRIP_FAIL`, "5 poly objects on page 26, got 244.17") confirmed PRE-EXISTING via git-stash re-run on the unmodified tree — not caused by this sprint; filed as a known issue for its own investigation.

## Phase 1 Scope Check

- ✅ No legal checker / OCR / AI / rule engine / FAR-OSR-setback touched
- ✅ proto/ untouched, lite-only
- ✅ No forbidden surface touched
- ✅ `.bmaplan` schema additive-only (no field added — in-memory arg only)

**Commits:** `1107e2e` (sprint card work order), `d0b3881` (docs: reconcile 2 shipped rows PHASE_INDEX → ROADMAP_DONE, unblocking the roadmap-recon preflight gate — TRUTH_CHECK_OK 5/5 restored), `878effd` (fix(lite): PM-META + PM-ID)

**Closes:** PM-META (I5 second half of BUG-20260703), PM-ID (I9)
