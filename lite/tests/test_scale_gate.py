"""
SCALE-GATE-2026-07-04: per-page scale gate + report null-area truth.

Extends the JIT tag gate (lite/static/js/tag-jit.js, INV-2026-07-04-002
slice 4/4) with a SECOND check: after the tag gate passes, a measure tool
(poly/dist/path/ref) still refuses to arm on a TAGGED-but-UNSCALED page,
showing a second banner variant with one action ("ตั้ง scale เลย") that
switches straight to the scale tool; once the scale is actually committed
(#cal-ok / #su-ok), the originally-requested tool is re-armed exactly
once. count is exempt (no scale needed to count items). scale itself is
never gated (it's the remedy).

Also closes the "report shows 0.00 for unscaled pages" finding: a null
area (buildReportPayload, export-annotate.js) now stays null end-to-end
instead of being coerced to 0 — the editable report grid (report-edit.js)
renders "—" with a tooltip for that row, and the group subtotal / page net
(the independent ground truth) simply excludes it from the sum.

5 sub-checks:
  taggedUnscaledBlocksAndBanner   setTool('poly') on a tagged-but-unscaled
                                  page -> refused + scale-banner (with the
                                  '#jit-set-scale-btn' action) shown
  bannerTapArmsScaleTool          tapping "ตั้ง scale เลย" -> scale tool
                                  arms immediately, banner hides
  scaleCommitRearmsPendingOnce    completing #cal-ok's calibration flow ->
                                  the ORIGINAL tool the user wanted (not
                                  'scale', not the pre-existing hardcoded
                                  'poly') re-arms via setTool EXACTLY once
  countExemptFromScaleGate        count tool arms directly on a tagged-but-
                                  unscaled page (only poly/dist/path/ref
                                  are scale-gated)
  reportNullAreaEndToEnd          a REAL PS object drawn on an unscaled
                                  page, run through the REAL
                                  buildReportPayload() (not a mock) ->
                                  row.area is null, the group subtotal /
                                  page net exclude it (Python-computed
                                  independent ground truth: both == 0.00);
                                  fed into the actual /report page, the
                                  grid cell renders the literal "—" with
                                  title "ยังไม่ตั้งมาตราส่วน"

Emits LITE_SCALE_GATE_OK on success.

    py -3 lite/tests/test_scale_gate.py
"""
import json
import socket
import sys
import threading
import time
from pathlib import Path

LITE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LITE))
import uvicorn
from playwright.sync_api import sync_playwright


def _free_port(start=8660):
    for p in range(start, start + 60):
        with socket.socket() as s:
            if s.connect_ex(("127.0.0.1", p)) != 0:
                return p
    raise RuntimeError("no free port")


SETUP_GLOBALS = r"""
async () => {
  await new Promise(r => setTimeout(r, 400));  // let all dynamic scripts (incl. tag-jit.js) load
  return { done: true, wrapInstalled: window.__jitWrapped === true };
}
"""

# ---------------------------------------------------------------------------
# Sub-check 1 — taggedUnscaledBlocksAndBanner
# ---------------------------------------------------------------------------
CHECK_UNSCALED_BLOCKS = r"""
() => {
  caseId = 'test'; pageCount = 5; pageTags = { 3: 'site' }; excluded = {};
  curPage = 3; state.tool = 'select';
  PS = { 3: { objects: [], scale: null, annotations: [] } };
  _jitHideBanner();

  var before = state.tool;
  setTool('poly');
  var after = state.tool;
  var toolBlocked = (after === before) && (after !== 'poly');

  var banner = document.getElementById('jit-banner');
  var bannerShown = !!banner && banner.style.display !== 'none';
  var hasScaleBtn = banner ? !!banner.querySelector('#jit-set-scale-btn') : false;

  return {
    toolBlocked, bannerShown, hasScaleBtn,
    pass: toolBlocked && bannerShown && hasScaleBtn
  };
}
"""

# ---------------------------------------------------------------------------
# Sub-check 2 — bannerTapArmsScaleTool
# ---------------------------------------------------------------------------
CHECK_BANNER_TAP_ARMS_SCALE = r"""
() => {
  caseId = 'test'; pageCount = 5; pageTags = { 3: 'site' }; excluded = {};
  curPage = 3; state.tool = 'select';
  PS = { 3: { objects: [], scale: null, annotations: [] } };
  _jitHideBanner();

  setTool('dist');  // blocked by scale gate -> scale banner, pending tool = 'dist'
  var banner = document.getElementById('jit-banner');
  var btn = banner ? banner.querySelector('#jit-set-scale-btn') : null;
  var btnFound = !!btn;
  if (btn) btn.click();

  var scaleArmed = state.tool === 'scale';
  var bannerHidden = !banner || banner.style.display === 'none';

  return { btnFound, scaleArmed, bannerHidden, pass: btnFound && scaleArmed && bannerHidden };
}
"""

