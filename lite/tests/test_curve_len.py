"""
LITE-CURVE-LEN regression guard (CURVE-LEN sprint, docs/status/PHASE_INDEX.md
"### sprint cards CURVE-2026-08-11").

Verifies the arc-edge mechanic ported from the polygon tool (draw-arc.js) to
the continuous-path tool (state.tool==="path", ⇧D):

  drawPathArcBasic     — drive path via REAL keydown events: Shift+D sets
                          tool=path (F-1 wire); keydown 'a' with a draft in
                          progress toggles arc-pending (LCURVE-1(+2) wire,
                          now extended to path); keydown 'Enter' finishes the
                          draft. Vertex pushes + arcOnClick calls are direct
                          state manipulation, matching test_arc_edge.py's
                          documented fallback (cv mousedown is gated on
                          PageRenderer.ready(), which is false without a
                          loaded PDF in this harness — so the mousedown
                          BRANCH LOGIC itself is not exercised end-to-end
                          here; the wiring at the keydown layer is).
  lengthMatchesClosedForm — lineLenWithArcs(o) (draw-arc.js) matches an
                          INDEPENDENT closed-form expected length (semicircle
                          arc + a trailing straight segment) — not derived
                          from the function under test.
  lengthLabelMatches    — showProps(o) (ui-lite.html) writes the SAME total
                          into #p-area as lineLenLabel(o) — the "object's
                          length label" consumer named in the sprint card.
  exportRowInvestigated — buildExportData() row for this line object: FINDING
                          documented by the sprint card is that kind!=="poly"
                          rows carry area:null and no length field today
                          (server_lite.py's /export-xlsx writer only ever
                          reads r.area/r.count for its fixed 6 columns, and
                          it is a forbidden-to-edit surface for this sprint)
                          — asserts that finding stays true, i.e. this test
                          fails LOUDLY if a future sprint silently changes
                          the row shape without updating this comment.
  saveLoadRoundTrip     — buildPageStore() -> loadProto() preserves o.edges
                          on a "line" object (pre-existing lossiness: lines
                          used to drop edges entirely on save) and
                          lineLenWithArcs is unchanged after reload.
  overlayFlattensArc    — ExportAnnotate.overlayPts(o) returns MORE than the
                          2 raw endpoints for the arc segment (flattened
                          curve, not a chord) — I5 (export must match
                          screen). Endpoints unchanged; a mid-arc point
                          deviates from the straight chord by roughly the
                          known sagitta (independent geometric check).

Emits LITE_CURVE_LEN_OK on success.

    python lite/tests/test_curve_len.py
"""
import math
import socket
import sys
import threading
import time
from pathlib import Path

LITE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LITE))
import uvicorn
from playwright.sync_api import sync_playwright


def _free_port(start=8460):
    for p in range(start, start + 60):
        with socket.socket() as s:
            if s.connect_ex(("127.0.0.1", p)) != 0:
                return p
    raise RuntimeError("no free port")


# ---------------------------------------------------------------------------
# Geometry (1 pt = 1 m, matches test_arc_edge.py convention):
#   v0=(0,0)  v1=(100,0)  v2=(150,50)
#   edge[0]: v0->v1, arc via through-point tp=(50,50) — perpendicular at
#     half-chord distance (chord=100) => EXACT semicircle: sweep=pi,
#     radius=50, arc length = 50*pi (independent closed form, same
#     construction as test_arc_edge.py's SC1).
#   edge[1]: v1->v2, straight — length = hypot(50,50) = 50*sqrt(2).
#   expected total = 50*pi + 50*sqrt(2)  ~=  227.7903 m
# ---------------------------------------------------------------------------
SETUP_STATE = r"""
var _TST_PAGE = 98;
if (!PS[_TST_PAGE]) PS[_TST_PAGE] = {objects:[], scale:null, annotations:[]};
PS[_TST_PAGE].scale = {pts_per_m: 1};
curPage = _TST_PAGE;
state.tool = 'select';
state.activeCat = 'gfa';
state.draft = null;
arcCancel();
if (typeof fhCancel === 'function') fhCancel();
"""

