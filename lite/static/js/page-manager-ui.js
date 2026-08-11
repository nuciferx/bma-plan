/*
 * page-manager-ui.js — Lite page-management UI overlay (INV-2026-05-29-LPM).
 *
 * ARCHITECTURE (v2 — self-contained overlay):
 *   pmOpenManager() — public entry, builds (once) and shows its OWN overlay
 *   appended to document.body, id="pm-overlay".  Does NOT touch #ov or the
 *   LOVS wizard (overview-setup.js).  Grid is rendered into #pm-grid.
 *
 *   Trigger: Shift+F12  (self-registered keydown listener in this file).
 *   Also exposed as window.pmOpenManager for menu items.
 *
 *   pmUiDecorate() is kept as a no-op alias (was the old openOv hook entry)
 *   so any surviving call sites don't throw.  The hook line in ui-lite.html
 *   is dead and MUST be removed by the orchestrator (see report footer).
 *
 * Hard constraints respected:
 *   - NEVER touches measure-engine.js, RS, pdfToC/cToPdf, page-manager.js,
 *     server_lite.py, overview-setup.js, ui-lite.html (#ov untouched).
 *   - No new fields added to .bmaplan (no schema change).
 *   - Plain global functions, no IIFE, no bundler.
 */

/* ============================================================
   Internal state
   ============================================================ */
var _pmui_dragSrcIdx = null;   // 0-based display index being dragged
var _pmGridId = 'pm-grid';     // grid container id (inside #pm-overlay)
var _pmThumbObserver = null;   // IntersectionObserver for lazy thumbnail loading

/* ============================================================
   _pmuiInjectCss() — inject styles once (idempotent).
   ============================================================ */
function _pmuiInjectCss() {
  if (document.getElementById('pmui-style')) return;
  var s = document.createElement('style');
  s.id = 'pmui-style';
  s.textContent = [
    /* overlay */
    '#pm-overlay{position:fixed;inset:0;background:rgba(6,8,12,.82);z-index:200;',
    '  display:none;align-items:flex-start;justify-content:center;padding-top:60px;}',
    '#pm-overlay.show{display:flex;}',
    '#pm-shell{width:min(92vw,1080px);max-height:84vh;display:flex;flex-direction:column;',
    '  background:var(--panel);border:1px solid var(--line);border-radius:12px;overflow:hidden;}',
    /* header */
    '#pm-header{display:flex;align-items:center;padding:10px 14px;border-bottom:1px solid var(--line);',
    '  background:rgba(22,26,34,.97);gap:10px;}',
    '#pm-header h3{flex:1;font-size:14px;font-weight:600;color:var(--ink);margin:0;}',
    '#pm-close{background:transparent;border:0;color:var(--muted);font-size:20px;cursor:pointer;',
    '  line-height:1;padding:0 4px;border-radius:5px;}',
    '#pm-close:hover{background:#2a3140;color:var(--ink);}',
    /* grid scroll area */
    '#pm-grid-wrap{flex:1;overflow:auto;padding:14px;}',
    '#pm-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(120px,1fr));gap:10px;}',
    /* tiles */
    '.pmui-thumb{position:relative;cursor:grab;user-select:none;',
    '  background:#0c0f14;border:1px solid var(--line);border-radius:8px;padding:6px;}',
    '.pmui-thumb:hover{outline:1px solid var(--accent);}',
    '.pmui-thumb.cur{outline:2px solid var(--accent);}',
    '.pmui-thumb.drag-over{outline:2px dashed var(--accent);opacity:.8;}',
    '.pmui-thumb.dragging{opacity:.4;}',
    '.pmui-thumb img{width:100%;border-radius:4px;display:block;margin-bottom:4px;',
    '  background:#1a212c;min-height:60px;}',
    /* per-tile controls */
    '.pmui-actions{position:absolute;top:4px;right:4px;display:flex;gap:3px;opacity:0;transition:opacity .15s;}',
    '.pmui-thumb:hover .pmui-actions{opacity:1;}',
    '.pmui-btn{background:rgba(0,0,0,.7);border:1px solid var(--line);color:var(--ink);',
    '  border-radius:5px;padding:2px 5px;font-size:12px;cursor:pointer;line-height:1.4;}',
    '.pmui-btn:hover{background:var(--accent);}',
    '.pmui-label{display:block;font-size:11px;color:var(--muted);margin-top:3px;text-align:center;}',
    '.pmui-pending{width:100%;height:80px;display:flex;align-items:center;justify-content:center;',
    '  color:var(--muted);font-size:12px;background:rgba(255,255,255,.04);border-radius:6px;}',
    /* skeleton placeholder shown while thumb loads */
    '.pmui-skel{width:100%;min-height:60px;border-radius:4px;margin-bottom:4px;',
    '  background:linear-gradient(90deg,#1a212c 25%,#222a37 50%,#1a212c 75%);',
    '  background-size:200% 100%;animation:pmui-shimmer 1.4s infinite linear;}',
    '@keyframes pmui-shimmer{0%{background-position:200% 0}100%{background-position:-200% 0}}',
    '.pmui-thumb-img{width:100%;border-radius:4px;display:block;margin-bottom:4px;',
    '  background:#1a212c;min-height:60px;}',
    /* action bar */
    '#pmui-bar{position:sticky;bottom:0;left:0;right:0;',
    '  background:rgba(22,26,34,.97);border-top:1px solid var(--line);',
    '  padding:8px 14px;display:flex;align-items:center;gap:10px;',
    '  flex-wrap:wrap;font-size:13px;z-index:10;}',
  ].join('');
  document.head.appendChild(s);
}

