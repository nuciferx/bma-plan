"""
SNAP-2026-07-04 slice 2/3 — test_snap_ray.py

Verifies computeSnapOnRay() (angle-lock + snap COMPOSITION — CAD "apparent
intersection" semantics) and the slice-1 residual-risk closure (mouseup now
busts the snap cache after a vertex-drag / move-object drag).

Six checks (mirrors the SNAP-2026-07-04 slice 2 spec's acceptance list):
  (a) rayCrossSegment     — locked ray (45 deg from origin (0,0)) crossing a
                            static segment returns "ray-x" ON the ray, at the
                            point an independent analytic calc (done in this
                            test, not by calling computeSnapOnRay twice) says
                            it must be.
  (b) rayEndpointProjects — an endpoint near (but not on) the ray, with no
                            competing ray-x candidate, returns "ray-end" at
                            the PERPENDICULAR PROJECTION of that endpoint
                            onto the ray (not the endpoint itself).
  (c) rayNullFallsBack    — an empty page (nothing in range) -> null; the
                            real liveTarget() then falls back to the EXACT
                            angleLock() point.
  (d) unlockedUnchanged   — a plain computeSnap() regression probe (shift/
                            ortho both off) — proves slice 2 did not touch
                            computeSnap()'s own behavior.
  (e) clickEqualsPreview  — real DOM mousemove then mousedown at the SAME
                            screen position: the committed draft point
                            equals liveTarget()'s preview point, because
                            both paths call computeSnapOnRay().
  (f) mouseupInvalidates  — a real vertex-drag (mousedown on a vertex ->
                            mousemove past the 3px threshold -> mouseup)
                            changes a segment's crossing point; computeSnap()
                            no longer reports the OLD crossing and correctly
                            reports the NEW one — proving mouseup's
                            snapInvalidate() call closed the slice-1 gap.

Emits LITE_SNAP_RAY_OK on success.

    py -3 lite/tests/test_snap_ray.py
"""
import socket, threading, time, sys, io
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

LITE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LITE))
import uvicorn
from playwright.sync_api import sync_playwright


def _free_port(start=8620):
    for p in range(start, start + 60):
        with socket.socket() as s:
            if s.connect_ex(("127.0.0.1", p)) != 0:
                return p
    raise RuntimeError("no free port")


# Shared helpers injected once: a canvas-relative synthetic-event dispatcher
# and a common "reset to a known baseline" routine.
JS_PRELUDE = """
() => {
    window.__prevImg = curImg; if (!curImg) curImg = { width: 800, height: 800 };
    window.__prevV = { k: V.k, ox: V.ox, oy: V.oy, rot: V.rot };
    V.k = 1; V.ox = 0; V.oy = 0; V.rot = 0;

    // Dispatch a synthetic MouseEvent on the real <canvas> at canvas-local
    // (offsetX/offsetY-equivalent) coordinates sx,sy — drives the ACTUAL
    // production event handlers (cv.addEventListener(...)), not a re-implementation.
    window.__dispatchAt = function (type, sx, sy, opts) {
        var r = cv.getBoundingClientRect();
        var init = Object.assign({
            clientX: r.left + sx, clientY: r.top + sy,
            bubbles: true, cancelable: true, button: 0
        }, opts || {});
        cv.dispatchEvent(new MouseEvent(type, init));
    };
    return { ok: true };
}
"""

JS_TEARDOWN = """
() => {
    curImg = window.__prevImg;
    V.k = window.__prevV.k; V.ox = window.__prevV.ox; V.oy = window.__prevV.oy; V.rot = window.__prevV.rot;
    state.draft = null; state.vertMode = null; state.vertEdit = null; state.tool = 'poly';
    state.shift = false; state.orthoOn = false;
    return { ok: true };
}
"""

# ---------------------------------------------------------------------------
# (a) rayCrossSegment
# Ray from origin (0,0) locked to 45 deg (cursor at raw (43,43) is exactly ON
# that ray, so quantization is unambiguous) and close enough (within SNAP_PX)
# to the expected candidate that it actually wins the "nearest to cursor"
# tie-break. Static segment S1 is the horizontal line y=40, x in [-10,90] ->
# analytic crossing with y=x is exactly (40,40); |(43,43)-(40,40)| = 4.24 pt
# = 6.36 screen px < SNAP_PX(11).
# ---------------------------------------------------------------------------
JS_CHECK_A = """
() => {
    var pg = 91;
    PS[pg] = { objects: [ { kind: 'line', pts: [{x:-10,y:40},{x:90,y:40}], counting:false, catId:'gfa' } ], scale:{pts_per_m:1}, annotations: [] };
    curPage = pg;
    state.tool = 'dist'; state.shift = false; state.orthoOn = true; state.snapOn = true;
    state.draft = [{x:0,y:0}];

    var origin = {x:0,y:0}, raw = {x:43,y:43};
    var la = _lockedAngle(origin, raw);
    var s = ptToScreen(raw);
    var res = computeSnapOnRay(s.x, s.y, origin, la);

    var ok = !!res && res.type === 'ray-x' && Math.abs(res.pt.x - 40) < 1e-6 && Math.abs(res.pt.y - 40) < 1e-6;
    return { pass: ok, res, la };
}
"""

