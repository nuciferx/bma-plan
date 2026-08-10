"""
SHELL-STATUS-2026-08-10: bottom status bar guard (docs/status/PHASE_INDEX.md
"sprint cards SHELL-2026-08-10", GO-2026-08-10).

Module under test: lite/static/js/status-bar.js (self-injecting, read-only
over app state; wraps window.draw() to refresh 7 cells: page/floor, scale,
tool, active layer, snap, dirty, and the right-aligned "สุทธิชั้นนี้" (I2
rollup consumer, registered in tests/INVARIANTS.md I2's consumer list).

RED-first: written and run BEFORE static/js/status-bar.js existed / before
its <script src> tag was added to ui-lite.html — #lite-status was absent,
every check failed by construction. See TEST_RESULT / builder report for
the captured RED transcript.

6 sub-checks:
  barExistsWithSevenCells     #lite-status renders with exactly 7 .sb-cell
                               elements (page/scale/tool/layer/snap/dirty/net)
  scaleCellTracksScale         PS[cp].scale=null -> "ยังไม่ตั้ง"; set a real
                               scale -> "✓" appears (via draw(), not a poll)
  toolAndSnapCellsTrackState   setTool() switches the tool cell's Thai label;
                               toggleSnap() switches the snap cell เปิด/ปิด
  dirtyCellTracksStateDirty    state.dirty false->true (as a real object
                               commit would set it) flips the dirty cell
  floorNetMatchesObjectAgg     a floor-tagged + scaled page with one gfa poly
                               (100x100=10000 m2) and one ded poly (20x10=200
                               m2) -> #sb-net text equals the SAME value
                               window.ObjectAgg.byFloorRole() computes
                               independently, gfa-ded=9800.00, within 0.01
                               (I2 fixture — this IS the ritual's required
                               fixture/assertion added to this file's sibling
                               obligation; see INVARIANTS.md I2 row diff)
  focusModeHidesBar            body.focus -> #lite-status not rendered
                               (offsetParent null / 0 height)

Emits LITE_STATUS_BAR_OK on success.

    py -3 lite/tests/test_status_bar.py
"""
import socket
import sys
import threading
import time
from pathlib import Path

LITE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LITE))
import uvicorn
from playwright.sync_api import sync_playwright


def _free_port(start=8720):
    for p in range(start, start + 60):
        with socket.socket() as s:
            if s.connect_ex(("127.0.0.1", p)) != 0:
                return p
    raise RuntimeError("no free port")


# ---------------------------------------------------------------------------
# Sub-check 1 — barExistsWithSevenCells
# ---------------------------------------------------------------------------
CHECK_BAR_EXISTS = r"""
() => {
  var bar = document.getElementById('lite-status');
  var cells = bar ? bar.querySelectorAll('.sb-cell') : [];
  var ids = ['sb-page','sb-scale','sb-tool','sb-layer','sb-snap','sb-dirty','sb-net'];
  var allPresent = ids.every(function(id) { return !!document.getElementById(id); });
  return {
    barFound: !!bar, cellCount: cells.length, allPresent,
    pass: !!bar && cells.length === 7 && allPresent
  };
}
"""

# ---------------------------------------------------------------------------
# Sub-check 2 — scaleCellTracksScale
# ---------------------------------------------------------------------------
CHECK_SCALE_TRACKS = r"""
() => {
  caseId = 'test'; pageCount = 3; pageTags = {}; excluded = {};
  curPage = 1; PS = { 1: { objects: [], scale: null, annotations: [] } };
  draw();
  var before = document.getElementById('sb-scale').textContent;

  PS[1].scale = { pts_per_m: 10 };
  draw();
  var after = document.getElementById('sb-scale').textContent;

  return {
    before, after,
    beforeUnset: before.indexOf('ยังไม่ตั้ง') >= 0,
    afterSet: after.indexOf('✓') >= 0,   // checkmark
    pass: before.indexOf('ยังไม่ตั้ง') >= 0 && after.indexOf('✓') >= 0
  };
}
"""

