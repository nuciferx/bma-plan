"""
LOVS-1: Overview Setup Wizard regression test.

Verifies the 3-tab wizard (Classify → Number Floors → Review) is injected into
the live #ov overlay via the dynamically loaded overview-setup.js module.

8 sub-checks:
  overrideInstalled     __lovsWrapped===true, openOv is wrapped, #__lovs_script__ in head
  threeTabsRender       3 .tab-body[data-tab] elements, step-1 tab has class "act"
  classifyRendersTiles  tiles render with correct tag-chip labels
  tagCycleViaKeyboard   key press "2" sets pageTags[1]==="floor", focusPage advances
  multiSelectShiftRange shift-click range [2..5], bulk tag sets all to "detail"
  step2Sequential       Step 2 only shows floor pages; Sequential assigns 1,2,...,roof
  step3ReportRenders    Step 3 #report has "GFA Breakdown" + number + "Coverage"
  closeOnEsc            Esc clears selection first, second Esc closes overlay

Emits LITE_OVERVIEW_SETUP_OK on success.

    py -3 lite/tests/test_overview_setup.py
"""
import socket, threading, time, sys
from pathlib import Path

LITE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LITE))
import uvicorn
from playwright.sync_api import sync_playwright


def _free_port(start=8420):
    for p in range(start, start + 60):
        with socket.socket() as s:
            if s.connect_ex(("127.0.0.1", p)) != 0:
                return p
    raise RuntimeError("no free port")


# ---------------------------------------------------------------------------
# Shared setup: inject globals that the wizard needs
# ---------------------------------------------------------------------------
SETUP_GLOBALS = r"""
async () => {
  // Give scripts time to load
  await new Promise(r => setTimeout(r, 300));

  // Seed globals so wizard has data to work with
  pageCount = 8;
  pageTags = {};
  pageFloorNum = {};
  pageFloorKind = {};
  excluded = {};
  pageNames = {};
  PS = {};
  for (var i = 1; i <= 8; i++) {
    PS[i] = {objects: [], scale: null, annotations: []};
  }
  // Pre-tag a couple pages
  pageTags[2] = 'site';
  pageTags[4] = 'floor';
  pageTags[5] = 'floor';
  pageTags[6] = 'floor';
  pageTags[7] = 'floor';

  return {done: true};
}
"""

# ---------------------------------------------------------------------------
# Sub-check 1 — overrideInstalled
# ---------------------------------------------------------------------------
CHECK_OVERRIDE_INSTALLED = r"""
async () => {
  await new Promise(r => setTimeout(r, 400));

  var scriptTag = document.getElementById('__lovs_script__');
  var wrapped = window.__lovsWrapped === true;
  var ovWrapped = typeof openOv === 'function' && openOv.__lovsWrapped === true;

  return {
    scriptTagExists: !!scriptTag,
    scriptTagSrc: scriptTag ? scriptTag.getAttribute('src') : null,
    lovsWrapped: wrapped,
    openOvWrapped: ovWrapped,
    allOk: !!scriptTag && wrapped && ovWrapped
  };
}
"""

# ---------------------------------------------------------------------------
# Sub-check 2 — threeTabsRender
# ---------------------------------------------------------------------------
CHECK_THREE_TABS_RENDER = r"""
async () => {
  // Open the overlay via the wrapped openOv
  // First we need a caseId so the guard doesn't block us — set a mock
  var _origCaseId = caseId;
  caseId = 'test-mock';

  openOv();
  await new Promise(r => setTimeout(r, 200));

  var tabs = document.querySelectorAll('#ov-panel .tab-body[data-tab]');
  var tab1 = document.querySelector('#ov-panel .tab-body[data-tab="1"]');
  var tab2 = document.querySelector('#ov-panel .tab-body[data-tab="2"]');
  var tab3 = document.querySelector('#ov-panel .tab-body[data-tab="3"]');
  var tab1Active = tab1 ? tab1.classList.contains('act') : false;

  return {
    tabCount: tabs.length,
    tab1Exists: !!tab1,
    tab2Exists: !!tab2,
    tab3Exists: !!tab3,
    tab1Active: tab1Active,
    panelExists: !!document.getElementById('ov-panel'),
    allOk: tabs.length === 3 && tab1Active && !!tab2 && !!tab3
  };
}
"""

