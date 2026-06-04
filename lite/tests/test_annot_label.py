"""
LITE-ANNOT-LABEL regression guard.

Two requested behaviours:
  - right-click an annotation = EDIT (select + open style/label panel), no longer
    delete-on-right-click; delete moved to the panel button / Delete key.
  - movable text label ("เทค") on shape annotations (highlight/arrow/rect/circle/
    cloud): add/edit via inline editor (generalized field='label'), drag to
    reposition (state.dragLabel), round-trips through .bmaplan.

node --check's both files. Emits LITE_ANNOT_LABEL_OK.

    py -3 lite/tests/test_annot_label.py
"""
import socket, threading, time, sys, re, subprocess, tempfile, os
from pathlib import Path
LITE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LITE))

mod = LITE / "static" / "js" / "annot-style.js"
r0 = subprocess.run(["node", "--check", str(mod)], capture_output=True, text=True)
print("node --check annot-style.js:", "OK" if r0.returncode == 0 else r0.stderr.strip())
if r0.returncode != 0: sys.exit(1)
html = open(LITE / "ui-lite.html", encoding="utf-8").read()
js = "\n".join(re.findall(r"<script>(.*?)</script>", html, re.S))
tf = tempfile.NamedTemporaryFile("w", suffix=".js", delete=False, encoding="utf-8"); tf.write(js); tf.close()
r1 = subprocess.run(["node", "--check", tf.name], capture_output=True, text=True); os.unlink(tf.name)
print("node --check ui-lite inline:", "OK" if r1.returncode == 0 else r1.stderr.strip())
if r1.returncode != 0: sys.exit(1)

import uvicorn
from playwright.sync_api import sync_playwright

def _free_port(start=8310):
    for p in range(start, start + 60):
        with socket.socket() as s:
            if s.connect_ex(("127.0.0.1", p)) != 0: return p
    raise RuntimeError("no port")

SCENARIO = r"""
() => {
  const out = {};
  const dummy = document.createElement('canvas'); dummy.width=400; dummy.height=400;
  window.curImg = dummy; curPage = 1; PS[1] = {objects:[], scale:{pts_per_m:10}, annotations:[]};
  undoStack.length=0; redoStack.length=0;
  const cv = document.getElementById('cv'), r = cv.getBoundingClientRect();

  // an arrow annotation
  let arrow = Object.assign({id:state._id++,type:'ann_arrow',pts:[{x:60,y:60},{x:160,y:120}]}, ANN_DEFAULTS.ann_arrow);
  PS[1].annotations.push(arrow);

  // right-click = EDIT (no delete): select + open style panel
  let sp = ptToScreen(arrow.pts[0]);
  cv.dispatchEvent(new MouseEvent('contextmenu', {clientX:r.left+sp.x, clientY:r.top+sp.y, bubbles:true, cancelable:true}));
  out.rightClickNoDelete = PS[1].annotations.length === 1;
  out.rightClickSelects = state.selAnn === arrow;
  out.rightClickOpensPanel = document.querySelector('.annstyle-panel').style.display === 'block';

  // add a label via the inline editor (field=label)
  pushUndo(); openAnnEditor(arrow, false, 'label');
  out.labelPtDefaulted = !!arrow.labelPt;
  document.getElementById('annEditor').value = 'ผนังกันไฟ'; commitAnnEditor();
  out.labelSaved = arrow.label === 'ผนังกันไฟ';
  out.labelBoxExists = !!_labelBox(arrow) && _labelBox(arrow).w > 0;

  // drag the label to reposition (one undo entry from drag start)
  setTool('select'); state.selAnn = arrow;
  let lb = _labelBox(arrow), before = {x:arrow.labelPt.x, y:arrow.labelPt.y};
  cv.dispatchEvent(new MouseEvent('mousedown', {button:0, clientX:r.left+lb.x+6, clientY:r.top+lb.y+6, bubbles:true}));
  out.dragStarted = !!state.dragLabel;
  cv.dispatchEvent(new MouseEvent('mousemove', {clientX:r.left+lb.x+90, clientY:r.top+lb.y+70, bubbles:true}));
  window.dispatchEvent(new MouseEvent('mouseup', {bubbles:true}));
  out.labelMoved = (arrow.labelPt.x !== before.x) && !state.dragLabel;

  // undo restores pre-drag label position
  undo(); let a2 = PS[1].annotations[0];
  out.undoMove = Math.abs(a2.labelPt.x - before.x) < 0.001;

  // clearing the label drops only the tag (annotation stays)
  pushUndo(); openAnnEditor(a2, false, 'label'); document.getElementById('annEditor').value = '   '; commitAnnEditor();
  out.labelCleared = !a2.label && !a2.labelPt && PS[1].annotations.length === 1;

  // .bmaplan round-trip carries label + labelPt
  a2.label = 'โซน A'; a2.labelPt = {x:5, y:5};
  let fwd = annFwd(a2); out.saveLabel = fwd.label === 'โซน A' && fwd.labelPt.x === 5;
  let rev = annRevFn(fwd); out.loadLabel = rev.label === 'โซน A' && rev.labelPt.x === 5;

  // text/comment editor still edits the body text (field defaults to 'text')
  let c = Object.assign({id:state._id++,type:'ann_comment',pt:{x:20,y:20},text:'a'}, ANN_DEFAULTS.ann_comment);
  PS[1].annotations.push(c);
  pushUndo(); openAnnEditor(c, false); document.getElementById('annEditor').value = 'แก้คอมเมนต์'; commitAnnEditor();
  out.textStillEdits = c.text === 'แก้คอมเมนต์';

  let threw=false; try{ draw(); }catch(e){ threw=true; out.err=String(e); } out.renderNoThrow=!threw;
  return out;
}
"""
CHECKS = ["rightClickNoDelete","rightClickSelects","rightClickOpensPanel","labelPtDefaulted",
          "labelSaved","labelBoxExists","dragStarted","labelMoved","undoMove","labelCleared",
          "saveLabel","loadLabel","textStillEdits","renderNoThrow"]

def main():
    from server_lite import app as lite_app
    port = _free_port()
    cfg = uvicorn.Config(lite_app, host="127.0.0.1", port=port, log_level="error")
    server = uvicorn.Server(cfg); threading.Thread(target=server.run, daemon=True).start(); time.sleep(2.0)
    failures = []; res = {}
    with sync_playwright() as pw:
        b = pw.chromium.launch(); pg = b.new_page(viewport={"width":1280,"height":820})
        pg.on("pageerror", lambda e: failures.append(f"pageerror: {e}"))
        pg.goto(f"http://127.0.0.1:{port}/", wait_until="networkidle"); time.sleep(0.7)
        res = pg.evaluate(SCENARIO); b.close()
    server.should_exit = True; time.sleep(0.4)
    for k in CHECKS:
        ok = res.get(k); print(f"  {k:20s} -> {ok}")
        if ok is not True: failures.append(f"{k}={ok!r}")
    if res.get("err"): print("  err:", res["err"])
    if failures:
        for f in failures: print("FAIL:", f)
        print("LITE_ANNOT_LABEL_FAIL"); sys.exit(1)
    print("LITE_ANNOT_LABEL_OK")

if __name__ == "__main__":
    main()
