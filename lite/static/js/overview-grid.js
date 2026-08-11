/* ============================================================
   OVERVIEW-GRID — Step-1 "classify grid" of the Overview wizard
   (INV-2026-07-04-002 slice 1/4 — extracted from overview-setup.js,
   which had crossed the 1000-line lite cap).
   Plain-globals module. No IIFE, no export, no bundler.
   Loaded dynamically from page-folder-layers.js (same LOVS-1 dynamic-
   inject pattern), BEFORE overview-setup.js so its render/wire fns
   exist before overview-setup.js's shell (Step nav / keyboard) calls
   into them.

   Owned here (module-level globals — promoted to explicit `_lovs`-
   prefixed globals per seam-cut rule; both are also read/cleared by
   the wizard shell in overview-setup.js, which is fine since neither
   file uses an IIFE — every `var` here is already a plain global):
     _LOVS_TAG_CYCLE   — tag cycle order (keyboard 0-6 + click-cycle)
     _LOVS_TAG_KEYS    — keyboard-digit → tag map
     _lovsSelected     — Set of currently multi-selected page numbers
     _lovsSelAnchor    — shift-click range anchor page number
     window.__lovsSelected — alias kept for test_overview_setup.py

   Globals required from overview-setup.js / ui-lite.html (read-only
   here, NOT redeclared):
     _lovsFocusPage, _lovsCurStep    — wizard shell state
     _lovsSetFloorNum(n,num), _lovsSetFloorKind(n,kind) — floor writers
       (still owned by overview-setup.js: also used by its Step-2
       _lovsSequentialFloor)
     pageTags, PAGE_TAGS, excluded, pageFloorNum, pageFloorKind, PS,
     pageNames, curPage, pageCount
     liteSetTag(n,val), loadPage(n), closeOverlays(), api(path)
     _lwizShowBlockHint()   — BUG-20260811-escape-paths: dblclick-escape
       guard now gates on _lovsSelected.size (this file's own state), not
       window.__lwizAutoLockActive (that lock was removed by WIZ-UNLOCK,
       fb9b2af — the flag it left behind is permanently false / dead)

   Exports (called from overview-setup.js shell):
     _lovsRenderClassify(), _lovsSetTagViaKey(k), _lovsHideCtx()

   INV-2026-07-04-002 slice 2/4 (bulk-bar upgrade — floor auto-number
   apply + overwrite-confirm + single-undo batch):
     _lovsBulkPending  — {pages,tag,kind,startNum,overlapCount} awaiting
                          user confirm, or null. Owned here (module state).
     _lovsBulkResolveMap(pages,kind,startNum) — pure, no mutation. Mirrors
       overview-setup.js's _lovsSequentialFloor numbering convention
       EXACTLY (basement DESCENDING, mezz/mech/roof consume no number,
       normal ascends from startNum) — see function doc for the one
       deliberate omission (Sequential's own last-page-auto-roof guess).
     _lovsBulkApply(pages,tag,kind,startNum) / _lovsBulkCommit(spec) —
       mutate via liteSetTag/liteSetFloorKind/liteSetFloorNum (ui-lite.html
       globals — liteSetTag is wrapped by page-folder-layers.js to reseed
       PF folders; NOT the internal _lovsSetFloorNum/_lovsSetFloorKind).
       Exactly one pushUndo() before the first mutation of a confirmed
       batch. Overlap (any selected page already carrying a tag) triggers
       an inline confirm bar (no window.confirm) before committing.

   Documented semantics (opus review, slice 2 — not code changes, just
   making the existing behavior explicit):
     (1) Per-page kind ALWAYS wins over the bulkbar kind selector, even on
         a CONFIRMED overwrite of an already-tagged page — _lovsBulkCommit
         always re-applies spec.tag (tag changes on overwrite) but
         _lovsBulkResolveMap's `pageFloorKind[p] || kind` means an
         already-floor-classified page's OWN kind is never replaced by
         the selector's kind, confirmed or not.
     (2) A page whose resolved row has num:null (mezzanine/mechanical/
         rooftop) does NOT get its pre-existing pageFloorNum cleared by
         _lovsBulkCommit — liteSetFloorNum is simply skipped (not called
         with null). In practice this is usually harmless because
         liteSetFloorKind itself already deletes pageFloorNum for those
         3 kinds (see ui-lite.html) UNLESS the per-page kind resolved to
         mezzanine/mechanical/rooftop while spec.kind (selector) differs —
         then liteSetFloorKind(row.p, row.kind) still runs with the
         RESOLVED kind (not the stale one) so the delete still fires. The
         only way a stale floorNum could theoretically survive is if a
         future change resolves kind without also calling liteSetFloorKind
         — flagging here so that invariant isn't broken silently later.

   INV-2026-07-04-002 slice 3/4 (verification view toggle — group-by-tag):
     _lovsViewMode ('pages'|'groups') — runtime-only (not persisted),
       default 'pages'. Toggled via the '#btn-grid-view' button rendered
       inline inside #grid-classify (overview-setup.js's static panel
       template / hint bar is NOT touched — out of scope this slice).
     _lovsVisualOrder — array of page numbers in the CURRENT rendered tile
       sequence (recomputed every _lovsRenderClassify() call). In 'pages'
       mode this is exactly [1..pageCount] (byte-identical to pre-slice-3
       behavior). In 'groups' mode it's the grouped/sub-ranked order below.
       The tile click handler's shift-range now walks _lovsVisualOrder by
       INDEX (visual order) instead of raw page-number arithmetic, so
       shift-click range is correct in both modes and unchanged in 'pages'
       mode (index range === number range there).
     _lovsTileHTML(n,pt,_tagSeq,_tagTot) — the exact per-tile markup,
       extracted out of the render loop so both view modes share one
       code path (no risk of the two modes' tile markup drifting apart).
     _lovsGroupedOrder(pc) / _lovsFloorRank(n) — grouping: site, floor
       (sub-sorted by _rankPFFolder via pageFolderIdFor — SAME PF-folder
       rank convention page-folder-layers.js already uses, not a
       reimplementation), plan, parking, amenity, detail, then untagged
       ('') LAST and visually flagged (warn-colored header).
     DnD conflict check (constraint bullet): `ltDndDecorate` (layer-dnd.js)
       is scoped EXCLUSIVELY to `#catlist` (the layer panel) — it never
       touches `#grid-classify` or `.ov-tile`. The only native
       `draggable=true` DnD in the whole Overview wizard is Step-2's
       floor-strip `.fchip` (a different tab/container, untouched by this
       slice). Step-1's rubber-band multi-select (_lovsWireDragBox) is
       NOT native DnD — it's mousedown/mousemove bounding-box math against
       live getBoundingClientRect() of whatever `.ov-tile`s are currently
       in the DOM, so it is unaffected by re-sorting/grouping tiles and
       needed NO changes. Conclusion: no real conflict exists to resolve;
       nothing was disabled.
   ============================================================ */