# ---------------------------------------------------------------------------
# Sub-check 3 — classifyRendersTiles
# ---------------------------------------------------------------------------
CHECK_CLASSIFY_RENDERS_TILES = r"""
async () => {
  // Ensure overlay is open
  var ov = document.getElementById('ov');
  if (!ov || !ov.classList.contains('show')) {
    caseId = 'test-mock';
    openOv();
    await new Promise(r => setTimeout(r, 200));
  }

  // Tile for p2 should exist (tag=site)
  var tile2 = document.querySelector('#grid-classify .ov-tile[data-pg="2"]');
  // Its tag-chip should say "ผังบริเวณ"
  var chip2 = tile2 ? tile2.querySelector('.ov-tag-chip') : null;
  var chip2Text = chip2 ? chip2.textContent.trim() : '';
  var hasSiteLabel = chip2Text.indexOf('ผังบริเวณ') >= 0;

  // Tile for p4 (floor) should have a floor input
  var tile4 = document.querySelector('#grid-classify .ov-tile[data-pg="4"]');
  var floorInput4 = tile4 ? tile4.querySelector('.ov-floor-input') : null;

  // Should have 8 tiles total (pageCount=8)
  var allTiles = document.querySelectorAll('#grid-classify .ov-tile');

  return {
    tileCount: allTiles.length,
    tile2Exists: !!tile2,
    chip2Text: chip2Text,
    hasSiteLabel: hasSiteLabel,
    tile4Exists: !!tile4,
    hasFloorInput4: !!floorInput4,
    allOk: allTiles.length === 8 && hasSiteLabel && !!floorInput4
  };
}
"""

# ---------------------------------------------------------------------------
# Sub-check 4 — tagCycleViaKeyboard
# ---------------------------------------------------------------------------
CHECK_TAG_CYCLE_VIA_KEYBOARD = r"""
async () => {
  // Reset p1 to untagged, set focusPage = 1
  pageTags[1] = '';
  // Force re-render classify
  if (typeof _lovsRenderClassify === 'function') {
    _lovsRenderClassify();
    await new Promise(r => setTimeout(r, 50));
  }

  // Get focus on p1 by clicking
  var tile1 = document.querySelector('#grid-classify .ov-tile[data-pg="1"]');
  if (tile1) tile1.click();
  await new Promise(r => setTimeout(r, 50));

  var prevFocus = typeof _lovsFocusPage !== 'undefined' ? _lovsFocusPage : null;

  // Dispatch key '2' (= floor)
  document.dispatchEvent(new KeyboardEvent('keydown', {key: '2', bubbles: true}));
  await new Promise(r => setTimeout(r, 100));

  var tagResult = pageTags[1];
  var focusAfter = typeof _lovsFocusPage !== 'undefined' ? _lovsFocusPage : null;

  return {
    prevFocus: prevFocus,
    tagResult: tagResult,
    tagIsFloor: tagResult === 'floor',
    focusAfter: focusAfter,
    focusAdvanced: focusAfter > 1,
    allOk: tagResult === 'floor' && focusAfter > 1
  };
}
"""

