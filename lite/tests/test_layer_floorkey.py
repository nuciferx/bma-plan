"""
INV-20260703-layer-floorkey — sub-sprint A (MODEL) acceptance test.

Ports the 4 spike proofs (lite/sandbox/invent-layer-floorkey/spike.js) against
the LIVE app via Playwright evaluate, plus a save/load round-trip proof.

The one seam under test: ObjectAgg.objectTuples() now derives each tuple's
floorKey from ObjectAgg.floorKeyOfObject(o, pg) — additive precedence
    instance master.floorKey (!= "multi")  ->  layer.floorKey (!= "multi")
    ->  floorKeyOfPage(pg)  (today's page-tag behaviour, the fallback).
byRole()/grand-total never read floorKey, so an override can only
REDISTRIBUTE area across floors, never change a role or project total.

Proofs (each its own reloaded scenario):
  P1 legacyParity     no layer/master floorKey anywhere -> every tuple's
                       floorKey === floorKeyOfPage(pg); byRole/byFloorRole
                       identical to the page-tag derivation; assertEnginesAgree.
  P2 followsLayer      layer pinned floor:1 on a page re-tagged floor:1->2:
                       pinned object stays in floor:1, default object follows
                       the page to floor:2, grand total unchanged, and
                       detectDivergence() returns exactly the one affected row.
  P3 twoLayersOnePage  two gfa layers pinned floor:1 / floor:2 on ONE floor-1
                       page -> distinct byFloorRole buckets, sum == byRole.gfa.
  P4 cfssMultiPerInst  master floorKey:"multi" + instances on two floors ->
                       each instance counts on its own page floor (== today).
  P5 saveLoadRoundtrip real mi-save serialises layer.floorKey into liteLayers;
                       loadProto restores it; deleting the field (old-format)
                       still loads and moves the object back to the page floor
                       with byRole.gfa unchanged (redistribution invariant).

RED demonstration: with static/js/object-agg.js stashed to its pre-sprint
version, objectTuples() uses floorKeyOfPage(pg) directly, so P2 followsLayer
and P3 twoLayersOnePage FAIL (objects follow the page, not the layer).

Emits LITE_LAYER_FLOORKEY_OK on success.

    py -3 lite/tests/test_layer_floorkey.py
"""
import socket, threading, time, sys
from pathlib import Path

LITE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LITE))
import uvicorn
from playwright.sync_api import sync_playwright


def _free_port(start=8560):
    for p in range(start, start + 60):
        with socket.socket() as s:
            if s.connect_ex(("127.0.0.1", p)) != 0:
                return p
    raise RuntimeError("no free port")


# Shared JS helpers prepended to every scenario.
PRELUDE = r"""
function rect(w, h, ox, oy) {
  ox = ox || 0; oy = oy || 0;
  return [{x:ox,y:oy},{x:ox+w,y:oy},{x:ox+w,y:oy+h},{x:ox,y:oy+h}];
}
function close(a, b) { return Math.abs(a - b) < 1e-6 * Math.max(1, Math.abs(b)); }
function poly(catId, w, h, ox, oy, tag) {
  return {id: state._id++, catId: catId, semanticTag: tag || 'gross_floor_area',
          kind: 'poly', counting: false, dimVisible: true, pts: rect(w, h, ox, oy)};
}
function A() { return window.ObjectAgg; }
"""


