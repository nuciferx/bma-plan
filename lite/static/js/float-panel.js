/* ============================================================
   FLOAT-PANEL — Photoshop-style floating palette wrapper for #picker
   (SHELL-FLOAT, 2026-08-10). docs/status/PHASE_INDEX.md "sprint cards
   SHELL-2026-08-10". Mockup: lite/sandbox/mockup-main-shell.html (rev.3)
   .fpal block. Research base: docs/invent/fullscreen-canvas-ui.md
   (GO 2026-05-19) + proto's bmaPlan.widgetPlacement.v1 precedent.

   Plain-globals module, self-injecting (no IIFE, no export, no bundler).
   WRAPS the EXISTING #picker element WITHOUT touching its inner content
   or buildPicker(): buildPicker() (layer-tree.js) and buildPagePicker()
   (page-folder-layers.js) both only ever write to #catlist's innerHTML
   (verified by reading both before writing this file) — #picker itself
   and its static `.h` toolbar row are never touched by either render
   path, so inserting a NEW header as #picker's first child is safe and
   survives every re-render.

   Behavior added (content untouched):
     - drag the new header (pointer events) to move #picker
     - clamp fully inside #stage bounds, on drag AND on window resize
     - ▾ collapse: hides the original `.h` toolbar row + #catlist (only
       those two known elements — see _fpSetCollapsed's doc for why)
     - ✕ hide: hides #picker entirely, shows a small edge restore tab
       "🗂 เลเยอร์" (proto restore-tab pattern) that brings it back
     - double-click header: reset POSITION only (not collapsed/hidden)
       to the default (10,54) — same spot #picker's own CSS already
       places it at today, so a first-ever visit looks byte-identical
     - persists {x,y,collapsed,hidden} in localStorage
       'bmaLite.floatPanel.v1' (try/catch; restored + re-clamped on load
       so a saved position from a larger window never restores off-screen)

   Old fixed-position CSS for #picker (`top:54px;left:10px` in
   ui-lite.html's <style> block) is neutralized here via inline
   style.left/style.top (higher specificity than the stylesheet rule) —
   ui-lite.html's CSS is never edited.

   z-index: #picker's existing z-index:20 (ui-lite.html CSS) is left
   untouched — already well below every overlay (.overlay=80, #modal=90,
   #pm-overlay/cheatsheet/.objmenu=200+), so the floating panel stays
   under any modal/overlay exactly like it does today.

   Focus mode: `body.focus #picker{display:none}` already exists in
   ui-lite.html's CSS (id-selector on #picker itself) — wrapping it with
   a child header does not change that; #picker is still hidden in full
   focus mode.
   ============================================================ */

var FP_KEY = "bmaLite.floatPanel.v1";
var FP_DEFAULT = { x: 10, y: 54 }; // matches #picker's existing CSS top/left

var FP_CSS =
  "#fp-header{display:flex;align-items:center;gap:6px;padding:5px 7px;margin:-8px -8px 8px -8px;" +
  "background:rgba(10,12,16,.85);border-bottom:1px solid var(--line);border-radius:10px 10px 0 0;" +
  "cursor:grab;font-size:11px;color:var(--muted);user-select:none;touch-action:none;}" +
  "#fp-header:active{cursor:grabbing;}" +
  "#fp-header .fp-grip{letter-spacing:-1px;color:#4a5468;}" +
  "#fp-header .fp-title{flex:1;color:var(--ink);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}" +
  "#fp-header button{background:transparent;border:0;color:var(--muted);cursor:pointer;font-size:12px;padding:0 3px;}" +
  "#fp-header button:hover{color:var(--ink);}" +
  "#fp-tab{position:absolute;z-index:20;display:none;align-items:center;" +
  "background:rgba(20,24,32,.92);border:1px solid var(--line);border-radius:8px;padding:6px 10px;" +
  "font-size:12px;color:var(--ink);cursor:pointer;}" +
  "#fp-tab:hover{background:#222a37;}";

/* ---- clamp {x,y} so #picker (at its CURRENT rendered size) stays fully
   inside #stage bounds. Re-queries live sizes every call — cheap, called
   only on drag/resize/restore, never per animation frame. ---- */
function _fpClamp(x, y, picker, stage) {
  if (!picker || !stage) return { x: x, y: y };
  var sw = stage.clientWidth, sh = stage.clientHeight;
  var w = picker.offsetWidth || 190, h = picker.offsetHeight || 40;
  var maxX = Math.max(0, sw - w), maxY = Math.max(0, sh - h);
  return { x: Math.min(Math.max(x, 0), maxX), y: Math.min(Math.max(y, 0), maxY) };
}

function _fpApplyPos(picker, x, y) {
  picker.style.position = "absolute";
  picker.style.left = x + "px";
  picker.style.top = y + "px";
  picker.style.right = "auto";
}

/* ---- persistence (try/catch — quota/disabled localStorage never throws
   into the caller) ---- */
function _fpSave(picker) {
  try {
    var x = parseFloat(picker.style.left) || 0;
    var y = parseFloat(picker.style.top) || 0;
    var data = { x: x, y: y, collapsed: !!picker._fpCollapsed, hidden: !!picker._fpHidden };
    localStorage.setItem(FP_KEY, JSON.stringify(data));
  } catch (e) { /* ignore */ }
}
function _fpLoad() {
  try {
    var raw = localStorage.getItem(FP_KEY);
    if (!raw) return null;
    var d = JSON.parse(raw);
    if (!d || typeof d.x !== "number" || typeof d.y !== "number") return null;
    return d;
  } catch (e) { return null; }
}

