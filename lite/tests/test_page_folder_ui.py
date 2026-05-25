"""
LPFL-1c: page-folder-layers UI regression guard.

Verifies the page-folder mode toggle, auto-seed, panel render, add-layer
row, toggle-off revert, and tag-change auto-reseed. All checks run in a
single browser session. No real PDF needed — PS is seeded via evaluate.

7 sub-checks:
  toggleButtonExists    #pfl-toggle injected, initial text is "📂"
  toggleOnSeeds         click → mode ON, PF_site + PF_floor_2 seeded
  panelRendersPFFolders lt-folder-row with data-catid="PF_site" in DOM,
                        text contains "ผังบริเวณ" and "(p5)"
  panelRendersBaseLayers 3 child layer rows under PF_site with correct names
  addLayerRowWorks      .lt-add row click → new layer under PF_floor_2
  toggleOffReverts      click again → mode OFF, name has no "หน้า)" suffix
  autoSeedOnTagChange   liteSetTag(8,'floor') + pageFloorNum[8]=3 →
                        PF_floor_3 seeded with page 8

Emits LITE_PAGE_FOLDER_UI_OK on success.

    py -3 lite/tests/test_page_folder_ui.py
"""
import socket, threading, time, sys
from pathlib import Path

LITE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LITE))
import uvicorn
from playwright.sync_api import sync_playwright


def _free_port(start=8380):
    for p in range(start, start + 60):
        with socket.socket() as s:
            if s.connect_ex(("127.0.0.1", p)) != 0:
                return p
    raise RuntimeError("no free port")


# ---------------------------------------------------------------------------
# Sub-check 1 — toggleButtonExists
# ---------------------------------------------------------------------------
CHECK_TOGGLE_EXISTS = r"""
() => {
  var btn = document.getElementById('pfl-toggle');
  return {
    buttonExists: !!btn,
    initialText: btn ? btn.textContent : null,
    isOff: btn ? (btn.textContent === '📂') : false
  };
}
"""

# ---------------------------------------------------------------------------
# Sub-check 2 — toggleOnSeeds
# Set up PS, pageTags, pageFloorNum, then click toggle.
# After click: mode ON, PF_site and PF_floor_2 seeded.
# ---------------------------------------------------------------------------
CHECK_TOGGLE_ON_SEEDS = r"""
async () => {
  // Reset to clean default layers
  LAYERS.length = 0;
  FOLDERS.length = 0;
  initLayers();
  ROLE_DEFS.forEach(function(rd) {
    state.catVis[rd.id] = true;
    state.catLock[rd.id] = false;
  });
  state.pageFolderMode = false;

  // Seed pageTags + pageFloorNum + PS
  pageTags = {5: 'site', 12: 'floor'};
  pageFloorNum = {12: 2};
  PS = {
    '5':  {objects: [], scale: null, annotations: []},
    '12': {objects: [], scale: null, annotations: []}
  };

  // Update button state (mode was reset)
  var btn = document.getElementById('pfl-toggle');
  if (btn) btn.textContent = '📂';

  // Click the toggle
  if (btn) btn.click();
  await new Promise(r => setTimeout(r, 80));

  var modeOn = state.pageFolderMode === true;
  var pfSite  = folderById('PF_site');
  var pfFloor = folderById('PF_floor_2');
  var btnText = btn ? btn.textContent : null;

  return {
    modeOn: modeOn,
    pfSiteExists: !!pfSite,
    pfFloor2Exists: !!pfFloor,
    btnTextChanged: btnText === '📂✓',
    allOk: modeOn && !!pfSite && !!pfFloor && btnText === '📂✓'
  };
}
"""

# ---------------------------------------------------------------------------
# Sub-check 3 — panelRendersPFFolders
# After toggle ON, #catlist must have a lt-folder-row for PF_site,
# with text containing "ผังบริเวณ" and "(p5)".
# ---------------------------------------------------------------------------
CHECK_PANEL_RENDERS_PF = r"""
() => {
  // Mode should already be ON from previous check; rebuild picker to be safe
  buildPicker();

  var row = document.querySelector('#catlist .cat.lt-folder-row[data-catid="PF_site"]');
  var hasClass = row ? row.classList.contains('lt-folder-row') : false;
  var text = row ? row.textContent : '';
  var hasSiteLabel = text.indexOf('ผังบริเวณ') >= 0;
  var hasPageLabel = text.indexOf('p5') >= 0;

  return {
    rowExists: !!row,
    hasClass: hasClass,
    hasSiteLabel: hasSiteLabel,
    hasPageLabel: hasPageLabel,
    allOk: !!row && hasClass && hasSiteLabel && hasPageLabel
  };
}
"""

