"""
LITE-LIVE regression guard.

Lite's measurement-display feedback was impoverished vs proto/ui.html: it drew
only the polyline between PLACED draft points (no rubber-band to the cursor), had
no live segment length / running total / area preview, no cursor-guide crosshair,
no coordinate readout, and the Shift angle-lock guide was a bare line with no
length/angle label. This sprint forked proto's redraw() in-progress overlay onto
lite as a single drawLiveOverlay() — pure overlay, no area-math / transform change
(ptToScreen / screenToPt / RS / polyAreaM2 untouched; polyAreaM2 only READ for the
live area preview).

Boots server_lite and drives the live-overlay helpers against a dummy curImg
(lite's inline script is classic, so state/V/cv/draw/liveTarget/fmtPtLen/
drawLiveOverlay are window globals). Asserts:

  fmtMeters       length formats as metres when the page scale is set
  fmtPt           length falls back to pt when no scale
  nullWhenSelect  liveTarget() is null outside a draw tool
  targetRaw       liveTarget() returns the raw cursor point (no snap/lock)
  targetSnap      liveTarget() honours an active snap hint
  targetLock      liveTarget() honours Shift angle-lock when a draft exists
  overlayNoThrow  drawLiveOverlay() runs during a poly draft without throwing
  coordReadout    a real draw() writes the live x,y coordinate into the HUD
  gatedWhilePan   drawLiveOverlay() short-circuits while panning (no throw)

Emits LITE_LIVE_OVERLAY_OK on success.

    py -3 lite/tests/test_live_overlay.py
"""
import socket, threading, time, sys
from pathlib import Path

LITE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LITE))
import uvicorn
from playwright.sync_api import sync_playwright


def _free_port(start=8260):
    for p in range(start, start + 60):
        with socket.socket() as s:
            if s.connect_ex(("127.0.0.1", p)) != 0:
                return p
    raise RuntimeError("no free port")


SCENARIO = r"""
() => {
  const out = {};
  const dummy = document.createElement('canvas'); dummy.width = 400; dummy.height = 400;
  window.curImg = dummy;
  curPage = 1; PS[1] = {objects:[], scale:{pts_per_m:10}, annotations:[]};
  setTool('poly');

  // length formatting: metres with scale, pt without
  out.fmtMeters = fmtPtLen(100).indexOf('m') >= 0 && fmtPtLen(100).indexOf('pt') < 0;
  PS[1].scale = null; out.fmtPt = fmtPtLen(100).indexOf('pt') >= 0; PS[1].scale = {pts_per_m:10};

  // liveTarget is null outside a draw tool
  setTool('select'); lastMouse = {x:50, y:60};
  out.nullWhenSelect = (liveTarget() === null);
  setTool('poly');

  // raw cursor point when no draft / no snap / no shift
  state.draft = null; state.snapHint = null; state.shift = false; lastMouse = {x:50, y:60};
  const lt0 = liveTarget(); out.targetRaw = !!lt0 && !lt0.locked && !lt0.snapped;

  // honours an active snap hint
  state.snapOn = true; state.snapHint = {pt:{x:5,y:5}, screen:{x:10,y:10}, type:'endpoint'};
  const lt1 = liveTarget(); out.targetSnap = !!lt1 && lt1.snapped === true && lt1.pt.x === 5;
  state.snapHint = null;

  // honours Shift angle-lock when a draft point exists
  state.draft = [screenToPt(100,100)]; state.shift = true; lastMouse = {x:160, y:105};
  const lt2 = liveTarget(); out.targetLock = !!lt2 && lt2.locked === true;
  state.shift = false;

  // drawLiveOverlay runs during a multi-point poly draft without throwing
  state.draft = [screenToPt(80,80), screenToPt(160,90)]; lastMouse = {x:200, y:140};
  let threw = false; try { drawLiveOverlay(); } catch (e) { threw = true; out.err = String(e); }
  out.overlayNoThrow = !threw;

  // a real draw() writes the live coordinate into the HUD
  draw();
  const hud = document.getElementById('hud-bl').innerHTML;
  out.coordReadout = /xy/.test(hud) && /\d+,\d+/.test(hud);

  // overlay short-circuits while panning (no throw, returns early)
  panning = true; let threw2 = false; try { drawLiveOverlay(); } catch (e) { threw2 = true; } panning = false;
  out.gatedWhilePan = !threw2;

  return out;
}
"""

CHECKS = ["fmtMeters", "fmtPt", "nullWhenSelect", "targetRaw", "targetSnap",
          "targetLock", "overlayNoThrow", "coordReadout", "gatedWhilePan"]


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
        print("LITE_LIVE_OVERLAY_FAIL")
        sys.exit(1)
    print("LITE_LIVE_OVERLAY_OK")


if __name__ == "__main__":
    main()
