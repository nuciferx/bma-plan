/*
 * page-manager-ui.js — Lite page-management UI overlay (INV-2026-05-29-LPM Slice 5).
 *
 * Decorates the #ov-grid built by openOv() with:
 *   - Drag-to-reorder thumbnails (HTML5 drag events, plain DOM)
 *   - Per-tile 🗑 (delete) + ⧉ (duplicate) action buttons
 *   - "Apply page changes" bar (visible only when pageMgr.pending.length > 0)
 *   - "↶ Undo" button (calls pageMgr.undo() + re-renders grid)
 *   - "＋ Merge PDF" button + hidden file input (disabled when pending exist)
 *
 * ARCHITECTURE:
 *   openOv() in ui-lite.html calls pmUiDecorate() at the end of its grid-build
 *   via ONE added line: if(typeof pmUiDecorate==='function') pmUiDecorate();
 *   All state lives here; pageMgr is the shared global from page-manager.js.
 *
 * Hard constraints respected:
 *   - NEVER touches measure-engine.js, RS, pdfToC/cToPdf, page-manager.js, server_lite.py
 *   - No new fields added to .bmaplan (no schema change)
 *   - overview-setup.js untouched (the #ov 3-tab WIZARD is orthogonal to this)
 *   - Plain global functions, no IIFE, no bundler
 */

/* ============================================================
   Internal state
   ============================================================ */
var _pmui_dragSrcIdx = null;   // 0-based display index being dragged

/* ============================================================
   Internal helpers
   ============================================================ */

/** Re-render the #ov-grid from pageMgr state WITHOUT calling openOv() again.
 *  Keeps all the new UI intact (action bar, etc.) and runs pmUiDecorate().
 */
function _pmuiRefreshGrid() {
  if (!pageMgr) return;
  var g = document.getElementById('ov-grid');
  if (!g) return;

  var html = '';
  var count = pageMgr.count();
  for (var n = 1; n <= count; n++) {
    var sn = pageMgr.serverNum(n);
    var imgSrc = sn ? api('/thumb/' + sn) : '';
    var id = pageMgr.idAt(n);
    // meta from globals (still the authoritative source until _pmCommit is called)
    // Use pageMgr model for display:
    var isCur = (n === curPage);
    // Build thumb
    html += '<div class="thumb pmui-thumb' + (isCur ? ' cur' : '') + '" draggable="true"' +
            ' data-pmui-idx="' + (n - 1) + '">' +
            (imgSrc
              ? '<img loading="lazy" src="' + imgSrc + '">'
              : '<div class="pmui-pending">⏳ pending</div>') +
            '<span class="pmui-label">หน้า ' + n + '</span>' +
            '<div class="pmui-actions">' +
            (count > 1 ? '<button class="pmui-btn pmui-del" data-pmui-idx="' + (n - 1) + '" title="ลบหน้านี้">🗑</button>' : '') +
            '<button class="pmui-btn pmui-dup" data-pmui-idx="' + (n - 1) + '" title="ทำสำเนาหน้านี้">⧉</button>' +
            '</div></div>';
  }
  g.innerHTML = html;
  pmUiDecorate();   // wire the freshly-built grid
}

/** Build/update the action bar below the grid. */
function _pmuiBuildActionBar() {
  var existing = document.getElementById('pmui-bar');
  if (existing) existing.remove();

  var ovEl = document.getElementById('ov');
  if (!ovEl || !pageMgr) return;

  var hasPending = pageMgr.pending.length > 0;

  var bar = document.createElement('div');
  bar.id = 'pmui-bar';
  bar.style.cssText = 'position:sticky;bottom:0;left:0;right:0;' +
    'background:rgba(22,26,34,.97);border-top:1px solid var(--line);' +
    'padding:8px 14px;display:flex;align-items:center;gap:10px;z-index:10;' +
    'flex-wrap:wrap;font-size:13px;';

  // Apply button (only when pending)
  var applyBtn = document.createElement('button');
  applyBtn.id = 'pmui-apply';
  applyBtn.textContent = 'Apply page changes (' + pageMgr.pending.length + ')';
  applyBtn.style.cssText = 'background:var(--accent);color:#fff;border:0;border-radius:7px;' +
    'padding:6px 14px;cursor:pointer;font-size:13px;' +
    (hasPending ? '' : 'display:none;');
  applyBtn.onclick = _pmuiApplyChanges;
  bar.appendChild(applyBtn);

  // Undo button (only when undo stack has entries)
  if (pageMgr.undoStack && pageMgr.undoStack.length > 0) {
    var undoBtn = document.createElement('button');
    undoBtn.id = 'pmui-undo';
    undoBtn.textContent = '↶ Undo';
    undoBtn.style.cssText = 'background:#222a37;color:var(--ink);border:1px solid var(--line);' +
      'border-radius:7px;padding:6px 12px;cursor:pointer;font-size:13px;';
    undoBtn.onclick = function () {
      if (pageMgr.undo()) _pmuiRefreshGrid();
      _pmuiBuildActionBar();
    };
    bar.appendChild(undoBtn);
  }

  // Spacer
  var sp = document.createElement('span');
  sp.style.flex = '1';
  bar.appendChild(sp);

  // Merge PDF button
  var mergeBtn = document.createElement('button');
  mergeBtn.id = 'pmui-merge';
  mergeBtn.textContent = '＋ Merge PDF';
  mergeBtn.title = hasPending ? 'Apply changes first before merging' : 'Append pages from another PDF';
  mergeBtn.disabled = hasPending;
  mergeBtn.style.cssText = 'background:#222a37;color:' + (hasPending ? 'var(--muted)' : 'var(--ink)') + ';' +
    'border:1px solid var(--line);border-radius:7px;padding:6px 12px;cursor:' +
    (hasPending ? 'not-allowed' : 'pointer') + ';font-size:13px;';
  mergeBtn.onclick = function () {
    if (pageMgr.pending.length > 0) {
      alert('กรุณา Apply page changes ก่อนแล้วค่อย Merge PDF');
      return;
    }
    document.getElementById('pmui-file-input').click();
  };
  bar.appendChild(mergeBtn);

  // Hidden file input for merge
  var fi = document.getElementById('pmui-file-input');
  if (!fi) {
    fi = document.createElement('input');
    fi.type = 'file';
    fi.id = 'pmui-file-input';
    fi.accept = '.pdf,application/pdf';
    fi.style.display = 'none';
    fi.onchange = _pmuiMergePdf;
    document.body.appendChild(fi);
  }

  var grid = document.getElementById('ov-grid');
  if (grid) {
    grid.parentNode.insertBefore(bar, grid.nextSibling);
  } else {
    ovEl.appendChild(bar);
  }
}

