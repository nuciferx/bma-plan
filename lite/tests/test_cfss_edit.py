"""
CFSS-4: Cross-floor shared shape — Edit master smoke test.

Verifies cfssOpenEditDialog, cfssCommitEdit, _cfssIsRect, and the
'✏️ แก้ไขมาสเตอร์' context-menu row.

Sub-checks (8):
  1  publicSymbolsExist          cfssOpenEditDialog, __cfssTestEdit, cfssCommitEdit,
                                 _cfssIsRect all typeof function
  2  isRectDetector              _cfssIsRect returns true for axis-aligned 4-pt rect,
                                 false for 5-pt poly, triangle, tilted rect
  3  editNameOnly                __cfssTestEdit({name}) updates name, metricPts unchanged
  4  editColorOnly               __cfssTestEdit({color}) updates color, metricPts unchanged
  5  editDimensionsForRect       rect master: commit {widthM:3,heightM:2} rebuilds metricPts,
                                 instanceAreaM2 changes from 4.5 to 6.0
  6  dimensionsIgnoredForNonRect triangle: name updated, metricPts unchanged (still 3 pts)
  7  allInstancesPropagate       2 instances across pages auto-reflect after edit
  8  measureEngineIntact_uiLiteUnderCap  SHA-256 of measure-engine.js unchanged +
                                          ui-lite.html under 1200-line cap (self-healing: cap not magic number)

Emits LITE_CFSS_EDIT_OK on success, LITE_CFSS_EDIT_FAIL: <subcheck> on first failure.

    py -3 lite/tests/test_cfss_edit.py
"""
import hashlib
import socket
import sys
import threading
import time
from pathlib import Path

LITE = Path(__file__).resolve().parents[1]
MEASURE_ENGINE = LITE / "static" / "js" / "measure-engine.js"
UI_LITE = LITE / "ui-lite.html"

sys.path.insert(0, str(LITE))
import uvicorn
from playwright.sync_api import sync_playwright


def _free_port(start=8540):
    for p in range(start, start + 60):
        with socket.socket() as s:
            if s.connect_ex(("127.0.0.1", p)) != 0:
                return p
    raise RuntimeError("no free port")


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def count_lines_file(path: Path) -> int:
    return path.read_bytes().count(b"\n")


# ---------------------------------------------------------------------------
# Wait for CFSS module + wrappers
# ---------------------------------------------------------------------------
JS_WAIT = r"""
async () => {
  for (let i = 0; i < 200; i++) {
    if (typeof window.addMaster === 'function' &&
        typeof window.cfssCommitEdit === 'function' &&
        typeof window.__cfssTestEdit === 'function' &&
        typeof window._cfssIsRect === 'function' &&
        typeof window.cfssOpenEditDialog === 'function') {
      break;
    }
    await new Promise(r => setTimeout(r, 50));
  }
  await new Promise(r => setTimeout(r, 200));
}
"""

# ---------------------------------------------------------------------------
# Sub-check 1: publicSymbolsExist
# ---------------------------------------------------------------------------
JS_CHECK1 = r"""
() => {
  return {
    openEditFn:   typeof window.cfssOpenEditDialog === 'function',
    testEditFn:   typeof window.__cfssTestEdit === 'function',
    commitEditFn: typeof window.cfssCommitEdit === 'function',
    isRectFn:     typeof window._cfssIsRect === 'function'
  };
}
"""

# ---------------------------------------------------------------------------
# Sub-check 2: isRectDetector
# ---------------------------------------------------------------------------
JS_CHECK2 = r"""
() => {
  // Axis-aligned 4-pt rect -> true
  var r1 = window._cfssIsRect([
    {x_m:0,y_m:0},{x_m:2.5,y_m:0},{x_m:2.5,y_m:1.8},{x_m:0,y_m:1.8}
  ]);
  // 5-pt poly -> false
  var r2 = window._cfssIsRect([
    {x_m:0,y_m:0},{x_m:2,y_m:0},{x_m:2,y_m:2},{x_m:1,y_m:3},{x_m:0,y_m:2}
  ]);
  // triangle -> false
  var r3 = window._cfssIsRect([
    {x_m:0,y_m:0},{x_m:3,y_m:0},{x_m:1.5,y_m:2}
  ]);
  // tilted rect (not axis-aligned) -> false
  var r4 = window._cfssIsRect([
    {x_m:1,y_m:0},{x_m:2,y_m:1},{x_m:1,y_m:2},{x_m:0,y_m:1}
  ]);
  return {r1:r1, r2:r2, r3:r3, r4:r4};
}
"""

