"""Pagina "Palestra Content Understanding": esercizi interattivi. Uso: python3 esercizi_page.py <repo>"""
import sys, os, json, html
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import argomenti, graph, store
from esercizi_gen import EX, it

root = sys.argv[1]
eds = graph.data(root)
N = len(EX)
lv = {l: sum(1 for e in EX if e['l'] == l) for l in (1, 2, 3)}
GR = [('costi', 'Costi'), ('pipeline', 'Pipeline'), ('qualita', 'Qualità'), ('sicurezza', 'Sicurezza'), ('produzione', 'Produzione'), ('casi', 'Casi')]

CSS = '''<style id="pal-css">
.pal-ctl{display:grid;gap:.9rem;margin-top:1.4rem}
.pal-row{display:flex;flex-wrap:wrap;gap:.45rem;align-items:center}
.pal-row .lab{font:700 .78rem var(--head,system-ui);letter-spacing:.08em;text-transform:uppercase;color:var(--muted);min-width:5.5rem}
.fbtn{min-height:36px;padding:.35rem .9rem;border-radius:999px;border:1px solid var(--line);background:var(--surface);color:var(--ink);font:600 .9rem var(--head,system-ui);cursor:pointer}
.fbtn[aria-pressed="true"]{background:var(--ink);color:var(--bg);border-color:var(--ink)}
.pal-search{flex:1;min-width:min(100%,16rem);font:inherit;padding:.6rem 1rem;border-radius:999px;border:1px solid var(--line);background:var(--surface);color:var(--ink)}
.pal-check{display:inline-flex;align-items:center;gap:.45rem;min-height:36px;font-weight:600}
.pal-check input{width:20px;height:20px}
.pal-stat{display:flex;flex-wrap:wrap;gap:.6rem 1.2rem;align-items:center;font-size:.95rem}
.pbar2{flex:1;min-width:10rem;height:10px;border-radius:999px;background:var(--soft);overflow:hidden;border:1px solid var(--line)}
.pbar2 i{display:block;height:100%;width:0;background:var(--violet)}
.chip.l1{background:var(--teal-soft)!important;color:var(--ink)!important;border:1px solid var(--teal)!important}
.chip.l2{background:var(--sun-soft)!important;color:var(--ink)!important;border:1px solid var(--sun)!important}
.chip.l3{background:var(--red-soft)!important;color:var(--ink)!important;border:1px solid var(--red)!important}
.chip.done{background:var(--violet)!important;color:var(--bg)!important}
.ex{margin-top:1rem;max-width:52rem;scroll-margin-top:8rem}\n#esercizi{scroll-margin-top:7rem}
.ex h3{font-size:1.15rem;margin:.55rem 0 .4rem}
.ex .qq{margin:.2rem 0 .8rem;font-size:1.02rem}
.ex .tw{overflow-x:auto;margin:.6rem 0}.ex table{border-collapse:collapse;font-size:.92rem}.ex th,.ex td{border:1px solid var(--line);padding:.35rem .7rem;text-align:right}
.ex fieldset{border:0;padding:0;margin:0;display:grid;gap:.4rem}
.ex legend{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0)}
.ex .opt2{display:flex;gap:.6rem;align-items:flex-start;padding:.55rem .8rem;border:1px solid var(--line);border-radius:12px;cursor:pointer;min-height:40px}
.ex .opt2:hover{border-color:var(--violet)}
.ex .opt2 input{margin-top:.25rem;width:18px;height:18px;flex:none}
.ex .opt2.ok{border:2px solid var(--teal);background:var(--teal-soft)}.ex .opt2.ko{border:2px solid var(--red);background:var(--red-soft)}
.ex .numrow{display:flex;flex-wrap:wrap;gap:.5rem;align-items:center}
.ex .numrow input{font:inherit;width:11rem;max-width:100%;padding:.5rem .8rem;border-radius:10px;border:1px solid var(--line);background:var(--surface);color:var(--ink)}
.ex .acts{display:flex;flex-wrap:wrap;gap:.5rem;margin-top:.8rem;align-items:center}
.ex .vbtn{min-height:40px;padding:.4rem 1.1rem;border-radius:999px;border:0;background:var(--violet);color:var(--bg);font:700 .95rem var(--head,system-ui);cursor:pointer}
.ex .fb{margin:.6rem 0 0;font-weight:700;min-height:1.4em}
.ex .fb.ok{color:var(--teal)}.ex .fb.ko{color:var(--red)}
.ex details{margin-top:.6rem}.ex details>summary{cursor:pointer;font-weight:700;color:var(--violet);min-height:32px;display:flex;align-items:center}
.ex .sol{margin-top:.4rem;padding:.8rem 1rem;border-left:4px solid var(--violet);background:var(--soft);border-radius:0 12px 12px 0}
.ex .ref{font-size:.85rem;color:var(--muted);margin-top:.5rem}
.pager{display:flex;flex-wrap:wrap;gap:.5rem;align-items:center;justify-content:center;margin:2rem 0 1rem}
.pager button{min-height:40px;min-width:40px;padding:.35rem .9rem;border-radius:999px;border:1px solid var(--line);background:var(--surface);color:var(--ink);font-weight:700;cursor:pointer}
.pager button:disabled{opacity:.45;cursor:default}
.pager .pinfo{font-weight:600}
.empty{margin-top:1.5rem;font-weight:600}
</style>'''