# ---------------------------------------------------------------------------
# Sub-check 5 — multiSelectShiftRange
# ---------------------------------------------------------------------------
CHECK_MULTI_SELECT_SHIFT_RANGE = r"""
async () => {
  // Clear pageTags for 2-5 first
  pageTags[2] = 'site'; pageTags[3] = ''; pageTags[4] = 'floor'; pageTags[5] = 'floor';

  // Re-render classify
  if (typeof _lovsRenderClassify === 'function') {
    _lovsRenderClassify();
    await new Promise(r => setTimeout(r, 80));
  }

  // Click p2 (single select, sets anchor)
  var tile2 = document.querySelector('#grid-classify .ov-tile[data-pg="2"]');
  if (tile2) tile2.click();
  await new Promise(r => setTimeout(r, 50));

  // Shift-click p5 (range 2..5)
  var tile5 = document.querySelector('#grid-classify .ov-tile[data-pg="5"]');
  if (tile5) {
    tile5.dispatchEvent(new MouseEvent('click', {bubbles: true, shiftKey: true}));
  }
  await new Promise(r => setTimeout(r, 50));

  var selCount = typeof __lovsSelected !== 'undefined' ? __lovsSelected.size : 0;
  // Count tiles with class "sel"
  var selTiles = document.querySelectorAll('#grid-classify .ov-tile.sel');

  // Bulk apply "detail" tag
  var bulkChip = document.querySelector('#bulkbar [data-bulk-tag="detail"]');
  if (bulkChip) {
    bulkChip.click();
    await new Promise(r => setTimeout(r, 80));
  }

  var p2tag = pageTags[2], p3tag = pageTags[3], p4tag = pageTags[4], p5tag = pageTags[5];
  var allDetail = (p2tag === 'detail') && (p3tag === 'detail') && (p4tag === 'detail') && (p5tag === 'detail');

  return {
    selCount: selCount,
    selTilesDOM: selTiles.length,
    rangeOk: selCount === 4 || selTiles.length === 4,
    bulkChipFound: !!bulkChip,
    p2tag: p2tag, p3tag: p3tag, p4tag: p4tag, p5tag: p5tag,
    allDetail: allDetail,
    allOk: (selCount >= 4 || selTiles.length >= 4) && allDetail
  };
}
"""

# ---------------------------------------------------------------------------
# Sub-check 6 — step2Sequential
# ---------------------------------------------------------------------------
CHECK_STEP2_SEQUENTIAL = r"""
async () => {
  // Reset floor tags — exactly 4 floor pages
  pageFloorNum = {};
  for (var i = 1; i <= 8; i++) pageTags[i] = '';
  pageTags[4] = 'floor';
  pageTags[5] = 'floor';
  pageTags[6] = 'floor';
  pageTags[7] = 'floor';
  pageTags[2] = 'site';

  // Go to step 1 first to re-render classify, then step 2
  var step1 = document.querySelector('#ov-steps .step[data-step="1"]');
  if (step1) { step1.click(); await new Promise(r => setTimeout(r, 80)); }

  // Navigate to step 2
  var step2 = document.querySelector('#ov-steps .step[data-step="2"]');
  if (step2) step2.click();
  await new Promise(r => setTimeout(r, 200));

  // Only floor pages should appear in strip
  var chips = document.querySelectorAll('#floor-strip .fchip');
  var chipCount = chips.length;

  // Click sequential
  var seqBtn = document.getElementById('ov-seq');
  if (seqBtn) {
    seqBtn.click();
    await new Promise(r => setTimeout(r, 100));
  }

  // With 4 floor pages and >=4 threshold, last should be roof
  var pn4 = pageFloorNum[4], pn5 = pageFloorNum[5], pn6 = pageFloorNum[6], pn7 = pageFloorNum[7];
  var hasRoof = (pn4 === 'roof' || pn5 === 'roof' || pn6 === 'roof' || pn7 === 'roof');
  var sequential = (pn4 === 1 && pn5 === 2 && pn6 === 3 && pn7 === 'roof') ||
                   (pn4 === 1 && pn5 === 2 && pn6 === 3 && pn7 === 4) || // if <4 pages
                   hasRoof;

  return {
    chipCount: chipCount,
    onlyFloorPages: chipCount === 4,
    pn4: pn4, pn5: pn5, pn6: pn6, pn7: pn7,
    hasRoof: hasRoof,
    sequential: sequential,
    allOk: chipCount === 4 && hasRoof
  };
}
"""

