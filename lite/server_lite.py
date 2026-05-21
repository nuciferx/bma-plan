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
import time
import uuid
from pathlib import Path

import fitz  # PyMuPDF
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles

LITE_VERSION = "0.2.0-LITE-1+2+3"
SCHEMA_VERSION = 1
RS = 1.5                       # render scale — MUST match proto (coord contract)
MAX_UPLOAD_BYTES = 80 * 1024 * 1024
MAX_IMAGE_CACHE = 24
CASE_TTL_SEC = 3600

_BASE_DIR = Path(__file__).resolve().parent
_STATIC_DIR = _BASE_DIR / "static"
_UI_FILE = _BASE_DIR / "ui-lite.html"

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
