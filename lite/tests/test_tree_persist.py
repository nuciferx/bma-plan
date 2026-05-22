"""
LITE-TREE-PERSIST regression guard (LST-2 sprint).

Verifies that the sublayer-tree (FOLDERS + layer.parentId) survives a
.bmaplan save/load round-trip and that the schema change is purely additive.

Checks:
  roundTripTree            build 2 folders (nested) + layer nested in inner
                           folder + sublayer under that layer → produce save doc
                           → reset LAYERS/FOLDERS → run load → FOLDERS rebuilt
                           (ids/parentId/order) AND each layer's parentId restored.
  backwardCompatNoGroups   load a doc with liteLayers WITHOUT parentId and NO
                           liteGroups → all layers parentId===null,
                           FOLDERS.length===0, no JS error.
  additiveShape            produced save doc has liteGroups array AND every
                           liteLayers entry has a parentId key; AND a pageStore
                           object still carries liteCatId + semanticTag.
  aliasIntactAfterLoad     capture LAYERS & FOLDERS refs before load; after
                           load both are the SAME array objects (identity ===).
  orphanReparentsToRoot    load a doc where a liteLayers entry has parentId
                           pointing to an id in neither liteGroups nor liteLayers
                           → after load that layer's parentId===null, no crash.

Emits LITE_TREE_PERSIST_OK on success.

    py -3 lite/tests/test_tree_persist.py
"""
import socket, threading, time, sys
from pathlib import Path

LITE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LITE))
import uvicorn
from playwright.sync_api import sync_playwright


def _free_port(start=8340):
    for p in range(start, start + 60):
        with socket.socket() as s:
            if s.connect_ex(("127.0.0.1", p)) != 0:
                return p
    raise RuntimeError("no free port")


