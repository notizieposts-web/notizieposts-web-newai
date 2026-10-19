"""Mappa interattiva delle edizioni: grafo edizioni <-> protagonisti condivisi. Inserita nell'archivio (index.html)."""
import re, sys, json, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import edx


THEMES = {1:['Decisionali','Costi'],2:['Decisionali','Grandi modelli','Sicurezza','Costi','Ricerca'],3:['Grandi modelli','Sicurezza','Ricerca','Costi'],
 4:['Decisionali','Valutazione','Pesi aperti'],5:['Decisionali','Pesi aperti','Sicurezza'],6:['Sicurezza','Ricerca','Valutazione'],7:['Hardware'],
 8:['Pesi aperti','Grandi modelli','Costi'],9:['Sicurezza','Grandi modelli'],10:['Sicurezza'],11:['Pesi aperti','Grandi modelli'],12:['Sicurezza','Ricerca'],
 13:['Grandi modelli','Costi'],14:['Grandi modelli','Hardware'],15:['Regole','Sicurezza'],16:['Regole'],17:['Pesi aperti','Grandi modelli'],
 18:['Sicurezza','Grandi modelli','Costi'],19:['Decisionali','Sicurezza','Ricerca'],20:['Grandi modelli','Hardware','Ricerca','Sicurezza'],
 21:['Grandi modelli','Regole','Sicurezza','Costi'],22:['Sicurezza','Ricerca','Grandi modelli'],23:['Sicurezza','Pesi aperti','Regole'],24:['Sicurezza','Ricerca','Pesi aperti','Decisionali','Costi'],25:['Regole','Sicurezza','Hardware','Costi','Ricerca']}
EXTRA = {4:['Jev'],5:['Jev','OpenAI','NVIDIA'],19:['Jev']}

def data(root):
    s = open(os.path.join(root, 'index.html'), encoding='utf-8').read()
    i = s.find('var ED=['); j = s.find('];', i)
    rows = re.findall(r"\['((?:[^'\\]|\\.)*)','((?:[^'\\]|\\.)*)','((?:[^'\\]|\\.)*)','((?:[^'\\]|\\.)*)'\]", s[i:j])
    x = edx.build()
    eds = []
    for n, r in enumerate(rows, 1):
        info = x.get(r[3], {})
        eds.append({'n': n, 'd': r[0].replace("\\'", "'"), 'u': r[3], 't': info.get('t', r[1]), 's': info.get('d', ''), 'c': info.get('c', []), 'm': THEMES.get(n, []), 'x': EXTRA.get(n, [])})
    return eds

SECTION = r'''<section class="ch" id="mappa" style="padding-top:2.5rem">
  <div class="ch-head"><div class="kicker"><span class="chip topic">Mappa</span></div><h2>Come sono collegate le edizioni</h2><p class="lead">Ogni cerchio numerato è un'edizione. Le etichette tonde sono i protagonisti, quelle arancioni squadrate i temi (ognuno ha la sua pagina in Argomenti), quella verde acqua la guida Content Understanding. Seleziona un nodo per vedere collegamenti e riassunto.</p></div>
  <div class="row" id="gmode" role="group" aria-label="Collega le edizioni per" style="margin-top:1.2rem"><button type="button" class="btn" data-m="both" aria-pressed="true">Protagonisti e temi</button><button type="button" class="btn" data-m="pr" aria-pressed="false">Solo protagonisti</button><button type="button" class="btn" data-m="th" aria-pressed="false">Solo temi</button><button type="button" class="btn gfull-open" id="gfullbtn" aria-haspopup="dialog">&#x26F6; Vedi tutta la mappa</button></div>
  <div class="gwrap">
    <div class="card gcanvas" id="gcanvas"><button type="button" class="gfull-close" id="gfullclose" aria-label="Chiudi la mappa a tutto schermo">&#x2715; Chiudi</button><svg id="egraph" viewBox="0 0 900 560" role="group" aria-label="Mappa delle edizioni e dei protagonisti condivisi"></svg>
      <div class="glegend" aria-hidden="true"><span><i class="lg-ed"></i>Edizione</span><span><i class="lg-pr"></i>Protagonista</span><span><i class="lg-th"></i>Tema</span><span><i class="lg-gu"></i>Guida</span></div></div>
    <aside class="card gpanel" id="gpanel" aria-live="polite"></aside>
  </div>
  <details class="gtext"><summary>Vista testuale dei collegamenti</summary><ul id="gtextlist"></ul></details>
</section>
'''

