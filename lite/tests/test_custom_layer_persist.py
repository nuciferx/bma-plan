"""
LITE-CUSTOM-LAYER-PERSIST regression guard (L2c-2 sprint).

Verifies that custom layers survive a .bmaplan save/load round-trip and that
the schema change is additive (proto-written / old files still load correctly).

Checks:
  roundtripCustomLayer      addLayer + object + buildPageStore/liteLayers →
                            loadProto → custom layer back, object.catId restored.
  liteCatIdPersisted        buildPageStore() records include liteCatId AND
                            semanticTag on every object branch.
  backwardCompatNoLiteLayers same doc WITHOUT liteLayers / liteCatId still loads;
                            LAYERS = 6 defaults; object resolves via SEM_REV.
  aliasIntact               after a liteLayers rebuild, CATS === LAYERS (same ref)
                            and CATS.length === LAYERS.length.
  defaultsAlwaysPresent     a doc.liteLayers that omits some defaults still
                            results in all 6 role defaults present after load.

Emits LITE_LAYER_PERSIST_OK on success.

    py -3 lite/tests/test_custom_layer_persist.py
"""
import socket, threading, time, sys
from pathlib import Path

LITE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LITE))
import uvicorn
from playwright.sync_api import sync_playwright


def _free_port(start=8320):
    for p in range(start, start + 60):
        with socket.socket() as s:
            if s.connect_ex(("127.0.0.1", p)) != 0:
                return p
    raise RuntimeError("no free port")


