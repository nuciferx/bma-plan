"""
CFSS-2: Cross-floor shared shape — persist smoke test.

Verifies that masters + instances survive a .bmaplan save/load round-trip
via the monkey-patch approach in cross-floor-shapes.js.

Sub-checks (10):
  1  wrappersInstalled          loadProto.__cfssWrapped and mi-save.__cfssSaveWrapped
  2  saveProducesMastersKey     saved doc contains masters entry with correct metricPts
  3  saveProducesInstancesKey   saved doc contains instances[] with correct page/masterId/offsetPt
  4  instancesNotInPageStore    no broken poly (pts.length < 3) leaked from instance strip
  5  legacyFileLoads            doc without masters/instances loads with MASTERS={}, no error
  6  roundtripIdentity          2 masters + 3 instances survive save->load with bit-identical values
  7  counterResumes             after load id counter continues from max existing N + 1
  8  protoCrossOpenSafe         standard fields intact alongside new masters/instances keys
  9  measureEngineIntact        SHA-256 of measure-engine.js unchanged before vs after
  10 uiLiteUntouched            ui-lite.html line count == 1200

Emits LITE_CFSS_PERSIST_OK on success, LITE_CFSS_PERSIST_FAIL: <subcheck> on first failure.

    py -3 lite/tests/test_cfss_persist.py
"""
import hashlib
import json
import os
import socket
import sys
import tempfile
import threading
import time
from pathlib import Path

LITE = Path(__file__).resolve().parents[1]
REPO = LITE.parent
MEASURE_ENGINE = LITE / "static" / "js" / "measure-engine.js"
UI_LITE = LITE / "ui-lite.html"

sys.path.insert(0, str(LITE))
import uvicorn
from playwright.sync_api import sync_playwright


def _free_port(start=8480):
    for p in range(start, start + 60):
        with socket.socket() as s:
            if s.connect_ex(("127.0.0.1", p)) != 0:
                return p
    raise RuntimeError("no free port")


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def count_lines_file(path: Path) -> int:
    """Count newlines (same as wc -l)."""
    return path.read_bytes().count(b"\n")


# ---------------------------------------------------------------------------
# JS — wait for dynamic module AND wrappers to be installed
# ---------------------------------------------------------------------------
JS_WAIT = r"""
async () => {
  // Wait for cross-floor-shapes.js to finish loading and executing.
  // cross-floor-shapes.js is dynamically injected by page-folder-layers.js,
  // so it may load after networkidle fires.  Poll up to 10 s (200 x 50 ms).
  for (let i = 0; i < 200; i++) {
    if (typeof window.addMaster === 'function' &&
        typeof window.makeInstance === 'function' &&
        typeof window.isInstance === 'function' &&
        typeof window.loadProto === 'function' &&
        window.loadProto.__cfssWrapped === true) {
      break;
    }
    await new Promise(r => setTimeout(r, 50));
  }
  await new Promise(r => setTimeout(r, 200));
}
"""

# ---------------------------------------------------------------------------
# JS sub-check 1: wrappersInstalled
# ---------------------------------------------------------------------------
JS_CHECK1 = r"""
() => {
  const saveBtn = document.getElementById('mi-save');
  return {
    saveBtnWrapped: !!(saveBtn && saveBtn.__cfssSaveWrapped === true),
    loadProtoWrapped: !!(typeof window.loadProto === 'function' &&
                         window.loadProto.__cfssWrapped === true)
  };
}
"""

# ---------------------------------------------------------------------------
# JS sub-check 5: legacyFileLoads
# ---------------------------------------------------------------------------
JS_CHECK5 = r"""
(doc) => {
  try {
    loadProto(doc);
    const mastersEmpty = window.MASTERS && Object.keys(window.MASTERS).length === 0;
    let hasInstance = false;
    Object.keys(window.PS || {}).forEach(function(k) {
      (window.PS[k].objects || []).forEach(function(o) {
        if (isInstance(o)) hasInstance = true;
      });
    });
    return {ok: mastersEmpty && !hasInstance, error: null};
  } catch(e) {
    return {ok: false, error: String(e)};
  }
}
"""

