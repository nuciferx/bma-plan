"""
BMA-Plan Lite — standalone backend (INV-2026-05-21-001, Approach A).

Fresh minimal FastAPI app — NOT derived from proto/server.py. Implements the
endpoints lite needs, reusing PyMuPDF directly:
    POST /upload          per-case PDF open (no global SESSION — case_id isolation)
    GET  /page/{n}        render page n -> JPEG at RS=1.5 (matches proto render scale)
    GET  /pageinfo/{n}    page size in PDF points (for coord conversion / origSize)
    GET  /thumb/{n}       small JPEG for ⌘K / F12 overview
    GET  /health  /       version + UI

Per-case isolation is a hard invariant: every render endpoint takes case_id; each
case owns its own doc + image_cache. RS=1.5 must match proto so .bmaplan geometry
(PDF-point coords) cross-opens with identical area values.

Anti-pattern guards (AGENTS.md §8): static dir from Path(__file__).resolve();
app.mount NOT guarded by if-exists (would swallow the aiofiles RuntimeError).
"""
import io
import time
import uuid
from pathlib import Path

import fitz  # PyMuPDF
from fastapi import FastAPI, File, Request, UploadFile
from fastapi.responses import FileResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles

LITE_VERSION = "0.2.0-LITE-1+2+3"
SCHEMA_VERSION = 1
RS = 1.5                       # render scale — MUST match proto (coord contract)
MAX_UPLOAD_BYTES = 1024 * 1024 * 1024   # 1 GB — real permit binders run into the 100s of MB
MAX_IMAGE_CACHE = 24                     # bounded per-case JPEG cache (only viewed pages render)
CASE_TTL_SEC = 3600

_BASE_DIR = Path(__file__).resolve().parent
_STATIC_DIR = _BASE_DIR / "static"
_UI_FILE = _BASE_DIR / "ui-lite.html"
_REPORT_FILE = _BASE_DIR / "lite-report.html"   # LITE-REPORT: editable web report page

CASES: dict = {}

app = FastAPI(title="BMA-Plan Lite", version=LITE_VERSION)
print(f"[lite][static] serving from: {_STATIC_DIR}")
app.mount("/static", StaticFiles(directory=str(_STATIC_DIR)), name="static")


def _prune():
    now = time.time()
    for cid in [c for c, v in CASES.items() if now - v["touched"] > CASE_TTL_SEC]:
        try:
            CASES[cid]["doc"].close()
        except Exception:
            pass
        CASES.pop(cid, None)


def _make_case(doc, path):
    _prune()
    cid = uuid.uuid4().hex
    CASES[cid] = {"doc": doc, "path": path, "image_cache": {}, "touched": time.time()}
    return cid


def _get_case(cid):
    c = CASES.get(cid)
    if c:
        c["touched"] = time.time()
    return c


@app.get("/")
def index():
    return FileResponse(str(_UI_FILE))


@app.get("/report")
def report():
    # LITE-REPORT: standalone editable report page. Receives its payload from the
    # main UI via sessionStorage["bmaReportPayload"] (same-origin window.open),
    # falls back to bundled sample data when opened directly.
    return FileResponse(str(_REPORT_FILE))


@app.get("/health")
def health():
    return JSONResponse({"ok": True, "app": "bma-plan-lite", "version": LITE_VERSION,
                         "schema_version": SCHEMA_VERSION, "cases": len(CASES)})


@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    import tempfile
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    total = 0
    try:
        while True:
            chunk = await file.read(1024 * 1024)
            if not chunk:
                break
            total += len(chunk)
            if total > MAX_UPLOAD_BYTES:
                return JSONResponse({"error": "file too large"}, 413)
            tmp.write(chunk)
        tmp.close()
        if total == 0:
            return JSONResponse({"error": "empty file"}, 400)
        try:
            doc = fitz.open(tmp.name)
        except Exception:
            return JSONResponse({"error": "invalid pdf"}, 400)
        if doc.is_encrypted:
            doc.close()
            return JSONResponse({"error": "encrypted pdf not supported"}, 400)
        case_id = _make_case(doc, tmp.name)
        sizes = []
        for pg in doc:
            r = pg.rect
            sizes.append({"w": round(r.width, 2), "h": round(r.height, 2),
                          "rot": pg.rotation})
        return {"pages": len(doc), "name": file.filename, "case_id": case_id, "sizes": sizes}
    except Exception:
        try:
            tmp.close()
        except Exception:
            pass
        return JSONResponse({"error": "upload failed"}, 500)