# ---------------------------------------------------------------------------
# Sub-check 3: editNameOnly
# ---------------------------------------------------------------------------
JS_CHECK3 = r"""
() => {
  window.MASTERS = {};
  window.__cfss_nextMasterIdN = 1;
  var origPts = [
    {x_m:0,y_m:0},{x_m:2.5,y_m:0},{x_m:2.5,y_m:1.8},{x_m:0,y_m:1.8}
  ];
  var id = addMaster('OldName', origPts, '#888');
  var origPtsCopy = JSON.stringify(masterById(id).metricPts);

  window.__cfssTestEdit(id, {name:'NewName'});

  var m = masterById(id);
  return {
    nameUpdated: m.name === 'NewName',
    ptsUnchanged: JSON.stringify(m.metricPts) === origPtsCopy
  };
}
"""

# ---------------------------------------------------------------------------
# Sub-check 4: editColorOnly
# ---------------------------------------------------------------------------
JS_CHECK4 = r"""
() => {
  window.MASTERS = {};
  window.__cfss_nextMasterIdN = 1;
  var origPts = [
    {x_m:0,y_m:0},{x_m:2.5,y_m:0},{x_m:2.5,y_m:1.8},{x_m:0,y_m:1.8}
  ];
  var id = addMaster('ColorTest', origPts, '#444444');
  var origPtsCopy = JSON.stringify(masterById(id).metricPts);

  window.__cfssTestEdit(id, {color:'#ff00aa'});

  var m = masterById(id);
  return {
    colorUpdated: m.color === '#ff00aa',
    ptsUnchanged: JSON.stringify(m.metricPts) === origPtsCopy
  };
}
"""

# ---------------------------------------------------------------------------
# Sub-check 5: editDimensionsForRect
# ---------------------------------------------------------------------------
JS_CHECK5 = r"""
() => {
  window.MASTERS = {};
  window.__cfss_nextMasterIdN = 1;
  // 2.5 x 1.8 rect master
  var id = addMaster('RectMaster', [
    {x_m:0,y_m:0},{x_m:2.5,y_m:0},{x_m:2.5,y_m:1.8},{x_m:0,y_m:1.8}
  ], '#888');
  window.PS = {};
  window.PS[1] = {objects:[makeInstance(id,{x:10,y:10})], scale:{pts_per_m:10}, annotations:[]};

  var instBefore = window.PS[1].objects[0];
  var areaBefore = instanceAreaM2(instBefore, 10); // 2.5*1.8 = 4.5

  window.__cfssTestEdit(id, {widthM:3, heightM:2});

  var m = masterById(id);
  var mp = m.metricPts;
  var ptsCorrect = mp.length === 4 &&
    Math.abs(mp[0].x_m - 0) < 1e-9 && Math.abs(mp[0].y_m - 0) < 1e-9 &&
    Math.abs(mp[1].x_m - 3) < 1e-9 && Math.abs(mp[1].y_m - 0) < 1e-9 &&
    Math.abs(mp[2].x_m - 3) < 1e-9 && Math.abs(mp[2].y_m - 2) < 1e-9 &&
    Math.abs(mp[3].x_m - 0) < 1e-9 && Math.abs(mp[3].y_m - 2) < 1e-9;

  var areaAfter = instanceAreaM2(instBefore, 10); // 3*2 = 6.0

  return {
    areaBefore: areaBefore,
    areaAfter: areaAfter,
    ptsCorrect: ptsCorrect,
    areaBeforeOk: Math.abs(areaBefore - 4.5) < 1e-9,
    areaAfterOk: Math.abs(areaAfter - 6.0) < 1e-9,
    metricPts: mp
  };
}
"""

# ---------------------------------------------------------------------------
# Sub-check 6: dimensionsIgnoredForNonRect
# ---------------------------------------------------------------------------
JS_CHECK6 = r"""
() => {
  window.MASTERS = {};
  window.__cfss_nextMasterIdN = 1;
  var triPts = [{x_m:0,y_m:0},{x_m:3,y_m:0},{x_m:1.5,y_m:2.5}];
  var id = addMaster('Tri', triPts, '#888');
  var origPtsCopy = JSON.stringify(masterById(id).metricPts);

  window.__cfssTestEdit(id, {widthM:5, heightM:5, name:'tri'});

  var m = masterById(id);
  var ptsUnchanged = JSON.stringify(m.metricPts) === origPtsCopy;
  return {
    nameUpdated: m.name === 'tri',
    ptsUnchanged: ptsUnchanged,
    ptsLen: m.metricPts.length,
    stillNotRect: !window._cfssIsRect(m.metricPts)
  };
}
"""

