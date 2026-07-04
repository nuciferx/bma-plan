/* ============================================================
   LITE-LAYER-SCOPE — context-scoped panel + floor-rail + search
   (INV-2026-07-04-001 slice 1/3 + slice 2/3)
   Plain-globals module. No IIFE, no export, no bundler.
   Loaded right after layer-tree.js, before layer-dnd.js.

   SLICE 2/3 ADDITIONS: a search row (input + results dropdown) mounted
   above the rail-controls row inside the same #ls-rail host. Flat
   case-insensitive substring scan over FOLDERS (page-folder kind) +
   LAYERS at query time (≤~600 entries — no persistent index needed).
   Results grouped by containing PF folder, kind-aware order, capped at
   LS_SEARCH_CAP (30) with a "shown/total" badge when truncated. Click
   a folder result -> _lsGoTo(folder); click a layer result ->
   _lsGoTo(its PF folder) then highlight that layer's row once it
   re-renders (queued in _lsPendingHighlight, applied by
   _lsApplyPendingHighlight() right after every wrapped buildPicker()
   call — handles the async gap in loadPage() without a second render
   path).

   TIMING NOTE (why this must be a DOMContentLoaded listener, not a
   synchronous top-level wrap like layer-dnd.js uses): PF mode is
   permanent (LFOC-1b) and page-folder-layers.js's own DOMContentLoaded
   listener reassigns the global `buildPicker` to a version whose
   SUCCESS path calls buildPagePicker() directly — it does not call
   whatever `buildPicker` pointed to before that reassignment except in
   an error-fallback branch. So a synchronous wrap registered here would
   be silently discarded from the normal render path. Instead this
   module also waits for DOMContentLoaded and registers its own
   listener; listener execution order follows registration order, which
   follows <script> tag order — page-folder-layers.js's script tag
   comes before this one, so its listener fires first (finishing the
   reassignment), and this module's listener fires second and wraps the
   FINAL, already-correct `buildPicker`.

   Scope: does NOT edit page-folder-layers.js or reimplement the
   folder/layer tree walk. It post-processes whatever DOM buildPicker()
   already produced in #catlist:
     (a) removes DOM rows belonging to non-active PF_* folders (plus
         their "+ เพิ่ม layer" add-rows), when scope is active
     (b) mounts/updates a floor-rail host directly above #catlist

   Bidirectional binding comes free, no second render path added:
   loadPage() -> afterPage() -> buildPicker() (ui-lite.html:427) already
   re-runs this module's post-process on every page navigation, and this
   module's rail controls call loadPage() themselves.

   Runtime-only state (NOT persisted; no .bmaplan change this slice):
     state.scopeByPage — bool, default true when undefined (PF mode ON
                         + scopeByPage !== false = scope active)

   Depends on globals from:
     layer-system.js       — FOLDERS, folderById, foldersInOrder,
                              childrenOf
     inline script          — state, curPage, loadPage (referenced
                              lazily inside click/change handlers —
                              already defined by the time a user can
                              click, even though page-renderer.js loads
                              after this file)

   Public API:
     lsScopeActive(), lsFolderForPage(page), lsPFFoldersOrdered(),
     lsEnsureRailHost(catlistEl), lsRenderRail(hostEl), lsSearch(query)
   ============================================================ */

/* ------------------------------------------------------------------
   lsScopeActive()
   PF mode is permanent (LFOC-1b) but this predicate still reads
   state.pageFolderMode defensively — tests may force it false to
   exercise the "render as before, no rail" path. scopeByPage defaults
   to ON: undefined is treated as true so no new .bmaplan field is
   required for the default behavior.
   ------------------------------------------------------------------ */
function lsScopeActive() {
  return !!(state && state.pageFolderMode && state.scopeByPage !== false);
}

/* ------------------------------------------------------------------
   lsFolderForPage(p)
   The PF_* folder whose .pages includes page p, else null.
   PF_excluded is deliberately treated as "no folder" — untagged/
   excluded pages fall back to the unfiltered render + a "—" rail
   instead of scoping down to the catch-all bucket (checkpoint decision
   in docs/invent/lite-layer-menu-ui-fix.md).
   ------------------------------------------------------------------ */
