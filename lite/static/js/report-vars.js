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
     computeReportVars(agg,opts)  → [{id,name,unit,expr,value,err}]
                                     opts.useLive:true (B1) sources role
                                     totals from ObjectAgg.byRole() instead
                                     of agg; default false = legacy/pure.
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

/* --- Roll up custom-layer areas into their role bucket ---
   Given an agg keyed by catId (layer.id), returns a new object that keeps all
   original keys AND adds/overwrites each role key with the sum of all layers
   that map to that role.  This means exprs referencing {ref:"gfa"} work even
   when every measured area sits on a custom layer like "L7".

   Algorithm (double-buffer to avoid double-count):
     1. Copy all original keys into out.
     2. Accumulate per-role sums into a SEPARATE roleSum map
        (so a default layer whose id===role is counted exactly once).
     3. Overwrite out[role] = roleSum[role] for every role found.

   Default-only safety: agg={gfa:10}, layerById("gfa").role="gfa"
     → roleSum={gfa:10} → out["gfa"]=10. Identical to input. No double-count.
   Custom-only case: agg={L7:50}, layerById("L7").role="gfa"
     → roleSum={gfa:50} → out={L7:50, gfa:50}. Now {ref:"gfa"} resolves.
   Mixed case: agg={gfa:30, L7:50}, both role=gfa
     → roleSum={gfa:80} → out["gfa"]=80. Correct total. */
function rollupAggByRole(agg) {
  agg = agg || {};
  var out = {};
  for (var k in agg) if (agg.hasOwnProperty(k)) out[k] = agg[k];   // keep original catId keys
  var roleSum = {};
  for (var k in agg) { if (!agg.hasOwnProperty(k)) continue;
    var lay = (typeof layerById === "function") ? layerById(k) : null;
    if (lay && lay.role) roleSum[lay.role] = (roleSum[lay.role] || 0) + agg[k];
  }
  for (var r in roleSum) if (roleSum.hasOwnProperty(r)) out[r] = roleSum[r]; // OVERWRITE role key with full role total
  return out;
}

/* --- Compute all REPORT_VARS in order ---
   agg = {catId: number}  (from computeSummary)
   opts.useLive (default false, B1 / INV-20260703-layer-linkage): when true
     AND window.ObjectAgg exists (typeof-guard), role totals (gfa/ded/site/
     open/...) are sourced from ObjectAgg.byRole() — the live object-tuple
     stream, which correctly skips excluded[] pages — instead of being
     re-derived from agg's own catId keys via rollupAggByRole(). Layer/catId
     keys from the passed agg are preserved so a var referencing one
     specific layer id (not just its role) still resolves. useLive is
     OPT-IN and defaults to false so this stays a pure function of `agg`
     with no window/PS coupling for the legacy path — required by
     test_report_vars*.py, which pass synthetic agg values and expect
     deterministic fold-eval regardless of any live page state. Production
     call sites (openSum, per-floor block, buildReportPayload) pass
     {useLive:true} explicitly.
   Returns [{id,name,unit,expr,value,err}].
   Later vars may reference earlier ones (chain). */
