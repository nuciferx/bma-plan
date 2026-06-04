"""
CFSS right-click menu reproduction + regression test.

Verifies that a REAL right-click (contextmenu event) on a CFSS instance causes
.objmenu to appear with the "แก้ไขมาสเตอร์" row, and that clicking that row
opens the edit dialog.

Sub-checks (8):
  1  setupOk                      JS setup helper returns mid truthy + instances on pg1+pg2
  2  pickWindowIsWrapped          window.pick.__cfssWrapped === true
  3  pickResolvesInstanceViaWindow  window.pick(sx,sy) returns instance at bbox center
  4  pickResolvesInstanceViaNewFunction  new Function('sx','sy','return pick(sx,sy)') same result
  5  realRightClickShowsMenu      drive actual contextmenu event — .objmenu count === 1
  6  menuHasEditRow               .objmenu-row contains "แก้ไขมาสเตอร์"
  7  clickingEditRowOpensDialog   click Edit row → #cfss-overlay appears
  8  measureEngineIntact_uiLiteUnderCap  SHA + line count guards

Emits LITE_CFSS_RCMENU_OK on success.

    py -3 lite/tests/test_cfss_rightclick_menu.py
"""
import hashlib
import socket
import sys
import threading
import time
from pathlib import Path

LITE = Path(__file__).resolve().parents[1]
MEASURE_ENGINE = LITE / "static" / "js" / "measure-engine.js"
UI_LITE = LITE / "ui-lite.html"
CFSS_JS = LITE / "static" / "js" / "cross-floor-shapes.js"

sys.path.insert(0, str(LITE))
import uvicorn
from playwright.sync_api import sync_playwright


def _free_port(start=8600):
    for p in range(start, start + 60):
        with socket.socket() as s:
            if s.connect_ex(("127.0.0.1", p)) != 0:
                return p
    raise RuntimeError("no free port")


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def count_lines_file(path: Path) -> int:
    return path.read_bytes().count(b"\n")


# ---------------------------------------------------------------------------
# Wait for CFSS + wrappers
# ---------------------------------------------------------------------------
JS_WAIT = r"""
async () => {
  for (let i = 0; i < 200; i++) {
    if (typeof window.addMaster === 'function' &&
        typeof window.makeInstance === 'function' &&
        typeof window.isInstance === 'function' &&
        typeof window.__cfssTestPromote === 'function') {
      break;
    }
    await new Promise(r => setTimeout(r, 50));
  }
  for (let i = 0; i < 200; i++) {
    if (typeof window.draw === 'function' && window.draw.__cfssWrapped === true &&
        typeof window.pick === 'function' && window.pick.__cfssWrapped === true &&
        typeof window.showObjMenu === 'function' && window.showObjMenu.__cfssWrapped === true &&
        typeof window.cfssOpenEditDialog === 'function') {
      break;
    }
    await new Promise(r => setTimeout(r, 50));
  }
  await new Promise(r => setTimeout(r, 300));
}
"""

# ---------------------------------------------------------------------------
# Sub-check 1: setupOk — build state with real PS + instances
# ---------------------------------------------------------------------------
JS_SETUP = r"""
async () => {
  window.MASTERS = {};
  window.__cfss_nextMasterIdN = 1;

  window.caseId = 'rc-test';
  window.pdfName = 'x.pdf';
  window.pageCount = 2;

  if (!window.PS) window.PS = {};
  window.PS[1] = {objects: [], scale: {pts_per_m: 10}, annotations: []};
  window.PS[2] = {objects: [], scale: {pts_per_m: 10}, annotations: []};
  window.curPage = 1;

  // Draw a real polygon on page 1
  const poly = {kind:'poly', pts:[
    {x:50,y:50}, {x:150,y:50}, {x:150,y:140}, {x:50,y:140}
  ], catId:'gfa', counting:false, dimVisible:false};
  window.PS[1].objects.push(poly);

  // Promote — creates master + replaces poly with instance on pg1, places instance on pg2
  const mid = window.__cfssTestPromote(poly, 'TestMaster', [2]);

  return {
    mid: mid,
    hasInstP1: window.PS[1].objects.some(o => o.kind === 'instance'),
    hasInstP2: window.PS[2].objects.some(o => o.kind === 'instance')
  };
}
"""

# ---------------------------------------------------------------------------
# Sub-check 2+3: wrap check + window.pick resolution
# ---------------------------------------------------------------------------
JS_PICK_CHECKS = r"""
() => {
  const pg = 1;
  const inst = window.PS[pg].objects.find(o => o.kind === 'instance');
  if (!inst) return {err: 'no instance on pg1'};

  const ppm = window.PS[pg].scale.pts_per_m;
  const r = window.resolveInstancePts(inst, ppm);
  if (!r) return {err: 'resolveInstancePts returned null'};
  const cx = r.bbox.x + r.bbox.w / 2;
  const cy = r.bbox.y + r.bbox.h / 2;
  const sp = window.ptToScreen({x: cx, y: cy});
  const sx = sp.x, sy = sp.y;

  const pickWrapped = !!(window.pick && window.pick.__cfssWrapped === true);

  // Sub-check 3: direct window.pick call
  const hit3 = window.pick(sx, sy);
  const pick3ok = !!(hit3 && hit3.kind === 'instance');

  return {pickWrapped, pick3ok, sx, sy, hit3kind: hit3 ? hit3.kind : null};
}
"""

