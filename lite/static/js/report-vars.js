/* ============================================================
   LITE-REPORT-VARS — project-level derived-variable registry + evaluator
   Plain-globals module. No IIFE, no export, no bundler.
   Loaded via <script src="static/js/report-vars.js"> AFTER
   layer-system.js so layerById() etc. exist.

   Public API:
     REPORT_VARS                  — mutable registry [{id,name,unit,expr}]
     seedReportVars()             — idempotent: populate 3 presets if empty
     evalReportExpr(expr,computed)→ {v:Number|null, err:String|null}
     resolveReportRef(id,agg,computed) → Number|null
     computeReportVars(agg)       → [{id,name,unit,expr,value,err}]
     addReportVar(name)           → new entry (pushed into REPORT_VARS)
     removeReportVar(id)          → bool
     serializeReportVars()        → deep-plain copy [{id,name,unit,expr}]
     loadReportVars(arr)          → replace REPORT_VARS contents in place

   Expr token format  (token array, left-to-right fold):
     first token : {ref:catId}  OR  {lit:number}
     subsequent  : {op:'+'|'-'|'*'|'/', ref:catId}
                   {op:'+'|'-'|'*'|'/', lit:number}

   agg = {catId: areaSum, …}  keyed by layer.id, from computeSummary().
   computed = {varId: number, …}  built inside computeReportVars as vars resolve.
   ============================================================ */

var REPORT_VARS = [];

/* --- internal sequence counter for generated ids --- */
var _rvSeq = 0;

/* --- Seed 3 presets referencing default role catIds (idempotent) --- */
function seedReportVars() {
  if (REPORT_VARS.length > 0) return;
  /* อาคารสุทธิ = gfa - ded */
  REPORT_VARS.push({
    id:   'v_net',
    name: 'อาคารสุทธิ',
    unit: 'ม²',
    expr: [{ref:'gfa'}, {op:'-', ref:'ded'}]
  });
  /* OSR = open / site * 100 */
  REPORT_VARS.push({
    id:   'v_osr',
    name: 'OSR',
    unit: '%',
    expr: [{ref:'open'}, {op:'/', ref:'site'}, {op:'*', lit:100}]
  });
  /* FAR = gfa / site */
  REPORT_VARS.push({
    id:   'v_far',
    name: 'FAR',
    unit: '',
    expr: [{ref:'gfa'}, {op:'/', ref:'site'}]
  });
}

/* --- Resolve one operand token to a number ---
   Looks in agg (measured layer totals) first,
   then in computed (earlier vars already resolved this pass).
   Returns null if not found in either. */
function resolveReportRef(id, agg, computed) {
  if (agg && (id in agg)) return agg[id];
  if (computed && (id in computed)) return computed[id];
  return null;
}

/* --- Evaluate a token-array expression ---
   Left-to-right fold.  computed = {varId:number} from earlier vars.
   Returns {v:Number, err:null} or {v:null, err:String}. */
function evalReportExpr(expr, computed, agg) {
  if (!expr || expr.length === 0) return {v: null, err: 'ว่าง'};
  agg = agg || {};
  computed = computed || {};

  function tokenVal(t) {
    if ('lit' in t) return t.lit;
    return resolveReportRef(t.ref, agg, computed);
  }

  var acc = tokenVal(expr[0]);
  if (acc === null || acc === undefined) {
    return {v: null, err: 'อ้างตัวแปรไม่พบ'};
  }

  for (var i = 1; i < expr.length; i++) {
    var t = expr[i];
    var rhs = tokenVal(t);
    if (rhs === null || rhs === undefined) {
      return {v: null, err: 'อ้างตัวแปรไม่พบ'};
    }
    if (t.op === '+') { acc += rhs; }
    else if (t.op === '-') { acc -= rhs; }
    else if (t.op === '*') { acc *= rhs; }
    else if (t.op === '/') {
      if (rhs === 0) return {v: null, err: '÷0'};
      acc /= rhs;
    }
  }
  return {v: acc, err: null};
}