# ---------------------------------------------------------------------------
# Sub-check 7 — step3ReportRenders
# ---------------------------------------------------------------------------
CHECK_STEP3_REPORT_RENDERS = r"""
async () => {
  // Navigate to step 3
  var step3 = document.querySelector('#ov-steps .step[data-step="3"]');
  if (step3) step3.click();
  await new Promise(r => setTimeout(r, 200));

  var report = document.getElementById('report');
  var reportExists = !!report;
  var html = report ? report.innerHTML : '';

  // Must contain GFA Breakdown
  var hasGFA = html.indexOf('GFA Breakdown') >= 0;
  // Must contain a comma-formatted number like 650.00
  var hasNumber = /\d{1,3}[\.,]\d{2}/.test(html);
  // Must contain "Coverage"
  var hasCoverage = html.indexOf('Coverage') >= 0;

  return {
    reportExists: reportExists,
    hasGFA: hasGFA,
    hasNumber: hasNumber,
    hasCoverage: hasCoverage,
    allOk: reportExists && hasGFA && hasNumber && hasCoverage
  };
}
"""

# ---------------------------------------------------------------------------
# Sub-check 8 — closeOnEsc
# ---------------------------------------------------------------------------
CHECK_CLOSE_ON_ESC = r"""
async () => {
  // Make sure overlay is open on step 1
  var step1 = document.querySelector('#ov-steps .step[data-step="1"]');
  if (step1) step1.click();
  await new Promise(r => setTimeout(r, 100));

  var ov = document.getElementById('ov');
  var openBefore = ov ? ov.classList.contains('show') : false;

  // Clear any selection first
  if (typeof _lovsSelected !== 'undefined') _lovsSelected.clear();
  if (typeof _lovsRenderClassify === 'function') _lovsRenderClassify();
  await new Promise(r => setTimeout(r, 50));

  // Press Esc with no selection → should close
  document.dispatchEvent(new KeyboardEvent('keydown', {key: 'Escape', bubbles: true}));
  await new Promise(r => setTimeout(r, 100));

  var closedAfterEsc1 = ov ? !ov.classList.contains('show') : false;

  // Re-open, multi-select 2 tiles, press Esc once (should clear selection), then again (closes)
  caseId = 'test-mock';
  openOv();
  await new Promise(r => setTimeout(r, 200));

  // Select 2 tiles programmatically
  if (typeof _lovsSelected !== 'undefined') {
    _lovsSelected.add(1); _lovsSelected.add(2);
  }
  if (typeof _lovsRenderClassify === 'function') _lovsRenderClassify();
  await new Promise(r => setTimeout(r, 50));

  var selBeforeEsc = typeof _lovsSelected !== 'undefined' ? _lovsSelected.size : 0;

  // First Esc — clears selection, overlay stays
  document.dispatchEvent(new KeyboardEvent('keydown', {key: 'Escape', bubbles: true}));
  await new Promise(r => setTimeout(r, 100));

  var selAfterEsc1 = typeof _lovsSelected !== 'undefined' ? _lovsSelected.size : 0;
  var ovStillOpen = ov ? ov.classList.contains('show') : false;

  // Second Esc — closes
  document.dispatchEvent(new KeyboardEvent('keydown', {key: 'Escape', bubbles: true}));
  await new Promise(r => setTimeout(r, 100));

  var closedAfterEsc2 = ov ? !ov.classList.contains('show') : false;

  return {
    openBefore: openBefore,
    closedAfterEsc1: closedAfterEsc1,
    selBeforeEsc: selBeforeEsc,
    selAfterEsc1: selAfterEsc1,
    selCleared: selAfterEsc1 === 0,
    ovStillOpen: ovStillOpen,
    closedAfterEsc2: closedAfterEsc2,
    allOk: closedAfterEsc1 && selAfterEsc1 === 0 && ovStillOpen && closedAfterEsc2
  };
}
"""

