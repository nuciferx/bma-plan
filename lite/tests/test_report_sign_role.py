"""
LITE sprint A-1: custom deduction layer sign fix (review row A-7).

Bug: buildReportPayload() used c.id==="ded" to pick sign=-1.
     Built-in ded layer (id==="ded") worked; custom ded layers (id like
     "L5", role==="ded") got sign=+1 → area ADDED instead of subtracted.

Fix: change to c.role==="ded".

This test proves:
  1. Custom ded layer (id="L5", role="ded") produces sign=-1 in its group.
  2. net = gfa_area - custom_ded_area (subtracted, not added).
  3. Built-in ded layer (id="ded", role="ded") still gets sign=-1 (regression).
  4. Excluded page is absent from payload.pages.

Fixture geometry (pts_per_m=10 on all pages):
  Page 1: gfa square 100x100 pt = 10x10 m = 100.00 m²
          + custom ded L5 square 50x50 pt = 5x5 m = 25.00 m²
          → net = 100 - 25 = 75.00
  Page 2: gfa square 200x100 pt = 20x10 m = 200.00 m² → net = 200.00
  Page 3: excluded; gfa 100x100 — must NOT appear in payload.pages

Emits LITE_REPORT_SIGN_ROLE_OK on success.

    py -3 lite/tests/test_report_sign_role.py
"""
import socket, threading, time, sys
from pathlib import Path

LITE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LITE))
import uvicorn
from playwright.sync_api import sync_playwright


def _free_port(start=8270):
    for p in range(start, start + 60):
        with socket.socket() as s:
            if s.connect_ex(("127.0.0.1", p)) != 0:
                return p
    raise RuntimeError("no free port")


# JS: add custom ded layer L5 (role="ded", id≠"ded") to LAYERS,
# set up PS with 2 active pages + 1 excluded page, then call buildReportPayload().
INJECT_CUSTOM_DED = """() => {
  // Push custom ded layer into LAYERS (CATS = LAYERS same reference).
  LAYERS.push({
    id:"L5", name:"หักช่องลิฟต์", color:"#ff6b6b",
    role:"ded", tag:"deduction_opening",
    counting:false, subTag:"", order:10, groupId:null, parentId:null
  });

  // Page 1: gfa 100x100 (100 m²) + custom ded L5 50x50 (25 m²)  → net=75
  PS[1] = { scale:{pts_per_m:10}, annotations:[], objects:[
    {id:201, catId:'gfa',  semanticTag:'gross_floor_area',   kind:'poly', counting:false,
     pts:[{x:0,y:0},{x:100,y:0},{x:100,y:100},{x:0,y:100}]},
    {id:202, catId:'L5',  semanticTag:'deduction_opening',   kind:'poly', counting:false,
     pts:[{x:0,y:0},{x:50,y:0},{x:50,y:50},{x:0,y:50}]}
  ]};

  // Page 2: gfa 200x100 (200 m²) → net=200
  PS[2] = { scale:{pts_per_m:10}, annotations:[], objects:[
    {id:203, catId:'gfa',  semanticTag:'gross_floor_area',   kind:'poly', counting:false,
     pts:[{x:0,y:0},{x:200,y:0},{x:200,y:100},{x:0,y:100}]}
  ]};

  // Page 3: excluded — must not appear in payload
  PS[3] = { scale:{pts_per_m:10}, annotations:[], objects:[
    {id:204, catId:'gfa',  semanticTag:'gross_floor_area',   kind:'poly', counting:false,
     pts:[{x:0,y:0},{x:100,y:0},{x:100,y:100},{x:0,y:100}]}
  ]};
  excluded[3] = true;

  projectInfo.name = 'ทดสอบ sign role';
  return buildReportPayload();
}"""


