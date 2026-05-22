/* ============================================================
   LITE-LAYER-SYSTEM — category / layer foundation (L1 sprint)
   Plain-globals module. No IIFE, no export, no bundler.
   Loaded via <script src="static/js/layer-system.js"> BEFORE
   the inline script in ui-lite.html.

   Public API:
     ROLE_DEFS          — array of 6 immutable role definitions
     LAYERS             — array of seeded default layers (1 per role)
     initLayers()       — idempotent seed; called at module load
     roleDef(role)      — returns ROLE_DEFS entry for role id
     roleSemanticTag(role) — returns role's semantic tag string
     layerById(id)      — returns LAYERS entry by id (or null)
     layersInOrder()    — sorted copy of LAYERS ascending by .order
     resolveSemanticTag(layerId) — roleSemanticTag(layerById(layerId).role)

   Invariants:
     - layer.id === role.id so existing objects' catId resolves unchanged
     - each layer also carries .tag and .counting copied from its roleDef
       so catOf(id).tag and catOf(id).counting work with zero call-site changes
     - insertion order of LAYERS matches original CATS order (picker looks identical)
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

/* --- Bootstrap --- */
initLayers();
