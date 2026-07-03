/* ============================================================
   LITE-LAYER-DND — drag-and-drop reorder for the layer tree (LDND-S1..S3)
   Plain-globals module. No IIFE, no export, no bundler.
   Loaded AFTER layer-tree.js (depends on buildPicker global).

   Wraps buildPicker() to post-process rows after each render.
   Uses pointer events (not HTML5 DnD) for touch + mouse parity.

   Algorithm ported from lite/sandbox/invent-layer-dnd.html (Approach A+D).
   Real model API (layer-system.js globals):
     LAYERS, FOLDERS, childrenOf(pid), layerById(id), folderById(id),
     ancestorsOf(id), addFolder

   Only mutates .order and .parentId on LAYERS/FOLDERS nodes.
   Does NOT touch: measure-engine.js, RS, pdfToC/cToPdf, area math,
   semanticTag. No .bmaplan schema change (both fields already persisted).

   Public globals (used internally only):
     ltDndDecorate()  — called automatically after every buildPicker()

   LDND-S3: auto-group on collision (Approach D).
     _ltAutoGroup — module-level flag (default OFF).
     When ON, dragging a root layer onto the middle 40% of another root layer
     auto-creates a folder wrapping both.
   ============================================================ */

/* ------------------------------------------------------------------
   0. Auto-group setting (LDND-S3)
   ------------------------------------------------------------------ */
var _ltAutoGroup = (function() {
  try { return localStorage.getItem("bmaPlan.lite.autoGroup.v1") === "1"; }
  catch(e) { return false; }
}());

/* ------------------------------------------------------------------
   1. Inject CSS (style block appended once to <head>)
   ------------------------------------------------------------------ */
(function _ltDndInjectStyles() {
  if (document.getElementById("lt-dnd-style")) return; // idempotent
  var s = document.createElement("style");
  s.id = "lt-dnd-style";
  s.textContent = [
    ".lt-grip{display:inline-flex;align-items:center;justify-content:center;",
    "  width:14px;height:100%;cursor:grab;touch-action:none;color:var(--muted,#888);",
    "  font-size:13px;flex-shrink:0;opacity:.6;margin-right:2px;user-select:none;}",
    ".lt-grip:hover{opacity:1;}",
    ".lt-grip:active{cursor:grabbing;}",
    ".lt-drop-into{box-shadow:inset 0 0 0 2px #4aa3ff !important;",
    "  background:rgba(74,163,255,.10) !important;}",
    ".lt-drop-group{box-shadow:inset 0 0 0 2px #3cb371,inset 0 0 0 4px rgba(60,179,113,.35) !important;",
    "  background:rgba(60,179,113,.12) !important;}",
    "#lt-dnd-ghost{position:fixed;z-index:9999;pointer-events:none;display:none;",
    "  background:#3a4150;border:1px solid #4aa3ff;border-radius:5px;",
    "  padding:3px 10px;font-size:12px;box-shadow:0 4px 14px rgba(0,0,0,.6);",
    "  max-width:260px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;",
    "  color:var(--txt,#e6e8ec);}",
    "#lt-dnd-line{position:absolute;left:4px;right:4px;height:2px;",
    "  background:#4aa3ff;border-radius:2px;display:none;pointer-events:none;",
    "  box-shadow:0 0 5px #4aa3ff;z-index:100;}",
    "#lt-dnd-line::before{content:'';position:absolute;left:-4px;top:-3px;",
    "  width:8px;height:8px;border-radius:50%;background:#4aa3ff;}",
    "#lt-autogroup-bar{display:flex;align-items:center;gap:5px;padding:3px 6px 3px 8px;",
    "  font-size:11px;color:var(--muted,#8b909a);border-bottom:1px solid rgba(255,255,255,.06);}",
    "#lt-autogroup-bar label{display:flex;align-items:center;gap:4px;cursor:pointer;}"
  ].join("\n");
  document.head.appendChild(s);
}());

