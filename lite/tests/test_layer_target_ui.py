"""
INV-20260703-layer-redesign — sub-sprint B-ui (layer draw-target UI) test.

Exercises the NEW module static/js/layer-target-ui.js against the LIVE app via
Playwright evaluate. The module is DOM-injected (ui-lite.html untouched except
+1 <script> tag) and builds on the A-model seams already shipped in
object-agg.js (floorKeyOfObject / floorKeyLabel / detectDivergence /
PF-seeded layer.floorKey).

Checks:
  C1 chip           #ltu-chip exists, shows the active layer name + the floor
                    label its floorKey resolves to; switching the active layer
                    updates chip text+color; switching page updates the floor
                    part (layer with no floorKey follows the page tag).
  C2 tint           #ltu-edge armed (data-armed=1, box-shadow set) when a
                    drawing tool (poly) is active, absent on select; the tint
                    colour tracks the active layer colour.
  C3 makeCurrent    real seeded layer rows: clicking a panel row moves the
                    single ◉ (.ltu-current) marker onto that row and the chip
                    follows. (Finding: rows ALREADY set state.activeCat on
                    click — the module only adds the visual current-marker.)
  C4 banner         build a divergence (layer pinned floor:1, page re-tagged
                    floor:2, 1 object) → reconcile() shows the banner with the
                    right text+count; [ตามหน้า] clears layer.floorKey, hides the
                    banner and moves the byFloorRole bucket back to the page
                    floor; [ตามเลเยอร์] dismiss hides it and it does NOT reappear
                    on the same page without a new divergence.
  C5 noPageError    no uncaught JS error across all scenarios.

Emits LITE_LAYER_TARGET_UI_OK on success.

RED note: the UI is brand-new (no pre-sprint version to stash), so there is no
meaningful RED baseline to demonstrate — with layer-target-ui.js absent every
check simply reports the element missing. Stated honestly per B-ui report.

    py -3 lite/tests/test_layer_target_ui.py
"""
import socket, threading, time, sys
from pathlib import Path

LITE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LITE))
import uvicorn
from playwright.sync_api import sync_playwright


def _free_port(start=8580):
    for p in range(start, start + 60):
        with socket.socket() as s:
            if s.connect_ex(("127.0.0.1", p)) != 0:
                return p
    raise RuntimeError("no free port")


PRELUDE = r"""
function sleep(ms){ return new Promise(function(r){ setTimeout(r, ms); }); }
async function waitChip(){
  for (var i=0; i<60 && !document.getElementById('ltu-chip'); i++) { await sleep(50); }
  return document.getElementById('ltu-chip');
}
function rect(w,h,ox,oy){ ox=ox||0; oy=oy||0; return [{x:ox,y:oy},{x:ox+w,y:oy},{x:ox+w,y:oy+h},{x:ox,y:oy+h}]; }
function poly(catId,w,h,ox,oy){ return {id: state._id++, catId:catId, semanticTag:'gross_floor_area',
  kind:'poly', counting:false, dimVisible:true, pts:rect(w,h,ox,oy)}; }
function lc(s){ return String(s||'').toLowerCase(); }
function A(){ return window.ObjectAgg; }
function LT(){ return window.LayerTargetUI; }
"""


# --- C1 chip -----------------------------------------------------------------
SC_C1 = r"""
async () => {
""" + PRELUDE + r"""
  var chip = await waitChip();
  if (!chip) return {pass:false, err:'chip not injected'};
  if (typeof LT() !== 'object') return {pass:false, err:'LayerTargetUI missing'};

  PS={}; excluded={}; pageTags={}; pageFloorKind={}; pageFloorNum={};
  pageTags[1]='floor'; pageFloorNum[1]=1; pageFloorKind[1]='normal';
  pageTags[2]='floor'; pageFloorNum[2]=2; pageFloorKind[2]='normal';
  curPage=1; state.activeCat='gfa';
  LT().sync();

  var gfa = layerById('gfa');
  var floor1 = document.getElementById('ltu-floor').textContent;
  var layer1 = document.getElementById('ltu-layer').textContent;
  var color1 = chip.getAttribute('data-color');
  var showsName = layer1.indexOf(gfa.name) >= 0;
  var floorOk1 = floor1 === A().floorKeyLabel('floor:1');   // 'ชั้น 1'
  var colorOk1 = lc(color1) === lc(gfa.color);

  // switch active layer -> text + colour update
  var L = addLayer('ded', 'ผนังหักทดสอบ', '#ff6b6b');
  state.activeCat = L.id; LT().sync();
  var layer2 = document.getElementById('ltu-layer').textContent;
  var color2 = chip.getAttribute('data-color');
  var switchName = layer2.indexOf(L.name) >= 0;
  var switchColor = lc(color2) === '#ff6b6b';

  // switch page -> floor part follows the page tag (L has no floorKey)
  curPage = 2; LT().sync();
  var floor2 = document.getElementById('ltu-floor').textContent;
  var pageChanged = floor2 === A().floorKeyLabel('floor:2');   // 'ชั้น 2'

  var pass = showsName && floorOk1 && colorOk1 && switchName && switchColor && pageChanged;
  return {pass:pass, _showsName:showsName,_floorOk1:floorOk1,_colorOk1:colorOk1,
          _switchName:switchName,_switchColor:switchColor,_pageChanged:pageChanged,
          _floor1:floor1,_layer1:layer1,_floor2:floor2};
}
"""


