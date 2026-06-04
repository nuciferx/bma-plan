/* ============================================================
   WIZ-AUTO — LWIZ-AUTO: auto-open Overview Setup wizard on PDF upload complete.
   Plain-globals module. No IIFE, no export, no bundler.
   Injected dynamically from page-folder-layers.js.

   Globals required (ui-lite.html):
     state, pageTags, openOv(), loadProto(), liteSetTag(), uploadPdf()

   Behavior:
   - Installs state.scaleStatus accessor (get/set) on state object (kept for compat).
   - Wraps uploadPdf to fire wizard when PDF upload completes (primary trigger).
   - scaleStatus='manual' remains as fallback trigger if wizard not yet fired.
   - Wraps loadProto to set __lwizAutoFired=true BEFORE body runs.
   - Wraps liteSetTag to lift hard-block when pageTags has ≥1 real tag.
   - Hard-block: ALL key/mouse/wheel/contextmenu events outside #ov-panel
     are stopped while __lwizAutoLockActive===true.
   ============================================================ */

window.__lwizAutoFired       = false;  // fired once per session
window.__lwizAutoSuppressed  = false;  // set by loadProto wrap
window.__lwizAutoLockActive  = false;  // hard-block guard active

// ---- internal storage for state.scaleStatus accessor ----
var _lwizScaleStatusVal = (typeof state !== 'undefined' && state._lwizScaleStatus) || 'unknown';

// ---- HUD block hint ---------------------------------------------------------
function _lwizShowBlockHint() {
  var panel = document.getElementById('ov-panel');
  if (!panel) return;
  var hint = document.getElementById('lwiz-hint');
  if (!hint) {
    hint = document.createElement('div');
    hint.id = 'lwiz-hint';
    hint.style.cssText =
      'position:absolute;top:8px;left:50%;transform:translateX(-50%);' +
      'background:#c84b11;color:#fff;font-size:12px;font-weight:600;' +
      'padding:6px 16px;border-radius:6px;z-index:9999;pointer-events:none;' +
      'transition:opacity .4s;white-space:nowrap;';
    panel.style.position = panel.style.position || 'relative';
    panel.appendChild(hint);
  }
  hint.textContent = 'ตั้งค่าหน้า (Page Setup) ให้เสร็จก่อน';
  hint.style.opacity = '1';
  clearTimeout(hint._lwizTimer);
  hint._lwizTimer = setTimeout(function() { hint.style.opacity = '0'; }, 2500);
}

// Keep old name as alias for backward compat
var _lwizShowHint = _lwizShowBlockHint;

// ---- hard-block guard -------------------------------------------------------
var _lwizBlockGuards = [];  // array of {event, fn} for removal

function _lwizInstallLock() {
  if (window.__lwizAutoLockActive) return;
  window.__lwizAutoLockActive = true;

  var BLOCKED_EVENTS = ['keydown', 'keypress', 'keyup', 'click', 'mousedown', 'mouseup', 'wheel', 'contextmenu'];

  BLOCKED_EVENTS.forEach(function(evtName) {
    var handler = function(e) {
      if (!window.__lwizAutoLockActive) return;
      var ov = document.getElementById('ov');
      // Only block when overlay is shown
      if (!ov || !ov.classList.contains('show')) return;
      var panel = document.getElementById('ov-panel');
      // Allow all events that target inside the wizard panel
      if (panel && panel.contains(e.target)) return;
      e.stopPropagation();
      e.stopImmediatePropagation();
      e.preventDefault();
      // Show hint only on keydown to avoid hint spam
      if (evtName === 'keydown') _lwizShowBlockHint();
    };
    document.addEventListener(evtName, handler, true);
    _lwizBlockGuards.push({event: evtName, fn: handler});
  });
}

function _lwizAutoLiftLock() {
  if (!window.__lwizAutoLockActive) return;
  window.__lwizAutoLockActive = false;
  _lwizBlockGuards.forEach(function(g) {
    document.removeEventListener(g.event, g.fn, true);
  });
  _lwizBlockGuards = [];
}

// ---- check tag count, lift lock if ≥1 real tag set -------------------------
function _lwizCheckLiftLock() {
  if (!window.__lwizAutoLockActive) return;
  if (typeof pageTags === 'undefined') return;
  var keys = Object.keys(pageTags);
  for (var i = 0; i < keys.length; i++) {
    var v = pageTags[keys[i]];
    if (v && v !== 'excluded') { _lwizAutoLiftLock(); return; }
  }
}

// ---- state.scaleStatus accessor (kept for compat + fallback trigger) --------
function _lwizInstallWatcher() {
  if (typeof state === 'undefined') return;
  if (Object.getOwnPropertyDescriptor(state, 'scaleStatus') &&
      typeof Object.getOwnPropertyDescriptor(state, 'scaleStatus').set === 'function') {
    return; // already installed
  }
  // Remove plain data property if present (e.g. state.scaleStatus = 'unknown' was set before us)
  delete state.scaleStatus;

  Object.defineProperty(state, 'scaleStatus', {
    configurable: true,
    enumerable: true,
    get: function() { return _lwizScaleStatusVal; },
    set: function(newVal) {
      var oldVal = _lwizScaleStatusVal;
      _lwizScaleStatusVal = newVal;
      // Fallback trigger: if upload trigger didn't fire yet, scaleStatus=manual still fires wizard
      if (oldVal !== 'manual' && newVal === 'manual' &&
          !window.__lwizAutoFired && !window.__lwizAutoSuppressed) {
        window.__lwizAutoFired = true;
        setTimeout(function() {
          if (typeof window.openOv === 'function') {
            window.openOv();
            _lwizInstallLock();
          }
        }, 0);
      }
    }
  });
}