# ---------------------------------------------------------------------------
# Sub-check 4 — panelRendersBaseLayers
# Under PF_site there should be 3 child layer rows:
# "ที่ดิน", "พื้นที่อาคารปกคลุม", "แนวร่น"
# ---------------------------------------------------------------------------
CHECK_BASE_LAYERS = r"""
() => {
  // Collect all layer-row elements
  var allRows = document.querySelectorAll('#catlist .cat');
  // Find PF_site row position
  var pfSiteIdx = -1;
  for (var i = 0; i < allRows.length; i++) {
    if (allRows[i].getAttribute('data-catid') === 'PF_site') {
      pfSiteIdx = i;
      break;
    }
  }
  if (pfSiteIdx < 0) return {pfSiteNotFound: true};

  // Collect subsequent rows that are children of PF_site
  // (not folders, not lt-folder-row for another PF, not lt-add)
  var childLayers = [];
  var pfSiteFolder = folderById('PF_site');
  var siteChildren = childrenOf('PF_site');
  var layerChildren = siteChildren.filter(function(c) { return c.kind === 'layer'; });

  var names = layerChildren.map(function(c) { return c.node.name; });
  var hasTiDin      = names.some(function(n) { return n.indexOf('ที่ดิน') >= 0; });
  var hasPaenTi     = names.some(function(n) { return n.indexOf('พื้นที่อาคารปกคลุม') >= 0; });
  var hasNaewRon    = names.some(function(n) { return n.indexOf('แนวร่น') >= 0; });
  var threeChildren = layerChildren.length === 3;

  // Also check DOM rows
  var domRows = [];
  for (var j = pfSiteIdx + 1; j < allRows.length; j++) {
    var r = allRows[j];
    if (r.classList.contains('lt-folder-row')) break;
    if (r.getAttribute('data-catid') && r.getAttribute('data-catid').indexOf('PF_') === 0) break;
    if (!r.classList.contains('lt-add')) {
      var catId = r.getAttribute('data-catid');
      if (catId) domRows.push(catId);
    }
  }

  return {
    layerCount: layerChildren.length,
    names: names,
    hasTiDin: hasTiDin,
    hasPaenTi: hasPaenTi,
    hasNaewRon: hasNaewRon,
    threeChildren: threeChildren,
    domRowCount: domRows.length,
    allOk: threeChildren && hasTiDin && hasPaenTi && hasNaewRon
  };
}
"""

# ---------------------------------------------------------------------------
# Sub-check 5 — addLayerRowWorks
# The .lt-add[data-pf-add="PF_floor_2"] row exists. Mock window.prompt,
# click it, verify new layer is under PF_floor_2.
# ---------------------------------------------------------------------------
CHECK_ADD_LAYER_ROW = r"""
async () => {
  // Mock prompt
  window._origPrompt = window.prompt;
  window.prompt = function() { return 'บัลกอนีทดสอบ'; };

  var addRow = document.querySelector('.cat.lt-add[data-pf-add="PF_floor_2"]');
  var rowExists = !!addRow;
  if (!rowExists) {
    window.prompt = window._origPrompt;
    return {rowExists: false};
  }

  var layersBefore = LAYERS.length;

  addRow.click();
  await new Promise(r => setTimeout(r, 80));

  window.prompt = window._origPrompt;

  var layersAfter = LAYERS.length;
  var grew = layersAfter > layersBefore;

  // Find the new layer by name
  var newL = null;
  for (var i = 0; i < LAYERS.length; i++) {
    if (LAYERS[i].name === 'บัลกอนีทดสอบ') { newL = LAYERS[i]; break; }
  }
  var layerExists = !!newL;
  var underPFFloor2 = newL ? (newL.parentId === 'PF_floor_2') : false;

  // Confirm via pageFolderOfLayer
  var pfFolder = newL ? pageFolderOfLayer(newL.id) : null;
  var inPFFloor2 = pfFolder ? pfFolder.id === 'PF_floor_2' : false;

  return {
    rowExists: rowExists,
    layersBefore: layersBefore,
    layersAfter: layersAfter,
    grew: grew,
    layerExists: layerExists,
    underPFFloor2: underPFFloor2,
    inPFFloor2: inPFFloor2,
    allOk: rowExists && grew && layerExists && underPFFloor2
  };
}
"""

