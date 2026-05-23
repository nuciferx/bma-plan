"""
LEXP-1: test_export_submenu.py — verifies XLSX Summary in Export submenu.

Four checks (driven by real DOM events via Playwright):
  1. flatXlsxHidden            — mi-xlsx element exists in DOM but display===none
  2. exportSubmenuHasTwoItems  — Export flyout sub-dd has 2 items: Report HTML + XLSX Summary
  3. xlsxSubmenuItemTriggersExport — click XLSX Summary → dlPost called with /export-xlsx
  4. ctrlEStillWorks           — Ctrl+E keydown → dlPost called once

Emits LITE_EXPORT_SUBMENU_OK on success.

    py -3 lite/tests/test_export_submenu.py
"""
import socket, threading, time, sys, io
from pathlib import Path

# Ensure stdout can handle UTF-8 (needed for Thai characters)
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

LITE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LITE))
import uvicorn
from playwright.sync_api import sync_playwright


def _free_port(start=8490):
    for p in range(start, start + 60):
        with socket.socket() as s:
            if s.connect_ex(("127.0.0.1", p)) != 0:
                return p
    raise RuntimeError("no free port")


# ---------------------------------------------------------------------------
# Check 1 — flatXlsxHidden
# mi-xlsx element must exist in DOM (for Ctrl+E) but have display===none.
# ---------------------------------------------------------------------------
SC1_FLAT_HIDDEN = """
() => {
    var el = document.getElementById('mi-xlsx');
    if (!el) return { pass: false, reason: 'mi-xlsx element not found in DOM' };
    var display = getComputedStyle(el).display;
    return { display, inDom: true, pass: display === 'none' };
}
"""

# ---------------------------------------------------------------------------
# Check 2 — exportSubmenuHasTwoItems
# The Export flyout parent (data-flyout-group="export") must have 2 .item
# children in its .sub-dd, labelled "Report HTML" and "XLSX Summary".
# ---------------------------------------------------------------------------
SC2_TWO_ITEMS = """
() => {
    var expParent = document.querySelector('.item.has-sub[data-flyout-group="export"]');
    if (!expParent) return { pass: false, reason: 'export has-sub not found' };
    var subDd = expParent.querySelector('.sub-dd');
    if (!subDd) return { pass: false, reason: 'sub-dd not found inside export has-sub' };
    var items = subDd.querySelectorAll('.item');
    var labels = Array.from(items).map(function(i){ return i.textContent.trim(); });
    var hasReport = labels.some(function(l){ return l.indexOf('Report HTML') >= 0; });
    var hasXlsx   = labels.some(function(l){ return l.indexOf('XLSX Summary') >= 0; });
    return {
        count: items.length, labels, hasReport, hasXlsx,
        pass: items.length === 2 && hasReport && hasXlsx
    };
}
"""

# ---------------------------------------------------------------------------
# Check 3 — xlsxSubmenuItemTriggersExport
# Stub dlPost, set caseId, click XLSX Summary item, assert dlPost called once
# with /export-xlsx as first arg.
# ---------------------------------------------------------------------------
SC3_STUB_SETUP = """
() => {
    // Stub out helpers so exportXlsx guard passes
    window.__xlsxCalls = [];
    window.dlPost = function() { window.__xlsxCalls.push(Array.from(arguments)); };
    window.buildExportData = function() { return {}; };
    window.baseName = function() { return 'test'; };
    window.caseId = 'test';
    return { stubbed: true };
}
"""

SC3_CLICK_XLSX = """
() => {
    var expParent = document.querySelector('.item.has-sub[data-flyout-group="export"]');
    if (!expParent) return { pass: false, reason: 'export has-sub not found' };
    var subDd = expParent.querySelector('.sub-dd');
    if (!subDd) return { pass: false, reason: 'sub-dd not found' };
    // Find the XLSX Summary item by its data-action attribute
    var xlsxItem = subDd.querySelector('.item[data-action="exportXlsx"]');
    if (!xlsxItem) return { pass: false, reason: 'XLSX Summary item not found' };
    xlsxItem.click();
    var calls = window.__xlsxCalls || [];
    var calledOnce = calls.length === 1;
    var firstArg = calledOnce ? calls[0][0] : null;
    var endpointOk = firstArg === '/export-xlsx';
    var thirdArg = calledOnce ? calls[0][2] : null;
    var xlsxSuffix = thirdArg && thirdArg.endsWith('.xlsx');
    return {
        callCount: calls.length, firstArg, thirdArg,
        calledOnce, endpointOk, xlsxSuffix,
        pass: calledOnce && endpointOk && xlsxSuffix
    };
}
"""