# --------------------------------------------------------------------------
# All checks run in a single page.evaluate() call for speed.
# loadProto() mutates global state (PS, LAYERS), so each check that calls it
# must reset LAYERS via reseed() + re-seed catVis/catLock to a clean slate
# before the next check.
# --------------------------------------------------------------------------
SCENARIO = r"""
() => {
  const out = {};

  /* Helper: reset LAYERS to the 6 defaults */
  function reseed() {
    LAYERS.length = 0;
    initLayers();
    // reset catVis/catLock so loadProto re-seed logic is exercised cleanly
    ROLE_DEFS.forEach(function(rd) {
      state.catVis[rd.id] = true;
      state.catLock[rd.id] = false;
    });
  }

  /* Helper: reset PS to empty */
  function resetPS() { PS = {}; }

  /* Helper: make a minimal PSpage entry for page 1 with one object */
  function makePage(catId, semanticTag) {
    PS["1"] = {
      scale: null,
      objects: [{
        id: 9001,
        catId: catId,
        semanticTag: semanticTag,
        kind: "poly",
        counting: false,
        pts: [{x:0,y:0},{x:1,y:0},{x:1,y:1},{x:0,y:1}],
        dimVisible: true
      }],
      annotations: []
    };
  }

  // -----------------------------------------------------------------------
  // roundtripCustomLayer
  //   1. addLayer('gfa', 'โซน A', '#80c0ff') → get customId
  //   2. push an object with that catId onto page 1
  //   3. call buildPageStore() and replicate the liteLayers field (real fns)
  //   4. JSON stringify/parse → doc
  //   5. call real loadProto(doc)
  //   6. assert layerById(customId) is back with correct name/color/role
  //      AND the object's catId === customId
  // -----------------------------------------------------------------------
  reseed(); resetPS();
  const customLayer = addLayer('gfa', 'โซน A', '#80c0ff');
  const customId = customLayer.id;
  makePage(customId, 'gross_floor_area');

  const ps = buildPageStore();
  const liteLayersArr = layersInOrder().map(function(l) {
    return {id:l.id, name:l.name, color:l.color, role:l.role, order:l.order};
  });
  const doc1 = {version:1, app:"bma-plan-lite", pdfName:"test.pdf",
    totalPages:1, pageStore:ps, pageRotations:{}, pageTags:{}, pageNames:{},
    projectInfo:{}, siteOrientation:{}, excludedPages:[], pageFloorKind:{},
    pageFloorNum:{}, liteLayers: liteLayersArr};
  const doc1str = JSON.stringify(doc1);
  const doc1parsed = JSON.parse(doc1str);

  reseed(); resetPS();
  loadProto(doc1parsed);

  const restoredLayer = layerById(customId);
  const restoredLayerOk = !!(restoredLayer
    && restoredLayer.name === 'โซน A'
    && restoredLayer.color === '#80c0ff'
    && restoredLayer.role === 'gfa');
  const obj1 = PS["1"] && PS["1"].objects && PS["1"].objects[0];
  const objCatIdOk = !!(obj1 && obj1.catId === customId);

  out.roundtripCustomLayer = restoredLayerOk && objCatIdOk;

  // -----------------------------------------------------------------------
  // liteCatIdPersisted
  //   buildPageStore() must include liteCatId on the poly record AND the
  //   record must still carry semanticTag.
  //   Also test counts, lines, refs branches.
  // -----------------------------------------------------------------------
  reseed(); resetPS();
  // poly object
  PS["1"] = {
    scale: null,
    objects: [
      {id:9010, catId:"gfa", semanticTag:"gross_floor_area", kind:"poly",
       counting:false, pts:[{x:0,y:0},{x:1,y:0},{x:1,y:1}], dimVisible:true},
      {id:9011, catId:"gfa", semanticTag:"dimension_line", kind:"line",
       counting:false, pts:[{x:0,y:0},{x:1,y:1}], dimVisible:true},
      {id:9012, catId:"gfa", semanticTag:"reference_line", kind:"ref",
       counting:false, pts:[{x:0,y:0},{x:1,y:1}], dimVisible:true},
      {id:9013, catId:"count", semanticTag:"count_marker", kind:"count",
       counting:true, pts:[{x:0.5,y:0.5}], dimVisible:false}
    ],
    annotations: []
  };
  const ps2 = buildPageStore();
  const st2 = ps2["1"];
  const polyRec = st2.polys[0];
  const lineRec = st2.lines[0];
  const refRec  = st2.refs[0];
  const cntRec  = st2.counts[0];
  out.liteCatIdPersisted =
    !!(polyRec && polyRec.liteCatId === "gfa" && polyRec.semanticTag === "gross_floor_area") &&
    !!(lineRec && lineRec.liteCatId === "gfa") &&
    !!(refRec  && refRec.liteCatId  === "gfa") &&
    !!(cntRec  && cntRec.liteCatId  === "count");

  // -----------------------------------------------------------------------
  // backwardCompatNoLiteLayers
  //   Take doc1parsed, remove liteLayers and liteCatId from objects,
  //   then loadProto → LAYERS still = 6 defaults, object resolves via SEM_REV.
  // -----------------------------------------------------------------------
  reseed(); resetPS();
  // rebuild a fresh doc from scratch (no liteLayers, no liteCatId)
  const docOld = {version:1, app:"bma-plan-lite", pdfName:"test.pdf",
    totalPages:1,
    pageStore: {"1": {
      polys: [{pts:[{x:0,y:0},{x:1,y:0},{x:1,y:1}], closed:true,
               areaType:"room", semanticTag:"gross_floor_area",
               id:"area-abc", color:"#4c8dff", opacity:0.18, useCategory:null}],
      openings:[], lines:[], refs:[], counts:[], annotations:[], calibScale:null
    }},
    pageRotations:{}, pageTags:{}, pageNames:{}, projectInfo:{},
    siteOrientation:{}, excludedPages:[], pageFloorKind:{}, pageFloorNum:{}
    /* NO liteLayers field */
  };

  reseed(); resetPS();
  loadProto(docOld);

  const layers6 = LAYERS.length === 6;
  const defaultsOk = ROLE_DEFS.every(function(rd) { return !!layerById(rd.id); });
  const objOld = PS["1"] && PS["1"].objects && PS["1"].objects[0];
  // SEM_REV["gross_floor_area"] === "gfa"
  const semRevOk = !!(objOld && objOld.catId === "gfa" && objOld.semanticTag === "gross_floor_area");
  out.backwardCompatNoLiteLayers = layers6 && defaultsOk && semRevOk;

  // -----------------------------------------------------------------------
  // aliasIntact
  //   After a loadProto that rebuilds LAYERS, CATS must === LAYERS (same ref)
  //   and CATS.length must === LAYERS.length.
  //   (CATS = LAYERS is set at startup; the load must mutate in-place.)
  // -----------------------------------------------------------------------
  reseed(); resetPS();
  // create a liteLayers doc that has a custom layer
  const customForAlias = addLayer('use', 'UseCustom', '#aabbcc');
  const liteLayersAlias = layersInOrder().map(function(l) {
    return {id:l.id, name:l.name, color:l.color, role:l.role, order:l.order};
  });
  const docAlias = {version:1, app:"bma-plan-lite", pdfName:"test.pdf",
    totalPages:1, pageStore:{}, pageRotations:{}, pageTags:{}, pageNames:{},
    projectInfo:{}, siteOrientation:{}, excludedPages:[], pageFloorKind:{},
    pageFloorNum:{}, liteLayers: liteLayersAlias};

  reseed(); resetPS();
  loadProto(docAlias);

  out.aliasIntact = (CATS === LAYERS) && (CATS.length === LAYERS.length);

  // -----------------------------------------------------------------------
  // defaultsAlwaysPresent
  //   A doc.liteLayers that only lists ONE layer (a custom gfa layer, omitting
  //   all 6 defaults) must still result in all 6 role defaults present after
  //   loadProto (the re-seed guard in loadProto ensures this).
  // -----------------------------------------------------------------------
  reseed(); resetPS();
  const docPartial = {version:1, app:"bma-plan-lite", pdfName:"test.pdf",
    totalPages:1, pageStore:{}, pageRotations:{}, pageTags:{}, pageNames:{},
    projectInfo:{}, siteOrientation:{}, excludedPages:[], pageFloorKind:{},
    pageFloorNum:{},
    liteLayers: [
      {id:"L99", name:"Only Layer", color:"#ff0000", role:"gfa", order:0}
      /* all 6 role defaults deliberately omitted */
    ]
  };

  reseed(); resetPS();
  loadProto(docPartial);

  const allDefaultsBack = ROLE_DEFS.every(function(rd) { return !!layerById(rd.id); });
  out.defaultsAlwaysPresent = allDefaultsBack;

  // Restore clean state
  reseed();
  return out;
}
"""

CHECKS = [
    "roundtripCustomLayer",
    "liteCatIdPersisted",
    "backwardCompatNoLiteLayers",
    "aliasIntact",
    "defaultsAlwaysPresent",
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
        result = pg.evaluate(SCENARIO)
        pg.close()
        b.close()

    server.should_exit = True
    time.sleep(0.4)

    for e in page_errors:
        print("  JS ERROR:", e)

    print()
    print("LITE-CUSTOM-LAYER-PERSIST checks:")
    for k in CHECKS:
        ok = result.get(k)
        print(f"  {k:35s} -> {ok}")
        if ok is not True:
            failures.append(f"check '{k}' = {ok!r} (expected True)")

    if failures:
        for f in failures:
            print("FAIL:", f)
        print("LITE_LAYER_PERSIST_FAIL")
        sys.exit(1)
    else:
        print("LITE_LAYER_PERSIST_OK")


if __name__ == "__main__":
    main()
