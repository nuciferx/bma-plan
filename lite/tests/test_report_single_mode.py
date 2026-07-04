"""
LITE report-truth slice C/4 (REVIEW_LITE_LAYER_REPORT_20260704.md ledger
S-1 ทาง ก, user GO) acceptance test.

/report has a SINGLE view now: the editable jspreadsheet grid IS the print
output. The old contenteditable "classic" per-page sheet view + the
view-toggle button (#re-toggle) were removed entirely (S-1 ทาง ก). This
test guards the structural invariant ("one view, grid always mounted, grid
prints") and the two regressions the spec explicitly flagged:
  - reportVars (FAR/OSR/... project-metrics card) used to render ONLY in
    the classic view -- it is now re-homed into #re-wrap (alongside the
    grid) so it isn't silently lost.
  - slice B's "grid shows ALL pages" must still hold after slice C's
    structural removal (regression check).

Checks (LITE_REPORT_SINGLE_MODE_OK on 5/5):
  (a) classicGoneOk        no #sheets element, no #re-toggle button, no
                          .sheet element anywhere in the DOM.
  (b) gridAutoMountOk      the grid is mounted + populated on load with NO
                          click/toggle interaction at all.
  (c) printCssOk           under print media emulation, #re-wrap is NOT
                          display:none (grid prints) and .toolbar IS
                          display:none (chrome hidden); the raw print
                          stylesheet text also no longer contains the old
                          force-classic rule.
  (d) reportVarsPrintedOk  a payload with reportVars renders a .rvcard in
                          #re-wrap, and it stays visible (not display:none)
                          under print media emulation too.
  (e) multiPageRegressionOk  a 3-page payload's grid still contains all 3
                          pages' rows (slice B regression, post slice-C
                          structural removal).

    py -3 lite/tests/test_report_single_mode.py
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

IMG = "data:image/svg+xml;utf8,%3Csvg%20xmlns='http://www.w3.org/2000/svg'%20width='400'%20height='300'%3E%3C/svg%3E"

PAYLOAD_VARS = {
    "project": "โครงการทดสอบ Single Mode",
    "date": "2026-07-04",
    "pages": [{
        "idx": 1, "title": "ชั้น 1", "tag": "แปลนชั้น", "imgUrl": IMG, "scaleSet": True, "overlays": [],
        "groups": [{"label": "พื้นที่อาคาร", "color": "#3b82f6", "sign": 1,
                    "rows": [{"name": "ห้อง A", "area": 40.00, "badge": 1}], "subtotal": 40.00}],
        "net": 40.00,
    }],
    "reportVars": [
        {"name": "FAR", "unit": "", "value": 1.2, "err": None},
        {"name": "OSR", "unit": "%", "value": 15, "err": None},
    ],
}

PAYLOAD_MULTI = {
    "project": "โครงการทดสอบ Multi Page Regression",
    "date": "2026-07-04",
    "pages": [
        {"idx": 1, "title": "ชั้น 1", "tag": "แปลนชั้น", "imgUrl": IMG, "scaleSet": True, "overlays": [],
         "groups": [{"label": "พื้นที่อาคาร", "color": "#3b82f6", "sign": 1,
                     "rows": [{"name": "ห้อง A", "area": 50.00, "badge": 1}], "subtotal": 50.00}], "net": 50.00},
        {"idx": 2, "title": "ชั้น 2", "tag": "แปลนชั้น", "imgUrl": IMG, "scaleSet": True, "overlays": [],
         "groups": [{"label": "พื้นที่อาคาร", "color": "#3b82f6", "sign": 1,
                     "rows": [{"name": "ห้อง B", "area": 30.00, "badge": 1}], "subtotal": 30.00}], "net": 30.00},
        {"idx": 3, "title": "ที่ดิน", "tag": "ผังบริเวณ", "imgUrl": IMG, "scaleSet": True, "overlays": [],
         "groups": [{"label": "พื้นที่อาคาร", "color": "#3b82f6", "sign": 1,
                     "rows": [{"name": "ห้อง C", "area": 20.00, "badge": 1}], "subtotal": 20.00}], "net": 20.00},
    ],
}


def _free_port(start=8660):
    for p in range(start, start + 60):
        with socket.socket() as s:
            if s.connect_ex(("127.0.0.1", p)) != 0:
                return p
    raise RuntimeError("no free port")


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
        errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))

        # ------------------------------------------------------------------
        # (a) + (b): standalone load (bundled SAMPLE, no payload needed)
        # ------------------------------------------------------------------
        pg.goto(f"{base}/report", wait_until="domcontentloaded")
        pg.wait_for_function("window.ReportEditAPI && document.querySelectorAll('#re-host td[data-x]').length > 0")
        time.sleep(0.4)

        dom = pg.evaluate("""() => ({
          hasSheets: !!document.getElementById('sheets'),
          hasToggle: !!document.getElementById('re-toggle'),
          hasSheetEl: !!document.querySelector('.sheet'),
          gridCells: document.querySelectorAll('#re-host td[data-x]').length
        })""")
        classicGoneOk = (not dom["hasSheets"]) and (not dom["hasToggle"]) and (not dom["hasSheetEl"])
        chk("(a) classic DOM gone (#sheets/#re-toggle/.sheet)", classicGoneOk, dom)

        gridAutoMountOk = dom["gridCells"] > 0
        chk("(b) grid auto-mounts + populates on load (no click)", gridAutoMountOk, dom)

        # ------------------------------------------------------------------
        # (c) print CSS: #re-wrap must NOT be hidden, .toolbar MUST be hidden
        # ------------------------------------------------------------------
        pg.emulate_media(media="print")
        printState = pg.evaluate("""() => {
          var reWrap = document.getElementById('re-wrap');
          var toolbar = document.querySelector('.toolbar');
          var styleText = Array.from(document.querySelectorAll('style')).map(function(s){return s.textContent;}).join('\\n');
          return {
            reWrapDisplay: reWrap ? getComputedStyle(reWrap).display : null,
            toolbarDisplay: toolbar ? getComputedStyle(toolbar).display : null,
            hasOldForceClassicRule: /#re-wrap\\s*\\{[^}]*display:\\s*none/i.test(styleText)
          };
        }""")
        pg.emulate_media(media="screen")
        printCssOk = (
            printState["reWrapDisplay"] != "none"
            and printState["toolbarDisplay"] == "none"
            and printState["hasOldForceClassicRule"] is False
        )
        chk("(c) print CSS: #re-wrap visible, .toolbar hidden, no old force-classic rule", printCssOk, printState)

        # ------------------------------------------------------------------
        # (d) reportVars renders in #re-wrap and stays visible under print
        # ------------------------------------------------------------------
        pg.evaluate(
            "(p) => { sessionStorage.setItem('bmaReportPayload', JSON.stringify(p)); localStorage.clear(); }",
            PAYLOAD_VARS,
        )
        pg.reload(wait_until="domcontentloaded")
        pg.wait_for_function("window.ReportEditAPI && document.querySelectorAll('#re-host td[data-x]').length > 0")
        time.sleep(0.4)
        rv1 = pg.evaluate("""() => {
          var card = document.querySelector('#re-wrap .rvcard');
          return { present: !!card, text: card ? card.innerText : '' };
        }""")
        pg.emulate_media(media="print")
        rv2 = pg.evaluate("""() => {
          var card = document.querySelector('#re-wrap .rvcard');
          return { display: card ? getComputedStyle(card).display : null };
        }""")
        pg.emulate_media(media="screen")
        reportVarsPrintedOk = (
            rv1["present"] and "FAR" in rv1["text"] and "OSR" in rv1["text"] and rv2["display"] != "none"
        )
        chk("(d) reportVars card present in #re-wrap + visible under print", reportVarsPrintedOk, {**rv1, **rv2})

        # ------------------------------------------------------------------
        # (e) slice B regression: multi-page payload's grid still shows ALL pages
        # ------------------------------------------------------------------
        pg.evaluate(
            "(p) => { sessionStorage.setItem('bmaReportPayload', JSON.stringify(p)); localStorage.clear(); }",
            PAYLOAD_MULTI,
        )
        pg.reload(wait_until="domcontentloaded")
        pg.wait_for_function("window.ReportEditAPI && document.querySelectorAll('#re-host td[data-x]').length > 0")
        time.sleep(0.4)
        me = pg.evaluate("""() => {
          var A = window.ReportEditAPI;
          var ids = A.rowIdsSnapshot();
          var rows = ids.map(function(_, i) { return A.rawGet('A' + (i + 1)); });
          return { rows: rows };
        }""")
        rows = me["rows"]
        multiPageRegressionOk = (
            len(rows) == 6  # 3 separators + 3 item rows
            and "หน้า 1" in (rows[0] or "") and rows[1] == "ห้อง A"
            and "หน้า 2" in (rows[2] or "") and rows[3] == "ห้อง B"
            and "หน้า 3" in (rows[4] or "") and rows[5] == "ห้อง C"
        )
        chk("(e) multi-page regression: grid still shows all 3 pages", multiPageRegressionOk, rows)

        b.close()

    server.should_exit = True
    time.sleep(0.4)

    print("\n=== LITE-REPORT-SINGLE-MODE checks ===")
    for name, ok in checks:
        print(f"  [{'OK' if ok else 'XX'}] {name}")
    if errs:
        print("  pageerrors:", errs[:6])
        failures.append(f"page errors: {errs[:6]}")
    if failures:
        for f in failures:
            print("FAIL:", f)
        print("LITE_REPORT_SINGLE_MODE_FAIL")
        sys.exit(1)
    print(f"LITE_REPORT_SINGLE_MODE_OK ({len(checks)}/{len(checks)})")


if __name__ == "__main__":
    main()
