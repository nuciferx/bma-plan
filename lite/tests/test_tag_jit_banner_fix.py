"""
page-manager-redesign approach D, SLICE 2 (TAG-JIT-FIX) —
docs/invent/page-manager-redesign.md, GO 2026-08-10, Decision note.

Fixes 3 known bugs in the SHIPPED JIT tag gate (lite/static/js/tag-jit.js,
INV-2026-07-04-002 slice 4/4) — NOT a new banner module:

  (a) banner tag-chip click handlers closed over the page number `n` at
      banner-RENDER time; if the user navigates away before tapping a
      chip, the stale closed-over page gets tagged instead of the page
      the user is actually looking at.
  (b) the banner never hid itself on page navigation (no hook on
      `afterPage()`), so a stale banner from page 1 could still be
      clicked while the user is looking at page 2.
  (c) window.__jitWrapped was set BEFORE confirming setTool actually got
      wrapped — a race at bootstrap could silently leave setTool
      unwrapped while __jitWrapped lied that it succeeded.

2 sub-checks (both target bugs (a)+(b) together, per spec):
  bannerHidesOnNavigate   arm a measure tool on untagged page 1 (banner
                          shows) -> simulate real navigation via the
                          actual global afterPage() -> banner must be
                          hidden + _jitPendingTool cleared.
  chipUsesLiveCurPage     arm on untagged page 1 (banner shows) -> curPage
                          changes to 2 (simulating an in-flight
                          navigation that hasn't called afterPage yet) ->
                          click the (still-DOM-present) tag chip -> must
                          tag page 2 (curPage AT CLICK TIME), never the
                          stale closed-over page 1.

Emits LITE_TAG_JIT_BANNER_OK on success.

    py -3 lite/tests/test_tag_jit_banner_fix.py
"""
import socket, threading, time, sys
from pathlib import Path

LITE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LITE))
import uvicorn
from playwright.sync_api import sync_playwright


def _free_port(start=8670):
    for p in range(start, start + 60):
        with socket.socket() as s:
            if s.connect_ex(("127.0.0.1", p)) != 0:
                return p
    raise RuntimeError("no free port")


SETUP_GLOBALS = r"""
async () => {
  await new Promise(r => setTimeout(r, 400));  // let all dynamic scripts (incl. tag-jit.js) load
  return {done: true, wrapInstalled: window.__jitWrapped === true};
}
"""

# ---------------------------------------------------------------------------
# Sub-check 1 — bannerHidesOnNavigate
# ---------------------------------------------------------------------------
CHECK_BANNER_HIDES_ON_NAVIGATE = r"""
() => {
  caseId = 'test'; pageCount = 5; pageTags = {}; excluded = {};
  curPage = 1; state.tool = 'select';
  PS = { 1: { objects: [], scale: null, annotations: [] },
         2: { objects: [], scale: null, annotations: [] } };
  _jitHideBanner();

  setTool('poly');   // page 1 untagged -> blocked, banner shows for page 1
  var banner = document.getElementById('jit-banner');
  var bannerShownOnP1 = !!banner && banner.style.display !== 'none';
  var pendingToolSet  = _jitPendingTool === 'poly';

  // Simulate REAL navigation: curPage flips, then the actual global
  // afterPage() runs (exactly what loadPage() does in page-renderer.js).
  curPage = 2;
  if (typeof window.afterPage === 'function') window.afterPage();

  var bannerHiddenAfterNav = !banner || banner.style.display === 'none';
  var pendingClearedAfterNav = _jitPendingTool === null;

  return {
    bannerShownOnP1, pendingToolSet, bannerHiddenAfterNav, pendingClearedAfterNav,
    pass: bannerShownOnP1 && pendingToolSet && bannerHiddenAfterNav && pendingClearedAfterNav
  };
}
"""

# ---------------------------------------------------------------------------
# Sub-check 2 — chipUsesLiveCurPage
# ---------------------------------------------------------------------------
CHECK_CHIP_USES_LIVE_CURPAGE = r"""
() => {
  caseId = 'test'; pageCount = 5; pageTags = {}; excluded = {};
  pageFloorNum = {}; pageFloorKind = {};
  curPage = 1; state.tool = 'select'; state.pageFolderMode = true;
  PS = { 1: { objects: [], scale: null, annotations: [] },
         2: { objects: [], scale: { pts_per_m: 10 }, annotations: [] } };
  _jitHideBanner();

  setTool('dist');   // page 1 untagged -> blocked, banner renders for page 1
  var banner = document.getElementById('jit-banner');
  var chip = banner ? banner.querySelector('[data-jit-tag="floor"]') : null;
  var chipFound = !!chip;

  // Simulate an in-flight navigation: curPage already flipped to 2, but
  // afterPage() has NOT run yet (banner still in the DOM, still clickable —
  // this isolates bug (a) from the afterPage-hide fix (b) above).
  curPage = 2;

  if (chip) chip.click();

  var page2Tagged = pageTags[2] === 'floor';
  var page1Untouched = !pageTags[1];

  return {
    chipFound, page2Tagged, page1Untouched,
    tagOnPage1: pageTags[1], tagOnPage2: pageTags[2],
    pass: chipFound && page2Tagged && page1Untouched
  };
}
"""

CHECKS = [
    ("bannerHidesOnNavigate",  CHECK_BANNER_HIDES_ON_NAVIGATE,  ["pass"]),
    ("chipUsesLiveCurPage",    CHECK_CHIP_USES_LIVE_CURPAGE,    ["pass"]),
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
        time.sleep(2.0)

        try:
            setup_result = pg.evaluate(SETUP_GLOBALS)
            print(f"  SETUP: {setup_result}")
        except Exception as ex:
            print(f"  SETUP FAILED: {ex}")
            failures.append(f"setup threw: {ex}")

        print()
        print("LITE-TAG-JIT-BANNER-FIX checks:")
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

    if failures:
        for f in failures:
            print("FAIL:", f)
        print("LITE_TAG_JIT_BANNER_FAIL")
        sys.exit(1)
    else:
        print("LITE_TAG_JIT_BANNER_OK")


if __name__ == "__main__":
    main()