/* ------------------------------------------------------------------
   2. Create ghost + drop-line elements (once)
   ------------------------------------------------------------------ */
var _ltDndGhost = (function() {
  var g = document.createElement("div");
  g.id = "lt-dnd-ghost";
  document.body.appendChild(g);
  return g;
}());

/* Drop-line is appended into #catlist each time ltDndDecorate() runs
   so it survives innerHTML="" clears. _ltDndLine is a live reference
   refreshed by ltDndDecorate. */
var _ltDndLine = null;

/* ------------------------------------------------------------------
   3. Wrap buildPicker — must run AFTER layer-tree.js defines it
   ------------------------------------------------------------------ */
(function _ltDndWrap() {
  var _origBP = buildPicker;
  buildPicker = function() {
    _origBP.apply(this, arguments);
    ltDndDecorate();
  };
}());

/* ------------------------------------------------------------------
   3b. Inject auto-group toggle bar ABOVE #catlist (once, idempotent)
   ------------------------------------------------------------------ */
function _ltAutoGroupInjectBar() {
  if (document.getElementById("lt-autogroup-bar")) return; // idempotent
  var container = document.getElementById("catlist");
  if (!container || !container.parentNode) return;
  var bar = document.createElement("div");
  bar.id = "lt-autogroup-bar";
  var lbl = document.createElement("label");
  var cb  = document.createElement("input");
  cb.type = "checkbox";
  cb.id   = "lt-autogroup-cb";
  cb.checked = _ltAutoGroup;
  cb.addEventListener("change", function() {
    _ltAutoGroup = cb.checked;
    try { localStorage.setItem("bmaPlan.lite.autoGroup.v1", _ltAutoGroup ? "1" : "0"); }
    catch(e) {}
  });
  lbl.appendChild(cb);
  lbl.appendChild(document.createTextNode(" จับกลุ่มเมื่อชนกัน"));
  bar.appendChild(lbl);
  container.parentNode.insertBefore(bar, container);
}

/* ------------------------------------------------------------------
   4. ltDndDecorate() — post-processes rows freshly rendered by buildPicker
   ------------------------------------------------------------------ */
function ltDndDecorate() {
  /* Inject auto-group toggle bar above #catlist (once) */
  _ltAutoGroupInjectBar();

  /* Refresh / create drop-line inside #catlist (survives innerHTML reset) */
  var container = document.getElementById("catlist");
  if (!container) return;

  var oldLine = document.getElementById("lt-dnd-line");
  if (oldLine && oldLine.parentNode) oldLine.parentNode.removeChild(oldLine);
  _ltDndLine = document.createElement("div");
  _ltDndLine.id = "lt-dnd-line";
  container.appendChild(_ltDndLine);

  /* Prepend grip + make focusable on every .cat row */
  var rows = container.querySelectorAll(".cat");
  for (var i = 0; i < rows.length; i++) {
    var row = rows[i];
    /* Make row keyboard-focusable */
    row.tabIndex = 0;

    /* Skip if already decorated (shouldn't happen after innerHTML="", but guard anyway) */
    if (row.querySelector(".lt-grip")) continue;

    var grip = document.createElement("span");
    grip.className = "lt-grip";
    grip.textContent = "⠇"; /* ⠿ braille pattern dots-1234567 */
    grip.title = "ลากเพื่อย้าย/จัดกลุ่ม"; /* ลากเพื่อย้าย/จัดกลุ่ม */
    /* Bind drag start — capture nodeId + kind from row */
    (function(r, g) {
      g.addEventListener("pointerdown", function(e) {
        var nodeId = r.getAttribute("data-catid");
        var nodeKind = r.getAttribute("data-nodekind");
        if (!nodeId) return;
        _ltDndStartDrag(e, nodeId, nodeKind, r);
      });
    }(row, grip));

    /* Prepend grip as first child */
    row.insertBefore(grip, row.firstChild);
  }

  /* Install delegated keydown handler (once per container) */
  if (!container._ltKbdBound) {
    container._ltKbdBound = true;
    container.addEventListener("keydown", _ltDndKeyDown);
  }
}