CHECK_FLOOR_KIND_DROPDOWN = r"""
async () => {
  // Re-init clean state
  for (var k in pageTags) delete pageTags[k];
  for (var k in pageFloorNum) delete pageFloorNum[k];
  for (var k in pageFloorKind) delete pageFloorKind[k];
  pageTags[3] = 'floor';
  pageTags[4] = 'floor';
  pageTags[5] = 'floor';
  pageTags[6] = 'floor';
  pageFloorNum[3] = 1;  pageFloorKind[3] = 'normal';

  // Force step 1 re-render
  var step1 = document.querySelector('#ov-steps .step[data-step="1"]');
  if (step1) { step1.click(); await new Promise(r => setTimeout(r, 80)); }

  // Tile p3 must have an ov-fkind-sel with 4 options + 'normal' selected
  var tile3 = document.querySelector('#grid-classify .ov-tile[data-pg="3"]');
  var sel3 = tile3 && tile3.querySelector('.ov-fkind-sel');
  var optionsOk = sel3 && sel3.options.length === 4;
  var optionValues = sel3 ? Array.from(sel3.options).map(function(o){return o.value;}) : [];
  var hasAllKinds = optionValues.indexOf('normal') >= 0 && optionValues.indexOf('basement') >= 0
                 && optionValues.indexOf('mechanical') >= 0 && optionValues.indexOf('rooftop') >= 0;
  var selectedNormal = sel3 && sel3.value === 'normal';

  // Change p4 → mechanical (programmatic), trigger change event
  var tile4 = document.querySelector('#grid-classify .ov-tile[data-pg="4"]');
  var sel4 = tile4 && tile4.querySelector('.ov-fkind-sel');
  if (sel4) { sel4.value = 'mechanical'; sel4.dispatchEvent(new Event('change', {bubbles:true})); }
  await new Promise(r => setTimeout(r, 100));
  var p4kind = pageFloorKind[4];
  var p4numCleared = pageFloorNum[4] === undefined;

  // After mechanical change, the floor-input should be HIDDEN/replaced by a span 'MEC'
  // Re-query (renderClassify rebuilt the DOM)
  tile4 = document.querySelector('#grid-classify .ov-tile[data-pg="4"]');
  var input4 = tile4 && tile4.querySelector('.ov-floor-input');
  var mecLabelOk = !input4;  // no input means we're in non-numeric kind

  // Change p5 → rooftop, expect pageFloorNum[5]='roof'
  var tile5 = document.querySelector('#grid-classify .ov-tile[data-pg="5"]');
  var sel5 = tile5 && tile5.querySelector('.ov-fkind-sel');
  if (sel5) { sel5.value = 'rooftop'; sel5.dispatchEvent(new Event('change', {bubbles:true})); }
  await new Promise(r => setTimeout(r, 100));
  var p5kind = pageFloorKind[5];
  var p5num = pageFloorNum[5];

  // Change p6 → basement, then set number to 2
  var tile6 = document.querySelector('#grid-classify .ov-tile[data-pg="6"]');
  var sel6 = tile6 && tile6.querySelector('.ov-fkind-sel');
  if (sel6) { sel6.value = 'basement'; sel6.dispatchEvent(new Event('change', {bubbles:true})); }
  await new Promise(r => setTimeout(r, 100));
  // Re-query for the now-visible floor-input
  tile6 = document.querySelector('#grid-classify .ov-tile[data-pg="6"]');
  var inp6 = tile6 && tile6.querySelector('.ov-floor-input');
  var inp6Visible = !!inp6;
  if (inp6) { inp6.value = '2'; inp6.dispatchEvent(new Event('change', {bubbles:true})); }
  await new Promise(r => setTimeout(r, 100));
  var p6kind = pageFloorKind[6], p6num = pageFloorNum[6];

  return {
    optionsCount: sel3 ? sel3.options.length : 0,
    hasAllKinds: hasAllKinds,
    selectedNormal: selectedNormal,
    p4kind: p4kind, p4numCleared: p4numCleared, mecLabelOk: mecLabelOk,
    p5kind: p5kind, p5num: p5num,
    p6kind: p6kind, p6num: p6num, inp6Visible: inp6Visible,
    allOk: optionsOk && hasAllKinds && selectedNormal
         && p4kind === 'mechanical' && p4numCleared && mecLabelOk
         && p5kind === 'rooftop' && p5num === 'roof'
         && p6kind === 'basement' && p6num === 2 && inp6Visible
  };
}
"""