var _LOVS_TAG_CYCLE = ['','site','floor','plan','parking','amenity','detail'];
var _LOVS_TAG_KEYS  = {'1':'site','2':'floor','3':'plan','4':'parking','5':'amenity','6':'detail','0':''};
var _lovsSelected   = new Set();
var _lovsSelAnchor  = null;
var _lovsBulkPending = null;
var _lovsViewMode    = "pages"; // 'pages' | 'groups' — slice 3/4, runtime-only, not persisted
var _lovsVisualOrder = [];      // slice 3/4 — page numbers in current rendered order (recomputed every render)
window.__lovsSelected = _lovsSelected;

/* ============================================================  STEP 1 */

/* Per-tile markup — extracted (slice 3/4) so 'pages' and 'groups' view
   modes share exactly one code path (byte-identical tile HTML either
   way; only the ITERATION ORDER + optional group headers differ). */
function _lovsTileHTML(n, pt, _tagSeq, _tagTot) {
  var tag = pageTags[n] || "";
  var tagLbl = tag ? (pt[tag] || tag) : "— ไม่ระบุ —";
  var fl = pageFloorNum[n];
  var flStr = fl === undefined ? "" : (fl === "roof" ? "roof" : String(fl));
  /* Default kind=normal for any tag=floor page that hasn't been classified yet — so the
     floor-input always shows (existing test classifyRendersTiles expects hasFloorInput4). */
  var fkind = pageFloorKind[n] || (fl === "roof" ? "rooftop" : "normal");
  var fkindNeedsNum = (fkind === "normal" || fkind === "basement");
  var objc = (PS[n] && PS[n].objects && PS[n].objects.length) ? PS[n].objects.length : 0;
  var thumbUrl = (typeof api === "function") ? api("/thumb/" + n) : ""; // LPM slice 4+: route through pageMgr.serverNum(n) once mutations exist
  var cls = "ov-tile" + ((typeof curPage !== "undefined" && n === curPage) ? " cur" : "") +
    (n === _lovsFocusPage ? " foc" : "") + (excluded[n] ? " exc" : "") + (_lovsSelected.has(n) ? " sel" : "");
  return '<div class="' + cls + '" data-pg="' + n + '">' +
    '<div class="thumb">' +
      (thumbUrl ? '<img class="ov-thumb-img" loading="lazy" src="' + thumbUrl + '" alt="p' + n + '" onerror="this.style.display=\'none\'">' : "") +
      '<span class="pn">p' + n + '</span>' + (objc ? '<span class="objc">' + objc + '</span>' : "") +
      '<span class="selchk">✓</span>' + (thumbUrl ? "" : "📄") +
    '</div><div class="info">' +
      '<div class="nm">หน้า ' + n + (pageNames[n] ? ' · ' + pageNames[n] : '') + '</div>' +
      '<div class="row"><span class="ov-tag-chip ov-tag-' + (tag || "untagged") + '" data-tag="' + tag + '">' + tagLbl + '</span></div>' +
      '<div class="row" style="justify-content:space-between">' +
        (tag === "floor"
          ? '<select class="ov-fkind-sel" data-fkind="' + n + '" title="ประเภทชั้น">' +
              '<option value="normal"'     + (fkind === "normal"     ? " selected" : "") + '>🏢 ชั้น</option>' +
              '<option value="basement"'   + (fkind === "basement"   ? " selected" : "") + '>⬇ ใต้ดิน</option>' +
              '<option value="mezzanine"'  + (fkind === "mezzanine"  ? " selected" : "") + '>🪜 ชั้นลอย</option>' +
              '<option value="mechanical"' + (fkind === "mechanical" ? " selected" : "") + '>⚙ ห้องเครื่อง</option>' +
              '<option value="rooftop"'    + (fkind === "rooftop"    ? " selected" : "") + '>⛅ ดาดฟ้า</option>' +
            '</select>' +
            (fkindNeedsNum
              ? '<input class="ov-floor-input" type="text" value="' + (fl != null && fl !== "roof" ? flStr : "") + '" placeholder="N" data-floor="' + n + '" title="เลขชั้น">'
              : '<span style="flex:0 0 50px;text-align:center;color:var(--muted,#8b97a8);font-size:10px">' + (fkind === "rooftop" ? "ROOF" : fkind === "mezzanine" ? "MEZ" : "MEC") + '</span>')
          : (tag && _tagSeq[n]
              ? '<span style="flex:1;text-align:center;color:var(--accent,#4c8dff);font-size:11px;font-weight:600;font-variant-numeric:tabular-nums" title="ลำดับใน tag ' + tag + '">#' + _tagSeq[n] + '/' + _tagTot[tag] + '</span>'
              : '<span style="flex:1"></span>')) +
        '<button class="ov-excl-btn" data-excl="' + n + '">' + (excluded[n] ? "⛔" : "·") + '</button>' +
      '</div>' +
    '</div></div>';
}

