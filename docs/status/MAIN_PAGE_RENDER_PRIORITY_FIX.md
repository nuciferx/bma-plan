# MAIN_PAGE_RENDER_PRIORITY_FIX — Sprint Result

**Date:** 2026-05-11
**Sprint:** RUN_MAIN_PAGE_RENDER_PRIORITY_FIX
**Status:** PASS — py_compile + smoke + full

---

## Problem

Real tester reports PDF page display is slow. Browser `BMA_PRE_FIRST_PAGE_LOAD` showed delay is almost entirely in `img request+onload` for `/page/{n}`. UI post-first-visible work is only ~20ms, so canvas top bar / panels are not the main bottleneck.

Investigation found that `startCheck()` called `buildSidebar()` **before** `loadPage()`, which meant all sidebar thumbnail `/thumb/{n}` requests started at the same time as (or before) the main `/page/{n}` request. For a 45-page PDF, this created massive server/render contention.

---

## Root Cause

```javascript
// startCheck() — old flow:
buildSidebar();   // <-- ALL thumbnails start loading NOW (45 requests!)
loadPage(target); // <-- Main page starts loading AFTER thumbnails
```

`buildSidebar()` creates `<img src="/thumb/n">` for every page. Browsers start fetching these immediately. The server (single FastAPI process) then tries to render 45 thumbnails + 1 main page concurrently via PyMuPDF, causing:
- Memory pressure (`malloc failed` seen in full test logs)
- CPU contention
- Main page blocked behind thumbnail queue

---

## Fix Applied

### 1. Frontend: Reorder startCheck() flow

**`proto/ui.html` — `startCheck()`:**
- Removed `buildSidebar()` call before `loadPage()`
- Now: `startCheck()` → `loadPage(target)` → main page loads first

**`proto/ui.html` — `loadPage()`:**
- `buildSidebar()` is called **after** `img.onload` (main page already visible)
- This ensures thumbnails only start loading after the current page is rendered

**Before:**
```
startCheck()
  → buildSidebar()     [45 thumb requests start]
  → loadPage(1)        [main page starts]
```

**After:**
```
startCheck()
  → loadPage(1)        [main page starts immediately]
    → img.onload       [main page visible]
    → buildSidebar()   [thumbnails start AFTER main page visible]
```

### 2. Server: Add thumbnail performance logging

**`proto/server.py` — `/thumb/{n}` and `/thumb-md/{n}`:**
- Added `[BMA_THUMB_RENDER_PERF]` log lines matching `/page/{n}` format
- Logs: `session`, `cache`, `get_pixmap`, `encode`, `bytes`, `total`, `HIT/MISS`

### 3. Server: Improve cache key completeness

**`proto/server.py`:**
- `/thumb/{n}` cache key: `("thumb", n, rot)` → `("thumb", n, rot, "jpeg", 70)`
- `/thumb-md/{n}` cache key: `("thumb-md", n, rot)` → `("thumb-md", n, rot, "jpeg", 82)`
- Prevents silent cache collisions if future code changes format/quality

---

## Test Results

```
python -m py_compile proto/server.py proto/e2e_ui_test.py  → PASS
python proto/e2e_ui_test.py smoke                          → PASS
python proto/e2e_ui_test.py full                           → PASS
```

All 17 E2E sections green: CACHE, SETUP, MAIN_UI, VECTOR, RECAL, SITE_UI, XLSX, PROJECT, RASTER, WHEEL, SNAP, SELECT, SETBACK, EXT_MEASURE, ANNOT, PERSIST, REAL.

---

## Instrumentation Evidence

From full test run on real 45-page permit PDF:

**Main page renders first:**
```
[BMA_PAGE_RENDER_PERF] page=1 scale=1.5 rot=0 ... total=526.1ms MISS
[BMA_PAGE_RENDER_PERF] page=1 scale=1.5 rot=0 ... total=360.9ms MISS
[BMA_PAGE_RENDER_PERF] page=2 scale=1.5 rot=0 ... total=518.0ms MISS
```

**Then thumbnails load (after main page visible):**
```
[BMA_THUMB_RENDER_PERF] thumb=1 rot=0 ... total=18.2ms MISS
[BMA_THUMB_RENDER_PERF] thumb-md=1 rot=0 ... total=67.1ms MISS
... (many more thumb requests)
```

**Observation:** Some thumbnails still take 1000–2200ms on complex pages (e.g., `thumb=13` took 2021ms). This is because the real permit PDF has large/complex pages. But the critical fix is that **the main page is no longer blocked behind the thumbnail queue** — it loads first.

**Memory pressure observed:** During full test, server logged `malloc (27098928 bytes) failed` and `realloc (33554432 bytes) failed` during concurrent thumbnail rendering. This confirms the original diagnosis: too many concurrent renders cause memory exhaustion. My fix reduces peak contention by deferring thumbnails.

---

## Files Changed

| File | Change |
|------|--------|
| `proto/ui.html` | Removed `buildSidebar()` from `startCheck()` before `loadPage()` |
| `proto/server.py` | Added `BMA_THUMB_RENDER_PERF` logging to `/thumb/{n}` and `/thumb-md/{n}` |
| `proto/server.py` | Cache keys for thumb/thumb-md now include `"jpeg"` and quality |
| `proto/e2e_ui_test.py` | Updated cache key assertions to match new format |

---

## Contracts Preserved

- RS=1.5 unchanged
- Coordinate math (`pdfToC`, `cToPdf`) untouched
- Measurement, calibration, drawing unchanged
- Save/load schema unchanged
- XLSX export unchanged
- Annotated PDF export unchanged
- No OCR/AI/legal checker added

---

## Known Limitations / Next Steps

1. **Sidebar thumbnails still load all at once** — `buildSidebar()` creates all thumbnail `<img>` elements simultaneously. Future improvement: use IntersectionObserver or virtual scrolling to only load visible thumbnails.
2. **Memory exhaustion on large PDFs** — Concurrent rendering of 45 complex pages can still exhaust server memory. This is a fundamental limit of the current single-process FastAPI + PyMuPDF architecture. Mitigation: cache more aggressively or limit concurrent renders server-side.
3. **JPEG quality not changed** — Kept at 88 for pages, 70 for thumbs, 82 for thumb-md. Quality reduction is a safe future optimization but was not needed for this sprint.

---

## Lessons Learned

1. **Startup sequencing matters.** `buildSidebar()` before `loadPage()` created an invisible queue of 45 thumbnail requests that blocked the main page.
2. **Browser `loading="lazy"` is not enough** when all thumbnails are in the visible sidebar area — they all start loading immediately.
3. **Instrumentation revealed the true bottleneck.** Without `BMA_PAGE_RENDER_PERF` and `BMA_THUMB_RENDER_PERF`, the thumb contention would be invisible.
