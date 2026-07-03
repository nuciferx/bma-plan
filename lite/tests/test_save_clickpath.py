"""
BUG-20260703-lite-save-wipes-data regression guard.

THE bug: Ctrl+S / mi-save wrote an EMPTY .bmaplan — every measurement and the
page scale wiped — because the save handler calls _pmCommit() before
serializing, and pageMgr's PS_by_id held deepCopy SNAPSHOTS taken at upload
time (when PS was empty). All drawing after upload mutated the live PS only;
_pmCommit projected the stale empty snapshots back over PS, then
buildPageStore() faithfully serialized the wiped state. Total silent data
loss on the core save path.

Why 72 green tests missed it: every save test called buildPageStore()
directly — the API path — never the mi-save CLICK path that runs _pmCommit
first. This guard drives the REAL handler.

Fix under test: projectToGlobals(livePS) resolves content from the live PS by
identity (baseline position via _initialIds; duplicates via dupSrc → deep
copy of source's live content; merged pages stay blank); _pmCommit passes PS.

Checks:
  C1 click-save keeps data — uploadPdf (real local-first path, pmSeed at
     upload with EMPTY PS) → draw poly + set scale AFTER seed → click
     #mi-save (dlBlob intercepted) → saved JSON has the poly + calibScale.
  C2 PS survives in-memory — after the click, live PS still has the objects
     and scale (the wipe also destroyed the in-memory session pre-fix).
  C3 round-trip — loadProto(saved JSON) → objects + scale restored.
  C4 duplicate content — pageMgr.duplicate carries the SOURCE's live
     (post-seed-drawn) content into the new page on commit, not the stale
     empty snapshot.

RED pre-fix: C1 fails with polys=0 / calibScale=null (exact journey-review
repro).

Emits LITE_SAVE_CLICKPATH_OK on success.

    py -3 lite/tests/test_save_clickpath.py
"""
import socket
import sys
import threading
import time
from pathlib import Path

LITE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LITE))

import fitz
import uvicorn
from playwright.sync_api import sync_playwright


def _free_port(start=9070):
    for p in range(start, start + 60):
        with socket.socket() as s:
            if s.connect_ex(("127.0.0.1", p)) != 0:
                return p
    raise RuntimeError("no free port")


def _make_pdf_bytes(pages=3, w=300, h=400):
    doc = fitz.open()
    for i in range(pages):
        pg = doc.new_page(width=w, height=h)
        pg.insert_text(fitz.Point(70, 200), f"SAVE {i+1}", fontsize=28)
    b = doc.tobytes()
    doc.close()
    return b