# --- P1: legacy parity (no floorKey anywhere) ------------------------------
SC_P1 = r"""
async () => {
  if (typeof window.ObjectAgg !== 'object') return {pass:false, err:'ObjectAgg missing'};
""" + PRELUDE + r"""
  PS = {}; excluded = {}; pageTags = {}; pageFloorKind = {}; pageFloorNum = {};
  pageTags[1]='floor'; pageFloorNum[1]=1; pageFloorKind[1]='normal';
  pageTags[2]='floor'; pageFloorNum[2]=2; pageFloorKind[2]='normal';
  pageTags[3]='floor'; pageFloorNum[3]=1; pageFloorKind[3]='normal';
  var L1 = addLayer('gfa', 'Custom (no floorKey)', '#8844ff');   // NO floorKey
  PS[1] = {scale:{pts_per_m:1}, annotations:[], objects:[
    poly('gfa',10,10),                                            // 100
    poly('ded',2,5,100,0,'deduction_opening'),                    // 10
    {id:state._id++,catId:'count',semanticTag:'count_marker',kind:'count',counting:true,dimVisible:false,pts:[{x:1,y:1}]}
  ]};
  PS[2] = {scale:{pts_per_m:1}, annotations:[], objects:[ poly('gfa',10,20) ]};   // 200
  PS[3] = {scale:{pts_per_m:1}, annotations:[], objects:[
    poly(L1.id,5,10),                                             // 50, role gfa, unpinned
    poly('ded',1,5,100,0,'deduction_opening')                     // 5
  ]};
  curPage = 1;

  var tuples = A().objectTuples();
  var allMatchPage = tuples.every(function(t){ return t.floorKey === A().floorKeyOfPage(t.pg); });
  var bfr = A().byFloorRole(tuples), br = A().byRole(tuples);
  var f1gfa = (bfr['floor:1']&&bfr['floor:1'].gfa&&bfr['floor:1'].gfa.area)||0;
  var f2gfa = (bfr['floor:2']&&bfr['floor:2'].gfa&&bfr['floor:2'].gfa.area)||0;
  var f1ded = (bfr['floor:1']&&bfr['floor:1'].ded&&bfr['floor:1'].ded.area)||0;
  // page1 gfa 100 + page3 custom-gfa 50 both floor:1 => 150; page2 => 200; ded 10+5 both floor:1 => 15
  var bucketsOk = close(f1gfa,150) && close(f2gfa,200) && close(f1ded,15);
  var roleOk = close(br.gfa.area, 350) && close(br.ded.area, 15) && (br.count&&br.count.count===1);
  var oracleOk = A().assertEnginesAgree(1e-6).ok === true;
  var noDiverge = A().detectDivergence().length === 0;

  return {legacyParity: allMatchPage && bucketsOk && roleOk && oracleOk && noDiverge,
          _allMatchPage:allMatchPage,_bucketsOk:bucketsOk,_roleOk:roleOk,_oracleOk:oracleOk,_noDiverge:noDiverge,
          _f1gfa:f1gfa,_f2gfa:f2gfa,_f1ded:f1ded,
          pass: allMatchPage && bucketsOk && roleOk && oracleOk && noDiverge};
}
"""


# --- P2: re-tag follows layer + divergence feed ----------------------------
SC_P2 = r"""
async () => {
  if (typeof window.ObjectAgg !== 'object') return {pass:false, err:'ObjectAgg missing'};
""" + PRELUDE + r"""
  PS = {}; excluded = {}; pageTags = {}; pageFloorKind = {}; pageFloorNum = {};
  pageTags[5]='floor'; pageFloorNum[5]=1; pageFloorKind[5]='normal';
  var Lp = addLayer('gfa', 'Pinned floor1', '#8844ff'); Lp.floorKey = 'floor:1';
  PS[5] = {scale:{pts_per_m:1}, annotations:[], objects:[
    poly(Lp.id,8,10),          // 80, pinned floor:1
    poly('gfa',4,10,100,0)     // 40, follows page
  ]};
  curPage = 5;

  var before = A().objectTuples();
  var totBefore = before.reduce(function(s,t){return s+(t.area||0);},0);
  var DA = A().detectDivergence;
  var divBefore = (typeof DA==='function') ? DA() : [];

  pageFloorNum[5] = 2;                    // RE-TAG floor 1 -> 2

  var after = A().objectTuples();
  var bf = A().byFloor(after);
  var totAfter = after.reduce(function(s,t){return s+(t.area||0);},0);
  var div = (typeof DA==='function') ? DA() : [];

  var pinnedStayed = !!(bf['floor:1']) && close(bf['floor:1'].area, 80);
  var defaultMoved = !!(bf['floor:2']) && close(bf['floor:2'].area, 40);
  var totalUnchanged = close(totBefore, totAfter);
  var divOk = div.length === 1 && div[0].layerId === Lp.id &&
              div[0].layerFloorKey === 'floor:1' && div[0].pageFloorKey === 'floor:2' &&
              div[0].pg === 5 && div[0].count === 1;
  var noDivBefore = divBefore.length === 0;

  return {followsLayer: pinnedStayed && defaultMoved && totalUnchanged && divOk && noDivBefore,
          _pinnedStayed:pinnedStayed,_defaultMoved:defaultMoved,_totalUnchanged:totalUnchanged,
          _divOk:divOk,_noDivBefore:noDivBefore,_div:div,_bfKeys:Object.keys(bf),
          pass: pinnedStayed && defaultMoved && totalUnchanged && divOk && noDivBefore};
}
"""