function computeReportVars(agg, opts) {
  agg = agg || {};
  var rolled;
  if (opts && opts.useLive && typeof window !== "undefined" && window.ObjectAgg &&
      typeof window.ObjectAgg.byRole === "function") {
    rolled = {};
    for (var k in agg) if (agg.hasOwnProperty(k)) rolled[k] = agg[k];
    var tupleRoles = window.ObjectAgg.byRole();
    for (var role in tupleRoles) if (tupleRoles.hasOwnProperty(role)) rolled[role] = tupleRoles[role].area;
  } else {
    rolled = rollupAggByRole(agg);
  }
  var computed = {};
  var results = [];
  for (var i = 0; i < REPORT_VARS.length; i++) {
    var vv = REPORT_VARS[i];
    var r = evalReportExpr(vv.expr, computed, rolled);
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

/* --- Render-time error classifier (UX batch2, seeded-vars neutral state) ---
   Distinguishes "waiting for data" (seeded FAR/OSR/net vars that error ONLY
   because their referenced role/layer totals are empty before any object is
   measured) from a GENUINE error (bad ref to a non-existent target, malformed
   empty expr, or a real division-by-zero once data exists). Classifies purely
   at render time by inspecting the expr tokens + current data presence —
   evalReportExpr itself is NOT modified (its err strings stay as-is).
     Returns 'wait'  → render neutral/dim "รอข้อมูล"
             'err'   → render red error (unchanged behavior). */
function _rvRefKnown(ref) {
  if (typeof ROLE_DEFS !== 'undefined' && ROLE_DEFS) {
    for (var i = 0; i < ROLE_DEFS.length; i++) if (ROLE_DEFS[i].id === ref) return true;
  }
  if (typeof layerById === 'function' && layerById(ref)) return true;
  for (var j = 0; j < REPORT_VARS.length; j++) if (REPORT_VARS[j].id === ref) return true;
  return false;
}
function _rvHasData(agg) {
  if (agg) for (var k in agg) if (agg.hasOwnProperty(k) && agg[k]) return true;
  if (typeof window !== 'undefined' && window.ObjectAgg && typeof window.ObjectAgg.byRole === 'function') {
    var tr = window.ObjectAgg.byRole();
    for (var r in tr) if (tr.hasOwnProperty(r) && tr[r] && tr[r].area) return true;
  }
  return false;
}
function classifyReportVarErr(v, agg) {
  if (!v || !v.err) return null;                 // no error → caller renders value
  var expr = v.expr;
  if (!expr || expr.length === 0) return 'err';  // 'ว่าง' — malformed, genuine
  var hasRef = false;
  for (var i = 0; i < expr.length; i++) {
    var t = expr[i];
    if ('ref' in t) { hasRef = true; if (!_rvRefKnown(t.ref)) return 'err'; } // unknown ref → genuine
  }
  if (v.err === '÷0') return _rvHasData(agg) ? 'err' : (hasRef ? 'wait' : 'err');
  if (v.err === 'อ้างตัวแปรไม่พบ') return hasRef ? 'wait' : 'err';
  return 'err';
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
    '.rv-val.rv-wait{color:var(--muted);font-weight:500;font-size:11px;opacity:.75;}',
    '.rv-addvar{background:transparent;border:1px solid var(--line);color:var(--muted);',
    '  font-size:12px;border-radius:6px;padding:5px 10px;cursor:pointer;margin-top:8px;}',
    '.rv-addvar:hover{background:#2a3140;color:var(--ink);}'
  ].join('');
  document.head.appendChild(s);
}

/* Build operand <select> option groups for var at index vIdx (B5,
   INV-20260703-layer-linkage, closes M4).
   Returns {roles, layers, vars} — three label/value lists:
     roles  = the 6 ROLE_DEFS, "Σ " prefix — picking one means "rollup of
              EVERY layer whose role is this" (resolves via rollupAggByRole /
              ObjectAgg.byRole(), never a single layer's own area).
     layers = CUSTOM layers only (added via addLayer — id !== role id),
              "▸ " prefix + layer name + role in parens — picking one means
              "this ONE layer's own area", never rolled up with siblings.
              Default per-role layers (layer.id === layer.role, e.g. the
              seeded "gfa" layer) are deliberately excluded here: their ref
              string is IDENTICAL to their role's ref string (rollupAggByRole
              always overwrites that key with the full role sum), so listing
              them a second time under "single layer" would just be a
              same-value duplicate of the role option — the exact ambiguity
              this sprint removes, not an addition to it.
     vars   = earlier vars in the chain (unchanged, ungrouped, "➜ " prefix). */
function _rvOperandOptions(vIdx) {
  var roles = [];
  for (var ri = 0; ri < ROLE_DEFS.length; ri++) {
    var rd = ROLE_DEFS[ri];
    roles.push({ val: 'ref:' + rd.id, label: 'Σ ' + rd.name });
  }
  var layerOpts = [];
  var layers = (typeof layersInOrder === 'function') ? layersInOrder() : [];
  for (var li = 0; li < layers.length; li++) {
    var lay = layers[li];
    if (lay.id === lay.role) continue; // default layer — already covered by its role option
    var rd2 = (typeof roleDef === 'function') ? roleDef(lay.role) : null;
    var roleName = rd2 ? rd2.name : lay.role;
    layerOpts.push({ val: 'ref:' + lay.id, label: '▸ ' + lay.name + ' (' + roleName + ')' });
  }
  var varOpts = [];
  for (var vi = 0; vi < vIdx; vi++) {
    varOpts.push({ val: 'ref:' + REPORT_VARS[vi].id, label: '➜ ' + REPORT_VARS[vi].name });
  }
  return { roles: roles, layers: layerOpts, vars: varOpts };
}

/* Append a flat list of {val,label} as <option> children of `parent`,
   marking the one matching curVal as selected. */
function _rvAppendOptions(parent, list, curVal) {
  for (var i = 0; i < list.length; i++) {
    var opt = document.createElement('option');
    opt.value = list[i].val;
    opt.textContent = list[i].label;
    if (list[i].val === curVal) opt.selected = true;
    parent.appendChild(opt);
  }
}

/* Build the operand widget (select + optional lit input) for token t at
   position tIdx in var vIdx. host + agg needed for re-render closure. */
function _rvOperandWidget(vIdx, tIdx, t, host, agg) {
  var wrap = document.createElement('span');
  wrap.style.cssText = 'display:inline-flex;gap:4px;align-items:center';

  var sel = document.createElement('select');
  var curVal = ('lit' in t) ? 'lit' : 'ref:' + t.ref;
  var groups = _rvOperandOptions(vIdx);

  var ogRole = document.createElement('optgroup');
  ogRole.label = 'หมวดรวม (ทุกเลเยอร์ใน role)';
  _rvAppendOptions(ogRole, groups.roles, curVal);
  sel.appendChild(ogRole);

  var ogLayer = document.createElement('optgroup');
  ogLayer.label = 'เลเยอร์เดี่ยว';
  _rvAppendOptions(ogLayer, groups.layers, curVal);
  sel.appendChild(ogLayer);

  _rvAppendOptions(sel, groups.vars, curVal);

  var litOpt = document.createElement('option');
  litOpt.value = 'lit';
  litOpt.textContent = 'ตัวเลข…';
  if (curVal === 'lit') litOpt.selected = true;
  sel.appendChild(litOpt);

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

/* Main public renderer. Clears host and rebuilds from REPORT_VARS + agg.
   opts (B1, optional) forwarded to computeReportVars — {useLive:true} routes
   role totals through ObjectAgg.byRole() (see computeReportVars doc). */
function renderReportVarsEditor(host, agg, opts) {
  _injectRvStyle();
  agg = agg || {};

  /* compute values for display */
  var results = computeReportVars(agg, opts);
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
        if (classifyReportVarErr(res, agg) === 'wait') {
          valSpan.className = 'rv-val rv-wait';
          valSpan.textContent = 'รอข้อมูล';
        } else {
          valSpan.className = 'rv-val rv-err';
          valSpan.textContent = '⚠ ' + res.err;
        }
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