# ---------------------------------------------------------------------------
# (b) rayEndpointProjects
# Only object present: a 2-pt line at x=25 spanning y in [32,60] — its own
# segment does NOT cross the ray (ray at x=25 has y=25, outside [32,60]), so
# the only candidate is endpoint (25,32) projected onto the ray y=x. Analytic
# foot of (25,32) onto y=x is ((25+32)/2, (25+32)/2) = (28.5, 28.5). Cursor
# raw (30,30) is exactly on the ray and close to that foot (within SNAP_PX).
# ---------------------------------------------------------------------------
JS_CHECK_B = """
() => {
    var pg = 92;
    PS[pg] = { objects: [ { kind:'line', pts:[{x:25,y:32},{x:25,y:60}], counting:false, catId:'gfa' } ], scale:{pts_per_m:1}, annotations: [] };
    curPage = pg;
    state.tool = 'dist'; state.shift = false; state.orthoOn = true; state.snapOn = true;
    state.draft = [{x:0,y:0}];

    var origin = {x:0,y:0}, raw = {x:30,y:30};
    var la = _lockedAngle(origin, raw);
    var s = ptToScreen(raw);
    var res = computeSnapOnRay(s.x, s.y, origin, la);

    var ok = !!res && res.type === 'ray-end' && Math.abs(res.pt.x - 28.5) < 1e-6 && Math.abs(res.pt.y - 28.5) < 1e-6;
    return { pass: ok, res };
}
"""

# ---------------------------------------------------------------------------
# (c) rayNullFallsBack — empty page, nothing in range.
# ---------------------------------------------------------------------------
JS_CHECK_C = """
() => {
    var pg = 93;
    PS[pg] = { objects: [], scale:{pts_per_m:1}, annotations: [] };
    curPage = pg;
    state.tool = 'dist'; state.shift = false; state.orthoOn = true; state.snapOn = true;
    state.draft = [{x:0,y:0}];

    var origin = {x:0,y:0}, raw = {x:50,y:30};
    var la = _lockedAngle(origin, raw);
    var s = ptToScreen(raw);
    var rayRes = computeSnapOnRay(s.x, s.y, origin, la);

    lastMouse = { x: s.x, y: s.y };
    var lt = liveTarget();
    var expect = angleLock(origin, raw);
    var ltMatchesLock = !!lt && Math.abs(lt.pt.x - expect.x) < 1e-6 && Math.abs(lt.pt.y - expect.y) < 1e-6;

    lastMouse = null;
    return { pass: rayRes === null && ltMatchesLock, rayRes, ltPt: lt ? lt.pt : null, expect };
}
"""

# ---------------------------------------------------------------------------
# (d) unlockedUnchanged — plain computeSnap() regression probe.
# ---------------------------------------------------------------------------
JS_CHECK_D = """
() => {
    var pg = 94;
    PS[pg] = { objects: [ { kind:'poly', pts:[{x:0,y:0},{x:100,y:0},{x:100,y:100},{x:0,y:100}], counting:false, catId:'gfa' } ], scale:{pts_per_m:1}, annotations: [] };
    curPage = pg;
    state.tool = 'poly'; state.shift = false; state.orthoOn = false; state.snapOn = true;
    state.draft = null;

    var s = ptToScreen({x:1,y:1});
    var res = computeSnap(s.x, s.y);
    var ok = !!res && res.type === 'endpoint' && Math.abs(res.pt.x - 0) < 1e-6 && Math.abs(res.pt.y - 0) < 1e-6;
    return { pass: ok, res };
}
"""

# ---------------------------------------------------------------------------
# (e) clickEqualsPreview — real mousemove then mousedown at the same screen
# position; the committed point (pts[1] of the finished 'dist' object) must
# equal liveTarget()'s preview point, since both call computeSnapOnRay().
# ---------------------------------------------------------------------------
JS_CHECK_E = """
() => {
    var pg = 95;
    PS[pg] = { objects: [ { kind:'line', pts:[{x:-10,y:40},{x:90,y:40}], counting:false, catId:'gfa' } ], scale:{pts_per_m:1}, annotations: [] };
    curPage = pg;
    state.tool = 'dist'; state.shift = false; state.orthoOn = true; state.snapOn = true;
    state.draft = [{x:0,y:0}];
    state.activeCat = 'gfa'; state.catLock['gfa'] = false;

    var s = ptToScreen({x:43,y:43});   // on the 45 deg ray, close to the (40,40) crossing -> expect ray-x

    window.__dispatchAt('mousemove', s.x, s.y);
    var preview = liveTarget();

    window.__dispatchAt('mousedown', s.x, s.y, { button: 0 });
    window.__dispatchAt('mouseup',   s.x, s.y, { button: 0 });

    var objs = PS[pg].objects;
    var committed = objs[objs.length - 1];
    var committedPt = committed && committed.pts ? committed.pts[1] : null;

    var previewIsRay = !!preview && Math.abs(preview.pt.x - 40) < 1e-6 && Math.abs(preview.pt.y - 40) < 1e-6;
    var matches = !!committedPt && !!preview && Math.abs(committedPt.x - preview.pt.x) < 1e-6 && Math.abs(committedPt.y - preview.pt.y) < 1e-6;

    return { pass: previewIsRay && matches, previewPt: preview ? preview.pt : null, committedPt };
}
"""

