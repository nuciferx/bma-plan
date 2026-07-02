"""
BUG-20260702-lite-pagerot-registration regression guard.

Bug: manual page rotate (pageRot) rotated the RASTER (PDF.js getViewport
rotation) but ptToScreen/screenToPt ignored pgRot — geometry drawn before a
rotate detached from the plan; geometry drawn while rotated was stored bound
to the un-rotated frame (right value, wrong location); /export-pdf-overlay
did not rotate either, so export != screen whenever pgRot != 0.

Fix (Fix A): getRot() now returns pageRot[pg]||0 and ptToScreen/screenToPt
route through the vendored, parity-tested pdfToC/cToPdf (which carry the
rotation branches). Export sends rot per page; server prerotates the raster
and maps coords through _rp (direction verified empirically vs prerotate).

Checks:
  SC1 registration  — with pageRot=90/180/270, ptToScreen(v) equals the
                      independently-computed quadrant mapping (90: x'=(H-y)RS,
                      y'=xRS etc.); screenToPt is an exact inverse (1e-9);
                      RED on pre-fix code (old ptToScreen ignored pgRot).
  SC2 area+roundtrip— polyMetricsAnyShape area identical before/after rotate
                      (pts never mutated); pageRotations survives a .bmaplan
                      build->loadProto round-trip and getRot reflects it.
  SC3 export WYSIWYG— upload real 300x400 PDF, export overlay with rot:90 ->
                      output page dims swapped (600x450 @ RS=1.5) and the
                      polyline stroke found at the rotated location.

Emits LITE_PAGEROT_REG_OK on success.

    py -3 lite/tests/test_pagerot_registration.py
"""
import socket
import sys
import threading
import time
from pathlib import Path

LITE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LITE))

import fitz
import requests
import uvicorn
from playwright.sync_api import sync_playwright


def _free_port(start=8650):
    for p in range(start, start + 60):
        with socket.socket() as s:
            if s.connect_ex(("127.0.0.1", p)) != 0:
                return p
    raise RuntimeError("no free port")


SC_REGISTRATION = r"""
async () => {
  var _P = 99;
  PS = {}; PS[_P] = {objects:[], scale:{pts_per_m:1}, annotations:[]};
  curPage = _P;
  pageData = {size:{orig_w_pt:300, orig_h_pt:400}};
  if (typeof pageRot === "undefined") window.pageRot = {};
  V.k = 1; V.ox = 0; V.oy = 0; V.rot = 0;

  var W = 300, H = 400;
  var rect = {id:1, catId:'gfa', semanticTag:'gross_floor_area', kind:'poly',
              counting:false, pts:[{x:10,y:10},{x:50,y:10},{x:50,y:40},{x:10,y:40}]};
  PS[_P].objects.push(rect);

  function expected(p, rot){
    if (rot === 90)  return {x:(H - p.y) * RS, y: p.x * RS};
    if (rot === 180) return {x:(W - p.x) * RS, y:(H - p.y) * RS};
    if (rot === 270) return {x: p.y * RS,      y:(W - p.x) * RS};
    return {x: p.x * RS, y: p.y * RS};
  }

  var areaBefore = polyMetricsAnyShape(rect, _P).area;   // 40x30 = 1200 m2 @ 1ppm

  var regFail = null, invFail = null;
  [0, 90, 180, 270].forEach(function(rot){
    pageRot[_P] = rot;
    rect.pts.forEach(function(p){
      var s = ptToScreen(p), e = expected(p, rot);
      if (Math.abs(s.x - e.x) > 1e-9 || Math.abs(s.y - e.y) > 1e-9)
        regFail = regFail || {rot:rot, p:p, got:s, want:e};
      var b = screenToPt(s.x, s.y);
      if (Math.abs(b.x - p.x) > 1e-9 || Math.abs(b.y - p.y) > 1e-9)
        invFail = invFail || {rot:rot, p:p, back:b};
    });
  });

  pageRot[_P] = 90;
  var areaAfter = polyMetricsAnyShape(rect, _P).area;
  var areaInvariant = Math.abs(areaAfter - areaBefore) < 1e-12 && Math.abs(areaBefore - 1200) < 1e-9;

  // SC2: pageRotations round-trip through the real loadProto path
  var doc = {
    version: 1, app: 'bma-plan-lite', pdfName: 'test.pdf', totalPages: 99,
    pageStore: buildPageStore(),
    pageRotations: {99: 90},
    pageTags: {}, pageNames: {}, projectInfo: {name:''},
    siteOrientation: {}, excludedPages: [],
    pageFloorKind: {}, pageFloorNum: {},
    liteLayers: layersInOrder().map(function(l){ return {id:l.id,name:l.name,color:l.color,role:l.role,order:l.order,parentId:l.parentId!==undefined?l.parentId:null}; }),
    liteGroups: foldersInOrder().map(function(f){ return {id:f.id,name:f.name,color:f.color,parentId:f.parentId!==undefined?f.parentId:null,order:f.order}; }),
    reportVars: []
  };
  var json = JSON.stringify(doc);
  pageRot = {};                                    // wipe
  loadProto(JSON.parse(json));
  curPage = _P;
  pageData = {size:{orig_w_pt:300, orig_h_pt:400}};
  var rotRestored = getRot(_P) === 90;
  var pAfterLoad = ptToScreen({x:10, y:10});
  var e90 = {x:(H - 10) * RS, y:10 * RS};
  var regAfterLoad = Math.abs(pAfterLoad.x - e90.x) < 1e-9 && Math.abs(pAfterLoad.y - e90.y) < 1e-9;

  return {
    areaBefore, areaAfter, regFail, invFail,
    areaInvariant, rotRestored, regAfterLoad,
    pass: !regFail && !invFail && areaInvariant && rotRestored && regAfterLoad
  };
}
"""


