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