# ---------------------------------------------------------------------------
# Sub-check 3 — toolAndSnapCellsTrackState
# ---------------------------------------------------------------------------
CHECK_TOOL_SNAP_TRACK = r"""
() => {
  // tag+scale the page so tag-jit.js's measure-tool gate does not block
  // setTool('dist') -- this check is about the status bar's OWN reactive
  // binding to state.tool, not the scale-gate (covered by test_scale_gate.py).
  caseId = 'test'; pageCount = 3; pageTags = { 1: 'site' }; excluded = {};
  curPage = 1; PS = { 1: { objects: [], scale: { pts_per_m: 10 }, annotations: [] } };

  setTool('poly');
  var polyTxt = document.getElementById('sb-tool').textContent;
  setTool('dist');
  var distTxt = document.getElementById('sb-tool').textContent;

  state.snapOn = true; draw();
  var snapOnTxt = document.getElementById('sb-snap').textContent;
  toggleSnap();  // flips + calls draw() itself
  var snapOffTxt = document.getElementById('sb-snap').textContent;
  toggleSnap();  // restore
  var snapRestoredTxt = document.getElementById('sb-snap').textContent;

  return {
    polyTxt, distTxt, snapOnTxt, snapOffTxt, snapRestoredTxt,
    toolTracks: polyTxt.indexOf('วัดพื้นที่') >= 0 && polyTxt !== distTxt,
    snapTracks: snapOnTxt.indexOf('เปิด') >= 0 && snapOffTxt.indexOf('ปิด') >= 0 && snapOnTxt !== snapOffTxt,
    snapRestored: snapRestoredTxt === snapOnTxt,
    pass: null
  };
}
"""

# ---------------------------------------------------------------------------
# Sub-check 4 — dirtyCellTracksStateDirty
# ---------------------------------------------------------------------------
CHECK_DIRTY_TRACKS = r"""
() => {
  caseId = 'test'; pageCount = 3; pageTags = {}; excluded = {};
  curPage = 1; PS = { 1: { objects: [], scale: null, annotations: [] } };

  state.dirty = false; draw();
  var clean = document.getElementById('sb-dirty').textContent;

  // A real polygon commit sets state.dirty=true via pushUndo()/commit code
  // (tested elsewhere); this checks the STATUS BAR's own reactive binding.
  state.dirty = true; draw();
  var dirty = document.getElementById('sb-dirty').textContent;

  state.dirty = false; draw();  // restore

  return {
    clean, dirty,
    cleanOk: clean.indexOf('✓') >= 0,
    dirtyOk: dirty.indexOf('●') >= 0,
    pass: clean.indexOf('✓') >= 0 && dirty.indexOf('●') >= 0
  };
}
"""

# ---------------------------------------------------------------------------
# Sub-check 5 — floorNetMatchesObjectAgg (I2 fixture)
# ---------------------------------------------------------------------------
CHECK_FLOOR_NET = r"""
() => {
  var _P = 55;
  caseId = 'test'; pageCount = 60; excluded = {};
  pageTags = {}; pageFloorKind = {}; pageFloorNum = {};
  pageTags[_P] = 'floor'; pageFloorKind[_P] = 'normal'; pageFloorNum[_P] = 2;
  curPage = _P;
  PS = {};
  PS[_P] = { objects: [], scale: { pts_per_m: 1 }, annotations: [] };

  var gfaPoly = { id: state._id++, catId: 'gfa', kind: 'poly', counting: false,
    pts: [{x:0,y:0},{x:100,y:0},{x:100,y:100},{x:0,y:100}] };            // 10000 m2
  var dedPoly = { id: state._id++, catId: 'ded', kind: 'poly', counting: false,
    pts: [{x:200,y:0},{x:220,y:0},{x:220,y:10},{x:200,y:10}] };          // 200 m2
  PS[_P].objects.push(gfaPoly);
  PS[_P].objects.push(dedPoly);

  draw();
  var cellTxt = document.getElementById('sb-net').textContent;
  var m = cellTxt.match(/([\d.]+)\s*ตร\.ม\.$/);
  var cellVal = m ? parseFloat(m[1]) : null;

  // Independent ground truth via the SAME public ObjectAgg API the module
  // itself is required to use (never a private re-walk of PS).
  var bfr = ObjectAgg.byFloorRole(ObjectAgg.objectTuples());
  var fk = ObjectAgg.floorKeyOfPage(_P);
  var row = bfr[fk];
  var expected = ((row.gfa && row.gfa.area) || 0) - ((row.ded && row.ded.area) || 0);

  var moduleVal = _sbFloorNet();

  return {
    cellTxt, cellVal, expected, fk, moduleVal,
    cellMatchesExpected: cellVal != null && Math.abs(cellVal - expected) < 0.01,
    moduleMatchesExpected: moduleVal != null && Math.abs(moduleVal - expected) < 0.01,
    expectedIs9800: Math.abs(expected - 9800) < 0.01,
    pass: cellVal != null && Math.abs(cellVal - expected) < 0.01 &&
          Math.abs(moduleVal - expected) < 0.01 && Math.abs(expected - 9800) < 0.01
  };
}
"""

