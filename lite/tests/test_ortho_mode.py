"""
LORTHO-1: test_ortho_mode.py — verifies sticky ortho mode (Shift+O).

Six scenarios (driven by real DOM events via Playwright):
  1. defaultOff               — fresh load (localStorage cleared): state.orthoOn === false
  2. shiftOToggles            — Shift+O toggles orthoOn; plain 'o' does NOT
  3. inputFocusGuards         — Shift+O inside <input> does NOT toggle
  4. orthoLocksAngleInLiveTarget — orthoOn=true produces angle-locked pt from liveTarget()
  5. menuItemTogglesAndLabelFlips — click #mi-ortho → state + label sync
  6. localStoragePersists     — toggle persists across page.reload()

Emits LITE_ORTHO_OK on success.

    py -3 lite/tests/test_ortho_mode.py
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
# SC1 — defaultOff
# ---------------------------------------------------------------------------
SC1 = """
() => {
    return {
        orthoOn: state.orthoOn,
        pass: state.orthoOn === false
    };
}
"""

# ---------------------------------------------------------------------------
# SC2 — shiftOToggles  (plain 'o' must NOT toggle)
# ---------------------------------------------------------------------------
SC2 = """
() => {
    // Reset to known off state
    state.orthoOn = false;

    // --- plain 'o' (no shift) must NOT toggle ---
    window.dispatchEvent(new KeyboardEvent('keydown', { key: 'o', shiftKey: false, bubbles: true }));
    var afterPlainO = state.orthoOn;  // must still be false

    // --- Shift+O: first press → true ---
    window.dispatchEvent(new KeyboardEvent('keydown', { key: 'o', shiftKey: true, bubbles: true }));
    var after1 = state.orthoOn;  // must be true

    // --- Shift+O: second press → false ---
    window.dispatchEvent(new KeyboardEvent('keydown', { key: 'o', shiftKey: true, bubbles: true }));
    var after2 = state.orthoOn;  // must be false

    return {
        afterPlainO: afterPlainO,
        after1: after1,
        after2: after2,
        pass: afterPlainO === false && after1 === true && after2 === false
    };
}
"""

# ---------------------------------------------------------------------------
# SC3 — inputFocusGuards
# ---------------------------------------------------------------------------
SC3 = """
() => {
    state.orthoOn = false;

    // Create a temporary input, focus it, then fire Shift+O
    var inp = document.createElement('input');
    document.body.appendChild(inp);
    inp.focus();
    inp.dispatchEvent(new KeyboardEvent('keydown', { key: 'o', shiftKey: true, bubbles: true }));
    var afterFocused = state.orthoOn;  // must still be false
    inp.blur();
    document.body.removeChild(inp);

    return {
        afterFocused: afterFocused,
        pass: afterFocused === false
    };
}
"""

# ---------------------------------------------------------------------------
# SC4 — orthoLocksAngleInLiveTarget
# Seed state with a draft point at origin, set orthoOn=true, position lastMouse
# to a screen position that maps to an off-axis PDF point (not at 0/45/90 etc.)
# liveTarget() must return an angle-locked pt.
# Then flip orthoOn=false → pt must be off-axis (not locked).
# ---------------------------------------------------------------------------
SC4 = """
() => {
    // Save context
    var prevPage = curPage;
    var prevImg  = curImg;
    var prevDraft = state.draft;
    var prevShift = state.shift;
    var prevOrtho = state.orthoOn;
    var prevSnap  = state.snapOn;
    var prevTool  = state.tool;

    // Set up a minimal environment
    var pg = 77;
    if (!PS[pg]) PS[pg] = { objects: [], scale: null, annotations: [] };
    PS[pg].scale = { pts_per_m: 1 };
    curPage = pg;
    if (!curImg) curImg = { width: 400, height: 400 };

    state.tool    = 'dist';
    state.shift   = false;
    state.snapOn  = false;

    // Place first draft point at PDF origin (0,0)
    state.draft = [{ x: 0, y: 0 }];

    // We need lastMouse to point at an off-axis location.
    // PDF point ~(50, 30) is off-axis (atan2(30,50) ≈ 0.54 rad, not a multiple of π/4).
    // Set lastMouse to the screen coords that map to (50,30).
    var s = ptToScreen({ x: 50, y: 30 });
    lastMouse = { x: s.x, y: s.y };

    // --- sub A: orthoOn=true → angle-locked ---
    state.orthoOn = true;
    var ltOn = liveTarget();
    // angleLock from (0,0) to (50,30): distance ≈ 58.3 pt, angle ≈ 0.54 rad
    // nearest π/4 step is π/4 (45°) → pt.x ≈ pt.y ≈ 41.23
    // Valid lock means the angle from prev to pt is a multiple of π/4 (within ε).
    var locked = false;
    if (ltOn) {
        var ax = ltOn.pt.x - 0, ay = ltOn.pt.y - 0;  // prev is (0,0)
        var ang = Math.atan2(ay, ax);
        var step = Math.PI / 4;
        var remainder = Math.abs(ang % step);
        // remainder near 0 or near step means it's on a π/4 multiple
        locked = remainder < 0.01 || Math.abs(remainder - step) < 0.01;
    }

    // --- sub B: orthoOn=false → raw (off-axis) ---
    state.orthoOn = false;
    var ltOff = liveTarget();
    // raw point should be close to (50, 30) — not axis-aligned
    var unlocked = ltOff && Math.abs(ltOff.pt.y) > 1 && Math.abs(ltOff.pt.x) > 1;

    // Restore
    curPage = prevPage;
    curImg  = prevImg;
    state.draft   = prevDraft;
    state.shift   = prevShift;
    state.orthoOn = prevOrtho;
    state.snapOn  = prevSnap;
    state.tool    = prevTool;
    lastMouse     = null;

    return {
        ptOn:    ltOn  ? { x: ltOn.pt.x,  y: ltOn.pt.y  } : null,
        ptOff:   ltOff ? { x: ltOff.pt.x, y: ltOff.pt.y } : null,
        locked:  locked,
        unlocked: unlocked,
        pass: locked && unlocked
    };
}
"""

# ---------------------------------------------------------------------------
# SC5 — menuItemTogglesAndLabelFlips
# ---------------------------------------------------------------------------
SC5 = """
() => {
    // Reset to known off state
    state.orthoOn = false;
    // Refresh label to off state
    if (typeof _refreshOrthoMenuLabel === 'function') _refreshOrthoMenuLabel();

    var el = document.getElementById('mi-ortho');
    if (!el) return { pass: false, reason: 'mi-ortho not found' };

    // --- click 1: off → on ---
    el.click();
    var afterClick1State = state.orthoOn;
    var afterClick1Label = el.textContent;
    var click1LabelOk   = afterClick1Label.indexOf('\\u2713') >= 0;  // ✓

    // --- click 2: on → off ---
    el.click();
    var afterClick2State = state.orthoOn;
    var afterClick2Label = el.textContent;
    var click2LabelOk   = afterClick2Label.indexOf('\\u2713') < 0;  // no ✓

    return {
        afterClick1State: afterClick1State,
        afterClick1Label: afterClick1Label,
        click1LabelOk:   click1LabelOk,
        afterClick2State: afterClick2State,
        afterClick2Label: afterClick2Label,
        click2LabelOk:   click2LabelOk,
        pass: afterClick1State === true && click1LabelOk &&
              afterClick2State === false && click2LabelOk
    };
}
"""

# ---------------------------------------------------------------------------
# SC6 — localStoragePersists (needs page reload — handled in Python)
# ---------------------------------------------------------------------------
SC6_TOGGLE = """
() => {
    state.orthoOn = false;
    // Toggle on via keyboard
    window.dispatchEvent(new KeyboardEvent('keydown', { key: 'o', shiftKey: true, bubbles: true }));
    return { orthoOn: state.orthoOn, toggled: state.orthoOn === true };
}
"""

SC6_AFTER_RELOAD = """
() => {
    return {
        orthoOn: state.orthoOn,
        pass: state.orthoOn === true
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
        print("LORTHO-1 ortho-mode checks:")

        # ---- SC1 defaultOff ----
        name = "defaultOff"
        try:
            pg.evaluate("() => { localStorage.removeItem('lite.orthoOn.v1'); }")
            pg.goto(base_url, wait_until="networkidle")
            time.sleep(0.5)
            result = pg.evaluate(SC1)
            ok = result.get("pass") is True
            print(f"  {name:46s} -> {'PASS' if ok else 'FAIL'}  {result}")
            if not ok:
                failures.append(f"'{name}' failed: {result}")
        except Exception as ex:
            print(f"  {name:46s} -> EXCEPTION: {ex}")
            failures.append(f"'{name}' threw: {ex}")

        # ---- SC2 shiftOToggles ----
        name = "shiftOToggles"
        try:
            result = pg.evaluate(SC2)
            ok = result.get("pass") is True
            print(f"  {name:46s} -> {'PASS' if ok else 'FAIL'}  {result}")
            if not ok:
                failures.append(f"'{name}' failed: {result}")
        except Exception as ex:
            print(f"  {name:46s} -> EXCEPTION: {ex}")
            failures.append(f"'{name}' threw: {ex}")

        # ---- SC3 inputFocusGuards ----
        name = "inputFocusGuards"
        try:
            result = pg.evaluate(SC3)
            ok = result.get("pass") is True
            print(f"  {name:46s} -> {'PASS' if ok else 'FAIL'}  {result}")
            if not ok:
                failures.append(f"'{name}' failed: {result}")
        except Exception as ex:
            print(f"  {name:46s} -> EXCEPTION: {ex}")
            failures.append(f"'{name}' threw: {ex}")

        # ---- SC4 orthoLocksAngleInLiveTarget ----
        name = "orthoLocksAngleInLiveTarget"
        try:
            result = pg.evaluate(SC4)
            ok = result.get("pass") is True
            print(f"  {name:46s} -> {'PASS' if ok else 'FAIL'}  {result}")
            if not ok:
                failures.append(f"'{name}' failed: {result}")
        except Exception as ex:
            print(f"  {name:46s} -> EXCEPTION: {ex}")
            failures.append(f"'{name}' threw: {ex}")

        # ---- SC5 menuItemTogglesAndLabelFlips ----
        name = "menuItemTogglesAndLabelFlips"
        try:
            result = pg.evaluate(SC5)
            ok = result.get("pass") is True
            print(f"  {name:46s} -> {'PASS' if ok else 'FAIL'}  {result}")
            if not ok:
                failures.append(f"'{name}' failed: {result}")
        except Exception as ex:
            print(f"  {name:46s} -> EXCEPTION: {ex}")
            failures.append(f"'{name}' threw: {ex}")

        # ---- SC6 localStoragePersists ----
        name = "localStoragePersists"
        try:
            pg.evaluate("() => { localStorage.removeItem('lite.orthoOn.v1'); }")
            pg.goto(base_url, wait_until="networkidle")
            time.sleep(0.5)

            r_before = pg.evaluate(SC6_TOGGLE)
            toggled_ok = r_before.get("toggled") is True

            pg.reload(wait_until="networkidle")
            time.sleep(0.8)

            r_after = pg.evaluate(SC6_AFTER_RELOAD)
            persist_ok = r_after.get("pass") is True

            ok = toggled_ok and persist_ok
            print(f"  {name:46s} -> {'PASS' if ok else 'FAIL'}  before={r_before}  after={r_after}")
            if not ok:
                failures.append(f"'{name}' failed: before={r_before} after={r_after}")
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
        print("LITE_ORTHO_FAIL")
        sys.exit(1)
    else:
        print("LITE_ORTHO_OK")


if __name__ == "__main__":
    main()
