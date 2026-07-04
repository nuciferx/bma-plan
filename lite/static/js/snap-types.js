/* LSNAP-1: snap-types.js — per-type snap toggles (Endpoint / Midpoint / Center /
   Intersection / Nearest-on-edge — 5th type added SNAP-2026-07-04 slice 3/3).
   Loaded BEFORE menu-flyout.js. Declares globals: initSnapTypes, toggleSnapType,
   snapTypeLabel, snapTypeChip, toggleSnapTypeEndpoint, toggleSnapTypeMidpoint,
   toggleSnapTypeCenter, toggleSnapTypeIntersection, toggleSnapTypeNearest.
   Runtime-only — snapTypes is stored in localStorage, NOT .bmaplan.
   Nearest-on-edge default = true (old behavior) — the merge-over-defaults in
   loadSnapTypesFromLocalStorage() below means an old saved payload that
   predates this key (no `nearest` field) still resolves to true, since
   Object.assign({}, _SNAP_DEFAULTS, parsed) only overrides keys `parsed`
   actually has. */

var _SNAP_TYPES_KEY = 'lite.snapTypes.v1';
var _SNAP_DEFAULTS  = { endpoint: true, midpoint: true, center: true, intersection: true, nearest: true };

/* --------------------------------------------------------------------------
   Persistence helpers
--------------------------------------------------------------------------- */
function loadSnapTypesFromLocalStorage() {
  try {
    var raw = localStorage.getItem(_SNAP_TYPES_KEY);
    if (raw) {
      var parsed = JSON.parse(raw);
      // merge over defaults so new keys survive
      Object.keys(_SNAP_DEFAULTS).forEach(function (k) {
        if (typeof parsed[k] === 'boolean') _SNAP_DEFAULTS[k] = parsed[k];
      });
      state.snapTypes = Object.assign({}, _SNAP_DEFAULTS, parsed);
    } else {
      state.snapTypes = Object.assign({}, _SNAP_DEFAULTS);
    }
  } catch (e) {
    state.snapTypes = Object.assign({}, _SNAP_DEFAULTS);
  }
}

function saveSnapTypesToLocalStorage() {
  try {
    localStorage.setItem(_SNAP_TYPES_KEY, JSON.stringify(state.snapTypes));
  } catch (e) { /* quota exceeded — silently ignore */ }
}

/* --------------------------------------------------------------------------
   Label helpers
--------------------------------------------------------------------------- */
function snapTypeLabel(name) {
  return { endpoint: 'Endpoint', midpoint: 'Midpoint', center: 'Center', intersection: 'Intersection', nearest: 'Nearest on Edge' }[name] || name;
}

function snapTypeChip(name) {
  var on = state.snapTypes && state.snapTypes[name];
  return (on ? '✓ ' : '   ') + snapTypeLabel(name);
}

/* --------------------------------------------------------------------------
   Core toggle
--------------------------------------------------------------------------- */
function toggleSnapType(name) {
  if (!state.snapTypes) return;
  state.snapTypes[name] = !state.snapTypes[name];
  saveSnapTypesToLocalStorage();
  state.snapHint = null;
  // Refresh any open snap sub-dd labels
  _refreshSnapMenuLabels();
  if (typeof draw === 'function') draw();
}

/* --------------------------------------------------------------------------
   Update snap sub-dd item text content after a toggle.
   Finds every .item[data-snap-type] inside the snap flyout and rewrites text.
--------------------------------------------------------------------------- */
function _refreshSnapMenuLabels() {
  var items = document.querySelectorAll('.item[data-snap-type]');
  items.forEach(function (el) {
    var stype = el.dataset.snapType;
    var shortcut = { endpoint: 'E', midpoint: 'M', center: 'C', intersection: null, nearest: null }[stype];
    var chip = snapTypeChip(stype);
    el.textContent = shortcut ? chip + ' (' + shortcut + ')' : chip;
  });
}

/* --------------------------------------------------------------------------
   Global wrappers — used by FLYOUT_GROUPS action strings.
--------------------------------------------------------------------------- */
window.toggleSnapTypeEndpoint     = function () { toggleSnapType('endpoint'); };
window.toggleSnapTypeMidpoint     = function () { toggleSnapType('midpoint'); };
window.toggleSnapTypeCenter       = function () { toggleSnapType('center'); };
window.toggleSnapTypeIntersection = function () { toggleSnapType('intersection'); };
window.toggleSnapTypeNearest      = function () { toggleSnapType('nearest'); };

/* --------------------------------------------------------------------------
   Keyboard shortcuts:  e/E → endpoint,  m/M → midpoint,  c/C → center.
   Intersection and Nearest-on-edge have NO keyboard shortcut (menu-only,
   same precedent — see cheatsheet.js, which only lists shortcuts that
   actually exist).
   Guard: skip if focus is inside INPUT/TEXTAREA/contentEditable, or a modal
   is open, or any modifier key (shift/ctrl/alt/meta) is held.
--------------------------------------------------------------------------- */
window.addEventListener('keydown', function (e) {
  // Only bare lowercase letters
  if (e.shiftKey || e.ctrlKey || e.altKey || e.metaKey) return;
  var key = e.key;
  if (key !== 'e' && key !== 'm' && key !== 'c') return;
  // Guard: active element is editable
  var ae = document.activeElement;
  if (ae) {
    var tag = ae.tagName;
    if (tag === 'INPUT' || tag === 'TEXTAREA') return;
    if (ae.isContentEditable) return;
  }
  // Guard: modal open
  if (typeof modalOpen === 'function' && modalOpen()) return;
  if (key === 'e') toggleSnapType('endpoint');
  else if (key === 'm') toggleSnapType('midpoint');
  else if (key === 'c') toggleSnapType('center');
});

/* --------------------------------------------------------------------------
   Init — called once on DOMContentLoaded.
   Merges persisted state over defaults; sets state.snapTypes if not yet set.
--------------------------------------------------------------------------- */
function initSnapTypes() {
  state.snapTypes = state.snapTypes || Object.assign({}, _SNAP_DEFAULTS);
  loadSnapTypesFromLocalStorage();
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initSnapTypes);
} else {
  initSnapTypes();
}