/* ============================================================
   Apply changes (flush to server)
   ============================================================ */
async function _pmuiApplyChanges() {
  if (!pageMgr || !caseId) return;
  if (pageMgr.pending.length === 0) return;

  // Check for merged pages (serverNum===null) — not supported by /apply-page-mutations
  // V1: if any merged (non-dup, true merge) page exists, tell user to use Merge PDF first.
  // Duplicates are fine — pageMgr.serverNum() returns the source's server page for dups.
  var order = [];
  var hasMergedPage = false;
  for (var n = 1; n <= pageMgr.count(); n++) {
    var sn = pageMgr.serverNum(n);
    if (sn === null) {
      // Could be a merged page (srcServer===null). Check srcServer directly.
      var id = pageMgr.idAt(n);
      if (pageMgr.srcServer[id] === null || pageMgr.srcServer[id] === undefined) {
        hasMergedPage = true;
        break;
      }
    }
    order.push(sn);
  }

  if (hasMergedPage) {
    alert('มีหน้าที่ Merge ค้างอยู่ — กรุณา Merge PDF ก่อนแล้วกด Apply');
    return;
  }

  // Disable button while processing
  var applyBtn = document.getElementById('pmui-apply');
  if (applyBtn) { applyBtn.disabled = true; applyBtn.textContent = 'กำลังบันทึก…'; }

  try {
    var resp = await fetch('/apply-page-mutations', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ case_id: caseId, order: order })
    });
    var data = await resp.json();
    if (!data.ok) throw new Error(data.error || 'server error');

    // Server applied OK — commit model
    pageMgr.applyFlush();
    pageCount = data.new_count;
    _pmCommit();      // sync pageMgr → PS / pageTags / etc. globals + reseed folders

    // Refresh overview and canvas
    openOv();
    loadPage(1);
  } catch (err) {
    // Keep pending, restore button, let user retry
    if (applyBtn) {
      applyBtn.disabled = false;
      applyBtn.textContent = 'Apply page changes (' + pageMgr.pending.length + ')';
    }
    alert('Apply ล้มเหลว: ' + err.message + '\nยังคงสถานะเดิม — กด Apply อีกครั้งเพื่อลองใหม่');
  }
}

/* ============================================================
   Merge PDF (append pages from another file)
   ============================================================ */
async function _pmuiMergePdf(evt) {
  var file = evt.target.files && evt.target.files[0];
  evt.target.value = '';   // reset so same file can be picked again
  if (!file || !caseId) return;

  if (pageMgr && pageMgr.pending.length > 0) {
    alert('กรุณา Apply page changes ก่อนแล้วค่อย Merge PDF');
    return;
  }

  var mergeBtn = document.getElementById('pmui-merge');
  if (mergeBtn) { mergeBtn.disabled = true; mergeBtn.textContent = 'กำลัง Merge…'; }

  try {
    var fd = new FormData();
    fd.append('case_id', caseId);
    fd.append('file', file);
    var resp = await fetch('/merge-pages', { method: 'POST', body: fd });
    var data = await resp.json();
    if (!data.ok) throw new Error(data.error || 'server error');

    var added = data.added_count;
    pageCount = data.new_count;

    // Model: append client ids for the merged pages then applyFlush so they
    // get real originNums (the server PDF already has them appended).
    pageMgr.merge(added);
    pageMgr.applyFlush();
    _pmCommit();

    openOv();
    loadPage(curPage);
  } catch (err) {
    alert('Merge ล้มเหลว: ' + err.message);
  } finally {
    if (mergeBtn) { mergeBtn.disabled = false; mergeBtn.textContent = '＋ Merge PDF'; }
  }
}

