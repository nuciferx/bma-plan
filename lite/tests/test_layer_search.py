"""
INV-2026-07-04-001 slice 2/3: global floor/layer search + result-cap UX —
regression guard.

Verifies the search row mounted above the floor-rail (layer-scope.js):
case-insensitive substring match over PF folder names + layer names,
grouped by containing PF folder (kind-aware order), capped at 30 shown
with a real-total badge when truncated, click-to-jump (folder or layer
result) reusing the rail's _lsGoTo()/loadPage() path, and a transient
highlight on the target layer row once it re-renders.

5 checks:
  folderNameSearchJumps     query "57" -> PF_floor_57 folder result
                            present; clicking it calls loadPage(6)
                            (PF_floor_57.pages[0]); curPage becomes 6;
                            catlist re-scopes to PF_floor_57 only
  commonLayerNameGroups     query "ลิฟต์" (a layer name seeded on every
                            normal/basement floor) across 4 seeded
                            floors -> >=3 distinct result groups
  capAndBadgeShowRealTotal  query matching 35 seeded floors' gfa layers
                            -> exactly 30 result rows shown, badge text
                            contains "35" (the real, untruncated total)
  layerResultHighlights     click a layer result -> after navigation +
                            re-render, that layer's row in #catlist
                            carries the "ls-search-hl" class
  clearedQueryHidesDropdown typing then clearing the query -> results
                            dropdown hidden + empty, no page errors

Emits LITE_LAYER_SEARCH_OK on success.

    py -3 lite/tests/test_layer_search.py
"""
import socket, threading, time, sys
from pathlib import Path

LITE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LITE))
import uvicorn
from playwright.sync_api import sync_playwright


def _free_port(start=8460):
    for p in range(start, start + 60):
        with socket.socket() as s:
            if s.connect_ex(("127.0.0.1", p)) != 0:
                return p
    raise RuntimeError("no free port")


def _reset():
    return r"""
  LAYERS.length = 0;
  FOLDERS.length = 0;
  initLayers();
  ROLE_DEFS.forEach(function(rd) {
    state.catVis[rd.id] = true;
    state.catLock[rd.id] = false;
  });
  if (!state.folderCollapsed) state.folderCollapsed = {};
  state.pageFolderMode = true;
  state.scopeByPage = true;
"""


def _sleep_js(ms):
    return "await new Promise(function(r) { setTimeout(r, %d); });" % ms


# ---------------------------------------------------------------------------
# Check 1 — folderNameSearchJumps
# 3 floors: page5->floor1, page6->floor57, page7->roof. curPage=5.
# Search "57" -> PF_floor_57 folder result. Click it (mousedown, stubbed
# loadPage) -> loadPage(6) called, curPage=6, catlist scoped to PF_floor_57.
# ---------------------------------------------------------------------------
CHECK_FOLDER_SEARCH = _reset() + r"""
  pageTags      = {5: 'floor', 6: 'floor', 7: 'floor'};
  pageFloorNum  = {5: 1, 6: 57, 7: 'roof'};
  pageFloorKind = {5: 'normal', 6: 'normal', 7: 'rooftop'};
  PS = {
    '5': {objects: [], scale: null, annotations: []},
    '6': {objects: [], scale: null, annotations: []},
    '7': {objects: [], scale: null, annotations: []}
  };
  pageCount = 7;
  reseedActivePageFolders();
  curPage = 5;
  buildPicker();
""" + _sleep_js(100) + r"""

  window._origLoadPage = loadPage;
  var calledWith = null;
  loadPage = function(n) { calledWith = n; curPage = n; afterPage(); return Promise.resolve(); };

  var input = document.getElementById('ls-search-input');
  input.value = '57';
  input.dispatchEvent(new Event('input', {bubbles: true}));
""" + _sleep_js(220) + r"""

  var resultRow = document.querySelector('.ls-search-result[data-ls-id="PF_floor_57"]');
  var groupPresent = !!resultRow;
  if (resultRow) resultRow.dispatchEvent(new MouseEvent('mousedown', {bubbles: true}));
""" + _sleep_js(80) + r"""

  loadPage = window._origLoadPage;

  var curPageCorrect = curPage === 6;
  var scopedToFloor57 = !!document.querySelector('[data-catid="PF_floor_57"]')
                      && !document.querySelector('[data-catid="PF_floor_1"]');

  return {
    groupPresent: groupPresent,
    calledWith: calledWith,
    curPageCorrect: curPageCorrect,
    scopedToFloor57: scopedToFloor57,
    allOk: groupPresent && calledWith === 6 && curPageCorrect && scopedToFloor57
  };
"""