/* ============================================================
   _pmuiBuildOverlay() — create #pm-overlay once, append to body.
   Returns the overlay element.
   ============================================================ */
function _pmuiBuildOverlay() {
  var existing = document.getElementById('pm-overlay');
  if (existing) return existing;

  var ov = document.createElement('div');
  ov.id = 'pm-overlay';

  var shell = document.createElement('div');
  shell.id = 'pm-shell';

  /* header */
  var hdr = document.createElement('div');
  hdr.id = 'pm-header';
  hdr.innerHTML = '<h3>จัดการหน้า</h3>';
  var closeBtn = document.createElement('button');
  closeBtn.id = 'pm-close';
  closeBtn.textContent = '✕';
  closeBtn.title = 'ปิด (Esc)';
  closeBtn.onclick = function () { _pmTryClose('close'); };
  hdr.appendChild(closeBtn);
  shell.appendChild(hdr);

  /* grid scroll area */
  var wrap = document.createElement('div');
  wrap.id = 'pm-grid-wrap';
  var grid = document.createElement('div');
  grid.id = _pmGridId;   // 'pm-grid'
  wrap.appendChild(grid);
  shell.appendChild(wrap);

  ov.appendChild(shell);
  document.body.appendChild(ov);

  /* Backdrop click routes through the single close funnel (guarded). */
  ov.addEventListener('click', function (e) {
    if (e.target === ov) _pmTryClose('backdrop');
  });

  return ov;
}

/* ============================================================
   _pmCloseOverlay() — hide the PM overlay UNCONDITIONALLY.
   Internal — callers that must respect the pending guard use
   _pmTryClose() instead. Kept because it is still the correct action
   AFTER the guard has already passed (see _pmTryClose below).
   ============================================================ */
function _pmCloseOverlay() {
  var ov = document.getElementById('pm-overlay');
  if (ov) ov.classList.remove('show');
  _pmHidePendingWarning();
  _pmHideDeleteConfirm();
}

/* ============================================================
   PM-GUARD (page-manager-redesign approach D, slice 1 —
   docs/invent/page-manager-redesign.md, GO 2026-08-10).

   _pmTryClose(src) — THE single close funnel. Backdrop click, Esc, and
   the ✕ button all route through here. If pending mutations exist,
   refuses to close and shows an in-shell warning bar instead of
   silently discarding unsaved page-manager work (BUG-20260810 CASE 2).
   Returns true if it actually closed, false if it refused.
   ============================================================ */
