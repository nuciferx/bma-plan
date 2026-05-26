/* ============================================================
   PAGE-FOLDER-LAYERS — per-page-setup folder model (LPFL-1a/1b/1c)
   Plain-globals module. No IIFE, no export, no bundler.
   Loaded AFTER layer-system.js, BEFORE inline script.

   Depends on (layer-system.js): FOLDERS, LAYERS, addFolder,
     folderById, addLayer, renameLayer, childrenOf, ancestorsOf, layerById,
     foldersInOrder, rollupArea, isDefaultLayer, removeFolder, removeLayer
   Depends on (layer-tree.js): _ltMakeSwatch, _ltOwnArea, _ltRenderLayer,
     _ltRenderFolder, buildPicker (wrapped in DOMContentLoaded)
   Depends on (inline script): state, PS, pageTags, pageFloorNum, pageCount,
     draw, liteSetTag, loadProto

   Public API (LPFL-1a):
     PAGE_FOLDER_PREFIX, pageFolderIdFor, seedPageFolders,
     pageFolderOfLayer, layersOfPage, isPageFolder, resetPageFolders

   Public API (LPFL-1c additions):
     togglePageFolderMode(forceState), reseedActivePageFolders,
     buildPagePicker (called via wrapped buildPicker when mode ON)

   Field extensions on FOLDERS entries (additive only):
     folder.pages?: number[]          — sorted unique page numbers
     folder.kind?: 'page-folder'|'user' — undefined on legacy = 'user'
   ============================================================ */

/* LOVS-1: dynamically load overview-setup.js (avoids editing ui-lite.html which is at cap) */
(function() {
  if (document.getElementById("__lovs_script__")) return;
  var s = document.createElement("script");
  s.src = "static/js/overview-setup.js";
  s.id = "__lovs_script__";
  s.async = false;
  document.head.appendChild(s);
})();

/* CFSS-1: dynamically load cross-floor-shapes.js (avoids editing ui-lite.html which is at cap) */
(function() {
  if (document.getElementById("__cfss_script__")) return;
  var s = document.createElement("script");
  s.id = "__cfss_script__";
  s.src = "static/js/cross-floor-shapes.js";
  s.async = false;
  document.head.appendChild(s);
})();

/* CFSS-MOVE: dynamically load cfss-dialogs.js AFTER cross-floor-shapes.js */
(function() {
  if (document.getElementById("__cfss_dialogs_script__")) return;
  var s = document.createElement("script");
  s.id = "__cfss_dialogs_script__";
  s.src = "static/js/cfss-dialogs.js";
  s.async = false;
  document.head.appendChild(s);
})();

/* LWIZ-AUTO: dynamically load wiz-auto.js (auto-open Overview wizard on first scale set) */
(function() {
  if (document.getElementById('__lwiz_auto_script__')) return;
  var s = document.createElement('script');
  s.id = '__lwiz_auto_script__';
  s.src = 'static/js/wiz-auto.js';
  s.async = false;
  document.head.appendChild(s);
})();

var PAGE_FOLDER_PREFIX = "PF_";

/* Return deterministic PF_* id for a page.
   site → PF_site | floor → PF_floor_<N> | else → PF_excluded */
function pageFolderIdFor(page, pageTags, pageFloorNum) {
  var tag = pageTags ? pageTags[page] : undefined;
  if (tag === "site") return "PF_site";
  if (tag === "floor") {
    var n = pageFloorNum ? pageFloorNum[page] : undefined;
    return "PF_floor_" + (n !== undefined && n !== null ? n : "?");
  }
  return "PF_excluded";
}

/* Internal: build {folderId → sorted unique page[]} map. */
function _collectFolderPages(pageList, pageTags, pageFloorNum) {
  var map = {};
  for (var i = 0; i < pageList.length; i++) {
    var pg = pageList[i];
    var fid = pageFolderIdFor(pg, pageTags, pageFloorNum);
    if (!map[fid]) map[fid] = [];
    map[fid].push(pg);
  }
  var result = {};
  for (var key in map) {
    if (Object.prototype.hasOwnProperty.call(map, key)) {
      var arr = map[key].sort(function(a, b) { return a - b; });
      var deduped = [];
      for (var j = 0; j < arr.length; j++) {
        if (j === 0 || arr[j] !== arr[j - 1]) deduped.push(arr[j]);
      }
      result[key] = deduped;
    }
  }
  return result;
}

