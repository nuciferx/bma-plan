"""
INV-2026-07-04-002 slice 2/4: bulk-bar upgrade regression test.

Verifies the Step-1 classify-grid bulkbar's new floor auto-number "Apply"
control (lite/static/js/overview-grid.js): select a page range, pick a
kind + start number, Apply once -> tag + kind + running floor number for
every selected page. Special-kind pages (mezzanine/mechanical/rooftop)
consume no number; basement numbers DESCENDING (mirrors
overview-setup.js's _lovsSequentialFloor EXACTLY — this is the exact
convention an earlier invention spike got backwards, per opus review).
Overlap (any selected page already tagged) requires an inline confirm
bar (no window.confirm); cancel = zero mutations; the whole confirmed
batch is exactly ONE undo() away from the pre-Apply state.

5 sub-checks:
  bulkApplyAscending    11..16, kind=normal start=1 -> nums 1..6 (pure _lovsBulkResolveMap)
  bulkApplySkipsMezz    page 14 pre-set kind=mezzanine -> no num; 15 still gets 4 (not 5)
  bulkApplyBasementDesc 3 fresh pages, kind=basement -> descending 3,2,1;
                        cross-checked against the real Sequential (Y) button
                        (_lovsSequentialFloor) on the identical 3 pages
  overlapConfirmFlow    1/3 selected pages already tagged -> confirm bar shown;
                        cancel = deep-equal no-op; confirm = exact expected map
  singleUndoBatch       fresh 3-page Apply = exactly ONE undoStack push;
                        one undo() call fully restores pre-Apply state

Emits LITE_BULK_APPLY_OK on success.

    py -3 lite/tests/test_bulk_tag_apply.py
"""
import socket, threading, time, sys
from pathlib import Path

LITE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LITE))
import uvicorn
from playwright.sync_api import sync_playwright


def _free_port(start=8480):
    for p in range(start, start + 60):
        with socket.socket() as s:
            if s.connect_ex(("127.0.0.1", p)) != 0:
                return p
    raise RuntimeError("no free port")


# ---------------------------------------------------------------------------
# Shared setup: 20 pages (need room for an 11-16 range), open the wizard once
# ---------------------------------------------------------------------------
SETUP_GLOBALS = r"""
async () => {
  await new Promise(r => setTimeout(r, 400));

  pageCount = 20;
  pageTags = {};
  pageFloorNum = {};
  pageFloorKind = {};
  excluded = {};
  pageNames = {};
  PS = {};
  for (var i = 1; i <= 20; i++) PS[i] = {objects: [], scale: null, annotations: []};

  caseId = 'test-mock';
  openOv();
  await new Promise(r => setTimeout(r, 250));

  return {done: true};
}
"""

# ---------------------------------------------------------------------------
# Sub-check 1 — bulkApplyAscending (pure _lovsBulkResolveMap, 11..16 normal)
# ---------------------------------------------------------------------------
CHECK_ASCENDING = r"""
async () => {
  for (var i = 1; i <= 20; i++) { delete pageFloorKind[i]; delete pageFloorNum[i]; }
  var pages = [11, 12, 13, 14, 15, 16];
  var map = _lovsBulkResolveMap(pages, 'normal', 1);
  var nums = map.map(function(r) { return r.num; });
  var kinds = map.map(function(r) { return r.kind; });
  var expected = [1, 2, 3, 4, 5, 6];
  var numsOk = JSON.stringify(nums) === JSON.stringify(expected);
  var kindsOk = kinds.every(function(k) { return k === 'normal'; });
  return { nums: nums, kinds: kinds, numsOk: numsOk, kindsOk: kindsOk, allOk: numsOk && kindsOk };
}
"""

# ---------------------------------------------------------------------------
# Sub-check 2 — bulkApplySkipsMezz (page 14 pre-set mezzanine; 15 gets 4)
# ---------------------------------------------------------------------------
CHECK_SKIPS_MEZZ = r"""
async () => {
  for (var i = 1; i <= 20; i++) { delete pageFloorKind[i]; delete pageFloorNum[i]; }
  pageFloorKind[14] = 'mezzanine';
  var pages = [11, 12, 13, 14, 15, 16];
  var map = _lovsBulkResolveMap(pages, 'normal', 1);
  var byPage = {}; map.forEach(function(r) { byPage[r.p] = r; });
  var p11 = byPage[11], p14 = byPage[14], p15 = byPage[15];
  var mezzNoNum = p14.kind === 'mezzanine' && p14.num === null;
  var p15Gets4 = p15.num === 4;
  var p11Gets1 = p11.num === 1;
  return {
    p14: p14, p15: p15, mezzNoNum: mezzNoNum, p15Gets4: p15Gets4, p11Gets1: p11Gets1,
    allOk: mezzNoNum && p15Gets4 && p11Gets1
  };
}
"""