# --- P3: two gfa layers, different floors, same page -----------------------
SC_P3 = r"""
async () => {
  if (typeof window.ObjectAgg !== 'object') return {pass:false, err:'ObjectAgg missing'};
""" + PRELUDE + r"""
  PS = {}; excluded = {}; pageTags = {}; pageFloorKind = {}; pageFloorNum = {};
  pageTags[7]='floor'; pageFloorNum[7]=1; pageFloorKind[7]='normal';
  var LA = addLayer('gfa','slab f1','#4c8dff'); LA.floorKey = 'floor:1';
  var LB = addLayer('gfa','mezz f2','#39d98a'); LB.floorKey = 'floor:2';
  PS[7] = {scale:{pts_per_m:1}, annotations:[], objects:[
    poly(LA.id,6,10),      // 60 -> floor:1
    poly(LB.id,9,10,100,0) // 90 -> floor:2
  ]};
  curPage = 7;

  var t = A().objectTuples();
  var bfr = A().byFloorRole(t), br = A().byRole(t);
  var f1 = (bfr['floor:1']&&bfr['floor:1'].gfa&&bfr['floor:1'].gfa.area)||0;
  var f2 = (bfr['floor:2']&&bfr['floor:2'].gfa&&bfr['floor:2'].gfa.area)||0;
  var distinct = close(f1,60) && close(f2,90);
  var sumEqRole = close(f1 + f2, br.gfa.area);
  var onePage = Object.keys(PS).length === 1;

  return {twoLayersOnePage: distinct && sumEqRole && onePage,
          _f1:f1,_f2:f2,_roleGfa:br.gfa.area,_distinct:distinct,_sumEqRole:sumEqRole,_onePage:onePage,
          pass: distinct && sumEqRole && onePage};
}
"""


# --- P4: CFSS master floorKey:"multi" -> per-instance page ------------------
SC_P4 = r"""
async () => {
  if (typeof window.ObjectAgg !== 'object') return {pass:false, err:'ObjectAgg missing'};
""" + PRELUDE + r"""
  // wait for cross-floor-shapes.js (rollupAreaM2/rollupCatId injected dynamically)
  for (var i=0; i<80 && typeof window.rollupAreaM2 !== 'function'; i++) {
    await new Promise(function(r){ setTimeout(r,50); });
  }
  if (typeof window.rollupAreaM2 !== 'function') return {pass:false, err:'cfss not loaded'};

  PS = {}; excluded = {}; pageTags = {}; pageFloorKind = {}; pageFloorNum = {};
  pageTags[1]='floor'; pageFloorNum[1]=1; pageFloorKind[1]='normal';
  pageTags[2]='floor'; pageFloorNum[2]=2; pageFloorKind[2]='normal';
  window.MASTERS['mMulti'] = {id:'mMulti', name:'lift core', color:'#888', createdAt:Date.now(),
    catId:'gfa', floorKey:'multi',
    metricPts:[{x_m:0,y_m:0},{x_m:5,y_m:0},{x_m:5,y_m:5},{x_m:0,y_m:5}]};   // area 25
  PS[1] = {scale:{pts_per_m:1}, annotations:[], objects:[{kind:'instance',masterId:'mMulti',offsetPt:{x:0,y:0}}]};
  PS[2] = {scale:{pts_per_m:1}, annotations:[], objects:[{kind:'instance',masterId:'mMulti',offsetPt:{x:0,y:0}}]};
  curPage = 1;

  var t = A().objectTuples();
  // every instance tuple follows its own page floor (multi master == today)
  var allMatchPage = t.every(function(x){ return x.floorKey === A().floorKeyOfPage(x.pg); });
  var bfr = A().byFloorRole(t);
  var f1 = (bfr['floor:1']&&bfr['floor:1'].gfa&&bfr['floor:1'].gfa.area)||0;
  var f2 = (bfr['floor:2']&&bfr['floor:2'].gfa&&bfr['floor:2'].gfa.area)||0;
  var perInstance = close(f1,25) && close(f2,25);
  var noDiverge = A().detectDivergence().length === 0;   // 'multi' never diverges

  return {cfssMultiPerInst: allMatchPage && perInstance && noDiverge,
          _allMatchPage:allMatchPage,_f1:f1,_f2:f2,_perInstance:perInstance,_noDiverge:noDiverge,
          pass: allMatchPage && perInstance && noDiverge};
}
"""


