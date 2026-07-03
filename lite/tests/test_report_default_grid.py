"""
LITE-REPORT-DEFAULT-GRID acceptance test.

The editable jspreadsheet grid (report-edit.js) is now the DEFAULT report view;
the old contenteditable table stays available as a "โหมดคลาสสิก" fallback toggle
(used for printing until the grid print CSS is validated).

Checks:
  1. gridDefault      /report opens with the grid visible + populated by default,
                      classic table rendered but OFF-SCREEN (hidden).
  2. toggleClassic    clicking #re-toggle shows the classic table on-screen and moves
                      the grid off-screen; numeric total is IDENTICAL between the two
                      views for the same payload (classic net == sum of grid area cells).
  3. gridPersist      an edit made in grid mode survives a full report reload
                      (existing localStorage seed-hash mechanism).
  4. printHint        the print hint is visible in grid mode, hidden in classic mode.

Emits LITE_REPORT_DEFAULT_GRID_OK on success.

    py -3 lite/tests/test_report_default_grid.py
"""
import socket, threading, time, sys
from pathlib import Path

LITE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LITE))
import uvicorn
from playwright.sync_api import sync_playwright


def _free_port(start=8300):
    for p in range(start, start + 60):
        with socket.socket() as s:
            if s.connect_ex(("127.0.0.1", p)) != 0:
                return p
    raise RuntimeError("no free port")


# One page, two POSITIVE groups (no deduction) so classic net == sum of grid rows.
# net = 30.00 + 20.00 = 50.00
IMG = "data:image/svg+xml;utf8,%3Csvg%20xmlns='http://www.w3.org/2000/svg'%20width='400'%20height='300'%3E%3C/svg%3E"
PAYLOAD = {
    "project": "โครงการทดสอบ Default Grid",
    "date": "2026-07-02",
    "pages": [{
        "idx": 1, "title": "ชั้น 1", "tag": "แปลนชั้น", "imgUrl": IMG, "scaleSet": True,
        "overlays": [],
        "groups": [
            {"label": "พื้นที่อาคาร", "color": "#3b82f6",
             "rows": [{"name": "ห้องโถง", "area": 30.00, "badge": 1}], "subtotal": 30.00, "sign": 1},
            {"label": "พื้นที่ใช้สอย", "color": "#39d98a",
             "rows": [{"name": "ห้องนอน", "area": 20.00, "badge": 2}], "subtotal": 20.00, "sign": 1},
        ],
        "net": 50.00,
    }],
}


