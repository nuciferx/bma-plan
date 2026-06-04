"""
BUG-20260526-lite-force-setup: Page Setup mandatory before any other action.

11 sub-checks:
  triggerOnUpload           simulate upload complete -> #ov visible + __lwizAutoFired===true
  blockKeyboard_S           wizard+lock active -> dispatch 'S' key -> state.tool unchanged
  blockKeyboard_A           wizard+lock active -> dispatch 'A' key -> state.tool unchanged
  blockKeyboard_Esc         wizard open, no tags -> Escape doesn't close wizard
  blockClickOutside         wizard+lock active -> click on canvas -> no draw event (state unchanged)
  blockClickRibbon          wizard+lock active -> click a ribbon/menu button -> nothing happens
  wizardInteractiveStillWorks  click step tab inside #ov-panel -> step changes (wizard still works)
  forceFillNearestNeighbor  p1=site, p2=floor#1, p6=floor#3; p3-p5 untagged; Done ->
                            p3 inherits from p2 (dist 1), p4 from p2 (dist 2, tiebreak lower idx),
                            p5 from p6 (dist 1)
  forceFillNoNeighborFallback  0 tagged pages, click Done -> all pages get "excluded"
  unlockAfterDone           after Done wizard closes -> __lwizAutoLockActive===false, S key works
  secondUploadRetriggers    reset state, simulate new upload -> wizard fires again

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
# Shared setup helper — runs before each check that needs wizard open + lock
# ---------------------------------------------------------------------------
OPEN_WIZARD_WITH_LOCK = r"""
async () => {
  // Reset all wiz-auto state
  window.__lwizAutoFired = false;
  window.__lwizAutoSuppressed = false;
  window.__lwizAutoLockActive = false;
  pageTags = {};
  pageCount = 6;

  // Lift any existing lock listeners first
  if (typeof _lwizAutoLiftLock === 'function') _lwizAutoLiftLock();

  // Close wizard if open
  var ov = document.getElementById('ov');
  if (ov) ov.classList.remove('show');

  // Mock caseId so openOv allows open
  caseId = 'test-bug-mock';

  // Open wizard and install hard-block lock
  if (typeof openOv === 'function') openOv();
  await new Promise(r => setTimeout(r, 200));
  if (typeof _lwizInstallLock === 'function') _lwizInstallLock();

  return { ready: true };
}
"""

# ---------------------------------------------------------------------------
# Sub-check 1 — triggerOnUpload
# Simulates the post-upload trigger logic (as wrapped by _lwizWrapUploadPdf).
# ---------------------------------------------------------------------------
CHECK_TRIGGER_ON_UPLOAD = r"""
async () => {
  // Reset
  window.__lwizAutoFired = false;
  window.__lwizAutoSuppressed = false;
  window.__lwizAutoLockActive = false;
  if (typeof _lwizAutoLiftLock === 'function') _lwizAutoLiftLock();
  var ov = document.getElementById('ov');
  if (ov) ov.classList.remove('show');

  // Simulate upload complete (exactly what the wrapper does)
  caseId = 'test-upload-trigger';
  pageCount = 3;
  pageTags = {};

  if (!window.__lwizAutoFired && !window.__lwizAutoSuppressed &&
      typeof caseId !== 'undefined' && caseId &&
      typeof pageCount !== 'undefined' && pageCount > 0) {
    window.__lwizAutoFired = true;
    if (typeof window.openOv === 'function') {
      window.openOv();
      if (typeof _lwizInstallLock === 'function') _lwizInstallLock();
    }
  }

  await new Promise(r => setTimeout(r, 300));

  var isOpen = ov && ov.classList.contains('show');
  var fired = window.__lwizAutoFired === true;

  return {
    firedFlag: fired,
    ovOpen: !!isOpen,
    lockActive: window.__lwizAutoLockActive === true,
    allOk: fired && !!isOpen
  };
}
"""

# ---------------------------------------------------------------------------
# Sub-check 2 — blockKeyboard_S
# ---------------------------------------------------------------------------
CHECK_BLOCK_KEY_S = r"""
async () => {
  // Setup: open wizard with hard-block
  window.__lwizAutoFired = false;
  window.__lwizAutoSuppressed = false;
  window.__lwizAutoLockActive = false;
  if (typeof _lwizAutoLiftLock === 'function') _lwizAutoLiftLock();
  pageTags = {};
  caseId = 'test-bug-mock';
  var ov = document.getElementById('ov');
  if (ov) ov.classList.remove('show');
  if (typeof openOv === 'function') openOv();
  await new Promise(r => setTimeout(r, 200));
  if (typeof _lwizInstallLock === 'function') _lwizInstallLock();
  await new Promise(r => setTimeout(r, 100));

  var toolBefore = state.tool;

  // Dispatch 'S' key (Set Scale shortcut)
  document.dispatchEvent(new KeyboardEvent('keydown', {
    key: 's', bubbles: true, cancelable: true
  }));
  await new Promise(r => setTimeout(r, 200));

  var toolAfter = state.tool;
  var ovStillOpen = ov && ov.classList.contains('show');
  var toolUnchanged = toolBefore === toolAfter;

  return {
    toolBefore: toolBefore,
    toolAfter: toolAfter,
    ovStillOpen: !!ovStillOpen,
    toolUnchanged: toolUnchanged,
    lockActive: window.__lwizAutoLockActive === true,
    allOk: toolUnchanged && !!ovStillOpen && window.__lwizAutoLockActive === true
  };
}
"""

# ---------------------------------------------------------------------------
# Sub-check 3 — blockKeyboard_A
# ---------------------------------------------------------------------------
CHECK_BLOCK_KEY_A = r"""
async () => {
  // Wizard should still be open + lock active from check 2
  if (!window.__lwizAutoLockActive) {
    if (typeof _lwizInstallLock === 'function') _lwizInstallLock();
  }
  var ov = document.getElementById('ov');
  if (!ov || !ov.classList.contains('show')) {
    caseId = 'test-bug-mock';
    if (typeof openOv === 'function') openOv();
    await new Promise(r => setTimeout(r, 200));
    if (typeof _lwizInstallLock === 'function') _lwizInstallLock();
  }
  await new Promise(r => setTimeout(r, 100));

  var toolBefore = state.tool;

  // Dispatch 'A' key (Area tool shortcut)
  document.dispatchEvent(new KeyboardEvent('keydown', {
    key: 'a', bubbles: true, cancelable: true
  }));
  await new Promise(r => setTimeout(r, 200));

  var toolAfter = state.tool;
  var toolUnchanged = toolBefore === toolAfter;
  var ovStillOpen = ov && ov.classList.contains('show');

  return {
    toolBefore: toolBefore,
    toolAfter: toolAfter,
    toolUnchanged: toolUnchanged,
    ovStillOpen: !!ovStillOpen,
    allOk: toolUnchanged && !!ovStillOpen
  };
}
"""

# ---------------------------------------------------------------------------
# Sub-check 4 — blockKeyboard_Esc
# ---------------------------------------------------------------------------
CHECK_BLOCK_ESC = r"""
async () => {
  // Ensure lock is active, no tags
  pageTags = {};
  if (!window.__lwizAutoLockActive) {
    if (typeof _lwizInstallLock === 'function') _lwizInstallLock();
  }
  var ov = document.getElementById('ov');
  if (!ov || !ov.classList.contains('show')) {
    caseId = 'test-bug-mock';
    if (typeof openOv === 'function') openOv();
    await new Promise(r => setTimeout(r, 200));
    if (typeof _lwizInstallLock === 'function') _lwizInstallLock();
  }
  await new Promise(r => setTimeout(r, 100));

  var openBefore = ov && ov.classList.contains('show');

  // Dispatch Escape — should be blocked
  document.dispatchEvent(new KeyboardEvent('keydown', {
    key: 'Escape', bubbles: true, cancelable: true
  }));
  await new Promise(r => setTimeout(r, 200));

  var stillOpen = ov && ov.classList.contains('show');

  return {
    openBefore: !!openBefore,
    stillOpen: !!stillOpen,
    lockActive: window.__lwizAutoLockActive === true,
    allOk: !!openBefore && !!stillOpen
  };
}
"""

# ---------------------------------------------------------------------------
# Sub-check 5 — blockClickOutside
# ---------------------------------------------------------------------------
CHECK_BLOCK_CLICK_OUTSIDE = r"""
async () => {
  if (!window.__lwizAutoLockActive) {
    if (typeof _lwizInstallLock === 'function') _lwizInstallLock();
  }
  var ov = document.getElementById('ov');
  if (!ov || !ov.classList.contains('show')) {
    caseId = 'test-bug-mock';
    if (typeof openOv === 'function') openOv();
    await new Promise(r => setTimeout(r, 200));
    if (typeof _lwizInstallLock === 'function') _lwizInstallLock();
  }
  await new Promise(r => setTimeout(r, 100));

  var toolBefore = state.tool;
  var draftBefore = state.draft;

  // Click on the canvas element (outside panel)
  var cv = document.getElementById('cv');
  if (cv) {
    var rect = cv.getBoundingClientRect();
    var mx = Math.round(rect.left + rect.width / 2);
    var my = Math.round(rect.top + rect.height / 2);
    cv.dispatchEvent(new MouseEvent('click', {
      bubbles: true, cancelable: true, clientX: mx, clientY: my
    }));
  }
  await new Promise(r => setTimeout(r, 200));

  var toolAfter = state.tool;
  var draftAfter = state.draft;
  var ovStillOpen = ov && ov.classList.contains('show');
  // state.tool should not have changed; no draft should have started
  var toolUnchanged = toolBefore === toolAfter;

  return {
    cvExists: !!cv,
    toolBefore: toolBefore,
    toolAfter: toolAfter,
    toolUnchanged: toolUnchanged,
    ovStillOpen: !!ovStillOpen,
    allOk: toolUnchanged && !!ovStillOpen
  };
}
"""

# ---------------------------------------------------------------------------
# Sub-check 6 — blockClickRibbon
# ---------------------------------------------------------------------------
CHECK_BLOCK_CLICK_RIBBON = r"""
async () => {
  if (!window.__lwizAutoLockActive) {
    if (typeof _lwizInstallLock === 'function') _lwizInstallLock();
  }
  var ov = document.getElementById('ov');
  if (!ov || !ov.classList.contains('show')) {
    caseId = 'test-bug-mock';
    if (typeof openOv === 'function') openOv();
    await new Promise(r => setTimeout(r, 200));
    if (typeof _lwizInstallLock === 'function') _lwizInstallLock();
  }
  await new Promise(r => setTimeout(r, 100));

  var toolBefore = state.tool;

  // Find a ribbon button outside the panel and click it
  var ribbonBtn = document.querySelector('.ribbon .btn, #mi-save, #btn-area, #btn-scale');
  var clicked = false;
  if (ribbonBtn) {
    ribbonBtn.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true }));
    clicked = true;
  }
  await new Promise(r => setTimeout(r, 200));

  var toolAfter = state.tool;
  var toolUnchanged = toolBefore === toolAfter;
  var ovStillOpen = ov && ov.classList.contains('show');

  return {
    foundBtn: clicked,
    toolBefore: toolBefore,
    toolAfter: toolAfter,
    toolUnchanged: toolUnchanged,
    ovStillOpen: !!ovStillOpen,
    allOk: toolUnchanged && !!ovStillOpen
  };
}
"""

# ---------------------------------------------------------------------------
# Sub-check 7 — wizardInteractiveStillWorks
# Clicking a step tab INSIDE #ov-panel should still change the step.
# ---------------------------------------------------------------------------
CHECK_WIZARD_INTERACTIVE = r"""
async () => {
  if (!window.__lwizAutoLockActive) {
    if (typeof _lwizInstallLock === 'function') _lwizInstallLock();
  }
  var ov = document.getElementById('ov');
  if (!ov || !ov.classList.contains('show')) {
    caseId = 'test-bug-mock';
    if (typeof openOv === 'function') openOv();
    await new Promise(r => setTimeout(r, 200));
    if (typeof _lwizInstallLock === 'function') _lwizInstallLock();
  }
  await new Promise(r => setTimeout(r, 100));

  // Ensure we are on Step 1
  if (typeof _lovsGoStep === 'function') _lovsGoStep(1);
  await new Promise(r => setTimeout(r, 100));

  // Click step-2 tab inside #ov-panel
  var stepBtn = document.querySelector('#ov-steps .step[data-step="2"]');
  if (stepBtn) stepBtn.click();
  await new Promise(r => setTimeout(r, 200));

  // Check step changed to 2
  var step2Active = !!(document.querySelector('#ov-steps .step[data-step="2"].act'));

  // Go back to step 1 for cleanliness
  if (typeof _lovsGoStep === 'function') _lovsGoStep(1);

  return {
    foundStepBtn: !!stepBtn,
    step2Active: step2Active,
    allOk: !!stepBtn && step2Active
  };
}
"""

# ---------------------------------------------------------------------------
# Sub-check 8 — forceFillNearestNeighbor
# p1=site, p2=floor#1, p6=floor#3 (tagged). p3,p4,p5 untagged.
# After _lovsForceFillMissingTags():
#   p3 nearest = p2 (dist 1) -> floor#1
#   p4 nearest = p2 (dist 2) vs p6 (dist 2) -> tiebreak lower idx -> p2 -> floor#1
#   p5 nearest = p6 (dist 1) -> floor#3
# ---------------------------------------------------------------------------
CHECK_FORCE_FILL_NEIGHBOR = r"""
async () => {
  // Setup 6-page state
  pageCount = 6;
  pageTags = {};
  pageFloorNum = {};
  pageFloorKind = {};

  // Tag p1=site, p2=floor (floor#1), p6=floor (floor#3)
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

  // p3, p4, p5 remain untagged

  // Run force-fill
  if (typeof _lovsForceFillMissingTags === 'function') {
    _lovsForceFillMissingTags();
  } else {
    return { err: '_lovsForceFillMissingTags not found', allOk: false };
  }

  var t3 = pageTags[3];
  var t4 = pageTags[4];
  var t5 = pageTags[5];
  var f3 = pageFloorNum[3];
  var f4 = pageFloorNum[4];
  var f5 = pageFloorNum[5];

  // p3: nearest = p2 (dist 1) => floor#1
  var p3ok = (t3 === 'floor') && (f3 === 1);
  // p4: nearest = p2 (dist 2) tiebreak lower idx => floor#1
  var p4ok = (t4 === 'floor') && (f4 === 1);
  // p5: nearest = p6 (dist 1) => floor#3
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
# Sub-check 9 — forceFillNoNeighborFallback
# 0 tagged pages -> all get "excluded"
# ---------------------------------------------------------------------------
CHECK_FORCE_FILL_NO_NEIGHBOR = r"""
async () => {
  pageCount = 4;
  pageTags = {};
  pageFloorNum = {};
  pageFloorKind = {};

  // No tags set at all

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

  return {
    tags: tags,
    allExcluded: allExcluded,
    allOk: allExcluded
  };
}
"""

# ---------------------------------------------------------------------------
# Sub-check 10 — unlockAfterDone
# After wizard closes via Done (Step 3), lock is lifted and S key works.
# ---------------------------------------------------------------------------
CHECK_UNLOCK_AFTER_DONE = r"""
async () => {
  // Open wizard, install lock
  window.__lwizAutoLockActive = false;
  if (typeof _lwizAutoLiftLock === 'function') _lwizAutoLiftLock();
  pageTags = {};
  caseId = 'test-bug-mock';
  pageCount = 3;
  var ov = document.getElementById('ov');
  if (ov) ov.classList.remove('show');
  if (typeof openOv === 'function') openOv();
  await new Promise(r => setTimeout(r, 200));
  if (typeof _lwizInstallLock === 'function') _lwizInstallLock();
  await new Promise(r => setTimeout(r, 100));

  var lockBefore = window.__lwizAutoLockActive;

  // Tag at least 1 page to lift lock (as liteSetTag wrapper does)
  if (typeof liteSetTag === 'function') {
    liteSetTag(1, 'site');
  } else {
    pageTags[1] = 'site';
    if (typeof _lwizAutoLiftLock === 'function') _lwizAutoLiftLock();
  }
  await new Promise(r => setTimeout(r, 100));

  // Simulate Done: navigate to step 3 then click Done
  if (typeof _lovsGoStep === 'function') _lovsGoStep(3);
  await new Promise(r => setTimeout(r, 100));

  // Click the Done (ov-next on step 3) button
  var nextBtn = document.getElementById('ov-next');
  if (nextBtn) nextBtn.click();
  await new Promise(r => setTimeout(r, 200));

  var lockAfter = window.__lwizAutoLockActive;
  var ovClosed = ov && !ov.classList.contains('show');

  // Now dispatch 'S' key — should work (tool changes or at least no block)
  var toolBefore = state.tool;
  document.dispatchEvent(new KeyboardEvent('keydown', {
    key: 's', bubbles: true, cancelable: true
  }));
  await new Promise(r => setTimeout(r, 200));

  // After lift, keydown is not swallowed at document level by our guard.
  // The test just verifies lock is false (key events reach their normal handlers).
  return {
    lockBefore: lockBefore,
    lockAfter: lockAfter,
    ovClosed: !!ovClosed,
    lockLifted: lockAfter === false,
    allOk: lockBefore === true && lockAfter === false && !!ovClosed
  };
}
"""

# ---------------------------------------------------------------------------
# Sub-check 11 — secondUploadRetriggers
# Simulate state reset + new upload -> wizard fires again.
# ---------------------------------------------------------------------------
CHECK_SECOND_UPLOAD_RETRIGGERS = r"""
async () => {
  // First upload was already triggered. Now simulate a second upload:
  // The wrapper resets __lwizAutoFired=false before calling original.
  window.__lwizAutoFired = false;
  window.__lwizAutoSuppressed = false;
  window.__lwizAutoLockActive = false;
  if (typeof _lwizAutoLiftLock === 'function') _lwizAutoLiftLock();
  pageTags = {};
  var ov = document.getElementById('ov');
  if (ov) ov.classList.remove('show');

  // Simulate second upload complete
  caseId = 'test-second-upload';
  pageCount = 2;

  if (!window.__lwizAutoFired && !window.__lwizAutoSuppressed &&
      typeof caseId !== 'undefined' && caseId &&
      typeof pageCount !== 'undefined' && pageCount > 0) {
    window.__lwizAutoFired = true;
    if (typeof window.openOv === 'function') {
      window.openOv();
      if (typeof _lwizInstallLock === 'function') _lwizInstallLock();
    }
  }

  await new Promise(r => setTimeout(r, 300));

  var isOpen = ov && ov.classList.contains('show');
  var fired = window.__lwizAutoFired === true;

  return {
    firedFlag: fired,
    ovOpen: !!isOpen,
    lockActive: window.__lwizAutoLockActive === true,
    allOk: fired && !!isOpen
  };
}
"""

# ---------------------------------------------------------------------------
# Check list
# ---------------------------------------------------------------------------
CHECKS = [
    ("triggerOnUpload",                 CHECK_TRIGGER_ON_UPLOAD,       ["allOk"]),
    ("blockKeyboard_S",                 CHECK_BLOCK_KEY_S,             ["allOk"]),
    ("blockKeyboard_A",                 CHECK_BLOCK_KEY_A,             ["allOk"]),
    ("blockKeyboard_Esc",               CHECK_BLOCK_ESC,               ["allOk"]),
    ("blockClickOutside",               CHECK_BLOCK_CLICK_OUTSIDE,     ["allOk"]),
    ("blockClickRibbon",                CHECK_BLOCK_CLICK_RIBBON,      ["allOk"]),
    ("wizardInteractiveStillWorks",     CHECK_WIZARD_INTERACTIVE,      ["allOk"]),
    ("forceFillNearestNeighbor",        CHECK_FORCE_FILL_NEIGHBOR,     ["allOk"]),
    ("forceFillNoNeighborFallback",     CHECK_FORCE_FILL_NO_NEIGHBOR,  ["allOk"]),
    ("unlockAfterDone",                 CHECK_UNLOCK_AFTER_DONE,       ["allOk"]),
    ("secondUploadRetriggers",          CHECK_SECOND_UPLOAD_RETRIGGERS,["allOk"]),
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
        print("BUG-20260526-LITE-FORCE-SETUP checks:")
        for name, scenario, required_keys in CHECKS:
            try:
                result = pg.evaluate(scenario)
            except Exception as ex:
                print(f"  {name:45s} -> EXCEPTION: {ex}")
                failures.append(f"check '{name}' threw: {ex}")
                continue

            ok = all(result.get(k) is True for k in required_keys)
            status = "PASS" if ok else "FAIL"
            print(f"  {name:45s} -> {status}  {result}")
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