# ---------------------------------------------------------------------------
# (f) mouseupInvalidates — real vertex-drag; mouseup must bust the cache.
# ---------------------------------------------------------------------------
JS_CHECK_F = """
() => {
    var pg = 96;
    var L1 = { kind:'line', pts:[{x:0,y:50},{x:100,y:50}], counting:false, catId:'gfa' };
    var L2 = { kind:'line', pts:[{x:50,y:0},{x:50,y:100}], counting:false, catId:'gfa' };
    PS[pg] = { objects: [L1, L2], scale:{pts_per_m:1}, annotations: [] };
    curPage = pg;
    state.tool = 'select'; state.shift = false; state.orthoOn = false; state.snapOn = true;
    state.draft = null; state.vertMode = L2; state.vertEdit = null;

    // force the static-intersection cache to build once, at the OLD crossing (50,50)
    var oldXY = ptToScreen({x:50,y:50});
    var before = computeSnap(oldXY.x, oldXY.y);
    var sawOldBefore = !!before && before.type === 'intersection' && Math.abs(before.pt.x-50)<1e-6 && Math.abs(before.pt.y-50)<1e-6;

    // real vertex-drag: grab L2's (50,100) vertex, drag it to (80,100)
    var vScr = ptToScreen({x:50,y:100});
    var tScr = ptToScreen({x:80,y:100});
    window.__dispatchAt('mousedown', vScr.x, vScr.y, { button: 0 });
    var enteredVertEdit = !!state.vertEdit;
    window.__dispatchAt('mousemove', tScr.x, tScr.y, { button: 0 });
    var moved = !!state.vertEdit && state.vertEdit.moved;
    window.__dispatchAt('mouseup', tScr.x, tScr.y, { button: 0 });
    var clearedAfter = !state.vertEdit;

    // new crossing analytic: L2 now (50,0)-(80,100); at y=50, s=0.5 -> x=65
    var newXY = ptToScreen({x:65,y:50});
    var afterOld = computeSnap(oldXY.x, oldXY.y);
    var oldGone = !(afterOld && afterOld.type === 'intersection' && Math.abs(afterOld.pt.x-50)<1 && Math.abs(afterOld.pt.y-50)<1);
    var afterNew = computeSnap(newXY.x, newXY.y);
    var newFound = !!afterNew && afterNew.type === 'intersection' && Math.abs(afterNew.pt.x-65)<1e-6 && Math.abs(afterNew.pt.y-50)<1e-6;

    return {
        pass: sawOldBefore && enteredVertEdit && moved && clearedAfter && oldGone && newFound,
        sawOldBefore, enteredVertEdit, moved, clearedAfter, oldGone, newFound,
        afterOldType: afterOld ? afterOld.type : null, afterOldPt: afterOld ? afterOld.pt : null,
        afterNewType: afterNew ? afterNew.type : null, afterNewPt: afterNew ? afterNew.pt : null
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
        print("SNAP-2026-07-04 slice 2 snap-ray checks:")

        pg.evaluate(JS_PRELUDE)

        checks = [
            ("rayCrossSegment", JS_CHECK_A),
            ("rayEndpointProjects", JS_CHECK_B),
            ("rayNullFallsBack", JS_CHECK_C),
            ("unlockedUnchanged", JS_CHECK_D),
            ("clickEqualsPreview", JS_CHECK_E),
            ("mouseupInvalidates", JS_CHECK_F),
        ]
        for name, script in checks:
            try:
                result = pg.evaluate(script)
                ok = result.get("pass") is True
                print(f"  {name:20s} -> {'PASS' if ok else 'FAIL'}  {result}")
                if not ok:
                    failures.append(f"'{name}' failed: {result}")
            except Exception as ex:
                print(f"  {name:20s} -> EXCEPTION: {ex}")
                failures.append(f"'{name}' threw: {ex}")

        try:
            pg.evaluate(JS_TEARDOWN)
        except Exception:
            pass

        pg.close()
        b.close()

    for e in page_errors:
        print("  JS ERROR:", e)

    server.should_exit = True
    time.sleep(0.4)

    if failures:
        for f in failures:
            print("FAIL:", f)
        print("LITE_SNAP_RAY_FAIL")
        sys.exit(1)
    else:
        print("LITE_SNAP_RAY_OK")


if __name__ == "__main__":
    main()
