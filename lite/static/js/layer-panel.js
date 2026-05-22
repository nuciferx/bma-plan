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
   buildPicker()
   Full replacement of the inline version. Wires:
     • header "+" button (add layer)
     • .sw swatch click → recolor (color picker)
     • .nm click → inline rename input
     • data-eye / data-lock (preserved from original)
     • ▲▼ reorder buttons (easier than drag/drop for Playwright tests)
     • ✕ delete button (custom layers only)
     • row click (not on controls) → set activeCat
   ------------------------------------------------------------------ */
function buildPicker() {
  var el = document.getElementById("catlist");
  el.innerHTML = "";

  var layers = layersInOrder();

  layers.forEach(function(c, idx) {
    var d = document.createElement("div");
    d.className = "cat" + (state.activeCat === c.id ? " active" : "");
    d.setAttribute("data-catid", c.id);

    /* ---- swatch (click → recolor) ---- */
    var sw = document.createElement("span");
    sw.className = "sw lp-sw";
    sw.style.background = c.color;
    sw.setAttribute("data-recolor", c.id);
    sw.title = "เปลี่ยนสี";
    sw.addEventListener("click", function(e) {
      e.stopPropagation();
      var inp = document.createElement("input");
      inp.type = "color";
      inp.value = c.color;
      inp.style.display = "none";
      document.body.appendChild(inp);
      inp.addEventListener("change", function() {
        recolorLayer(c.id, inp.value);
        state.dirty = true;
        document.body.removeChild(inp);
        buildPicker();
        draw();
      });
      inp.addEventListener("blur", function() {
        // remove orphan picker if no change event fired
        if (inp.parentNode) document.body.removeChild(inp);
      });
      inp.click();
    });

    /* ---- name span / inline rename ---- */
    var nm = document.createElement("span");
    nm.className = "nm";
    nm.textContent = c.name;
    nm.title = "คลิกเพื่อเปลี่ยนชื่อ";
    nm.addEventListener("click", function(e) {
      e.stopPropagation();
      // replace span with input
      var inp = document.createElement("input");
      inp.className = "lp-rename-inp";
      inp.value = c.name;
      nm.replaceWith(inp);
      inp.focus();
      inp.select();
      var committed = false;
      function commit() {
        if (committed) return;
        committed = true;
        _lpCommitRename(c.id, inp.value);
      }
      inp.addEventListener("keydown", function(ev) {
        if (ev.key === "Enter") { ev.preventDefault(); commit(); }
        if (ev.key === "Escape") { committed = true; buildPicker(); }
        ev.stopPropagation(); // prevent canvas keydown handlers
      });
      inp.addEventListener("blur", commit);
    });

    /* ---- eye toggle ---- */
    var eye = document.createElement("span");
    eye.className = "eye" + (state.catVis[c.id] ? "" : " off");
    eye.setAttribute("data-eye", c.id);
    eye.textContent = state.catVis[c.id] ? "👁" : "🚫";

    /* ---- lock toggle ---- */
    var lk = document.createElement("span");
    lk.className = "eye" + (state.catLock[c.id] ? " off" : "");
    lk.setAttribute("data-lock", c.id);
    lk.textContent = state.catLock[c.id] ? "🔒" : "🔓";

    /* ---- ▲▼ reorder buttons ---- */
    var btnUp = document.createElement("button");
    btnUp.className = "lp-ord-btn";
    btnUp.textContent = "▲";
    btnUp.title = "เลื่อนขึ้น";
    btnUp.disabled = (idx === 0);
    btnUp.setAttribute("data-reorder-up", c.id);

    var btnDn = document.createElement("button");
    btnDn.className = "lp-ord-btn";
    btnDn.textContent = "▼";
    btnDn.title = "เลื่อนลง";
    btnDn.disabled = (idx === layers.length - 1);
    btnDn.setAttribute("data-reorder-dn", c.id);

    btnUp.addEventListener("click", function(e) {
      e.stopPropagation();
      if (idx === 0) return;
      var orderedIds = layers.map(function(l) { return l.id; });
      // swap with previous
      var tmp = orderedIds[idx - 1];
      orderedIds[idx - 1] = orderedIds[idx];
      orderedIds[idx] = tmp;
      reorderLayers(orderedIds);
      state.dirty = true;
      buildPicker();
      draw();
    });

    btnDn.addEventListener("click", function(e) {
      e.stopPropagation();
      if (idx === layers.length - 1) return;
      var orderedIds = layers.map(function(l) { return l.id; });
      // swap with next
      var tmp = orderedIds[idx + 1];
      orderedIds[idx + 1] = orderedIds[idx];
      orderedIds[idx] = tmp;
      reorderLayers(orderedIds);
      state.dirty = true;
      buildPicker();
      draw();
    });

    /* ---- delete button (custom only) ---- */
    var btnDel = null;
    if (!isDefaultLayer(c.id)) {
      btnDel = document.createElement("button");
      btnDel.className = "lp-del-btn";
      btnDel.textContent = "✕";
      btnDel.title = "ลบ layer นี้";
      btnDel.setAttribute("data-layer-del", c.id);
      btnDel.addEventListener("click", function(e) {
        e.stopPropagation();
        if (!confirm("ลบ layer \"" + c.name + "\"?\nวัตถุทั้งหมดจะถูกย้ายไป layer หลัก")) return;
        var r = removeLayer(c.id);
        if (!r.removed) return; // defensive
        // reassign ALL objects across ALL pages
        Object.keys(PS).forEach(function(k) {
          (PS[k].objects || []).forEach(function(o) {
            if (o.catId === c.id) o.catId = r.reassignTo;
          });
        });
        if (state.activeCat === c.id) state.activeCat = r.reassignTo;
        delete state.catVis[c.id];
        delete state.catLock[c.id];
        state.dirty = true;
        buildPicker();
        draw();
      });
    }

    /* ---- row click (not on controls) → set activeCat ---- */
    d.addEventListener("click", function(e) {
      if (e.target.dataset.eye) {
        state.catVis[c.id] = !state.catVis[c.id];
        buildPicker(); draw(); return;
      }
      if (e.target.dataset.lock) {
        state.catLock[c.id] = !state.catLock[c.id];
        buildPicker(); draw(); return;
      }
      // any other click on the row (not on a control button) = select
      if (e.target.classList.contains("lp-ord-btn")) return;
      if (e.target.classList.contains("lp-del-btn")) return;
      if (e.target.classList.contains("lp-sw")) return;
      if (e.target.classList.contains("nm")) return; // rename handled separately
      state.activeCat = c.id;
      state.tool = c.counting ? "count" : (state.tool === "count" ? "poly" : state.tool);
      buildPicker(); draw();
    });

    d.appendChild(sw);
    d.appendChild(nm);
    d.appendChild(eye);
    d.appendChild(lk);
    d.appendChild(btnUp);
    d.appendChild(btnDn);
    if (btnDel) d.appendChild(btnDel);
    el.appendChild(d);
  });
}

/* ------------------------------------------------------------------
   lpHandleAddLayer()
   Wired to the "+" button in the picker header.
   New layer inherits the ROLE of the currently active layer so the
   semanticTag is role-derived (INVARIANT: never from name).
   ------------------------------------------------------------------ */
function lpHandleAddLayer() {
  var active = layerById(state.activeCat);
  if (!active) return;
  var n = layersInOrder().length + 1;
  var newLayer = addLayer(active.role, active.name + " " + n, active.color);
  if (!newLayer) return;
  state.catVis[newLayer.id] = true;
  state.catLock[newLayer.id] = false;
  state.activeCat = newLayer.id;
  state.dirty = true;
  buildPicker();
  draw();
}