/* Internal: extract floor label from PF_floor_<N>, else null. */
function _floorLabel(folderId) {
  var p = "PF_floor_";
  return folderId.indexOf(p) === 0 ? folderId.slice(p.length) : null;
}

/* LFOC-ORDER-A: deterministic .order rank for a PF folder id.
   PF_site=0, PF_floor_N=10+N*10 (floor#1→20, floor#2→30, …),
   PF_floor_roof=900, unknown PF=5000, PF_excluded=9999.
   Gap at order=10 reserved for a future PF_floor_0/mezzanine slot.
   Non-PF folders are never passed here. */
function _rankPFFolder(folderId) {
  if (folderId === "PF_site")        return 0;
  if (folderId === "PF_excluded")    return 9999;
  if (folderId === "PF_floor_roof")  return 900;
  var m = /^PF_floor_(\d+)$/.exec(folderId);
  if (m) return 10 + parseInt(m[1], 10) * 10;
  return 5000;
}

/* Internal: seed base layers under a newly created PF folder.
   site     → ที่ดิน(site) · พื้นที่อาคารปกคลุม(gfa) · แนวร่น(use)
   floor_N  → GFA ชั้น N(gfa) · หักช่องลิฟต์(ded) · หักช่องบันได(ded)
   excluded → none */
function _seedBaseLayers(folder) {
  var ids = [];
  function mk(role, name, color) {
    var l = addLayer(role, name, color);
    l.parentId = folder.id;
    ids.push(l.id);
  }
  if (folder.id === "PF_site") {
    mk("site", "ที่ดิน", "#c084fc");
    mk("gfa",  "พื้นที่อาคารปกคลุม", "#4c8dff");
    mk("use",  "แนวร่น (Setback)", "#ffb454");
  } else {
    var n = _floorLabel(folder.id);
    if (n !== null) {
      mk("gfa", "GFA ชั้น " + n, "#4c8dff");
      mk("ded", "หักช่องลิฟต์", "#ff6b6b");
      mk("ded", "หักช่องบันได", "#ff6b6b");
    }
    // PF_excluded → no base layers
  }
  return ids;
}

/* Idempotent seed. Creates PF_* folders for every distinct id derived
   from pageList. Existing folders: update .pages only (skip creation).
   New folders: create via addFolder → override .id with PF_* id →
   set .kind + .pages → seed base layers.
   Returns {created:[{kind,folderId,baseLayerIds}], skipped:[folderId]} */
function seedPageFolders(pageList, pageTags, pageFloorNum) {
  var folderPageMap = _collectFolderPages(pageList, pageTags, pageFloorNum);
  var created = [], skipped = [];

  // Stable order: PF_site(0) < PF_floor_*(1, numeric) < PF_excluded(2)
  var folderIds = Object.keys(folderPageMap);
  folderIds.sort(function(a, b) {
    var rank = function(id) {
      return id === "PF_site" ? 0 : id === "PF_excluded" ? 2 : 1;
    };
    var ra = rank(a), rb = rank(b);
    if (ra !== rb) return ra - rb;
    var na = _floorLabel(a), nb = _floorLabel(b);
    var fa = parseFloat(na), fb = parseFloat(nb);
    if (!isNaN(fa) && !isNaN(fb)) return fa - fb;
    return na < nb ? -1 : na > nb ? 1 : 0;
  });

  for (var i = 0; i < folderIds.length; i++) {
    var fid = folderIds[i];
    var pages = folderPageMap[fid];
    var existing = folderById(fid);
    if (existing) {
      existing.pages = pages;   // re-aggregate pages (only field updated on skip)
      skipped.push(fid);
    } else {
      var n = _floorLabel(fid);
      var displayName = fid === "PF_site" ? "ชั้นพื้นดิน / Site"
                      : n !== null        ? "ชั้น " + n
                      :                    "อื่น ๆ";
      var folder = addFolder(displayName, null, null);
      folder.id   = fid;          // override auto-id (F+n discarded for PF folders)
      folder.kind = "page-folder";
      folder.pages = pages;
      // Seed visibility/lock so eye/lock buttons work immediately
      if (!state.catVis[fid])  state.catVis[fid]  = true;
      if (state.catLock[fid] === undefined) state.catLock[fid] = false;
      var baseLayerIds = _seedBaseLayers(folder);
      created.push({kind: fid === "PF_site" ? "site" : n !== null ? "floor" : "excluded",
                    folderId: fid, baseLayerIds: baseLayerIds});
    }
  }
  /* LFOC-ORDER-A: re-rank PF folder .order deterministically so they render
     in workflow order regardless of creation sequence. Idempotent — safe to
     call on every seed. Non-PF folders (kind !== 'page-folder') are untouched. */
  for (var fi = 0; fi < FOLDERS.length; fi++) {
    var _f = FOLDERS[fi];
    if (_f && _f.kind === "page-folder") {
      _f.order = _rankPFFolder(_f.id);
    }
  }

  return {created: created, skipped: skipped};
}

