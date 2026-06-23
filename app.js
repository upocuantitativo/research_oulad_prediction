/* OULAD MPI decision-support companion — interactivity & charts (ECharts), academic skin. */
(function () {
  "use strict";
  var D = window.DATA;
  var charts = {};

  function cssVar(n){ return getComputedStyle(document.documentElement).getPropertyValue(n).trim(); }
  var P = {
    ink:cssVar('--ink'), muted:cssVar('--muted'), line:'#bdbdb4', grid:'#ececE4', card:cssVar('--card'),
    navy:cssVar('--navy'), maroon:cssVar('--maroon'), teal:cssVar('--teal'), ochre:cssVar('--ochre'), gray:cssVar('--gray'),
    good:cssVar('--good'), warn:cssVar('--warn'), bad:cssVar('--bad')
  };
  var SERIF = getComputedStyle(document.body).fontFamily || 'Georgia, serif';

  /* ---------- static KPI values (academic: no count-up) ---------- */
  document.querySelectorAll('[data-count]').forEach(function(el){
    var t = parseFloat(el.dataset.count), dec = parseInt(el.dataset.dec || '0', 10);
    var suf = el.dataset.suffix || '', pre = el.dataset.prefix || '';
    el.innerHTML = pre + (dec ? t.toFixed(dec) : t.toLocaleString('en-US')) + suf;
  });

  function mk(id){ var c = echarts.init(document.getElementById(id)); charts[id] = c; return c; }
  var baseGrid = {left:8,right:18,top:24,bottom:8,containLabel:true};
  function root(opt){ opt.textStyle = {fontFamily:SERIF, color:P.ink}; return opt; }
  function axisStyle(){ return {
    axisLine:{lineStyle:{color:P.line}}, axisTick:{show:false},
    axisLabel:{color:P.muted, fontFamily:SERIF}, nameTextStyle:{color:P.muted, fontFamily:SERIF},
    splitLine:{lineStyle:{color:P.grid, type:'solid'}}
  };}

  /* ================= EARLY-WARNING ================= */
  var selWeekIdx = 3; // week 16
  function tier(auc){
    if(auc >= 0.90) return {t:'High confidence', cls:'b-high', tierTxt:'High',
      chan:'Escalate to human tutoring', act:'Confidence is high enough to commit scarce tutoring resources. <b>Prioritise flagged students for one-to-one outreach</b> and personalised study plans.'};
    if(auc >= 0.82) return {t:'Usable triage', cls:'b-mid', tierTxt:'Usable',
      chan:'Tutor outreach + nudges', act:'Good enough to triage. <b>Send automated nudges to all flagged students and shortlist the highest-risk for tutor contact</b>, then re-check next checkpoint.'};
    return {t:'Too early', cls:'b-low', tierTxt:'Low',
      chan:'Automated nudges only', act:'Signal is still weak — flags are unreliable. <b>Use light-touch automated nudges only</b> and avoid costly interventions until more behaviour accrues.'};
  }
  function tierColor(a){ return a>=0.90 ? P.teal : (a>=0.82 ? P.ochre : P.maroon); }
  function renderEarly(){
    var c = charts.earlyChart || mk('earlyChart');
    var pts = D.early.weeks.map(function(w,i){
      var a = D.early.auc[i], sel = i===selWeekIdx;
      return {value:[w,a], itemStyle:{color: sel ? P.maroon : tierColor(a), borderColor:'#fff', borderWidth: sel?2.5:1.2},
        symbolSize: sel ? 16 : 9};
    });
    c.setOption(root({
      grid: baseGrid, animationDuration:500,
      tooltip:{trigger:'axis', textStyle:{fontFamily:SERIF}, valueFormatter:function(v){return (+v).toFixed(3);}},
      xAxis: Object.assign({type:'value', min:2, max:34, interval:4, name:'Course week',
        nameLocation:'middle', nameGap:30}, axisStyle()),
      yAxis: Object.assign({type:'value', min:0.62, max:0.99, name:'ROC-AUC'}, axisStyle()),
      series:[
        {type:'line', smooth:false, symbol:'none', lineStyle:{width:1.8,color:P.navy},
         areaStyle:{color:'rgba(31,59,115,.05)'}, data:D.early.weeks.map(function(w,i){return [w,D.early.auc[i]];}), z:1},
        {type:'scatter', data:pts, z:3,
         markLine:{silent:true, symbol:'none', lineStyle:{color:P.teal,type:'dashed'},
           data:[{yAxis:0.90, label:{formatter:'high-confidence ≥ 0.90', color:P.teal, fontFamily:SERIF, position:'insideStartTop'}}]}}
      ]
    }));
  }
  function updateReadout(){
    var w = D.early.weeks[selWeekIdx], a = D.early.auc[selWeekIdx], info = tier(a);
    document.getElementById('roWeek').textContent = 'week ' + w;
    document.getElementById('roAuc').textContent = a.toFixed(3);
    var b = document.getElementById('roBadge'); b.textContent = info.t; b.className = 'badge ' + info.cls;
    document.getElementById('roAction').innerHTML = info.act;
    document.getElementById('kAuc').textContent = a.toFixed(3);
    document.getElementById('kTier').textContent = info.tierTxt;
    document.getElementById('kChan').textContent = info.chan;
  }
  document.getElementById('weekSlider').addEventListener('input', function(e){
    selWeekIdx = +e.target.value; renderEarly(); updateReadout();
  });

  /* ================= DRIVERS ================= */
  var impKey = 'shap';
  function renderDrivers(){
    var c = charts.driverChart || mk('driverChart');
    var fam = {behavioural:P.navy, MPI:P.maroon, demographic:P.gray};
    var rows = D.drivers.slice().sort(function(a,b){ return a[impKey]-b[impKey]; });
    c.setOption(root({
      grid: Object.assign({}, baseGrid, {left:8,right:46}), animationDuration:500,
      tooltip:{trigger:'item', textStyle:{fontFamily:SERIF}, formatter:function(o){return o.name+'<br/><b>'+(+o.value).toFixed(4)+'</b> ('+rows[o.dataIndex].fam+')';}},
      xAxis: Object.assign({type:'value', name: impKey==='shap'?'mean |SHAP|':'permutation importance',
        nameLocation:'middle', nameGap:28}, axisStyle()),
      yAxis: Object.assign({type:'category', data:rows.map(function(r){return r.f;})}, axisStyle(), {splitLine:{show:false}}),
      series:[{type:'bar', data:rows.map(function(r){return {value:Math.max(r[impKey],0), itemStyle:{color:fam[r.fam]}};}),
        barWidth:'58%', label:{show:true, position:'right', color:P.muted, fontFamily:SERIF,
          formatter:function(o){return (+o.value).toFixed(3);}}}]
    }));
  }
  document.querySelectorAll('#impSeg button').forEach(function(btn){
    btn.addEventListener('click', function(){
      document.querySelectorAll('#impSeg button').forEach(function(b){b.classList.remove('on');});
      btn.classList.add('on'); impKey = btn.dataset.k; renderDrivers();
    });
  });

  /* ================= MPI RADAR ================= */
  var mpiOn = {Distinction:true, Pass:true, Fail:true, Withdrawn:true};
  var OCOL = {Distinction:P.navy, Pass:P.teal, Fail:P.ochre, Withdrawn:P.maroon};
  (function buildChecks(){
    var box = document.getElementById('mpiChecks');
    ['Distinction','Pass','Fail','Withdrawn'].forEach(function(o){
      var l = document.createElement('label'); l.className='chk';
      l.innerHTML = '<input type="checkbox" checked> '+o;
      l.querySelector('input').addEventListener('change', function(e){ mpiOn[o]=e.target.checked; renderRadar(); });
      box.appendChild(l);
    });
  })();
  function renderRadar(){
    var c = charts.radarChart || mk('radarChart');
    var ind = D.mpi.dims.map(function(d){ return {name:d, max:0.42, min:-0.32}; });
    var keys = Object.keys(D.mpi.outcomes).filter(function(o){return mpiOn[o];});
    var series = keys.map(function(o){
      return {value:D.mpi.outcomes[o], name:o,
        lineStyle:{color:OCOL[o],width:2}, itemStyle:{color:OCOL[o]}, areaStyle:{color:OCOL[o],opacity:.05}};
    });
    c.setOption(root({
      tooltip:{textStyle:{fontFamily:SERIF}}, legend:{top:0, textStyle:{color:P.muted, fontFamily:SERIF}, data:keys},
      color:keys.map(function(o){return OCOL[o];}),
      radar:{indicator:ind, center:['50%','56%'], radius:'66%',
        axisName:{color:P.ink, fontFamily:SERIF, fontSize:12},
        splitLine:{lineStyle:{color:P.grid}}, splitArea:{areaStyle:{color:['transparent']}},
        axisLine:{lineStyle:{color:P.grid}}},
      series:[{type:'radar', data:series, animationDuration:500}]
    }));
  }

  /* ================= FAIRNESS ================= */
  var mitKey = 'before';
  function renderFair(){
    var c = charts.fairChart || mk('fairChart');
    var m = D.mitigation[mitKey];
    var groups = ['Prior attempts > 0','Prior attempts = 0'];
    var tpr = [m.tpr_dis, m.tpr_adv];
    c.setOption(root({
      grid: Object.assign({}, baseGrid, {top:34}), animationDuration:500,
      tooltip:{trigger:'axis', textStyle:{fontFamily:SERIF}, valueFormatter:function(v){return (+v*100).toFixed(1)+'%';}},
      xAxis: Object.assign({type:'category', data:groups}, axisStyle()),
      yAxis: Object.assign({type:'value', min:0.80, max:1.0, name:'True-positive rate (recall)',
        axisLabel:{color:P.muted, fontFamily:SERIF, formatter:function(v){return Math.round(v*100)+'%';}}}, axisStyle()),
      series:[{type:'bar', barWidth:'46%',
        data:[{value:tpr[0], itemStyle:{color:P.ochre}}, {value:tpr[1], itemStyle:{color:P.navy}}],
        label:{show:true, position:'top', color:P.ink, fontFamily:SERIF, formatter:function(o){return (o.value*100).toFixed(1)+'%';}},
        markLine:{silent:true, symbol:'none', lineStyle:{color:P.maroon, type:'dashed'},
          label:{formatter:'gap '+ (m.eo).toFixed(3), color:P.maroon, fontFamily:SERIF},
          data:[[{xAxis:0, yAxis:tpr[0]},{xAxis:1, yAxis:tpr[1]}]]}}]
    }));
    document.getElementById('eoVal').textContent = m.eo.toFixed(3);
    document.getElementById('eoVal').className = 'v ' + (mitKey==='after'?'delta-up':'');
    document.getElementById('accVal').textContent = (mitKey==='before'?'91.5%':'91.3%');
    document.getElementById('mitNote').textContent = mitKey==='after'
      ? D.mitigation.method + ' — equal opportunity restored (ΔTPR ≈ 0).'
      : 'Repeat-attempt students who actually pass are missed 7.7 pp more often than first-time students.';
  }
  document.querySelectorAll('#mitSeg button').forEach(function(btn){
    btn.addEventListener('click', function(){
      document.querySelectorAll('#mitSeg button').forEach(function(b){b.classList.remove('on');});
      btn.classList.add('on'); mitKey = btn.dataset.k; renderFair();
    });
  });

  /* ================= OUTCOMES DONUT ================= */
  function renderDonut(){
    var c = charts.donutChart || mk('donutChart');
    var data = Object.keys(D.final_result).map(function(k){
      return {name:k, value:D.final_result[k], itemStyle:{color:OCOL[k]}};
    });
    c.setOption(root({
      tooltip:{trigger:'item', textStyle:{fontFamily:SERIF}, formatter:function(o){return o.name+': '+o.value+'%  ('+D.final_counts[o.name].toLocaleString('en-US')+')';}},
      legend:{bottom:0, textStyle:{color:P.muted, fontFamily:SERIF}},
      series:[{type:'pie', radius:['50%','74%'], center:['50%','45%'], avoidLabelOverlap:true,
        itemStyle:{borderColor:P.card, borderWidth:2},
        label:{formatter:'{b}\n{d}%', color:P.ink, fontFamily:SERIF}, data:data, animationDuration:600,
        emphasis:{scale:true, scaleSize:5}}]
    }));
  }

  /* ================= DISPARITY ================= */
  var dispKeys = Object.keys(D.disparity), dispKey = dispKeys[0];
  (function buildDispSeg(){
    var seg = document.getElementById('dispSeg');
    dispKeys.forEach(function(k,i){
      var b = document.createElement('button'); b.textContent = k; if(i===0) b.classList.add('on');
      b.addEventListener('click', function(){
        seg.querySelectorAll('button').forEach(function(x){x.classList.remove('on');});
        b.classList.add('on'); dispKey = k; renderDisp();
      });
      seg.appendChild(b);
    });
  })();
  function renderDisp(){
    var c = charts.dispChart || mk('dispChart');
    var rows = D.disparity[dispKey];
    c.setOption(root({
      grid: Object.assign({}, baseGrid, {left:8,right:46,top:10}), animationDuration:500,
      tooltip:{trigger:'item', textStyle:{fontFamily:SERIF}, valueFormatter:function(v){return (v*100).toFixed(1)+'%';}},
      xAxis: Object.assign({type:'value', max:0.8, axisLabel:{color:P.muted, fontFamily:SERIF, formatter:function(v){return Math.round(v*100)+'%';}}}, axisStyle()),
      yAxis: Object.assign({type:'category', data:rows.map(function(r){return r[0];}).reverse()}, axisStyle(), {splitLine:{show:false}}),
      series:[{type:'bar', barWidth:'56%',
        data:rows.map(function(r){return r[1];}).reverse().map(function(v){
          return {value:v, itemStyle:{color: v>=0.6?P.maroon:(v>=0.5?P.ochre:P.navy)}};}),
        label:{show:true, position:'right', color:P.muted, fontFamily:SERIF, formatter:function(o){return (o.value*100).toFixed(1)+'%';}}}]
    }));
  }

  /* ---------- orchestrate ---------- */
  document.getElementById('weekSlider').value = selWeekIdx;
  renderEarly(); renderDrivers(); renderRadar(); renderFair(); renderDonut(); renderDisp(); updateReadout();
  window.addEventListener('resize', function(){ Object.keys(charts).forEach(function(k){ charts[k].resize(); }); });
})();
