"""
INV-2026-07-04-001 slice 3/3 — real-permit integration proof.

Manual/demo script (not a pass/fail regression test): opens the real 45-page
RAMA4 permit PDF in the live lite app, tags a handful of pages using the
project's canonical fixture (tests/fixtures/permit-45p-tags.json), navigates
to a floor page, and screenshots the P2 Balanced (260px) layer panel +
floor-rail + search — full window and a panel closeup.

Output:
  artifacts/invent/lite-layer-menu-ui-fix/live-p2-fullapp.png
  artifacts/invent/lite-layer-menu-ui-fix/live-p2-panel.png

Also asserts + prints the live #picker offsetWidth (must be ~260, the P2
geometry applied in this slice) and checks for zero browser console errors
during load.

    py -3 lite/tests/manual_layer_scope_screenshot.py
"""
import socket
import sys
import threading
import time
from pathlib import Path

LITE = Path(__file__).resolve().parents[1]
REPO = LITE.parent
PDF_PATH = REPO / "20250616_RAMA4 APARTMENT PERMIT rev 1.pdf"
ARTIFACTS = REPO / "artifacts" / "invent" / "lite-layer-menu-ui-fix"
ARTIFACTS.mkdir(parents=True, exist_ok=True)

sys.path.insert(0, str(LITE))
import uvicorn
from playwright.sync_api import sync_playwright


def _free_port(start=8470):
    for p in range(start, start + 60):
        with socket.socket() as s:
            if s.connect_ex(("127.0.0.1", p)) != 0:
                return p
    raise RuntimeError("no free port")


# Tags from tests/fixtures/permit-45p-tags.json (site: 5,7,8 / floor: 11-16,
# with 16 = "roof deck" — mapped to kind=rooftop so it becomes PF_floor_roof
# instead of a numbered floor).
JS_TAG_AND_NAVIGATE = r"""
async () => {
  pageTags = Object.assign({}, pageTags, {
    5: 'site', 7: 'site', 8: 'site',
    11: 'floor', 12: 'floor', 13: 'floor', 14: 'floor', 15: 'floor', 16: 'floor'
  });
  pageFloorNum = Object.assign({}, pageFloorNum, {
    11: 1, 12: 2, 13: 3, 14: 4, 15: 5, 16: 'roof'
  });
  pageFloorKind = Object.assign({}, pageFloorKind, {
    16: 'rooftop'
  });
  reseedActivePageFolders();
  await loadPage(12); // floor 2 — mid-stack, scoped panel + rail with siblings both directions
  await new Promise(r => setTimeout(r, 300));
  buildPicker();

  var picker = document.getElementById('picker');
  var rail = document.getElementById('ls-rail');
  var jump = document.getElementById('ls-rail-jump');
  return {
    curPage: curPage,
    pickerWidth: picker ? picker.offsetWidth : null,
    railVisible: !!(rail && rail.style.display !== 'none'),
    railOptionCount: jump ? jump.options.length : 0,
    floor2Shown: !!document.querySelector('[data-catid="PF_floor_2"]'),
    siteHidden: !document.querySelector('[data-catid="PF_site"]')
  };
}
"""


def main():
    from server_lite import app as lite_app

    if not PDF_PATH.exists():
        print(f"MANUAL_SCREENSHOT_SKIP: real PDF not found at {PDF_PATH}")
        sys.exit(0)

    port = _free_port()
    cfg = uvicorn.Config(lite_app, host="127.0.0.1", port=port, log_level="error")
    server = uvicorn.Server(cfg)
    threading.Thread(target=server.run, daemon=True).start()
    time.sleep(2.0)

    console_errors = []
    page_errors = []

    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        ctx = browser.new_context(viewport={"width": 1440, "height": 900})
        page = ctx.new_page()
        page.on("console", lambda m: console_errors.append(m.text) if m.type == "error" else None)
        page.on("pageerror", lambda e: page_errors.append(str(e)))

        page.goto(f"http://127.0.0.1:{port}/", wait_until="networkidle")
        page.wait_for_timeout(500)

        print(f"  uploading real PDF: {PDF_PATH.name}")
        page.set_input_files("#file-pdf", str(PDF_PATH))
        page.wait_for_timeout(2500)  # local-first PDF.js open + first page render

        # LWIZ-AUTO opens the Page Setup / Overview wizard automatically on first
        # PDF open — close it so the layer panel is unobstructed for the screenshot
        # (the wizard is a separate, unrelated overlay; not part of this slice).
        closed_wizard = page.evaluate(
            "() => { var b = document.getElementById('ov-close'); "
            "if (b) { b.click(); return true; } return false; }"
        )
        print(f"  closed Page Setup wizard overlay: {closed_wizard}")
        page.wait_for_timeout(300)

        info = page.evaluate(JS_TAG_AND_NAVIGATE)
        print(f"  tag+navigate result: {info}")

        page.wait_for_timeout(1800)  # give the page-12 raster/PDF.js paint time to land

        shot1 = ARTIFACTS / "live-p2-fullapp.png"
        page.screenshot(path=str(shot1), full_page=False)
        print(f"  saved: {shot1}")

        shot2 = ARTIFACTS / "live-p2-panel.png"
        picker_locator = page.locator("#picker")
        if picker_locator.count() > 0:
            picker_locator.screenshot(path=str(shot2))
            print(f"  saved: {shot2}")
        else:
            print("  WARN: #picker not found for closeup screenshot")

        ctx.close()
        browser.close()

    server.should_exit = True
    time.sleep(0.4)

    for e in console_errors:
        print("  CONSOLE ERROR:", e)
    for e in page_errors:
        print("  JS ERROR:", e)

    width = info.get("pickerWidth")
    width_ok = width is not None and 250 <= width <= 270
    ok = (
        width_ok
        and info.get("railVisible") is True
        and info.get("railOptionCount", 0) >= 2
        and info.get("floor2Shown") is True
        and info.get("siteHidden") is True
        and not console_errors
        and not page_errors
        and shot1.exists()
        and shot2.exists()
    )

    print()
    print(f"  #picker offsetWidth = {width} (expected ~260)")
    print(f"  rail option count   = {info.get('railOptionCount')}")
    print(f"  console errors      = {len(console_errors)}")
    print(f"  screenshots exist   = {shot1.exists()} / {shot2.exists()}")

    if ok:
        print("MANUAL_SCREENSHOT_OK")
    else:
        print("MANUAL_SCREENSHOT_FAIL")
        sys.exit(1)


if __name__ == "__main__":
    main()