function _pmTryClose(src) {
  if (pageMgr && pageMgr.pending && pageMgr.pending.length > 0) {
    _pmShowPendingWarning();
    return false;
  }
  _pmCloseOverlay();
  return true;
}

/* ---- in-shell "pending mutations" warning bar (replaces silent close) ---- */
function _pmShowPendingWarning() {
  if (!pageMgr) return;
  var shell = document.getElementById('pm-shell');
  var wrap = document.getElementById('pm-grid-wrap');
  if (!shell || !wrap) return;

  var bar = document.getElementById('pmui-warn');
  if (!bar) {
    bar = document.createElement('div');
    bar.id = 'pmui-warn';
    bar.style.cssText = 'display:flex;align-items:center;gap:10px;' +
      'background:#2a1c10;border:1px solid #ffb454;color:#ffb454;' +
      'border-radius:7px;padding:6px 12px;margin:0 14px 8px 14px;font-size:12px;';
    var txt = document.createElement('span');
    txt.className = 'pmui-warn-text';
    bar.appendChild(txt);
    var discardBtn = document.createElement('button');
    discardBtn.id = 'pmui-discard';
    discardBtn.textContent = 'ทิ้งการแก้ไข';
    discardBtn.style.cssText = 'margin-left:auto;background:#ff453a;border:0;color:#fff;' +
      'border-radius:6px;padding:3px 10px;cursor:pointer;font-size:12px;';
    discardBtn.onclick = _pmDiscardPending;
    bar.appendChild(discardBtn);
    shell.insertBefore(bar, wrap);
  }
  var txtEl = bar.querySelector('.pmui-warn-text');
  if (txtEl) {
    txtEl.textContent = '⚠ มีการแก้ไขค้าง (' + pageMgr.pending.length +
      ') — บันทึก หรือ ทิ้งการแก้ไข';
  }
  bar.style.display = 'flex';
}

function _pmHidePendingWarning() {
  var bar = document.getElementById('pmui-warn');
  if (bar) bar.style.display = 'none';
}

/* ---- discard pending: reverse safely via the undo stack (each pending-
   generating mutation snapshots BEFORE pushing to pending, 1:1 — see
   page-manager.js reorder/del/duplicate/merge, all call _snap() then
   push exactly one pending entry), not a raw pending=[] wipe. ---- */
function _pmDiscardPending() {
  if (!pageMgr) return;
  var guard = 0;
  while (pageMgr.pending.length > 0 && guard < 10000) {
    if (!pageMgr.undo()) break;
    guard++;
  }
  if (pageMgr.pending.length > 0) pageMgr.pending = []; // defensive: undo stack exhausted
  _pmHidePendingWarning();
  _pmuiRenderGrid();
  _pmuiWire();
}

/* ---- in-shell delete confirm (replaces window.confirm) ---- */
function _pmShowDeleteConfirm(idx) {
  if (!pageMgr) return;
  var shell = document.getElementById('pm-shell');
  var wrap = document.getElementById('pm-grid-wrap');
  if (!shell || !wrap) return;

  var displayPage = idx + 1;
  var objCount = (typeof PS !== 'undefined' && PS[displayPage] &&
                  Array.isArray(PS[displayPage].objects))
    ? PS[displayPage].objects.length : 0;

  var bar = document.getElementById('pmui-delcfm');
  if (!bar) {
    bar = document.createElement('div');
    bar.id = 'pmui-delcfm';
    bar.style.cssText = 'display:flex;align-items:center;gap:10px;' +
      'background:#1c1114;border:1px solid #ff453a;color:var(--ink,#e8ecf3);' +
      'border-radius:7px;padding:6px 12px;margin:0 14px 8px 14px;font-size:12px;';
    shell.insertBefore(bar, wrap);
  }
  bar.innerHTML =
    '<span>ลบหน้า ' + displayPage + '? หน้านี้มีงานวัด ' + objCount + ' ชิ้น</span>' +
    '<span style="margin-left:auto;display:flex;gap:8px">' +
    '<button id="pmui-delcfm-cancel" style="border-radius:6px;padding:3px 10px;cursor:pointer;' +
    'border:1px solid var(--line,#2a3140);background:#222a37;color:var(--ink,#e8ecf3);">ยกเลิก</button>' +
    '<button id="pmui-delcfm-go" style="border-radius:6px;padding:3px 10px;cursor:pointer;' +
    'border:0;background:#ff453a;color:#fff;">ลบหน้า</button></span>';
  bar.style.display = 'flex';

  document.getElementById('pmui-delcfm-cancel').onclick = _pmHideDeleteConfirm;
  document.getElementById('pmui-delcfm-go').onclick = function () {
    _pmHideDeleteConfirm();
    pageMgr.del(idx);
    if (typeof state !== 'undefined') state.dirty = true;
    _pmuiRenderGrid();
    _pmuiWire();
  };
}

