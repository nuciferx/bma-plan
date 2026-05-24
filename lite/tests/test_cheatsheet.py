"""
LHELP-1: test_cheatsheet.py — verifies the F1 / ? cheatsheet overlay.

Six scenarios (driven by real DOM events via Playwright):
  1. f1OpensCheatsheet       — F1 opens overlay; F1 again closes
  2. questionMarkOpens       — fresh load; ? (shiftKey) opens overlay
  3. escapeCloses            — open via F1; Escape closes; Esc when closed = no-op / no-throw
  4. clickOutsideCloses      — click backdrop = close; click inside panel = stays open
  5. inputFocusGuards        — F1 while INPUT focused = no open; after blur = opens
  6. contentHasAllSections   — open overlay; h4 titles and ≥20 .kv rows present

Emits LITE_CHEATSHEET_OK on success.

    py -3 lite/tests/test_cheatsheet.py
"""
import socket, threading, time, sys, io
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

LITE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LITE))
import uvicorn
from playwright.sync_api import sync_playwright


def _free_port(start=8510):
    for p in range(start, start + 60):
        with socket.socket() as s:
            if s.connect_ex(("127.0.0.1", p)) != 0:
                return p
    raise RuntimeError("no free port")


# ---------------------------------------------------------------------------
# SC1 — f1OpensCheatsheet
# ---------------------------------------------------------------------------
SC1 = """
() => {
    // ensure overlay is closed to start
    if (typeof closeCheatsheet === 'function') closeCheatsheet();
    var bd = document.querySelector('.cheatsheet-backdrop');
    var wasOpen = bd && bd.classList.contains('open');

    // dispatch F1
    window.dispatchEvent(new KeyboardEvent('keydown', { key: 'F1', bubbles: true }));

    // check open
    var bd2 = document.querySelector('.cheatsheet-backdrop');
    var isOpen = bd2 && bd2.classList.contains('open');
    var displayOpen = bd2 ? window.getComputedStyle(bd2).display : 'none';

    // dispatch F1 again to close
    window.dispatchEvent(new KeyboardEvent('keydown', { key: 'F1', bubbles: true }));
    var bd3 = document.querySelector('.cheatsheet-backdrop');
    var isClosed = bd3 && !bd3.classList.contains('open');

    return {
        wasOpen: wasOpen,
        isOpen: isOpen,
        displayOpen: displayOpen,
        isClosed: isClosed,
        pass: !wasOpen && isOpen && displayOpen === 'flex' && isClosed
    };
}
"""

# ---------------------------------------------------------------------------
# SC2 — questionMarkOpens
# ---------------------------------------------------------------------------
SC2 = """
() => {
    // ensure closed
    if (typeof closeCheatsheet === 'function') closeCheatsheet();

    // dispatch ? (Shift+/ → key='?', shiftKey:true)
    window.dispatchEvent(new KeyboardEvent('keydown', { key: '?', shiftKey: true, bubbles: true }));

    var bd = document.querySelector('.cheatsheet-backdrop');
    var isOpen = bd && bd.classList.contains('open');

    // clean up
    if (typeof closeCheatsheet === 'function') closeCheatsheet();

    return { isOpen: isOpen, pass: isOpen === true };
}
"""

# ---------------------------------------------------------------------------
# SC3 — escapeCloses
# ---------------------------------------------------------------------------
SC3 = """
() => {
    // open via F1
    window.dispatchEvent(new KeyboardEvent('keydown', { key: 'F1', bubbles: true }));
    var bd = document.querySelector('.cheatsheet-backdrop');
    var openedOk = bd && bd.classList.contains('open');

    // close via Escape
    window.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape', bubbles: true }));
    var closedOk = bd && !bd.classList.contains('open');

    // Escape when already closed — must not throw, must stay closed
    var noException = true;
    try {
        window.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape', bubbles: true }));
    } catch (ex) {
        noException = false;
    }
    var stillClosed = bd && !bd.classList.contains('open');

    return {
        openedOk: openedOk,
        closedOk: closedOk,
        noException: noException,
        stillClosed: stillClosed,
        pass: openedOk && closedOk && noException && stillClosed
    };
}
"""