/* Slice 3/4 grouping. Order: site, floor (sub-ranked via _rankPFFolder/
   pageFolderIdFor — the SAME convention page-folder-layers.js uses to
   order PF folders; not reimplemented), plan, parking, amenity, detail,
   then untagged ('') LAST, flagged via grp.untagged. */
function _lovsFloorRank(n) {
  if (typeof pageFolderIdFor === "function" && typeof _rankPFFolder === "function") {
    return _rankPFFolder(pageFolderIdFor(n, "floor", pageFloorNum[n], pageFloorKind[n]));
  }
  return 5000; // defensive fallback only — page-folder-layers.js always loads first in practice
}

function _lovsGroupedOrder(pc) {
  var byTag = { "": [], site: [], floor: [], plan: [], parking: [], amenity: [], detail: [] };
  for (var n = 1; n <= pc; n++) {
    var t = pageTags[n] || "";
    if (!byTag[t]) byTag[t] = []; // safety net for any unexpected tag value
    byTag[t].push(n);
  }
  if (byTag.floor.length > 1) {
    byTag.floor.sort(function(a, b) {
      var ra = _lovsFloorRank(a), rb = _lovsFloorRank(b);
      return (ra !== rb) ? (ra - rb) : (a - b);
    });
  }
  var pt = (typeof PAGE_TAGS !== "undefined") ? PAGE_TAGS : {};
  var groups = [];
  var canonical = ["site", "floor", "plan", "parking", "amenity", "detail"];
  canonical.forEach(function(t) {
    if (byTag[t] && byTag[t].length) groups.push({ key: t, label: pt[t] || t, pages: byTag[t], untagged: false });
  });
  // Drift guard (Fable review, slice 3): any tag value outside the canonical
  // set (legacy save / future PAGE_TAGS addition not mirrored here) must
  // still be VISIBLE — hiding pages defeats the verification grid's purpose.
  Object.keys(byTag).forEach(function(t) {
    if (t === "" || canonical.indexOf(t) >= 0) return;
    if (byTag[t].length) groups.push({ key: t, label: pt[t] || t, pages: byTag[t], untagged: false });
  });
  if (byTag[""].length) groups.push({ key: "", label: "ยังไม่แท็ก", pages: byTag[""], untagged: true });
  return groups;
}

