"""
SNAP-2026-07-04 slice 1/3 — test_snap_engine.py

Verifies the extracted static/js/snap-engine.js keeps computeSnap()'s output
byte-identical to the pre-extraction always-rebuild algorithm, while the new
per-page/per-view static-intersection cache (_segCache) actually avoids
redoing the O(segCount^2) segIntersect double loop on every call.

Five checks (mirrors the SNAP-2026-07-04 spec's acceptance list):
  (a) identicalOutput        — 12 probe cursor positions, cached computeSnap()
                                vs an independent reference re-implementation
                                (defined fresh in this test's JS, NOT calling
                                the cached fn twice) built on a 6-object fixture
                                with genuine crossing segments.
  (b) cacheHit                — a second computeSnap() call with an unchanged
                                page/view/object fingerprint does NOT redo the
                                static-static intersection rebuild
                                (_segCache.rebuildCount unchanged, hitCount up).
  (c) invalidateOnAdd          — adding an object busts the fingerprint; the
                                very next computeSnap() sees its endpoint AND
                                a rebuild happens.
  (d) invalidateOnUndo          — undo() (which runs _afterHistory() ->
                                snapInvalidate()) removes the added object's
                                endpoint from what computeSnap() reports.
  (e) draftStillSnaps           — a draft segment (state.draft, in-progress
                                measurement) crossing static geometry is found
                                as an "intersection" snap on the very next
                                call, proving the static-cache short-circuit
                                does not swallow fresh draft-vs-static pairs.

Emits LITE_SNAP_ENGINE_OK on success.

    py -3 lite/tests/test_snap_engine.py
"""
import socket, threading, time, sys, io
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

LITE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LITE))
import uvicorn
from playwright.sync_api import sync_playwright


def _free_port(start=8560):
    for p in range(start, start + 60):
        with socket.socket() as s:
            if s.connect_ex(("127.0.0.1", p)) != 0:
                return p
    raise RuntimeError("no free port")