# --- P5: save/load round-trip (real mi-save + loadProto) --------------------
SC_P5 = r"""
async () => {
  if (typeof window.ObjectAgg !== 'object') return {pass:false, err:'ObjectAgg missing'};
""" + PRELUDE + r"""
  // fixture: custom layer pinned floor:2, object drawn on a floor:1 page
  PS = {}; excluded = {}; pageTags = {}; pageFloorKind = {}; pageFloorNum = {};
  pageRot = pageRot || {}; pageNames = pageNames || {}; projectInfo = projectInfo || {};
  pageTags[1]='floor'; pageFloorNum[1]=1; pageFloorKind[1]='normal';
  pageTags[2]='floor'; pageFloorNum[2]=2; pageFloorKind[2]='normal';
  var Lp = addLayer('gfa','Pinned f2','#8844ff'); Lp.floorKey = 'floor:2';
  var obj = poly(Lp.id, 8, 10);          // 80, layer pinned floor:2, on floor:1 page
  PS[1] = {scale:{pts_per_m:1}, annotations:[], objects:[obj]};
  PS[2] = {scale:{pts_per_m:1}, annotations:[], objects:[]};
  curPage = 1; pageCount = 2;
  window.caseId = 'test-case'; window.pdfName = 'roundtrip.pdf';

  // ---- SAVE: capture the real serialised doc via the mi-save click path ----
  var captured = null;
  var origCreate = URL.createObjectURL;
  var origClick = HTMLAnchorElement.prototype.click;
  URL.createObjectURL = function(b){ captured = b; return 'blob:test'; };
  HTMLAnchorElement.prototype.click = function(){};
  try {
    await document.getElementById('mi-save').onclick({});
  } finally {
    URL.createObjectURL = origCreate;
    HTMLAnchorElement.prototype.click = origClick;
  }
  if (!captured) return {pass:false, err:'save produced no blob'};
  var docText = await captured.text();
  var doc = JSON.parse(docText);
  var savedLayer = (doc.liteLayers||[]).filter(function(l){ return l.id === Lp.id; })[0];
  var saveWritesFloorKey = !!savedLayer && savedLayer.floorKey === 'floor:2';

  // ---- LOAD (with floorKey): loadProto restores the pin ----
  window.loadProto(JSON.parse(docText));
  var loadedLayer = layerById(Lp.id);
  var loadReadsFloorKey = !!loadedLayer && loadedLayer.floorKey === 'floor:2';
  // locate the reloaded object and check its bucket
  var ro = null; Object.keys(PS).forEach(function(k){ (PS[k].objects||[]).forEach(function(o){ if(o.catId===Lp.id) ro={o:o,pg:+k}; }); });
  var objOnF2 = !!ro && A().floorKeyOfObject(ro.o, ro.pg) === 'floor:2';
  var brWith = A().byRole(A().objectTuples());
  var gfaWith = brWith.gfa ? brWith.gfa.area : 0;

  // ---- LOAD (old-format): delete floorKey, must still load + fall back to page ----
  var docOld = JSON.parse(docText);
  (docOld.liteLayers||[]).forEach(function(l){ delete l.floorKey; });
  window.loadProto(docOld);
  var oldLayer = layerById(Lp.id);
  var oldNoFloorKey = !!oldLayer && !oldLayer.floorKey;
  var ro2 = null; Object.keys(PS).forEach(function(k){ (PS[k].objects||[]).forEach(function(o){ if(o.catId===Lp.id) ro2={o:o,pg:+k}; }); });
  var objOnPageFloor = !!ro2 && A().floorKeyOfObject(ro2.o, ro2.pg) === 'floor:1';
  var brOld = A().byRole(A().objectTuples());
  var gfaOld = brOld.gfa ? brOld.gfa.area : 0;
  var roleTotalUnchanged = close(gfaWith, gfaOld) && close(gfaWith, 80);

  return {saveLoadRoundtrip: saveWritesFloorKey && loadReadsFloorKey && objOnF2 &&
                             oldNoFloorKey && objOnPageFloor && roleTotalUnchanged,
          _saveWrites:saveWritesFloorKey,_loadReads:loadReadsFloorKey,_objOnF2:objOnF2,
          _oldNoFloorKey:oldNoFloorKey,_objOnPageFloor:objOnPageFloor,
          _gfaWith:gfaWith,_gfaOld:gfaOld,_roleTotalUnchanged:roleTotalUnchanged,
          pass: saveWritesFloorKey && loadReadsFloorKey && objOnF2 &&
                oldNoFloorKey && objOnPageFloor && roleTotalUnchanged};
}
"""


CHECKS = [
    ("P1 legacyParity",      SC_P1, ["legacyParity"]),
    ("P2 followsLayer",      SC_P2, ["followsLayer"]),
    ("P3 twoLayersOnePage",  SC_P3, ["twoLayersOnePage"]),
    ("P4 cfssMultiPerInst",  SC_P4, ["cfssMultiPerInst"]),
    ("P5 saveLoadRoundtrip", SC_P5, ["saveLoadRoundtrip"]),
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
        print("LITE-LAYER-FLOORKEY checks:")
        for name, scenario, required_keys in CHECKS:
            pg.reload(wait_until="networkidle")
            time.sleep(0.4)
            try:
                result = pg.evaluate(scenario)
            except Exception as ex:
                print(f"  {name:24s} -> EXCEPTION: {ex}")
                failures.append(f"check '{name}' threw: {ex}")
                continue
            ok = all(result.get(k) is True for k in required_keys)
            status = "PASS" if ok else "FAIL"
            print(f"  {name:24s} -> {status}  {result}")
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
        print("LITE_LAYER_FLOORKEY_FAIL")
        sys.exit(1)
    else:
        print("LITE_LAYER_FLOORKEY_OK")


if __name__ == "__main__":
    main()