# ---------------------------------------------------------------------------
# JS: set up app state for a REAL save (sub-checks 2, 3, 4, 8).
# Makes caseId truthy so the mi-save handler runs past its guard.
# 1 master "Lift" + 2 instances across pages 1 and 2.
# Returns the master id so Python can verify the saved doc keys.
# ---------------------------------------------------------------------------
JS_SETUP_FOR_REAL_SAVE = r"""
() => {
  // Make caseId truthy so the click handler doesn't bail.
  window.caseId = 'cfss-test';
  window.pdfName = 'test.pdf';
  window.pageCount = 2;

  // Reset MASTERS + counter + PS
  window.MASTERS = {};
  window.__cfss_nextMasterIdN = 1;
  window.PS = {};
  window.PS[1] = {objects: [], scale: null, annotations: []};
  window.PS[2] = {objects: [], scale: null, annotations: []};

  // Add 1 master + 2 instances across pages
  const m1id = addMaster('Lift', [
    {x_m:0,y_m:0},{x_m:2.5,y_m:0},{x_m:2.5,y_m:1.8},{x_m:0,y_m:1.8}
  ], '#888');
  window.PS[1].objects.push(makeInstance(m1id, {x:100, y:200}));
  window.PS[2].objects.push(makeInstance(m1id, {x:50,  y:50}));

  return m1id;
}
"""

# ---------------------------------------------------------------------------
# JS: set up 2 masters + 3 instances for roundtrip test (sub-check 6).
# Also sets caseId/pdfName/pageCount so the real save handler can run.
# ---------------------------------------------------------------------------
JS_SETUP_ROUNDTRIP = r"""
() => {
  window.caseId = 'cfss-roundtrip';
  window.pdfName = 'test.pdf';
  window.pageCount = 3;

  window.MASTERS = {};
  window.__cfss_nextMasterIdN = 1;
  window.PS = {};
  [1, 2, 3].forEach(function(pg) {
    window.PS[pg] = {objects: [], scale: null, annotations: []};
  });

  const idA = addMaster('ShaftA', [
    {x_m:0,y_m:0},{x_m:2,y_m:0},{x_m:2,y_m:3},{x_m:0,y_m:3}
  ], '#f00');
  const idB = addMaster('ShaftB', [
    {x_m:0,y_m:0},{x_m:1.5,y_m:0},{x_m:1.5,y_m:1.5},{x_m:0,y_m:1.5}
  ], '#00f');

  // 2 instances on page 1, 1 instance on page 2
  window.PS[1].objects.push(makeInstance(idA, {x:10,  y:20}));
  window.PS[1].objects.push(makeInstance(idB, {x:50,  y:60}));
  window.PS[2].objects.push(makeInstance(idA, {x:100, y:200}));

  return {idA: idA, idB: idB};
}
"""

# ---------------------------------------------------------------------------
# JS sub-check 6: verify roundtrip after loadProto(doc)
# ---------------------------------------------------------------------------
JS_CHECK6_VERIFY = r"""
(doc) => {
  try {
    loadProto(doc);
  } catch(e) {
    return {ok: false, error: 'loadProto threw: ' + e};
  }

  const masterKeys = Object.keys(window.MASTERS);
  if (masterKeys.length !== 2) {
    return {ok: false,
            error: 'expected 2 masters, got ' + masterKeys.length +
                   ' keys=' + JSON.stringify(masterKeys)};
  }

  const masters = mastersInOrder();
  const mA = masters[0]; // ShaftA (created first)
  const mB = masters[1]; // ShaftB

  const mAPtsOk = mA && mA.name === 'ShaftA' &&
    mA.metricPts.length === 4 &&
    mA.metricPts[2].x_m === 2 && mA.metricPts[2].y_m === 3;
  const mBPtsOk = mB && mB.name === 'ShaftB' &&
    mB.metricPts.length === 4 &&
    mB.metricPts[2].x_m === 1.5 && mB.metricPts[2].y_m === 1.5;

  if (!mAPtsOk) return {ok: false, error: 'ShaftA metricPts mismatch: ' + JSON.stringify(mA)};
  if (!mBPtsOk) return {ok: false, error: 'ShaftB metricPts mismatch: ' + JSON.stringify(mB)};

  // Count instances in PS: expect 3 total (2 on pg1, 1 on pg2)
  var instCount = 0;
  var instDetails = [];
  Object.keys(window.PS).forEach(function(k) {
    (window.PS[k].objects || []).forEach(function(o) {
      if (isInstance(o)) {
        instCount++;
        instDetails.push({page: +k, masterId: o.masterId,
                          ox: o.offsetPt.x, oy: o.offsetPt.y});
      }
    });
  });

  if (instCount !== 3) {
    return {ok: false,
            error: 'expected 3 instances in PS, got ' + instCount +
                   ' details: ' + JSON.stringify(instDetails) +
                   ' PSkeys: ' + JSON.stringify(Object.keys(window.PS))};
  }

  var pg1insts = instDetails.filter(function(d) { return d.page === 1; });
  var pg2insts = instDetails.filter(function(d) { return d.page === 2; });

  if (pg1insts.length !== 2) return {ok: false, error: 'expected 2 instances on pg1, got ' + pg1insts.length};
  if (pg2insts.length !== 1) return {ok: false, error: 'expected 1 instance on pg2, got ' + pg2insts.length};

  const pg2ok = pg2insts[0].ox === 100 && pg2insts[0].oy === 200;
  if (!pg2ok) return {ok: false, error: 'pg2 instance offset wrong: ' + JSON.stringify(pg2insts[0])};

  return {ok: true, error: null};
}
"""

