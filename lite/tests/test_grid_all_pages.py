"""
LITE report-truth slice B/4 (REVIEW_LITE_LAYER_REPORT_20260704.md ledger
B-2 + B-3) acceptance test.

B-2: the default report VIEW (the editable jspreadsheet grid) used to flatten
only payload.pages[0] -- a multi-page project silently lost every page after
the first, with no warning. Fix: gridRows() (lite-report.html) now flattens
EVERY page, with a text-only page-title separator row inserted before each
page's own rows (only when there is more than one page, so a single-page
project's grid is byte-identical to the old behavior -- see check d).

B-3: the grid didn't know which rows were deduction rows, so building a
subtotal by naively clicking through cells (the natural workflow) silently
ADDED deduction areas instead of subtracting them; the user had to remember
to click the "-" operator button themselves before every ded-row pick. Fix:
report-edit.js now carries a per-row `sign` (from the payload group's own
role-derived sign) and the cell-picker auto-defaults to "-B{n}" for a
deduction row UNLESS the user already typed/clicked an explicit operator
(which always wins) -- see checks b/c.

In passing (flagged, not a full B-10 fix): the localStorage edit-hash now
folds in each row's page index, so two rows with the identical name+area on
DIFFERENT pages (very plausible now that the grid shows every floor) no
longer share a localStorage key -- see check e. This does NOT fix B-10's
broader issues (cross-project collision, no orphan GC); those are unrelated
and out of scope for this slice.

Checks (LITE_GRID_ALL_PAGES_OK on 5/5):
  (a) allPagesPresentOk   a 3-page payload's grid contains all 3 pages'
                          rows (7 total: 3 page-separators + 4 item rows),
                          in the right page-grouped order.
  (b) dedNegativeOk       clicking cell-by-cell through mixed-sign rows with
                          NO explicit operator clicks auto-produces a
                          formula where the deduction row's ref is negated.
  (c) signedSumOk         that subtotal's computed VALUE equals an
                          independently (Python-side) hand-computed signed
                          sum: 50 - 5 + 30 = 75.
  (d) singlePageAsBeforeOk a single-page payload's grid has exactly the
                          item rows (no separator row prepended) -- same
                          shape as the pre-slice gridRows().
  (e) hashDistinguishesPagesOk  ReportEdit.mount() with the SAME name+area
                          on two different `page` values produces two
                          DIFFERENT seed hashes; an edit saved under page 1
                          does NOT leak into page 3's identical-looking row,
                          and DOES restore when page 1 is remounted again.

    py -3 lite/tests/test_grid_all_pages.py
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

PAYLOAD_MULTI = {
    "project": "โครงการทดสอบ Grid All Pages",
    "date": "2026-07-04",
    "pages": [
        {"idx": 1, "title": "ชั้น 1", "tag": "แปลนชั้น", "imgUrl": IMG, "scaleSet": True, "overlays": [],
         "groups": [
             {"label": "พื้นที่อาคาร", "color": "#3b82f6", "sign": 1,
              "rows": [{"name": "ห้อง A", "area": 50.00, "badge": 1}], "subtotal": 50.00},
             {"label": "ช่องว่าง/หัก", "color": "#ff6b6b", "sign": -1,
              "rows": [{"name": "ช่องบันได", "area": 5.00, "badge": 2}], "subtotal": 5.00},
         ], "net": 45.00},
        {"idx": 2, "title": "ชั้น 2", "tag": "แปลนชั้น", "imgUrl": IMG, "scaleSet": True, "overlays": [],
         "groups": [
             {"label": "พื้นที่อาคาร", "color": "#3b82f6", "sign": 1,
              "rows": [{"name": "ห้อง B", "area": 30.00, "badge": 1}], "subtotal": 30.00},
         ], "net": 30.00},
        {"idx": 3, "title": "ที่ดิน", "tag": "ผังบริเวณ", "imgUrl": IMG, "scaleSet": True, "overlays": [],
         # deliberately SAME name+area as page 1's "ห้อง A" row, to exercise
         # the page-aware localStorage hash (check e) at the payload level too
         "groups": [
             {"label": "พื้นที่อาคาร", "color": "#3b82f6", "sign": 1,
              "rows": [{"name": "ห้อง A", "area": 50.00, "badge": 1}], "subtotal": 50.00},
         ], "net": 50.00},
    ],
}

PAYLOAD_SINGLE = {
    "project": "โครงการทดสอบ Grid Single Page",
    "date": "2026-07-04",
    "pages": [
        {"idx": 1, "title": "ชั้น 1", "tag": "แปลนชั้น", "imgUrl": IMG, "scaleSet": True, "overlays": [],
         "groups": [
             {"label": "พื้นที่อาคาร", "color": "#3b82f6", "sign": 1,
              "rows": [{"name": "ห้องโถง", "area": 30.00, "badge": 1}], "subtotal": 30.00},
             {"label": "พื้นที่ใช้สอย", "color": "#39d98a", "sign": 1,
              "rows": [{"name": "ห้องนอน", "area": 20.00, "badge": 2}], "subtotal": 20.00},
         ], "net": 50.00},
    ],
}


def _free_port(start=8630):
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
        pg.goto(f"{base}/report", wait_until="domcontentloaded")
        pg.wait_for_function("window.ReportEditAPI && document.querySelectorAll('#re-host td[data-x]').length > 0")
        time.sleep(0.4)

        sa = pg.evaluate("""() => {
          var A = window.ReportEditAPI;
          var ids = A.rowIdsSnapshot();
          var rows = ids.map(function(_, i) {
            return { name: A.rawGet('A' + (i + 1)), area: A.rawGet('B' + (i + 1)) };
          });
          return { ids: ids, rows: rows };
        }""")
        rows = sa["rows"]
        allPagesPresentOk = (
            len(rows) == 7
            and "หน้า 1" in (rows[0]["name"] or "") and "ชั้น 1" in (rows[0]["name"] or "")
            and rows[1]["name"] == "ห้อง A" and abs(float(rows[1]["area"] or 0) - 50.0) < 0.01
            and rows[2]["name"] == "ช่องบันได" and abs(float(rows[2]["area"] or 0) - 5.0) < 0.01
            and "หน้า 2" in (rows[3]["name"] or "") and "ชั้น 2" in (rows[3]["name"] or "")
            and rows[4]["name"] == "ห้อง B" and abs(float(rows[4]["area"] or 0) - 30.0) < 0.01
            and "หน้า 3" in (rows[5]["name"] or "") and "ที่ดิน" in (rows[5]["name"] or "")
            and rows[6]["name"] == "ห้อง A" and abs(float(rows[6]["area"] or 0) - 50.0) < 0.01
        )
        chk("(a) all 3 pages present + correctly grouped/ordered", allPagesPresentOk, rows)

        # (b)+(c): build a subtotal by clicking B2(+50), B3(ded,-5), B5(+30)
        # in sequence with NO explicit operator clicks -> auto-signed formula.
        sbc = pg.evaluate("""() => {
          var A = window.ReportEditAPI;
          A.insertSubtotalFormula('รวม', '');
          var idsAfter = A.rowIdsSnapshot();
          var subIdx = idsAfter.length - 1;   // index 7
          A.openEditor(1, subIdx);
          A.typeIntoEditor('=');
          A.clickCell(1, 1); var v1 = A.editorValue();   // ห้อง A  (+50)
          A.clickCell(1, 2); var v2 = A.editorValue();   // ช่องบันได (ded, -5)
          A.clickCell(1, 4); var v3 = A.editorValue();   // ห้อง B  (+30)
          A.commitEditor();
          var val = A.get('B' + (subIdx + 1));
          var raw = A.rawGet('B' + (subIdx + 1));
          return { v1: v1, v2: v2, v3: v3, val: val, raw: raw };
        }""")
        dedNegativeOk = (sbc["v1"] == "=B2" and sbc["v2"] == "=B2-B3" and sbc["v3"] == "=B2-B3+B5")
        chk("(b) ded row auto-negated with no explicit op click", dedNegativeOk, sbc)

        expected_signed_sum = 50.0 - 5.0 + 30.0  # independent ground truth, not read from app
        signedSumOk = abs((sbc["val"] or 0) - expected_signed_sum) < 0.01
        chk(f"(c) subtotal value == signed sum ({expected_signed_sum:.2f})", signedSumOk, sbc["val"])

        # ------------------------------------------------------------------
        # (d) single-page payload behaves as before (no separator row)
        # ------------------------------------------------------------------
        pg.evaluate(
            "(p) => { sessionStorage.setItem('bmaReportPayload', JSON.stringify(p)); localStorage.clear(); }",
            PAYLOAD_SINGLE,
        )
        pg.reload(wait_until="domcontentloaded")
        pg.wait_for_function("window.ReportEditAPI && document.querySelectorAll('#re-host td[data-x]').length > 0")
        time.sleep(0.4)
        sd = pg.evaluate("""() => {
          var A = window.ReportEditAPI;
          var ids = A.rowIdsSnapshot();
          return {
            len: ids.length,
            name0: A.rawGet('A1'), area0: A.get('B1'),
            name1: A.rawGet('A2'), area1: A.get('B2')
          };
        }""")
        singlePageAsBeforeOk = (
            sd["len"] == 2 and sd["name0"] == "ห้องโถง" and abs((sd["area0"] or 0) - 30.0) < 0.01
            and sd["name1"] == "ห้องนอน" and abs((sd["area1"] or 0) - 20.0) < 0.01
        )
        chk("(d) single-page grid unchanged (no separator row, 2 rows)", singlePageAsBeforeOk, sd)

        # ------------------------------------------------------------------
        # (e) localStorage hash distinguishes same-name/area rows on
        #     different pages -- edit saved under page 1 does not leak into
        #     page 3's identical-looking row, and DOES restore on remount.
        # ------------------------------------------------------------------
        se = pg.evaluate("""async () => {
          var host = document.getElementById('re-host');
          var rowsA = [{name:'ห้อง A', area:50, sign:1, page:1}];
          var rowsB = [{name:'ห้อง A', area:50, sign:1, page:3}];

          ReportEdit.mount(host, rowsA);
          var hashA = window.ReportEditAPI.seedHash();

          // edit B1 -> 999
          window.ReportEditAPI.openEditor(1, 0);
          var td = document.querySelector('#re-host td.editor');
          var inp = td && (td.querySelector('input') || td.querySelector('textarea'));
          if (inp) { inp.value=''; inp.selectionStart = inp.selectionEnd = 0; }
          window.ReportEditAPI.typeIntoEditor('999');
          window.ReportEditAPI.commitEditor();
          await new Promise(function(r){ setTimeout(r, 500); });   // let MutationObserver persist
          var b1AfterEdit = window.ReportEditAPI.get('B1');

          ReportEdit.mount(host, rowsB);
          var hashB = window.ReportEditAPI.seedHash();
          var b1OnPageB = window.ReportEditAPI.get('B1');   // must be baseline 50, NOT 999

          ReportEdit.mount(host, rowsA);   // remount page 1 -> should restore 999
          var b1Restored = window.ReportEditAPI.get('B1');

          return { hashA: hashA, hashB: hashB, b1AfterEdit: b1AfterEdit, b1OnPageB: b1OnPageB, b1Restored: b1Restored };
        }""")
        hashDistinguishesPagesOk = (
            se["hashA"] != se["hashB"]
            and abs((se["b1AfterEdit"] or 0) - 999.0) < 0.01
            and abs((se["b1OnPageB"] or 0) - 50.0) < 0.01
            and abs((se["b1Restored"] or 0) - 999.0) < 0.01
        )
        chk("(e) page-aware hash: no cross-page leak, same-page restores", hashDistinguishesPagesOk, se)

        b.close()

    server.should_exit = True
    time.sleep(0.4)

    print("\n=== LITE-GRID-ALL-PAGES checks ===")
    for name, ok in checks:
        print(f"  [{'OK' if ok else 'XX'}] {name}")
    if errs:
        print("  pageerrors:", errs[:6])
        failures.append(f"page errors: {errs[:6]}")
    if failures:
        for f in failures:
            print("FAIL:", f)
        print("LITE_GRID_ALL_PAGES_FAIL")
        sys.exit(1)
    print(f"LITE_GRID_ALL_PAGES_OK ({len(checks)}/{len(checks)})")


if __name__ == "__main__":
    main()