CSS = r'''<style id="egraph-css">
.gwrap{display:grid;grid-template-columns:minmax(0,1fr) 18rem;gap:1rem;margin-top:1.5rem;align-items:start}
@media (max-width:900px){.gwrap{grid-template-columns:minmax(0,1fr)}}
.gcanvas{padding:.5rem!important;overflow-x:auto}
@media (max-width:700px){#egraph{min-width:640px}.gcanvas::after{content:'Scorri di lato per vedere tutta la mappa';display:block;font-size:.8rem;color:var(--muted);padding:.2rem .6rem}}
#egraph{width:100%;height:auto;display:block;touch-action:manipulation}
#egraph .edge{stroke:var(--line);stroke-width:1.4;transition:stroke .15s,opacity .15s}
#egraph .edge.on{stroke:var(--violet);stroke-width:2.6}
#egraph .node{cursor:pointer;outline:none}
#egraph .node .ring{fill:none;stroke:var(--violet);stroke-width:3;opacity:0}
#egraph .node:focus-visible .ring,#egraph .node.sel .ring{opacity:1}
#egraph .ed circle.b{fill:var(--violet)}
#egraph .ed text{fill:var(--bg);font:700 13px var(--head,system-ui);pointer-events:none}
#egraph .pr rect.b{fill:var(--surface);stroke:var(--ink);stroke-width:1.5}
#egraph .pr text{fill:var(--ink);font:700 12px var(--head,system-ui);pointer-events:none}
#egraph .th rect.b{fill:var(--sun-soft);stroke:var(--sun);stroke-width:1.5}
#egraph .th text{fill:var(--ink);font:700 12px var(--head,system-ui);pointer-events:none}
#egraph .th.on rect.b{fill:var(--sun);stroke:var(--sun)}#egraph .th.on text{fill:var(--bg)}
#egraph .edge.th{stroke-dasharray:4 3}
#egraph .edge.gu{stroke-dasharray:1.5 4;opacity:.7}
#egraph .gu rect.b{fill:var(--teal-soft);stroke:var(--teal);stroke-width:2}
#egraph .gu text{fill:var(--ink);font:800 12px var(--head,system-ui);pointer-events:none}
#egraph .gu.on rect.b,#egraph .gu.sel rect.b{fill:var(--teal);stroke:var(--teal)}#egraph .gu.on text,#egraph .gu.sel text{fill:var(--bg)}
#egraph .node.gu .ring{stroke:var(--teal)}
.glegend i.lg-gu{border-radius:3px;background:var(--teal-soft);border:2px solid var(--teal)}
.chip.guide{background:var(--teal-soft)!important;color:var(--ink)!important;border:1px solid var(--teal)!important}
.gpanel .gl{margin:.6rem 0 0;font-size:.78rem;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:var(--muted)}
.chip.theme{background:var(--sun-soft)!important;color:var(--ink)!important;border:1px solid var(--sun)!important}
#egraph .pr.on rect.b{fill:var(--violet);stroke:var(--violet)}#egraph .pr.on text{fill:var(--bg)}
#egraph.focus .edge:not(.on){opacity:.35}
#egraph.focus .ed:not(.on):not(.sel) circle.b{fill:var(--soft);stroke:var(--line);stroke-width:1.5}
#egraph.focus .ed:not(.on):not(.sel) text{fill:var(--ink)}
.glegend{display:flex;gap:1rem;padding:.3rem .6rem .2rem;font-size:.8rem;color:var(--muted)}
.glegend i{display:inline-block;width:12px;height:12px;margin-right:.35rem;vertical-align:-1px;border-radius:50%;background:var(--violet)}
.glegend i.lg-th{border-radius:3px;background:var(--sun-soft);border:1.5px solid var(--sun)}
.glegend i.lg-pr{border-radius:4px;background:var(--surface);border:1.5px solid var(--ink)}
.gpanel h3{font-size:1.05rem;margin:.3rem 0 .4rem}.gpanel p{margin:.3rem 0;font-size:.93rem}
.gpanel ul{list-style:none;padding:0;margin:.5rem 0 0;display:flex;flex-wrap:wrap;gap:.35rem}
.gpanel button.chip{border:0;cursor:pointer;min-height:24px}
.gpanel .gbtn{display:inline-flex;align-items:center;min-height:32px;margin-top:.6rem;padding:.35rem .85rem;border-radius:999px;background:var(--violet);color:var(--bg);font-weight:700;text-decoration:none}
.gfull-open{margin-left:auto}
.gfull-close{display:none}
.gcanvas.gfull{position:fixed;inset:0;z-index:9000;margin:0;border-radius:0;padding:3.6rem 1rem 1rem!important;overflow:auto;background:var(--surface)}
.gcanvas.gfull #egraph{min-width:0;width:100%;height:calc(100vh - 6rem);max-height:none}
.gcanvas.gfull .gfull-close{display:inline-flex;align-items:center;gap:.4rem;position:fixed;top:.8rem;right:1rem;z-index:9001;min-height:40px;padding:.4rem 1rem;border-radius:999px;border:1px solid var(--line);background:var(--ink);color:var(--bg);font-weight:700;cursor:pointer}
.gcanvas.gfull::after{display:none!important}
body.gfull-lock{overflow:hidden}
.gtext{margin-top:1rem}.gtext summary{cursor:pointer;font-weight:600;min-height:24px}
.edfilter{display:flex;align-items:center;gap:.6rem;flex-wrap:wrap;margin:1rem 0 0;font-size:.92rem}
.edfilter button{border:1px solid var(--line);background:var(--surface);color:var(--ink);border-radius:999px;padding:.3rem .8rem;min-height:32px;cursor:pointer;font-weight:600}
</style>'''

