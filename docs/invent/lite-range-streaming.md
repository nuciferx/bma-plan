# INVENT — lite Range-request streaming (PERF-20260702-open-streaming, final piece)

Date: 2026-07-03 · Phase 2 (RESEARCH) complete · **Verdict: PRIOR_ART_PARTIAL → spike required → HALTED at human checkpoint (GO / NOGO / RESHAPE)**

## Problem
PDF.js holds ~600 MB doc-level shared objects (fonts/XObjects, worker heap) on a
91 MB customer binder — unreachable by the shipped page-LRU (which took 766→628 MB).
Whole file also resident via `getDocument({data: buf})` (openLocal / /raw path).

## Research summary (bma-researcher, 2026-07-03)
- **Mature parts:** HTTP Range (RFC 7233); Starlette 0.35+ `FileResponse` supports
  Range natively (=> `/raw` may need zero backend work — verify); PDF.js 4.x
  `{url, disableAutoFetch:true, disableStream:true, rangeChunkSize}` is the
  Chrome-viewer pattern; linearized PDFs stream, non-linearized force full fetch
  (xref at end).
- **Open risks (why PARTIAL, not MATURE):**
  1. **PDF.js worker memory bug #10730 (unfixed since v2):** `doc.destroy()` /
     `cleanup()` may NOT release worker `commonObjs` heap — the ~600 MB may be
     irreducible without killing the worker. Must verify on pdfjs-dist 4.0.379.
  2. **Local-first conflict:** our fastest path feeds a local ArrayBuffer.
     Lazy-reading a local File via `Blob.slice()` + custom `PDFDataRangeTransport`
     is undocumented/untested territory; transfer-vs-copy semantics unclear.
  3. **Linearization unknown** for real customer PDFs (RAMA4, CHH). If
     non-linearized: fallback = full buffer (status quo) or silent server-side
     linearization on upload (QPDF/PyMuPDF cost — measure).

## Recommended spike (narrow, in lite/sandbox/ — NOT live app)
1. Check linearization of RAMA4 + CHH (`qpdf --show-linearization` / fitz).
2. Verify Starlette /raw sends 206 + Accept-Ranges as-is.
3. `{url, disableAutoFetch}` on a linearized file → measure worker heap before/
   after `destroy()` (bug #10730 check on 4.0.379).
4. Custom PDFDataRangeTransport over `Blob.slice()` for the local-first path →
   confirm no full-buffer copy.
5. CHH binder: streaming vs current openLocal — heap + first-paint numbers.

GO criteria: worker heap on CHH drops ≥50% AND first-paint not regressed AND
local-first path preserved (or consciously traded). NOGO if #10730 makes the
heap irreducible → alternative RESHAPE: periodic worker recycle (destroy worker
+ reopen at idle) as a cruder but honest memory release.

Full research report with sources: see the 2026-07-03 session log / researcher
output (PDF.js API docs, GitHub #10730, Starlette release notes, linearized-PDF
guides, MDN transferable objects).

**Awaiting human decision — invention never auto-promotes (Pack H doctrine).**
