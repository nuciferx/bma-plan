"""
UX batch 3 regression guard (UX-20260703-review-findings — remaining FRICTION
F-8 + COSMETIC set).

Covers the five UX-batch-3 items implemented in lite/:

  F-8         raw error alerts gain a one-line actionable Thai next step.
              Two easily-triggered messages are asserted: the Set-Scale distance
              validation ("ใส่ระยะเป็นตัวเลขมากกว่า 0" + "เมตร" hint) and the
              Save-with-no-PDF gate ("ยังไม่ได้เปิด PDF" + "Ctrl+O" hint).
  COSMETIC-1  the 7 annotate tools get Shift+<letter> hotkeys wired through the
              SAME central keydown path (input guard + modalOpen guard). Shift+T
              → ann_text, Shift+A → ann_arrow (must NOT fall through to the poly
              'A' handler), Shift+H → ann_highlight (must NOT toggle pan). Typing
              in an input, or with a modal open, must NOT switch tool.
  COSMETIC-3  pre-open dim empty-state hint on the layer panel (#ls-empty-state);
              visible before any PDF, gone after a real uploadPdf() open.
  COSMETIC-4  per-page scanned/fallback HUD badge (#scan-badge): visible on a
              page flagged scanned, hidden after switching to a clean page.
  COSMETIC-2  Page Manager + wizard strings translated to Thai (no residual
              "Step"/"Manage Pages"/"Classify" English in the visible chrome).

Emits LITE_UX_BATCH3_OK on success.

    py -3 lite/tests/test_ux_batch3.py
"""
import socket, threading, time, sys, io
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

LITE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LITE))
import fitz
import uvicorn
from playwright.sync_api import sync_playwright


def _free_port(start=8590):
    for p in range(start, start + 60):
        with socket.socket() as s:
            if s.connect_ex(("127.0.0.1", p)) != 0:
                return p
    raise RuntimeError("no free port")


def _make_pdf_bytes(pages=1, w=300, h=400):
    doc = fitz.open()
    for i in range(pages):
        pg = doc.new_page(width=w, height=h)
        pg.insert_text(fitz.Point(70, 200), f"UXB3 {i+1}", fontsize=28)
    b = doc.tobytes()
    doc.close()
    return b


# ---------------------------------------------------------------------------
# F-8 — actionableErrorMessages
# ---------------------------------------------------------------------------
F8_MSGS = r"""
() => {
  var msgs = []; var _oa = window.alert; window.alert = function(m){ msgs.push(String(m)); };

  // (a) Set-Scale distance validation — empty input
  state.calib = {pts:[{x:0,y:0},{x:10,y:0}], ptDist:10};
  document.getElementById("cal-m").value = "";
  try { document.getElementById("cal-ok").onclick(); } catch(e) {}
  var m1 = msgs.length ? msgs[msgs.length-1] : "";

  // (b) Save with no case open
  caseId = null;
  try { document.getElementById("mi-save").onclick(); } catch(e) {}
  var m2 = msgs.length ? msgs[msgs.length-1] : "";

  window.alert = _oa;

  var scaleHasStep = m1.indexOf("ใส่ระยะเป็นตัวเลขมากกว่า 0") >= 0 &&
                     m1.indexOf("\n") >= 0 && m1.indexOf("เมตร") >= 0;
  var saveHasStep  = m2.indexOf("ยังไม่ได้เปิด PDF") >= 0 &&
                     m2.indexOf("\n") >= 0 && m2.indexOf("Ctrl+O") >= 0;
  return {m1, m2, scaleHasStep, saveHasStep, pass: scaleHasStep && saveHasStep};
}
"""

# ---------------------------------------------------------------------------
# COSMETIC-1 — annotateHotkeysGuarded
# ---------------------------------------------------------------------------
HOTKEYS = r"""
() => {
  function press(el, key){ el.dispatchEvent(new KeyboardEvent("keydown",{key:key,shiftKey:true,bubbles:true})); }

  // Shift+T -> ann_text
  setTool("select"); press(window, "T"); var afterT = state.tool;
  // Shift+A -> ann_arrow (NOT poly, which owns bare/upper 'A')
  setTool("select"); press(window, "A"); var afterA = state.tool;
  // Shift+H -> ann_highlight (must NOT toggle pan tool)
  setTool("select"); var panBefore = state.panTool; press(window, "H");
  var afterH = state.tool; var panAfter = state.panTool;

  // Guard 1: typing Shift+C inside an <input> must NOT switch tool
  setTool("select");
  var inp = document.getElementById("cal-m"); inp.focus();
  press(inp, "C");
  var afterInput = state.tool; inp.blur();

  // Guard 2: a modal open must NOT switch tool
  setTool("select");
  document.getElementById("modal").classList.add("show");
  press(window, "R");
  var afterModal = state.tool;
  document.getElementById("modal").classList.remove("show");

  return {afterT, afterA, afterH, panBefore, panAfter, afterInput, afterModal,
          pass: afterT==="ann_text" && afterA==="ann_arrow" && afterH==="ann_highlight" &&
                panAfter===panBefore && afterInput==="select" && afterModal==="select"};
}
"""