hero = ('<header class="hero"><div><div class="meta"><span class="chip guide">Esercizi</span><span class="chip l1">Media: %s</span><span class="chip l2">Alta: %s</span><span class="chip l3">Estrema: %s</span></div>'
        '<h1 style="margin-top:1.2rem">Palestra Content Understanding: %s esercizi</h1>'
        '<p class="sub">Calcoli di pagine, quote, token e costi, scelte di architettura, qualità, sicurezza e casi completi. Ogni esercizio si verifica qui e ha la soluzione spiegata, con la puntata della rubrica da cui nasce. I tuoi progressi restano in questo browser.</p></div>%s</header>') % (
        it(lv[1]), it(lv[2]), it(lv[3]), it(N), argomenti.MARK)

ctl = '''<section class="ch" id="esercizi" style="padding-top:2.5rem"><div class="ch-head"><div class="kicker"><span class="chip guide">Allenamento</span></div><h2>Scegli livello e tema</h2>
<p class="lead">Media: un passaggio e una regola. Alta: più regole insieme o un calcolo in più passi. Estrema: casi completi, trappole e scelte con vincoli. Le tariffe dei modelli negli esercizi sono ipotetiche e indicate nel testo: quelle reali vanno lette sul listino della tua regione.</p></div>
<div class="pal-ctl">
<div class="pal-row" role="group" aria-label="Livello"><span class="lab" aria-hidden="true">Livello</span><button type="button" class="fbtn" data-l="0" aria-pressed="true">Tutti</button><button type="button" class="fbtn" data-l="1" aria-pressed="false">Media</button><button type="button" class="fbtn" data-l="2" aria-pressed="false">Alta</button><button type="button" class="fbtn" data-l="3" aria-pressed="false">Estrema</button></div>
<div class="pal-row" role="group" aria-label="Tema"><span class="lab" aria-hidden="true">Tema</span><button type="button" class="fbtn" data-g="" aria-pressed="true">Tutti</button>''' + ''.join('<button type="button" class="fbtn" data-g="%s" aria-pressed="false">%s</button>' % g for g in GR) + '''</div>
<div class="pal-row"><label class="sr-only" for="pq">Cerca negli esercizi</label><input class="pal-search" id="pq" type="search" placeholder="Cerca: max_tokens, Excel, 429, Reader, EER…" autocomplete="off">
<label class="pal-check"><input type="checkbox" id="phide"> Nascondi i completati</label><button type="button" class="fbtn" id="prand">🎲 Esercizio a caso</button></div>
<div class="pal-stat"><span id="pcount" aria-live="polite"></span><span id="pdone"></span><div class="pbar2" aria-hidden="true"><i id="pbar"></i></div><button type="button" class="fbtn" id="preset">Azzera i progressi</button></div>''' + store.backup_html('e') + store.mysol_html('e') + '''
</div><div id="plist"></div><nav class="pager" id="ppager" aria-label="Pagine degli esercizi"></nav></section>'''

