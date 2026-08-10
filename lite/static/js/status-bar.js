/* ============================================================
   STATUS-BAR — bottom shell status bar (SHELL-STATUS, 2026-08-10).
   docs/status/PHASE_INDEX.md "sprint cards SHELL-2026-08-10".
   Mockup: lite/sandbox/mockup-main-shell.html (rev.3) .status block.

   Plain-globals module, self-injecting (no IIFE, no export, no
   bundler — matches the lite static/js convention). Loaded as the LAST
   <script src> in ui-lite.html, i.e. AFTER the inline <script> block
   that declares state/curPage/pageCount/catOf/scaleN/getScaleForPage/
   pageNames and AFTER object-agg.js — so every dependency below already
   exists by the time this file runs. The DOMContentLoaded + retry-ladder
   bootstrap (same discipline as tag-jit.js's _jitBootstrap) is kept
   anyway for load-order robustness if the script tag ever moves.

   READ-ONLY over app state: never mutates PS / state / pageTags / LAYERS
   — only wraps window.draw() (post-hook, does not change its return
   value or behavior) and wires ONE click handler that calls the already-
   shipped guarded entry point window.pmOpenManager().

   7 cells (left -> right, spec order):
     1. หน้า N/M · <ชื่อชั้น>      click -> window.pmOpenManager()
     2. ⚖ scale ✓ / ยังไม่ตั้ง
     3. เครื่องมือ (Thai tool name)
     4. วาดเป็น: ■ <active layer name>   (display only — reads layer NAME
        for display, never for calculation; see catOf() below)
     5. 🧲 Snap เปิด/ปิด
     6. ● ยังไม่บันทึก / ✓ บันทึกแล้ว
     7. (right-aligned) สุทธิชั้นนี้ <net> ตร.ม.  — INVARIANTS.md I2
        consumer. Net = gfa - ded for the CURRENT floor, computed ONLY
        via the ObjectAgg public API (byFloorRole over objectTuples()),
        never a private re-walk of PS. "—" when the current page has no
        scale, is not a floor page, or the floor has no gfa/ded objects
        at all (see _sbFloorNet doc below).

   Hidden entirely in focus mode via `body.focus #lite-status{display:none}`
   (injected CSS — ui-lite.html's own `body.focus #picker,...` rule is
   never touched).
   ============================================================ */

/* ---- cell 3: Thai tool names (separate from the English TOOLNAME map
   ui-lite.html's HUD already uses — that map is a forbidden-adjacent
   inline global, this module never edits it, it just keeps its own). */
var SB_TOOLNAME_TH = {
  select: "เลือก", scale: "ตั้งสเกล", poly: "วัดพื้นที่", dist: "ระยะ",
  path: "ระยะต่อเนื่อง", ref: "เส้นอ้างอิง", count: "นับจุด",
  ann_text: "ตัวหนังสือ", ann_comment: "คอมเมนต์", ann_arrow: "ลูกศร",
  ann_highlight: "ไฮไลต์", ann_rect: "กรอบสี่เหลี่ยม",
  ann_circle: "กรอบวงกลม", ann_cloud: "กรอบเมฆ"
};

/* ---- cell 7: I2 rollup consumer. Registered in tests/INVARIANTS.md I2
   consumer list alongside computeSummary/buildExportData/... (same
   sprint, per the I2 ritual: "ทุก rollup consumer == Σ ค่าป้าย object").
   Net for the CURRENT page's floor bucket, via ObjectAgg's public API
   only (floorKeyOfPage + objectTuples + byFloorRole) — never a private
   PS walk. Returns null (caller renders "—") when: ObjectAgg/curPage
   unavailable, the current page has no scale, the current page is not a
   floor-tagged page (floorKeyOfPage -> ""), or the floor bucket has no
   gfa/ded objects at all (row undefined -- distinct from a real 0). */