function lsFolderForPage(p) {
  if (typeof FOLDERS === "undefined" || p === undefined || p === null) return null;
  for (var i = 0; i < FOLDERS.length; i++) {
    var f = FOLDERS[i];
    if (f && f.kind === "page-folder" && f.id !== "PF_excluded" &&
        Array.isArray(f.pages) && f.pages.indexOf(p) !== -1) {
      return f;
    }
  }
  return null;
}

/* ------------------------------------------------------------------
   lsPFFoldersOrdered()
   Kind-aware ordered PF folders. Reuses foldersInOrder() — PF folders'
   .order already equals _rankPFFolder(id) after any reseed (see
   page-folder-layers.js's seedPageFolders re-rank pass), so this needs
   no new sort. PF_excluded is excluded from the rail (no "next floor"
   semantics for the catch-all bucket).
   ------------------------------------------------------------------ */
function lsPFFoldersOrdered() {
  if (typeof foldersInOrder !== "function") return [];
  return foldersInOrder().filter(function(f) {
    return f && f.kind === "page-folder" && f.id !== "PF_excluded";
  });
}

/* ------------------------------------------------------------------
   _lsSubtreeIds(rootId)
   rootId + every descendant id (folders and layers), via childrenOf().
   Rows in #catlist are flat siblings indented by marginLeft (not real
   parent/child DOM nodes), so removing a whole non-active PF folder's
   rendered rows needs the model-level id set, not DOM traversal.
   ------------------------------------------------------------------ */
function _lsSubtreeIds(rootId) {
  var ids = [rootId];
  if (typeof childrenOf !== "function") return ids;
  var kids = childrenOf(rootId);
  for (var i = 0; i < kids.length; i++) {
    ids = ids.concat(_lsSubtreeIds(kids[i].node.id));
  }
  return ids;
}

/* ------------------------------------------------------------------
   lsEnsureRailHost(catlistEl)
   Creates (once) a '#ls-rail' div as the previous sibling of #catlist,
   so it survives buildPicker()'s el.innerHTML="" clears (those only
   clear #catlist's own contents, never its siblings).
   ------------------------------------------------------------------ */
function lsEnsureRailHost(catlistEl) {
  if (!catlistEl || !catlistEl.parentNode) return null;
  var host = document.getElementById("ls-rail");
  if (!host) {
    host = document.createElement("div");
    host.id = "ls-rail";
    host.className = "ls-rail";
    catlistEl.parentNode.insertBefore(host, catlistEl);
  }
  return host;
}

/* ------------------------------------------------------------------
   _lsGoTo(folder)
   Shared navigation: warps the canvas to folder.pages[0] via the real
   loadPage(). Used by both the rail controls (prev/select/next) and
   search-result clicks.
   ------------------------------------------------------------------ */
function _lsGoTo(folder) {
  if (folder && Array.isArray(folder.pages) && folder.pages.length &&
      typeof loadPage === "function") {
    loadPage(folder.pages[0]);
  }
}

/* ------------------------------------------------------------------
   lsRenderRail(hostEl)
   Mounts (once) a search row above a rail-controls row, both inside
   hostEl (#ls-rail). The search row persists across renders (so typing
   a query survives unrelated buildPicker() calls, e.g. an eye-toggle
   click elsewhere); only the controls row is rebuilt every call.
   Controls: ◀ | <select of PF folders, kind-aware order> | ▶ + "ชั้น
   i/N" counter, navigating via _lsGoTo(). When the current page
   doesn't resolve to any folder (lsFolderForPage returns null), shows
   a plain "—" instead of non-functional controls.
   ------------------------------------------------------------------ */
