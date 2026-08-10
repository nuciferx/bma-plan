"""
BUG-20260526-lite-force-setup — RETIRED.

UPDATED (page-manager-redesign approach D, slice 3 — WIZ-UNLOCK,
docs/invent/page-manager-redesign.md, GO 2026-08-10, Decision note): this
file used to lock down "Page Setup mandatory before any other action" —
a document-wide keyboard+mouse hard lock (wiz-auto.js's _lwizInstallLock)
that swallowed every key/click outside the wizard panel until a page was
tagged. That hard lock is now RETIRED outright (docs/invent/
page-manager-redesign.md CHECKPOINT policy question, answered GO):
per-page measure discipline moved to tag-jit.js's JIT banner (see
test_tag_jit.py / test_scale_gate.py / test_tag_jit_banner_fix.py) instead
of an app-wide lock. This file now asserts the NEW contract: nothing is
blocked anymore, the wizard opens only manually, and the ONE remaining
gate on measurement (the JIT banner) lives entirely in tag-jit.js, not
here.

The force-fill-nearest-neighbor logic (Step-3 "Done" auto-tagging of any
still-untagged pages, lite/static/js/overview-setup.js's
_lovsForceFillMissingTags) is UNRELATED to the retired lock and still
ships — its coverage is kept verbatim.

8 sub-checks:
  keyboardSNotBlocked       wizard open manually, 0 tagged pages -> 'S' key
                            is NOT swallowed (state.tool free to change)
  keyboardANotBlocked       same, 'A' key
  escNotBlocked             wizard open, 0 tags, Esc (no selection) closes
                            the wizard normally — no hard-lock veto
  clickOutsideNoHint        wizard open, 0 tags, click on canvas -> the old
                            lock's "ตั้งค่าหน้า...ให้เสร็จก่อน" hint never
                            appears (the mousedown/keydown hint handler that
                            lived inside _lwizInstallLock is gone)
  wizardInteractiveStillWorks  click a step tab INSIDE #ov-panel -> step
                            still changes (the wizard itself still works,
                            only the auto-open+lock around it is gone)
  forceFillNearestNeighbor  UNCHANGED — p1=site, p2=floor#1, p6=floor#3;
                            p3-p5 untagged; Done -> p3 inherits from p2
                            (dist 1), p4 from p2 (dist 2, tiebreak lower
                            idx), p5 from p6 (dist 1)
  forceFillNoNeighborFallback  UNCHANGED — 0 tagged pages, click Done ->
                            all pages get "excluded"
  pageSetupNoLongerMandatory  0 tagged pages, wizard CLOSED (never even
                            opened) -> arming a measure tool is still
                            safely gated, but by tag-jit.js's JIT banner
                            (jitGuardTool), not by anything in this file —
                            the "mandatory Page Setup" concept this bug
                            once enforced is structurally gone

Emits BUG_20260526_LITE_FORCE_SETUP_OK on success.

    py -3 lite/tests/test_bug_force_setup.py
"""
import socket, threading, time, sys
from pathlib import Path

LITE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LITE))
import uvicorn
from playwright.sync_api import sync_playwright

REPO = LITE.parent
PDF_PATH = REPO / "proto" / "test_plan_A1.pdf"


def _free_port(start=8600):
    for p in range(start, start + 60):
        with socket.socket() as s:
            if s.connect_ex(("127.0.0.1", p)) != 0:
                return p
    raise RuntimeError("no free port")


# ---------------------------------------------------------------------------
# Sub-check 1 — keyboardSNotBlocked
# ---------------------------------------------------------------------------
CHECK_KEY_S_NOT_BLOCKED = r"""
async () => {
  pageTags = {};
  caseId = 'test-bug-mock';
  var ov = document.getElementById('ov');
  if (ov) ov.classList.remove('show');
  if (typeof openOv === 'function') openOv();
  await new Promise(r => setTimeout(r, 200));

  var toolBefore = state.tool;
  document.dispatchEvent(new KeyboardEvent('keydown', {
    key: 's', bubbles: true, cancelable: true
  }));
  await new Promise(r => setTimeout(r, 150));
  var toolAfter = state.tool;
  var ovStillOpen = ov && ov.classList.contains('show');

  return {
    toolBefore: toolBefore,
    toolAfter: toolAfter,
    toolChanged: toolAfter !== toolBefore,
    ovStillOpen: !!ovStillOpen,
    lockActive: window.__lwizAutoLockActive === true,
    allOk: toolAfter === 'scale' && window.__lwizAutoLockActive !== true
  };
}
"""

