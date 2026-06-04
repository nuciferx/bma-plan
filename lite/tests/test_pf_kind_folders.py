"""
LFOC-ORDER-B: kind-aware PF folder separation regression guard.

Verifies that pageFloorKind drives distinct PF folder IDs so that basement,
mezzanine, mechanical, and rooftop pages land in their own folders rather
than collapsing into PF_floor_<N>.

11 sub-checks, marker LITE_PF_KIND_OK:
  basementSeparate      p11 floor#1 normal + p15 floor#1 basement → separate folders
  mezzSeparate          p12 floor#2 normal + p14 floor#2 mezzanine → separate folders
  mechSeparate          p18 floor#5 mechanical → PF_mech_5 exists; PF_floor_5 absent
  basementSeeds         PF_basement_1 has 3 children [gfa,ded,ded]; name has "B1"
  mezzSeeds             PF_mezz_2 has 2 children [gfa,ded]
  mechSeeds             PF_mech_5 has 1 child [gfa]
  siteAndFloorUnchanged PF_site has 3 children; PF_floor_1 has 3 children (regression)
  rankOrder             sorted .order: site<basement_3<basement_2<basement_1
                        <floor_1<floor_2<mezz_2<floor_3<floor_roof<excluded
  backwardCompatNoKind  kind missing → pageFolderIdFor returns PF_floor_<N>
  backwardCompatRooftop floor#=roof, kind=undefined === floor#=roof, kind=rooftop
  addLayerOrphanFallback curPage=basement page → _lpDoAddLayer → layer.parentId===PF_basement_1

Emits LITE_PF_KIND_OK <n>/<total> on success.

    py -3 lite/tests/test_pf_kind_folders.py
"""
import socket, threading, time, sys
from pathlib import Path

LITE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LITE))
import uvicorn
from playwright.sync_api import sync_playwright


def _free_port(start=8620):
    for p in range(start, start + 60):
        with socket.socket() as s:
            if s.connect_ex(("127.0.0.1", p)) != 0:
                return p
    raise RuntimeError("no free port")