/* ============================================================
   pmUiDecorate() — PUBLIC entry point.
   Called by openOv() via:  if(typeof pmUiDecorate==='function') pmUiDecorate();
   ============================================================ */
function pmUiDecorate() {
  var g = document.getElementById('ov-grid');
  if (!g || !pageMgr) return;

  /* ---- Inject CSS once ---- */
  if (!document.getElementById('pmui-style')) {
    var s = document.createElement('style');
    s.id = 'pmui-style';
    s.textContent = [
      '.pmui-thumb{position:relative;cursor:grab;user-select:none;}',
      '.pmui-thumb.drag-over{outline:2px dashed var(--accent);opacity:.8;}',
      '.pmui-thumb.dragging{opacity:.4;}',
      '.pmui-actions{position:absolute;top:4px;right:4px;display:flex;gap:3px;opacity:0;transition:opacity .15s;}',
      '.pmui-thumb:hover .pmui-actions{opacity:1;}',
      '.pmui-btn{background:rgba(0,0,0,.7);border:1px solid var(--line);color:var(--ink);',
      '  border-radius:5px;padding:2px 5px;font-size:12px;cursor:pointer;line-height:1.4;}',
      '.pmui-btn:hover{background:var(--accent);}',
      '.pmui-label{display:block;font-size:11px;color:var(--muted);margin-top:3px;text-align:center;}',
      '.pmui-pending{width:100%;height:80px;display:flex;align-items:center;justify-content:center;',
      '  color:var(--muted);font-size:12px;background:rgba(255,255,255,.04);border-radius:6px;}',
    ].join('');
    document.head.appendChild(s);
  }

  /* ---- Wire drag events on each .pmui-thumb ---- */
  var thumbs = g.querySelectorAll('.pmui-thumb');
  thumbs.forEach(function (thumb) {
    var idx = parseInt(thumb.getAttribute('data-pmui-idx'), 10);

    /* Navigate on body click (not on action buttons) */
    thumb.onclick = function (e) {
      if (e.target.classList.contains('pmui-btn')) return;
      var displayPage = idx + 1;
      loadPage(displayPage);
      closeOverlays();
    };

    /* Drag source */
    thumb.addEventListener('dragstart', function (e) {
      _pmui_dragSrcIdx = idx;
      thumb.classList.add('dragging');
      e.dataTransfer.effectAllowed = 'move';
    });
    thumb.addEventListener('dragend', function () {
      thumb.classList.remove('dragging');
      g.querySelectorAll('.pmui-thumb').forEach(function (t) {
        t.classList.remove('drag-over');
      });
      _pmui_dragSrcIdx = null;
    });

    /* Drag target */
    thumb.addEventListener('dragover', function (e) {
      e.preventDefault();
      e.dataTransfer.dropEffect = 'move';
    });
    thumb.addEventListener('dragenter', function () {
      if (_pmui_dragSrcIdx !== null && _pmui_dragSrcIdx !== idx) {
        thumb.classList.add('drag-over');
      }
    });
    thumb.addEventListener('dragleave', function () {
      thumb.classList.remove('drag-over');
    });
    thumb.addEventListener('drop', function (e) {
      e.preventDefault();
      thumb.classList.remove('drag-over');
      if (_pmui_dragSrcIdx === null || _pmui_dragSrcIdx === idx) return;
      pageMgr.reorder(_pmui_dragSrcIdx, idx);
      _pmui_dragSrcIdx = null;
      _pmuiRefreshGrid();
      _pmuiBuildActionBar();
    });
  });

  /* ---- Wire delete buttons ---- */
  g.querySelectorAll('.pmui-del').forEach(function (btn) {
    btn.addEventListener('click', function (e) {
      e.stopPropagation();
      var idx = parseInt(btn.getAttribute('data-pmui-idx'), 10);
      if (pageMgr.count() <= 1) return;   // guard: refuse last page
      if (!confirm('ลบหน้า ' + (idx + 1) + '?')) return;
      pageMgr.del(idx);
      _pmuiRefreshGrid();
      _pmuiBuildActionBar();
    });
  });

  /* ---- Wire duplicate buttons ---- */
  g.querySelectorAll('.pmui-dup').forEach(function (btn) {
    btn.addEventListener('click', function (e) {
      e.stopPropagation();
      var idx = parseInt(btn.getAttribute('data-pmui-idx'), 10);
      pageMgr.duplicate(idx);
      _pmuiRefreshGrid();
      _pmuiBuildActionBar();
    });
  });

  /* ---- Build (or refresh) the action bar ---- */
  _pmuiBuildActionBar();
}
