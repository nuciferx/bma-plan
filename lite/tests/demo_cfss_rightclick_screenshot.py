"""
CFSS demo — drive the lite app, promote a poly to master, navigate to another
page, right-click an instance, and capture a screenshot showing the menu.

Output: artifacts/screenshots/cfss-rcmenu-demo.png + cfss-edit-dialog-demo.png
"""
import socket
import sys
import threading
import time
from pathlib import Path

LITE = Path(__file__).resolve().parents[1]
REPO = LITE.parent
ARTIFACTS = REPO / "artifacts" / "screenshots"
ARTIFACTS.mkdir(parents=True, exist_ok=True)

sys.path.insert(0, str(LITE))
import uvicorn
from playwright.sync_api import sync_playwright


def _free_port(start=8590):
    for p in range(start, start + 60):
        with socket.socket() as s:
            if s.connect_ex(("127.0.0.1", p)) != 0:
                return p
    raise RuntimeError("no free port")


JS_WAIT = r"""
async () => {
  for (let i = 0; i < 200; i++) {
    if (typeof window.addMaster === 'function' &&
        typeof window.__cfssTestPromote === 'function' &&
        typeof window.cfssOpenEditDialog === 'function' &&
        window.draw.__cfssWrapped === true) break;
    await new Promise(r => setTimeout(r, 50));
  }
  await new Promise(r => setTimeout(r, 200));
}
"""

JS_SETUP_FULL_STATE = r"""
() => {
  // Stub a fake PDF-loaded state so curImg is truthy.
  window.caseId = 'demo';
  window.pdfName = 'demo.pdf';
  window.pageCount = 3;

  // Fake curImg so ui-lite.html's contextmenu guard "if(!curImg)return" passes
  // (we want to prove right-click works in BOTH guarded and unguarded states).
  if (!window.curImg) {
    // Create a 1x1 transparent image as placeholder
    var img = new Image();
    img.src = 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkAAIAAAoAAv/lxKUAAAAASUVORK5CYII=';
    window.curImg = img;
  }
  // Fake pageData so origSize() works
  if (!window.pageData) {
    window.pageData = {size: {orig_w_pt: 595, orig_h_pt: 842}};
  }
  window.pageRot = window.pageRot || {1: 0, 2: 0, 3: 0};

  if (!window.PS) window.PS = {};
  [1, 2, 3].forEach(function(pg) {
    window.PS[pg] = {objects: [], scale: {pts_per_m: 10}, annotations: []};
  });
  window.pageTags = window.pageTags || {1:'floor', 2:'floor', 3:'floor'};
  window.pageFloorNum = window.pageFloorNum || {1:1, 2:2, 3:3};
  window.curPage = 1;

  // Draw a poly on page 1
  var poly = {
    id: 'poly-demo', catId: 'gfa',
    semanticTag: 'gfa', kind: 'poly', counting: false, dimVisible: true,
    pts: [{x:80,y:80}, {x:200,y:80}, {x:200,y:200}, {x:80,y:200}]
  };
  window.PS[1].objects.push(poly);

  // Promote to master with name "ลิฟต์" and place on pages 2+3
  var mid = window.__cfssTestPromote(poly, 'ลิฟต์', [2, 3]);

  // Trigger a draw so instances appear
  if (typeof window.draw === 'function') window.draw();

  return {
    mid: mid,
    page1Has: window.PS[1].objects.some(o => o.kind === 'instance'),
    page2Has: window.PS[2].objects.some(o => o.kind === 'instance'),
    page3Has: window.PS[3].objects.some(o => o.kind === 'instance')
  };
}
"""

JS_COMPUTE_INST_COORDS = r"""
({pg}) => {
  var inst = window.PS[pg].objects.find(o => o.kind === 'instance');
  if (!inst) return null;
  var scale = window.PS[pg].scale;
  var r = window.resolveInstancePts(inst, scale.pts_per_m);
  var cx = r.bbox.x + r.bbox.w / 2;
  var cy = r.bbox.y + r.bbox.h / 2;
  var sp = window.ptToScreen({x: cx, y: cy});
  return {sx: sp.x, sy: sp.y};
}
"""

