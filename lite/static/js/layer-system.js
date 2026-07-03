/* ============================================================
   LITE-LAYER-SYSTEM — category / layer foundation (L1 sprint)
   Plain-globals module. No IIFE, no export, no bundler.
   Loaded via <script src="static/js/layer-system.js"> BEFORE
   the inline script in ui-lite.html.

   Public API:
     ROLE_DEFS          — array of 6 immutable role definitions
     LAYERS             — array of seeded default layers (1 per role)
     FOLDERS            — array of folder nodes (LST-1; starts empty)
     initLayers()       — idempotent seed; called at module load
     roleDef(role)      — returns ROLE_DEFS entry for role id
     roleSemanticTag(role) — returns role's semantic tag string
     layerById(id)      — returns LAYERS entry by id (or null)
     layersInOrder()    — sorted copy of LAYERS ascending by .order
     resolveSemanticTag(layerId) — roleSemanticTag(layerById(layerId).role)
     reassignObjectsOfLayer(layerId,toLayerId) — B3: retarget PS objects + CFSS
       masters' catId; used by removeLayer() before it splices
     sweepOrphanCatIds() — B3: heal any catId with no resolving layer (PS +
       CFSS masters), called once at the end of loadProto()

     -- Folder CRUD (LST-1) --
     nextFolderId()     — next collision-free "F"+n id
     addFolder(name,color,parentId) — push folder, return it
     folderById(id)     — folder or null
     removeFolder(id)   — splice + reparent children; returns {removed,reparentedTo}
     foldersInOrder()   — sorted copy by .order

     -- Tree accessors (LST-1) — pure, no area math --
     nodeParent(id)     — parentId of layer or folder, else null
     ancestorsOf(id)    — [parent…root] ids (excl. self), cycle-guarded
     childrenOf(parentId) — [{kind,node}] folders-before-layers, asc .order
     effVisible(id, isHidden)  — false if any ancestor isHidden
     effLocked(id, isLocked)   — false if any ancestor isLocked
     rollupArea(nodeId, ownAreaOf) — Σ ownAreaOf over all descendant layers

   Invariants:
     - layer.id === role.id so existing objects' catId resolves unchanged
     - each layer also carries .tag and .counting copied from its roleDef
       so catOf(id).tag and catOf(id).counting work with zero call-site changes
     - insertion order of LAYERS matches original CATS order (picker looks identical)
     - LAYERS and FOLDERS identity never reassigned; splice in place
     - parentId is additive (NOT yet written to .bmaplan — that is LST-2)
     - semanticTag is always role-derived; folders never enter any tag/area path
   ============================================================ */

/* --- Role definitions — verbatim copy of the CATS array from ui-lite.html --- */
var ROLE_DEFS = [
  {id:"gfa",  name:"พื้นที่อาคาร",  tag:"gross_floor_area",   color:"#4c8dff"},
  {id:"use",  name:"พื้นที่ใช้สอย", tag:"use_area",           color:"#39d98a"},
  {id:"ded",  name:"ช่องว่าง/หัก",  tag:"deduction_opening",  color:"#ff6b6b"},
  {id:"site", name:"ที่ดิน",        tag:"site_land_area",     color:"#c084fc"},
  {id:"open", name:"ที่ว่าง",       tag:"legal_open_space",   color:"#ffb454"},
  {id:"count",name:"นับจำนวน",      tag:"count_marker",       color:"#22d3ee", counting:true},
];

/* --- Mutable layer list (seeded by initLayers) --- */
var LAYERS = [];

/* --- Mutable folder list (LST-1; seeded empty — folders created by user) --- */
/* Folder shape: {id, name, color, parentId, order}                           */
/* No role, no tag, no objects. ids use "F"+n prefix (independent of layers). */
var FOLDERS = [];

/* --- Seed one default layer per role (idempotent: no-op if already seeded) --- */
function initLayers() {
  if (LAYERS.length > 0) return; // idempotent guard
  ROLE_DEFS.forEach(function (r, idx) {
    var layer = {
      id:       r.id,       // layer.id === role.id — catId resolves unchanged
      name:     r.name,
      color:    r.color,
      role:     r.id,
      /* compatibility shim — catOf(id).tag and catOf(id).counting still work */
      tag:      r.tag,
      counting: r.counting || false,
      subTag:   "",
      order:    idx,
      groupId:  null,
      parentId: null,       // LST-1: null = root; additive, not yet persisted
    };
    LAYERS.push(layer);
  });
}