/* ------------------------------------------------------------------
   4b. _ltDndKeyDown — keyboard reorder/indent/outdent on focused rows
   Keys: Shift+ArrowUp/Down = reorder; ArrowRight = indent; ArrowLeft = outdent
   ------------------------------------------------------------------ */
function _ltDndKeyDown(e) {
  var active = document.activeElement;
  if (!active || !active.classList.contains("cat")) return;
  /* Don't hijack inline rename inputs */
  if (active.tagName === "INPUT" || active.tagName === "TEXTAREA") return;
  /* Check if the focused element contains an active input */
  var inp = active.querySelector("input, textarea");
  if (inp && document.activeElement === inp) return;

  var handled = false;
  var nodeId = active.getAttribute("data-catid");
  if (!nodeId) return;

  var node = layerById(nodeId) || folderById(nodeId);
  if (!node) return;

  if (e.shiftKey && e.key === "ArrowUp") {
    /* Reorder up among siblings */
    var sibs = _ltSiblingsOf(nodeId);
    var idx = -1;
    for (var i = 0; i < sibs.length; i++) {
      if (sibs[i].node.id === nodeId) { idx = i; break; }
    }
    if (idx > 0) {
      if (typeof pushUndo === "function") pushUndo(); // undo covers LAYERS/FOLDERS: capture BEFORE reorder
      _ltSwapOrder(sibs[idx].node, sibs[idx - 1].node);
      state.dirty = true;
      handled = true;
    }
  } else if (e.shiftKey && e.key === "ArrowDown") {
    /* Reorder down among siblings */
    var sibs2 = _ltSiblingsOf(nodeId);
    var idx2 = -1;
    for (var j = 0; j < sibs2.length; j++) {
      if (sibs2[j].node.id === nodeId) { idx2 = j; break; }
    }
    if (idx2 >= 0 && idx2 < sibs2.length - 1) {
      if (typeof pushUndo === "function") pushUndo(); // undo covers LAYERS/FOLDERS: capture BEFORE reorder
      _ltSwapOrder(sibs2[idx2].node, sibs2[idx2 + 1].node);
      state.dirty = true;
      handled = true;
    }
  } else if (!e.shiftKey && e.key === "ArrowRight") {
    /* Indent: nest under immediately preceding sibling */
    var pre = _ltPrecedingNode(nodeId);
    if (pre) {
      if (typeof pushUndo === "function") pushUndo(); // undo covers LAYERS/FOLDERS: capture BEFORE reparent (indent)
      var oldParent = (node.parentId !== undefined) ? node.parentId : null;
      node.parentId = pre.node.id;
      _ltDndReindex(oldParent);
      var nestKids = childrenOf(pre.node.id);
      node.order = nestKids.length - 1;
      _ltDndReindex(pre.node.id);
      state.dirty = true;
      handled = true;
    }
  } else if (!e.shiftKey && e.key === "ArrowLeft") {
    /* Outdent: move up to grandparent */
    var currentParentId = (node.parentId !== undefined) ? node.parentId : null;
    if (currentParentId !== null) {
      if (typeof pushUndo === "function") pushUndo(); // undo covers LAYERS/FOLDERS: capture BEFORE reparent (outdent)
      var parentNode = layerById(currentParentId) || folderById(currentParentId);
      var grandParentId = parentNode ? ((parentNode.parentId !== undefined) ? parentNode.parentId : null) : null;
      var oldParent2 = currentParentId;
      node.parentId = grandParentId;
      _ltDndReindex(oldParent2);
      var gpKids = childrenOf(grandParentId);
      node.order = gpKids.length - 1;
      _ltDndReindex(grandParentId);
      state.dirty = true;
      handled = true;
    }
  }

  if (handled) {
    e.preventDefault();
    e.stopPropagation();
    buildPicker();
    draw();
    /* Restore focus to the same node after rebuild */
    var container = document.getElementById("catlist");
    if (container) {
      var target = container.querySelector("[data-catid='" + nodeId + "']");
      if (target) target.focus();
    }
  }
}

