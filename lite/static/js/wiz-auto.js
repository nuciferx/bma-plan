/* ============================================================
   WIZ-AUTO — LWIZ-AUTO: auto-open Overview Setup wizard on first scale set.
   Plain-globals module. No IIFE, no export, no bundler.
   Injected dynamically from page-folder-layers.js.

   Globals required (ui-lite.html):
     state, pageTags, openOv(), loadProto(), liteSetTag()

   Behavior:
   - Installs state.scaleStatus accessor (get/set) on state object.
   - Wraps cal-ok button onclick to set state.scaleStatus='manual'.
   - Wraps loadProto to set __lwizAutoFired=true BEFORE body runs.
   - Wraps liteSetTag to lift soft-force guard when pageTags has ≥1 entry.
   - Soft-force: blocks Esc + outside-click on #ov until 1 tag is set.
   ============================================================ */

window.__lwizAutoFired       = false;  // fired once per session
window.__lwizAutoSuppressed  = false;  // set by loadProto wrap
window.__lwizAutoLockActive  = false;  // soft-force guard active

// ---- internal storage for state.scaleStatus accessor ----
var _lwizScaleStatusVal = (typeof state !== 'undefined' && state._lwizScaleStatus) || 'unknown';

// ---- HUD hint ----------------------------------------------------------------
function _lwizShowHint() {
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
  hint.textContent = 'เลือก tag อย่างน้อย 1 หน้าก่อนปิด';
  hint.style.opacity = '1';
  clearTimeout(hint._lwizTimer);
  hint._lwizTimer = setTimeout(function() { hint.style.opacity = '0'; }, 2500);
}

// ---- soft-force guard -------------------------------------------------------
var _lwizEscGuard = null;
var _lwizClickGuard = null;

function _lwizInstallLock() {
  if (window.__lwizAutoLockActive) return;
  window.__lwizAutoLockActive = true;

  _lwizEscGuard = function(e) {
    if (e.key !== 'Escape') return;
    var ov = document.getElementById('ov');
    if (!ov || (ov.style.display === 'none' || !ov.classList.contains('show'))) return;
    if (!window.__lwizAutoLockActive) return;
    e.stopPropagation();
    e.preventDefault();
    _lwizShowHint();
  };

  _lwizClickGuard = function(e) {
    if (!window.__lwizAutoLockActive) return;
    var ov = document.getElementById('ov');
    if (!ov || (ov.style.display === 'none' && !ov.classList.contains('show'))) return;
    var panel = document.getElementById('ov-panel');
    if (!panel) return;
    // Block clicks on the overlay backdrop (outside the panel)
    if (!panel.contains(e.target) && ov.contains(e.target)) {
      e.stopPropagation();
      e.preventDefault();
      _lwizShowHint();
    }
  };

  document.addEventListener('keydown', _lwizEscGuard, true);
  document.getElementById('ov') &&
    document.getElementById('ov').addEventListener('click', _lwizClickGuard, true);
}

function _lwizAutoLiftLock() {
  if (!window.__lwizAutoLockActive) return;
  window.__lwizAutoLockActive = false;
  if (_lwizEscGuard) {
    document.removeEventListener('keydown', _lwizEscGuard, true);
    _lwizEscGuard = null;
  }
  if (_lwizClickGuard) {
    var ov = document.getElementById('ov');
    if (ov) ov.removeEventListener('click', _lwizClickGuard, true);
    _lwizClickGuard = null;
  }
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

// ---- state.scaleStatus accessor ---------------------------------------------
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
}

// Dynamic injection: DOMContentLoaded may have already fired.
if (document.readyState === 'loading') {
  window.addEventListener('DOMContentLoaded', _lwizBootstrap);
} else {
  setTimeout(_lwizBootstrap, 0);
}