# ---------------------------------------------------------------------------
# Check 2 — commonLayerNameGroups
# 3 normal floors (each auto-seeds "หักช่องลิฟต์") + 1 basement (also
# auto-seeds "หักช่องลิฟต์"). Query "ลิฟต์" -> >=3 distinct groups.
# ---------------------------------------------------------------------------
CHECK_COMMON_NAME = _reset() + r"""
  pageTags      = {10: 'floor', 11: 'floor', 12: 'floor', 13: 'floor'};
  pageFloorNum  = {10: 1, 11: 2, 12: 3, 13: 1};
  pageFloorKind = {10: 'normal', 11: 'normal', 12: 'normal', 13: 'basement'};
  PS = {
    '10': {objects: [], scale: null, annotations: []},
    '11': {objects: [], scale: null, annotations: []},
    '12': {objects: [], scale: null, annotations: []},
    '13': {objects: [], scale: null, annotations: []}
  };
  pageCount = 13;
  reseedActivePageFolders();
  curPage = 10;
  buildPicker();
""" + _sleep_js(100) + r"""

  var input = document.getElementById('ls-search-input');
  input.value = 'ลิฟต์';
  input.dispatchEvent(new Event('input', {bubbles: true}));
""" + _sleep_js(220) + r"""

  var headers = document.querySelectorAll('.ls-search-group-header');
  var groupCount = headers.length;

  return {
    groupCount: groupCount,
    allOk: groupCount >= 3
  };
"""

# ---------------------------------------------------------------------------
# Check 3 — capAndBadgeShowRealTotal
# 35 normal floors, each auto-seeds a "GFA ชั้น <n>" layer (roof/basement
# also contain that substring but none seeded here) -> exactly 35 matches.
# ---------------------------------------------------------------------------
CHECK_CAP_BADGE = _reset() + r"""
  pageTags = {}; pageFloorNum = {}; pageFloorKind = {}; PS = {};
  for (var i = 1; i <= 35; i++) {
    pageTags[i] = 'floor';
    pageFloorNum[i] = i;
    pageFloorKind[i] = 'normal';
    PS[String(i)] = {objects: [], scale: null, annotations: []};
  }
  pageCount = 35;
  reseedActivePageFolders();
  curPage = 1;
  buildPicker();
""" + _sleep_js(150) + r"""

  var input = document.getElementById('ls-search-input');
  input.value = 'GFA ชั้น';
  input.dispatchEvent(new Event('input', {bubbles: true}));
""" + _sleep_js(250) + r"""

  var rows = document.querySelectorAll('.ls-search-result');
  var shownCount = rows.length;
  var badge = document.querySelector('.ls-search-badge');
  var badgeText = badge ? badge.textContent : '';
  var badgeHas35 = badgeText.indexOf('35') !== -1;
  // ASCII-only echo for console-safe printing (raw Thai badgeText breaks
  // Windows cp1252 stdout) -- ASCII digits/punctuation only.
  var badgeAscii = badgeText.replace(/[^\x00-\x7F]/g, '');

  return {
    shownCount: shownCount,
    badgeAscii: badgeAscii,
    badgeHas35: badgeHas35,
    allOk: shownCount === 30 && badgeHas35
  };
"""