function _lovsViewToggleHTML() {
  var isGroups = _lovsViewMode === "groups";
  return '<div id="grid-view-toggle" style="grid-column:1/-1;display:flex;justify-content:flex-end;margin-bottom:2px">' +
    '<button id="btn-grid-view" title="สลับมุมมองสำหรับตรวจทาน">' +
      (isGroups ? '📄 เรียงตามหน้า' : '🏷 จัดกลุ่มตามแท็ก') +
    '</button></div>';
}

function _lovsRenderClassify() {
  var g = document.getElementById("grid-classify"); if (!g) return;
  var pc = (typeof pageCount !== "undefined") ? pageCount : 0;
  var pt = (typeof PAGE_TAGS !== "undefined") ? PAGE_TAGS : {};
  var h = "";
  /* LFLOOR-1c: pre-compute per-tag sequence (excl floor + excluded pages).
     _tagSeq[n] = 1-based position within its tag; _tagTot[tag] = total */
  var _tagSeq = {}, _tagTot = {};
  for (var ti = 1; ti <= pc; ti++) {
    var ttag = pageTags[ti];
    if (!ttag || ttag === "floor" || excluded[ti]) continue;
    _tagTot[ttag] = (_tagTot[ttag] || 0) + 1;
    _tagSeq[ti] = _tagTot[ttag];
  }

  h += _lovsViewToggleHTML();

  if (_lovsSelected.size >= 2) {
    if (_lovsBulkPending) {
      /* INV-2026-07-04-002 slice 2/4: overwrite-confirm bar (no window.confirm). */
      h += '<div id="bulkbar" class="confirm"><span style="color:var(--warn,#ffb454)">⚠ ' +
        _lovsBulkPending.overlapCount + ' จาก ' + _lovsBulkPending.pages.length +
        ' หน้าที่เลือกมี tag อยู่แล้ว — ทับข้อมูลเดิม?</span>' +
        '<button id="bulk-confirm-yes">✓ ยืนยัน ทับข้อมูล</button>' +
        '<button id="bulk-confirm-no">✕ ยกเลิก</button></div>';
    } else {
      h += '<div id="bulkbar"><span>เลือก <span class="ct">' + _lovsSelected.size + '</span> หน้า</span>' +
        '<button id="bulk-clearsel">ล้าง (Esc)</button><span style="opacity:.5">|</span>';
      _LOVS_TAG_CYCLE.filter(function(t) { return t; }).forEach(function(t) {
        h += '<span class="ov-tag-chip ov-tag-' + t + '" data-bulk-tag="' + t + '">' + t + '</span>';
      });
      h += '<span class="ov-tag-chip ov-tag-untagged" data-bulk-tag="">ล้าง</span>' +
        '<span style="opacity:.5">|</span><button id="bulk-excl">⛔ exclude</button>' +
        '<span style="opacity:.5">|</span>' +
        /* slice 2/4: bulk floor auto-number apply (tag + kind + running number in one click) */
        '<select id="bulk-kind" class="ov-fkind-sel" title="ประเภทชั้น (สำหรับ Apply)">' +
          '<option value="normal">🏢 ชั้น</option>' +
          '<option value="basement">⬇ ใต้ดิน</option>' +
          '<option value="mezzanine">🪜 ชั้นลอย</option>' +
          '<option value="mechanical">⚙ ห้องเครื่อง</option>' +
          '<option value="rooftop">⛅ ดาดฟ้า</option>' +
        '</select>' +
        '<input id="bulk-start" class="ov-floor-input" type="number" min="1" step="1" value="1" title="เริ่มที่เลขชั้น">' +
        '<button id="bulk-apply">⚡ Apply</button></div>';
    }
  }

  if (_lovsViewMode === "groups") {
    var groups = _lovsGroupedOrder(pc);
    _lovsVisualOrder = [];
    groups.forEach(function(grp) {
      _lovsVisualOrder = _lovsVisualOrder.concat(grp.pages);
      h += '<div class="ov-group-header' + (grp.untagged ? " ov-group-untagged" : "") + '" ' +
        'style="grid-column:1/-1;padding:6px 4px 2px;font-size:11px;font-weight:700;' +
        'color:' + (grp.untagged ? "var(--warn,#ffb454)" : "var(--accent,#4c8dff)") + ';' +
        'border-bottom:1px solid var(--line,#2a3140);margin-top:4px">' +
        grp.label + ' <span style="opacity:.6;font-weight:400">(' + grp.pages.length + ')</span></div>';
      grp.pages.forEach(function(n) { h += _lovsTileHTML(n, pt, _tagSeq, _tagTot); });
    });
  } else {
    _lovsVisualOrder = [];
    for (var n = 1; n <= pc; n++) { _lovsVisualOrder.push(n); h += _lovsTileHTML(n, pt, _tagSeq, _tagTot); }
  }

  g.innerHTML = h;
  _lovsWireClassify();
}

