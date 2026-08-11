"""
BUG-20260526-lite-wizard-followup regression test.

Two precise regressions in lite/static/js/overview-setup.js, both already
patched; this test locks the behaviour so it can't silently regress again.

(A) Step-1 tile dblclick must be gated on unfinished triage work.
    UPDATED 2026-08-11 (BUG-20260811-escape-paths): originally gated on
    window.__lwizAutoLockActive, but WIZ-UNLOCK (fb9b2af) permanently set
    that flag false when the hard lock it belonged to was removed — the
    branch went dead and dblclick could always escape. The guard now
    checks LIVE work-in-progress instead: _lovsSelected.size > 0 (pages
    still selected mid-triage). While selected, dblclick must NOT navigate
    (loadPage/closeOverlays untouched) and must surface the wizard block
    hint (#lwiz-hint). Once selection is cleared, dblclick navigates
    normally — same observable contract as before, new trigger condition.

(B) Done (Step 3) runs _lovsForceFillMissingTags() -> reseedActivePageFolders()
    which creates PF folders + base layers, but the left panel (#catlist) was
    never re-rendered. Fix appends buildPicker() so the panel refreshes and the
    seeded layers become visible immediately.

4 sub-checks:
  dblclickNoOpWhenSelected   pages selected -> dblclick does not navigate + hint shown
  dblclickWorksWhenClear     selection cleared -> dblclick calls loadPage(pn)+closeOverlays
  doneRefreshesPicker        _lovsForceFillMissingTags() invokes buildPicker()
  layersVisibleAfterDone     emptied #catlist is repopulated after Done -> layers visible

Emits BUG_20260526_LITE_WIZ_FOLLOWUP_OK 4/4 on success.

    py -3 lite/tests/test_wiz_followup.py
"""
import socket, threading, time, sys
from pathlib import Path

LITE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LITE))
import uvicorn
from playwright.sync_api import sync_playwright


def _free_port(start=8280):
    for p in range(start, start + 60):
        with socket.socket() as s:
            if s.connect_ex(("127.0.0.1", p)) != 0:
                return p
    raise RuntimeError("no free port")


# ---------------------------------------------------------------------------
# Sub-check 1 — dblclickNoOpWhenSelected  (fix A, RED side)
# UPDATED 2026-08-11 (BUG-20260811-escape-paths): the guard trigger is now
# live selection state (_lovsSelected.size > 0), not the dead
# window.__lwizAutoLockActive flag WIZ-UNLOCK left behind.
# ---------------------------------------------------------------------------
CHECK_DBLCLICK_NOOP_WHEN_SELECTED = r"""
async () => {
  caseId = 'test-mock';
  pageCount = 3;
  pageTags = {1:'site', 2:'floor', 3:'plan'};

  // Open the wizard fresh at Step 1 (renders #grid-classify tiles)
  if (typeof openOv === 'function') openOv();
  await new Promise(r => setTimeout(r, 300));

  // Simulate unfinished triage: a page is selected (single click selects it)
  var selTile = document.querySelector('#grid-classify .ov-tile[data-pg="1"]');
  if (selTile) selTile.dispatchEvent(new MouseEvent('click', {bubbles: true, cancelable: true}));
  var selCount = (typeof _lovsSelected !== 'undefined') ? _lovsSelected.size : 0;

  // Spy navigation — do NOT call originals; a blocked dblclick must not fire them
  window.__loadPageArg = null;
  window.__closeOverlaysCalled = false;
  loadPage = function(n) { window.__loadPageArg = n; };
  closeOverlays = function() { window.__closeOverlaysCalled = true; };

  // Clear any stale hint from a previous run
  var h0 = document.getElementById('lwiz-hint'); if (h0) h0.remove();

  var ov = document.getElementById('ov');
  var openBefore = ov && ov.classList.contains('show');

  var tile = document.querySelector('#grid-classify .ov-tile[data-pg="1"]');
  var tileFound = !!tile;
  if (tile) tile.dispatchEvent(new MouseEvent('dblclick', {bubbles: true, cancelable: true}));
  await new Promise(r => setTimeout(r, 150));

  var hintVisible = !!document.getElementById('lwiz-hint');

  return {
    tileFound: tileFound,
    selCount: selCount,
    openBefore: !!openBefore,
    loadPageNotCalled: window.__loadPageArg === null,
    closeOverlaysNotCalled: window.__closeOverlaysCalled === false,
    hintVisible: hintVisible,
    stillOpen: !!(ov && ov.classList.contains('show')),
    allOk: tileFound && selCount > 0 && !!openBefore &&
           window.__loadPageArg === null &&
           window.__closeOverlaysCalled === false &&
           hintVisible
  };
}
"""