/* --- Accessors --- */
function roleDef(role) {
  for (var i = 0; i < ROLE_DEFS.length; i++) {
    if (ROLE_DEFS[i].id === role) return ROLE_DEFS[i];
  }
  return null;
}

function roleSemanticTag(role) {
  var rd = roleDef(role);
  return rd ? rd.tag : null;
}

function layerById(id) {
  for (var i = 0; i < LAYERS.length; i++) {
    if (LAYERS[i].id === id) return LAYERS[i];
  }
  return null;
}

function layersInOrder() {
  return LAYERS.slice().sort(function (a, b) { return a.order - b.order; });
}

function resolveSemanticTag(layerId) {
  var layer = layerById(layerId);
  return layer ? roleSemanticTag(layer.role) : null;
}

/* --- Z-order helpers (L2a) --- */

/** Return the .order value for the layer identified by catId (999 = unknown / fallback). */
function layerOrderOf(catId) {
  var l = layerById(catId);
  return l ? l.order : 999;
}

/**
 * Return a NEW array of objects sorted ASCENDING by layer .order.
 * Stable: objects with the same .order keep their original relative sequence.
 * The input array is NOT mutated — PSpage().objects insertion order is preserved
 * for save/load and export builders which depend on it.
 */
function objectsInZOrder(objs) {
  // Decorate with original index for stable sort, then sort, then undecorate.
  return objs
    .map(function(o, i) { return { o: o, i: i, ord: layerOrderOf(o.catId) }; })
    .sort(function(a, b) { return a.ord !== b.ord ? a.ord - b.ord : a.i - b.i; })
    .map(function(d) { return d.o; });
}

/* --- Custom-layer CRUD helpers (L2c-1) --- */

/** True iff a layer exists with this id AND id === its role (i.e. it is the seed/default). */
function isDefaultLayer(id) {
  var l = layerById(id);
  return !!(l && l.id === l.role);
}

/** The seed layer id for a role equals the role id itself. Returns null if role invalid. */
function defaultLayerIdForRole(role) {
  return roleDef(role) ? role : null;
}

/**
 * Generate a new id string NOT colliding with any existing LAYERS id and NOT
 * equal to any role id. Uses scheme "L" + n, n starting at 1, incrementing
 * until a free slot is found.
 */
function nextLayerId() {
  var existing = {};
  for (var i = 0; i < LAYERS.length; i++) existing[LAYERS[i].id] = true;
  var roleIds = {};
  for (var j = 0; j < ROLE_DEFS.length; j++) roleIds[ROLE_DEFS[j].id] = true;
  var n = 1;
  while (true) {
    var candidate = "L" + n;
    if (!existing[candidate] && !roleIds[candidate]) return candidate;
    n++;
  }
}

/**
 * Add a custom layer for the given role.
 * Returns the new layer, or null if role is invalid.
 * INVARIANT: .tag always equals roleSemanticTag(role), never derived from name.
 */
function addLayer(role, name, color) {
  var rd = roleDef(role);
  if (!rd) return null;
  var maxOrder = -1;
  for (var i = 0; i < LAYERS.length; i++) {
    if (LAYERS[i].order > maxOrder) maxOrder = LAYERS[i].order;
  }
  var layer = {
    id:       nextLayerId(),
    name:     (name && name.length > 0) ? name : rd.name,
    color:    (color && color.length > 0) ? color : rd.color,
    role:     role,
    tag:      roleSemanticTag(role),   // INVARIANT: from role, never from name
    counting: !!rd.counting,
    subTag:   "",
    order:    maxOrder + 1,
    groupId:  null,
    parentId: null,                    // LST-1: null = root; additive, not yet persisted
  };
  LAYERS.push(layer);
  return layer;
}

/** Rename a layer's display name only. Does NOT touch role/tag/counting. Returns bool. */
function renameLayer(id, name) {
  if (!name || name.length === 0) return false;
  var l = layerById(id);
  if (!l) return false;
  l.name = name;
  return true;
}