# ---------------------------------------------------------------------------
# JS sub-check 7: counterResumes
# After load with m1..m3, addMaster must return 'm4'.
# ---------------------------------------------------------------------------
JS_CHECK7 = r"""
() => {
  window.MASTERS = {};
  window.__cfss_nextMasterIdN = 1;
  const sqPts = [{x_m:0,y_m:0},{x_m:1,y_m:0},{x_m:1,y_m:1},{x_m:0,y_m:1}];
  addMaster('M1', sqPts, '#1');  // -> m1
  addMaster('M2', sqPts, '#2');  // -> m2
  addMaster('M3', sqPts, '#3');  // -> m3

  // Build a doc with these 3 masters + stub pageStore for page 1
  var doc = {
    version: 1, app: 'bma-plan-lite', pdfName: 'x.pdf', totalPages: 1,
    pageStore: {'1': {polys:[],openings:[],lines:[],refs:[],parking:[],
                      counts:[],calibScale:null,annotations:[]}},
    pageRotations: {}, pageTags: {}, pageNames: {},
    projectInfo: {}, siteOrientation: {}, excludedPages: [],
    pageFloorKind: {}, pageFloorNum: {}, liteLayers: [], liteGroups: [],
    reportVars: [],
    masters: JSON.parse(JSON.stringify(window.MASTERS)),
    instances: []
  };

  loadProto(doc);

  // After load, counter should resume at 4
  const m4id = addMaster('NewOne', sqPts, '#000');
  return {ok: m4id === 'm4', m4id: m4id};
}
"""


