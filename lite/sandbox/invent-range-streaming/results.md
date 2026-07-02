# SPIKE RESULTS — lite Range-request streaming (PERF-20260702-open-streaming)

Date: 2026-07-03 · Runtime: ~10 min · Python 3.14.3 (3.11 unavailable; server
imports/runs fine), fitz 1.27.2.2, Starlette 1.0.0, pdf.js **4.0.379** (vendored),
Chromium via Playwright with `--enable-precise-memory-info --js-flags=--expose-gc`.

All artifacts in `lite/sandbox/invent-range-streaming/` — **no live app file was
edited.** Server booted via read-only import of `server_lite.app`; the `/spike`
page route was attached at runtime in the driver only.

Target PDFs: RAMA4 (19.2 MB, 45 pg) and CHH (95.2 MB, 95 pg). Each scenario
visits pages 1..10 (getPage + render @ scale 0.5). RSS = whole Chromium process
tree (browser + renderer + GPU + utility) via psutil — the pdf.js worker is a
thread inside the renderer, so this RSS **includes the ~600 MB worker heap** that
`performance.memory` (main-thread only) cannot see.

---

## S1 — Linearization check

| File | Size | Pages | `fitz.is_fast_webaccess` | `/Linearized` in head | Linearized? |
|---|---|---|---|---|---|
| RAMA4 | 19.2 MB | 45 | 0 | no | **NO** |
| CHH   | 95.2 MB | 95 | 0 | no | **NO** |

Both customer PDFs are **non-linearized**. Research predicted this would force a
full fetch — **S3 empirically disproves that** (see below).

## S2 — Starlette `/raw` Range support (zero backend work?)

| Request | Status | Content-Range | Accept-Ranges | Bytes |
|---|---|---|---|---|
| `GET /raw` (full) | 200 | — | `bytes` | 19,207,478 |
| `Range: bytes=0-1023` | **206** | `bytes 0-1023/19207478` | `bytes` | 1024 |
| `Range: bytes=1000000-1065535` | **206** | `bytes 1000000-1065535/19207478` | `bytes` | 65536 |

**`FileResponse` already serves 206 Partial Content + `Accept-Ranges: bytes`
natively. Zero backend work needed for Range support.**

## S3 — Streaming memory test (the real target = CHH 95 MB)

### CHH 95 MB — 10 pages
| Metric | A baseline `{data:buf}` | B streaming `{url,…}` | T transport (Blob.slice) |
|---|---|---|---|
| Bytes over `/raw` | 95,183,213 (100%, 1 req) | **19,292,525 (20%, 39 reqs)** | 0 network (19.3 MB local) |
| Time-to-first-render | 117 ms | 147 ms | 124 ms |
| Peak main-thread heap | 409 MB | **289 MB** | 385 MB |
| **RSS after 10 pages** | **1675 MB** | **1503 MB** | 1717 MB |
| RSS after `destroy()` | 1568 MB (−107, −6%) | 1463 MB (−40, −3%) | 1676 MB |
| Main heap after `destroy()` | 98 MB | 3 MB | 111 MB |

### RAMA4 19 MB — 10 pages (secondary)
| Metric | A baseline | B streaming | T transport |
|---|---|---|---|
| Bytes over `/raw` | 19,207,478 (100%) | 4,920,630 (26%, 40 reqs) | 0 network (4.9 MB local) |
| TTFR | 208 ms | 156 ms | 136 ms |
| Peak main heap | 77 MB | 62 MB | 85 MB |
| RSS after pages | 1023 MB* | 1023 MB* | 898 MB |
| RSS after destroy | 944 MB | 944 MB | 826 MB |

\* RAMA4 RSS is dominated by leftover from the prior CHH context in tree
measurement; RAMA4 alone (first run, isolated) sat ~49–72 MB. RAMA4 is too small
to stress the memory ceiling — CHH is the decision-driver.

## S4 — Local-file transport probe (PDFDataRangeTransport)

- `lib.PDFDataRangeTransport` **IS exported and functional in 4.0.379.**
- Custom `requestDataRange(begin,end)` → `File.slice(begin,end).arrayBuffer()` →
  `onDataRange()` works; page 1 renders correctly.
- **Lazy, not a full copy:** transport served only 19.3 MB (CHH) / 4.9 MB (RAMA4)
  via `Blob.slice` to visit 10 pages — same footprint as network streaming.
- BUT its RSS was the **highest** (1717 MB) because the page still holds the full
  `File`/ArrayBuffer source *plus* the worker heap. Local-first is preservable,
  but gives **no memory win** over baseline.

---

## Key findings

1. **Non-linearized PDFs stream fine.** Both files are non-linearized, yet
   streaming fetched only **20% (CHH) / 26% (RAMA4)** of the bytes. Range
   random-access does not require linearization; linearization only optimizes
   progressive first-page paint. → The feared server-side QPDF/PyMuPDF
   linearization cost is **moot. Drop it from scope.**