# --- C2 tint -----------------------------------------------------------------
SC_C2 = r"""
async () => {
""" + PRELUDE + r"""
  var chip = await waitChip();
  if (!chip) return {pass:false, err:'chip not injected'};
  var edge = document.getElementById('ltu-edge');
  if (!edge) return {pass:false, err:'edge not injected'};

  PS={}; excluded={}; pageTags={}; pageFloorKind={}; pageFloorNum={};
  pageTags[1]='floor'; pageFloorNum[1]=1; pageFloorKind[1]='normal';
  curPage=1; state.activeCat='gfa'; state.panTool=false;

  state.tool='poly'; LT().sync();
  var armedPoly = edge.getAttribute('data-armed') === '1';
  var shadowOn  = !!edge.style.boxShadow && edge.style.boxShadow !== 'none';
  var colorPoly = lc(edge.getAttribute('data-color')) === lc(layerById('gfa').color);

  // colour tracks the active layer (custom colour)
  var Lg = addLayer('gfa', 'สแลบทดสอบ', '#39d98a');
  state.activeCat = Lg.id; LT().sync();
  var colorCustom = lc(edge.getAttribute('data-color')) === '#39d98a';

  state.tool='select'; LT().sync();
  var armedSel = edge.getAttribute('data-armed') === '1';
  var shadowOff = !edge.style.boxShadow || edge.style.boxShadow === 'none';

  var pass = armedPoly && shadowOn && colorPoly && colorCustom && !armedSel && shadowOff;
  return {pass:pass, _armedPoly:armedPoly,_shadowOn:shadowOn,_colorPoly:colorPoly,
          _colorCustom:colorCustom,_armedSel:armedSel,_shadowOff:shadowOff};
}
"""


# --- C3 make-current ---------------------------------------------------------
SC_C3 = r"""
async () => {
""" + PRELUDE + r"""
  var chip = await waitChip();
  if (!chip) return {pass:false, err:'chip not injected'};

  PS={}; excluded={}; pageTags={}; pageFloorKind={}; pageFloorNum={};
  pageTags[1]='floor'; pageFloorNum[1]=1; pageFloorKind[1]='normal';
  pageCount=1; curPage=1;
  if (typeof reseedActivePageFolders === 'function') reseedActivePageFolders();
  buildPicker();

  var list = document.getElementById('catlist');
  var rows = list.querySelectorAll('[data-nodekind="layer"]');
  if (rows.length < 2) return {pass:false, err:'need >=2 seeded layer rows, got '+rows.length};

  function markerCatId(){
    var m = list.querySelector('.ltu-current');
    if (!m) return null;
    var r = m.closest('[data-catid]');
    return r ? r.getAttribute('data-catid') : null;
  }
  function rowClickHasActiveCat(){
    // FINDING probe: confirm the row's own click handler already sets activeCat.
    return true; // asserted behaviourally below (click moves activeCat)
  }

  var catA = rows[0].getAttribute('data-catid');
  rows[0].dispatchEvent(new MouseEvent('click', {bubbles:true}));
  var markerOnA = markerCatId() === catA;
  var single1 = list.querySelectorAll('.ltu-current').length === 1;
  var chipFollowsA = document.getElementById('ltu-layer').textContent.indexOf(layerById(catA).name) >= 0;
  var activeIsA = state.activeCat === catA;   // rows already set activeCat

  // click a different row
  rows = list.querySelectorAll('[data-nodekind="layer"]');
  var rowB = null, catB = null;
  for (var i=0;i<rows.length;i++){ if (rows[i].getAttribute('data-catid') !== catA){ rowB=rows[i]; catB=rowB.getAttribute('data-catid'); break; } }
  if (!rowB) return {pass:false, err:'no distinct second row'};
  rowB.dispatchEvent(new MouseEvent('click', {bubbles:true}));
  var markerMoved = markerCatId() === catB;
  var single2 = document.querySelectorAll('#catlist .ltu-current').length === 1;
  var chipFollowsB = document.getElementById('ltu-layer').textContent.indexOf(layerById(catB).name) >= 0;
  var activeIsB = state.activeCat === catB;

  var pass = markerOnA && single1 && chipFollowsA && activeIsA &&
             markerMoved && single2 && chipFollowsB && activeIsB;
  return {pass:pass, _markerOnA:markerOnA,_single1:single1,_chipFollowsA:chipFollowsA,_activeIsA:activeIsA,
          _markerMoved:markerMoved,_single2:single2,_chipFollowsB:chipFollowsB,_activeIsB:activeIsB,
          _nRows:rows.length, _catA:catA, _catB:catB};
}
"""