# ---------------------------------------------------------------------------
# Sub-check 2 — dblclickWorksWhenClear  (fix A, GREEN side)
# UPDATED 2026-08-11 (BUG-20260811-escape-paths): clears _lovsSelected
# instead of the retired window.__lwizAutoLockActive flag.
# ---------------------------------------------------------------------------
CHECK_DBLCLICK_WORKS_WHEN_CLEAR = r"""
async () => {
  caseId = 'test-mock';
  pageCount = 3;
  pageTags = {1:'site', 2:'floor', 3:'plan'};

  // Re-open + render Step 1 fresh, with no selection
  if (typeof openOv === 'function') openOv();
  await new Promise(r => setTimeout(r, 300));
  if (typeof _lovsSelected !== 'undefined') _lovsSelected.clear();
  if (typeof _lovsRenderClassify === 'function') _lovsRenderClassify();
  await new Promise(r => setTimeout(r, 100));

  // Fresh spies
  window.__loadPageArg = null;
  window.__closeOverlaysCalled = false;
  loadPage = function(n) { window.__loadPageArg = n; };
  closeOverlays = function() { window.__closeOverlaysCalled = true; };

  // p3 = 'plan' (no floor-input, so dblclick target is the tile itself)
  var tile = document.querySelector('#grid-classify .ov-tile[data-pg="3"]');
  var tileFound = !!tile;
  if (tile) tile.dispatchEvent(new MouseEvent('dblclick', {bubbles: true, cancelable: true}));
  await new Promise(r => setTimeout(r, 150));

  return {
    tileFound: tileFound,
    loadPageArg: window.__loadPageArg,
    closeOverlaysCalled: window.__closeOverlaysCalled,
    allOk: tileFound && window.__loadPageArg === 3 && window.__closeOverlaysCalled === true
  };
}
"""

# ---------------------------------------------------------------------------
# Sub-check 3 — doneRefreshesPicker  (fix B — buildPicker invoked)
# ---------------------------------------------------------------------------
CHECK_DONE_REFRESHES_PICKER = r"""
async () => {
  caseId = 'test-mock';
  pageCount = 4;
  pageTags = {1:'site', 2:'floor'};          // 3,4 untagged -> force-fill runs
  if (typeof pageFloorNum !== 'undefined') pageFloorNum[2] = 1;
  if (typeof state !== 'undefined') state.pageFolderMode = true;

  // Spy buildPicker (wrap, still call original so panel really re-renders)
  window.__bpCount = 0;
  var _origBP = buildPicker;
  buildPicker = function() { window.__bpCount++; return _origBP.apply(this, arguments); };

  // Empty the panel so we can prove the Done flow repopulates it
  var cl = document.getElementById('catlist'); if (cl) cl.innerHTML = '';

  var fnExists = typeof _lovsForceFillMissingTags === 'function';
  if (fnExists) _lovsForceFillMissingTags();
  await new Promise(r => setTimeout(r, 150));

  var count = window.__bpCount;
  buildPicker = _origBP;   // restore

  return {
    fnExists: fnExists,
    buildPickerCount: count,
    buildPickerCalled: count >= 1,
    allOk: fnExists && count >= 1
  };
}
"""

# ---------------------------------------------------------------------------
# Sub-check 4 — layersVisibleAfterDone  (fix B — panel actually shows layers)
# ---------------------------------------------------------------------------
CHECK_LAYERS_VISIBLE_AFTER_DONE = r"""
async () => {
  caseId = 'test-mock';
  pageCount = 4;
  pageTags = {1:'site', 2:'floor'};
  if (typeof pageFloorNum !== 'undefined') pageFloorNum[2] = 1;
  if (typeof state !== 'undefined') state.pageFolderMode = true;

  var cl = document.getElementById('catlist');
  if (cl) cl.innerHTML = '';
  var emptiedBefore = cl ? cl.childElementCount : -1;

  if (typeof _lovsForceFillMissingTags === 'function') _lovsForceFillMissingTags();
  await new Promise(r => setTimeout(r, 150));

  var after = cl ? cl.childElementCount : -1;

  return {
    emptiedBefore: emptiedBefore,
    catlistChildrenAfter: after,
    layersVisible: after > 0,
    allOk: emptiedBefore === 0 && after > 0
  };
}
"""

# ---------------------------------------------------------------------------
CHECKS = [
    ("dblclickNoOpWhenSelected", CHECK_DBLCLICK_NOOP_WHEN_SELECTED, ["allOk"]),
    ("dblclickWorksWhenClear",   CHECK_DBLCLICK_WORKS_WHEN_CLEAR,   ["allOk"]),
    ("doneRefreshesPicker",      CHECK_DONE_REFRESHES_PICKER,       ["allOk"]),
    ("layersVisibleAfterDone",   CHECK_LAYERS_VISIBLE_AFTER_DONE,   ["allOk"]),
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
        pg.set_default_timeout(90_000)
        pg.goto(f"http://127.0.0.1:{port}/", wait_until="networkidle")
        time.sleep(2.5)  # allow dynamic script load + setTimeout bootstrap

        print()
        print("BUG-20260526-lite-wizard-followup checks:")
        for name, scenario, required_keys in CHECKS:
            try:
                result = pg.evaluate(scenario)
            except Exception as ex:
                print(f"  {name:28s} -> EXCEPTION: {ex}")
                failures.append(f"check '{name}' threw: {ex}")
                continue

            ok = all(result.get(k) is True for k in required_keys)
            status = "PASS" if ok else "FAIL"
            print(f"  {name:28s} -> {status}  {result}")
            if not ok:
                bad = [k for k in required_keys if result.get(k) is not True]
                failures.append(f"check '{name}' failed keys: {bad}  result={result}")

        pg.close()
        b.close()

    for e in page_errors:
        print("  JS ERROR:", e)

    server.should_exit = True
    time.sleep(0.4)

    total = len(CHECKS)
    passed = total - len(failures)
    if failures:
        for f in failures:
            print("FAIL:", f)
        print(f"BUG_20260526_LITE_WIZ_FOLLOWUP_FAIL {passed}/{total}")
        sys.exit(1)
    else:
        print(f"BUG_20260526_LITE_WIZ_FOLLOWUP_OK {total}/{total}")


if __name__ == "__main__":
    main()