# ---------------------------------------------------------------------------
# Check 4 — ctrlEStillWorks
# Reset __xlsxCalls, dispatch Ctrl+E keydown, assert dlPost called once.
# ---------------------------------------------------------------------------
SC4_CTRL_E_RESET = """
() => {
    window.__xlsxCalls = [];
    return { reset: true };
}
"""

SC4_CTRL_E_CHECK = """
() => {
    var calls = window.__xlsxCalls || [];
    var calledOnce = calls.length === 1;
    var firstArg = calledOnce ? calls[0][0] : null;
    var endpointOk = firstArg === '/export-xlsx';
    return { callCount: calls.length, firstArg, calledOnce, endpointOk,
             pass: calledOnce && endpointOk };
}
"""


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

        print()
        print("LEXP-1 export submenu checks:")

        # ------------------------------------------------------------------
        # Check 1 — flatXlsxHidden
        # ------------------------------------------------------------------
        name = "flatXlsxHidden"
        try:
            result = pg.evaluate(SC1_FLAT_HIDDEN)
            ok = result.get("pass") is True
            status = "PASS" if ok else "FAIL"
            print(f"  {name:42s} -> {status}  {result}")
            if not ok:
                failures.append(f"check '{name}' failed: {result}")
        except Exception as ex:
            print(f"  {name:42s} -> EXCEPTION: {ex}")
            failures.append(f"check '{name}' threw: {ex}")

        # ------------------------------------------------------------------
        # Check 2 — exportSubmenuHasTwoItems
        # Open File menu first so flyout is initialised, then check DOM
        # ------------------------------------------------------------------
        name = "exportSubmenuHasTwoItems"
        try:
            # Open the File menu to ensure _rebuildFileMenu has run
            file_btn = pg.query_selector('.menu[data-m="file"] > button')
            if file_btn:
                file_btn.click()
                time.sleep(0.1)
            result = pg.evaluate(SC2_TWO_ITEMS)
            ok = result.get("pass") is True
            status = "PASS" if ok else "FAIL"
            print(f"  {name:42s} -> {status}  {result}")
            if not ok:
                failures.append(f"check '{name}' failed: {result}")
            pg.keyboard.press("Escape")
            time.sleep(0.05)
        except Exception as ex:
            print(f"  {name:42s} -> EXCEPTION: {ex}")
            failures.append(f"check '{name}' threw: {ex}")

        # ------------------------------------------------------------------
        # Check 3 — xlsxSubmenuItemTriggersExport
        # ------------------------------------------------------------------
        name = "xlsxSubmenuItemTriggersExport"
        try:
            # Install stubs
            pg.evaluate(SC3_STUB_SETUP)
            result = pg.evaluate(SC3_CLICK_XLSX)
            ok = result.get("pass") is True
            status = "PASS" if ok else "FAIL"
            print(f"  {name:42s} -> {status}  {result}")
            if not ok:
                failures.append(f"check '{name}' failed: {result}")
        except Exception as ex:
            print(f"  {name:42s} -> EXCEPTION: {ex}")
            failures.append(f"check '{name}' threw: {ex}")

        # ------------------------------------------------------------------
        # Check 4 — ctrlEStillWorks
        # Stubs already in place from check 3; reset call log then fire Ctrl+E
        # ------------------------------------------------------------------
        name = "ctrlEStillWorks"
        try:
            pg.evaluate(SC4_CTRL_E_RESET)
            pg.keyboard.press("Control+e")
            time.sleep(0.15)
            result = pg.evaluate(SC4_CTRL_E_CHECK)
            ok = result.get("pass") is True
            status = "PASS" if ok else "FAIL"
            print(f"  {name:42s} -> {status}  {result}")
            if not ok:
                failures.append(f"check '{name}' failed: {result}")
        except Exception as ex:
            print(f"  {name:42s} -> EXCEPTION: {ex}")
            failures.append(f"check '{name}' threw: {ex}")

        pg.close()
        b.close()

    for e in page_errors:
        print("  JS ERROR:", e)

    server.should_exit = True
    time.sleep(0.4)

    if failures:
        for f in failures:
            print("FAIL:", f)
        print("LITE_EXPORT_SUBMENU_FAIL")
        sys.exit(1)
    else:
        print("LITE_EXPORT_SUBMENU_OK")


if __name__ == "__main__":
    main()
