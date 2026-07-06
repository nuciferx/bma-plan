"""
INV-2026-07-04-001 slice 1/3: context-scoped layer panel + floor-rail +
bidirectional PDF-page binding — regression guard.

Verifies: when PF mode is active (permanent, LFOC-1b) and scopeByPage is
active (default), the layer panel shows only the active page's PF_*
folder plus a floor-rail (◀ / <select> / ▶) above #catlist. Selecting a
different floor in the rail calls loadPage(folder.pages[0]); once curPage
changes, buildPicker() re-scopes (via the existing afterPage() call
chain — no second render path). Untagged/excluded pages fall back to an
unfiltered render + a "—" rail. PF-mode-OFF renders exactly as before
this slice (no rail, unfiltered).

Seeded scenario (kind-aware, mirrors LFOC-ORDER-A style):
  page 5 -> floor #1, kind=basement -> PF_basement_1  (order 95)
  page 6 -> floor #2, kind=normal   -> PF_floor_2      (order 120)
  page 7 -> floor roof, kind=rooftop-> PF_floor_roof   (order 9000)

5 checks:
  scopedRenderShowsOnlyActive   curPage=6 -> only PF_floor_2 rendered;
                                 PF_basement_1/PF_floor_roof absent;
                                 a user layer nested under PF_floor_2
                                 stays visible
  railListsKindAwareOrder       #ls-rail-jump options = [PF_basement_1,
                                 PF_floor_2, PF_floor_roof] in that order
  railSelectionIsBidirectional  selecting PF_floor_roof in the rail calls
                                 loadPage(7); curPage becomes 7; catlist
                                 now shows PF_floor_roof only (proves
                                 both directions of the binding)
  untaggedPageFallsBack         curPage on an untracked page number ->
                                 lsFolderForPage returns null -> full
                                 unfiltered render (all 3 folders show)
                                 + rail shows "—"
  pfModeOffNoRail               state.pageFolderMode = false -> #ls-rail
                                 hidden, catlist renders unfiltered
                                 (same as before this slice)

Emits LITE_LAYER_SCOPE_OK on success.

    py -3 lite/tests/test_layer_scope.py
"""
import socket, threading, time, sys
from pathlib import Path

LITE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LITE))
import uvicorn
from playwright.sync_api import sync_playwright


def _free_port(start=8440):
    for p in range(start, start + 60):
        with socket.socket() as s:
            if s.connect_ex(("127.0.0.1", p)) != 0:
                return p
    raise RuntimeError("no free port")


# ---------------------------------------------------------------------------
# Shared seed script — 3 kind-distinct floors, run at the top of each check
# so every check starts from a clean, identical model.
# ---------------------------------------------------------------------------
SEED = r"""
  LAYERS.length = 0;
  FOLDERS.length = 0;
  initLayers();
  ROLE_DEFS.forEach(function(rd) {
    state.catVis[rd.id] = true;
    state.catLock[rd.id] = false;
  });
  if (!state.folderCollapsed) state.folderCollapsed = {};

  pageTags     = {5: 'floor', 6: 'floor', 7: 'floor'};
  pageFloorNum = {5: 1, 6: 2, 7: 'roof'};
  pageFloorKind = {5: 'basement', 6: 'normal', 7: 'rooftop'};
  PS = {
    '5': {objects: [], scale: null, annotations: []},
    '6': {objects: [], scale: null, annotations: []},
    '7': {objects: [], scale: null, annotations: []}
  };
  pageCount = 7;

  state.pageFolderMode = true;
  state.scopeByPage = true;  // explicit — default is also true when undefined
  reseedActivePageFolders();
"""

