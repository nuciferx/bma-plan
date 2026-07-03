/* page-scan-badge.js — COSMETIC-4 (UX batch3): persistent per-page HUD badge for
   scanned pages (PageRenderer.isScanned) or raster server-render fallback. Follows
   the current page (re-evaluated every draw); hidden on pages where neither applies.
   Display-only — reads PageRenderer/curImg state, never touches render math or
   overlay registration. Global: updateScanBadge. Plain-globals module. */
(function () {
  var style = document.createElement('style');
  style.textContent = [
    '#scan-badge{position:absolute;top:10px;right:10px;z-index:7;display:none;',
    '  padding:4px 9px;border-radius:6px;font-size:11px;line-height:1.4;',
    '  background:rgba(40,30,10,.92);border:1px solid #6b5a2a;color:#ffd479;',
    '  pointer-events:none;white-space:nowrap;box-shadow:0 2px 8px rgba(0,0,0,.4);}',
    'body.focus #scan-badge{display:none !important;}',
  ].join('');
  document.head.appendChild(style);

  function _badge() {
    var el = document.getElementById('scan-badge');
    if (!el) {
      var stage = document.getElementById('stage');
      if (!stage) return null;
      el = document.createElement('div');
      el.id = 'scan-badge';
      stage.appendChild(el);
    }
    return el;
  }

  function _mode() {
    /* Raster fallback is doc-global: pdf.js unavailable → every page renders from
       the server JPEG held in curImg. Detect via the same predicate _drawImage uses. */
    if (typeof pdfDoc !== 'undefined' && !pdfDoc &&
        typeof HTMLImageElement !== 'undefined' &&
        typeof curImg !== 'undefined' && curImg instanceof HTMLImageElement) return 'fallback';
    /* Scanned is per-page. */
    try {
      if (typeof PageRenderer !== 'undefined' && PageRenderer.isScanned &&
          typeof curPage !== 'undefined' && PageRenderer.isScanned(curPage)) return 'scanned';
    } catch (_) {}
    return null;
  }

  function updateScanBadge() {
    var el = _badge();
    if (!el) return;
    var m = _mode();
    if (m === 'fallback') { el.textContent = 'โหมดสำรอง (เซิร์ฟเวอร์เรนเดอร์)'; el.style.display = 'block'; }
    else if (m === 'scanned') { el.textContent = 'สแกน — ความคมชัดจำกัด'; el.style.display = 'block'; }
    else { el.style.display = 'none'; }
  }
  window.updateScanBadge = updateScanBadge;

  function _wrapDraw() {
    if (typeof window.draw === 'function' && !window.draw.__scanBadgeWrapped) {
      var orig = window.draw;
      window.draw = function () {
        var r = orig.apply(this, arguments);
        try { updateScanBadge(); } catch (_) {}
        return r;
      };
      window.draw.__scanBadgeWrapped = true;
    }
  }

  function _init() { _badge(); updateScanBadge(); _wrapDraw(); }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', _init);
  else _init();
})();
