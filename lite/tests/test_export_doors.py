"""
LITE report-truth slice D/4 (REVIEW_LITE_LAYER_REPORT_20260704.md ledger
S-6 + S-12) acceptance test.

Door inventory BEFORE this slice:
  File menu (flat, top-level):
    #mi-xlsx   "Export XLSX" + Ctrl+E hint chip -- HIDDEN (display:none) by
               _rebuildFileMenu, but Ctrl+E's keydown handler still calls
               document.getElementById("mi-xlsx").onclick() directly --
               a "ghost feature": functionally alive, invisible in the menu.
    #mi-pdfov  "Export PDF (overlay)" -- flat, visible, NOT grouped with
               Export ▶ at all (structurally inconsistent with Report/XLSX).
    Export ▶ (flyout submenu, replaces #mi-report's DOM slot):
      "Report HTML"   -> openReport()
      "XLSX Summary"  -> window.exportXlsx() (menu-flyout.js's own copy)
  Wizard (overview-setup.js, Step 3 nav):
    #ov-export "📄 ส่งออก PDF" -> _lovsExportReport() -> openReport() (opens
               the HTML /report page -- the button's own label claims a PDF
               export that never happens).
  Overlay-label display (export-annotate.js exportPdfOverlay()):
    per-object/instance labels used the raw semanticTag enum (English,
    schema-internal, e.g. "gross_floor_area") instead of the layer's Thai
    display name.

Door inventory AFTER this slice (3 doors total, no new actions):
  File ▸ Export ▶ (3 items, all visible, truthful Thai labels):
    "รายงาน (แก้ไข/พิมพ์ได้)"  -> openReport()
    "XLSX (Ctrl+E)"             -> window.exportXlsx()
    "PDF ทับ Annotation"        -> window.exportPdfOverlay() (new thin
                                   delegate to ExportAnnotate.exportPdfOverlay)
  #mi-xlsx UNHIDDEN (visible again) -- ghost feature closed; it and the
    submenu's "XLSX (Ctrl+E)" item both point at the SAME exportXlsx action
    (tolerated duplicate reachability, same pattern as the wizard button).
  #mi-pdfov REMOVED outright (absorbed into Export ▶'s 3rd item; no hotkey
    depended on it).
  #ov-export relabeled "📄 เปิดรายงาน" (still calls the same
    _lovsExportReport() -> openReport(), one of the same 3 actions).
  exportPdfOverlay() labels now use catOf(cid).name (Thai layer display
    name), object's own .name taking priority when set -- DISPLAY ONLY,
    semanticTag untouched in the row/schema data itself.

Checks (LITE_EXPORT_DOORS_OK on 4/4):
  (a) exportSubmenuOk     Export ▶ submenu has exactly 3 items, wired (in
                          order) to openReport/exportXlsx/exportPdfOverlay,
                          none individually display:none.
  (b) mixlsxVisibleOk     #mi-xlsx exists and is NOT display:none (the
                          ghost-feature gap is closed).
  (c) wizardLabelOk       #ov-export's text no longer says "PDF" (still
                          opens the HTML report via the same action).
  (d) overlayLabelThaiOk  exportPdfOverlay()'s captured pages{} payload
                          (dlPost intercepted) uses the layer's Thai display
                          name in the object label, NOT the raw semanticTag
                          enum string.

    py -3 lite/tests/test_export_doors.py
"""
import socket
import sys
import threading
import time
from pathlib import Path

LITE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LITE))
import uvicorn
from playwright.sync_api import sync_playwright


def _free_port(start=8680):
    for p in range(start, start + 60):
        with socket.socket() as s:
            if s.connect_ex(("127.0.0.1", p)) != 0:
                return p
    raise RuntimeError("no free port")


CHECK_EXPORT_SUBMENU = r"""
() => {
  var sub = document.querySelector('.menu[data-m="file"] .dd [data-flyout-group="export"] .sub-dd');
  var items = sub ? Array.from(sub.querySelectorAll('.item')) : [];
  return {
    count: items.length,
    actions: items.map(function(el){ return el.dataset.action; }),
    labels: items.map(function(el){ return el.textContent; }),
    anyHidden: items.some(function(el){ return getComputedStyle(el).display === 'none'; })
  };
}
"""

CHECK_MI_XLSX = r"""
() => {
  var el = document.getElementById('mi-xlsx');
  return {
    exists: !!el,
    display: el ? getComputedStyle(el).display : null,
    hasHotkeyChip: !!(el && el.textContent.indexOf('Ctrl+E') !== -1)
  };
}
"""