# ---------------------------------------------------------------------------
# Sub-check 2 — keyboardANotBlocked
# 'a' maps to the 'poly' tool, which tag-jit.js DOES gate on an untagged
# page (by design — see test_tag_jit.py) — that gate is NOT the retired
# hard lock. Tag + scale the current page first so this check isolates
# "is the OLD force-setup lock gone" from "is the (still-shipping) JIT
# gate active", which is covered elsewhere.
# ---------------------------------------------------------------------------
CHECK_KEY_A_NOT_BLOCKED = r"""
async () => {
  caseId = 'test-bug-mock';
  pageTags = { 1: 'site' };
  if (typeof curPage !== 'undefined') curPage = 1;
  PS = PS || {}; PS[1] = { objects: [], scale: { pts_per_m: 10 }, annotations: [] };
  var ov = document.getElementById('ov');
  if (!ov || !ov.classList.contains('show')) {
    if (typeof openOv === 'function') openOv();
    await new Promise(r => setTimeout(r, 200));
  }

  var toolBefore = state.tool;
  document.dispatchEvent(new KeyboardEvent('keydown', {
    key: 'a', bubbles: true, cancelable: true
  }));
  await new Promise(r => setTimeout(r, 150));
  var toolAfter = state.tool;

  return {
    toolBefore: toolBefore,
    toolAfter: toolAfter,
    toolChanged: toolAfter !== toolBefore,
    allOk: toolAfter === 'poly'
  };
}
"""

# ---------------------------------------------------------------------------
# Sub-check 3 — escNotBlocked
# ---------------------------------------------------------------------------
CHECK_ESC_NOT_BLOCKED = r"""
async () => {
  pageTags = {};
  caseId = 'test-bug-mock';
  var ov = document.getElementById('ov');
  if (ov) ov.classList.remove('show');
  if (typeof openOv === 'function') openOv();
  await new Promise(r => setTimeout(r, 200));
  if (typeof _lovsSelected !== 'undefined') _lovsSelected.clear();

  var openBefore = ov && ov.classList.contains('show');

  document.dispatchEvent(new KeyboardEvent('keydown', {
    key: 'Escape', bubbles: true, cancelable: true
  }));
  await new Promise(r => setTimeout(r, 200));

  var closedAfter = ov && !ov.classList.contains('show');

  return {
    openBefore: !!openBefore,
    closedAfter: !!closedAfter,
    allOk: !!openBefore && !!closedAfter
  };
}
"""

# ---------------------------------------------------------------------------
# Sub-check 4 — clickOutsideNoHint
# The old lock showed a "ตั้งค่าหน้า...ให้เสร็จก่อน" hint on any click
# outside #ov-panel. With the lock gone, that hint must never appear.
# ---------------------------------------------------------------------------
CHECK_CLICK_OUTSIDE_NO_HINT = r"""
async () => {
  pageTags = {};
  caseId = 'test-bug-mock';
  var ov = document.getElementById('ov');
  if (ov) ov.classList.remove('show');
  if (typeof openOv === 'function') openOv();
  await new Promise(r => setTimeout(r, 200));

  var existingHint = document.getElementById('lwiz-hint');
  if (existingHint) existingHint.remove();

  var cv = document.getElementById('cv');
  if (cv) {
    var rect = cv.getBoundingClientRect();
    cv.dispatchEvent(new MouseEvent('click', {
      bubbles: true, cancelable: true,
      clientX: Math.round(rect.left + rect.width / 2),
      clientY: Math.round(rect.top + rect.height / 2)
    }));
  }
  await new Promise(r => setTimeout(r, 200));

  var hintEl = document.getElementById('lwiz-hint');
  var hintShown = !!hintEl && hintEl.style.opacity !== '0';

  return {
    cvExists: !!cv,
    hintShown: hintShown,
    allOk: !!cv && !hintShown
  };
}
"""