JS_NAV_TO_PAGE = r"""
(pg) => {
  window.curPage = pg;
  if (typeof window.draw === 'function') window.draw();
}
"""


def main():
    from server_lite import app as lite_app

    port = _free_port()
    cfg = uvicorn.Config(lite_app, host="127.0.0.1", port=port, log_level="error")
    server = uvicorn.Server(cfg)
    threading.Thread(target=server.run, daemon=True).start()
    time.sleep(2.0)

    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        ctx = browser.new_context(viewport={"width": 1280, "height": 720})
        page = ctx.new_page()
        page.goto(f"http://127.0.0.1:{port}/", wait_until="networkidle")
        page.evaluate(JS_WAIT)

        # Setup full state: 1 master + 3 instances across pg 1, 2, 3
        setup = page.evaluate(JS_SETUP_FULL_STATE)
        print(f"  setup: {setup}")

        # Hide #empty overlay so canvas is clickable
        page.evaluate("""
          () => {
            var emp = document.getElementById('empty');
            if (emp) emp.style.display = 'none';
          }
        """)

        # Navigate to page 2 (where instance was placed, not the source)
        page.evaluate(JS_NAV_TO_PAGE, 2)
        page.wait_for_timeout(300)

        # Compute screen coords of instance on pg 2
        coords = page.evaluate(JS_COMPUTE_INST_COORDS, {"pg": 2})
        print(f"  instance coords on pg2: {coords}")

        # Real right-click on the instance
        page.locator("#cv").click(
            button="right",
            position={"x": coords["sx"], "y": coords["sy"]}
        )
        page.wait_for_timeout(400)

        # Verify menu is up
        menu_info = page.evaluate("""
          () => {
            var m = document.querySelector('.objmenu');
            if (!m) return {visible: false};
            var rows = Array.from(m.querySelectorAll('.objmenu-row'))
                            .map(r => r.textContent);
            var rect = m.getBoundingClientRect();
            return {visible: true, rows: rows, rect: {x:rect.x,y:rect.y,w:rect.width,h:rect.height}};
          }
        """)
        print(f"  menu: {menu_info}")

        # Screenshot 1: right-click menu visible
        shot1 = ARTIFACTS / "cfss-rcmenu-demo.png"
        page.screenshot(path=str(shot1), full_page=False)
        print(f"  saved: {shot1}")

        # Click the Edit row to open Edit dialog
        edit_row_count = page.evaluate("""
          () => {
            var rows = Array.from(document.querySelectorAll('.objmenu .objmenu-row'));
            var editRow = rows.find(r => r.textContent.includes('แก้ไขมาสเตอร์'));
            if (!editRow) return 0;
            editRow.click();
            return 1;
          }
        """)
        page.wait_for_timeout(400)

        # Verify Edit dialog up
        dlg_info = page.evaluate("""
          () => {
            var d = document.querySelector('#cfss-dlg');
            if (!d) return {visible: false};
            var h = d.querySelector('h4');
            var name = d.querySelector('input[type=text], input#cfss-edit-name, #cfss-name-inp');
            var color = d.querySelector('input[type=color]');
            var w = d.querySelector('input[id*="w"], input[placeholder*="W"]');
            return {
              visible: true,
              title: h ? h.textContent : null,
              nameValue: name ? name.value : null,
              colorValue: color ? color.value : null
            };
          }
        """)
        print(f"  edit dialog: {dlg_info}")

        # Screenshot 2: Edit dialog open
        shot2 = ARTIFACTS / "cfss-edit-dialog-demo.png"
        page.screenshot(path=str(shot2), full_page=False)
        print(f"  saved: {shot2}")

        # Take a wider one showing the full layout
        ctx.close()
        browser.close()

    server.should_exit = True
    time.sleep(0.4)
    print("DEMO_DONE")


if __name__ == "__main__":
    main()
