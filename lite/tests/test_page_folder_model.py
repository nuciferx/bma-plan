"""
LITE-PAGE-FOLDER-MODEL regression guard (LPFL-1a sprint).

Verifies the in-memory page-folder model in page-folder-layers.js:
  idFor              pageFolderIdFor returns correct PF_* id
  seedCreatesFolders seedPageFolders creates PF_site, PF_floor_N, PF_excluded with correct pages
  seedCreatesBaseLayers base layers seeded with correct roles per kind
  baseLayerNames     floor layer names contain floor number
  idempotent         re-seeding does not add new folders or layers
  identityPreserved  LAYERS and FOLDERS are same array objects after seed
  pageFolderOfLayer  walks ancestor chain to find PF folder
  layersOfPage       returns correct descendant layers for a page
  isPageFolder       distinguishes PF folders from user folders
  resetClean         resetPageFolders removes all PF folders + layers; defaults intact
  noRoleTagMutation  base layer .tag === roleSemanticTag(.role)
  semanticTagDecoupled renaming a base layer does not change .tag

Emits LITE_PAGE_FOLDER_MODEL_OK on success.

    py -3 lite/tests/test_page_folder_model.py
"""
import socket, threading, time, sys
from pathlib import Path

LITE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LITE))
import uvicorn
from playwright.sync_api import sync_playwright


def _free_port(start=8360):
    for p in range(start, start + 60):
        with socket.socket() as s:
            if s.connect_ex(("127.0.0.1", p)) != 0:
                return p
    raise RuntimeError("no free port")


