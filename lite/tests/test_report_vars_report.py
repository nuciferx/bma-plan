"""
LITE-REPORT-VARS-REPORT acceptance test (LRV-S3 sprint).

Verifies that buildReportPayload() includes a reportVars array and that
lite-report.html renders those vars in a project-level summary card.

Checks:
  payloadHasVars     main page: buildReportPayload().reportVars has 3 entries
                     (the seeded presets), each with name + (value or err).
  reportRendersVars  /report renders a crafted payload with 3 vars including
                     one err-var; asserts FAR/OSR values visible, err row shows "—".
  oldPayloadNoCrash  payload without reportVars does NOT crash; page still renders.

Emits LITE_REPORT_VARS_REPORT_OK on success.

    py -3 lite/tests/test_report_vars_report.py
"""
import socket, threading, time, sys, json
from pathlib import Path

LITE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LITE))
import uvicorn
from playwright.sync_api import sync_playwright


def _free_port(start=8360):
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

    failures = []
    page_errors = []
    checks = []

    def chk(name, cond, extra=""):
        checks.append((name, bool(cond)))
        if not cond:
            failures.append(f"{name} {extra}")

    base = f"http://127.0.0.1:{port}"

    with sync_playwright() as pw:
        b = pw.chromium.launch()

        # ---- 1. payloadHasVars ----
        pg = b.new_page()
        pg.on("pageerror", lambda e: page_errors.append(f"pageerror(app): {e}"))
        pg.goto(f"{base}/", wait_until="networkidle")
        time.sleep(0.6)

        rv_result = pg.evaluate("""() => {
          var p = buildReportPayload();
          if (!p.reportVars) return {ok: false, reason: 'reportVars missing'};
          var arr = p.reportVars;
          if (arr.length < 3) return {ok: false, reason: 'length=' + arr.length};
          for (var i = 0; i < arr.length; i++) {
            var v = arr[i];
            if (!v.name) return {ok: false, reason: 'entry ' + i + ' has no name'};
            if (!('value' in v) && !('err' in v))
              return {ok: false, reason: 'entry ' + i + ' has no value/err'};
          }
          return {ok: true, length: arr.length};
        }""")
        chk("payloadHasVars", rv_result.get("ok") is True,
            rv_result.get("reason", rv_result))
        pg.close()

        # ---- 2. reportRendersVars ----
        crafted = {
            "project": "T",
            "date": "x",
            "generated": 1,
            "pages": [],
            "reportVars": [
                {"name": "FAR",  "unit": "",   "value": 1.6, "err": None},
                {"name": "OSR",  "unit": "%",  "value": 20,  "err": None},
                {"name": "ว่าง", "unit": "ม²", "value": None, "err": "อ้างไม่พบ"},
            ]
        }
        rp = b.new_page()
        rp.on("pageerror", lambda e: page_errors.append(f"pageerror(report): {e}"))
        rp.goto(f"{base}/report", wait_until="domcontentloaded")
        rp.evaluate("(p) => sessionStorage.setItem('bmaReportPayload', JSON.stringify(p))",
                    crafted)
        rp.goto(f"{base}/report", wait_until="domcontentloaded")
        time.sleep(0.5)

        rstate = rp.evaluate("""() => {
          var host = document.getElementById('sheets');
          var text = host ? host.innerText : '';
          var rvcard = document.querySelector('.rvcard');
          return {
            hasFAR:  text.indexOf('FAR') !== -1,
            has1_6:  text.indexOf('1.6') !== -1,
            hasOSR:  text.indexOf('OSR') !== -1,
            has20:   text.indexOf('20') !== -1,
            hasDash: text.indexOf('—') !== -1,
            hasCard: rvcard !== null
          };
        }""")
        chk("reportRendersVars_hasFAR",  rstate.get("hasFAR"),  rstate)
        chk("reportRendersVars_has1.6",  rstate.get("has1_6"),  rstate)
        chk("reportRendersVars_hasOSR",  rstate.get("hasOSR"),  rstate)
        chk("reportRendersVars_has20",   rstate.get("has20"),   rstate)
        chk("reportRendersVars_hasDash", rstate.get("hasDash"), rstate)
        chk("reportRendersVars_hasCard", rstate.get("hasCard"), rstate)
        rp.close()

        # ---- 3. oldPayloadNoCrash ----
        old_payload = {"project": "T", "date": "x", "generated": 1, "pages": []}
        sp = b.new_page()
        old_page_errors = []
        sp.on("pageerror", lambda e: old_page_errors.append(str(e)))
        sp.goto(f"{base}/report", wait_until="domcontentloaded")
        sp.evaluate("(p) => sessionStorage.setItem('bmaReportPayload', JSON.stringify(p))",
                    old_payload)
        sp.goto(f"{base}/report", wait_until="domcontentloaded")
        time.sleep(0.4)
        old_state = sp.evaluate("""() => {
          var host = document.getElementById('sheets');
          return { rendered: host !== null, text: host ? host.innerText : '' };
        }""")
        chk("oldPayloadNoCrash_noError",  len(old_page_errors) == 0,
            old_page_errors)
        chk("oldPayloadNoCrash_renders",  old_state.get("rendered") is True,
            old_state)
        sp.close()

        b.close()

    server.should_exit = True
    time.sleep(0.4)

    for e in page_errors:
        print("  JS ERROR:", e)

    print()
    print("LITE-REPORT-VARS-REPORT checks:")
    for name, ok in checks:
        print(f"  [{'OK' if ok else 'XX'}] {name}")

    if failures:
        for f in failures:
            print("FAIL:", f)
        print("LITE_REPORT_VARS_REPORT_FAIL")
        sys.exit(1)
    print(f"LITE_REPORT_VARS_REPORT_OK ({len(checks)}/{len(checks)})")


if __name__ == "__main__":
    main()
