"""
LEMPTY-1: test_empty_hub.py — verifies the empty-state hub for BMA-Plan Lite.

Five checks driven by real DOM events via Playwright (no internal-function bypass):

1. hubVisibleOnEmpty         — fresh load: .empty-hub exists, not hidden, contains
                               Thai tagline "วัดพื้นที่จาก PDF" and both mandatory buttons.
2. openPdfButtonTriggersFileInput — stub file-pdf.click BEFORE action; click #hub-open-pdf
                               via real el.click(); assert stub called once.
3. recentProjectsShowsIfPresent — set localStorage, reload, assert both filenames in
                               #hub-recent; then remove key, reload, assert #hub-recent empty.
4. dragoverDropAcceptsPdfFile — dispatch real dragover on hub (no throw); stub
                               window.handlePdfFile BEFORE drop; dispatch drop with
                               synthetic DataTransfer carrying a PDF File; assert stub called.
5. hubHidesAfterPageLoad     — spy on window.hideEmptyHub; call afterPage() directly
                               (it's the page-render hook, per spec); assert spy called ≥1
                               AND .empty display === 'none'.

Emits LITE_EMPTY_HUB_OK on success.

    py -3 lite/tests/test_empty_hub.py
"""
import socket, threading, time, sys, io
from pathlib import Path

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
# Check 1 — hubVisibleOnEmpty
# ---------------------------------------------------------------------------
SC1 = """
() => {
    var hub = document.querySelector('.empty-hub');
    if (!hub) return { pass: false, reason: '.empty-hub not found' };
    var container = document.querySelector('.empty');
    var display = container ? getComputedStyle(container).display : 'none';
    var text = hub.textContent || '';
    var hasTagline = text.indexOf('วัดพื้นที่จาก PDF') >= 0;
    var btnPdf = document.getElementById('hub-open-pdf');
    var btnProj = document.getElementById('hub-open-project');
    return {
        hubFound: !!hub,
        containerDisplay: display,
        hasTagline: hasTagline,
        btnPdfFound: !!btnPdf,
        btnProjFound: !!btnProj,
        pass: !!hub && display !== 'none' && hasTagline && !!btnPdf && !!btnProj
    };
}
"""

# ---------------------------------------------------------------------------
# Check 2 — openPdfButtonTriggersFileInput
# ---------------------------------------------------------------------------
SC2 = """
() => {
    var inp = document.getElementById('file-pdf');
    if (!inp) return { pass: false, reason: '#file-pdf not found' };
    var calls = 0;
    var orig = inp.click.bind(inp);
    inp.click = function() { calls++; };
    var btn = document.getElementById('hub-open-pdf');
    if (!btn) return { pass: false, reason: '#hub-open-pdf not found' };
    btn.click();
    inp.click = orig;
    return { calls: calls, pass: calls === 1 };
}
"""

# ---------------------------------------------------------------------------
# Check 3 — recentProjectsShowsIfPresent
# (This check requires page reloads; handled specially below)
# ---------------------------------------------------------------------------

SC3_WITH_RECENT = """
() => {
    var el = document.getElementById('hub-recent');
    if (!el) return { pass: false, reason: '#hub-recent not found' };
    var text = el.textContent || '';
    return {
        text: text.substring(0, 120),
        hasA: text.indexOf('a.bmaplan') >= 0,
        hasB: text.indexOf('b.bmaplan') >= 0,
        pass: text.indexOf('a.bmaplan') >= 0 && text.indexOf('b.bmaplan') >= 0
    };
}
"""

SC3_WITHOUT_RECENT = """
() => {
    var el = document.getElementById('hub-recent');
    if (!el) return { pass: false, reason: '#hub-recent not found' };
    var text = (el.textContent || '').trim();
    return { text: text.substring(0, 60), isEmpty: text === '', pass: text === '' };
}
"""

# ---------------------------------------------------------------------------
# Check 4 — dragoverDropAcceptsPdfFile
# ---------------------------------------------------------------------------
SC4 = """
() => {
    var hub = document.querySelector('.empty') || document.querySelector('.empty-hub');
    if (!hub) return { pass: false, reason: 'hub container not found' };

    // Test dragover doesn't throw
    var dragoverOk = false;
    try {
        var dov = new DragEvent('dragover', { bubbles: true, cancelable: true });
        hub.dispatchEvent(dov);
        dragoverOk = true;
    } catch(e) {
        return { pass: false, reason: 'dragover threw: ' + e.message };
    }

    // Stub handlePdfFile before dispatching drop
    var stubCalls = 0;
    var stubFile = null;
    var origHandle = window.handlePdfFile;
    window.handlePdfFile = function(f) { stubCalls++; stubFile = f; };

    // DataTransfer constructor args don't reliably carry files in headless Chromium.
    // Instead, build a fake drop event with a custom dataTransfer object injected
    // via Object.defineProperty on the event instance so our drop listener can read
    // e.dataTransfer.files[0] correctly.
    var file = new File([new Uint8Array([0x25, 0x50, 0x44, 0x46])], 'test.pdf',
                        { type: 'application/pdf' });
    var fakeFiles = [file];
    fakeFiles[0] = file;
    Object.defineProperty(fakeFiles, 'length', { value: 1 });

    var dropEvt = new Event('drop', { bubbles: true, cancelable: true });
    Object.defineProperty(dropEvt, 'dataTransfer', {
        value: { files: fakeFiles, types: ['Files'] },
        writable: false
    });
    hub.dispatchEvent(dropEvt);

    window.handlePdfFile = origHandle;

    return {
        dragoverOk: dragoverOk,
        stubCalls: stubCalls,
        fileNameOk: stubFile ? stubFile.name === 'test.pdf' : false,
        pass: dragoverOk && stubCalls === 1 && (stubFile ? stubFile.name === 'test.pdf' : false)
    };
}
"""