function lsRenderRail(hostEl) {
  if (!hostEl) return;
  lsEnsureSearchRow(hostEl);

  var controls = document.getElementById("ls-rail-controls");
  if (!controls) {
    controls = document.createElement("div");
    controls.id = "ls-rail-controls";
    controls.className = "ls-rail-controls";
    hostEl.appendChild(controls);
  }
  controls.innerHTML = "";

  var activeFolder = lsFolderForPage(typeof curPage !== "undefined" ? curPage : null);
  if (!activeFolder) {
    var dash = document.createElement("span");
    dash.className = "ls-rail-dash";
    dash.textContent = "—";
    controls.appendChild(dash);
    return;
  }

  var ordered = lsPFFoldersOrdered();
  var idx = -1;
  for (var i = 0; i < ordered.length; i++) {
    if (ordered[i].id === activeFolder.id) { idx = i; break; }
  }

  var prevBtn = document.createElement("button");
  prevBtn.type = "button";
  prevBtn.className = "ls-rail-btn";
  prevBtn.id = "ls-rail-prev";
  prevBtn.textContent = "◀";
  prevBtn.title = "ชั้นก่อนหน้า";
  prevBtn.disabled = idx <= 0;
  prevBtn.addEventListener("click", function() { if (idx > 0) _lsGoTo(ordered[idx - 1]); });

  var sel = document.createElement("select");
  sel.className = "ls-rail-select";
  sel.id = "ls-rail-jump";
  ordered.forEach(function(f) {
    var opt = document.createElement("option");
    opt.value = f.id;
    opt.textContent = f.name;
    sel.appendChild(opt);
  });
  sel.value = activeFolder.id;
  sel.addEventListener("change", function() { _lsGoTo(folderById(sel.value)); });

  var nextBtn = document.createElement("button");
  nextBtn.type = "button";
  nextBtn.className = "ls-rail-btn";
  nextBtn.id = "ls-rail-next";
  nextBtn.textContent = "▶";
  nextBtn.title = "ชั้นถัดไป";
  nextBtn.disabled = (idx < 0) || (idx >= ordered.length - 1);
  nextBtn.addEventListener("click", function() {
    if (idx >= 0 && idx < ordered.length - 1) _lsGoTo(ordered[idx + 1]);
  });

  var counter = document.createElement("span");
  counter.className = "ls-rail-counter";
  counter.textContent = "ชั้น " + (idx >= 0 ? (idx + 1) : "?") + "/" + ordered.length;

  controls.appendChild(prevBtn);
  controls.appendChild(sel);
  controls.appendChild(nextBtn);
  controls.appendChild(counter);
}

/* ------------------------------------------------------------------
   LS_SEARCH_CAP / lsSearch(q)
   Flat case-insensitive substring scan over PF folder names + layer
   names (folder.name / layer.name). Layers with no PF ancestor are
   skipped (this is a floor-scoped search — a layer that isn't inside
   any PF folder has nowhere to jump to). Grouped by containing PF
   folder in kind-aware order (lsPFFoldersOrdered()); a folder-name
   match adds the folder itself (type "folder") to its own group.
   Cap applies across ALL matches in group order — badge shows the
   REAL total so a common name (e.g. "ผนัง") across 100 floors never
   silently truncates without saying so (opus review concern #1).
   ------------------------------------------------------------------ */