def _norm_scale(s):
    try:
        s = float(s)
    except Exception:
        return None
    return s if 0.2 <= s <= 4.0 else None


@app.get("/page/{n}")
def get_page(n: int, case_id: str, scale: float = RS, rot: int = 0):
    case = _get_case(case_id)
    if not case:
        return JSONResponse({"error": "invalid case"}, 400)
    rs = _norm_scale(scale)
    if rs is None:
        return JSONResponse({"error": "bad scale"}, 400)
    doc = case["doc"]
    if n < 1 or n > len(doc):
        return JSONResponse({"error": "page out of range"}, 404)
    cache = case["image_cache"]
    key = ("page", n, rs, rot)
    if key not in cache:
        page = doc[n - 1]
        mat = fitz.Matrix(rs, rs).prerotate(rot)
        pix = page.get_pixmap(matrix=mat)
        cache[key] = pix.tobytes("jpeg", jpg_quality=88)
        if len(cache) > MAX_IMAGE_CACHE:
            cache.pop(next(iter(cache)))
    return Response(cache[key], media_type="image/jpeg")


@app.get("/raw")
def raw_pdf(case_id: str):
    """Return the raw PDF bytes for a case — used by PDF.js client-side renderer."""
    case = _get_case(case_id)
    if not case:
        return JSONResponse({"error": "invalid case"}, 400)
    pdf_path = case["path"]
    return FileResponse(str(pdf_path), media_type="application/pdf")


@app.get("/pageinfo/{n}")
def pageinfo(n: int, case_id: str):
    case = _get_case(case_id)
    if not case:
        return JSONResponse({"error": "invalid case"}, 400)
    doc = case["doc"]
    if n < 1 or n > len(doc):
        return JSONResponse({"error": "page out of range"}, 404)
    r = doc[n - 1].rect
    return {"w_pt": r.width, "h_pt": r.height, "rot": doc[n - 1].rotation,
            "render_scale": RS}


def _hex_rgb(h):
    h = (h or "#ff3b30").lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    try:
        return (int(h[0:2], 16) / 255, int(h[2:4], 16) / 255, int(h[4:6], 16) / 255)
    except Exception:
        return (1, 0.23, 0.19)


@app.post("/export-xlsx")
async def export_xlsx(req: Request):
    """rows = [{page,category,semanticTag,kind,area,count}]; summary = [{category,total}]."""
    from openpyxl import Workbook
    data = await req.json()
    wb = Workbook()
    ws = wb.active
    ws.title = "Measurements"
    ws.append(["Page", "Category", "Semantic Tag", "Type", "Area (m²)", "Count"])
    for r in data.get("rows", []):
        ws.append([r.get("page"), r.get("category"), r.get("semanticTag"),
                   r.get("kind"), r.get("area"), r.get("count")])
    ws2 = wb.create_sheet("Summary")
    ws2.append(["Category", "Total Area (m²) — all pages"])
    for s in data.get("summary", []):
        ws2.append([s.get("category"), s.get("total")])
    buf = io.BytesIO()
    wb.save(buf)
    return Response(buf.getvalue(),
                    media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    headers={"Content-Disposition": "attachment; filename=bma-lite-export.xlsx"})


def _arrow(shape, p0, p1, col):
    import math
    shape.draw_line(fitz.Point(p0), fitz.Point(p1))
    ang = math.atan2(p1[1] - p0[1], p1[0] - p0[0]); hl = 9
    for s in (-0.4, 0.4):
        shape.draw_line(fitz.Point(p1), fitz.Point(p1[0] - hl * math.cos(ang + s), p1[1] - hl * math.sin(ang + s)))


def _cloud(shape, x, y, w, h):
    import math
    r = max(5, min(abs(w), abs(h)) / 8.0); step = r * 1.6
    def bumps(x0, y0, x1, y1):
        dx, dy = x1 - x0, y1 - y0; ln = math.hypot(dx, dy) or 1; n = max(1, round(ln / step))
        for i in range(n):
            shape.draw_circle(fitz.Point(x0 + dx * (i + 0.5) / n, y0 + dy * (i + 0.5) / n), r)
    bumps(x, y, x + w, y); bumps(x + w, y, x + w, y + h); bumps(x + w, y + h, x, y + h); bumps(x, y + h, x, y)