/* Walk parentId chain; return first ancestor folder with kind==='page-folder', else null. */
function pageFolderOfLayer(layerId) {
  var ancestors = ancestorsOf(layerId);
  for (var i = 0; i < ancestors.length; i++) {
    var f = folderById(ancestors[i]);
    if (f && f.kind === "page-folder") return f;
  }
  return null;
}

/* Internal: DFS over childrenOf(nodeId), collect only layer nodes. */
function _descendantLayers(nodeId) {
  var result = [];
  var children = childrenOf(nodeId);
  for (var i = 0; i < children.length; i++) {
    var child = children[i];
    if (child.kind === "layer") {
      result.push(child.node);
    } else {
      var sub = _descendantLayers(child.node.id);
      for (var j = 0; j < sub.length; j++) result.push(sub[j]);
    }
  }
  return result;
}

/* Return all layers that are descendants of the PF folder for this page. */
function layersOfPage(page, pageTags, pageFloorNum) {
  var fid = pageFolderIdFor(page, pageTags, pageFloorNum);
  var folder = folderById(fid);
  return folder ? _descendantLayers(fid) : [];
}

/* True iff the given folder id or folder object has kind==='page-folder'. */
function isPageFolder(folderIdOrFolder) {
  var f = typeof folderIdOrFolder === "string"
        ? folderById(folderIdOrFolder)
        : folderIdOrFolder;
  return !!(f && f.kind === "page-folder");
}

/* Remove all PF folders and layers parented under them. Splice in place.
   Returns count of folders removed. */
function resetPageFolders() {
  var removed = 0;
  // Remove PF-parented layers first (reverse for safe splice)
  for (var i = LAYERS.length - 1; i >= 0; i--) {
    var l = LAYERS[i];
    if (l.parentId && typeof l.parentId === "string" &&
        l.parentId.indexOf(PAGE_FOLDER_PREFIX) === 0) {
      LAYERS.splice(i, 1);
    }
  }
  // Remove PF folders
  for (var j = FOLDERS.length - 1; j >= 0; j--) {
    if (FOLDERS[j].kind === "page-folder") { FOLDERS.splice(j, 1); removed++; }
  }
  return removed;
}

/* ================================================================
   LPFL-1c: UI layer — page-folder mode panel + toggle + bootstrap
   ================================================================ */

/* ------------------------------------------------------------------
   _pflPageLabel(folder)
   Build the page suffix label for a PF folder header.
   ≤4 pages → "(p5,12)" ; >4 pages → "(8 หน้า)"
   ------------------------------------------------------------------ */
function _pflPageLabel(folder) {
  var pages = folder.pages;
  if (!pages || pages.length === 0) return "";
  if (pages.length <= 4) {
    return "(p" + pages.join(",") + ")";
  }
  return "(" + pages.length + " หน้า)";
}

/* ------------------------------------------------------------------
   _pflFolderDisplayName(folder)
   Human-readable header for a PF folder: icon + role label.
   ------------------------------------------------------------------ */
function _pflFolderDisplayName(folder) {
  if (folder.id === "PF_site") return "🏗 ผังบริเวณ";
  if (folder.id === "PF_excluded") return "📦 อื่น ๆ";
  var n = _floorLabel(folder.id);
  if (n !== null) return "🏢 ชั้น " + n;
  return folder.name;
}

/* ------------------------------------------------------------------
   buildPagePicker()
   Renders the #catlist in page-folder mode.
   Only PF folders (kind==='page-folder') are rendered with the PF
   decoration. User folders/layers are rendered via existing helpers.
   ------------------------------------------------------------------ */
