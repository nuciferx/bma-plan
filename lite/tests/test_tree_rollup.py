"""
LITE-TREE-ROLLUP regression guard (LST-3b sprint).

Verifies that the folder Σ roll-up and layer own-area displays work correctly
in the tree picker. Uses real _ltOwnArea / rollupArea / buildPicker — does NOT
re-implement area math.

Required checks (spec LST-3b):
  folderRollupEqualsDescendantSum  folder with 2 gfa + 1 ded; rollupArea === sum of descendants AND finite
  dedContributesNegative           _ltOwnArea(ded) < 0, _ltOwnArea(gfa) > 0 for equal polys
  rollupShownOnFolderRow           folder row DOM contains .lt-area with "Σ"
  layerRowShowsOwnNotRollup        layer row .lt-area === _ltOwnArea(parentLayer) (excludes child)
  liveUpdateOnAddObject            capture folder Σ; push poly to descendant; rebuild; Σ grows
  emptyFolderNoCrash               empty folder → rollupArea===0, no lt-area, no throw
  areaSpanDoesNotBlockClicks       .lt-area has pointer-events:none; eye toggle still works

Emits LITE_TREE_ROLLUP_OK on success.

    py -3 lite/tests/test_tree_rollup.py
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
# Helper: set up a clean state with a known page scale (10 pts_per_m) so
# polyMetrics returns real numbers. Used by most scenarios via in-page setup.
# A unit square in PDF points at 10 pts/m → area = (1/10)² = 0.01 m²
# A 10×10 square in PDF points → area = 1.0 m²
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Scenario 1 — folderRollupEqualsDescendantSum
# Folder F with 2 gfa-role layers (g1,g2, 1 poly each = 1.0 m² each) and
# 1 ded layer (d1, 1 poly = 1.0 m²). ded contributes −1.0 to roll-up.
# Expected rollup = 1.0 + 1.0 + (−1.0) = 1.0 m²
# Check: rollupArea(F.id, _ltOwnArea) === _ltOwnArea(g1)+_ltOwnArea(g2)+_ltOwnArea(d1)
# AND the result is finite.
# ---------------------------------------------------------------------------
FOLDER_ROLLUP_EQUALS_DESCENDANT_SUM = r"""
() => {
  // Clean state
  LAYERS.length = 0;
  FOLDERS.length = 0;
  initLayers();
  ROLE_DEFS.forEach(function(rd) { state.catVis[rd.id] = true; state.catLock[rd.id] = false; });

  // Page scale: 10 pts per metre
  PS['1'] = { scale: { pts_per_m: 10 }, objects: [], annotations: [] };

  // Add folder F
  const F = addFolder('RollupFolder', '#aabbcc', null);
  F.order = -1;
  state.catVis[F.id] = true;
  state.catLock[F.id] = false;

  // Two custom gfa layers nested under F
  const g1 = addLayer('gfa', 'GFA1', '#4c8dff');
  g1.parentId = F.id;
  state.catVis[g1.id] = true;
  state.catLock[g1.id] = false;

  const g2 = addLayer('gfa', 'GFA2', '#1155aa');
  g2.parentId = F.id;
  state.catVis[g2.id] = true;
  state.catLock[g2.id] = false;

  // One custom ded layer nested under F
  const d1 = addLayer('ded', 'DED1', '#ff6b6b');
  d1.parentId = F.id;
  state.catVis[d1.id] = true;
  state.catLock[d1.id] = false;

  // 10×10 square at PDF pts → area = (10×10/2) via shoelace = 100 pt²;
  // at 10 pts/m → 100/100 = 1.0 m²
  const sq = [
    {x:0,y:0},{x:10,y:0},{x:10,y:10},{x:0,y:10}
  ];
  PS['1'].objects.push({id:1001, catId:g1.id, kind:'poly', pts:sq, dimVisible:true, counting:false, semanticTag:'gross_floor_area'});
  PS['1'].objects.push({id:1002, catId:g2.id, kind:'poly', pts:sq, dimVisible:true, counting:false, semanticTag:'gross_floor_area'});
  PS['1'].objects.push({id:1003, catId:d1.id, kind:'poly', pts:sq, dimVisible:true, counting:false, semanticTag:'deduction_opening'});

  const ownG1 = _ltOwnArea(g1.id);   // +1.0
  const ownG2 = _ltOwnArea(g2.id);   // +1.0
  const ownD1 = _ltOwnArea(d1.id);   // -1.0

  const sumDescendants = ownG1 + ownG2 + ownD1;  // 1.0
  const rollF = rollupArea(F.id, _ltOwnArea);     // should also be 1.0

  // allow floating-point tolerance
  const diff = Math.abs(rollF - sumDescendants);
  const equalsDescendantSum = diff < 1e-9;
  const resultIsFinite = isFinite(rollF);

  return {
    ownG1, ownG2, ownD1, sumDescendants, rollF,
    equalsDescendantSum,
    resultIsFinite,
    ok: equalsDescendantSum && resultIsFinite
  };
}
"""

# ---------------------------------------------------------------------------
# Scenario 2 — dedContributesNegative
# A ded-role layer with a 10×10 square → _ltOwnArea < 0.
# A gfa-role layer with the same poly → _ltOwnArea > 0.
# ---------------------------------------------------------------------------
DED_CONTRIBUTES_NEGATIVE = r"""
() => {
  LAYERS.length = 0;
  FOLDERS.length = 0;
  initLayers();

  PS['1'] = { scale: { pts_per_m: 10 }, objects: [], annotations: [] };

  const sq = [{x:0,y:0},{x:10,y:0},{x:10,y:10},{x:0,y:10}];

  const gLyr = layerById('gfa');  // default gfa layer
  const dLyr = layerById('ded');  // default ded layer

  PS['1'].objects.push({id:2001, catId:'gfa', kind:'poly', pts:sq, dimVisible:true, counting:false, semanticTag:'gross_floor_area'});
  PS['1'].objects.push({id:2002, catId:'ded', kind:'poly', pts:sq, dimVisible:true, counting:false, semanticTag:'deduction_opening'});

  const ownGfa = _ltOwnArea('gfa');
  const ownDed = _ltOwnArea('ded');

  return {
    ownGfa,
    ownDed,
    gfaPositive: ownGfa > 0,
    dedNegative: ownDed < 0,
    sameAbsValue: Math.abs(Math.abs(ownGfa) - Math.abs(ownDed)) < 1e-9,
    ok: ownGfa > 0 && ownDed < 0
  };
}
"""

# ---------------------------------------------------------------------------
# Scenario 3 — rollupShownOnFolderRow
# Folder with a gfa layer that has an object → after buildPicker the folder
# row must contain a .lt-area span whose text includes "Σ".
# ---------------------------------------------------------------------------
ROLLUP_SHOWN_ON_FOLDER_ROW = r"""
() => {
  LAYERS.length = 0;
  FOLDERS.length = 0;
  initLayers();
  ROLE_DEFS.forEach(function(rd) { state.catVis[rd.id] = true; state.catLock[rd.id] = false; });

  PS['1'] = { scale: { pts_per_m: 10 }, objects: [], annotations: [] };

  const F = addFolder('ShowFolder', '#aabbcc', null);
  F.order = -1;
  state.catVis[F.id] = true;
  state.catLock[F.id] = false;

  const gfa = layerById('gfa');
  gfa.parentId = F.id;

  const sq = [{x:0,y:0},{x:10,y:0},{x:10,y:10},{x:0,y:10}];
  PS['1'].objects.push({id:3001, catId:'gfa', kind:'poly', pts:sq, dimVisible:true, counting:false, semanticTag:'gross_floor_area'});

  buildPicker();

  const folderRow = document.querySelector('[data-catid="' + F.id + '"]');
  if (!folderRow) return {no_folder_row: true};

  const areaSpan = folderRow.querySelector('.lt-area');
  const hasSigma = areaSpan ? areaSpan.textContent.includes('Σ') : false;  // Σ

  // cleanup
  gfa.parentId = null;

  return {
    folderRowPresent: !!folderRow,
    areaSpanPresent: !!areaSpan,
    areaText: areaSpan ? areaSpan.textContent : '',
    hasSigma,
    ok: !!folderRow && !!areaSpan && hasSigma
  };
}
"""

# ---------------------------------------------------------------------------
# Scenario 4 — layerRowShowsOwnNotRollup
# A parent layer P has a poly on page 1 (1.0 m²).
# A child layer C (nested under P) has a poly on page 1 (1.0 m²).
# P's layer row .lt-area must show _ltOwnArea(P) = 1.0 m², NOT the rollup (2.0 m²).
# ---------------------------------------------------------------------------
LAYER_ROW_SHOWS_OWN_NOT_ROLLUP = r"""
() => {
  LAYERS.length = 0;
  FOLDERS.length = 0;
  initLayers();
  ROLE_DEFS.forEach(function(rd) { state.catVis[rd.id] = true; state.catLock[rd.id] = false; });

  PS['1'] = { scale: { pts_per_m: 10 }, objects: [], annotations: [] };

  const P = addLayer('gfa', 'ParentLayer', '#4c8dff');
  state.catVis[P.id] = true;
  state.catLock[P.id] = false;

  const C = addLayer('gfa', 'ChildLayer', '#1155aa');
  C.parentId = P.id;
  state.catVis[C.id] = true;
  state.catLock[C.id] = false;

  const sq = [{x:0,y:0},{x:10,y:0},{x:10,y:10},{x:0,y:10}];
  PS['1'].objects.push({id:4001, catId:P.id, kind:'poly', pts:sq, dimVisible:true, counting:false, semanticTag:'gross_floor_area'});
  PS['1'].objects.push({id:4002, catId:C.id, kind:'poly', pts:sq, dimVisible:true, counting:false, semanticTag:'gross_floor_area'});

  buildPicker();

  const ownP = _ltOwnArea(P.id);            // 1.0
  const rollP = rollupArea(P.id, _ltOwnArea); // 2.0 (P own + C own)

  const pRow = document.querySelector('[data-catid="' + P.id + '"]');
  if (!pRow) return {no_p_row: true};
  const areaSpan = pRow.querySelector('.lt-area');

  // The span text must match ownP (1.0 m²), not rollP (2.0 m²)
  // We check: the displayed number rounded to 2dp matches ownP.toFixed(2)
  var spanText = areaSpan ? areaSpan.textContent : '';
  var ownFormatted = ownP.toLocaleString(undefined, {maximumFractionDigits: 2});
  var rollFormatted = rollP.toLocaleString(undefined, {maximumFractionDigits: 2});

  // span should contain ownFormatted but the span text ≠ sigma rollFormatted
  var containsOwnValue = areaSpan && spanText.includes(ownFormatted);
  // NOT showing sigma (sigma would mean rollup, which belongs only to folders)
  var noSigma = areaSpan ? !spanText.includes('Σ') : true;

  return {
    ownP, rollP,
    spanText,
    ownFormatted, rollFormatted,
    areaSpanPresent: !!areaSpan,
    containsOwnValue,
    noSigma,
    ok: !!areaSpan && containsOwnValue && noSigma
  };
}
"""

# ---------------------------------------------------------------------------
# Scenario 5 — liveUpdateOnAddObject
# Build folder with 1 gfa poly (1.0 m²). Capture folder Σ (= 1.0).
# Push another poly to the same gfa layer. Rebuild. Σ should be 2.0.
# ---------------------------------------------------------------------------
LIVE_UPDATE_ON_ADD_OBJECT = r"""
async () => {
  LAYERS.length = 0;
  FOLDERS.length = 0;
  initLayers();
  ROLE_DEFS.forEach(function(rd) { state.catVis[rd.id] = true; state.catLock[rd.id] = false; });

  PS['1'] = { scale: { pts_per_m: 10 }, objects: [], annotations: [] };

  const F = addFolder('LiveFolder', '#aabbcc', null);
  F.order = -1;
  state.catVis[F.id] = true;
  state.catLock[F.id] = false;

  const gfa = layerById('gfa');
  gfa.parentId = F.id;

  const sq = [{x:0,y:0},{x:10,y:0},{x:10,y:10},{x:0,y:10}];
  PS['1'].objects.push({id:5001, catId:'gfa', kind:'poly', pts:sq, dimVisible:true, counting:false, semanticTag:'gross_floor_area'});

  buildPicker();

  // Capture folder Σ before
  const rollBefore = rollupArea(F.id, _ltOwnArea);
  const folderRowBefore = document.querySelector('[data-catid="' + F.id + '"]');
  const spanBefore = folderRowBefore ? folderRowBefore.querySelector('.lt-area') : null;
  const textBefore = spanBefore ? spanBefore.textContent : '';

  // Add another poly object to gfa layer
  PS['1'].objects.push({id:5002, catId:'gfa', kind:'poly', pts:sq, dimVisible:true, counting:false, semanticTag:'gross_floor_area'});

  // Rebuild
  buildPicker();
  await new Promise(r => setTimeout(r, 30));

  const rollAfter = rollupArea(F.id, _ltOwnArea);
  const folderRowAfter = document.querySelector('[data-catid="' + F.id + '"]');
  const spanAfter = folderRowAfter ? folderRowAfter.querySelector('.lt-area') : null;
  const textAfter = spanAfter ? spanAfter.textContent : '';

  // cleanup
  gfa.parentId = null;

  return {
    rollBefore, rollAfter,
    textBefore, textAfter,
    increasedCorrectly: Math.abs(rollAfter - rollBefore * 2) < 1e-9,
    domUpdated: textBefore !== textAfter,
    ok: rollAfter > rollBefore && Math.abs(rollAfter - rollBefore * 2) < 1e-9
  };
}
"""

# ---------------------------------------------------------------------------
# Scenario 6 — emptyFolderNoCrash
# Folder with no objects (no descendants). rollupArea===0, .lt-area absent.
# buildPicker must not throw.
# ---------------------------------------------------------------------------
EMPTY_FOLDER_NO_CRASH = r"""
() => {
  LAYERS.length = 0;
  FOLDERS.length = 0;
  initLayers();
  ROLE_DEFS.forEach(function(rd) { state.catVis[rd.id] = true; state.catLock[rd.id] = false; });

  PS['1'] = { scale: { pts_per_m: 10 }, objects: [], annotations: [] };

  const F = addFolder('EmptyFolder', '#aabbcc', null);
  F.order = -1;
  state.catVis[F.id] = true;
  state.catLock[F.id] = false;

  var threw = false;
  try {
    buildPicker();
  } catch(e) {
    threw = true;
  }

  const roll = rollupArea(F.id, _ltOwnArea);
  const folderRow = document.querySelector('[data-catid="' + F.id + '"]');
  const areaSpan = folderRow ? folderRow.querySelector('.lt-area') : null;

  return {
    threw,
    roll,
    rollIsZero: roll === 0,
    noAreaSpan: !areaSpan,
    ok: !threw && roll === 0 && !areaSpan
  };
}
"""

# ---------------------------------------------------------------------------
# Scenario 7 — areaSpanDoesNotBlockClicks
# Folder with a gfa poly → Σ span exists. Assert:
#   (a) computed style pointer-events = "none"
#   (b) clicking the eye button on a folder row that has a Σ span still works
#       (eye toggle changes catVis state).
# ---------------------------------------------------------------------------
AREA_SPAN_NO_BLOCK_CLICKS = r"""
async () => {
  LAYERS.length = 0;
  FOLDERS.length = 0;
  initLayers();
  ROLE_DEFS.forEach(function(rd) { state.catVis[rd.id] = true; state.catLock[rd.id] = false; });

  PS['1'] = { scale: { pts_per_m: 10 }, objects: [], annotations: [] };

  const F = addFolder('ClickFolder', '#aabbcc', null);
  F.order = -1;
  state.catVis[F.id] = true;
  state.catLock[F.id] = false;

  const gfa = layerById('gfa');
  gfa.parentId = F.id;

  const sq = [{x:0,y:0},{x:10,y:0},{x:10,y:10},{x:0,y:10}];
  PS['1'].objects.push({id:7001, catId:'gfa', kind:'poly', pts:sq, dimVisible:true, counting:false, semanticTag:'gross_floor_area'});

  buildPicker();

  const folderRow = document.querySelector('[data-catid="' + F.id + '"]');
  if (!folderRow) return {no_folder_row: true};

  const areaSpan = folderRow.querySelector('.lt-area');
  if (!areaSpan) return {no_area_span: true};

  // (a) pointer-events must be "none"
  const pe = window.getComputedStyle(areaSpan).pointerEvents;
  const pointerEventsNone = pe === 'none';

  // (b) eye toggle still works
  const visBefore = state.catVis[F.id];
  const eyeBtn = folderRow.querySelector('[data-eye="' + F.id + '"]');
  if (!eyeBtn) return {no_eye_btn: true};

  eyeBtn.click();
  await new Promise(r => setTimeout(r, 50));

  const visAfter = state.catVis[F.id];
  const eyeToggled = visBefore !== visAfter;

  // cleanup
  gfa.parentId = null;
  state.catVis[F.id] = true;

  return {
    pointerEventsStyle: pe,
    pointerEventsNone,
    visBefore, visAfter,
    eyeToggled,
    ok: pointerEventsNone && eyeToggled
  };
}
"""

CHECKS = [
    ("folderRollupEqualsDescendantSum", FOLDER_ROLLUP_EQUALS_DESCENDANT_SUM,  ["ok"]),
    ("dedContributesNegative",          DED_CONTRIBUTES_NEGATIVE,             ["ok"]),
    ("rollupShownOnFolderRow",          ROLLUP_SHOWN_ON_FOLDER_ROW,           ["ok"]),
    ("layerRowShowsOwnNotRollup",       LAYER_ROW_SHOWS_OWN_NOT_ROLLUP,       ["ok"]),
    ("liveUpdateOnAddObject",           LIVE_UPDATE_ON_ADD_OBJECT,            ["ok"]),
    ("emptyFolderNoCrash",              EMPTY_FOLDER_NO_CRASH,                ["ok"]),
    ("areaSpanDoesNotBlockClicks",      AREA_SPAN_NO_BLOCK_CLICKS,            ["ok"]),
]


def _safe_print(msg: str) -> None:
    """Print a string, replacing unencodable characters for Windows consoles."""
    try:
        print(msg)
    except UnicodeEncodeError:
        print(msg.encode(sys.stdout.encoding or "ascii", errors="replace").decode(sys.stdout.encoding or "ascii"))


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

        _safe_print("")
        _safe_print("LITE-TREE-ROLLUP checks:")
        for name, scenario, required_keys in CHECKS:
            try:
                result = pg.evaluate(scenario)
            except Exception as ex:
                _safe_print(f"  {name:45s} -> EXCEPTION: {ex}")
                failures.append(f"check '{name}' threw: {ex}")
                continue

            ok = all(result.get(k) is True for k in required_keys)
            status = "PASS" if ok else "FAIL"
            # Sanitise result repr for Windows consoles
            result_str = str(result).encode(sys.stdout.encoding or "ascii", errors="replace").decode(sys.stdout.encoding or "ascii")
            _safe_print(f"  {name:45s} -> {status}  {result_str}")
            if not ok:
                bad = [k for k in required_keys if result.get(k) is not True]
                failures.append(f"check '{name}' failed keys: {bad}  result={result}")

        pg.close()
        b.close()

    for e in page_errors:
        _safe_print(f"  JS ERROR: {e}")

    server.should_exit = True
    time.sleep(0.4)

    if failures:
        for f in failures:
            _safe_print(f"FAIL: {f}")
        print("LITE_TREE_ROLLUP_FAIL")
        sys.exit(1)
    else:
        print("LITE_TREE_ROLLUP_OK")


if __name__ == "__main__":
    main()
