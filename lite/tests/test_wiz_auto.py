"""
LWIZ-AUTO: wiz-auto.js compat-shim regression test.

UPDATED (page-manager-redesign approach D, slice 3 — WIZ-UNLOCK,
docs/invent/page-manager-redesign.md, GO 2026-08-10, Decision note):
wiz-auto.js used to auto-open the Overview Setup wizard on PDF upload
complete / first scale-set, and hard-lock ALL keyboard+mouse input outside
#ov-panel until a page was tagged. Both are now RETIRED — replaced by
tag-jit.js's per-page JIT banner (see test_tag_jit.py / test_scale_gate.py /
test_tag_jit_banner_fix.py). This file asserts the NEW contract:
  - the wizard is still fully usable, but ONLY opened manually (F12/⇧F12/
    btn-ov — unaffected by this file, wired elsewhere)
  - nothing auto-opens it on upload or on first scale commit anymore
  - the hard-lock functions are gone outright (not merely unused)
  - keyboard is never captured/blocked by this file anymore, even with
    zero tagged pages

8 sub-checks:
  scriptInjected            <script id="__lwiz_auto_script__"> exists, src ends /wiz-auto.js
  bootInstalledWatcher      state.scaleStatus has get+set accessor (compat only, not data prop)
  noAutoOpenOnUpload        simulate upload-complete globals (caseId+pageCount set,
                            no manual openOv() call) -> #ov stays closed
  noAutoOpenOnFirstScale    state.scaleStatus='manual' -> #ov stays closed (fallback
                            trigger removed)
  manualOpenStillWorks      openOv() called directly -> #ov opens (the wizard itself
                            is untouched by this retirement — only auto-open is gone)
  hardLockFunctionsRemoved  _lwizInstallLock / _lwizAutoLiftLock / _lwizCheckLiftLock /
                            _lwizWrapLiteSetTag / _lwizWrapUploadPdf / _lwizWrapLoadProto
                            are all `undefined` — removed outright, not dead-but-present
  keyboardNeverBlocked      wizard open manually, 0 tagged pages -> 's' key is NOT
                            swallowed (state.tool free to change) and a single Esc
                            (no selection) closes the wizard normally — no hard lock
  loadProtoNoSideEffects    loadProto() with a minimal doc does not throw and does not
                            leave the wizard open (no retired-trigger side effects)

Emits LITE_WIZ_AUTO_OK 8/8 on success.

    py -3 lite/tests/test_wiz_auto.py
"""
import socket, threading, time, sys
from pathlib import Path

LITE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LITE))
import uvicorn
from playwright.sync_api import sync_playwright

REPO = LITE.parent
PDF_PATH = REPO / "proto" / "test_plan_A1.pdf"


def _free_port(start=8260):
    for p in range(start, start + 60):
        with socket.socket() as s:
            if s.connect_ex(("127.0.0.1", p)) != 0:
                return p
    raise RuntimeError("no free port")


# ---------------------------------------------------------------------------
# Sub-check 1 — scriptInjected
# ---------------------------------------------------------------------------
CHECK_SCRIPT_INJECTED = r"""
async () => {
  await new Promise(r => setTimeout(r, 600));
  var el = document.getElementById('__lwiz_auto_script__');
  var src = el ? el.getAttribute('src') : '';
  var srcOk = src && src.indexOf('/wiz-auto.js') >= 0;
  return {
    elementExists: !!el,
    src: src,
    srcOk: !!srcOk,
    allOk: !!el && !!srcOk
  };
}
"""

# ---------------------------------------------------------------------------
# Sub-check 2 — bootInstalledWatcher (compat accessor still installed)
# ---------------------------------------------------------------------------
CHECK_BOOT_INSTALLED_WATCHER = r"""
async () => {
  await new Promise(r => setTimeout(r, 400));
  var desc = Object.getOwnPropertyDescriptor(state, 'scaleStatus');
  var hasAccessor = !!(desc && typeof desc.get === 'function' && typeof desc.set === 'function');
  var isDataProp  = !!(desc && ('value' in desc));
  return {
    descExists: !!desc,
    hasGet: !!(desc && desc.get),
    hasSet: !!(desc && desc.set),
    hasAccessor: hasAccessor,
    isDataProp: isDataProp,
    allOk: hasAccessor && !isDataProp
  };
}
"""

