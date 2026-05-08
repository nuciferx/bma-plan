import sys
import re

with open("proto/ui.html", "r", encoding="utf-8") as f:
    content = f.read()

# 1. shiftDown
content = content.replace("let spaceDown=false", "let spaceDown=false, shiftDown=false")

# 2. snap function
snap_old = """function snap(cx,cy){
  if(snapModes.off||!pageData)return{x:cx,y:cy,t:null};
  const R=snapRadius/Math.max(zoom,0.1),R2=R*R,CR=closeRadius/Math.max(zoom,0.1);"""
snap_new = """function snap(cx,cy){
  if(snapModes.off||!pageData)return{x:cx,y:cy,t:null};
  if(shiftDown && mPts.length && (mode==="area"||mode==="dist"||mode==="path"||mode==="ref")){
    const c0=pdfToC(mPts[mPts.length-1].x, mPts[mPts.length-1].y);
    if(Math.abs(cx-c0.x)>Math.abs(cy-c0.y)){ cy=c0.y; }else{ cx=c0.x; }
  }
  const R=snapRadius/Math.max(zoom,0.1),R2=R*R,CR=closeRadius/Math.max(zoom,0.1);"""
content = content.replace(snap_old, snap_new)

# 3. keydown/keyup
kd_old = """document.addEventListener("keydown",e=>{"""
kd_new = """document.addEventListener("keydown",e=>{if(e.key==="Shift")shiftDown=true;"""
content = content.replace(kd_old, kd_new)

ku_old = """document.addEventListener("keyup",e=>{"""
ku_new = """document.addEventListener("keyup",e=>{if(e.key==="Shift")shiftDown=false;"""
content = content.replace(ku_old, ku_new)

# 4. Bigger Vertex (Hit Test & Highlight)
content = content.replace("const THR=Math.max(8,10/zoom);", "const THR=Math.max(12,16/zoom);")
content = content.replace("const hw=6/zoom;", "const hw=10/zoom;")

# 5. Loupe & Draw mPts inside handleMouseMove / redraw
hmm_end_new = """  redraw();
  if(!isPan && (mode==="area"||mode==="dist"||mode==="path"||mode==="ref"||(mode==="sel"&&dragState))){
    let l=document.getElementById("loupe");
    if(!l){
      l=document.createElement("canvas");l.id="loupe";l.width=200;l.height=200;
      l.style.cssText="position:fixed;border:2px solid var(--blue);border-radius:50%;pointer-events:none;display:none;z-index:9999;box-shadow:0 4px 12px rgba(0,0,0,0.5);background:#fff;image-rendering:pixelated";
      document.body.appendChild(l);
    }
    l.style.display="block";
    l.style.left=(e.clientX+24)+"px";
    l.style.top=(e.clientY+24)+"px";
    const lctx=l.getContext("2d");
    lctx.clearRect(0,0,200,200);
    const srcW=100,srcH=100;
    const r=ws.getBoundingClientRect();
    const sx=(e.clientX-r.left)*(canvas.width/r.width)-srcW/2;
    const sy=(e.clientY-r.top)*(canvas.height/r.height)-srcH/2;
    lctx.drawImage(canvas,sx,sy,srcW,srcH,0,0,200,200);
    lctx.strokeStyle="rgba(255,0,0,0.4)";lctx.lineWidth=1;
    lctx.beginPath();lctx.moveTo(100,0);lctx.lineTo(100,200);lctx.moveTo(0,100);lctx.lineTo(200,100);lctx.stroke();
    lctx.strokeStyle="#000";lctx.beginPath();lctx.arc(100,100,2,0,Math.PI*2);lctx.stroke();
  }else{
    const l=document.getElementById("loupe");if(l)l.style.display="none";
  }
}
ws.addEventListener("mousemove",e=>{"""
content = content.replace('snapLbl.style.display="none";}redraw();}\nws.addEventListener("mousemove",e=>{', 'snapLbl.style.display="none";}' + hmm_end_new)

# Hide Loupe on mouseleave and mouseup
content = content.replace('ws.addEventListener("mouseleave",()=>{', 'ws.addEventListener("mouseleave",()=>{const l=document.getElementById("loupe");if(l)l.style.display="none";')
content = content.replace('ws.addEventListener("mouseup",()=>{', 'ws.addEventListener("mouseup",()=>{const l=document.getElementById("loupe");if(l)l.style.display="none";')

# Draw mPts explicitly at the end of redraw()
mPts_draw = """  if(mPts.length && (mode==="area"||mode==="dist"||mode==="path"||mode==="ref"||mode==="calib")){
    ctx.save(); ctx.fillStyle="#fff"; ctx.strokeStyle="#0a84ff"; const hw=10/zoom; ctx.lineWidth=1.5/zoom;
    mPts.forEach(p=>{const c=pdfToC(p.x,p.y); ctx.fillRect(c.x-hw,c.y-hw,hw*2,hw*2); ctx.strokeRect(c.x-hw,c.y-hw,hw*2,hw*2);});
    ctx.restore();
  }
}
function selectedObj(sel){"""
content = re.sub(r'\}\nfunction selectedObj\(sel\)\{', mPts_draw, content)

with open("proto/ui.html", "w", encoding="utf-8") as f:
    f.write(content)

print("Patch completed successfully.")
