"""
CFSS-MOVE: Cross-floor shared shape — drag-to-reposition smoke test.

Verifies:
  (A) extract is invisible — cfss-dialogs.js loaded, all dialog symbols present.
  (B) drag mutates instance.offsetPt correctly (programmatic via __cfssTestDrag).

Sub-checks (7):
  1  dragListenerInstalled       cv.__cfssDragListened === true AND __cfssTestDrag function
  2  extractedDialogsAvailable   cfssOpenPromoteDialog, cfssOpenEditDialog, cfssCommitPromote,
                                  cfssCommitEdit all on window; __cfss_dialogs_loaded__ === true
  3  dragMovesInstance           __cfssTestDrag(mid, 50, -30) → offsetPt={x:150,y:70}; dirty=true;
                                  master.metricPts unchanged
  4  dragDoesNotMutateMaster     JSON.stringify(master.metricPts) identical before/after drag
  5  dragSurvivesSaveLoad        drag to (200,100), save, clear, loadProto → instance offsetPt persists
  6  dragOnInstanceOnlyClickIntercepted  structural: cfssPickInstance returns null far outside,
                                          returns instance at center
  7  measureEngineIntact_uiLiteUntouched_capsHealthy
                                  SHA-256 measure-engine.js unchanged; wc -l ui-lite=1200;
                                  cross-floor-shapes.js ≤ 1000; cfss-dialogs.js ≤ 1000

Emits LITE_CFSS_DRAG_OK on success.

    py -3 lite/tests/test_cfss_drag.py
"""
import hashlib
import json
import socket
import sys
import tempfile
import threading
import time
from pathlib import Path

LITE = Path(__file__).resolve().parents[1]
MEASURE_ENGINE = LITE / "static" / "js" / "measure-engine.js"
UI_LITE = LITE / "ui-lite.html"
CFSS_JS = LITE / "static" / "js" / "cross-floor-shapes.js"
CFSS_DLG_JS = LITE / "static" / "js" / "cfss-dialogs.js"

sys.path.insert(0, str(LITE))
import uvicorn
from playwright.sync_api import sync_playwright


def _free_port(start=8560):
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
# JS: Wait for CFSS + CFSS-DIALOGS modules and wrappers to be installed.
# ---------------------------------------------------------------------------
JS_WAIT = r"""
async () => {
  // Wait for cross-floor-shapes.js
  for (let i = 0; i < 200; i++) {
    if (typeof window.addMaster === 'function' &&
        typeof window.makeInstance === 'function' &&
        typeof window.isInstance === 'function' &&
        typeof window.__cfss_loaded__ === 'boolean' &&
        window.__cfss_loaded__ === true) {
      break;
    }
    await new Promise(r => setTimeout(r, 50));
  }
  // Wait for cfss-dialogs.js
  for (let i = 0; i < 200; i++) {
    if (typeof window.__cfss_dialogs_loaded__ === 'boolean' &&
        window.__cfss_dialogs_loaded__ === true &&
        typeof window.cfssOpenPromoteDialog === 'function' &&
        typeof window.cfssOpenEditDialog === 'function') {
      break;
    }
    await new Promise(r => setTimeout(r, 50));
  }
  // Wait for draw/pick wrappers (DOMContentLoaded may fire before inline script)
  for (let i = 0; i < 200; i++) {
    if (typeof window.draw === 'function' && window.draw.__cfssWrapped === true &&
        typeof window.pick === 'function' && window.pick.__cfssWrapped === true &&
        typeof window.__cfssTestDrag === 'function') {
      break;
    }
    await new Promise(r => setTimeout(r, 50));
  }
  await new Promise(r => setTimeout(r, 200));
}
"""

# ---------------------------------------------------------------------------
# Sub-check 1: dragListenerInstalled
# ---------------------------------------------------------------------------
JS_CHECK1 = r"""
() => {
  var cv = document.getElementById('cv');
  return {
    cvDragListened: !!(cv && cv.__cfssDragListened === true),
    testDragFn:     typeof window.__cfssTestDrag === 'function'
  };
}
"""