SC1_PATH_ARC_BASIC = r"""
async () => {
  """ + SETUP_STATE + r"""

  var v0={x:0,y:0}, v1={x:100,y:0}, v2={x:150,y:50};
  var tp={x:50,y:50};

  // --- WIRE: keydown Shift+D -> tool=path (F-1) ---
  window.dispatchEvent(new KeyboardEvent('keydown', {bubbles:true, cancelable:true, key:'D', shiftKey:true}));
  if (state.tool !== 'path') return {fail: 'Shift+D did not set tool=path', tool: state.tool};

  state.draft = [];
  state.draft.push(v0);

  // --- WIRE: keydown 'a' with draft.length>=1 on tool=path -> arcToggle() ---
  window.dispatchEvent(new KeyboardEvent('keydown', {bubbles:true, cancelable:true, key:'a'}));
  if (!_arcDraft.pending) return {fail: 'keydown a on path draft did not set pending', pending: _arcDraft.pending};

  var r1 = arcOnClick(tp, state.draft);
  if (!r1.consumed) return {fail: 'through-pt not consumed', r1};

  var r2 = arcOnClick(v1, state.draft);
  if (r2.consumed) return {fail: 'v1 should not be consumed (arc-close)', r2};
  state.draft.push(v1);
  if (r2.edgeRecord) {
    if (!state.draft.edges) state.draft.edges = [];
    state.draft.edges[state.draft.length - 2] = r2.edgeRecord;
  }
  var hasArcInDraft = !!(state.draft.edges && state.draft.edges[0] && state.draft.edges[0].edgeType === 'arc');

  // straight segment v1 -> v2
  arcOnClick(v2, state.draft);
  state.draft.push(v2);

  var objsBefore = PS[_TST_PAGE].objects.length;
  window.dispatchEvent(new KeyboardEvent('keydown', {bubbles:true, cancelable:true, key:'Enter'}));
  var objsAfter = PS[_TST_PAGE].objects.length;
  if (objsAfter !== objsBefore + 1) return {fail: 'Enter keydown did not finishDraft', objsBefore, objsAfter};

  var o = PS[_TST_PAGE].objects[PS[_TST_PAGE].objects.length - 1];
  if (!o) return {fail: 'no object saved'};

  var hasArcEdge = !!(o.edges && o.edges[0] && o.edges[0].edgeType === 'arc');
  var kindOk = o.kind === 'line';
  var sweepOk = hasArcEdge && Math.abs(Math.abs(o.edges[0].arcSweep) - Math.PI) < 0.05;

  // independent closed-form expected length
  var expected = 50 * Math.PI + Math.hypot(50, 50);
  var appLen = (typeof lineLenWithArcs === 'function') ? lineLenWithArcs(o) : null;
  var lenErr = (appLen != null) ? Math.abs(appLen - expected) : Infinity;
  var lenOk = lenErr < (expected * 0.005); // <0.5%

  // showProps label consumer
  showProps(o);
  var labelTxt = document.getElementById('p-area').textContent;
  var labelNum = parseFloat(labelTxt);
  var labelOk = !isNaN(labelNum) && Math.abs(labelNum - expected) < 0.5;

  // export row investigation
  var xd = buildExportData();
  var row = xd.rows.find(function(r){ return r.page === _TST_PAGE && r.kind === 'line'; });
  var rowFound = !!row;
  var rowAreaNull = rowFound && row.area === null;
  var rowNoLength = rowFound && !('length' in row);

  // save/load round trip
  var doc = {
    version: 1, app: 'bma-plan-lite', pdfName: 'test.pdf', totalPages: 98,
    pageStore: buildPageStore(),
    pageRotations: {}, pageTags: {}, pageNames: {}, projectInfo: {name:''},
    siteOrientation: {}, excludedPages: [],
    pageFloorKind: {}, pageFloorNum: {},
    liteLayers: layersInOrder().map(function(l){ return {id:l.id,name:l.name,color:l.color,role:l.role,order:l.order,parentId:l.parentId!==undefined?l.parentId:null}; }),
    liteGroups: foldersInOrder().map(function(f){ return {id:f.id,name:f.name,color:f.color,parentId:f.parentId!==undefined?f.parentId:null,order:f.order}; }),
    reportVars: []
  };
  var docJson = JSON.stringify(doc);
  PS = {};
  loadProto(JSON.parse(docJson));
  PS[_TST_PAGE] = PS[_TST_PAGE] || {objects:[], scale:null};
  if (!PS[_TST_PAGE].scale) PS[_TST_PAGE].scale = {pts_per_m:1};
  curPage = _TST_PAGE;
  var objs2 = PS[_TST_PAGE] ? PS[_TST_PAGE].objects : [];
  var restored = objs2.find(function(x){ return x.kind === 'line' && x.edges && x.edges.some(function(e){return e && e.edgeType === 'arc';}); });
  var restoredFound = !!restored;
  var restoredLen = restoredFound ? lineLenWithArcs(restored) : null;
  var roundTripOk = restoredFound && Math.abs(restoredLen - appLen) < 0.001;

  // overlay flatten (I5)
  var flat = (window.ExportAnnotate && window.ExportAnnotate.overlayPts) ? window.ExportAnnotate.overlayPts(o) : null;
  var flatCount = flat ? flat.length : 0;
  var flatMoreThanChord = flatCount > o.pts.length + 5; // 3 raw pts + arc interior samples
  var flatEndpointsOk = flat && Math.abs(flat[0].x - o.pts[0].x) < 0.01 && Math.abs(flat[0].y - o.pts[0].y) < 0.01
    && Math.abs(flat[flat.length-1].x - o.pts[o.pts.length-1].x) < 0.01 && Math.abs(flat[flat.length-1].y - o.pts[o.pts.length-1].y) < 0.01;
  // a mid-arc sample should bulge toward the through-point (y up to ~50), not sit on the y=0 chord
  var maxBulge = 0;
  if (flat) { for (var i = 0; i < flatCount; i++) { if (flat[i].x > 1 && flat[i].x < 99) maxBulge = Math.max(maxBulge, flat[i].y); } }
  var bulgeOk = maxBulge > 20; // well off the chord (semicircle sagitta = 50)

  return {
    kindOk, hasArcEdge, sweepOk,
    appLen, expected, lenErr, lenOk,
    labelTxt, labelNum, labelOk,
    rowFound, rowAreaNull, rowNoLength,
    restoredFound, roundTripOk,
    flatCount, flatMoreThanChord, flatEndpointsOk, maxBulge, bulgeOk,
    pass: kindOk && hasArcEdge && sweepOk && lenOk && labelOk && rowFound && rowAreaNull && rowNoLength
      && restoredFound && roundTripOk && flatMoreThanChord && flatEndpointsOk && bulgeOk
  };
}
"""


