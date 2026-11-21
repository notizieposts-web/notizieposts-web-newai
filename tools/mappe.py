"""Mappa viva: per ogni capitolo di un'edizione, una mappa concettuale che cresce mentre si legge.

Inserita da tools/inject.py solo nelle pagine edizioni/NN.html (id mv-css, mv-js, mv-data). Idempotente.

Da dove viene la mappa
  - tools/mappe/NN.json, se esiste: mappa scritta e controllata quando si prepara l'edizione (con l'aiuto dell'AI).
    Formato: {"<id capitolo>": {"root": "Concetto centrale", "nodes": [{"id","t" titolo,"d" spiegazione breve,
    "at" indice del paragrafo (.prose > p, da 0) in cui compare,"i" emoji,"p" id del genitore o "root","r" relazione}],
    "x": [[id_a, id_b, "relazione trasversale"]]}}
  - altrimenti una mappa automatica: i sottotitoli h3 come rami e i termini del glossario come foglie.

Che cosa fa nel browser (nessun servizio esterno)
  - "Segui la lettura": i nodi spuntano sul ramo quando arrivi al loro paragrafo; "Tutta" la mostra intera.
  - Toccando un nodo: spiegazione, collegamenti e "Vai al punto nel testo".
  - "Raccontami la mappa": Sapio la legge nodo per nodo (voce del browser) e illumina il collegamento.
  - "Completala tu": i titoli diventano foglie vuote da riempire scegliendo le parole giuste.
  - "Scarica": la mappa come immagine PNG.
Sul computer sta nella colonna laterale del capitolo; sul telefono è un pannello in basso.
"""
import json, os

