/* ============================================================
   LITE-LAYER-TREE — tree-picker UI (LST-3a sprint)
   Plain-globals module. No IIFE, no export, no bundler.
   Loaded after layer-panel.js, before the inline script.

   Replaces the flat buildPicker() from layer-panel.js with a
   pre-order tree render that handles folder rows + layer rows,
   indent/outdent (→/←), collapse/expand, and folder CRUD.

   Depends on globals from:
     layer-system.js  — LAYERS, FOLDERS, childrenOf, folderById,
                        layerById, addFolder, removeFolder,
                        foldersInOrder, isDefaultLayer, removeLayer,
                        reorderLayers, renameLayer, recolorLayer,
                        ancestorsOf, effVisible, effLocked
     layer-panel.js   — _lpCommitRename
     inline script    — state, PS, draw()

   Runtime-only state (NOT persisted):
     state.folderCollapsed  — {[folderId]: bool}  (undefined = expanded)

   Visibility/lock predicates (globals used by ui-lite.html):
     _isHidden(id)  — true when state.catVis[id] === false
     _isLocked(id)  — true when state.catLock[id] === true
   ============================================================ */

/* ------------------------------------------------------------------
   Visibility / lock predicates (globals — used by ui-lite.html draw/pick).
   The === false / === true form treats undefined as visible/unlocked,
   so missing seeds never wrongly hide anything.
   ------------------------------------------------------------------ */
function _isHidden(id) {
  return state.catVis[id] === false;
}
function _isLocked(id) {
  return state.catLock[id] === true;
}

/* ------------------------------------------------------------------
   _ltCollapsed(folderId)
   Safe read with lazy init of folderCollapsed dict.
   ------------------------------------------------------------------ */
function _ltCollapsed(folderId) {
  if (!state.folderCollapsed) state.folderCollapsed = {};
  return !!state.folderCollapsed[folderId];
}

/* ------------------------------------------------------------------
   _ltMakeSwatch(id, getColor, setColor)
   Shared swatch (click → hidden <input type=color>) for folders + layers.
   ------------------------------------------------------------------ */
function _ltMakeSwatch(id, getColor, setColorFn) {
  var sw = document.createElement("span");
  sw.className = "sw lp-sw";
  sw.style.background = getColor();
  sw.setAttribute("data-recolor", id);
  sw.title = "เปลี่ยนสี";
  sw.addEventListener("click", function(e) {
    e.stopPropagation();
    var inp = document.createElement("input");
    inp.type = "color";
    inp.value = getColor();
    inp.style.display = "none";
    document.body.appendChild(inp);
    inp.addEventListener("change", function() {
      setColorFn(inp.value);
      state.dirty = true;
      if (inp.parentNode) document.body.removeChild(inp);
      buildPicker();
      draw();
    });
    inp.addEventListener("blur", function() {
      if (inp.parentNode) document.body.removeChild(inp);
    });
    inp.click();
  });
  return sw;
}

/* ------------------------------------------------------------------
   _ltSiblingsOf(nodeId, kind)
   Returns ordered siblings (same parentId, same kind or all kinds)
   used for ▲▼ reorder within tree level.
   kind: "folder" | "layer" | "any"
   Returns [{kind,node}] from childrenOf, filtered and sorted.
   ------------------------------------------------------------------ */
function _ltSiblingsOf(nodeId) {
  var node = layerById(nodeId) || folderById(nodeId);
  if (!node) return [];
  var parentId = (node.parentId !== undefined) ? node.parentId : null;
  return childrenOf(parentId); // already sorted
}

/* ------------------------------------------------------------------
   _ltSwapOrder(itemA, itemB)
   Swap .order between two nodes (layer or folder objects).
   ------------------------------------------------------------------ */
function _ltSwapOrder(nodeA, nodeB) {
  var tmp = nodeA.order;
  nodeA.order = nodeB.order;
  nodeB.order = tmp;
}

