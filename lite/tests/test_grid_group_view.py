"""
INV-2026-07-04-002 slice 3/4: Step-1 classify-grid view-toggle regression test.

Verifies the "เรียงตามหน้า <-> จัดกลุ่มตามแท็ก" verification view toggle
(lite/static/js/overview-grid.js): a runtime-only `_lovsViewMode` flag that
re-sorts the SAME tiles into tag-group buckets (with count headers) so
mis-tagged pages stand out visually. Click/select/chip/bulk-apply all keep
working identically in both modes. No native drag-and-drop exists on the
classify grid (`ltDndDecorate` is scoped to #catlist only) so nothing needed
disabling; the rubber-band multi-select is purely bounding-box math and is
unaffected by re-sorting.

5 sub-checks:
  toggleRebucketsWithCounts  toggle -> tiles land under correct tag headers with correct counts
  untaggedGroupLast          untagged pages bucket into "ยังไม่แท็ก", rendered as the LAST header, flagged
  chipTagRebucketsLive       cycling a tile's tag chip WHILE in grouped mode moves it to the new group immediately
  toggleBackExactOrder       toggle groups -> pages restores the EXACT original 1..N page order
  bulkApplyStillWorksGrouped Apply (with overlap-confirm) from grouped mode still routes through _lovsBulkApply

Emits LITE_GRID_GROUP_VIEW_OK on success.

    py -3 lite/tests/test_grid_group_view.py
"""
import socket, threading, time, sys
from pathlib import Path

LITE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LITE))
import uvicorn
from playwright.sync_api import sync_playwright


def _free_port(start=8540):
    for p in range(start, start + 60):
        with socket.socket() as s:
            if s.connect_ex(("127.0.0.1", p)) != 0:
                return p
    raise RuntimeError("no free port")


# ---------------------------------------------------------------------------
# Shared setup: 12 pages with a realistic tag mix, open the wizard once
# ---------------------------------------------------------------------------
SETUP_GLOBALS = r"""
async () => {
  await new Promise(r => setTimeout(r, 400));

  pageCount = 12;
  pageTags = {};
  pageFloorNum = {};
  pageFloorKind = {};
  excluded = {};
  pageNames = {};
  PS = {};
  for (var i = 1; i <= 12; i++) PS[i] = {objects: [], scale: null, annotations: []};

  // Realistic mix: 1=site, 2/3/4=floor(3,1,2 asc so sort is exercised), 5=plan,
  // 6=parking, 7=amenity, 8=detail, 9/10/11/12=untagged
  pageTags[1] = 'site';
  pageTags[2] = 'floor'; pageFloorKind[2] = 'normal'; pageFloorNum[2] = 3;
  pageTags[3] = 'floor'; pageFloorKind[3] = 'normal'; pageFloorNum[3] = 1;
  pageTags[4] = 'floor'; pageFloorKind[4] = 'normal'; pageFloorNum[4] = 2;
  pageTags[5] = 'plan';
  pageTags[6] = 'parking';
  pageTags[7] = 'amenity';
  pageTags[8] = 'detail';
  // 9,10,11,12 left untagged

  caseId = 'test-mock';
  openOv();
  await new Promise(r => setTimeout(r, 250));

  return {done: true};
}
"""

# ---------------------------------------------------------------------------
# Sub-check 1 — toggleRebucketsWithCounts
# ---------------------------------------------------------------------------
CHECK_REBUCKET_COUNTS = r"""
async () => {
  // Ensure pages mode + selection cleared first
  _lovsViewMode = 'pages'; _lovsSelected.clear();
  _lovsRenderClassify();
  await new Promise(r => setTimeout(r, 80));

  var toggleBtn = document.getElementById('btn-grid-view');
  var toggleFound = !!toggleBtn;
  if (toggleBtn) toggleBtn.click();
  await new Promise(r => setTimeout(r, 100));

  var isGroupsMode = _lovsViewMode === 'groups';
  var headers = document.querySelectorAll('#grid-classify .ov-group-header');
  var headerTexts = Array.prototype.map.call(headers, function(h) { return h.textContent.trim(); });

  // floor group should show count (3): pages 2,3,4
  var floorHeader = headerTexts.find(function(t) { return t.indexOf('แปลนชั้น') >= 0; });
  var floorHeaderHasCount3 = !!floorHeader && floorHeader.indexOf('(3)') >= 0;

  // site group count (1)
  var siteHeader = headerTexts.find(function(t) { return t.indexOf('ผังบริเวณ') >= 0; });
  var siteHeaderHasCount1 = !!siteHeader && siteHeader.indexOf('(1)') >= 0;

  // Every tile still present (12 total), no data lost
  var tileCount = document.querySelectorAll('#grid-classify .ov-tile').length;

  return {
    toggleFound: toggleFound, isGroupsMode: isGroupsMode,
    headerCount: headers.length, headerTexts: headerTexts,
    floorHeaderHasCount3: floorHeaderHasCount3, siteHeaderHasCount1: siteHeaderHasCount1,
    tileCount: tileCount,
    allOk: toggleFound && isGroupsMode && floorHeaderHasCount3 && siteHeaderHasCount1 && tileCount === 12
  };
}
"""