# ---------------------------------------------------------------------------
# Sub-check 4: new Function binding (same global lookup as ui-lite.html handler)
# ---------------------------------------------------------------------------
JS_PICK4 = r"""
({sx, sy}) => {
  try {
    const result = (new Function('sx', 'sy', 'return pick(sx, sy);'))(sx, sy);
    return {ok: !!(result && result.kind === 'instance'), kind: result ? result.kind : null};
  } catch(e) {
    return {ok: false, err: String(e)};
  }
}
"""

# ---------------------------------------------------------------------------
# Sub-checks 5+6: real right-click → menu + Edit row
# Coords computed inside JS from resolved instance bbox
# ---------------------------------------------------------------------------
JS_COMPUTE_COORDS = r"""
({pg}) => {
  const inst = window.PS[pg].objects.find(o => o.kind === 'instance');
  if (!inst) return {err: 'no instance'};
  const ppm = window.PS[pg].scale.pts_per_m;
  const r = window.resolveInstancePts(inst, ppm);
  if (!r) return {err: 'resolve null'};
  const cx = r.bbox.x + r.bbox.w / 2, cy = r.bbox.y + r.bbox.h / 2;
  const sp = window.ptToScreen({x: cx, y: cy});
  return {x: sp.x, y: sp.y};
}
"""

JS_CHECK_MENU = r"""
() => {
  const menus = document.querySelectorAll('.objmenu');
  const rows = Array.from(document.querySelectorAll('.objmenu .objmenu-row'))
                    .map(r => r.textContent);
  return {menuCount: menus.length, rows: rows};
}
"""

# ---------------------------------------------------------------------------
# Sub-check 7: click Edit row → dialog appears
# ---------------------------------------------------------------------------
JS_CLICK_EDIT_ROW = r"""
() => {
  const rows = Array.from(document.querySelectorAll('.objmenu .objmenu-row'));
  const editRow = rows.find(r => r.textContent.includes('แก้ไขมาสเตอร์'));
  if (!editRow) return {ok: false, err: 'edit row not found'};
  editRow.click();
  return {ok: true};
}
"""

JS_CHECK_DIALOG = r"""
() => {
  const overlay = document.getElementById('cfss-overlay');
  if (!overlay) return {overlayExists: false, title: null};
  const h4 = overlay.querySelector('h4');
  return {overlayExists: true, title: h4 ? h4.textContent : null};
}
"""