# ---------------------------------------------------------------------------
# Check 1 — scopedRenderShowsOnlyActive
# ---------------------------------------------------------------------------
CHECK_SCOPED_RENDER = SEED + r"""
  curPage = 6; // PF_floor_2

  // nested user layer under the active folder — must stay visible
  var userLayer = addLayer('gfa', 'ScopeTestUserLayer', '#4c8dff');
  userLayer.parentId = 'PF_floor_2';
  state.catVis[userLayer.id] = true;
  state.catLock[userLayer.id] = false;

  buildPicker();
""" + r"""
  return (function() {
    var activeShown   = !!document.querySelector('[data-catid="PF_floor_2"]');
    var basementHidden = !document.querySelector('[data-catid="PF_basement_1"]');
    var roofHidden      = !document.querySelector('[data-catid="PF_floor_roof"]');
    var userLayerShown  = !!document.querySelector('[data-catid="' + userLayer.id + '"]');
    return {
      activeShown: activeShown,
      basementHidden: basementHidden,
      roofHidden: roofHidden,
      userLayerShown: userLayerShown,
      allOk: activeShown && basementHidden && roofHidden && userLayerShown
    };
  })();
"""

# ---------------------------------------------------------------------------
# Check 2 — railListsKindAwareOrder
# ---------------------------------------------------------------------------
CHECK_RAIL_ORDER = SEED + r"""
  curPage = 6;
  buildPicker();
""" + r"""
  return (function() {
    var sel = document.getElementById('ls-rail-jump');
    if (!sel) return {no_select: true, allOk: false};
    var ids = Array.prototype.map.call(sel.options, function(o) { return o.value; });
    var expected = ['PF_basement_1', 'PF_floor_2', 'PF_floor_roof'];
    var matches = JSON.stringify(ids) === JSON.stringify(expected);
    return {ids: ids, expected: expected, matches: matches, allOk: matches};
  })();
"""

# ---------------------------------------------------------------------------
# Check 3 — railSelectionIsBidirectional
# loadPage is stubbed to observe the call (no real PDF is loaded in this
# harness — same constraint every page-folder-layers test works under) but
# still performs the real side effects loadPage() would perform before any
# network/PDF.js work: curPage assignment + afterPage(). afterPage() and
# buildPicker() themselves are NOT stubbed, so the "panel follows the page"
# half of the proof is fully genuine.
# ---------------------------------------------------------------------------
CHECK_BIDIRECTIONAL = SEED + r"""
  curPage = 6;
  buildPicker();

  window._origLoadPage = loadPage;
  var calledWith = null;
  loadPage = function(n) {
    calledWith = n;
    curPage = n;
    afterPage();
    return Promise.resolve();
  };

  var sel = document.getElementById('ls-rail-jump');
""" + r"""
  return (async function() {
    if (!sel) { loadPage = window._origLoadPage; return {no_select: true, allOk: false}; }
    sel.value = 'PF_floor_roof';
    sel.dispatchEvent(new Event('change', {bubbles: true}));
    await new Promise(function(r) { setTimeout(r, 80); });

    loadPage = window._origLoadPage;

    var curPageIsRoofPage = curPage === 7;
    var roofShown  = !!document.querySelector('[data-catid="PF_floor_roof"]');
    var floor2Hidden = !document.querySelector('[data-catid="PF_floor_2"]');

    return {
      calledWith: calledWith,
      curPageIsRoofPage: curPageIsRoofPage,
      roofShown: roofShown,
      floor2Hidden: floor2Hidden,
      allOk: calledWith === 7 && curPageIsRoofPage && roofShown && floor2Hidden
    };
  })();
"""

# ---------------------------------------------------------------------------
# Check 4 — untaggedPageFallsBack
# Page 2 has no tag (only 5/6/7 are tagged) -> reseedActivePageFolders()
# (called from SEED, iterating 1..pageCount) buckets it into PF_excluded.
# lsFolderForPage() deliberately treats PF_excluded as "no folder", so this
# also proves the excluded-bucket special-case, not just an out-of-range page.
# ---------------------------------------------------------------------------
CHECK_FALLBACK = SEED + r"""
  curPage = 2; // untagged -> PF_excluded bucket -> treated as "no folder"
  buildPicker();
""" + r"""
  return (function() {
    var dash = document.querySelector('.ls-rail-dash');
    var dashShown = !!dash && dash.textContent.indexOf('—') >= 0;
    var allThreeShown = !!document.querySelector('[data-catid="PF_basement_1"]')
                      && !!document.querySelector('[data-catid="PF_floor_2"]')
                      && !!document.querySelector('[data-catid="PF_floor_roof"]');
    return {
      dashShown: dashShown,
      allThreeShown: allThreeShown,
      allOk: dashShown && allThreeShown
    };
  })();
"""