var LS_SEARCH_CAP = 30;
function lsSearch(q) {
  var query = (q || "").trim().toLowerCase();
  var out = {groups: [], total: 0, shown: 0};
  if (!query) return out;
  if (typeof FOLDERS === "undefined" || typeof LAYERS === "undefined") return out;

  var ordered = lsPFFoldersOrdered();
  var orderIndex = {};
  ordered.forEach(function(f, i) { orderIndex[f.id] = i; });

  var groupMap = {};
  var total = 0;
  function ensureGroup(folder) {
    if (!groupMap[folder.id]) groupMap[folder.id] = {folder: folder, items: []};
    return groupMap[folder.id];
  }

  ordered.forEach(function(f) {
    if (f.name && f.name.toLowerCase().indexOf(query) !== -1) {
      total++;
      if (total <= LS_SEARCH_CAP) ensureGroup(f).items.push({type: "folder", node: f});
    }
  });

  LAYERS.forEach(function(l) {
    if (!l.name || l.name.toLowerCase().indexOf(query) === -1) return;
    var folder = (typeof pageFolderOfLayer === "function") ? pageFolderOfLayer(l.id) : null;
    if (!folder) return; // no PF ancestor — not floor-navigable, skip
    total++;
    if (total <= LS_SEARCH_CAP) ensureGroup(folder).items.push({type: "layer", node: l});
  });

  var groups = Object.keys(groupMap).map(function(fid) { return groupMap[fid]; });
  groups.sort(function(a, b) {
    var ai = (orderIndex[a.folder.id] !== undefined) ? orderIndex[a.folder.id] : 9999;
    var bi = (orderIndex[b.folder.id] !== undefined) ? orderIndex[b.folder.id] : 9999;
    return ai - bi;
  });

  out.groups = groups;
  out.total = total;
  out.shown = Math.min(total, LS_SEARCH_CAP);
  return out;
}

/* ------------------------------------------------------------------
   _lsPendingHighlight / _lsApplyPendingHighlight()
   Clicking a layer search result queues its id here, then navigates.
   loadPage() is async (canvas/PDF work happens before afterPage() ->
   buildPicker() eventually re-renders #catlist) so the target row may
   not exist yet on the render right after the click. Every wrapped
   buildPicker() call re-checks (see bootstrap below); once the row
   exists it gets a transient highlight class, auto-removed ~1.5s
   later, and the pending id is cleared. A 3s safety timeout also
   clears it in case navigation never lands, so a later unrelated
   render never highlights a stale id.
   ------------------------------------------------------------------ */
var _lsPendingHighlight = null;
function _lsApplyPendingHighlight() {
  if (!_lsPendingHighlight) return;
  var catlist = document.getElementById("catlist");
  if (!catlist) return;
  var row = catlist.querySelector('.cat[data-catid="' + _lsPendingHighlight + '"]');
  if (!row) return; // not rendered yet — wait for a later buildPicker() call
  row.classList.add("ls-search-hl");
  _lsPendingHighlight = null;
  setTimeout(function() { row.classList.remove("ls-search-hl"); }, 1500);
}
function _lsQueueHighlight(layerId) {
  _lsPendingHighlight = layerId;
  setTimeout(function() {
    if (_lsPendingHighlight === layerId) _lsPendingHighlight = null;
  }, 3000);
}

/* ------------------------------------------------------------------
   lsEnsureSearchRow(hostEl)
   Creates (once) the search input + results dropdown as the first
   child of hostEl (#ls-rail), above the rail-controls row. Debounced
   ~120ms; Esc clears + closes; blur closes (mousedown+preventDefault
   on result rows keeps focus so a click registers before blur would
   close the dropdown); Enter activates the first result.
   ------------------------------------------------------------------ */
function lsEnsureSearchRow(hostEl) {
  var wrap = document.getElementById("ls-search-wrap");
  if (wrap) return wrap;

  wrap = document.createElement("div");
  wrap.id = "ls-search-wrap";
  wrap.className = "ls-search-wrap";

  var input = document.createElement("input");
  input.type = "text";
  input.id = "ls-search-input";
  input.className = "ls-search-input";
  input.placeholder = "ค้นหาชั้น / layer…";
  input.autocomplete = "off";

  var results = document.createElement("div");
  results.id = "ls-search-results";
  results.className = "ls-search-results";
  results.style.display = "none";

  var debounceTimer = null;
  input.addEventListener("input", function() {
    if (debounceTimer) clearTimeout(debounceTimer);
    var val = input.value;
    debounceTimer = setTimeout(function() { _lsRenderSearchResults(val, results); }, 120);
  });
  input.addEventListener("keydown", function(e) {
    if (e.key === "Escape") {
      input.value = "";
      results.innerHTML = "";
      results.style.display = "none";
    } else if (e.key === "Enter") {
      var first = results.querySelector("[data-ls-result]");
      if (first) first.dispatchEvent(new MouseEvent("mousedown", {bubbles: true}));
    }
  });
  input.addEventListener("blur", function() {
    setTimeout(function() { results.style.display = "none"; }, 150);
  });

  wrap.appendChild(input);
  wrap.appendChild(results);
  hostEl.insertBefore(wrap, hostEl.firstChild);
  return wrap;
}

