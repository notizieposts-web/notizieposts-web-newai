"""Laboratorio di Radar AI (nuovo standard): hub e pagine dei percorsi. Uso: python3 tools/arena_page.py <repo>

Legge i pacchetti tools/arena/packs/*.json (scritti da arena_gen.py), scrive una sfida per file in lab/a<id>.json
e genera azure-laboratorio.html (hub), lab-estrai.html, lab-trasforma.html, lab-confronta.html, lab-prova.html.
"""
import sys, os, json, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import argomenti, graph, bench, store

TOOLS = os.path.dirname(os.path.abspath(__file__))
PACKS = [json.load(open(p, encoding='utf-8')) for p in sorted(glob.glob(os.path.join(TOOLS, 'arena', 'packs', '*.json')))]
CH = [c for p in PACKS for c in p['sfide']]
LAST = PACKS[-1]['giorno'] if PACKS else ''
TRACKS = [('estrai', '🔎', 'Estrai', 'lab-estrai.html', 'Leggi il documento, dai il valore di ogni campo e scegli il metodo giusto: cosa fa il modello e cosa fa il codice.'),
          ('trasforma', '🧮', 'Trasforma', 'lab-trasforma.html', 'Fai scrivere all\'agente la funzione che trasforma l\'output dell\'analizzatore: test visibili e nascosti, come su HackerRank.'),
          ('confronta', '🔀', 'Confronta', 'lab-confronta.html', 'Più documenti collegati e regole precise: applicale e dai l\'esito, come il controllo automatico prima del pagamento.')]
PAGES = {t[0]: t[3] for t in TRACKS}
PAGES['prova'] = 'lab-prova.html'

def meta(c):
    return {'id': c['id'], 't': c['t'], 'd': c['d'], 'p': c['pts'], 'g': c['giorno'], 'k': c['k'], 'tr': c['track'], 'kind': c.get('kind', '')}

