"""
LITE-HARDENING regression guard (Undo/Redo + annotation rubber-band + inline comment editor).

Adds three capabilities the LITE EPIC shipped without:
  - snapshot Undo/Redo over the per-page document model (Ctrl+Z / Ctrl+Y, Edit menu)
  - rubber-band preview while placing shape annotations (drawAnnotPreview)
  - inline <textarea> editor for text/comment annotations replacing prompt(),
    editable after creation, multi-line, empty-on-commit discards.

Boots server_lite and drives the window globals. node --check's the inline JS first.
Emits LITE_HARDENING_OK.

    py -3 lite/tests/test_hardening.py
"""
import socket, threading, time, sys, re, subprocess, tempfile, os
from pathlib import Path
LITE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LITE))

html = open(LITE / "ui-lite.html", encoding="utf-8").read()
js = "\n".join(re.findall(r"<script>(.*?)</script>", html, re.S))
tf = tempfile.NamedTemporaryFile("w", suffix=".js", delete=False, encoding="utf-8"); tf.write(js); tf.close()
r = subprocess.run(["node", "--check", tf.name], capture_output=True, text=True); os.unlink(tf.name)
print("node --check:", "OK" if r.returncode == 0 else r.stderr.strip())
if r.returncode != 0: sys.exit(1)

import uvicorn
from playwright.sync_api import sync_playwright

def _free_port(start=8290):
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

  // 1. Undo/Redo on a polygon object
  setTool('poly'); state.draft = [{x:0,y:0},{x:100,y:0},{x:100,y:100}]; finishDraft();
  out.added = PS[1].objects.length === 1;
  undo(); out.undoRemoves = PS[1].objects.length === 0;
  redo(); out.redoRestores = PS[1].objects.length === 1;

  // 2. count add + delete + undo restores
  setTool('count'); pushUndo(); PS[1].objects.push(mkObj([{x:5,y:5}],'count',true));
  out.countAdded = PS[1].objects.length === 2;
  state.sel = PS[1].objects[1]; document.getElementById('p-del').onclick();
  out.deleted = PS[1].objects.length === 1;
  undo(); out.undoDelete = PS[1].objects.length === 2;
  undo();  // drop the count add too, back to single poly
  out.undoDelete2 = PS[1].objects.length === 1;

  // 3. inline comment editor — create + commit non-empty
  setTool('ann_comment');
  pushUndo(); let ann = {id:state._id++,type:'ann_comment',pt:{x:10,y:10},text:''};
  PS[1].annotations.push(ann); openAnnEditor(ann,true);
  document.getElementById('annEditor').value = 'ตำแหน่งบันไดผิด'; commitAnnEditor();
  out.commentSaved = PS[1].annotations.length===1 && PS[1].annotations[0].text==='ตำแหน่งบันไดผิด';
  out.toolSwitchedSel = state.tool === 'select';   // proto-parity: one comment per activation
  undo(); out.undoComment = PS[1].annotations.length === 0;
  redo(); out.redoComment = PS[1].annotations.length === 1;

  // 4. empty new comment discarded + no stray history entry
  const hLen = undoStack.length;
  pushUndo(); let ann2 = {id:state._id++,type:'ann_text',pt:{x:20,y:20},text:''};
  PS[1].annotations.push(ann2); openAnnEditor(ann2,true);
  document.getElementById('annEditor').value = '   '; commitAnnEditor();
  out.emptyDiscarded = PS[1].annotations.length===1 && undoStack.length===hLen;

  // 5. edit existing comment (multi-line) + undo restores prior text
  let c0 = PS[1].annotations[0];
  pushUndo(); openAnnEditor(c0,false);
  document.getElementById('annEditor').value = 'แก้แล้ว\nบรรทัดสอง'; commitAnnEditor();
  out.editExisting = c0.text === 'แก้แล้ว\nบรรทัดสอง';
  undo(); out.undoEdit = PS[1].annotations[0].text === 'ตำแหน่งบันไดผิด';
  redo(); out.redoEdit = PS[1].annotations[0].text === 'แก้แล้ว\nบรรทัดสอง';

  // 6. cancel (Esc) on a new comment removes it and drops history
  const hLen2 = undoStack.length;
  pushUndo(); let ann3 = {id:state._id++,type:'ann_comment',pt:{x:30,y:30},text:''};
  PS[1].annotations.push(ann3); openAnnEditor(ann3,true);
  document.getElementById('annEditor').value = 'ทิ้ง'; cancelAnnEditor();
  out.cancelDiscards = PS[1].annotations.length===1 && undoStack.length===hLen2;

  // 7. multi-line render + rubber-band preview do not throw
  let threw = false;
  try { draw(); } catch(e){ threw = true; out.errA = String(e); }
  setTool('ann_rect'); state.draft = [{x:0,y:0}]; lastMouse = {x:60,y:50};
  try { draw(); } catch(e){ threw = true; out.errB = String(e); }
  out.previewNoThrow = !threw;

  return out;
}
"""
CHECKS = ["added","undoRemoves","redoRestores","countAdded","deleted","undoDelete","undoDelete2",
          "commentSaved","toolSwitchedSel","undoComment","redoComment","emptyDiscarded",
          "editExisting","undoEdit","redoEdit","cancelDiscards","previewNoThrow"]

def main():
    from server_lite import app as lite_app
    port = _free_port()
    cfg = uvicorn.Config(lite_app, host="127.0.0.1", port=port, log_level="error")
    server = uvicorn.Server(cfg); threading.Thread(target=server.run, daemon=True).start(); time.sleep(2.0)
    failures = []; res = {}
    with sync_playwright() as pw:
        b = pw.chromium.launch(); pg = b.new_page()
        pg.on("pageerror", lambda e: failures.append(f"pageerror: {e}"))
        pg.goto(f"http://127.0.0.1:{port}/", wait_until="networkidle"); time.sleep(0.6)
        res = pg.evaluate(SCENARIO); b.close()
    server.should_exit = True; time.sleep(0.4)
    for k in CHECKS:
        ok = res.get(k); print(f"  {k:16s} -> {ok}")
        if ok is not True: failures.append(f"{k}={ok!r}")
    if res.get("errA"): print("  errA:", res["errA"])
    if res.get("errB"): print("  errB:", res["errB"])
    if failures:
        for f in failures: print("FAIL:", f)
        print("LITE_HARDENING_FAIL"); sys.exit(1)
    print("LITE_HARDENING_OK")

if __name__ == "__main__":
    main()