# ---------------------------------------------------------------------------
# Shared JS: fixture builder + independent reference computeSnap.
# Reference is a verbatim copy of the ORIGINAL (pre-cache) computeSnap body —
# always rebuilds everything from scratch, never touches _segCache — so
# comparing it against the real (cached) computeSnap() genuinely proves the
# cache changed nothing observable.
# ---------------------------------------------------------------------------
JS_SETUP = """
() => {
    var pg = 77;
    PS[pg] = { objects: [], scale: { pts_per_m: 1 }, annotations: [] };
    var A = { kind:'poly', pts:[{x:0,y:0},{x:240,y:0},{x:240,y:160},{x:0,y:160}], counting:false, catId:'gfa' };
    var B = { kind:'line', pts:[{x:-30,y:55},{x:270,y:55}], counting:false, catId:'gfa' };
    var C = { kind:'line', pts:[{x:77,y:-30},{x:77,y:190}], counting:false, catId:'gfa' };
    var D = { kind:'line', pts:[{x:300,y:0},{x:300,y:40},{x:340,y:40},{x:340,y:90}], counting:false, catId:'gfa' };
    var E = { kind:'poly', pts:[{x:600,y:600}], counting:true, catId:'count' };
    var F = { kind:'poly', pts:[{x:400,y:300},{x:460,y:300},{x:430,y:350}], counting:false, catId:'gfa' };
    PS[pg].objects = [A, B, C, D, E, F];

    window.__prevPage = curPage; curPage = pg;
    window.__prevImg  = curImg;  if (!curImg) curImg = { width: 800, height: 800 };
    window.__prevV    = { k: V.k, ox: V.ox, oy: V.oy, rot: V.rot };
    V.k = 1; V.ox = 0; V.oy = 0; V.rot = 0;

    state.snapOn = true;
    state.snapTypes = { endpoint: true, midpoint: true, center: true, intersection: true };
    state.draft = null; state.tool = 'poly';

    // clean undo/redo slate so later steps are unambiguous
    undoStack.length = 0; redoStack.length = 0;

    // reference impl: original always-rebuild computeSnap, copied verbatim
    // (renamed) — never touches _segCache.
    window.__refComputeSnap = function (sx, sy) {
        if (!PageRenderer.ready() || !state.snapOn) return null;
        var ST = state.snapTypes || { endpoint: true, midpoint: true, center: true, intersection: true };
        var objs = PSpage().objects.concat(state.draft ? [{ pts: state.draft, counting: false }] : []);
        var best = null, bd = SNAP_PX;
        if (ST.endpoint) {
            objs.forEach(function (o) {
                if (o.counting || !o.pts) return;
                o.pts.forEach(function (p) {
                    var s = ptToScreen(p), d = Math.hypot(s.x - sx, s.y - sy);
                    if (d < bd) { bd = d; best = { pt: p, screen: s, type: 'endpoint' }; }
                });
            });
            if (best) return best;
        }
        var segs = pageSegs();
        if (ST.intersection) {
            for (var i = 0; i < segs.length; i++) for (var j = i + 1; j < segs.length; j++) {
                var a0 = ptToScreen(segs[i][0]), a1 = ptToScreen(segs[i][1]), b0 = ptToScreen(segs[j][0]), b1 = ptToScreen(segs[j][1]);
                var ix = segIntersect(a0.x, a0.y, a1.x, a1.y, b0.x, b0.y, b1.x, b1.y);
                if (ix) { var d = Math.hypot(ix.x - sx, ix.y - sy); if (d < bd) { bd = d; best = { pt: screenToPt(ix.x, ix.y), screen: ix, type: 'intersection' }; } }
            }
            if (best) return best;
        }
        if (ST.midpoint) {
            segs.forEach(function (seg) {
                var m = { x: (seg[0].x + seg[1].x) / 2, y: (seg[0].y + seg[1].y) / 2 }, s = ptToScreen(m), d = Math.hypot(s.x - sx, s.y - sy);
                if (d < bd) { bd = d; best = { pt: m, screen: s, type: 'midpoint' }; }
            });
            if (best) return best;
        }
        if (ST.center) {
            PSpage().objects.forEach(function (o) {
                if (o.counting || o.kind !== 'poly' || !effVisible(o.catId, _isHidden)) return;
                var c = centroid(o.pts), s = ptToScreen(c), d = Math.hypot(s.x - sx, s.y - sy);
                if (d < bd) { bd = d; best = { pt: c, screen: s, type: 'center' }; }
            });
            if (best) return best;
        }
        if (state.draft && state.draft.length) {
            var lp = state.draft[state.draft.length - 1];
            segs.forEach(function (seg) {
                var foot = footPerp(lp, seg[0], seg[1]); var s = ptToScreen(foot), d = Math.hypot(s.x - sx, s.y - sy);
                if (d < bd) { bd = d; best = { pt: foot, screen: s, type: 'perp' }; }
            });
        }
        if (best) return best;
        segs.forEach(function (seg) {
            var s0 = ptToScreen(seg[0]), s1 = ptToScreen(seg[1]), np = nearOnSegS(sx, sy, s0, s1), d = Math.hypot(np.x - sx, np.y - sy);
            if (d < bd) { bd = d; best = { pt: screenToPt(np.x, np.y), screen: np, type: 'nearest' }; }
        });
        return best;
    };

    return { ok: true };
}
"""

JS_TEARDOWN = """
() => {
    curPage = window.__prevPage; curImg = window.__prevImg;
    V.k = window.__prevV.k; V.ox = window.__prevV.ox; V.oy = window.__prevV.oy; V.rot = window.__prevV.rot;
    state.draft = null;
    return { ok: true };
}
"""

# 12 probe positions (PDF-pt space) -> expected snap type + expected snapped pt.
# Offsets are 0.5-2 pt away from the target feature; every neighbouring
# feature in the fixture is tens of units away, so there is no ambiguity
# within SNAP_PX (11 screen px == ~7.33 pt at the default 1.5x RS scale).
JS_CHECK_A = """
() => {
    var probes = [
        [1, 1,             'endpoint',     0, 0],
        [239, 159,          'endpoint',     240, 160],
        [77.5, 54.5,        'intersection', 77, 55],
        [1, 55.5,           'intersection', 0, 55],
        [239, 55.5,         'intersection', 240, 55],
        [77.5, 1,           'intersection', 77, 0],
        [77.5, 159,         'intersection', 77, 160],
        [120, 1.2,          'midpoint',     120, 0],
        [1.2, 80,           'midpoint',     0, 80],
        [430.5, 317,        'center',       430, 316.6666666666667],
        [320, 41,           'midpoint',     320, 40],
        [302, 10,           'nearest',      300, 10]
    ];
    var rows = [];
    var allOk = true;
    probes.forEach(function (pr) {
        var pdfx = pr[0], pdfy = pr[1], expType = pr[2], expx = pr[3], expy = pr[4];
        var s = ptToScreen({ x: pdfx, y: pdfy });
        var cached = computeSnap(s.x, s.y);
        var ref = window.__refComputeSnap(s.x, s.y);
        var cachedOk = !!cached && cached.type === expType && Math.abs(cached.pt.x - expx) < 1e-6 && Math.abs(cached.pt.y - expy) < 1e-6;
        var matchesRef = !!cached && !!ref && cached.type === ref.type && Math.abs(cached.pt.x - ref.pt.x) < 1e-6 && Math.abs(cached.pt.y - ref.pt.y) < 1e-6;
        var ok = cachedOk && matchesRef;
        if (!ok) allOk = false;
        rows.push({ probe: [pdfx, pdfy], expType, cachedType: cached ? cached.type : null, refType: ref ? ref.type : null, cachedOk, matchesRef });
    });
    return { pass: allOk, rows };
}
"""