# ---------------------------------------------------------------------------
# Sub-check 2: extractedDialogsAvailable
# ---------------------------------------------------------------------------
JS_CHECK2 = r"""
() => {
  return {
    dialogsLoaded:      window.__cfss_dialogs_loaded__ === true,
    openPromoteFn:      typeof window.cfssOpenPromoteDialog === 'function',
    openEditFn:         typeof window.cfssOpenEditDialog === 'function',
    commitPromoteFn:    typeof window.cfssCommitPromote === 'function',
    commitEditFn:       typeof window.cfssCommitEdit === 'function'
  };
}
"""

# ---------------------------------------------------------------------------
# Sub-check 3: dragMovesInstance
# Setup 1 master + 1 instance, drag by (50, -30), verify offsetPt + dirty.
# Also verify master.metricPts UNCHANGED.
# ---------------------------------------------------------------------------
JS_CHECK3 = r"""
() => {
  window.MASTERS = {};
  window.__cfss_nextMasterIdN = 1;
  var mid = addMaster('DragTest', [
    {x_m:0,y_m:0},{x_m:2,y_m:0},{x_m:2,y_m:2},{x_m:0,y_m:2}
  ], '#4c8dff');

  window.PS = {};
  window.PS[1] = {objects: [makeInstance(mid, {x:100, y:100})],
                  scale: {pts_per_m: 10}, annotations: []};
  if (window.state) window.state.dirty = false;

  var master = masterById(mid);
  var ptsBefore = JSON.stringify(master.metricPts);

  var result = window.__cfssTestDrag(mid, 50, -30);

  var master2 = masterById(mid);
  var ptsAfter = JSON.stringify(master2.metricPts);

  var inst = window.PS[1].objects[0];
  return {
    ok: result.ok === true,
    resultOk: result.ok,
    newOffsetX: inst.offsetPt.x,
    newOffsetY: inst.offsetPt.y,
    expectedX: 150,
    expectedY: 70,
    offsetCorrect: inst.offsetPt.x === 150 && inst.offsetPt.y === 70,
    dirtySet: !!(window.state && window.state.dirty === true),
    masterPtsUnchanged: ptsBefore === ptsAfter,
    ptsBefore: ptsBefore,
    ptsAfter: ptsAfter
  };
}
"""

# ---------------------------------------------------------------------------
# Sub-check 4: dragDoesNotMutateMaster
# Separate fresh setup; stringify master.metricPts before/after.
# ---------------------------------------------------------------------------
JS_CHECK4 = r"""
() => {
  window.MASTERS = {};
  window.__cfss_nextMasterIdN = 1;
  var mid = addMaster('MasterIntact', [
    {x_m:0,y_m:0},{x_m:3,y_m:0},{x_m:3,y_m:1.5},{x_m:0,y_m:1.5}
  ], '#ff0');

  window.PS = {};
  window.PS[1] = {objects: [makeInstance(mid, {x:50, y:50})],
                  scale: {pts_per_m: 10}, annotations: []};

  var before = JSON.stringify(masterById(mid).metricPts);
  window.__cfssTestDrag(mid, 100, 100);
  var after = JSON.stringify(masterById(mid).metricPts);

  return {
    ok: before === after,
    before: before,
    after: after
  };
}
"""

# ---------------------------------------------------------------------------
# Sub-check 5: dragSurvivesSaveLoad
# Move instance to (200, 100), save, clear state, loadProto, verify offsetPt.
# ---------------------------------------------------------------------------
JS_SETUP_DRAG_SAVE = r"""
() => {
  window.caseId = 'drag-test';
  window.pdfName = 'x.pdf';
  window.pageCount = 1;

  window.MASTERS = {};
  window.__cfss_nextMasterIdN = 1;
  window.PS = {};
  window.PS[1] = {objects: [], scale: null, annotations: []};

  var mid = addMaster('SaveDrag', [
    {x_m:0,y_m:0},{x_m:2,y_m:0},{x_m:2,y_m:2},{x_m:0,y_m:2}
  ], '#0f0');
  window.PS[1].objects.push(makeInstance(mid, {x:0, y:0}));

  // Drag to (200, 100)
  window.__cfssTestDrag(mid, 200, 100);

  return mid;
}
"""

