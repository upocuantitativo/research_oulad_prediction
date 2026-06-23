/* OULAD MPI decision-support dashboard — interactivity & charts (ECharts). */
(function () {
  "use strict";
  var D = window.DATA;
  var charts = {};

  /* ---------- theme ---------- */
  function cssVar(n){ return getComputedStyle(document.documentElement).getPropertyValue(n).trim(); }
  function palette(){
    return {
      ink: cssVar('--ink'), muted: cssVar('--muted'), line: cssVar('--line'),
      accent: cssVar('--accent'), accent2: cssVar('--accent2'),
      good: cssVar('--good'), warn: cssVar('--warn'), bad: cssVar('--bad'),
      card: cssVar('--card')
    };
  }
  var saved = localStorage.getItem('oulad-theme');
  if (saved) document.documentElement.setAttribute('data-theme', saved);
  function syncBtn(){ document.getElementById('themeBtn').textContent =
    document.documentElement.getAttribute('data-theme') === 'dark' ? '☀️' : '🌙'; }
  syncBtn();
  document.getElementById('themeBtn').addEventListener('click', function(){
    var cur = document.documentElement.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', cur);
    localStorage.setItem('oulad-theme', cur); syncBtn();
    setTimeout(renderAll, 60);
  });

  /* ---------- KPI count-up ---------- */
  function animateCount(el){
    var target = parseFloat(el.dataset.count), dec = parseInt(el.dataset.dec || '0', 10);
    var suf = el.dataset.suffix || '', pre = el.dataset.prefix || '', t0 = null, dur = 1300;
    function step(ts){
      if(!t0) t0 = ts; var p = Math.min((ts - t0)/dur, 1);
      var e = 1 - Math.pow(1 - p, 3); // easeOutCubic
      var val = target * e;
      el.textContent = pre + (dec ? val.toFixed(dec) : Math.round(val).toLocaleString('en-US')) + suf;
      if(p < 1) requestAnimationFrame(step);
      else el.textContent = pre + (dec ? target.toFixed(dec) : target.toLocaleString('en-US')) + suf;
    }
    requestAnimationFrame(step);
  }
  var io = new IntersectionObserver(function(es){
    es.forEach(function(e){ if(e.isIntersecting){ animateCount(e.target); io.unobserve(e.target); } });
  }, {threshold:.5});
  document.querySelectorAll('[data-count]').forEach(function(el){ io.observe(el); });

  function mk(id){ var c = echarts.init(document.getElementById(id)); charts[id] = c; return c; }
  var baseGrid = {left:8,right:18,top:24,bottom:8,containLabel:true};
  function axisStyle(p){ return {
    axisLine:{lineStyle:{color:p.line}}, axisTick:{show:false},
    axisLabel:{color:p.muted}, splitLine:{lineStyle:{color:p.line,type:'dashed'}}
  };}

  /* ================= EARLY-WARNING ================= */
  var selWeekIdx = 3; // start at week 16
  function tier(auc){
    if(auc >= 0.90) return {t:'High confidence', cls:'b-high', tierTxt:'High',
      chan:'Escalate to human tutoring', act:'Confidence is high enough to commit scarce tutoring resources. <b>Prioritise flagged students for one-to-one outreach</b> and personalised study plans.'};
    if(auc >= 0.82) return {t:'Usable triage', cls:'b-mid', tierTxt:'Usable',
      chan:'Tutor outreach + nudges', act:'Good enough to triage. <b>Send automated nudges to all flagged students and shortlist the highest-risk for tutor contact</b>, then re-check next checkpoint.'};
    return {t:'Too early', cls:'b-low', tierTxt:'Low',
      chan:'Automated nudges only', act:'Signal is still weak — flags are unreliable. <b>Use light-touch automated nudges only</b> and avoid costly interventions until more behaviour accrues.'};
  }
  function renderEarly(){
    var p = palette(), c = charts.earlyChart || mk('earlyChart');
    var pts = D.early.weeks.map(function(w,i){
      var a = D.early.auc[i];
      var col = a>=0.90 ? p.good : (a>=0.82 ? p.warn : p.bad);
      return {value:[w,a], itemStyle:{color: i===selWeekIdx ? p.accent2 : col,
        borderColor:'#fff', borderWidth: i===selWeekIdx?3:1.5},
        symbolSize: i===selWeekIdx ? 18 : 10};
    });
    c.setOption({
      grid: baseGrid, animationDuration:600,
      tooltip:{trigger:'axis', valueFormatter:function(v){return (+v).toFixed(3);}},
      xAxis: Object.assign({type:'value', min:2, max:34, interval:4, name:'Course week',
        nameLocation:'middle', nameGap:30, nameTextStyle:{color:p.muted}}, axisStyle(p)),
      yAxis: Object.assign({type:'value', min:0.62, max:0.99, name:'ROC-AUC',
        nameTextStyle:{color:p.muted}}, axisStyle(p)),
      series:[
        {type:'line', smooth:true, symbol:'none', lineStyle:{width:3,color:p.accent},
         areaStyle:{color:'rgba(37,99,235,.10)'}, data:D.early.weeks.map(function(w,i){return [w,D.early.auc[i]];}), z:1},
        {type:'scatter', data:pts, z:3,
         markLine:{silent:true, symbol:'none', lineStyle:{color:p.good,type:'dashed'},
           data:[{yAxis:0.90, label:{formatter:'high-confidence ≥ 0.90', color:p.good, position:'insideStartTop'}}]}}
      ]
    });
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
    var p = palette(), c = charts.driverChart || mk('driverChart');
    var fam = {behavioural:p.accent, MPI:p.accent2, demographic:p.muted};
    var rows = D.drivers.slice().sort(function(a,b){ return a[impKey]-b[impKey]; });
    c.setOption({
      grid: Object.assign({}, baseGrid, {left:8,right:40}), animationDuration:600,
      tooltip:{trigger:'item', formatter:function(o){return o.name+'<br/><b>'+(+o.value).toFixed(4)+'</b> ('+rows[o.dataIndex].fam+')';}},
      xAxis: Object.assign({type:'value', name: impKey==='shap'?'mean |SHAP|':'permutation importance',
        nameLocation:'middle', nameGap:28, nameTextStyle:{color:p.muted}}, axisStyle(p)),
      yAxis: Object.assign({type:'category', data:rows.map(function(r){return r.f;})}, axisStyle(p),
        {splitLine:{show:false}}),
      series:[{type:'bar', data:rows.map(function(r){return {value:Math.max(r[impKey],0), itemStyle:{color:fam[r.fam], borderRadius:[0,6,6,0]}};}),
        barWidth:'62%', label:{show:true, position:'right', color:p.muted,
          formatter:function(o){return (+o.value).toFixed(3);}}}]
    });
  }
  document.querySelectorAll('#impSeg button').forEach(function(btn){
    btn.addEventListener('click', function(){
      document.querySelectorAll('#impSeg button').forEach(function(b){b.classList.remove('on');});
      btn.classList.add('on'); impKey = btn.dataset.k; renderDrivers();
    });
  });

  /* ================= MPI RADAR ================= */
  var mpiOn = {Distinction:true, Pass:true, Fail:true, Withdrawn:true};
  var ocol = function(p){ return {Distinction:p.good, Pass:p.accent, Fail:p.warn, Withdrawn:p.bad}; };
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
    var p = palette(), c = charts.radarChart || mk('radarChart'), col = ocol(p);
    var ind = D.mpi.dims.map(function(d){ return {name:d, max:0.42, min:-0.32}; });
    var series = Object.keys(D.mpi.outcomes).filter(function(o){return mpiOn[o];}).map(function(o){
      return {value:D.mpi.outcomes[o], name:o,
        lineStyle:{color:col[o],width:2.4}, itemStyle:{color:col[o]}, areaStyle:{color:col[o],opacity:.07}};
    });
    c.setOption({
      tooltip:{}, legend:{top:0, textStyle:{color:p.muted}, data:Object.keys(D.mpi.outcomes).filter(function(o){return mpiOn[o];})},
      color:Object.keys(D.mpi.outcomes).filter(function(o){return mpiOn[o];}).map(function(o){return col[o];}),
      radar:{indicator:ind, center:['50%','56%'], radius:'66%',
        axisName:{color:p.ink, fontSize:12},
        splitLine:{lineStyle:{color:p.line}}, splitArea:{areaStyle:{color:['transparent']}},
        axisLine:{lineStyle:{color:p.line}}},
      series:[{type:'radar', data:series, animationDuration:600}]
    });
  }

  /* ================= FAIRNESS ================= */
  var mitKey = 'before';
  function renderFair(){
    var p = palette(), c = charts.fairChart || mk('fairChart');
    var m = D.mitigation[mitKey];
    var groups = ['Prior attempts > 0','Prior attempts = 0'];
    var tpr = [m.tpr_dis, m.tpr_adv];
    c.setOption({
      grid: Object.assign({}, baseGrid, {top:34}), animationDuration:600,
      tooltip:{trigger:'axis', valueFormatter:function(v){return (+v*100).toFixed(1)+'%';}},
      legend:{show:false},
      xAxis: Object.assign({type:'category', data:groups}, axisStyle(p)),
      yAxis: Object.assign({type:'value', min:0.80, max:1.0, name:'True-positive rate (recall)',
        nameTextStyle:{color:p.muted}, axisLabel:{color:p.muted, formatter:function(v){return Math.round(v*100)+'%';}}}, axisStyle(p)),
      series:[{type:'bar', barWidth:'48%',
        data:[{value:tpr[0], itemStyle:{color:p.warn,borderRadius:[8,8,0,0]}},
              {value:tpr[1], itemStyle:{color:p.accent,borderRadius:[8,8,0,0]}}],
        label:{show:true, position:'top', color:p.ink, formatter:function(o){return (o.value*100).toFixed(1)+'%';}},
        markLine:{silent:true, symbol:'none', lineStyle:{color:p.bad, type:'dashed'},
          label:{formatter:'gap '+ (m.eo).toFixed(3), color:p.bad},
          data:[[{xAxis:0, yAxis:tpr[0]},{xAxis:1, yAxis:tpr[1]}]]}}]
    });
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
    var p = palette(), c = charts.donutChart || mk('donutChart');
    var col = {Distinction:p.good, Pass:p.accent, Fail:p.warn, Withdrawn:p.bad};
    var data = Object.keys(D.final_result).map(function(k){
      return {name:k, value:D.final_result[k], itemStyle:{color:col[k]}};
    });
    c.setOption({
      tooltip:{trigger:'item', formatter:function(o){return o.name+': '+o.value+'%  ('+D.final_counts[o.name].toLocaleString('en-US')+')';}},
      legend:{bottom:0, textStyle:{color:p.muted}},
      series:[{type:'pie', radius:['52%','78%'], center:['50%','46%'], avoidLabelOverlap:true,
        itemStyle:{borderColor:p.card, borderWidth:3},
        label:{formatter:'{b}\n{d}%', color:p.ink}, data:data, animationDuration:700,
        emphasis:{scale:true, scaleSize:6}}]
    });
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
    var p = palette(), c = charts.dispChart || mk('dispChart');
    var rows = D.disparity[dispKey];
    c.setOption({
      grid: Object.assign({}, baseGrid, {left:8,right:46,top:10}), animationDuration:600,
      tooltip:{trigger:'item', valueFormatter:function(v){return (v*100).toFixed(1)+'%';}},
      xAxis: Object.assign({type:'value', max:0.8, axisLabel:{color:p.muted, formatter:function(v){return Math.round(v*100)+'%';}}}, axisStyle(p)),
      yAxis: Object.assign({type:'category', data:rows.map(function(r){return r[0];}).reverse()}, axisStyle(p), {splitLine:{show:false}}),
      series:[{type:'bar', barWidth:'58%',
        data:rows.map(function(r){return r[1];}).reverse().map(function(v){
          return {value:v, itemStyle:{color: v>=0.6?p.bad:(v>=0.5?p.warn:p.accent), borderRadius:[0,6,6,0]}};}),
        label:{show:true, position:'right', color:p.muted, formatter:function(o){return (o.value*100).toFixed(1)+'%';}}}]
    });
  }

  /* ---------- orchestrate ---------- */
  function renderAll(){
    renderEarly(); renderDrivers(); renderRadar(); renderFair(); renderDonut(); renderDisp();
  }
  document.getElementById('weekSlider').value = selWeekIdx;
  renderAll(); updateReadout();
  window.addEventListener('resize', function(){ Object.keys(charts).forEach(function(k){ charts[k].resize(); }); });
})();