function _lovsWireClassify() {
  var g = document.getElementById("grid-classify"); if (!g) return;
  var vb = document.getElementById("btn-grid-view");
  if (vb) vb.addEventListener("click", function() {
    _lovsViewMode = (_lovsViewMode === "groups") ? "pages" : "groups";
    _lovsRenderClassify();
  });
  g.querySelectorAll(".ov-tile").forEach(function(tile) {
    var pn = +tile.dataset.pg;
    tile.addEventListener("mousedown", function(e) {
      if (e.button !== 0 || e.target.closest(".ov-tag-chip") || e.target.closest(".ov-floor-input") || e.target.closest(".ov-fkind-sel") || e.target.closest(".ov-excl-btn")) return;
      e.stopPropagation();
    });
    tile.addEventListener("click", function(e) {
      if (e.target.closest(".ov-tag-chip") || e.target.closest(".ov-floor-input") || e.target.closest(".ov-fkind-sel") || e.target.closest(".ov-excl-btn")) return;
      if (e.shiftKey && _lovsSelAnchor != null) {
        /* slice 3/4: range = VISUAL order (identical to page-number order
           in 'pages' mode; the grouped visual sequence in 'groups' mode). */
        var ia = _lovsVisualOrder.indexOf(_lovsSelAnchor), ib = _lovsVisualOrder.indexOf(pn);
        _lovsSelected.clear();
        if (ia === -1 || ib === -1) {
          var lo = Math.min(_lovsSelAnchor, pn), hi = Math.max(_lovsSelAnchor, pn);
          for (var i = lo; i <= hi; i++) _lovsSelected.add(i);
        } else {
          var lo2 = Math.min(ia, ib), hi2 = Math.max(ia, ib);
          for (var j = lo2; j <= hi2; j++) _lovsSelected.add(_lovsVisualOrder[j]);
        }
        _lovsFocusPage = pn;
      } else if (e.ctrlKey || e.metaKey) {
        if (_lovsSelected.has(pn)) _lovsSelected.delete(pn); else _lovsSelected.add(pn);
        _lovsSelAnchor = pn; _lovsFocusPage = pn;
      } else {
        _lovsSelected.clear(); _lovsSelected.add(pn); _lovsSelAnchor = pn; _lovsFocusPage = pn;
      }
      _lovsRenderClassify();
    });
    tile.addEventListener("dblclick", function(e) {
      if (e.target.closest(".ov-floor-input")) return;
      // BUG-20260811-escape-paths: this used to gate on window.__lwizAutoLockActive
      // (BUG-20260526-lite-wizard-followup), but WIZ-UNLOCK (fb9b2af) permanently
      // set that flag false when it removed the hard lock -> the branch went dead
      // and dblclick could always escape mid-triage. Replaced with a LIVE
      // work-in-progress check: pages still selected = unfinished triage, block
      // the escape and show a hint instead of navigating away silently.
      if (_lovsSelected && _lovsSelected.size > 0) {
        if (typeof _lwizShowBlockHint === "function") _lwizShowBlockHint();
        return;
      }
      if (typeof loadPage === "function") loadPage(pn);
      if (typeof closeOverlays === "function") closeOverlays();
      _lovsSelected.clear();
    });
    var chip = tile.querySelector(".ov-tag-chip");
    if (chip) {
      chip.addEventListener("click", function(e) { e.stopPropagation(); _lovsCycleTag(pn); });
      chip.addEventListener("contextmenu", function(e) { e.preventDefault(); e.stopPropagation(); _lovsShowCtxMenu(e, pn); });
    }
    var fi = tile.querySelector(".ov-floor-input");
    if (fi) {
      fi.addEventListener("mousedown", function(e) { e.stopPropagation(); });
      fi.addEventListener("click", function(e) { e.stopPropagation(); });
      fi.addEventListener("change", function() { _lovsSetFloorNum(pn, fi.value.trim()); _lovsRenderClassify(); });
      fi.addEventListener("keydown", function(e) { if (e.key === "Enter") fi.blur(); });
    }
    var fk = tile.querySelector(".ov-fkind-sel");
    if (fk) {
      fk.addEventListener("mousedown", function(e) { e.stopPropagation(); });
      fk.addEventListener("click", function(e) { e.stopPropagation(); });
      fk.addEventListener("change", function() { _lovsSetFloorKind(pn, fk.value); _lovsRenderClassify(); });
    }
    var eb = tile.querySelector(".ov-excl-btn");
    if (eb) eb.addEventListener("click", function(e) { e.stopPropagation(); excluded[pn] = !excluded[pn]; _lovsRenderClassify(); });
  });
  var bb = document.getElementById("bulkbar");
  if (bb) {
    if (_lovsBulkPending) {
      var byes = document.getElementById("bulk-confirm-yes");
      var bno  = document.getElementById("bulk-confirm-no");
      if (byes) byes.addEventListener("click", function() {
        var spec = _lovsBulkPending; _lovsBulkPending = null; _lovsBulkCommit(spec);
      });
      if (bno) bno.addEventListener("click", function() { _lovsBulkPending = null; _lovsRenderClassify(); });
    } else {
      bb.querySelectorAll("[data-bulk-tag]").forEach(function(chip) {
        chip.addEventListener("click", function() {
          var t = chip.dataset.bulkTag;
          _lovsSelected.forEach(function(n) { liteSetTag(n, t); });
          _lovsRenderClassify();
        });
      });
      var bcs = document.getElementById("bulk-clearsel"); if (bcs) bcs.addEventListener("click", function() { _lovsSelected.clear(); _lovsRenderClassify(); });
      var bex = document.getElementById("bulk-excl");
      if (bex) bex.addEventListener("click", function() {
        var any = false; _lovsSelected.forEach(function(n) { if (excluded[n]) any = true; });
        _lovsSelected.forEach(function(n) { excluded[n] = !any; }); _lovsRenderClassify();
      });
      var ba = document.getElementById("bulk-apply");
      if (ba) ba.addEventListener("click", function() {
        var pages = []; _lovsSelected.forEach(function(n) { pages.push(n); }); pages.sort(function(a, b) { return a - b; });
        var bk = document.getElementById("bulk-kind"), bs = document.getElementById("bulk-start");
        var kind = bk ? bk.value : "normal";
        var startNum = bs ? (+bs.value || 1) : 1;
        _lovsBulkApply(pages, "floor", kind, startNum);
      });
    }
  }
  _lovsWireDragBox();
}