# ---------------------------------------------------------------------------
# Sub-check 6 — focusModeHidesBar
# ---------------------------------------------------------------------------
CHECK_FOCUS_HIDES = r"""
() => {
  document.body.classList.remove('focus');
  draw();
  var beforeVisible = document.getElementById('lite-status').offsetHeight > 0;

  document.body.classList.add('focus');
  var afterVisible = document.getElementById('lite-status').offsetHeight > 0;

  document.body.classList.remove('focus');  // restore

  return {
    beforeVisible, afterVisible,
    pass: beforeVisible === true && afterVisible === false
  };
}
"""

CHECKS = [
    ("barExistsWithSevenCells",   CHECK_BAR_EXISTS,        ["pass"]),
    ("scaleCellTracksScale",      CHECK_SCALE_TRACKS,      ["pass"]),
    ("dirtyCellTracksStateDirty", CHECK_DIRTY_TRACKS,      ["pass"]),
    ("floorNetMatchesObjectAgg",  CHECK_FLOOR_NET,         ["pass"]),
    ("focusModeHidesBar",         CHECK_FOCUS_HIDES,       ["pass"]),
]


def main():
    from server_lite import app as lite_app
    port = _free_port()
    cfg = uvicorn.Config(lite_app, host="127.0.0.1", port=port, log_level="error")
    server = uvicorn.Server(cfg)
    threading.Thread(target=server.run, daemon=True).start()
    time.sleep(2.0)

    failures = []
    page_errors = []

    with sync_playwright() as pw:
        b = pw.chromium.launch()
        pg = b.new_page()
        pg.on("pageerror", lambda e: page_errors.append(f"pageerror: {e}"))
        pg.goto(f"http://127.0.0.1:{port}/", wait_until="networkidle")
        time.sleep(1.0)

        print()
        print("LITE-STATUS-BAR checks:")
        for name, scenario, required_keys in CHECKS:
            try:
                result = pg.evaluate(scenario)
            except Exception as ex:
                print(f"  {name:32s} -> EXCEPTION: {ex}")
                failures.append(f"check '{name}' threw: {ex}")
                continue

            ok = all(result.get(k) is True for k in required_keys)
            status = "PASS" if ok else "FAIL"
            print(f"  {name:32s} -> {status}  {result}")
            if not ok:
                bad = [k for k in required_keys if result.get(k) is not True]
                failures.append(f"check '{name}' failed keys: {bad}  result={result}")

        # sub-check 3 has manual multi-field pass logic (no single `pass` key
        # from JS); evaluate here for a consistent failure message.
        try:
            r3 = pg.evaluate(CHECK_TOOL_SNAP_TRACK)
            ok3 = r3.get("toolTracks") is True and r3.get("snapTracks") is True and r3.get("snapRestored") is True
            status = "PASS" if ok3 else "FAIL"
            print(f"  {'toolAndSnapCellsTrackState':32s} -> {status}  {r3}")
            if not ok3:
                failures.append(f"check 'toolAndSnapCellsTrackState' failed: result={r3}")
        except Exception as ex:
            print(f"  {'toolAndSnapCellsTrackState':32s} -> EXCEPTION: {ex}")
            failures.append(f"check 'toolAndSnapCellsTrackState' threw: {ex}")

        pg.close()
        b.close()

    for e in page_errors:
        print("  JS ERROR:", e)

    server.should_exit = True
    time.sleep(0.4)

    if failures:
        for f in failures:
            print("FAIL:", f)
        print("LITE_STATUS_BAR_FAIL")
        sys.exit(1)
    else:
        print("LITE_STATUS_BAR_OK")


if __name__ == "__main__":
    main()