CSS = '''<style id="arena-css">
.gbar{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,12rem),1fr));gap:.8rem;margin-top:1.4rem}
.gstat{padding:1rem 1.1rem!important}.gstat .k{font:700 .75rem var(--head,system-ui);letter-spacing:.08em;text-transform:uppercase;color:var(--muted)}
.gstat .v{font:800 1.5rem var(--head,system-ui);margin-top:.2rem}.gstat .s{font-size:.85rem;color:var(--muted)}
.xpbar{height:10px;border-radius:999px;background:var(--soft);border:1px solid var(--line);overflow:hidden;margin-top:.5rem}.xpbar i{display:block;height:100%;background:var(--violet);width:0}
.tracks{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,15rem),1fr));gap:.8rem;margin-top:1.4rem}
a.tcard{display:flex;flex-direction:column;gap:.35rem;padding:1rem 1.1rem;border-radius:18px;border:1px solid var(--line);background:var(--surface);color:var(--ink);text-decoration:none;min-height:44px}
a.tcard b{font:800 1.15rem var(--head,system-ui)}a.tcard .d{font-size:.9rem;color:var(--muted)}a.tcard[aria-current="page"]{border:2px solid var(--violet);background:var(--violet-soft)}
.dprog{display:flex;flex-wrap:wrap;gap:.35rem;margin-top:.3rem}
.chip.dF{background:var(--teal-soft)!important;color:var(--ink)!important;border:1px solid var(--teal)!important}
.chip.dM{background:var(--sun-soft)!important;color:var(--ink)!important;border:1px solid var(--sun)!important}
.chip.dD{background:var(--red-soft)!important;color:var(--ink)!important;border:1px solid var(--red)!important}
.filters{display:flex;flex-wrap:wrap;gap:1rem 1.6rem;margin:1.2rem 0 .6rem;align-items:flex-start}
.filters fieldset{border:0;padding:0;margin:0}.filters legend{font-weight:700;font-size:.85rem;margin-bottom:.3rem}
.seg{display:flex;flex-wrap:wrap;gap:.3rem}.seg label{position:relative}.seg input{position:absolute;opacity:0;width:1px;height:1px}
.seg span{display:inline-flex;align-items:center;min-height:36px;padding:.25rem .8rem;border-radius:999px;border:1px solid var(--line);background:var(--surface);cursor:pointer;font-size:.9rem;font-weight:600}
.seg input:checked+span{background:var(--ink);color:var(--bg);border-color:var(--ink)}.seg input:focus-visible+span{outline:3px solid var(--violet);outline-offset:2px}
.plist{list-style:none;padding:0;margin:.4rem 0 0;border-top:1px solid var(--line)}
.plist li{display:flex;flex-wrap:wrap;align-items:center;gap:.4rem .8rem;padding:.75rem .2rem;border-bottom:1px solid var(--line)}
.plist .pt{flex:1 1 16rem;min-width:0}.plist .pt a{font-weight:700;color:var(--ink)}.plist .pt .sub2{display:block;font-size:.85rem;color:var(--muted)}
.plist .st{font-weight:700;font-size:.9rem;min-width:7.5rem}.plist .st.ok{color:var(--teal)}.plist .st.pa{color:var(--sun-ink,var(--ink))}
.pcount{font-size:.9rem;color:var(--muted);margin:.4rem 0 0}
.back{display:inline-flex;align-items:center;min-height:40px;padding:.3rem .9rem;border-radius:999px;border:1px solid var(--line);background:var(--surface);color:var(--ink);font-weight:700;cursor:pointer;font:inherit;font-weight:700}
.chead h2{margin:.5rem 0 .4rem;font-size:1.5rem}.chead h2:focus{outline:none}
.goal{font-size:1.05rem;font-weight:600}
.guide{margin:1rem 0;padding:1rem 1.2rem;border:2px solid var(--sun);border-left-width:8px;border-radius:14px;background:var(--sun-soft);color:var(--ink)}
.guide h3{margin:0 0 .4rem;font-size:1.05rem}.guide ul{margin:0;padding-left:1.2rem}.guide li{margin:.25rem 0}
.rules{margin:1rem 0;padding:1rem 1.2rem;border:2px solid var(--violet);border-radius:14px;background:var(--violet-soft)}.rules h3{margin:0 0 .4rem;font-size:1.05rem}.rules ol{margin:0;padding-left:1.3rem}.rules li{margin:.3rem 0}
.lgrid{display:grid;grid-template-columns:minmax(0,1fr);gap:1rem;margin-top:1rem}@media (min-width:1000px){.lgrid{grid-template-columns:minmax(0,1fr) minmax(0,1fr)}}
.docs{display:grid;grid-template-columns:minmax(0,1fr);gap:1rem;align-content:start;min-width:0}.docs>div{min-width:0}.dname{font-weight:700;margin:0 0 .3rem}
.paper{background:#FFFFFF;color:#121A2B;border:1px solid #D3D9E6;border-radius:6px;padding:1.2rem 1.3rem;font:15px/1.6 Georgia,'Times New Roman',serif;box-shadow:0 10px 30px rgba(10,14,30,.12);overflow-x:auto;display:flow-root}
.paper .dh{margin-bottom:.6rem}.paper .dr{text-align:right;margin-bottom:.6rem;padding-top:.6rem;border-top:1px solid #D3D9E6}.paper table{display:table!important;width:100%!important;border-collapse:collapse;margin:1rem 0;font-size:14px}
.paper th,.paper td{color:#121A2B;background:#FFFFFF;border-bottom:1px solid #D3D9E6;padding:.3rem .6rem .3rem .4rem;text-align:left}.paper td:nth-child(n+2),.paper th:nth-child(n+2){text-align:right}
.paper .tot{text-align:right;margin:.8rem 0}.paper p{margin:.6rem 0}.paper .ctr{text-align:center}.paper .small{font-size:12px}.paper .h{font-weight:700}.paper .mail{font-family:ui-monospace,Menlo,monospace;font-size:13px;border-bottom:1px solid #D3D9E6;padding-bottom:.5rem}
.paper .hid{opacity:0}.paper.show .hid{opacity:1;background:#FFF5D1;outline:2px dashed #A34E08;color:#121A2B}
.paper .dv.hl-ok{background:#D6F3EC;box-shadow:0 0 0 2px #0A6A7C;border-radius:3px}.paper .dv.hl-ko{background:#FCE7EF;box-shadow:0 0 0 2px #C2185B;border-radius:3px}.paper .dv.hl-hint{background:#FFF5D1;box-shadow:0 0 0 2px #A34E08;border-radius:3px}
.paper sup.tag{font:700 10px system-ui;background:#121A2B;color:#FFFFFF;border-radius:6px;padding:0 4px;margin-left:2px}
.ptool{display:flex;gap:.5rem;flex-wrap:wrap;margin:.5rem 0 0}a.pbtn{display:inline-flex;align-items:center;text-decoration:none}
.pbtn{min-height:40px;padding:.4rem .9rem;border-radius:999px;border:1px solid var(--line);background:var(--surface);color:var(--ink);font-weight:700;cursor:pointer;font-size:.95rem}
.vbtn2{min-height:44px;padding:.45rem 1.2rem;border-radius:999px;border:0;background:var(--violet);color:var(--bg);font:700 1rem var(--head,system-ui);cursor:pointer}
.acts2{display:flex;flex-wrap:wrap;gap:.5rem;margin-top:1rem}
.frow{padding:.8rem 0;border-bottom:1px solid var(--line)}.frow>label,.frow .fl{font-weight:700;display:block}.frow .fmt{display:block;font-size:.88rem;color:var(--muted);margin:.1rem 0 .35rem}
.frow input[type=text],.frow select{font:inherit;min-height:40px;padding:.4rem .7rem;border-radius:10px;border:1px solid var(--line);background:var(--surface);color:var(--ink);width:100%;max-width:22rem;box-sizing:border-box}
.meth{border:0;padding:0;margin:.5rem 0 0}.meth legend{font-size:.85rem;font-weight:700;margin-bottom:.2rem}
.meth .seg span{font-size:.85rem;min-height:34px}
.res{display:block;font-size:.9rem;font-weight:600;margin-top:.3rem}.res.ok{color:var(--teal)}.res.ko{color:var(--red)}
.win{margin:.8rem 0;padding:.6rem .8rem;border-radius:12px;background:var(--teal-soft);border:1px solid var(--teal);font-weight:700}
.warn{margin:.8rem 0;padding:.6rem .8rem;border-radius:12px;background:var(--red-soft);border:1px solid var(--red);font-weight:600}
.code{background:var(--soft);border:1px solid var(--line);border-radius:12px;padding:1rem;overflow-x:auto;font:13px/1.55 ui-monospace,Menlo,Consolas,monospace;white-space:pre;color:var(--ink);max-height:28rem}.code.wrap{white-space:pre-wrap;overflow-wrap:anywhere}
.spec{width:100%;border-collapse:collapse;margin:.6rem 0;font-size:.92rem}.spec th,.spec td{border-bottom:1px solid var(--line);padding:.4rem .5rem;text-align:left;vertical-align:top}.spec td:first-child code{white-space:nowrap}
.tw{overflow-x:auto;max-width:100%}
.editor{width:100%;min-height:16rem;box-sizing:border-box;font:14px/1.55 ui-monospace,Menlo,Consolas,monospace;padding:.8rem;border-radius:12px;border:1px solid var(--line);background:var(--soft);color:var(--ink);tab-size:2}
.tests{list-style:none;padding:0;margin:.6rem 0}.tests li{border:1px solid var(--line);border-radius:12px;padding:.6rem .8rem;margin:.4rem 0}.tests li.ok{border:2px solid var(--teal);background:var(--teal-soft)}.tests li.ko{border:2px solid var(--red);background:var(--red-soft)}
.tests .tt{font-weight:700}.tests pre{margin:.3rem 0 0;white-space:pre-wrap;overflow-wrap:anywhere;font:12.5px/1.5 ui-monospace,Menlo,monospace}
.tsum{font-weight:800;font-size:1.05rem;margin:.6rem 0}
.take{margin-top:1.4rem;padding:1rem 1.2rem;border-radius:16px;border:2px solid var(--teal);background:var(--surface)}.take h3{margin:0 0 .5rem}.take h4{margin:1rem 0 .4rem}
.cost{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,13rem),1fr));gap:.6rem;margin:.6rem 0}.cost div{border:1px solid var(--line);border-radius:12px;padding:.6rem .8rem}.cost b{display:block;font:800 1.3rem var(--head,system-ui)}
.agentbox{margin-top:1rem;border:1px solid var(--line);border-radius:16px;padding:.2rem 1rem 1rem;background:var(--surface)}.agentbox h3{margin:.8rem 0 .2rem;font-size:1.05rem}
.toast{position:fixed;left:50%;bottom:1.2rem;transform:translateX(-50%);z-index:9600;padding:.7rem 1.2rem;border-radius:999px;background:var(--ink);color:var(--bg);font-weight:700;box-shadow:0 10px 30px rgba(0,0,0,.25);opacity:0;transition:opacity .2s;pointer-events:none}.toast.on{opacity:1}
@media (prefers-reduced-motion:reduce){.toast{transition:none}}
#stage{scroll-margin-top:7rem;margin-top:1.6rem}
</style>'''

