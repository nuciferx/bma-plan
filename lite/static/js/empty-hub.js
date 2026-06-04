/*
 * empty-hub.js — LEMPTY-1: empty-state hub for BMA-Plan Lite.
 * Globals: renderEmptyHub, renderRecentList, hideEmptyHub, showEmptyHubIfEmpty, handlePdfFile
 * Loaded as plain global script before inline script closes; no IIFE, no module.
 */

(function () {
  /* Inject hub styles into <head> — avoids editing ui-lite.html's style block. */
  var style = document.createElement('style');
  style.textContent = [
    '.empty-hub{display:flex;flex-direction:column;align-items:center;justify-content:center;',
    '  gap:18px;padding:32px 24px;max-width:480px;width:100%;text-align:center;}',
    '.empty-hub h2{font-size:24px;font-weight:700;color:var(--ink);letter-spacing:-.3px;}',
    '.empty-hub .tagline{font-size:14px;color:var(--muted);line-height:1.6;}',
    '.hub-actions{display:flex;flex-direction:column;gap:10px;width:100%;max-width:320px;}',
    '.hub-btn{border:0;border-radius:8px;padding:11px 20px;font-size:14px;',
    '  font-family:inherit;cursor:pointer;transition:opacity .15s;}',
    '.hub-btn.primary{background:var(--accent);color:#fff;}',
    '.hub-btn.ghost{background:transparent;border:1px solid var(--line);color:var(--ink);}',
    '.hub-btn:hover{opacity:.85;}',
    '.hub-recent{width:100%;max-width:320px;font-size:12px;color:var(--muted);text-align:left;}',
    '.hub-recent .hub-recent-label{margin-bottom:6px;font-size:11px;text-transform:uppercase;',
    '  letter-spacing:.5px;}',
    '.hub-recent ul{list-style:none;margin:0;padding:0;}',
    '.hub-recent li{padding:4px 0;border-bottom:1px solid var(--line);white-space:nowrap;',
    '  overflow:hidden;text-overflow:ellipsis;}',
    '.hub-recent li:last-child{border-bottom:0;}',
    '.hub-dragdrop-hint{font-size:12px;color:var(--muted);margin-top:4px;}',
  ].join('');
  document.head.appendChild(style);

  /* ---- public functions ---- */

  function renderRecentList() {
    var el = document.getElementById('hub-recent');
    if (!el) return;
    var raw = localStorage.getItem('bmaPlan.recentProjects.v1');
    if (!raw) { el.innerHTML = ''; return; }
    var list;
    try { list = JSON.parse(raw); } catch (_) { el.innerHTML = ''; return; }
    if (!Array.isArray(list) || list.length === 0) { el.innerHTML = ''; return; }
    var items = list.slice(0, 5);
    var html = '<div class="hub-recent-label">ไฟล์ล่าสุด:</div><ul>';
    items.forEach(function (name) {
      html += '<li title="' + _esc(name) + '">' + _esc(name) + '</li>';
    });
    html += '</ul>';
    el.innerHTML = html;
  }

  function renderEmptyHub() {
    var container = document.querySelector('.empty');
    if (!container) return;
    container.innerHTML = [
      '<div class="empty-hub">',
      '  <h2>BMA-Plan Lite</h2>',
      '  <p class="tagline">วัดพื้นที่จาก PDF แบบเร็ว ๆ — มาเริ่มกัน</p>',
      '  <div class="hub-actions">',
      '    <button class="hub-btn primary" id="hub-open-pdf">เปิดไฟล์ PDF…</button>',
      '    <button class="hub-btn ghost" id="hub-open-project">เปิดโปรเจกต์ .bmaplan</button>',
      '  </div>',
      '  <div class="hub-recent" id="hub-recent"></div>',
      '  <div class="hub-dragdrop-hint">หรือลาก PDF มาวางตรงนี้ก็ได้</div>',
      '</div>',
    ].join('');

    /* Wire buttons */
    var btnPdf = document.getElementById('hub-open-pdf');
    if (btnPdf) {
      btnPdf.addEventListener('click', function () {
        var inp = document.getElementById('file-pdf');
        if (inp) inp.click();
      });
    }
    var btnProj = document.getElementById('hub-open-project');
    if (btnProj) {
      btnProj.addEventListener('click', function () {
        var inp = document.getElementById('file-bma');
        if (inp) inp.click();
      });
    }

    renderRecentList();
  }

  function hideEmptyHub() {
    var el = document.querySelector('.empty');
    if (el) el.style.display = 'none';
  }

  function showEmptyHubIfEmpty() {
    /* PageRenderer.ready() is the page-render predicate from page-renderer.js */
    var el = document.querySelector('.empty');
    if (!el) return;
    if (typeof PageRenderer !== 'undefined' && PageRenderer.ready && PageRenderer.ready()) {
      el.style.display = 'none';
    } else {
      el.style.display = '';
      renderEmptyHub();
      renderRecentList();
    }
  }

  function handlePdfFile(file) {
    /* uploadPdf is the existing function in ui-lite.html that handles a File object */
    if (typeof uploadPdf === 'function') uploadPdf(file);
  }

  /* ---- drag-drop wiring ---- */
  function _wireDragDrop(container) {
    container.addEventListener('dragover', function (e) {
      e.preventDefault();
    });
    container.addEventListener('drop', function (e) {
      e.preventDefault();
      var f = e.dataTransfer && e.dataTransfer.files && e.dataTransfer.files[0];
      if (!f) return;
      var isPdf = f.type === 'application/pdf' || /\.pdf$/i.test(f.name);
      /* Call via window so tests can stub window.handlePdfFile. */
      if (isPdf) window.handlePdfFile(f);
    });
  }

  /* ---- HTML escape helper ---- */
  function _esc(s) {
    return String(s)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  /* ---- init ---- */
  function _initEmptyHub() {
    var container = document.querySelector('.empty');
    if (!container) return;
    renderEmptyHub();
    _wireDragDrop(container);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', _initEmptyHub);
  } else {
    _initEmptyHub();
  }

  /* Expose globals */
  window.renderEmptyHub = renderEmptyHub;
  window.renderRecentList = renderRecentList;
  window.hideEmptyHub = hideEmptyHub;
  window.showEmptyHubIfEmpty = showEmptyHubIfEmpty;
  window.handlePdfFile = handlePdfFile;
})();