# ---------------------------------------------------------------------------
# Sub-check 3 — scaleCommitRearmsPendingOnce
# ---------------------------------------------------------------------------
CHECK_SCALE_COMMIT_REARM = r"""
() => {
  caseId = 'test'; pageCount = 5; pageTags = { 3: 'site' }; excluded = {};
  curPage = 3; state.tool = 'select';
  PS = { 3: { objects: [], scale: null, annotations: [] } };
  _jitHideBanner();

  setTool('dist');                     // blocked -> pending tool = 'dist'
  var banner = document.getElementById('jit-banner');
  var scaleBtn = banner ? banner.querySelector('#jit-set-scale-btn') : null;
  if (scaleBtn) scaleBtn.click();       // arms 'scale' tool
  var armedScale = state.tool === 'scale';

  // Simulate completing the calibration modal (bypasses actual canvas
  // draw — state.calib is exactly what openCalib() itself would set).
  state.calib = { pts: [{x:0,y:0},{x:100,y:0}], ptDist: 100 };
  document.getElementById('cal-m').value = '5';

  var callCount = 0;
  var _origSetTool = setTool;
  setTool = function(t) { callCount++; return _origSetTool(t); };

  document.getElementById('cal-ok').click();

  setTool = _origSetTool;  // restore

  var scaleNowSet = !!(PS[3] && PS[3].scale);
  var toolReArmed = state.tool === 'dist';   // the ORIGINAL intended tool, not 'poly'/'scale'
  var rearmedExactlyOnce = callCount === 1;

  return {
    armedScale, scaleNowSet, toolReArmed, rearmedExactlyOnce, callCount,
    pass: armedScale && scaleNowSet && toolReArmed && rearmedExactlyOnce
  };
}
"""

# ---------------------------------------------------------------------------
# Sub-check 4 — countExemptFromScaleGate
# ---------------------------------------------------------------------------
CHECK_COUNT_EXEMPT = r"""
() => {
  caseId = 'test'; pageCount = 5; pageTags = { 3: 'site' }; excluded = {};
  curPage = 3; state.tool = 'select';
  PS = { 3: { objects: [], scale: null, annotations: [] } };
  _jitHideBanner();

  setTool('count');
  var armed = state.tool === 'count';
  var banner = document.getElementById('jit-banner');
  var bannerHidden = !banner || banner.style.display === 'none';

  return { armed, bannerHidden, pass: armed && bannerHidden };
}
"""

CHECKS = [
    ("taggedUnscaledBlocksAndBanner", CHECK_UNSCALED_BLOCKS,          ["pass"]),
    ("bannerTapArmsScaleTool",        CHECK_BANNER_TAP_ARMS_SCALE,    ["pass"]),
    ("scaleCommitRearmsPendingOnce",  CHECK_SCALE_COMMIT_REARM,       ["pass"]),
    ("countExemptFromScaleGate",      CHECK_COUNT_EXEMPT,             ["pass"]),
]

# ---------------------------------------------------------------------------
# Sub-check 5 — reportNullAreaEndToEnd (real buildReportPayload -> real
# /report grid). Runs across TWO pages: page1 builds the payload via the
# real production function; page2 loads /report with that exact payload
# pre-seeded into sessionStorage (via add_init_script, since a fresh
# Playwright page/tab does not inherit page1's sessionStorage the way a
# same-origin window.open() would in the real app).
# ---------------------------------------------------------------------------
BUILD_PAYLOAD = r"""
() => {
  LAYERS.length = 0; FOLDERS.length = 0; initLayers();
  pageCount = 8; excluded = {}; pageFloorNum = {}; pageFloorKind = {};
  state.pageFolderMode = true; caseId = 'test'; curPage = 7;
  PS = { 7: { objects: [], scale: null, annotations: [] } };  // NO scale — legacy unscaled page
  pageTags = { 7: 'floor' };
  liteSetFloorKind(7, 'normal');
  liteSetFloorNum(7, 2);
  reseedActivePageFolders();

  var gfaLayer = null;
  childrenOf('PF_floor_2').forEach(function(c) {
    if (c.kind === 'layer' && c.node.role === 'gfa') gfaLayer = c.node;
  });
  if (!gfaLayer) return JSON.stringify({ err: 'no gfa layer seeded' });

  // ONE real poly object (state object, not a mock) on the unscaled page.
  PS[7].objects.push({ kind: 'poly', catId: gfaLayer.id,
    pts: [{x:0,y:0},{x:100,y:0},{x:100,y:100},{x:0,y:100}] });

  var payload = buildReportPayload();
  return JSON.stringify(payload);
}
"""