# ---------------------------------------------------------------------------
# Sub-check 5 — wizardInteractiveStillWorks
# ---------------------------------------------------------------------------
CHECK_WIZARD_INTERACTIVE = r"""
async () => {
  caseId = 'test-bug-mock';
  var ov = document.getElementById('ov');
  if (!ov || !ov.classList.contains('show')) {
    if (typeof openOv === 'function') openOv();
    await new Promise(r => setTimeout(r, 200));
  }

  if (typeof _lovsGoStep === 'function') _lovsGoStep(1);
  await new Promise(r => setTimeout(r, 100));

  var stepBtn = document.querySelector('#ov-steps .step[data-step="2"]');
  if (stepBtn) stepBtn.click();
  await new Promise(r => setTimeout(r, 200));

  var step2Active = !!(document.querySelector('#ov-steps .step[data-step="2"].act'));

  if (typeof _lovsGoStep === 'function') _lovsGoStep(1);

  return {
    foundStepBtn: !!stepBtn,
    step2Active: step2Active,
    allOk: !!stepBtn && step2Active
  };
}
"""

# ---------------------------------------------------------------------------
# Sub-check 6 — forceFillNearestNeighbor (UNCHANGED — unrelated feature)
# ---------------------------------------------------------------------------
CHECK_FORCE_FILL_NEIGHBOR = r"""
async () => {
  pageCount = 6;
  pageTags = {};
  pageFloorNum = {};
  pageFloorKind = {};

  if (typeof liteSetTag === 'function') {
    liteSetTag(1, 'site');
    liteSetTag(2, 'floor');
    liteSetTag(6, 'floor');
  } else {
    pageTags[1] = 'site';
    pageTags[2] = 'floor';
    pageTags[6] = 'floor';
  }
  pageFloorNum[2] = 1;
  pageFloorKind[2] = 'normal';
  pageFloorNum[6] = 3;
  pageFloorKind[6] = 'normal';

  if (typeof _lovsForceFillMissingTags === 'function') {
    _lovsForceFillMissingTags();
  } else {
    return { err: '_lovsForceFillMissingTags not found', allOk: false };
  }

  var t3 = pageTags[3], t4 = pageTags[4], t5 = pageTags[5];
  var f3 = pageFloorNum[3], f4 = pageFloorNum[4], f5 = pageFloorNum[5];

  var p3ok = (t3 === 'floor') && (f3 === 1);
  var p4ok = (t4 === 'floor') && (f4 === 1);
  var p5ok = (t5 === 'floor') && (f5 === 3);

  return {
    p3tag: t3, p3floor: f3, p3ok: p3ok,
    p4tag: t4, p4floor: f4, p4ok: p4ok,
    p5tag: t5, p5floor: f5, p5ok: p5ok,
    allOk: p3ok && p4ok && p5ok
  };
}
"""

# ---------------------------------------------------------------------------
# Sub-check 7 — forceFillNoNeighborFallback (UNCHANGED — unrelated feature)
# ---------------------------------------------------------------------------
CHECK_FORCE_FILL_NO_NEIGHBOR = r"""
async () => {
  pageCount = 4;
  pageTags = {};
  pageFloorNum = {};
  pageFloorKind = {};

  if (typeof _lovsForceFillMissingTags === 'function') {
    _lovsForceFillMissingTags();
  } else {
    return { err: '_lovsForceFillMissingTags not found', allOk: false };
  }

  var allExcluded = true;
  var tags = [];
  for (var i = 1; i <= 4; i++) {
    tags.push(pageTags[i]);
    if (pageTags[i] !== 'excluded') allExcluded = false;
  }

  return { tags: tags, allExcluded: allExcluded, allOk: allExcluded };
}
"""