function _pmHideDeleteConfirm() {
  var bar = document.getElementById('pmui-delcfm');
  if (bar) bar.style.display = 'none';
}

/* ---- no-PDF hint: pmOpenManager() with no PDF loaded must give
   VISIBLE feedback, never a silent return. Uses the app's own
   state.hintFlash mechanism if a hintFlash() global exists; otherwise
   a tiny self-made toast. ---- */
function _pmShowNoPdfHint() {
  var msg = 'ยังไม่ได้เปิดไฟล์ PDF — เปิดไฟล์ก่อนจึงจะจัดการหน้าได้';
  if (typeof hintFlash === 'function') {
    hintFlash(msg);
    return;
  }
  var el = document.getElementById('pmui-nopdf-hint');
  if (!el) {
    el = document.createElement('div');
    el.id = 'pmui-nopdf-hint';
    el.style.cssText = 'position:fixed;left:50%;top:16px;transform:translateX(-50%);' +
      'z-index:400;background:#2a1c10;border:1px solid #ffb454;color:#ffb454;' +
      'border-radius:8px;padding:8px 16px;font-size:13px;transition:opacity .4s;' +
      'pointer-events:none;';
    document.body.appendChild(el);
  }
  el.textContent = msg;
  el.style.display = 'block';
  el.style.opacity = '1';
  clearTimeout(el._pmuiTimer);
  el._pmuiTimer = setTimeout(function () { el.style.opacity = '0'; }, 2500);
}

/* ============================================================
   _pmuiRenderGrid() — PURE DOM WRITE, no wiring.
   Rewrites #pm-grid with .pmui-thumb tiles from pageMgr state.
   Called by pmOpenManager() before _pmuiWire().
   Never calls pmOpenManager() — no recursion.
   ============================================================ */