# --------------------------------------------------------------------------
# All checks run in a single page.evaluate() for speed.
# reseed() resets LAYERS to the 6 defaults, FOLDERS to empty, in-place.
# resetPageFolders() removes PF folders + their layers; called between checks.
# --------------------------------------------------------------------------
SCENARIO = r"""
() => {
  const out = {};

  // Helper: reset LAYERS to 6 defaults and FOLDERS to empty — in-place.
  function reseed() {
    LAYERS.length = 0;
    FOLDERS.length = 0;
    initLayers();
  }

  // Mock dataset as specified in the sprint spec.
  const mockTags  = {5:"site",7:"site",8:"site",11:"floor",12:"floor",13:"floor",14:"floor",15:"floor",16:"floor",1:"cover",3:"detail",9:"section"};
  const mockFloors = {11:1,12:2,13:3,14:4,15:5,16:"roof"};
  const allPages  = [1,3,5,7,8,9,11,12,13,14,15,16];

  // -----------------------------------------------------------------------
  // idFor: pageFolderIdFor returns correct id for different tag/floor combos.
  // -----------------------------------------------------------------------
  reseed();
  const idCheck = (
    pageFolderIdFor(5, mockTags, mockFloors)    === "PF_site"      &&
    pageFolderIdFor(7, mockTags, mockFloors)    === "PF_site"      &&
    pageFolderIdFor(12, mockTags, mockFloors)   === "PF_floor_2"   &&
    pageFolderIdFor(16, mockTags, mockFloors)   === "PF_floor_roof" &&
    pageFolderIdFor(1, mockTags, mockFloors)    === "PF_excluded"  &&
    pageFolderIdFor(3, mockTags, mockFloors)    === "PF_excluded"  &&
    pageFolderIdFor(9, mockTags, mockFloors)    === "PF_excluded"
  );
  out.idFor = idCheck;

  // -----------------------------------------------------------------------
  // seedCreatesFolders: after seed, correct folders exist with pages + kind.
  // -----------------------------------------------------------------------
  reseed();
  seedPageFolders(allPages, mockTags, mockFloors);

  const fSite = folderById("PF_site");
  const siteOk = !!(fSite &&
    fSite.pages && fSite.pages.length === 3 &&
    JSON.stringify(fSite.pages) === JSON.stringify([5,7,8]) &&
    fSite.kind === "page-folder");

  const fFloor1 = folderById("PF_floor_1");
  const floor1Ok = !!(fFloor1 && fFloor1.pages && JSON.stringify(fFloor1.pages) === JSON.stringify([11]) && fFloor1.kind === "page-folder");
  const fFloor2 = folderById("PF_floor_2");
  const floor2Ok = !!(fFloor2 && fFloor2.pages && JSON.stringify(fFloor2.pages) === JSON.stringify([12]) && fFloor2.kind === "page-folder");
  const fFloor3 = folderById("PF_floor_3");
  const floor3Ok = !!(fFloor3 && fFloor3.pages && JSON.stringify(fFloor3.pages) === JSON.stringify([13]) && fFloor3.kind === "page-folder");
  const fFloor4 = folderById("PF_floor_4");
  const floor4Ok = !!(fFloor4 && fFloor4.pages && JSON.stringify(fFloor4.pages) === JSON.stringify([14]) && fFloor4.kind === "page-folder");
  const fFloor5 = folderById("PF_floor_5");
  const floor5Ok = !!(fFloor5 && fFloor5.pages && JSON.stringify(fFloor5.pages) === JSON.stringify([15]) && fFloor5.kind === "page-folder");
  const fFloorRoof = folderById("PF_floor_roof");
  const floorRoofOk = !!(fFloorRoof && fFloorRoof.pages && JSON.stringify(fFloorRoof.pages) === JSON.stringify([16]) && fFloorRoof.kind === "page-folder");
  const fExcl = folderById("PF_excluded");
  const exclOk = !!(fExcl &&
    fExcl.pages && fExcl.pages.length === 3 &&
    JSON.stringify(fExcl.pages) === JSON.stringify([1,3,9]) &&
    fExcl.kind === "page-folder");

  out.seedCreatesFolders = siteOk && floor1Ok && floor2Ok && floor3Ok && floor4Ok && floor5Ok && floorRoofOk && exclOk;

  // -----------------------------------------------------------------------
  // seedCreatesBaseLayers: correct roles under each folder kind.
  // PF_site has 3 layers: [site, gfa, use]
  // PF_floor_2 has 3 layers: [gfa, ded, ded]
  // PF_excluded has 0 layers
  // -----------------------------------------------------------------------
  // (continuing from state after seedCreatesFolders check)
  const siteDescLayers = layersOfPage(5, mockTags, mockFloors);
  const siteRoles = siteDescLayers.map(function(l){return l.role;});
  const siteLayersOk = siteRoles.length === 3 &&
    siteRoles[0] === "site" && siteRoles[1] === "gfa" && siteRoles[2] === "use";

  const floor2DescLayers = layersOfPage(12, mockTags, mockFloors);
  const floor2Roles = floor2DescLayers.map(function(l){return l.role;});
  const floor2LayersOk = floor2Roles.length === 3 &&
    floor2Roles[0] === "gfa" && floor2Roles[1] === "ded" && floor2Roles[2] === "ded";

  const exclDescLayers = layersOfPage(1, mockTags, mockFloors);
  const exclLayersOk = exclDescLayers.length === 0;

  out.seedCreatesBaseLayers = siteLayersOk && floor2LayersOk && exclLayersOk;

  // -----------------------------------------------------------------------
  // baseLayerNames: floor layer names contain the floor number.
  // PF_floor_3's gfa layer name contains "ชั้น 3"
  // PF_floor_roof's gfa layer name contains "roof"
  // -----------------------------------------------------------------------
  const floor3Layers = layersOfPage(13, mockTags, mockFloors);
  const floor3GfaLayer = floor3Layers.find(function(l){return l.role==="gfa";});
  const floor3NameOk = !!(floor3GfaLayer && floor3GfaLayer.name.indexOf("ชั้น 3") !== -1);

  const floorRoofLayers = layersOfPage(16, mockTags, mockFloors);
  const floorRoofGfaLayer = floorRoofLayers.find(function(l){return l.role==="gfa";});
  const floorRoofNameOk = !!(floorRoofGfaLayer && floorRoofGfaLayer.name.indexOf("roof") !== -1);

  out.baseLayerNames = floor3NameOk && floorRoofNameOk;

  // -----------------------------------------------------------------------
  // idempotent: calling seedPageFolders again does NOT add new folders or layers.
  // -----------------------------------------------------------------------
  const folderCountBefore = FOLDERS.length;
  const layerCountBefore  = LAYERS.length;
  const result2 = seedPageFolders(allPages, mockTags, mockFloors);
  const folderCountAfter  = FOLDERS.length;
  const layerCountAfter   = LAYERS.length;
  const skippedAll = result2.skipped.length > 0 && result2.created.length === 0;
  const countsUnchanged = folderCountAfter === folderCountBefore && layerCountAfter === layerCountBefore;

  // Also verify pages are still updated on skipped folders
  const fSiteAgain = folderById("PF_site");
  const pagesStillOk = !!(fSiteAgain && JSON.stringify(fSiteAgain.pages) === JSON.stringify([5,7,8]));

  out.idempotent = skippedAll && countsUnchanged && pagesStillOk;

  // -----------------------------------------------------------------------
  // identityPreserved: LAYERS and FOLDERS are the SAME array objects.
  // -----------------------------------------------------------------------
  reseed();
  const layersRef  = LAYERS;
  const foldersRef = FOLDERS;
  seedPageFolders(allPages, mockTags, mockFloors);
  seedPageFolders(allPages, mockTags, mockFloors); // second call
  out.identityPreserved = (LAYERS === layersRef) && (FOLDERS === foldersRef);

  // -----------------------------------------------------------------------
  // pageFolderOfLayer: returns correct PF ancestor folder.
  // -----------------------------------------------------------------------
  // (state already has PF folders from above; grab a floor_2 layer)
  const floor2Layers2 = layersOfPage(12, mockTags, mockFloors);
  const aFloor2Layer = floor2Layers2[0];
  let pfOfLayerOk = false;
  if (aFloor2Layer) {
    const pf = pageFolderOfLayer(aFloor2Layer.id);
    pfOfLayerOk = !!(pf && pf.id === "PF_floor_2");
  }

  // A default seed layer (root, no folder parent) should return null
  const defaultLayer = layerById("gfa"); // default seed layer
  const pfOfDefault = pageFolderOfLayer(defaultLayer.id);
  const pfOfDefaultNull = pfOfDefault === null;

  out.pageFolderOfLayer = pfOfLayerOk && pfOfDefaultNull;

  // -----------------------------------------------------------------------
  // layersOfPage: returns 3 layers for a floor page, all under PF_floor_2.
  // -----------------------------------------------------------------------
  const page12Layers = layersOfPage(12, mockTags, mockFloors);
  const page12Ok = page12Layers.length === 3 &&
    page12Layers.every(function(l) {
      var pf = pageFolderOfLayer(l.id);
      return pf && pf.id === "PF_floor_2";
    });
  out.layersOfPage = page12Ok;

  // -----------------------------------------------------------------------
  // isPageFolder: true for PF folders, false for user-created folders.
  // -----------------------------------------------------------------------
  const pfSite = folderById("PF_site");
  const isPFSite = isPageFolder("PF_site") && isPageFolder(pfSite);

  const userFolder = addFolder("user", null, null);
  const isNotPFUser = !isPageFolder(userFolder.id) && !isPageFolder(userFolder);

  out.isPageFolder = isPFSite && isNotPFUser;

  // -----------------------------------------------------------------------
  // resetClean: after resetPageFolders(), no PF folders, no PF-parented
  //   layers remain; default 6 layers still present.
  // -----------------------------------------------------------------------
  reseed();
  seedPageFolders(allPages, mockTags, mockFloors);
  resetPageFolders();

  const noPFFolders  = FOLDERS.every(function(f){ return f.kind !== "page-folder"; });
  const noPFLayers   = LAYERS.every(function(l){
    return !(l.parentId && typeof l.parentId === "string" && l.parentId.indexOf("PF_") === 0);
  });
  const defaultLayersIntact = layersInOrder().length === 6;

  out.resetClean = noPFFolders && noPFLayers && defaultLayersIntact;

  // -----------------------------------------------------------------------
  // noRoleTagMutation: base layer .tag === roleSemanticTag(.role)
  // -----------------------------------------------------------------------
  reseed();
  seedPageFolders(allPages, mockTags, mockFloors);
  const pfSite2 = folderById("PF_site");
  const siteLayers2 = layersOfPage(5, mockTags, mockFloors);
  const tagMatchOk = siteLayers2.every(function(l){
    return l.tag === roleSemanticTag(l.role);
  });
  const floor2Layers3 = layersOfPage(12, mockTags, mockFloors);
  const floor2TagOk = floor2Layers3.every(function(l){
    return l.tag === roleSemanticTag(l.role);
  });
  out.noRoleTagMutation = tagMatchOk && floor2TagOk;

  // -----------------------------------------------------------------------
  // semanticTagDecoupled: renaming a base layer does NOT change .tag
  // -----------------------------------------------------------------------
  const fl2Layers = layersOfPage(12, mockTags, mockFloors);
  const gfaLayer = fl2Layers.find(function(l){ return l.role === "gfa"; });
  let tagDecoupledOk = false;
  if (gfaLayer) {
    const tagBefore = gfaLayer.tag;
    renameLayer(gfaLayer.id, "FOOBAR");
    const tagAfter = gfaLayer.tag;
    tagDecoupledOk = (tagAfter === tagBefore) && (tagAfter === roleSemanticTag("gfa")) && (gfaLayer.name === "FOOBAR");
  }
  out.semanticTagDecoupled = tagDecoupledOk;

  // Restore clean state
  reseed();

  return out;
}
"""

CHECKS = [
    "idFor",
    "seedCreatesFolders",
    "seedCreatesBaseLayers",
    "baseLayerNames",
    "idempotent",
    "identityPreserved",
    "pageFolderOfLayer",
    "layersOfPage",
    "isPageFolder",
    "resetClean",
    "noRoleTagMutation",
    "semanticTagDecoupled",
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
    print("LITE-PAGE-FOLDER-MODEL checks:")
    for k in CHECKS:
        ok = result.get(k)
        print(f"  {k:30s} -> {ok}")
        if ok is not True:
            failures.append(f"check '{k}' = {ok!r} (expected True)")

    if failures:
        for f in failures:
            print("FAIL:", f)
        print("LITE_PAGE_FOLDER_MODEL_FAIL")
        sys.exit(1)
    else:
        print("LITE_PAGE_FOLDER_MODEL_OK")


if __name__ == "__main__":
    main()