# --------------------------------------------------------------------------
# All checks run in a single page.evaluate() call for speed.
# Each check resets LAYERS and FOLDERS before running via reseed().
# --------------------------------------------------------------------------
SCENARIO = r"""
() => {
  const out = {};

  /* Helper: reset LAYERS to the 6 defaults and FOLDERS to empty */
  function reseed() {
    LAYERS.length = 0;
    FOLDERS.length = 0;
    initLayers();
    ROLE_DEFS.forEach(function(rd) {
      state.catVis[rd.id] = true;
      state.catLock[rd.id] = false;
    });
  }

  /* Helper: reset PS to empty */
  function resetPS() { PS = {}; }

  /* Helper: capture LAYERS and FOLDERS array references */
  function captureRefs() { return { layers: LAYERS, folders: FOLDERS }; }

  // -----------------------------------------------------------------------
  // roundTripTree
  //   Build: outer folder F_out → inner folder F_in (child of F_out) →
  //          one layer under F_in (parentId=F_in.id) →
  //          one sublayer under that layer (parentId=parentLayer.id)
  //   Produce save doc (replicate what the SAVE button builds) →
  //   JSON round-trip → loadProto(doc) →
  //   Assert: FOLDERS has both folders with correct ids/parentId/order,
  //           and each layer's parentId is restored exactly.
  // -----------------------------------------------------------------------
  reseed(); resetPS();

  const F_out = addFolder('ชั้น 1', '#ff0000', null);
  const F_in  = addFolder('โซน A', '#00ff00', F_out.id);
  const parentLayer = addLayer('gfa', 'พื้นที่หลัก', '#4c8dff');
  parentLayer.parentId = F_in.id;
  const childLayer = addLayer('use', 'พื้นที่ย่อย', '#39d98a');
  childLayer.parentId = parentLayer.id;

  // Replicate SAVE block exactly
  const liteLayersArr = layersInOrder().map(function(l) {
    return {id:l.id, name:l.name, color:l.color, role:l.role, order:l.order,
            parentId:(l.parentId!==undefined?l.parentId:null)};
  });
  const liteGroupsArr = foldersInOrder().map(function(f) {
    return {id:f.id, name:f.name, color:f.color,
            parentId:(f.parentId!==undefined?f.parentId:null), order:f.order};
  });
  const docRT = {version:1, app:"bma-plan-lite", pdfName:"test.pdf",
    totalPages:1, pageStore:{}, pageRotations:{}, pageTags:{}, pageNames:{},
    projectInfo:{}, siteOrientation:{}, excludedPages:[], pageFloorKind:{},
    pageFloorNum:{}, liteLayers: liteLayersArr, liteGroups: liteGroupsArr};

  const savedFOutId = F_out.id;
  const savedFInId  = F_in.id;
  const savedParentLayerId = parentLayer.id;
  const savedChildLayerId  = childLayer.id;

  reseed(); resetPS();
  loadProto(JSON.parse(JSON.stringify(docRT)));

  // FOLDERS check
  const fOut2 = folderById(savedFOutId);
  const fIn2  = folderById(savedFInId);
  const foldersOk = !!(fOut2 && fOut2.parentId === null
                    && fIn2  && fIn2.parentId  === savedFOutId);

  // Layer parentIds check
  const pLayer2 = layerById(savedParentLayerId);
  const cLayer2 = layerById(savedChildLayerId);
  const layerParentsOk = !!(pLayer2 && pLayer2.parentId === savedFInId
                          && cLayer2 && cLayer2.parentId === savedParentLayerId);

  out.roundTripTree = foldersOk && layerParentsOk;

  // -----------------------------------------------------------------------
  // backwardCompatNoGroups
  //   Load a doc with liteLayers that have NO parentId field and NO liteGroups.
  //   → all layers should have parentId===null; FOLDERS.length===0; no crash.
  // -----------------------------------------------------------------------
  reseed(); resetPS();

  const docOldFormat = {version:1, app:"bma-plan-lite", pdfName:"test.pdf",
    totalPages:1, pageStore:{}, pageRotations:{}, pageTags:{}, pageNames:{},
    projectInfo:{}, siteOrientation:{}, excludedPages:[], pageFloorKind:{},
    pageFloorNum:{},
    liteLayers: [
      {id:"gfa",  name:"พื้นที่อาคาร",  color:"#4c8dff", role:"gfa",  order:0},
      {id:"use",  name:"พื้นที่ใช้สอย", color:"#39d98a", role:"use",  order:1},
      {id:"ded",  name:"ช่องว่าง/หัก",  color:"#ff6b6b", role:"ded",  order:2},
      {id:"site", name:"ที่ดิน",        color:"#c084fc", role:"site", order:3},
      {id:"open", name:"ที่ว่าง",       color:"#ffb454", role:"open", order:4},
      {id:"count",name:"นับจำนวน",      color:"#22d3ee", role:"count",order:5}
      /* NO parentId fields, NO liteGroups */
    ]
    /* NO liteGroups key */
  };

  reseed(); resetPS();
  loadProto(JSON.parse(JSON.stringify(docOldFormat)));

  const foldersEmpty = (FOLDERS.length === 0);
  const allParentsNull = LAYERS.every(function(l) { return l.parentId === null; });
  out.backwardCompatNoGroups = foldersEmpty && allParentsNull;

  // -----------------------------------------------------------------------
  // additiveShape
  //   Produce a save doc via the real save-block logic, then assert:
  //   1. doc.liteGroups is an Array
  //   2. every liteLayers entry has a "parentId" key (even if null)
  //   3. a pageStore poly still carries liteCatId AND semanticTag
  // -----------------------------------------------------------------------
  reseed(); resetPS();

  // Add one folder and a custom layer
  const fAdditiveTest = addFolder('TestFolder', '#aabbcc', null);
  const lAdditiveTest = addLayer('gfa', 'TestLayer', '#112233');
  lAdditiveTest.parentId = fAdditiveTest.id;

  // Add a poly object on page 1
  PS["1"] = {
    scale: null,
    objects: [{
      id: 9001,
      catId: "gfa",
      semanticTag: "gross_floor_area",
      kind: "poly",
      counting: false,
      pts: [{x:0,y:0},{x:1,y:0},{x:1,y:1}],
      dimVisible: true
    }],
    annotations: []
  };

  const liteLayersA = layersInOrder().map(function(l) {
    return {id:l.id, name:l.name, color:l.color, role:l.role, order:l.order,
            parentId:(l.parentId!==undefined?l.parentId:null)};
  });
  const liteGroupsA = foldersInOrder().map(function(f) {
    return {id:f.id, name:f.name, color:f.color,
            parentId:(f.parentId!==undefined?f.parentId:null), order:f.order};
  });
  const psA = buildPageStore();

  const groupsIsArray = Array.isArray(liteGroupsA) && liteGroupsA.length >= 1;
  const allHaveParentId = liteLayersA.every(function(e) { return 'parentId' in e; });

  const poly0 = psA["1"] && psA["1"].polys && psA["1"].polys[0];
  const protoFieldsOk = !!(poly0 && 'liteCatId' in poly0 && 'semanticTag' in poly0);

  out.additiveShape = groupsIsArray && allHaveParentId && protoFieldsOk;

  // -----------------------------------------------------------------------
  // aliasIntactAfterLoad
  //   Capture LAYERS and FOLDERS references BEFORE load.
  //   After loadProto, the same array objects must be at LAYERS and FOLDERS.
  // -----------------------------------------------------------------------
  reseed(); resetPS();

  const refsBefore = captureRefs();

  const customForAlias = addLayer('use', 'AliasTest', '#aabbcc');
  const folderForAlias = addFolder('AliasFolder', '#ccbbaa', null);
  customForAlias.parentId = folderForAlias.id;

  const liteLayersAl = layersInOrder().map(function(l) {
    return {id:l.id, name:l.name, color:l.color, role:l.role, order:l.order,
            parentId:(l.parentId!==undefined?l.parentId:null)};
  });
  const liteGroupsAl = foldersInOrder().map(function(f) {
    return {id:f.id, name:f.name, color:f.color,
            parentId:(f.parentId!==undefined?f.parentId:null), order:f.order};
  });
  const docAlias = {version:1, app:"bma-plan-lite", pdfName:"test.pdf",
    totalPages:1, pageStore:{}, pageRotations:{}, pageTags:{}, pageNames:{},
    projectInfo:{}, siteOrientation:{}, excludedPages:[], pageFloorKind:{},
    pageFloorNum:{}, liteLayers: liteLayersAl, liteGroups: liteGroupsAl};

  reseed(); resetPS();
  loadProto(JSON.parse(JSON.stringify(docAlias)));

  const layersSameRef  = (LAYERS  === refsBefore.layers);
  const foldersSameRef = (FOLDERS === refsBefore.folders);
  out.aliasIntactAfterLoad = layersSameRef && foldersSameRef;

  // -----------------------------------------------------------------------
  // orphanReparentsToRoot
  //   Load a doc where one liteLayers entry has parentId pointing to an id
  //   that exists in NEITHER liteGroups NOR liteLayers.
  //   → after load that layer's parentId must be null; no crash.
  // -----------------------------------------------------------------------
  reseed(); resetPS();

  const docOrphan = {version:1, app:"bma-plan-lite", pdfName:"test.pdf",
    totalPages:1, pageStore:{}, pageRotations:{}, pageTags:{}, pageNames:{},
    projectInfo:{}, siteOrientation:{}, excludedPages:[], pageFloorKind:{},
    pageFloorNum:{},
    liteLayers: [
      {id:"gfa",  name:"พื้นที่อาคาร",  color:"#4c8dff", role:"gfa",  order:0, parentId:"GHOST_ID_THAT_DOES_NOT_EXIST"},
      {id:"use",  name:"พื้นที่ใช้สอย", color:"#39d98a", role:"use",  order:1, parentId:null},
      {id:"ded",  name:"ช่องว่าง/หัก",  color:"#ff6b6b", role:"ded",  order:2, parentId:null},
      {id:"site", name:"ที่ดิน",        color:"#c084fc", role:"site", order:3, parentId:null},
      {id:"open", name:"ที่ว่าง",       color:"#ffb454", role:"open", order:4, parentId:null},
      {id:"count",name:"นับจำนวน",      color:"#22d3ee", role:"count",order:5, parentId:null}
    ],
    liteGroups: [] /* no folders — the "GHOST_ID" is truly orphaned */
  };

  reseed(); resetPS();
  loadProto(JSON.parse(JSON.stringify(docOrphan)));

  const gfaLayer = layerById("gfa");
  const orphanFixed = !!(gfaLayer && gfaLayer.parentId === null);
  out.orphanReparentsToRoot = orphanFixed;

  // Restore clean state
  reseed();
  return out;
}
"""

CHECKS = [
    "roundTripTree",
    "backwardCompatNoGroups",
    "additiveShape",
    "aliasIntactAfterLoad",
    "orphanReparentsToRoot",
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
    print("LITE-TREE-PERSIST checks:")
    for k in CHECKS:
        ok = result.get(k)
        print(f"  {k:35s} -> {ok}")
        if ok is not True:
            failures.append(f"check '{k}' = {ok!r} (expected True)")

    if failures:
        for f in failures:
            print("FAIL:", f)
        print("LITE_TREE_PERSIST_FAIL")
        sys.exit(1)
    else:
        print("LITE_TREE_PERSIST_OK")


if __name__ == "__main__":
    main()