# ---------------------------------------------------------------------------
# Sub-check 3 — noAutoOpenOnUpload
# Simulates exactly what a completed upload leaves behind (caseId + pageCount
# set) WITHOUT calling openOv() manually — the wizard must stay closed, since
# the auto-open-on-upload trigger no longer exists.
# ---------------------------------------------------------------------------
CHECK_NO_AUTO_OPEN_ON_UPLOAD = r"""
async () => {
  var ov = document.getElementById('ov');
  if (ov) ov.classList.remove('show');

  caseId = 'test-upload-mock';
  pageCount = 3;
  pageTags = {};

  await new Promise(r => setTimeout(r, 300));

  var stillClosed = ov && !ov.classList.contains('show');
  return { stillClosed: !!stillClosed, allOk: !!stillClosed };
}
"""

# ---------------------------------------------------------------------------
# Sub-check 4 — noAutoOpenOnFirstScale
# ---------------------------------------------------------------------------
CHECK_NO_AUTO_OPEN_ON_SCALE = r"""
async () => {
  var ov = document.getElementById('ov');
  if (ov) ov.classList.remove('show');
  caseId = 'test-mock';

  state.scaleStatus = 'unknown';
  state.scaleStatus = 'manual';

  await new Promise(r => setTimeout(r, 300));

  var stillClosed = ov && !ov.classList.contains('show');
  return { stillClosed: !!stillClosed, allOk: !!stillClosed };
}
"""

# ---------------------------------------------------------------------------
# Sub-check 5 — manualOpenStillWorks
# ---------------------------------------------------------------------------
CHECK_MANUAL_OPEN_STILL_WORKS = r"""
async () => {
  var ov = document.getElementById('ov');
  if (ov) ov.classList.remove('show');
  caseId = 'test-mock';

  var opened = false;
  if (typeof openOv === 'function') {
    openOv();
    await new Promise(r => setTimeout(r, 200));
    opened = ov && ov.classList.contains('show');
  }

  return { opened: !!opened, allOk: !!opened };
}
"""

# ---------------------------------------------------------------------------
# Sub-check 6 — hardLockFunctionsRemoved
# ---------------------------------------------------------------------------
CHECK_HARD_LOCK_FUNCTIONS_REMOVED = r"""
async () => {
  var gone = {
    _lwizInstallLock:    typeof _lwizInstallLock === 'undefined',
    _lwizAutoLiftLock:   typeof _lwizAutoLiftLock === 'undefined',
    _lwizCheckLiftLock:  typeof _lwizCheckLiftLock === 'undefined',
    _lwizWrapLiteSetTag: typeof _lwizWrapLiteSetTag === 'undefined',
    _lwizWrapUploadPdf:  typeof _lwizWrapUploadPdf === 'undefined',
    _lwizWrapLoadProto:  typeof _lwizWrapLoadProto === 'undefined'
  };
  var allGone = Object.keys(gone).every(function(k) { return gone[k]; });
  return Object.assign({}, gone, { allOk: allGone });
}
"""