CHECK_WIZARD_LABEL = r"""
async () => {
  caseId = 'test-mock';
  openOv();
  await new Promise(function(r){ setTimeout(r, 200); });
  _lovsGoStep(3);
  await new Promise(function(r){ setTimeout(r, 200); });
  var btn = document.getElementById('ov-export');
  return {
    exists: !!btn,
    visible: !!btn && btn.style.display !== 'none',
    text: btn ? btn.textContent : null
  };
}
"""

CHECK_OVERLAY_LABEL = r"""
() => {
  var captured = null;
  var _origDlPost = window.dlPost;
  window.dlPost = function(url, payload, fname) { captured = { url: url, payload: payload, fname: fname }; return Promise.resolve(); };

  caseId = 'test-mock';
  var customLayer = addLayer('gfa', 'ห้องนอนใหญ่', '#4c8dff');
  PS[1] = { scale: { pts_per_m: 10 }, annotations: [], objects: [
    { id: 9001, catId: customLayer.id, semanticTag: 'gross_floor_area', kind: 'poly', counting: false,
      pts: [{x:0,y:0},{x:50,y:0},{x:50,y:50},{x:0,y:50}] }   // 50x50pt @ 10pt/m -> 5x5m -> 25.00 m2
  ]};

  ExportAnnotate.exportPdfOverlay();
  window.dlPost = _origDlPost;

  if (!captured) return { captured: false };
  var pg1 = captured.payload && captured.payload.pages && captured.payload.pages['1'];
  var obj0 = pg1 && pg1.objects && pg1.objects[0];
  var label = obj0 ? obj0.label : null;
  return {
    captured: true,
    label: label,
    hasThaiName: !!(label && label.indexOf('ห้องนอนใหญ่') !== -1),
    hasArea: !!(label && label.indexOf('25.00') !== -1),
    hasRawSemanticTag: !!(label && label.indexOf('gross_floor_area') !== -1)
  };
}
"""


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

    with sync_playwright() as pw:
        b = pw.chromium.launch()
        pg = b.new_page()
        errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.goto(f"http://127.0.0.1:{port}/", wait_until="networkidle")
        time.sleep(0.6)

        # ---- (a) Export submenu: exactly 3 items, correct actions, none hidden ----
        sm = pg.evaluate(CHECK_EXPORT_SUBMENU)
        exportSubmenuOk = (
            sm["count"] == 3
            and sm["actions"] == ["openReport", "exportXlsx", "exportPdfOverlay"]
            and sm["anyHidden"] is False
        )
        chk("(a) Export submenu: 3 items, wired, none hidden", exportSubmenuOk, sm)

        # ---- (b) mi-xlsx unhidden (ghost feature closed) ----
        mx = pg.evaluate(CHECK_MI_XLSX)
        mixlsxVisibleOk = mx["exists"] and mx["display"] != "none" and mx["hasHotkeyChip"]
        chk("(b) #mi-xlsx visible (no longer a ghost feature)", mixlsxVisibleOk, mx)

        # ---- (c) wizard button relabeled (no longer claims PDF) ----
        wz = pg.evaluate(CHECK_WIZARD_LABEL)
        wizardLabelOk = (
            wz["exists"] and wz["visible"]
            and wz["text"] is not None
            and "PDF" not in wz["text"]
            and "เปิดรายงาน" in wz["text"]
        )
        chk("(c) wizard button no longer claims PDF (opens HTML report)", wizardLabelOk, wz)

        # ---- (d) overlay payload labels use Thai layer name, not raw semanticTag ----
        ov = pg.evaluate(CHECK_OVERLAY_LABEL)
        overlayLabelThaiOk = (
            ov.get("captured") is True
            and ov.get("hasThaiName") is True
            and ov.get("hasArea") is True
            and ov.get("hasRawSemanticTag") is False
        )
        chk("(d) overlay label uses Thai layer name, not raw semanticTag", overlayLabelThaiOk, ov)

        b.close()

    server.should_exit = True
    time.sleep(0.4)

    print("\n=== LITE-EXPORT-DOORS checks ===")
    for name, ok in checks:
        print(f"  [{'OK' if ok else 'XX'}] {name}")
    if errs:
        print("  pageerrors:", errs[:6])
        failures.append(f"page errors: {errs[:6]}")
    if failures:
        for f in failures:
            print("FAIL:", f)
        print("LITE_EXPORT_DOORS_FAIL")
        sys.exit(1)
    print(f"LITE_EXPORT_DOORS_OK ({len(checks)}/{len(checks)})")


if __name__ == "__main__":
    main()