function buildPagePicker() {
  var el = document.getElementById("catlist");
  if (!el) return;
  el.innerHTML = "";

  if (!state.folderCollapsed) state.folderCollapsed = {};

  // Partition roots: PF folders first (ordered), then rest
  var roots = childrenOf(null);
  var pfRoots = [], otherRoots = [];
  for (var ri = 0; ri < roots.length; ri++) {
    var item = roots[ri];
    if (item.kind === "folder" && item.node.kind === "page-folder") {
      pfRoots.push(item);
    } else {
      otherRoots.push(item);
    }
  }

  // Render PF folders with decoration
  for (var pi = 0; pi < pfRoots.length; pi++) {
    _pflRenderPFFolder(pfRoots[pi].node, 0, el);
  }

  // LFOC-1a + LFOC-1b reconciled: orphan items (non-PF roots) HIDDEN in folder-only mode.
  // Show a single info banner so user knows data exists but is suppressed.
  if (otherRoots.length > 0) {
    var hidden = document.createElement("div");
    hidden.className = "cat lt-orphan-info";
    hidden.style.cssText = "padding:6px 10px;color:var(--muted,#8b97a8);font-size:11px;font-style:italic;border-top:1px dashed var(--line,#2a3140);margin-top:4px";
    hidden.textContent = "(ซ่อน " + otherRoots.length + " รายการที่อยู่นอก page-folder)";
    el.appendChild(hidden);
  }
}

/* ------------------------------------------------------------------
   _pflRenderPFFolder(folder, depth, el)
   Render one PF folder row with page-count decoration, then recurse
   into children. No delete button for PF folders (they are managed).
   Matches the DOM structure of _ltRenderFolder for DnD compatibility.
   ------------------------------------------------------------------ */