# ---------------------------------------------------------------------------
# Sub-check 7 — keyboardNeverBlocked
# Wizard open manually, ZERO tagged pages -> 's' key must NOT be swallowed,
# and a single Esc (no selection) must close the wizard normally (no hard
# lock intercepting either).
# ---------------------------------------------------------------------------
CHECK_KEYBOARD_NEVER_BLOCKED = r"""
async () => {
  pageTags = {};
  caseId = 'test-mock';
  var ov = document.getElementById('ov');
  if (ov) ov.classList.remove('show');
  if (typeof openOv === 'function') openOv();
  await new Promise(r => setTimeout(r, 200));
  if (typeof _lovsSelected !== 'undefined') _lovsSelected.clear();

  var openBefore = ov && ov.classList.contains('show');
  var toolBefore = state.tool;

  // 's' key: with the hard lock gone, this must reach the app's normal
  // handlers (not be stopImmediatePropagation'd by a document-capture guard).
  document.dispatchEvent(new KeyboardEvent('keydown', {
    key: 's', bubbles: true, cancelable: true
  }));
  await new Promise(r => setTimeout(r, 150));
  var hintAfterS = document.getElementById('lwiz-hint');
  var hintShownForS = !!hintAfterS && hintAfterS.style.opacity !== '0';

  // Escape (no selection) -> closes normally, no lock veto.
  document.dispatchEvent(new KeyboardEvent('keydown', {
    key: 'Escape', bubbles: true, cancelable: true
  }));
  await new Promise(r => setTimeout(r, 150));
  var closedAfterEsc = ov && !ov.classList.contains('show');

  return {
    openBefore: !!openBefore,
    toolBefore: toolBefore,
    hintShownForS: hintShownForS,
    closedAfterEsc: !!closedAfterEsc,
    lockActive: window.__lwizAutoLockActive === true,
    allOk: !!openBefore && !hintShownForS && !!closedAfterEsc &&
           window.__lwizAutoLockActive !== true
  };
}
"""

# ---------------------------------------------------------------------------
# Sub-check 8 — loadProtoNoSideEffects
# ---------------------------------------------------------------------------
CHECK_LOAD_PROTO_NO_SIDE_EFFECTS = r"""
async () => {
  var ov = document.getElementById('ov');
  if (ov) ov.classList.remove('show');

  var minDoc = {
    version: 1,
    pageStore: {},
    pageTags: {},
    pageRotations: {},
    excludedPages: [],
    pageNames: {},
    pageFloorKind: {},
    pageFloorNum: {},
    projectInfo: {},
    liteGroups: [],
    liteLayers: []
  };

  var loadProtoExists = typeof loadProto === 'function';
  var threw = false;
  if (loadProtoExists) {
    try { loadProto(minDoc); } catch (e) { threw = true; }
  }

  caseId = 'test-mock';
  state.scaleStatus = 'unknown';
  state.scaleStatus = 'manual';
  await new Promise(r => setTimeout(r, 300));

  var wizardStillClosed = ov && !ov.classList.contains('show');

  return {
    loadProtoExists: loadProtoExists,
    threw: threw,
    wizardStillClosed: !!wizardStillClosed,
    allOk: loadProtoExists && !threw && !!wizardStillClosed
  };
}
"""

# ---------------------------------------------------------------------------
# Check list
# ---------------------------------------------------------------------------
CHECKS = [
    ("scriptInjected",             CHECK_SCRIPT_INJECTED,                 ["allOk"]),
    ("bootInstalledWatcher",       CHECK_BOOT_INSTALLED_WATCHER,          ["allOk"]),
    ("noAutoOpenOnUpload",         CHECK_NO_AUTO_OPEN_ON_UPLOAD,          ["allOk"]),
    ("noAutoOpenOnFirstScale",     CHECK_NO_AUTO_OPEN_ON_SCALE,           ["allOk"]),
    ("manualOpenStillWorks",       CHECK_MANUAL_OPEN_STILL_WORKS,         ["allOk"]),
    ("hardLockFunctionsRemoved",   CHECK_HARD_LOCK_FUNCTIONS_REMOVED,     ["allOk"]),
    ("keyboardNeverBlocked",       CHECK_KEYBOARD_NEVER_BLOCKED,          ["allOk"]),
    ("loadProtoNoSideEffects",     CHECK_LOAD_PROTO_NO_SIDE_EFFECTS,      ["allOk"]),
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
        print("LITE-WIZ-AUTO checks:")
        for name, scenario, required_keys in CHECKS:
            try:
                result = pg.evaluate(scenario)
            except Exception as ex:
                print(f"  {name:40s} -> EXCEPTION: {ex}")
                failures.append(f"check '{name}' threw: {ex}")
                continue

            ok = all(result.get(k) is True for k in required_keys)
            status = "PASS" if ok else "FAIL"
            print(f"  {name:40s} -> {status}  {result}")
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
        print(f"LITE_WIZ_AUTO_FAIL {passed}/{total}")
        sys.exit(1)
    else:
        print(f"LITE_WIZ_AUTO_OK {total}/{total}")


if __name__ == "__main__":
    main()