# ---------------------------------------------------------------------------
# Sub-check 3 — bulkApplyBasementDesc (3 fresh pages, descending 3,2,1;
# cross-checked against the real Sequential button on the identical pages)
# ---------------------------------------------------------------------------
CHECK_BASEMENT_DESC = r"""
async () => {
  for (var i = 1; i <= 20; i++) { pageTags[i] = ''; delete pageFloorKind[i]; delete pageFloorNum[i]; }

  var pages = [1, 2, 3];
  var map = _lovsBulkResolveMap(pages, 'basement', 1);
  var byPage = {}; map.forEach(function(r) { byPage[r.p] = r; });
  var bulkNums = [byPage[1].num, byPage[2].num, byPage[3].num];
  var bulkExpected = [3, 2, 1];
  var bulkOk = JSON.stringify(bulkNums) === JSON.stringify(bulkExpected);

  // Cross-check vs the real Sequential (Y) button convention (_lovsSequentialFloor,
  // overview-setup.js) on the SAME 3 pages, same kind, same start.
  pageTags[1] = 'floor'; pageFloorKind[1] = 'basement'; delete pageFloorNum[1];
  pageTags[2] = 'floor'; pageFloorKind[2] = 'basement'; delete pageFloorNum[2];
  pageTags[3] = 'floor'; pageFloorKind[3] = 'basement'; delete pageFloorNum[3];

  var step2 = document.querySelector('#ov-steps .step[data-step="2"]');
  if (step2) step2.click();
  await new Promise(r => setTimeout(r, 150));
  var seqStart = document.getElementById('seq-start'); if (seqStart) seqStart.value = '1';
  var seqBtn = document.getElementById('ov-seq');
  if (seqBtn) seqBtn.click();
  await new Promise(r => setTimeout(r, 120));

  var seqNums = [pageFloorNum[1], pageFloorNum[2], pageFloorNum[3]];
  var seqMatchesBulk = JSON.stringify(seqNums) === JSON.stringify(bulkExpected);

  // back to step 1 for subsequent checks
  var step1 = document.querySelector('#ov-steps .step[data-step="1"]');
  if (step1) { step1.click(); await new Promise(r => setTimeout(r, 100)); }

  return {
    bulkNums: bulkNums, bulkExpected: bulkExpected, bulkOk: bulkOk,
    seqNums: seqNums, seqMatchesBulk: seqMatchesBulk,
    allOk: bulkOk && seqMatchesBulk
  };
}
"""

# ---------------------------------------------------------------------------
# Sub-check 4 — overlapConfirmFlow (1/3 pages already tagged -> confirm bar;
# cancel = no-op; confirm = exact map)
# ---------------------------------------------------------------------------
CHECK_OVERLAP_CONFIRM = r"""
async () => {
  for (var i = 1; i <= 20; i++) { pageTags[i] = ''; delete pageFloorKind[i]; delete pageFloorNum[i]; }
  var step1 = document.querySelector('#ov-steps .step[data-step="1"]');
  if (step1) { step1.click(); await new Promise(r => setTimeout(r, 100)); }

  pageTags[5] = 'site';  // page 5 pre-tagged with a DIFFERENT tag -> overlap
  _lovsRenderClassify();
  await new Promise(r => setTimeout(r, 80));

  var snapBefore = JSON.stringify({ tags: pageTags, kind: pageFloorKind, num: pageFloorNum });

  _lovsSelected.clear(); [4, 5, 6].forEach(function(p) { _lovsSelected.add(p); });
  _lovsRenderClassify();
  await new Promise(r => setTimeout(r, 80));

  var bk = document.getElementById('bulk-kind'); if (bk) bk.value = 'normal';
  var bs = document.getElementById('bulk-start'); if (bs) bs.value = '1';
  var applyBtn = document.getElementById('bulk-apply');
  var applyFound = !!applyBtn;
  if (applyBtn) applyBtn.click();
  await new Promise(r => setTimeout(r, 100));

  var confirmShown = !!document.getElementById('bulk-confirm-yes');

  // -- CANCEL path: must be a total no-op --
  var cancelBtn = document.getElementById('bulk-confirm-no');
  if (cancelBtn) cancelBtn.click();
  await new Promise(r => setTimeout(r, 80));
  var snapAfterCancel = JSON.stringify({ tags: pageTags, kind: pageFloorKind, num: pageFloorNum });
  var cancelIsNoOp = snapAfterCancel === snapBefore;

  // -- re-trigger, this time CONFIRM --
  _lovsSelected.clear(); [4, 5, 6].forEach(function(p) { _lovsSelected.add(p); });
  _lovsRenderClassify();
  await new Promise(r => setTimeout(r, 80));
  var bk2 = document.getElementById('bulk-kind'); if (bk2) bk2.value = 'normal';
  var bs2 = document.getElementById('bulk-start'); if (bs2) bs2.value = '1';
  var applyBtn2 = document.getElementById('bulk-apply');
  if (applyBtn2) applyBtn2.click();
  await new Promise(r => setTimeout(r, 100));
  var confirmYes = document.getElementById('bulk-confirm-yes');
  if (confirmYes) confirmYes.click();
  await new Promise(r => setTimeout(r, 100));

  var p4 = { tag: pageTags[4], num: pageFloorNum[4] };
  var p5 = { tag: pageTags[5], num: pageFloorNum[5] };
  var p6 = { tag: pageTags[6], num: pageFloorNum[6] };
  var confirmApplied = p4.tag === 'floor' && p4.num === 1 &&
                        p5.tag === 'floor' && p5.num === 2 &&
                        p6.tag === 'floor' && p6.num === 3;

  return {
    applyFound: applyFound, confirmShown: confirmShown, cancelIsNoOp: cancelIsNoOp,
    p4: p4, p5: p5, p6: p6, confirmApplied: confirmApplied,
    allOk: applyFound && confirmShown && cancelIsNoOp && confirmApplied
  };
}
"""