function _pflRenderPFFolder(folder, depth, el) {
  var collapsed = !!state.folderCollapsed[folder.id];
  var vis = state.catVis[folder.id] !== false;
  var lk  = state.catLock[folder.id] === true;

  var d = document.createElement("div");
  d.className = "cat lt-folder-row";
  d.setAttribute("data-catid", folder.id);
  d.setAttribute("data-nodekind", "folder");
  d.style.marginLeft = (depth * 16) + "px";

  // Collapse toggle
  var tog = document.createElement("span");
  tog.className = "lt-collapse-toggle";
  tog.textContent = collapsed ? "▸" : "▾";
  tog.title = collapsed ? "ขยาย" : "ย่อ";
  tog.style.cursor = "pointer";
  tog.style.fontSize = "11px";
  tog.style.marginRight = "2px";
  tog.style.color = "var(--muted)";
  tog.addEventListener("click", function(e) {
    e.stopPropagation();
    if (!state.folderCollapsed) state.folderCollapsed = {};
    state.folderCollapsed[folder.id] = !state.folderCollapsed[folder.id];
    buildPicker();
  });

  // Folder icon (open book for PF)
  var icon = document.createElement("span");
  icon.textContent = "📂";
  icon.style.fontSize = "12px";
  icon.style.marginRight = "2px";

  // Swatch (use existing helper if available)
  var sw;
  if (typeof _ltMakeSwatch === "function") {
    sw = _ltMakeSwatch(
      folder.id,
      function() { return folder.color || "#4c8dff"; },
      function(v) { folder.color = v; }
    );
  } else {
    sw = document.createElement("span");
    sw.className = "sw lp-sw";
    sw.style.background = folder.color || "#4c8dff";
  }

  // Name span with page-label decoration
  var nm = document.createElement("span");
  nm.className = "nm";
  var pageLabel = _pflPageLabel(folder);
  nm.textContent = _pflFolderDisplayName(folder) + (pageLabel ? " " : "");
  if (pageLabel) {
    var small = document.createElement("small");
    small.textContent = pageLabel;
    small.style.color = "var(--muted)";
    small.style.fontSize = "10px";
    nm.appendChild(small);
  }

  // Roll-up area
  var roll = (typeof rollupArea === "function" && typeof _ltOwnArea === "function")
    ? rollupArea(folder.id, _ltOwnArea) : 0;
  var rollSpan = null;
  if (isFinite(roll) && roll !== 0) {
    rollSpan = document.createElement("span");
    rollSpan.className = "lt-area";
    rollSpan.textContent = "Σ " + roll.toLocaleString(undefined, {maximumFractionDigits: 2}) + " m²";
    rollSpan.style.marginLeft = "auto";
    rollSpan.style.color = "#8b949e";
    rollSpan.style.fontSize = "11px";
    rollSpan.style.pointerEvents = "none";
  }

  // Eye button
  var eye = document.createElement("span");
  eye.className = "eye" + (vis ? "" : " off");
  eye.setAttribute("data-eye", folder.id);
  eye.textContent = vis ? "👁" : "🚫";

  // Lock button
  var lkBtn = document.createElement("span");
  lkBtn.className = "eye" + (lk ? " off" : "");
  lkBtn.setAttribute("data-lock", folder.id);
  lkBtn.textContent = lk ? "🔒" : "🔓";

  // Row click handler (eye / lock)
  d.addEventListener("click", function(e) {
    if (e.target.dataset.eye) {
      state.catVis[folder.id] = (state.catVis[folder.id] === false) ? true : false;
      buildPicker(); draw(); return;
    }
    if (e.target.dataset.lock) {
      state.catLock[folder.id] = !state.catLock[folder.id];
      buildPicker(); draw(); return;
    }
  });

  d.appendChild(tog);
  d.appendChild(icon);
  d.appendChild(sw);
  d.appendChild(nm);
  if (rollSpan) d.appendChild(rollSpan);
  d.appendChild(eye);
  d.appendChild(lkBtn);
  // NOTE: no ✕ delete button for PF folders (managed by page-folder system)
  el.appendChild(d);

  // Recurse into children unless collapsed
  if (!collapsed) {
    var kids = childrenOf(folder.id);
    for (var ki = 0; ki < kids.length; ki++) {
      var kid = kids[ki];
      if (kid.kind === "folder") {
        if (kid.node.kind === "page-folder") {
          _pflRenderPFFolder(kid.node, depth + 1, el);
        } else if (typeof _ltRenderFolder === "function") {
          _ltRenderFolder(kid.node, depth + 1, el);
        }
      } else {
        if (typeof _ltRenderLayer === "function") {
          _ltRenderLayer(kid.node, depth + 1, el);
        }
      }
    }
    // "+ เพิ่ม layer" row inside each PF folder
    var addRow = document.createElement("div");
    addRow.className = "cat lt-add";
    addRow.setAttribute("data-pf-add", folder.id);
    addRow.style.marginLeft = ((depth + 1) * 16) + "px";
    addRow.style.color = "var(--muted)";
    addRow.style.fontSize = "12px";
    var floorN = _floorLabel(folder.id);
    var folderLabel = folder.id === "PF_site" ? "ผังบริเวณ"
                    : floorN !== null ? "ชั้น " + floorN
                    : "อื่น ๆ";
    var addNm = document.createElement("span");
    addNm.className = "nm";
    addNm.textContent = "+ เพิ่ม layer ใน" + folderLabel;
    addRow.appendChild(addNm);
    addRow.addEventListener("click", function(fid, flabel) {
      return function(e) {
        e.stopPropagation();
        var name = window.prompt("ชื่อ layer ใหม่ใน " + flabel + ":", "");
        if (!name || !name.trim()) return;
        var newLayer = addLayer("gfa", name.trim(), "#4c8dff");
        if (!newLayer) return;
        newLayer.parentId = fid;
        if (state.catVis[newLayer.id] === undefined) state.catVis[newLayer.id] = true;
        if (state.catLock[newLayer.id] === undefined) state.catLock[newLayer.id] = false;
        state.activeCat = newLayer.id;
        state.dirty = true;
        buildPicker();
        if (typeof draw === "function") draw();
      };
    }(folder.id, folderLabel));
    el.appendChild(addRow);
  }
}

/* ------------------------------------------------------------------
   togglePageFolderMode(forceState)
   LFOC-1b: page-folder mode is permanent. Always forces ON.
   forceState ignored (no flat mode). Kept for test/forward-compat.
   ------------------------------------------------------------------ */
function togglePageFolderMode(forceState) {
  // LFOC-1b: page-folder mode is permanent. Always force ON. forceState ignored.
  state.pageFolderMode = true;
  reseedActivePageFolders();
  buildPicker();
}

/* ------------------------------------------------------------------
   reseedActivePageFolders()
   Idempotent reseed — always active (LFOC-1b: mode is always ON).
   ------------------------------------------------------------------ */
