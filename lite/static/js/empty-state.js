/* empty-state.js — COSMETIC-3 (UX batch3): dim pre-open empty-state hint on the
   layer panel (#picker) so it does not look "live" before any PDF is open. The
   canvas itself already shows the empty hub (#empty). Pure display — removed on
   the first successful open (draw() runs after loadPage → updateEmptyState hides).
   Global: updateEmptyState. Plain-globals module, no IIFE export/bundler. */
(function () {
  var HINT = 'เปิดไฟล์ PDF เพื่อเริ่ม (Ctrl+O หรือลากไฟล์มาวาง)';

  var style = document.createElement('style');
  style.textContent = [
    '#ls-empty-state{position:absolute;inset:0;z-index:6;display:flex;',
    '  align-items:center;justify-content:center;text-align:center;padding:16px;',
    '  background:rgba(20,24,32,.88);border-radius:inherit;cursor:default;',
    '  color:var(--muted,#8b97a8);font-size:12px;line-height:1.6;}',
  ].join('');
  document.head.appendChild(style);

  function _docOpen() {
    if (typeof PageRenderer !== 'undefined' && PageRenderer.ready && PageRenderer.ready()) return true;
    if (typeof pdfDoc !== 'undefined' && !!pdfDoc) return true;
    return false;
  }

  function _ensure() {
    var picker = document.getElementById('picker');
    if (!picker) return null;
    var el = document.getElementById('ls-empty-state');
    if (!el) {
      var cs = window.getComputedStyle(picker);
      if (cs && cs.position === 'static') picker.style.position = 'relative';
      el = document.createElement('div');
      el.id = 'ls-empty-state';
      el.textContent = HINT;
      picker.appendChild(el);
    }
    return el;
  }

  function updateEmptyState() {
    var el = _ensure();
    if (!el) return;
    el.style.display = _docOpen() ? 'none' : 'flex';
  }
  window.updateEmptyState = updateEmptyState;

  /* Wrap draw() so the overlay auto-hides on the first open (draw runs after
     loadPage). Guard flag prevents double-wrapping across re-inits. */
  function _wrapDraw() {
    if (typeof window.draw === 'function' && !window.draw.__lsEmptyWrapped) {
      var orig = window.draw;
      window.draw = function () {
        var r = orig.apply(this, arguments);
        try { updateEmptyState(); } catch (_) {}
        return r;
      };
      window.draw.__lsEmptyWrapped = true;
    }
  }

  function _init() { _ensure(); updateEmptyState(); _wrapDraw(); }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', _init);
  else _init();
})();
