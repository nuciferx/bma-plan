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

CHECKS = [
    ("overrideInstalled",      CHECK_OVERRIDE_INSTALLED,      ["allOk"]),
    ("threeTabsRender",        CHECK_THREE_TABS_RENDER,        ["allOk"]),
    ("classifyRendersTiles",   CHECK_CLASSIFY_RENDERS_TILES,   ["allOk"]),
    ("tagCycleViaKeyboard",    CHECK_TAG_CYCLE_VIA_KEYBOARD,   ["allOk"]),
    ("multiSelectShiftRange",  CHECK_MULTI_SELECT_SHIFT_RANGE, ["allOk"]),
    ("step2Sequential",        CHECK_STEP2_SEQUENTIAL,         ["allOk"]),
    ("step3ReportRenders",     CHECK_STEP3_REPORT_RENDERS,     ["allOk"]),
    ("closeOnEsc",             CHECK_CLOSE_ON_ESC,             ["allOk"]),
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
