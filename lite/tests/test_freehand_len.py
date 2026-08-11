"""
LITE-FREEHAND-LEN regression guard (FREEHAND-LEN sprint, docs/status/PHASE_INDEX.md
"### sprint cards CURVE-2026-08-11", done after CURVE-LEN).

Ports proto's shipped Alt-hold streaming design (INV-2026-05-17-001, commit
023b988, Approach D) to the lite continuous-path tool (⇧D): Alt-hold during
drag = streaming sample (distance-bin >=6px screen), release = commit via
rdpSimplify decimation, mixed click+drag in one draft.

Like test_arc_edge.py / test_curve_len.py, cv's real mousedown/mousemove
listeners are gated on PageRenderer.ready() (false without a loaded PDF in
this fast headless harness) — so this test exercises the underlying engine
functions directly (fhStart/fhSample/fhCommit — the exact functions the
mousedown/mousemove/mouseup DOM handlers call) plus REAL keydown events for
the wires that don't need a loaded page (Shift+D tool-switch, Enter finish).

Single scenario, 3 sub-cases in sequence:
  case1_streamOnly   — Alt-drag IS the entire path (draft starts empty):
                        (1) object created; (2) raw~100 -> decimated <=40 via
                        rdpSimplify; (3) length within 3% of true semicircle
                        length pi*R (independent closed-form, converted
                        through the real screenToPt/RS pipeline).
  case2_mixedMode    — click 2 vertices, Alt-drag a stretch, click 1 more —
                        ONE object, finite positive length.
  case3_roundTrip    — buildPageStore()/loadProto() preserves obj.freeform
                        (additive metadata) on the case1 object; length
                        (lineLenWithArcs) unchanged after reload.

Emits LITE_FREEHAND_LEN_OK on success.

    python lite/tests/test_freehand_len.py
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


def _free_port(start=8470):
    for p in range(start, start + 60):
        with socket.socket() as s:
            if s.connect_ex(("127.0.0.1", p)) != 0:
                return p
    raise RuntimeError("no free port")


SETUP_STATE = r"""
var _TST_PAGE = 97;
if (!PS[_TST_PAGE]) PS[_TST_PAGE] = {objects:[], scale:null, annotations:[]};
PS[_TST_PAGE].scale = {pts_per_m: 1};
curPage = _TST_PAGE;
state.tool = 'select';
state.activeCat = 'gfa';
state.draft = null;
arcCancel();
if (typeof fhCancel === 'function') fhCancel();
"""

SCENARIO = r"""
async () => {
  """ + SETUP_STATE + r"""

  // --- WIRE: Shift+D -> tool=path (real keydown, F-1) ---
  window.dispatchEvent(new KeyboardEvent('keydown', {bubbles:true, cancelable:true, key:'D', shiftKey:true}));
  if (state.tool !== 'path') return {fail: 'Shift+D did not set tool=path', tool: state.tool};

  // =========================================================================
  // case1: Alt-drag IS the whole path — semicircle, radius R=190 screen px,
  // sampled at ~600 fine-grained candidates so the real 6px distance-bin gate
  // (fhSample) governs which ones survive — mirrors an actual mousemove burst.
  // =========================================================================
  var Cx=300, Cy=300, R=190;
  fhStart(Cx+R, Cy);   // angle=0 start point (mirrors Alt+mousedown)
  var N=600, acceptedCount=0;
  for (var i=1; i<N; i++) {
    var ang = (i/(N-1))*Math.PI;
    var x = Cx + R*Math.cos(ang), y = Cy + R*Math.sin(ang);
    if (fhSample(x, y, 6)) acceptedCount++;
  }
  state.draft = state.draft || [];
  var objsBefore1 = PS[_TST_PAGE].objects.length;
  var commit1 = fhCommit(state.draft, 4);
  window.dispatchEvent(new KeyboardEvent('keydown', {bubbles:true, cancelable:true, key:'Enter'}));
  var objsAfter1 = PS[_TST_PAGE].objects.length;
  var case1_objectCreated = (objsAfter1 === objsBefore1 + 1);
  var obj1 = case1_objectCreated ? PS[_TST_PAGE].objects[objsAfter1 - 1] : null;

  var case1_rawOk = commit1.rawCount >= 60;                 // real streaming happened (not just 2 pts)
  var case1_decimatedOk = commit1.simplifiedCount >= 3 && commit1.simplifiedCount <= 40;
  var case1_freeformOk = !!(obj1 && obj1.freeform && obj1.freeform.originalCount === commit1.rawCount);

  var trueLen = Math.PI * (R / RS);   // independent closed-form: screen radius -> PDF via /RS (rot=0 page), pts_per_m=1 so PDF-units==m
  var appLen1 = obj1 ? lineLenWithArcs(obj1) : null;
  var lenErr1 = (appLen1 != null) ? Math.abs(appLen1 - trueLen) / trueLen : Infinity;
  var case1_lenOk = lenErr1 < 0.03;   // <3%

  // =========================================================================
  // case2: mixed mode — click v0, click v1, Alt-drag a stretch, click v2 — ONE object.
  // =========================================================================
  state.draft = null;
  if (typeof fhCancel === 'function') fhCancel();
  var v0 = screenToPt(50, 50), v1 = screenToPt(50, 250);
  state.draft = [v0, v1];
  fhStart(50, 250);   // starts exactly at v1's screen pos (dedup-skip check)
  var jitterAccepted = 0;
  for (var j = 1; j <= 60; j++) {
    var jx = 50 + j * 2, jy = 250 - Math.sin(j/60*Math.PI) * 30;
    if (fhSample(jx, jy, 6)) jitterAccepted++;
  }
  var commit2 = fhCommit(state.draft, 4);
  var v2 = screenToPt(170, 220);
  state.draft.push(v2);
  var objsBefore2 = PS[_TST_PAGE].objects.length;
  window.dispatchEvent(new KeyboardEvent('keydown', {bubbles:true, cancelable:true, key:'Enter'}));
  var objsAfter2 = PS[_TST_PAGE].objects.length;
  var case2_oneObject = (objsAfter2 === objsBefore2 + 1);
  var obj2 = case2_oneObject ? PS[_TST_PAGE].objects[objsAfter2 - 1] : null;
  var case2_ptsOk = !!(obj2 && obj2.pts && obj2.pts.length >= 4);   // v0 + v1 + >=1 burst pt + v2
  var appLen2 = obj2 ? lineLenWithArcs(obj2) : null;
  var case2_lenSane = (appLen2 != null) && isFinite(appLen2) && appLen2 > 0;

  // =========================================================================
  // case3: save/load round trip of the case1 (pure-freehand) object.
  // =========================================================================
  var areaBefore = appLen1;
  var doc = {
    version: 1, app: 'bma-plan-lite', pdfName: 'test.pdf', totalPages: 97,
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
  var objs3 = PS[_TST_PAGE] ? PS[_TST_PAGE].objects : [];
  // both restored objects are kind:'line' with no edges — pick the one whose
  // freeform.originalCount matches case1's burst (case2's burst count differs).
  var restored = objs3.find(function(x){ return x.kind === 'line' && x.freeform && x.freeform.originalCount === commit1.rawCount; });
  var case3_freeformSurvived = !!restored;
  var case3_lenMatch = case3_freeformSurvived && Math.abs(lineLenWithArcs(restored) - areaBefore) < 0.001;

  return {
    acceptedCount, case1_objectCreated, case1_rawOk, case1_decimatedOk, case1_freeformOk,
    rawCount: commit1.rawCount, simplifiedCount: commit1.simplifiedCount,
    trueLen, appLen1, lenErr1, case1_lenOk,
    case2_oneObject, case2_ptsOk, appLen2, case2_lenSane,
    case3_freeformSurvived, case3_lenMatch,
    pass: case1_objectCreated && case1_rawOk && case1_decimatedOk && case1_freeformOk && case1_lenOk
      && case2_oneObject && case2_ptsOk && case2_lenSane
      && case3_freeformSurvived && case3_lenMatch
  };
}
"""

CHECKS = [
    ("freehandStreamMixedRoundTrip", SCENARIO, ["pass"]),
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
        print("LITE-FREEHAND-LEN checks:")
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
        print("LITE_FREEHAND_LEN_FAIL")
        sys.exit(1)
    else:
        print("LITE_FREEHAND_LEN_OK")


if __name__ == "__main__":
    main()