// ---- primary trigger: wrap uploadPdf to fire wizard on upload complete ------
function _lwizWrapUploadPdf() {
  if (window.__lwizUploadWrapped) return;
  if (typeof uploadPdf !== 'function') return;
  window.__lwizUploadWrapped = true;
  var origUP = uploadPdf;
  uploadPdf = function(file) {
    // Reset fired flag on new upload so second PDF retriggers wizard
    window.__lwizAutoFired = false;
    window.__lwizAutoSuppressed = false;
    var result = origUP.apply(this, arguments);
    // origUP is async; we hook completion via a MutationObserver on caseId change
    // by polling after the async function settles.
    if (result && typeof result.then === 'function') {
      result.then(function() {
        // Upload completed — fire wizard if not suppressed
        setTimeout(function() {
          if (!window.__lwizAutoFired && !window.__lwizAutoSuppressed &&
              typeof caseId !== 'undefined' && caseId &&
              typeof pageCount !== 'undefined' && pageCount > 0) {
            window.__lwizAutoFired = true;
            if (typeof window.openOv === 'function') {
              window.openOv();
              _lwizInstallLock();
            }
          }
        }, 0);
      }).catch(function() { /* upload failed — do nothing */ });
    }
    return result;
  };
  // Copy own properties from original (e.g. introspection flags from other wrappers)
  try {
    var keys = Object.getOwnPropertyNames(origUP);
    for (var i = 0; i < keys.length; i++) {
      var k = keys[i];
      if (k === 'length' || k === 'name' || k === 'prototype' || k === 'arguments' || k === 'caller') continue;
      try { uploadPdf[k] = origUP[k]; } catch(_) {}
    }
  } catch(_) {}
}

// ---- wrap cal-ok to set scaleStatus='manual' after calib confirmed ----------
function _lwizWrapCalOk() {
  var btn = document.getElementById('cal-ok');
  if (!btn || btn.__lwizCalWrapped) return;
  var orig = btn.onclick;
  btn.onclick = function(e) {
    // call original first (it validates + sets PSpage().scale)
    if (orig) orig.call(this, e);
    // if scale was actually set (modal closed = success), flip scaleStatus
    var modal = document.getElementById('modal');
    if (modal && !modal.classList.contains('show')) {
      // original confirmed: scale is now set
      state.scaleStatus = 'manual';
    }
  };
  btn.__lwizCalWrapped = true;
}

// ---- wrap loadProto to suppress auto-fire -----------------------------------
function _lwizWrapLoadProto() {
  if (window.__lwizAutoWrapped) return;
  if (typeof loadProto !== 'function') return;
  window.__lwizAutoWrapped = true;
  var origLP = loadProto;
  loadProto = function(doc) {
    window.__lwizAutoFired = true;  // suppress wizard for any scale set after load
    origLP.apply(this, arguments);
  };
  // LWIZ-CFSS-WRAP-FIX: preserve introspection flags set by prior wrappers
  // (e.g. CFSS sets loadProto.__cfssWrapped=true). Copy own enumerable properties.
  try {
    var keys = Object.getOwnPropertyNames(origLP);
    for (var i = 0; i < keys.length; i++) {
      var k = keys[i];
      if (k === 'length' || k === 'name' || k === 'prototype' || k === 'arguments' || k === 'caller') continue;
      try { loadProto[k] = origLP[k]; } catch(_) {}
    }
  } catch(_) {}
  window.__lwizAutoWrappedFn = loadProto;  // for diagnostics
}

// ---- wrap liteSetTag to lift soft-force lock --------------------------------
function _lwizWrapLiteSetTag() {
  if (window.__lwizSetTagWrapped) return;
  if (typeof liteSetTag !== 'function') return;
  window.__lwizSetTagWrapped = true;
  var origST = liteSetTag;
  liteSetTag = function(n, val) {
    origST.apply(this, arguments);
    _lwizCheckLiftLock();
  };
  // LWIZ-CFSS-WRAP-FIX: preserve introspection flags set by prior wrappers
  // (same pattern as _lwizWrapLoadProto — copy own enumerable properties)
  try {
    var keys = Object.getOwnPropertyNames(origST);
    for (var i = 0; i < keys.length; i++) {
      var k = keys[i];
      if (k === 'length' || k === 'name' || k === 'prototype' || k === 'arguments' || k === 'caller') continue;
      try { liteSetTag[k] = origST[k]; } catch(_) {}
    }
  } catch(_) {}
}

// ---- bootstrap --------------------------------------------------------------
function _lwizBootstrap() {
  if (window.__lwizBootDone) return;
  window.__lwizBootDone = true;

  _lwizInstallWatcher();
  _lwizWrapCalOk();
  _lwizWrapLoadProto();
  _lwizWrapLiteSetTag();
  _lwizWrapUploadPdf();
}

// Dynamic injection: DOMContentLoaded may have already fired.
if (document.readyState === 'loading') {
  window.addEventListener('DOMContentLoaded', _lwizBootstrap);
} else {
  setTimeout(_lwizBootstrap, 0);
}
