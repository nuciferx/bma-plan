#!/usr/bin/env python3
"""
BMA-Plan Lite — measurement-parity / anti-drift test (INV-2026-05-21-001 / LITE-0).

Approach A (vendored standalone) keeps lite's measurement math as a BYTE-IDENTICAL
copy of proto's. This test is the enforcement mechanism. It:

  1. Extracts the vendored functions from BOTH proto/ui.html and
     lite/static/js/measure-engine.js by name.
  2. Asserts each FORBIDDEN-surface function's source line is identical
     (after whitespace strip) between the two files  -> catches a silent edit.
  3. Builds a tiny Node harness for EACH side (stubbed host globals), runs the
     pinned fixtures, and asserts the numeric output is identical -> catches a
     behavioural drift even if the source somehow differs.

Run:  python lite/tests/test_measure_parity.py
Requires: Node.js on PATH. Exits 0 + prints MEASURE_PARITY_OK on success.

Version-sync policy: this test MUST pass before any proto commit that touches the
9 vendored functions. On failure, re-sync lite/static/js/measure-engine.js from
proto/ui.html and re-run.
"""
import json
import os
import re
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROTO_UI = os.path.join(ROOT, "proto", "ui.html")
LITE_ENGINE = os.path.join(ROOT, "lite", "static", "js", "measure-engine.js")
FIXTURES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures", "measure_parity_v1.json")

# Functions that are vendored and MUST match byte-for-byte (the forbidden surfaces
# + their pure helpers). objectAreaM2Lite is intentionally lite-only and excluded.
VENDORED_FUNCS = [
    "segIntersect", "_flattenCubicSeg", "flattenPathToPoints", "polySelfIntersects",
    "origSize", "pdfToC", "cToPdf", "polyAreaM2", "polyMetrics", "pathAreaM2",
]
VENDORED_CONSTS = ["RS", "_PATH_FLATTEN_TOL"]


def extract_func(src, name):
    """Functions are each on their own line; return the stripped line."""
    for line in src.splitlines():
        s = line.strip()
        if s.startswith("function " + name + "("):
            return s
    return None


def extract_const(src, name):
    """Consts may be mid-line (e.g. `...=null;const RS=1.5;`); regex the declaration."""
    m = re.search(r"const\s+" + re.escape(name) + r"\s*=\s*[^;]*;", src)
    return m.group(0).strip() if m else None


def collect(path, funcs, consts):
    src = open(path, encoding="utf-8").read()
    out = {}
    for n in funcs:
        ln = extract_func(src, n)
        if ln is None:
            sys.exit(f"FAIL: could not find function `{n}` in {path}")
        out[n] = ln
    for n in consts:
        ln = extract_const(src, n)
        if ln is None:
            sys.exit(f"FAIL: could not find const `{n}` in {path}")
        out[n] = ln
    return out


def build_harness(decls_in_order, fixtures):
    """decls_in_order: list of source lines (consts first, then functions)."""
    stub = """
let PPM=20, ROT=0;
let curPage=1;
let pageData=null;
let canvas={width:1500,height:1200};
function getRot(pg){return ROT;}
function getScaleForPage(pg){return {pts_per_m:PPM};}
"""
    body = "\n".join(decls_in_order)
    runner = """
const FIX=""" + json.dumps(fixtures) + """;
const R={};
R.poly=FIX.polys.map(f=>{PPM=f.ppm;curPage=1;return {area:polyAreaM2(f.pts),metrics:polyMetrics({pts:f.pts}).area,self:polySelfIntersects(f.pts)};});
R.path=FIX.paths.map(f=>{PPM=f.ppm;curPage=1;return {area:pathAreaM2({segments:f.segments}),npts:flattenPathToPoints({segments:f.segments}).length};});
R.coord=FIX.coords.map(f=>{ROT=f.rot;pageData={size:{orig_w_pt:f.W,orig_h_pt:f.H}};const c=pdfToC(f.px,f.py);const b=cToPdf(c.x,c.y);return {c,roundtrip:b};});
console.log(JSON.stringify(R));
"""
    return stub + "\n" + body + "\n" + runner


def run_node(js):
    fd, p = tempfile.mkstemp(suffix=".js")
    os.close(fd)
    open(p, "w", encoding="utf-8").write(js)
    try:
        r = subprocess.run(["node", p], capture_output=True, text=True)
        if r.returncode != 0:
            sys.exit("FAIL: node error\n" + r.stderr)
        return json.loads(r.stdout)
    finally:
        os.unlink(p)


def main():
    if not os.path.exists(PROTO_UI):
        sys.exit("FAIL: proto/ui.html not found at " + PROTO_UI)
    fixtures = json.load(open(FIXTURES, encoding="utf-8"))

    proto = collect(PROTO_UI, VENDORED_FUNCS, VENDORED_CONSTS)
    lite = collect(LITE_ENGINE, VENDORED_FUNCS, VENDORED_CONSTS)

    # (1) byte-identical source check
    mismatches = [n for n in VENDORED_FUNCS + VENDORED_CONSTS if proto[n] != lite[n]]
    if mismatches:
        print("FAIL: vendored source DRIFT in:", ", ".join(mismatches))
        for n in mismatches:
            print(f"  proto: {proto[n]}")
            print(f"  lite : {lite[n]}")
        sys.exit(1)

    # (2) numeric parity check (independently extracted from each file)
    order = VENDORED_CONSTS + VENDORED_FUNCS  # consts before fns
    proto_out = run_node(build_harness([proto[n] for n in order], fixtures))
    lite_out = run_node(build_harness([lite[n] for n in order], fixtures))
    if proto_out != lite_out:
        print("FAIL: numeric parity drift")
        print("  proto:", json.dumps(proto_out))
        print("  lite :", json.dumps(lite_out))
        sys.exit(1)

    # sanity: a known value (unit square 100x100 pt @ 20 pts/m = 25 m^2)
    sq = lite_out["poly"][0]["area"]
    assert abs(sq - 25.0) < 1e-9, f"expected 25.0 m^2, got {sq}"

    print(f"checked {len(VENDORED_FUNCS)} fns + {len(VENDORED_CONSTS)} consts; "
          f"{len(fixtures['polys'])} polys, {len(fixtures['paths'])} paths, "
          f"{len(fixtures['coords'])} coords")
    print("MEASURE_PARITY_OK")


if __name__ == "__main__":
    main()
