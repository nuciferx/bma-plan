"""
BUG-20260526-stale-pf-cleanup: regression guard for PF folder pruning.

Verifies that seedPageFolders() correctly prunes PF folders that disappear
from the current folderPageMap, with safety guards for user-drawn objects.

4 cases:
  Case A - basic cleanup      re-tag p2 excluded → PF_floor_1 pruned
  Case B - safety preservation user-drawn object on PF_floor_1 → NOT pruned
  Case C - idempotency         5x seed with same tags → stable state
  Case D - PF_excluded never pruned  even if not in activeFids

Emits PF_CLEANUP_OK on success.

    py -3 lite/tests/test_pf_cleanup_on_exclude.py
"""
import socket, threading, time, sys
from pathlib import Path

LITE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LITE))
import uvicorn
from playwright.sync_api import sync_playwright


def _free_port(start=8660):
    for p in range(start, start + 60):
        with socket.socket() as s:
            if s.connect_ex(("127.0.0.1", p)) != 0:
                return p
    raise RuntimeError("no free port")


SCENARIO = r"""
() => {
  const results = {};

  // Helper: reset LAYERS + FOLDERS in-place, then re-init defaults.
  function reseed() {
    LAYERS.length  = 0;
    FOLDERS.length = 0;
    initLayers();
  }

  // -------------------------------------------------------------------------
  // Case A — basic cleanup
  //   1. seed p1=basement/1, p2=floor/1, p3=floor/2
  //   2. verify PF_basement_1, PF_floor_1, PF_floor_2 exist
  //   3. re-tag p2 as excluded → seedPageFolders again
  //   4. assert PF_floor_1 is gone, its layers are gone, PF_excluded has p2
  // -------------------------------------------------------------------------
  {
    reseed();
    const tags1  = {1:"floor", 2:"floor", 3:"floor"};
    const nums1  = {1:1, 2:1, 3:2};
    const kinds1 = {1:"basement", 2:"normal", 3:"normal"};
    seedPageFolders([1,2,3], tags1, nums1, kinds1);

    const afterFirst = !!(folderById("PF_basement_1") && folderById("PF_floor_1") && folderById("PF_floor_2"));

    // Re-tag p2 as excluded
    const tags2  = {1:"floor", 3:"floor"};
    const nums2  = {1:1, 3:2};
    const kinds2 = {1:"basement", 3:"normal"};
    const r2 = seedPageFolders([1,2,3], tags2, nums2, kinds2);

    const floorGone   = folderById("PF_floor_1") === null;
    const layersGone  = LAYERS.filter(function(l){ return l.parentId === "PF_floor_1"; }).length === 0;
    const excl        = folderById("PF_excluded");
    const exclHasP2   = !!(excl && excl.pages && excl.pages.indexOf(2) !== -1);
    const prunedCount = typeof r2.pruned === "number" && r2.pruned >= 1;

    const ok = afterFirst && floorGone && layersGone && exclHasP2 && prunedCount;
    results.caseA = ok;
    if (!ok) results.caseA_detail = {afterFirst, floorGone, layersGone, exclHasP2, prunedCount: r2.pruned};
  }

  // -------------------------------------------------------------------------
  // Case B — safety preservation
  //   Same as A but BEFORE re-tag: push a user-drawn object on the GFA ชั้น 1 layer.
  //   PF_floor_1 must NOT be pruned.
  // -------------------------------------------------------------------------
  {
    reseed();
    const tags1  = {1:"floor", 2:"floor", 3:"floor"};
    const nums1  = {1:1, 2:1, 3:2};
    const kinds1 = {1:"basement", 2:"normal", 3:"normal"};
    seedPageFolders([1,2,3], tags1, nums1, kinds1);

    // Find the GFA layer inside PF_floor_1
    const floor1Children = childrenOf("PF_floor_1");
    const gfaLayer = floor1Children
      .filter(function(c){ return c.kind === "layer"; })
      .map(function(c){ return c.node; })
      .find(function(l){ return l.role === "gfa"; });

    const gfaLayerId = gfaLayer ? gfaLayer.id : null;

    // Simulate a user-drawn object on that layer in PS[2]
    if (gfaLayerId) {
      if (!PS[2]) PS[2] = {objects: []};
      if (!PS[2].objects) PS[2].objects = [];
      PS[2].objects.push({id: 9901, catId: gfaLayerId, pts: [[0,0],[1,0],[1,1]], kind: "poly"});
    }

    // Re-tag p2 as excluded
    const tags2  = {1:"floor", 3:"floor"};
    const nums2  = {1:1, 3:2};
    const kinds2 = {1:"basement", 3:"normal"};
    seedPageFolders([1,2,3], tags2, nums2, kinds2);

    const folderStillExists = folderById("PF_floor_1") !== null;
    const layersIntact = LAYERS.filter(function(l){ return l.parentId === "PF_floor_1"; }).length > 0;

    // Clean up the fake object before next case
    if (PS[2] && PS[2].objects) {
      PS[2].objects = PS[2].objects.filter(function(o){ return o.id !== 9901; });
    }

    const ok = !!(gfaLayerId && folderStillExists && layersIntact);
    results.caseB = ok;
    if (!ok) results.caseB_detail = {gfaLayerId, folderStillExists, layersIntact};
  }

  // -------------------------------------------------------------------------
  // Case C — idempotency
  //   Same tags as Case A initial setup. Call seedPageFolders 5 times.
  //   Snapshot after run 1 and run 5 must be identical (same folder ids,
  //   same pages arrays, same folder count).
  // -------------------------------------------------------------------------
  {
    reseed();
    const tags1  = {1:"floor", 2:"floor", 3:"floor"};
    const nums1  = {1:1, 2:1, 3:2};
    const kinds1 = {1:"basement", 2:"normal", 3:"normal"};

    function snapshot() {
      return JSON.stringify(
        FOLDERS
          .filter(function(f){ return f && f.kind === "page-folder"; })
          .map(function(f){ return {id: f.id, pages: (f.pages || []).slice().sort(function(a,b){return a-b;})}; })
          .sort(function(a,b){ return a.id < b.id ? -1 : a.id > b.id ? 1 : 0; })
      );
    }

    seedPageFolders([1,2,3], tags1, nums1, kinds1);
    const snap1 = snapshot();

    for (var _i = 0; _i < 4; _i++) {
      seedPageFolders([1,2,3], tags1, nums1, kinds1);
    }
    const snap5 = snapshot();

    const ok = snap1 === snap5;
    results.caseC = ok;
    if (!ok) results.caseC_detail = {snap1, snap5};
  }

  // -------------------------------------------------------------------------
  // Case D — PF_excluded never pruned
  //   Tag all 3 pages as 'site' → folderPageMap = {PF_site:[1,2,3]}, no PF_excluded key.
  //   Manually inject a PF_excluded folder into FOLDERS THEN call seedPageFolders again.
  //   PF_excluded must still exist.
  // -------------------------------------------------------------------------
  {
    reseed();
    const tagsSite = {1:"site", 2:"site", 3:"site"};
    seedPageFolders([1,2,3], tagsSite, {}, {});

    // Manually add PF_excluded (simulates a prior run that created it)
    addFolder("อื่น ๆ", null, null);
    // Override the last folder's id and kind to make it PF_excluded
    var lastF = FOLDERS[FOLDERS.length - 1];
    if (lastF) { lastF.id = "PF_excluded"; lastF.kind = "page-folder"; lastF.pages = []; }

    // Now seedPageFolders again — activeFids = ["PF_site"] only, no PF_excluded
    seedPageFolders([1,2,3], tagsSite, {}, {});

    const exclStillExists = folderById("PF_excluded") !== null;
    results.caseD = exclStillExists;
    if (!exclStillExists) results.caseD_detail = "PF_excluded was pruned";
  }

  return results;
}
"""


def main():
    from server_lite import app as lite_app
    port = _free_port()
    cfg = uvicorn.Config(lite_app, host="127.0.0.1", port=port, log_level="error")
    server = uvicorn.Server(cfg)
    threading.Thread(target=server.run, daemon=True).start()
    time.sleep(2.0)

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

    cases = [
        ("A", "basic cleanup"),
        ("B", "safety preservation"),
        ("C", "idempotency"),
        ("D", "PF_excluded never pruned"),
    ]

    all_pass = True
    for key, desc in cases:
        ckey = "case" + key
        ok = result.get(ckey)
        detail = result.get(ckey + "_detail", "")
        if ok is True:
            print(f"[CASE_{key}] PASS  ({desc})")
        else:
            print(f"[CASE_{key}] FAIL: {desc} — detail={detail}")
            all_pass = False

    print()
    if all_pass:
        print("PF_CLEANUP_OK")
        sys.exit(0)
    else:
        print("PF_CLEANUP_FAIL")
        sys.exit(1)


if __name__ == "__main__":
    main()