# ---------------------------------------------------------------------------
# Check 4 — layerResultHighlights
# 3 normal floors, each seeds "หักช่องลิฟต์". Click the layer result for
# floor 2's copy -> after (stubbed) navigation + re-render, that layer's
# row carries "ls-search-hl".
# ---------------------------------------------------------------------------
CHECK_HIGHLIGHT = _reset() + r"""
  pageTags      = {5: 'floor', 6: 'floor', 7: 'floor'};
  pageFloorNum  = {5: 1, 6: 2, 7: 3};
  pageFloorKind = {5: 'normal', 6: 'normal', 7: 'normal'};
  PS = {
    '5': {objects: [], scale: null, annotations: []},
    '6': {objects: [], scale: null, annotations: []},
    '7': {objects: [], scale: null, annotations: []}
  };
  pageCount = 7;
  reseedActivePageFolders();
  curPage = 5;
  buildPicker();
""" + _sleep_js(100) + r"""

  window._origLoadPage = loadPage;
  loadPage = function(n) { curPage = n; afterPage(); return Promise.resolve(); };

  var input = document.getElementById('ls-search-input');
  input.value = 'หักช่องลิฟต์';
  input.dispatchEvent(new Event('input', {bubbles: true}));
""" + _sleep_js(220) + r"""

  var layerRows = document.querySelectorAll('.ls-search-result[data-ls-type="layer"]');
  var target = null;
  for (var i = 0; i < layerRows.length; i++) {
    var folder = pageFolderOfLayer(layerRows[i].getAttribute('data-ls-id'));
    if (folder && folder.id === 'PF_floor_2') { target = layerRows[i]; break; }
  }
  var targetFound = !!target;
  var targetLayerId = target ? target.getAttribute('data-ls-id') : null;
  if (target) target.dispatchEvent(new MouseEvent('mousedown', {bubbles: true}));
""" + _sleep_js(100) + r"""

  loadPage = window._origLoadPage;

  var row = targetLayerId ? document.querySelector('[data-catid="' + targetLayerId + '"]') : null;
  var highlighted = !!(row && row.classList.contains('ls-search-hl'));

  return {
    targetFound: targetFound,
    curPage: curPage,
    rowFound: !!row,
    highlighted: highlighted,
    allOk: targetFound && curPage === 6 && highlighted
  };
"""

# ---------------------------------------------------------------------------
# Check 5 — clearedQueryHidesDropdown
# ---------------------------------------------------------------------------
CHECK_CLEARED = _reset() + r"""
  pageTags = {5: 'floor'}; pageFloorNum = {5: 1}; pageFloorKind = {5: 'normal'};
  PS = {'5': {objects: [], scale: null, annotations: []}};
  pageCount = 5;
  reseedActivePageFolders();
  curPage = 5;
  buildPicker();
""" + _sleep_js(100) + r"""

  var input = document.getElementById('ls-search-input');
  input.value = 'ชั้น';
  input.dispatchEvent(new Event('input', {bubbles: true}));
""" + _sleep_js(220) + r"""

  var results = document.getElementById('ls-search-results');
  var shownWhileTyping = results.style.display !== 'none';

  input.value = '';
  input.dispatchEvent(new Event('input', {bubbles: true}));
""" + _sleep_js(220) + r"""

  var hiddenAfterClear = results.style.display === 'none';
  var emptyAfterClear = results.innerHTML === '';

  return {
    shownWhileTyping: shownWhileTyping,
    hiddenAfterClear: hiddenAfterClear,
    emptyAfterClear: emptyAfterClear,
    allOk: shownWhileTyping && hiddenAfterClear && emptyAfterClear
  };
"""

CHECKS = [
    ("folderNameSearchJumps",     CHECK_FOLDER_SEARCH, ["allOk"]),
    ("commonLayerNameGroups",     CHECK_COMMON_NAME,   ["allOk"]),
    ("capAndBadgeShowRealTotal",  CHECK_CAP_BADGE,      ["allOk"]),
    ("layerResultHighlights",     CHECK_HIGHLIGHT,      ["allOk"]),
    ("clearedQueryHidesDropdown", CHECK_CLEARED,        ["allOk"]),
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
        time.sleep(0.8)  # allow DOMContentLoaded + setTimeout(0) auto-seed to fire

        print()
        print("LITE-LAYER-SEARCH checks:")
        for name, scenario, required_keys in CHECKS:
            wrapped = "async () => {\n" + scenario + "\n}"
            try:
                result = pg.evaluate(wrapped)
            except Exception as ex:
                print(f"  {name:32s} -> EXCEPTION: {ex}")
                failures.append(f"check '{name}' threw: {ex}")
                continue

            ok = all(result.get(k) is True for k in required_keys)
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
        print("LITE_LAYER_SEARCH_FAIL")
        sys.exit(1)
    else:
        print("LITE_LAYER_SEARCH_OK")


if __name__ == "__main__":
    main()
