#!/usr/bin/env python3
"""
BMA-Plan Lite — property-based tests for vendored measure-engine.js (EVOLT-1).

Runs via Node.js (same pattern as test_measure_parity.py).  Loads the vendored
measure-engine.js into a Node context and asserts 6 mathematical properties
over ≥500 deterministic random cases each.

All randomness is seeded by a fixed constant (SEED=42 via an LCG PRNG)
so runs are reproducible and cannot be gamed with Date.now().

Properties tested:
  P1 non-negativity       polyAreaM2(randomClosedPoly) >= 0
  P2 vertex-order-reverse reversing the point list → identical area (within 1e-9)
  P3 cyclic-shift         cyclically rotating the vertex list → identical area
  P4 scale-linearity      area(ppm=k) vs area(ppm=2k) → ratio exactly 4 (k^2 law)
  P5 translation-invariant shift all pts by (dx,dy) → identical area
  P6 degenerate-safety    <3 points / collinear → returns 0 or finite, never NaN/Inf/throw

All 6 should PASS (the math is correct).  If any FAILS that is a real
measure-engine bug — report it loudly.

Also: records the measure-engine.js content SHA-256 so the PBT is pinned
to a known engine version.

Run:  py -3 lite/tests/test_pbt_measure.py
Exits 0 + prints LITE_PBT_MEASURE_OK on all-pass.
Exits 1 + prints LITE_PBT_MEASURE_FAIL: <list> on any failure.

Requires: Node.js on PATH.
"""

import hashlib
import json
import os
import subprocess
import sys
import tempfile

# ---- paths ---------------------------------------------------------------
HERE      = os.path.dirname(os.path.abspath(__file__))
LITE_ROOT = os.path.dirname(HERE)
ENGINE    = os.path.join(LITE_ROOT, "static", "js", "measure-engine.js")


# ---- Node discovery (mirrors test_measure_parity.py) ----------------------
def _find_node():
    import shutil
    node = shutil.which("node")
    if node:
        return node
    for candidate in [
        r"C:\Program Files\nodejs\node.exe",
        r"C:\Program Files (x86)\nodejs\node.exe",
    ]:
        if os.path.isfile(candidate):
            return candidate
    sys.exit("FAIL: node not found on PATH.  Install Node.js to run this test.")


# ---- engine version hash --------------------------------------------------
def _engine_hash(path: str) -> str:
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


# ---- Node harness builder -------------------------------------------------
# We load the engine verbatim; stub the HOST CONTRACT globals it expects.
# N_CASES and SEED are injected by Python via JSON so the JS stays a template.