CHECKS = [
    ("drawPathArcBasic_allInOne", SC1_PATH_ARC_BASIC, ["pass"]),
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
        time.sleep(0.6)

        print()
        print("LITE-CURVE-LEN checks:")
        for name, scenario, required_keys in CHECKS:
            pg.reload(wait_until="networkidle")
            time.sleep(0.4)
            try:
                result = pg.evaluate(scenario)
            except Exception as ex:
                print(f"  {name:30s} -> EXCEPTION: {ex}")
                failures.append(f"check '{name}' threw: {ex}")
                continue

            if result and result.get("skip"):
                print(f"  {name:30s} -> SKIP  ({result['skip']})")
                failures.append(f"check '{name}' skipped: {result['skip']}")
                continue

            ok = all(result.get(k) is True for k in required_keys)
            status = "PASS" if ok else "FAIL"
            print(f"  {name:30s} -> {status}  {result}")
            if not ok:
                bad = [k for k in required_keys if result.get(k) is not True]
                failures.append(f"check '{name}' failed keys: {bad}  result={result}")

        pg.close()
        b.close()

    for e in page_errors:
        print("  JS ERROR:", e)

    server.should_exit = True
    time.sleep(0.4)

    if failures:
        for f in failures:
            print("FAIL:", f)
        print("LITE_CURVE_LEN_FAIL")
        sys.exit(1)
    else:
        print("LITE_CURVE_LEN_OK")


if __name__ == "__main__":
    main()