function _lovsWireDragBox() {
  var g = document.getElementById("grid-classify"), box = document.getElementById("ov-dragbox");
  if (!g || !box) return;
  var ds = null, drg = false, addM = false;
  g.addEventListener("mousedown", function(e) {
    if (e.target !== g || e.button !== 0) return;
    addM = e.ctrlKey || e.metaKey; if (!addM) _lovsSelected.clear();
    var gr = g.getBoundingClientRect();
    ds = {x: e.clientX - gr.left + g.scrollLeft, y: e.clientY - gr.top + g.scrollTop}; drg = false;
  });
  g.addEventListener("mousemove", function(e) {
    if (!ds) return;
    var gr = g.getBoundingClientRect();
    var x = e.clientX - gr.left + g.scrollLeft, y = e.clientY - gr.top + g.scrollTop;
    if (!drg && (Math.abs(x - ds.x) > 4 || Math.abs(y - ds.y) > 4)) drg = true;
    if (drg) {
      var lx = Math.min(x, ds.x), ly = Math.min(y, ds.y), w = Math.abs(x - ds.x), h = Math.abs(y - ds.y);
      box.style.cssText = "display:block;left:" + lx + "px;top:" + ly + "px;width:" + w + "px;height:" + h + "px";
      var sel = addM ? new Set(_lovsSelected) : new Set();
      g.querySelectorAll(".ov-tile").forEach(function(tile) {
        var tr = tile.getBoundingClientRect();
        var tx = tr.left - gr.left + g.scrollLeft, ty = tr.top - gr.top + g.scrollTop;
        if (tx + tr.width > lx && tx < lx + w && ty + tr.height > ly && ty < ly + h) sel.add(+tile.dataset.pg);
      });
      _lovsSelected = sel; window.__lovsSelected = _lovsSelected;
      g.querySelectorAll(".ov-tile").forEach(function(tile) { tile.classList.toggle("sel", _lovsSelected.has(+tile.dataset.pg)); });
    }
  });
  g.addEventListener("mouseup", function(e) {
    box.style.display = "none";
    if (ds && drg) { if (_lovsSelected.size) { var mn = Infinity; _lovsSelected.forEach(function(n) { if (n < mn) mn = n; }); _lovsSelAnchor = mn; } _lovsRenderClassify(); }
    else if (ds && !drg && e.target === g) { _lovsSelected.clear(); _lovsSelAnchor = null; _lovsRenderClassify(); }
    ds = null; drg = false;
  });
}

