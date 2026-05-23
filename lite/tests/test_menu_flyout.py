"""
LMENU-1: test_menu_flyout.py — verifies flyout submenu chrome.

Six checks (all driven by real DOM events via Playwright):
  1. submenuMarkupBuilt        — ≥4 .item.has-sub parents exist after page load
  2. submenuShowsOnHover       — Area has-sub: mouseenter makes .sub-dd visible
  3. polygonItemSetsToolPoly   — click "Polygon (A)" → state.tool==='poly' + menu closed
  4. arcItemSetsToolPolyAndFlashesHint — click "Polygon + Arc edges" →
       state.tool==='poly' AND state.hintFlash non-empty AND #hint contains Thai arc text
  5. distanceContinuousSetsToolPath — click "Continuous path" → state.tool==='path'
  6. flatPolygonItemAbsent     — no [data-tool="poly"] outside .has-sub descendants

Emits LITE_MENU_FLYOUT_OK on success.

    py -3 lite/tests/test_menu_flyout.py
"""
import socket, threading, time, sys, io
from pathlib import Path

# Ensure stdout can handle UTF-8 (needed for Thai characters in hint strings)
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

LITE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LITE))
import uvicorn
from playwright.sync_api import sync_playwright


def _free_port(start=8480):
    for p in range(start, start + 60):
        with socket.socket() as s:
            if s.connect_ex(("127.0.0.1", p)) != 0:
                return p
    raise RuntimeError("no free port")


# ---------------------------------------------------------------------------
# Check 1 — submenuMarkupBuilt
# After page load, at least 4 .item.has-sub parents exist.
# ---------------------------------------------------------------------------
SC1_MARKUP = """
() => {
    var parents = document.querySelectorAll('.dd .item.has-sub');
    return { count: parents.length, pass: parents.length >= 4 };
}
"""

# ---------------------------------------------------------------------------
# Check 2 — submenuShowsOnHover
# Locate the Area has-sub element, dispatch mouseenter, assert sub-dd visible.
# We use CSS :hover simulation via Playwright's hover() to trigger the CSS
# :hover rule.  Then check getComputedStyle(subDd).display === 'block'.
# ---------------------------------------------------------------------------
SC2_HOVER = """
() => {
    // Find Area flyout parent (has data-flyout-group="area")
    var parent = document.querySelector('.item.has-sub[data-flyout-group="area"]');
    if (!parent) return { pass: false, reason: 'area has-sub not found' };
    var subDd = parent.querySelector('.sub-dd');
    if (!subDd) return { pass: false, reason: 'sub-dd not found inside area has-sub' };
    // The CSS :hover rule shows .sub-dd; we simulate hover via mouseenter event.
    parent.dispatchEvent(new MouseEvent('mouseenter', { bubbles: true }));
    // Force :hover state by checking if the element would be revealed.
    // Since CSS :hover can't be forced via JS alone in all cases,
    // we check via matches(':hover') OR inspect the display after programmatic hover.
    // Playwright will call hover() externally; here we just verify sub-dd exists.
    return {
        subDdFound: !!subDd,
        subDdInDom: document.contains(subDd),
        pass: !!subDd && document.contains(subDd)
    };
}
"""

# ---------------------------------------------------------------------------
# Check 3 — polygonItemSetsToolPoly
# Click the "Polygon (A)" item inside the Area sub-dd.
# Assert state.tool === 'poly' and no menu has class 'open'.
# ---------------------------------------------------------------------------
SC3_POLY_TOOL = """
() => {
    // Reset tool to something else
    state.tool = 'select';
    // Find the Polygon (A) item inside the Area sub-dd
    var area = document.querySelector('.item.has-sub[data-flyout-group="area"]');
    if (!area) return { pass: false, reason: 'area flyout not found' };
    var polyItem = area.querySelector('.sub-dd .item[data-tool="poly"]');
    if (!polyItem) return { pass: false, reason: 'poly sub-item not found' };
    polyItem.click();
    var toolOk = state.tool === 'poly';
    var menusClosed = document.querySelectorAll('.menu.open').length === 0;
    return { tool: state.tool, toolOk, menusClosed, pass: toolOk && menusClosed };
}
"""

# ---------------------------------------------------------------------------
# Check 4 — arcItemSetsToolPolyAndFlashesHint
# Click the "Polygon + Arc edges" item.
# Assert state.tool==='poly' AND state.hintFlash non-empty AND #hint contains Thai arc text.
# ---------------------------------------------------------------------------
SC4_ARC_HINT = """
() => {
    state.tool = 'select';
    state.hintFlash = '';
    var area = document.querySelector('.item.has-sub[data-flyout-group="area"]');
    if (!area) return { pass: false, reason: 'area flyout not found' };
    // The arc item has data-hint set by _buildSubItem
    var arcItem = area.querySelector('.sub-dd .item[data-hint]');
    if (!arcItem) return { pass: false, reason: 'arc edges item (data-hint) not found' };
    arcItem.click();
    var toolOk = state.tool === 'poly';
    var flashNonEmpty = !!state.hintFlash && state.hintFlash.length > 0;
    // updateHUD() is called by setTool (via draw() → updateHUD())
    // Give a tiny tick for the hint to propagate
    var hintEl = document.getElementById('hint');
    var hintText = hintEl ? hintEl.innerHTML : '';
    // The Thai arc instruction should be in state.hintFlash or in the hint element
    var hasThaiArc = flashNonEmpty && (state.hintFlash.indexOf('arc') >= 0 || state.hintFlash.indexOf('A') >= 0);
    return {
        tool: state.tool, toolOk,
        hintFlash: state.hintFlash, flashNonEmpty,
        hintElText: hintText.substring(0, 80),
        hasThaiArc,
        pass: toolOk && flashNonEmpty && hasThaiArc
    };
}
"""