JS = r'''<script id="egraph-js">
(function(){
  var ED=__DATA__,GU=__GU__,TU=__TU__;
  var svg=document.getElementById('egraph');if(!svg)return;
  var NS='http://www.w3.org/2000/svg',W=900,H=560,mode='both',nodes,links,byId,cnt,cur=null;
  var panel=document.getElementById('gpanel');
  var GENERIC=['Costi','Benchmark','Confronto','Laboratori','Architetture','Settembre','Ricerca','Hardware','Open source','Guardrail','Audizione','Decisionali','Incidenti','Valutatori','Codice','Robot','Privacy','MoE','Piste'];
  function tagsOf(e,k){if(k==='gu')return GU.filter(function(g){return g.eds.indexOf(e.n)>=0}).map(function(g){return g.c});return k==='pr'?e.c.concat(e.x.filter(function(x){return e.c.indexOf(x)<0})).filter(function(c){return GENERIC.indexOf(c)<0}):e.m}
  function esc(s){return String(s).replace(/[&<>"]/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]})}
  function el(t,a){var x=document.createElementNS(NS,t);for(var k in a)x.setAttribute(k,a[k]);return x}
  function build(){
    nodes=[];links=[];byId={};cnt={pr:{},th:{}};
    ED.forEach(function(e){tagsOf(e,'pr').forEach(function(c){cnt.pr[c]=(cnt.pr[c]||0)+1});tagsOf(e,'th').forEach(function(c){cnt.th[c]=(cnt.th[c]||0)+1})});
    ED.forEach(function(e,i){var a=i/ED.length*Math.PI*2-Math.PI/2;var n={id:'e'+e.n,k:'ed',e:e,x:W/2+Math.cos(a)*250,y:H/2+Math.sin(a)*210};nodes.push(n);byId[n.id]=n;});
    ['pr','th'].forEach(function(k){
      if(mode!=='both'&&mode!==k)return;
      var L=Object.keys(cnt[k]).filter(function(c){return cnt[k][c]>1}).sort(function(a,b){return cnt[k][b]-cnt[k][a]});
      L.forEach(function(c,i){var a=i/L.length*Math.PI*2+(k==='th'?0.3:0);var n={id:k+':'+c,k:k,c:c,x:W/2+Math.cos(a)*(k==='th'?60:120),y:H/2+Math.sin(a)*(k==='th'?50:90)};nodes.push(n);byId[n.id]=n;});
      ED.forEach(function(e){tagsOf(e,k).forEach(function(c){if(byId[k+':'+c])links.push({s:byId['e'+e.n],t:byId[k+':'+c],k:k})})});
    });
    GU.forEach(function(g,i){var n={id:'gu:'+g.c,k:'gu',c:g.c,g:g,x:W/2+40,y:H/2+i*40};nodes.push(n);byId[n.id]=n;ED.forEach(function(e){if(g.eds.indexOf(e.n)>=0)links.push({s:byId['e'+e.n],t:n,k:'gu'})})});
    nodes.forEach(function(n){n.hw=n.k==='ed'?24:(n.c.length*7.6+22)/2+8;n.hh=n.k==='ed'?24:19;});
    function collide(a,b,k){var dx=b.x-a.x,dy=b.y-a.y,ox=a.hw+b.hw-Math.abs(dx),oy=a.hh+b.hh-Math.abs(dy);if(ox>0&&oy>0){if(ox<oy*1.6){var s=(dx<0?-1:1)*ox*k;a.x-=s;b.x+=s}else{var t=(dy<0?-1:1)*oy*k;a.y-=t;b.y+=t}}}
    for(var it=0;it<480;it++){var al=1-it/480;
      for(var i=0;i<nodes.length;i++)for(var j=i+1;j<nodes.length;j++){var a=nodes[i],b=nodes[j],dx=b.x-a.x,dy=b.y-a.y,d2=dx*dx+dy*dy+0.01,d=Math.sqrt(d2),f=(2600/d2)*al;dx/=d;dy/=d;a.x-=dx*f;a.y-=dy*f;b.x+=dx*f;b.y+=dy*f;collide(a,b,0.25);}
      links.forEach(function(l){var dx=l.t.x-l.s.x,dy=l.t.y-l.s.y,d=Math.sqrt(dx*dx+dy*dy)||1,f=(d-(l.k==='gu'?150:115))*(l.k==='gu'?0.006:0.018)*al;dx/=d;dy/=d;l.s.x+=dx*f;l.s.y+=dy*f;l.t.x-=dx*f;l.t.y-=dy*f;});
      nodes.forEach(function(n){n.x+=(W/2-n.x)*0.004*al;n.y+=(H/2-n.y)*0.006*al;});
    }
    for(var it2=0;it2<300;it2++)for(var i2=0;i2<nodes.length;i2++)for(var j2=i2+1;j2<nodes.length;j2++)collide(nodes[i2],nodes[j2],0.5);
    var minX=1e9,minY=1e9,maxX=-1e9,maxY=-1e9;nodes.forEach(function(n){var w=n.k==='ed'?22:n.c.length*4+26;minX=Math.min(minX,n.x-w);maxX=Math.max(maxX,n.x+w);minY=Math.min(minY,n.y-22);maxY=Math.max(maxY,n.y+22);});
    svg.setAttribute('viewBox',(minX-10).toFixed(0)+' '+(minY-10).toFixed(0)+' '+(maxX-minX+20).toFixed(0)+' '+(maxY-minY+20).toFixed(0));
    while(svg.firstChild)svg.removeChild(svg.firstChild);
    var gE=el('g',{'aria-hidden':'true'}),gN=el('g',{});svg.appendChild(gE);svg.appendChild(gN);
    links.forEach(function(l){l.el=el('line',{x1:l.s.x,y1:l.s.y,x2:l.t.x,y2:l.t.y,'class':'edge '+l.k});gE.appendChild(l.el)});
    nodes.forEach(function(n){
      var g=el('g',{'class':'node '+n.k,tabindex:'0',role:'button',transform:'translate('+n.x.toFixed(1)+','+n.y.toFixed(1)+')'});
      if(n.k==='ed'){g.setAttribute('aria-label','Edizione '+n.e.n+', '+n.e.d+': '+n.e.t);g.appendChild(el('circle',{r:22,'class':'ring'}));g.appendChild(el('circle',{r:17,'class':'b'}));var t=el('text',{'text-anchor':'middle',dy:'4.5'});t.textContent=n.e.n;g.appendChild(t);}
      else{var w=n.c.length*7.6+22,rx=n.k==='pr'?13:n.k==='th'?7:4;g.setAttribute('aria-label',n.k==='gu'?n.c+', collegata a '+n.g.eds.length+' edizioni':(n.k==='th'?'Tema ':'')+n.c+', in '+cnt[n.k][n.c]+' edizioni');g.appendChild(el('rect',{x:-w/2-5,y:-18,width:w+10,height:36,rx:rx+5,'class':'ring'}));g.appendChild(el('rect',{x:-w/2,y:-13,width:w,height:26,rx:rx,'class':'b'}));var t2=el('text',{'text-anchor':'middle',dy:'4'});t2.textContent=n.c;g.appendChild(t2);}
      n.el=g;gN.appendChild(g);
      g.addEventListener('click',function(){select(n)});
      g.addEventListener('keydown',function(ev){if(ev.key==='Enter'||ev.key===' '){ev.preventDefault();select(n)}});
      g.addEventListener('mouseenter',function(){highlight(n)});g.addEventListener('mouseleave',function(){highlight(cur)});
      g.addEventListener('focus',function(){highlight(n)});
    });
    var tl=document.getElementById('gtextlist');
    if(tl)tl.innerHTML=nodes.filter(function(n){return n.k!=='ed'}).map(function(n){var l=ED.filter(function(o){return tagsOf(o,n.k).indexOf(n.c)>=0}).map(function(o){return o.n});return '<li><b>'+(n.k==='th'?'Tema ':'')+esc(n.c)+'</b>: edizioni '+l.join(', ')+'</li>'}).join('')+'<li><b>Senza collegamenti</b>: '+(nodes.filter(function(n){return n.k==='ed'&&!links.some(function(l){return l.s===n})}).map(function(n){return n.e.n}).join(', ')||'nessuna')+'</li>';
    var keep=cur&&(cur.k==='ed'?byId[cur.id]:byId[cur.id]);cur=null;select(keep||byId['e'+ED[ED.length-1].n]);
  }
  function neighbors(n){return links.filter(function(l){return l.s===n||l.t===n})}
  function highlight(n){
    svg.classList.toggle('focus',!!n);
    nodes.forEach(function(m){m.el.classList.remove('on')});links.forEach(function(l){l.el.classList.remove('on')});
    if(!n)return;n.el.classList.add('on');
    neighbors(n).forEach(function(l){l.el.classList.add('on');l.s.el.classList.add('on');l.t.el.classList.add('on');});
  }
  function chipBtn(c,k){return '<li><button type="button" class="chip '+(k==='th'?'theme':k==='gu'?'guide':'topic')+'" data-k="'+k+'" data-p="'+esc(c)+'">'+esc(c)+'</button></li>'}
  function select(n){
    if(!n)return;if(cur&&cur.el)cur.el.classList.remove('sel');cur=n;n.el.classList.add('sel');highlight(n);
    if(n.k==='ed'){var e=n.e,rel={};
      neighbors(n).forEach(function(l){var c=l.t.c;ED.forEach(function(o){if(o!==e&&tagsOf(o,l.k).indexOf(c)>=0)rel[o.n]=(rel[o.n]||[]).concat(c)})});
      var rl=Object.keys(rel).sort(function(a,b){return rel[b].length-rel[a].length||b-a});
      panel.innerHTML='<span class="chip date">'+esc(e.d)+'</span> <span class="chip">Edizione '+e.n+'</span><h3>'+esc(e.t)+'</h3><p>'+esc(e.s)+'</p>'
        +'<p class="gl">Protagonisti</p><ul aria-label="Protagonisti">'+tagsOf(e,'pr').map(function(c){return chipBtn(c,'pr')}).join('')+'</ul>'
        +'<p class="gl">Temi</p><ul aria-label="Temi">'+e.m.map(function(c){return chipBtn(c,'th')}).join('')+'</ul>'
        +(tagsOf(e,'gu').length?'<p class="gl">Guide</p><ul aria-label="Guide">'+tagsOf(e,'gu').map(function(c){return chipBtn(c,'gu')}).join('')+'</ul>':'')
        +(rl.length?'<p><b>Più vicine:</b> '+rl.slice(0,5).map(function(k){return 'n. '+k+' ('+rel[k].join(', ')+')'}).join('; ')+(rl.length>5?'; e altre '+(rl.length-5):'')+'.</p>':'<p>Nessun collegamento in questa vista: prova "Protagonisti e temi".</p>')
        +(e.u?'<a class="gbtn" href="'+e.u+'">Apri l\'edizione '+e.n+'</a>':'<p class="note">Solo email, senza pagina.</p>');
    }else if(n.k==='gu'){var gl=ED.filter(function(o){return n.g.eds.indexOf(o.n)>=0}).sort(function(a,b){return b.n-a.n});
      panel.innerHTML='<span class="chip guide">Guida</span><h3>'+esc(n.c)+'</h3><p>'+esc(n.g.s)+'</p><p class="gl">'+gl.length+' edizioni collegate</p><ul aria-label="Edizioni">'+gl.map(function(o){return '<li><a class="chip" href="'+(o.u||'#edizioni')+'">n. '+o.n+'</a></li>'}).join('')+'</ul><a class="gbtn" href="'+n.g.u+'">Apri la guida</a>';
    }else{var list=ED.filter(function(o){return tagsOf(o,n.k).indexOf(n.c)>=0}).sort(function(a,b){return b.n-a.n});
      panel.innerHTML='<span class="chip '+(n.k==='th'?'theme':'topic')+'">'+(n.k==='th'?'Tema':'Protagonista')+'</span><h3>'+esc(n.c)+' in '+list.length+' edizioni</h3><ul aria-label="Edizioni">'+list.map(function(o){return '<li><a class="chip" href="'+(o.u||'#edizioni')+'">n. '+o.n+' · '+esc(o.d)+'</a></li>'}).join('')+'</ul>'+(n.k==='pr'?'<button type="button" class="gbtn" data-filter="'+esc(n.c)+'">Mostra solo queste nella lista</button>':(TU[n.c]?'<a class="gbtn" href="'+TU[n.c]+'">Apri la pagina del tema</a>':''));
    }
    panel.querySelectorAll('[data-p]').forEach(function(b){b.onclick=function(){var p=byId[b.dataset.k+':'+b.dataset.p];if(p){select(p);p.el.focus()}else if(b.dataset.k==='pr')filter(b.dataset.p)}});
    panel.querySelectorAll('[data-filter]').forEach(function(b){b.onclick=function(){filter(b.dataset.filter)}});
  }
  function filter(c){
    var list=document.getElementById('edlist');if(!list)return;var shown=0;
    list.querySelectorAll('article.edcard').forEach(function(a){var ok=!c||[].some.call(a.querySelectorAll('.topics li'),function(li){return li.textContent===c});a.hidden=!ok;if(ok)shown++;});
    var bar=document.getElementById('edfilter');
    if(!bar){bar=document.createElement('div');bar.id='edfilter';bar.className='edfilter';bar.setAttribute('aria-live','polite');list.parentNode.insertBefore(bar,list);}
    if(c){bar.innerHTML='<span>Edizioni con <b>'+esc(c)+'</b>: '+shown+'</span><button type="button">Mostra tutte</button>';bar.querySelector('button').onclick=function(){filter(null)};document.getElementById('edizioni').scrollIntoView();}
    else bar.innerHTML='';
  }
  document.querySelectorAll('#gmode button').forEach(function(b){b.onclick=function(){mode=b.dataset.m;document.querySelectorAll('#gmode button').forEach(function(x){x.setAttribute('aria-pressed',x===b?'true':'false')});build();}});
  /* vista d'insieme a tutto schermo */
  var cv=document.getElementById('gcanvas'),ob=document.getElementById('gfullbtn'),cb=document.getElementById('gfullclose');
  function openFull(){cv.classList.add('gfull');cv.setAttribute('role','dialog');cv.setAttribute('aria-modal','true');cv.setAttribute('aria-label','Mappa delle edizioni a tutto schermo');document.body.classList.add('gfull-lock');cb.focus();}
  function closeFull(){cv.classList.remove('gfull');cv.removeAttribute('role');cv.removeAttribute('aria-modal');cv.removeAttribute('aria-label');document.body.classList.remove('gfull-lock');ob.focus();}
  if(ob&&cb&&cv){ob.onclick=openFull;cb.onclick=closeFull;
    document.addEventListener('keydown',function(ev){if(!cv.classList.contains('gfull'))return;if(ev.key==='Escape'){ev.preventDefault();closeFull();}
      if(ev.key==='Tab'){var f=[].slice.call(cv.querySelectorAll('button,[tabindex="0"]'));if(!f.length)return;var a=f[0],z=f[f.length-1];if(ev.shiftKey&&document.activeElement===a){ev.preventDefault();z.focus();}else if(!ev.shiftKey&&document.activeElement===z){ev.preventDefault();a.focus();}}});}
  build();
})();
</script>'''

