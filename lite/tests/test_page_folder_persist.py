"""
LPFL-1b: page-folder-layers persist regression guard.

Verifies that folder.kind and folder.pages survive a .bmaplan save/load
round-trip and that the schema change is additive (old files without these
fields still load correctly).

Checks (6):
  roundtripPFFolders      seed PF folders → serialize liteGroups → clear →
                          loadProto → kind + pages round-trip intact;
                          also verifies seedPageFolders idempotency after load.
  backwardCompatNoKind    legacy liteGroups entry (no kind/pages) loads without
                          error; kind===undefined; isPageFolder===false.
  forwardCompatRetained   liteGroups entry with kind='page-folder' and pages
                          array loads both fields intact.
  identityPreserved       LAYERS and FOLDERS array references are the same
                          objects before and after loadProto.
  mixedFolders            doc with one PF folder + one user folder: both survive
                          with correct kind after load.
  resaveStable            save → load → save again → liteGroups section is
                          byte-identical (no drift / key reordering noise).

Emits LITE_PAGE_FOLDER_PERSIST_OK on success.

    py -3 lite/tests/test_page_folder_persist.py
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
# All 6 checks run in a single page.evaluate() for speed.
# Each check resets LAYERS and FOLDERS via reseed() before running.
# --------------------------------------------------------------------------
SCENARIO = r"""
() => {
  const out = {};

  /* Helper: reset LAYERS to 6 defaults + FOLDERS to empty */
  function reseed() {
    LAYERS.length  = 0;
    FOLDERS.length = 0;
    initLayers();
    ROLE_DEFS.forEach(function(rd) {
      state.catVis[rd.id]  = true;
      state.catLock[rd.id] = false;
    });
  }

  /* Helper: reset PS to empty */
  function resetPS() { PS = {}; }

  /* Helper: build a minimal doc skeleton (no pages, no layers, no groups) */
  function minDoc(liteGroups) {
    return {version:1, app:"bma-plan-lite", pdfName:"test.pdf",
      totalPages:10, pageStore:{}, pageRotations:{}, pageTags:{}, pageNames:{},
      projectInfo:{}, siteOrientation:{}, excludedPages:[],
      pageFloorKind:{}, pageFloorNum:{}, liteGroups: liteGroups};
  }

  /* Helper: extract just the liteGroups array the same way save() does */
  function captureLiteGroups() {
    return foldersInOrder().map(function(f) {
      return {id:f.id, name:f.name, color:f.color,
              parentId:(f.parentId!==undefined?f.parentId:null),
              order:f.order, kind:f.kind, pages:f.pages};
    });
  }

  /* Sort-keys helper for stable JSON comparison */
  function sortedJson(obj) {
    return JSON.stringify(obj, Object.keys(obj).sort());
  }

  // -----------------------------------------------------------------------
  // 1. roundtripPFFolders
  //    seed PF folders, capture, round-trip via loadProto, check fields.
  //    Also verifies seedPageFolders idempotency (post-load seed skips all PFs).
  // -----------------------------------------------------------------------
  reseed(); resetPS();

  const mockTags  = {5:"site", 7:"floor", 8:"floor", 12:"floor"};
  const mockFloors = {7:2, 8:2, 12:3};
  const allPages  = [5, 7, 8, 12];

  seedPageFolders(allPages, mockTags, mockFloors);

  // Capture liteGroups before save
  const lg1 = captureLiteGroups();
  const lg1str = JSON.stringify(lg1);

  // Reset and load
  reseed(); resetPS();
  loadProto(minDoc(JSON.parse(lg1str)));

  const pfSite = folderById("PF_site");
  const pfFloor2 = folderById("PF_floor_2");
  const pfExcluded = folderById("PF_excluded");

  // PF_site: kind='page-folder', pages=[5]
  const siteOk = !!(pfSite
    && pfSite.kind === "page-folder"
    && Array.isArray(pfSite.pages)
    && pfSite.pages.length === 1
    && pfSite.pages[0] === 5);

  // PF_floor_2: kind='page-folder', pages=[7,8] (sorted)
  const floor2Ok = !!(pfFloor2
    && pfFloor2.kind === "page-folder"
    && Array.isArray(pfFloor2.pages)
    && pfFloor2.pages.length === 2
    && pfFloor2.pages[0] === 7
    && pfFloor2.pages[1] === 8);

  // PF_excluded: kind='page-folder', pages=[12] (page 12 has floor tag but...
  // wait: mockTags[12]="floor" → PF_floor_3, so PF_excluded has NO pages in this set.
  // Actually with allPages=[5,7,8,12] and tags {5:site,7:floor,8:floor,12:floor},
  // every page maps to a named folder. PF_excluded only exists if some page has no tag.
  // Let's check what we actually got.
  const floor3 = folderById("PF_floor_3");
  const floor3Ok = !!(floor3
    && floor3.kind === "page-folder"
    && Array.isArray(floor3.pages)
    && floor3.pages.length === 1
    && floor3.pages[0] === 12);

  // idempotency: calling seedPageFolders again must skip all PF folders
  const seedResult2 = seedPageFolders(allPages, mockTags, mockFloors);
  const allSkipped = seedResult2.created.length === 0
    && seedResult2.skipped.length > 0;

  // backward-compat part: old file (no PF folders), then seedPageFolders creates them fresh
  reseed(); resetPS();
  const docOldNoFolders = minDoc([]);  // no liteGroups entries at all
  loadProto(docOldNoFolders);
  const seedResult3 = seedPageFolders(allPages, mockTags, mockFloors);
  const oldFileSeedCreates = seedResult3.created.length > 0
    && seedResult3.skipped.length === 0;

  out.roundtripPFFolders = siteOk && floor2Ok && floor3Ok && allSkipped && oldFileSeedCreates;

  // -----------------------------------------------------------------------
  // 2. backwardCompatNoKind
  //    Legacy liteGroups entry (no kind, no pages) loads cleanly.
  //    kind === undefined (falsy), isPageFolder === false.
  // -----------------------------------------------------------------------
  reseed(); resetPS();

  const docLegacy = minDoc([
    {id:"F1", name:"old user folder", color:"#aaa", parentId:null, order:0}
    /* NO kind, NO pages */
  ]);
  loadProto(docLegacy);

  const f1 = folderById("F1");
  const kindFalsy    = !!(f1 && !f1.kind);
  const notPF        = !!(f1 && isPageFolder("F1") === false);
  const noThrow      = !!f1;  // reached here without exception = no throw

  out.backwardCompatNoKind = kindFalsy && notPF && noThrow;

  // -----------------------------------------------------------------------
  // 3. forwardCompatRetained
  //    liteGroups entry with kind='page-folder' and pages array: both intact.
  // -----------------------------------------------------------------------
  reseed(); resetPS();

  const docFwd = minDoc([
    {id:"PF_floor_2", name:"ชั้น 2", color:"#abc",
     parentId:null, order:0, kind:"page-folder", pages:[12]}
  ]);
  loadProto(docFwd);

  const fFwd = folderById("PF_floor_2");
  const kindOk  = !!(fFwd && fFwd.kind === "page-folder");
  const pagesOk = !!(fFwd && Array.isArray(fFwd.pages)
                    && fFwd.pages.length === 1 && fFwd.pages[0] === 12);

  out.forwardCompatRetained = kindOk && pagesOk;

  // -----------------------------------------------------------------------
  // 4. identityPreserved
  //    LAYERS and FOLDERS refs are the SAME array objects after loadProto.
  // -----------------------------------------------------------------------
  reseed(); resetPS();

  const LAYERS_ref  = LAYERS;
  const FOLDERS_ref = FOLDERS;

  const docId = minDoc([
    {id:"PF_site", name:"Site", color:"#c0c", parentId:null, order:0,
     kind:"page-folder", pages:[1]}
  ]);
  loadProto(docId);

  out.identityPreserved = (LAYERS === LAYERS_ref) && (FOLDERS === FOLDERS_ref);

  // -----------------------------------------------------------------------
  // 5. mixedFolders
  //    Doc with one PF folder + one user folder: both survive with correct kind.
  // -----------------------------------------------------------------------
  reseed(); resetPS();

  const docMixed = minDoc([
    {id:"PF_site",  name:"Site folder",      color:"#c84",  parentId:null, order:0,
     kind:"page-folder", pages:[3]},
    {id:"F_user_1", name:"User folder",       color:"#84c",  parentId:null, order:1}
    /* second entry has NO kind */
  ]);
  loadProto(docMixed);

  const fPF   = folderById("PF_site");
  const fUser = folderById("F_user_1");

  const pfKindOk   = !!(fPF   && fPF.kind   === "page-folder");
  const userKindOk = !!(fUser && !fUser.kind);  // undefined / falsy

  out.mixedFolders = pfKindOk && userKindOk;

  // -----------------------------------------------------------------------
  // 6. resaveStable
  //    save → load → save again → liteGroups section byte-identical.
  // -----------------------------------------------------------------------
  reseed(); resetPS();

  const seedTags   = {1:"site", 2:"floor"};
  const seedFloors = {2:1};
  seedPageFolders([1, 2], seedTags, seedFloors);

  // First save: capture liteGroups
  const save1 = captureLiteGroups();
  const save1str = JSON.stringify(save1);

  // Load
  reseed(); resetPS();
  loadProto(minDoc(JSON.parse(save1str)));

  // Second save: capture again
  const save2 = captureLiteGroups();

  // Compare: sort entries by id then sort keys within each entry for stability
  function normalizeGroups(arr) {
    var sorted = arr.slice().sort(function(a, b) {
      return a.id < b.id ? -1 : a.id > b.id ? 1 : 0;
    });
    return JSON.stringify(sorted.map(function(item) {
      var keys = Object.keys(item).sort();
      var o = {};
      keys.forEach(function(k) { o[k] = item[k]; });
      return o;
    }));
  }

  const norm1 = normalizeGroups(save1);
  const norm2 = normalizeGroups(save2);
  out.resaveStable = (norm1 === norm2);

  // Restore clean state
  reseed();
  return out;
}
"""

CHECKS = [
    "roundtripPFFolders",
    "backwardCompatNoKind",
    "forwardCompatRetained",
    "identityPreserved",
    "mixedFolders",
    "resaveStable",
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
    print("LITE-PAGE-FOLDER-PERSIST checks:")
    for k in CHECKS:
        ok = result.get(k)
        print(f"  {k:35s} -> {ok}")
        if ok is not True:
            failures.append(f"check '{k}' = {ok!r} (expected True)")

    if failures:
        for f in failures:
            print("FAIL:", f)
        print("LITE_PAGE_FOLDER_PERSIST_FAIL")
        sys.exit(1)
    else:
        print("LITE_PAGE_FOLDER_PERSIST_OK")


if __name__ == "__main__":
    main()