# ---------------------------------------------------------------------------
# SC4 — clickOutsideCloses / clickInsideStaysOpen
# ---------------------------------------------------------------------------
SC4 = """
() => {
    // open
    if (typeof openCheatsheet === 'function') openCheatsheet();
    var bd = document.querySelector('.cheatsheet-backdrop');
    if (!bd) return { pass: false, reason: 'no backdrop' };
    var openedOk = bd.classList.contains('open');

    // click on backdrop (outside panel) → should close
    bd.dispatchEvent(new MouseEvent('click', { bubbles: true }));
    var afterOutside = !bd.classList.contains('open');

    // open again
    if (typeof openCheatsheet === 'function') openCheatsheet();
    var reopenOk = bd.classList.contains('open');

    // click inside panel → should NOT close
    var panel = bd.querySelector('.cheatsheet-panel');
    if (panel) {
        panel.dispatchEvent(new MouseEvent('click', { bubbles: true }));
    }
    var afterInside = bd.classList.contains('open');

    // clean up
    if (typeof closeCheatsheet === 'function') closeCheatsheet();

    return {
        openedOk: openedOk,
        afterOutside: afterOutside,
        reopenOk: reopenOk,
        afterInside: afterInside,
        pass: openedOk && afterOutside && reopenOk && afterInside
    };
}
"""

# ---------------------------------------------------------------------------
# SC5 — inputFocusGuards
# ---------------------------------------------------------------------------
SC5 = """
() => {
    // ensure overlay is closed
    if (typeof closeCheatsheet === 'function') closeCheatsheet();

    // create a fake input and focus it
    var inp = document.createElement('input');
    document.body.appendChild(inp);
    inp.focus();

    // dispatch F1 while input focused → should NOT open
    window.dispatchEvent(new KeyboardEvent('keydown', { key: 'F1', bubbles: true }));
    var bd = document.querySelector('.cheatsheet-backdrop');
    var notOpenWhileFocused = !bd || !bd.classList.contains('open');

    // blur and remove
    inp.blur();
    document.body.removeChild(inp);

    // dispatch F1 now → SHOULD open
    window.dispatchEvent(new KeyboardEvent('keydown', { key: 'F1', bubbles: true }));
    var bd2 = document.querySelector('.cheatsheet-backdrop');
    var openedAfterBlur = bd2 && bd2.classList.contains('open');

    // clean up
    if (typeof closeCheatsheet === 'function') closeCheatsheet();

    return {
        notOpenWhileFocused: notOpenWhileFocused,
        openedAfterBlur: openedAfterBlur,
        pass: notOpenWhileFocused && openedAfterBlur
    };
}
"""

