# Test History — 2026-08

Archived entries superseded out of `TEST_RESULT.md`'s Latest + 1 Previous window.

---

# PM-META + PM-ID

Date: 2026-08-10 · Area: page-manager / layer identity (lite)

_lite-only, proto untouched. No forbidden surface (measure-engine/pdfToC/RS/snap untouched) — no proto E2E run._

Both guard tests proven RED before the fix, then GREEN after — a genuine regression-proof cycle, not just a green run:

- **E21 (`LITE_PM_META_LIVE_OK`, PM-META):** before the fix, `_pmCommit` reverted page meta (tags/rotations/floor numbers/exclusions) to the open-time snapshot on every Save/Apply/Merge — proven by asserting a tag set post-open survives a commit cycle (FAILED pre-fix, PASSED post-fix with `_liveMetaFor` + `projectToGlobals(livePS, liveMeta)`).
- **E22 (`LITE_PM_ID_SEED_OK`, PM-ID):** before the fix, `adoptId()` did not advance the `_idc` mint counter past adopted `pg<N>` ids on load/seed — proven by reopening a `.bmaplan` with a duplicate page and asserting no id collision on next mint (FAILED pre-fix, PASSED post-fix).

| Marker / Suite | Result |
|---|---|
| `page_manager_eval.js` E21 `LITE_PM_META_LIVE_OK` | FAIL (pre-fix) → PASS (post-fix) |
| `page_manager_eval.js` E22 `LITE_PM_ID_SEED_OK` | FAIL (pre-fix) → PASS (post-fix) |
| `lite/tests/test_page_manager.py` (`LITE_PAGE_MANAGER_OK`) | PASS (23/23) |
| `scripts/check_executable_truth.py` (`TRUTH_CHECK_OK`) | PASS (5/5) |
| `lite/tests/run_all_tests.py` (full suite) | 101/102 in 15.9 min — 1 pre-existing failure, see below |

**Pre-existing failure (not caused by this sprint):** `test_closing_dup_strip.py` failed with `LITE_CLOSING_DUP_STRIP_FAIL` ("5 poly objects on page 26, got 244.17"). Verified PRE-EXISTING by re-running the same test against the unmodified tree via `git stash` — the failure reproduces identically with none of this sprint's changes applied. Not a regression from PM-META/PM-ID; filed as a known issue needing its own investigation, not blocking this ship.

**Baseline comparison:** prior full-suite run (2026-07-04 full-day block, archived) was 97/98 green with the same single pre-existing failure category (`test_closing_dup_strip.py`) already present at that time — this sprint's 101/102 confirms the suite has otherwise grown (98→102 files) with zero new failures introduced.

Commits: `1107e2e`, `d0b3881`, `878effd`. Closes: PM-META (I5 second half of BUG-20260703), PM-ID (I9)
