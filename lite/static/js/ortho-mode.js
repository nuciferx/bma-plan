/* LORTHO-1: ortho-mode.js — sticky angle-lock toggle (Shift+O).
   Loaded after page-rotate.js, before menu-flyout.js.
   Declares globals: initOrtho, toggleOrtho, orthoMenuChip.
   Runtime-only — orthoOn is stored in localStorage, NOT .bmaplan. */

var _ORTHO_KEY = 'lite.orthoOn.v1';

/* --------------------------------------------------------------------------
   Label helper — used by initOrtho and toggleOrtho to refresh menu text.
--------------------------------------------------------------------------- */
function orthoMenuChip() {
  return state.orthoOn ? '✓ Ortho Mode' : '   Ortho Mode';
}

function _refreshOrthoMenuLabel() {
  var el = document.getElementById('mi-ortho');
  if (el) {
    var kEl = el.querySelector('.k');
    var kHtml = kEl ? kEl.outerHTML : '';
    el.textContent = orthoMenuChip();
    if (kHtml) el.insertAdjacentHTML('beforeend', kHtml);
  }
}

/* --------------------------------------------------------------------------
   Core toggle
--------------------------------------------------------------------------- */
function toggleOrtho() {
  state.orthoOn = !state.orthoOn;
  try {
    localStorage.setItem(_ORTHO_KEY, state.orthoOn ? '1' : '0');
  } catch (e) { /* quota exceeded — silently ignore */ }
  _refreshOrthoMenuLabel();
  if (typeof draw === 'function') draw();
}

/* --------------------------------------------------------------------------
   Keyboard shortcut: Shift+O toggles ortho mode.
   Guard: skip if focus is inside INPUT/TEXTAREA/contentEditable, or a modal
   is open. Plain 'o'/'O' without Shift is NOT handled here (reserved for
   future Opening tool).
--------------------------------------------------------------------------- */
window.addEventListener('keydown', function (e) {
  // Must have Shift + o/O, no other modifiers
  if (!e.shiftKey || e.ctrlKey || e.altKey || e.metaKey) return;
  if (e.key !== 'o' && e.key !== 'O') return;
  // Guard: active element is editable
  var ae = document.activeElement;
  if (ae) {
    var tag = ae.tagName;
    if (tag === 'INPUT' || tag === 'TEXTAREA') return;
    if (ae.isContentEditable) return;
  }
  // Guard: modal open
  if (typeof modalOpen === 'function' && modalOpen()) return;
  toggleOrtho();
});

/* --------------------------------------------------------------------------
   Init — called once on DOMContentLoaded.
   Loads persisted state and wires the menu item click handler.
--------------------------------------------------------------------------- */
function initOrtho() {
  // Load from localStorage (default false)
  try {
    state.orthoOn = localStorage.getItem(_ORTHO_KEY) === '1';
  } catch (e) {
    state.orthoOn = false;
  }
  // Wire menu item
  var el = document.getElementById('mi-ortho');
  if (el) {
    el.onclick = function () { toggleOrtho(); };
  }
  _refreshOrthoMenuLabel();
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initOrtho);
} else {
  initOrtho();
}
