"""
LITE-ANNOT-STYLE regression guard.

Annotation style editor (color / opacity / font size) lives in the standalone
module lite/static/js/annot-style.js (NOT in ui-lite.html). The main file only
holds render-reads-fields + a selection hook + per-type ANN_DEFAULTS. This test
confirms the module loads, mutates the annotation in place, batches one undo
entry per editing session, and that style survives the .bmaplan round-trip.

node --check's BOTH files first. Emits LITE_ANNOT_STYLE_OK.

    py -3 lite/tests/test_annot_style.py
"""
import socket, threading, time, sys, re, subprocess, tempfile, os
from pathlib import Path
LITE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LITE))

# node --check both the module and the inline JS
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

def _free_port(start=8300):
    for p in range(start, start + 60):
        with socket.socket() as s:
            if s.connect_ex(("127.0.0.1", p)) != 0: return p
    raise RuntimeError("no free port")

SCENARIO = r"""
() => {
  const out = {};
  const dummy = document.createElement('canvas'); dummy.width=400; dummy.height=400;
  window.curImg = dummy; curPage = 1; PS[1] = {objects:[], scale:{pts_per_m:10}, annotations:[]};
  undoStack.length = 0; redoStack.length = 0;

  out.moduleLoaded = typeof window.openAnnStyle === 'function' && typeof window.closeAnnStyle === 'function';

  // a comment carries per-type defaults
  let ann = Object.assign({id:state._id++,type:'ann_comment',pt:{x:10,y:10},text:'หมายเหตุ'}, ANN_DEFAULTS.ann_comment);
  PS[1].annotations.push(ann);
  out.defaults = ann.color==='#ffe08a' && ann.opacity===1 && ann.fontSize===13;

  openAnnStyle(ann, 50, 50);
  let panel = document.querySelector('.annstyle-panel');
  out.panelShown = !!panel && panel.style.display==='block';
  out.fontRowShown = panel.querySelector('.as-fontrow').style.display==='flex';

  const hLen = undoStack.length;
  panel.querySelector('.as-sw[data-c="#4c8dff"]').click();
  out.colorChanged = ann.color==='#4c8dff';
  let op = panel.querySelector('.as-opacity'); op.value='0.5'; op.dispatchEvent(new Event('input'));
  out.opacityChanged = ann.opacity===0.5;
  let fn = panel.querySelector('.as-font'); fn.value='24'; fn.dispatchEvent(new Event('input'));
  out.fontChanged = ann.fontSize===24;
  out.oneUndoEntry = undoStack.length === hLen+1;   // whole session = one undo entry

  undo();
  let a2 = PS[1].annotations[0];
  out.undoRestores = a2.color==='#ffe08a' && a2.opacity===1 && a2.fontSize===13;

  // shape annotation: font row hidden
  let rect = Object.assign({id:state._id++,type:'ann_rect',pts:[{x:0,y:0},{x:50,y:50}]}, ANN_DEFAULTS.ann_rect);
  PS[1].annotations.push(rect);
  openAnnStyle(rect, 60, 60);
  out.fontHiddenForShape = panel.querySelector('.as-fontrow').style.display==='none';

  // delete from panel
  let before = PS[1].annotations.length;
  panel.querySelector('.as-del').click();
  out.deletedFromPanel = PS[1].annotations.length === before-1;

  // style survives .bmaplan round-trip
  let c = {id:state._id++,type:'ann_comment',pt:{x:5,y:5},text:'x',color:'#30d158',opacity:0.7,fontSize:20};
  let fwd = annFwd(c);
  out.saveStyle = fwd.color==='#30d158' && fwd.opacity===0.7 && fwd.fontSize===20;
  let rev = annRevFn(fwd);
  out.loadStyle = rev.color==='#30d158' && rev.opacity===0.7 && rev.fontSize===20;

  // highlight fill uses color+opacity without throwing
  let hl = Object.assign({id:state._id++,type:'ann_highlight',pts:[{x:0,y:0},{x:40,y:40}]}, ANN_DEFAULTS.ann_highlight);
  PS[1].annotations.push(hl);
  let threw=false; try{ draw(); }catch(e){threw=true;out.err=String(e);} out.renderNoThrow=!threw;

  return out;
}
"""
CHECKS = ["moduleLoaded","defaults","panelShown","fontRowShown","colorChanged","opacityChanged",
          "fontChanged","oneUndoEntry","undoRestores","fontHiddenForShape","deletedFromPanel",
          "saveStyle","loadStyle","renderNoThrow"]

def main():
    from server_lite import app as lite_app
    port = _free_port()
    cfg = uvicorn.Config(lite_app, host="127.0.0.1", port=port, log_level="error")
    server = uvicorn.Server(cfg); threading.Thread(target=server.run, daemon=True).start(); time.sleep(2.0)
    failures = []; res = {}
    with sync_playwright() as pw:
        b = pw.chromium.launch(); pg = b.new_page()
        pg.on("pageerror", lambda e: failures.append(f"pageerror: {e}"))
        pg.goto(f"http://127.0.0.1:{port}/", wait_until="networkidle"); time.sleep(0.7)
        res = pg.evaluate(SCENARIO); b.close()
    server.should_exit = True; time.sleep(0.4)
    for k in CHECKS:
        ok = res.get(k); print(f"  {k:18s} -> {ok}")
        if ok is not True: failures.append(f"{k}={ok!r}")
    if res.get("err"): print("  err:", res["err"])
    if failures:
        for f in failures: print("FAIL:", f)
        print("LITE_ANNOT_STYLE_FAIL"); sys.exit(1)
    print("LITE_ANNOT_STYLE_OK")

if __name__ == "__main__":
    main()