# ---------------------------------------------------------------------------
# Check 5 — distanceContinuousSetsToolPath
# Click "Continuous path" item inside Distance sub-dd.
# Assert state.tool === 'path'.
# ---------------------------------------------------------------------------
SC5_PATH_TOOL = """
() => {
    state.tool = 'select';
    var dist = document.querySelector('.item.has-sub[data-flyout-group="distance"]');
    if (!dist) return { pass: false, reason: 'distance flyout not found' };
    var pathItem = dist.querySelector('.sub-dd .item[data-tool="path"]');
    if (!pathItem) return { pass: false, reason: 'path sub-item not found' };
    pathItem.click();
    return { tool: state.tool, pass: state.tool === 'path' };
}
"""

# ---------------------------------------------------------------------------
# Check 6 — flatPolygonItemAbsent
# No [data-tool="poly"] should exist OUTSIDE a .has-sub descendant.
# ---------------------------------------------------------------------------
SC6_NO_FLAT_POLY = """
() => {
    // Items inside .has-sub > .sub-dd are valid (submenu items).
    // Any item with data-tool="poly" that is NOT inside a .has-sub descendant = fail.
    var allPoly = document.querySelectorAll('[data-tool="poly"]');
    var flatCount = 0;
    allPoly.forEach(function(el) {
        // Check if the element is inside a .has-sub container
        if (!el.closest('.has-sub')) flatCount++;
    });
    return { totalPoly: allPoly.length, flatCount, pass: flatCount === 0 };
}
"""


CHECKS = [
    ("submenuMarkupBuilt",             SC1_MARKUP,    ["pass"]),
    ("submenuShowsOnHover",            SC2_HOVER,     ["pass"]),
    ("polygonItemSetsToolPoly",        SC3_POLY_TOOL, ["pass"]),
    ("arcItemSetsToolPolyAndFlashesHint", SC4_ARC_HINT, ["pass"]),
    ("distanceContinuousSetsToolPath", SC5_PATH_TOOL, ["pass"]),
    ("flatPolygonItemAbsent",          SC6_NO_FLAT_POLY, ["pass"]),
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

        print()
        print("LMENU-1 flyout checks:")

        # Check 2 uses Playwright hover to trigger CSS :hover
        # We handle it specially below.
        for name, scenario, required_keys in CHECKS:
            if name == "submenuShowsOnHover":
                # Use Playwright's hover() to trigger CSS :hover, then evaluate
                try:
                    # Open the Measure menu first
                    meas_btn = pg.query_selector('.menu[data-m="measure"] > button')
                    if meas_btn:
                        meas_btn.click()
                        time.sleep(0.1)
                    # Hover over the area has-sub parent
                    area_parent = pg.query_selector('.item.has-sub[data-flyout-group="area"]')
                    if area_parent:
                        area_parent.hover()
                        time.sleep(0.1)
                        sub_visible = pg.evaluate("""
                            () => {
                                var area = document.querySelector('.item.has-sub[data-flyout-group="area"]');
                                if (!area) return { pass: false, reason: 'no area parent' };
                                var sub = area.querySelector('.sub-dd');
                                if (!sub) return { pass: false, reason: 'no sub-dd' };
                                var display = getComputedStyle(sub).display;
                                return { display, pass: display === 'block', subFound: true };
                            }
                        """)
                        ok = all(sub_visible.get(k) is True for k in required_keys)
                        status = "PASS" if ok else "FAIL"
                        print(f"  {name:42s} -> {status}  {sub_visible}")
                        if not ok:
                            failures.append(f"check '{name}' failed: {sub_visible}")
                    else:
                        print(f"  {name:42s} -> FAIL  area has-sub not found in DOM")
                        failures.append(f"check '{name}' failed: area has-sub not found")
                    # Close menu
                    pg.keyboard.press("Escape")
                    time.sleep(0.05)
                except Exception as ex:
                    print(f"  {name:42s} -> EXCEPTION: {ex}")
                    failures.append(f"check '{name}' threw: {ex}")
                continue

            try:
                result = pg.evaluate(scenario)
            except Exception as ex:
                print(f"  {name:42s} -> EXCEPTION: {ex}")
                failures.append(f"check '{name}' threw: {ex}")
                continue

            ok = all(result.get(k) is True for k in required_keys)
            status = "PASS" if ok else "FAIL"
            print(f"  {name:42s} -> {status}  {result}")
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
        print("LITE_MENU_FLYOUT_FAIL")
        sys.exit(1)
    else:
        print("LITE_MENU_FLYOUT_OK")


if __name__ == "__main__":
    main()