function _sbFloorNet() {
  if (typeof ObjectAgg === "undefined") return null;
  if (typeof curPage === "undefined" || typeof PS === "undefined") return null;
  var s = (typeof getScaleForPage === "function") ? getScaleForPage(curPage) : null;
  if (!s) return null;
  var fk = ObjectAgg.floorKeyOfPage(curPage);
  if (!fk) return null;
  var bfr = ObjectAgg.byFloorRole(ObjectAgg.objectTuples());
  var row = bfr[fk];
  if (!row) return null;
  var gfa = (row.gfa && row.gfa.area) || 0;
  var ded = (row.ded && row.ded.area) || 0;
  return gfa - ded;
}
function _sbFloorNetText() {
  var v = _sbFloorNet();
  return (v == null) ? "—" : (v.toFixed(2) + " ตร.ม.");
}

/* ---- CSS (injected once; matches #app's own dark-theme vars) ---- */
var SB_CSS =
  "#lite-status{flex:0 0 26px;height:26px;display:flex;align-items:center;" +
  "background:var(--panel);border-top:1px solid var(--line);font-size:11.5px;" +
  "color:var(--muted);overflow:hidden;white-space:nowrap;}" +
  "#lite-status .sb-cell{padding:0 11px;height:100%;display:flex;align-items:center;" +
  "gap:6px;border-right:1px solid #1b2230;flex:0 0 auto;}" +
  "#lite-status .sb-cell.sb-click{cursor:pointer;}" +
  "#lite-status .sb-cell.sb-click:hover{background:#1b2230;}" +
  "#lite-status b{color:var(--ink);font-weight:500;}" +
  "#lite-status .sb-ok{color:var(--good);}" +
  "#lite-status .sb-warn{color:var(--warn);}" +
  "#lite-status .sb-sw{width:9px;height:9px;border-radius:2px;flex:0 0 auto;display:inline-block;}" +
  "#lite-status .sb-spacer{flex:1;}" +
  "#lite-status .sb-net{margin-left:auto;font-weight:500;}" +
  "body.focus #lite-status{display:none;}";

/* ---- DOM build (idempotent) ---- */
function _sbEnsureDom() {
  if (document.getElementById("lite-status")) return true;
  var app = document.getElementById("app");
  if (!app) return false;

  var style = document.createElement("style");
  style.id = "sb-style";
  style.textContent = SB_CSS;
  document.head.appendChild(style);

  var bar = document.createElement("div");
  bar.id = "lite-status";
  bar.innerHTML =
    '<span class="sb-cell sb-click" id="sb-page"></span>' +
    '<span class="sb-cell" id="sb-scale"></span>' +
    '<span class="sb-cell" id="sb-tool"></span>' +
    '<span class="sb-cell" id="sb-layer"></span>' +
    '<span class="sb-cell" id="sb-snap"></span>' +
    '<span class="sb-cell" id="sb-dirty"></span>' +
    '<span class="sb-spacer"></span>' +
    '<span class="sb-cell sb-net" id="sb-net"></span>';
  app.appendChild(bar);

  document.getElementById("sb-page").onclick = function() {
    if (typeof window.pmOpenManager === "function") window.pmOpenManager();
  };
  return true;
}

/* ---- refresh: recompute a cache string, touch DOM only on change
   (draw() runs per-frame during pan/zoom — avoid needless reflow). ---- */