def _build_node_js(engine_src: str, n_cases: int, seed: int) -> str:
    """Return a complete Node.js script that runs the PBT suite."""
    return r"""
'use strict';

// ---- HOST CONTRACT stubs (required by measure-engine.js) ----------------
// These mirror the stubs in test_measure_parity.py's build_harness().
var PPM = 20;
var ROT = 0;
var curPage = 1;
var pageData = null;
var canvas = { width: 1500, height: 1200 };
function getRot(pg)           { return ROT; }
function getScaleForPage(pg)  { return { pts_per_m: PPM }; }

// ---- inline the engine --------------------------------------------------
""" + engine_src + r"""

// ---- Deterministic LCG PRNG (seed constant) -----------------------------
// LCG parameters (Knuth / glibc): m=2^31, a=1103515245, c=12345
var _lcg_state = """ + str(seed) + r""";
function _rand() {
  _lcg_state = ((_lcg_state * 1103515245 + 12345) >>> 0) % 2147483648;
  return _lcg_state / 2147483648;   // [0, 1)
}
function _randInRange(lo, hi) { return lo + _rand() * (hi - lo); }
function _randInt(lo, hi)     { return Math.floor(_randInRange(lo, hi + 1)); }

// ---- Polygon generators -------------------------------------------------

// Generate a random CLOSED convex polygon with n vertices in [0, size]^2.
// Convex guarantees no self-intersection and a well-defined positive area.
function _randomConvexPoly(n, size) {
  // Use the classical Valtr algorithm for random convex polygons.
  // Step 1: generate two sets of sorted random numbers.
  n = Math.max(3, n);
  var xs = [], ys = [];
  for (var i = 0; i < n; i++) { xs.push(_rand()); ys.push(_rand()); }
  xs.sort(function(a,b){return a-b;}); ys.sort(function(a,b){return a-b;});
  var minX=xs[0], maxX=xs[n-1], minY=ys[0], maxY=ys[n-1];
  var vx=[minX], vy=[minY];
  var wx=[minX], wy=[minY];
  var lastTopX=minX, lastTopY=minY, lastBotX=minX, lastBotY=minY;
  for (var i=1;i<n-1;i++){
    if (_rand()<0.5){vx.push(xs[i]);vy.push(ys[i]);}
    else           {wx.push(xs[i]);wy.push(ys[i]);}
  }
  vx.push(maxX); vy.push(maxY);
  wx.push(maxX); wy.push(maxY);
  // Differences
  var dxV=[],dyV=[],dxW=[],dyW=[];
  for(var i=1;i<vx.length;i++){dxV.push(vx[i]-vx[i-1]);dyV.push(vy[i]-vy[i-1]);}
  for(var i=1;i<wx.length;i++){dxW.push(wx[i]-wx[i-1]);dyW.push(wy[i]-wy[i-1]);}
  // Shuffle and alternate signs
  function shuffle(a){for(var i=a.length-1;i>0;i--){var j=_randInt(0,i);var t=a[i];a[i]=a[j];a[j]=t;}}
  shuffle(dxV); shuffle(dyV); shuffle(dxW); shuffle(dyW);
  // Mix into x/y vectors
  var vecs=[];
  for(var i=0;i<dxV.length;i++) vecs.push({x:dxV[i],y:-dyV[i]});
  for(var i=0;i<dxW.length;i++) vecs.push({x:-dxW[i],y:dyW[i]});
  // Sort by angle
  vecs.sort(function(a,b){return Math.atan2(a.y,a.x)-Math.atan2(b.y,b.x);});
  // Build polygon
  var pts=[{x:0,y:0}];
  for(var i=0;i<vecs.length;i++){
    pts.push({x:pts[pts.length-1].x+vecs[i].x*size,y:pts[pts.length-1].y+vecs[i].y*size});
  }
  // Translate to positive quadrant
  var minPx=Math.min.apply(0,pts.map(function(p){return p.x;}));
  var minPy=Math.min.apply(0,pts.map(function(p){return p.y;}));
  return pts.map(function(p){return{x:p.x-minPx,y:p.y-minPy};});
}

// Simple random polygon (may self-intersect, but polyAreaM2 must still return >=0)
function _randomSimplePoly(n, size) {
  var pts = [];
  for (var i = 0; i < n; i++) {
    pts.push({x: _randInRange(0, size), y: _randInRange(0, size)});
  }
  return pts;
}

// ---- Utilities ----------------------------------------------------------
function _cyclicShift(pts, k) {
  k = ((k % pts.length) + pts.length) % pts.length;
  return pts.slice(k).concat(pts.slice(0, k));
}
function _reverse(pts) { return pts.slice().reverse(); }
function _translate(pts, dx, dy) {
  return pts.map(function(p){return{x:p.x+dx,y:p.y+dy};});
}
function _isFinite_(v) { return v !== null && isFinite(v) && !isNaN(v); }
function _areEq(a, b, tol) {
  if (a === null && b === null) return true;
  if (a === null || b === null) return Math.abs((a||0)-(b||0)) < tol;
  return Math.abs(a - b) <= tol;
}

var N   = """ + str(n_cases) + r""";
var TOL = 1e-9;
var results = {};
var failCounts = {};
var failDetails = {};

// =========================================================================
// P1 — non-negativity: area >= 0 for any closed polygon
// =========================================================================
(function testP1() {
  var name = 'P1-non-negativity';
  var fails = 0;
  var firstFail = null;
  for (var i = 0; i < N; i++) {
    var n   = _randInt(3, 12);
    var pts = _randomSimplePoly(n, 200);
    var ppm = _randInRange(5, 50);
    PPM = ppm; curPage = 1;
    var area;
    try { area = polyAreaM2(pts); } catch(e) { area = 'throw:' + e.message; }
    var ok = (area === null) || (typeof area === 'number' && area >= -1e-12 && !isNaN(area));
    if (!ok && !firstFail) firstFail = {i, pts: pts.slice(0,4), ppm, area};
    if (!ok) fails++;
  }
  results[name] = {pass: fails === 0, failCount: fails, firstFail};
})();

// =========================================================================
// P2 — vertex-order independence: reverse → identical area
// =========================================================================
(function testP2() {
  var name = 'P2-vertex-order-reverse';
  var fails = 0;
  var firstFail = null;
  for (var i = 0; i < N; i++) {
    var n   = _randInt(3, 12);
    var pts = _randomConvexPoly(n, 200);
    var ppm = _randInRange(5, 50);
    PPM = ppm; curPage = 1;
    var a1, a2;
    try { a1 = polyAreaM2(pts); } catch(e) { a1 = null; }
    try { a2 = polyAreaM2(_reverse(pts)); } catch(e) { a2 = null; }
    var ok = _areEq(a1, a2, Math.max(TOL, Math.abs(a1||0) * 1e-9));
    if (!ok && !firstFail) firstFail = {i, n, ppm, a1, a2, diff: Math.abs((a1||0)-(a2||0))};
    if (!ok) fails++;
  }
  results[name] = {pass: fails === 0, failCount: fails, firstFail};
})();

// =========================================================================
// P3 — cyclic-shift independence: rotate vertex list → identical area
// =========================================================================
(function testP3() {
  var name = 'P3-cyclic-shift';
  var fails = 0;
  var firstFail = null;
  for (var i = 0; i < N; i++) {
    var n   = _randInt(3, 12);
    var pts = _randomConvexPoly(n, 200);
    var ppm = _randInRange(5, 50);
    var k   = _randInt(1, n - 1);
    PPM = ppm; curPage = 1;
    var a1, a2;
    try { a1 = polyAreaM2(pts); } catch(e) { a1 = null; }
    try { a2 = polyAreaM2(_cyclicShift(pts, k)); } catch(e) { a2 = null; }
    var ok = _areEq(a1, a2, Math.max(TOL, Math.abs(a1||0) * 1e-9));
    if (!ok && !firstFail) firstFail = {i, n, k, ppm, a1, a2, diff: Math.abs((a1||0)-(a2||0))};
    if (!ok) fails++;
  }
  results[name] = {pass: fails === 0, failCount: fails, firstFail};
})();

// =========================================================================
// P4 — scale linearity: area(ppm=k) vs area(ppm=2k) → ratio = 4
// The shoelace returns pt-area / ppm^2, so doubling ppm → area / 4.
// =========================================================================
(function testP4() {
  var name = 'P4-scale-linearity';
  var fails = 0;
  var firstFail = null;
  for (var i = 0; i < N; i++) {
    var n   = _randInt(3, 12);
    var pts = _randomConvexPoly(n, 200);
    var ppm = _randInRange(5, 25);  // k in [5,25]; 2k in [10,50] — both reasonable
    curPage = 1;
    var aK, a2K;
    try { PPM = ppm;     aK  = polyAreaM2(pts); } catch(e) { aK  = null; }
    try { PPM = ppm * 2; a2K = polyAreaM2(pts); } catch(e) { a2K = null; }
    // Expected: aK / a2K === 4  (area at ppm=k is 4x the area at ppm=2k)
    var ok;
    if (aK === null || a2K === null) {
      ok = true;  // null propagation is acceptable
    } else if (Math.abs(a2K) < 1e-15) {
      ok = Math.abs(aK) < 1e-12;   // both effectively zero
    } else {
      var ratio = aK / a2K;
      ok = Math.abs(ratio - 4.0) < 1e-6;
    }
    if (!ok && !firstFail) {
      firstFail = {i, n, ppm, aK, a2K, ratio: (aK !== null && a2K !== null) ? aK/a2K : null};
    }
    if (!ok) fails++;
  }
  results[name] = {pass: fails === 0, failCount: fails, firstFail};
})();

// =========================================================================
// P5 — translation invariance: shift all pts by (dx,dy) → identical area
// =========================================================================
(function testP5() {
  var name = 'P5-translation-invariant';
  var fails = 0;
  var firstFail = null;
  for (var i = 0; i < N; i++) {
    var n   = _randInt(3, 12);
    var pts = _randomConvexPoly(n, 200);
    var ppm = _randInRange(5, 50);
    var dx  = _randInRange(-1e4, 1e4);
    var dy  = _randInRange(-1e4, 1e4);
    PPM = ppm; curPage = 1;
    var a1, a2;
    try { a1 = polyAreaM2(pts); } catch(e) { a1 = null; }
    try { a2 = polyAreaM2(_translate(pts, dx, dy)); } catch(e) { a2 = null; }
    var ok = _areEq(a1, a2, Math.max(TOL, Math.abs(a1||0) * 1e-9));
    if (!ok && !firstFail) firstFail = {i, n, ppm, dx, dy, a1, a2, diff: Math.abs((a1||0)-(a2||0))};
    if (!ok) fails++;
  }
  results[name] = {pass: fails === 0, failCount: fails, firstFail};
})();

// =========================================================================
// P6 — degenerate safety: <3 pts / all-collinear → 0 or finite, never NaN/Inf/throw
// =========================================================================
(function testP6() {
  var name = 'P6-degenerate-safety';
  var fails = 0;
  var firstFail = null;
  // Sub-cases: 0-pt, 1-pt, 2-pt, collinear-3, collinear-4, collinear-10, duplicate-pts
  var cases = [];
  // Empty
  cases.push({label: '0-pts',    pts: []});
  cases.push({label: '1-pt',     pts: [{x:5,y:5}]});
  cases.push({label: '2-pts',    pts: [{x:0,y:0},{x:100,y:0}]});
  // Collinear
  cases.push({label: 'collinear-3', pts: [{x:0,y:0},{x:50,y:0},{x:100,y:0}]});
  cases.push({label: 'collinear-4', pts: [{x:0,y:5},{x:25,y:5},{x:75,y:5},{x:100,y:5}]});
  // Random collinear
  for (var i = 0; i < 10; i++) {
    var ax=_rand()*100, ay=_rand()*100, bx=_rand()*100, by=_rand()*100;
    var pts3=[];
    for(var j=0;j<_randInt(3,8);j++){var t=j/7;pts3.push({x:ax+t*(bx-ax),y:ay+t*(by-ay)});}
    cases.push({label:'rand-collinear-'+i, pts:pts3});
  }
  // Duplicate all-same points
  cases.push({label:'all-same', pts:[{x:50,y:50},{x:50,y:50},{x:50,y:50}]});
  // Additional random < 3 at various PPM
  for (var i = 0; i < N; i++) {
    var n   = _randInt(0, 2);   // 0, 1, or 2 points
    var pts = _randomSimplePoly(n, 200);
    cases.push({label:'rand-lt3-'+i, pts:pts});
  }
  PPM = 20; curPage = 1;
  for (var ci = 0; ci < cases.length; ci++) {
    var c = cases[ci];
    var area, threw = false;
    try { area = polyAreaM2(c.pts); } catch(e) { area = null; threw = true; }
    // polyAreaM2 is allowed to return null or 0 for degenerate cases.
    // It must NOT return NaN, Infinity, or throw.
    var ok = !threw && (area === null || (typeof area === 'number' && _isFinite_(area)));
    if (!ok && !firstFail) firstFail = {label: c.label, pts: c.pts, area, threw};
    if (!ok) fails++;
  }
  results[name] = {pass: fails === 0, failCount: fails, firstFail};
})();

// =========================================================================
// Output
// =========================================================================
var allPass = Object.keys(results).every(function(k){ return results[k].pass; });
var failing  = Object.keys(results).filter(function(k){ return !results[k].pass; });

console.log(JSON.stringify({allPass, failing, results, nCases: """ + str(n_cases) + r"""}));
""".strip()