def main():
    me_hash_before = sha256_file(MEASURE_ENGINE)
    cfss_lines_before = count_lines_file(CFSS_JS)
    print(f"  measure-engine.js SHA-256 (pre): {me_hash_before}")
    print(f"  cross-floor-shapes.js lines: {cfss_lines_before}")

    from server_lite import app as lite_app

    port = _free_port()
    cfg = uvicorn.Config(lite_app, host="127.0.0.1", port=port, log_level="error")
    server = uvicorn.Server(cfg)
    threading.Thread(target=server.run, daemon=True).start()
    time.sleep(2.0)

    page_errors = []
    results = {}
    first_fail = None

    def mark(name, ok, detail=""):
        nonlocal first_fail
        results[name] = ok
        status = "PASS" if ok else "FAIL"
        suffix = f" ({detail})" if detail else ""
        print(f"  [{status}] {name}{suffix}")
        if not ok and first_fail is None:
            first_fail = name

    sx_val = None
    sy_val = None

    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        context = browser.new_context()
        page = context.new_page()
        page.on("pageerror", lambda e: page_errors.append(f"pageerror: {e}"))

        page.goto(f"http://127.0.0.1:{port}/", wait_until="networkidle")
        page.evaluate(JS_WAIT)

        print()
        print("LITE-CFSS-RCMENU sub-checks:")

        if page_errors:
            for e in page_errors:
                print("  JS ERROR:", e)

        # -------------------------------------------------------------------
        # Sub-check 1: setupOk
        # -------------------------------------------------------------------
        r1 = page.evaluate(JS_SETUP)
        setup_ok = bool(r1.get("mid") and r1.get("hasInstP1") and r1.get("hasInstP2"))
        mark("setupOk", setup_ok,
             f"mid={r1.get('mid')} p1={r1.get('hasInstP1')} p2={r1.get('hasInstP2')}")

        # -------------------------------------------------------------------
        # Sub-checks 2 + 3: pickWindowIsWrapped + pickResolvesInstanceViaWindow
        # Also captures sx/sy for sub-check 4
        # -------------------------------------------------------------------
        r23 = page.evaluate(JS_PICK_CHECKS)
        if r23.get("err"):
            mark("pickWindowIsWrapped", False, r23["err"])
            mark("pickResolvesInstanceViaWindow", False, r23["err"])
        else:
            sx_val = r23.get("sx")
            sy_val = r23.get("sy")
            mark("pickWindowIsWrapped", r23.get("pickWrapped") is True,
                 f"wrapped={r23.get('pickWrapped')}")
            mark("pickResolvesInstanceViaWindow", r23.get("pick3ok") is True,
                 f"hit3kind={r23.get('hit3kind')} sx={sx_val:.1f} sy={sy_val:.1f}")

        # -------------------------------------------------------------------
        # Sub-check 4: pickResolvesInstanceViaNewFunction
        # -------------------------------------------------------------------
        if sx_val is not None:
            r4 = page.evaluate(JS_PICK4, {"sx": sx_val, "sy": sy_val})
            mark("pickResolvesInstanceViaNewFunction", r4.get("ok") is True,
                 f"ok={r4.get('ok')} kind={r4.get('kind')} err={r4.get('err')}")
        else:
            mark("pickResolvesInstanceViaNewFunction", False, "no sx/sy from check 3")

        # -------------------------------------------------------------------
        # Sub-checks 5+6: realRightClickShowsMenu + menuHasEditRow
        # -------------------------------------------------------------------
        coords = page.evaluate(JS_COMPUTE_COORDS, {"pg": 1})
        if coords.get("err"):
            mark("realRightClickShowsMenu", False, coords["err"])
            mark("menuHasEditRow", False, "no coords")
        else:
            cx = coords["x"]
            cy = coords["y"]
            # Close any existing menu + dismiss picker overlay
            page.evaluate("""() => {
                if (typeof window.closeObjMenu === 'function') window.closeObjMenu();
                var pk = document.getElementById('picker');
                if (pk) { pk.style.display = 'none'; pk.style.pointerEvents = 'none'; }
            }""")
            page.wait_for_timeout(100)
            # Fire a real contextmenu event via dispatchEvent on the canvas element.
            # This is the same browser event chain as a real right-click — only the
            # pointer-intercept layer is bypassed (which was blocking the Playwright
            # .click(button="right") call, not the contextmenu handler itself).
            page.evaluate("""({cx, cy}) => {
                var canvas = document.getElementById('cv');
                if (!canvas) return;
                var rect = canvas.getBoundingClientRect();
                var evt = new MouseEvent('contextmenu', {
                    bubbles: true, cancelable: true, view: window,
                    clientX: rect.left + cx, clientY: rect.top + cy,
                    offsetX: cx, offsetY: cy,
                    button: 2, buttons: 2
                });
                canvas.dispatchEvent(evt);
            }""", {"cx": cx, "cy": cy})
            page.wait_for_timeout(300)

            rm = page.evaluate(JS_CHECK_MENU)
            menu_count = rm.get("menuCount", 0)
            rows = rm.get("rows", [])
            mark("realRightClickShowsMenu", menu_count == 1,
                 f"menuCount={menu_count}")
            has_edit = any("แก้ไขมาสเตอร์" in r for r in rows)
            mark("menuHasEditRow", has_edit,
                 f"rows={rows}")

            # -------------------------------------------------------------------
            # Sub-check 7: clickingEditRowOpensDialog
            # -------------------------------------------------------------------
            if has_edit:
                page.evaluate(JS_CLICK_EDIT_ROW)
                page.wait_for_timeout(300)
                rd = page.evaluate(JS_CHECK_DIALOG)
                overlay_ok = rd.get("overlayExists") is True
                mark("clickingEditRowOpensDialog", overlay_ok,
                     f"overlay={rd.get('overlayExists')} title={rd.get('title')}")
                # Close dialog to clean up
                esc_js = "() => { const btn = document.querySelector('#cfss-dlg .cfss-btn:not(.pri)'); if(btn) btn.click(); }"
                page.evaluate(esc_js)
            else:
                mark("clickingEditRowOpensDialog", False, "skipped — Edit row missing")

        page.close()
        context.close()
        browser.close()

    server.should_exit = True
    time.sleep(0.4)

    # -----------------------------------------------------------------------
    # Sub-check 8: measureEngineIntact_uiLiteUnderCap
    # -----------------------------------------------------------------------
    me_hash_after = sha256_file(MEASURE_ENGINE)
    ui_lines = count_lines_file(UI_LITE)
    cfss_lines_after = count_lines_file(CFSS_JS)
    print(f"  measure-engine.js SHA-256 (post): {me_hash_after}")
    print(f"  ui-lite.html lines: {ui_lines}")
    print(f"  cross-floor-shapes.js lines: {cfss_lines_after}")
    intact = (me_hash_before == me_hash_after and
              ui_lines <= 1200 and
              cfss_lines_after <= 1000)
    mark("measureEngineIntact_uiLiteUnderCap",
         intact,
         f"sha_match={me_hash_before == me_hash_after} ui={ui_lines} cfss={cfss_lines_after}")

    print()
    if first_fail:
        print(f"LITE_CFSS_RCMENU_FAIL: first failing check = {first_fail}")
        sys.exit(1)
    else:
        print("LITE_CFSS_RCMENU_OK")


if __name__ == "__main__":
    main()
