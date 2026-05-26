"""
LPFL-1c / LFOC-1b: page-folder-layers UI regression guard.

Verifies page-folder mode (always ON after LFOC-1b), auto-seed, panel
render, add-layer row, togglePageFolderMode no-op for OFF, and tag-change
auto-reseed. All checks run in a single browser session.
No real PDF needed — PS is seeded via evaluate.

7 sub-checks:
  modeAlwaysOn          state.pageFolderMode===true on load; no #pfl-toggle button
  modeOnSeeds           seed PS/pageTags/pageFloorNum + reseedActivePageFolders()
                        → PF_site + PF_floor_2 seeded (no button click needed)
  panelRendersPFFolders lt-folder-row with data-catid="PF_site" in DOM,
                        text contains "ผังบริเวณ" and "(p5)"
  panelRendersBaseLayers 3 child layer rows under PF_site (LFOC-1c reverted: seeded default)
  addLayerRowWorks      .lt-add row click → new layer under PF_floor_2
  toggleOffIgnored      togglePageFolderMode(false) → mode stays ON (no revert)
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
# Sub-check 1 — modeAlwaysOn (LFOC-1b)
# After DOMContentLoaded, state.pageFolderMode must be true.
# No #pfl-toggle button should exist (removed in LFOC-1b).
# ---------------------------------------------------------------------------
CHECK_TOGGLE_EXISTS = r"""
() => {
  var btn = document.getElementById('pfl-toggle');
  return {
    buttonExists: !!btn,
    modeIsTrue: state.pageFolderMode === true,
    noToggleBtn: !btn
  };
}
"""

# ---------------------------------------------------------------------------
# Sub-check 2 — modeOnSeeds (LFOC-1b)
# Set up PS, pageTags, pageFloorNum, then call reseedActivePageFolders().
# Mode is already ON (no button click needed).
# After seed: PF_site and PF_floor_2 exist.
# ---------------------------------------------------------------------------
CHECK_TOGGLE_ON_SEEDS = r"""
async () => {
  // Reset to clean default layers (do NOT reset pageFolderMode — it stays true)
  LAYERS.length = 0;
  FOLDERS.length = 0;
  initLayers();
  ROLE_DEFS.forEach(function(rd) {
    state.catVis[rd.id] = true;
    state.catLock[rd.id] = false;
  });

  // Seed pageTags + pageFloorNum + PS
  pageTags = {5: 'site', 12: 'floor'};
  pageFloorNum = {12: 2};
  PS = {
    '5':  {objects: [], scale: null, annotations: []},
    '12': {objects: [], scale: null, annotations: []}
  };

  // LFOC-1b: mode is already ON — just reseed directly
  reseedActivePageFolders();
  buildPicker();
  await new Promise(r => setTimeout(r, 80));

  var modeOn = state.pageFolderMode === true;
  var pfSite  = folderById('PF_site');
  var pfFloor = folderById('PF_floor_2');

  return {
    modeOn: modeOn,
    pfSiteExists: !!pfSite,
    pfFloor2Exists: !!pfFloor,
    allOk: modeOn && !!pfSite && !!pfFloor
  };
}
"""

# ---------------------------------------------------------------------------
# Sub-check 3 — panelRendersPFFolders
# After mode ON, #catlist must have a lt-folder-row for PF_site,
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
# LFOC-1c reverted: PF_site has 3 seeded child layers.
# Verify PF_site exists in DOM and childrenOf() returns 3 layer children.
# ---------------------------------------------------------------------------
CHECK_BASE_LAYERS = r"""
() => {
  var allRows = document.querySelectorAll('#catlist .cat');
  // Find PF_site row position
  var pfSiteIdx = -1;
  for (var i = 0; i < allRows.length; i++) {
    if (allRows[i].getAttribute('data-catid') === 'PF_site') {
      pfSiteIdx = i;
      break;
    }
  }
  if (pfSiteIdx < 0) return {pfSiteNotFound: true, allOk: false};

  // LFOC-1c reverted: 3 base layers seeded — childrenOf PF_site returns 3 layer children
  var siteChildren = childrenOf('PF_site');
  var layerChildren = siteChildren.filter(function(c) { return c.kind === 'layer'; });
  var threeChildren = layerChildren.length === 3;

  var names = layerChildren.map(function(c) { return c.node.name; });
  var hasTiDin   = names.some(function(n) { return n.indexOf('ที่ดิน') >= 0; });
  var hasPaenTi  = names.some(function(n) { return n.indexOf('พื้นที่อาคารปกคลุม') >= 0; });
  var hasNaewRon = names.some(function(n) { return n.indexOf('แนวร่น') >= 0; });

  return {
    layerCount: layerChildren.length,
    threeChildren: threeChildren,
    hasTiDin: hasTiDin,
    hasPaenTi: hasPaenTi,
    hasNaewRon: hasNaewRon,
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
# Sub-check 6 — toggleOffIgnored (LFOC-1b)
# LFOC-1b: calling togglePageFolderMode(false) must keep mode ON (no flat mode).
# PF folders still exist in model. Picker still renders PF decoration.
# No toggle button expected.
# ---------------------------------------------------------------------------
CHECK_TOGGLE_OFF = r"""
async () => {
  // Attempt to force OFF via togglePageFolderMode — must be ignored
  togglePageFolderMode(false);
  await new Promise(r => setTimeout(r, 80));

  var modeStillOn = state.pageFolderMode === true;

  // PF folders should still exist in model
  var pfSiteStillInModel = !!folderById('PF_site');

  // In PF mode, the picker renders page decoration "(pN)" — verify it is still there
  buildPicker();
  var pfSiteRow = document.querySelector('#catlist .cat.lt-folder-row[data-catid="PF_site"]');
  var rowText = pfSiteRow ? pfSiteRow.textContent : '';
  // "(p5)" should still be present (PF mode active)
  var hasPageDecoration = rowText.indexOf('p5') >= 0;

  // No toggle button exists
  var noBtn = !document.getElementById('pfl-toggle');

  return {
    modeStillOn: modeStillOn,
    pfSiteStillInModel: pfSiteStillInModel,
    hasPageDecoration: hasPageDecoration,
    noBtn: noBtn,
    allOk: modeStillOn && pfSiteStillInModel && hasPageDecoration && noBtn
  };
}
"""

# ---------------------------------------------------------------------------
# Sub-check 7 — autoSeedOnTagChange
# LFOC-1b: mode is always ON. No button click needed.
# Call liteSetTag(8,'floor') then set pageFloorNum[8]=3.
# After liteSetTag, reseed should fire. PF_floor_3 should exist with page 8.
# Note: liteSetTag clears pageFloorNum for floor tags (sets autoNamePage),
# so we set pageFloorNum[8] AFTER the liteSetTag call and re-trigger reseed.
# ---------------------------------------------------------------------------
CHECK_AUTO_RESEED = r"""
async () => {
  // LFOC-1b: mode is always ON, no button click needed
  // Ensure page 8 is in PS
  PS['8'] = PS['8'] || {objects: [], scale: null, annotations: []};

  // Call liteSetTag — the wrapped version calls reseedActivePageFolders after
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
    ("modeAlwaysOn",            CHECK_TOGGLE_EXISTS,    ["modeIsTrue", "noToggleBtn"]),
    ("modeOnSeeds",             CHECK_TOGGLE_ON_SEEDS,  ["allOk"]),
    ("panelRendersPFFolders",   CHECK_PANEL_RENDERS_PF, ["allOk"]),
    ("panelRendersBaseLayers",  CHECK_BASE_LAYERS,      ["allOk"]),
    ("addLayerRowWorks",        CHECK_ADD_LAYER_ROW,    ["allOk"]),
    ("toggleOffIgnored",        CHECK_TOGGLE_OFF,       ["allOk"]),
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