# ---- Python runner --------------------------------------------------------

def main():
    if not os.path.isfile(ENGINE):
        sys.exit(f"FAIL: measure-engine.js not found at {ENGINE}")

    node = _find_node()

    # Read engine source
    with open(ENGINE, encoding="utf-8") as f:
        engine_src = f.read()

    # Strip the module.exports line (safe; it's at the very end and Node won't
    # error on it either way, but stripping keeps our harness self-contained).
    # The engine's own `if(typeof module!=='undefined'...)` guard handles this
    # gracefully — we don't need to strip it.

    engine_hash = _engine_hash(ENGINE)

    N_CASES = 500
    SEED    = 42

    js = _build_node_js(engine_src, N_CASES, SEED)

    # Write to a temp file and run
    fd, tmp_path = tempfile.mkstemp(suffix=".js")
    os.close(fd)
    try:
        with open(tmp_path, "w", encoding="utf-8") as f:
            f.write(js)
        proc = subprocess.run([node, tmp_path], capture_output=True, text=True, timeout=60)
    except subprocess.TimeoutExpired:
        sys.exit("FAIL: Node PBT timed out after 60 s")
    finally:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass

    if proc.returncode != 0:
        print("FAIL: Node exited non-zero")
        print(proc.stderr[:2000])
        sys.exit(1)

    # Parse output
    try:
        output = json.loads(proc.stdout.strip())
    except json.JSONDecodeError as e:
        print("FAIL: could not parse Node output as JSON")
        print(proc.stdout[:500])
        print(proc.stderr[:500])
        sys.exit(1)

    # Report
    print(f"measure-engine.js SHA-256: {engine_hash}")
    print(f"N={output.get('nCases')} cases per property, seed=SEED={SEED}")
    print()

    all_pass = output.get("allPass", False)
    failing  = output.get("failing", [])
    results  = output.get("results", {})

    props = [
        ("P1-non-negativity",       "P1 area >= 0 for any closed polygon"),
        ("P2-vertex-order-reverse", "P2 reverse vertex list → identical area"),
        ("P3-cyclic-shift",         "P3 cyclic vertex rotation → identical area"),
        ("P4-scale-linearity",      "P4 area(ppm=k) / area(ppm=2k) = 4"),
        ("P5-translation-invariant","P5 translate all pts → identical area"),
        ("P6-degenerate-safety",    "P6 degenerate input → 0 or finite, no throw"),
    ]

    for key, desc in props:
        r = results.get(key, {})
        ok = r.get("pass", False)
        fc = r.get("failCount", "?")
        status = "PASS" if ok else f"FAIL ({fc} failing cases)"
        print(f"  {status:<20} {desc}")
        if not ok:
            ff = r.get("firstFail")
            if ff:
                print(f"    first fail: {json.dumps(ff, default=str)[:300]}")

    print()
    if failing:
        # A failing property is a REAL measure-engine bug — report loudly.
        print(f"REAL MEASURE-ENGINE BUG DETECTED in: {', '.join(failing)}")
        print("These properties MUST hold.  Investigate measure-engine.js.")
        print(f"LITE_PBT_MEASURE_FAIL: {', '.join(failing)}")
        sys.exit(1)
    else:
        print(f"All 6 properties hold over {N_CASES} cases (seed={SEED}).")
        print(f"Engine pinned to SHA-256: {engine_hash}")
        print("LITE_PBT_MEASURE_OK")
        sys.exit(0)


if __name__ == "__main__":
    main()
