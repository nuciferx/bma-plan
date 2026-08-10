/* ============================================================
   WIZ-AUTO — compat shim for the Overview Setup wizard.
   Plain-globals module. No IIFE, no export, no bundler.
   Injected dynamically from page-folder-layers.js.

   HISTORY: this file used to auto-open the wizard on PDF upload / first
   scale commit AND enforce a document-wide keyboard+mouse hard lock until
   at least one page was tagged (BUG-20260526-lite-force-setup).

   RETIRED (page-manager-redesign approach D — docs/invent/
   page-manager-redesign.md, GO 2026-08-10, Decision note): "ปลด wizard
   เด้งอัตโนมัติ + hard-lock ตอนเปิดไฟล์ (แทนด้วย JIT banner)". Auto-open
   and the hard lock are now STRUCTURALLY GONE — not patched around — so
   there is no more auto-open trigger to accidentally swallow Shift+F12
   (BUG-20260810). Per-page measure discipline is owned by tag-jit.js's
   JIT banner instead: arming a measure tool on an untagged page shows a
   1-tap banner right there on the canvas, never a document-wide lock.
   The wizard itself (⇧F12 / F12 / btn-ov, wired in ui-lite.html /
   page-manager-ui.js / overview-setup.js — none of which this file
   touches) remains fully usable, just opened MANUALLY, never forced.

   What stays here (compat only — see each function's comment):
     - state.scaleStatus get/set accessor: no consumer left in
       ui-lite.html, kept only so external/legacy reads don't throw.
     - window.__lwizAutoLockActive (declared false): overview-grid.js
       still branches on it for its dblclick-guard path
       (locked by test_wiz_followup.py); only test harnesses simulating
       the OLD lock set it true now — nothing in this file does anymore.
     - _lwizShowBlockHint() / _lwizShowHint alias: still called by
       overview-grid.js's __lwizAutoLockActive branch above.
     - _lwizWrapCalOk(): keeps state.scaleStatus in sync after a
       successful calibration commit (compat bookkeeping only — nothing
       reads it to auto-open anything anymore).

   Removed (approach D, slice 3 — page-manager-redesign):
     - _lwizWrapUploadPdf() / the auto-open-on-upload trigger
     - the scaleStatus setter's auto-open-on-first-scale fallback trigger
     - _lwizInstallLock() / _lwizAutoLiftLock() / _lwizCheckLiftLock() /
       the global-capture keydown+keypress+keyup+click+mousedown+mouseup+
       wheel+contextmenu hard-block listeners
     - _lwizWrapLiteSetTag() (existed only to lift the removed lock)
     - _lwizWrapLoadProto() / window.__lwizAutoFired /
       window.__lwizAutoSuppressed bookkeeping (existed only to stop the
       removed triggers from double-firing)

   Globals required (ui-lite.html): state, #cal-ok button
   ============================================================ */

// Legacy flag — kept because overview-grid.js still branches on it
// (test_wiz_followup.py locks that branch). Only test harnesses set it
// true now; nothing in this file installs an automatic lock anymore.
window.__lwizAutoLockActive  = false;

// ---- internal storage for state.scaleStatus accessor (compat only) ----
var _lwizScaleStatusVal = (typeof state !== 'undefined' && state._lwizScaleStatus) || 'unknown';

// ---- HUD block hint — still called by overview-grid.js's
//      __lwizAutoLockActive branch when a test simulates the old lock ----
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

// ---- state.scaleStatus accessor (compat only — the setter no longer
//      triggers anything; nothing in ui-lite.html reads this value) ----
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
    set: function(newVal) { _lwizScaleStatusVal = newVal; }
  });
}

// ---- wrap cal-ok to keep scaleStatus in sync after calib confirmed
//      (compat bookkeeping only — see file header) ----
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

// ---- bootstrap --------------------------------------------------------------
function _lwizBootstrap() {
  if (window.__lwizBootDone) return;
  window.__lwizBootDone = true;

  _lwizInstallWatcher();
  _lwizWrapCalOk();
}

// Dynamic injection: DOMContentLoaded may have already fired.
if (document.readyState === 'loading') {
  window.addEventListener('DOMContentLoaded', _lwizBootstrap);
} else {
  setTimeout(_lwizBootstrap, 0);
}