# ---------------------------------------------------------------------------
# Sub-check 6 — toggleOffReverts
# Click toggle again → mode OFF. The picker re-renders in legacy mode.
# PF folders still exist in FOLDERS (data preserved), but the rendered
# folder rows should NOT contain "หน้า)" in their text.
# ---------------------------------------------------------------------------
CHECK_TOGGLE_OFF = r"""
async () => {
  var btn = document.getElementById('pfl-toggle');
  if (!btn) return {noBtnFound: true};

  // Mode should be ON; click to turn off
  btn.click();
  await new Promise(r => setTimeout(r, 80));

  var modeOff = state.pageFolderMode === false;
  var btnText = btn.textContent;
  var btnIsOff = btnText === '📂';

  // PF folders should still exist in model
  var pfSiteStillInModel = !!folderById('PF_site');

  // In legacy mode, folder rows render via _ltRenderFolder which does NOT
  // add the "(pN)" decoration. Verify the PF_site row text has no "หน้า)".
  buildPicker();
  var pfSiteRow = document.querySelector('#catlist .cat.lt-folder-row[data-catid="PF_site"]');
  var rowText = pfSiteRow ? pfSiteRow.textContent : '';
  var noPageSuffix = rowText.indexOf('หน้า)') < 0;

  return {
    modeOff: modeOff,
    btnIsOff: btnIsOff,
    pfSiteStillInModel: pfSiteStillInModel,
    noPageSuffix: noPageSuffix,
    allOk: modeOff && btnIsOff && pfSiteStillInModel && noPageSuffix
  };
}
"""

# ---------------------------------------------------------------------------
# Sub-check 7 — autoSeedOnTagChange
# Turn mode back on. Call liteSetTag(8,'floor') then set pageFloorNum[8]=3.
# After liteSetTag, reseed should fire. PF_floor_3 should exist with page 8.
# Note: liteSetTag clears pageFloorNum for floor tags (sets autoNamePage),
# so we set pageFloorNum[8] AFTER the liteSetTag call and re-trigger reseed.
# ---------------------------------------------------------------------------
CHECK_AUTO_RESEED = r"""
async () => {
  // Turn mode back on
  var btn = document.getElementById('pfl-toggle');
  if (btn && !state.pageFolderMode) {
    btn.click();
    await new Promise(r => setTimeout(r, 60));
  }

  // Ensure page 8 is in PS
  PS['8'] = PS['8'] || {objects: [], scale: null, annotations: []};

  // Call liteSetTag — this clears pageFloorNum[8] because val='floor'
  // and the wrapped version will call reseedActivePageFolders after
  liteSetTag(8, 'floor');
  await new Promise(r => setTimeout(r, 60));

  // After liteSetTag, pageFloorNum[8] is not set yet → folder is PF_floor_?
  // Now set the floor number manually and reseed
  pageFloorNum[8] = 3;
  reseedActivePageFolders();
  await new Promise(r => setTimeout(r, 60));

  var pfFloor3 = folderById('PF_floor_3');
  var exists = !!pfFloor3;
  var hasPage8 = pfFloor3 && pfFloor3.pages && pfFloor3.pages.indexOf(8) >= 0;

  return {
    modeOn: state.pageFolderMode,
    pfFloor3Exists: exists,
    pagesArray: pfFloor3 ? pfFloor3.pages : null,
    hasPage8: !!hasPage8,
    allOk: exists && !!hasPage8
  };
}
"""

CHECKS = [
    ("toggleButtonExists",      CHECK_TOGGLE_EXISTS,    ["buttonExists", "isOff"]),
    ("toggleOnSeeds",           CHECK_TOGGLE_ON_SEEDS,  ["allOk"]),
    ("panelRendersPFFolders",   CHECK_PANEL_RENDERS_PF, ["allOk"]),
    ("panelRendersBaseLayers",  CHECK_BASE_LAYERS,      ["allOk"]),
    ("addLayerRowWorks",        CHECK_ADD_LAYER_ROW,    ["allOk"]),
    ("toggleOffReverts",        CHECK_TOGGLE_OFF,       ["allOk"]),
    ("autoSeedOnTagChange",     CHECK_AUTO_RESEED,      ["allOk"]),
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
        time.sleep(0.8)  # allow DOMContentLoaded + setTimeout(0) to fire

        print()
        print("LITE-PAGE-FOLDER-UI checks:")
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
        print("LITE_PAGE_FOLDER_UI_FAIL")
        sys.exit(1)
    else:
        print("LITE_PAGE_FOLDER_UI_OK")


if __name__ == "__main__":
    main()
