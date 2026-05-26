"""
LFOC-ORDER-A: PF folder deterministic ordering regression guard.

Verifies that seedPageFolders (re-)assigns .order on PF folders so they render
in workflow order regardless of creation sequence.

Checks (4):
  siteFirst          PF_site has .order=0, appears first among PF folders
  floorsAscending    PF_floor_1.order < PF_floor_2.order < PF_floor_3.order
  roofAfterFloors    PF_floor_roof.order > PF_floor_3.order
  excludedLast       PF_excluded.order > all other PF folder .order values

Emits LITE_PF_ORDER_OK 4/4 on success.

    py -3 lite/tests/test_pf_folder_order.py
"""
import socket, threading, time, sys
from pathlib import Path

LITE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LITE))
import uvicorn
from playwright.sync_api import sync_playwright


def _free_port(start=8430):
    for p in range(start, start + 60):
        with socket.socket() as s:
            if s.connect_ex(("127.0.0.1", p)) != 0:
                return p
    raise RuntimeError("no free port")


# ---------------------------------------------------------------------------
# Scenario: pages tagged in REVERSE / arbitrary order so that creation order
# differs from logical workflow order.
#   p10 = floor#3  (first floor created)
#   p11 = site      (site created second)
#   p12 = floor#1   (floor#1 created third)
#   p13 = floor#2   (floor#2 created fourth)
#   p14 = roof      (roof created fifth)
#   p5, p6, p7 = untagged → PF_excluded
#
# Expected .order after seedPageFolders:
#   PF_site        → 0
#   PF_floor_1     → 20
#   PF_floor_2     → 30
#   PF_floor_3     → 40
#   PF_floor_roof  → 900
#   PF_excluded    → 9999
# ---------------------------------------------------------------------------
SCENARIO = r"""
() => {
  const out = {};

  /* Reset to 6 defaults, empty folders — in-place. */
  function reseed() {
    LAYERS.length  = 0;
    FOLDERS.length = 0;
    initLayers();
  }

  /* Arbitrary-order tags: floors tagged BEFORE site, out of numeric order */
  const mockTags  = {10:"floor", 11:"site", 12:"floor", 13:"floor", 14:"floor"};
  const mockFloors = {10:3, 12:1, 13:2, 14:"roof"};
  const allPages  = [5, 6, 7, 10, 11, 12, 13, 14];

  reseed();
  seedPageFolders(allPages, mockTags, mockFloors);

  /* Collect PF folders from FOLDERS (raw array, not sorted) */
  var pfFolders = FOLDERS.filter(function(f){ return f && f.kind === "page-folder"; });

  /* Build id→order map */
  var orderMap = {};
  pfFolders.forEach(function(f){ orderMap[f.id] = f.order; });

  /* -----------------------------------------------------------------------
     siteFirst: PF_site.order === 0 AND is the minimum order among all PF folders
     ----------------------------------------------------------------------- */
  var siteOrder = orderMap["PF_site"];
  var siteIsZero = siteOrder === 0;
  var siteIsMin  = pfFolders.every(function(f){ return f.order >= siteOrder; });
  out.siteFirst = siteIsZero && siteIsMin;

  /* -----------------------------------------------------------------------
     floorsAscending: PF_floor_1.order < PF_floor_2.order < PF_floor_3.order
     ----------------------------------------------------------------------- */
  var o1 = orderMap["PF_floor_1"];
  var o2 = orderMap["PF_floor_2"];
  var o3 = orderMap["PF_floor_3"];
  out.floorsAscending = (typeof o1 === "number" && typeof o2 === "number" && typeof o3 === "number")
                      && (o1 < o2) && (o2 < o3);

  /* -----------------------------------------------------------------------
     roofAfterFloors: PF_floor_roof.order > PF_floor_3.order
     ----------------------------------------------------------------------- */
  var oRoof = orderMap["PF_floor_roof"];
  out.roofAfterFloors = (typeof oRoof === "number" && typeof o3 === "number")
                      && (oRoof > o3);

  /* -----------------------------------------------------------------------
     excludedLast: PF_excluded.order > every other PF folder .order
     ----------------------------------------------------------------------- */
  var oExcl = orderMap["PF_excluded"];
  var otherPFs = pfFolders.filter(function(f){ return f.id !== "PF_excluded"; });
  out.excludedLast = (typeof oExcl === "number")
                   && otherPFs.every(function(f){ return oExcl > f.order; });

  /* -----------------------------------------------------------------------
     Bonus idempotent check: re-seeding does not change the .order values
     ----------------------------------------------------------------------- */
  var ordersBefore = JSON.stringify(pfFolders.map(function(f){ return {id:f.id, order:f.order}; }).sort(function(a,b){ return a.id < b.id ? -1 : 1; }));
  seedPageFolders(allPages, mockTags, mockFloors);
  var pfFolders2 = FOLDERS.filter(function(f){ return f && f.kind === "page-folder"; });
  var ordersAfter = JSON.stringify(pfFolders2.map(function(f){ return {id:f.id, order:f.order}; }).sort(function(a,b){ return a.id < b.id ? -1 : 1; }));
  out.idempotentOrder = (ordersBefore === ordersAfter);

  reseed();
  return out;
}
"""

CHECKS = [
    "siteFirst",
    "floorsAscending",
    "roofAfterFloors",
    "excludedLast",
]

BONUS_CHECKS = ["idempotentOrder"]


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
        result = pg.evaluate(SCENARIO)
        pg.close()
        b.close()

    server.should_exit = True
    time.sleep(0.4)

    for e in page_errors:
        print("  JS ERROR:", e)

    print()
    print("LFOC-ORDER-A checks:")
    passed = 0
    for k in CHECKS:
        ok = result.get(k)
        print(f"  {k:30s} -> {ok}")
        if ok is True:
            passed += 1
        else:
            failures.append(f"check '{k}' = {ok!r} (expected True)")

    # Bonus (informational — does not affect pass/fail)
    for k in BONUS_CHECKS:
        ok = result.get(k)
        print(f"  {k:30s} -> {ok}  (bonus)")

    total = len(CHECKS)
    print()
    if failures:
        for f in failures:
            print("FAIL:", f)
        print(f"LITE_PF_ORDER_FAIL {passed}/{total}")
        sys.exit(1)
    else:
        print(f"LITE_PF_ORDER_OK {passed}/{total}")


if __name__ == "__main__":
    main()
