/* ============================================================
   LAYER-TARGET-UI — draw-target chip + canvas edge tint +
   ◉ make-current marker + reconcile banner
   (INV-20260703-layer-redesign, sub-sprint B-ui).
   Plain-globals module. No IIFE-exported API needed by callers;
   wrapped in an IIFE only to keep its own helpers off the global
   scope. Loaded AFTER object-agg.js / layer-tree.js /
   page-folder-layers.js, BEFORE (well — via DOMContentLoaded, so
   order-independent for wrapping). DOM-injected: ui-lite.html is
   untouched except for the one <script> tag that loads this file.

   Reads (all typeof/window-guarded):
     state, curPage, layerById, buildPicker, draw, loadPage,
     liteSetTag, loadProto, isDrawTool, pushUndo          (inline / modules)
     window.ObjectAgg.{floorKeyOfPage, floorKeyLabel,
                       detectDivergence}                   (object-agg.js, A-model)

   NEVER touches measure-engine.js / polyAreaM2 / pdfToC / cToPdf / RS.
   The edge tint is a pure DOM overlay (pointer-events:none, no canvas
   context) so it has ZERO effect on coordinates or hit-testing.
   The banner's [ตามหน้า] only UNSETS the optional layer.floorKey field
   (additive-only schema — nothing renamed/removed).

   Public (for tests + programmatic refresh):
     window.LayerTargetUI = { sync, reconcile, dismissed }
   ============================================================ */
