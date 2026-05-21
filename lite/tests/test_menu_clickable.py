"""
BUG-20260521-lite-menu-clip regression guard.

The lite top-bar dropdowns once opened (display:block) but were invisible &
unclickable because #topbar had a fixed 42px height + overflow:hidden, which
clipped the .dd dropdown (it hangs below the bar into #stage), and #topbar
created no stacking context so dropdowns sat under #stage content.

This test boots server_lite, opens each top-level menu, and asserts that the
FIRST item of each dropdown is the topmost element at its own center
(elementFromPoint == the item, not .empty / canvas). Emits
BUG_20260521_LITE_MENU_CLIP_OK on success.

    py -3 lite/tests/test_menu_clickable.py
"""
import socket, threading, time, sys
from pathlib import Path

LITE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LITE))
import uvicorn
from playwright.sync_api import sync_playwright


def _free_port(start=8230):
    for p in range(start, start + 60):
        with socket.socket() as s:
            if s.connect_ex(("127.0.0.1", p)) != 0:
                return p
    raise RuntimeError("no free port")


# (menu data-m, first-item selector within its .dd)
MENUS = [
    ("file", "#mi-open"),
    ("measure", '.menu[data-m=measure] .item[data-tool=select]'),
    ("page", "#mi-prev"),
    ("annotate", '.menu[data-m=annotate] .item[data-tool=ann_text]'),
]


def main():
    from server_lite import app as lite_app
    port = _free_port()
    cfg = uvicorn.Config(lite_app, host="127.0.0.1", port=port, log_level="error")
    server = uvicorn.Server(cfg)
    threading.Thread(target=server.run, daemon=True).start()
    time.sleep(2.0)

    failures, results = [], []
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        pg = b.new_page()
        pg.on("pageerror", lambda e: failures.append(f"pageerror: {e}"))
        pg.goto(f"http://127.0.0.1:{port}/", wait_until="networkidle")
        time.sleep(0.6)
        for m, item_sel in MENUS:
            btn = pg.query_selector(f'.menu[data-m={m}] > button')
            bb = btn.bounding_box()
            pg.mouse.click(bb["x"] + bb["width"] / 2, bb["y"] + bb["height"] / 2)
            time.sleep(0.15)
            ok = pg.evaluate(
                """(sel) => {
                    const it = document.querySelector(sel);
                    if (!it) return {found:false};
                    const r = it.getBoundingClientRect();
                    const top = document.elementFromPoint(r.x + r.width/2, r.y + r.height/2);
                    return {found:true,
                            hit: top ? (top === it || it.contains(top) || (top.closest && top.closest('.dd .item') === it)) : false,
                            topEl: top ? (top.id || top.className || top.tagName) : 'null'};
                }""",
                item_sel,
            )
            results.append((m, ok))
            if not (ok.get("found") and ok.get("hit")):
                failures.append(f"menu '{m}' first item not topmost (got {ok.get('topEl')})")
            # close before next
            pg.mouse.click(bb["x"] + bb["width"] / 2, bb["y"] + bb["height"] / 2)
            time.sleep(0.1)
        b.close()
    server.should_exit = True
    time.sleep(0.4)

    for m, ok in results:
        print(f"  menu {m:9s} -> hit={ok.get('hit')} top={ok.get('topEl')}")
    if failures:
        for f in failures:
            print("FAIL:", f)
        print("BUG_20260521_LITE_MENU_CLIP_FAIL")
        sys.exit(1)
    print("BUG_20260521_LITE_MENU_CLIP_OK")


if __name__ == "__main__":
    main()