JS = r'''<script id="pal-js">(function(){
var EX=__EX__,GN={costi:'Costi',pipeline:'Pipeline',qualita:'Qualità',sicurezza:'Sicurezza',produzione:'Produzione',casi:'Casi'},LN={1:'Media',2:'Alta',3:'Estrema'};
var PER=20,st={l:0,g:'',q:'',hide:false,page:1},done={};
__CODEC__
var _sv=RStore.load('radar_ex');if(_sv){done=decD(_sv)}else{try{done=JSON.parse(localStorage.getItem('radar-cu-done')||'{}')||{}}catch(e){done={}}}
function save(){RStore.save('radar_ex',encD(done,EX.length));if($('ebk'))$('ebk').value='EX1:'+encD(done,EX.length)}
var $=function(id){return document.getElementById(id)};
function plain(s){return s.replace(/<[^>]+>/g,' ').toLowerCase()}
EX.forEach(function(e){e.txt=plain(e.t+' '+e.q+' '+e.s)});
function list(){var q=st.q.trim().toLowerCase();return EX.filter(function(e){return(!st.l||e.l==st.l)&&(!st.g||e.g===st.g)&&(!q||e.txt.indexOf(q)>=0)&&(!st.hide||!done[e.id])})}
function num(v){v=String(v).replace(/[\s$%€]/g,'').replace(/[a-zà-ú\/\.]+$/i,'');if(!v)return NaN;
  if(v.indexOf(',')>=0){v=v.replace(/\./g,'').replace(',','.')}else if(/^-?[1-9]\d{0,2}(\.\d{3})+$/.test(v)){v=v.replace(/\./g,'')}return parseFloat(v)}
var SV=RSol.all('ex');
function card(e){
  var h='<article class="card ex" id="ex'+e.id+'" aria-labelledby="ext'+e.id+'"><div class="kicker"><span class="chip">N. '+e.id+'</span><span class="chip l'+e.l+'">'+LN[e.l]+'</span><span class="chip topic">'+GN[e.g]+'</span>'+(done[e.id]?'<span class="chip done">✓ Fatto</span>':'')+'</div>';
  h+='<h3 id="ext'+e.id+'">'+e.t+'</h3><div class="qq">'+e.q+'</div>';
  if(e.k==='mcq'){h+='<fieldset><legend>Scegli una risposta</legend>'+e.o.map(function(o,i){return '<label class="opt2"><input type="radio" name="r'+e.id+'" value="'+i+'"'+(SV[e.id]&&SV[e.id].v===i?' checked':'')+'><span>'+o+'</span></label>'}).join('')+'</fieldset>'}
  else{h+='<div class="numrow"><label for="n'+e.id+'">La tua risposta'+(e.u?' ('+e.u+')':'')+'</label><input id="n'+e.id+'" inputmode="decimal" autocomplete="off" value="'+(SV[e.id]&&SV[e.id].v!=null?String(SV[e.id].v).replace(/"/g,'&quot;'):'')+'"></div>'}
  h+='<div class="acts"><button type="button" class="vbtn" data-v="'+e.id+'">Verifica</button></div><p class="fb" id="fb'+e.id+'" role="status"></p>';
  h+='<details><summary>Mostra la soluzione</summary><div class="sol">'+(e.k==='num'?'<p><b>Risposta: '+e.fa+'</b></p>':'')+'<p>'+e.s+'</p></div></details><p class="ref">Riferimento: '+e.p+' · <a href="azure.html">guida Content Understanding</a></p></article>';
  return h}
function render(keep){
  var L=list(),pages=Math.max(1,Math.ceil(L.length/PER));if(st.page>pages)st.page=pages;
  var cur=L.slice((st.page-1)*PER,st.page*PER);
  $('plist').innerHTML=cur.length?cur.map(card).join(''):'<p class="empty">Nessun esercizio con questi filtri.</p>';
  $('pcount').textContent=L.length+(L.length===1?' esercizio':' esercizi')+' · pagina '+st.page+' di '+pages;
  var pg=$('ppager');pg.innerHTML='<button type="button" data-p="'+(st.page-1)+'"'+(st.page<=1?' disabled':'')+'>← Precedenti</button><span class="pinfo">'+st.page+' / '+pages+'</span><button type="button" data-p="'+(st.page+1)+'"'+(st.page>=pages?' disabled':'')+'>Successivi →</button>';
  var n=Object.keys(done).length;$('pdone').textContent='Completati: '+n+' su '+EX.length;$('pbar').style.width=(n/EX.length*100)+'%';
}
function check(id){
  var e=EX.filter(function(x){return x.id==id})[0],fb=$('fb'+id),ok;
  if(e.k==='mcq'){var sel=document.querySelector('input[name="r'+id+'"]:checked');if(!sel){fb.className='fb ko';fb.textContent='Scegli prima una risposta.';return}RSol.set('ex',id,{v:+sel.value});SV=RSol.all('ex');
    ok=+sel.value===e.c;document.querySelectorAll('input[name="r'+id+'"]').forEach(function(r){var l=r.parentNode;l.classList.remove('ok','ko');if(+r.value===e.c&&ok)l.classList.add('ok');if(r===sel&&!ok)l.classList.add('ko')});}
  else{var v=num($('n'+id).value);if(isNaN(v)){fb.className='fb ko';fb.textContent='Scrivi un numero, per esempio 1.250 o 3,5.';return}ok=Math.abs(v-e.a)<=e.tol;RSol.set('ex',id,{v:$('n'+id).value});SV=RSol.all('ex');}
  fb.className='fb '+(ok?'ok':'ko');fb.textContent=ok?'✓ Corretto. Esercizio segnato come fatto.':'✗ Non ancora: riprova o apri la soluzione.';
  if(ok&&!done[id]){done[id]=1;save();var k=document.querySelector('#ex'+id+' .kicker');if(k&&!k.querySelector('.done'))k.insertAdjacentHTML('beforeend','<span class="chip done">✓ Fatto</span>');var n=Object.keys(done).length;$('pdone').textContent='Completati: '+n+' su '+EX.length;$('pbar').style.width=(n/EX.length*100)+'%';}
}
document.addEventListener('click',function(ev){var b=ev.target.closest('[data-v]');if(b)check(b.getAttribute('data-v'));
  var p=ev.target.closest('#ppager [data-p]');if(p&&!p.disabled){st.page=+p.getAttribute('data-p');render();$('esercizi').scrollIntoView();}});
document.addEventListener('keydown',function(ev){if(ev.key==='Enter'&&ev.target.matches('.numrow input')){ev.preventDefault();check(ev.target.id.slice(1))}});
document.querySelectorAll('[data-l]').forEach(function(b){b.onclick=function(){st.l=+b.dataset.l;st.page=1;document.querySelectorAll('[data-l]').forEach(function(x){x.setAttribute('aria-pressed',x===b?'true':'false')});render()}});
document.querySelectorAll('[data-g]').forEach(function(b){b.onclick=function(){st.g=b.dataset.g;st.page=1;document.querySelectorAll('[data-g]').forEach(function(x){x.setAttribute('aria-pressed',x===b?'true':'false')});render()}});
var tq;$('pq').addEventListener('input',function(){clearTimeout(tq);tq=setTimeout(function(){st.q=$('pq').value;st.page=1;render()},200)});
$('phide').onchange=function(){st.hide=this.checked;st.page=1;render()};
$('prand').onclick=function(){var L=list();if(!L.length)return;var e=L[Math.floor(Math.random()*L.length)],i=L.indexOf(e);st.page=Math.floor(i/PER)+1;render();var el=$('ex'+e.id);if(el){el.scrollIntoView({block:'start'});var f=el.querySelector('input');if(f)f.focus({preventScroll:true})}};
function resInit(){var b=$('preset');b.textContent='Azzera i progressi';delete b.dataset.ask;var x=$('pres2');if(x)x.remove();b.onclick=function(){b.dataset.ask='1';b.textContent='Sì, azzera tutto';b.insertAdjacentHTML('afterend','<button type="button" class="fbtn" id="pres2">Annulla</button>');$('pres2').onclick=function(){resInit();b.focus()};b.onclick=function(){done={};save();resInit();render();b.focus();}}}resInit();
function esolList(){var n=Object.keys(RSol.all('ex')).length;$('esolcount').textContent=n?('Risposte salvate: '+n+' esercizi.'):'Non hai ancora risposte salvate.'}esolList();
$('esolexp').onclick=function(){RSol.exportFile();$('esolmsg').textContent='File scaricato.'};
$('esolimp').onchange=function(){var f=this.files&&this.files[0];if(!f)return;RSol.importFile(f,function(err,d){if(err){$('esolmsg').textContent='⚠ '+err.message;return}var v=RStore.load('radar_ex');if(v)done=decD(v);SV=RSol.all('ex');render();esolList();$('esolmsg').textContent='Ripristinato il salvataggio del '+new Date(d.data).toLocaleDateString('it-IT')+'.'})};
$('ebk').value='EX1:'+encD(done,EX.length);
$('ebc').onclick=function(){var t=$('ebk');t.select();try{navigator.clipboard.writeText(t.value).then(function(){$('ebm').textContent='Codice copiato.'},function(){document.execCommand('copy');$('ebm').textContent='Codice copiato.'})}catch(e){document.execCommand('copy');$('ebm').textContent='Codice copiato.'}};
$('ebr').onclick=function(){var v=$('ebi').value.trim();if(v.indexOf('EX1:')!==0){$('ebm').textContent='⚠ Questo non sembra un codice della Palestra (deve iniziare con EX1:).';return}done=decD(v.slice(4));save();render();$('ebi').value='';$('ebm').textContent='Progressi ripristinati: '+Object.keys(done).length+' esercizi completati.'};
if(location.hash&&/^#ex\d+$/.test(location.hash)){var id=+location.hash.slice(3),i=EX.findIndex(function(x){return x.id===id});if(i>=0)st.page=Math.floor(i/PER)+1}
render();
})();</script>'''

ex_js = json.dumps(EX, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
page = argomenti.head_from(root, 'Palestra Content Understanding') + CSS + store.BACKUP_CSS + store.SOL_CSS + '</head>\n<body>\n' + argomenti.NAV('azure-esercizi.html', eds) + hero + '<main class="wrap">' + ctl + '</main>' + argomenti.FOOT + argomenti.JS + store.JS + store.SOL_JS + JS.replace('__CODEC__', store.EX_CODEC).replace('__EX__', ex_js) + '\n</body>\n</html>\n'
open(os.path.join(root, 'azure-esercizi.html'), 'w', encoding='utf-8').write(page)
print('ok', N, len(page))