/** Change a layer's display color only. Returns bool. */
function recolorLayer(id, color) {
  var l = layerById(id);
  if (!l) return false;
  l.color = color;
  return true;
}

/**
 * Rewrite .order for each layer to its index in orderedIds.
 * Requires a full permutation (orderedIds.length === LAYERS.length).
 * Returns false (changes nothing) if lengths differ.
 * Ids in orderedIds not found in LAYERS are silently ignored for position
 * assignment, but the length check still applies.
 */
function reorderLayers(orderedIds) {
  if (!orderedIds || orderedIds.length !== LAYERS.length) return false;
  for (var i = 0; i < orderedIds.length; i++) {
    var l = layerById(orderedIds[i]);
    if (l) l.order = i;
  }
  return true;
}

/**
 * B3 (INV-20260703-layer-linkage, H3 orphaned-catId fix).
 * Reassign every object (across all PS pages, if PS is loaded) and every
 * CFSS master (window.MASTERS, if the module is loaded) whose catId ===
 * layerId to toLayerId. Pure-ish: reads PS/window.MASTERS via typeof-guard
 * so it is a harmless no-op in contexts where they don't exist yet (e.g.
 * pure layer-model tests). Mutates matching objects/masters in place.
 * Returns the count reassigned.
 */
function reassignObjectsOfLayer(layerId, toLayerId) {
  if (!layerId || !toLayerId || layerId === toLayerId) return 0;
  var n = 0;
  if (typeof PS !== "undefined" && PS) {
    Object.keys(PS).forEach(function (k) {
      var objs = (PS[k] && PS[k].objects) || [];
      for (var i = 0; i < objs.length; i++) {
        if (objs[i].catId === layerId) { objs[i].catId = toLayerId; n++; }
      }
    });
  }
  if (typeof window !== "undefined" && window.MASTERS) {
    Object.keys(window.MASTERS).forEach(function (mid) {
      var m = window.MASTERS[mid];
      if (m && m.catId === layerId) { m.catId = toLayerId; n++; }
    });
  }
  return n;
}

/**
 * Remove a custom layer from LAYERS.
 * - Not found         → {removed:false, reason:"not_found"}
 * - Is default layer  → {removed:false, reason:"is_default"}
 * - Else              → reassigns every object/master on this layer to the
 *                        role's default layer FIRST (reassignObjectsOfLayer),
 *                        THEN removes from LAYERS. Returns {removed:true,
 *                        role:<role>, reassignTo:<defaultLayerIdForRole(role)>}
 */
function removeLayer(id) {
  var l = layerById(id);
  if (!l) return {removed: false, reason: "not_found"};
  if (isDefaultLayer(id)) return {removed: false, reason: "is_default"};
  var savedRole = l.role;
  var reassignTo = defaultLayerIdForRole(savedRole);
  reassignObjectsOfLayer(id, reassignTo);
  // splice IN PLACE — never reassign LAYERS, or the `var CATS = LAYERS` alias in
  // ui-lite.html would keep pointing at the old array and silently diverge.
  for (var i = 0; i < LAYERS.length; i++) { if (LAYERS[i].id === id) { LAYERS.splice(i, 1); break; } }
  return {removed: true, role: savedRole, reassignTo: reassignTo};
}

/**
 * B3 (H3 orphaned-catId fix) — load-time healing sweep.
 * Scans every object across all PS pages plus every CFSS master
 * (window.MASTERS) and reassigns any catId that no longer resolves to a
 * layer in LAYERS (e.g. a legacy save referencing a since-deleted custom
 * layer, or any other path that produced a stale catId before this sprint's
 * removeLayer/resetPageFolders fixes existed). Fallback target: SEM_REV[
 * o.semanticTag] (ui-lite.html global, typeof-guarded — absent in pure JS
 * test contexts) else the 'use' role's default layer else the literal
 * string 'use'. Idempotent; safe to call repeatedly (e.g. once at the end
 * of every loadProto()). Returns the count of catIds healed.
 */