function _lovsCycleTag(pn) {
  var cur = pageTags[pn] || "", i = _LOVS_TAG_CYCLE.indexOf(cur);
  liteSetTag(pn, _LOVS_TAG_CYCLE[(i + 1) % _LOVS_TAG_CYCLE.length]);
  _lovsFocusPage = pn; _lovsRenderClassify();
}

function _lovsSetTagViaKey(k) {
  if (!(k in _LOVS_TAG_KEYS)) return false;
  var t = _LOVS_TAG_KEYS[k], pc = (typeof pageCount !== "undefined") ? pageCount : 0;
  if (_lovsSelected.size > 1) { _lovsSelected.forEach(function(n) { liteSetTag(n, t); }); _lovsRenderClassify(); return true; }
  if (!_lovsFocusPage) return false;
  liteSetTag(_lovsFocusPage, t);
  if (_lovsFocusPage < pc) _lovsFocusPage++;
  _lovsSelected.clear(); _lovsSelected.add(_lovsFocusPage); _lovsSelAnchor = _lovsFocusPage;
  _lovsRenderClassify();
  var el = document.querySelector('#grid-classify .ov-tile[data-pg="' + _lovsFocusPage + '"]');
  if (el) el.scrollIntoView({block: "nearest"});
  return true;
}

/* -- context menu -- */
function _lovsShowCtxMenu(e, pn) {
  var m = document.getElementById("ov-ctxmenu"); if (!m) return;
  var targets = _lovsSelected.has(pn) ? (function() { var a = []; _lovsSelected.forEach(function(n) { a.push(n); }); return a; })() : [pn];
  var pt = (typeof PAGE_TAGS !== "undefined") ? PAGE_TAGS : {};
  var h = targets.length > 1 ? '<div style="padding:4px 9px;font-size:10px;color:var(--muted,#8b97a8)">ทำกับ ' + targets.length + ' หน้า</div><div class="sep"></div>' : "";
  _LOVS_TAG_CYCLE.forEach(function(k) {
    var lbl = k ? (pt[k] || k) : "— ล้าง tag —";
    var cur = targets.length === 1 && (pageTags[targets[0]] || "") === k ? " ✓" : "";
    var ky = k ? ((Object.entries(_LOVS_TAG_KEYS).find(function(kv) { return kv[1] === k; }) || [])[0] || "") : "0";
    h += '<div class="it" data-ctx-tag="' + k + '"><span>' + lbl + cur + '</span><span class="k">' + ky + '</span></div>';
  });
  h += '<div class="sep"></div><div class="it" data-ctx-act="excl"><span>toggle exclude</span><span class="k">X</span></div>';
  if (targets.length === 1) h += '<div class="it" data-ctx-act="goto"><span>ไปหน้านี้</span><span class="k">Enter</span></div>';
  m.innerHTML = h; m.style.left = e.clientX + "px"; m.style.top = e.clientY + "px"; m.style.display = "block";
  m.querySelectorAll(".it").forEach(function(it) {
    it.addEventListener("click", function() {
      if (it.dataset.ctxAct === "excl") { var any = targets.some(function(t) { return excluded[t]; }); targets.forEach(function(t) { excluded[t] = !any; }); }
      else if (it.dataset.ctxAct === "goto") { if (typeof loadPage === "function") loadPage(targets[0]); if (typeof closeOverlays === "function") closeOverlays(); _lovsSelected.clear(); }
      else { targets.forEach(function(t) { liteSetTag(t, it.dataset.ctxTag); }); }
      _lovsRenderClassify(); _lovsHideCtx();
    });
  });
}