/* ------------------------------------------------------------------
   _lsRenderSearchResults(query, resultsEl)
   Runs lsSearch(query), renders grouped results (group header = PF
   folder name) + a "shown/total" badge when capped. Click on a folder
   result jumps there; click on a layer result jumps to its folder and
   queues a highlight for that layer's row.
   ------------------------------------------------------------------ */
function _lsRenderSearchResults(query, resultsEl) {
  var q = (query || "").trim();
  resultsEl.innerHTML = "";
  if (!q) { resultsEl.style.display = "none"; return; }

  var res = lsSearch(q);
  if (res.groups.length === 0) { resultsEl.style.display = "none"; return; }

  res.groups.forEach(function(g) {
    var header = document.createElement("div");
    header.className = "ls-search-group-header";
    header.textContent = g.folder.name;
    resultsEl.appendChild(header);

    g.items.forEach(function(item) {
      var row = document.createElement("div");
      row.className = "ls-search-result";
      row.setAttribute("data-ls-result", "1");
      row.setAttribute("data-ls-type", item.type);
      row.setAttribute("data-ls-id", item.node.id);
      row.textContent = (item.type === "folder" ? "📁 " : "▫ ") + item.node.name;
      row.addEventListener("mousedown", function(e) {
        e.preventDefault(); // keep input focused so this fires before blur would close us
        if (item.type === "layer") {
          _lsQueueHighlight(item.node.id);
          var folder = (typeof pageFolderOfLayer === "function") ? pageFolderOfLayer(item.node.id) : null;
          _lsGoTo(folder);
        } else {
          _lsGoTo(item.node);
        }
        resultsEl.style.display = "none";
      });
      resultsEl.appendChild(row);
    });
  });

  if (res.total > res.shown) {
    var badge = document.createElement("div");
    badge.className = "ls-search-badge";
    badge.textContent = "แสดง " + res.shown + " จาก " + res.total + " — พิมพ์เพิ่มเพื่อกรอง";
    resultsEl.appendChild(badge);
  }

  resultsEl.style.display = "block";
}

/* ------------------------------------------------------------------
   _lsPostRender()
   Runs after every buildPicker() call (wrapped below). Mounts/updates
   the rail, then — when scope is active and the current page resolves
   to a folder — removes non-active PF_* folders' rows from #catlist.
   Non-PF top-level items (user layers/folders) are never touched;
   only kind==="page-folder" subtrees other than the active one.
   ------------------------------------------------------------------ */
function _lsPostRender() {
  var catlist = document.getElementById("catlist");
  if (!catlist) return;
  var host = lsEnsureRailHost(catlist);
  var active = lsScopeActive();

  if (host) host.style.display = active ? "" : "none";
  if (!active) return;
  if (host) lsRenderRail(host);

  var activeFolder = lsFolderForPage(typeof curPage !== "undefined" ? curPage : null);
  if (!activeFolder) return; // untagged/excluded page — fallback, unfiltered render

  if (typeof FOLDERS === "undefined") return;
  var others = FOLDERS.filter(function(f) {
    return f && f.kind === "page-folder" && f.id !== activeFolder.id;
  });
  others.forEach(function(f) {
    _lsSubtreeIds(f.id).forEach(function(id) {
      var row = catlist.querySelector('.cat[data-catid="' + id + '"]');
      if (row) row.remove();
      var addRow = catlist.querySelector('.lt-add[data-pf-add="' + id + '"]');
      if (addRow) addRow.remove();
    });
  });
}

/* ------------------------------------------------------------------
   CSS (injected once).
   ------------------------------------------------------------------ */