def main():
    from server_lite import app as lite_app
    port = _free_port()
    cfg = uvicorn.Config(lite_app, host="127.0.0.1", port=port, log_level="error")
    server = uvicorn.Server(cfg)
    threading.Thread(target=server.run, daemon=True).start()
    time.sleep(2.0)

    failures, checks = [], []

    def chk(name, cond, extra=""):
        checks.append((name, bool(cond)))
        if not cond:
            failures.append(f"{name} {extra}")

    base = f"http://127.0.0.1:{port}"
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        pg = b.new_page()
        pg.on("pageerror", lambda e: failures.append(f"pageerror: {e}"))
        pg.goto(f"{base}/", wait_until="networkidle")
        time.sleep(0.6)

        payload = pg.evaluate(INJECT_CUSTOM_DED)

        # ---- structural checks ----
        pages = payload.get("pages", [])
        chk("2 active pages (pg3 excluded)", len(pages) == 2, len(pages))

        # ---- page 1: custom ded group must have sign=-1 ----
        pg1 = next((p for p in pages if p["idx"] == 1), None)
        chk("pg1 present", pg1 is not None, pages)
        if pg1:
            groups = pg1.get("groups", [])
            gfa_grp = next((g for g in groups if g.get("sign") == 1), None)
            ded_grp = next((g for g in groups if g.get("sign") == -1), None)

            # MAIN BUG: custom ded layer (id="L5", role="ded") must have sign=-1
            chk("custom ded sign=-1 (role-based, not id-based)",
                ded_grp is not None, groups)
            chk("custom ded label is L5 layer name",
                ded_grp is not None and ded_grp.get("label") == "หักช่องลิฟต์",
                ded_grp)

            chk("gfa subtotal = 100.00",
                gfa_grp is not None and abs(gfa_grp.get("subtotal", 0) - 100.0) < 0.01,
                gfa_grp)
            chk("custom ded subtotal = 25.00",
                ded_grp is not None and abs(ded_grp.get("subtotal", 0) - 25.0) < 0.01,
                ded_grp)

            # NET must be 75 (subtracted), not 125 (added — the bug)
            net1 = pg1.get("net", None)
            chk("pg1 net = 75.00 (ded subtracted, not added)",
                net1 is not None and abs(net1 - 75.0) < 0.01,
                f"net={net1}")

        # ---- page 2: gfa only, net=200 ----
        pg2 = next((p for p in pages if p["idx"] == 2), None)
        chk("pg2 present", pg2 is not None, pages)
        if pg2:
            net2 = pg2.get("net", None)
            chk("pg2 net = 200.00",
                net2 is not None and abs(net2 - 200.0) < 0.01,
                f"net={net2}")

        # ---- excluded page 3 not in payload ----
        pg3 = next((p for p in pages if p["idx"] == 3), None)
        chk("excluded pg3 absent from payload", pg3 is None, pg3)

        # ---- regression: built-in ded (id="ded") still works ----
        # Inject built-in ded object (catId="ded") on page 4, no custom layer needed
        INJECT_BUILTIN_DED = """() => {
          PS[4] = { scale:{pts_per_m:10}, annotations:[], objects:[
            {id:301, catId:'gfa', semanticTag:'gross_floor_area', kind:'poly', counting:false,
             pts:[{x:0,y:0},{x:100,y:0},{x:100,y:100},{x:0,y:100}]},
            {id:302, catId:'ded', semanticTag:'deduction_opening', kind:'poly', counting:false,
             pts:[{x:0,y:0},{x:50,y:0},{x:50,y:50},{x:0,y:50}]}
          ]};
          return buildReportPayload();
        }"""
        payload2 = pg.evaluate(INJECT_BUILTIN_DED)
        pg4 = next((p for p in payload2.get("pages", []) if p["idx"] == 4), None)
        chk("builtin ded regression: pg4 present", pg4 is not None, payload2.get("pages"))
        if pg4:
            ded_grp_builtin = next(
                (g for g in pg4.get("groups", []) if g.get("sign") == -1), None)
            net4 = pg4.get("net", None)
            chk("builtin ded sign=-1 (regression)",
                ded_grp_builtin is not None, pg4.get("groups"))
            chk("builtin ded net=75 (regression)",
                net4 is not None and abs(net4 - 75.0) < 0.01,
                f"net={net4}")

        b.close()

    server.should_exit = True
    time.sleep(0.4)

    for name, ok in checks:
        print(f"  [{'OK' if ok else 'XX'}] {name}")
    if failures:
        for f in failures:
            print("FAIL:", f.encode("ascii", "replace").decode("ascii"))
        print("LITE_REPORT_SIGN_ROLE_FAIL")
        sys.exit(1)
    print(f"LITE_REPORT_SIGN_ROLE_OK ({len(checks)}/{len(checks)})")


if __name__ == "__main__":
    main()