CSS = r'''<style id="mv-css">
.mv-open-btn{padding:.3rem 1rem}
.mv{box-sizing:border-box;border:2px solid #5E9E4B;border-radius:18px;background:var(--surface);color:var(--ink);display:flex;flex-direction:column;min-height:0}
.mv.mv-side{max-height:calc(100vh - 100px)}
.stick.mv-on>*:not(.mv){display:none!important}
.mv.mv-sheet{position:fixed;left:0;right:0;bottom:0;z-index:58;height:46vh;border-radius:18px 18px 0 0;border-bottom:0;box-shadow:0 -8px 30px rgba(0,0,0,.22)}
html.mv-sheet-on .kw-tts,html.mv-sheet-on .kw-lf,html.mv-sheet-on .kw-mark{bottom:calc(46vh + 10px)!important}
.mv-h{display:flex;align-items:center;gap:.5rem;padding:.6rem .8rem .4rem;border-bottom:1px solid var(--line)}
.mv-h h2{font-size:1rem;margin:0;line-height:1.25;flex:1;min-width:0}
.mv-h h2 small{display:block;font-weight:500;font-size:.82rem;color:var(--muted);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.mv-grow{display:none;flex:none;min-height:44px;padding:0 .7rem;border-radius:999px;border:1px solid var(--line);background:var(--surface);color:var(--ink);font:inherit;font-size:.88rem;cursor:pointer}
.mv-sheet .mv-grow{display:inline-block}
.mv.mv-sheet.mv-big{height:88vh}
html.mv-big-on .kw-tts,html.mv-big-on .kw-lf{bottom:calc(88vh + 10px)!important}
.mv-sheet .mv-bar{flex-wrap:nowrap;overflow-x:auto;scrollbar-width:thin}.mv-sheet .mv-bar button{flex:none}
.mv-sheet .mv-h{padding:.45rem .7rem .3rem}
.mv-x{flex:none;min-width:44px;min-height:44px;border-radius:999px;border:1px solid var(--line);background:var(--surface);color:var(--ink);font-weight:700;cursor:pointer}
.mv-bar{display:flex;flex-wrap:wrap;gap:.35rem;padding:.5rem .8rem;border-bottom:1px solid var(--line)}
.mv-bar button{min-height:40px;padding:.2rem .7rem;border-radius:10px;border:1px solid var(--line);background:var(--surface);color:var(--ink);font:inherit;font-size:.9rem;cursor:pointer}
.mv-bar button[aria-pressed="true"]{background:#5E9E4B;border-color:#3A2618;color:#fff}
.mv-body{overflow:auto;padding:.7rem .8rem 1rem;flex:1;min-height:0;overscroll-behavior:contain}
.mv-prog{font-size:.85rem;color:var(--muted);margin:0 0 .5rem}
.mv-root{display:flex;align-items:center;gap:.5rem;padding:.55rem .8rem;border-radius:14px;background:#7A5230;color:#fff;font-weight:800;line-height:1.3;border:1.5px solid #3A2618}
.mv-tree{list-style:none;margin:0 0 0 1.1rem;padding:0 0 0 0;border-left:6px solid #7A5230;border-radius:0 0 0 6px}
.mv-tree .mv-tree{margin-left:1.2rem;border-left-width:4px;border-left-color:#9A6A3C}
.mv-n{position:relative;padding:.45rem 0 .1rem 1.1rem}
.mv-n::before{content:"";position:absolute;left:0;top:1.55rem;width:1rem;height:3px;background:#7A5230;border-radius:2px}
.mv-r{font-size:.8rem;font-style:italic;color:var(--muted);margin:0 0 .15rem}
.mv-b{display:flex;align-items:center;gap:.5rem;width:100%;min-height:44px;padding:.35rem .7rem;text-align:left;border:1.5px solid #3A2618;border-radius:4px 18px 4px 18px;background:#EAF5E1;color:#1C1D1F;font:inherit;font-weight:700;line-height:1.3;cursor:pointer}
.mv-b:hover{background:#DDEFD0}
.mv-i{flex:none;font-size:1.15rem}
.mv-n.on>.mv-b,.mv-n.on-p>.mv-b{box-shadow:0 0 0 3px var(--violet-ink)}
.mv-n.on>.mv-b{background:#FFE08A}
.mv-d{margin:.35rem 0 .2rem;padding:.55rem .7rem;border-radius:10px;background:var(--soft);color:var(--ink);font-size:.93rem;line-height:1.5}
.mv-d[hidden]{display:none}
.mv-d p{margin:0 0 .35rem}.mv-d .mv-go{min-height:40px;padding:.2rem .7rem;border-radius:10px;border:1px solid var(--violet);background:var(--surface);color:var(--ink);font:inherit;cursor:pointer}
.mv-n.mv-blank>.mv-b{background:var(--surface);border-style:dashed;color:var(--muted)}
.mv-n.mv-blank>.mv-b[aria-pressed="true"]{box-shadow:0 0 0 3px var(--violet-ink)}
.mv-n.mv-wrong>.mv-b{border-color:var(--red)}
.mv-bank{display:flex;flex-wrap:wrap;gap:.4rem;padding:.6rem .8rem;border-top:1px solid var(--line);max-height:38%;overflow:auto}
.mv-bank[hidden]{display:none}
.mv-bank p{flex-basis:100%;margin:0;font-size:.88rem}
.mv-bank button{min-height:40px;padding:.2rem .7rem;border-radius:999px;border:1px solid var(--line);background:var(--soft);color:var(--ink);font:inherit;font-size:.9rem;cursor:pointer}
.mv-bank button[aria-pressed="true"]{background:var(--violet);border-color:var(--violet);color:var(--on-violet)}
.mv-bank button[disabled]{display:none}
.mv-msg{margin:.4rem 0 0;font-weight:600;font-size:.92rem}
.mv-msg:empty{display:none}
.mv-x-links{margin:.3rem 0 0;padding-left:1rem}
.mv-flash{animation:mv-flash 1.6s ease-out 1}
@keyframes mv-flash{0%,30%{background:#FFE08A;box-shadow:0 0 0 6px #FFE08A}100%{background:transparent;box-shadow:0 0 0 6px transparent}}
@media (prefers-reduced-motion:no-preference){.mv-n.mv-new{animation:mv-grow .55s ease-out 1;transform-origin:left center}.mv-n.mv-new::before{animation:mv-twig .35s ease-out 1;transform-origin:left center}
  @keyframes mv-grow{0%{opacity:0;transform:scale(.6) translateX(-12px)}70%{opacity:1;transform:scale(1.04)}100%{transform:none}}@keyframes mv-twig{from{transform:scaleX(0)}to{transform:scaleX(1)}}}
@media (prefers-reduced-motion:reduce){.mv-flash{animation:none;outline:3px solid #E3A22E}}
@media (prefers-color-scheme:dark){html:not([data-theme="light"]) .mv-b{background:#24331C;color:#EDEDED;border-color:#9CD84A}html:not([data-theme="light"]) .mv-b:hover{background:#2C3F22}html:not([data-theme="light"]) .mv-n.on>.mv-b{background:#5A4A12}}
html[data-theme="dark"] .mv-b{background:#24331C;color:#EDEDED;border-color:#9CD84A}html[data-theme="dark"] .mv-n.on>.mv-b{background:#5A4A12}
@media (forced-colors:active){.mv-tree{border-left-color:CanvasText}.mv-n::before{background:CanvasText}.mv-root{background:Canvas;color:CanvasText;border-color:CanvasText}}
@media print{.mv.mv-sheet{display:none}}
</style>'''

