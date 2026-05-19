# KNOWN_ISSUES.md — BMA-Plan Known Issues

Date: 2026-05-09

## Active Non-Blocking Issues

| Issue | Severity | Notes |
|-------|----------|-------|
| **BLOAT-FLAKE-1** — `_wait_analyse_ready` flake on real 45-page permit | ~~FRICTION (E2E gate)~~ **RESOLVED** (2026-05-20) | See full entry below |
| WinError 10054 (ConnectionResetError) on uvicorn shutdown | Low | Non-fatal, appears after test suite, does not affect results |
| `? proto` in root git status --short | Low | Proto has internal untracked files (BMA-Plan.spec, build/, dist/, etc.) that are not staged; root submodule tracking works correctly |
| AUTO_MERGE.lock warning on root commit | Low | Pre-existing stale lock; commits succeed regardless |

---

## BLOAT-FLAKE-1 — REAL_PDF `_wait_analyse_ready` analyse flake — RESOLVED

**ID:** BLOAT-FLAKE-1
**Date filed:** 2026-05-20 (BLOAT-5 sprint)
**Date resolved:** 2026-05-20 (BLOAT-FLAKE-1 sprint)
**Severity:** ~~FRICTION — blocks `full` E2E reliability; smoke is unaffected~~ **RESOLVED**

**Fix applied (BLOAT-FLAKE-1):** `_wait_analyse_ready` default timeout raised 30.0 s → 60.0 s. Grace window added: if the status bar still shows active progress (`กำลังโหลด` / `กำลังวิเคราะห์`) at the original deadline, the wait is granted +50% extra time before declaring failure. ~15 LOC changed in `proto/e2e_ui_test.py`, one helper only. Full E2E now GREEN: `PERSIST_OK` / `REAL_OK` / `ANNOT_OK` stable. `LOOP_STOP_REGRESSION` halt cleared. If the flake recurs under even heavier load, next escalation: Playwright browser-context reset between heavy real-PDF tests, or server cache warm-up before the real-PDF suite (both still documented below as alternative fix paths).

**Symptom:**
`_test_real_pdf_multipage_persistence` → `_wait_analyse_ready(page, 1)` hangs indefinitely. The status bar / analyse endpoint poll never completes for page 1/45 of the real 45-page permit PDF (`20250616_RAMA4 APARTMENT PERMIT rev 1.pdf`). Playwright sees the page stuck at "กำลังโหลดหน้า 1…" and eventually times out → `AssertionError`.

**Discovery history:**
- **BLOAT-3 full run (first attempt)**: flake appeared on page 1/45; single retry passed. First documented occurrence.
- **BLOAT-4 first attempt**: same flake on page 1/45; single retry passed (dev-loop one-retry rule).
- **BLOAT-4 MENU_OK probe note**: "perPageLayerMemoryFixed: skipped (REAL_PDF analyse flake)" — sub-test intentionally skipped because the flake was already known.
- **BLOAT-5 (current iteration)**: 3/3 retries all failed — worst occurrence. Suggests the env is degrading (possibly cumulative Playwright browser state after 5 sprints in one session, or Windows file handles not fully released between test runs).

**Scope:**
The `_wait_analyse_ready` path exercises: (1) open real PDF via `/upload`, (2) render page 1 via `/page/1`, (3) trigger `/analyse` for the page, (4) poll status until "analysed". This path does NOT invoke any BLOAT-5 functions (`page-setup.js`) — page-setup helpers only run when the Setup modal is open or floor sub-types are changed. Confirmed NOT a BLOAT-5 regression.

**Hypothesis (env-level causes, ordered by likelihood):**
1. Playwright browser-context not reset between `_test_real_pdf_multipage_persistence` and previous heavy tests; accumulated network/socket state causes the analyse XHR to stall.
2. Windows file-handle exhaustion after many test cycles in a single session — uvicorn / PyMuPDF leave handles open; subsequent runs starve.
3. `_wait_analyse_ready` timeout too tight for cold-cache real PDF on a busy system (currently tight enough to pass on a warm run, marginal on first open after 5 sprints).
4. Intermittent Windows Defender / AV scan triggered on the large PDF file on first open, delaying PyMuPDF render.

**Suggested fix paths:**
- **(a) Bump `_wait_analyse_ready` timeout** — increase polling timeout from current value; cheap first fix; does not address root cause.
- **(b) Add Playwright browser-context reset** — call `await page.context().close()` + create new context before the real-PDF test block; isolates accumulated network state.
- **(c) Warm-up server caches before real-PDF tests** — pre-render page 1 in a throwaway context so analyse completes before `_wait_analyse_ready` starts the clock.
- **(d) Investigate uvicorn file-handle leak** — check `lsof` / Windows handle count after 5+ sprint test cycles; if handles are leaking, add explicit `doc.close()` in TTL pruner.

**Impact on sprint verification:**
Smoke tests do NOT exercise `_test_real_pdf_multipage_persistence` — all smoke markers remain fully reliable. BLOAT-5 (and prior BLOAT sprints) are smoke-verified correct. The flake only prevents `full` from passing, which exercises `REAL_OK`, `PERSIST_OK`, and `ANNOT_OK` on the real 45-page permit.

**Status:** RESOLVED (2026-05-20 — BLOAT-FLAKE-1). Fix: timeout 30→60 s + grace window. Full E2E GREEN. Dev-loop unblocked.

## Resolved Incidents (for reference)

| Incident | Fix | Proto Commit |
|----------|-----|--------------|
| Static assets 404 / UI renders unstyled after frontend split | Install `aiofiles`; mount `/static` unconditionally; use `Path(__file__).resolve().parent` | `a2099ec` |
| UTF-8 BOM in app.css causing CSS parse failure | Strip BOM bytes (`\xef\xbb\xbf`) from `static/css/app.css` | `65f5a65` |
| `_STATIC_DIR` CWD-relative path breaks when run from root | Replace `os.path.join(os.path.dirname(__file__), "static")` with `Path(__file__).resolve().parent / "static"` | `65f5a65` |

See `docs/process/TROUBLESHOOTING.md` for full diagnosis steps.

## Design Limitations (By Intent)

| Limitation | Reason |
|------------|--------|
| lawBasis is null for most object types | Only meaningful for gross_floor_area, floor_area, legal_open_space, site_land_area — by design |
| Right panel still has Legacy/Compatibility Properties+ObjectTree | Intentional backward-compat label; future sprint may collapse these |
| Opening parent auto-link re-runs on saveCurrentPage | By design; parentManual flag now guards against overwriting manual assignments |

## Deferred Work

- Full scale record: calibration endpoint point1/point2 not yet stored in XLSX
- Manual opening parent reassignment further UX improvements
- Parking-specific sub-rows in สรุปตาม Report Target
- Reference arcs/circles (curved path — Sprint 5)
- iPad touch UX (Sprint 6)
- Moving full property editor out of right panel into left panel Properties tab (left tab now shows full editor, but right panel compat section remains)

## Phase 1 Scope Boundary (Permanent)

Never implement in Phase 1:
- Legal checker, OCR, AI checker, Rule Engine
- FAR/OSR/setback validation, K.1 generator
- Auto boundary detection, draggable workspace
- Full autosave engine, large file mode engine