function _lovsHideCtx() { var m = document.getElementById("ov-ctxmenu"); if (m) m.style.display = "none"; }

/* ============================================================
   INV-2026-07-04-002 slice 2/4 — bulk floor auto-number apply
   ============================================================ */

/* Pure — no mutation, no undo. Mirrors overview-setup.js's
   _lovsSequentialFloor numbering convention EXACTLY:
     - basement: DESCENDING (first page in `pages` = deepest = largest
       number; last page in `pages` = 1) — same basementTotal/basementSeen
       formula as _lovsSequentialFloor, just driven by `pages` order
       (ascending page-number, i.e. Step-1 range-select order) instead of
       the Step-2 floor-strip DOM order.
     - mezzanine/mechanical/rooftop: consume NO number (num:null).
     - normal: ascends from startNum, only incrementing on normal pages
       (mirrors the exact same "n++ only in the normal/basement branches"
       shape as the source function).
   Per-page kind resolution is `pageFloorKind[p] || kind`: a page that
   was ALREADY floor-classified with a specific kind (e.g. hand-set to
   mezzanine before this range was selected) keeps ITS OWN kind — only
   untouched pages default to the bulk-kind selector's value. This
   mirrors _lovsSequentialFloor's own `pageFloorKind[pi] || "normal"`
   fallback.
   Deliberately EXCLUDED: _lovsSequentialFloor's "auto-infer the last
   page of a >=4 run as roof" heuristic. That guess is specific to the
   Sequential ⚡ button numbering a whole blind floor-strip; here kind is
   always explicit (bulkbar kind selector), so no such inference is
   needed or wanted. */
function _lovsBulkResolveMap(pages, kind, startNum) {
  var basementTotal = 0;
  for (var bi = 0; bi < pages.length; bi++) {
    if ((pageFloorKind[pages[bi]] || kind) === "basement") basementTotal++;
  }
  var basementSeen = 0;
  var n = (startNum > 0 ? startNum : 1);
  var out = [];
  for (var i = 0; i < pages.length; i++) {
    var p = pages[i];
    var k = pageFloorKind[p] || kind;
    if (k === "mezzanine" || k === "mechanical" || k === "rooftop") {
      out.push({p: p, kind: k, num: null});
    } else if (k === "basement") {
      out.push({p: p, kind: "basement", num: basementTotal - basementSeen});
      basementSeen++;
    } else {
      out.push({p: p, kind: "normal", num: n});
      n++;
    }
  }
  return out;
}

/* Entry point — called from the bulkbar "⚡ Apply" button.
   `pages` MUST be pre-sorted ascending (caller does this). If any
   selected page already carries a tag, defers to an inline confirm bar
   (_lovsBulkPending render branch above) instead of window.confirm —
   commit only happens on explicit user confirm; cancel = zero mutations. */
function _lovsBulkApply(pages, tag, kind, startNum) {
  if (!pages || !pages.length) return;
  var overlap = pages.filter(function(p) { return !!pageTags[p]; });
  if (overlap.length > 0) {
    _lovsBulkPending = {pages: pages, tag: tag, kind: kind, startNum: startNum, overlapCount: overlap.length};
    _lovsRenderClassify();
    return;
  }
  _lovsBulkCommit({pages: pages, tag: tag, kind: kind, startNum: startNum});
}

/* Commits a resolved batch: exactly ONE pushUndo() before the first
   mutation, then per-page liteSetTag + liteSetFloorKind + (if numbered)
   liteSetFloorNum — the same ui-lite.html writers every other Step-1/
   Step-2 control uses, so the liteSetTag PF-reseed wrap still fires. */
function _lovsBulkCommit(spec) {
  var map = _lovsBulkResolveMap(spec.pages, spec.kind, spec.startNum);
  if (typeof pushUndo === "function") pushUndo();
  map.forEach(function(row) {
    liteSetTag(row.p, spec.tag);
    liteSetFloorKind(row.p, row.kind);
    if (row.num != null) liteSetFloorNum(row.p, row.num);
  });
  _lovsSelected.clear();
  _lovsRenderClassify();
  if (typeof _lovsUpdateHeader === "function") _lovsUpdateHeader();
}