# ---------------------------------------------------------------------------
# Check 5 — hubHidesAfterPageLoad
# ---------------------------------------------------------------------------
SC5 = """
() => {
    // Spy on window.hideEmptyHub
    var orig = window.hideEmptyHub;
    if (typeof orig !== 'function')
        return { pass: false, reason: 'hideEmptyHub not a function' };
    var spyCalls = 0;
    window.hideEmptyHub = function() { spyCalls++; orig(); };

    // afterPage() is the page-render hook that must call hideEmptyHub
    if (typeof afterPage !== 'function') {
        window.hideEmptyHub = orig;
        return { pass: false, reason: 'afterPage not found' };
    }
    afterPage();

    window.hideEmptyHub = orig;

    var container = document.querySelector('.empty');
    var display = container ? getComputedStyle(container).display : 'unknown';
    return {
        spyCalls: spyCalls,
        display: display,
        pass: spyCalls >= 1 && display === 'none'
    };
}
"""

CHECKS = [
    ("hubVisibleOnEmpty",            SC1,  ["pass"]),
    ("openPdfButtonTriggersFileInput", SC2, ["pass"]),
    ("dragoverDropAcceptsPdfFile",   SC4,  ["pass"]),
    ("hubHidesAfterPageLoad",        SC5,  ["pass"]),
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

        print()
        print("LEMPTY-1 hub checks:")

        for name, scenario, required_keys in CHECKS:
            try:
                result = pg.evaluate(scenario)
            except Exception as ex:
                print(f"  {name:44s} -> EXCEPTION: {ex}")
                failures.append(f"check '{name}' threw: {ex}")
                continue
            ok = all(result.get(k) is True for k in required_keys)
            status = "PASS" if ok else "FAIL"
            print(f"  {name:44s} -> {status}  {result}")
            if not ok:
                bad = [k for k in required_keys if result.get(k) is not True]
                failures.append(f"check '{name}' failed keys: {bad}  result={result}")

        # ------------------------------------------------------------------
        # Check 3 — recentProjectsShowsIfPresent (requires reload)
        # ------------------------------------------------------------------
        print()
        print("  check 3 (recentProjectsShowsIfPresent) — requires 2 reloads:")

        # Set key then reload
        pg.evaluate("""
            () => {
                localStorage.setItem('bmaPlan.recentProjects.v1',
                    JSON.stringify(['a.bmaplan', 'b.bmaplan']));
            }
        """)
        pg.reload(wait_until="networkidle")
        time.sleep(0.6)

        try:
            r3a = pg.evaluate(SC3_WITH_RECENT)
            ok3a = all(r3a.get(k) is True for k in ["pass"])
            print(f"    with recent   -> {'PASS' if ok3a else 'FAIL'}  {r3a}")
            if not ok3a:
                failures.append(f"check 'recentProjectsShowsIfPresent(with)' failed: {r3a}")
        except Exception as ex:
            print(f"    with recent   -> EXCEPTION: {ex}")
            failures.append(f"check 'recentProjectsShowsIfPresent(with)' threw: {ex}")

        # Remove key then reload
        pg.evaluate("""
            () => { localStorage.removeItem('bmaPlan.recentProjects.v1'); }
        """)
        pg.reload(wait_until="networkidle")
        time.sleep(0.6)

        try:
            r3b = pg.evaluate(SC3_WITHOUT_RECENT)
            ok3b = all(r3b.get(k) is True for k in ["pass"])
            print(f"    without recent-> {'PASS' if ok3b else 'FAIL'}  {r3b}")
            if not ok3b:
                failures.append(f"check 'recentProjectsShowsIfPresent(without)' failed: {r3b}")
        except Exception as ex:
            print(f"    without recent-> EXCEPTION: {ex}")
            failures.append(f"check 'recentProjectsShowsIfPresent(without)' threw: {ex}")

        pg.close()
        b.close()

    for e in page_errors:
        print("  JS ERROR:", e)

    server.should_exit = True
    time.sleep(0.4)

    if failures:
        for f in failures:
            print("FAIL:", f)
        print("LITE_EMPTY_HUB_FAIL")
        sys.exit(1)
    else:
        print()
        print("LITE_EMPTY_HUB_OK")


if __name__ == "__main__":
    main()
