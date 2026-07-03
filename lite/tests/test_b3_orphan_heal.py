"""
INV-20260703-layer-linkage -- sprint B3 acceptance test.

Verifies the H3 "orphaned catId" fix:
  (a) removeLayer(id) now reassigns every PS-object/CFSS-master catId ===
      id to the role's default layer BEFORE splicing (previously the
      caller's responsibility; layer-tree.js's own tree-delete reassign
      still runs too but is now redundant, not load-bearing).
  (b) page-folder-layers.js's _pflPrunePF (via removeLayer, now fixed for
      free) and resetPageFolders() (no removeLayer at all -- fixed
      directly) no longer orphan objects when PF-scoped layers are pruned.
  (c) loadProto()'s new sweepOrphanCatIds() call heals any catId that does
      not resolve to a loaded layer (legacy `doc.pages` format never
      validated catId at all -- the realistic vector for a pre-existing
      orphan showing up in a save file).
  (d) crash guards: draw()/buildExportData()/openSum() must not throw even
      when an orphaned catId briefly exists.

Checks:
  removeLayerReassigns   removeLayer(customId) on a layer with objects on
                          2 pages -> every object's catId becomes the role
                          default; ObjectAgg.byRole()[role].area unchanged
                          before/after (tuple total preserved under the
                          role bucket); draw() does not throw;
                          assertEnginesAgree().ok stays true.
  legacyLoadHeals         loadProto() on a legacy `doc.pages`-format doc
                          whose only object has catId:'Lgone' (nowhere in
                          LAYERS) -> after load the object's catId no
                          longer equals 'Lgone', resolves to a real layer,
                          and equals SEM_REV[semanticTag] ('gfa' for
                          gross_floor_area); draw()/buildExportData()/
                          openSum() all run without throwing.
  resetPageFoldersHeals   a PF_-parented custom layer with a live object ->
                          resetPageFolders() removes the folder+layer BUT
                          the object's catId now resolves to a real layer
                          (not orphaned) -- pins the fix for the
                          no-guard prune hole (H3b). (_pflPrunePF's OWN
                          prune hole is guarded by a pre-existing
                          _pflFolderHasUserDrawnObjects() safety check that
                          refuses to prune folders with live objects at
                          all -- verified intact here too -- so
                          resetPageFolders(), which has no such guard, is
                          the reachable path for this regression pin.)
  oracleStillOk           ObjectAgg.assertEnginesAgree() stays ok:true
                          after every heal above.

Emits LITE_B3_ORPHAN_HEAL_OK on success.

    py -3 lite/tests/test_b3_orphan_heal.py
"""
import socket, threading, time, sys
from pathlib import Path

LITE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LITE))
import uvicorn
from playwright.sync_api import sync_playwright


def _free_port(start=9130):
    for p in range(start, start + 60):
        with socket.socket() as s:
            if s.connect_ex(("127.0.0.1", p)) != 0:
                return p
    raise RuntimeError("no free port")


