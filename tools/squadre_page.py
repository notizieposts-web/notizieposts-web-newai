"""Pagina "Pacchetti e squadre": tre modi di usare gli esercizi (da soli, in gruppo, in azienda) e classifica di squadra senza server.
Uso: python3 squadre_page.py <repo>

Come funziona senza account: ogni persona crea nella pagina il proprio "codice risultato" (RS1:...), che contiene nome, squadra e punti
letti dai progressi salvati nel browser (Palestra: radar_ex; Laboratorio: radar_arena). Chi coordina incolla i codici e ottiene la classifica,
che resta nel suo browser (radar-team) e si esporta in CSV. Non c'è controllo antifrode: si basa sulla fiducia.
"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import argomenti, graph, store, tutor
from esercizi_gen import EX, it

root = sys.argv[1]
eds = graph.data(root)
GR = [('costi', 'Costi'), ('pipeline', 'Pipeline'), ('qualita', 'Qualità'), ('sicurezza', 'Sicurezza'), ('produzione', 'Produzione'), ('casi', 'Casi')]
GI = {g[0]: i for i, g in enumerate(GR)}
assert [e['id'] for e in EX] == list(range(1, len(EX) + 1))
LV = ''.join(str(e['l']) for e in EX)
GS = ''.join(str(GI[e['g']]) for e in EX)

CSS = '''<style id="sq-css">
.pk{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,17rem),1fr));gap:1rem;margin-top:1.6rem}
.pk .card{padding:1.3rem 1.4rem;display:flex;flex-direction:column;gap:.5rem}
.pk .card.p1{border-top:6px solid var(--teal)}.pk .card.p2{border-top:6px solid var(--violet)}.pk .card.p3{border-top:6px solid var(--sun)}
.pk h3{font-size:1.3rem;margin:.2rem 0 0}.pk .who{color:var(--muted);margin:0}
.pk ul{margin:.3rem 0;padding-left:1.2rem}.pk li{margin:.3rem 0}
.pk .cta{margin-top:auto;display:flex;flex-wrap:wrap;gap:.5rem;padding-top:.6rem}
.sbtn{display:inline-flex;align-items:center;min-height:44px;padding:.45rem 1.1rem;border-radius:999px;border:1px solid var(--line);background:var(--surface);color:var(--ink);font:700 .95rem var(--head,system-ui);cursor:pointer;text-decoration:none;box-sizing:border-box}
.sbtn.pri{background:var(--violet);color:var(--bg);border-color:var(--violet)}
.paths{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,14rem),1fr));gap:.7rem;margin-top:1rem}
.paths a{display:block;padding:.9rem 1rem;border-radius:14px;border:1px solid var(--line);background:var(--surface);color:var(--ink);text-decoration:none}
.paths a b{display:block;font:700 1rem var(--head,system-ui)}.paths a span{font-size:.9rem;color:var(--muted)}
.paths a:hover{border-color:var(--violet)}
.me{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,11rem),1fr));gap:.8rem;margin-top:1rem}
.me .card{padding:.9rem 1rem}.me .k{font:700 .75rem var(--head,system-ui);letter-spacing:.08em;text-transform:uppercase;color:var(--muted)}.me .v{font:800 1.4rem var(--head,system-ui)}.me .s{font-size:.88rem;color:var(--muted)}
.frm{display:grid;gap:.8rem;max-width:40rem;margin-top:1.2rem}
.frm label{font-weight:700;display:block;margin-bottom:.25rem}
.frm input[type=text],.frm textarea{font:inherit;width:100%;box-sizing:border-box;padding:.6rem .8rem;border-radius:10px;border:1px solid var(--line);background:var(--surface);color:var(--ink);min-height:44px}
.frm textarea{min-height:6.5rem;font:13px/1.5 ui-monospace,Menlo,monospace;word-break:break-all}
.frm .hint{font-size:.88rem;color:var(--muted);margin:.25rem 0 0}
.frm .row{display:flex;flex-wrap:wrap;gap:.5rem;align-items:center}
.msg{font-weight:700;min-height:1.4em;margin:0}
.tw{overflow-x:auto;margin-top:1rem;position:relative}
.board{border-collapse:collapse;width:100%;font-size:.95rem}
.board caption{text-align:left;font-weight:700;padding:.4rem 0}
.board th,.board td{border:1px solid var(--line);padding:.5rem .7rem;text-align:right;white-space:nowrap}
.board th:nth-child(2),.board td:nth-child(2),.board th:nth-child(3),.board td:nth-child(3){text-align:left}
.board thead th{background:var(--soft)}
.board tr.top td{font-weight:700}
.board .rm{min-width:44px;min-height:44px;border-radius:999px;border:1px solid var(--line);background:var(--surface);color:var(--ink);cursor:pointer;font-weight:700}
.steps{counter-reset:s;list-style:none;padding:0;display:grid;gap:.6rem;max-width:44rem}
.steps li{counter-increment:s;padding:.8rem 1rem .8rem 3.2rem;border:1px solid var(--line);border-radius:14px;background:var(--surface);position:relative}
.steps li::before{content:counter(s);position:absolute;left:.9rem;top:.75rem;width:1.7rem;height:1.7rem;border-radius:50%;background:var(--violet);color:var(--bg);font-weight:800;display:flex;align-items:center;justify-content:center}
</style>'''

hero = ('<header class="hero"><div><div class="meta"><span class="chip guide">Pacchetti</span><span class="chip">Da soli</span><span class="chip">In gruppo</span><span class="chip">In azienda</span></div>'
        '<h1 style="margin-top:1.2rem">Pacchetti e squadre: allenarsi da soli, in gruppo o in azienda</h1>'
        '<p class="sub">Gli stessi esercizi della Palestra e le stesse sfide del Laboratorio, organizzati in tre modi. Tutto gratuito e senza registrazione: i progressi restano nel browser di ognuno, e la classifica di squadra si costruisce con un codice che ogni persona decide di condividere.</p></div>%s</header>') % argomenti.MARK

def path(href, title, sub): return '<a href="%s"><b>%s</b><span>%s</span></a>' % (href, title, sub)

body = ('''<section class="ch" id="pacchetti" style="padding-top:2.5rem"><div class="ch-head"><div class="kicker"><span class="chip guide">Tre pacchetti</span></div><h2>Scegli come allenarti</h2>
<p class="lead">Non cambia il contenuto, cambia l'organizzazione: un percorso personale, una squadra con la sua classifica, oppure più squadre con un riepilogo per l'azienda.</p></div>
<div class="pk">
<div class="card p1"><span><span class="chip">Per una persona</span></span><h3>Utente</h3><p class="who">Per chi studia da solo, con i suoi tempi.</p><ul>
<li>''' + it(len(EX)) + ''' esercizi della Palestra e le sfide quotidiane del Laboratorio.</li><li>Percorsi per tema e tre difficoltà, con punti e gradi.</li><li>Aiuti graduali, lettura facilitata e Rada che legge ad alta voce.</li><li>Progressi salvati nel browser, con codice di backup.</li></ul>
<div class="cta"><a class="sbtn pri" href="azure-esercizi.html?l=1">Inizia dai facili</a><a class="sbtn" href="azure-laboratorio.html">Sfide di oggi</a></div></div>
<div class="card p2"><span><span class="chip">Da 2 a 30 persone</span></span><h3>Gruppo</h3><p class="who">Per una classe, un team, un gruppo di studio.</p><ul>
<li>Tutto il pacchetto Utente, per ogni persona.</li><li>Un codice squadra scelto da chi coordina.</li><li>Ogni persona crea il suo codice risultato e lo manda a chi coordina.</li><li>Classifica della squadra con punti di Palestra e Laboratorio.</li></ul>
<div class="cta"><a class="sbtn pri" href="#scheda">Crea il mio codice</a><a class="sbtn" href="#classifica">Apri la classifica</a></div></div>
<div class="card p3"><span><span class="chip">Più squadre</span></span><h3>Azienda</h3><p class="who">Per reparti diversi che seguono lo stesso programma.</p><ul>
<li>Tutto il pacchetto Gruppo, per ogni squadra.</li><li>Una sola classifica con più squadre e il totale per squadra.</li><li>Percorsi consigliati per ruolo: acquisti, sviluppo, sicurezza, qualità.</li><li>Esportazione in CSV per i propri rapporti.</li></ul>
<div class="cta"><a class="sbtn pri" href="#classifica">Classifica e CSV</a><a class="sbtn" href="#percorsi">Percorsi per ruolo</a></div></div>
</div></section>

<section class="ch" id="percorsi"><div class="ch-head"><div class="kicker"><span class="chip guide">Percorsi</span></div><h2>Da dove partire, per ruolo</h2><p class="lead">Ogni percorso apre la Palestra già filtrata. Chi coordina può assegnarne uno alla settimana.</p></div>
<div class="paths">''' +
    path('azure-esercizi.html?l=1', 'Primi passi', 'Tutti gli esercizi facili: una regola alla volta.') +
    path('azure-esercizi.html?g=costi', 'Acquisti e finanza', 'Costi: pagine, token, tariffe, conti di un lotto.') +
    path('azure-esercizi.html?g=pipeline', 'Sviluppo', 'Pipeline: metodi dei campi, smistamento, formati.') +
    path('azure-esercizi.html?g=produzione', 'Operazioni', 'Produzione: quote, versioni, monitoraggio.') +
    path('azure-esercizi.html?g=sicurezza', 'Sicurezza e conformità', 'Dove stanno i dati, ruoli, filtri.') +
    path('azure-esercizi.html?g=qualita', 'Qualità', 'Misurare gli errori e la confidenza dei campi.') +
    path('azure-esercizi.html?g=casi&l=3', 'Responsabili di progetto', 'Casi completi, difficili: scelte con vincoli.') +
    path('azure-laboratorio.html', 'Tutti: la sfida del giorno', '30 sfide nuove ogni giorno nel Laboratorio.') + '''</div></section>

<section class="ch" id="scheda"><div class="ch-head"><div class="kicker"><span class="chip guide">Per ogni persona</span></div><h2>La mia scheda e il mio codice risultato</h2>
<p class="lead">Questi numeri vengono dai progressi salvati in questo browser. Il codice risultato li riassume: lo crei tu e decidi tu a chi mandarlo.</p></div>
<div class="me"><div class="card"><div class="k">Punti Palestra</div><div class="v" id="mpp">0</div><div class="s" id="mps"></div></div>
<div class="card"><div class="k">Punti Laboratorio</div><div class="v" id="mlp">0</div><div class="s" id="mls"></div></div>
<div class="card"><div class="k">Totale</div><div class="v" id="mtot">0</div><div class="s" id="mth"></div></div></div>
<form class="frm" id="mf" novalidate>
<div><label for="mn">Il tuo nome, o un soprannome</label><input type="text" id="mn" maxlength="40" autocomplete="nickname" aria-describedby="mnh"><p class="hint" id="mnh">Compare nella classifica di chi riceve il codice. Puoi usare un soprannome.</p></div>
<div><label for="mt">Codice squadra (facoltativo)</label><input type="text" id="mt" maxlength="24" autocomplete="off" aria-describedby="mth2"><p class="hint" id="mth2">Te lo dà chi coordina la squadra, per esempio VENDITE-7K2Q.</p></div>
<div class="row"><button type="submit" class="sbtn pri">Crea il mio codice risultato</button></div>
<div><label for="mc">Il tuo codice risultato</label><textarea id="mc" readonly aria-describedby="mch"></textarea><p class="hint" id="mch">Copialo e mandalo a chi coordina, per email o in chat. Contiene solo nome, squadra, data e punti.</p></div>
<div class="row"><button type="button" class="sbtn" id="mcopy">Copia il codice</button></div><p class="msg" id="mmsg" role="status" aria-live="polite"></p></form></section>

<section class="ch" id="classifica"><div class="ch-head"><div class="kicker"><span class="chip guide">Per chi coordina</span></div><h2>La classifica della squadra</h2>
<p class="lead">Scegli un codice squadra e dallo alle persone. Quando ti mandano i loro codici risultato, incollali qui: la classifica si aggiorna e resta in questo browser.</p></div>
<div class="frm">
<div><label for="tn">Nome della squadra</label><input type="text" id="tn" maxlength="16" autocomplete="off"></div>
<div class="row"><button type="button" class="sbtn" id="tgen">Crea un codice squadra</button><span class="msg" id="tcode" role="status" aria-live="polite"></span></div>
<div><label for="bin">Incolla qui i codici risultato, uno per riga</label><textarea id="bin" aria-describedby="binh"></textarea><p class="hint" id="binh">Se una persona manda un codice nuovo, sostituisce quello vecchio.</p></div>
<div class="row"><button type="button" class="sbtn pri" id="badd">Aggiungi alla classifica</button><button type="button" class="sbtn" id="bcsv">⬇ Scarica in CSV</button><button type="button" class="sbtn" id="bclr">Svuota la classifica</button></div>
<p class="msg" id="bmsg" role="status" aria-live="polite"></p></div>
<div class="tw" id="bwrap" tabindex="0" role="region" aria-label="Classifica delle persone"></div>
<div class="tw" id="twrap" tabindex="0" role="region" aria-label="Totale per squadra"></div>
</section>

<section class="ch" id="come"><div class="ch-head"><div class="kicker"><span class="chip guide">Come funziona</span></div><h2>In quattro passi, e i limiti da sapere</h2></div>
<ol class="steps"><li>Chi coordina crea un codice squadra e lo comunica alle persone, con il percorso della settimana.</li>
<li>Ognuno si allena nella Palestra e nel Laboratorio, con i propri tempi e con gli aiuti che gli servono.</li>
<li>Quando vuole, ognuno apre questa pagina, scrive nome e codice squadra e crea il suo codice risultato.</li>
<li>Chi coordina incolla i codici nella classifica e, se serve, la scarica in CSV.</li></ol>
<div class="prose" style="margin-top:1.2rem"><ul>
<li><b>Nessun dato va a un server.</b> Punti e classifica restano nei browser. Per questo non esiste una classifica che si aggiorna da sola: serve il passaggio dei codici.</li>
<li><b>Si basa sulla fiducia.</b> Il codice non è protetto contro le modifiche: va bene per allenarsi insieme, non per esami o premi.</li>
<li><b>Gli aiuti non compaiono in classifica.</b> Usarli non toglie punti nella Palestra: la classifica non distingue chi li ha usati.</li>
<li><b>Account e classifica in tempo reale</b> non ci sono ancora: richiedono un servizio esterno di accesso e una informativa sulla privacy.</li></ul></div></section>''')

JS = r'''<script id="sq-js">(function(){
var LV=__LV__,GS=__GS__,GR=__GR__,PT={1:20,2:40,3:80};
var RANK=[[0,'Nuovo arrivo'],[200,'★ Bronzo'],[1000,'★★ Argento'],[3000,'★★★ Oro'],[8000,'★★★★ Platino'],[20000,'★★★★★ Diamante']];
var $=function(id){return document.getElementById(id)};
function esc(s){return String(s==null?'':s).replace(/[&<>"]/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]})}
function fmt(n){return (+n||0).toLocaleString('it-IT')}
__CODEC__
function mine(){var d=decD(RStore.load('radar_ex')),o={pp:0,pl:[0,0,0],pg:[0,0,0,0,0,0],lp:0,ls:0};
  Object.keys(d).forEach(function(k){k=+k;if(k<1||k>LV.length)return;var l=+LV.charAt(k-1);o.pp+=PT[l];o.pl[l-1]++;o.pg[+GS.charAt(k-1)]++});
  var a=String(RStore.load('radar_arena')||'').split('~')[0];if(a)a.split('_').forEach(function(x){var q=x.split('-');if(q.length===2){var v=+q[1]||0;o.lp+=v;if(v>0)o.ls++}});return o}
function rank(x){var r=0;for(var i=0;i<RANK.length;i++)if(x>=RANK[i][0])r=i;return RANK[r][1]}
function b64e(s){return btoa(unescape(encodeURIComponent(s))).replace(/\+/g,'-').replace(/\//g,'_').replace(/=+$/,'')}
function b64d(s){s=s.replace(/-/g,'+').replace(/_/g,'/');while(s.length%4)s+='=';return decodeURIComponent(escape(atob(s)))}
function sum(s){var h=0;for(var i=0;i<s.length;i++)h=(h*31+s.charCodeAt(i))%65521;return h.toString(36)}
function clean(s,n){return String(s||'').replace(/[\u0000-\u001f<>]/g,'').replace(/\s+/g,' ').trim().slice(0,n)}
function team(s){return clean(s,24).toUpperCase()}
var M=mine();
$('mpp').textContent=fmt(M.pp);$('mps').textContent='Facili '+M.pl[0]+' · Medie '+M.pl[1]+' · Difficili '+M.pl[2];$('mlp').textContent=fmt(M.lp);$('mls').textContent=M.ls+(M.ls===1?' sfida con punti':' sfide con punti');
$('mtot').textContent=fmt(M.pp+M.lp);$('mth').textContent='Grado in Palestra: '+rank(M.pp);
try{var me=JSON.parse(localStorage.getItem('radar-me')||'{}');$('mn').value=me.n||'';$('mt').value=me.t||''}catch(e){}
$('mf').onsubmit=function(ev){ev.preventDefault();var n=clean($('mn').value,40),t=team($('mt').value);if(!n){$('mmsg').textContent='Scrivi prima il tuo nome o un soprannome.';$('mn').focus();return}
  try{localStorage.setItem('radar-me',JSON.stringify({n:n,t:t}))}catch(e){}
  var p=b64e(JSON.stringify({n:n,t:t,d:new Date().toISOString().slice(0,10),pp:M.pp,pl:M.pl,pg:M.pg,lp:M.lp,ls:M.ls}));$('mc').value='RS1:'+p+'.'+sum(p);$('mmsg').textContent='Codice creato. Copialo e mandalo a chi coordina.'};
$('mcopy').onclick=function(){var t=$('mc');if(!t.value){$('mmsg').textContent='Crea prima il codice.';return}t.select();try{navigator.clipboard.writeText(t.value).then(function(){$('mmsg').textContent='Codice copiato.'},function(){document.execCommand('copy');$('mmsg').textContent='Codice copiato.'})}catch(e){document.execCommand('copy');$('mmsg').textContent='Codice copiato.'}};
/* ---------------- classifica (resta in questo browser) */
var B=[];try{B=JSON.parse(localStorage.getItem('radar-team')||'[]')||[]}catch(e){B=[]}
function keep(){try{localStorage.setItem('radar-team',JSON.stringify(B))}catch(e){}}
function parse(line){var m=/RS1:([A-Za-z0-9_\-]+)\.([a-z0-9]+)/.exec(line);if(!m||sum(m[1])!==m[2])return null;try{var o=JSON.parse(b64d(m[1]));if(!o||!o.n)return null;
  return {n:clean(o.n,40),t:team(o.t),d:/^\d{4}-\d{2}-\d{2}$/.test(o.d)?o.d:'',pp:Math.max(0,+o.pp||0),lp:Math.max(0,+o.lp||0),ps:(o.pl||[]).reduce(function(a,b){return a+(+b||0)},0),ls:Math.max(0,+o.ls||0)}}catch(e){return null}}
function draw(){B.sort(function(a,b){return (b.pp+b.lp)-(a.pp+a.lp)||a.n.localeCompare(b.n)});
  if(!B.length){$('bwrap').innerHTML='<p>La classifica è vuota. Incolla qui sopra i codici risultato delle persone.</p>';$('twrap').innerHTML='';return}
  $('bwrap').innerHTML='<table class="board"><caption>Persone: '+B.length+'</caption><thead><tr><th scope="col">Posto</th><th scope="col">Nome</th><th scope="col">Squadra</th><th scope="col">Palestra</th><th scope="col">Laboratorio</th><th scope="col">Totale</th><th scope="col">Esercizi</th><th scope="col">Sfide</th><th scope="col">Data</th><th scope="col">Togli</th></tr></thead><tbody>'+
    B.map(function(r,i){return '<tr'+(i<3?' class="top"':'')+'><td>'+(i+1)+'</td><th scope="row">'+esc(r.n)+'</th><td>'+esc(r.t||'—')+'</td><td>'+fmt(r.pp)+'</td><td>'+fmt(r.lp)+'</td><td>'+fmt(r.pp+r.lp)+'</td><td>'+fmt(r.ps)+'</td><td>'+fmt(r.ls)+'</td><td>'+esc(r.d.split('-').reverse().join('/'))+'</td><td><button type="button" class="rm" data-rm="'+i+'" aria-label="Togli '+esc(r.n)+' dalla classifica">✕</button></td></tr>'}).join('')+'</tbody></table>';
  var T={};B.forEach(function(r){var k=r.t||'—';T[k]=T[k]||{n:0,p:0};T[k].n++;T[k].p+=r.pp+r.lp});var ks=Object.keys(T).sort(function(a,b){return T[b].p-T[a].p});
  $('twrap').innerHTML=ks.length>1?'<table class="board"><caption>Totale per squadra</caption><thead><tr><th scope="col">Posto</th><th scope="col">Squadra</th><th scope="col">Persone</th><th scope="col">Punti totali</th><th scope="col">Media a persona</th></tr></thead><tbody>'+ks.map(function(k,i){return '<tr><td>'+(i+1)+'</td><th scope="row">'+esc(k)+'</th><td style="text-align:right">'+T[k].n+'</td><td>'+fmt(T[k].p)+'</td><td>'+fmt(Math.round(T[k].p/T[k].n))+'</td></tr>'}).join('')+'</tbody></table>':''}
$('badd').onclick=function(){var ok=0,bad=0;$('bin').value.split(/\n+/).forEach(function(l){l=l.trim();if(!l)return;var r=parse(l);if(!r){bad++;return}B=B.filter(function(x){return !(x.n.toLowerCase()===r.n.toLowerCase()&&x.t===r.t)});B.push(r);ok++});
  keep();draw();if(ok)$('bin').value='';$('bmsg').textContent=(ok?ok+(ok===1?' codice aggiunto.':' codici aggiunti.'):'')+(bad?' '+bad+(bad===1?' riga non è un codice valido':' righe non sono codici validi')+': controlla che siano state copiate per intero.':'')||'Incolla almeno un codice.'};
$('bwrap').onclick=function(ev){var b=ev.target.closest('[data-rm]');if(!b)return;var r=B[+b.dataset.rm];B.splice(+b.dataset.rm,1);keep();draw();$('bmsg').textContent=r.n+' tolto dalla classifica.';$('bin').focus()};
function clrInit(){var b=$('bclr');b.textContent='Svuota la classifica';var x=$('bclr2');if(x)x.remove();b.onclick=function(){if(!B.length){$('bmsg').textContent='La classifica è già vuota.';return}b.textContent='Sì, svuota tutto';b.insertAdjacentHTML('afterend','<button type="button" class="sbtn" id="bclr2">Annulla</button>');$('bclr2').onclick=function(){clrInit();b.focus()};b.onclick=function(){B=[];keep();draw();clrInit();b.focus();$('bmsg').textContent='Classifica svuotata.'}}}clrInit();
$('bcsv').onclick=function(){if(!B.length){$('bmsg').textContent='Non c\'è ancora nulla da scaricare.';return}function q(v){v=String(v);if(/^[=+\-@\t\r]/.test(v))v="'"+v;return '"'+v.replace(/"/g,'""')+'"'}
  var rows=[['Posto','Nome','Squadra','Punti Palestra','Punti Laboratorio','Totale','Esercizi risolti','Sfide con punti','Data']].concat(B.map(function(r,i){return [i+1,r.n,r.t,r.pp,r.lp,r.pp+r.lp,r.ps,r.ls,r.d]}));
  var blob=new Blob(['\ufeff'+rows.map(function(r){return r.map(q).join(';')}).join('\r\n')],{type:'text/csv;charset=utf-8'}),a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download='radar-ai-classifica-'+new Date().toISOString().slice(0,10)+'.csv';document.body.appendChild(a);a.click();setTimeout(function(){URL.revokeObjectURL(a.href);a.remove()},500);$('bmsg').textContent='File CSV scaricato.'};
$('tgen').onclick=function(){var n=clean($('tn').value,16).toUpperCase().replace(/[^A-Z0-9À-Ú]+/g,'-').replace(/^-+|-+$/g,'');if(!n){$('tcode').textContent='Scrivi prima il nome della squadra.';$('tn').focus();return}
  var c='',A='ABCDEFGHJKLMNPQRSTUVWXYZ23456789',r=new Uint8Array(4);(window.crypto||window.msCrypto).getRandomValues(r);for(var i=0;i<4;i++)c+=A.charAt(r[i]%A.length);$('tcode').textContent='Codice squadra: '+n+'-'+c+' · comunicalo alle persone.'};
draw();
})();</script>'''

js = (JS.replace('__CODEC__', store.EX_CODEC).replace('__LV__', json.dumps(LV)).replace('__GS__', json.dumps(GS)).replace('__GR__', json.dumps(GR, ensure_ascii=False)))
page = (argomenti.head_from(root, 'Pacchetti e squadre') + CSS + tutor.CSS + '</head>\n<body>\n' + argomenti.NAV('squadre.html', eds) + hero +
        '<main class="wrap">' + body + '</main>' + argomenti.FOOT + argomenti.JS + store.JS + tutor.JS + js + '\n</body>\n</html>\n')
open(os.path.join(root, 'squadre.html'), 'w', encoding='utf-8').write(page)
print('ok squadre', len(page))
