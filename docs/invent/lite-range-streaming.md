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

---

## SPIKE RESULTS (2026-07-03 — artifacts: `lite/sandbox/invent-range-streaming/`)

| ขั้น | ผล |
|---|---|
| S1 linearization | RAMA4 **ไม่** / CHH **ไม่** — แต่กลายเป็นไม่สำคัญ (ดู S3) |
| S2 /raw Range | Starlette FileResponse ตอบ **206 + Content-Range อยู่แล้ว** — backend ไม่ต้องแก้อะไรเลย |
| S3 memory (CHH 95MB) | streaming ดึงแค่ **19 MB (20%)** แต่ RSS ลดแค่ 1675→1503 MB (**−10%**); TTFR 117→147 ms |
| S3 bug #10730 | **ยืนยันบน 4.0.379** — destroy() คืน main-thread heap (409→98 MB) แต่ worker heap อยู่ครบ (RSS −6%) |
| S4 Blob.slice transport | ใช้งานได้จริง (lazy 19 MB, ไม่ copy เต็ม) แต่ RSS สูงสุด — ไม่ช่วย memory |

**VERDICT: NOGO สำหรับ streaming-เพื่อ-memory → RESHAPE เป็น worker-recycle**
GO criterion (heap ลด ≥50%) FAIL ชัดเจน — เพดาน ~1.5 GB คือ worker commonObjs/render
heap ที่ streaming ไม่แตะและ destroy() ไม่คืน ทางเดียวที่คืนได้คือ terminate worker

**Sprint cards ที่เสนอ (รอ GO):**
1. **RESHAPE-worker-recycle** [หลัก] — idle/page-away → destroy() + terminate worker +
   lazy reinit (warm-up path มีอยู่แล้ว); acceptance: CHH RSS ลด ≥50% หลัง recycle,
   first-paint หลัง reinit ไม่แย่กว่า cold-open ปัจจุบัน
2. **streaming-as-bandwidth** [รอง, optional] — ship `{url, disableAutoFetch}` เป็น
   ชัยชนะด้าน bandwidth ล้วน (byte ลด 80%, backend พร้อมแล้ว, ไม่ต้อง linearize) —
   ประกาศชัดว่า**ไม่ใช่**ทางแก้ memory

**HALTED at checkpoint #2 — รอ GO/NOGO ต่อ card ทั้งสอง**