# ---------------------------------------------------------------------------
# Dataset: 13-page mixed-kind setup (matches LFOC-ORDER-B frame doc sample)
#
#  p1 = site
#  p2 = site
#  p3 = cover (untagged → excluded)
#  p10= floor#3, kind=normal
#  p11= floor#1, kind=normal
#  p12= floor#2, kind=normal
#  p13= floor#3, kind=normal   (second page same floor as p10)
#  p14= floor#2, kind=mezzanine
#  p15= floor#1, kind=basement
#  p16= floor#3, kind=basement
#  p17= floor#2, kind=basement
#  p18= floor#5, kind=mechanical
#  p19= floor#?,  kind=rooftop
# ---------------------------------------------------------------------------
SCENARIO = r"""
() => {
  const out = {};

  function reseed() {
    LAYERS.length  = 0;
    FOLDERS.length = 0;
    initLayers();
  }

  const mockTags = {
    1:"site", 2:"site", 3:"cover",
    10:"floor", 11:"floor", 12:"floor", 13:"floor",
    14:"floor", 15:"floor", 16:"floor", 17:"floor",
    18:"floor", 19:"floor"
  };
  const mockFloors = {
    10:3, 11:1, 12:2, 13:3,
    14:2, 15:1, 16:3, 17:2,
    18:5, 19:1
  };
  const mockKind = {
    10:"normal", 11:"normal", 12:"normal", 13:"normal",
    14:"mezzanine", 15:"basement", 16:"basement", 17:"basement",
    18:"mechanical", 19:"rooftop"
  };
  const allPages = [1,2,3,10,11,12,13,14,15,16,17,18,19];

  // -----------------------------------------------------------------------
  // basementSeparate: p11 (floor#1, normal) + p15 (floor#1, basement)
  //   → PF_floor_1 AND PF_basement_1 both exist as separate folders
  //   → each contains only its own page(s)
  // -----------------------------------------------------------------------
  reseed();
  seedPageFolders(allPages, mockTags, mockFloors, mockKind);

  const fFloor1   = folderById("PF_floor_1");
  const fBasement1 = folderById("PF_basement_1");
  const basementSep = !!(
    fFloor1 && fBasement1 &&
    fFloor1 !== fBasement1 &&
    fFloor1.pages && fFloor1.pages.indexOf(11) !== -1 &&
    fFloor1.pages.indexOf(15) === -1 &&
    fBasement1.pages && fBasement1.pages.indexOf(15) !== -1 &&
    fBasement1.pages.indexOf(11) === -1
  );
  out.basementSeparate = basementSep;

  // -----------------------------------------------------------------------
  // mezzSeparate: p12 (floor#2, normal) + p14 (floor#2, mezzanine)
  //   → PF_floor_2 AND PF_mezz_2 both exist
  // -----------------------------------------------------------------------
  const fFloor2 = folderById("PF_floor_2");
  const fMezz2  = folderById("PF_mezz_2");
  const mezzSep = !!(
    fFloor2 && fMezz2 &&
    fFloor2 !== fMezz2 &&
    fFloor2.pages && fFloor2.pages.indexOf(12) !== -1 &&
    fFloor2.pages.indexOf(14) === -1 &&
    fMezz2.pages && fMezz2.pages.indexOf(14) !== -1 &&
    fMezz2.pages.indexOf(12) === -1
  );
  out.mezzSeparate = mezzSep;

  // -----------------------------------------------------------------------
  // mechSeparate: p18 (floor#5, mechanical) → PF_mech_5 exists;
  //   PF_floor_5 should NOT exist (no normal floor#5 in dataset)
  // -----------------------------------------------------------------------
  const fMech5  = folderById("PF_mech_5");
  const fFloor5 = folderById("PF_floor_5");
  const mechSep = !!(fMech5 && !fFloor5 && fMech5.pages && fMech5.pages.indexOf(18) !== -1);
  out.mechSeparate = mechSep;

  // -----------------------------------------------------------------------
  // basementSeeds: PF_basement_1 has exactly 3 layers with roles [gfa,ded,ded]
  //   and gfa layer name contains "B1" or "ใต้ดิน"
  // -----------------------------------------------------------------------
  const fB1 = folderById("PF_basement_1");
  let basementSeedsOk = false;
  if (fB1) {
    const ch = childrenOf("PF_basement_1");
    const layers = ch.filter(function(c){ return c.kind === "layer"; }).map(function(c){return c.node;});
    const roles = layers.map(function(l){return l.role;});
    const rolesOk = roles.length === 3 && roles[0]==="gfa" && roles[1]==="ded" && roles[2]==="ded";
    const gfaL = layers.find(function(l){return l.role==="gfa";});
    const nameOk = !!(gfaL && (gfaL.name.indexOf("B1") !== -1 || gfaL.name.indexOf("ใต้ดิน") !== -1));
    basementSeedsOk = rolesOk && nameOk;
  }
  out.basementSeeds = basementSeedsOk;

  // -----------------------------------------------------------------------
  // mezzSeeds: PF_mezz_2 has exactly 2 layers with roles [gfa, ded]
  // -----------------------------------------------------------------------
  const fM2 = folderById("PF_mezz_2");
  let mezzSeedsOk = false;
  if (fM2) {
    const ch = childrenOf("PF_mezz_2");
    const layers = ch.filter(function(c){ return c.kind === "layer"; }).map(function(c){return c.node;});
    const roles = layers.map(function(l){return l.role;});
    mezzSeedsOk = roles.length === 2 && roles[0]==="gfa" && roles[1]==="ded";
  }
  out.mezzSeeds = mezzSeedsOk;

  // -----------------------------------------------------------------------
  // mechSeeds: PF_mech_5 has exactly 1 layer with role gfa
  // -----------------------------------------------------------------------
  const fMe5 = folderById("PF_mech_5");
  let mechSeedsOk = false;
  if (fMe5) {
    const ch = childrenOf("PF_mech_5");
    const layers = ch.filter(function(c){ return c.kind === "layer"; }).map(function(c){return c.node;});
    const roles = layers.map(function(l){return l.role;});
    mechSeedsOk = roles.length === 1 && roles[0]==="gfa";
  }
  out.mechSeeds = mechSeedsOk;

  // -----------------------------------------------------------------------
  // siteAndFloorUnchanged: PF_site has 3 children; PF_floor_1 has 3 children (regression)
  // -----------------------------------------------------------------------
  const fSite = folderById("PF_site");
  let siteOk = false;
  if (fSite) {
    const ch = childrenOf("PF_site");
    const layers = ch.filter(function(c){ return c.kind === "layer"; }).map(function(c){return c.node;});
    siteOk = layers.length === 3 && layers[0].role==="site" && layers[1].role==="gfa" && layers[2].role==="use";
  }
  const fF1 = folderById("PF_floor_1");
  let floor1Ok = false;
  if (fF1) {
    const ch = childrenOf("PF_floor_1");
    const layers = ch.filter(function(c){ return c.kind === "layer"; }).map(function(c){return c.node;});
    floor1Ok = layers.length === 3 && layers[0].role==="gfa" && layers[1].role==="ded" && layers[2].role==="ded";
  }
  out.siteAndFloorUnchanged = siteOk && floor1Ok;

  // -----------------------------------------------------------------------
  // rankOrder: assert PF folder .order satisfies the expected sequence.
  // Expected ascending .order:
  //   PF_site(0) < PF_basement_3(85) < PF_basement_2(90) < PF_basement_1(95)
  //   < PF_floor_1(110) < PF_floor_2(120) < PF_mezz_2(125)
  //   < PF_floor_3(130) < PF_floor_roof(9000) < PF_excluded(9999)
  // -----------------------------------------------------------------------
  const pfFolders = FOLDERS.filter(function(f){ return f && f.kind==="page-folder"; });
  const orderOf = {};
  pfFolders.forEach(function(f){ orderOf[f.id] = f.order; });

  const rankOk = (
    typeof orderOf["PF_site"]       === "number" &&
    typeof orderOf["PF_basement_3"] === "number" &&
    typeof orderOf["PF_basement_2"] === "number" &&
    typeof orderOf["PF_basement_1"] === "number" &&
    typeof orderOf["PF_floor_1"]    === "number" &&
    typeof orderOf["PF_floor_2"]    === "number" &&
    typeof orderOf["PF_mezz_2"]     === "number" &&
    typeof orderOf["PF_floor_3"]    === "number" &&
    typeof orderOf["PF_floor_roof"] === "number" &&
    typeof orderOf["PF_excluded"]   === "number" &&
    orderOf["PF_site"]       < orderOf["PF_basement_3"] &&
    orderOf["PF_basement_3"] < orderOf["PF_basement_2"] &&
    orderOf["PF_basement_2"] < orderOf["PF_basement_1"] &&
    orderOf["PF_basement_1"] < orderOf["PF_floor_1"]    &&
    orderOf["PF_floor_1"]    < orderOf["PF_floor_2"]    &&
    orderOf["PF_floor_2"]    < orderOf["PF_mezz_2"]     &&
    orderOf["PF_mezz_2"]     < orderOf["PF_floor_3"]    &&
    orderOf["PF_floor_3"]    < orderOf["PF_floor_roof"] &&
    orderOf["PF_floor_roof"] < orderOf["PF_excluded"]
  );
  out.rankOrder = rankOk;

  // -----------------------------------------------------------------------
  // backwardCompatNoKind: calling pageFolderIdFor with no kind
  //   (page, tag-string, floorNum-value, undefined) → PF_floor_<N>
  // -----------------------------------------------------------------------
  const idNoKind = pageFolderIdFor(99, "floor", 4, undefined);
  out.backwardCompatNoKind = (idNoKind === "PF_floor_4");

  // -----------------------------------------------------------------------
  // backwardCompatRooftop: floor#=roof and kind=undefined === kind=rooftop === "PF_floor_roof"
  // -----------------------------------------------------------------------
  const idRoofNoKind  = pageFolderIdFor(99, "floor", "roof", undefined);
  const idRoofKind    = pageFolderIdFor(99, "floor", "roof", "rooftop");
  const idRooftopKind = pageFolderIdFor(99, "floor", 1,      "rooftop");
  out.backwardCompatRooftop = (
    idRoofNoKind  === "PF_floor_roof" &&
    idRoofKind    === "PF_floor_roof" &&
    idRooftopKind === "PF_floor_roof"
  );

  // -----------------------------------------------------------------------
  // addLayerOrphanFallback: set curPage to a basement page, call _lpDoAddLayer("gfa")
  //   → new layer's parentId === "PF_basement_1"
  // -----------------------------------------------------------------------
  reseed();
  // Set up minimal state for page 15 (floor#1, basement)
  pageTags[15]     = "floor";
  pageFloorNum[15] = 1;
  pageFloorKind[15] = "basement";
  curPage          = 15;
  seedPageFolders([15], pageTags, pageFloorNum, pageFloorKind);

  // Make sure state.activeCat is null/undefined (no parentId carrier)
  state.activeCat = null;

  const layersBefore = LAYERS.length;
  _lpDoAddLayer("gfa");
  const layersAfter = LAYERS.length;
  let addFallbackOk = false;
  if (layersAfter > layersBefore) {
    const newest = LAYERS[LAYERS.length - 1];
    addFallbackOk = !!(newest && newest.parentId === "PF_basement_1");
  }
  out.addLayerOrphanFallback = addFallbackOk;

  reseed();
  return out;
}
"""

CHECKS = [
    "basementSeparate",
    "mezzSeparate",
    "mechSeparate",
    "basementSeeds",
    "mezzSeeds",
    "mechSeeds",
    "siteAndFloorUnchanged",
    "rankOrder",
    "backwardCompatNoKind",
    "backwardCompatRooftop",
    "addLayerOrphanFallback",
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
        result = pg.evaluate(SCENARIO)
        pg.close()
        b.close()

    server.should_exit = True
    time.sleep(0.4)

    for e in page_errors:
        print("  JS ERROR:", e)

    print()
    print("LFOC-ORDER-B kind-folder checks:")
    pass_n = 0
    total = len(CHECKS)
    for k in CHECKS:
        ok = result.get(k)
        print(f"  {k:30s} -> {ok}")
        if ok is True:
            pass_n += 1
        else:
            failures.append(f"check '{k}' = {ok!r} (expected True)")

    print()
    if failures:
        for f in failures:
            print("FAIL:", f)
        print(f"LITE_PF_KIND_FAIL {pass_n}/{total}")
        sys.exit(1)
    else:
        print(f"LITE_PF_KIND_OK {pass_n}/{total}")


if __name__ == "__main__":
    main()