function _pmuiRenderGrid() {
  if (!pageMgr) return;
  var g = document.getElementById(_pmGridId);
  if (!g) return;

  /* Disconnect any previous observer to avoid leaking observers on grid rebuild */
  if (_pmThumbObserver) {
    _pmThumbObserver.disconnect();
    _pmThumbObserver = null;
  }

  var html = '';
  var count = pageMgr.count();
  for (var n = 1; n <= count; n++) {
    var sn = pageMgr.serverNum(n);
    var imgSrc = sn ? api('/thumb/' + sn) : '';
    var isCur = (n === curPage);
    html += '<div class="thumb pmui-thumb' + (isCur ? ' cur' : '') + '" draggable="true"' +
            ' data-pmui-idx="' + (n - 1) + '">' +
            (imgSrc
              ? '<div class="pmui-skel"></div>' +
                '<img class="pmui-thumb-img" data-src="' + imgSrc + '">'
              : '<div class="pmui-pending">⏳ รอประมวลผล</div>') +
            '<span class="pmui-label">หน้า ' + n + '</span>' +
            '<div class="pmui-actions">' +
            (count > 1 ? '<button class="pmui-btn pmui-del" data-pmui-idx="' + (n - 1) + '" title="ลบหน้านี้">🗑</button>' : '') +
            '<button class="pmui-btn pmui-dup" data-pmui-idx="' + (n - 1) + '" title="ทำสำเนาหน้านี้">⧉</button>' +
            '</div></div>';
  }
  g.innerHTML = html;

  /* Set up IntersectionObserver on scroll container (#pm-grid-wrap as root).
     Only tiles that enter the scroll-container viewport trigger a fetch.
     rootMargin="200px" pre-fetches ~one row ahead of the visible edge. */
  var wrap = document.getElementById('pm-grid-wrap');
  if (!wrap || !window.IntersectionObserver) return;

  _pmThumbObserver = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (!entry.isIntersecting) return;
      var img = entry.target;
      var src = img.getAttribute('data-src');
      if (!src) return;
      img.src = src;
      img.removeAttribute('data-src');
      img.onload = function () {
        var skel = img.previousElementSibling;
        if (skel && skel.classList.contains('pmui-skel')) {
          skel.style.display = 'none';
        }
      };
      _pmThumbObserver.unobserve(img);
    });
  }, {
    root: wrap,
    rootMargin: '200px'
  });

  var imgs = g.querySelectorAll('.pmui-thumb-img[data-src]');
  imgs.forEach(function (img) {
    _pmThumbObserver.observe(img);
  });
}

/* ============================================================
   _pmuiWire() — event wiring + action bar.
   Assumes #pm-grid already contains .pmui-thumb tiles.
   Never calls pmOpenManager() — no recursion.
   ============================================================ */
function _pmuiWire() {
  var g = document.getElementById(_pmGridId);
  if (!g || !pageMgr) return;

  /* ---- Wire drag events on each .pmui-thumb ---- */
  var thumbs = g.querySelectorAll('.pmui-thumb');
  thumbs.forEach(function (thumb) {
    var idx = parseInt(thumb.getAttribute('data-pmui-idx'), 10);

    /* Navigate on body click (not on action buttons).
       BUG-20260811-escape-paths: this used to call _pmCloseOverlay()
       directly, skipping the pending-mutation guard — the funnel is
       _pmTryClose(), same door backdrop/Esc/✕ already use. Check pending
       FIRST: if there is unsaved work, warn and refuse (no navigation,
       no close); otherwise navigate then close via the guarded funnel. */
    thumb.onclick = function (e) {
      if (e.target.classList.contains('pmui-btn')) return;
      if (pageMgr && pageMgr.pending && pageMgr.pending.length > 0) {
        _pmShowPendingWarning();
        return;
      }
      var displayPage = idx + 1;
      loadPage(displayPage);
      _pmTryClose('tile-click');
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
      // FIX-B5: mark document dirty after reorder
      if (typeof state !== 'undefined') state.dirty = true;
      _pmuiRenderGrid();   // re-render grid after reorder
      _pmuiWire();
    });
  });

  /* ---- Wire delete buttons ---- */
  g.querySelectorAll('.pmui-del').forEach(function (btn) {
    btn.addEventListener('click', function (e) {
      e.stopPropagation();
      var idx = parseInt(btn.getAttribute('data-pmui-idx'), 10);
      if (pageMgr.count() <= 1) return;   // guard: refuse last page
      // PM-GUARD: in-shell confirm (shows live object count), no window.confirm.
      // Actual delete + dirty flag + re-render happen in _pmShowDeleteConfirm's
      // "ลบหน้า" button handler.
      _pmShowDeleteConfirm(idx);
    });
  });

  /* ---- Wire duplicate buttons ---- */
  g.querySelectorAll('.pmui-dup').forEach(function (btn) {
    btn.addEventListener('click', function (e) {
      e.stopPropagation();
      var idx = parseInt(btn.getAttribute('data-pmui-idx'), 10);
      pageMgr.duplicate(idx);
      // FIX-B5: mark document dirty after duplicate
      if (typeof state !== 'undefined') state.dirty = true;
      _pmuiRenderGrid();   // re-render grid after duplicate
      _pmuiWire();
    });
  });

  /* ---- Build (or refresh) the action bar ---- */
  _pmuiBuildActionBar();
}