JS_CHECK5_VERIFY = r"""
(doc) => {
  try {
    window.MASTERS = {};
    window.__cfss_nextMasterIdN = 1;
    window.PS = {};
    loadProto(doc);
  } catch(e) {
    return {ok: false, error: 'loadProto threw: ' + e};
  }

  // Find instances in PS
  var found = null;
  Object.keys(window.PS || {}).forEach(function(k) {
    (window.PS[k].objects || []).forEach(function(o) {
      if (isInstance(o)) found = o;
    });
  });

  if (!found) return {ok: false, error: 'no instance found after loadProto'};

  var oxOk = found.offsetPt.x === 200;
  var oyOk = found.offsetPt.y === 100;
  return {
    ok: oxOk && oyOk,
    offsetX: found.offsetPt.x,
    offsetY: found.offsetPt.y,
    expectedX: 200,
    expectedY: 100
  };
}
"""

# ---------------------------------------------------------------------------
# Sub-check 6: dragOnInstanceOnlyClickIntercepted (structural)
# cfssPickInstance returns null far outside, returns instance at center.
# ---------------------------------------------------------------------------
JS_CHECK6 = r"""
() => {
  window.MASTERS = {};
  window.__cfss_nextMasterIdN = 1;
  var mid = addMaster('PickTarget', [
    {x_m:0,y_m:0},{x_m:2,y_m:0},{x_m:2,y_m:2},{x_m:0,y_m:2}
  ], '#888');

  var ppm = 10;
  window.PS = {};
  window.PS[1] = {
    objects: [makeInstance(mid, {x:100, y:100})],
    scale: {pts_per_m: ppm}, annotations: []
  };
  window.curPage = 1;

  // Instance occupies pt-space: x=100..120, y=100..120
  // Screen-space center: ptToScreen({x:110, y:110})
  var center = window.ptToScreen ? window.ptToScreen({x:110, y:110}) : null;
  var far = {x: -9999, y: -9999};

  var hitFar = cfssPickInstance(far.x, far.y);
  var hitCenter = center ? cfssPickInstance(center.x, center.y) : null;

  return {
    cvDragListened: !!(document.getElementById('cv') &&
                       document.getElementById('cv').__cfssDragListened === true),
    missOnFar: hitFar === null,
    hitOnCenter: hitCenter !== null && isInstance(hitCenter),
    centerScrX: center ? center.x : null,
    centerScrY: center ? center.y : null
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
        print("LITE-CFSS-DRAG sub-checks:")

        if page_errors:
            for e in page_errors:
                print("  JS ERROR:", e)

        # -------------------------------------------------------------------
        # Sub-check 1: dragListenerInstalled
        # -------------------------------------------------------------------
        r1 = page.evaluate(JS_CHECK1)
        mark("dragListenerInstalled",
             r1.get("cvDragListened") is True and r1.get("testDragFn") is True,
             f"cvDragListened={r1.get('cvDragListened')} testDragFn={r1.get('testDragFn')}")

        # -------------------------------------------------------------------
        # Sub-check 2: extractedDialogsAvailable
        # -------------------------------------------------------------------
        r2 = page.evaluate(JS_CHECK2)
        mark("extractedDialogsAvailable",
             (r2.get("dialogsLoaded") is True and
              r2.get("openPromoteFn") is True and
              r2.get("openEditFn") is True and
              r2.get("commitPromoteFn") is True and
              r2.get("commitEditFn") is True),
             f"loaded={r2.get('dialogsLoaded')} promote={r2.get('openPromoteFn')} "
             f"edit={r2.get('openEditFn')} commitP={r2.get('commitPromoteFn')} "
             f"commitE={r2.get('commitEditFn')}")

        # -------------------------------------------------------------------
        # Sub-check 3: dragMovesInstance
        # -------------------------------------------------------------------
        r3 = page.evaluate(JS_CHECK3)
        mark("dragMovesInstance",
             (r3.get("ok") is True and
              r3.get("offsetCorrect") is True and
              r3.get("dirtySet") is True and
              r3.get("masterPtsUnchanged") is True),
             f"ok={r3.get('ok')} offsetX={r3.get('newOffsetX')} offsetY={r3.get('newOffsetY')} "
             f"dirty={r3.get('dirtySet')} ptsUnchanged={r3.get('masterPtsUnchanged')}")

        # -------------------------------------------------------------------
        # Sub-check 4: dragDoesNotMutateMaster
        # -------------------------------------------------------------------
        r4 = page.evaluate(JS_CHECK4)
        mark("dragDoesNotMutateMaster",
             r4.get("ok") is True,
             f"before={r4.get('before')[:40] if r4.get('before') else None} "
             f"after={r4.get('after')[:40] if r4.get('after') else None}")

        # -------------------------------------------------------------------
        # Sub-check 5: dragSurvivesSaveLoad
        # -------------------------------------------------------------------
        mid5 = page.evaluate(JS_SETUP_DRAG_SAVE)

        saved_doc = None
        try:
            with page.expect_download(timeout=10_000) as dl_info:
                page.evaluate("() => { var btn = document.getElementById('mi-save'); btn.onclick(null); }")
            download = dl_info.value
            tmp_path = Path(tempfile.gettempdir()) / "cfss_drag_test.bmaplan"
            download.save_as(str(tmp_path))
            saved_doc = json.loads(tmp_path.read_text(encoding="utf-8"))
        except Exception as exc:
            print(f"  [WARN] drag save download failed: {exc}")

        if saved_doc is not None:
            r5 = page.evaluate(JS_CHECK5_VERIFY, saved_doc)
            mark("dragSurvivesSaveLoad",
                 r5.get("ok") is True,
                 f"offsetX={r5.get('offsetX')} offsetY={r5.get('offsetY')} "
                 f"error={r5.get('error') or ''}")
        else:
            mark("dragSurvivesSaveLoad", False, "no saved doc")

        # -------------------------------------------------------------------
        # Sub-check 6: dragOnInstanceOnlyClickIntercepted (structural)
        # -------------------------------------------------------------------
        r6 = page.evaluate(JS_CHECK6)
        mark("dragOnInstanceOnlyClickIntercepted",
             (r6.get("cvDragListened") is True and
              r6.get("missOnFar") is True and
              r6.get("hitOnCenter") is True),
             f"cvDragged={r6.get('cvDragListened')} miss={r6.get('missOnFar')} "
             f"hit={r6.get('hitOnCenter')} scrX={r6.get('centerScrX')} scrY={r6.get('centerScrY')}")

        page.close()
        context.close()
        browser.close()

    server.should_exit = True
    time.sleep(0.4)

    # -----------------------------------------------------------------------
    # Sub-check 7: measureEngineIntact + uiLiteUntouched + capsHealthy
    # -----------------------------------------------------------------------
    me_hash_after = sha256_file(MEASURE_ENGINE)
    me_ok = me_hash_before == me_hash_after

    ui_lines = count_lines_file(UI_LITE)
    ui_ok = ui_lines == 1200

    cfss_lines = count_lines_file(CFSS_JS)
    cfss_ok = cfss_lines <= 1000

    dlg_lines = count_lines_file(CFSS_DLG_JS)
    dlg_ok = dlg_lines <= 1000

    mark("measureEngineIntact_uiLiteUntouched_capsHealthy",
         me_ok and ui_ok and cfss_ok and dlg_ok,
         f"me_hash={'ok' if me_ok else 'CHANGED'} "
         f"ui={ui_lines}/1200 cfss={cfss_lines}/1000 dlg={dlg_lines}/1000")

    print()
    if first_fail:
        print(f"LITE_CFSS_DRAG_FAIL: {first_fail}")
        sys.exit(1)
    else:
        print("LITE_CFSS_DRAG_OK")


if __name__ == "__main__":
    main()