JS = r'''<script id="arena-js">(function(){
var META=__META__,DAY=__DAY__,PAGES=__PAGES__,PAGE=__PAGE__,LAST=__LAST__,TRACKS=__TRACKS__;
var DN={F:'Facile',M:'Media',D:'Difficile'},DO={F:0,M:1,D:2};
var LV=[[0,'Apprendista'],[200,'Lettore'],[600,'Analista'],[1500,'Ingegnere'],[3000,'Architetto'],[6000,'Maestro'],[10000,'Leggenda']];
var MLAB={extract:'Estrai: è scritto',classify:'Classifica: da un elenco',codice:'Estrai e trasforma nel codice',generate:'Generate: lo produce il modello'};
var $=function(id){return document.getElementById(id)};
function esc(s){return String(s==null?'':s).replace(/[&<>"]/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]})}
/* profilo: punti per sfida (il migliore), giorni con almeno una sfida risolta */
var D0=Date.UTC(2026,9,20);function dnum(s){var p=s.split('-');return Math.round((Date.UTC(+p[0],+p[1]-1,+p[2])-D0)/864e5)}
function enc(S){return Object.keys(S.done).map(function(k){return (+k).toString(36)+'-'+S.done[k]}).join('_')+'~'+Object.keys(S.days).map(function(d){return (+d).toString(36)}).join('.')}
function dec(t){var o={done:{},days:{}};if(!t)return o;var p=String(t).split('~');(p[0]||'').split('_').forEach(function(x){var q=x.split('-');if(q.length===2)o.done[parseInt(q[0],36)]=+q[1]||0});(p[1]||'').split('.').forEach(function(x){if(x)o.days[parseInt(x,36)]=1});return o}
var S=dec(RStore.load('radar_arena'));function save(){RStore.save('radar_arena',enc(S))}
function xp(){return Object.keys(S.done).reduce(function(a,k){return a+S.done[k]},0)}
function today(){var d=new Date();return Math.round((Date.UTC(d.getFullYear(),d.getMonth(),d.getDate())-D0)/864e5)}
function streak(){var t=today(),n=0,d=S.days[t]?t:t-1;while(S.days[d]){n++;d--}return n}
function toast(t){var x=$('toast');if(!x)return;x.textContent=t;x.classList.add('on');clearTimeout(toast.t);toast.t=setTimeout(function(){x.classList.remove('on')},2400)}
function hud(){if(!$('glv'))return;var X=xp(),l=0;for(var i=0;i<LV.length;i++)if(X>=LV[i][0])l=i;$('glv').textContent=LV[l][1];$('gxp').textContent=X.toLocaleString('it-IT');var nx=LV[l+1];
  $('gnext').textContent=nx?('ancora '+(nx[0]-X).toLocaleString('it-IT')+' punti per '+nx[1]):'livello massimo';$('gxpbar').style.width=(nx?((X-LV[l][0])/(nx[0]-LV[l][0])*100):100)+'%';
  var s=streak();$('gstreak').textContent=s+(s===1?' giorno':' giorni');var solved=META.filter(function(m){return S.done[m.id]>=m.p}).length;$('gdone').textContent=solved+' / '+META.length;
  if($('bk'))$('bk').value='ARENA1:'+enc(S)}
function record(c,score){var prev=S.done[c.id]||0,first=S.done[c.id]===undefined;score=Math.round(score);if(score>prev||first){S.done[c.id]=Math.max(prev,score)}
  if(score>=c.pts)S.days[today()]=1;save();hud();toast(score>prev?('+'+(score-prev)+' punti'+(score>=c.pts?' · sfida risolta!':'')):(score>=c.pts?'Sfida risolta':'Tentativo registrato: il punteggio migliore resta '+prev))}
function stat(m){var v=S.done[m.id];if(v===undefined)return ['Da fare',''];if(v>=m.p)return ['✓ Risolta','ok'];return ['Tentata · '+v+'/'+m.p,'pa']}
function num(v){v=String(v).trim().replace(/[\s$€%]/g,'');if(!v)return NaN;if(v.indexOf(',')>=0&&v.indexOf('.')>=0){if(v.lastIndexOf(',')>v.lastIndexOf('.'))v=v.replace(/\./g,'').replace(',','.');else v=v.replace(/,/g,'')}else if(v.indexOf(',')>=0)v=v.replace(',','.');else if(/^-?[1-9]\d{0,2}(\.\d{3})+$/.test(v))v=v.replace(/\./g,'');return parseFloat(v)}
function right(f,v){v=String(v||'').trim().replace(/\s+/g,' ');if(!v)return false;if(f.type==='num'){var n=num(v);return !isNaN(n)&&Math.abs(n-f.ans)<=0.011}
  if(f.type==='date'||f.type==='enum'||/MAIUSCOLO/.test(f.fmt))return v===String(f.ans);return v.toLowerCase()===String(f.ans).toLowerCase()}
function deq(a,b){if(typeof a==='number'&&typeof b==='number')return Math.abs(a-b)<=0.005;if(a===null||b===null||typeof a!=='object'||typeof b!=='object')return a===b;
  if(Array.isArray(a)!==Array.isArray(b))return false;var ka=Object.keys(a),kb=Object.keys(b);if(ka.length!==kb.length)return false;return ka.every(function(k){return Object.prototype.hasOwnProperty.call(b,k)&&deq(a[k],b[k])})}
function J(o){return JSON.stringify(o,null,2)}
function pascal(s){return s.split('_').map(function(p){return p.charAt(0).toUpperCase()+p.slice(1)}).join('')}
var CACHE={};function get(id){if(CACHE[id])return Promise.resolve(CACHE[id]);return fetch('lab/a'+id+'.json').then(function(r){if(!r.ok)throw new Error(r.status);return r.json()}).then(function(c){CACHE[id]=c;return c})}
function fday(g){var p=g.split('-');return +p[2]+'/'+(+p[1])}
/* ---------------- elenco sfide (stile HackerRank) */
var F={d:'all',s:'all',g:'oggi'};
function list(){var L=META.filter(function(m){return (F.d==='all'||m.d===F.d)&&(F.g==='all'||m.g===LAST)&&(F.s==='all'||(F.s==='todo'?!(S.done[m.id]>=m.p):S.done[m.id]>=m.p))})
    .sort(function(a,b){return a.g<b.g?1:a.g>b.g?-1:(DO[a.d]-DO[b.d])||(a.id-b.id)});
  $('pcount').textContent=L.length+(L.length===1?' sfida':' sfide');
  $('plist').innerHTML=L.length?L.map(function(m){var s=stat(m);return '<li><span class="pt"><a href="#a'+m.id+'" id="l'+m.id+'">'+esc(m.t)+'</a><span class="sub2">'+esc(m.kind)+' · giorno '+fday(m.g)+' · livello '+m.k+'</span></span><span class="chip d'+m.d+'">'+DN[m.d]+'</span><span class="chip">'+m.p+' punti</span><span class="st '+s[1]+'">'+s[0]+'</span></li>'}).join(''):'<li>Nessuna sfida con questi filtri.</li>'}
function filters(){document.querySelectorAll('.filters input').forEach(function(i){if(F[i.name]===i.value)i.checked=true;i.onchange=function(){F[this.name]=this.value;list()}})}
/* ---------------- vista sfida */
var cur=null;
function head(c){var s=stat({id:c.id,p:c.pts});return '<div class="chead"><button type="button" class="back" id="back">← Tutte le sfide</button><div class="kicker" style="margin-top:.8rem"><span class="chip d'+c.d+'">'+DN[c.d]+'</span><span class="chip">'+c.pts+' punti</span><span class="chip">'+esc(c.kind)+'</span><span class="chip">giorno '+fday(c.giorno)+' · livello '+c.k+'</span>'+(s[1]?'<span class="chip done">'+s[0]+'</span>':'')+'</div>'+
  '<h2 id="ctitle" tabindex="-1">'+esc(c.t)+'</h2><p class="goal">'+esc(c.goal)+'</p><p>'+esc(c.ctx)+'</p></div>'+
  '<section class="guide" aria-labelledby="gh'+c.id+'"><h3 id="gh'+c.id+'">📋 Linee guida: cosa notare prima di iniziare</h3><ul>'+c.guide.map(function(g){return '<li>'+esc(g)+'</li>'}).join('')+'</ul></section>'}
function docs(c){return '<div class="docs">'+c.docs.map(function(d,j){return '<div><p class="dname" id="dn'+c.id+'_'+j+'">📄 '+esc(d.nome)+'</p><div class="paper" id="paper'+j+'" tabindex="0" role="document" aria-labelledby="dn'+c.id+'_'+j+'">'+d.html+'</div>'+
  '<div class="ptool">'+(d.dl?'<a class="pbtn" href="'+d.dl+'" download>⬇ Scarica il PDF'+(d.kb?' ('+d.kb+' KB)':'')+'</a>':'')+(c.trap&&j===0?'<button type="button" class="pbtn" id="showhid" aria-pressed="false">👁 Mostra il testo nascosto (quello che legge il servizio)</button>':'')+'</div></div>'}).join('')+'</div>'}
function wireHid(){if($('showhid'))$('showhid').onclick=function(){var p=$('paper0'),on=!p.classList.contains('show');p.classList.toggle('show',on);this.setAttribute('aria-pressed',on?'true':'false')}}
function paint(c,ok){document.querySelectorAll('.paper sup.tag').forEach(function(s){s.remove()});document.querySelectorAll('.paper .dv').forEach(function(s){s.classList.remove('hl-ok','hl-ko','hl-hint')});
  c.fields.forEach(function(f,i){(f.src||[]).forEach(function(k){document.querySelectorAll('.paper .dv[data-k="'+k+'"]').forEach(function(s){s.classList.add(ok[i]?'hl-ok':'hl-ko');if(!s.querySelector('sup'))s.insertAdjacentHTML('beforeend','<sup class="tag" aria-hidden="true">'+(i+1)+'</sup>')})})})}
function hint(c,i){document.querySelectorAll('.paper .dv').forEach(function(s){s.classList.remove('hl-hint')});(c.fields[i].src||[]).forEach(function(k){document.querySelectorAll('.paper .dv[data-k="'+k+'"]').forEach(function(s){s.classList.add('hl-hint')})})}
/* campi: Estrai (valore + metodo) e Confronta (solo valore) */
function form(c,withMeth){var h='<form id="ff" novalidate>';c.fields.forEach(function(f,i){var id='f'+c.id+'_'+i;h+='<div class="frow"><label for="'+id+'"><span aria-hidden="true">'+(i+1)+'.</span> <code>'+esc(f.label)+'</code></label><span class="fmt" id="'+id+'d">Formato: '+esc(f.fmt)+'</span>';
    if(f.type==='enum')h+='<select id="'+id+'" aria-describedby="'+id+'d"><option value="">Scegli…</option>'+f.opts.map(function(o){return '<option>'+esc(o)+'</option>'}).join('')+'</select>';
    else h+='<input type="text" id="'+id+'" autocomplete="off" aria-describedby="'+id+'d"'+(f.type==='num'?' inputmode="decimal"':'')+'>';
    if(withMeth)h+='<fieldset class="meth"><legend>Metodo per <code>'+esc(f.label)+'</code></legend><div class="seg">'+['extract','classify','codice','generate'].map(function(m){return '<label><input type="radio" name="m'+i+'" value="'+m+'"><span>'+MLAB[m]+'</span></label>'}).join('')+'</div></fieldset>';
    h+='<span class="res" id="'+id+'r" role="status"></span></div>'});
  return h+'<div class="acts2" id="facts"><button type="submit" class="vbtn2">Verifica</button><button type="button" class="pbtn" id="fhint">💡 Indizio (−10%)</button><button type="button" class="pbtn" id="fsol">Mostra la soluzione</button></div><p class="tsum" id="fsum" role="status" aria-live="polite"></p></form>'}
function fieldGame(c,withMeth){var a={tries:0,hints:0,closed:false},n=c.fields.length;
  function val(i){return $('f'+c.id+'_'+i).value}function meth(i){var r=document.querySelector('input[name="m'+i+'"]:checked');return r?r.value:''}
  $('ff').onsubmit=function(ev){ev.preventDefault();if(a.closed){toast('Sfida chiusa: premi «Rifai la sfida» per ricominciare');return}
    if(withMeth&&c.fields.some(function(f,i){return !meth(i)})){$('fsum').textContent='Scegli il metodo per ogni campo prima di verificare.';return}
    a.tries++;var okv={},sc=0,allv=true,allm=true;
    c.fields.forEach(function(f,i){var v=right(f,val(i)),m=!withMeth||meth(i)===f.meth;okv[i]=v&&m;if(!v)allv=false;if(!m)allm=false;sc+=(withMeth?(v?.7:0)+(m?.3:0):(v?1:0))/n;
      var r=$('f'+c.id+'_'+i+'r');r.className='res '+(v&&m?'ok':'ko');r.textContent=withMeth?((v?'✓ Valore':'✗ Valore')+' · '+(m?'✓ Metodo':'✗ Metodo')):(v?'✓ Giusto':'✗ Non ancora')});
    var mult=Math.max(.4,1-.15*(a.tries-1)-.1*a.hints),pts=c.pts*sc*mult;paint(c,okv);
    if(allv&&allm){a.closed=true;record(c,pts);$('fsum').textContent='Tutto giusto: '+Math.round(pts)+' punti su '+c.pts+'.';take(c,withMeth)}
    else $('fsum').textContent='Corretti '+Object.keys(okv).filter(function(k){return okv[k]}).length+' campi su '+n+'. Correggi e verifica di nuovo'+(a.tries>=1?' (ogni nuovo tentativo vale un po\' meno)':'')+'.'};
  $('fhint').onclick=function(){if(a.closed)return;var i=c.fields.findIndex(function(f,j){var r=$('f'+c.id+'_'+j+'r');return !(r&&r.classList.contains('ok'))});if(i<0)i=0;a.hints++;hint(c,i);
    var f=c.fields[i];toast('Campo '+(i+1)+': '+((f.src||[]).length?'guarda le parti evidenziate in giallo':'rileggi le linee guida')+(withMeth?'. Il metodo: '+(f.meth==='codice'?'il valore richiesto è diverso da quello scritto?':'il valore è già scritto così com\'è serve?'):''))};
  $('fsol').onclick=function(){if(!a.closed){a.closed=true;if(S.done[c.id]===undefined){S.done[c.id]=0;save();hud()}}
    c.fields.forEach(function(f,i){var r=$('f'+c.id+'_'+i+'r');r.className='res';r.textContent='Risposta: '+f.ans+(withMeth?' · metodo: '+MLAB[f.meth]:'')});paint(c,{});take(c,withMeth)};}
function redo(c){var b=$('redo');if(b)b.onclick=function(){open(c.id,true)}}
function take(c,withMeth){var h='<section class="take" aria-labelledby="tk'+c.id+'"><h3 id="tk'+c.id+'">Cosa porti a casa</h3><ol>'+c.fields.map(function(f){return '<li><code>'+esc(f.label)+'</code> = <b>'+esc(f.ans)+'</b>'+(withMeth?' · <i>'+MLAB[f.meth]+'</i>':'')+'. '+esc(f.why)+(f.note?' <b>'+esc(f.note)+'</b>':'')+'</li>'}).join('')+'</ol>';
  if(withMeth){h+='<h4>Perché questi metodi</h4><ul><li><b>Estrai</b>: '+esc(c.meth_why.extract)+'</li><li><b>Classifica</b>: '+esc(c.meth_why.classify)+'</li><li><b>Nel codice</b>: '+esc(c.meth_why.codice)+'</li></ul>';
    h+='<h4>Lo schema per Content Understanding</h4><p>Solo quello che il modello deve leggere: i campi da calcolare arrivano come dati grezzi e li trasforma il tuo codice (è il percorso 🧮 Trasforma).</p><div class="code" tabindex="0" role="region" aria-label="Schema JSON">'+esc(c.schema)+'</div>'}
  else{h+='<h4>Le regole in codice (Python)</h4><p>Il modello estrae i valori dai documenti; il confronto lo fa questo codice, sempre uguale e senza costi per documento.</p><div class="code" tabindex="0" role="region" aria-label="Codice Python">'+esc(c.py)+'</div>'}
  h+='<div class="acts2"><button type="button" class="pbtn" id="redo">↺ Rifai la sfida</button><button type="button" class="pbtn" id="nextc">Prossima sfida da fare →</button></div></section>';
  $('out').innerHTML=h;redo(c);$('nextc').onclick=nextTodo}
function rEstrai(c){var h=head(c)+'<div class="lgrid">'+docs(c)+'<div class="card">'+form(c,true)+'</div></div><div id="out"></div><div id="benchbox"></div>';$('stage').innerHTML=h;wireHid();fieldGame(c,true);
  var T={};c.fields.forEach(function(f){if(f.meth!=='codice')T[pascal(f.label)]=f.ans});
  RadarBench.mount($('benchbox'),{doc:function(){return c.docs.map(function(d){return RadarBench.h2t(d.html)}).join('\n\n')},schema:c.schema,truth:T,trap:c.trap,title:'Banco di prova: fai leggere il documento a un modello gratuito con lo schema'})}
function rConfronta(c){var h=head(c)+'<section class="rules" aria-labelledby="rh'+c.id+'"><h3 id="rh'+c.id+'">⚖️ Regole di confronto</h3><ol>'+c.rules.map(function(r){return '<li>'+esc(r)+'</li>'}).join('')+'</ol></section><div class="lgrid">'+docs(c)+'<div class="card">'+form(c,false)+'</div></div><div id="out"></div>';
  $('stage').innerHTML=h;fieldGame(c,false)}
/* ---------------- Trasforma: editor, Worker isolato, test visibili e nascosti */
var WK='self.fetch=undefined;self.XMLHttpRequest=undefined;self.WebSocket=undefined;self.importScripts=undefined;self.EventSource=undefined;self.indexedDB=undefined;'+
  'onmessage=function(e){var fn,out=[];try{fn=(new Function(e.data.code+"\\n;return typeof trasforma===\\"function\\"?trasforma:null;"))()}catch(err){postMessage({err:"Il codice non si compila: "+err.message});return}'+
  'if(!fn){postMessage({err:"Non trovo function trasforma(input)."});return}e.data.cases.forEach(function(c){try{out.push({v:fn(JSON.parse(JSON.stringify(c)))})}catch(err){out.push({e:String(err&&err.message||err)})}});postMessage({out:out})}';
var WURL=URL.createObjectURL(new Blob([WK],{type:'text/javascript'}));
function runCases(code,cases){return new Promise(function(res){var w=new Worker(WURL),done=false;var t=setTimeout(function(){if(done)return;done=true;w.terminate();res({err:'Tempo scaduto (3 secondi): c\'è un ciclo infinito?'})},3000);
  w.onmessage=function(e){if(done)return;done=true;clearTimeout(t);w.terminate();res(e.data)};w.onerror=function(e){if(done)return;done=true;clearTimeout(t);w.terminate();res({err:e.message||'Errore nel codice'});e.preventDefault()};
  w.postMessage({code:code,cases:cases.map(function(x){return x.in})})})}
var STUB='function trasforma(input) {\n  // input: i campi estratti dall\'analizzatore (vedi gli esempi)\n  // restituisci un oggetto con i campi richiesti dalla specifica\n  return {};\n}';
function rTrasforma(c){var key='arena_code_'+c.id,saved='';try{saved=localStorage.getItem(key)||''}catch(e){}
  var h=head(c)+'<div class="card"><h3 style="margin-top:0">Specifica dell\'output</h3><div class="tw"><table class="spec"><thead><tr><th scope="col">Campo</th><th scope="col">Tipo</th><th scope="col">Regola</th></tr></thead><tbody>'+
    c.spec.map(function(s){return '<tr><td>'+(s.k==='—'?'<i>nota</i>':'<code>'+esc(s.k)+'</code>')+'</td><td>'+esc(s.t)+'</td><td>'+esc(s.r)+'</td></tr>'}).join('')+'</tbody></table></div>'+
    '<h3>Esempi (test visibili)</h3><ul class="tests">'+c.visible.map(function(t,i){return '<li><span class="tt">Esempio '+(i+1)+'</span><pre>input:  '+esc(JSON.stringify(t.in))+'\noutput: '+esc(JSON.stringify(t.out))+'</pre></li>'}).join('')+'</ul>'+
    '<p>Oltre a questi ci sono <b>'+c.hidden.length+' test nascosti</b>: vedi solo se passano.</p></div>'+
    '<div class="lgrid"><div class="card"><label for="ed" style="font-weight:700;display:block">La tua funzione (JavaScript)</label><p class="fmt" style="font-size:.88rem;color:var(--muted);margin:.2rem 0 .5rem" id="edd">Gira nel tuo browser, isolata: niente rete, al massimo 3 secondi. Puoi scriverla tu o farla scrivere all\'agente qui accanto.</p>'+
    '<textarea id="ed" class="editor" spellcheck="false" autocapitalize="off" aria-describedby="edd">'+esc(saved||STUB)+'</textarea><div class="acts2"><button type="button" class="pbtn" id="runv">▶ Prova sugli esempi</button><button type="button" class="vbtn2" id="runall">Invia: tutti i test</button><button type="button" class="pbtn" id="tsol">Mostra la soluzione</button></div>'+
    '<p class="tsum" id="tsum" role="status" aria-live="polite"></p><ul class="tests" id="tres"></ul></div>'+
    '<div class="agentbox"><h3>🤖 Chiedi all\'agente di scriverla</h3><label style="display:flex;gap:.5rem;align-items:center;font-weight:600;margin:.4rem 0"><input type="checkbox" id="attach" checked> Allega alla richiesta gli esempi visibili</label><div id="agent"></div></div></div><div id="out"></div>';
  $('stage').innerHTML=h;var a={tries:0,best:0,solved:false,shown:false};
  $('ed').addEventListener('keydown',function(e){if(e.key==='Enter'&&(e.ctrlKey||e.metaKey)){e.preventDefault();$('runv').click()}});
  function store(){try{localStorage.setItem(key,$('ed').value)}catch(e){}}
  function show(res,cases,vis){var ok=0,html='';if(res.err){$('tsum').textContent='⚠ '+res.err;$('tres').innerHTML='';return 0}
    res.out.forEach(function(r,i){var t=cases[i],g=!r.e&&deq(r.v,t.out);if(g)ok++;var lab=i<c.visible.length?'Esempio '+(i+1):'Test nascosto '+(i-c.visible.length+1);
      if(i<c.visible.length)html+='<li class="'+(g?'ok':'ko')+'"><span class="tt">'+(g?'✓ ':'✗ ')+lab+'</span>'+(g?'':'<pre>atteso:    '+esc(JSON.stringify(t.out))+'\nottenuto:  '+esc(r.e?('errore: '+r.e):JSON.stringify(r.v===undefined?null:r.v))+'</pre>')+'</li>';
      else html+='<li class="'+(g?'ok':'ko')+'"><span class="tt">'+(g?'✓ ':'✗ ')+lab+'</span>'+(g?'':(r.e?' · errore durante l\'esecuzione':' · risultato diverso dall\'atteso'))+'</li>'});
    $('tres').innerHTML=html;$('tsum').textContent=(vis?'Esempi superati: ':'Test superati: ')+ok+' su '+cases.length+(ok===cases.length?' ✓':'');return ok}
  $('runv').onclick=function(){store();$('tsum').textContent='Eseguo…';runCases($('ed').value,c.visible).then(function(r){show(r,c.visible,true)})};
  $('runall').onclick=function(){store();var cases=c.visible.concat(c.hidden);$('tsum').textContent='Eseguo tutti i test…';runCases($('ed').value,cases).then(function(r){var ok=show(r,cases,false);if(r.err)return;a.tries++;
    var sc=c.pts*ok/cases.length*(a.shown?0:1);record(c,sc);if(ok===cases.length&&!a.solved){a.solved=true;takeT(c,true)}else if(ok<cases.length){
      var vok=r.out.slice(0,c.visible.length).every(function(x,i){return !x.e&&deq(x.v,c.visible[i].out)});if(vok)$('tsum').textContent+=' · Gli esempi passano ma qualche test nascosto no: rileggi la specifica e chiediti "e se…?" (vuoto, negativo, formato diverso).'}})};
  $('tsol').onclick=function(){a.shown=true;if(S.done[c.id]===undefined){S.done[c.id]=0;save();hud()}takeT(c,false)};
  RadarBench.mountAgent($('agent'),{placeholder:'Esempio: scrivi una funzione JavaScript trasforma(input) che riceve … e restituisce … Se … allora … Arrotonda …',
    context:function(){return $('attach').checked?'Esempi di input e output attesi:\n'+c.visible.map(function(t){return JSON.stringify(t.in)+' → '+JSON.stringify(t.out)}).join('\n'):''},
    saved:(function(){try{return localStorage.getItem('arena_ask_'+c.id)||''}catch(e){return ''}})(),onAsk:function(q){try{localStorage.setItem('arena_ask_'+c.id,q)}catch(e){}},
    onCode:function(code){$('ed').value=code;store();$('ed').focus();toast('Codice copiato nell\'editor: provalo sugli esempi')}})}
function takeT(c,won){var tin=c.gen.tin,tout=c.gen.tout,per=(tin*0.4+tout*1.6)/1e6,N=100000;
  var h='<section class="take" aria-labelledby="tk'+c.id+'"><h3 id="tk'+c.id+'">'+(won?'Tutti i test passano. ':'')+'Cosa porti a casa</h3>'+
  '<h4>Perché una funzione e non un campo generate</h4><p>La trasformazione è fissa: la scrivi (o la fai scrivere) una volta e gira gratis, sempre uguale, su ogni documento. Con un campo <code>generate</code> pagheresti il modello a ogni documento, e il risultato potrebbe cambiare da una volta all\'altra.</p>'+
  '<div class="cost"><div><span>Campo generate, per documento</span><b>'+(per*1000).toFixed(3).replace('.',',')+' $ ogni 1.000</b><span>circa '+tin+' token in ingresso e '+tout+' in uscita</span></div><div><span>'+N.toLocaleString('it-IT')+' documenti al mese con generate</span><b>'+(per*N).toFixed(2).replace('.',',')+' $</b><span>e qualche risposta da ricontrollare</span></div><div><span>Con la funzione</span><b>0 $</b><span>più i pochi centesimi della richiesta all\'agente, una volta</span></div></div>'+
  '<p class="fmt" style="font-size:.85rem;color:var(--muted)">Tariffe del gioco, ipotetiche, per un modello mini: 0,40 $ per milione di token in ingresso e 1,60 $ in uscita.</p>'+
  '<h4>Una soluzione di riferimento (JavaScript)</h4><div class="code" tabindex="0" role="region" aria-label="Soluzione in JavaScript">'+esc(c.ref_js)+'</div>'+
  '<h4>La stessa, in Python, da usare dopo Content Understanding</h4><div class="code" tabindex="0" role="region" aria-label="Soluzione in Python">'+esc(c.ref_py)+'</div>'+
  '<div class="acts2"><button type="button" class="pbtn" id="redo">↺ Rifai la sfida</button><button type="button" class="pbtn" id="nextc">Prossima sfida da fare →</button></div></section>';
  $('out').innerHTML=h;$('redo').onclick=function(){try{localStorage.removeItem('arena_code_'+c.id)}catch(e){}open(c.id,true)};$('nextc').onclick=nextTodo}
var REND={estrai:rEstrai,trasforma:rTrasforma,confronta:rConfronta};
function open(id,keep){$('listview').hidden=true;$('stage').hidden=false;$('stage').innerHTML='<p role="status">Carico la sfida…</p>';
  get(id).then(function(c){cur=c;REND[c.track](c);$('back').onclick=function(){location.hash=''};if(!keep)$('stage').scrollIntoView({block:'start'});$('ctitle').focus({preventScroll:true})})
    .catch(function(){$('stage').innerHTML='<p class="warn">Non riesco a caricare la sfida: controlla la connessione e riprova.</p><button type="button" class="back" id="back">← Tutte le sfide</button>';$('back').onclick=function(){location.hash=''}})}
function nextTodo(){var L=META.slice().sort(function(a,b){return a.g<b.g?1:a.g>b.g?-1:(DO[a.d]-DO[b.d])||(a.id-b.id)});var m=L.find(function(x){return !(S.done[x.id]>=x.p)&&(!cur||x.id!==cur.id)});if(m)location.hash='a'+m.id;else toast('Hai risolto tutte le sfide di questo percorso!')}
function route(){var m=/^#a(\d+)$/.exec(location.hash);if(m&&META.some(function(x){return x.id===+m[1]})){open(+m[1])}else{var back=cur;cur=null;$('stage').hidden=true;$('stage').innerHTML='';$('listview').hidden=false;list();if(back&&$('l'+back.id))$('l'+back.id).focus()}}
/* ---------------- hub */
function hubToday(){TRACKS.forEach(function(t){var el=$('tp_'+t[0]);if(!el)return;var L=DAY.filter(function(m){return m.tr===t[0]});
  el.innerHTML=['F','M','D'].map(function(d){var x=L.filter(function(m){return m.d===d}),ok=x.filter(function(m){return S.done[m.id]>=m.p}).length;return '<span class="chip d'+d+'">'+DN[d]+' '+ok+'/'+x.length+'</span>'}).join('')})}
hud();hubToday();
if(PAGE==='hub'){
  $('bc').onclick=function(){var t=$('bk');t.select();try{navigator.clipboard.writeText(t.value).then(function(){$('bm').textContent='Codice copiato.'},function(){document.execCommand('copy');$('bm').textContent='Codice copiato.'})}catch(e){document.execCommand('copy');$('bm').textContent='Codice copiato.'}};
  $('br').onclick=function(){var v=$('bi').value.trim();if(v.indexOf('ARENA1:')!==0){$('bm').textContent='⚠ Questo non sembra un codice del Laboratorio (deve iniziare con ARENA1:).';return}S=dec(v.slice(7));save();hud();hubToday();$('bi').value='';$('bm').textContent='Progressi ripristinati: '+Object.keys(S.done).length+' sfide.'};
  var lr=$('lreset');function lrInit(){lr.innerHTML='<button type="button" class="pbtn" id="r1">Azzera i progressi del Laboratorio</button>';$('r1').onclick=function(){lr.innerHTML='<span style="font-weight:700">Cancellare punti e sfide risolte?</span> <button type="button" class="vbtn2" id="r2">Sì, azzera</button> <button type="button" class="pbtn" id="r3">Annulla</button>';$('r3').focus();$('r3').onclick=function(){lrInit();$('r1').focus()};$('r2').onclick=function(){S={done:{},days:{}};save();hud();hubToday();lrInit();$('r1').focus();toast('Progressi azzerati')}}}lrInit();
  var hm=/^#a(\d+)$/.exec(location.hash);if(hm){var mm=META.find(function(x){return x.id===+hm[1]});if(mm)location.replace(PAGES[mm.tr]+'#a'+mm.id)}}
else if(PAGE==='prova'){var first=null;RadarBench.mount($('sbox'),{open:true,docText:__PROVA_DOC__,schema:__PROVA_SCHEMA__,title:'Banco di prova libero',
  savedDoc:(function(){try{return localStorage.getItem('arena_prova_doc')||''}catch(e){return ''}})(),onSave:function(v){try{localStorage.setItem('arena_prova_doc',v.doc||'')}catch(e){}}})}
else{filters();window.addEventListener('hashchange',route);route()}
})();</script>'''