JS = r'''<script id="mv-js">
/* Mappa viva (tools/mappe.py) */
(function(){
  var DATA={};try{var el=document.getElementById('mv-data');if(el)DATA=JSON.parse(el.textContent)}catch(e){}
  function esc(s){return String(s).replace(/[&<>"]/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]})}
  function clean(el){var c=el.cloneNode(true);c.querySelectorAll('.gl-tip,.sr-only,.kw-hd-tip,.kw-ps,.gl-ico,.kw-br').forEach(function(x){x.remove()});return c.textContent.replace(/\s+/g,' ').trim();}
  function first(t){var m=t.match(/^.{20,220}?[.!?](?=\s|$)/);return m?m[0]:t.slice(0,180);}
  function paras(sec){return [].slice.call(sec.querySelectorAll('.prose>p'));}
  /* mappa automatica: sottotitoli e glossario */
  function auto(sec){var h2=sec.querySelector('.ch-head h2');if(!h2)return null;var M={root:clean(h2).split(':')[0],nodes:[],x:[]},P=paras(sec),k=0;
    sec.querySelectorAll('.prose>h3').forEach(function(h){var p=h.nextElementSibling;while(p&&p.tagName!=='P'&&p.tagName!=='H3')p=p.nextElementSibling;var at=p&&p.tagName==='P'?P.indexOf(p):-1;if(at<0)return;var id='h'+(++k);
      M.nodes.push({id:id,t:clean(h),d:first(clean(p)),at:at,i:'🍃',p:'root',r:''});
      var g=0;p.querySelectorAll('.gl').forEach(function(s){if(g>=2)return;var b=s.querySelector('.gl-btn'),tip=s.querySelector('.gl-tip');if(!b)return;var t=(b.firstChild?b.firstChild.textContent:'').trim();if(!t)return;var d='';if(tip){var c=tip.cloneNode(true);c.querySelectorAll('.gl-ex,.gl-act,b').forEach(function(x){x.remove()});d=first(c.textContent.replace(/^\s*\.\s*/,'').trim());}
        g++;M.nodes.push({id:id+'g'+g,t:t,d:d,at:at,i:'🌱',p:id,r:'parola chiave'});});});
    return M.nodes.length>=2?M:null;}
  var MAPS={},cur=null,panel=null,follow=true,reached={},built={},narr=null,buildMode=null,uid=0;
  function mapOf(sec){if(MAPS[sec.id]!==undefined)return MAPS[sec.id];var m=DATA[sec.id]||auto(sec);if(m){m.byId={};m.nodes.forEach(function(n){m.byId[n.id]=n});m.auto=!DATA[sec.id];}MAPS[sec.id]=m||null;return MAPS[sec.id];}
  function depth(m,n){var d=0,p=n.p;while(p&&p!=='root'&&m.byId[p]&&d<5){d++;p=m.byId[p].p;}return d;}
  function title(m,id){return id==='root'?m.root:(m.byId[id]?m.byId[id].t:'');}
  /* ---------- pannello ---------- */
  function wide(){return matchMedia('(min-width: 901px)').matches;}
  function makePanel(){var a=document.createElement('aside');a.className='mv';a.id='mv-panel';a.setAttribute('role','region');a.setAttribute('aria-labelledby','mv-title');
    a.innerHTML='<div class="mv-h"><span aria-hidden="true" style="font-size:1.4rem">🗺</span><h2 id="mv-title">Mappa viva<small></small></h2><button type="button" class="mv-grow" aria-pressed="false">Ingrandisci</button><button type="button" class="mv-x" aria-label="Chiudi la mappa">✕</button></div>'+
      '<div class="mv-bar" role="toolbar" aria-label="Comandi della mappa"><button type="button" data-a="follow" aria-pressed="true">Segui la lettura</button><button type="button" data-a="all" aria-pressed="false">Tutta</button>'+
      ('speechSynthesis' in window?'<button type="button" data-a="tell" aria-pressed="false">▶ Raccontami</button>':'<button type="button" data-a="tell" aria-pressed="false">▶ Passo passo</button>')+
      '<button type="button" data-a="build" aria-pressed="false">✍ Completala tu</button><button type="button" data-a="png">⬇ Scarica</button></div>'+
      '<div class="mv-body"><p class="mv-prog" aria-live="polite"></p><div class="mv-root"></div><ol class="mv-tree" aria-label="Rami della mappa"></ol></div><div class="mv-bank" hidden></div>';
    a.querySelector('.mv-x').addEventListener('click',function(){close(true)});
    a.querySelector('.mv-grow').addEventListener('click',function(){big(!a.classList.contains('mv-big'))});
    a.querySelector('.mv-bar').addEventListener('click',function(e){var b=e.target.closest('button');if(!b)return;var k=b.getAttribute('data-a');
      if(k==='follow'||k==='all'){follow=k==='follow';sync();render(true);}
      else if(k==='tell'){if(narr)tellStop();else tell();}
      else if(k==='build'){if(buildMode)buildStop();else buildStart();}
      else if(k==='png')png();});
    a.addEventListener('click',function(e){var b=e.target.closest('.mv-b');if(b){nodeClick(b.closest('.mv-n'));return;}var g=e.target.closest('.mv-go');if(g){goText(g.getAttribute('data-at'));return;}
      var w=e.target.closest('.mv-bank button');if(w){bankPick(w);}});
    a.addEventListener('keydown',function(e){if(e.key==='Escape'){e.stopPropagation();if(buildMode&&buildMode.word){buildMode.word.setAttribute('aria-pressed','false');buildMode.word=null;return;}close(true);}});
    return a;}
  function big(on){if(!panel)return;panel.classList.toggle('mv-big',on);document.documentElement.classList.toggle('mv-big-on',on&&panel.classList.contains('mv-sheet'));var g=panel.querySelector('.mv-grow');g.setAttribute('aria-pressed',on?'true':'false');g.textContent=on?'Riduci':'Ingrandisci';tick();}
  function sync(){if(!panel)return;panel.querySelector('[data-a=follow]').setAttribute('aria-pressed',follow?'true':'false');panel.querySelector('[data-a=all]').setAttribute('aria-pressed',follow?'false':'true');}
  function place(){if(!panel||!cur)return;var st=cur.querySelector('.stick');document.querySelectorAll('.stick.mv-on').forEach(function(s){if(s!==st||!wide())s.classList.remove('mv-on')});
    if(wide()&&st){if(panel.parentNode!==st)st.prepend(panel);st.classList.add('mv-on');panel.classList.add('mv-side');panel.classList.remove('mv-sheet');document.documentElement.classList.remove('mv-sheet-on');}
    else{if(panel.parentNode!==document.body)document.body.appendChild(panel);panel.classList.add('mv-sheet');panel.classList.remove('mv-side');document.documentElement.classList.add('mv-sheet-on');}}
  var opener=null;
  function open(sec,btn){var m=mapOf(sec);if(!m)return;if(!panel)panel=makePanel();opener=btn||opener;var was=cur;cur=sec;place();
    if(was!==sec){tellStop();buildStop();}
    document.querySelectorAll('.mv-open-btn').forEach(function(b){b.setAttribute('aria-expanded',b.closest('section.ch')===sec?'true':'false')});
    var h=sec.querySelector('.ch-head h2');panel.querySelector('#mv-title small').textContent=(h?clean(h):'');
    tick();render(true);}
  function close(back){tellStop();buildStop();if(panel){var st=panel.parentNode;if(st&&st.classList)st.classList.remove('mv-on');panel.remove();}document.documentElement.classList.remove('mv-sheet-on','mv-big-on');
    document.querySelectorAll('.mv-open-btn').forEach(function(b){b.setAttribute('aria-expanded','false')});var s=cur;cur=null;if(back&&s){var b=s.querySelector('.mv-open-btn');if(b)b.focus();}}
  /* ---------- quanto hai letto ---------- */
  function line(){var y=innerHeight*.6;if(panel&&panel.classList.contains('mv-sheet')){var t=panel.getBoundingClientRect().top;y=Math.min(y,t-30);}return y;}
  function tick(){if(!cur)return;var P=paras(cur),y=line(),r=reached[cur.id]==null?-1:reached[cur.id];
    for(var i=0;i<P.length;i++){var rc=P[i].getBoundingClientRect();if(!rc.height)continue;if(rc.top<y)r=Math.max(r,i);}
    if(r!==reached[cur.id]){reached[cur.id]=r;render(false);}}
  function visible(m){return m.nodes.filter(function(n){return !follow||buildMode||n.at<=(reached[cur.id]==null?-1:reached[cur.id])});}
  /* ---------- disegno ---------- */
  function render(full){if(!panel||!cur)return;var m=mapOf(cur);var V=visible(m),seen=built[cur.id]||(built[cur.id]={}),tree=panel.querySelector('.mv-tree');
    panel.querySelector('.mv-root').innerHTML='<span aria-hidden="true">🌳</span><span>'+esc(m.root)+'</span>';
    var prog=panel.querySelector('.mv-prog');prog.textContent=(buildMode?'Completa la mappa: ':'')+V.length+' di '+m.nodes.length+' concetti'+(follow&&!buildMode&&V.length<m.nodes.length?' · gli altri spuntano mentre leggi':'')+(m.auto?' · mappa automatica':'');
    if(full){tree.innerHTML='';}
    var ids={};V.forEach(function(n){ids[n.id]=1});
    tree.querySelectorAll('.mv-n').forEach(function(li){if(!ids[li.getAttribute('data-id')])li.remove();});
    V.forEach(function(n){if(tree.querySelector('.mv-n[data-id="'+n.id+'"]'))return;var li=document.createElement('li');li.className='mv-n';li.setAttribute('data-id',n.id);
      var dd='mvd'+(++uid),xs=(m.x||[]).filter(function(x){return x[0]===n.id||x[1]===n.id});
      li.innerHTML=(n.r?'<p class="mv-r">'+esc(n.p==='root'?m.root:title(m,n.p))+' '+esc(n.r)+' ↓</p>':'')+
        '<button type="button" class="mv-b" aria-expanded="false" aria-controls="'+dd+'"><span class="mv-i" aria-hidden="true">'+esc(n.i||'🍃')+'</span><span class="mv-t">'+esc(n.t)+'</span></button>'+
        '<div class="mv-d" id="'+dd+'" hidden><p>'+esc(n.d||'')+'</p>'+(xs.length?'<p style="margin:0"><b>Collegamenti</b></p><ul class="mv-x-links">'+xs.map(function(x){return '<li>'+esc(title(m,x[0]))+' '+esc(x[2])+' '+esc(title(m,x[1]))+'</li>'}).join('')+'</ul>':'')+
        '<button type="button" class="mv-go" data-at="'+n.at+'">Vai al punto nel testo</button></div>';
      var parentList=tree;if(n.p&&n.p!=='root'){var pl=tree.querySelector('.mv-n[data-id="'+n.p+'"]');if(pl){var sub=pl.querySelector(':scope>ol');if(!sub){sub=document.createElement('ol');sub.className='mv-tree';pl.appendChild(sub);}parentList=sub;}}
      /* inserisci nell'ordine della mappa */
      var order=m.nodes.indexOf(n),placed=false;[].slice.call(parentList.children).some(function(c){var cn=m.byId[c.getAttribute('data-id')];if(cn&&m.nodes.indexOf(cn)>order){parentList.insertBefore(li,c);placed=true;return true;}});
      if(!placed)parentList.appendChild(li);
      if(!seen[n.id]&&!full){li.classList.add('mv-new');setTimeout(function(){li.classList.remove('mv-new')},700);var body=panel.querySelector('.mv-body');var r=li.getBoundingClientRect(),br=body.getBoundingClientRect();if(r.bottom>br.bottom||r.top<br.top)li.scrollIntoView({block:'nearest',behavior:matchMedia('(prefers-reduced-motion: reduce)').matches?'auto':'smooth'});}
      seen[n.id]=1;
      if(buildMode)blank(li,n);});
    if(buildMode)relabel();}
  function relabel(){var m=mapOf(cur);panel.querySelectorAll('.mv-n').forEach(function(li){var n=m.byId[li.getAttribute('data-id')],r=li.querySelector(':scope>.mv-r');if(!n||!r)return;var pt=n.p==='root'?m.root:(buildMode&&!buildMode.filled[n.p]?'…':title(m,n.p));r.textContent=pt+' '+n.r+' ↓';});}
  function nodeClick(li){if(!li)return;var m=mapOf(cur),n=m.byId[li.getAttribute('data-id')];if(buildMode&&li.classList.contains('mv-blank')){leafPick(li,n);return;}
    var b=li.querySelector(':scope>.mv-b'),d=li.querySelector(':scope>.mv-d'),o=d.hidden;d.hidden=!o;b.setAttribute('aria-expanded',o?'true':'false');}
  function goText(at){var P=paras(cur),p=P[+at];if(!p)return;if(p.classList.contains('kw-hide')){var st=cur._steps;}
    if(!wide())p.scrollIntoView({block:'start',behavior:'auto'});else p.scrollIntoView({block:'center',behavior:matchMedia('(prefers-reduced-motion: reduce)').matches?'auto':'smooth'});
    p.classList.remove('mv-flash');void p.offsetWidth;p.classList.add('mv-flash');p.setAttribute('tabindex','-1');try{p.focus({preventScroll:true})}catch(e){}}
  /* ---------- Raccontami ---------- */
  function tell(){var m=mapOf(cur),V=visible(m);if(!V.length)return;var btn=panel.querySelector('[data-a=tell]');btn.setAttribute('aria-pressed','true');btn.textContent='⏹ Ferma';
    narr={i:-1,V:V,tok:0};var hasV='speechSynthesis' in window;
    function step(){if(!narr)return;narr.i++;panel.querySelectorAll('.mv-n.on,.mv-n.on-p').forEach(function(x){x.classList.remove('on','on-p')});
      if(narr.i>=narr.V.length){tellStop();return;}var n=narr.V[narr.i],li=panel.querySelector('.mv-n[data-id="'+n.id+'"]');if(!li){step();return;}
      li.classList.add('on');var pl=n.p&&n.p!=='root'?panel.querySelector('.mv-n[data-id="'+n.p+'"]'):null;if(pl)pl.classList.add('on-p');
      li.scrollIntoView({block:'nearest',behavior:matchMedia('(prefers-reduced-motion: reduce)').matches?'auto':'smooth'});
      var txt=(n.r?(n.p==='root'?m.root:title(m,n.p))+' '+n.r+' '+n.t+'. ':n.t+'. ')+(n.d||'');
      var my=++narr.tok;
      if(hasV){try{speechSynthesis.cancel();var u=new SpeechSynthesisUtterance(txt);u.lang='it-IT';u.rate=.95;var vs=speechSynthesis.getVoices().filter(function(v){return /^it/i.test(v.lang)});if(vs[0])u.voice=vs[0];u.onend=function(){if(narr&&narr.tok===my)setTimeout(step,350)};speechSynthesis.speak(u);}catch(e){narr.t=setTimeout(step,4500);}}
      else narr.t=setTimeout(step,Math.max(3500,txt.length*60));}
    var r0='Mappa: '+m.root+'.';if(hasV){try{speechSynthesis.cancel();var u0=new SpeechSynthesisUtterance(r0);u0.lang='it-IT';u0.onend=function(){if(narr&&narr.tok===0)step()};speechSynthesis.speak(u0);setTimeout(function(){if(narr&&narr.i<0)step()},2500);}catch(e){step();}}else step();}
  function tellStop(){if(!narr)return;clearTimeout(narr.t);narr.tok=-1;narr=null;try{speechSynthesis.cancel()}catch(e){}if(panel){panel.querySelectorAll('.mv-n.on,.mv-n.on-p').forEach(function(x){x.classList.remove('on','on-p')});var b=panel.querySelector('[data-a=tell]');b.setAttribute('aria-pressed','false');b.textContent='speechSynthesis' in window?'▶ Raccontami':'▶ Passo passo';}}
  /* ---------- Completala tu ---------- */
  function blank(li,n){li.classList.add('mv-blank');var b=li.querySelector(':scope>.mv-b');b.setAttribute('aria-pressed','false');b.querySelector('.mv-t').textContent='?';b.setAttribute('aria-label','Foglia vuota'+(n.r?': '+(n.p==='root'?mapOf(cur).root:(buildMode.filled[n.p]?title(mapOf(cur),n.p):'un\'altra foglia'))+' '+n.r+' …':''));}
  function buildStart(){tellStop();var m=mapOf(cur);buildMode={left:m.nodes.length,word:null,leaf:null,ok:0,err:0,filled:{}};var b=panel.querySelector('[data-a=build]');b.setAttribute('aria-pressed','true');b.textContent='Esci da Completala';
    if(panel.classList.contains('mv-sheet')){buildMode.autoBig=!panel.classList.contains('mv-big');big(true);}render(true);var words=m.nodes.map(function(n){return n.t}).sort(function(a,c){return (a.length*13%7)-(c.length*13%7)||a.localeCompare(c)});
    var bank=panel.querySelector('.mv-bank');bank.hidden=false;bank.innerHTML='<p>Scegli una parola, poi tocca la foglia vuota dove va (o al contrario).</p>'+words.map(function(w){return '<button type="button" aria-pressed="false">'+esc(w)+'</button>'}).join('')+'<p class="mv-msg" aria-live="polite"></p>';
    var f=bank.querySelector('button');if(f)f.focus();}
  function buildStop(){if(!buildMode)return;var ab=buildMode.autoBig;buildMode=null;if(ab)big(false);if(panel){var b=panel.querySelector('[data-a=build]');b.setAttribute('aria-pressed','false');b.textContent='✍ Completala tu';var bank=panel.querySelector('.mv-bank');bank.hidden=true;bank.innerHTML='';render(true);}}
  function bankPick(w){if(!buildMode)return;if(buildMode.word)buildMode.word.setAttribute('aria-pressed','false');if(buildMode.word===w){buildMode.word=null;return;}buildMode.word=w;w.setAttribute('aria-pressed','true');if(buildMode.leaf)tryFill();}
  function leafPick(li,n){if(buildMode.leaf)buildMode.leaf.querySelector(':scope>.mv-b').setAttribute('aria-pressed','false');buildMode.leaf=li;li.querySelector(':scope>.mv-b').setAttribute('aria-pressed','true');if(buildMode.word)tryFill();}
  function tryFill(){var m=mapOf(cur),li=buildMode.leaf,w=buildMode.word,n=m.byId[li.getAttribute('data-id')],msg=panel.querySelector('.mv-msg');
    if(w.textContent===n.t){li.classList.remove('mv-blank','mv-wrong');var b=li.querySelector(':scope>.mv-b');b.removeAttribute('aria-pressed');b.removeAttribute('aria-label');b.querySelector('.mv-t').textContent=n.t;w.disabled=true;buildMode.ok++;buildMode.left--;buildMode.filled[n.id]=1;relabel();
      li.classList.add('mv-new');setTimeout(function(){li.classList.remove('mv-new')},700);msg.textContent='Giusto: '+n.t+'.';
      if(!buildMode.left){msg.textContent='Mappa completata! '+buildMode.ok+' foglie, '+buildMode.err+(buildMode.err===1?' tentativo sbagliato.':' tentativi sbagliati.')+' Costruire la mappa aiuta a ricordare più che guardarla.';}
      var nx=panel.querySelector('.mv-bank button:not([disabled])');if(nx)nx.focus();else{var bb=panel.querySelector('[data-a=build]');bb.focus();}}
    else{buildMode.err++;li.classList.add('mv-wrong');setTimeout(function(){li.classList.remove('mv-wrong')},900);msg.textContent='Non qui: guarda il ramo e la relazione sopra la foglia.';w.setAttribute('aria-pressed','false');li.querySelector(':scope>.mv-b').setAttribute('aria-pressed','false');}
    buildMode.word=null;buildMode.leaf=null;}
  /* ---------- Scarica come immagine ---------- */
  function png(){var m=mapOf(cur),N=m.nodes,W=1000,pad=40,lh=26,c=document.createElement('canvas'),x=c.getContext('2d');
    function wrap(t,max,font){x.font=font;var w=t.split(' '),L=[],s='';w.forEach(function(k){var tt=s?s+' '+k:k;if(x.measureText(tt).width>max&&s){L.push(s);s=k;}else s=tt;});if(s)L.push(s);return L;}
    var rows=[];N.forEach(function(n){var d=depth(m,n),ind=pad+40+d*48,max=W-ind-pad-20;rows.push({n:n,d:d,ind:ind,t:wrap((n.i?n.i+' ':'')+n.t,max,'bold 22px system-ui, sans-serif'),dd:wrap(n.d||'',max,'17px system-ui, sans-serif'),r:n.r?(n.p==='root'?m.root:title(m,n.p))+' '+n.r:''});});
    var H=pad*2+70+rows.reduce(function(a,r){return a+18+(r.r?22:0)+r.t.length*lh+r.dd.length*22+14},0)+40;c.width=W;c.height=H;
    x.fillStyle='#FFFDF7';x.fillRect(0,0,W,H);x.fillStyle='#7A5230';x.beginPath();if(x.roundRect)x.roundRect(pad,pad,W-pad*2,56,14);else x.rect(pad,pad,W-pad*2,56);x.fill();
    x.fillStyle='#fff';x.font='bold 24px system-ui, sans-serif';x.fillText('🌳 '+m.root,pad+18,pad+36);var y=pad+80,top=y;
    x.strokeStyle='#7A5230';x.lineWidth=6;
    rows.forEach(function(r){y+=10;if(r.r){x.fillStyle='#55575B';x.font='italic 16px system-ui, sans-serif';x.fillText(r.r+' ↓',r.ind,y+14);y+=22;}
      var h=r.t.length*lh+r.dd.length*22+12;x.fillStyle='#EAF5E1';x.strokeStyle='#3A2618';x.lineWidth=1.5;x.beginPath();if(x.roundRect)x.roundRect(r.ind,y,W-r.ind-pad,h,[4,18,4,18]);else x.rect(r.ind,y,W-r.ind-pad,h);x.fill();x.stroke();
      x.strokeStyle='#7A5230';x.lineWidth=4;x.beginPath();x.moveTo(r.ind-30-0,y+20);x.lineTo(r.ind,y+20);x.stroke();
      x.fillStyle='#1C1D1F';x.font='bold 22px system-ui, sans-serif';r.t.forEach(function(t,i){x.fillText(t,r.ind+14,y+28+i*lh)});
      x.font='17px system-ui, sans-serif';x.fillStyle='#33363A';r.dd.forEach(function(t,i){x.fillText(t,r.ind+14,y+28+r.t.length*lh+i*22)});y+=h+8;});
    x.strokeStyle='#7A5230';x.lineWidth=6;x.beginPath();x.moveTo(pad+10,pad+56);x.lineTo(pad+10,y-10);x.stroke();
    x.fillStyle='#55575B';x.font='15px system-ui, sans-serif';x.fillText('Sapit · Mappa viva · '+location.pathname.replace(/.*\//,''),pad,H-18);
    c.toBlob(function(bl){if(!bl)return;var a=document.createElement('a');a.href=URL.createObjectURL(bl);a.download='sapit-mappa-'+(cur?cur.id:'capitolo')+'.png';document.body.appendChild(a);a.click();setTimeout(function(){URL.revokeObjectURL(a.href);a.remove()},1500);});}
  /* ---------- avvio ---------- */
  function addButtons(){document.querySelectorAll('section.ch').forEach(function(sec){var row=sec.querySelector('.kw-row');if(!row||row.querySelector('.mv-open-btn'))return;if(!mapOf(sec))return;
      var b=document.createElement('button');b.type='button';b.className='kw-btn mv-open-btn';b.setAttribute('aria-expanded','false');b.setAttribute('aria-controls','mv-panel');b.innerHTML='<span aria-hidden="true">🗺</span> Mappa viva';
      b.addEventListener('click',function(){if(cur===sec&&panel&&panel.isConnected){close(false);}else open(sec,b);});row.appendChild(b);});}
  var raf=0;function onScroll(){if(raf)return;raf=requestAnimationFrame(function(){raf=0;if(!cur)return;
      /* cambia capitolo da solo quando entri in un altro */
      var y=innerHeight*.35,s=null;document.querySelectorAll('section.ch').forEach(function(x){var r=x.getBoundingClientRect();if(r.top<=y&&r.bottom>y)s=x});
      if(s&&s!==cur&&mapOf(s)&&!narr&&!buildMode)open(s);tick();});}
  window.addEventListener('scroll',onScroll,{passive:true});window.addEventListener('resize',function(){place();tick();});
  function boot(){addButtons();}
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',function(){setTimeout(boot,0)});else setTimeout(boot,0);
})();
</script>'''


def data_tag(root, n):
    p = os.path.join(root, 'tools', 'mappe', '%s.json' % n)
    if not os.path.exists(p):
        return ''
    d = json.load(open(p, encoding='utf-8'))
    return '<script type="application/json" id="mv-data">' + json.dumps(d, ensure_ascii=False).replace('</', '<\\/') + '</script>'