# ---------------------------------------------------------------------------
# Check 5 — pfModeOffNoRail
# ---------------------------------------------------------------------------
CHECK_MODE_OFF = SEED + r"""
  curPage = 6;
  state.pageFolderMode = false; // bypass the LFOC-1b force for this one call
  buildPicker();
""" + r"""
  return (function() {
    var host = document.getElementById('ls-rail');
    var railHidden = !host || host.style.display === 'none';
    var allThreeShown = !!document.querySelector('[data-catid="PF_basement_1"]')
                      && !!document.querySelector('[data-catid="PF_floor_2"]')
                      && !!document.querySelector('[data-catid="PF_floor_roof"]');
    return {
      railHidden: railHidden,
      allThreeShown: allThreeShown,
      allOk: railHidden && allThreeShown
    };
  })();
"""

# ---------------------------------------------------------------------------
# Check 6 — activeLayerRestoredOnReturn (slice 4 bug fix regression)
# User report: create a custom layer on a floor, navigate away, navigate BACK
# via a click path -> the panel/active-layer reverts to an old/default layer
# instead of the one created for that floor. Repro headlessly confirmed the
# ROW always rendered correctly (3 real click paths, see
# tests/repro_layer_scope_pageclick.py) but state.activeCat has no per-floor
# memory -- this check pins the fix: create+activate a custom layer on
# PF_floor_2, switch active layer on PF_floor_3, navigate back to page 6 ->
# activeCat must be restored to the floor-2 custom layer (not the floor-3 one
# or a default), and the DOM ".active" class must sit on ITS row immediately.
# ---------------------------------------------------------------------------
CHECK_ACTIVE_RESTORE = SEED + r"""
  curPage = 6; // PF_floor_2
  var custom2 = addLayer('gfa', 'CustomFloor2', '#ff00ff');
  custom2.parentId = 'PF_floor_2';
  state.catVis[custom2.id] = true; state.catLock[custom2.id] = false;
  state.activeCat = custom2.id; // simulate: user clicked this row to activate it
  buildPicker();

  window._origLoadPage = loadPage;
  loadPage = function(n) { curPage = n; afterPage(); return Promise.resolve(); };
""" + r"""
  return (async function() {
    // navigate to floor 3, activate a DIFFERENT (base) layer there
    await loadPage(7);
    var floor3BaseId = LAYERS.find(function(l) { return l.parentId === 'PF_floor_roof'; }).id;
    state.activeCat = floor3BaseId;
    buildPicker();

    // navigate back to floor 2 (click-path proxy — same loadPage() the real
    // click handlers call; afterPage()/buildPicker() are NOT stubbed)
    await loadPage(6);

    loadPage = window._origLoadPage;

    var activeCatRestored = state.activeCat === custom2.id;
    var domRow = document.querySelector('.lt-layer-row[data-catid="' + custom2.id + '"]');
    var domActiveClass = !!(domRow && domRow.classList.contains('active'));
    var noStaleActiveElsewhere = document.querySelectorAll('.lt-layer-row.active').length === 1;

    return {
      activeCatRestored: activeCatRestored,
      domActiveClass: domActiveClass,
      noStaleActiveElsewhere: noStaleActiveElsewhere,
      allOk: activeCatRestored && domActiveClass && noStaleActiveElsewhere
    };
  })();
"""

