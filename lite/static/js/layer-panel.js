/* ============================================================
   LITE-LAYER-PANEL — custom-layer CRUD UI (L2c-3 sprint)
   Plain-globals module. No IIFE, no export, no bundler.
   Loaded after layer-system.js, before the inline script.

   Exports: buildPicker()
   All CRUD calls delegate to layer-system.js:
     addLayer, renameLayer, recolorLayer, removeLayer,
     reorderLayers, isDefaultLayer, layerById, layersInOrder
   State reads/writes: state.activeCat, state.catVis,
     state.catLock, state.dirty
   Calls: draw() — provided by inline script (hoisted global)
   ============================================================ */

/* ------------------------------------------------------------------
   _lpCommitRename(id, value)
   Called on Enter/blur of the inline rename input.
   Empty value = revert (no change). Non-empty = renameLayer + dirty.
   ------------------------------------------------------------------ */
function _lpCommitRename(id, value) {
  var v = (value || "").trim();
  if (v.length > 0) {
    renameLayer(id, v);
    state.dirty = true;
  }
  buildPicker();
  // draw() not strictly needed for name-only, but keeps HUD in sync
  draw();
}

/* ------------------------------------------------------------------
   NOTE: buildPicker() is defined in layer-tree.js (LST-3a) — that
   module replaces the flat picker with a pre-order tree render.
   This file retains only _lpCommitRename and lpHandleAddLayer.
   ------------------------------------------------------------------

/* ------------------------------------------------------------------
   lpHandleAddLayer()
   LFOC-1d: opens a role-picker modal. User picks which role/kind to add.
   Default name = roleDef.name + counter to keep unique. parentId carries
   from currently active layer's PF folder (preserves folder context).
   ------------------------------------------------------------------ */
function lpHandleAddLayer() {
  // Remove any existing picker (idempotent — re-click cancels prior)
  var existing = document.getElementById("lp-addlayer-picker");
  if (existing) { existing.remove(); return; }

  var roles;
  try { roles = ROLE_DEFS; } catch(e) { roles = null; }
  if (!roles || !roles.length) return;

  var ovl = document.createElement("div");
  ovl.id = "lp-addlayer-picker";
  ovl.style.cssText = "position:fixed;inset:0;background:rgba(6,8,12,.72);z-index:300;display:flex;align-items:center;justify-content:center";

  var box = document.createElement("div");
  box.style.cssText = "background:var(--panel,#161a22);border:1px solid var(--line,#2a3140);border-radius:10px;padding:14px 16px;min-width:280px;max-width:360px;box-shadow:0 10px 40px rgba(0,0,0,.6)";

  var h = document.createElement("div");
  h.style.cssText = "font-size:13px;font-weight:600;color:var(--ink,#e7ecf3);margin-bottom:10px";
  h.textContent = "เลือกชนิด layer ที่ต้องการเพิ่ม";
  box.appendChild(h);

  var list = document.createElement("div");
  list.style.cssText = "display:flex;flex-direction:column;gap:5px";

  for (var i = 0; i < roles.length; i++) {
    (function(rd) {
      var btn = document.createElement("button");
      btn.setAttribute("data-lp-role", rd.id);
      btn.style.cssText = "display:flex;align-items:center;gap:10px;padding:8px 10px;background:#1a1d24;border:1px solid var(--line,#2a3140);border-radius:6px;cursor:pointer;color:var(--ink,#e7ecf3);font-size:12px;text-align:left;width:100%";
      btn.onmouseover = function() { btn.style.background = "#22262e"; };
      btn.onmouseout  = function() { btn.style.background = "#1a1d24"; };
      btn.innerHTML =
        '<span style="display:inline-block;width:14px;height:14px;border-radius:3px;background:' + rd.color + ';flex:0 0 auto"></span>' +
        '<span style="flex:1"><b>' + rd.name + '</b><span style="display:block;color:var(--muted,#8b97a8);font-size:10px;font-family:ui-monospace,monospace">' + rd.id + (rd.counting ? " · counting" : "") + '</span></span>';
      btn.addEventListener("click", function() {
        ovl.remove();
        _lpDoAddLayer(rd.id);
      });
      list.appendChild(btn);
    })(roles[i]);
  }
  box.appendChild(list);

  var foot = document.createElement("div");
  foot.style.cssText = "margin-top:10px;text-align:right";
  var cancel = document.createElement("button");
  cancel.textContent = "ยกเลิก (Esc)";
  cancel.style.cssText = "background:#2d3036;color:var(--muted,#8b97a8);border:1px solid var(--line,#2a3140);padding:5px 12px;border-radius:5px;cursor:pointer;font-size:11px";
  cancel.addEventListener("click", function() { ovl.remove(); });
  foot.appendChild(cancel);
  box.appendChild(foot);

  ovl.appendChild(box);
  ovl.addEventListener("click", function(e) { if (e.target === ovl) ovl.remove(); });
  document.addEventListener("keydown", function escH(e) {
    if (e.key === "Escape") {
      var el = document.getElementById("lp-addlayer-picker");
      if (el) el.remove();
      document.removeEventListener("keydown", escH);
    }
  });
  document.body.appendChild(ovl);
}