def apply(root):
    p = os.path.join(root, 'index.html'); s = open(p, encoding='utf-8').read()
    for pat in (r'<section class="ch" id="mappa".*?</section>\s*', r'<style id="egraph-css">.*?</style>', r'<script id="egraph-js">.*?</script>\s*'):
        s = re.sub(pat, '', s, flags=re.S)
    s = s.replace('<section class="ch" id="edizioni">', SECTION + '\n<section class="ch" id="edizioni">', 1)
    s = s.replace('</head>', CSS + '</head>', 1)
    import argomenti
    gu = [{'c': g['c'], 'u': g['u'], 's': g['s'], 'eds': g['eds']} for g in argomenti.GUIDES if g.get('map', True)]
    tu = {t: argomenti.theme_url(t) for t in argomenti.THEME_INFO}
    s = s.replace('</body>', JS.replace('__DATA__', json.dumps(data(root), ensure_ascii=False)).replace('__GU__', json.dumps(gu, ensure_ascii=False)).replace('__TU__', json.dumps(tu, ensure_ascii=False)) + '\n</body>', 1)
    # voce di menu
    if 'href="#mappa"' not in s:
        s = s.replace('<div class="links" id="links">', '<div class="links" id="links"><a href="#mappa">Mappa</a>', 1)
    # grafico in testata: il marchio del logo, al posto dei cerchi numerati
    s = re.sub(r"var arc='';ED\.forEach\(.*?\$\('arcsvg'\)\.innerHTML=arc;",
               lambda m: "$('arcsvg').innerHTML='<g transform=\"translate(80 80) scale(7.5)\"><rect width=\"32\" height=\"32\" rx=\"9\" fill=\"var(--violet)\"/><path d=\"M16 16 L16 5.5 A10.5 10.5 0 0 1 25.1 10.75 Z\" fill=\"var(--bg)\" opacity=\".28\"/><g fill=\"none\" stroke=\"var(--bg)\" stroke-linecap=\"round\"><circle cx=\"16\" cy=\"16\" r=\"10.5\" stroke-width=\"2\" opacity=\".6\"/><circle cx=\"16\" cy=\"16\" r=\"5.6\" stroke-width=\"2\" opacity=\".85\"/><path d=\"M16 16 L25.1 10.75\" stroke-width=\"2.4\"/></g><circle cx=\"16\" cy=\"16\" r=\"2.3\" fill=\"var(--bg)\"/><circle cx=\"22.6\" cy=\"21.4\" r=\"2.2\" fill=\"var(--bg)\"/></g>';",
               s, count=1, flags=re.S)
    s = s.replace('<svg class="radar" viewBox="0 0 400 400" role="img" aria-label="Archivio">', '<svg class="radar" viewBox="0 0 400 400" aria-hidden="true">', 1)
    open(p, 'w', encoding='utf-8').write(s)

if __name__ == '__main__':
    apply(sys.argv[1]); print('ok')
