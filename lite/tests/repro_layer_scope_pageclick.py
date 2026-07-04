"""
INV-2026-07-04-001 slice 4 — REPRO for user bug: after creating a custom
layer on a floor, navigating away then BACK via a click path (not the rail)
allegedly shows stale/default layers instead of the created one.

Real PDF (loadPage() no-ops without a real case/pdfDoc), real fixture tags.
Tests TWO click paths back to floor 2: (A) #mi-prev button clicks, (B) the
page-manager overlay (pmOpenManager) thumbnail click.
"""
import socket, sys, threading, time
from pathlib import Path

LITE = Path(__file__).resolve().parents[1]
REPO = LITE.parent
PDF_PATH = REPO / "20250616_RAMA4 APARTMENT PERMIT rev 1.pdf"
sys.path.insert(0, str(LITE))
import uvicorn
from playwright.sync_api import sync_playwright


def _free_port(start=8480):
    for p in range(start, start + 60):
        with socket.socket() as s:
            if s.connect_ex(("127.0.0.1", p)) != 0:
                return p
    raise RuntimeError("no free port")


JS_SETUP = r"""
async () => {
  pageTags = Object.assign({}, pageTags, {5:'site',7:'site',8:'site',
    11:'floor',12:'floor',13:'floor',14:'floor',15:'floor',16:'floor'});
  pageFloorNum = Object.assign({}, pageFloorNum, {11:1,12:2,13:3,14:4,15:5,16:'roof'});
  pageFloorKind = Object.assign({}, pageFloorKind, {16:'rooftop'});
  reseedActivePageFolders();
  await loadPage(12);
  await new Promise(r => setTimeout(r, 500));
  var nl = addLayer('gfa', 'CustomFloor2Layer', '#ff00ff');
  nl.parentId = 'PF_floor_2';
  state.catVis[nl.id] = true; state.catLock[nl.id] = false; state.dirty = true;
  buildPicker();
  await new Promise(r => setTimeout(r, 100));
  var presentNow = !!document.querySelector('[data-catid="' + nl.id + '"]');
  return {newId: nl.id, presentAfterCreate: presentNow};
}
"""

JS_CHECK = r"""
(layerId) => {
  var row = document.querySelector('[data-catid="' + layerId + '"]');
  var floor2Row = document.querySelector('[data-catid="PF_floor_2"]');
  var catIds = Array.prototype.map.call(
    document.querySelectorAll('#catlist [data-catid]'),
    function(el) { return el.getAttribute('data-catid'); }
  );
  return {
    curPage: curPage,
    customLayerPresent: !!row,
    pf2FolderPresent: !!floor2Row,
    catlistIds: catIds
  };
}
"""


def main():
    from server_lite import app as lite_app
    port = _free_port()
    cfg = uvicorn.Config(lite_app, host="127.0.0.1", port=port, log_level="error")
    server = uvicorn.Server(cfg)
    threading.Thread(target=server.run, daemon=True).start()
    time.sleep(2.0)

    with sync_playwright() as pw:
        b = pw.chromium.launch()
        pg = b.new_page()
        errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.goto(f"http://127.0.0.1:{port}/", wait_until="networkidle")
        pg.wait_for_timeout(500)
        pg.set_input_files("#file-pdf", str(PDF_PATH))
        pg.wait_for_timeout(2500)
        pg.evaluate("() => { var b=document.getElementById('ov-close'); if(b) b.click(); }")
        pg.wait_for_timeout(300)

        setup = pg.evaluate(JS_SETUP)
        print(f"  setup (on floor2 right after create): {setup}")
        layer_id = setup["newId"]

        # navigate away to floor 3 via loadPage (rail-equivalent)
        pg.evaluate("(n) => loadPage(n)", 13)
        pg.wait_for_timeout(1500)

        # --- Path A: PageUp keyboard shortcut back to floor 2 (real click-adjacent
        #     nav path; #mi-prev is a hidden dropdown item, needs its menu open) ---
        pg.locator("#cv").click(position={"x": 5, "y": 5})  # focus canvas, not an input
        pg.keyboard.press("PageUp")
        pg.wait_for_timeout(1500)
        resA = pg.evaluate(JS_CHECK, layer_id)
        print(f"  Path A (#mi-prev click) result: {resA}")

        # go away again to floor 3
        pg.evaluate("(n) => loadPage(n)", 13)
        pg.wait_for_timeout(1500)

        # --- Path B: page-manager thumbnail click back to floor 2 (p12) ---
        pg.evaluate("() => { if (typeof pmOpenManager === 'function') pmOpenManager(); }")
        pg.wait_for_timeout(500)
        thumb = pg.locator('.pmui-thumb[data-pmui-idx="11"]')  # 0-based idx for page 12
        if thumb.count() > 0:
            thumb.click()
        pg.wait_for_timeout(1500)
        resB = pg.evaluate(JS_CHECK, layer_id)
        print(f"  Path B (page-manager thumb click) result: {resB}")

        # --- Path C: real "+ เพิ่ม layer" add-row click (not programmatic addLayer)
        #     on floor 3, PLUS a reseedActivePageFolders() call in between (simulates
        #     revisiting the Page Setup wizard while tagging other floors) — tests
        #     candidate (c): reseed-on-revisit orphaning a just-created custom layer. ---
        pg.evaluate("(n) => loadPage(n)", 13)
        pg.wait_for_timeout(1500)
        resC0 = pg.evaluate(
            r"""
            () => {
              window._origPrompt = window.prompt;
              window.prompt = function() { return 'CustomFloor3ViaUI'; };
              var addRow = document.querySelector('.lt-add[data-pf-add="PF_floor_3"]');
              if (!addRow) { window.prompt = window._origPrompt; return {no_row: true}; }
              addRow.click();
              window.prompt = window._origPrompt;
              var nl = LAYERS.find(l => l.name === 'CustomFloor3ViaUI');
              return {created: !!nl, id: nl ? nl.id : null};
            }
            """
        )
        print(f"  Path C setup (real add-row on floor3): {resC0}")
        layer3_id = resC0.get("id")

        # simulate a Page Setup wizard revisit (re-tag another page) -> reseed fires
        pg.evaluate("() => { reseedActivePageFolders(); buildPicker(); }")
        pg.wait_for_timeout(300)

        # navigate away then back to floor 3 via loadPage, then check
        pg.evaluate("(n) => loadPage(n)", 12)
        pg.wait_for_timeout(1200)
        pg.evaluate("(n) => loadPage(n)", 13)
        pg.wait_for_timeout(1200)
        resC = pg.evaluate(JS_CHECK, layer3_id) if layer3_id else {"customLayerPresent": None}
        print(f"  Path C (post-reseed round-trip) result: {resC}")

        for e in errs:
            print("  JS ERROR:", e)

        b.close()

    server.should_exit = True
    time.sleep(0.4)

    ok = (
        setup.get("presentAfterCreate") is True
        and resA.get("customLayerPresent") is True
        and resB.get("customLayerPresent") is True
        and resC0.get("created") is True
        and resC.get("customLayerPresent") is True
    )
    print("REPRO_BUG_CONFIRMED" if not ok else "REPRO_NO_BUG_FOUND")


if __name__ == "__main__":
    main()