/* ============================================================
   _pmuiBuildActionBar() — Build/update the action bar inside #pm-shell.
   ============================================================ */
function _pmuiBuildActionBar() {
  var existing = document.getElementById('pmui-bar');
  if (existing) existing.remove();

  var shell = document.getElementById('pm-shell');
  if (!shell || !pageMgr) return;

  var hasPending = pageMgr.pending.length > 0;

  var bar = document.createElement('div');
  bar.id = 'pmui-bar';

  // Apply button (only when pending)
  var applyBtn = document.createElement('button');
  applyBtn.id = 'pmui-apply';
  applyBtn.textContent = 'บันทึกการแก้ไขหน้า (' + pageMgr.pending.length + ')';
  applyBtn.style.cssText = 'background:var(--accent);color:#fff;border:0;border-radius:7px;' +
    'padding:6px 14px;cursor:pointer;font-size:13px;' +
    (hasPending ? '' : 'display:none;');
  applyBtn.onclick = _pmuiApplyChanges;
  bar.appendChild(applyBtn);

  // Undo button (only when undo stack has entries)
  if (pageMgr.undoStack && pageMgr.undoStack.length > 0) {
    var undoBtn = document.createElement('button');
    undoBtn.id = 'pmui-undo';
    undoBtn.textContent = '↶ เลิกทำ';
    undoBtn.style.cssText = 'background:#222a37;color:var(--ink);border:1px solid var(--line);' +
      'border-radius:7px;padding:6px 12px;cursor:pointer;font-size:13px;';
    undoBtn.onclick = function () {
      if (pageMgr.undo()) {
        // FIX-B5: mark document dirty after undo
        if (typeof state !== 'undefined') state.dirty = true;
        _pmuiRenderGrid(); _pmuiWire();
      }
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
  mergeBtn.textContent = '＋ รวมไฟล์ PDF';
  mergeBtn.title = hasPending ? 'บันทึกการแก้ไขหน้าให้เสร็จก่อนจึงจะรวมไฟล์ได้' : 'เพิ่มหน้าจากไฟล์ PDF อื่น';
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

  // Hidden file input for merge (singleton on body)
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

  shell.appendChild(bar);
}

/* ============================================================
   Apply changes (flush to server)
   ============================================================ */
async function _pmuiApplyChanges() {
  if (!pageMgr || !caseId) return;
  if (pageMgr.pending.length === 0) return;

  // Build order from simulateFlush (the tested, canonical flush algorithm).
  // This is the same algorithm the tests exercise, so live and test paths are unified.
  var sim = pageMgr.simulateFlush();
  var order = [];
  var hasMergedPage = false;
  for (var i = 0; i < sim.order.length; i++) {
    var id = sim.order[i];
    var sn = (pageMgr.originNum[id] != null) ? pageMgr.originNum[id]
             : (pageMgr.srcServer[id] != null ? pageMgr.srcServer[id] : null);
    if (sn === null) { hasMergedPage = true; break; }
    order.push(sn);
  }

  if (hasMergedPage) {
    alert('มีหน้าที่ Merge ค้างอยู่ — กรุณา Merge PDF ก่อนแล้วกด Apply');
    return;
  }

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

    // BUG-20260703: commit BEFORE re-baselining — _pmCommit(livePS) maps each
    // page's live content via the PRE-flush baseline (_initialIds/dupSrc);
    // applyFlush() destroys that mapping, so it must run after.
    _pmCommit();
    pageMgr.applyFlush();
    pageCount = data.new_count;

    // Refresh PM grid and canvas — do NOT call openOv() (that's the LOVS wizard)
    _pmuiRenderGrid();
    _pmuiWire();
    loadPage(1);
  } catch (err) {
    if (applyBtn) {
      applyBtn.disabled = false;
      applyBtn.textContent = 'บันทึกการแก้ไขหน้า (' + pageMgr.pending.length + ')';
    }
    alert('Apply ล้มเหลว: ' + err.message + '\nยังคงสถานะเดิม — กด Apply อีกครั้งเพื่อลองใหม่');
  }
}

/* ============================================================
   Merge PDF (append pages from another file)
   ============================================================ */
async function _pmuiMergePdf(evt) {
  var file = evt.target.files && evt.target.files[0];
  evt.target.value = '';
  if (!file || !caseId) return;

  if (pageMgr && pageMgr.pending.length > 0) {
    alert('กรุณา Apply page changes ก่อนแล้วค่อย Merge PDF');
    return;
  }

  var mergeBtn = document.getElementById('pmui-merge');
  if (mergeBtn) { mergeBtn.disabled = true; mergeBtn.textContent = 'กำลังรวมไฟล์…'; }

  try {
    var fd = new FormData();
    fd.append('case_id', caseId);
    fd.append('file', file);
    var resp = await fetch('/merge-pages', { method: 'POST', body: fd });
    var data = await resp.json();
    if (!data.ok) throw new Error(data.error || 'server error');

    var added = data.added_count;
    pageCount = data.new_count;

    pageMgr.merge(added);
    // BUG-20260703: commit (pre-flush baseline content mapping) before re-baseline
    _pmCommit();
    pageMgr.applyFlush();

    // Refresh PM grid and canvas — do NOT call openOv() (that's the LOVS wizard)
    _pmuiRenderGrid();
    _pmuiWire();
    loadPage(curPage);
  } catch (err) {
    alert('Merge ล้มเหลว: ' + err.message);
  } finally {
    if (mergeBtn) { mergeBtn.disabled = false; mergeBtn.textContent = '＋ รวมไฟล์ PDF'; }
  }
}

/* ============================================================
   pmOpenManager() — PUBLIC entry point.
   Builds (once) and shows the #pm-overlay, renders the PM grid.
   Guard: only opens if a PDF is loaded (caseId truthy) and pageMgr exists.
   Exposed as window.pmOpenManager for menu items.
   ============================================================ */
function pmOpenManager() {
  if (!caseId || !pageMgr) {
    // PM-GUARD: give visible feedback instead of a silent no-op.
    _pmShowNoPdfHint();
    return;
  }
  _pmuiInjectCss();
  _pmuiBuildOverlay();
  _pmuiRenderGrid();
  _pmuiWire();
  var ov = document.getElementById('pm-overlay');
  if (ov) ov.classList.add('show');
}
window.pmOpenManager = pmOpenManager;

/* ============================================================
   Keyboard trigger: Shift+F12 → pmOpenManager()
   Self-registered; requires zero changes to ui-lite.html.
   ============================================================ */
document.addEventListener('keydown', function (e) {
  if (e.shiftKey && e.key === 'F12') {
    e.preventDefault();
    pmOpenManager();
  }
});

/* Also close on Esc (complement to closeOverlays which won't see #pm-overlay
   since it's not a .overlay-classed element in #app). */
document.addEventListener('keydown', function (e) {
  if (e.key === 'Escape') {
    var ov = document.getElementById('pm-overlay');
    if (ov && ov.classList.contains('show')) {
      // Only act while open; stop the bubble so the app's window-level Escape
      // handler never also fires (lpm-9: no double-fire). preventDefault for
      // good measure. When closed, fall through so app Esc behaves normally.
      e.preventDefault();
      e.stopPropagation();
      // PM-GUARD: route through the single close funnel — refuses to close
      // (shows warning bar) while pending mutations exist.
      _pmTryClose('esc');
    }
  }
});

/* ============================================================
   pmUiDecorate() — kept as no-op alias so surviving call sites
   don't throw.  The openOv hook line in ui-lite.html is dead
   and should be removed by the orchestrator.

   REMOVE from ui-lite.html line 1008:
     if(typeof pmUiDecorate==='function') pmUiDecorate();
   ============================================================ */
function pmUiDecorate() {
  /* intentional no-op — overlay has moved to pmOpenManager() */
}