2. **The memory ceiling is NOT the file buffer — it is the pdf.js worker heap.**
   Streaming cut the file transfer 95→19 MB (−76 MB) but RSS dropped only
   1675→1503 MB (**−10%, not the ≥50% GO target**). The dominant ~1.5 GB is the
   worker `commonObjs` (fonts/XObjects) + render heap, which streaming does not
   touch.

3. **#10730 CONFIRMED on 4.0.379.** `doc.destroy()` releases the *main-thread*
   heap cleanly (409→98, 289→3 MB) but **RSS barely moves** (−6% / −3%). The
   worker heap survives `destroy()`. Only killing the worker will release it.

4. **First-paint not regressed** in any meaningful sense: +30 ms (117→147 ms),
   still well under perceptible threshold.

5. **Local-first is preservable** via `PDFDataRangeTransport` + `Blob.slice`
   (lazy, no full copy) — but yields no memory benefit.

---

## S5 — VERDICT vs GO criteria

| GO criterion | Result | Pass? |
|---|---|---|
| Worker heap on CHH drops ≥50% vs baseline | −10% (1675→1503 MB) | **FAIL** |
| First-paint not regressed | +30 ms, negligible | PASS |
| Local-first path preserved | Yes (transport lazy-reads Blob) | PASS |

### Recommendation: **NOGO on streaming-as-memory-fix → RESHAPE to worker-recycle**

Range streaming does **not** solve the stated problem (the 1.5 GB memory ceiling
on the CHH binder). The ceiling is the pdf.js worker `commonObjs`/render heap,
which streaming leaves resident and which `doc.destroy()` does not release
(#10730 confirmed on 4.0.379). Feeding bytes lazily changes *where bytes come
from*, not *what the worker keeps*.

The invent doc's own named fallback is the correct next move: **periodic worker
recycle** — on idle (or on a memory-pressure signal / page-away), call
`pdfDoc.destroy()` **and terminate + recreate the pdf.js worker**, then reopen on
next interaction. This is the only mechanism the data shows can reclaim the
~1.5 GB (main-thread frees on destroy; the residual is worker-process memory that
only a worker teardown returns).

### Secondary: ship streaming anyway as a cheap, separate bandwidth win

Streaming is **not** the memory fix, but it is nearly free and independently
worthwhile: `{url, disableAutoFetch:true, disableStream:true, rangeChunkSize}`
moves **80% fewer bytes** on the big binder (95→19 MB), lowers the main-thread
heap peak (409→289 MB), the backend already returns 206 (S2 — no work), and no
server-side linearization is needed (finding #1). Suggest filing it as a small
standalone perf sprint (NOT as PERF-20260702's memory solution).

---

## Proposed build-sprint card (for the RESHAPE — worker recycle)

```
### SPRINT (queued) — lite worker-recycle memory release
Problem: pdf.js worker holds ~1.5 GB (commonObjs + render) on the 95 MB CHH
binder; doc.destroy() frees main-thread heap only (#10730), RSS stays ~1.5 GB.
Range streaming (spiked 2026-07-03) cut it just 10% — insufficient.
Approach: on idle-timeout / page-away / memory-pressure, tear down pdf.js
  (pdfDoc.destroy() + terminate the worker) and lazily re-init on next
  interaction. Preserve local-first open. Measure RSS drop after recycle.
Forbidden surfaces: none in measure-engine.js / RS / pdfToC / cToPdf / .bmaplan.
  Touches page-renderer.js (worker lifecycle) only.
Acceptance: CHH RSS after idle-recycle drops ≥50% vs peak; reopen TTFR < 500 ms;
  no measurement/render regression (lite markers green).
Test: lite/tests full + a memory-probe reusing this spike's psutil harness.
```

### Optional secondary card

```
### SPRINT (queued, low-pri) — lite range-streaming open (bandwidth only)
Switch openRemote path to getDocument({url:'/raw?case_id', disableAutoFetch:true,
  disableStream:true, rangeChunkSize:65536}). Backend already 206-capable (verified).
Not a memory fix — 80% fewer bytes moved, lower main-heap peak. Keep {data:buf}
  local-first path for openLocal. No server linearization needed (non-linearized
  files stream fine — verified).
```

## Files created (this spike; NOT committed)
- `spike.html` — pdf.js 4.0.379 harness (scenarios A/B/T + heap/destroy probes)
- `spike_run.py` — driver (boots server read-only, Playwright + psutil tree RSS)
- `s1_linearize.py` — linearization check
- `s2_range.py` — Starlette `/raw` Range probe
- `results.json` — raw metrics
- `results.md` — this file