(function _lsInjectCSS() {
  if (document.getElementById("ls-rail-style")) return;
  var style = document.createElement("style");
  style.id = "ls-rail-style";
  /* INV-2026-07-04-001 slice 3/3: geometry aligned to the spike's P2 preset
     tokens (lite/sandbox/invent-lite-layer-menu-ui-fix.html applyPreset('P2')):
     --p-rail-pad:6px, --p-railbtn-pad:'3px 7px', --p-input-pad:5px,
     --p-font-sm:12px — read verbatim, not re-guessed. Colors are NOT part of
     the P2 decision, so var(--line)/var(--ink)/var(--muted) (lite's existing
     dark palette, already aligned with the spike's own P2/P3 hex values in
     design-tokens.css) are kept as-is. */
  style.textContent =
    ".ls-rail{display:flex;flex-direction:column;gap:4px;padding:6px;" +
      "border-bottom:1px solid var(--line,#2a3140);font-size:12px;}" +
    ".ls-rail-controls{display:flex;align-items:center;gap:4px;}" +
    ".ls-rail-btn{padding:3px 7px;font-size:12px;cursor:pointer;background:#222a37;" +
      "border:1px solid var(--line,#2a3140);color:var(--ink,#e6e6e6);border-radius:4px;}" +
    ".ls-rail-btn:disabled{opacity:.4;cursor:default;}" +
    ".ls-rail-select{flex:1;min-width:0;font-size:12px;background:#0c0f14;" +
      "color:var(--ink,#e6e6e6);border:1px solid var(--line,#2a3140);border-radius:4px;padding:4px;}" +
    ".ls-rail-counter{color:var(--muted,#8b97a8);font-size:11px;white-space:nowrap;}" +
    ".ls-rail-dash{color:var(--muted,#8b97a8);font-size:12px;padding:3px 7px;}" +
    ".ls-search-wrap{position:relative;}" +
    ".ls-search-input{width:100%;box-sizing:border-box;font-size:12px;padding:5px;" +
      "background:#0c0f14;color:var(--ink,#e6e6e6);border:1px solid var(--line,#2a3140);border-radius:4px;}" +
    ".ls-search-results{position:absolute;left:0;right:0;top:100%;z-index:20;max-height:260px;" +
      "overflow-y:auto;background:#161b22;border:1px solid var(--line,#2a3140);border-radius:4px;" +
      "box-shadow:0 4px 10px rgba(0,0,0,.4);margin-top:2px;}" +
    ".ls-search-group-header{padding:3px 8px;font-size:11px;color:var(--muted,#8b97a8);" +
      "text-transform:uppercase;background:#10141b;}" +
    ".ls-search-result{padding:6px 8px;font-size:12px;cursor:pointer;color:var(--ink,#e6e6e6);}" +
    ".ls-search-result:hover{background:#222a37;}" +
    ".ls-search-badge{padding:4px 8px;font-size:11px;color:var(--muted,#8b97a8);" +
      "font-style:italic;border-top:1px dashed var(--line,#2a3140);}" +
    ".ls-search-hl{outline:2px solid #4aa3ff;outline-offset:-1px;background:rgba(74,163,255,.15);}";
  document.head.appendChild(style);
}());

/* ------------------------------------------------------------------
   Bootstrap — wrap the GLOBAL buildPicker on DOMContentLoaded.
   Registered AFTER page-folder-layers.js's own DOMContentLoaded
   listener (script order — see header note), so this wraps the
   version that actually calls buildPagePicker() in PF mode, not a
   discarded intermediate. Post-processing (not a re-render) keeps this
   correct regardless of which underlying function built the DOM.
   ------------------------------------------------------------------ */
window.addEventListener("DOMContentLoaded", function() {
  if (typeof buildPicker === "function" && !buildPicker.__lsWrapped) {
    var _lsOrigBuildPicker = buildPicker;
    var _lsWrapped = function() {
      _lsOrigBuildPicker.apply(this, arguments);
      _lsPostRender();
      _lsApplyPendingHighlight();
    };
    _lsWrapped.__lsWrapped = true;
    buildPicker = _lsWrapped;
  }
});