/* ------------------------------------------------------------------
   _lpDoAddLayer(role)
   Internal: create the layer with chosen role. Carries parentId from
   the currently active layer if active is inside a PF folder (so the
   new layer appears in the same folder, not at root).
   ------------------------------------------------------------------ */
function _lpDoAddLayer(role) {
  var rd;
  try { rd = roleDef(role); } catch(e) { rd = null; }
  if (!rd) return;
  // Find a unique name: rd.name + counter, e.g. "พื้นที่อาคาร 2"
  var n = 1;
  for (var i = 0; i < LAYERS.length; i++) {
    if (LAYERS[i].role === role) n++;
  }
  var newLayer = addLayer(role, rd.name + " " + n, rd.color);
  if (!newLayer) return;
  // Carry parentId from currently active layer (puts new layer in same folder)
  var active = layerById(state.activeCat);
  if (active && active.parentId) {
    newLayer.parentId = active.parentId;
  } else if (typeof pageFolderIdFor === "function" && typeof curPage !== "undefined") {
    // LFOC-1f: fallback — in folder-only mode (LFOC-1b), a root-level layer is
    // contextually lost. Place new layer under the current page's PF folder if any.
    var _tag  = (typeof pageTags     !== "undefined") ? pageTags[curPage]     : null;
    var _fnum = (typeof pageFloorNum !== "undefined") ? pageFloorNum[curPage] : null;
    var _kind = (typeof pageFloorKind !== "undefined") ? pageFloorKind[curPage] : null;
    var pfId = pageFolderIdFor(curPage, _tag, _fnum, _kind);
    if (pfId && typeof folderById === "function" && folderById(pfId)) {
      newLayer.parentId = pfId;
    }
  }
  state.catVis[newLayer.id] = true;
  state.catLock[newLayer.id] = false;
  state.activeCat = newLayer.id;
  state.dirty = true;
  buildPicker();
  draw();
}

/* ------------------------------------------------------------------
   _lpFirstPageOfLayer(layerId)
   LFOC-1e: returns smallest pageN containing an object with catId===layerId.
   Returns null if PS empty or no object found.
   ------------------------------------------------------------------ */
function _lpFirstPageOfLayer(layerId) {
  if (typeof PS === "undefined" || !PS) return null;
  var keys = Object.keys(PS).map(Number).filter(function(k){return !isNaN(k);}).sort(function(a,b){return a-b;});
  for (var i = 0; i < keys.length; i++) {
    var pg = keys[i];
    var objs = (PS[pg] && PS[pg].objects) || [];
    for (var j = 0; j < objs.length; j++) {
      if (objs[j].catId === layerId) return pg;
    }
  }
  return null;
}