def main(root):
    eds = graph.data(root)
    lab = os.path.join(root, 'lab'); os.makedirs(lab, exist_ok=True)
    for c in CH:
        json.dump(c, open(os.path.join(lab, 'a%d.json' % c['id']), 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    head = argomenti.head_from(root, 'Laboratorio') + CSS + bench.CSS + store.BACKUP_CSS + '</head>\n<body>\n'
    first = next((c for c in reversed(CH) if c['track'] == 'estrai'), None)
    def page(fname, pg, title, hero_html, body_html, meta_list):
        js = (JS.replace('__META__', json.dumps(meta_list, ensure_ascii=False, separators=(',', ':'))).replace('__PAGES__', json.dumps(PAGES)).replace('__PAGE__', json.dumps(pg))
              .replace('__LAST__', json.dumps(LAST)).replace('__DAY__', json.dumps([{'id': c['id'], 'tr': c['track'], 'd': c['d'], 'p': c['pts']} for c in CH if c['giorno'] == LAST], separators=(',', ':'))).replace('__TRACKS__', json.dumps([t[:4] for t in TRACKS], ensure_ascii=False))
              .replace('__PROVA_DOC__', json.dumps(bench_text(first) if first else '', ensure_ascii=False)).replace('__PROVA_SCHEMA__', json.dumps(first['schema'] if first else '{}', ensure_ascii=False)))
        h = (head.replace('<title>Laboratorio · Radar AI</title>', '<title>%s · Radar AI</title>' % title) + argomenti.NAV('azure-laboratorio.html', eds) + hero_html +
             '<main class="wrap">' + body_html + '</main><div class="toast" id="toast" role="status" aria-live="polite"></div>' + argomenti.FOOT + argomenti.JS + store.JS + bench.JS + js + '\n</body>\n</html>\n')
        open(os.path.join(root, fname), 'w', encoding='utf-8').write(h); return len(h)
    GBAR = ('<div class="gbar"><div class="card gstat"><div class="k">Livello</div><div class="v" id="glv">Apprendista</div><div class="xpbar" aria-hidden="true"><i id="gxpbar"></i></div><div class="s" id="gnext"></div></div>'
            '<div class="card gstat"><div class="k">Punti</div><div class="v" id="gxp">0</div><div class="s">il punteggio migliore di ogni sfida</div></div>'
            '<div class="card gstat"><div class="k">Serie</div><div class="v" id="gstreak">0 giorni</div><div class="s">giorni di fila con almeno una sfida risolta</div></div>'
            '<div class="card gstat"><div class="k">Sfide risolte</div><div class="v" id="gdone">0</div><div class="s">con il punteggio pieno</div></div></div>')
    def tracks_nav(curp):
        return ('<nav class="tracks" aria-label="Percorsi del Laboratorio">' + ''.join(
            '<a class="tcard" href="%s"%s><b>%s %s</b><span class="d">%s</span><span class="dprog" id="tp_%s"></span></a>' % (f, ' aria-current="page"' if k == curp else '', ic, lab_, d, k)
            for k, ic, lab_, f, d in TRACKS) + '<a class="tcard" href="lab-prova.html"%s><b>🤖 Prova libera</b><span class="d">Incolla un documento e uno schema e fai lavorare un modello gratuito.</span></a></nav>' % (' aria-current="page"' if curp == 'prova' else ''))
    n_day = sum(1 for c in CH if c['giorno'] == LAST)
    gday = ('%d/%d' % (int(LAST[8:10]), int(LAST[5:7]))) if LAST else ''
    hero = ('<header class="hero"><div><div class="meta"><span class="chip guide">Laboratorio</span><span class="chip">%d sfide</span><span class="chip">3 percorsi</span></div>'
            '<h1 style="margin-top:1.2rem">Laboratorio: usare bene agenti e Content Understanding</h1>'
            '<p class="sub">Non si tratta di programmare: si impara a decidere cosa far fare al modello, cosa al codice, e come chiedere a un agente di scriverlo. Ogni giorno 10 sfide nuove per percorso, 4 facili, 4 medie e 2 difficili, un po\' più impegnative del giorno prima.</p></div>%s</header>') % (len(CH), argomenti.MARK)
    RULES = ('<section class="ch" id="regole"><div class="ch-head"><div class="kicker"><span class="chip guide">Regole</span></div><h2>Come funziona</h2></div><div class="prose"><ul>'
             '<li><b>Ogni giorno</b> escono 30 sfide: 10 per percorso, con 4 Facili (20 punti), 4 Medie (40) e 2 Difficili (80). Le sfide dei giorni passati restano disponibili.</li>'
             '<li><b>🔎 Estrai</b>: per ogni campo dai il valore (70% del punteggio) e il metodo (30%): estrarre, classificare, oppure estrarre il dato grezzo e trasformarlo nel codice. <code>generate</code> è quasi sempre la scelta sbagliata quando una regola fissa basta.</li>'
             '<li><b>🧮 Trasforma</b>: il punteggio è la quota di test superati, visibili e nascosti. Puoi scrivere la funzione o farla scrivere all\'agente: il bello è imparare a chiedere bene.</li>'
             '<li><b>🔀 Confronta</b>: applica le regole a più documenti e dai l\'esito. Il punteggio è la quota di risposte giuste.</li>'
             '<li>Ogni nuovo tentativo e ogni indizio valgono un po\' meno; conta sempre il punteggio migliore. "Mostra la soluzione" chiude la sfida senza punti, ma puoi rifarla.</li>'
             '<li>Le <b>linee guida</b> di ogni sfida dicono cosa notare, non la risposta. Dopo la verifica trovi "Cosa porti a casa": metodo di ogni campo, schema, codice Python.</li>'
             '<li>Il modello gratuito gira nel tuo browser (WebLLM) o è Gemini con la tua chiave: simula il passaggio generativo, non è il servizio Azure. Prezzi e tariffe nel gioco sono ipotetici.</li></ul></div></section>')
    VERO = ('<section class="ch" id="vero"><div class="ch-head"><div class="kicker"><span class="chip guide">Il servizio vero</span></div><h2>Provare Content Understanding senza spendere</h2></div>'
            '<div class="prose"><ul><li><b>Account gratuito di Azure</b>: 200 dollari di credito da usare entro 30 giorni; alla registrazione servono una carta non prepagata e un numero di telefono.</li>'
            '<li><b>Livello gratuito F0</b> della risorsa Foundry per le prime prove, poi un piano a pagamento per la produzione.</li>'
            '<li><b>Attenzione ai token</b>: i campi generativi usano la distribuzione del modello collegata in Foundry, e quei token si pagano a parte. <code>prebuilt-read</code> e <code>prebuilt-layout</code> non usano modelli linguistici.</li>'
            '<li>I PDF scaricabili del Laboratorio sono fatti apposta: dati inventati, nessun dato reale.</li></ul><p class="note">Fonti: Microsoft Azure, account gratuito; Microsoft Learn, tutorial Content Understanding e guida ai prezzi.</p></div></section>')
    BACKUP = ('<details class="backup"><summary>💾 Codice di backup dei progressi</summary><p>I progressi si salvano da soli in questo browser. Per portarli su un altro computer, copia questo codice e incollalo là.</p>'
              '<label for="bk">Il tuo codice</label><textarea id="bk" readonly></textarea><div class="brow"><button type="button" class="pbtn" id="bc">Copia il codice</button></div>'
              '<label for="bi">Incolla un codice salvato</label><textarea id="bi"></textarea><div class="brow"><button type="button" class="pbtn" id="br">Ripristina</button></div><p class="bmsg" id="bm" role="status" aria-live="polite"></p></details>')
    sizes = {}
    sizes['azure-laboratorio.html'] = page('azure-laboratorio.html', 'hub', 'Laboratorio', hero,
        '<section class="ch" id="gioco" style="padding-top:2.5rem"><div class="ch-head"><div class="kicker"><span class="chip guide">Oggi</span></div><h2>Le sfide del %s</h2><p class="lead">%d sfide nuove: scegli un percorso. Sotto ogni percorso vedi quante ne hai risolte oggi, per difficoltà.</p></div>' % (gday, n_day) +
        tracks_nav(None) + GBAR + '<div class="acts2" id="lreset"></div>' + BACKUP + '</section>' + RULES + VERO, [meta(c) for c in CH])
    for k, ic, lab_, f, d in TRACKS:
        ml = [meta(c) for c in CH if c['track'] == k]
        hh = ('<header class="hero"><div><div class="meta"><span class="chip guide">Laboratorio</span><span class="chip">%d sfide</span></div><h1 style="margin-top:1.2rem">%s %s</h1><p class="sub">%s <a href="azure-laboratorio.html#regole">Come funziona</a>.</p></div>%s</header>'
              % (len(ml), ic, lab_, d, argomenti.MARK))
        body = ('<section class="ch" id="gioco" style="padding-top:2rem">' + GBAR + tracks_nav(k) +
                '<div id="listview"><h2 style="margin-top:1.6rem">Sfide</h2><div class="filters">'
                '<fieldset><legend>Giorno</legend><div class="seg"><label><input type="radio" name="g" value="oggi"><span>Le ultime (%s)</span></label><label><input type="radio" name="g" value="all"><span>Tutti i giorni</span></label></div></fieldset>' % gday +
                '<fieldset><legend>Difficoltà</legend><div class="seg"><label><input type="radio" name="d" value="all"><span>Tutte</span></label><label><input type="radio" name="d" value="F"><span>Facile</span></label><label><input type="radio" name="d" value="M"><span>Media</span></label><label><input type="radio" name="d" value="D"><span>Difficile</span></label></div></fieldset>'
                '<fieldset><legend>Stato</legend><div class="seg"><label><input type="radio" name="s" value="all"><span>Tutte</span></label><label><input type="radio" name="s" value="todo"><span>Da fare</span></label><label><input type="radio" name="s" value="ok"><span>Risolte</span></label></div></fieldset></div>'
                '<p class="pcount" id="pcount" role="status" aria-live="polite"></p><ul class="plist" id="plist"></ul></div><div class="stage" id="stage" hidden></div></section>')
        sizes[f] = page(f, k, 'Laboratorio · ' + lab_, hh, body, ml)
    hh = ('<header class="hero"><div><div class="meta"><span class="chip guide">Laboratorio</span><span class="chip">banco di prova</span></div><h1 style="margin-top:1.2rem">🤖 Prova libera</h1>'
          '<p class="sub">Incolla il testo di un documento di esempio e scrivi lo schema dei campi nel formato di Content Understanding. Il modello restituisce il JSON: confronta, correggi le descrizioni e riprova. Non incollare documenti reali o aziendali.</p></div>%s</header>' % argomenti.MARK)
    sizes['lab-prova.html'] = page('lab-prova.html', 'prova', 'Laboratorio · Prova libera', hh, '<section class="ch" style="padding-top:2rem">' + tracks_nav('prova') + '<div class="card" style="margin-top:1.2rem"><div id="sbox"></div></div></section>', [])
    print('ok', len(CH), 'sfide', {k: round(v / 1024) for k, v in sizes.items()})

def bench_text(c):
    import re, html as H
    t = ' '.join(d['html'] for d in c['docs'])
    t = re.sub(r'<span class="hid".*?</span>', '', t)
    t = re.sub(r'</(tr|p|div)>|<br>', '\n', t); t = re.sub(r'</t[dh]>', ' | ', t); t = re.sub(r'<[^>]+>', '', t)
    return re.sub(r'\n{3,}', '\n\n', H.unescape(t)).strip()

if __name__ == '__main__':
    main(sys.argv[1])