/* --- Compute all REPORT_VARS in order ---
   agg = {catId: number}  (from computeSummary)
   Returns [{id,name,unit,expr,value,err}].
   Later vars may reference earlier ones (chain). */
function computeReportVars(agg) {
  agg = agg || {};
  var computed = {};
  var results = [];
  for (var i = 0; i < REPORT_VARS.length; i++) {
    var vv = REPORT_VARS[i];
    var r = evalReportExpr(vv.expr, computed, agg);
    if (r.err === null) computed[vv.id] = r.v;
    results.push({
      id:    vv.id,
      name:  vv.name,
      unit:  vv.unit,
      expr:  vv.expr,
      value: r.err === null ? r.v : null,
      err:   r.err
    });
  }
  return results;
}

/* --- Add a new blank variable; returns it --- */
function addReportVar(name) {
  _rvSeq++;
  var entry = {
    id:   'v_' + _rvSeq,
    name: (name && name.length > 0) ? name : 'ตัวแปรใหม่',
    unit: '',
    expr: [{lit: 0}]
  };
  REPORT_VARS.push(entry);
  return entry;
}

/* --- Remove a variable by id; returns bool --- */
function removeReportVar(id) {
  for (var i = 0; i < REPORT_VARS.length; i++) {
    if (REPORT_VARS[i].id === id) {
      REPORT_VARS.splice(i, 1);
      return true;
    }
  }
  return false;
}

/* --- Serialize to plain deep copy (for S4 save) --- */
function serializeReportVars() {
  return REPORT_VARS.map(function(vv) {
    return {
      id:   vv.id,
      name: vv.name,
      unit: vv.unit,
      expr: vv.expr.map(function(t) {
        var out = {};
        if ('op'  in t) out.op  = t.op;
        if ('ref' in t) out.ref = t.ref;
        if ('lit' in t) out.lit = t.lit;
        return out;
      })
    };
  });
}

/* --- Replace REPORT_VARS contents in place (for S4 load) ---
   Tolerates null/undefined arr — no-op. */
function loadReportVars(arr) {
  if (!arr || !arr.length) return;
  REPORT_VARS.length = 0;
  for (var i = 0; i < arr.length; i++) {
    REPORT_VARS.push(arr[i]);
  }
}

/* ============================================================
   LITE-REPORT-VARS EDITOR  (LRV-S2)
   renderReportVarsEditor(host, agg)
     host = DOM element to render into
     agg  = {catId: number}  (from computeSummary — layerId→areaSum)
   All DOM building + CSS lives here so ui-lite.html stays lean.
   ============================================================ */

var _OPS = ['+', '-', '*', '/'];
var _rvFmt = function(n) {
  if (n == null) return '—';
  return Math.abs(n) >= 100 ? n.toFixed(0) : n.toFixed(2);
};