/* ------------------------------------------------------------------
   5. Drag state
   ------------------------------------------------------------------ */
var _ltDrag = null; /* {id, kind, name, startX, startY, moved, target} */

/* ------------------------------------------------------------------
   6. Descendants helper (cycle-guarded breadth-first)
   ------------------------------------------------------------------ */
function _ltDndDescendants(id) {
  var out = [];
  var queue = childrenOf(id).map(function(c) { return c.node.id; });
  var visited = {};
  while (queue.length) {
    var cur = queue.shift();
    if (visited[cur]) continue;
    visited[cur] = true;
    out.push(cur);
    var kids = childrenOf(cur);
    for (var i = 0; i < kids.length; i++) queue.push(kids[i].node.id);
  }
  return out;
}

/* ------------------------------------------------------------------
   7. _ltDndStartDrag(e, nodeId, nodeKind, rowEl)
   ------------------------------------------------------------------ */
function _ltDndStartDrag(e, nodeId, nodeKind, rowEl) {
  e.preventDefault();
  e.stopPropagation();

  var node = (nodeKind === "folder") ? folderById(nodeId) : layerById(nodeId);
  if (!node) return;

  _ltDrag = {
    id: nodeId,
    kind: nodeKind,
    name: node.name,
    startX: e.clientX,
    startY: e.clientY,
    moved: false,
    target: null,
    sourceRow: rowEl
  };

  _ltDndGhost.textContent = "⠇ " + node.name;

  rowEl.setPointerCapture(e.pointerId);
  window.addEventListener("pointermove", _ltDndOnMove);
  window.addEventListener("pointerup", _ltDndOnUp, { once: true });
  window.addEventListener("pointercancel", _ltDndOnUp, { once: true });
}

/* ------------------------------------------------------------------
   8. _ltDndOnMove(e)
   ------------------------------------------------------------------ */
function _ltDndOnMove(e) {
  if (!_ltDrag) return;

  var dx = e.clientX - _ltDrag.startX;
  var dy = e.clientY - _ltDrag.startY;
  if (!_ltDrag.moved && Math.abs(dx) + Math.abs(dy) < 4) return;

  _ltDrag.moved = true;

  /* Position ghost */
  _ltDndGhost.style.display = "block";
  _ltDndGhost.style.left = (e.clientX + 14) + "px";
  _ltDndGhost.style.top  = (e.clientY + 8) + "px";

  /* Dim source row */
  if (_ltDrag.sourceRow) _ltDrag.sourceRow.style.opacity = "0.35";

  /* Auto-scroll container near edges */
  var container = document.getElementById("catlist");
  if (container) {
    var cr = container.getBoundingClientRect();
    if (e.clientY < cr.top + 30)     container.scrollTop -= 8;
    else if (e.clientY > cr.bottom - 30) container.scrollTop += 8;
  }

  _ltDndClearViz();
  var descIds = _ltDndDescendants(_ltDrag.id);

  /* Find row under pointer */
  var row = _ltDndRowUnder(e.clientY);
  _ltDrag.target = null;

  if (!row) {
    /* Empty area below all rows → move to root tail */
    _ltDrag.target = { mode: "root" };
    _ltDndShowLineAtTail();
    return;
  }

  var tid = row.getAttribute("data-catid");
  var tkind = row.getAttribute("data-nodekind");

  /* Self or descendant → no-drop */
  if (tid === _ltDrag.id) return;
  if (descIds.indexOf(tid) >= 0) return;

  var r = row.getBoundingClientRect();
  var rel = (e.clientY - r.top) / (r.height || 1);

  if (rel < 0.30) {
    _ltDrag.target = { mode: "before", id: tid };
    _ltDndShowLineBefore(row);
  } else if (rel > 0.70) {
    _ltDrag.target = { mode: "after", id: tid };
    _ltDndShowLineAfter(row);
  } else {
    /* Middle 40% */
    if (tkind === "folder") {
      /* Nest-into folder */
      _ltDrag.target = { mode: "nest", id: tid };
      row.classList.add("lt-drop-into");
    } else {
      /* Layer middle — check auto-group condition (LDND-S3) */
      var dragNode = layerById(_ltDrag.id);
      var tgtNode  = layerById(tid);
      var dragIsRootLayer = (dragNode && (dragNode.parentId === null || dragNode.parentId === undefined));
      var tgtIsRootLayer  = (tgtNode  && (tgtNode.parentId  === null || tgtNode.parentId  === undefined));
      if (_ltAutoGroup && dragIsRootLayer && tgtIsRootLayer) {
        /* Auto-group: green double-ring indicator */
        _ltDrag.target = { mode: "group", id: tid };
        row.classList.add("lt-drop-group");
      } else {
        /* No auto-group → insert-after */
        _ltDrag.target = { mode: "after", id: tid };
        _ltDndShowLineAfter(row);
      }
    }
  }
}