var _sbLastCache = null;
function _sbBuild() {
  var hasDoc = typeof caseId !== "undefined" && !!caseId;
  var cp = (typeof curPage !== "undefined") ? curPage : 1;
  var pc = (typeof pageCount !== "undefined") ? pageCount : 0;
  var nm = (typeof pageNames !== "undefined" && pageNames[cp]) ? (" · " + pageNames[cp]) : "";
  var pageTxt = hasDoc ? ("หน้า <b>" + cp + "</b>/" + pc + nm) : "—";

  var s = (typeof getScaleForPage === "function") ? getScaleForPage(cp) : null;
  var scaleTxt = (s && typeof scaleN === "function")
    ? ('<span class="sb-ok">⚖ 1:' + scaleN(s) + ' ✓</span>')
    : '<span class="sb-warn">⚖ ยังไม่ตั้ง</span>';

  var tool = (typeof state !== "undefined") ? state.tool : "select";
  var toolTxt = "เครื่องมือ: <b>" + (SB_TOOLNAME_TH[tool] || tool) + "</b>";

  var cat = (typeof catOf === "function" && typeof state !== "undefined")
    ? (catOf(state.activeCat) || { color: "#888", name: "—" }) : { color: "#888", name: "—" };
  var layerTxt = 'วาดเป็น: <span class="sb-sw" style="background:' + cat.color + '"></span> <b>' + cat.name + '</b>';

  var snapOn = typeof state !== "undefined" && !!state.snapOn;
  var snapTxt = "🧲 " + (snapOn ? '<span class="sb-ok">เปิด</span>' : '<span class="sb-warn">ปิด</span>');

  var dirty = typeof state !== "undefined" && !!state.dirty;
  var dirtyTxt = dirty ? '<span class="sb-warn">● ยังไม่บันทึก</span>' : '<span class="sb-ok">✓ บันทึกแล้ว</span>';

  var netVal = _sbFloorNet();
  var netTxt = "สุทธิชั้นนี้ <b>" + _sbFloorNetText() + "</b>";

  return {
    cache: [hasDoc, cp, pc, nm, s ? s.pts_per_m : null, tool, cat.id, cat.color, snapOn, dirty, netVal].join("|"),
    pageTxt: pageTxt, scaleTxt: scaleTxt, toolTxt: toolTxt, layerTxt: layerTxt,
    snapTxt: snapTxt, dirtyTxt: dirtyTxt, netTxt: netTxt
  };
}

function _sbRefresh() {
  if (!_sbEnsureDom()) return;
  var b = _sbBuild();
  if (b.cache === _sbLastCache) return;
  _sbLastCache = b.cache;
  document.getElementById("sb-page").innerHTML = b.pageTxt;
  document.getElementById("sb-scale").innerHTML = b.scaleTxt;
  document.getElementById("sb-tool").innerHTML = b.toolTxt;
  document.getElementById("sb-layer").innerHTML = b.layerTxt;
  document.getElementById("sb-snap").innerHTML = b.snapTxt;
  document.getElementById("sb-dirty").innerHTML = b.dirtyTxt;
  document.getElementById("sb-net").innerHTML = b.netTxt;
}

/* ---- bootstrap: wrap window.draw() so every draw() call (pan/zoom/tool
   switch/undo/...) also refreshes the status bar. Same idiom as
   tag-jit.js's _jitBootstrap: idempotent per-piece (.__sbWrapped guard),
   5x200ms retry ladder for whichever piece isn't ready yet. ---- */
function _sbTryWrapDraw() {
  if (typeof window.draw !== "function") return false;
  if (window.draw.__sbWrapped) return true;
  var _origDraw = window.draw;
  var wrapped = function() {
    var ret = _origDraw.apply(this, arguments);
    _sbRefresh();
    return ret;
  };
  wrapped.__sbWrapped = true;
  window.draw = wrapped;
  return true;
}

function _sbBootstrap(attempt) {
  attempt = attempt || 0;
  var built = _sbEnsureDom();
  var wrapped = _sbTryWrapDraw();
  if (built) _sbRefresh();
  if ((!built || !wrapped) && attempt < 5) {
    setTimeout(function() { _sbBootstrap(attempt + 1); }, 200);
  }
}

if (document.readyState === "loading") {
  window.addEventListener("DOMContentLoaded", function() { _sbBootstrap(0); });
} else {
  setTimeout(function() { _sbBootstrap(0); }, 0);
}