# ---------------------------------------------------------------------------
# Sub-check 2 — untaggedGroupLast
# ---------------------------------------------------------------------------
CHECK_UNTAGGED_LAST = r"""
async () => {
  // Already in groups mode from check 1; re-assert to be safe
  _lovsViewMode = 'groups';
  _lovsRenderClassify();
  await new Promise(r => setTimeout(r, 80));

  var headers = document.querySelectorAll('#grid-classify .ov-group-header');
  var lastHeader = headers[headers.length - 1];
  var lastIsUntagged = !!lastHeader && lastHeader.classList.contains('ov-group-untagged');
  var lastText = lastHeader ? lastHeader.textContent.trim() : '';
  var lastLabelOk = lastText.indexOf('ยังไม่แท็ก') >= 0;
  var lastCountOk = lastText.indexOf('(4)') >= 0; // pages 9,10,11,12

  // Untagged pages 9-12 should physically appear AFTER all tagged tiles in DOM order
  var allTiles = Array.prototype.slice.call(document.querySelectorAll('#grid-classify .ov-tile'));
  var lastFourPg = allTiles.slice(-4).map(function(t) { return +t.dataset.pg; }).sort(function(a,b){return a-b;});
  var untaggedAtEnd = JSON.stringify(lastFourPg) === JSON.stringify([9, 10, 11, 12]);

  return {
    headerCount: headers.length, lastIsUntagged: lastIsUntagged, lastText: lastText,
    lastLabelOk: lastLabelOk, lastCountOk: lastCountOk, untaggedAtEnd: untaggedAtEnd,
    allOk: lastIsUntagged && lastLabelOk && lastCountOk && untaggedAtEnd
  };
}
"""

# ---------------------------------------------------------------------------
# Sub-check 3 — chipTagRebucketsLive
# ---------------------------------------------------------------------------
CHECK_CHIP_REBUCKETS_LIVE = r"""
async () => {
  _lovsViewMode = 'groups'; _lovsSelected.clear();
  _lovsRenderClassify();
  await new Promise(r => setTimeout(r, 80));

  // Page 8 is 'detail'. Click its tag chip once: detail -> '' (cycle wraps to untagged,
  // since _LOVS_TAG_CYCLE = ['','site','floor','plan','parking','amenity','detail']).
  var tile8 = document.querySelector('#grid-classify .ov-tile[data-pg="8"]');
  var tile8FoundBefore = !!tile8;
  var chip8 = tile8 ? tile8.querySelector('.ov-tag-chip') : null;
  if (chip8) chip8.click();
  await new Promise(r => setTimeout(r, 100));

  var newTag = pageTags[8];
  var tagIsUntagged = newTag === '';

  // Page 8 should now be gone from the old "รายละเอียด/รูปด้าน" (detail) header's
  // page list and present in the "ยังไม่แท็ก" (untagged) group instead.
  var headers = document.querySelectorAll('#grid-classify .ov-group-header');
  var untaggedHeader = Array.prototype.find.call(headers, function(h) { return h.classList.contains('ov-group-untagged'); });
  var untaggedHeaderCount5 = !!untaggedHeader && untaggedHeader.textContent.indexOf('(5)') >= 0; // was 4, now 5

  // tile 8 must still exist (re-bucketed, not deleted) and NOT carry the old detail chip class
  var tile8After = document.querySelector('#grid-classify .ov-tile[data-pg="8"]');
  var tile8Exists = !!tile8After;
  var tile8ChipUntagged = tile8After ? tile8After.querySelector('.ov-tag-untagged') !== null : false;

  return {
    tile8FoundBefore: tile8FoundBefore, newTag: newTag, tagIsUntagged: tagIsUntagged,
    untaggedHeaderCount5: untaggedHeaderCount5, tile8Exists: tile8Exists, tile8ChipUntagged: tile8ChipUntagged,
    allOk: tile8FoundBefore && tagIsUntagged && untaggedHeaderCount5 && tile8Exists && tile8ChipUntagged
  };
}
"""