def main():
    from server_lite import app as lite_app
    port = _free_port()
    cfg = uvicorn.Config(lite_app, host="127.0.0.1", port=port, log_level="error")
    server = uvicorn.Server(cfg)
    threading.Thread(target=server.run, daemon=True).start()
    time.sleep(2.0)

    failures, checks = [], []

    def chk(name, cond, extra=""):
        checks.append((name, bool(cond)))
        if not cond:
            failures.append(f"{name} {extra}")

    base = f"http://127.0.0.1:{port}"
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        pg = b.new_page()
        pg.on("pageerror", lambda e: failures.append(f"pageerror(report): {e}"))

        # seed payload + clean localStorage, then load fresh
        pg.goto(f"{base}/report", wait_until="domcontentloaded")
        pg.evaluate("(p) => { sessionStorage.setItem('bmaReportPayload', JSON.stringify(p)); localStorage.clear(); }", PAYLOAD)
        pg.goto(f"{base}/report", wait_until="domcontentloaded")
        pg.wait_for_function("window.ReportEditAPI && document.querySelectorAll('#re-host td[data-x]').length > 0")
        time.sleep(0.4)

        # ---- 1. grid is default, classic off-screen ----
        s1 = pg.evaluate("""() => {
          var gridCells = document.querySelectorAll('#re-host td[data-x]').length;
          var wrap = document.getElementById('re-wrap').getBoundingClientRect();
          var sheets = document.getElementById('sheets').getBoundingClientRect();
          return {
            modeGrid: document.body.classList.contains('mode-grid'),
            gridCells: gridCells,
            gridOnScreen: wrap.left >= 0 && wrap.right > 0,
            classicOffScreen: sheets.right < 0,
            sheetCount: document.querySelectorAll('.sheet').length
          };
        }""")
        chk("1 default mode = grid", s1["modeGrid"] is True, s1)
        chk("1 grid populated (cells>0)", s1["gridCells"] > 0, s1)
        chk("1 grid visible on-screen", s1["gridOnScreen"] is True, s1)
        chk("1 classic rendered but off-screen", s1["classicOffScreen"] is True, s1)
        chk("1 classic sheet still in DOM", s1["sheetCount"] == 1, s1)

        # ---- 2. toggle to classic: classic on-screen, grid off-screen, totals identical ----
        pg.click("#re-toggle")
        time.sleep(0.3)
        s2 = pg.evaluate("""() => {
          var wrap = document.getElementById('re-wrap').getBoundingClientRect();
          var sheets = document.querySelector('#sheets .sheet').getBoundingClientRect();
          var grand = (document.querySelector('tr.grand .area')||{}).textContent || '';
          var A = window.ReportEditAPI;
          var gridSum = (A.get('B1')||0) + (A.get('B2')||0);
          return {
            modeClassic: document.body.classList.contains('mode-classic'),
            classicOnScreen: sheets.left >= 0 && sheets.right > 0,
            gridOffScreen: wrap.right < 0,
            grand: grand,
            gridSum: gridSum
          };
        }""")
        chk("2 mode = classic after toggle", s2["modeClassic"] is True, s2)
        chk("2 classic visible on-screen", s2["classicOnScreen"] is True, s2)
        chk("2 grid moved off-screen", s2["gridOffScreen"] is True, s2)
        chk("2 classic net = 50.00", "50.00" in s2["grand"], s2["grand"])
        chk("2 grid sum == classic net (50.00)", abs(s2["gridSum"] - 50.00) < 0.01, s2["gridSum"])

        # toggle back to grid for the persistence edit
        pg.click("#re-toggle")
        time.sleep(0.3)

        # ---- 3. edit in grid persists across reload ----
        pg.evaluate("""() => {
          var A = window.ReportEditAPI;
          A.openEditor(1, 0);      // cell B1 (col=1,row=0)
          // clear existing content so the typed value fully replaces it
          var td = document.querySelector('#re-host td.editor');
          var inp = td && (td.querySelector('input') || td.querySelector('textarea'));
          if(inp){ inp.value=''; inp.selectionStart = inp.selectionEnd = 0; }
          A.typeIntoEditor('99.99');
          A.commitEditor();
        }""")
        time.sleep(0.5)  # let MutationObserver persist to localStorage
        editedBefore = pg.evaluate("() => window.ReportEditAPI.get('B1')")
        chk("3 edit applied in grid (B1=99.99)", abs((editedBefore or 0) - 99.99) < 0.01, editedBefore)

        pg.reload(wait_until="domcontentloaded")
        pg.wait_for_function("window.ReportEditAPI && document.querySelectorAll('#re-host td[data-x]').length > 0")
        time.sleep(0.4)
        editedAfter = pg.evaluate("() => window.ReportEditAPI.get('B1')")
        chk("3 edit survived reload (B1=99.99)", abs((editedAfter or 0) - 99.99) < 0.01, editedAfter)

        # ---- 4. print hint visible in grid, hidden in classic ----
        h_grid = pg.evaluate("() => getComputedStyle(document.getElementById('printHint')).display")
        chk("4 print hint visible in grid mode", h_grid != "none", h_grid)
        pg.click("#re-toggle")
        time.sleep(0.3)
        h_classic = pg.evaluate("() => getComputedStyle(document.getElementById('printHint')).display")
        chk("4 print hint hidden in classic mode", h_classic == "none", h_classic)

        b.close()
    server.should_exit = True
    time.sleep(0.4)

    for name, ok in checks:
        print(f"  [{'OK' if ok else 'XX'}] {name}")
    if failures:
        for f in failures:
            print("FAIL:", f)
        print("LITE_REPORT_DEFAULT_GRID_FAIL")
        sys.exit(1)
    print(f"LITE_REPORT_DEFAULT_GRID_OK ({len(checks)}/{len(checks)})")


if __name__ == "__main__":
    main()