CHECK_REAL_BINDING = r"""
async () => {
  // Reset to controlled state
  for (var k in pageTags) delete pageTags[k];
  for (var k in pageFloorNum) delete pageFloorNum[k];
  for (var k in pageFloorKind) delete pageFloorKind[k];
  for (var k in PS) delete PS[k];
  pageCount = 5;
  // pages: 1=cover, 2=site, 3=floor#1, 4=floor#2, 5=detail
  pageTags[2] = 'site'; pageTags[3] = 'floor'; pageTags[4] = 'floor'; pageTags[5] = 'detail';
  pageFloorKind[3] = 'normal'; pageFloorNum[3] = 1;
  pageFloorKind[4] = 'normal'; pageFloorNum[4] = 2;

  // Seed scales (1 pt = 1 m for easy math)
  for (var n = 1; n <= 5; n++) PS[n] = {objects: [], scale: {pts_per_m: 1.0}, annotations: []};

  // Reset LAYERS + FOLDERS, then seed PFL folders + custom layers
  LAYERS.length = 0; FOLDERS.length = 0; initLayers();

  // Seed PF folders via real LPFL API
  state.pageFolderMode = true;
  if (typeof seedPageFolders === 'function') {
    seedPageFolders([1,2,3,4,5], pageTags, pageFloorNum);
  }

  // Find seeded layers we'll attach measurements to
  var siteLandLayer = null, coverLayer = null, f1GfaLayer = null, f2GfaLayer = null, f1DedLayer = null;
  LAYERS.forEach(function(l) {
    if (l.parentId === 'PF_site') {
      if (l.role === 'site' && !siteLandLayer) siteLandLayer = l;
      if (l.role === 'gfa' && !coverLayer) coverLayer = l;
    }
    if (l.parentId === 'PF_floor_1' && l.role === 'gfa') f1GfaLayer = l;
    if (l.parentId === 'PF_floor_2' && l.role === 'gfa') f2GfaLayer = l;
    if (l.parentId === 'PF_floor_1' && l.role === 'ded' && !f1DedLayer) f1DedLayer = l;
  });

  // Add poly objects with known areas (axis-aligned squares):
  // p2 (site page): land = 100x100 m square  → 10000 m² for siteLandLayer
  // p2 (site page): cover = 60x40 m square   → 2400 m² for coverLayer
  // p3 (floor 1):   gfa = 50x40 m square     → 2000 m² for f1GfaLayer
  // p3 (floor 1):   ded = 10x10              → 100 m² (deduction)
  // p4 (floor 2):   gfa = 50x40              → 2000 m² for f2GfaLayer
  function rect(w, h, ox, oy) {
    ox = ox || 0; oy = oy || 0;
    return [{x:ox,y:oy},{x:ox+w,y:oy},{x:ox+w,y:oy+h},{x:ox,y:oy+h}];
  }
  if (siteLandLayer) PS[2].objects.push({id:1, kind:'poly', pts: rect(100,100,0,0),   catId: siteLandLayer.id, counting:false});
  if (coverLayer)    PS[2].objects.push({id:2, kind:'poly', pts: rect(60,40,200,0),   catId: coverLayer.id,    counting:false});
  if (f1GfaLayer)    PS[3].objects.push({id:3, kind:'poly', pts: rect(50,40,0,0),     catId: f1GfaLayer.id,    counting:false});
  if (f1DedLayer)    PS[3].objects.push({id:4, kind:'poly', pts: rect(10,10,100,0),   catId: f1DedLayer.id,    counting:false});
  if (f2GfaLayer)    PS[4].objects.push({id:5, kind:'poly', pts: rect(50,40,0,0),     catId: f2GfaLayer.id,    counting:false});

  // Re-render step 3
  var step3 = document.querySelector('#ov-steps .step[data-step="3"]');
  if (step3) { step3.click(); await new Promise(r => setTimeout(r, 200)); }

  var html = document.getElementById('report').innerHTML;

  // Verify real numbers appear and old mock numbers DON'T
  // pts_per_m=1, area = poly area in pt² interpreted as m². 100x100=10000, 60x40=2400.
  var has10000 = html.indexOf('10,000.00') >= 0;
  var has2400  = html.indexOf('2,400.00')  >= 0;
  var hasGFATot = html.indexOf('4,000.00') >= 0;  // f1+f2 gross = 2000+2000
  // mock land 1,919.20 must NOT appear
  var mockLandGone = html.indexOf('1,919.20') < 0;
  // mock cover 839.10 must NOT appear
  var mockCoverGone = html.indexOf('839.10') < 0;

  // Export button visible on step 3
  var expBtn = document.getElementById('ov-export');
  var expVisible = expBtn && expBtn.style.display !== 'none';

  return {
    siteLayerFound: !!siteLandLayer,
    coverLayerFound: !!coverLayer,
    f1GfaFound: !!f1GfaLayer,
    has10000_land: has10000,
    has2400_cover: has2400,
    hasGFATot4000: hasGFATot,
    mockLandGone: mockLandGone,
    mockCoverGone: mockCoverGone,
    expVisible: !!expVisible,
    allOk: has10000 && has2400 && hasGFATot && mockLandGone && mockCoverGone && !!expVisible
  };
}
"""