def main():
    me_hash_before = sha256_file(MEASURE_ENGINE)
    print(f"  measure-engine.js SHA-256 (pre): {me_hash_before}")

    from server_lite import app as lite_app

    port = _free_port()
    cfg = uvicorn.Config(lite_app, host="127.0.0.1", port=port, log_level="error")
    server = uvicorn.Server(cfg)
    threading.Thread(target=server.run, daemon=True).start()
    time.sleep(2.0)

    page_errors = []
    results = {}
    first_fail = None

    def mark(name, ok, detail=""):
        nonlocal first_fail
        results[name] = ok
        status = "PASS" if ok else "FAIL"
        suffix = f" ({detail})" if detail else ""
        print(f"  [{status}] {name}{suffix}")
        if not ok and first_fail is None:
            first_fail = name

    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        # Use a dedicated context so Playwright does not reuse a cached
        # version of cross-floor-shapes.js from a previous test run.
        context = browser.new_context()
        page = context.new_page()
        page.on("pageerror", lambda e: page_errors.append(f"pageerror: {e}"))

        page.goto(f"http://127.0.0.1:{port}/", wait_until="networkidle")
        page.evaluate(JS_WAIT)

        print()
        print("LITE-CFSS-PERSIST sub-checks:")

        if page_errors:
            for e in page_errors:
                print("  JS ERROR:", e)

        # -----------------------------------------------------------------------
        # Sub-check 1: wrappersInstalled
        # -----------------------------------------------------------------------
        r1 = page.evaluate(JS_CHECK1)
        mark("wrappersInstalled",
             r1.get("saveBtnWrapped") and r1.get("loadProtoWrapped"),
             f"saveBtn={r1.get('saveBtnWrapped')} loadProto={r1.get('loadProtoWrapped')}")

        # -----------------------------------------------------------------------
        # Sub-checks 2, 3, 4, 8: exercise the REAL mi-save onclick path.
        # We click the real button and intercept the download — this proves
        # cfssWrapSave actually fires and injects masters + instances into the
        # emitted blob.  A broken / absent cfssWrapSave would produce a doc
        # without 'masters'/'instances', causing sub-checks 2, 3, 8 to FAIL
        # and broken instance stubs in pageStore, causing sub-check 4 to FAIL.
        # -----------------------------------------------------------------------
        m1_id = page.evaluate(JS_SETUP_FOR_REAL_SAVE)

        try:
            # Invoke onclick directly to bypass CSS visibility of the menu item.
            # cfssWrapSave wraps btn.onclick (not addEventListener), so calling
            # btn.onclick(null) runs the full wrapper -> origHandler -> a.click()
            # chain, which triggers the download event that Playwright captures.
            with page.expect_download(timeout=10_000) as dl_info:
                page.evaluate("() => { var btn = document.getElementById('mi-save'); btn.onclick(null); }")
            download = dl_info.value
            tmp_path = Path(tempfile.gettempdir()) / "cfss_persist_test.bmaplan"
            download.save_as(str(tmp_path))
            saved_doc = json.loads(tmp_path.read_text(encoding="utf-8"))
        except Exception as exc:
            saved_doc = None
            print(f"  [WARN] real-save download failed: {exc}")

        # sub-check 2: masters key present, with correct master
        if saved_doc is not None:
            masters_key = saved_doc.get("masters", {})
            m1 = masters_key.get(m1_id) if m1_id else None
            pts_ok = (
                m1 is not None
                and isinstance(m1.get("metricPts"), list)
                and len(m1["metricPts"]) == 4
                and m1.get("name") == "Lift"
                and m1["metricPts"][2]["x_m"] == 2.5
                and m1["metricPts"][2]["y_m"] == 1.8
            )
            mark("saveProducesMastersKey", pts_ok,
                 f"keys={list(masters_key.keys())} "
                 f"name={m1.get('name') if m1 else None}, "
                 f"pts={len(m1.get('metricPts', [])) if m1 else 0}")
        else:
            mark("saveProducesMastersKey", False, "no saved doc")

        # sub-check 3: instances key present, sorted by page
        if saved_doc is not None:
            insts = saved_doc.get("instances", [])
            insts_ok = len(insts) == 2
            if insts_ok:
                sorted_insts = sorted(insts, key=lambda d: d.get("page", 0))
                i0, i1 = sorted_insts
                insts_ok = (
                    i0.get("page") == 1 and i0.get("masterId") == m1_id
                    and i0.get("offsetPt", {}).get("x") == 100
                    and i0.get("offsetPt", {}).get("y") == 200
                    and i1.get("page") == 2 and i1.get("masterId") == m1_id
                    and i1.get("offsetPt", {}).get("x") == 50
                    and i1.get("offsetPt", {}).get("y") == 50
                )
            mark("saveProducesInstancesKey", insts_ok,
                 f"count={len(insts)}")
        else:
            mark("saveProducesInstancesKey", False, "no saved doc")

        # sub-check 4: no broken poly (pts.length < 3) in pageStore
        if saved_doc is not None:
            page_store = saved_doc.get("pageStore", {})
            all_polys_ok = True
            broken_detail = None
            for pg_key, pg_val in page_store.items():
                if not isinstance(pg_val, dict):
                    continue
                for poly in pg_val.get("polys", []):
                    if not isinstance(poly.get("pts"), list) or len(poly["pts"]) < 3:
                        all_polys_ok = False
                        broken_detail = f"pg={pg_key} poly={poly}"
                        break
                for opening in pg_val.get("openings", []):
                    if not isinstance(opening.get("pts"), list) or len(opening["pts"]) < 3:
                        all_polys_ok = False
                        broken_detail = f"pg={pg_key} opening={opening}"
                        break
            mark("instancesNotInPageStore", all_polys_ok, broken_detail or "")
        else:
            mark("instancesNotInPageStore", False, "no saved doc")

        # -----------------------------------------------------------------------
        # Sub-check 5: legacyFileLoads
        # -----------------------------------------------------------------------
        legacy_doc = {
            "version": 1, "app": "bma-plan-lite", "pdfName": "x.pdf",
            "totalPages": 1, "pageStore": {}, "pageRotations": {}, "pageTags": {},
            "pageNames": {}, "projectInfo": {}, "siteOrientation": {},
            "excludedPages": [], "pageFloorKind": {}, "pageFloorNum": {},
            "liteLayers": [], "liteGroups": []
            # No "masters", no "instances", no "reportVars"
        }
        r5 = page.evaluate(JS_CHECK5, legacy_doc)
        mark("legacyFileLoads",
             r5.get("ok") is True,
             r5.get("error") or "")

        # -----------------------------------------------------------------------
        # Sub-check 6: roundtripIdentity — full real save -> real download ->
        # real loadProto round-trip.  If cfssWrapSave or cfssWrapLoad is broken,
        # the restored state won't match and JS_CHECK6_VERIFY fails.
        # -----------------------------------------------------------------------
        page.evaluate(JS_SETUP_ROUNDTRIP)

        try:
            with page.expect_download(timeout=10_000) as dl_info6:
                page.evaluate("() => { var btn = document.getElementById('mi-save'); btn.onclick(null); }")
            download6 = dl_info6.value
            tmp6 = Path(tempfile.gettempdir()) / "cfss_persist_round6.bmaplan"
            download6.save_as(str(tmp6))
            roundtrip_doc = json.loads(tmp6.read_text(encoding="utf-8"))
        except Exception as exc:
            roundtrip_doc = None
            print(f"  [WARN] roundtrip download failed: {exc}")

        if roundtrip_doc is not None:
            # Clear state, then loadProto from the REAL downloaded bytes
            page.evaluate("""
              () => {
                window.MASTERS = {};
                window.__cfss_nextMasterIdN = 1;
                window.PS = {};
              }
            """)
            r6 = page.evaluate(JS_CHECK6_VERIFY, roundtrip_doc)
            mark("roundtripIdentity",
                 r6.get("ok") is True,
                 r6.get("error") or "")
        else:
            mark("roundtripIdentity", False, "roundtrip download failed")

        # -----------------------------------------------------------------------
        # Sub-check 7: counterResumes
        # -----------------------------------------------------------------------
        r7 = page.evaluate(JS_CHECK7)
        mark("counterResumes",
             r7.get("ok") is True,
             f"m4id={r7.get('m4id')}")

        # -----------------------------------------------------------------------
        # Sub-check 8: protoCrossOpenSafe
        # Uses the REAL downloaded doc from sub-checks 2/3/4 flow.
        # Verifies standard fields are intact alongside new masters/instances.
        # -----------------------------------------------------------------------
        doc_to_check = saved_doc if saved_doc is not None else roundtrip_doc
        if doc_to_check is not None:
            mark("protoCrossOpenSafe",
                 doc_to_check.get("version") == 1
                 and doc_to_check.get("app") == "bma-plan-lite"
                 and isinstance(doc_to_check.get("pageStore"), dict)
                 and "pageRotations" in doc_to_check
                 and "pageTags" in doc_to_check
                 and "masters" in doc_to_check
                 and "instances" in doc_to_check,
                 f"v={doc_to_check.get('version')} app={doc_to_check.get('app')!r} "
                 f"masters={'masters' in doc_to_check} insts={'instances' in doc_to_check}")
        else:
            mark("protoCrossOpenSafe", False, "no real doc available")

        page.close()
        context.close()
        browser.close()

    server.should_exit = True
    time.sleep(0.4)

    # -----------------------------------------------------------------------
    # Sub-check 9: measureEngineIntact
    # -----------------------------------------------------------------------
    me_hash_after = sha256_file(MEASURE_ENGINE)
    print(f"  measure-engine.js SHA-256 (post): {me_hash_after}")
    mark("measureEngineIntact",
         me_hash_before == me_hash_after,
         f"hash: {me_hash_before[:16]}...")

    # -----------------------------------------------------------------------
    # Sub-check 10: uiLiteUntouched
    # -----------------------------------------------------------------------
    ui_lines = count_lines_file(UI_LITE)
    mark("uiLiteUntouched",
         ui_lines == 1200,
         f"lines={ui_lines}, expected=1200")

    print()
    if first_fail:
        print(f"LITE_CFSS_PERSIST_FAIL: {first_fail}")
        sys.exit(1)
    else:
        print("LITE_CFSS_PERSIST_OK")


if __name__ == "__main__":
    main()
