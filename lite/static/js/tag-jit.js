/* ============================================================
   TAG-JIT — Just-In-Time per-page tag gate for measure tools
   (INV-2026-07-04-002 slice 4/4).
   Plain-globals module. No IIFE, no export, no bundler.
   Dynamically loaded from page-folder-layers.js (same LOVS-1 dynamic-
   inject pattern as overview-grid.js/overview-setup.js), AFTER
   overview-setup.js so its always-injected `.ov-tag-chip.ov-tag-*` CSS
   (from _lovsInjectCSS, run unconditionally at overview-setup.js's own
   bootstrap regardless of whether the wizard is ever opened) is already
   in <head> by the time the banner is first rendered. This is the ONE
   cross-module CSS dependency this file has — no CSS of its own.

   Replaces the wizard's SET gate (removed from overview-setup.js in the
   SAME diff — see that file's `_lovsWireNav`): instead of blocking the
   wizard's Step-1 "Next" button at 0 tagged pages, every MEASURE tool
   now refuses to arm on an untagged page and shows a 1-tap banner
   instead. The wizard stays fully usable (optional, not gone).

   Arming-path survey (ALL of them funnel through ui-lite.html's single
   `setTool(t)` function — confirmed by reading every call site):
     1. Menu dropdown clicks: `.dd .item[data-tool]` -> setTool(dataset.tool)
        (covers select/scale/poly/dist/path/ref/count/ann_text/ann_comment/
        ann_arrow/ann_highlight/ann_rect/ann_circle/ann_cloud)
     2. Central keydown handler: Shift+letter -> ann_* ; 'a'/'A' -> poly ;
        Shift+D -> path ; v/s/d/r/n map -> select/scale/dist/ref/count
     3. NOT via setTool (confirmed unaffected, no wrap needed):
        pan ('h'/'H' toggles state.panTool directly; space-hold pan),
        zoom buttons (zin/zout/zfit), verifyScaleStart() (scale
        verification, not a measure tool), page nav, undo/redo, etc.
   Because every path funnels through one function, this file wraps
   `setTool` ONCE (same idiom as liteSetTag/buildPicker/openOv elsewhere)
   instead of touching N separate call sites or editing ui-lite.html.

   Measure tools (JIT-gated): poly, dist, path, ref, count.
   NOT gated (arm immediately regardless of tag): select (edits existing
   objects, not measurement), scale (calibration — precedes tagging in
   the normal workflow), all ann_* (annotation/markup, not measurement).

   Public API:
     jitPageTagged(n)      — true if page n carries a non-empty tag
     jitGuardTool(toolId)  — true = allowed to arm; false = blocked
                             (banner shown as a side effect)
   Globals required (ui-lite.html / page-folder-layers.js, read-only):
     pageTags, pageFloorNum, pageFloorKind, PAGE_TAGS, curPage, caseId,
     state, setTool (wrapped), pushUndo(), liteSetTag(n,val),
     liteSetFloorKind(n,kind), liteSetFloorNum(n,num), buildPicker(),
     reseedActivePageFolders()
   ============================================================ */

var _JIT_MEASURE_TOOLS = { poly: 1, dist: 1, path: 1, ref: 1, count: 1 };
var _jitPendingTool = null; // toolId the user tried to arm while blocked, or null

/* -- gate predicate -- */
function jitPageTagged(n) {
  if (typeof pageTags === "undefined" || !n) return true; // defensive: no doc yet, don't block
  return !!pageTags[n];
}

/* -- gate entry point — called from the setTool() wrap below -- */
function jitGuardTool(toolId) {
  if (!_JIT_MEASURE_TOOLS[toolId]) return true; // not a measure tool -> always allowed
  if (typeof caseId !== "undefined" && !caseId) return true; // no PDF open — nothing to gate yet
  var n = (typeof curPage !== "undefined") ? curPage : 0;
  if (!n) return true;
  if (jitPageTagged(n)) { _jitHideBanner(); return true; }
  _jitPendingTool = toolId;
  _jitShowBanner(n);
  return false;
}

/* -- next available floor number (1-tap floor default) --
   Mirrors the spirit of overview-setup.js's sequential numbering (next
   free slot) without the basement-descending/roof-heuristic — this is a
   ONE-page quick-default, not a batch renumber. */
