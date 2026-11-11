"""Pagina "Palestra Content Understanding": esercizi interattivi. Uso: python3 esercizi_page.py <repo>

Struttura (dall'11 novembre 2026), sul modello di HackerRank e del Laboratorio:
- elenco degli esercizi con difficoltà (Facile 20 punti, Media 40, Difficile 80), stato e filtri; percorsi per tema con avanzamento;
- un esercizio alla volta (#exN), con verifica e quattro aiuti che NON tolgono punti: indizio, metodo, soluzione passo passo, esempio svolto;
- "Spiegamelo facile": schema Dati -> Devo trovare -> Come rispondo, parole difficili spiegate, calcolatrice;
- Rada (tools/tutor.py) legge ad alta voce consegna e aiuti, con il testo sempre scritto, e offre la lettura facilitata.
Gli aiuti si costruiscono da soli da consegna e soluzione di ogni esercizio (tools/esercizi_gen.py): non serve scriverli a mano.
"""
import sys, os, json, html, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import argomenti, graph, store, tutor
from esercizi_gen import EX, it

root = sys.argv[1]
eds = graph.data(root)
N = len(EX)
lv = {l: sum(1 for e in EX if e['l'] == l) for l in (1, 2, 3)}
PTS = {1: 20, 2: 40, 3: 80}
TOT = sum(PTS[e['l']] for e in EX)
GR = [('costi', 'Costi'), ('pipeline', 'Pipeline'), ('qualita', 'Qualità'), ('sicurezza', 'Sicurezza'), ('produzione', 'Produzione'), ('casi', 'Casi')]

# titoli delle puntate della rubrica (da tools/guida.py), per l'indizio "dove è spiegata la regola"
_gs = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'guida.py'), encoding='utf-8').read()
EPT = {int(n): t.replace("\\'", "'") for n, t in re.findall(r"^\s*\((\d+),\s*'\d+',\s*'\w+',\s*'\w+',\s*'((?:[^'\\]|\\.)*)'\)", _gs, re.M)}

# parole difficili: [etichetta, espressione regolare, spiegazione]. Maiuscole/minuscole contano solo se l'etichetta ha maiuscole o cifre.
_G = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'glossario.json'), encoding='utf-8'))
def _gl(k): return _G[k]['spiega']
WORDS = [
    ['TPM', 'TPM', 'Token al minuto: quanti token la distribuzione del modello può elaborare in un minuto. È un tetto: oltre, le richieste vengono respinte.'],
    ['max_tokens', 'max_tokens', 'Il numero massimo di token che il modello può scrivere in una risposta. Nei calcoli di quota si somma ai token del prompt.'],
    ['token', 'token', _gl('token')],
    ['prompt', 'prompt', 'Il testo che si manda al modello: le istruzioni più il contenuto da leggere.'],
    ['OCR', 'OCR', 'Riconoscimento ottico dei caratteri: trasforma l\'immagine di una pagina in testo che il computer può leggere.'],
    ['WER', 'WER', 'La percentuale di parole sbagliate: parole sbagliate diviso parole totali, per 100. Più è bassa, meglio è.'],
    ['EER', 'EER', 'Il tasso di errore sui valori estratti: valori sbagliati diviso valori totali, per 100. Più è basso, meglio è.'],
    ['429', '429', 'Il codice con cui un servizio risponde «troppe richieste»: bisogna aspettare un po\' e riprovare.'],
    ['PTU', 'PTU', 'Capacità riservata: potenza del modello comprata in anticipo, invece di pagare a consumo.'],
    ['BYOC', 'BYOC', 'Capacità portata da te: Content Understanding usa una distribuzione del modello che sta in un\'altra tua risorsa.'],
    ['RAG', 'RAG', _gl('rag')],
    ['API', 'API', _gl('api')],
    ['embedding', 'embedding', _gl('embedding')],
    ['latenza', 'latenz[ae]', _gl('latenza')],
    ['lotto', 'lott[oi]', 'Un gruppo di documenti elaborati tutti insieme, spesso di notte.'],
    ['quota', 'quot[ae]', 'Il limite di lavoro che il servizio concede in un certo tempo, per esempio richieste o token al minuto.'],
    ['analizzatore', 'analizzator[ei]', 'La configurazione di Content Understanding che dice quali campi leggere da un tipo di documento.'],
    ['contestualizzazione', 'contestualizzazione', 'Una delle voci di costo di Content Understanding, contata per pagina. Negli esercizi la tariffa è scritta nel testo.'],
    ['campo generativo', 'generativ[oi]|generate', 'Un campo il cui valore non è scritto nel documento: lo produce il modello, e per questo consuma token.'],
    ['extract', 'extract', 'Il metodo per i campi il cui valore è scritto nel documento così com\'è.'],
    ['classify', 'classify', 'Il metodo per i campi il cui valore va scelto da un elenco fisso.'],
    ['thread', 'thread', 'Uno dei lavori che un programma porta avanti in parallelo, nello stesso momento.'],
    ['per eccesso', 'per eccesso', 'Arrotondare sempre verso l\'alto: 5,1 diventa 6, e anche 5,9 diventa 6.'],
    ['percentuale', 'percentuale', 'Una parte su cento. Per trovarla: dividi la parte per il totale e moltiplica per 100.'],
    ['milione di token', 'milion[ei] di token', 'Le tariffe dei modelli sono per milione di token: dividi i tuoi token per 1.000.000 e moltiplica per la tariffa.'],
]

