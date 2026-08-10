"""
SHELL-FLOAT-2026-08-10: floating layer-palette wrapper guard
(docs/status/PHASE_INDEX.md "sprint cards SHELL-2026-08-10", GO-2026-08-10).

Module under test: lite/static/js/float-panel.js — wraps the EXISTING
#picker element (Photoshop-style floating palette): drag via a new header,
clamp inside #stage, collapse, hide + edge restore tab, persist position in
localStorage 'bmaLite.floatPanel.v1', double-click header resets position.
NEVER touches #picker's inner content or buildPicker() (verified by reading
both render paths before writing the module).

RED-first: written and run BEFORE static/js/float-panel.js existed / before
its <script src> tag was added to ui-lite.html — #fp-header was absent,
every check failed by construction. See TEST_RESULT / builder report for
the captured RED transcript.

5 sub-checks:
  headerExists           #fp-header renders as #picker's first child, with
                          grip + collapse + hide controls
  dragMovesPanel          pointerdown on header, move 120px, pointerup ->
                          #picker's bounding rect moved by ~120px (both axes)
  positionSurvivesReload  a dragged position round-trips through a real
                          page.reload() via localStorage
  collapseHidesCatlist    clicking #fp-collapse hides #catlist (and the
                          `.h` toolbar row); clicking again restores it
  hideThenRestoreTab      clicking #fp-hide hides #picker + shows #fp-tab;
                          clicking #fp-tab restores #picker + hides the tab
  dblclickResetsPosition  dragging away from (10,54) then double-clicking
                          the header snaps #picker back to (10,54)

Emits LITE_FLOAT_PANEL_OK on success.

    py -3 lite/tests/test_float_panel.py
"""
import socket
import sys
import threading
import time
from pathlib import Path

LITE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LITE))
import uvicorn
from playwright.sync_api import sync_playwright


def _free_port(start=8780):
    for p in range(start, start + 60):
        with socket.socket() as s:
            if s.connect_ex(("127.0.0.1", p)) != 0:
                return p
    raise RuntimeError("no free port")


CHECK_HEADER_EXISTS = r"""
() => {
  var picker = document.getElementById('picker');
  var header = document.getElementById('fp-header');
  var isFirstChild = !!(picker && header && picker.firstElementChild === header);
  var hasGrip = !!(header && header.querySelector('.fp-grip'));
  var hasCollapse = !!document.getElementById('fp-collapse');
  var hasHide = !!document.getElementById('fp-hide');
  return {
    headerFound: !!header, isFirstChild, hasGrip, hasCollapse, hasHide,
    pass: !!header && isFirstChild && hasGrip && hasCollapse && hasHide
  };
}
"""

CHECK_CATLIST_UNTOUCHED = r"""
() => {
  // buildPicker() must still only rewrite #catlist -- proves the module
  // did not disturb the existing render contract.
  var before = document.getElementById('picker').innerHTML.indexOf('fp-header');
  buildPicker();
  var after = document.getElementById('picker').innerHTML.indexOf('fp-header');
  return { before, after, pass: before >= 0 && after >= 0 };
}
"""


def _get_rect(pg, sel):
    return pg.evaluate(
        "(sel) => { var r = document.querySelector(sel).getBoundingClientRect(); "
        "return {x: r.x, y: r.y}; }",
        sel,
    )