# ---------------------------------------------------------------------------
# COSMETIC-3 — emptyStatePreAndPostOpen  (real uploadPdf)
# ---------------------------------------------------------------------------
EMPTY_STATE = r"""
async () => {
  updateEmptyState();
  var ov = document.getElementById("ls-empty-state");
  var preVisible = !!ov && ov.style.display !== "none" &&
                   window.getComputedStyle(ov).display !== "none";
  var textOk = !!ov && ov.textContent.indexOf("เปิดไฟล์ PDF เพื่อเริ่ม") >= 0 &&
               ov.textContent.indexOf("Ctrl+O") >= 0;

  var bytes = new Uint8Array(%PDF_BYTES%);
  var file = new File([bytes], "uxb3-open.pdf", {type:"application/pdf"});
  await uploadPdf(file);
  await new Promise(function(r){ setTimeout(r, 700); });
  updateEmptyState();

  var ov2 = document.getElementById("ls-empty-state");
  var postHidden = !ov2 || ov2.style.display === "none";
  return {preVisible, textOk, postHidden, docOpen: !!pdfDoc,
          pass: preVisible && textOk && postHidden};
}
"""

# ---------------------------------------------------------------------------
# COSMETIC-4 — scannedBadgeFollowsPage
# ---------------------------------------------------------------------------
SCAN_BADGE = r"""
() => {
  // mark page 5 scanned, page 6 clean, via the live _scanned map
  curPage = 5;
  PageRenderer._test_scanned()[5] = true;
  PageRenderer._test_scanned()[6] = false;
  updateScanBadge();
  var badge = document.getElementById("scan-badge");
  var shownScanned = !!badge && badge.style.display !== "none" &&
                     badge.textContent.indexOf("สแกน") >= 0;

  // switch to a clean page -> badge hides
  curPage = 6;
  updateScanBadge();
  var hiddenOnClean = !!badge && badge.style.display === "none";

  return {shownScanned, hiddenOnClean, txt: badge ? badge.textContent : null,
          pass: shownScanned && hiddenOnClean};
}
"""

# ---------------------------------------------------------------------------
# COSMETIC-2 — thaiStrings (Page Manager + wizard)
# ---------------------------------------------------------------------------
THAI = r"""
() => {
  // ---- wizard ----
  caseId = 'test'; pageCount = 3; pageTags = {}; excluded = {};
  if (typeof openOv === 'function') openOv();
  var prog  = document.getElementById('ov-prog');
  var step1 = document.querySelector('#ov-steps .step[data-step="1"] b');
  var step2 = document.querySelector('#ov-steps .step[data-step="2"] b');
  var progThai  = !!prog  && prog.textContent.indexOf('ขั้นที่') >= 0 && prog.textContent.indexOf('Step') < 0;
  var step1Thai = !!step1 && step1.textContent === 'จัดหมวดหน้า';
  var step2Thai = !!step2 && step2.textContent === 'เรียงชั้น';

  // ---- page manager (stub pageMgr so overlay + action bar build) ----
  pageMgr = {count:function(){return 1;}, serverNum:function(n){return n;}, pending:[], undoStack:[]};
  if (typeof pmOpenManager === 'function') { try { pmOpenManager(); } catch(e) {} }
  var h3    = document.querySelector('#pm-header h3');
  var merge = document.getElementById('pmui-merge');
  var pmHdrThai   = !!h3 && h3.textContent === 'จัดการหน้า' && h3.textContent.indexOf('Manage Pages') < 0;
  var pmMergeThai = !!merge && merge.textContent.indexOf('รวมไฟล์') >= 0 && merge.textContent.indexOf('Merge') < 0;

  var pm = document.getElementById('pm-overlay'); if (pm) pm.classList.remove('show');
  caseId = null;
  return {progThai, step1Thai, step2Thai, pmHdrThai, pmMergeThai,
          pass: progThai && step1Thai && step2Thai && pmHdrThai && pmMergeThai};
}
"""


def _build_checks(pdf_bytes):
    pdf_arr = "[" + ",".join(str(b) for b in pdf_bytes) + "]"
    return [
        ("F8_actionableErrorMessages",   F8_MSGS,                                   ["pass"]),
        ("cos1_annotateHotkeysGuarded",  HOTKEYS,                                   ["pass"]),
        ("cos3_emptyStatePreAndPost",    EMPTY_STATE.replace("%PDF_BYTES%", pdf_arr), ["pass"]),
        ("cos4_scannedBadgeFollowsPage", SCAN_BADGE,                                ["pass"]),
        ("cos2_thaiStrings",             THAI,                                      ["pass"]),
    ]


def main():
    from server_lite import app as lite_app
    port = _free_port()
    cfg = uvicorn.Config(lite_app, host="127.0.0.1", port=port, log_level="error")
    server = uvicorn.Server(cfg)
    threading.Thread(target=server.run, daemon=True).start()
    time.sleep(2.0)

    checks = _build_checks(_make_pdf_bytes())

    failures = []
    page_errors = []

    with sync_playwright() as pw:
        b = pw.chromium.launch()
        pg = b.new_page()
        pg.on("pageerror", lambda e: page_errors.append(f"pageerror: {e}"))
        pg.goto(f"http://127.0.0.1:{port}/", wait_until="networkidle")
        time.sleep(0.6)

        print()
        print("UX-BATCH3 checks:")
        for name, scenario, required_keys in checks:
            pg.reload(wait_until="networkidle")
            time.sleep(0.4)
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

        pg.close()
        b.close()

    for e in page_errors:
        print("  JS ERROR:", e)
        failures.append(e)

    server.should_exit = True
    time.sleep(0.4)

    if failures:
        for f in failures:
            print("FAIL:", f)
        print("LITE_UX_BATCH3_FAIL")
        sys.exit(1)
    else:
        print("LITE_UX_BATCH3_OK")


if __name__ == "__main__":
    main()