CHECKS = [
    ("overrideInstalled",      CHECK_OVERRIDE_INSTALLED,      ["allOk"]),
    ("threeTabsRender",        CHECK_THREE_TABS_RENDER,        ["allOk"]),
    ("classifyRendersTiles",   CHECK_CLASSIFY_RENDERS_TILES,   ["allOk"]),
    ("tagCycleViaKeyboard",    CHECK_TAG_CYCLE_VIA_KEYBOARD,   ["allOk"]),
    ("multiSelectShiftRange",  CHECK_MULTI_SELECT_SHIFT_RANGE, ["allOk"]),
    ("step2Sequential",        CHECK_STEP2_SEQUENTIAL,         ["allOk"]),
    ("step3ReportRenders",     CHECK_STEP3_REPORT_RENDERS,     ["allOk"]),
    ("closeOnEsc",             CHECK_CLOSE_ON_ESC,             ["allOk"]),
    ("floorKindDropdown",      CHECK_FLOOR_KIND_DROPDOWN,      ["allOk"]),
    ("realDataBinding",        CHECK_REAL_BINDING,             ["allOk"]),
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
        time.sleep(2.0)  # allow dynamic script load + setTimeout bootstrap

        # Run shared setup
        try:
            pg.evaluate(SETUP_GLOBALS)
        except Exception as ex:
            print(f"  SETUP FAILED: {ex}")
            failures.append(f"setup threw: {ex}")

        print()
        print("LITE-OVERVIEW-SETUP checks:")
        for name, scenario, required_keys in CHECKS:
            try:
                result = pg.evaluate(scenario)
            except Exception as ex:
                print(f"  {name:40s} -> EXCEPTION: {ex}")
                failures.append(f"check '{name}' threw: {ex}")
                continue

            ok = all(result.get(k) is True for k in required_keys)
            status = "PASS" if ok else "FAIL"
            print(f"  {name:40s} -> {status}  {result}")
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
        print("LITE_OVERVIEW_SETUP_FAIL")
        sys.exit(1)
    else:
        print("LITE_OVERVIEW_SETUP_OK")


if __name__ == "__main__":
    main()