/* ---- collapse: hide the pre-existing `.h` toolbar row + #catlist
   together (#picker has no separate "footer" element in the real app,
   unlike the mockup — `.h` plays that role here). Deliberately targets
   ONLY those two known elements, NOT "every child except header": other
   modules append their OWN children to #picker with their own visibility
   rules (e.g. empty-state.js's #ls-empty-state, shown/hidden by
   updateEmptyState() based on whether a PDF is open) — blindly clearing
   style.display on every child would strip an unrelated module's inline
   override and let its CSS default (display:flex) re-show it, fighting
   that module's own state. */
function _fpSetCollapsed(picker, header, collapsed) {
  var targets = [];
  var toolbar = picker.querySelector(".h");
  if (toolbar) targets.push(toolbar);
  var catlist = document.getElementById("catlist");
  if (catlist) targets.push(catlist);
  targets.forEach(function(el) { el.style.display = collapsed ? "none" : ""; });
  var btn = document.getElementById("fp-collapse");
  if (btn) btn.textContent = collapsed ? "▸" : "▾";
  picker._fpCollapsed = collapsed;
}

function _fpSetHidden(picker, tab, hidden) {
  picker.style.display = hidden ? "none" : "";
  tab.style.display = hidden ? "flex" : "none";
  picker._fpHidden = hidden;
}

/* ---- drag: pointer events on the header only; clicking a header BUTTON
   (collapse/hide) must not also start a drag. ---- */
function _fpIsButton(target) {
  return !!(target && target.closest && target.closest("button"));
}
function _fpStartDrag(e, picker, stage) {
  if (_fpIsButton(e.target)) return;
  e.preventDefault();
  var startPX = e.clientX, startPY = e.clientY;
  var startLeft = parseFloat(picker.style.left) || 0;
  var startTop = parseFloat(picker.style.top) || 0;
  function onMove(ev) {
    var dx = ev.clientX - startPX, dy = ev.clientY - startPY;
    var pos = _fpClamp(startLeft + dx, startTop + dy, picker, stage);
    _fpApplyPos(picker, pos.x, pos.y);
  }
  function onUp() {
    document.removeEventListener("pointermove", onMove);
    document.removeEventListener("pointerup", onUp);
    _fpSave(picker);
  }
  document.addEventListener("pointermove", onMove);
  document.addEventListener("pointerup", onUp);
}

/* ---- DOM build (idempotent) + event wiring + restore-from-localStorage ---- */
function _fpEnsureDom() {
  var picker = document.getElementById("picker");
  var stage = document.getElementById("stage");
  if (!picker || !stage) return false;
  if (document.getElementById("fp-header")) return true; // already built

  var style = document.createElement("style");
  style.id = "fp-style";
  style.textContent = FP_CSS;
  document.head.appendChild(style);

  var header = document.createElement("div");
  header.id = "fp-header";
  header.title = "ลากเพื่อย้าย — ดับเบิลคลิก = รีเซ็ตตำแหน่ง";
  header.innerHTML =
    '<span class="fp-grip">⠿</span>' +
    '<span class="fp-title">กำลังวัดอะไร</span>' +
    '<button type="button" id="fp-collapse" title="พับ/กาง">▾</button>' +
    '<button type="button" id="fp-hide" title="ซ่อน (⇧F ซ่อนทั้งหมดได้เหมือนเดิม)">✕</button>';
  picker.insertBefore(header, picker.firstChild);

  var tab = document.createElement("div");
  tab.id = "fp-tab";
  tab.title = "แสดง panel เลเยอร์";
  tab.textContent = "🗂 เลเยอร์";
  stage.appendChild(tab);

  header.addEventListener("pointerdown", function(e) { _fpStartDrag(e, picker, stage); });
  header.addEventListener("dblclick", function(e) {
    if (_fpIsButton(e.target)) return;
    var pos = _fpClamp(FP_DEFAULT.x, FP_DEFAULT.y, picker, stage);
    _fpApplyPos(picker, pos.x, pos.y);
    _fpSave(picker);
  });
  document.getElementById("fp-collapse").addEventListener("click", function() {
    _fpSetCollapsed(picker, header, !picker._fpCollapsed);
    _fpSave(picker);
  });
  document.getElementById("fp-hide").addEventListener("click", function() {
    _fpSetHidden(picker, tab, true);
    _fpSave(picker);
  });
  tab.addEventListener("click", function() {
    _fpSetHidden(picker, tab, false);
    _fpSave(picker);
  });
  window.addEventListener("resize", function() {
    var x = parseFloat(picker.style.left) || 0, y = parseFloat(picker.style.top) || 0;
    var pos = _fpClamp(x, y, picker, stage);
    _fpApplyPos(picker, pos.x, pos.y);
  });

  var saved = _fpLoad();
  var pos = saved ? _fpClamp(saved.x, saved.y, picker, stage) : _fpClamp(FP_DEFAULT.x, FP_DEFAULT.y, picker, stage);
  _fpApplyPos(picker, pos.x, pos.y);
  _fpSetCollapsed(picker, header, saved ? !!saved.collapsed : false);
  _fpSetHidden(picker, tab, saved ? !!saved.hidden : false);

  return true;
}

/* ---- bootstrap: #picker/#stage are static markup already parsed by the
   time this <script> (last tag before </body>) runs, so this normally
   succeeds on attempt 0; the DOMContentLoaded guard + short retry is
   kept only for load-order robustness if the tag ever moves. ---- */
function _fpBootstrap(attempt) {
  attempt = attempt || 0;
  if (!_fpEnsureDom() && attempt < 5) {
    setTimeout(function() { _fpBootstrap(attempt + 1); }, 200);
  }
}

if (document.readyState === "loading") {
  window.addEventListener("DOMContentLoaded", function() { _fpBootstrap(0); });
} else {
  setTimeout(function() { _fpBootstrap(0); }, 0);
}
