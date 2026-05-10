# ANNOTATED_PDF_EXPORT_AUDIT.md — Annotated PDF Export Feasibility

Date: 2026-05-10

## Current State

The `/export-pdf` endpoint (server.py line 541) already produces annotated PDFs. It is used by the Page Manager (pgmgrExportPDF) when the user clicks "PDF + annotations".

## Coordinate System

Object coordinates are stored in **PDF points** (not screen pixels or CSS pixels).

Flow:
1. User draws on canvas → click handler divides by `RS` (zoom/render-scale) → stores raw PDF-point coordinates in `mLines`, `mPolys`, `mRefs`, etc.
2. `saveCurrentPage()` persists to `pageStore[page]`
3. Export sends `pageStore` to server
4. Server draws via PyMuPDF: `fitz.Point(p["x"], p["y"])` → placed directly on the page

No coordinate transformation needed between stored values and PDF drawing. The system is consistent end-to-end.

## Rotation Handling

Implemented via `_rot_pt(x, y, rot, W, H)` in server.py:
- rot=0: identity
- rot=90: `(y, W - x)`
- rot=180: `(W - x, H - y)`
- rot=270: `(H - y, x)`

Applied to all object types before drawing. Consistent with `page.set_rotation(rot)` applied to the new page.

## Object Types Supported

| Type | Server code | Status |
|------|-------------|--------|
| `lines` | draw_polyline + label | ✓ |
| `refs` | draw_polyline + label | ✓ |
| `parking` | draw_rect (dot) + label | ✓ |
| `polys` | draw_polyline filled + name/area | ✓ |
| `openings` | draw_polyline filled (see below) | ✓ |

Openings are drawn similarly to polys (existing code handles them).

## E2E Verification

The existing full-mode E2E test (`_test_pdf_annotations_export`) already verifies:
- Server accepts `annotations` payload
- Returned PDF is valid and contains polygon label text
- `ANNOT_OK {'annotated_file': 'annotated_export.pdf', 'label': 'E2E_ROOM_A'}`

## Gaps (for Phase 7 / Phase 8)

| Gap | Current | Phase 7/8 Fix |
|-----|---------|---------------|
| No "quick" single-page export button | Page Manager only | Add button: pages=[curPage] |
| No "all pages" annotated export button | Page Manager requires manual selection | Add button: pages=all non-excluded |

## Risk Assessment

| Item | Risk | Notes |
|------|------|-------|
| Single-page export | Very Low | Same endpoint, just `pages=[curPage]` |
| All-pages export | Low | Same endpoint, pages = all non-excluded |
| Coordinate errors | None | Verified by E2E test |
| Large PDF (45 pages) | Low | Server handles it; memory bounded by fitz |
| Excluded pages | Low | Filter with `excludedPages` set |

## Verdict: SAFE — Proceed with Phase 7 and Phase 8

The `/export-pdf` endpoint is proven, the coordinate system is consistent, and the implementation is trivial (reuse existing call pattern). No server changes needed.
