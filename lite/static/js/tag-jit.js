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

   SCALE-GATE-2026-07-04: extends the SAME per-page JIT gate with a SECOND
   check, run AFTER the tag check passes (gate ORDER: tag first, then
   scale) — a tagged-but-unscaled page also refuses to arm poly/dist/
   path/ref (count is EXEMPT — "นับจำนวนไม่ต้องมี scale"; the scale tool
   itself is NEVER gated, since it's the remedy — it's simply not in
   _JIT_MEASURE_TOOLS at all, same reason select/ann_* aren't gated).
   Scale-presence source: `getScaleForPage(pg)` (ui-lite.html) — thin
   wrapper over the real truth `PS[pg].scale` (see PSpage()/openCalib()/
   #cal-ok). Scale-COMMIT hook: `#cal-ok` (the "Set Scale" 2-point-draw ->
   modal -> OK flow) and `#su-ok` (the Page Setup dialog's manual
   pts_per_m entry) are the only two user-facing scale-commit points in
   ui-lite.html (grepped every `.scale=` assignment to confirm) — both are
   plain `.onclick=` PROPERTY assignments (not addEventListener), so they
   are wrapped the exact same way `setTool` is: capture the original
   handler, splice in a before/after scale-presence diff, call the
   original, then fire `_jitScaleCommitted()` if a scale that didn't exist
   before now does. `#cal-ok` additionally hardcodes `state.tool="poly"`
   directly (bypassing setTool) as pre-existing behavior; our hook runs
   AFTER that (post-original-handler) and re-invokes `setTool(pendingTool)`
   with the ACTUAL tool the user originally wanted — correctly overriding
   that hardcoded default as a side effect. Same zero-ui-lite.html-edits
   approach as the setTool wrap (own the load order, wrap onclick
   properties from here).
   ============================================================ */

var _JIT_MEASURE_TOOLS = { poly: 1, dist: 1, path: 1, ref: 1, count: 1 };
var _JIT_SCALE_EXEMPT  = { count: 1 }; // measure tools that do NOT need a scale ("นับจำนวนไม่ต้องมี scale")
var _jitPendingTool = null; // toolId the user tried to arm while blocked, or null

/* -- gate predicates -- */
function jitPageTagged(n) {
  if (typeof pageTags === "undefined" || !n) return true; // defensive: no doc yet, don't block
  return !!pageTags[n];
}
function jitPageScaled(n) {
  if (typeof getScaleForPage !== "function" || !n) return true; // defensive: no doc yet, don't block
  return !!getScaleForPage(n);
}

/* -- gate entry point — called from the setTool() wrap below.
   Gate ORDER: tag gate first (existing), then scale gate. -- */
function jitGuardTool(toolId) {
  if (!_JIT_MEASURE_TOOLS[toolId]) return true; // not a measure tool -> always allowed
  if (typeof caseId !== "undefined" && !caseId) return true; // no PDF open — nothing to gate yet
  var n = (typeof curPage !== "undefined") ? curPage : 0;
  if (!n) return true;
  if (!jitPageTagged(n)) {
    _jitPendingTool = toolId;
    _jitShowTagBanner(n);
    return false;
  }
  if (!_JIT_SCALE_EXEMPT[toolId] && !jitPageScaled(n)) {
    _jitPendingTool = toolId;
    _jitShowScaleBanner(n);
    return false;
  }
  _jitHideBanner();
  return true;
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

function _jitShowTagBanner(n) {
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
  // page-manager-redesign approach D, slice 2 (TAG-JIT-FIX): re-read curPage
  // AT CLICK TIME, never the closed-over `n` from render time — if the user
  // navigates away before tapping a chip, the stale page must NOT get tagged.
  el.querySelectorAll("[data-jit-tag]").forEach(function(chip) {
    chip.addEventListener("click", function() {
      var live = (typeof curPage !== "undefined") ? curPage : n;
      _jitCompleteTag(live, chip.dataset.jitTag);
    });
  });
}

/* -- SCALE-GATE-2026-07-04: second banner variant — tagged page, no scale.
   Second message, single action: switch straight to the scale tool. -- */
function _jitShowScaleBanner(n) {
  _jitInjectBannerDOM();
  var el = document.getElementById("jit-banner");
  if (!el) return;
  el.innerHTML = '<span style="color:var(--warn,#ffb454);font-weight:600">⚠ หน้านี้ยังไม่ตั้งมาตราส่วน</span>' +
    '<span class="ov-tag-chip ov-tag-floor" id="jit-set-scale-btn" style="cursor:pointer">ตั้ง scale เลย</span>';
  el.style.display = "flex";
  var btn = document.getElementById("jit-set-scale-btn");
  if (btn) btn.addEventListener("click", function() {
    _jitHideBanner();
    // 'scale' is not in _JIT_MEASURE_TOOLS -> jitGuardTool('scale') always
    // returns true -> arms immediately, no re-entrant gating.
    if (typeof setTool === "function") setTool("scale");
  });
}

function _jitHideBanner() {
  var el = document.getElementById("jit-banner");
  if (el) el.style.display = "none";
}

/* -- called once a scale-commit point (see _jitWrapScaleCommit below)
   detects the current page went from unscaled -> scaled. Re-arms the
   tool the user originally tried to use, exactly once. -- */
function _jitScaleCommitted() {
  _jitHideBanner();
  if (_jitPendingTool && typeof setTool === "function") {
    var t = _jitPendingTool; _jitPendingTool = null;
    setTool(t); // re-invoke the (wrapped) setTool — passes both gates now
  }
}

/* -- page-manager-redesign approach D, slice 2 (TAG-JIT-FIX) bug (b):
   hide the banner (and clear any pending-tool arm request) on every page
   navigation, so a stale banner from a page the user has left can never
   be tapped. Wraps the REAL global afterPage() (called by loadPage() in
   page-renderer.js on every navigation branch) — no ui-lite.html edit. */
function _jitTryWrapAfterPage() {
  if (typeof window.afterPage !== "function") return false;
  if (window.afterPage.__jitWrapped) return true;
  var _origAfterPage = window.afterPage;
  window.afterPage = function() {
    var ret = _origAfterPage.apply(this, arguments);
    _jitHideBanner();
    _jitPendingTool = null;
    return ret;
  };
  window.afterPage.__jitWrapped = true;
  return true;
}

/* -- setTool wrap, extracted so bootstrap can retry it independently. -- */
function _jitTryWrapSetTool() {
  if (typeof setTool !== "function") return false;
  if (!setTool.__jitWrapped) {
    var _origSetTool = setTool;
    setTool = function(t) {
      if (!jitGuardTool(t)) return; // refuse to arm; banner already shown
      _origSetTool(t);
    };
    setTool.__jitWrapped = true;
  }
  return true;
}

/* -- bootstrap — wraps setTool(), the two scale-commit buttons, and
   afterPage(), each independently idempotent (own .__xWrapped guard).
   Same safe-timing idiom as overview-setup.js's _lovsBootstrap: this
   script is injected dynamically AFTER DOMContentLoaded may already have
   fired, so setTimeout(0) is used to let in-progress scripts finish when
   that's the case; otherwise wait for the event.

   BUG-FIX (c): window.__jitWrapped used to be set to true BEFORE
   confirming setTool actually got wrapped — a bootstrap race (setTool not
   yet defined) could leave setTool permanently unwrapped while
   __jitWrapped lied that the gate was live. Now __jitWrapped is set ONLY
   after a successful setTool wrap; whichever piece(s) aren't ready yet
   (setTool / #cal-ok+#su-ok / afterPage) retry on a 5x200ms ladder. */
function _jitBootstrap(attempt) {
  attempt = attempt || 0;
  var setToolOk = _jitTryWrapSetTool();
  var scaleOk   = _jitWrapScaleCommit();
  var afterOk   = _jitTryWrapAfterPage();
  if (setToolOk) window.__jitWrapped = true;
  if ((!setToolOk || !scaleOk || !afterOk) && attempt < 5) {
    setTimeout(function() { _jitBootstrap(attempt + 1); }, 200);
  }
}

/* -- SCALE-GATE-2026-07-04: wrap the two user-facing scale-commit points.
   Both are plain `.onclick=` PROPERTY assignments in ui-lite.html (not
   addEventListener), so they're wrapped the same way as setTool: capture
   the original handler, diff scale-presence before/after calling it, fire
   _jitScaleCommitted() only on a genuine none->some transition (so an
   invalid #cal-ok input, which its own handler alert()s+returns early
   without setting a scale, correctly does NOT retrigger).

   BUG-FIX (c): returns true only when BOTH buttons end up wrapped (either
   just now or already, from a prior attempt) — false if either #cal-ok or
   #su-ok isn't in the DOM yet / has no onclick yet, so _jitBootstrap's
   retry ladder can try again instead of silently giving up forever. -- */
function _jitWrapScaleCommit() {
  var allOk = true;
  ["cal-ok", "su-ok"].forEach(function(id) {
    var btn = document.getElementById(id);
    if (!btn) { allOk = false; return; }
    if (btn.__jitScaleWrapped) return; // already wrapped -> fine
    var _origOnClick = btn.onclick;
    if (typeof _origOnClick !== "function") { allOk = false; return; }
    btn.onclick = function(e) {
      var n = (typeof curPage !== "undefined") ? curPage : 0;
      var hadScaleBefore = n ? jitPageScaled(n) : true;
      var ret = _origOnClick.call(this, e);
      var hasScaleNow = n ? jitPageScaled(n) : true;
      if (n && !hadScaleBefore && hasScaleNow) _jitScaleCommitted();
      return ret;
    };
    btn.__jitScaleWrapped = true;
  });
  return allOk;
}

if (document.readyState === "loading") {
  window.addEventListener("DOMContentLoaded", _jitBootstrap);
} else {
  setTimeout(_jitBootstrap, 0);
}