function sweepOrphanCatIds() {
  var healed = 0;
  var semRev = (typeof SEM_REV !== "undefined") ? SEM_REV : {};
  function fallbackFor(semanticTag) {
    return semRev[semanticTag] || defaultLayerIdForRole("use") || "use";
  }
  if (typeof PS !== "undefined" && PS) {
    Object.keys(PS).forEach(function (k) {
      var objs = (PS[k] && PS[k].objects) || [];
      for (var i = 0; i < objs.length; i++) {
        var o = objs[i];
        if (o.catId != null && !layerById(o.catId)) {
          o.catId = fallbackFor(o.semanticTag);
          healed++;
        }
      }
    });
  }
  if (typeof window !== "undefined" && window.MASTERS) {
    Object.keys(window.MASTERS).forEach(function (mid) {
      var m = window.MASTERS[mid];
      if (m && m.catId != null && !layerById(m.catId)) {
        m.catId = fallbackFor(m.semanticTag);
        healed++;
      }
    });
  }
  if (healed > 0 && typeof console !== "undefined" && console.warn) {
    console.warn("[layer-system] sweepOrphanCatIds healed " + healed + " orphaned catId(s)");
  }
  return healed;
}

/* ============================================================
   FOLDER CRUD (LST-1)
   FOLDERS uses "F"+n ids; prefix keeps them independent of LAYERS ids.
   All mutations splice in place — never reassign FOLDERS.
   ============================================================ */

/**
 * Generate next folder id "F1","F2",… not colliding with any existing FOLDERS id.
 * Folder ids are independent of layer ids; the "F" prefix guarantees no clash.
 */
function nextFolderId() {
  var existing = {};
  for (var i = 0; i < FOLDERS.length; i++) existing[FOLDERS[i].id] = true;
  var n = 1;
  while (true) {
    var candidate = "F" + n;
    if (!existing[candidate]) return candidate;
    n++;
  }
}

/**
 * Add a folder.
 * Folder shape: {id, name, color, parentId, order}
 * NO role, NO tag, NO objects.
 * Returns the new folder.
 */
function addFolder(name, color, parentId) {
  var maxOrder = -1;
  for (var i = 0; i < FOLDERS.length; i++) {
    if (FOLDERS[i].order > maxOrder) maxOrder = FOLDERS[i].order;
  }
  var folder = {
    id:       nextFolderId(),
    name:     (name && name.length > 0) ? name : "กลุ่มใหม่",
    color:    (color && color.length > 0) ? color : "#ffb454",
    parentId: (parentId !== undefined && parentId !== null) ? parentId : null,
    order:    maxOrder + 1,
  };
  FOLDERS.push(folder);
  return folder;
}

/** Return folder by id or null. */
function folderById(id) {
  for (var i = 0; i < FOLDERS.length; i++) {
    if (FOLDERS[i].id === id) return FOLDERS[i];
  }
  return null;
}

/**
 * Remove a folder by id.
 * - Not found → {removed:false}
 * - Else: splice in place AND reparent — every layer or folder whose
 *   parentId === id gets parentId set to the removed folder's own parentId
 *   (children move up one level). Returns {removed:true, reparentedTo:<parentId>}.
 */
function removeFolder(id) {
  var f = folderById(id);
  if (!f) return {removed: false};
  var parentOfRemoved = f.parentId;
  // Splice the folder from FOLDERS in place.
  for (var i = 0; i < FOLDERS.length; i++) {
    if (FOLDERS[i].id === id) { FOLDERS.splice(i, 1); break; }
  }
  // Reparent children (folders).
  for (var j = 0; j < FOLDERS.length; j++) {
    if (FOLDERS[j].parentId === id) FOLDERS[j].parentId = parentOfRemoved;
  }
  // Reparent children (layers).
  for (var k = 0; k < LAYERS.length; k++) {
    if (LAYERS[k].parentId === id) LAYERS[k].parentId = parentOfRemoved;
  }
  return {removed: true, reparentedTo: parentOfRemoved};
}

/** Return a sorted copy of FOLDERS ascending by .order. */
function foldersInOrder() {
  return FOLDERS.slice().sort(function (a, b) { return a.order - b.order; });
}

/* ============================================================
   TREE ACCESSORS (LST-1)
   Pure — no dependency on state, measure-engine, or area math.
   Callers supply lookup functions (isHidden, isLocked, ownAreaOf).
   ============================================================ */

/**
 * Return the parentId of the layer or folder with this id, or null if not found.
 */