@app.post("/export-pdf-overlay")
async def export_pdf_overlay(req: Request):
    """Rotation-PROOF overlay: render each measured page to a raster at its displayed
    orientation, then draw measurement geometry + annotations on top (coords * RS).
    Exports only pages that carry content. WYSIWYG; correct for any page rotation."""
    data = await req.json()
    case = _get_case(data.get("case_id"))
    if not case:
        return JSONResponse({"error": "invalid case"}, 400)
    doc = case["doc"]
    pages = data.get("pages", {})
    out = fitz.open()
    for n in sorted(pages.keys(), key=lambda k: int(k)):
        idx = int(n) - 1
        if idx < 0 or idx >= len(doc):
            continue
        pg = pages[n]
        pix = doc[idx].get_pixmap(matrix=fitz.Matrix(RS, RS))   # displayed orientation
        page = out.new_page(width=pix.width, height=pix.height)
        page.insert_image(fitz.Rect(0, 0, pix.width, pix.height), pixmap=pix)
        sh = page.new_shape()
        for o in pg.get("objects", []):
            pts = [(p["x"] * RS, p["y"] * RS) for p in o.get("pts", [])]
            col = _hex_rgb(o.get("color"))
            if o.get("counting"):
                if pts:
                    sh.draw_circle(fitz.Point(pts[0]), 4)
                    sh.finish(color=col, fill=col, width=1)
                continue
            if o.get("kind") == "poly" and len(pts) >= 3:
                sh.draw_polyline(pts + [pts[0]]); sh.finish(color=col, width=1.4)
            elif len(pts) >= 2:
                sh.draw_polyline(pts); sh.finish(color=col, width=1.4)
            if o.get("label") and pts:
                cx = sum(p[0] for p in pts) / len(pts); cy = sum(p[1] for p in pts) / len(pts)
                try:
                    page.insert_text(fitz.Point(cx, cy), o["label"], fontsize=9, color=col)
                except Exception:
                    pass
        # annotations
        for a in pg.get("annotations", []):
            t = a.get("type"); col = _hex_rgb(a.get("color") or "#ff453a")
            if t in ("ann_text", "ann_comment"):
                pt = a.get("pt") or (a.get("pts") or [{}])[0]
                if "x" in pt:
                    try:
                        page.insert_text(fitz.Point(pt["x"] * RS, pt["y"] * RS),
                                         ("[!] " if t == "ann_comment" else "") + (a.get("text") or ""),
                                         fontsize=10, color=col)
                    except Exception:
                        pass
                continue
            pp = a.get("pts") or []
            if len(pp) < 2:
                continue
            a0 = (pp[0]["x"] * RS, pp[0]["y"] * RS); a1 = (pp[1]["x"] * RS, pp[1]["y"] * RS)
            x, y = min(a0[0], a1[0]), min(a0[1], a1[1]); w = abs(a1[0] - a0[0]); h = abs(a1[1] - a0[1])
            if t == "ann_arrow":
                _arrow(sh, a0, a1, col); sh.finish(color=col, width=1.6)
            elif t == "ann_highlight":
                sh.draw_rect(fitz.Rect(x, y, x + w, y + h)); sh.finish(color=None, fill=(1, 0.84, 0.04), fill_opacity=0.30)
            elif t == "ann_rect":
                sh.draw_rect(fitz.Rect(x, y, x + w, y + h)); sh.finish(color=col, width=1.6)
            elif t == "ann_circle":
                sh.draw_oval(fitz.Rect(x, y, x + w, y + h)); sh.finish(color=col, width=1.6)
            elif t == "ann_cloud":
                _cloud(sh, x, y, w, h); sh.finish(color=col, width=1.4)
        sh.commit()
    if len(out) == 0:
        out.new_page()
    data_bytes = out.tobytes()
    out.close()
    return Response(data_bytes, media_type="application/pdf",
                    headers={"Content-Disposition": "attachment; filename=bma-lite-overlay.pdf"})


def _apply_page_mutations(doc, order_1based):
    """Pure function: reorder/delete/duplicate pages in *doc* using doc.select().

    order_1based: list of 1-based original page numbers.  Repeats = duplicate;
    omissions = delete.  Returns (new_doc, renumber_map, new_count).

    renumber_map: {original_1based: new_1based} for each surviving original page;
    first occurrence wins when an original appears more than once (duplicates).

    Raises ValueError if order_1based is empty or contains out-of-range values.
    Never performs file I/O.
    """
    if not order_1based:
        raise ValueError("order must be non-empty")
    n_pages = len(doc)
    for idx in order_1based:
        if idx < 1 or idx > n_pages:
            raise ValueError(f"page {idx} out of range 1..{n_pages}")

    # Build 0-based list for doc.select()
    order_0based = [i - 1 for i in order_1based]

    # Work on an in-memory copy so the original doc is never mutated by this fn.
    # open("", "pdf") opens a blank in-memory PDF; insert_pdf copies pages.
    new_doc = fitz.open()
    new_doc.insert_pdf(doc)          # full copy
    new_doc.select(order_0based)     # reorder/delete/dup in place

    # Build renumber_map: first occurrence of each original page number → new pos.
    renumber_map = {}
    for new_idx, orig_1based in enumerate(order_1based):
        if orig_1based not in renumber_map:
            renumber_map[orig_1based] = new_idx + 1   # 1-based new position

    new_count = len(new_doc)
    return new_doc, renumber_map, new_count