JS_CHECK_B = """
() => {
    snapInvalidate();
    var s = ptToScreen({ x: 77.5, y: 54.5 });  // lands on the intersection branch
    var before = _segCache.rebuildCount;
    var r1 = computeSnap(s.x, s.y);
    var afterFirst = _segCache.rebuildCount;
    var hitBefore = _segCache.hitCount;
    var r2 = computeSnap(s.x, s.y);   // identical fp -> must NOT rebuild again
    var afterSecond = _segCache.rebuildCount;
    var hitAfter = _segCache.hitCount;
    return {
        pass: (afterFirst === before + 1) && (afterSecond === afterFirst) && (hitAfter > hitBefore),
        before, afterFirst, afterSecond, hitBefore, hitAfter,
        r1Type: r1 ? r1.type : null, r2Type: r2 ? r2.type : null
    };
}
"""

JS_CHECK_C = """
() => {
    pushUndo();   // snapshot BEFORE adding G — undo() in check (d) rolls back to here
    var G = { kind: 'line', pts: [{ x: 700, y: 700 }, { x: 750, y: 750 }], counting: false, catId: 'gfa' };
    PS[77].objects.push(G);
    var rebuildBefore = _segCache.rebuildCount;
    var s = ptToScreen({ x: 701, y: 701 });
    var res = computeSnap(s.x, s.y);
    var sawEndpoint = !!res && res.type === 'endpoint' && Math.abs(res.pt.x - 700) < 1e-6 && Math.abs(res.pt.y - 700) < 1e-6;
    // endpoint check returns before the intersection branch is even reached, so
    // rebuildCount alone can't prove invalidation here — probe the intersection
    // branch too (away from any endpoint) to confirm the fingerprint changed.
    var s2 = ptToScreen({ x: 77.5, y: 54.5 });
    computeSnap(s2.x, s2.y);
    var rebuildAfter = _segCache.rebuildCount;
    return { pass: sawEndpoint && (rebuildAfter === rebuildBefore + 1), sawEndpoint, rebuildBefore, rebuildAfter };
}
"""

JS_CHECK_D = """
() => {
    undo();   // -> _afterHistory() -> snapInvalidate(); restores PS[77] to pre-G snapshot
    var stillHasG = PS[77].objects.some(function (o) { return o.pts && o.pts.length && o.pts[0].x === 700 && o.pts[0].y === 700; });
    var s = ptToScreen({ x: 701, y: 701 });
    var res = computeSnap(s.x, s.y);
    var goneAsEndpoint = !res || res.type !== 'endpoint' || Math.abs(res.pt.x - 700) > 1e-6;
    return { pass: !stillHasG && goneAsEndpoint, stillHasG, resType: res ? res.type : null };
}
"""

JS_CHECK_E = """
() => {
    // draft: horizontal line y=120 crossing rect edges e1/e3 AND the vertical
    // static line C (x=77) — none of these 3 crossings exist in the static
    // cache (they only exist because of the in-progress draft).
    state.tool = 'dist';
    state.draft = [{ x: -10, y: 120 }, { x: 250, y: 120 }];
    var s = ptToScreen({ x: 77.2, y: 120.3 });
    var res = computeSnap(s.x, s.y);
    var ok = !!res && res.type === 'intersection' && Math.abs(res.pt.x - 77) < 1e-6 && Math.abs(res.pt.y - 120) < 1e-6;
    state.draft = null;
    return { pass: ok, resType: res ? res.type : null, pt: res ? res.pt : null };
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
        print("SNAP-2026-07-04 snap-engine checks:")

        pg.evaluate(JS_SETUP)

        checks = [
            ("identicalOutput", JS_CHECK_A),
            ("cacheHit", JS_CHECK_B),
            ("invalidateOnAdd", JS_CHECK_C),
            ("invalidateOnUndo", JS_CHECK_D),
            ("draftStillSnaps", JS_CHECK_E),
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
        print("LITE_SNAP_ENGINE_FAIL")
        sys.exit(1)
    else:
        print("LITE_SNAP_ENGINE_OK")


if __name__ == "__main__":
    main()