# ---------------------------------------------------------------------------
# Check 7 — activeLayerDefaultsOnFirstVisit
# BUG-20260706-lite-active-layer-not-following-page (fix part a): navigating
# to a folder NEVER visited this session (no per-folder memory) must default
# state.activeCat to a layer OF that folder — not leave it pointing at the
# previous folder's layer (user screenshot: on roof page, "วาดที่: ที่ดิน").
# ---------------------------------------------------------------------------
CHECK_DEFAULT_ON_FIRST_VISIT = SEED + r"""
  curPage = 6; // PF_floor_2
  var floor2Base = LAYERS.find(function(l) { return l.parentId === 'PF_floor_2'; });
  state.activeCat = floor2Base.id;
  buildPicker();

  window._origLoadPage = loadPage;
  loadPage = function(n) { curPage = n; afterPage(); return Promise.resolve(); };
""" + r"""
  return (async function() {
    // PF_floor_roof has never been visited -> no mem entry for it
    await loadPage(7);
    loadPage = window._origLoadPage;

    var f = (typeof pageFolderOfLayer === 'function') ? pageFolderOfLayer(state.activeCat) : null;
    var belongsToRoof = !!(f && f.id === 'PF_floor_roof');
    var isRealLayer = !!layerById(state.activeCat);
    return {
      activeCat: state.activeCat,
      belongsToRoof: belongsToRoof,
      isRealLayer: isRealLayer,
      allOk: belongsToRoof && isRealLayer
    };
  })();
"""

# ---------------------------------------------------------------------------
# Check 8 — foreignDrawCommitBlocked
# BUG-20260706 (fix part b, belt-and-suspenders): even if some path leaves
# state.activeCat pointing at another folder's layer, finishDraft() must
# REFUSE the commit (no object pushed) and show a hint — never silently
# misattribute measured area to the wrong floor's layer.
# ---------------------------------------------------------------------------
CHECK_FOREIGN_DRAW_BLOCKED = SEED + r"""
  curPage = 6; // PF_floor_2
  buildPicker();
  // force a FOREIGN activeCat (bypass the picker sync deliberately)
  var roofBase = LAYERS.find(function(l) { return l.parentId === 'PF_floor_roof'; });
  state.activeCat = roofBase.id;
  state.catLock[roofBase.id] = false;
  state.tool = 'poly';
  state.draft = [{x: 10, y: 10}, {x: 110, y: 10}, {x: 110, y: 110}];
""" + r"""
  return (function() {
    var before = PS['6'].objects.length;
    finishDraft();
    var after = PS['6'].objects.length;
    var hintEl = document.getElementById('hint');
    var blocked = after === before;
    var draftCleared = state.draft === null;
    var hintWarns = !!(hintEl && hintEl.innerHTML.indexOf('⚠') >= 0);
    return {
      before: before, after: after,
      blocked: blocked, draftCleared: draftCleared, hintWarns: hintWarns,
      allOk: blocked && draftCleared && hintWarns
    };
  })();
"""

# ---------------------------------------------------------------------------
# Check 9 — multiPageFolderRailReachesAllPages
# BUG-20260706-lite-multi-site-page-tag: a PF folder holding MORE than one
# page (2 site-plan sheets -> PF_site.pages=[5,6]) must be fully reachable
# from the rail: counter shows "แผ่น i/N", ▶ steps within the folder before
# crossing folders, and _lsGoTo() on the already-active folder advances to
# the folder's next page (wrap) instead of always resetting to pages[0].
# ---------------------------------------------------------------------------
CHECK_MULTI_PAGE_FOLDER = SEED + r"""
  pageTags      = {5: 'site', 6: 'site', 7: 'floor'};
  pageFloorNum  = {7: 1};
  pageFloorKind = {7: 'normal'};
  reseedActivePageFolders();

  curPage = 5; // PF_site page 1 of 2
  buildPicker();

  window._origLoadPage = loadPage;
  loadPage = function(n) { curPage = n; afterPage(); return Promise.resolve(); };
""" + r"""
  return (async function() {
    function counterText() {
      var c = document.querySelector('.ls-rail-counter');
      return c ? c.textContent : '';
    }
    var sitePagesOk = JSON.stringify(folderById('PF_site').pages) === JSON.stringify([5, 6]);
    var counterShowsSheet1 = counterText().indexOf('แผ่น 1/2') >= 0;

    // ▶ steps WITHIN the folder first: page 5 -> 6
    document.getElementById('ls-rail-next').click();
    await new Promise(function(r) { setTimeout(r, 40); });
    var steppedWithin = curPage === 6;
    var counterShowsSheet2 = counterText().indexOf('แผ่น 2/2') >= 0;

    // ▶ again: end of folder pages -> crosses to the NEXT folder (page 7)
    document.getElementById('ls-rail-next').click();
    await new Promise(function(r) { setTimeout(r, 40); });
    var crossedFolder = curPage === 7;

    // jump back to PF_site from another folder -> lands on pages[0]
    _lsGoTo(folderById('PF_site'));
    await new Promise(function(r) { setTimeout(r, 40); });
    var landedFirst = curPage === 5;

    // re-select the folder the canvas is already in -> advances (wrap)
    _lsGoTo(folderById('PF_site'));
    await new Promise(function(r) { setTimeout(r, 40); });
    var advancedOnReselect = curPage === 6;

    loadPage = window._origLoadPage;
    return {
      sitePagesOk: sitePagesOk,
      counterShowsSheet1: counterShowsSheet1,
      steppedWithin: steppedWithin,
      counterShowsSheet2: counterShowsSheet2,
      crossedFolder: crossedFolder,
      landedFirst: landedFirst,
      advancedOnReselect: advancedOnReselect,
      allOk: sitePagesOk && counterShowsSheet1 && steppedWithin && counterShowsSheet2 &&
             crossedFolder && landedFirst && advancedOnReselect
    };
  })();
"""