/* ------------------------------------------------------------------
   _ltPrecedingNode(nodeId)
   The item just before nodeId among its siblings.
   Returns {kind,node} or null.
   ------------------------------------------------------------------ */
function _ltPrecedingNode(nodeId) {
  var siblings = _ltSiblingsOf(nodeId);
  for (var i = 1; i < siblings.length; i++) {
    if (siblings[i].node.id === nodeId) return siblings[i - 1];
  }
  return null;
}

/* ------------------------------------------------------------------
   _ltRenderFolder(folderId, depth, el)
   Render one folder row + recurse into children if not collapsed.
   ------------------------------------------------------------------ */
function _ltRenderFolder(folder, depth, el) {
  if (!state.folderCollapsed) state.folderCollapsed = {};
  var collapsed = !!state.folderCollapsed[folder.id];
  var vis = !_isHidden(folder.id); // own only for the eye icon
  var lk  = _isLocked(folder.id);

  var d = document.createElement("div");
  d.className = "cat lt-folder-row";
  d.setAttribute("data-catid", folder.id);
  d.setAttribute("data-nodekind", "folder");
  d.style.marginLeft = (depth * 16) + "px";

  /* --- collapse toggle --- */
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

  /* --- folder icon --- */
  var icon = document.createElement("span");
  icon.textContent = "📁";
  icon.style.fontSize = "12px";
  icon.style.marginRight = "2px";

  /* --- swatch --- */
  var sw = _ltMakeSwatch(
    folder.id,
    function() { return folder.color; },
    function(v) { folder.color = v; }
  );

  /* --- name (click = inline rename) --- */
  var nm = document.createElement("span");
  nm.className = "nm";
  nm.textContent = folder.name;
  nm.title = "คลิกเพื่อเปลี่ยนชื่อ";
  nm.addEventListener("click", function(e) {
    e.stopPropagation();
    var inp = document.createElement("input");
    inp.className = "lp-rename-inp";
    inp.value = folder.name;
    nm.replaceWith(inp);
    inp.focus();
    inp.select();
    var committed = false;
    function commit() {
      if (committed) return;
      committed = true;
      var v = (inp.value || "").trim();
      if (v.length > 0) {
        folder.name = v;
        state.dirty = true;
      }
      buildPicker();
      draw();
    }
    inp.addEventListener("keydown", function(ev) {
      if (ev.key === "Enter") { ev.preventDefault(); commit(); }
      if (ev.key === "Escape") { committed = true; buildPicker(); }
      ev.stopPropagation();
    });
    inp.addEventListener("blur", commit);
  });

  /* --- eye --- */
  var eye = document.createElement("span");
  eye.className = "eye" + (vis ? "" : " off");
  eye.setAttribute("data-eye", folder.id);
  eye.textContent = vis ? "👁" : "🚫";

  /* --- lock --- */
  var lkBtn = document.createElement("span");
  lkBtn.className = "eye" + (lk ? " off" : "");
  lkBtn.setAttribute("data-lock", folder.id);
  lkBtn.textContent = lk ? "🔒" : "🔓";

  /* --- ▲▼ reorder among siblings --- */
  var siblings = _ltSiblingsOf(folder.id);
  var sibIdx = -1;
  for (var i = 0; i < siblings.length; i++) {
    if (siblings[i].node.id === folder.id) { sibIdx = i; break; }
  }

  var btnUp = document.createElement("button");
  btnUp.className = "lp-ord-btn";
  btnUp.textContent = "▲";
  btnUp.title = "เลื่อนขึ้น";
  btnUp.disabled = (sibIdx <= 0);
  btnUp.setAttribute("data-reorder-up", folder.id);
  btnUp.addEventListener("click", function(e) {
    e.stopPropagation();
    var sibs = _ltSiblingsOf(folder.id);
    var idx2 = -1;
    for (var j = 0; j < sibs.length; j++) if (sibs[j].node.id === folder.id) { idx2 = j; break; }
    if (idx2 <= 0) return;
    _ltSwapOrder(sibs[idx2].node, sibs[idx2 - 1].node);
    state.dirty = true;
    buildPicker();
    draw();
  });

  var btnDn = document.createElement("button");
  btnDn.className = "lp-ord-btn";
  btnDn.textContent = "▼";
  btnDn.title = "เลื่อนลง";
  btnDn.disabled = (sibIdx < 0 || sibIdx >= siblings.length - 1);
  btnDn.setAttribute("data-reorder-dn", folder.id);
  btnDn.addEventListener("click", function(e) {
    e.stopPropagation();
    var sibs = _ltSiblingsOf(folder.id);
    var idx2 = -1;
    for (var j = 0; j < sibs.length; j++) if (sibs[j].node.id === folder.id) { idx2 = j; break; }
    if (idx2 < 0 || idx2 >= sibs.length - 1) return;
    _ltSwapOrder(sibs[idx2].node, sibs[idx2 + 1].node);
    state.dirty = true;
    buildPicker();
    draw();
  });

  /* --- → indent (nest under preceding sibling) --- */
  var btnIn = document.createElement("button");
  btnIn.className = "lp-ord-btn";
  btnIn.textContent = "→";
  btnIn.title = "ซ้อนใต้รายการก่อนหน้า";
  var preceding = _ltPrecedingNode(folder.id);
  btnIn.disabled = !preceding;
  btnIn.setAttribute("data-indent", folder.id);
  btnIn.addEventListener("click", function(e) {
    e.stopPropagation();
    var pre = _ltPrecedingNode(folder.id);
    if (!pre) return;
    folder.parentId = pre.node.id;
    state.dirty = true;
    buildPicker();
    draw();
  });

  /* --- ← outdent (move up one level) --- */
  var btnOut = document.createElement("button");
  btnOut.className = "lp-ord-btn";
  btnOut.textContent = "←";
  btnOut.title = "ย้ายออกจากกลุ่ม";
  var folderParentId = (folder.parentId !== undefined) ? folder.parentId : null;
  btnOut.disabled = (folderParentId === null);
  btnOut.setAttribute("data-outdent", folder.id);
  btnOut.addEventListener("click", function(e) {
    e.stopPropagation();
    var grandParentId = null;
    var currentParentId = (folder.parentId !== undefined) ? folder.parentId : null;
    if (currentParentId !== null) {
      var parentNode = layerById(currentParentId) || folderById(currentParentId);
      grandParentId = parentNode ? ((parentNode.parentId !== undefined) ? parentNode.parentId : null) : null;
    }
    folder.parentId = grandParentId;
    state.dirty = true;
    buildPicker();
    draw();
  });

  /* --- ✕ delete folder --- */
  var btnDel = document.createElement("button");
  btnDel.className = "lp-del-btn";
  btnDel.textContent = "✕";
  btnDel.title = "ลบกลุ่มนี้ (รายการย่อยจะถูกย้ายออก)";
  btnDel.setAttribute("data-folder-del", folder.id);
  btnDel.addEventListener("click", function(e) {
    e.stopPropagation();
    if (!confirm("ลบกลุ่ม \"" + folder.name + "\"?\nรายการย่อยจะถูกย้ายออกจากกลุ่ม")) return;
    var savedId = folder.id;
    var r = removeFolder(savedId);
    if (!r.removed) return;
    delete state.catVis[savedId];
    delete state.catLock[savedId];
    if (state.folderCollapsed) delete state.folderCollapsed[savedId];
    state.dirty = true;
    buildPicker();
    draw();
  });

  /* --- row click events (eye/lock) --- */
  d.addEventListener("click", function(e) {
    if (e.target.dataset.eye) {
      // toggle: if currently hidden (catVis===false) → make visible (true); else → hide (false)
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
  d.appendChild(eye);
  d.appendChild(lkBtn);
  d.appendChild(btnUp);
  d.appendChild(btnDn);
  d.appendChild(btnIn);
  d.appendChild(btnOut);
  d.appendChild(btnDel);
  el.appendChild(d);

  /* --- recurse into children unless collapsed --- */
  if (!collapsed) {
    var kids = childrenOf(folder.id);
    for (var ki = 0; ki < kids.length; ki++) {
      var kid = kids[ki];
      if (kid.kind === "folder") {
        _ltRenderFolder(kid.node, depth + 1, el);
      } else {
        _ltRenderLayer(kid.node, depth + 1, el);
      }
    }
  }
}

/* ------------------------------------------------------------------
   _ltRenderLayer(layer, depth, el)
   Render one layer row (same controls as flat panel + indent/outdent).
   ------------------------------------------------------------------ */
function _ltRenderLayer(layer, depth, el) {
  var vis = !_isHidden(layer.id);
  var lk  = _isLocked(layer.id);

  var d = document.createElement("div");
  d.className = "cat lt-layer-row" + (state.activeCat === layer.id ? " active" : "");
  d.setAttribute("data-catid", layer.id);
  d.setAttribute("data-nodekind", "layer");
  d.style.marginLeft = (depth * 16) + "px";

  /* --- collapse toggle for layers that have sub-layers/folders --- */
  var kids = childrenOf(layer.id);
  if (kids.length > 0) {
    if (!state.folderCollapsed) state.folderCollapsed = {};
    var layerCollapsed = !!state.folderCollapsed[layer.id];
    var ltog = document.createElement("span");
    ltog.className = "lt-collapse-toggle";
    ltog.textContent = layerCollapsed ? "▸" : "▾";
    ltog.title = layerCollapsed ? "ขยาย" : "ย่อ";
    ltog.style.cursor = "pointer";
    ltog.style.fontSize = "11px";
    ltog.style.marginRight = "2px";
    ltog.style.color = "var(--muted)";
    ltog.addEventListener("click", function(e) {
      e.stopPropagation();
      if (!state.folderCollapsed) state.folderCollapsed = {};
      state.folderCollapsed[layer.id] = !state.folderCollapsed[layer.id];
      buildPicker();
    });
    d.appendChild(ltog);
  } else {
    /* spacer to keep alignment */
    var sp = document.createElement("span");
    sp.style.display = "inline-block";
    sp.style.width = "13px";
    d.appendChild(sp);
  }

  /* --- swatch --- */
  var sw = _ltMakeSwatch(
    layer.id,
    function() { return layer.color; },
    function(v) { recolorLayer(layer.id, v); }
  );

  /* --- name span / inline rename --- */
  var nm = document.createElement("span");
  nm.className = "nm";
  nm.textContent = layer.name;
  nm.title = "คลิกเพื่อเปลี่ยนชื่อ";
  nm.addEventListener("click", function(e) {
    e.stopPropagation();
    var inp = document.createElement("input");
    inp.className = "lp-rename-inp";
    inp.value = layer.name;
    nm.replaceWith(inp);
    inp.focus();
    inp.select();
    var committed = false;
    function commit() {
      if (committed) return;
      committed = true;
      _lpCommitRename(layer.id, inp.value);
    }
    inp.addEventListener("keydown", function(ev) {
      if (ev.key === "Enter") { ev.preventDefault(); commit(); }
      if (ev.key === "Escape") { committed = true; buildPicker(); }
      ev.stopPropagation();
    });
    inp.addEventListener("blur", commit);
  });

  /* --- eye --- */
  var eye = document.createElement("span");
  eye.className = "eye" + (vis ? "" : " off");
  eye.setAttribute("data-eye", layer.id);
  eye.textContent = vis ? "👁" : "🚫";

  /* --- lock --- */
  var lkBtn = document.createElement("span");
  lkBtn.className = "eye" + (lk ? " off" : "");
  lkBtn.setAttribute("data-lock", layer.id);
  lkBtn.textContent = lk ? "🔒" : "🔓";

  /* --- ▲▼ reorder among siblings --- */
  var siblings = _ltSiblingsOf(layer.id);
  var sibIdx = -1;
  for (var i = 0; i < siblings.length; i++) {
    if (siblings[i].node.id === layer.id) { sibIdx = i; break; }
  }

  var btnUp = document.createElement("button");
  btnUp.className = "lp-ord-btn";
  btnUp.textContent = "▲";
  btnUp.title = "เลื่อนขึ้น";
  btnUp.disabled = (sibIdx <= 0);
  btnUp.setAttribute("data-reorder-up", layer.id);
  btnUp.addEventListener("click", function(e) {
    e.stopPropagation();
    var sibs = _ltSiblingsOf(layer.id);
    var idx2 = -1;
    for (var j = 0; j < sibs.length; j++) if (sibs[j].node.id === layer.id) { idx2 = j; break; }
    if (idx2 <= 0) return;
    _ltSwapOrder(sibs[idx2].node, sibs[idx2 - 1].node);
    state.dirty = true;
    buildPicker();
    draw();
  });

  var btnDn = document.createElement("button");
  btnDn.className = "lp-ord-btn";
  btnDn.textContent = "▼";
  btnDn.title = "เลื่อนลง";
  btnDn.disabled = (sibIdx < 0 || sibIdx >= siblings.length - 1);
  btnDn.setAttribute("data-reorder-dn", layer.id);
  btnDn.addEventListener("click", function(e) {
    e.stopPropagation();
    var sibs = _ltSiblingsOf(layer.id);
    var idx2 = -1;
    for (var j = 0; j < sibs.length; j++) if (sibs[j].node.id === layer.id) { idx2 = j; break; }
    if (idx2 < 0 || idx2 >= sibs.length - 1) return;
    _ltSwapOrder(sibs[idx2].node, sibs[idx2 + 1].node);
    state.dirty = true;
    buildPicker();
    draw();
  });

  /* --- → indent (nest under preceding sibling) --- */
  var btnIn = document.createElement("button");
  btnIn.className = "lp-ord-btn";
  btnIn.textContent = "→";
  btnIn.title = "ซ้อนใต้รายการก่อนหน้า";
  var preceding = _ltPrecedingNode(layer.id);
  btnIn.disabled = !preceding;
  btnIn.setAttribute("data-indent", layer.id);
  btnIn.addEventListener("click", function(e) {
    e.stopPropagation();
    var pre = _ltPrecedingNode(layer.id);
    if (!pre) return;
    layer.parentId = pre.node.id;
    state.dirty = true;
    buildPicker();
    draw();
  });

  /* --- ← outdent (move up one level) --- */
  var btnOut = document.createElement("button");
  btnOut.className = "lp-ord-btn";
  btnOut.textContent = "←";
  btnOut.title = "ย้ายออกจากกลุ่ม";
  var layerParentId = (layer.parentId !== undefined) ? layer.parentId : null;
  btnOut.disabled = (layerParentId === null);
  btnOut.setAttribute("data-outdent", layer.id);
  btnOut.addEventListener("click", function(e) {
    e.stopPropagation();
    var currentParentId = (layer.parentId !== undefined) ? layer.parentId : null;
    var grandParentId = null;
    if (currentParentId !== null) {
      var parentNode = layerById(currentParentId) || folderById(currentParentId);
      grandParentId = parentNode ? ((parentNode.parentId !== undefined) ? parentNode.parentId : null) : null;
    }
    layer.parentId = grandParentId;
    state.dirty = true;
    buildPicker();
    draw();
  });

  /* --- ✕ delete (custom layers only) --- */
  var btnDel = null;
  if (!isDefaultLayer(layer.id)) {
    btnDel = document.createElement("button");
    btnDel.className = "lp-del-btn";
    btnDel.textContent = "✕";
    btnDel.title = "ลบ layer นี้";
    btnDel.setAttribute("data-layer-del", layer.id);
    btnDel.addEventListener("click", function(e) {
      e.stopPropagation();
      if (!confirm("ลบ layer \"" + layer.name + "\"?\nวัตถุทั้งหมดจะถูกย้ายไป layer หลัก")) return;
      var r = removeLayer(layer.id);
      if (!r.removed) return;
      // reparent this layer's sub-layers/sub-folders up to its parent — removeLayer
      // does not touch children, so without this they orphan (vanish from the tree
      // until the load-time integrity pass runs). Mirror removeFolder's reparent-up.
      var delParentId = (layer.parentId !== undefined) ? layer.parentId : null;
      LAYERS.forEach(function(x){ if (x.parentId === layer.id) x.parentId = delParentId; });
      FOLDERS.forEach(function(x){ if (x.parentId === layer.id) x.parentId = delParentId; });
      // reassign ALL objects across ALL pages
      Object.keys(PS).forEach(function(k) {
        (PS[k].objects || []).forEach(function(o) {
          if (o.catId === layer.id) o.catId = r.reassignTo;
        });
      });
      if (state.activeCat === layer.id) state.activeCat = r.reassignTo;
      delete state.catVis[layer.id];
      delete state.catLock[layer.id];
      if (state.folderCollapsed) delete state.folderCollapsed[layer.id];
      state.dirty = true;
      buildPicker();
      draw();
    });
  }

  /* --- row click (not on controls) → set activeCat --- */
  d.addEventListener("click", function(e) {
    if (e.target.dataset.eye) {
      state.catVis[layer.id] = (state.catVis[layer.id] === false) ? true : false;
      buildPicker(); draw(); return;
    }
    if (e.target.dataset.lock) {
      state.catLock[layer.id] = !state.catLock[layer.id];
      buildPicker(); draw(); return;
    }
    if (e.target.classList.contains("lp-ord-btn")) return;
    if (e.target.classList.contains("lp-del-btn")) return;
    if (e.target.classList.contains("lp-sw")) return;
    if (e.target.classList.contains("nm")) return;
    if (e.target.classList.contains("lt-collapse-toggle")) return;
    state.activeCat = layer.id;
    state.tool = layer.counting ? "count" : (state.tool === "count" ? "poly" : state.tool);
    buildPicker(); draw();
  });

  d.appendChild(sw);
  d.appendChild(nm);
  d.appendChild(eye);
  d.appendChild(lkBtn);
  d.appendChild(btnUp);
  d.appendChild(btnDn);
  d.appendChild(btnIn);
  d.appendChild(btnOut);
  if (btnDel) d.appendChild(btnDel);
  el.appendChild(d);

  /* --- recurse into sub-layers/sub-folders if not collapsed --- */
  if (!state.folderCollapsed) state.folderCollapsed = {};
  if (!state.folderCollapsed[layer.id] && kids.length > 0) {
    for (var ki = 0; ki < kids.length; ki++) {
      var kid = kids[ki];
      if (kid.kind === "folder") {
        _ltRenderFolder(kid.node, depth + 1, el);
      } else {
        _ltRenderLayer(kid.node, depth + 1, el);
      }
    }
  }
}

/* ------------------------------------------------------------------
   buildPicker()
   Pre-order walk of the tree: childrenOf(null) → recurse.
   Replaces the flat buildPicker() in layer-panel.js.
   ------------------------------------------------------------------ */
function buildPicker() {
  var el = document.getElementById("catlist");
  el.innerHTML = "";

  if (!state.folderCollapsed) state.folderCollapsed = {};

  var roots = childrenOf(null);
  for (var i = 0; i < roots.length; i++) {
    var item = roots[i];
    if (item.kind === "folder") {
      _ltRenderFolder(item.node, 0, el);
    } else {
      _ltRenderLayer(item.node, 0, el);
    }
  }
}