SCENARIO = r"""
() => {
  const out = {};
  const dummy = document.createElement('canvas'); dummy.width = 400; dummy.height = 400;

  function reseed() {
    LAYERS.length = 0; FOLDERS.length = 0; initLayers();
    ROLE_DEFS.forEach(function(rd) { state.catVis[rd.id] = true; state.catLock[rd.id] = false; });
  }
  function resetPS() {
    for (var k in PS) delete PS[k];
    for (var k in excluded) delete excluded[k];
    for (var k in pageTags) delete pageTags[k];
    for (var k in pageFloorNum) delete pageFloorNum[k];
    for (var k in pageFloorKind) delete pageFloorKind[k];
    if (window.MASTERS) window.MASTERS = {};
  }
  function rect(w, h, ox, oy) { ox = ox || 0; oy = oy || 0; return [{x:ox,y:oy},{x:ox+w,y:oy},{x:ox+w,y:oy+h},{x:ox,y:oy+h}]; }
  function noThrow(fn) { try { fn(); return true; } catch (e) { return String((e && e.message) || e); } }

  const savedCaseId = (typeof caseId !== 'undefined') ? caseId : undefined;
  window.curImg = dummy;

  // -----------------------------------------------------------------------
  // removeLayerReassigns
  // -----------------------------------------------------------------------
  {
    reseed(); resetPS();
    pageCount = 2; curPage = 1;
    PS[1] = {objects: [], scale: {pts_per_m: 1}, annotations: []};
    PS[2] = {objects: [], scale: {pts_per_m: 1}, annotations: []};

    const custom = addLayer('gfa', 'Temp GFA', '#123456');
    PS[1].objects.push({id: 101, kind: 'poly', pts: rect(10, 10), catId: custom.id, counting: false, semanticTag: 'gross_floor_area'});
    PS[2].objects.push({id: 102, kind: 'poly', pts: rect(5, 4),   catId: custom.id, counting: false, semanticTag: 'gross_floor_area'});

    const byRoleBefore = window.ObjectAgg.byRole();
    const gfaBefore = (byRoleBefore.gfa && byRoleBefore.gfa.area) || 0;

    const res = removeLayer(custom.id);

    const obj1Ok = PS[1].objects[0].catId === 'gfa';
    const obj2Ok = PS[2].objects[0].catId === 'gfa';
    const goneFromLayers = layerById(custom.id) === null;

    const byRoleAfter = window.ObjectAgg.byRole();
    const gfaAfter = (byRoleAfter.gfa && byRoleAfter.gfa.area) || 0;
    const totalPreserved = Math.abs(gfaBefore - gfaAfter) < 1e-6;

    const drawResult = noThrow(draw);
    const oracle1 = window.ObjectAgg.assertEnginesAgree();

    out.removeLayerReassigns = !!(
      res.removed === true && res.reassignTo === 'gfa' &&
      obj1Ok && obj2Ok && goneFromLayers && totalPreserved &&
      drawResult === true && oracle1.ok
    );
    out._removeLayerDetail = {res, obj1Ok, obj2Ok, goneFromLayers, gfaBefore, gfaAfter, drawResult, oracleDiffs: oracle1.diffs};
  }

  // -----------------------------------------------------------------------
  // legacyLoadHeals -- legacy `doc.pages` format never validated catId at
  // all (unlike the pageStore branch, which resolves via liteCatId/SEM_REV
  // at construction time) -- the realistic vector for a stale/orphaned
  // catId surviving into a loaded session.
  // -----------------------------------------------------------------------
  {
    reseed(); resetPS();
    caseId = 'test-mock-b3';
    curPage = 1; pageCount = 1;

    const docLegacy = {
      version: 1, app: 'bma-plan-lite', pdfName: 'test.pdf', totalPages: 1,
      pages: {
        1: {
          scale: {pts_per_m: 1},
          objects: [{id: 1, catId: 'Lgone', kind: 'poly', counting: false,
                     semanticTag: 'gross_floor_area', pts: rect(20, 15), dimVisible: true}],
          annotations: []
        }
      },
      pageRotations: {}, pageTags: {}, pageNames: {}, projectInfo: {}, siteOrientation: {},
      excludedPages: [], pageFloorKind: {}, pageFloorNum: {}
      /* NO liteLayers field -- defaults reseed to 6; NO liteCatId on the object */
    };

    loadProto(JSON.parse(JSON.stringify(docLegacy)));

    const obj = PS['1'] && PS['1'].objects && PS['1'].objects[0];
    const noLongerLgone = !!(obj && obj.catId !== 'Lgone');
    const resolvesToRealLayer = !!(obj && layerById(obj.catId));
    const matchesSemRev = !!(obj && obj.catId === (SEM_REV['gross_floor_area'] || 'use'));

    const drawResult = noThrow(draw);
    const exportResult = noThrow(function() { return buildExportData(); });
    const sumResult = noThrow(openSum);
    if (document.getElementById('sum')) document.getElementById('sum').classList.remove('show');

    out.legacyLoadHeals = !!(noLongerLgone && resolvesToRealLayer && matchesSemRev &&
      drawResult === true && exportResult === true && sumResult === true);
    out._legacyDetail = {noLongerLgone, resolvesToRealLayer, matchesSemRev, catId: obj && obj.catId, drawResult, exportResult, sumResult};
  }

  // -----------------------------------------------------------------------
  // resetPageFoldersHeals -- PF_-parented custom layer with a live object;
  // resetPageFolders() has no _pflFolderHasUserDrawnObjects guard (unlike
  // _pflPrunePF), so it is the reachable path for the "prune hole" (H3b).
  // -----------------------------------------------------------------------
  {
    reseed(); resetPS();
    pageCount = 1; curPage = 1;
    PS[1] = {objects: [], scale: {pts_per_m: 1}, annotations: []};
    pageTags[1] = 'floor'; pageFloorKind[1] = 'normal'; pageFloorNum[1] = 1;
    state.pageFolderMode = true;
    seedPageFolders([1], pageTags, pageFloorNum, pageFloorKind);

    let f1Gfa = null;
    LAYERS.forEach(function(l) { if (l.parentId === 'PF_floor_1' && l.role === 'gfa') f1Gfa = l; });
    const f1GfaId = f1Gfa ? f1Gfa.id : null;

    PS[1].objects.push({id: 201, kind: 'poly', pts: rect(6, 6), catId: f1GfaId, counting: false, semanticTag: 'gross_floor_area'});

    // Confirm the pre-existing safety guard still blocks _pflPrunePF from
    // orphaning THIS folder while the object is live (unaffected baseline).
    const prunedWhileLive = _pflPrunePF([]);   // activeFolderIds=[] -> nothing active
    const guardStillBlocks = layerById(f1GfaId) !== null && PS[1].objects[0].catId === f1GfaId;

    // Now exercise the real no-guard hole: resetPageFolders() unconditionally
    // wipes PF-parented layers regardless of live objects.
    resetPageFolders();

    const layerGone = layerById(f1GfaId) === null;
    const objSurvivesResolvable = !!(PS[1].objects[0] && layerById(PS[1].objects[0].catId));
    const objNotOrphaned = PS[1].objects[0].catId !== f1GfaId;

    const drawResult = noThrow(draw);
    const oracle2 = window.ObjectAgg.assertEnginesAgree();

    out.resetPageFoldersHeals = !!(
      f1GfaId && guardStillBlocks && layerGone && objSurvivesResolvable && objNotOrphaned &&
      drawResult === true && oracle2.ok
    );
    out._resetDetail = {f1GfaId, prunedWhileLive, guardStillBlocks, layerGone, objSurvivesResolvable,
      objNotOrphaned, finalCatId: PS[1].objects[0] && PS[1].objects[0].catId, drawResult, oracleDiffs: oracle2.diffs};
  }

  out.oracleStillOk = !!(out._removeLayerDetail && out._resetDetail &&
    window.ObjectAgg.assertEnginesAgree().ok);

  if (savedCaseId !== undefined) caseId = savedCaseId; else caseId = null;
  reseed(); resetPS();

  return out;
}
"""

CHECKS = [
    "removeLayerReassigns",
    "legacyLoadHeals",
    "resetPageFoldersHeals",
    "oracleStillOk",
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
    print("LITE-B3-ORPHAN-HEAL checks:")
    for k in CHECKS:
        ok = result.get(k)
        print(f"  {k:24s} -> {ok}")
        if ok is not True:
            failures.append(f"check '{k}' = {ok!r} (expected True)")

    for dk in ("_removeLayerDetail", "_legacyDetail", "_resetDetail"):
        if dk in result:
            print(f"  {dk}: {result[dk]}")

    if page_errors:
        failures.append(f"{len(page_errors)} page error(s) during scenario")

    if failures:
        for f in failures:
            print("FAIL:", f)
        print("LITE_B3_ORPHAN_HEAL_FAIL")
        sys.exit(1)
    else:
        print("LITE_B3_ORPHAN_HEAL_OK")


if __name__ == "__main__":
    main()