CSS = '''<style id="pal-css">
.pal-ctl{display:grid;gap:.9rem;margin-top:1.4rem}
.pal-row{display:flex;flex-wrap:wrap;gap:.45rem;align-items:center}
.pal-row .lab{font:700 .78rem var(--head,system-ui);letter-spacing:.08em;text-transform:uppercase;color:var(--muted);min-width:5.5rem}
.fbtn{min-height:40px;padding:.35rem .9rem;border-radius:999px;border:1px solid var(--line);background:var(--surface);color:var(--ink);font:600 .9rem var(--head,system-ui);cursor:pointer}
.fbtn[aria-pressed="true"]{background:var(--ink);color:var(--bg);border-color:var(--ink)}
.pbtn{min-height:40px;padding:.4rem .9rem;border-radius:999px;border:1px solid var(--line);background:var(--surface);color:var(--ink);font-weight:700;cursor:pointer;font-size:.95rem}
.pal-search{flex:1;min-width:min(100%,16rem);font:inherit;padding:.6rem 1rem;border-radius:999px;border:1px solid var(--line);background:var(--surface);color:var(--ink);min-height:44px;box-sizing:border-box}
.chip.l1{background:var(--teal-soft)!important;color:var(--ink)!important;border:1px solid var(--teal)!important}
.chip.l2{background:var(--sun-soft)!important;color:var(--ink)!important;border:1px solid var(--sun)!important}
.chip.l3{background:var(--red-soft)!important;color:var(--ink)!important;border:1px solid var(--red)!important}
.chip.done{background:var(--violet)!important;color:var(--bg)!important}
#esercizi{scroll-margin-top:7rem}
.hud{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,13rem),1fr));gap:.8rem;margin-top:1.4rem}
.hud .card{padding:1rem 1.1rem}
.hud .k{font:700 .75rem var(--head,system-ui);letter-spacing:.08em;text-transform:uppercase;color:var(--muted)}
.hud .v{font:800 1.5rem var(--head,system-ui);margin:.15rem 0}
.hud .s{font-size:.88rem;color:var(--muted)}
.xbar{height:10px;border-radius:999px;background:var(--soft);overflow:hidden;border:1px solid var(--line);margin:.4rem 0}
.xbar i{display:block;height:100%;width:0;background:var(--violet)}
.trk{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,10.5rem),1fr));gap:.6rem;margin-top:.9rem}
.trk button{text-align:left;padding:.75rem .9rem;border-radius:14px;border:1px solid var(--line);background:var(--surface);color:var(--ink);cursor:pointer;font:inherit;min-height:44px}
.trk button b{display:block;font:700 1rem var(--head,system-ui)}
.trk button .n{font-size:.86rem;color:var(--muted)}
.trk button[aria-pressed="true"]{border:2px solid var(--violet);background:var(--violet-soft)}
.trk button[aria-pressed="true"] .n{color:var(--ink)}
.xlist{list-style:none;padding:0;margin:1rem 0 0;display:grid;gap:.5rem}
.xlist li{display:flex;flex-wrap:wrap;gap:.5rem .7rem;align-items:center;padding:.8rem 1rem;border:1px solid var(--line);border-radius:14px;background:var(--surface)}
.xlist .pt{flex:1 1 16rem;min-width:0}
.xlist .pt a{font:700 1.02rem var(--head,system-ui);text-decoration:none;color:var(--ink);display:inline-block;min-height:24px;padding:.15rem 0}
.xlist .pt a:hover{text-decoration:underline}
.xlist .sub2{display:block;font-size:.88rem;color:var(--muted);overflow-wrap:anywhere}
.xlist .st{font-weight:700;font-size:.9rem;min-width:5.5rem;text-align:right}.xlist .st.ok{color:var(--teal)}
.pcount{font-weight:600;margin:.9rem 0 0}
.pager{display:flex;flex-wrap:wrap;gap:.5rem;align-items:center;justify-content:center;margin:1.5rem 0 1rem}
.pager button{min-height:44px;min-width:44px;padding:.35rem .9rem;border-radius:999px;border:1px solid var(--line);background:var(--surface);color:var(--ink);font-weight:700;cursor:pointer}
.pager button:disabled{opacity:.45;cursor:default}.pager .pinfo{font-weight:600}
.stage{margin-top:1.4rem;max-width:56rem}
.back{min-height:44px;padding:.4rem 1rem;border-radius:999px;border:1px solid var(--line);background:var(--surface);color:var(--ink);font-weight:700;cursor:pointer}
.stage h2{font-size:clamp(1.4rem,4vw,1.9rem);margin:.6rem 0 .5rem}
.stage .qq{font-size:1.1rem;line-height:1.8;margin:.2rem 0 1rem}
.stage .tw{overflow-x:auto;margin:.6rem 0}.stage table{border-collapse:collapse;font-size:.95rem}.stage th,.stage td{border:1px solid var(--line);padding:.35rem .7rem;text-align:right}
.ans{margin-top:1rem;padding:1.1rem 1.2rem}
.ans fieldset{border:0;padding:0;margin:0;display:grid;gap:.5rem}
.ans legend{font-weight:700;margin-bottom:.5rem;padding:0}
.opt2{display:flex;gap:.7rem;align-items:flex-start;padding:.7rem .9rem;border:1px solid var(--line);border-radius:12px;cursor:pointer;min-height:44px;box-sizing:border-box}
.opt2:hover{border-color:var(--violet)}
.opt2 input{margin-top:.3rem;width:20px;height:20px;flex:none}
.opt2.ok{border:2px solid var(--teal);background:var(--teal-soft)}.opt2.ko{border:2px solid var(--red);background:var(--red-soft)}
.opt2.out{opacity:.75;text-decoration:line-through}
.numrow{display:flex;flex-wrap:wrap;gap:.5rem .8rem;align-items:center}
.numrow label{font-weight:700}
.numrow input,.calc input{font:inherit;width:12rem;max-width:100%;padding:.55rem .8rem;border-radius:10px;border:1px solid var(--line);background:var(--surface);color:var(--ink);min-height:44px;box-sizing:border-box}
.acts{display:flex;flex-wrap:wrap;gap:.5rem;margin-top:.9rem;align-items:center}
.vbtn{min-height:44px;padding:.45rem 1.3rem;border-radius:999px;border:0;background:var(--violet);color:var(--bg);font:700 1rem var(--head,system-ui);cursor:pointer}
.fb{margin:.7rem 0 0;font-weight:700;min-height:1.4em}
.fb.ok{color:var(--teal)}.fb.ko{color:var(--red)}
.help{margin-top:1.4rem;padding:1.1rem 1.2rem;border:2px dashed var(--line);border-radius:16px}
.help h3{margin:0 0 .2rem;font-size:1.1rem}
.help .nop{margin:0 0 .7rem;color:var(--muted);font-size:.95rem}
.hbtns{display:flex;flex-wrap:wrap;gap:.45rem}
.hbtn{min-height:44px;padding:.4rem .95rem;border-radius:12px;border:1px solid var(--line);background:var(--surface);color:var(--ink);font:700 .93rem var(--head,system-ui);cursor:pointer}
.hbtn[aria-expanded="true"]{background:var(--violet-soft);border-color:var(--violet)}
.hpan{margin-top:.8rem;padding:.9rem 1rem;border-left:4px solid var(--violet);background:var(--soft);border-radius:0 12px 12px 0}
.hpan[hidden]{display:none}
.hpan h4{margin:0 0 .4rem;font-size:1.02rem}
.hpan p{margin:.3rem 0}.hpan ol,.hpan ul{margin:.3rem 0;padding-left:1.3rem}.hpan li{margin:.3rem 0}
.hpan .rt-say{margin-top:.6rem}
.schema{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,13rem),1fr));gap:.6rem;margin:.5rem 0}
.schema .sb{padding:.7rem .8rem;border-radius:12px;background:var(--surface);border:1px solid var(--line)}
.schema .sb h5{margin:0 0 .3rem;font:700 .95rem var(--head,system-ui)}
.schema .sb.s1{border-top:5px solid var(--teal)}.schema .sb.s2{border-top:5px solid var(--violet)}.schema .sb.s3{border-top:5px solid var(--sun)}
.words dt{font-weight:700;margin-top:.4rem}.words dd{margin:0 0 .2rem}
.calc{display:flex;flex-wrap:wrap;gap:.5rem .8rem;align-items:center}
.calc input{width:18rem}
.calc output,.calcout{font-weight:700}
.exq{padding:.6rem .8rem;border-radius:10px;background:var(--surface);border:1px solid var(--line)}
.snav{display:flex;flex-wrap:wrap;gap:.5rem;justify-content:space-between;margin-top:1.4rem}
.ref{font-size:.9rem;color:var(--muted);margin-top:.9rem}
.empty{margin-top:1.5rem;font-weight:600}
</style>'''

