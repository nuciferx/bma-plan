# PATCH_SUMMARY.md — Latest Sprint

> Full patch history: [docs/archive/patch-history-2026-05-09.md](docs/archive/patch-history-2026-05-09.md)

---

# Latest: E2E Test Split Audit

Date: 2026-05-09

## Outcome: AUDIT_ONLY_STOP

## What Was Audited

- proto/e2e_ui_test.py (1525 lines) — full read and structure map.
- 17 test functions identified, forming an irreversible stateful pipeline.
- 9 infrastructure helper functions identified (~114 lines) as safe to extract.

## Decision

AUDIT_ONLY_STOP. The 17 test functions share a single browser page object and form
a stateful pipeline — each test depends on state left by the previous. Splitting into
independent modules would require duplicating state setup (test weakening risk) or
passing fragile state across modules. Only helpers (~7.5%) are safely extractable,
which is insufficient to justify the refactor.

## What Changed

- docs/design/E2E_TEST_SPLIT_AUDIT.md — new audit document.
- Sprint card: sprints/completed/2026-05-09-e2e-test-split-audit-and-safe-split/

## What Did Not Change

- proto/e2e_ui_test.py: unchanged (1525 lines).
- No runtime code changes.

---

# Previous: Frontend UI HTML Split

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