/* ------------------------------------------------------------------
   9. _ltDndOnUp(e)
   ------------------------------------------------------------------ */
function _ltDndOnUp(e) {
  window.removeEventListener("pointermove", _ltDndOnMove);

  /* Restore source row opacity */
  if (_ltDrag && _ltDrag.sourceRow) _ltDrag.sourceRow.style.opacity = "";

  _ltDndGhost.style.display = "none";
  _ltDndClearViz();

  if (_ltDrag && _ltDrag.moved && _ltDrag.target) {
    if (typeof pushUndo === "function") pushUndo(); // undo covers LAYERS/FOLDERS: capture BEFORE reparent/reorder (incl. group auto-folder)
    _ltDndCommit(_ltDrag);
    buildPicker();
    draw();
    state.dirty = true;
  }

  _ltDrag = null;
}

/* ------------------------------------------------------------------
   10. _ltDndCommit(d)  — mutates .order / .parentId, then renumbers
   ------------------------------------------------------------------ */
function _ltDndCommit(d) {
  var node = (d.kind === "folder") ? folderById(d.id) : layerById(d.id);
  if (!node) return;
  var t = d.target;

  if (t.mode === "root") {
    var oldParent = (node.parentId !== undefined) ? node.parentId : null;
    node.parentId = null;
    _ltDndReindex(oldParent);
    /* Append at tail of root */
    var rootKids = childrenOf(null);
    node.order = rootKids.length; /* tentative */
    _ltDndReindex(null);
    return;
  }

  if (t.mode === "nest") {
    var oldParent2 = (node.parentId !== undefined) ? node.parentId : null;
    node.parentId = t.id;
    _ltDndReindex(oldParent2);
    var nestKids = childrenOf(t.id);
    node.order = nestKids.length; /* tentative */
    _ltDndReindex(t.id);
    return;
  }

  if (t.mode === "group") {
    /* LDND-S3: auto-create folder wrapping targetNode + draggedNode */
    var targetNode  = layerById(t.id);
    if (!targetNode) return;
    var oldParentG  = (node.parentId !== undefined) ? node.parentId : null;
    /* Create folder at target's old position in root */
    var f = addFolder(targetNode.name + " กลุ่ม", targetNode.color, null);
    f.order = targetNode.order; /* land where target was */
    /* Reparent both nodes */
    targetNode.parentId = f.id;
    node.parentId       = f.id;
    /* Renumber root (folder now occupies target's slot; target + dragged gone) */
    _ltDndReindex(null);
    /* Renumber folder children: target=0, dragged=1 */
    targetNode.order = 0;
    node.order       = 1;
    _ltDndReindex(f.id);
    /* Activate the dragged layer (NOT the folder id — activeCat must stay a
       layer id; updateHUD()/catOf() resolve layers only and crash on a folder
       id). Expand the new folder so both children are visible. */
    state.activeCat = node.id;
    if (!state.folderCollapsed) state.folderCollapsed = {};
    state.folderCollapsed[f.id] = false;
    /* Ensure catVis/catLock initialised for new folder */
    if (state.catVis  && state.catVis[f.id]  === undefined) state.catVis[f.id]  = true;
    if (state.catLock && state.catLock[f.id] === undefined) state.catLock[f.id] = false;
    return;
  }

  /* before / after: move node into target's sibling group */
  var tnode = folderById(t.id) || layerById(t.id);
  if (!tnode) return;

  var newParent = (tnode.parentId !== undefined) ? tnode.parentId : null;
  var oldParent3 = (node.parentId !== undefined) ? node.parentId : null;

  node.parentId = newParent;

  /* Build new sibling order: get siblings WITHOUT the dragged node */
  var sibs = childrenOf(newParent).filter(function(x) { return x.node.id !== node.id; });
  var idx = -1;
  for (var i = 0; i < sibs.length; i++) {
    if (sibs[i].node.id === t.id) { idx = i; break; }
  }
  if (t.mode === "after") idx++;
  if (idx < 0) idx = 0;
  sibs.splice(idx, 0, { kind: d.kind, node: node });
  for (var j = 0; j < sibs.length; j++) sibs[j].node.order = j;

  /* Renumber old parent group if parent changed */
  if (oldParent3 !== newParent) _ltDndReindex(oldParent3);
}

