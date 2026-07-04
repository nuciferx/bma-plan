/* report-edit.js — Editable area-report engine for lite-report.html
   Public API: ReportEdit.mount(hostEl, rows), ReportEdit.unmount()
   Also exposes window.ReportEditAPI for test automation.
   Ported from lite/sandbox/invent-lite-editable-report-d3.html (D3_SPIKE_OK 6/6).
   Lean: plain global, no IIFE, no export, no bundler. */

var ReportEdit = (function(){
  /* ---------- module state ---------- */
  var jss = null;
  var hostEl = null;
  var opsEl = null;
  var statusEl = null;
  var baseline = [];
  var rowIds = [];
  var subMeta = {};
  var rowSign = {};       /* B-3 (REVIEW ledger slice B/4): rowId -> 1|-1, from the seed row's own `sign` (role-derived upstream) */
  var _currentRows = null; /* rich seed rows [{name,area,sign,page}] behind the current seedData -- source for rowSign + makeHash */
  var stCounter = 0;
  var _rebuilding = false;

  /* picker state */
  var pickerActive = false;
  var editorInput = null;
  var editorCellX = -1, editorCellY = -1;

  /* default sample seed (matches d3 eval expectations) */
  var DEFAULT_SEED = [
    ['หลังคา A', 50.45],
    ['หลังคา B', 36.48],
    ['ทางเดิน', 26.16],
    ['ช่องลิฟต์ (หัก)', 10.00]
  ];

  /* ---------- helpers ---------- */
  function colCell(y){ return 'B'+(y+1); }
  function colLetter(x){ return String.fromCharCode(65+x); }
  function areaCount(){
    var n=0;
    for(var i=0;i<rowIds.length;i++){
      if(rowIds[i].charAt(0)==='r') n++;
      else break;
    }
    return n;
  }
  /* B-3: sign of the row at sheet-row index y (1 unless its seed row was
     marked sign:-1, e.g. a deduction-role group row). Defaults to +1 for
     subtotal rows / out-of-range indices -- unchanged current behavior. */
  function rowSignOf(y){
    var rid=rowIds[y];
    if(rid==null) return 1;
    return rowSign[rid]===-1?-1:1;
  }

  function refreshOverrideStyles(){
    if(!jss) return;
    var ac=areaCount();
    for(var i=0;i<ac;i++){
      var raw=jss.getValueFromCoords(1,i);
      var isFormula=typeof raw==='string'&&raw.charAt(0)==='=';
      var num=parseFloat(raw);
      var overridden=!isFormula&&isFinite(num)&&Math.abs(num-baseline[i])>1e-9;
      jss.setStyle(colCell(i),'color',overridden?'#1d4ed8':'');
      jss.setStyle(colCell(i),'font-weight',overridden?'700':'');
    }
  }

  /* ---------- formula <-> semantic-id translation ---------- */
  function parseFormula(f){
    var body=String(f).replace(/^=/,'');
    var terms=[]; var re=/([+\-*/]?)\s*B(\d+)/gi; var m;
    while((m=re.exec(body))){
      var op=m[1]||'+';
      var n=parseInt(m[2],10);
      var id=rowIds[n-1];
      if(id) terms.push({id:id,op:(op==='-'?'-':'+')});
    }
    return terms;
  }
  function captureFormula(rowIdx,value){
    var id=rowIds[rowIdx];
    if(!id) return;
    subMeta[id]=parseFormula(value);
  }
  function rebuildSubtotals(){
    _rebuilding=true;
    for(var p=0;p<rowIds.length;p++){
      var meta=subMeta[rowIds[p]];
      if(!meta) continue;
      var s='', dropped=false;
      for(var k=0;k<meta.length;k++){
        var t=meta[k];
        var pos=rowIds.indexOf(t.id);
        if(pos<0){ dropped=true; continue; }
        var ref='B'+(pos+1);
        if(s===''){ s=(t.op==='-'?'-':'')+ref; }
        else      { s+=t.op+ref; }
      }
      jss.setValueFromCoords(1,p,s===''?'0':'='+s,true);
      jss.setStyle('B'+(p+1),'background-color',dropped?'#ffe0e0':'');
    }
    _rebuilding=false;
  }

  /* ---------- structural mutations ---------- */
  function addSubtotalRow(label,formula){
    var id='st'+(++stCounter);
    rowIds.push(id);
    _rebuilding=true;
    jss.insertRow([label,formula||'']);
    _rebuilding=false;
    if(formula){ captureFormula(rowIds.length-1,formula); rebuildSubtotals(); }
  }
  function doDeleteRow(idx){
    if(idx<0||idx>=rowIds.length) return;
    var ac=areaCount();
    delete rowSign[rowIds[idx]];
    rowIds.splice(idx,1);
    if(idx<ac) baseline.splice(idx,1);
    _rebuilding=true;
    jss.deleteRow(idx,1);
    _rebuilding=false;
    rebuildSubtotals();
    refreshOverrideStyles();
  }

  /* ---------- picker ---------- */
  function setPickerActive(on){
    pickerActive=on;
    /* toggle picker-mode on host's ownerDocument.body */
    if(hostEl&&hostEl.ownerDocument){
      hostEl.ownerDocument.body.classList.toggle('re-picker-mode',on);
    }
    if(opsEl){
      [].forEach.call(opsEl.querySelectorAll('button[data-op]'),function(b){ b.disabled=!on; });
    }
    if(!hostEl) return;
    [].forEach.call(hostEl.querySelectorAll('td.re-picker-hot'),function(td){ td.classList.remove('re-picker-hot'); });
    if(on){
      [].forEach.call(hostEl.querySelectorAll('td[data-x="1"]'),function(td){
        var y=parseInt(td.getAttribute('data-y'),10);
        if(y!==editorCellY) td.classList.add('re-picker-hot');
      });
    }
  }
  /* B-3: last non-whitespace char of a formula body, used to detect the
     user already picked an explicit operator (+, -, *, /) before clicking
     a cell -- in that case we must NOT also auto-insert a sign. */
  function lastMeaningfulChar(v){
    var t=String(v||'').replace(/\s+$/,'');
    return t.length?t.charAt(t.length-1):'';
  }
  function insertAtCaret(text){
    if(!editorInput) return;
    var s=editorInput.selectionStart||editorInput.value.length;
    var e=editorInput.selectionEnd||editorInput.value.length;
    var v=editorInput.value;
    editorInput.value=v.slice(0,s)+text+v.slice(e);
    var pos=s+text.length;
    editorInput.selectionStart=editorInput.selectionEnd=pos;
    editorInput.focus();
    editorInput.dispatchEvent(new Event('input',{bubbles:true}));
  }
  function bindHostPicker(){
    hostEl.addEventListener('mousedown',function(e){
      if(!pickerActive||!editorInput) return;
      var td=e.target.closest&&e.target.closest('td');
      if(!td) return;
      var xs=td.getAttribute('data-x'),ys=td.getAttribute('data-y');
      if(xs===null||ys===null) return;
      var x=parseInt(xs,10),y=parseInt(ys,10);
      if(x!==1) return;
      if(x===editorCellX&&y===editorCellY) return;
      e.preventDefault();
      e.stopImmediatePropagation();
      var ref=colLetter(x)+(y+1);
      /* B-3: auto-default the sign for a picked cell UNLESS the user already
         typed/clicked an explicit operator right before this pick (that
         explicit choice always wins, e.g. building a ratio with '*'/'/').
         With no explicit op pending: ded-role rows (rowSignOf<0) insert
         '-B{n}' instead of a bare ref, so naively clicking through rows in
         order produces a correctly SIGNED sum with no manual '-' click
         needed -- this is the fix for B-3 ("grid ไม่รู้เครื่องหมายลบ"). */
      var body=String(editorInput.value||'').replace(/^=/,'');
      var lastCh=lastMeaningfulChar(body);
      var hasExplicitOp=(lastCh==='+'||lastCh==='-'||lastCh==='*'||lastCh==='/');
      var text=ref;
      if(!hasExplicitOp){
        var neg=rowSignOf(y)<0;
        var isFirst=body.replace(/\s+/g,'')==='';
        text=(neg?'-':(isFirst?'':'+'))+ref;
      }
      insertAtCaret(text);
    },true);
  }

  /* ---------- persistence ---------- */
  /* B-3/B-10-in-passing (REVIEW ledger slice B/4): rows are the rich seed
     objects [{name,area,page,...}], not [name,area] pairs -- the hash now
     includes each row's page index, so two rows with the SAME name+area on
     DIFFERENT pages (plausible once grid shows every page, e.g. the same
     category repeated per floor) no longer collide into the same
     localStorage key. This does NOT fully close B-10 (still a plain
     content hash, still no cross-project namespacing / orphan GC -- flagged,
     out of scope this slice); old-format keys from before this change
     simply won't match on load (acceptable, no migration code per spec). */
  function makeHash(rows){
    return (rows||[]).map(function(r){
      var pg=(r&&r.page!=null)?r.page:'';
      var nm=(r&&r.name!=null)?r.name:'';
      var ar=(r&&r.area!=null)?r.area:'';
      return pg+'|'+nm+'|'+ar;
    }).join('||');
  }
  function lsKey(hash){ return 'bmaReportEdit.v1::'+hash; }
  function saveState(seedHash){
    if(!jss) return;
    try{
      var payload=JSON.stringify({data:jss.getData(),baseline:baseline,areaCount:areaCount(),subMeta:subMeta,rowSign:rowSign});
      localStorage.setItem(lsKey(seedHash),payload);
    }catch(e){}
  }
  function loadState(seedHash){
    try{ return JSON.parse(localStorage.getItem(lsKey(seedHash))); }catch(e){ return null; }
  }

  /* ---------- init / mount ---------- */
  function init(seedData, saved){
    var data=saved&&saved.data?saved.data:seedData.map(function(r){return r.slice();});
    if(saved&&saved.baseline) baseline=saved.baseline.slice();
    else baseline=seedData.map(function(r){return r[1];});
    rowIds=[]; subMeta={}; rowSign={}; stCounter=0;
    var nArea=saved&&saved.areaCount!=null?saved.areaCount:seedData.length;
    for(var i=0;i<data.length;i++){
      if(i<nArea){ rowIds.push('r'+i); }
      else { rowIds.push('st'+(++stCounter)); }
    }
    if(saved&&saved.subMeta){ subMeta=JSON.parse(JSON.stringify(saved.subMeta)); }
    /* B-3: restore persisted per-row sign if this session had one saved,
       else derive fresh from the rich seed rows (_currentRows) set by
       mount()/reset() just before this call. */
    if(saved&&saved.rowSign){ rowSign=JSON.parse(JSON.stringify(saved.rowSign)); }
    else{
      for(var si=0; si<nArea; si++){
        var src=_currentRows&&_currentRows[si];
        rowSign['r'+si]=(src&&src.sign===-1)?-1:1;
      }
    }

    hostEl.innerHTML='';
    jss=jspreadsheet(hostEl,{
      data:data,
      columns:[
        {type:'text',title:'ประเภท',width:240},
        {type:'numeric',title:'พื้นที่ (ตร.ม.)',width:160,align:'right'}
      ],
      allowInsertRow:true,allowDeleteRow:true,allowInsertColumn:false,
      editable:true,about:false,tableOverflow:false,

      oneditionstart:function(el,cell,x,y){
        editorCellX=parseInt(x,10); editorCellY=parseInt(y,10);
      },
      oncreateeditor:function(el,cell,x,y,inputEl){
        var inp=inputEl||cell.querySelector('input,textarea');
        if(!inp) return;
        editorInput=inp;
        var update=function(){ if(!inp) return; setPickerActive((inp.value||'').charAt(0)==='='); };
        inp.addEventListener('input',update);
        inp.addEventListener('keyup',update);
        update();
      },
      oneditionend:function(){
        setPickerActive(false);
        editorInput=null; editorCellX=-1; editorCellY=-1;
      },
      onchange:function(instance,cell,x,y,value){
        if(_rebuilding) return;
        var xi=parseInt(x,10),yi=parseInt(y,10);
        /* NaN-guard: reject non-numeric input on area-row column B */
        if(xi===1&&yi<areaCount()){
          var isFormula=typeof value==='string'&&value.charAt(0)==='=';
          if(!isFormula&&!isFinite(parseFloat(value))){
            /* revert to previous baseline value */
            jss.setValueFromCoords(1,yi,baseline[yi],true);
            if(statusEl){ statusEl.textContent='ต้องเป็นตัวเลขเท่านั้น'; }
            return;
          }
        }
        if(statusEl){ statusEl.textContent=''; }
        refreshOverrideStyles();
        /* capture semantic formula */
        if(xi===1&&typeof value==='string'&&value.charAt(0)==='='){ captureFormula(yi,value); }
      },
      onload:refreshOverrideStyles
    });

    bindHostPicker();
    refreshOverrideStyles();
    if(saved) rebuildSubtotals();
  }

  /* ---------- PUBLIC API ---------- */
  var _currentSeed=null;
  var _currentSeedHash=null;

  function mount(el, rows){
    if(jss) unmount();
    hostEl=el;
    /* build seedData from rows [{name,area,sign,page}]; keep the rich rows
       around (_currentRows) for rowSign derivation + the page-aware hash */
    var srcRows=rows&&rows.length
      ? rows
      : DEFAULT_SEED.map(function(r){return {name:r[0],area:r[1],sign:1};});
    var seedData=srcRows.map(function(r){return [r.name,r.area];});
    _currentRows=srcRows;
    _currentSeed=seedData;
    _currentSeedHash=makeHash(srcRows);

    /* inject picker CSS into page if not already there */
    if(!document.getElementById('re-picker-style')){
      var st=document.createElement('style');
      st.id='re-picker-style';
      st.textContent='body.re-picker-mode .jss td.re-picker-hot{outline:2px solid #2d6cdf;outline-offset:-2px;cursor:cell}'+
        'body.re-picker-mode .jss td.re-picker-hot:hover{background:#eff6ff!important}'+
        '.jexcel_container td.editor input,.jss td.editor input,td.editor input,td.editor textarea{'+
        'background:#fffbe6!important;border:2px solid #2d6cdf!important;color:#1a1d21!important;'+
        'font:14px "Segoe UI"!important;width:100%!important;box-sizing:border-box!important;padding:2px 4px!important}';
      document.head.appendChild(st);
    }

    /* build ops toolbar and status inside host's parent */
    var wrapper=el.parentElement||el;
    var existingOps=wrapper.querySelector('.re-ops');
    if(existingOps) existingOps.remove();
    var existingStatus=wrapper.querySelector('.re-status');
    if(existingStatus) existingStatus.remove();

    opsEl=document.createElement('div');
    opsEl.className='re-ops';
    opsEl.style.cssText='display:flex;gap:8px;align-items:center;margin:8px 0 4px;flex-wrap:wrap';
    opsEl.innerHTML='<button class="re-btn" id="re-btn-sub" style="font:13px \'Segoe UI\';padding:5px 10px;border:1px solid #c7ccd3;background:#fff;border-radius:6px;cursor:pointer">+ แทรกแถว Subtotal</button>'+
      '<span style="display:inline-flex;gap:4px;align-items:center;padding-left:10px;border-left:1px solid #e3e6ea">'+
      '<button data-op="+" disabled style="font:600 13px;padding:4px 10px;border:1px solid #c7ccd3;background:#fff;border-radius:6px;cursor:pointer;min-width:32px">+</button>'+
      '<button data-op="-" disabled style="font:600 13px;padding:4px 10px;border:1px solid #c7ccd3;background:#fff;border-radius:6px;cursor:pointer;min-width:32px">−</button>'+
      '<button data-op="*" disabled style="font:600 13px;padding:4px 10px;border:1px solid #c7ccd3;background:#fff;border-radius:6px;cursor:pointer;min-width:32px">×</button>'+
      '<button data-op="/" disabled style="font:600 13px;padding:4px 10px;border:1px solid #c7ccd3;background:#fff;border-radius:6px;cursor:pointer;min-width:32px">÷</button>'+
      '</span>';
    wrapper.insertBefore(opsEl,el);

    statusEl=document.createElement('div');
    statusEl.className='re-status';
    statusEl.style.cssText='font-size:12px;min-height:16px;color:#b45454;margin:4px 0';
    wrapper.insertBefore(statusEl,el);

    opsEl.addEventListener('click',function(e){
      var b=e.target.closest('button[data-op]'); if(!b||b.disabled) return;
      insertAtCaret(b.getAttribute('data-op'));
    });
    opsEl.querySelector('#re-btn-sub').addEventListener('click',function(){
      addSubtotalRow('รวม (พิมพ์ = แล้วคลิก cell)','');
      if(statusEl){ statusEl.textContent='แถว Subtotal เพิ่มแล้ว — ดับเบิลคลิก → = → คลิก cell'; }
    });

    var saved=loadState(_currentSeedHash);
    init(seedData, saved);

    /* wire save on change */
    var _origChange=jss&&jss.options&&jss.options.onchange;
    /* auto-persist every change */
    var _savedOnChange=function(instance,cell,x,y,value){
      saveState(_currentSeedHash);
    };
    if(hostEl){
      /* attach as secondary listener via jss custom event not available in CE — use MutationObserver instead */
      var mo=new MutationObserver(function(){ saveState(_currentSeedHash); });
      mo.observe(hostEl,{childList:true,subtree:true,characterData:true});
    }

    /* expose test API */
    _exposeAPI();
  }

  function unmount(){
    if(opsEl){ try{ opsEl.remove(); }catch(e){} opsEl=null; }
    if(statusEl){ try{ statusEl.remove(); }catch(e){} statusEl=null; }
    if(hostEl){ hostEl.innerHTML=''; }
    jss=null; hostEl=null;
    pickerActive=false; editorInput=null; editorCellX=-1; editorCellY=-1;
    rowIds=[]; subMeta={}; rowSign={}; stCounter=0; baseline=[];
    _currentSeed=null; _currentSeedHash=null; _currentRows=null;
  }

  /* ---------- test automation API (window.ReportEditAPI) ---------- */
  function _exposeAPI(){
    window.ReportEditAPI={
      reset: function(rows){
        var srcRows=rows&&rows.length
          ? rows
          : DEFAULT_SEED.map(function(r){return {name:r[0],area:r[1],sign:1};});
        var seedData=srcRows.map(function(r){return [r.name,r.area];});
        /* clear persistence for this seed so reset is clean */
        try{ localStorage.removeItem(lsKey(makeHash(srcRows))); }catch(e){}
        _currentRows=srcRows;
        _currentSeed=seedData;
        _currentSeedHash=makeHash(srcRows);
        baseline=seedData.map(function(r){return r[1];});
        rowIds=[]; subMeta={}; rowSign={}; stCounter=0;
        /* re-mount into same hostEl */
        if(hostEl){
          hostEl.innerHTML='';
          init(seedData,null);
        }
      },
      seedHash: function(){ return _currentSeedHash; },   /* B-3/B-10-in-passing test hook */
      openEditor: function(x,y){
        var td=hostEl&&hostEl.querySelector('td[data-x="'+x+'"][data-y="'+y+'"]');
        if(!td) return false;
        jss.openEditor(td);
        return !!editorInput;
      },
      typeIntoEditor: function(text){
        if(!editorInput) return false;
        var s=editorInput.selectionStart,e=editorInput.selectionEnd;
        if(s==null) s=editorInput.value.length;
        if(e==null) e=editorInput.value.length;
        editorInput.value=editorInput.value.slice(0,s)+text+editorInput.value.slice(e);
        var pos=s+text.length;
        editorInput.selectionStart=editorInput.selectionEnd=pos;
        editorInput.dispatchEvent(new Event('input',{bubbles:true}));
        return true;
      },
      clickCell: function(x,y){
        var td=hostEl&&hostEl.querySelector('td[data-x="'+x+'"][data-y="'+y+'"]');
        if(!td) return false;
        var rect=td.getBoundingClientRect();
        td.dispatchEvent(new MouseEvent('mousedown',{bubbles:true,cancelable:true,
          clientX:rect.left+5,clientY:rect.top+5,button:0}));
        return true;
      },
      clickOp: function(op){
        var b=opsEl&&opsEl.querySelector('button[data-op="'+op+'"]');
        if(!b||b.disabled) return false;
        b.click(); return true;
      },
      commitEditor: function(){
        if(!editorInput) return false;
        var inp=editorInput;
        inp.dispatchEvent(new KeyboardEvent('keydown',{bubbles:true,cancelable:true,key:'Enter',code:'Enter',keyCode:13,which:13}));
        inp.dispatchEvent(new KeyboardEvent('keyup',{bubbles:true,cancelable:true,key:'Enter',code:'Enter',keyCode:13,which:13}));
        try{ inp.blur(); }catch(e){}
        return true;
      },
      get: function(cell){ return parseFloat(jss.getValue(cell,true)); },
      rawGet: function(cell){ return jss.getValue(cell,false); },
      deleteRow: function(idx){ doDeleteRow(idx); },
      insertSubtotalFormula: function(label,formula){ addSubtotalRow(label,formula); },
      rowIdsSnapshot: function(){ return rowIds.slice(); },
      subMetaOf: function(rowIdx){ var m=subMeta[rowIds[rowIdx]]; return m?JSON.parse(JSON.stringify(m)):null; },
      isDropped: function(cell){
        var st=jss.getStyle(cell);
        return /ffe0e0|255,\s*224,\s*224/.test((st&&st['background-color'])||(typeof st==='string'?st:'')||'');
      },
      editorValue: function(){ return editorInput?editorInput.value:null; },
      pickerActive: function(){ return pickerActive; }
    };
  }

  return {mount:mount, unmount:unmount};
})();