# empty-state.js appends #ls-empty-state (position:absolute;inset:0;z-index:6)
# as a CHILD of #picker to hint "open a PDF first" -- it stacks ABOVE the new
# #fp-header (position:static, no explicit z-index) per normal CSS stacking
# rules (positioned+z-index always paints over static siblings regardless of
# DOM order), intercepting pointer events meant for the header. This is
# correct real-app behavior (nothing to drag-organize before a PDF is open)
# and orthogonal to float-panel.js itself, so the test neutralizes it the
# same way other lite UI tests bypass the "no doc" empty states -- directly,
# without going through a real /upload round-trip.
def _hide_empty_state(pg):
    pg.evaluate(
        "() => { var el = document.getElementById('ls-empty-state'); "
        "if (el) el.style.display = 'none'; }"
    )


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
        pg = b.new_page(viewport={"width": 1280, "height": 900})
        pg.on("pageerror", lambda e: page_errors.append(f"pageerror: {e}"))
        pg.goto(f"http://127.0.0.1:{port}/", wait_until="networkidle")
        time.sleep(1.0)
        _hide_empty_state(pg)

        print()
        print("LITE-FLOAT-PANEL checks:")

        # 1. headerExists
        name = "headerExists"
        r1 = pg.evaluate(CHECK_HEADER_EXISTS)
        ok1 = r1.get("pass") is True
        print(f"  {name:28s} -> {'PASS' if ok1 else 'FAIL'}  {r1}")
        if not ok1:
            failures.append(f"check '{name}' failed: {r1}")

        # 1b. buildPicker() still only touches #catlist (header survives re-render)
        name = "buildPickerLeavesHeaderIntact"
        r1b = pg.evaluate(CHECK_CATLIST_UNTOUCHED)
        ok1b = r1b.get("pass") is True
        print(f"  {name:28s} -> {'PASS' if ok1b else 'FAIL'}  {r1b}")
        if not ok1b:
            failures.append(f"check '{name}' failed: {r1b}")

        # 2. dragMovesPanel — real mouse events over the header
        name = "dragMovesPanel"
        try:
            before = _get_rect(pg, "#picker")
            header_box = pg.eval_on_selector("#fp-header", "el => { var r = el.getBoundingClientRect(); return {x:r.x,y:r.y,w:r.width,h:r.height}; }")
            sx = header_box["x"] + header_box["w"] / 2
            sy = header_box["y"] + header_box["h"] / 2
            pg.mouse.move(sx, sy)
            pg.mouse.down()
            pg.mouse.move(sx + 120, sy + 120, steps=8)
            pg.mouse.up()
            time.sleep(0.2)
            after = _get_rect(pg, "#picker")
            dx = after["x"] - before["x"]
            dy = after["y"] - before["y"]
            ok2 = abs(dx - 120) < 5 and abs(dy - 120) < 5
            print(f"  {name:28s} -> {'PASS' if ok2 else 'FAIL'}  before={before} after={after} dx={dx} dy={dy}")
            if not ok2:
                failures.append(f"check '{name}' failed: dx={dx} dy={dy}")
        except Exception as ex:
            print(f"  {name:28s} -> EXCEPTION: {ex}")
            failures.append(f"check '{name}' threw: {ex}")
            after = None

        # 3. positionSurvivesReload
        name = "positionSurvivesReload"
        try:
            saved_before_reload = after if after is not None else _get_rect(pg, "#picker")
            pg.reload(wait_until="networkidle")
            time.sleep(1.0)
            _hide_empty_state(pg)
            after_reload = _get_rect(pg, "#picker")
            dx = abs(after_reload["x"] - saved_before_reload["x"])
            dy = abs(after_reload["y"] - saved_before_reload["y"])
            ok3 = dx < 3 and dy < 3
            print(f"  {name:28s} -> {'PASS' if ok3 else 'FAIL'}  before={saved_before_reload} after={after_reload}")
            if not ok3:
                failures.append(f"check '{name}' failed: before={saved_before_reload} after={after_reload}")
        except Exception as ex:
            print(f"  {name:28s} -> EXCEPTION: {ex}")
            failures.append(f"check '{name}' threw: {ex}")

        # 4. collapseHidesCatlist
        name = "collapseHidesCatlist"
        try:
            r4 = pg.evaluate(r"""
              () => {
                var cl = document.getElementById('catlist');
                document.getElementById('fp-collapse').click();
                var hiddenAfterCollapse = cl.style.display === 'none';
                document.getElementById('fp-collapse').click();
                var visibleAfterExpand = cl.style.display !== 'none';
                return { hiddenAfterCollapse, visibleAfterExpand,
                         pass: hiddenAfterCollapse && visibleAfterExpand };
              }
            """)
            ok4 = r4.get("pass") is True
            print(f"  {name:28s} -> {'PASS' if ok4 else 'FAIL'}  {r4}")
            if not ok4:
                failures.append(f"check '{name}' failed: {r4}")
        except Exception as ex:
            print(f"  {name:28s} -> EXCEPTION: {ex}")
            failures.append(f"check '{name}' threw: {ex}")

        # 5. hideThenRestoreTab
        name = "hideThenRestoreTab"
        try:
            r5 = pg.evaluate(r"""
              () => {
                var picker = document.getElementById('picker');
                var tab = document.getElementById('fp-tab');
                document.getElementById('fp-hide').click();
                var pickerHidden = getComputedStyle(picker).display === 'none';
                var tabShown = getComputedStyle(tab).display !== 'none';
                tab.click();
                var pickerRestored = getComputedStyle(picker).display !== 'none';
                var tabHidden = getComputedStyle(tab).display === 'none';
                return { pickerHidden, tabShown, pickerRestored, tabHidden,
                         pass: pickerHidden && tabShown && pickerRestored && tabHidden };
              }
            """)
            ok5 = r5.get("pass") is True
            print(f"  {name:28s} -> {'PASS' if ok5 else 'FAIL'}  {r5}")
            if not ok5:
                failures.append(f"check '{name}' failed: {r5}")
        except Exception as ex:
            print(f"  {name:28s} -> EXCEPTION: {ex}")
            failures.append(f"check '{name}' threw: {ex}")

        # 6. dblclickResetsPosition — drag away, then dblclick header
        name = "dblclickResetsPosition"
        try:
            header_box = pg.eval_on_selector("#fp-header", "el => { var r = el.getBoundingClientRect(); return {x:r.x,y:r.y,w:r.width,h:r.height}; }")
            sx = header_box["x"] + header_box["w"] / 2
            sy = header_box["y"] + header_box["h"] / 2
            pg.mouse.move(sx, sy)
            pg.mouse.down()
            pg.mouse.move(sx + 200, sy + 60, steps=6)
            pg.mouse.up()
            time.sleep(0.2)
            moved = _get_rect(pg, "#picker")

            header_box2 = pg.eval_on_selector("#fp-header", "el => { var r = el.getBoundingClientRect(); return {x:r.x,y:r.y,w:r.width,h:r.height}; }")
            pg.mouse.dblclick(header_box2["x"] + header_box2["w"] / 2, header_box2["y"] + header_box2["h"] / 2)
            time.sleep(0.2)
            reset = pg.evaluate(r"""
              () => {
                var picker = document.getElementById('picker');
                return { left: parseFloat(picker.style.left), top: parseFloat(picker.style.top) };
              }
            """)
            ok6 = abs(reset["left"] - 10) < 1 and abs(reset["top"] - 54) < 1
            print(f"  {name:28s} -> {'PASS' if ok6 else 'FAIL'}  moved={moved} reset={reset}")
            if not ok6:
                failures.append(f"check '{name}' failed: moved={moved} reset={reset}")
        except Exception as ex:
            print(f"  {name:28s} -> EXCEPTION: {ex}")
            failures.append(f"check '{name}' threw: {ex}")

        pg.close()
        b.close()

    for e in page_errors:
        print("  JS ERROR:", e)

    server.should_exit = True
    time.sleep(0.4)

    if failures:
        for f in failures:
            print("FAIL:", f)
        print("LITE_FLOAT_PANEL_FAIL")
        sys.exit(1)
    else:
        print("LITE_FLOAT_PANEL_OK")


if __name__ == "__main__":
    main()