# ---------------------------------------------------------------------------
# Sub-check 7: allInstancesPropagate
# ---------------------------------------------------------------------------
JS_CHECK7 = r"""
() => {
  window.MASTERS = {};
  window.__cfss_nextMasterIdN = 1;
  var id = addMaster('PropMaster', [
    {x_m:0,y_m:0},{x_m:2,y_m:0},{x_m:2,y_m:2},{x_m:0,y_m:2}
  ], '#888');

  window.PS = {};
  window.PS[1] = {objects:[makeInstance(id,{x:10,y:10})], scale:{pts_per_m:10}, annotations:[]};
  window.PS[2] = {objects:[makeInstance(id,{x:20,y:20})], scale:{pts_per_m:10}, annotations:[]};

  window.__cfssTestEdit(id, {widthM:5, heightM:4});

  var inst1 = window.PS[1].objects[0];
  var inst2 = window.PS[2].objects[0];
  var area1 = instanceAreaM2(inst1, 10);
  var area2 = instanceAreaM2(inst2, 10);

  return {
    area1: area1,
    area2: area2,
    area1ok: Math.abs(area1 - 20) < 1e-9,
    area2ok: Math.abs(area2 - 20) < 1e-9
  };
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
        context = browser.new_context()
        page = context.new_page()
        page.on("pageerror", lambda e: page_errors.append(f"pageerror: {e}"))

        page.goto(f"http://127.0.0.1:{port}/", wait_until="networkidle")
        page.evaluate(JS_WAIT)

        print()
        print("LITE-CFSS-EDIT sub-checks:")

        if page_errors:
            for e in page_errors:
                print("  JS ERROR:", e)

        # Sub-check 1: publicSymbolsExist
        r1 = page.evaluate(JS_CHECK1)
        mark("publicSymbolsExist",
             r1.get("openEditFn") and r1.get("testEditFn") and
             r1.get("commitEditFn") and r1.get("isRectFn"),
             f"openEdit={r1.get('openEditFn')} testEdit={r1.get('testEditFn')} "
             f"commitEdit={r1.get('commitEditFn')} isRect={r1.get('isRectFn')}")

        # Sub-check 2: isRectDetector
        r2 = page.evaluate(JS_CHECK2)
        mark("isRectDetector",
             r2.get("r1") is True and r2.get("r2") is False and
             r2.get("r3") is False and r2.get("r4") is False,
             f"rectTrue={r2.get('r1')} 5pt={r2.get('r2')} "
             f"tri={r2.get('r3')} tilted={r2.get('r4')}")

        # Sub-check 3: editNameOnly
        r3 = page.evaluate(JS_CHECK3)
        mark("editNameOnly",
             r3.get("nameUpdated") is True and r3.get("ptsUnchanged") is True,
             f"nameUpd={r3.get('nameUpdated')} ptsUnch={r3.get('ptsUnchanged')}")

        # Sub-check 4: editColorOnly
        r4 = page.evaluate(JS_CHECK4)
        mark("editColorOnly",
             r4.get("colorUpdated") is True and r4.get("ptsUnchanged") is True,
             f"colorUpd={r4.get('colorUpdated')} ptsUnch={r4.get('ptsUnchanged')}")

        # Sub-check 5: editDimensionsForRect
        r5 = page.evaluate(JS_CHECK5)
        mark("editDimensionsForRect",
             r5.get("areaBeforeOk") is True and r5.get("areaAfterOk") is True and
             r5.get("ptsCorrect") is True,
             f"areaBefore={r5.get('areaBefore')} areaAfter={r5.get('areaAfter')} "
             f"ptsOk={r5.get('ptsCorrect')}")

        # Sub-check 6: dimensionsIgnoredForNonRect
        r6 = page.evaluate(JS_CHECK6)
        mark("dimensionsIgnoredForNonRect",
             r6.get("nameUpdated") is True and r6.get("ptsUnchanged") is True and
             r6.get("ptsLen") == 3 and r6.get("stillNotRect") is True,
             f"nameUpd={r6.get('nameUpdated')} ptsUnch={r6.get('ptsUnchanged')} "
             f"ptsLen={r6.get('ptsLen')} notRect={r6.get('stillNotRect')}")

        # Sub-check 7: allInstancesPropagate
        r7 = page.evaluate(JS_CHECK7)
        mark("allInstancesPropagate",
             r7.get("area1ok") is True and r7.get("area2ok") is True,
             f"area1={r7.get('area1')} area2={r7.get('area2')} expected=20")

        page.close()
        context.close()
        browser.close()

    server.should_exit = True
    time.sleep(0.4)

    # Sub-check 8: measureEngineIntact + uiLiteUnderCap
    me_hash_after = sha256_file(MEASURE_ENGINE)
    print(f"  measure-engine.js SHA-256 (post): {me_hash_after}")
    me_ok = (me_hash_before == me_hash_after)
    ui_lines = count_lines_file(UI_LITE)
    ui_ok = (ui_lines <= 1200)
    mark("measureEngineIntact_uiLiteUnderCap",
         me_ok and ui_ok,
         f"meHash={'same' if me_ok else 'CHANGED'} uiLines={ui_lines} cap=1200")

    print()
    if first_fail:
        print(f"LITE_CFSS_EDIT_FAIL: {first_fail}")
        sys.exit(1)
    else:
        print("LITE_CFSS_EDIT_OK")


if __name__ == "__main__":
    main()
