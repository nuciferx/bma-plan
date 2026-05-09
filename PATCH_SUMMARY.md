# PATCH_SUMMARY.md — Latest Sprint

> Full patch history: [docs/archive/patch-history-2026-05-09.md](docs/archive/patch-history-2026-05-09.md)

---

# Latest: Frontend UI HTML Split

Date: 2026-05-09

## Outcome: PASS

## What Changed

- `proto/static/css/app.css` — new file; 307 lines extracted from ui.html `<style>` block.
- `proto/static/js/semantic-meta.js` — new file; 6 constants + 2 functions (isAreaSemanticTag, deriveMeasurementMeta) extracted.
- `proto/static/js/opening-parent.js` — new file; 5 functions (openingProbePoints, openingInsidePoly, openingParentCandidates, linkOpeningParent, linkOpeningsInStore) extracted.
- `proto/server.py` — added StaticFiles mount (guarded by os.path.exists). 3 lines added.
- `proto/ui.html` — 1437 → 1111 lines (-326 lines, -23%); `<style>` replaced with `<link>`, 2 `<script src>` added, 13 inline definitions removed.
- Sprint card moved to sprints/completed/.

## What Did Not Change

- No behavior changes — all extracted JS runs in same global scope.
- No save/load format changes.
- No export behavior changes.
- No legal/OCR/AI/Rule Engine.

## Files Touched

- `proto/server.py`, `proto/export/__init__.py`, `proto/export/semantic_metadata.py`, `proto/export/xlsx_helpers.py`
- `docs/design/RUNTIME_FILE_SPLIT_AUDIT.md`, `docs/design/E2E_SPLIT_PLAN.md`, `docs/status/READ_ORDER.md`
- `CURRENT_STATUS.md`, `PATCH_SUMMARY.md`, `TEST_RESULT.md`, `FINAL_REPORT_FOR_CHATGPT.md`, `log.md`
- `docs/status/LATEST_STATUS.md`, `docs/status/NEXT_ACTIONS.md`, `docs/status/COMMIT_HISTORY.md`