function _jitNextFloorNum() {
  var max = 0;
  if (typeof pageFloorNum !== "undefined") {
    Object.keys(pageFloorNum).forEach(function(k) {
      var v = pageFloorNum[k];
      if (typeof v === "number" && v > max) max = v;
    });
  }
  return max + 1;
}

/* -- 1-tap tag completion: same writers + ONE pushUndo, then reseed +
   retry the tool the user originally tried to arm. -- */
function _jitCompleteTag(n, tag) {
  if (typeof pushUndo === "function") pushUndo();
  liteSetTag(n, tag);
  if (tag === "floor") {
    // 1-tap default: normal kind + next free floor number, so a single
    // tap is always enough to produce a real PF_floor_<N> folder.
    liteSetFloorKind(n, "normal");
    liteSetFloorNum(n, _jitNextFloorNum());
  }
  if (typeof reseedActivePageFolders === "function") reseedActivePageFolders();
  if (typeof buildPicker === "function") buildPicker();
  _jitHideBanner();
  if (_jitPendingTool && typeof setTool === "function") {
    var t = _jitPendingTool; _jitPendingTool = null;
    setTool(t); // re-invoke the (wrapped) setTool — passes the gate now
  }
}

/* -- banner DOM (idempotent injection into #stage, no ui-lite.html edit) -- */
function _jitInjectBannerDOM() {
  if (document.getElementById("jit-banner")) return;
  var stage = document.getElementById("stage");
  if (!stage) return;
  var el = document.createElement("div");
  el.id = "jit-banner";
  el.style.cssText = "position:absolute;left:50%;bottom:14px;transform:translateX(-50%);" +
    "display:none;align-items:center;gap:8px;z-index:60;background:#1a1d24ee;" +
    "border:1px solid var(--warn,#ffb454);border-radius:8px;padding:8px 12px;" +
    "font-size:12px;color:var(--ink,#e7ecf3);box-shadow:0 6px 20px rgba(0,0,0,.5)";
  stage.appendChild(el);
}

function _jitShowBanner(n) {
  _jitInjectBannerDOM();
  var el = document.getElementById("jit-banner");
  if (!el) return;
  var pt = (typeof PAGE_TAGS !== "undefined") ? PAGE_TAGS : {};
  var tags = ["site", "floor", "plan", "parking", "amenity", "detail"];
  var h = '<span style="color:var(--warn,#ffb454);font-weight:600">⚠ หน้านี้ยังไม่ได้แท็ก — แตะเพื่อแท็กแล้ววัดต่อ:</span>';
  tags.forEach(function(t) {
    h += '<span class="ov-tag-chip ov-tag-' + t + '" data-jit-tag="' + t + '" style="cursor:pointer">' + (pt[t] || t) + '</span>';
  });
  el.innerHTML = h;
  el.style.display = "flex";
  el.querySelectorAll("[data-jit-tag]").forEach(function(chip) {
    chip.addEventListener("click", function() { _jitCompleteTag(n, chip.dataset.jitTag); });
  });
}

function _jitHideBanner() {
  var el = document.getElementById("jit-banner");
  if (el) el.style.display = "none";
}

/* -- bootstrap — wraps setTool() exactly once.
   Same safe-timing idiom as overview-setup.js's _lovsBootstrap: this
   script is injected dynamically AFTER DOMContentLoaded may already have
   fired, so setTimeout(0) is used to let in-progress scripts finish when
   that's the case; otherwise wait for the event. Guard via
   window.__jitWrapped for idempotency. */
function _jitBootstrap() {
  if (window.__jitWrapped) return;
  window.__jitWrapped = true;
  if (typeof setTool === "function" && !setTool.__jitWrapped) {
    var _origSetTool = setTool;
    setTool = function(t) {
      if (!jitGuardTool(t)) return; // refuse to arm; banner already shown
      _origSetTool(t);
    };
    setTool.__jitWrapped = true;
  }
}

if (document.readyState === "loading") {
  window.addEventListener("DOMContentLoaded", _jitBootstrap);
} else {
  setTimeout(_jitBootstrap, 0);
}