/* Inject CSS once per page load. */
function _injectRvStyle() {
  if (document.getElementById('rv-style')) return;
  var s = document.createElement('style');
  s.id = 'rv-style';
  s.textContent = [
    '.rv-seg{margin-top:12px;padding-top:10px;border-top:1px solid var(--line);}',
    '.rv-head{display:flex;align-items:center;justify-content:space-between;margin-bottom:6px;}',
    '.rv-head .rv-ttl{font-size:13px;font-weight:600;}',
    '.rv-badge{font-size:9.5px;background:#243;color:var(--good);border:1px solid #2f5a44;',
    '  border-radius:4px;padding:1px 5px;margin-left:6px;vertical-align:middle;}',
    '.rv-row{display:flex;gap:5px;align-items:center;flex-wrap:wrap;',
    '  padding:5px 0;border-bottom:1px dashed var(--line);}',
    '.rv-row:last-of-type{border-bottom:0;}',
    '.rv-name{width:118px;background:#0c0f14;border:1px solid var(--line);',
    '  border-radius:5px;color:var(--ink);padding:4px 7px;font-size:12.5px;}',
    '.rv-eq{color:var(--muted);padding:0 2px;}',
    '.rv-seg select{background:#0c0f14;border:1px solid var(--line);border-radius:5px;',
    '  color:var(--ink);padding:3px 6px;font-size:12px;cursor:pointer;}',
    '.rv-seg select.rv-op{width:40px;text-align:center;}',
    '.rv-lit{width:50px;background:#0c0f14;border:1px solid var(--line);border-radius:5px;',
    '  color:var(--ink);padding:3px 5px;font-size:12px;}',
    '.rv-mini{background:transparent;border:1px solid var(--line);color:var(--muted);',
    '  font-size:11px;border-radius:5px;padding:2px 7px;cursor:pointer;}',
    '.rv-mini.rv-add{color:var(--good);border-color:#2f5a44;}',
    '.rv-mini.rv-del-op{color:var(--muted);}',
    '.rv-mini.rv-del{color:#ff6b6b;border-color:#4d2f31;}',
    '.rv-val{margin-left:auto;font-weight:700;font-variant-numeric:tabular-nums;',
    '  min-width:78px;text-align:right;color:var(--good);}',
    '.rv-val.rv-err{color:#ff6b6b;font-weight:500;font-size:11px;}',
    '.rv-addvar{background:transparent;border:1px solid var(--line);color:var(--muted);',
    '  font-size:12px;border-radius:6px;padding:5px 10px;cursor:pointer;margin-top:8px;}',
    '.rv-addvar:hover{background:#2a3140;color:var(--ink);}'
  ].join('');
  document.head.appendChild(s);
}

/* Build operand <select> option list for var at index vIdx.
   Options: every layer ref, every earlier var ref, then literal. */
function _rvOperandOptions(vIdx) {
  var opts = [];
  /* layers */
  var layers = (typeof layersInOrder === 'function') ? layersInOrder() : [];
  for (var li = 0; li < layers.length; li++) {
    opts.push({ val: 'ref:' + layers[li].id, label: layers[li].name });
  }
  /* earlier vars (chain) */
  for (var vi = 0; vi < vIdx; vi++) {
    opts.push({ val: 'ref:' + REPORT_VARS[vi].id, label: '➜ ' + REPORT_VARS[vi].name });
  }
  opts.push({ val: 'lit', label: 'ตัวเลข…' });
  return opts;
}

/* Build the operand widget (select + optional lit input) for token t at
   position tIdx in var vIdx. host + agg needed for re-render closure. */
function _rvOperandWidget(vIdx, tIdx, t, host, agg) {
  var wrap = document.createElement('span');
  wrap.style.cssText = 'display:inline-flex;gap:4px;align-items:center';

  var sel = document.createElement('select');
  var curVal = ('lit' in t) ? 'lit' : 'ref:' + t.ref;
  var opts = _rvOperandOptions(vIdx);
  for (var oi = 0; oi < opts.length; oi++) {
    var opt = document.createElement('option');
    opt.value = opts[oi].val;
    opt.textContent = opts[oi].label;
    if (opts[oi].val === curVal) opt.selected = true;
    sel.appendChild(opt);
  }
  sel.onchange = (function(token, h, ag) {
    return function(ev) {
      var x = ev.target.value;
      if (x === 'lit') { delete token.ref; token.lit = 0; }
      else             { delete token.lit; token.ref = x.slice(4); }
      renderReportVarsEditor(h, ag);
    };
  })(t, host, agg);
  wrap.appendChild(sel);

  if ('lit' in t) {
    var li = document.createElement('input');
    li.className = 'rv-lit';
    li.type = 'number';
    li.value = t.lit;
    li.oninput = (function(token, h, ag) {
      return function(ev) {
        token.lit = parseFloat(ev.target.value) || 0;
        renderReportVarsEditor(h, ag);
      };
    })(t, host, agg);
    wrap.appendChild(li);
  }
  return wrap;
}

