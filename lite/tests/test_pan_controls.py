"""
BUG-20260521-lite-pan-controls regression guard.

Lite's view/navigation control system was impoverished vs proto/ui.html:
pan worked ONLY on left-drag in select/empty mode (any draw tool blocked it),
no spacebar pan, no middle-mouse pan, no zoom clamp, no fit/zoom shortcuts.
This sprint forked proto's view-control BEHAVIOR onto lite's ctx-transform
V={k,ox,oy,rot} model (coordinate math ptToScreen/screenToPt/RS untouched).

This test boots server_lite and drives synthetic mouse/keyboard/wheel events
against a dummy curImg (no PDF render needed — lite's inline script is classic,
so V/cv/setTool/spaceDown/ZMIN/ZMAX are window globals). It asserts:

  midPan          middle-button drag pans while a DRAW tool (poly) is active
  spacePanMidDraw spacebar-hold pan works WHILE poly tool active (headline bug)
  panToolDrag     H toggles a sticky pan tool; left-drag then pans
  selectPan       left-drag in select/empty mode still pans (no regression)
  clampMax/Min    wheel zoom is clamped to [ZMIN, ZMAX] (no runaway)
  wheelZoomIn     wheel-up increases zoom (smooth exp)
  actualSize      Ctrl+1 resets zoom to exactly 1.0
  fit             Ctrl+0 fit runs and leaves a finite positive zoom
  ctrlZoomIn      Ctrl+= zooms in about viewport center within clamp

Emits BUG_20260521_LITE_PAN_OK on success.

    py -3 lite/tests/test_pan_controls.py
"""
import socket, threading, time, sys
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


SCENARIO = r"""
() => {
  const out = {};
  // dummy image so the `if(!curImg)return` guards pass without a PDF render
  const dummy = document.createElement('canvas'); dummy.width = 300; dummy.height = 300;
  window.curImg = dummy;
  const rect = cv.getBoundingClientRect();
  const cx = rect.left + rect.width/2, cy = rect.top + rect.height/2;
  const md  = (btn) => cv.dispatchEvent(new MouseEvent('mousedown', {button:btn, clientX:cx, clientY:cy, bubbles:true, cancelable:true}));
  const mm  = (dx,dy) => window.dispatchEvent(new MouseEvent('mousemove', {clientX:cx+dx, clientY:cy+dy, bubbles:true}));
  const mu  = () => window.dispatchEvent(new MouseEvent('mouseup', {bubbles:true}));
  const key = (t,k,ctrl) => window.dispatchEvent(new KeyboardEvent(t, {key:k, ctrlKey:!!ctrl, bubbles:true, cancelable:true}));
  const whl = (dy) => cv.dispatchEvent(new WheelEvent('wheel', {deltaY:dy, clientX:cx, clientY:cy, bubbles:true, cancelable:true}));
  const reset = () => { V.k=1; V.ox=0; V.oy=0; V.rot=0; dragging=false; panning=false; spaceDown=false; state.panTool=false; };
  const eq = (a,b) => Math.round(a)===b;

  // 1. middle-button pan WHILE a draw tool (poly) is active
  setTool('poly'); reset();
  md(1); mm(40,30); mu();
  out.midPan = eq(V.ox,40) && eq(V.oy,30);

  // 2. spacebar-hold pan WHILE poly tool active (the headline bug)
  setTool('poly'); reset();
  key('keydown',' '); out.spaceArmed = (spaceDown === true);
  md(0); mm(25,15); mu();
  key('keyup',' ');
  out.spacePanMidDraw = eq(V.ox,25) && eq(V.oy,15) && spaceDown === false;

  // 3. H toggles a sticky pan tool; left-drag then pans in any mode
  setTool('poly'); reset();
  key('keydown','h'); out.panToolOn = (state.panTool === true);
  md(0); mm(-20,-10); mu();
  out.panToolDrag = eq(V.ox,-20) && eq(V.oy,-10);
  key('keydown','h'); out.panToolOff = (state.panTool === false);

  // 4. left-drag in select/empty mode still pans (no regression)
  setTool('select'); reset();
  md(0); mm(12,8); mu();
  out.selectPan = eq(V.ox,12) && eq(V.oy,8);

  // 5. wheel zoom clamp — upper bound
  reset(); V.k = ZMAX;
  for (let i=0;i<25;i++) whl(-300);
  out.clampMax = (V.k <= ZMAX + 1e-9);

  // 6. wheel zoom clamp — lower bound
  reset(); V.k = ZMIN;
  for (let i=0;i<25;i++) whl(300);
  out.clampMin = (V.k >= ZMIN - 1e-9);

  // 7. wheel-up increases zoom (smooth exponential)
  reset(); V.k = 1; whl(-120);
  out.wheelZoomIn = (V.k > 1);

  // 8. Ctrl+1 = actual size -> exactly 1.0
  reset(); V.k = 3.5; key('keydown','1',true);
  out.actualSize = (Math.abs(V.k - 1) < 1e-9);

  // 9. Ctrl+0 = fit -> finite positive zoom, no throw
  reset(); V.k = 99; key('keydown','0',true);
  out.fit = (isFinite(V.k) && V.k > 0);

  // 10. Ctrl+= zoom in about center, within clamp
  reset(); V.k = 1; key('keydown','=',true);
  out.ctrlZoomIn = (V.k > 1 && V.k <= ZMAX);

  return out;
}
"""

CHECKS = ["midPan", "spaceArmed", "spacePanMidDraw", "panToolOn", "panToolDrag",
          "panToolOff", "selectPan", "clampMax", "clampMin", "wheelZoomIn",
          "actualSize", "fit", "ctrlZoomIn"]


def main():
    from server_lite import app as lite_app
    port = _free_port()
    cfg = uvicorn.Config(lite_app, host="127.0.0.1", port=port, log_level="error")
    server = uvicorn.Server(cfg)
    threading.Thread(target=server.run, daemon=True).start()
    time.sleep(2.0)

    failures = []
    res = {}
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        pg = b.new_page()
        pg.on("pageerror", lambda e: failures.append(f"pageerror: {e}"))
        pg.goto(f"http://127.0.0.1:{port}/", wait_until="networkidle")
        time.sleep(0.6)
        res = pg.evaluate(SCENARIO)
        b.close()
    server.should_exit = True
    time.sleep(0.4)

    for k in CHECKS:
        ok = res.get(k)
        print(f"  {k:16s} -> {ok}")
        if ok is not True:
            failures.append(f"check '{k}' = {ok!r} (expected True)")

    if failures:
        for f in failures:
            print("FAIL:", f)
        print("BUG_20260521_LITE_PAN_FAIL")
        sys.exit(1)
    print("BUG_20260521_LITE_PAN_OK")


if __name__ == "__main__":
    main()