# --- C4 reconcile banner -----------------------------------------------------
SC_C4 = r"""
async () => {
""" + PRELUDE + r"""
  var chip = await waitChip();
  if (!chip) return {pass:false, err:'chip not injected'};
  var banner = document.getElementById('ltu-banner');
  if (!banner) return {pass:false, err:'banner not injected'};

  PS={}; excluded={}; pageTags={}; pageFloorKind={}; pageFloorNum={};
  pageTags[5]='floor'; pageFloorNum[5]=1; pageFloorKind[5]='normal';
  pageCount=5; curPage=5;
  var Lp = addLayer('gfa', 'ปักชั้น1ทดสอบ', '#8844ff'); Lp.floorKey = 'floor:1';
  PS[5] = {scale:{pts_per_m:1}, annotations:[], objects:[ poly(Lp.id, 8, 10) ]};  // area 80

  // build divergence: re-tag the page floor:1 -> floor:2 (same path as floorkey P2)
  pageFloorNum[5] = 2;
  LT().reconcile();

  var shown = banner.classList.contains('show');
  var msg = document.getElementById('ltu-banner-msg').textContent;
  var textOk = msg.indexOf(Lp.name) >= 0 &&
               msg.indexOf(A().floorKeyLabel('floor:1')) >= 0 &&
               msg.indexOf(A().floorKeyLabel('floor:2')) >= 0 &&
               msg.indexOf('1') >= 0 && msg.indexOf('วัตถุ') >= 0;

  // ---- [ตามหน้า]: clear the pin, banner hides, bucket moves to page floor ----
  document.getElementById('ltu-by-page').dispatchEvent(new MouseEvent('click', {bubbles:true}));
  var pinCleared = !layerById(Lp.id).floorKey;
  var hiddenAfterPage = !banner.classList.contains('show');
  var bfr = A().byFloorRole(A().objectTuples());
  var onF2 = !!(bfr['floor:2'] && bfr['floor:2'].gfa) && Math.abs(bfr['floor:2'].gfa.area - 80) < 1e-6;
  var notOnF1 = !(bfr['floor:1'] && bfr['floor:1'].gfa && bfr['floor:1'].gfa.area);

  // ---- rebuild divergence, then dismiss [ตามเลเยอร์]: must not reappear ----
  layerById(Lp.id).floorKey = 'floor:1';   // page still floor:2 -> diverges again
  LT().reconcile();
  var shownAgain = banner.classList.contains('show');
  document.getElementById('ltu-by-layer').dispatchEvent(new MouseEvent('click', {bubbles:true}));
  var hiddenAfterDismiss = !banner.classList.contains('show');
  LT().reconcile();   // same divergence, already dismissed -> stays hidden
  var noReappear = !banner.classList.contains('show');

  var pass = shown && textOk && pinCleared && hiddenAfterPage && onF2 && notOnF1 &&
             shownAgain && hiddenAfterDismiss && noReappear;
  return {pass:pass, _shown:shown,_textOk:textOk,_pinCleared:pinCleared,_hiddenAfterPage:hiddenAfterPage,
          _onF2:onF2,_notOnF1:notOnF1,_shownAgain:shownAgain,_hiddenAfterDismiss:hiddenAfterDismiss,
          _noReappear:noReappear, _msg:msg};
}
"""


CHECKS = [
    ("C1 chip",         SC_C1),
    ("C2 tint",         SC_C2),
    ("C3 makeCurrent",  SC_C3),
    ("C4 banner",       SC_C4),
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
        print("LITE-LAYER-TARGET-UI checks:")
        for name, scenario in CHECKS:
            pg.reload(wait_until="networkidle")
            time.sleep(0.4)
            try:
                result = pg.evaluate(scenario)
            except Exception as ex:
                print(f"  {name:18s} -> EXCEPTION: {ex}")
                failures.append(f"check '{name}' threw: {ex}")
                continue
            ok = result.get("pass") is True
            status = "PASS" if ok else "FAIL"
            print(f"  {name:18s} -> {status}  {result}")
            if not ok:
                failures.append(f"check '{name}' failed: {result}")

        pg.close()
        b.close()

    for e in page_errors:
        print("  JS ERROR:", e)
    if page_errors:
        failures.append(f"{len(page_errors)} pageerror(s) during run")

    server.should_exit = True
    time.sleep(0.4)

    if failures:
        for f in failures:
            print("FAIL:", f)
        print("LITE_LAYER_TARGET_UI_FAIL")
        sys.exit(1)
    else:
        print("LITE_LAYER_TARGET_UI_OK")


if __name__ == "__main__":
    main()
