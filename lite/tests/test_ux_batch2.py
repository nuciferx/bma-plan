"""
UX batch 2 regression guard (UX-20260703-review-findings, PHASE_INDEX row 63).

Covers the six UX-batch-2 findings implemented in lite/:

  F-4  scale-verified badge visible in HUD after Verify Scale accept
       (PS[pg].scale.verifyResult present -> green "✓✓ ยืนยันแล้ว" marker;
        absent when unverified). Display-only; state already persists.
  F-6  misleading "เปิด PDF ก่อน" alert during background upload — with a
       local doc open (pdfDoc set) but caseId still null, server-gated actions
       show the upload-in-progress message instead. Original message when
       nothing is open at all.
  F-9  verify-scale uses window.prompt -> replaced with an in-app modal
       (assert no window.prompt call; assert #vs-input-modal opens).
  seeded-vars  report vars whose expr errors ONLY because referenced role/
       layer totals are empty render neutral "รอข้อมูล" (dim) not red;
       a genuinely malformed expr (unknown ref) stays red.
  wizard-next-gate  UPDATED (INV-2026-07-04-002 slice 4/4): the SET gate this
       check used to verify (Step 1 Next blocked at 0 tags via window.confirm)
       was REMOVED and replaced by a per-page JIT tag gate on the measure
       tools themselves (tag-jit.js, see test_tag_jit.py). This check now
       asserts the gate is GONE: Next always proceeds, 0 tags or not, and
       never calls window.confirm.

F-5 (wizard mousedown/click hint) is NOT auto-tested here: reproducing it
needs the LWIZ hard-block lock, which is installed only on a REAL PDF upload
completing (uploadPdf wrap in wiz-auto.js). That path is not headless-feasible
without a live upload + wizard auto-fire. The code change is a 1-line extension
of the existing keydown hint to also fire on 'mousedown' in wiz-auto.js
(_lwizInstallLock handler). MANUAL REPRO: upload a PDF -> wizard auto-opens and
locks the canvas -> click anywhere OUTSIDE #ov-panel -> the orange
"ตั้งค่าหน้า (Page Setup) ให้เสร็จก่อน" hint must flash (previously it flashed
only on keypress, leaving mouse clicks blocked silently).

Emits LITE_UX_BATCH2_OK on success.

    py -3 lite/tests/test_ux_batch2.py
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
# F-4 — verifiedBadgeVisibleInHud
# ---------------------------------------------------------------------------
F4_BADGE = r"""
() => {
  var _P = 91;
  PS = {}; PS[_P] = {objects:[], scale:{pts_per_m:10}, annotations:[]};
  curPage = _P; caseId = 'test';
  updateHUD();
  var htmlUnver = document.getElementById('hud-tl').innerHTML;
  var unverifiedNoBadge = htmlUnver.indexOf('ยืนยันแล้ว') === -1;
  // simulate an accepted verifyResult (verify-scale.js writes {pct,action,...})
  PS[_P].scale.verifyResult = {accepted:true, action:'accept', pct:0.2, verifyPts_per_m:10, ts:Date.now()};
  updateHUD();
  var htmlVer = document.getElementById('hud-tl').innerHTML;
  var verifiedHasBadge = htmlVer.indexOf('ยืนยันแล้ว') !== -1 && htmlVer.indexOf('hud-verified') !== -1;
  caseId = null;
  return {unverifiedNoBadge, verifiedHasBadge, pass: unverifiedNoBadge && verifiedHasBadge};
}
"""

# ---------------------------------------------------------------------------
# F-6 — uploadPendingMessageSwap
# ---------------------------------------------------------------------------
F6_MSG = r"""
() => {
  var msgs = [];
  var _oa = window.alert; window.alert = function(m){ msgs.push(m); };

  // (a) nothing open at all -> original message
  caseId = null; pdfDoc = null;
  var msgNothingOpen = gateNoCaseMsg();

  // (b) local doc open, upload pending (caseId null, pdfDoc set) -> uploading msg
  pdfDoc = {numPages:3};
  var msgUploading = gateNoCaseMsg();
  var hasDocOk = typeof PageRenderer.hasDoc === 'function' && PageRenderer.hasDoc() === true;

  // (c) a server-gated action shows the uploading message, not the old alert
  caseId = null; pdfDoc = {numPages:3};
  try { exportXlsx(); } catch(e) {}
  var gatedMsg = msgs.length ? msgs[msgs.length-1] : null;

  window.alert = _oa; pdfDoc = null;

  var nothingOk   = msgNothingOpen === 'เปิด PDF ก่อน';
  var uploadingOk = typeof msgUploading === 'string' && msgUploading.indexOf('กำลังอัปโหลด') === 0;
  var gatedOk     = !!gatedMsg && gatedMsg.indexOf('กำลังอัปโหลด') === 0;
  return {msgNothingOpen, msgUploading, gatedMsg, nothingOk, uploadingOk, gatedOk, hasDocOk,
          pass: nothingOk && uploadingOk && gatedOk && hasDocOk};
}
"""

# ---------------------------------------------------------------------------
# F-9 — verifyUsesInAppModalNotPrompt
# ---------------------------------------------------------------------------
F9_MODAL = r"""
() => {
  var _P = 92;
  PS = {}; PS[_P] = {objects:[], scale:{pts_per_m:10}, annotations:[]};
  curPage = _P; caseId = 'test';
  var promptUsed = false; var _op = window.prompt;
  window.prompt = function(){ promptUsed = true; throw new Error('window.prompt used'); };
  state.draft = [{x:0,y:0},{x:100,y:0}];
  state.verifyMode = true;
  var threw = false;
  try { VerifyScale.onTwoPoints(); } catch(e){ threw = true; }
  window.prompt = _op;
  var modal = document.getElementById('vs-input-modal');
  var modalShown = !!modal && modal.style.display === 'flex';
  var inputExists = !!document.getElementById('vs-input-m');
  // covered by modalOpen() guard so digit-typing doesn't switch tools
  var guardCovers = typeof modalOpen === 'function' && modalOpen() === true;
  caseId = null;
  return {promptUsed, threw, modalShown, inputExists, guardCovers,
          pass: !promptUsed && !threw && modalShown && inputExists && guardCovers};
}
"""

# ---------------------------------------------------------------------------
# seeded-vars — emptyRefsRenderWaitingNotRed
# ---------------------------------------------------------------------------
SEED_WAIT = r"""
() => {
  seedReportVars();  // idempotent: v_net (gfa-ded), v_osr (open/site*100), v_far (gfa/site)
  var bad = addReportVar('มั่ว'); bad.expr = [{ref:'__nonexistent__'}];  // genuinely malformed
  var host = document.createElement('div'); document.body.appendChild(host);
  renderReportVarsEditor(host, {});   // empty agg -> no measured data yet
  var waits = host.querySelectorAll('.rv-wait').length;
  var errs  = host.querySelectorAll('.rv-err').length;
  var firstWait = host.querySelector('.rv-wait');
  var waitText = firstWait ? firstWait.textContent : '';
  var badRow = null;
  // the malformed var must be a red error, not waiting
  var badCls = classifyReportVarErr({expr: bad.expr, err: 'อ้างตัวแปรไม่พบ'}, {});
  host.remove();
  var seededWaitOk = waits >= 3;                 // 3 seeded presets all waiting
  var badErrOk = errs >= 1 && badCls === 'err';  // malformed stays red
  var waitTextOk = waitText.indexOf('รอข้อมูล') >= 0;
  return {waits, errs, waitText, badCls, seededWaitOk, badErrOk, waitTextOk,
          pass: seededWaitOk && badErrOk && waitTextOk};
}
"""

# ---------------------------------------------------------------------------
# wizard-next-gate — nextBlockedAtZeroTags
# ---------------------------------------------------------------------------
WIZ_GATE = r"""
() => {
  // INV-2026-07-04-002 slice 4/4: SET gate removed — Next must proceed
  // unconditionally now, 0 tags or not, and never touch window.confirm.
  caseId = 'test';
  pageCount = 3;
  pageTags = {};
  excluded = {};
  if (typeof openOv !== 'function') return {pass:false, err:'openOv missing'};
  openOv();
  var startStep = _lovsCurStep;
  var next = document.getElementById('ov-next');
  if (!next) return {pass:false, err:'ov-next missing'};

  var _oc = window.confirm; var confirmCalls = 0;
  window.confirm = function(){ confirmCalls++; return false; };

  // 0 tagged -> Next proceeds immediately, no confirm
  next.click();
  var stepAfterZeroTags = _lovsCurStep;

  // back to step 1, tag a page -> still no confirm, still proceeds
  _lovsGoStep(1);
  pageTags = {1:'site'};
  next.click();
  var stepWithTag = _lovsCurStep;

  window.confirm = _oc;
  caseId = null;
  return {startStep, stepAfterZeroTags, stepWithTag, confirmCalls,
          pass: startStep===1 && stepAfterZeroTags===2 && stepWithTag===2 && confirmCalls===0};
}
"""


CHECKS = [
    ("F4_verifiedBadgeVisibleInHud",       F4_BADGE,  ["pass"]),
    ("F6_uploadPendingMessageSwap",        F6_MSG,    ["pass"]),
    ("F9_verifyUsesInAppModalNotPrompt",   F9_MODAL,  ["pass"]),
    ("seed_emptyRefsRenderWaitingNotRed",  SEED_WAIT, ["pass"]),
    ("wiz_nextNeverBlocksNow_slice4",      WIZ_GATE,  ["pass"]),
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
        pg.goto(f"http://127.0.0.1:{port}/", wait_until="networkidle")
        time.sleep(0.6)

        print()
        print("UX-BATCH2 checks:")
        for name, scenario, required_keys in CHECKS:
            pg.reload(wait_until="networkidle")
            time.sleep(0.4)
            try:
                result = pg.evaluate(scenario)
            except Exception as ex:
                print(f"  {name:38s} -> EXCEPTION: {ex}")
                failures.append(f"check '{name}' threw: {ex}")
                continue
            ok = all(result.get(k) is True for k in required_keys)
            status = "PASS" if ok else "FAIL"
            print(f"  {name:38s} -> {status}  {result}")
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
        print("LITE_UX_BATCH2_FAIL")
        sys.exit(1)
    else:
        print("LITE_UX_BATCH2_OK")


if __name__ == "__main__":
    main()