# ---------------------------------------------------------------------------
# Sub-check 4 — toggleBackExactOrder
# ---------------------------------------------------------------------------
CHECK_TOGGLE_BACK_EXACT = r"""
async () => {
  // Force back to pages mode and capture the canonical order
  _lovsViewMode = 'pages'; _lovsSelected.clear();
  _lovsRenderClassify();
  await new Promise(r => setTimeout(r, 80));
  var order1 = Array.prototype.map.call(
    document.querySelectorAll('#grid-classify .ov-tile'), function(t) { return +t.dataset.pg; }
  );

  // Toggle to groups then back to pages
  var toggleBtn = document.getElementById('btn-grid-view');
  if (toggleBtn) toggleBtn.click();  // -> groups
  await new Promise(r => setTimeout(r, 80));
  var inGroupsNow = _lovsViewMode === 'groups';
  var toggleBtn2 = document.getElementById('btn-grid-view');
  if (toggleBtn2) toggleBtn2.click(); // -> pages
  await new Promise(r => setTimeout(r, 80));

  var order2 = Array.prototype.map.call(
    document.querySelectorAll('#grid-classify .ov-tile'), function(t) { return +t.dataset.pg; }
  );
  var expected = [1,2,3,4,5,6,7,8,9,10,11,12];
  var order1Ok = JSON.stringify(order1) === JSON.stringify(expected);
  var order2Ok = JSON.stringify(order2) === JSON.stringify(expected);
  var noGroupHeadersLeft = document.querySelectorAll('#grid-classify .ov-group-header').length === 0;

  return {
    order1: order1, order2: order2, inGroupsNow: inGroupsNow,
    order1Ok: order1Ok, order2Ok: order2Ok, noGroupHeadersLeft: noGroupHeadersLeft,
    allOk: inGroupsNow && order1Ok && order2Ok && noGroupHeadersLeft
  };
}
"""

# ---------------------------------------------------------------------------
# Sub-check 5 — bulkApplyStillWorksGrouped (overlap-confirm flow, from grouped mode)
# ---------------------------------------------------------------------------
CHECK_BULK_APPLY_GROUPED = r"""
async () => {
  // Reset a clean 3-page target: 9 (untagged), 10 (untagged), 11 pre-tagged 'plan' -> overlap
  pageTags[9] = ''; pageTags[10] = ''; pageTags[11] = 'plan';
  delete pageFloorKind[9]; delete pageFloorKind[10]; delete pageFloorKind[11];
  delete pageFloorNum[9]; delete pageFloorNum[10]; delete pageFloorNum[11];

  _lovsViewMode = 'groups'; _lovsSelected.clear();
  _lovsRenderClassify();
  await new Promise(r => setTimeout(r, 100));
  var inGroupsMode = _lovsViewMode === 'groups';

  _lovsSelected.clear(); [9, 10, 11].forEach(function(p) { _lovsSelected.add(p); });
  _lovsRenderClassify();
  await new Promise(r => setTimeout(r, 80));

  var bk = document.getElementById('bulk-kind'); if (bk) bk.value = 'normal';
  var bs = document.getElementById('bulk-start'); if (bs) bs.value = '1';
  var applyBtn = document.getElementById('bulk-apply');
  var applyFound = !!applyBtn;
  if (applyBtn) applyBtn.click();
  await new Promise(r => setTimeout(r, 100));

  var confirmShown = !!document.getElementById('bulk-confirm-yes');
  var confirmYes = document.getElementById('bulk-confirm-yes');
  if (confirmYes) confirmYes.click();
  await new Promise(r => setTimeout(r, 100));

  var p9 = { tag: pageTags[9], num: pageFloorNum[9] };
  var p10 = { tag: pageTags[10], num: pageFloorNum[10] };
  var p11 = { tag: pageTags[11], num: pageFloorNum[11] };
  var appliedOk = p9.tag === 'floor' && p9.num === 1 &&
                  p10.tag === 'floor' && p10.num === 2 &&
                  p11.tag === 'floor' && p11.num === 3;

  return {
    inGroupsMode: inGroupsMode, applyFound: applyFound, confirmShown: confirmShown,
    p9: p9, p10: p10, p11: p11, appliedOk: appliedOk,
    allOk: inGroupsMode && applyFound && confirmShown && appliedOk
  };
}
"""

CHECKS = [
    ("toggleRebucketsWithCounts",  CHECK_REBUCKET_COUNTS,       ["allOk"]),
    ("untaggedGroupLast",          CHECK_UNTAGGED_LAST,         ["allOk"]),
    ("chipTagRebucketsLive",       CHECK_CHIP_REBUCKETS_LIVE,   ["allOk"]),
    ("toggleBackExactOrder",       CHECK_TOGGLE_BACK_EXACT,     ["allOk"]),
    ("bulkApplyStillWorksGrouped", CHECK_BULK_APPLY_GROUPED,    ["allOk"]),
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
        print("LITE-GRID-GROUP-VIEW checks:")
        for name, scenario, required_keys in CHECKS:
            try:
                result = pg.evaluate(scenario)
            except Exception as ex:
                print(f"  {name:28s} -> EXCEPTION: {ex}")
                failures.append(f"check '{name}' threw: {ex}")
                continue

            ok = all(result.get(k) is True for k in required_keys)
            status = "PASS" if ok else "FAIL"
            print(f"  {name:28s} -> {status}  {result}")
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
        print("LITE_GRID_GROUP_VIEW_FAIL")
        sys.exit(1)
    else:
        print("LITE_GRID_GROUP_VIEW_OK")


if __name__ == "__main__":
    main()