/* ------------------------------------------------------------------
   11. _ltDndReindex(parentId)  — rewrite .order 0..n-1 for sibling group
   ------------------------------------------------------------------ */
function _ltDndReindex(parentId) {
  var kids = childrenOf(parentId);
  for (var i = 0; i < kids.length; i++) kids[i].node.order = i;
}

/* ------------------------------------------------------------------
   12. Drop-indicator helpers
   ------------------------------------------------------------------ */
function _ltDndRowUnder(clientY) {
  var container = document.getElementById("catlist");
  if (!container) return null;
  var rows = container.querySelectorAll(".cat");
  for (var i = 0; i < rows.length; i++) {
    var r = rows[i].getBoundingClientRect();
    if (clientY >= r.top && clientY <= r.bottom) return rows[i];
  }
  return null;
}

function _ltDndClearViz() {
  if (_ltDndLine) _ltDndLine.style.display = "none";
  var over = document.querySelectorAll(".lt-drop-into,.lt-drop-group");
  for (var i = 0; i < over.length; i++) {
    over[i].classList.remove("lt-drop-into");
    over[i].classList.remove("lt-drop-group");
  }
}

function _ltDndShowLineBefore(row) {
  _ltDndPlaceLine(row, true);
}

function _ltDndShowLineAfter(row) {
  _ltDndPlaceLine(row, false);
}

function _ltDndPlaceLine(row, before) {
  if (!_ltDndLine) return;
  var container = document.getElementById("catlist");
  if (!container) return;
  var rr = row.getBoundingClientRect();
  var cr = container.getBoundingClientRect();
  var indentPx = parseFloat(row.style.marginLeft || 0);
  _ltDndLine.style.top  = ((before ? rr.top : rr.bottom) - cr.top + container.scrollTop - 1) + "px";
  _ltDndLine.style.left = (indentPx + 4) + "px";
  _ltDndLine.style.display = "block";
}

function _ltDndShowLineAtTail() {
  if (!_ltDndLine) return;
  var container = document.getElementById("catlist");
  if (!container) return;
  _ltDndLine.style.top  = (container.scrollHeight - 6) + "px";
  _ltDndLine.style.left = "4px";
  _ltDndLine.style.display = "block";
}