failures = []


def check(label, cond, detail=""):
    if cond:
        print(f"  PASS {label}")
    else:
        msg = f"FAIL {label}" + (f": {detail}" if detail else "")
        failures.append(msg)
        print(f"  {msg}")


def _make_pdf_bytes(w=300, h=400):
    doc = fitz.open()
    pg = doc.new_page(width=w, height=h)
    pg.insert_text(fitz.Point(150, 200), "X", fontsize=18)
    b = doc.tobytes()
    doc.close()
    return b


def sc3_export_wysiwyg(base):
    RS = 1.5
    up = requests.post(base + "/upload",
                       files={"file": ("t.pdf", _make_pdf_bytes(), "application/pdf")},
                       timeout=30)
    check("SC3 upload 200", up.status_code == 200, f"got {up.status_code}")
    cid = up.json().get("case_id")
    payload = {"case_id": cid, "pages": {"1": {
        "rot": 90,
        "objects": [{"kind": "poly", "counting": False, "color": "#ff0000",
                     "pts": [{"x": 10, "y": 10}, {"x": 50, "y": 10},
                             {"x": 50, "y": 40}, {"x": 10, "y": 40}]}],
        "annotations": []}}}
    r = requests.post(base + "/export-pdf-overlay", json=payload, timeout=30)
    check("SC3 export 200", r.status_code == 200, f"got {r.status_code}: {r.text[:200]}")
    if r.status_code != 200:
        return
    out = fitz.open(stream=r.content, filetype="pdf")
    pg = out[0]
    # 300x400 pt page @ RS=1.5, rot 90 -> output page 600x450
    dims_ok = abs(pg.rect.width - 600) < 1.0 and abs(pg.rect.height - 450) < 1.0
    check("SC3 page dims swapped (600x450)", dims_ok, f"got {pg.rect.width}x{pg.rect.height}")
    # vertex (10,10)pt -> img (15,15) -> rot90 (H-y, x) with H=600 -> (585, 15)
    pix = pg.get_pixmap(matrix=fitz.Matrix(1, 1))
    found = False
    for dx in range(-5, 6):
        for dy in range(-5, 6):
            x, y = 585 + dx, 15 + dy
            if 0 <= x < pix.width and 0 <= y < pix.height:
                c = pix.pixel(x, y)
                if c[0] > 150 and c[1] < 120 and c[2] < 120:
                    found = True
                    break
        if found:
            break
    check("SC3 stroke at rotated vertex (585,15)", found)
    out.close()


def main():
    from server_lite import app as lite_app
    port = _free_port()
    cfg = uvicorn.Config(lite_app, host="127.0.0.1", port=port, log_level="error")
    server = uvicorn.Server(cfg)
    threading.Thread(target=server.run, daemon=True).start()
    time.sleep(2.0)
    base = f"http://127.0.0.1:{port}"

    page_errors = []
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        pg = b.new_page()
        pg.on("pageerror", lambda e: page_errors.append(f"pageerror: {e}"))
        pg.goto(base + "/", wait_until="networkidle")
        time.sleep(0.6)

        print()
        print("LITE-PAGEROT-REGISTRATION checks:")
        try:
            result = pg.evaluate(SC_REGISTRATION)
            check("SC1+SC2 registration/area/roundtrip", result.get("pass") is True, str(result))
        except Exception as ex:
            check("SC1+SC2 registration/area/roundtrip", False, f"threw: {ex}")
        pg.close()
        b.close()

    sc3_export_wysiwyg(base)

    for e in page_errors:
        print("  JS ERROR:", e)

    server.should_exit = True
    time.sleep(0.4)

    if failures:
        print()
        for f in failures:
            print("FAIL:", f)
        print("LITE_PAGEROT_REG_FAIL")
        sys.exit(1)
    print()
    print("LITE_PAGEROT_REG_OK")


if __name__ == "__main__":
    main()
