"""
LITE-REPORT-VARS regression guard (LRV-S1 sprint).

Verifies report-vars.js public surface:
  presetSeed    after REPORT_VARS.length=0; seedReportVars() → 3 vars (v_net/v_osr/v_far).
  foldEval      computeReportVars({gfa:480,ded:30,site:300,open:60})
                  → อาคารสุทธิ=450, OSR=20, FAR=1.6 (within 0.01).
  chainRef      a var referencing v_net / site → value ≈ 1.5.
  divZeroGuard  div by zero/absent ref → err set, value null, no throw.
  unknownRefErr expr:[{ref:'nope'}] → err set.

Emits LITE_REPORT_VARS_OK on success.

    py -3 lite/tests/test_report_vars.py
"""
import socket, threading, time, sys
from pathlib import Path

LITE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LITE))
import uvicorn
from playwright.sync_api import sync_playwright


def _free_port(start=8340):
    for p in range(start, start + 60):
        with socket.socket() as s:
            if s.connect_ex(("127.0.0.1", p)) != 0:
                return p
    raise RuntimeError("no free port")


# --------------------------------------------------------------------------
# All checks run in a single page.evaluate() call for speed.
# --------------------------------------------------------------------------
SCENARIO = r"""
() => {
  const out = {};
  const AGG = {gfa: 480, ded: 30, site: 300, open: 60};

  // -----------------------------------------------------------------------
  // presetSeed: reset and reseed → 3 vars with correct ids.
  // -----------------------------------------------------------------------
  REPORT_VARS.length = 0;
  seedReportVars();
  out.presetSeed = REPORT_VARS.length === 3
    && REPORT_VARS[0].id === 'v_net'
    && REPORT_VARS[1].id === 'v_osr'
    && REPORT_VARS[2].id === 'v_far';

  // -----------------------------------------------------------------------
  // foldEval: computeReportVars with known agg.
  //   อาคารสุทธิ = 480 - 30 = 450
  //   OSR        = 60 / 300 * 100 = 20
  //   FAR        = 480 / 300 = 1.6
  // -----------------------------------------------------------------------
  REPORT_VARS.length = 0;
  seedReportVars();
  const results = computeReportVars(AGG);
  const net = results.find(r => r.id === 'v_net');
  const osr = results.find(r => r.id === 'v_osr');
  const far = results.find(r => r.id === 'v_far');
  out.foldEval = !!(
    net && osr && far &&
    net.err === null && Math.abs(net.value - 450) < 0.01 &&
    osr.err === null && Math.abs(osr.value - 20)  < 0.01 &&
    far.err === null && Math.abs(far.value - 1.6) < 0.01
  );

  // -----------------------------------------------------------------------
  // chainRef: add a var that references v_net (an earlier computed var).
  //   new_var = v_net / site = 450 / 300 = 1.5
  // -----------------------------------------------------------------------
  REPORT_VARS.length = 0;
  seedReportVars();
  const chainVar = addReportVar('chain_test');
  chainVar.expr = [{ref: 'v_net'}, {op: '/', ref: 'site'}];
  const results2 = computeReportVars(AGG);
  const cv = results2.find(r => r.id === chainVar.id);
  out.chainRef = !!(cv && cv.err === null && Math.abs(cv.value - 1.5) < 0.01);

  // -----------------------------------------------------------------------
  // divZeroGuard: dividing by a ref that resolves to 0 → err, value null.
  // -----------------------------------------------------------------------
  REPORT_VARS.length = 0;
  let threw = false;
  let divErr = null;
  try {
    const dv = addReportVar('divzero');
    dv.expr = [{ref: 'gfa'}, {op: '/', ref: 'ded'}];  // ded=0 in the test agg below
    const results3 = computeReportVars({gfa: 480, ded: 0});
    const dr = results3.find(r => r.id === dv.id);
    divErr = dr ? dr.err : null;
  } catch(e) {
    threw = true;
  }
  out.divZeroGuard = !threw && divErr !== null && divErr.length > 0;

  // -----------------------------------------------------------------------
  // unknownRefErr: ref to unknown id → err set.
  // -----------------------------------------------------------------------
  REPORT_VARS.length = 0;
  let ukErr = null;
  let ukThrew = false;
  try {
    const uv = addReportVar('unknown');
    uv.expr = [{ref: 'nope'}];
    const results4 = computeReportVars({});
    const ur = results4.find(r => r.id === uv.id);
    ukErr = ur ? ur.err : null;
  } catch(e) {
    ukThrew = true;
  }
  out.unknownRefErr = !ukThrew && ukErr !== null && ukErr.length > 0;

  // Restore clean state
  REPORT_VARS.length = 0;
  seedReportVars();

  return out;
}
"""

CHECKS = [
    "presetSeed",
    "foldEval",
    "chainRef",
    "divZeroGuard",
    "unknownRefErr",
]


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
        pg = b.new_page()
        pg.on("pageerror", lambda e: page_errors.append(f"pageerror: {e}"))
        pg.goto(f"http://127.0.0.1:{port}/", wait_until="networkidle")
        time.sleep(0.6)
        result = pg.evaluate(SCENARIO)
        pg.close()
        b.close()

    server.should_exit = True
    time.sleep(0.4)

    for e in page_errors:
        print("  JS ERROR:", e)

    print()
    print("LITE-REPORT-VARS checks:")
    for k in CHECKS:
        ok = result.get(k)
        print(f"  {k:20s} -> {ok}")
        if ok is not True:
            failures.append(f"check '{k}' = {ok!r} (expected True)")

    if failures:
        for f in failures:
            print("FAIL:", f)
        print("LITE_REPORT_VARS_FAIL")
        sys.exit(1)
    else:
        print("LITE_REPORT_VARS_OK")


if __name__ == "__main__":
    main()