hero = ('<header class="hero"><div><div class="meta"><span class="chip guide">Esercizi</span><span class="chip l1">Facile: %s</span><span class="chip l2">Media: %s</span><span class="chip l3">Difficile: %s</span></div>'
        '<h1 style="margin-top:1.2rem">Palestra Content Understanding: %s esercizi</h1>'
        '<p class="sub">Calcoli di pagine, quote, token e costi, scelte di architettura, qualità, sicurezza e casi completi. Un esercizio alla volta, senza limiti di tempo, con aiuti che non tolgono punti: un indizio, il metodo, la soluzione passo passo e un esempio già svolto. Rada, la guida, te li legge ad alta voce. I tuoi progressi restano in questo browser.</p></div>%s</header>') % (
        it(lv[1]), it(lv[2]), it(lv[3]), it(N), argomenti.MARK)

ctl = '''<section class="ch" id="esercizi" style="padding-top:2.5rem"><div class="ch-head"><div class="kicker"><span class="chip guide">Allenamento</span></div><h2>Scegli un percorso e una difficoltà</h2>
<p class="lead">Facile (20 punti): un passaggio e una regola. Media (40 punti): più regole insieme o un calcolo in più passi. Difficile (80 punti): casi completi, trappole e scelte con vincoli. Le tariffe dei modelli negli esercizi sono ipotetiche e indicate nel testo: quelle reali vanno lette sul listino della tua regione.</p></div>
<div id="listview">
<div class="hud"><div class="card"><div class="k">Grado</div><div class="v" id="hgr">Nuovo arrivo</div><div class="xbar" aria-hidden="true"><i id="hbar"></i></div><div class="s" id="hnext"></div></div>
<div class="card"><div class="k">Punti</div><div class="v" id="hpt">0</div><div class="s">su ''' + it(TOT) + ''' · gli aiuti non tolgono punti</div></div>
<div class="card"><div class="k">Esercizi risolti</div><div class="v" id="hdn">0</div><div class="s" id="hdn2"></div></div></div>
<h3 style="margin:1.6rem 0 0" id="trkh">Percorsi per tema</h3>
<div class="trk" id="trk" role="group" aria-labelledby="trkh"></div>
<div class="pal-ctl">
<div class="pal-row" role="group" aria-label="Difficoltà"><span class="lab" aria-hidden="true">Difficoltà</span><button type="button" class="fbtn" data-l="0" aria-pressed="true">Tutte</button><button type="button" class="fbtn" data-l="1" aria-pressed="false">Facile</button><button type="button" class="fbtn" data-l="2" aria-pressed="false">Media</button><button type="button" class="fbtn" data-l="3" aria-pressed="false">Difficile</button></div>
<div class="pal-row" role="group" aria-label="Stato"><span class="lab" aria-hidden="true">Stato</span><button type="button" class="fbtn" data-s="all" aria-pressed="true">Tutti</button><button type="button" class="fbtn" data-s="todo" aria-pressed="false">Da fare</button><button type="button" class="fbtn" data-s="ok" aria-pressed="false">Risolti</button></div>
<div class="pal-row"><label class="sr-only" for="pq">Cerca negli esercizi</label><input class="pal-search" id="pq" type="search" placeholder="Cerca: max_tokens, Excel, 429, EER…" autocomplete="off">
<button type="button" class="fbtn" id="prand">🎲 Esercizio a caso</button><button type="button" class="fbtn" id="pnext">▶ Il prossimo da fare</button></div>
</div>
<p class="pcount" id="pcount" role="status" aria-live="polite"></p>
<ul class="xlist" id="plist"></ul><nav class="pager" id="ppager" aria-label="Pagine degli esercizi"></nav>
<div class="pal-row" style="margin-top:1rem"><button type="button" class="fbtn" id="preset">Azzera i progressi</button></div>''' + store.backup_html('e') + store.mysol_html('e') + '''
</div><div class="stage" id="stage" hidden></div></section>'''