/* Main public renderer. Clears host and rebuilds from REPORT_VARS + agg. */
function renderReportVarsEditor(host, agg) {
  _injectRvStyle();
  agg = agg || {};

  /* compute values for display */
  var results = computeReportVars(agg);
  /* build id→result map */
  var resMap = {};
  for (var ri = 0; ri < results.length; ri++) resMap[results[ri].id] = results[ri];

  /* clear and rebuild */
  host.innerHTML = '';

  var seg = document.createElement('div');
  seg.className = 'rv-seg';

  /* header */
  var head = document.createElement('div');
  head.className = 'rv-head';
  head.innerHTML = '<span class="rv-ttl">ค่าที่คำนวณ / ตัวแปร' +
    '<span class="rv-badge">แก้ได้</span></span>';
  seg.appendChild(head);

  /* one row per REPORT_VARS entry */
  for (var vi = 0; vi < REPORT_VARS.length; vi++) {
    (function(vIdx) {
      var vv = REPORT_VARS[vIdx];
      var row = document.createElement('div');
      row.className = 'rv-row';

      /* editable name */
      var nm = document.createElement('input');
      nm.className = 'rv-name';
      nm.value = vv.name;
      nm.oninput = (function(entry, h, ag) {
        return function(ev) { entry.name = ev.target.value; };
      })(vv, host, agg);
      row.appendChild(nm);

      /* = sign */
      var eq = document.createElement('span');
      eq.className = 'rv-eq';
      eq.textContent = '=';
      row.appendChild(eq);

      /* token chain */
      for (var ti = 0; ti < vv.expr.length; ti++) {
        var t = vv.expr[ti];
        /* operator select for tokens after the first */
        if (ti > 0) {
          var opSel = document.createElement('select');
          opSel.className = 'rv-op';
          for (var oi2 = 0; oi2 < _OPS.length; oi2++) {
            var optEl = document.createElement('option');
            optEl.value = _OPS[oi2];
            optEl.textContent = _OPS[oi2];
            if (_OPS[oi2] === t.op) optEl.selected = true;
            opSel.appendChild(optEl);
          }
          opSel.onchange = (function(token, h, ag) {
            return function(ev) { token.op = ev.target.value; renderReportVarsEditor(h, ag); };
          })(t, host, agg);
          row.appendChild(opSel);
        }
        row.appendChild(_rvOperandWidget(vIdx, ti, t, host, agg));
      }

      /* + ขั้น button */
      var more = document.createElement('button');
      more.className = 'rv-mini rv-add';
      more.textContent = '+ ขั้น';
      more.onclick = (function(entry, h, ag) {
        return function() { entry.expr.push({op: '+', lit: 0}); renderReportVarsEditor(h, ag); };
      })(vv, host, agg);
      row.appendChild(more);

      /* − (pop last token) — only when > 1 token */
      if (vv.expr.length > 1) {
        var less = document.createElement('button');
        less.className = 'rv-mini rv-del-op';
        less.textContent = '−';
        less.onclick = (function(entry, h, ag) {
          return function() { entry.expr.pop(); renderReportVarsEditor(h, ag); };
        })(vv, host, agg);
        row.appendChild(less);
      }

      /* computed value or error */
      var res = resMap[vv.id];
      var valSpan = document.createElement('span');
      if (res && res.err) {
        valSpan.className = 'rv-val rv-err';
        valSpan.textContent = '⚠ ' + res.err;
      } else {
        valSpan.className = 'rv-val';
        valSpan.textContent = _rvFmt(res ? res.value : null) + (vv.unit ? ' ' + vv.unit : '');
      }
      row.appendChild(valSpan);

      /* ✕ delete */
      var del = document.createElement('button');
      del.className = 'rv-mini rv-del';
      del.textContent = '✕';
      del.onclick = (function(vid, h, ag) {
        return function() { removeReportVar(vid); renderReportVarsEditor(h, ag); };
      })(vv.id, host, agg);
      row.appendChild(del);

      seg.appendChild(row);
    })(vi);
  }

  /* + เพิ่มตัวแปร button */
  var addBtn = document.createElement('button');
  addBtn.className = 'rv-addvar';
  addBtn.textContent = '+ เพิ่มตัวแปร';
  addBtn.onclick = (function(h, ag) {
    return function() { addReportVar(); renderReportVarsEditor(h, ag); };
  })(host, agg);
  seg.appendChild(addBtn);

  host.appendChild(seg);
}