# ---------------------------------------------------------------------------
# Sub-check 5 — singleUndoBatch (fresh 3-page Apply = ONE undoStack push;
# one undo() restores everything)
# ---------------------------------------------------------------------------
CHECK_SINGLE_UNDO = r"""
async () => {
  for (var i = 1; i <= 20; i++) { pageTags[i] = ''; delete pageFloorKind[i]; delete pageFloorNum[i]; }
  _lovsRenderClassify();
  await new Promise(r => setTimeout(r, 80));

  var snapBefore = JSON.stringify({ tags: pageTags, kind: pageFloorKind, num: pageFloorNum });
  var undoStackBefore = (typeof undoStack !== 'undefined') ? undoStack.length : null;

  _lovsSelected.clear(); [8, 9, 10].forEach(function(p) { _lovsSelected.add(p); });
  _lovsRenderClassify();
  await new Promise(r => setTimeout(r, 80));
  var bk = document.getElementById('bulk-kind'); if (bk) bk.value = 'normal';
  var bs = document.getElementById('bulk-start'); if (bs) bs.value = '1';
  var applyBtn = document.getElementById('bulk-apply');
  if (applyBtn) applyBtn.click();
  await new Promise(r => setTimeout(r, 100));

  // 8/9/10 are all fresh (no overlap) -> commits immediately, no confirm bar
  var noConfirmNeeded = !document.getElementById('bulk-confirm-yes');
  var undoStackAfter = (typeof undoStack !== 'undefined') ? undoStack.length : null;
  var pushedExactlyOne = (undoStackAfter === undoStackBefore + 1);

  var appliedOk = pageTags[8] === 'floor' && pageTags[9] === 'floor' && pageTags[10] === 'floor' &&
                  pageFloorNum[8] === 1 && pageFloorNum[9] === 2 && pageFloorNum[10] === 3;

  if (typeof undo === 'function') undo();
  await new Promise(r => setTimeout(r, 80));

  var snapAfterUndo = JSON.stringify({ tags: pageTags, kind: pageFloorKind, num: pageFloorNum });
  var undoRestoredExactly = snapAfterUndo === snapBefore;

  return {
    noConfirmNeeded: noConfirmNeeded, pushedExactlyOne: pushedExactlyOne,
    appliedOk: appliedOk, undoRestoredExactly: undoRestoredExactly,
    undoStackBefore: undoStackBefore, undoStackAfter: undoStackAfter,
    allOk: noConfirmNeeded && pushedExactlyOne && appliedOk && undoRestoredExactly
  };
}
"""

CHECKS = [
    ("bulkApplyAscending",    CHECK_ASCENDING,        ["allOk"]),
    ("bulkApplySkipsMezz",    CHECK_SKIPS_MEZZ,       ["allOk"]),
    ("bulkApplyBasementDesc", CHECK_BASEMENT_DESC,    ["allOk"]),
    ("overlapConfirmFlow",    CHECK_OVERLAP_CONFIRM,  ["allOk"]),
    ("singleUndoBatch",       CHECK_SINGLE_UNDO,      ["allOk"]),
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
        time.sleep(2.0)  # allow dynamic script load + setTimeout bootstrap

        try:
            pg.evaluate(SETUP_GLOBALS)
        except Exception as ex:
            print(f"  SETUP FAILED: {ex}")
            failures.append(f"setup threw: {ex}")

        print()
        print("LITE-BULK-TAG-APPLY checks:")
        for name, scenario, required_keys in CHECKS:
            try:
                result = pg.evaluate(scenario)
            except Exception as ex:
                print(f"  {name:24s} -> EXCEPTION: {ex}")
                failures.append(f"check '{name}' threw: {ex}")
                continue

            ok = all(result.get(k) is True for k in required_keys)
            status = "PASS" if ok else "FAIL"
            print(f"  {name:24s} -> {status}  {result}")
            if not ok:
                bad = [k for k in required_keys if result.get(k) is not True]
                failures.append(f"check '{name}' failed keys: {bad}  result={result}")

        pg.close()
        b.close()

    for e in page_errors:
        print("  JS ERROR:", e)

    server.should_exit = True
    time.sleep(0.4)

    if failures:
        for f in failures:
            print("FAIL:", f)
        print("LITE_BULK_APPLY_FAIL")
        sys.exit(1)
    else:
        print("LITE_BULK_APPLY_OK")


if __name__ == "__main__":
    main()