CHECK_GRID_RENDER = r"""
() => {
  var tds = document.querySelectorAll('#re-host td[data-x="1"]');
  var nullCell = null;
  tds.forEach(function(td) { if (td.textContent.trim() === '—') nullCell = td; });
  return {
    nullCellFound: !!nullCell,
    title: nullCell ? nullCell.title : null,
    hasClass: nullCell ? nullCell.classList.contains('re-null-area') : false
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
        pg.goto(f"http://127.0.0.1:{port}/", wait_until="networkidle")
        time.sleep(2.0)  # allow dynamic script load + setTimeout bootstrap

        try:
            setup_result = pg.evaluate(SETUP_GLOBALS)
            print(f"  SETUP: {setup_result}")
        except Exception as ex:
            print(f"  SETUP FAILED: {ex}")
            failures.append(f"setup threw: {ex}")

        print()
        print("LITE-SCALE-GATE checks:")
        for name, scenario, required_keys in CHECKS:
            try:
                result = pg.evaluate(scenario)
            except Exception as ex:
                print(f"  {name:32s} -> EXCEPTION: {ex}")
                failures.append(f"check '{name}' threw: {ex}")
                continue

            ok = all(result.get(k) is True for k in required_keys)
            status = "PASS" if ok else "FAIL"
            print(f"  {name:32s} -> {status}  {result}")
            if not ok:
                bad = [k for k in required_keys if result.get(k) is not True]
                failures.append(f"check '{name}' failed keys: {bad}  result={result}")

        # --- check 5: reportNullAreaEndToEnd ---
        name = "reportNullAreaEndToEnd"
        try:
            payload_json = pg.evaluate(BUILD_PAYLOAD)
            payload = json.loads(payload_json)
        except Exception as ex:
            print(f"  {name:32s} -> EXCEPTION building payload: {ex}")
            failures.append(f"check '{name}' threw building payload: {ex}")
            payload = None

        if payload is not None and "err" not in payload:
            # -- independent ground truth (Python side) --
            null_row = None
            group_with_null = None
            for p in payload.get("pages", []):
                for g in p.get("groups", []):
                    for r in g.get("rows", []):
                        if r.get("area") is None:
                            null_row = r
                            group_with_null = g
            rowFoundNull = null_row is not None
            subtotalExcludesNull = (group_with_null is not None) and (group_with_null.get("subtotal") == 0.0)
            netExcludesNull = payload["pages"] and payload["pages"][0].get("net") == 0.0

            # -- feed the SAME payload into the real /report page --
            pg2 = b.new_page()
            pg2.on("pageerror", lambda e: page_errors.append(f"pageerror(report): {e}"))
            pg2.add_init_script(
                "window.sessionStorage.setItem('bmaReportPayload', " + json.dumps(payload_json) + ");"
            )
            pg2.goto(f"http://127.0.0.1:{port}/report", wait_until="networkidle")
            time.sleep(1.0)
            grid_result = pg2.evaluate(CHECK_GRID_RENDER)
            pg2.close()

            nullCellFound = grid_result.get("nullCellFound") is True
            titleOk = (grid_result.get("title") or "") == "ยังไม่ตั้งมาตราส่วน"
            classOk = grid_result.get("hasClass") is True

            result = {
                "rowFoundNull": rowFoundNull, "subtotalExcludesNull": subtotalExcludesNull,
                "netExcludesNull": netExcludesNull, "nullCellFound": nullCellFound,
                "titleOk": titleOk, "classOk": classOk,
            }
            ok = rowFoundNull and subtotalExcludesNull and netExcludesNull and nullCellFound and titleOk and classOk
            status = "PASS" if ok else "FAIL"
            print(f"  {name:32s} -> {status}  {result}")
            if not ok:
                failures.append(f"check '{name}' failed: result={result}")
        elif payload is not None:
            print(f"  {name:32s} -> FAIL  {payload}")
            failures.append(f"check '{name}' failed: {payload}")

        pg.close()
        b.close()

    for e in page_errors:
        print("  JS ERROR:", e)

    server.should_exit = True
    time.sleep(0.4)

    if failures:
        for f in failures:
            print("FAIL:", f)
        print("LITE_SCALE_GATE_FAIL")
        sys.exit(1)
    else:
        print("LITE_SCALE_GATE_OK")


if __name__ == "__main__":
    main()