function reseedActivePageFolders() {
  if (!state) return;
  var pages = Object.keys(PS).map(Number).filter(function(n) { return !isNaN(n); });
  if (pages.length === 0 && typeof pageCount !== "undefined" && pageCount > 0) {
    for (var i = 1; i <= pageCount; i++) pages.push(i);
  }
  if (pages.length === 0) return;
  seedPageFolders(pages, pageTags, pageFloorNum);
}

/* ------------------------------------------------------------------
   _pflInjectToggleButton()
   Inject #pfl-toggle button into #picker .h. Idempotent.
   ------------------------------------------------------------------ */
function _pflInjectToggleButton() {
  var header = document.querySelector("#picker .h");
  if (!header) return;
  // Find the existing button cluster (last span child of header)
  var spans = header.querySelectorAll("span");
  if (!spans.length) return;
  var btnGroup = spans[spans.length - 1];
  if (!btnGroup) return;
  if (document.getElementById("pfl-toggle")) return; // idempotent
  var btn = document.createElement("button");
  btn.className = "lp-add-btn";
  btn.id = "pfl-toggle";
  btn.title = "สลับ page-folder mode (auto-seed ตาม pageTags)";
  btn.textContent = (state && state.pageFolderMode) ? "📂✓" : "📂";
  btn.addEventListener("click", function() {
    togglePageFolderMode();
  });
  btnGroup.appendChild(btn);
}

/* ------------------------------------------------------------------
   Bootstrap — runs after DOMContentLoaded (all scripts loaded).
   LFOC-1b: page-folder mode is now ALWAYS ON (no toggle).
   1. Force state.pageFolderMode = true (backward compat: old .bmaplan
      with pageFolderMode=false is upgraded silently here).
   2. Wrap buildPicker → always returns page-folder render.
   3. Wrap liteSetTag  → reseed after tag change.
   4. Wrap loadProto   → reseed after .bmaplan load (always).
   5. Auto-seed on init (defer one tick for DOM settle).
   Note: no toggle button injection. Mode is permanent.
   ------------------------------------------------------------------ */
window.addEventListener("DOMContentLoaded", function() {
  // LFOC-1b: page-folder mode is now ALWAYS ON (no toggle). Default true on init.
  // For backward compat (loading old .bmaplan with state.pageFolderMode=false),
  // we still force true here — there is no flat mode anymore.
  if (state) state.pageFolderMode = true;

  // 1. Wrap buildPicker — now always returns page-folder render.
  // IMPORTANT: at DOMContentLoaded time, buildPicker has already been wrapped by
  // layer-dnd.js at module load time (DND wraps = _origBP() + ltDndDecorate()).
  // We must preserve ltDndDecorate() post-processing by calling it explicitly
  // after buildPagePicker() — this keeps tabIndex + keyboard reorder working.
  if (typeof buildPicker === "function" && !buildPicker.__pflWrapped) {
    var _pflOrigBuildPicker = buildPicker;
    buildPicker = function() {
      // LFOC-1b: always page-folder render. After buildPagePicker() runs,
      // call ltDndDecorate() to restore DND post-processing (tabIndex + keydown).
      try { buildPagePicker(); }
      catch (_e) { _pflOrigBuildPicker.apply(this, arguments); return; }
      if (typeof ltDndDecorate === "function") ltDndDecorate();
    };
    buildPicker.__pflWrapped = true;
  }

  // 2. Wrap liteSetTag — reseed always (mode is always on)
  if (typeof liteSetTag === "function" && !liteSetTag.__pflWrapped) {
    var _pflOrigSetTag = liteSetTag;
    liteSetTag = function(n, val) {
      _pflOrigSetTag(n, val);
      reseedActivePageFolders();
    };
    liteSetTag.__pflWrapped = true;
  }

  // 3. Wrap loadProto — reseed after load (mode always on)
  if (typeof loadProto === "function" && !loadProto.__pflWrapped) {
    var _pflOrigLoad = loadProto;
    loadProto = function(doc) {
      _pflOrigLoad(doc);
      reseedActivePageFolders();
    };
    loadProto.__pflWrapped = true;
  }

  // 4. Auto-seed on init (don't wait for first action)
  setTimeout(function() { reseedActivePageFolders(); }, 0);

  // 5. LFOC-1b: no toggle button injection. Mode is permanent.
});