CHECKS = [
    ("scopedRenderShowsOnlyActive",  CHECK_SCOPED_RENDER,   ["allOk"]),
    ("railListsKindAwareOrder",      CHECK_RAIL_ORDER,      ["allOk"]),
    ("railSelectionIsBidirectional", CHECK_BIDIRECTIONAL,   ["allOk"]),
    ("untaggedPageFallsBack",        CHECK_FALLBACK,        ["allOk"]),
    ("pfModeOffNoRail",              CHECK_MODE_OFF,        ["allOk"]),
    ("activeLayerRestoredOnReturn",  CHECK_ACTIVE_RESTORE,  ["allOk"]),
    ("activeLayerDefaultsOnFirstVisit", CHECK_DEFAULT_ON_FIRST_VISIT, ["allOk"]),
    ("foreignDrawCommitBlocked",     CHECK_FOREIGN_DRAW_BLOCKED, ["allOk"]),
    ("multiPageFolderRailReachesAllPages", CHECK_MULTI_PAGE_FOLDER, ["allOk"]),
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
    passed = set()

    with sync_playwright() as pw:
        b = pw.chromium.launch()
        pg = b.new_page()
        pg.on("pageerror", lambda e: page_errors.append(f"pageerror: {e}"))
        pg.goto(f"http://127.0.0.1:{port}/", wait_until="networkidle")
        time.sleep(0.8)  # allow DOMContentLoaded + setTimeout(0) auto-seed to fire

        print()
        print("LITE-LAYER-SCOPE checks:")
        for name, scenario, required_keys in CHECKS:
            wrapped = "async () => {\n" + scenario + "\n}"
            try:
                result = pg.evaluate(wrapped)
            except Exception as ex:
                print(f"  {name:32s} -> EXCEPTION: {ex}")
                failures.append(f"check '{name}' threw: {ex}")
                continue

            ok = all(result.get(k) is True for k in required_keys)
            if ok:
                passed.add(name)
            status = "PASS" if ok else "FAIL"
            print(f"  {name:32s} -> {status}  {result}")
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
        print("LITE_LAYER_SCOPE_FAIL")
        sys.exit(1)
    else:
        if {"activeLayerDefaultsOnFirstVisit", "foreignDrawCommitBlocked"} <= passed:
            print("LITE_ACTIVE_LAYER_FOLLOW_OK")
        if "multiPageFolderRailReachesAllPages" in passed:
            print("LITE_LAYER_SCOPE_MULTI_PAGE_FOLDER_OK")
        print("LITE_LAYER_SCOPE_OK")


if __name__ == "__main__":
    main()