@app.post("/apply-page-mutations")
async def apply_page_mutations(req: Request):
    """Apply a set_order mutation to the case PDF atomically.

    Body: {"case_id": str, "order": [1-based original page numbers]}.

    Repeats in order = duplicate; omissions = delete.  After success the
    on-disk PDF and in-memory doc reflect the new order and image_cache is
    cleared.  On any failure the original doc + file are left untouched.

    Returns: {"ok": true, "renumber_map": {...}, "new_count": N}
    """
    import os
    import tempfile

    data = await req.json()
    cid = data.get("case_id")
    order = data.get("order")

    case = _get_case(cid)
    if not case:
        return JSONResponse({"error": "invalid case"}, 404)

    if not order:
        return JSONResponse({"error": "order must be non-empty"}, 400)

    old_doc = case["doc"]
    n_pages = len(old_doc)

    # Validate range
    for idx in order:
        try:
            idx_int = int(idx)
        except (TypeError, ValueError):
            return JSONResponse({"error": f"non-integer page index: {idx!r}"}, 400)
        if idx_int < 1 or idx_int > n_pages:
            return JSONResponse(
                {"error": f"page {idx_int} out of range 1..{n_pages}"}, 400
            )

    # Coerce to ints (JSON may deliver floats)
    order_int = [int(i) for i in order]

    # ATOMIC write: build new doc → temp file → fsync → os.replace → swap in CASES
    old_path = case["path"]
    tmp_path = None
    new_doc_mem = None
    try:
        new_doc_mem, renumber_map, new_count = _apply_page_mutations(old_doc, order_int)

        # Write to temp file in same directory (same filesystem → os.replace is atomic)
        tmp_fd, tmp_path = tempfile.mkstemp(
            dir=str(Path(old_path).parent), suffix=".pdf"
        )
        try:
            new_doc_mem.save(tmp_path)
            # fsync to ensure bytes are on disk before the rename
            with open(tmp_path, "rb") as f:
                os.fsync(f.fileno())
        finally:
            os.close(tmp_fd)

        # Atomically replace the case file on disk
        os.replace(tmp_path, old_path)
        tmp_path = None  # rename consumed it; don't try to delete on error

        # Reopen from the new file and swap into the case
        new_doc_disk = fitz.open(old_path)
        old_doc.close()
        case["doc"] = new_doc_disk
        case["image_cache"] = {}       # stale renders must not survive page reorder
        case["touched"] = time.time()

        # Return string-keyed renumber_map for JSON compat (JS expects string keys)
        return JSONResponse({
            "ok": True,
            "renumber_map": {str(k): v for k, v in renumber_map.items()},
            "new_count": new_count,
        })

    except (ValueError, KeyError) as exc:
        return JSONResponse({"error": str(exc)}, 400)
    except Exception as exc:
        # On failure, clean up the temp file if it still exists; original is untouched.
        if tmp_path:
            try:
                os.unlink(tmp_path)
            except Exception:
                pass
        if new_doc_mem:
            try:
                new_doc_mem.close()
            except Exception:
                pass
        return JSONResponse({"error": f"mutation failed: {exc}"}, 500)


@app.get("/thumb/{n}")
def get_thumb(n: int, case_id: str, rot: int = 0):
    case = _get_case(case_id)
    if not case:
        return JSONResponse({"error": "invalid case"}, 400)
    doc = case["doc"]
    if n < 1 or n > len(doc):
        return JSONResponse({"error": "page out of range"}, 404)
    cache = case["image_cache"]
    key = ("thumb", n, rot)
    if key not in cache:
        page = doc[n - 1]
        mat = fitz.Matrix(0.18, 0.18).prerotate(rot)
        pix = page.get_pixmap(matrix=mat)
        cache[key] = pix.tobytes("jpeg", jpg_quality=80)
    return Response(cache[key], media_type="image/jpeg")
