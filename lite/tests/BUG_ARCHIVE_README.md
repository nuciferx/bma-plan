# Bug Archive — the evolutionary loop's memory

`bug-archive.jsonl` is the feedback memory that makes the test+develop loop **self-improving** (see `docs/design/EVOLUTIONARY_TEST_LOOP.md`, pillar 4). One JSON object per line, one confirmed bug each.

## The contract
Every future test/hunt run **seeds from this file first** — "you have already missed these before; verify they are still guarded." This is the prompt-side analog of an evolutionary archive (Darwin-Gödel Machine): the loop never re-ships a bug class it has already learned. Because Claude weights are frozen, the "learning" lives here, not in the model.

## Fields
| field | meaning |
|---|---|
| `id` | stable bug id (e.g. `BUG-20260530-lpm-3`) |
| `date` | found date (absolute) |
| `severity` | CRASH / BROKEN / FRICTION / COSMETIC |
| `surface` | file + region where it lived |
| `summary` | one-line what-was-wrong |
| `repro` | how to reproduce |
| `guard_test` | the test that now PERMANENTLY guards it (green guard = the bug can't silently return) |
| `fixed_commit` | commit that fixed it (`null`/`pending` if not yet) |
| `status` | `fixed` or `open` |

## How to use
- **Before a release / hunt:** run every `guard_test` listed here. All must be green.
- **`status:open` items are the next fix targets.** Currently open: **none** — the entire post-LPM hunt is closed + guarded (2026-05-31). Last three fixed: `lpm-7` (unify Apply to `simulateFlush` — single tested flush path, `10be96c`, guard `test_pm_apply_flush_unified.py`), `lpm-8` (lazy-load thumbnails, no open burst, `b3e4fd9`, guard `test_pm_thumb_lazy.py`), `lpm-9` (pm-overlay hotkey-leak + Esc double-fire, `3611e31`, guard `test_pm_modal_hotkeys.py`). (`lpm-4` undo-desync was the last BROKEN — `7d6f230`, guard `MR-undo-consistency`.)
- **When you confirm a NEW bug:** append a line with `status:"open"`; the moment you write its guard test, fill `guard_test`; on fix set `fixed_commit`+`status:"fixed"`. A bug is not "done" until it has a green guard_test — that is what stops regression.

## Seeded history (2026-05-30 full-program hunt)
10 bugs from the post-INV-2026-05-29-LPM hunt. **10 fixed — ALL closed (2026-05-31)** (lpm-1..9 + cfss-guard) with permanent guards — metamorphic MRs (`MR-save-roundtrip`/`MR-save-pending`/`MR-render-source`/`MR-dirty`/`MR-undo-consistency`), server `test_apply_page_mutations.py` T1–T7, EVOLT-3 cap-check, `test_pm_modal_hotkeys.py` (lpm-9), `test_pm_thumb_lazy.py` (lpm-8), `test_pm_apply_flush_unified.py` (lpm-7). **0 open.** The 42-green unit suite missed all 10 — which is exactly why this archive + the metamorphic/PBT layer (`test_metamorphic_pages.py`, `test_pbt_measure.py`) now exist. Every BROKEN/data-loss bug from the hunt is now closed + guarded.

## Later finds
- **`BUG-20260604-pdfjs-cdn`** (BROKEN, fixed `c5a2a5e`) — lite's sole renderer (`page-renderer.js _loadPdfjsLib`) imported pdfjs from `cdn.jsdelivr.net` only, so offline / proxy-blocked CDN meant **no page rendered at all** ("Failed to fetch dynamically imported module"). Because `draw()` bails at `if(!PageRenderer.ready())return`, a failed page render also hides every measured object on that page (the "no obj on page 26" report). Fix: vendor pdfjs 4.0.379 into `lite/static/js/vendor/pdfjs/`, import same-origin first, CDN fallback. Guard: `test_pdfjs_offline.py` (`LITE_PDFJS_OFFLINE_OK`) — blocks jsdelivr, asserts render from local vendor.
- **`BUG-20260604-poly-closing-dup`** (BROKEN, fixed `acbf048`) — area polygons stored ring-style (first vertex duplicated as last) trip the vendored `polySelfIntersects` wrap-around guard → `polyMetrics.area=null` → areas vanish from **every** report (summary / XLSX / web report / reportVars). Vendored math is forbidden, so fix normalizes lite-side: `stripClosingDup` in `loadProto`. Verified on user fixture: page-26 areas 0 → 241.06 m². Guard: `test_closing_dup_strip.py` (`LITE_CLOSING_DUP_STRIP_OK`).
- **`BUG-20260604-reportvars-role-rollup`** (BROKEN, fixed `0e45d6a`) — reportVars aggregate keyed by layer-id not role → custom-layer areas never reach the role bucket → FAR/OSR/อาคารสุทธิ show 0/blank (default layers escape because id===role). Fix: `rollupAggByRole` in `computeReportVars`. Guard: `test_report_vars_rollup.py` (`LITE_REPORT_VARS_ROLLUP_OK`). **0 open.**

> **SCR_Permit bug report (2026-06-04) — 3 user symptoms, root-caused to the 3 bugs above, no 4th bug.** A real-file repro (33-page PDF + `custom_layer_report.bmaplan`, driven end-to-end) showed all three reproduce as **working** once the fixes are applied: page-26 objects load + are visible (was pdfjs render-bail), display 26 = server 26 (page mapping correct), and page-setup tag/floor edits set dirty + persist to the saved doc. No new bug filed; the "page setup save ไม่ได้" symptom could not be reproduced at the data layer — needs concrete repro steps if it recurs after a hard refresh.