JS = r'''<script id="pal-js">(function(){
var EX=__EX__,EPT=__EPT__,WORDS=__WORDS__,GR=__GR__,GN={},LN={1:'Facile',2:'Media',3:'Difficile'},PT={1:20,2:40,3:80};
GR.forEach(function(g){GN[g[0]]=g[1]});
var UN={'$':'dollari','%':'percentuale','min':'minuti','s':'secondi','rich./min':'richieste al minuto','rich./s':'richieste al secondo','pagine/min':'pagine al minuto'};
var RANK=[[0,'Nuovo arrivo'],[200,'★ Bronzo'],[1000,'★★ Argento'],[3000,'★★★ Oro'],[8000,'★★★★ Platino'],[20000,'★★★★★ Diamante']];
var PER=25,st={l:0,g:'',q:'',s:'all',page:1},done={},cur=null,tries={};
__CODEC__
var _sv=RStore.load('radar_ex');if(_sv){done=decD(_sv)}else{try{done=JSON.parse(localStorage.getItem('radar-cu-done')||'{}')||{}}catch(e){done={}}}
function save(){RStore.save('radar_ex',encD(done,EX.length));if($('ebk'))$('ebk').value='EX1:'+encD(done,EX.length)}
var $=function(id){return document.getElementById(id)};
var T=window.RTutor;
function esc(s){return String(s==null?'':s).replace(/[&<>"]/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]})}
function plain(s){return T.text(String(s))}
function fmt(n,d){return n.toLocaleString('it-IT',{maximumFractionDigits:d==null?4:d})}
var BY={};EX.forEach(function(e){e.txt=plain(e.t+' '+e.q+' '+e.s).toLowerCase();BY[e.id]=e});
function list(){var q=st.q.trim().toLowerCase();return EX.filter(function(e){return(!st.l||e.l==st.l)&&(!st.g||e.g===st.g)&&(!q||e.txt.indexOf(q)>=0)&&(st.s==='all'||(st.s==='ok'?!!done[e.id]:!done[e.id]))})}
function num(v){v=String(v).replace(/[\s$%€]/g,'').replace(/[a-zà-ú\/\.]+$/i,'');if(!v)return NaN;
  if(v.indexOf(',')>=0){v=v.replace(/\./g,'').replace(',','.')}else if(/^-?[1-9]\d{0,2}(\.\d{3})+$/.test(v)){v=v.replace(/\./g,'')}return parseFloat(v)}
var SV=RSol.all('ex');
function points(){return Object.keys(done).reduce(function(a,k){var e=BY[k];return a+(e?PT[e.l]:0)},0)}
/* ---------------- cruscotto ed elenco */
function hud(){var X=points(),r=0;for(var i=0;i<RANK.length;i++)if(X>=RANK[i][0])r=i;var nx=RANK[r+1],n=Object.keys(done).filter(function(k){return BY[k]}).length;
  $('hgr').textContent=RANK[r][1];$('hpt').textContent=fmt(X,0);$('hnext').textContent=nx?('ancora '+fmt(nx[0]-X,0)+' punti per '+nx[1]):'grado massimo';$('hbar').style.width=(nx?((X-RANK[r][0])/(nx[0]-RANK[r][0])*100):100)+'%';
  $('hdn').textContent=fmt(n,0)+' su '+fmt(EX.length,0);var by={1:0,2:0,3:0};Object.keys(done).forEach(function(k){if(BY[k])by[BY[k].l]++});$('hdn2').textContent='Facili '+by[1]+' · Medie '+by[2]+' · Difficili '+by[3];
  $('trk').innerHTML='<button type="button" data-g="" aria-pressed="'+(st.g===''?'true':'false')+'"><b>Tutti i temi</b><span class="n">'+fmt(n,0)+' su '+fmt(EX.length,0)+' risolti</span></button>'+GR.map(function(g){var all=EX.filter(function(e){return e.g===g[0]}),ok=all.filter(function(e){return done[e.id]}).length;
    return '<button type="button" data-g="'+g[0]+'" aria-pressed="'+(st.g===g[0]?'true':'false')+'"><b>'+g[1]+'</b><span class="n">'+ok+' su '+all.length+' risolti</span><span class="xbar" aria-hidden="true"><i style="width:'+(ok/all.length*100)+'%"></i></span></button>'}).join('')}
function snip(e){var t=plain(e.q);return t.length>110?t.slice(0,108).replace(/\s+\S*$/,'')+'…':t}
function render(){
  var L=list(),pages=Math.max(1,Math.ceil(L.length/PER));if(st.page>pages)st.page=pages;var c=L.slice((st.page-1)*PER,st.page*PER);
  $('plist').innerHTML=c.length?c.map(function(e){return '<li><span class="pt"><a href="#ex'+e.id+'" id="lx'+e.id+'">N. '+e.id+' · '+e.t+'</a><span class="sub2">'+GN[e.g]+' · '+esc(snip(e))+'</span></span><span class="chip l'+e.l+'">'+LN[e.l]+'</span><span class="chip">'+PT[e.l]+' punti</span><span class="st'+(done[e.id]?' ok':'')+'">'+(done[e.id]?'✓ Risolto':'Da fare')+'</span></li>'}).join(''):'<li>Nessun esercizio con questi filtri.</li>';
  $('pcount').textContent=fmt(L.length,0)+(L.length===1?' esercizio':' esercizi')+' · pagina '+st.page+' di '+pages;
  $('ppager').innerHTML='<button type="button" data-p="'+(st.page-1)+'"'+(st.page<=1?' disabled':'')+'>← Precedenti</button><span class="pinfo">'+st.page+' / '+pages+'</span><button type="button" data-p="'+(st.page+1)+'"'+(st.page>=pages?' disabled':'')+'>Successivi →</button>';
  hud()}
/* ---------------- aiuti costruiti da consegna e soluzione */
function steps(html){return T.sents(String(html)).filter(function(s){return plain(s).length>1})}
function unit(e){return e.u?(UN[e.u]||e.u):''}
function qparts(e){var ss=T.sents(plain(e.q)),know=[],ask=[];ss.forEach(function(s){(/\?\s*$/.test(s)||/^(Quant|Qual|Calcola|Stima|Scegli|Indica|Cosa|Che cosa|Dove|Come|Perché)/.test(s)?ask:know).push(s)});if(!ask.length&&know.length)ask.push(know.pop());return {know:know,ask:ask}}
function how(e){return e.k==='mcq'?'Scegli una sola risposta tra le '+e.o.length+'. Puoi riprovare tutte le volte che vuoi.':'Scrivi un numero'+(e.u?' in '+unit(e):'')+'. Per i decimali usa la virgola. Un piccolo arrotondamento va bene.'}
function words(e){var t=plain(e.q+' '+(e.o||[]).join(' ')),out=[];WORDS.forEach(function(w){var cs=/[A-Z0-9_]/.test(w[0]);if(new RegExp('(^|[^A-Za-zÀ-ú0-9_])('+w[1]+')(?![A-Za-zÀ-ú0-9_])',cs?'':'i').test(t))out.push(w)});return out.slice(0,7)}
function ep(e){var m=/P(\d+)/.exec(e.p||'');return m&&EPT[+m[1]]?[+m[1],EPT[+m[1]]]:null}
function mask(e){var s=String(e.s).replace(/<b>.*?<\/b>/g,'▢');return steps(plain(s)).map(function(x){var i=x.lastIndexOf('=');if(i>=0)x=x.slice(0,i)+'= ?';return x})}
function sibling(e){var c=EX.filter(function(x){return x.t===e.t&&x.id!==e.id&&x.k===e.k&&plain(x.q)!==plain(e.q)});if(!c.length)return null;c.sort(function(a,b){return (Math.abs(a.l-e.l)-Math.abs(b.l-e.l))||(Math.abs(a.id-e.id)-Math.abs(b.id-e.id))});return c[0]}
function sayBtn(){return '<button type="button" class="rt-say" data-say="1">'+T.avatar(28)+'<span>Ascolta da Rada</span></button>'}
var HELP={
 facile:function(e){var q=qparts(e),w=words(e);return '<h4>🧩 Spiegamelo facile</h4><div class="schema">'+
   '<div class="sb s1"><h5>1. Che cosa so</h5>'+(q.know.length?'<ul>'+q.know.map(function(s){return '<li>'+T.nums(esc(s))+'</li>'}).join('')+'</ul>':'<p>Tutto quello che serve è nella domanda qui accanto.</p>')+'</div>'+
   '<div class="sb s2"><h5>2. Che cosa devo trovare</h5>'+q.ask.map(function(s){return '<p>'+T.nums(esc(s))+'</p>'}).join('')+'</div>'+
   '<div class="sb s3"><h5>3. Come rispondo</h5><p>'+how(e)+'</p></div></div>'+
   (w.length?'<h4 style="margin-top:.8rem">Parole difficili</h4><dl class="words">'+w.map(function(x){return '<dt>'+esc(x[0])+'</dt><dd>'+esc(x[2])+'</dd>'}).join('')+'</dl>':'')+sayBtn()},
 h1:function(e){var p=ep(e);return '<h4>💡 Aiuto 1: un indizio</h4><p>Questo esercizio è del tipo «'+e.t+'».</p>'+(p?'<p>La regola che ti serve è spiegata nella puntata '+p[0]+' della rubrica: «'+esc(p[1])+'». La trovi nella <a href="azure.html">guida Content Understanding</a>.</p>':'')+
   '<p>'+(e.k==='mcq'?'Leggi tutte le risposte prima di scegliere. Spesso una o due si possono escludere subito.':'Scrivi su un foglio i numeri del testo. Poi chiediti: quali vanno divisi, quali moltiplicati, e in che ordine?'+(e.u?' Il risultato è in '+unit(e)+'.':''))+'</p>'+sayBtn()},
 h2:function(e){if(e.k==='mcq'&&e.o.length>=3){var wr=[];e.o.forEach(function(o,i){if(i!==e.c)wr.push(i)});wr=wr.slice(0,Math.max(1,Math.floor(e.o.length/2)));
     document.querySelectorAll('#stage .opt2').forEach(function(l,i){if(wr.indexOf(i)>=0)l.classList.add('out')});
     return '<h4>🧭 Aiuto 2: restringi il campo</h4><p>Queste risposte le puoi escludere:</p><ul>'+wr.map(function(i){return '<li>'+e.o[i]+'</li>'}).join('')+'</ul><p>Nell\'elenco le vedi barrate. Scegli tra quelle rimaste.</p>'+sayBtn()}
   return '<h4>🧭 Aiuto 2: il metodo</h4><p>Ecco i passaggi, senza i risultati. I conti falli tu, anche con la calcolatrice qui sotto.</p><ol>'+mask(e).map(function(s){return '<li>'+T.nums(esc(s))+'</li>'}).join('')+'</ol>'+sayBtn()},
 h3:function(e){return '<h4>✅ Aiuto 3: la soluzione passo passo</h4><ol>'+steps(e.s).map(function(s){return '<li>'+T.nums(s)+'</li>'}).join('')+'</ol><p><b>Risposta: '+(e.k==='num'?e.fa:e.o[e.c])+'</b></p><p>Ora prova a rifare i passaggi da solo e premi Verifica: i punti li prendi lo stesso.</p>'+sayBtn()},
 es:function(e){var x=sibling(e);if(!x)return '<h4>📘 Esempio svolto</h4><p>Per questo tipo di esercizio non c\'è un secondo esempio. Apri l\'aiuto 3 per vedere la soluzione passo passo.</p>'+sayBtn();
   return '<h4>📘 Esempio svolto: stesso tipo, altri dati</h4><p>Guarda come si risolve questo. Poi torna al tuo e fai gli stessi passaggi.</p><div class="exq">'+T.nums(x.q)+'</div><ol>'+steps(x.s).map(function(s){return '<li>'+T.nums(s)+'</li>'}).join('')+'</ol><p><b>Risposta dell\'esempio: '+(x.k==='num'?x.fa:x.o[x.c])+'</b></p>'+sayBtn()},
 calc:function(e){return '<h4>🔢 Calcolatrice</h4><p id="calch">Scrivi un calcolo con + − × ÷ e le parentesi, per esempio 17.646 / 3.000. Il punto separa le migliaia, la virgola i decimali.</p><div class="calc"><label for="calci">Calcolo</label><input id="calci" inputmode="text" autocomplete="off" aria-describedby="calch"><button type="button" class="pbtn" id="calcb">= Calcola</button></div><p class="calcout" id="calco" role="status" aria-live="polite"></p>'}
};
function calc(){var raw=$('calci').value,v=raw.replace(/\s/g,'').replace(/[÷:]/g,'/').replace(/[×xX]/g,'*').replace(/−/g,'-');
  v=v.replace(/\d[\d.,]*/g,function(n){n=n.replace(/[.,]+$/,'');if(n.indexOf(',')>=0)return n.replace(/\./g,'').replace(',','.');if(/^\d{1,3}(\.\d{3})+$/.test(n))return n.replace(/\./g,'');return n});
  if(!v||!/^[\d.+\-*\/()]+$/.test(v)){$('calco').textContent='Non riesco a leggere il calcolo. Usa solo numeri e i segni + − × ÷ ( ).';return}
  var r;try{r=(new Function('return ('+v+')'))()}catch(err){r=NaN}
  if(typeof r!=='number'||!isFinite(r)){$('calco').textContent='Il calcolo non torna: controlla parentesi e segni.';return}
  $('calco').textContent='= '+fmt(r,4)+(Math.abs(r-Math.round(r))>1e-9?' · per eccesso: '+fmt(Math.ceil(r),0)+' · per difetto: '+fmt(Math.floor(r),0):'')}
/* ---------------- vista di un esercizio */
function order(){var L=list();return L.length?L:EX}
function open(id){var e=BY[id];cur=e;$('listview').hidden=true;var S=$('stage');S.hidden=false;
  var hb=[['h1','💡 1. Un indizio'],['h2',e.k==='mcq'&&e.o.length>=3?'🧭 2. Restringi il campo':'🧭 2. Il metodo'],['h3','✅ 3. Soluzione passo passo'],['es','📘 Esempio svolto'],['facile','🧩 Spiegamelo facile']];if(e.k==='num')hb.push(['calc','🔢 Calcolatrice']);
  var h='<button type="button" class="back" id="xback">← Tutti gli esercizi</button><div class="kicker" style="margin-top:.9rem"><span class="chip">N. '+e.id+'</span><span class="chip l'+e.l+'">'+LN[e.l]+'</span><span class="chip">'+PT[e.l]+' punti</span><span class="chip topic">'+GN[e.g]+'</span>'+(done[e.id]?'<span class="chip done">✓ Risolto</span>':'')+'</div>'+
    '<h2 id="xt" tabindex="-1">'+e.t+'</h2><div class="qq" id="xq">'+T.nums(e.q)+'</div>'+
    '<button type="button" class="rt-say" id="xsay">'+T.avatar(28)+'<span>Rada, leggimi l\'esercizio</span></button>'+
    '<form class="card ans" id="xf" novalidate>';
  if(e.k==='mcq'){h+='<fieldset><legend>Scegli una risposta</legend>'+e.o.map(function(o,i){return '<label class="opt2"><input type="radio" name="r'+e.id+'" value="'+i+'"'+(SV[e.id]&&SV[e.id].v===i?' checked':'')+'><span>'+o+'</span></label>'}).join('')+'</fieldset>'}
  else{h+='<div class="numrow"><label for="xn">La tua risposta'+(e.u?' ('+e.u+')':'')+'</label><input id="xn" inputmode="decimal" autocomplete="off" aria-describedby="xfb" value="'+(SV[e.id]&&SV[e.id].v!=null?esc(SV[e.id].v):'')+'"></div>'}
  h+='<div class="acts"><button type="submit" class="vbtn">Verifica</button></div><p class="fb" id="xfb" role="status" aria-live="polite"></p></form>'+
    '<section class="help" aria-labelledby="xh"><h3 id="xh">Hai bisogno di una mano?</h3><p class="nop">Gli aiuti non tolgono punti e non c\'è limite di tempo. Parti dal primo e apri il successivo solo se serve.</p><div class="hbtns">'+
    hb.map(function(b){return '<button type="button" class="hbtn" data-h="'+b[0]+'" aria-expanded="false" aria-controls="hp_'+b[0]+'">'+b[1]+'</button>'}).join('')+'</div>'+hb.map(function(b){return '<div class="hpan" id="hp_'+b[0]+'" hidden></div>'}).join('')+'</section>'+
    '<div class="snav"><button type="button" class="pbtn" id="xprev">← Precedente</button><button type="button" class="pbtn" id="xnext">Prossimo da fare →</button></div>'+
    '<p class="ref">Riferimento: '+e.p+' · <a href="azure.html">guida Content Understanding</a></p>';
  S.innerHTML=h;
  $('xback').onclick=function(){location.hash='esercizi'};
  $('xf').onsubmit=function(ev){ev.preventDefault();check(e)};
  $('xsay').onclick=function(){var q=qparts(e);T.say(e.t,[plain(e.q),'Devi trovare questo: '+q.ask.join(' '),how(e),'Se vuoi una mano, apri gli aiuti sotto la risposta: non tolgono punti.'],{play:true})};
  S.querySelectorAll('.hbtn').forEach(function(b){b.onclick=function(){var k=b.dataset.h,p=$('hp_'+k),on=p.hidden;if(on&&!p.innerHTML){p.innerHTML=HELP[k](e);if(k==='calc'){$('calcb').onclick=calc;$('calci').addEventListener('keydown',function(x){if(x.key==='Enter'){x.preventDefault();calc()}})}}
    p.hidden=!on;b.setAttribute('aria-expanded',on?'true':'false');if(on){if(T.prefs.auto&&k!=='calc')speak(p,false);if(k==='calc')$('calci').focus()}}});
  S.onclick=function(ev){var b=ev.target.closest('[data-say]');if(b)speak(b.closest('.hpan'),true)};
  var O=order(),i=O.indexOf(e);$('xprev').disabled=i<=0;$('xprev').onclick=function(){if(i>0)location.hash='ex'+O[i-1].id};
  $('xnext').onclick=function(){var n=O.slice(i+1).concat(O.slice(0,Math.max(i,0))).filter(function(x){return !done[x.id]&&x.id!==e.id})[0];if(n)location.hash='ex'+n.id;else{$('xfb').className='fb ok';$('xfb').textContent='Hai risolto tutti gli esercizi di questo elenco!'}};
  S.scrollIntoView({block:'start'});$('xt').focus({preventScroll:true})}
function speak(p,play){var h=p.querySelector('h4'),parts=[];p.querySelectorAll('p,li,dt,dd,h5,.exq').forEach(function(n){if(n.closest('.calc')||n.id==='calch'||n.id==='calco')return;var t=T.text(n);if(t)parts.push(/[.!?:]$/.test(t)?t:t+'.')});T.say(h?T.text(h):'',parts,{play:play})}
function check(e){var id=e.id,fb=$('xfb'),ok,dir='';tries[id]=(tries[id]||0)+1;
  if(e.k==='mcq'){var sel=document.querySelector('input[name="r'+id+'"]:checked');if(!sel){fb.className='fb ko';fb.textContent='Scegli prima una risposta.';return}RSol.set('ex',id,{v:+sel.value});SV=RSol.all('ex');
    ok=+sel.value===e.c;document.querySelectorAll('input[name="r'+id+'"]').forEach(function(r){var l=r.parentNode;l.classList.remove('ok','ko');if(+r.value===e.c&&ok)l.classList.add('ok');if(r===sel&&!ok)l.classList.add('ko')})}
  else{var v=num($('xn').value);if(isNaN(v)){fb.className='fb ko';fb.textContent='Scrivi un numero, per esempio 1.250 o 3,5.';return}ok=Math.abs(v-e.a)<=e.tol;RSol.set('ex',id,{v:$('xn').value});SV=RSol.all('ex');
    if(!ok&&tries[id]>=2)dir=v>e.a?' Il tuo numero è troppo alto.':' Il tuo numero è troppo basso.'}
  fb.className='fb '+(ok?'ok':'ko');
  if(ok){var first=!done[id];if(first){done[id]=1;save();var k=document.querySelector('#stage .kicker');if(k&&!k.querySelector('.done'))k.insertAdjacentHTML('beforeend','<span class="chip done">✓ Risolto</span>')}
    fb.textContent='✓ Giusto!'+(first?' +'+PT[e.l]+' punti.':' Era già risolto: i punti li avevi già.')+' Puoi passare al prossimo.'}
  else fb.textContent='✗ Non ancora.'+dir+' Nessun problema: riprova, oppure apri un aiuto qui sotto.'}
function route(){var m=/^#ex(\d+)$/.exec(location.hash);if(m&&BY[+m[1]]){open(+m[1])}else{var back=cur;cur=null;T.stop();$('stage').hidden=true;$('stage').innerHTML='';$('listview').hidden=false;
  if(back){var L=list(),i=L.indexOf(back);if(i>=0)st.page=Math.floor(i/PER)+1}render();if(back&&$('lx'+back.id))$('lx'+back.id).focus()}}
/* ---------------- comandi dell'elenco */
document.addEventListener('click',function(ev){var p=ev.target.closest('#ppager [data-p]');if(p&&!p.disabled){st.page=+p.getAttribute('data-p');render();$('esercizi').scrollIntoView()}
  var g=ev.target.closest('#trk [data-g]');if(g){st.g=g.dataset.g;st.page=1;render()}});
function seg(attr,key,conv){document.querySelectorAll('.pal-row ['+attr+']').forEach(function(b){b.onclick=function(){st[key]=conv(b.getAttribute(attr));st.page=1;document.querySelectorAll('.pal-row ['+attr+']').forEach(function(x){x.setAttribute('aria-pressed',x===b?'true':'false')});render()}})}
seg('data-l','l',function(v){return +v});seg('data-s','s',function(v){return v});
var tq;$('pq').addEventListener('input',function(){clearTimeout(tq);tq=setTimeout(function(){st.q=$('pq').value;st.page=1;render()},200)});
$('prand').onclick=function(){var L=list();if(L.length)location.hash='ex'+L[Math.floor(Math.random()*L.length)].id};
$('pnext').onclick=function(){var n=list().filter(function(e){return !done[e.id]})[0];if(n)location.hash='ex'+n.id;else $('pcount').textContent='Con questi filtri non resta nulla da fare.'};
function resInit(){var b=$('preset');b.textContent='Azzera i progressi';var x=$('pres2');if(x)x.remove();b.onclick=function(){b.textContent='Sì, azzera tutto';b.insertAdjacentHTML('afterend','<button type="button" class="fbtn" id="pres2">Annulla</button>');$('pres2').onclick=function(){resInit();b.focus()};b.onclick=function(){done={};save();resInit();render();b.focus()}}}resInit();
function esolList(){var n=Object.keys(RSol.all('ex')).length;$('esolcount').textContent=n?('Risposte salvate: '+n+' esercizi.'):'Non hai ancora risposte salvate.'}esolList();
$('esolexp').onclick=function(){RSol.exportFile();$('esolmsg').textContent='File scaricato.'};
$('esolimp').onchange=function(){var f=this.files&&this.files[0];if(!f)return;RSol.importFile(f,function(err,d){if(err){$('esolmsg').textContent='⚠ '+err.message;return}var v=RStore.load('radar_ex');if(v)done=decD(v);SV=RSol.all('ex');render();esolList();$('esolmsg').textContent='Ripristinato il salvataggio del '+new Date(d.data).toLocaleDateString('it-IT')+'.'})};
$('ebk').value='EX1:'+encD(done,EX.length);
$('ebc').onclick=function(){var t=$('ebk');t.select();try{navigator.clipboard.writeText(t.value).then(function(){$('ebm').textContent='Codice copiato.'},function(){document.execCommand('copy');$('ebm').textContent='Codice copiato.'})}catch(e){document.execCommand('copy');$('ebm').textContent='Codice copiato.'}};
$('ebr').onclick=function(){var v=$('ebi').value.trim();if(v.indexOf('EX1:')!==0){$('ebm').textContent='⚠ Questo non sembra un codice della Palestra (deve iniziare con EX1:).';return}done=decD(v.slice(4));save();render();$('ebi').value='';$('ebm').textContent='Progressi ripristinati: '+Object.keys(done).length+' esercizi completati.'};
window.addEventListener('hashchange',route);route();
})();</script>'''

ex_js = json.dumps(EX, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
js = (JS.replace('__CODEC__', store.EX_CODEC).replace('__EX__', ex_js).replace('__EPT__', json.dumps(EPT, ensure_ascii=False, separators=(',', ':')))
      .replace('__WORDS__', json.dumps(WORDS, ensure_ascii=False, separators=(',', ':'))).replace('__GR__', json.dumps(GR, ensure_ascii=False)))
page = (argomenti.head_from(root, 'Palestra Content Understanding') + CSS + tutor.CSS + store.BACKUP_CSS + store.SOL_CSS + '</head>\n<body>\n' + argomenti.NAV('azure-esercizi.html', eds) + hero +
        '<main class="wrap">' + ctl + '</main>' + argomenti.FOOT + argomenti.JS + store.JS + store.SOL_JS + tutor.JS + js + '\n</body>\n</html>\n')
open(os.path.join(root, 'azure-esercizi.html'), 'w', encoding='utf-8').write(page)
print('ok', N, len(page))