# ---------------------------------------------------------------------------
# Sub-check 8 — pageSetupNoLongerMandatory
# 0 tagged pages, wizard CLOSED (never opened) -> arming a measure tool is
# still safely gated, but by tag-jit.js's JIT banner, not this file.
# ---------------------------------------------------------------------------
CHECK_PAGE_SETUP_NOT_MANDATORY = r"""
async () => {
  caseId = 'test-bug-mock'; pageCount = 5; pageTags = {}; excluded = {};
  curPage = 1; state.tool = 'select';
  PS = { 1: { objects: [], scale: null, annotations: [] } };
  var ov = document.getElementById('ov');
  if (ov) ov.classList.remove('show');   // wizard never opened at all
  if (typeof _jitHideBanner === 'function') _jitHideBanner();

  var wizardNeverOpened = ov && !ov.classList.contains('show');

  var toolBefore = state.tool;
  setTool('poly');
  var toolBlocked = state.tool === toolBefore && state.tool !== 'poly';

  var banner = document.getElementById('jit-banner');
  var bannerShown = !!banner && banner.style.display !== 'none';

  return {
    wizardNeverOpened: !!wizardNeverOpened,
    toolBlocked: toolBlocked,
    bannerShown: bannerShown,
    allOk: !!wizardNeverOpened && toolBlocked && bannerShown
  };
}
"""

# ---------------------------------------------------------------------------
# Check list
# ---------------------------------------------------------------------------
CHECKS = [
    ("keyboardSNotBlocked",         CHECK_KEY_S_NOT_BLOCKED,           ["allOk"]),
    ("keyboardANotBlocked",         CHECK_KEY_A_NOT_BLOCKED,           ["allOk"]),
    ("escNotBlocked",               CHECK_ESC_NOT_BLOCKED,             ["allOk"]),
    ("clickOutsideNoHint",          CHECK_CLICK_OUTSIDE_NO_HINT,       ["allOk"]),
    ("wizardInteractiveStillWorks", CHECK_WIZARD_INTERACTIVE,          ["allOk"]),
    ("forceFillNearestNeighbor",    CHECK_FORCE_FILL_NEIGHBOR,         ["allOk"]),
    ("forceFillNoNeighborFallback", CHECK_FORCE_FILL_NO_NEIGHBOR,      ["allOk"]),
    ("pageSetupNoLongerMandatory",  CHECK_PAGE_SETUP_NOT_MANDATORY,    ["allOk"]),
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
        pg.set_default_timeout(90_000)
        pg.goto(f"http://127.0.0.1:{port}/", wait_until="networkidle")
        time.sleep(2.5)  # allow dynamic script load + setTimeout bootstrap

        print()
        print("BUG-20260526-LITE-FORCE-SETUP checks (RETIRED-lock contract):")
        for name, scenario, required_keys in CHECKS:
            try:
                result = pg.evaluate(scenario)
            except Exception as ex:
                print(f"  {name:30s} -> EXCEPTION: {ex}")
                failures.append(f"check '{name}' threw: {ex}")
                continue

            ok = all(result.get(k) is True for k in required_keys)
            status = "PASS" if ok else "FAIL"
            print(f"  {name:30s} -> {status}  {result}")
            if not ok:
                bad = [k for k in required_keys if result.get(k) is not True]
                failures.append(f"check '{name}' failed keys: {bad}  result={result}")

        pg.close()
        b.close()

    for e in page_errors:
        print("  JS ERROR:", e)

    server.should_exit = True
    time.sleep(0.4)

    total = len(CHECKS)
    passed = total - len(failures)
    if failures:
        for f in failures:
            print("FAIL:", f)
        print(f"BUG_20260526_LITE_FORCE_SETUP_FAIL {passed}/{total}")
        sys.exit(1)
    else:
        print(f"BUG_20260526_LITE_FORCE_SETUP_OK {total}/{total}")


if __name__ == "__main__":
    main()
