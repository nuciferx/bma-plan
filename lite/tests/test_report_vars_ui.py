"""
LITE-REPORT-VARS-UI test (LRV-S2 sprint).

Verifies renderReportVarsEditor() drives REAL DOM interactions — NOT just
model-function calls (that is the repeated lite anti-pattern).

Checks (each exercising real DOM + event dispatch):
  editorRenders      create host div, call renderReportVarsEditor with known
                     agg; assert >=3 var rows present, "+ เพิ่มตัวแปร" button
                     present, and v_far row shows value text containing "1.6".
  selectChangeRecalcs find first operand <select> of a var, change its value
                     to a different layer ref via dispatchEvent (real change
                     Event), then assert (a) the REPORT_VARS entry expr
                     changed AND (b) the displayed value text updated.
  addVarFlow         click "+ เพิ่มตัวแปร" button (real .click()); assert
                     REPORT_VARS grew by 1 and a new .rv-row appeared.
  deleteVarFlow      click a row's "✕" (real .click()); assert REPORT_VARS
                     shrank and the row is gone.
  noPageError        no JS pageerror fired during the above.

Emits LITE_REPORT_VARS_UI_OK on success.

    py -3 lite/tests/test_report_vars_ui.py
"""
import socket, threading, time, sys
from pathlib import Path

LITE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LITE))
import uvicorn
from playwright.sync_api import sync_playwright


def _free_port(start=8350):
    for p in range(start, start + 60):
        with socket.socket() as s:
            if s.connect_ex(("127.0.0.1", p)) != 0:
                return p
    raise RuntimeError("no free port")


