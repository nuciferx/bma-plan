"""
LITE-FLOOR regression guard.

Lite could only set a coarse page TAG (in Page Setup) and saved pageFloorKind/
pageFloorNum/pageNames as empty stubs. This sprint ported proto's per-page floor
designation into lite (gated on tag 'floor' = แปลนชั้น): floor kind
(basement/normal/mechanical/rooftop/custom) + floor number + an editable page name,
exposed through one shared control (floorOptsHTML) reused by BOTH the Page Setup
modal and the Σ Summary panel, and persisted into the .bmaplan fields proto reads.

Boots server_lite and drives the floor helpers (window globals; lite's inline
script is classic). Also node --check's the inline JS first. Emits LITE_FLOOR_OK.

    py -3 lite/tests/test_floor_designation.py
"""
import socket, threading, time, sys, re, subprocess, tempfile, os
from pathlib import Path
LITE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LITE))

# 1) node syntax check of inline JS
html=open(LITE/'ui-lite.html',encoding='utf-8').read()
js="\n".join(re.findall(r'<script>(.*?)</script>', html, re.S))
tf=tempfile.NamedTemporaryFile('w',suffix='.js',delete=False,encoding='utf-8'); tf.write(js); tf.close()
r=subprocess.run(['node','--check',tf.name],capture_output=True,text=True); os.unlink(tf.name)
print("node --check:", "OK" if r.returncode==0 else r.stderr.strip())
if r.returncode!=0: sys.exit(1)

import uvicorn
from playwright.sync_api import sync_playwright
def _free_port(start=8270):
    for p in range(start, start+60):
        with socket.socket() as s:
            if s.connect_ex(("127.0.0.1", p)) != 0: return p
    raise RuntimeError("no free port")

SCENARIO = r"""
() => {
  const out = {};
  curPage = 3; caseId = "x"; pageCount = 5;
  out.tagOnlyNoKind = floorOptsHTML(3).includes('fc-tag') && !floorOptsHTML(3).includes('fc-kind');
  liteSetTag(3,'floor');
  let h = floorOptsHTML(3);
  out.kindAppears = h.includes('fc-kind');
  out.nameInputAlways = h.includes('fc-name');         // name input present once tagged floor
  liteSetFloorKind(3,'normal'); liteSetFloorNum(3,2);
  out.autoName = pageNames[3]==='ชั้น 2' && floorOptsHTML(3).includes('value="ชั้น 2"');
  // manual override via name input handler
  onFloorName(3,'ชั้นลอย M', null);
  out.manualName = pageNames[3]==='ชั้นลอย M';
  // changing the floor number re-derives auto name (overrides manual)
  onFloorNum(3,5,null); out.numRederives = pageNames[3]==='ชั้น 5';
  // clear name -> re-derive
  onFloorName(3,'  ',null); out.clearRederives = pageNames[3]==='ชั้น 5';
  // custom: manual name sticks, no auto overwrite
  liteSetFloorKind(3,'custom'); onFloorName(3,'เมซซานีน',null);
  liteSetFloorKind(3,'custom');   // re-pick custom: must NOT wipe name
  out.customKeepsName = pageNames[3]==='เมซซานีน';
  out.customNoNum = !('3' in pageFloorNum);
  // escAttr guards quotes/markup in value attribute
  out.escWorks = escAttr('a"<b>&')==='a&quot;&lt;b&gt;&amp;';
  // save/load round trip
  liteSetTag(3,'floor'); liteSetFloorKind(3,'basement'); liteSetFloorNum(3,1); onFloorName(3,'',null);
  const doc={pageTags:pageTags,pageNames:pageNames,pageFloorKind:pageFloorKind,pageFloorNum:pageFloorNum};
  out.saveHasFields = doc.pageFloorKind[3]==='basement' && doc.pageFloorNum[3]===1 && doc.pageNames[3]==='ชั้นใต้ดิน 1';
  pageFloorKind={}; pageFloorNum={}; pageNames={};
  pageNames=doc.pageNames||{}; pageFloorKind=doc.pageFloorKind||{}; pageFloorNum=doc.pageFloorNum||{};
  out.loadRestores = pageFloorKind[3]==='basement' && pageNames[3]==='ชั้นใต้ดิน 1';
  return out;
}
"""
CHECKS=["tagOnlyNoKind","kindAppears","nameInputAlways","autoName","manualName",
        "numRederives","clearRederives","customKeepsName","customNoNum","escWorks",
        "saveHasFields","loadRestores"]

def main():
    from server_lite import app as lite_app
    port=_free_port()
    cfg=uvicorn.Config(lite_app, host="127.0.0.1", port=port, log_level="error")
    server=uvicorn.Server(cfg); threading.Thread(target=server.run, daemon=True).start(); time.sleep(2.0)
    failures=[]; res={}
    with sync_playwright() as pw:
        b=pw.chromium.launch(); pg=b.new_page()
        pg.on("pageerror", lambda e: failures.append(f"pageerror: {e}"))
        pg.goto(f"http://127.0.0.1:{port}/", wait_until="networkidle"); time.sleep(0.6)
        res=pg.evaluate(SCENARIO); b.close()
    server.should_exit=True; time.sleep(0.4)
    for k in CHECKS:
        ok=res.get(k); print(f"  {k:16s} -> {ok}")
        if ok is not True: failures.append(f"{k}={ok!r}")
    if failures:
        for f in failures: print("FAIL:", f)
        print("LITE_FLOOR_FAIL"); sys.exit(1)
    print("LITE_FLOOR_OK")

if __name__=="__main__": main()
