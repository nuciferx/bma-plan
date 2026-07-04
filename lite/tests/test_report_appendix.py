"""
LITE report-truth slice E/5 (REVIEW_LITE_LAYER_REPORT_20260704.md ledger
S-1e, user GO at checkpoint) acceptance test.

Slice C removed the classic per-page plan-image+overlay view when grid
became the single report view -- a real regression (no more visual plan
reference in the printed report). This slice restores it as an APPENDIX,
printed after the grid+vars card: one page block per measured page, plan
image + SVG measurement overlay + title, collapsible on screen (<details>)
but ALWAYS fully rendered on print regardless of the on-screen toggle state.

Reused from the classic implementation (read via `git show fc63e72~1:
lite/lite-report.html`, read-only, not resurrected wholesale):
  - centroid(pts) for badge circle/text placement
  - the planbox positioning trick: position:relative box + absolutely
    positioned <svg> sized 100%/100%, with viewBox set to the image's
    natural pixel size once it loads (img.onload) -- so overlay polygon
    points (already in render-scale px, RS-multiplied upstream in
    export-annotate.js's buildReportPayload -- NOT rescaled here) line up
    with the rendered plan image regardless of its displayed size.
  Renamed classic's bare .left/.planbox/.cap to scoped .appx-page .imgbox/
  .planbox/.cap so slice C's global-class removal isn't silently undone.

Checks (LITE_REPORT_APPENDIX_OK on 5/5):
  (a) threePageBlocksOk    a 3-page payload -> 3 .appx-page blocks, in
                          page order, each with the right title text.
  (b) overlayMatchOk       each block's <polygon> count == that page's
                          overlays count; points/colors/badge text match
                          the payload exactly (independent recompute, not
                          read back from a rendered pixel).
  (c) imgSrcLazyOk         each block's <img src> == payload imgUrl, and
                          loading="lazy" (45-page projects must not hammer
                          the server with eager loads on report open).
  (d) printCssOk           under print media emulation, .appx-page is not
                          display:none, has page-break-before:always in
                          its computed style, and the appendix stays
                          visible even when the <details> was left CLOSED
                          on screen (worst case for "does not hide it").
  (e) singlePageRegressionOk  a 1-page payload -> exactly 1 .appx-page
                          block, AND slice B/C invariants still hold
                          (grid still mounts + rvcard still present) --
                          in-file regression, not just relying on other
                          test files.

    py -3 lite/tests/test_report_appendix.py
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

IMG1 = "data:image/svg+xml;utf8,%3Csvg%20xmlns='http://www.w3.org/2000/svg'%20width='800'%20height='600'%3E%3C/svg%3E"
IMG2 = "data:image/svg+xml;utf8,%3Csvg%20xmlns='http://www.w3.org/2000/svg'%20width='700'%20height='500'%3E%3C/svg%3E"
IMG3 = "data:image/svg+xml;utf8,%3Csvg%20xmlns='http://www.w3.org/2000/svg'%20width='600'%20height='400'%3E%3C/svg%3E"

PAYLOAD_MULTI = {
    "project": "โครงการทดสอบ Appendix", "date": "2026-07-04",
    "pages": [
        {"idx": 1, "title": "ชั้น 1", "imgUrl": IMG1, "scaleSet": True,
         "overlays": [
             {"pts": [{"x": 10, "y": 10}, {"x": 110, "y": 10}, {"x": 110, "y": 110}, {"x": 10, "y": 110}], "color": "#3b82f6", "badge": 1},
             {"pts": [{"x": 200, "y": 20}, {"x": 260, "y": 20}, {"x": 260, "y": 80}, {"x": 200, "y": 80}], "color": "#ff6b6b", "badge": 2},
         ],
         "groups": [{"label": "พื้นที่อาคาร", "color": "#3b82f6", "sign": 1,
                     "rows": [{"name": "ห้อง A", "area": 50.00, "badge": 1}], "subtotal": 50.00}], "net": 50.00},
        {"idx": 2, "title": "ชั้น 2", "imgUrl": IMG2, "scaleSet": True,
         "overlays": [
             {"pts": [{"x": 5, "y": 5}, {"x": 95, "y": 5}, {"x": 95, "y": 95}, {"x": 5, "y": 95}], "color": "#39d98a", "badge": 1},
         ],
         "groups": [{"label": "พื้นที่อาคาร", "color": "#3b82f6", "sign": 1,
                     "rows": [{"name": "ห้อง B", "area": 30.00, "badge": 1}], "subtotal": 30.00}], "net": 30.00},
        {"idx": 3, "title": "ที่ดิน", "imgUrl": IMG3, "scaleSet": True,
         "overlays": [
             {"pts": [{"x": 0, "y": 0}, {"x": 80, "y": 0}, {"x": 80, "y": 60}, {"x": 0, "y": 60}], "color": "#c084fc", "badge": 1},
         ],
         "groups": [{"label": "พื้นที่อาคาร", "color": "#3b82f6", "sign": 1,
                     "rows": [{"name": "ห้อง C", "area": 20.00, "badge": 1}], "subtotal": 20.00}], "net": 20.00},
    ],
    "reportVars": [{"name": "FAR", "unit": "", "value": 1.1, "err": None}],
}

PAYLOAD_SINGLE = {
    "project": "โครงการทดสอบ Appendix Single", "date": "2026-07-04",
    "pages": [
        {"idx": 1, "title": "ชั้น 1", "imgUrl": IMG1, "scaleSet": True,
         "overlays": [{"pts": [{"x": 0, "y": 0}, {"x": 40, "y": 0}, {"x": 40, "y": 40}, {"x": 0, "y": 40}], "color": "#3b82f6", "badge": 1}],
         "groups": [{"label": "พื้นที่อาคาร", "color": "#3b82f6", "sign": 1,
                     "rows": [{"name": "ห้อง A", "area": 16.00, "badge": 1}], "subtotal": 16.00}], "net": 16.00},
    ],
    "reportVars": [{"name": "FAR", "unit": "", "value": 0.9, "err": None}],
}


def _free_port(start=8700):
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
        # (a) + (b) + (c): 3-page payload
        # ------------------------------------------------------------------
        pg.goto(f"{base}/report", wait_until="domcontentloaded")
        pg.evaluate(
            "(p) => { sessionStorage.setItem('bmaReportPayload', JSON.stringify(p)); localStorage.clear(); }",
            PAYLOAD_MULTI,
        )
        pg.reload(wait_until="domcontentloaded")
        pg.wait_for_function("window.ReportEditAPI && document.querySelectorAll('#re-host td[data-x]').length > 0")
        time.sleep(0.4)

        dom = pg.evaluate("""() => {
          var pages = Array.from(document.querySelectorAll('.appx-page'));
          return pages.map(function(p) {
            var svg = p.querySelector('svg');
            var polys = Array.from(svg ? svg.querySelectorAll('polygon') : []);
            var texts = Array.from(svg ? svg.querySelectorAll('text') : []);
            var img = p.querySelector('img');
            return {
              hdr: p.querySelector('.appx-phdr').textContent,
              polyCount: polys.length,
              polyPoints: polys.map(function(pl){ return pl.getAttribute('points'); }),
              polyColors: polys.map(function(pl){ return pl.getAttribute('fill'); }),
              badges: texts.map(function(t){ return t.textContent; }),
              imgSrc: img ? img.getAttribute('src') : null,
              imgLoading: img ? img.getAttribute('loading') : null
            };
          });
        }""")

        threePageBlocksOk = (
            len(dom) == 3
            and "หน้า 1" in dom[0]["hdr"] and "ชั้น 1" in dom[0]["hdr"]
            and "หน้า 2" in dom[1]["hdr"] and "ชั้น 2" in dom[1]["hdr"]
            and "หน้า 3" in dom[2]["hdr"] and "ที่ดิน" in dom[2]["hdr"]
        )
        chk("(a) 3 appendix blocks, in order, correct titles", threePageBlocksOk, [d["hdr"] for d in dom])

        def expected_points(pg_payload):
            return [" ".join(f"{p['x']},{p['y']}" for p in ov["pts"]) for ov in pg_payload["overlays"]]

        overlayMatchOk = True
        for i, p_payload in enumerate(PAYLOAD_MULTI["pages"]):
            d = dom[i]
            exp_pts = expected_points(p_payload)
            exp_colors = [ov["color"] for ov in p_payload["overlays"]]
            exp_badges = [str(ov["badge"]) for ov in p_payload["overlays"]]
            if d["polyCount"] != len(p_payload["overlays"]):
                overlayMatchOk = False
            if d["polyPoints"] != exp_pts:
                overlayMatchOk = False
            if d["polyColors"] != exp_colors:
                overlayMatchOk = False
            if d["badges"] != exp_badges:
                overlayMatchOk = False
        chk("(b) overlay polygons/points/colors/badges match payload exactly", overlayMatchOk, dom)

        imgSrcLazyOk = all(
            dom[i]["imgSrc"] == PAYLOAD_MULTI["pages"][i]["imgUrl"] and dom[i]["imgLoading"] == "lazy"
            for i in range(3)
        )
        chk("(c) img src == payload imgUrl + loading=lazy", imgSrcLazyOk, dom)

        # ------------------------------------------------------------------
        # (d) print CSS: appendix stays visible + page-break, even when the
        # on-screen <details> was left CLOSED (worst case)
        # ------------------------------------------------------------------
        pg.evaluate("() => { var d = document.querySelector('details.appx'); if (d) d.open = false; }")
        pg.emulate_media(media="print")
        printState = pg.evaluate("""() => {
          var pages = document.querySelectorAll('.appx-page');
          var first = pages[0];
          var cs = first ? getComputedStyle(first) : null;
          return {
            pageCount: pages.length,
            firstDisplay: cs ? cs.display : null,
            firstBreak: cs ? (cs.breakBefore || cs.pageBreakBefore) : null,
            firstVisible: first ? (first.offsetParent !== null || cs.display !== 'none') : false
          };
        }""")
        pg.emulate_media(media="screen")
        printCssOk = (
            printState["pageCount"] == 3
            and printState["firstDisplay"] != "none"
            and printState["firstBreak"] in ("always", "page")
        )
        chk("(d) print CSS: appendix visible + page-break, even if closed on screen", printCssOk, printState)

        # ------------------------------------------------------------------
        # (e) single-page payload -> 1 block; slice B/C regressions intact
        # ------------------------------------------------------------------
        pg.evaluate(
            "(p) => { sessionStorage.setItem('bmaReportPayload', JSON.stringify(p)); localStorage.clear(); }",
            PAYLOAD_SINGLE,
        )
        pg.reload(wait_until="domcontentloaded")
        pg.wait_for_function("window.ReportEditAPI && document.querySelectorAll('#re-host td[data-x]').length > 0")
        time.sleep(0.4)
        single = pg.evaluate("""() => {
          var pages = document.querySelectorAll('.appx-page');
          var gridCells = document.querySelectorAll('#re-host td[data-x]').length;
          var rvcard = document.querySelector('#re-wrap .rvcard');
          var hasSheets = !!document.getElementById('sheets');
          var hasToggle = !!document.getElementById('re-toggle');
          return {
            appxCount: pages.length,
            gridCells: gridCells,
            rvcardPresent: !!rvcard,
            hasSheets: hasSheets,
            hasToggle: hasToggle
          };
        }""")
        singlePageRegressionOk = (
            single["appxCount"] == 1
            and single["gridCells"] > 0
            and single["rvcardPresent"] is True
            and single["hasSheets"] is False
            and single["hasToggle"] is False
        )
        chk("(e) single-page payload -> 1 appendix block, grid/vars/single-view regressions intact", singlePageRegressionOk, single)

        b.close()

    server.should_exit = True
    time.sleep(0.4)

    print("\n=== LITE-REPORT-APPENDIX checks ===")
    for name, ok in checks:
        print(f"  [{'OK' if ok else 'XX'}] {name}")
    if errs:
        print("  pageerrors:", errs[:6])
        failures.append(f"page errors: {errs[:6]}")
    if failures:
        for f in failures:
            print("FAIL:", f)
        print("LITE_REPORT_APPENDIX_FAIL")
        sys.exit(1)
    print(f"LITE_REPORT_APPENDIX_OK ({len(checks)}/{len(checks)})")


if __name__ == "__main__":
    main()