# ---------------------------------------------------------------------------
# SC6 — contentHasAllSections
# ---------------------------------------------------------------------------
SC6 = """
() => {
    if (typeof openCheatsheet === 'function') openCheatsheet();

    var h4s = Array.from(document.querySelectorAll('.cheatsheet-grid h4'));
    var titles = h4s.map(function(el) { return el.textContent.trim(); });

    var hasTool   = titles.some(function(t) { return t.indexOf('เครื่องมือ') >= 0; });  // เครื่องมือ
    var hasSnap   = titles.some(function(t) { return t.indexOf('Snap') >= 0; });
    var hasPage   = titles.some(function(t) { return t.indexOf('หน้า') >= 0; });  // หน้า
    var hasEdit   = titles.some(function(t) { return t.indexOf('แก้ไข') >= 0; });  // แก้ไข

    var kvs = document.querySelectorAll('.cheatsheet-grid .kv');
    var kvCount = kvs.length;

    if (typeof closeCheatsheet === 'function') closeCheatsheet();

    return {
        titles: titles,
        hasTool: hasTool,
        hasSnap: hasSnap,
        hasPage: hasPage,
        hasEdit: hasEdit,
        kvCount: kvCount,
        pass: hasTool && hasSnap && hasPage && hasEdit && kvCount >= 20
    };
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
        base_url = f"http://127.0.0.1:{port}/"
        pg.goto(base_url, wait_until="networkidle")
        time.sleep(0.8)

        print()
        print("LHELP-1 cheatsheet checks:")

        # ---- SC1 f1OpensCheatsheet ----
        name = "f1OpensCheatsheet"
        try:
            result = pg.evaluate(SC1)
            ok = result.get("pass") is True
            print(f"  {name:46s} -> {'PASS' if ok else 'FAIL'}  {result}")
            if not ok:
                failures.append(f"'{name}' failed: {result}")
        except Exception as ex:
            print(f"  {name:46s} -> EXCEPTION: {ex}")
            failures.append(f"'{name}' threw: {ex}")

        # ---- SC2 questionMarkOpens ----
        name = "questionMarkOpens"
        try:
            # fresh page load to clear any overlay state
            pg.goto(base_url, wait_until="networkidle")
            time.sleep(0.5)
            result = pg.evaluate(SC2)
            ok = result.get("pass") is True
            print(f"  {name:46s} -> {'PASS' if ok else 'FAIL'}  {result}")
            if not ok:
                failures.append(f"'{name}' failed: {result}")
        except Exception as ex:
            print(f"  {name:46s} -> EXCEPTION: {ex}")
            failures.append(f"'{name}' threw: {ex}")

        # ---- SC3 escapeCloses ----
        name = "escapeCloses"
        try:
            result = pg.evaluate(SC3)
            ok = result.get("pass") is True
            print(f"  {name:46s} -> {'PASS' if ok else 'FAIL'}  {result}")
            if not ok:
                failures.append(f"'{name}' failed: {result}")
        except Exception as ex:
            print(f"  {name:46s} -> EXCEPTION: {ex}")
            failures.append(f"'{name}' threw: {ex}")

        # ---- SC4 clickOutsideCloses ----
        name = "clickOutsideCloses"
        try:
            result = pg.evaluate(SC4)
            ok = result.get("pass") is True
            print(f"  {name:46s} -> {'PASS' if ok else 'FAIL'}  {result}")
            if not ok:
                failures.append(f"'{name}' failed: {result}")
        except Exception as ex:
            print(f"  {name:46s} -> EXCEPTION: {ex}")
            failures.append(f"'{name}' threw: {ex}")

        # ---- SC5 inputFocusGuards ----
        name = "inputFocusGuards"
        try:
            result = pg.evaluate(SC5)
            ok = result.get("pass") is True
            print(f"  {name:46s} -> {'PASS' if ok else 'FAIL'}  {result}")
            if not ok:
                failures.append(f"'{name}' failed: {result}")
        except Exception as ex:
            print(f"  {name:46s} -> EXCEPTION: {ex}")
            failures.append(f"'{name}' threw: {ex}")

        # ---- SC6 contentHasAllSections ----
        name = "contentHasAllSections"
        try:
            result = pg.evaluate(SC6)
            ok = result.get("pass") is True
            print(f"  {name:46s} -> {'PASS' if ok else 'FAIL'}  {result}")
            if not ok:
                failures.append(f"'{name}' failed: {result}")
        except Exception as ex:
            print(f"  {name:46s} -> EXCEPTION: {ex}")
            failures.append(f"'{name}' threw: {ex}")

        pg.close()
        b.close()

    for e in page_errors:
        print("  JS ERROR:", e)

    server.should_exit = True
    time.sleep(0.4)

    if failures:
        for f in failures:
            print("FAIL:", f)
        print("LITE_CHEATSHEET_FAIL")
        sys.exit(1)
    else:
        print("LITE_CHEATSHEET_OK")


if __name__ == "__main__":
    main()
