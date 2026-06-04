"""
LITE-REPORT (INV-2026-05-21-002) acceptance + regression guard.

Editable web report page: Export → opens /report in a new window with a
sessionStorage hand-off, renders one A4-landscape sheet per measured page
(plan image + overlay left, area table grouped by category right), lets the
user edit text inline while area numbers stay read-only, then browser-print
to PDF.

This test (no real PDF needed — it injects PS directly):
  1. main app: inject PS with a gfa square + a deduction square at a known
     scale, call buildReportPayload(), assert grouping / area math (via the
     vendored polyMetrics) / overlay px = pt*RS / net sign.
  2. /report: seed that payload into sessionStorage, reload, assert sheets
     render, area cells are READ-ONLY, row-name cells are contenteditable,
     net total prints.
  3. /report standalone: open with no payload -> bundled SAMPLE renders.

Emits LITE_REPORT_OK on success.

    py -3 lite/tests/test_report.py
"""
import socket, threading, time, sys, json
from pathlib import Path

LITE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LITE))
import uvicorn
from playwright.sync_api import sync_playwright


def _free_port(start=8240):
    for p in range(start, start + 60):
        with socket.socket() as s:
            if s.connect_ex(("127.0.0.1", p)) != 0:
                return p
    raise RuntimeError("no free port")


# gfa square 100pt side @ pts_per_m=10 -> 10m side -> 100.00 m2
# ded square  50pt side @ pts_per_m=10 ->  5m side ->  25.00 m2
# net = 100 - 25 = 75.00 ; overlay px = pt*RS(1.5) -> gfa corner (100,0)->(150,0)
INJECT_PS = """() => {
  PS[1] = { scale:{pts_per_m:10}, annotations:[], objects:[
    {id:101,catId:'gfa',semanticTag:'gross_floor_area',kind:'poly',counting:false,
     pts:[{x:0,y:0},{x:100,y:0},{x:100,y:100},{x:0,y:100}]},
    {id:102,catId:'ded',semanticTag:'deduction_opening',kind:'poly',counting:false,
     pts:[{x:0,y:0},{x:50,y:0},{x:50,y:50},{x:0,y:50}]}
  ]};
  projectInfo.name = 'โครงการทดสอบ';
  return buildReportPayload();
}"""


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
        pg.on("pageerror", lambda e: failures.append(f"pageerror(app): {e}"))
        pg.goto(f"{base}/", wait_until="networkidle")
        time.sleep(0.6)

        # ---- 1. buildReportPayload() against real vendored polyMetrics ----
        payload = pg.evaluate(INJECT_PS)
        chk("payload.pages==1", len(payload.get("pages", [])) == 1, payload)
        page0 = (payload.get("pages") or [{}])[0]
        groups = page0.get("groups", [])
        chk("two groups (gfa+ded)", len(groups) == 2, groups)
        gfa = next((g for g in groups if g["sign"] == 1), None)
        ded = next((g for g in groups if g["sign"] == -1), None)
        chk("gfa subtotal 100", gfa and abs(gfa["subtotal"] - 100.0) < 0.01, gfa)
        chk("ded subtotal 25", ded and abs(ded["subtotal"] - 25.0) < 0.01, ded)
        chk("net = 75 (ded subtracted)", abs(page0.get("net", 0) - 75.0) < 0.01, page0.get("net"))
        # overlay px = pt*RS(1.5): gfa second corner (100,0) -> (150,0)
        ov = page0.get("overlays", [])
        chk("overlays present (2)", len(ov) == 2, len(ov))
        chk("overlay px = pt*RS", ov and abs(ov[0]["pts"][1]["x"] - 150.0) < 0.5,
            ov[0]["pts"][1] if ov else None)

        # ---- 2. /report renders the handed-off payload, area read-only ----
        rp = b.new_page()
        rp.on("pageerror", lambda e: failures.append(f"pageerror(report): {e}"))
        rp.goto(f"{base}/report", wait_until="domcontentloaded")
        rp.evaluate("(p) => sessionStorage.setItem('bmaReportPayload', JSON.stringify(p))", payload)
        rp.reload(wait_until="domcontentloaded")
        time.sleep(0.5)
        rstate = rp.evaluate(
            """() => {
              const sheets = document.querySelectorAll('.sheet');
              const areaCells = document.querySelectorAll('td.area');
              const anyAreaEditable = [...areaCells].some(td => td.getAttribute('contenteditable')==='true');
              const nameEditable = !!document.querySelector('td[contenteditable="true"]');
              const grand = document.querySelector('tr.grand .area');
              const src = (document.getElementById('srcTag')||{}).textContent||'';
              return { sheets: sheets.length, areaCells: areaCells.length,
                       anyAreaEditable, nameEditable,
                       grandTxt: grand ? grand.textContent : '', src };
            }"""
        )
        chk("report: 1 sheet", rstate["sheets"] == 1, rstate)
        chk("report: area cells exist", rstate["areaCells"] >= 3, rstate)
        chk("report: area cells READ-ONLY", rstate["anyAreaEditable"] is False, rstate)
        chk("report: row name editable", rstate["nameEditable"] is True, rstate)
        chk("report: net 75.00 printed", "75.00" in rstate["grandTxt"], rstate["grandTxt"])
        chk("report: src=real data", "จริง" in rstate["src"], rstate["src"])

        # ---- 3. /report standalone (no payload) -> SAMPLE ----
        sp = b.new_page()
        sp.on("pageerror", lambda e: failures.append(f"pageerror(sample): {e}"))
        sp.goto(f"{base}/report", wait_until="domcontentloaded")
        time.sleep(0.4)
        sstate = sp.evaluate(
            """() => ({ sheets: document.querySelectorAll('.sheet').length,
                        groups: document.querySelectorAll('tr.grp').length,
                        grand: (document.querySelector('tr.grand .area')||{}).textContent||'',
                        src: (document.getElementById('srcTag')||{}).textContent||'' })"""
        )
        chk("standalone: 1 sheet", sstate["sheets"] == 1, sstate)
        chk("standalone: 3 group headers", sstate["groups"] == 3, sstate)
        chk("standalone: net 68.50", "68.50" in sstate["grand"], sstate["grand"])
        chk("standalone: src=sample", "ตัวอย่าง" in sstate["src"], sstate["src"])

        b.close()
    server.should_exit = True
    time.sleep(0.4)

    for name, ok in checks:
        print(f"  [{'OK' if ok else 'XX'}] {name}")
    if failures:
        for f in failures:
            print("FAIL:", f)
        print("LITE_REPORT_FAIL")
        sys.exit(1)
    print(f"LITE_REPORT_OK ({len(checks)}/{len(checks)})")


if __name__ == "__main__":
    main()
