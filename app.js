/* OULAD MPI decision-support companion — scientific monochrome figures (ECharts).
   Grayscale only; series encoded by marker shape, line style, hatching and error bars. */
(function () {
  "use strict";
  var D = window.DATA;
  var charts = {};
  var SERIF = getComputedStyle(document.body).fontFamily || 'Georgia, serif';
  var GR = { ink:'#1a1a1a', d:'#3a3a3a', m:'#6e6e6e', l:'#9a9a9a', xl:'#c4c4c4',
             band:'#f1f1f1', grid:'#e8e8e8', minor:'#f4f4f4', axis:'#8c8c8c' };

  /* static KPI values */
  document.querySelectorAll('[data-count]').forEach(function(el){
    var t = parseFloat(el.dataset.count), dec = parseInt(el.dataset.dec || '0', 10);
    var suf = el.dataset.suffix || '', pre = el.dataset.prefix || '';
    el.innerHTML = pre + (dec ? t.toFixed(dec) : t.toLocaleString('en-US')) + suf;
  });

  function mk(id){ var c = echarts.init(document.getElementById(id)); charts[id] = c; return c; }
  function root(opt){ opt.textStyle = {fontFamily:SERIF, color:GR.ink}; return opt; }
  function axisStyle(){ return {
    axisLine:{lineStyle:{color:GR.axis}}, axisTick:{lineStyle:{color:GR.axis}},
    axisLabel:{color:GR.m, fontFamily:SERIF}, nameTextStyle:{color:GR.m, fontFamily:SERIF, fontStyle:'italic'},
    splitLine:{lineStyle:{color:GR.grid}}
  };}

  /* ============ FIGURE 1 · EARLY WARNING ============ */
  var selWeekIdx = 3;
  function tier(a){
    if(a>=0.90) return {t:'High confidence', cls:'b-high', tierTxt:'High', chan:'Escalate to human tutoring',
      act:'Confidence is high enough to commit scarce tutoring resources. <b>Prioritise flagged students for one-to-one outreach</b> and personalised study plans.'};
    if(a>=0.82) return {t:'Usable triage', cls:'b-mid', tierTxt:'Usable', chan:'Tutor outreach + nudges',
      act:'Good enough to triage. <b>Send automated nudges to all flagged students and shortlist the highest-risk for tutor contact</b>, then re-check next checkpoint.'};
    return {t:'Too early', cls:'b-low', tierTxt:'Low', chan:'Automated nudges only',
      act:'Signal is still weak — flags are unreliable. <b>Use light-touch automated nudges only</b> and avoid costly interventions until more behaviour accrues.'};
  }
  function renderEarly(){
    var c = charts.earlyChart || mk('earlyChart');
    var wk = D.early.weeks, au = D.early.auc, w = wk[selWeekIdx], a = au[selWeekIdx];
    c.setOption(root({
      grid:{left:10,right:18,top:18,bottom:42,containLabel:true}, animationDuration:450,
      tooltip:{trigger:'axis', textStyle:{fontFamily:SERIF}, valueFormatter:function(v){return (+v).toFixed(3);}},
      xAxis: Object.assign({type:'value', min:2, max:34, interval:4, name:'course week (cumulative behaviour)',
        nameLocation:'middle', nameGap:30, minorTick:{show:true, splitNumber:4},
        minorSplitLine:{show:true, lineStyle:{color:GR.minor}}}, axisStyle()),
      yAxis: Object.assign({type:'value', min:0.62, max:0.99, name:'test ROC-AUC',
        minorTick:{show:true}, minorSplitLine:{show:true, lineStyle:{color:GR.minor}}}, axisStyle()),
      series:[{
        type:'line', data:wk.map(function(x,i){return [x,au[i]];}), smooth:false, z:3,
        lineStyle:{color:GR.ink, width:1.6}, symbol:'circle', symbolSize:7,
        itemStyle:{color:'#fff', borderColor:GR.ink, borderWidth:1.4},
        label:{show:true, position:'top', distance:7, color:GR.m, fontFamily:SERIF, fontSize:10,
          formatter:function(p){return p.value[1].toFixed(3);}},
        markArea:{silent:true, itemStyle:{color:GR.band}, data:[[{yAxis:0.90},{yAxis:0.99}]]},
        markLine:{silent:true, symbol:'none',
          data:[
            {yAxis:0.90, lineStyle:{color:GR.m, type:'dashed'}, label:{formatter:'high-confidence  AUC ≥ 0.90', color:GR.m, fontFamily:SERIF, position:'insideStartTop'}},
            {xAxis:w, lineStyle:{color:GR.d, type:[5,4]}, label:{formatter:'wk '+w, color:GR.d, fontFamily:SERIF}},
            {yAxis:a, lineStyle:{color:GR.d, type:[5,4]}, label:{formatter:a.toFixed(3), color:GR.d, fontFamily:SERIF, position:'insideEndTop'}}
          ]}
      },{
        type:'scatter', data:[[w,a]], symbol:'circle', symbolSize:13, z:5,
        itemStyle:{color:GR.ink, borderColor:'#fff', borderWidth:1.5}
      }]
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

  /* ============ FIGURE 2 · DRIVERS (Cleveland dot plot + error bars) ============ */
  var impKey = 'shap', dRows = [];
  function tri(x,y,s){ return {type:'polygon', shape:{points:[[x,y-s],[x-s,y+s*0.85],[x+s,y+s*0.85]]}}; }
  function driverRender(params, api){
    var v = api.value(0), cat = api.value(1), pc = api.coord([v,cat]);
    var r = dRows[params.dataIndex], ch = [], labelX = pc[0];
    if(impKey==='perm' && r.sd>0){
      var p0 = api.coord([v-r.sd,cat]), p1 = api.coord([v+r.sd,cat]); labelX = p1[0];
      ch.push({type:'line', shape:{x1:p0[0],y1:p0[1],x2:p1[0],y2:p1[1]}, style:{stroke:GR.d, lineWidth:1}});
      ch.push({type:'line', shape:{x1:p0[0],y1:p0[1]-4,x2:p0[0],y2:p0[1]+4}, style:{stroke:GR.d, lineWidth:1}});
      ch.push({type:'line', shape:{x1:p1[0],y1:p1[1]-4,x2:p1[0],y2:p1[1]+4}, style:{stroke:GR.d, lineWidth:1}});
    }
    var x=pc[0], y=pc[1], m;
    if(r.fam==='behavioural'){ m={type:'circle', shape:{cx:x,cy:y,r:5}, style:{fill:GR.ink}}; }
    else if(r.fam==='MPI'){ m={type:'rect', shape:{x:x-4.6,y:y-4.6,width:9.2,height:9.2}, style:{fill:'#fff', stroke:GR.ink, lineWidth:1.5}}; }
    else { m=tri(x,y,5.6); m.style={fill:'#fff', stroke:GR.ink, lineWidth:1.5}; }
    ch.push(m);
    ch.push({type:'text', style:{text:(v<0?'−':'')+Math.abs(v).toFixed(3), x:labelX+9, y:y, fill:GR.m,
      font:'12px '+SERIF, textVerticalAlign:'middle'}});
    return {type:'group', children:ch};
  }
  function renderDrivers(){
    var rows = D.drivers.slice().sort(function(a,b){return a[impKey]-b[impKey];}); dRows = rows;
    var showErr = impKey==='perm';
    var lo = Math.min(0, Math.min.apply(null, rows.map(function(r){return r[impKey]-(showErr?r.sd:0);})));
    var hi = Math.max.apply(null, rows.map(function(r){return r[impKey]+(showErr?r.sd:0);}));
    var pad = (hi-lo)*0.16;
    var c = charts.driverChart || mk('driverChart');
    c.setOption(root({
      grid:{left:10,right:58,top:14,bottom:44,containLabel:true}, animationDuration:450,
      tooltip:{trigger:'item', textStyle:{fontFamily:SERIF}, formatter:function(p){var r=dRows[p.dataIndex];
        return '<b>'+r.f+'</b><br/>'+(impKey==='perm'?('permutation = '+r.perm.toFixed(4)+' ± '+r.sd.toFixed(4)):('mean |SHAP| = '+r.shap.toFixed(4)))+'<br/>family: '+r.fam;}},
      xAxis: Object.assign({type:'value', min:lo-pad, max:hi+pad,
        name:(impKey==='shap'?'mean |SHAP|':'permutation importance (Δ ROC-AUC)'),
        nameLocation:'middle', nameGap:28, minorTick:{show:true}, minorSplitLine:{show:true, lineStyle:{color:GR.minor}}}, axisStyle()),
      yAxis: Object.assign({type:'category', data:rows.map(function(r){return r.f;})}, axisStyle(),
        {splitLine:{show:false}, axisLabel:{color:GR.ink, fontFamily:SERIF}}),
      series:[{type:'custom', renderItem:driverRender, encode:{x:0,y:1}, z:5,
        data:rows.map(function(r){return [r[impKey], r.f];}),
        markLine:{silent:true, symbol:'none', lineStyle:{color:GR.l, type:'dashed'},
          label:{show:false}, data:[{xAxis:0}]}}]
    }));
  }
  document.querySelectorAll('#impSeg button').forEach(function(btn){
    btn.addEventListener('click', function(){
      document.querySelectorAll('#impSeg button').forEach(function(b){b.classList.remove('on');});
      btn.classList.add('on'); impKey = btn.dataset.k; renderDrivers();
    });
  });

  /* ============ FIGURE 3 · MPI RADAR (monochrome line styles) ============ */
  var mpiOn = {Distinction:true, Pass:true, Fail:true, Withdrawn:true};
  var STY = {
    Distinction:{c:'#1a1a1a', t:'solid',      s:'circle'},
    Pass:       {c:'#4a4a4a', t:'dashed',     s:'rect'},
    Fail:       {c:'#787878', t:'dotted',     s:'triangle'},
    Withdrawn:  {c:'#a2a2a2', t:[7,3,2,3],    s:'diamond'}
  };
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
    var series = keys.map(function(o){ var s=STY[o];
      return {value:D.mpi.outcomes[o], name:o, symbol:s.s, symbolSize:6,
        lineStyle:{color:s.c, width:1.8, type:s.t}, itemStyle:{color:s.c}, areaStyle:null};
    });
    c.setOption(root({
      tooltip:{textStyle:{fontFamily:SERIF}},
      legend:{top:0, textStyle:{color:GR.ink, fontFamily:SERIF}, data:keys, itemWidth:24, icon:'roundRect'},
      color:keys.map(function(o){return STY[o].c;}),
      radar:{indicator:ind, center:['50%','57%'], radius:'64%',
        axisName:{color:GR.ink, fontFamily:SERIF, fontSize:12},
        splitLine:{lineStyle:{color:GR.grid}}, splitArea:{areaStyle:{color:['#ffffff','#fafafa']}},
        axisLine:{lineStyle:{color:GR.grid}}},
      series:[{type:'radar', data:series, animationDuration:450,
        markLine:{silent:true}}]
    }));
  }

  /* ============ FIGURE 4 · FAIRNESS (dumbbell / connected-dot) ============ */
  var mitKey = 'before', fRows = [];
  function fairRender(params, api){
    var b = api.value(0), a = api.value(1), cat = api.value(2);
    var pb = api.coord([b,cat]), pa = api.coord([a,cat]), ch = [], emphB = mitKey==='before';
    ch.push({type:'line', shape:{x1:pb[0],y1:pb[1],x2:pa[0],y2:pa[1]}, style:{stroke:GR.m, lineWidth:2}});
    ch.push({type:'circle', shape:{cx:pb[0],cy:pb[1],r:emphB?7:5.5}, style:{fill:'#fff', stroke:GR.ink, lineWidth:1.7}});
    ch.push({type:'circle', shape:{cx:pa[0],cy:pa[1],r:emphB?5.5:7}, style:{fill:GR.ink, stroke:GR.ink}});
    ch.push({type:'text', style:{text:(b*100).toFixed(1)+'%', x:pb[0], y:pb[1]-13, fill:GR.m, font:'11px '+SERIF, textAlign:'center'}});
    if(Math.abs(a-b)>0.002)
      ch.push({type:'text', style:{text:(a*100).toFixed(1)+'%', x:pa[0], y:pa[1]+17, fill:GR.ink, font:'12px '+SERIF, textAlign:'center'}});
    return {type:'group', children:ch};
  }
  function renderFair(){
    var c = charts.fairChart || mk('fairChart');
    var M = D.mitigation;
    fRows = [
      {g:'Prior attempts = 0', before:M.before.tpr_adv, after:M.after.tpr_adv, n:7098},
      {g:'Prior attempts > 0', before:M.before.tpr_dis, after:M.after.tpr_dis, n:1051}
    ];
    c.setOption(root({
      grid:{left:10,right:26,top:30,bottom:46,containLabel:true}, animationDuration:450,
      tooltip:{trigger:'item', textStyle:{fontFamily:SERIF}, formatter:function(p){var r=fRows[p.dataIndex];
        return '<b>'+r.g+'</b> (n = '+r.n.toLocaleString('en-US')+')<br/>standard (0.50): '+(r.before*100).toFixed(1)+'%<br/>group-aware: '+(r.after*100).toFixed(1)+'%';}},
      xAxis: Object.assign({type:'value', min:0.84, max:1.0, name:'true-positive rate (recall on actual passers)',
        nameLocation:'middle', nameGap:30, axisLabel:{formatter:function(v){return Math.round(v*100)+'%';}, color:GR.m, fontFamily:SERIF},
        minorTick:{show:true}, minorSplitLine:{show:true, lineStyle:{color:GR.minor}}}, axisStyle()),
      yAxis: Object.assign({type:'category', data:fRows.map(function(r){return r.g;}), boundaryGap:true}, axisStyle(),
        {axisLabel:{color:GR.ink, fontFamily:SERIF}, splitLine:{show:false}}),
      series:[{type:'custom', renderItem:fairRender, encode:{x:[0,1], y:2}, z:5,
        data:fRows.map(function(r){return [r.before, r.after, r.g];})}]
    }));
    document.getElementById('eoVal').textContent = (mitKey==='before'?M.before.eo:M.after.eo).toFixed(3);
    document.getElementById('eoVal').className = 'v';
    document.getElementById('accVal').textContent = (mitKey==='before'?'91.5%':'91.3%');
    document.getElementById('mitNote').textContent = mitKey==='after'
      ? M.method + ' — equal opportunity restored (ΔTPR ≈ 0).'
      : 'Repeat-attempt students who actually pass are missed 7.7 pp more often than first-time students.';
  }
  document.querySelectorAll('#mitSeg button').forEach(function(btn){
    btn.addEventListener('click', function(){
      document.querySelectorAll('#mitSeg button').forEach(function(b){b.classList.remove('on');});
      btn.classList.add('on'); mitKey = btn.dataset.k; renderFair();
    });
  });

  /* ============ FIGURE 5 · OUTCOMES (grayscale bar + hatching) ============ */
  function renderOutcome(){
    var c = charts.outcomeChart || mk('outcomeChart');
    var order = ['Pass','Withdrawn','Fail','Distinction'];
    var shade = {Pass:'#3a3a3a', Withdrawn:'#6e6e6e', Fail:'#9a9a9a', Distinction:'#c4c4c4'};
    var rev = order.slice().reverse();
    c.setOption(root({
      aria:{enabled:true, decal:{show:true}},
      grid:{left:10,right:96,top:8,bottom:30,containLabel:true}, animationDuration:550,
      tooltip:{trigger:'item', textStyle:{fontFamily:SERIF}, formatter:function(p){return p.name+': '+p.value.toFixed(1)+'%  (n = '+D.final_counts[p.name].toLocaleString('en-US')+')';}},
      xAxis: Object.assign({type:'value', max:40, name:'% of enrolments', nameLocation:'middle', nameGap:26,
        axisLabel:{formatter:'{value}%', color:GR.m, fontFamily:SERIF}}, axisStyle()),
      yAxis: Object.assign({type:'category', data:rev}, axisStyle(), {splitLine:{show:false}, axisLabel:{color:GR.ink, fontFamily:SERIF}}),
      series:[{type:'bar', barWidth:'54%',
        data:rev.map(function(k){return {value:D.final_result[k], itemStyle:{color:shade[k], borderColor:GR.ink, borderWidth:0.8}};}),
        label:{show:true, position:'right', color:GR.ink, fontFamily:SERIF,
          formatter:function(p){return p.value.toFixed(1)+'%  (n='+D.final_counts[p.name].toLocaleString('en-US')+')';}}}]
    }));
  }

  /* ============ FIGURE 6 · DISPARITIES (sequential gray + reference line) ============ */
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
    var rows = D.disparity[dispKey], nmap = {};
    rows.forEach(function(r){ nmap[r[0]] = r[2]; });
    function shade(v){ var t=Math.max(0,Math.min(1,(v-0.34)/0.37)); var g=Math.round(205-160*t); return 'rgb('+g+','+g+','+g+')'; }
    var rev = rows.slice().reverse();
    c.setOption(root({
      grid:{left:10,right:104,top:10,bottom:34,containLabel:true}, animationDuration:450,
      tooltip:{trigger:'item', textStyle:{fontFamily:SERIF}, formatter:function(p){return p.name+'<br/>fail/withdraw rate '+(p.value*100).toFixed(1)+'%  (n = '+nmap[p.name].toLocaleString('en-US')+')';}},
      xAxis: Object.assign({type:'value', max:0.8, name:'fail / withdraw rate', nameLocation:'middle', nameGap:26,
        axisLabel:{formatter:function(v){return Math.round(v*100)+'%';}, color:GR.m, fontFamily:SERIF}}, axisStyle()),
      yAxis: Object.assign({type:'category', data:rev.map(function(r){return r[0];})}, axisStyle(), {splitLine:{show:false}, axisLabel:{color:GR.ink, fontFamily:SERIF}}),
      series:[{type:'bar', barWidth:'60%',
        data:rev.map(function(r){return {value:r[1], itemStyle:{color:shade(r[1]), borderColor:GR.ink, borderWidth:0.8}};}),
        label:{show:true, position:'right', color:GR.ink, fontFamily:SERIF,
          formatter:function(p){return (p.value*100).toFixed(1)+'%  (n='+nmap[p.name].toLocaleString('en-US')+')';}},
        markLine:{silent:true, symbol:'none', lineStyle:{color:GR.ink, type:'dashed', width:1},
          label:{formatter:'overall 52.8%', color:GR.ink, fontFamily:SERIF, position:'insideEndTop'},
          data:[{xAxis:0.528}]}}]
    }));
  }

  /* ---------- orchestrate ---------- */
  document.getElementById('weekSlider').value = selWeekIdx;
  renderEarly(); renderDrivers(); renderRadar(); renderFair(); renderOutcome(); renderDisp(); updateReadout();
  window.addEventListener('resize', function(){ Object.keys(charts).forEach(function(k){ charts[k].resize(); }); });
})();