SC_SAVE = r"""
async () => {
  // ---- open through the REAL uploadPdf path (seeds pageMgr from EMPTY PS) ----
  var bytes = new Uint8Array(%PDF_BYTES%);
  var file = new File([bytes], "save-test.pdf", {type: "application/pdf"});
  await uploadPdf(file);
  if (!caseId) return {pass:false, err:"upload failed"};
  if (typeof pageMgr === "undefined" || !pageMgr) return {pass:false, err:"pageMgr not seeded"};

  // ---- draw AFTER the seed (the exact sequence that triggered the wipe) ----
  var pg = PS[1] || (PS[1] = {objects:[], scale:null, annotations:[]});
  pg.scale = {pts_per_m: 2};
  pg.objects.push({id: 9001, catId: "gfa", semanticTag: "gross_floor_area",
                   kind: "poly", counting: false, dimVisible: true,
                   pts: [{x:10,y:10},{x:110,y:10},{x:110,y:60},{x:10,y:60}]});
  pg.objects.push({id: 9002, catId: "count", semanticTag: "count_marker",
                   kind: "count", counting: true, pts: [{x:50,y:50}]});

  // ---- intercept the download sink (save = new Blob + createObjectURL + a.click),
  //      then CLICK the real save handler ----
  var savedJson = null;
  var _ocu = URL.createObjectURL.bind(URL);
  URL.createObjectURL = function(blob){
    try { blob.text().then(function(t){ savedJson = t; }); } catch(e) {}
    return "blob:intercepted";
  };

  await document.getElementById("mi-save").onclick();
  for (var i = 0; i < 40 && savedJson === null; i++) {
    await new Promise(function(r){ setTimeout(r, 50); });
  }
  URL.createObjectURL = _ocu;
  if (savedJson === null) return {pass:false, err:"save produced no blob"};

  var doc = JSON.parse(savedJson);
  var st1 = doc.pageStore && doc.pageStore["1"];
  var savedPolys  = st1 && st1.polys  ? st1.polys.length  : -1;
  var savedCounts = st1 && st1.counts ? st1.counts.length : -1;
  var savedCalib  = !!(st1 && st1.calibScale && st1.calibScale.pts_per_m === 2);
  var c1 = savedPolys === 1 && savedCounts === 1 && savedCalib;

  // C2: the in-memory session must also survive the click
  var c2 = PS[1] && PS[1].objects.length === 2 &&
           PS[1].scale && PS[1].scale.pts_per_m === 2;

  // C3: round-trip through the real load path
  PS = {}; curPage = 1;
  loadProto(JSON.parse(savedJson));
  var c3 = PS[1] && PS[1].objects && PS[1].objects.length === 2 &&
           PS[1].scale && PS[1].scale.pts_per_m === 2;

  // C4: duplicate carries the SOURCE's live content on commit
  //     (re-seed to a clean baseline, draw, dup page 1, commit with live PS)
  _pmSeed(undefined);
  PS[1] = {objects:[{id:9100, catId:"gfa", semanticTag:"gross_floor_area",
                     kind:"poly", counting:false,
                     pts:[{x:0,y:0},{x:20,y:0},{x:20,y:20},{x:0,y:20}]}],
           scale:{pts_per_m:1}, annotations:[]};
  pageMgr.duplicate(0);            // dup display page 1 → new page at position 2
  _pmCommit();                     // real Apply order: commit (pre-flush baseline)...
  pageMgr.applyFlush();            // ...THEN re-baseline (matches _pmuiApplyChanges)
  var c4 = PS[2] && PS[2].objects && PS[2].objects.length === 1 &&
           PS[2].objects[0].id === 9100 &&
           PS[1].objects.length === 1;

  return {savedPolys, savedCounts, savedCalib, c1, c2, c3, c4,
          pass: c1 && c2 && c3 && c4};
}
"""


def main():
    from server_lite import app as lite_app
    port = _free_port()
    cfg = uvicorn.Config(lite_app, host="127.0.0.1", port=port, log_level="error")
    server = uvicorn.Server(cfg)
    threading.Thread(target=server.run, daemon=True).start()
    time.sleep(2.0)

    pdf = _make_pdf_bytes()
    scenario = SC_SAVE.replace("%PDF_BYTES%", "[" + ",".join(str(b) for b in pdf) + "]")

    failures = []
    page_errors = []
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        pg = b.new_page()
        pg.on("pageerror", lambda e: page_errors.append(f"pageerror: {e}"))
        pg.goto(f"http://127.0.0.1:{port}/", wait_until="networkidle")
        time.sleep(0.6)

        print()
        print("LITE-SAVE-CLICKPATH checks:")
        try:
            result = pg.evaluate(scenario)
            ok = result.get("pass") is True
            print(f"  realSaveClickPathKeepsData          -> {'PASS' if ok else 'FAIL'}  {result}")
            if not ok:
                failures.append(f"result={result}")
        except Exception as ex:
            print(f"  realSaveClickPathKeepsData          -> EXCEPTION: {ex}")
            failures.append(f"threw: {ex}")
        pg.close()
        b.close()

    for e in page_errors:
        print("  JS ERROR:", e)

    server.should_exit = True
    time.sleep(0.4)

    if failures:
        for f in failures:
            print("FAIL:", f)
        print("LITE_SAVE_CLICKPATH_FAIL")
        sys.exit(1)
    print("LITE_SAVE_CLICKPATH_OK")


if __name__ == "__main__":
    main()