# --------------------------------------------------------------------------
# Setup: seed REPORT_VARS to 3 presets, create a host div, call the renderer.
# The AGG keys match the preset refs so v_far = gfa/site = 480/300 = 1.6.
# --------------------------------------------------------------------------
SCENARIO = r"""
async () => {
  const out = {};
  const AGG = {gfa: 480, ded: 30, site: 300, open: 60};

  // Ensure clean state: 3 presets (v_net / v_osr / v_far).
  REPORT_VARS.length = 0;
  seedReportVars();

  // Create a detached host div so we can query it freely.
  const host = document.createElement('div');
  host.id = '__rv_test_host';
  document.body.appendChild(host);

  // -----------------------------------------------------------------------
  // editorRenders: renderReportVarsEditor fills host correctly.
  // -----------------------------------------------------------------------
  renderReportVarsEditor(host, AGG);

  const rows = host.querySelectorAll('.rv-row');
  const addBtn = host.querySelector('.rv-addvar');
  out.editorRenders_rowCount = rows.length;
  out.editorRenders_hasAddBtn = addBtn !== null;

  // Find the v_far row by looking for a .rv-val that contains "1.6".
  let farValFound = false;
  host.querySelectorAll('.rv-val').forEach(function(el) {
    if (el.textContent.indexOf('1.6') !== -1) farValFound = true;
  });
  out.editorRenders_farVal = farValFound;

  out.editorRenders = rows.length >= 3 && addBtn !== null && farValFound;

  // -----------------------------------------------------------------------
  // selectChangeRecalcs: change an operand select via real dispatchEvent
  // and verify REPORT_VARS entry expr AND displayed value both update.
  //
  // Strategy: use v_far (index 2) which is gfa/site = 1.6.
  //   Its first token has ref='gfa'. We change it to ref='ded'.
  //   New value = ded / site = 30 / 300 = 0.1  (not 1.6).
  // -----------------------------------------------------------------------
  // Re-render fresh so we have a clean host state.
  renderReportVarsEditor(host, AGG);

  // Find the v_far row: it's the 3rd .rv-row (index 2 in preset order).
  const allRows = host.querySelectorAll('.rv-row');
  const farRow = allRows[2];  // v_far is the 3rd preset

  // The first <select> in farRow is the first operand select.
  const firstSel = farRow.querySelector('select:not(.rv-op)');
  if (!firstSel) {
    out.selectChangeRecalcs = false;
  } else {
    // Change to 'ref:ded'
    firstSel.value = 'ref:ded';
    firstSel.dispatchEvent(new Event('change', {bubbles: true}));

    // After re-render: REPORT_VARS[2].expr[0].ref must be 'ded'
    const exprChanged = REPORT_VARS[2] && REPORT_VARS[2].expr[0] && REPORT_VARS[2].expr[0].ref === 'ded';

    // The host should have been re-rendered; find a .rv-val that has "0.1"
    // (ded/site = 30/300 = 0.10) — check for "0.10" or "0.1"
    let newValFound = false;
    host.querySelectorAll('.rv-val').forEach(function(el) {
      // "0.10" contains "0.1"
      if (el.textContent.indexOf('0.1') !== -1) newValFound = true;
    });

    out.selectChangeRecalcs_exprChanged = exprChanged;
    out.selectChangeRecalcs_valUpdated = newValFound;
    out.selectChangeRecalcs = !!(exprChanged && newValFound);
  }

  // Restore v_far expr to gfa/site so later checks work on clean state.
  REPORT_VARS.length = 0;
  seedReportVars();
  renderReportVarsEditor(host, AGG);

  // -----------------------------------------------------------------------
  // addVarFlow: clicking "+ เพิ่มตัวแปร" grows REPORT_VARS by 1 and
  // adds a new .rv-row to the host.
  // -----------------------------------------------------------------------
  const lenBefore = REPORT_VARS.length;
  const rowsBefore = host.querySelectorAll('.rv-row').length;
  const btn = host.querySelector('.rv-addvar');
  if (!btn) {
    out.addVarFlow = false;
  } else {
    btn.click();
    const lenAfter = REPORT_VARS.length;
    const rowsAfter = host.querySelectorAll('.rv-row').length;
    out.addVarFlow_lenGrew = lenAfter === lenBefore + 1;
    out.addVarFlow_rowGrew = rowsAfter === rowsBefore + 1;
    out.addVarFlow = lenAfter === lenBefore + 1 && rowsAfter === rowsBefore + 1;
  }

  // -----------------------------------------------------------------------
  // deleteVarFlow: clicking a row's "✕" shrinks REPORT_VARS and removes
  // that row from the host.
  // -----------------------------------------------------------------------
  // Current state: 3 presets + 1 just added = 4 vars.
  const lenBeforeDel = REPORT_VARS.length;
  const rowsBeforeDel = host.querySelectorAll('.rv-row').length;
  // Delete the LAST row (the newly added blank one).
  const delBtns = host.querySelectorAll('.rv-del');
  const lastDel = delBtns[delBtns.length - 1];
  if (!lastDel) {
    out.deleteVarFlow = false;
  } else {
    lastDel.click();
    const lenAfterDel = REPORT_VARS.length;
    const rowsAfterDel = host.querySelectorAll('.rv-row').length;
    out.deleteVarFlow_lenShrunk = lenAfterDel === lenBeforeDel - 1;
    out.deleteVarFlow_rowShrunk = rowsAfterDel === rowsBeforeDel - 1;
    out.deleteVarFlow = lenAfterDel === lenBeforeDel - 1 && rowsAfterDel === rowsBeforeDel - 1;
  }

  // Restore clean state.
  REPORT_VARS.length = 0;
  seedReportVars();

  return out;
}
"""

CHECKS = [
    "editorRenders",
    "selectChangeRecalcs",
    "addVarFlow",
    "deleteVarFlow",
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

    # noPageError check uses page_errors list collected during the run.
    no_page_error = len(page_errors) == 0
    result["noPageError"] = no_page_error
    CHECKS.append("noPageError")

    for e in page_errors:
        print("  JS ERROR:", e)

    print()
    print("LITE-REPORT-VARS-UI checks:")
    for k in CHECKS:
        ok = result.get(k)
        print(f"  {k:30s} -> {ok}")
        if ok is not True:
            failures.append(f"check '{k}' = {ok!r} (expected True)")

    # Extra diagnostics for partial results.
    diag_keys = [
        "editorRenders_rowCount", "editorRenders_hasAddBtn", "editorRenders_farVal",
        "selectChangeRecalcs_exprChanged", "selectChangeRecalcs_valUpdated",
        "addVarFlow_lenGrew", "addVarFlow_rowGrew",
        "deleteVarFlow_lenShrunk", "deleteVarFlow_rowShrunk",
    ]
    print()
    print("  Diagnostics:")
    for k in diag_keys:
        if k in result:
            print(f"    {k}: {result[k]}")

    if failures:
        for f in failures:
            print("FAIL:", f)
        print("LITE_REPORT_VARS_UI_FAIL")
        sys.exit(1)
    else:
        print("LITE_REPORT_VARS_UI_OK")


if __name__ == "__main__":
    main()