(function () {
  "use strict";

  /* in-memory only (NOT persisted): dismissed reconcile prompts,
     keyed "layerId@pg" so a dismissed divergence never re-nags on the
     same page until a NEW divergence appears. */
  var _dismissed = {};
  var _lastActiveCat = null;
  var _lastPage = null;

  var CSS = "" +
    "#ltu-edge{position:absolute;inset:0;pointer-events:none;z-index:5;box-shadow:none;transition:box-shadow .16s ease;}" +
    "#ltu-chip{position:absolute;left:10px;bottom:52px;z-index:30;display:flex;align-items:center;gap:8px;" +
      "background:rgba(11,13,17,.92);border:1px solid var(--accent);border-radius:999px;padding:6px 13px 6px 11px;" +
      "font-size:12px;font-weight:600;color:var(--ink);cursor:pointer;box-shadow:0 6px 20px -8px #000;max-width:60%;}" +
    "#ltu-chip .ltu-sub{color:var(--muted);font-weight:400;font-size:11px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}" +
    "#ltu-chip b{color:var(--ink);}" +
    "#ltu-dot{width:10px;height:10px;border-radius:50%;background:var(--accent);flex:none;box-shadow:0 0 7px currentColor;}" +
    "#ltu-chip.ltu-flash{animation:ltuflash .8s ease;}" +
    "@keyframes ltuflash{0%{transform:scale(1)}28%{transform:scale(1.08)}100%{transform:scale(1)}}" +
    "#ltu-banner{position:absolute;left:50%;top:14px;transform:translateX(-50%);z-index:40;max-width:620px;" +
      "width:calc(100% - 60px);display:none;gap:10px;align-items:center;background:#2a2113;border:1px solid var(--warn);" +
      "border-radius:8px;padding:9px 12px;box-shadow:0 8px 24px -10px #000;}" +
    "#ltu-banner.show{display:flex;}" +
    "#ltu-banner .ltu-ic{font-size:15px;flex:none;}" +
    "#ltu-banner .ltu-msg{flex:1;font-size:12px;color:#ffe4bd;line-height:1.5;}" +
    "#ltu-banner .ltu-msg b{color:#fff;}" +
    "#ltu-banner button{border:1px solid var(--line);background:#161a21;color:var(--ink);border-radius:6px;" +
      "padding:5px 10px;cursor:pointer;font-size:12px;flex:none;}" +
    "#ltu-banner button:hover{border-color:var(--warn);}" +
    "#ltu-banner button.ltu-b-prim{background:var(--warn);color:#221a0a;border-color:var(--warn);font-weight:600;}" +
    ".ltu-current{color:var(--accent);font-size:11px;margin-right:2px;flex:none;}" +
    "#picker.ltu-flashpanel{outline:2px solid var(--accent);outline-offset:-2px;transition:outline .2s;}";

  function _q(id) { return document.getElementById(id); }
  function _esc(s) {
    return String(s == null ? "" : s)
      .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  }
  function _agg() { return (typeof window !== "undefined") ? window.ObjectAgg : null; }

  function _activeLayer() {
    if (typeof state === "undefined" || typeof layerById !== "function") return null;
    return layerById(state.activeCat) || null;
  }

  /* active layer's floorKey ?? current page's floorKey (ObjectAgg semantics) */
  function _resolvedFloorKey() {
    var lyr = _activeLayer();
    var lfk = lyr && lyr.floorKey;
    if (lfk && lfk !== "multi") return lfk;
    var A = _agg();
    return (A && typeof A.floorKeyOfPage === "function") ? A.floorKeyOfPage(curPage) : "";
  }

  function _floorLabel(fk) {
    var A = _agg();
    var lbl = (A && typeof A.floorKeyLabel === "function") ? A.floorKeyLabel(fk) : "";
    return lbl || "—";
  }

  /* ---------------- DOM injection (idempotent) ---------------- */
  function _inject() {
    var stage = _q("stage");
    if (!stage || _q("ltu-chip")) return;

    if (!_q("ltu-style")) {
      var st = document.createElement("style");
      st.id = "ltu-style";
      st.textContent = CSS;
      document.head.appendChild(st);
    }

    var edge = document.createElement("div");
    edge.id = "ltu-edge";
    edge.setAttribute("data-armed", "0");
    stage.appendChild(edge);

    var chip = document.createElement("div");
    chip.id = "ltu-chip";
    chip.title = "เลเยอร์/ชั้นที่กำลังวาดอยู่ — คลิกเพื่อไปที่แผงเลเยอร์";
    chip.innerHTML =
      '<span id="ltu-dot"></span>' +
      '<span>วาดที่: <b id="ltu-floor">—</b></span>' +
      '<span id="ltu-layer" class="ltu-sub"></span>';
    chip.addEventListener("click", _focusPanel);
    stage.appendChild(chip);

    var b = document.createElement("div");
    b.id = "ltu-banner";
    b.innerHTML =
      '<span class="ltu-ic">⚠️</span>' +
      '<span class="ltu-msg" id="ltu-banner-msg"></span>' +
      '<button class="ltu-b-prim" id="ltu-by-layer">ตามเลเยอร์</button>' +
      '<button id="ltu-by-page">ตามหน้า</button>';
    stage.appendChild(b);
    _q("ltu-by-layer").addEventListener("click", _onByLayer);
    _q("ltu-by-page").addEventListener("click", _onByPage);
  }

  /* chip click → open/focus the layer panel (cheap discoverability) */
  function _focusPanel() {
    if (document.body.classList.contains("focus")) document.body.classList.remove("focus");
    var picker = _q("picker");
    if (picker) {
      picker.classList.add("ltu-flashpanel");
      setTimeout(function () { picker.classList.remove("ltu-flashpanel"); }, 900);
    }
  }

  /* ---------------- chip + edge tint (cheap; safe every draw) ------------- */
  function sync() {
    var chip = _q("ltu-chip");
    if (!chip) return;
    var lyr = _activeLayer();
    var color = (lyr && lyr.color) || "#4c8dff";

    var floorEl = _q("ltu-floor");
    if (floorEl) floorEl.textContent = _floorLabel(_resolvedFloorKey());
    var layerEl = _q("ltu-layer");
    if (layerEl) layerEl.textContent = lyr ? ("· " + lyr.name) : "";
    var dot = _q("ltu-dot");
    if (dot) { dot.style.background = color; dot.style.color = color; }
    chip.style.borderColor = color;
    chip.setAttribute("data-color", color);

    /* flash chip when the active layer changed since last sync */
    if (_lastActiveCat !== null && lyr && lyr.id !== _lastActiveCat) {
      chip.classList.remove("ltu-flash");
      void chip.offsetWidth; /* reflow → restart animation */
      chip.classList.add("ltu-flash");
    }
    if (lyr) _lastActiveCat = lyr.id;

    /* edge tint — armed only for drawing tools, never select/pan/annotate */
    var edge = _q("ltu-edge");
    if (edge) {
      var armed = (typeof isDrawTool === "function") && isDrawTool() &&
                  !(typeof state !== "undefined" && state.panTool);
      edge.setAttribute("data-armed", armed ? "1" : "0");
      edge.setAttribute("data-color", color);
      edge.style.boxShadow = armed
        ? ("inset 0 0 0 2px " + color + ", inset 0 0 26px -6px " + color)
        : "none";
    }

    /* page navigation always ends in a draw() -> sync(); reconcile the banner
       when the page actually changed (covers loadPage without wrapping it,
       robust against loadPage wrap-ordering). Cheap: only on real change. */
    if (typeof curPage !== "undefined" && _lastPage !== curPage) {
      _lastPage = curPage;
      reconcile();
    }
  }

  /* ---------------- ◉ make-current marker (row rows already set
     state.activeCat on click — we only add the visual current-marker) ----- */
  function _decorateRows() {
    var list = _q("catlist");
    if (!list || typeof state === "undefined") return;
    var rows = list.querySelectorAll('[data-nodekind="layer"]');
    for (var i = 0; i < rows.length; i++) {
      var row = rows[i];
      var isActive = row.getAttribute("data-catid") === state.activeCat;
      var existing = row.querySelector(".ltu-current");
      if (isActive && !existing) {
        var mk = document.createElement("span");
        mk.className = "ltu-current";
        mk.textContent = "◉";
        mk.title = "เลเยอร์ปัจจุบัน";
        var nm = row.querySelector(".nm");
        if (nm) row.insertBefore(mk, nm); else row.insertBefore(mk, row.firstChild);
      } else if (!isActive && existing) {
        existing.remove();
      }
    }
  }

  /* ---------------- reconcile banner (expensive: walks PS via
     ObjectAgg.detectDivergence — call only on page/tag/load events) ------- */
  function reconcile() {
    var banner = _q("ltu-banner");
    if (!banner) return;
    var A = _agg();
    if (!A || typeof A.detectDivergence !== "function") { banner.classList.remove("show"); return; }

    var rows = A.detectDivergence().filter(function (r) { return r.pg === curPage; });
    var row = null;
    for (var i = 0; i < rows.length; i++) {
      if (!_dismissed[rows[i].layerId + "@" + rows[i].pg]) { row = rows[i]; break; }
    }
    if (!row) { banner.classList.remove("show"); banner._ltuRow = null; return; }

    var lyr = (typeof layerById === "function") ? layerById(row.layerId) : null;
    var nm = (lyr && lyr.name) || row.layerId;
    var msg = _q("ltu-banner-msg");
    if (msg) {
      msg.innerHTML =
        "เลเยอร์ <b>" + _esc(nm) + "</b> ปักไว้<b>" + _esc(_floorLabel(row.layerFloorKey)) +
        "</b> แต่หน้านี้แท็กเป็น<b>" + _esc(_floorLabel(row.pageFloorKey)) +
        "</b> (" + row.count + " วัตถุ)";
    }
    banner._ltuRow = row;
    banner.classList.add("show");
  }

  /* [ตามเลเยอร์] keep the pin — dismiss + remember (per layer+page) */
  function _onByLayer() {
    var banner = _q("ltu-banner");
    var row = banner && banner._ltuRow;
    if (row) _dismissed[row.layerId + "@" + row.pg] = true;
    if (banner) banner.classList.remove("show");
  }

  /* [ตามหน้า] clear the layer's floorKey → object falls back to the page
     tag. This MUTATES a layer; layers are not snapshot-covered by undo yet,
     but we pushUndo() first for cheap forward-compat (see B-ui report). */
  function _onByPage() {
    var banner = _q("ltu-banner");
    var row = banner && banner._ltuRow;
    if (!row) return;
    if (typeof pushUndo === "function") pushUndo();
    var lyr = (typeof layerById === "function") ? layerById(row.layerId) : null;
    if (lyr) delete lyr.floorKey;   /* unset optional field → additive-safe */
    if (typeof state !== "undefined") state.dirty = true;
    if (typeof buildPicker === "function") buildPicker();
    if (typeof draw === "function") draw();
    reconcile();   /* divergence resolved → banner hides */
    sync();
  }

  /* ---------------- wiring ---------------- */
  function _wrap(name, after) {
    var fn = (typeof window !== "undefined") ? window[name] : undefined;
    if (typeof fn !== "function" || fn.__ltuWrapped) return;
    var orig = fn;
    var wrapped = function () {
      var r = orig.apply(this, arguments);
      try { after.apply(this, arguments); } catch (_e) {}
      return r;
    };
    wrapped.__ltuWrapped = true;
    window[name] = wrapped;
  }

  function _boot() {
    _inject();

    /* Defer wrapping to a macrotask so it runs AFTER every synchronous
       DOMContentLoaded bootstrap — critically page-folder-layers.js, whose
       buildPicker wrapper is DESTRUCTIVE (it renders buildPagePicker() and
       drops any prior wrapper). Wrapping synchronously here raced ahead of it
       and got clobbered; a setTimeout(0) lands us last + stable (pfl wraps
       once, guarded, and never re-wraps after this point). draw/liteSetTag/
       loadProto wrappers elsewhere (cfss, empty-state) all COMPOSE, so order
       vs. them is immaterial. */
    setTimeout(function () {
      /* chip + tint refresh on every draw (also fires page-change reconcile) */
      _wrap("draw", function () { sync(); });
      /* ◉ current-marker + chip refresh after every picker rebuild */
      _wrap("buildPicker", function () { _decorateRows(); sync(); });
      /* banner reconcile after tag change / project load */
      function _defer() { setTimeout(function () { reconcile(); sync(); }, 0); }
      _wrap("liteSetTag", _defer);
      _wrap("loadProto", _defer);

      /* initial paint */
      _decorateRows(); sync(); reconcile();
    }, 0);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", _boot);
  } else {
    _boot();
  }

  if (typeof window !== "undefined") {
    window.LayerTargetUI = { sync: sync, reconcile: reconcile, dismissed: _dismissed };
  }
})();