function nodeParent(id) {
  var l = layerById(id);
  if (l) return l.parentId !== undefined ? l.parentId : null;
  var f = folderById(id);
  if (f) return f.parentId !== undefined ? f.parentId : null;
  return null;
}

/**
 * Return array of ancestor ids [parent, grandparent, … root] (excluding self).
 * Walks nodeParent. Cycle-guarded at depth 100.
 */
function ancestorsOf(id) {
  var result = [];
  var current = nodeParent(id);
  var depth = 0;
  var seen = {};
  seen[id] = true;
  while (current !== null && current !== undefined && depth < 100) {
    if (seen[current]) break; // cycle guard
    seen[current] = true;
    result.push(current);
    current = nodeParent(current);
    depth++;
  }
  return result;
}

/**
 * Return [{kind:"folder"|"layer", node}] for every folder and layer
 * whose parentId === parentId argument (pass null for roots).
 * Ordering: folders before layers on equal .order, then ascending .order, stable.
 * Uses decorate-index trick for stability (mirrors objectsInZOrder).
 */
function childrenOf(parentId) {
  var items = [];
  for (var i = 0; i < FOLDERS.length; i++) {
    var f = FOLDERS[i];
    var fp = (f.parentId !== undefined) ? f.parentId : null;
    if (fp === parentId) items.push({kind: "folder", node: f});
  }
  for (var j = 0; j < LAYERS.length; j++) {
    var l = LAYERS[j];
    var lp = (l.parentId !== undefined) ? l.parentId : null;
    if (lp === parentId) items.push({kind: "layer", node: l});
  }
  // Stable sort: folders before layers on equal .order, then ascending .order.
  // Decorate with original index for stability.
  items = items
    .map(function(item, idx) { return {item: item, idx: idx}; })
    .sort(function(a, b) {
      var aOrd = a.item.node.order;
      var bOrd = b.item.node.order;
      if (aOrd !== bOrd) return aOrd - bOrd;
      // Equal order: folders sort before layers.
      var aKind = a.item.kind === "folder" ? 0 : 1;
      var bKind = b.item.kind === "folder" ? 0 : 1;
      if (aKind !== bKind) return aKind - bKind;
      // Equal order + kind: stable by original index.
      return a.idx - b.idx;
    })
    .map(function(d) { return d.item; });
  return items;
}

/**
 * effVisible: returns false if isHidden(id) or any ancestor isHidden, else true.
 * isHidden is a caller-supplied fn(nodeId)->bool.
 */
function effVisible(id, isHidden) {
  if (isHidden(id)) return false;
  var ancestors = ancestorsOf(id);
  for (var i = 0; i < ancestors.length; i++) {
    if (isHidden(ancestors[i])) return false;
  }
  return true;
}

/**
 * effLocked: returns true if isLocked(id) or any ancestor isLocked, else false.
 * isLocked is a caller-supplied fn(nodeId)->bool.
 */
function effLocked(id, isLocked) {
  if (isLocked(id)) return true;
  var ancestors = ancestorsOf(id);
  for (var i = 0; i < ancestors.length; i++) {
    if (isLocked(ancestors[i])) return true;
  }
  return false;
}

/**
 * rollupArea: signed sum of ownAreaOf(layerId) over every descendant LAYER
 * (recurse through folders and sub-layers). Folders contribute 0 of their own.
 * ownAreaOf is a caller-supplied fn(layerId)->number (returns signed values;
 * deductions are negative because the caller makes them so).
 * Area math is NOT computed here — just sum what ownAreaOf returns.
 */
function rollupArea(nodeId, ownAreaOf) {
  var total = 0;
  // If nodeId is a layer, include its own area.
  if (layerById(nodeId)) total += ownAreaOf(nodeId);
  // Recurse into all children (folders and layers).
  var children = childrenOf(nodeId);
  for (var i = 0; i < children.length; i++) {
    var child = children[i];
    if (child.kind === "layer") {
      // Add own area of child layer plus any of its sub-layers.
      total += rollupArea(child.node.id, ownAreaOf);
    } else {
      // Folder: recurse (folder itself contributes 0 own area).
      total += rollupArea(child.node.id, ownAreaOf);
    }
  }
  return total;
}

/* --- Bootstrap --- */
initLayers();
