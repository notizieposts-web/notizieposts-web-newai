"""Pagina "Laboratorio Content Understanding": gioco di sfide pratiche. Uso: python3 lab_page.py <repo>"""
import sys, os, json, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import argomenti, graph, bench, store
from lab_gen import CH
MAN = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'lab_manifest.json')))
for c in CH:
    c.pop('_file', None)
    m = MAN.get(str(c['id']))
    if m: c['dl'] = m['f']; c['dlkb'] = m['kb']
import glob as _glob
PACKS = []
for _p in sorted(_glob.glob(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'lab_daily', 'packs', '*.json'))):
    _d = json.load(open(_p, encoding='utf-8')); PACKS.append(_d)
    for _i, _c in enumerate(_d['sfide']):
        _c['o'] = -(_d['livello'] * 1000) + _i; CH.append(_c)
LAST = PACKS[-1] if PACKS else None

root = sys.argv[1]
eds = graph.data(root)
# mescola in modo deterministico opzioni e problemi
for c in CH:
    r = random.Random('lab%d' % c['id'])
    if c['mode'] == 'debug':
        idx = list(range(len(c['opts']))); r.shuffle(idx); c['opts'] = [c['opts'][i] for i in idx]; c['c'] = idx.index(c['c'])
    if c['mode'] == 'ottimizza':
        r.shuffle(c['issues'])
MODES = [('estrai', '📄', 'Estrai e trasforma', 'Leggi il documento, estrai i valori, applica le condizioni e scrivili nel formato richiesto.'),
         ('ottimizza', '🛠', 'Ottimizza il prompt', 'Trova cosa non va nello schema o nel prompt, poi confronta con la versione migliorata.'),
         ('costi', '💶', 'Taglia i costi', 'Muovi le leve e porta il conto sotto l\'obiettivo, senza violare i requisiti.'),
         ('vuln', '🛡', 'Trova le vulnerabilità', 'Tocca le righe della configurazione che espongono dati o lasciano spazio agli attacchi.'),
         ('debug', '🔍', 'Perché non funziona', 'Il sistema non fa quello che chiedi: trova la causa vera.'),
         ('prova', '🤖', 'Prova libera', 'Incolla un documento e uno schema, e fai estrarre i campi a un modello gratuito.')]
cnt = {m[0]: sum(1 for c in CH if c['mode'] == m[0]) for m in MODES}

CSS = '''<style id="lab-css">
.gbar{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,13rem),1fr));gap:.8rem;margin-top:1.4rem}
.gstat{padding:1rem 1.1rem!important}.gstat .k{font:700 .75rem var(--head,system-ui);letter-spacing:.08em;text-transform:uppercase;color:var(--muted)}
.gstat .v{font:800 1.5rem var(--head,system-ui);margin-top:.2rem}.gstat .s{font-size:.85rem;color:var(--muted)}
.xpbar{height:10px;border-radius:999px;background:var(--soft);border:1px solid var(--line);overflow:hidden;margin-top:.5rem}.xpbar i{display:block;height:100%;background:var(--violet);width:0}
.modes{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,11rem),1fr));gap:.6rem;margin-top:1.4rem}
.mbtn{display:flex;flex-direction:column;align-items:flex-start;gap:.2rem;padding:.8rem 1rem;border-radius:16px;border:1px solid var(--line);background:var(--surface);color:var(--ink);cursor:pointer;text-align:left;font:inherit;min-height:44px}
.mbtn b{font:700 1rem var(--head,system-ui)}.mbtn span{font-size:.82rem;color:var(--muted)}
.mbtn[aria-pressed="true"]{border:2px solid var(--violet);background:var(--violet-soft)}
.picker{display:flex;flex-wrap:wrap;gap:.5rem;align-items:center;margin-top:1.2rem}
.picker select{font:inherit;min-height:40px;padding:.4rem .7rem;border-radius:10px;border:1px solid var(--line);background:var(--surface);color:var(--ink);max-width:100%;flex:1;min-width:min(100%,16rem)}
.pbtn{min-height:40px;padding:.4rem .9rem;border-radius:999px;border:1px solid var(--line);background:var(--surface);color:var(--ink);font-weight:700;cursor:pointer}
.stage{margin-top:1.2rem}
.lgrid{display:grid;grid-template-columns:minmax(0,1fr);gap:1rem}@media (min-width:980px){.lgrid{grid-template-columns:minmax(0,1.05fr) minmax(0,1fr)}}
.paper{background:#FFFFFF;color:#121A2B;border:1px solid #D3D9E6;border-radius:6px;padding:1.4rem 1.5rem;font:15px/1.6 Georgia,'Times New Roman',serif;box-shadow:0 10px 30px rgba(10,14,30,.12);overflow-x:auto}
.paper{display:flow-root}.paper .dh{margin-bottom:.6rem}.paper .dr{text-align:right;margin-bottom:.6rem;padding-top:.6rem;border-top:1px solid #D3D9E6}.paper table{display:table!important;width:100%;border-collapse:collapse;margin:1rem 0;font-size:14px}
.paper th,.paper td{border-bottom:1px solid #D3D9E6;padding:.3rem .6rem .3rem .4rem;text-align:left;white-space:nowrap}.paper td:nth-child(n+2),.paper th:nth-child(n+2){text-align:right}
.paper .tot{clear:both;text-align:right;margin:.8rem 0}.paper p{clear:both;margin:.6rem 0}.paper .ctr{text-align:center}.paper .small{font-size:12px}.paper .mail{font-family:ui-monospace,Menlo,monospace;font-size:13px;border-bottom:1px solid #D3D9E6;padding-bottom:.5rem}
.paper .hid{opacity:0}.paper.show .hid{opacity:1;background:#FFF5D1;outline:2px dashed #A34E08;color:#121A2B}
.paper .dv.hl-ok{background:#D6F3EC;box-shadow:0 0 0 2px #0A6A7C;border-radius:3px}.paper .dv.hl-ko{background:#FCE7EF;box-shadow:0 0 0 2px #C2185B;border-radius:3px}
.paper .dv.hl-hint{background:#FFF5D1;box-shadow:0 0 0 2px #A34E08;border-radius:3px}
.paper sup.tag{font:700 10px system-ui;background:#121A2B;color:#FFFFFF;border-radius:6px;padding:0 4px;margin-left:2px}
.ptool{display:flex;gap:.5rem;flex-wrap:wrap;margin:.6rem 0 0}
a.pbtn{display:inline-flex;align-items:center;text-decoration:none}
.chip.fmt{background:var(--ink)!important;color:var(--bg)!important;font-family:ui-monospace,Menlo,monospace}
.paper .xl,.paper .pp,.paper .ml,.paper .vt,.paper .wd{font-family:system-ui,-apple-system,'Segoe UI',sans-serif;font-size:14px}
.paper .xltabs{display:flex;flex-wrap:wrap;gap:4px;border-bottom:2px solid #1D6F42;margin-bottom:10px}.paper .xltabs span{background:#E8F3EC;color:#123;border:1px solid #9BC8AE;border-bottom:0;padding:2px 8px;font-size:12px;border-radius:4px 4px 0 0}
.paper .sheet{margin:10px 0}.paper .sname{font-weight:700;color:#1D4D33;margin:4px 0}.paper .xl table{font-size:13px;display:table!important;width:auto!important;min-width:60%}.paper .xl th{background:#E8F3EC}
.paper .hidsheet{display:none!important}.paper.show .hidsheet{display:block!important;outline:2px dashed #A34E08;background:#FFF5D1}.paper.show .xltabs .hidsheet{display:inline-block!important}
.paper .pp{display:grid;grid-template-columns:repeat(auto-fill,minmax(180px,1fr));gap:10px}.paper .slide{aspect-ratio:16/9;border:1px solid #C9D1E0;border-radius:6px;padding:8px 10px;position:relative;background:#FBFCFF;overflow:hidden}
.paper .slide b{display:block;font-size:13px;color:#3F3FD9;margin-bottom:4px}.paper .slide p{font-size:12px;margin:0;clear:none}.paper .slide .sn{position:absolute;right:6px;bottom:4px;font-size:10px;color:#4E5A72}
.paper .ml p{margin:6px 0}.paper .mlbody{border-top:1px solid #D3D9E6;padding-top:8px;max-height:22rem;overflow:auto;font-size:13px}
.paper .vt p{margin:5px 0}.paper .vt .tc{font-family:ui-monospace,Menlo,monospace;font-size:12px;color:#4E5A72}
.paper .im{text-align:center}.paper .im img{max-width:100%;height:auto;border:1px solid #D3D9E6}.paper details.ocr{margin-top:8px}.paper details.ocr summary{cursor:pointer;font-weight:700;min-height:32px}.paper details.ocr pre{white-space:pre-wrap;font-size:13px}
.paper.show details.ocr{}
.paper .wd .h,.paper .rep .h,.paper .bdoc .h{font-weight:700;font-size:15px}
.paper .cmt{display:block;margin:.4rem 0 .4rem 1rem;padding:.4rem .6rem;border-left:4px solid #A34E08;background:#FFF5D1;font-size:13px;border-radius:0 8px 8px 0}
.paper figure.chart{margin:.6rem 0;max-width:440px}.paper .notes{font-size:13px;background:#F1F3F8;border:1px solid #D3D9E6;border-radius:8px;padding:.5rem .7rem}
.paper .slide.wide{grid-column:1/-1;aspect-ratio:auto}.paper .slide table{font-size:11px;margin:4px 0}
.paper .pb{text-align:center;color:#4E5A72;font-size:12px;border-top:2px dashed #C9D1E0;padding-top:6px}
.paper .bundle{display:grid;gap:12px}.paper .bdoc{border:1px solid #C9D1E0;border-radius:6px;padding:8px 10px;overflow-x:auto}
.paper .bdoc td,.paper .bdoc th,.paper .rep td,.paper .rep th,.paper .wd td,.paper .wd th{white-space:normal;padding-right:.6rem}.paper .bdoc table,.paper .wd table,.paper .rep table{font-size:13px;table-layout:fixed;width:100%!important;min-width:0!important}.paper .bdoc td,.paper .bdoc th{overflow-wrap:anywhere}
.newday{margin-top:1rem;padding:1rem 1.2rem;border:2px solid var(--violet);border-radius:18px;background:var(--surface)}.newday ul{list-style:none;padding:0;display:flex;flex-wrap:wrap;gap:.4rem;margin:.5rem 0 0}
.task h3{font-size:1.2rem;margin:.3rem 0 .5rem}
.frow{display:grid;grid-template-columns:minmax(0,1fr);gap:.25rem;padding:.7rem 0;border-bottom:1px solid var(--line)}
.frow label{font-weight:700}.frow label code{font-size:.95rem}.frow .fmt{font-size:.85rem;color:var(--muted)}
.frow input,.frow select{font:inherit;min-height:40px;padding:.4rem .7rem;border-radius:10px;border:1px solid var(--line);background:var(--surface);color:var(--ink);max-width:22rem}
.frow .res{font-size:.9rem;font-weight:600}.frow .res.ok{color:var(--teal)}.frow .res.ko{color:var(--red)}
.acts2{display:flex;flex-wrap:wrap;gap:.5rem;margin-top:1rem}
.vbtn2{min-height:44px;padding:.45rem 1.2rem;border-radius:999px;border:0;background:var(--violet);color:var(--bg);font:700 1rem var(--head,system-ui);cursor:pointer}
.code{background:var(--soft);border:1px solid var(--line);border-radius:12px;padding:1rem;overflow-x:auto;font:13px/1.55 ui-monospace,Menlo,Consolas,monospace;white-space:pre;color:var(--ink);max-height:28rem}
.code.wrap{white-space:pre-wrap}
.out{margin-top:1rem}.out h4{margin:1rem 0 .4rem}
.iss{display:flex;gap:.6rem;align-items:flex-start;padding:.6rem .8rem;border:1px solid var(--line);border-radius:12px;margin:.4rem 0;cursor:pointer}
.iss input{width:20px;height:20px;margin-top:.15rem;flex:none}.iss.ok{border:2px solid var(--teal);background:var(--teal-soft)}.iss.ko{border:2px solid var(--red);background:var(--red-soft)}.iss.miss{border:2px dashed var(--sun);background:var(--sun-soft)}
.iss .why{display:block;font-size:.88rem;margin-top:.2rem}
.lever{border:1px solid var(--line);border-radius:14px;padding:.8rem 1rem;margin:.6rem 0}
.lever legend{font-weight:700;padding:0 .3rem}.lever label{display:flex;gap:.5rem;align-items:flex-start;min-height:32px;padding:.2rem 0;cursor:pointer}.lever input{width:18px;height:18px;margin-top:.2rem}
.meter{position:sticky;top:7rem}.meter .big{font:800 2rem var(--head,system-ui)}.meter .row{display:flex;justify-content:space-between;gap:1rem;font-size:.92rem;padding:.2rem 0}
.mbar{height:14px;border-radius:999px;background:var(--soft);border:1px solid var(--line);overflow:hidden;margin:.6rem 0;position:relative}.mbar i{display:block;height:100%;background:var(--violet)}
.mbar b{position:absolute;top:-3px;bottom:-3px;width:3px;background:var(--ink)}
.warn{margin:.6rem 0;padding:.6rem .8rem;border-radius:12px;background:var(--red-soft);border:1px solid var(--red);font-weight:600}
.win{margin:.6rem 0;padding:.6rem .8rem;border-radius:12px;background:var(--teal-soft);border:1px solid var(--teal);font-weight:700}
.vline{display:flex;gap:.7rem;align-items:flex-start;width:100%;text-align:left;font:14px/1.5 ui-monospace,Menlo,Consolas,monospace;padding:.55rem .8rem;border:1px solid var(--line);border-radius:10px;background:var(--surface);color:var(--ink);margin:.35rem 0;cursor:pointer;min-height:40px}
.vline .n{color:var(--muted);min-width:1.6rem}.vline[aria-pressed="true"]{border:2px solid var(--violet);background:var(--violet-soft)}
.vline.ok{border:2px solid var(--teal);background:var(--teal-soft)}.vline.ko{border:2px solid var(--red);background:var(--red-soft)}.vline.miss{border:2px dashed var(--sun);background:var(--sun-soft)}
.vline .why{display:block;font-family:var(--body,system-ui);font-size:.88rem;margin-top:.2rem}
.dopt{display:flex;gap:.6rem;align-items:flex-start;padding:.6rem .8rem;border:1px solid var(--line);border-radius:12px;margin:.4rem 0;cursor:pointer}
.dopt input{width:18px;height:18px;margin-top:.2rem;flex:none}.dopt.ok{border:2px solid var(--teal);background:var(--teal-soft)}.dopt.ko{border:2px solid var(--red);background:var(--red-soft)}
.fbk{font-weight:700;margin:.8rem 0 0;min-height:1.4em}
.toast{position:fixed;left:50%;bottom:1.2rem;transform:translateX(-50%);z-index:9600;padding:.7rem 1.2rem;border-radius:999px;background:var(--ink);color:var(--bg);font-weight:700;box-shadow:0 10px 30px rgba(0,0,0,.25);opacity:0;transition:opacity .2s;pointer-events:none}
.toast.on{opacity:1}
@media (prefers-reduced-motion:reduce){.toast{transition:none}}
.chip.l1{background:var(--teal-soft)!important;color:var(--ink)!important;border:1px solid var(--teal)!important}
.chip.l2{background:var(--sun-soft)!important;color:var(--ink)!important;border:1px solid var(--sun)!important}
.chip.l3{background:var(--red-soft)!important;color:var(--ink)!important;border:1px solid var(--red)!important}
.badges{display:flex;flex-wrap:wrap;gap:.4rem;margin-top:.4rem}
</style>'''

hero = ('<header class="hero"><div><div class="meta"><span class="chip guide">Laboratorio</span><span class="chip">%d sfide</span><span class="chip">5 modalità</span></div>'
        '<h1 style="margin-top:1.2rem">Laboratorio Content Understanding: il gioco</h1>'
        '<p class="sub">Documenti veri da cui estrarre e trasformare valori, schemi e prompt da ottimizzare, conti da tagliare, configurazioni da mettere in sicurezza e guasti da diagnosticare. Guadagni punti, sali di livello, e ogni risposta ti spiega il perché.</p></div>%s</header>') % (len(CH), argomenti.MARK)

PAGES = {'estrai': 'lab-estrai.html', 'ottimizza': 'lab-ottimizza.html', 'costi': 'lab-costi.html', 'vuln': 'lab-vulnerabilita.html', 'debug': 'lab-debug.html', 'prova': 'lab-prova.html'}
GBAR = ('<div class="gbar"><div class="card gstat"><div class="k">Livello</div><div class="v" id="glv">Apprendista</div><div class="xpbar" aria-hidden="true"><i id="gxpbar"></i></div><div class="s" id="gnext"></div></div>'
        '<div class="card gstat"><div class="k">Punti</div><div class="v" id="gxp">0</div><div class="s">esperienza totale</div></div>'
        '<div class="card gstat"><div class="k">Serie perfetta</div><div class="v" id="gstreak">0</div><div class="s" id="gbest">record: 0</div></div>'
        '<div class="card gstat"><div class="k">Sfide completate</div><div class="v" id="gdone">0</div><div class="badges" id="gbadges"></div></div></div>')
def modes_nav(cur):
    return ('<nav class="modes" aria-label="Modalità di gioco">' + ''.join('<a class="mbtn" href="%s"%s><b>%s %s</b><span>%s · %s</span></a>' % (PAGES[m], ' aria-current="page"' if m == cur else '', ic, lab, ('%d sfide' % cnt[m]) if cnt[m] else 'banco di prova', d) for m, ic, lab, d in MODES) + '</nav>')
PICKER = ('<div class="picker" id="gpick"><label class="sr-only" for="gsel">Scegli la sfida</label><select id="gsel"></select>'
          '<button type="button" class="pbtn" id="gprev" aria-label="Sfida precedente">←</button><button type="button" class="pbtn" id="gnextc" aria-label="Sfida successiva">→</button>'
          '<button type="button" class="pbtn" id="gtodo">Prossima da fare</button><button type="button" class="pbtn" id="grand">🎲 A caso</button></div>')
RULES = ('<section class="ch" id="regole"><div class="ch-head"><div class="kicker"><span class="chip guide">Regole</span></div><h2>Come si fanno i punti</h2></div>'
        '<div class="prose"><ul><li><b>Estrai e trasforma</b>: 10 punti per ogni campo giusto al primo tentativo, 5 dopo. Dopo la verifica il documento evidenzia da dove viene ogni valore, come la "messa a terra" del servizio. Ogni documento si può scaricare nel suo formato.</li>'
        '<li><b>Ottimizza il prompt</b>: 10 punti per ogni problema vero individuato, meno 5 per ogni falso allarme.</li><li><b>Taglia i costi</b>: 50 punti se arrivi sotto l\'obiettivo senza violare i requisiti, 20 in più se sei a meno dell\'1% dall\'ottimo.</li>'
        '<li><b>Trova le vulnerabilità</b>: 10 punti per ogni riga vulnerabile trovata, meno 5 per ogni riga sicura segnata.</li><li><b>Perché non funziona</b>: 30 punti al primo tentativo, 10 dopo.</li>'
        '<li>La <b>serie perfetta</b> conta le sfide di fila risolte con il punteggio pieno. Livelli: Apprendista, Lettore (150), Analista (400), Ingegnere (800), Architetto (1.500), Maestro (2.500), Leggenda (4.000). Punti e progressi valgono in tutte le pagine del Laboratorio.</li>'
        '<li><b>Banco di prova</b>: in ogni sfida "Estrai" e nella modalità "Prova libera" puoi far lavorare un modello gratuito, nel browser (WebLLM, nessun account, il documento resta sul tuo computer) o Gemini con la tua chiave personale. È una simulazione del passaggio generativo, non il servizio Azure.</li>'
        '<li>Prezzi e tariffe dei modelli nel gioco sono ipotetici e indicati nel testo; quote, limiti e comportamenti vengono dalla documentazione ufficiale citata nella <a href="azure.html">guida</a>.</li></ul></div></section>')
VERO = ('<section class="ch" id="vero"><div class="ch-head"><div class="kicker"><span class="chip guide">Il servizio vero</span></div><h2>Provare Content Understanding senza spendere</h2></div>'
        '<div class="prose"><p>Il servizio vero non è un modello da scaricare: gira solo su Azure. Ma si può provare a costo zero, con due avvertenze.</p><ul>'
        '<li><b>Account gratuito di Azure</b>: 200 dollari di credito da usare entro 30 giorni. Alla registrazione servono una carta di credito o di debito non prepagata e un numero di telefono; la carta non viene addebitata all\'iscrizione.</li>'
        '<li><b>Livello gratuito F0</b>: il tutorial ufficiale con Logic Apps indica che per provare Content Understanding si può usare il piano gratuito F0 della risorsa Foundry, e poi passare a un piano a pagamento per la produzione.</li>'
        '<li><b>Attenzione ai token</b>: i campi generativi usano la distribuzione del modello che colleghi in Foundry, e quei token si pagano a parte (dal credito, finché c\'è). <code>prebuilt-read</code> e <code>prebuilt-layout</code> non usano modelli linguistici: sono il modo più economico per fare le prime prove.</li>'
        '<li><b>Da dove partire</b>: Content Understanding Studio per provare gli analizzatori senza codice, oppure la CU CLI del Content Understanding Toolkit su una cartella di file di esempio. I documenti scaricabili del Laboratorio sono fatti apposta: dati inventati, nessun dato reale.</li></ul>'
        '<p class="note">Fonti: Microsoft Azure, account gratuito; Microsoft Learn, tutorial Content Understanding con Logic Apps e guida ai prezzi.</p></div></section>')
NEWDAY = ''
if LAST:
    _first = {}
    for _c in LAST['sfide']: _first.setdefault(_c['mode'], _c['id'])
    NEWDAY = ('<div class="newday"><p style="margin:0;font-weight:700">🆕 Sfide del giorno %s · livello %d</p><p style="margin:.3rem 0 0">Ogni giorno 10 nuove sfide per modalità, più difficili del giorno prima: documenti con commenti, tabelle, grafici, note e pacchetti di più file.</p><ul>' % (LAST['giorno'][8:10] + '/' + LAST['giorno'][5:7], LAST['livello']) +
              ''.join('<li><a class="chip" href="%s#s%d">%s %s</a></li>' % (PAGES[m], _first[m], ic, lab) for m, ic, lab, d in MODES if m in _first) + '</ul></div>')
TOAST = '<div class="toast" id="toast" role="status" aria-live="polite"></div>'
JS = r'''<script id="lab-js">(function(){
var META=__META__,IDX=__IDX__,PAGES=__PAGES__,PAGE=__PAGE__,MODES=__MODES__,LV=[[0,'Apprendista'],[150,'Lettore'],[400,'Analista'],[800,'Ingegnere'],[1500,'Architetto'],[2500,'Maestro'],[4000,'Leggenda']],LN={1:'Media',2:'Alta',3:'Estrema'};
__CODEC__
var S={xp:0,done:{},streak:0,best:0};(function(){var o=decS(RStore.load('radar_lab'));if(!o){try{o=JSON.parse(localStorage.getItem('radar-lab')||'null')}catch(e){}}if(o)S=Object.assign(S,o)})();
function save(){RStore.save('radar_lab',encS(S))}
var $=function(id){return document.getElementById(id)},mode='estrai',cur=null,att={};
function esc(s){return String(s).replace(/[&<>"]/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]})}
function byMode(m){return META.slice().sort(function(a,b){return (a.o!=null?a.o:a.id)-(b.o!=null?b.o:b.id)})}
function toast(t){var x=$('toast');x.textContent=t;x.classList.add('on');clearTimeout(toast.t);toast.t=setTimeout(function(){x.classList.remove('on')},2200)}
function hud(){var l=0;for(var i=0;i<LV.length;i++)if(S.xp>=LV[i][0])l=i;$('glv').textContent=LV[l][1];$('gxp').textContent=S.xp.toLocaleString('it-IT');
  var nx=LV[l+1];$('gnext').textContent=nx?('ancora '+(nx[0]-S.xp)+' punti per '+nx[1]):'livello massimo';$('gxpbar').style.width=(nx?((S.xp-LV[l][0])/(nx[0]-LV[l][0])*100):100)+'%';
  $('gstreak').textContent=S.streak;$('gbest').textContent='record: '+S.best;var TOT=Object.keys(IDX).reduce(function(a,k){return a+IDX[k].length},0);$('gdone').textContent=Object.keys(S.done).length+' / '+TOT;
  $('gbadges').innerHTML=MODES.filter(function(m){return m[0]!=='prova'}).map(function(m){var t=IDX[m[0]]||[],d=t.filter(function(id){return S.done[id]!==undefined}).length;return '<span class="chip'+(d===t.length?' done':'')+'" title="'+esc(m[2])+'">'+m[1]+' '+d+'/'+t.length+'</span>'}).join('');}
function finish(c,score,max){var first=S.done[c.id]===undefined;var prev=S.done[c.id]||0;if(score>prev){S.xp+=score-prev;S.done[c.id]=score}else if(first)S.done[c.id]=score;
  if(first){if(score>=max&&max>0){S.streak++;if(S.streak>S.best)S.best=S.streak}else S.streak=0}
  save();hud();fillSel();toast(score>prev?('+'+(score-prev)+' punti'+(score>=max?' · perfetto!':'')):'Sfida registrata')}
var NOREST=false;
function retry(c,box){var el=document.getElementById(box);if(!el||el.querySelector('.rbtn'))return;el.insertAdjacentHTML('beforeend','<button type="button" class="pbtn rbtn">↺ Riprova la sfida</button>');el.querySelector('.rbtn').onclick=function(){NOREST=true;REND[c.mode](c);NOREST=false;var f=document.querySelector('#stage input,#stage select,#stage button');if(f)f.focus()}}
function svNote(sv){if(!sv||!sv.t)return '';var d=new Date(sv.t);return '<p class="savednote">📒 Ho ripristinato le risposte che avevi salvato il '+d.toLocaleDateString('it-IT')+' alle '+d.toLocaleTimeString('it-IT',{hour:'2-digit',minute:'2-digit'})+'. Puoi verificarle di nuovo o cambiarle.</p>'}
function benchSave(c){return function(v){RSol.set('lab',c.id,{bench:{schema:v.schema,sys:v.sys}})}}
function closedMsg(){toast('Sfida già verificata: premi «Riprova la sfida» per rifarla da capo')}
function num(v){v=String(v).trim().replace(/[\s$€%]/g,'');if(!v)return NaN;if(v.indexOf(',')>=0&&v.indexOf('.')>=0){if(v.lastIndexOf(',')>v.lastIndexOf('.'))v=v.replace(/\./g,'').replace(',','.');else v=v.replace(/,/g,'')}else if(v.indexOf(',')>=0)v=v.replace(',','.');else if(/^-?[1-9]\d{0,2}(\.\d{3})+$/.test(v))v=v.replace(/\./g,'');return parseFloat(v)}
function fillSel(){if(!$('gsel'))return;var L=byMode(mode);$('gsel').innerHTML=L.map(function(c,i){return '<option value="'+c.id+'"'+(cur&&cur.id===c.id?' selected':'')+'>'+(S.done[c.id]!==undefined?'✓ ':'')+(i+1)+'. '+esc(c.t)+' · '+LN[c.l]+(c.fmt?' · '+c.fmt:'')+'</option>'}).join('')}
function kick(c){var L=byMode(c.mode);return '<div class="kicker"><span class="chip">Sfida '+(L.findIndex(function(x){return x.id===c.id})+1)+' di '+L.length+'</span><span class="chip l'+c.l+'">'+LN[c.l]+'</span>'+(c.fmt?'<span class="chip fmt">.'+(c.dl?c.dl.split('.').pop():c.fmt)+'</span>':'')+(S.done[c.id]!==undefined?'<span class="chip done">✓ '+S.done[c.id]+' punti</span>':'')+'</div>'}
/* ---------- ESTRAI */
/* schema per il banco di prova: i campi che l'esercizio chiede, con formati e regole (non solo l'estrazione standard) */
function exSchema(c){var F={},T={},n=0;(c.fields||[]).forEach(function(f){if(f.src&&!f.src.length)return;var d={description:f.fmt||''};
    if(f.type==='num'){d.type='number';d.method='generate'}else if(f.type==='date'){d.type='date';d.method='generate'}else if(f.type==='enum'){d.type='string';d.method='classify';d.enum=f.opts}else{d.type='string';d.method='generate'}
    F[f.label]=d;T[f.label]=f.ans;n++});if(!n)return null;
  var tmp=document.createElement('div');tmp.innerHTML=c.task||'';
  return {schema:JSON.stringify({description:'Campi richiesti dall\'esercizio',fieldSchema:{fields:F}},null,2),truth:T,rules:(tmp.textContent||'').trim()}}
function rEstrai(c){
  var FL={pdf:'PDF',xlsx:'Excel',docx:'Word',pptx:'PowerPoint',eml:'Email',png:'Immagine',vtt:'Trascrizione audio'};
  var h='<div class="lgrid"><div><div class="paper" id="paper" tabindex="0" role="document" aria-label="Documento da analizzare, formato '+FL[c.fmt]+'">'+c.doc+'</div><div class="ptool">'+(c.dl?'<a class="pbtn" href="'+c.dl+'" download>⬇ Scarica il documento ('+c.dl.split('.').pop()+', '+c.dlkb+' KB)</a>':'')+(/class="(hid|hidsheet)/.test(c.doc)||c.fmt==='xlsx'?'<button type="button" class="pbtn" id="showhid" aria-pressed="false">👁 Mostra il contenuto nascosto (come lo legge il servizio)</button>':'')+'</div></div>';
  h+='<div class="task card">'+kick(c)+'<h3>'+esc(c.t)+'</h3><p>'+c.task+'</p><div id="esv"></div><form id="ef" novalidate>';
  c.fields.forEach(function(f,i){var id='f'+c.id+'_'+i;h+='<div class="frow"><label for="'+id+'"><span aria-hidden="true">'+(i+1)+'.</span> <code>'+esc(f.label)+'</code></label><span class="fmt" id="'+id+'d">Formato: '+esc(f.fmt)+'</span>';
    if(f.type==='enum')h+='<select id="'+id+'" aria-describedby="'+id+'d"><option value="">Scegli…</option>'+f.opts.map(function(o){return '<option>'+esc(o)+'</option>'}).join('')+'</select>';
    else h+='<input id="'+id+'" autocomplete="off" aria-describedby="'+id+'d"'+(f.type==='num'?' inputmode="decimal"':'')+'>';
    h+='<span class="res" id="'+id+'r" role="status"></span></div>'});
  h+='<div class="acts2"><button type="submit" class="vbtn2">Verifica</button><button type="button" class="pbtn" id="ehint">💡 Suggerimento (−5)</button><button type="button" class="pbtn" id="esol">Mostra la soluzione</button></div><div class="acts2" id="eacts"></div></form><div class="out" id="eout"></div></div></div><div id="benchbox"></div>';
  $('stage').innerHTML=h;var a=att[c.id]={tries:0,ok:{},score:0,hints:0,closed:false};
  if(window.RadarBench)var sv=RSol.get('lab',c.id);if(sv&&sv.f&&!NOREST){c.fields.forEach(function(f,i){var el=document.getElementById('f'+c.id+'_'+i);if(el&&sv.f[i]!=null)el.value=sv.f[i]});$('esv').innerHTML=svNote(sv)}
  RadarBench.mount($('benchbox'),{doc:function(){return c.ocr||RadarBench.h2t(c.doc)},schema:c.schema,truth:c.truth,alt:exSchema(c),trap:c.trap,savedSchema:sv&&sv.bench&&sv.bench.schema,savedSys:sv&&sv.bench&&sv.bench.sys,onSave:benchSave(c),title:'Banco di prova: fai estrarre questo documento a un modello gratuito'});
  if($('showhid'))$('showhid').onclick=function(){var p=$('paper'),on=!p.classList.contains('show');p.classList.toggle('show',on);this.setAttribute('aria-pressed',on?'true':'false')};
  function val(f,i){return document.getElementById('f'+c.id+'_'+i).value}
  function right(f,v){if(f.type==='num'){var n=num(v);return !isNaN(n)&&Math.abs(n-f.ans)<=(f.tol!=null?f.tol:0.011)}
    v=String(v).trim().replace(/\s+/g,' ');if(f.type==='date')return v===f.ans;if(f.type==='enum')return v===f.ans;if(/MAIUSCOLO/.test(f.fmt))return v===f.ans;return v.toLowerCase()===String(f.ans).toLowerCase()}
  function paint(show){var p=$('paper');p.querySelectorAll('sup.tag').forEach(function(s){s.remove()});p.querySelectorAll('.dv').forEach(function(s){s.classList.remove('hl-ok','hl-ko','hl-hint')});
    c.fields.forEach(function(f,i){var ok=a.ok[i];f.src.forEach(function(k){p.querySelectorAll('.dv[data-k="'+k+'"]').forEach(function(s){s.classList.add(ok?'hl-ok':(show?'hl-ko':'hl-ko'));if(!s.querySelector('sup'))s.insertAdjacentHTML('beforeend','<sup class="tag" aria-hidden="true">'+(i+1)+'</sup>')})})})}
  function outp(full){var o={};c.fields.forEach(function(f){o[f.label]=f.ans});$('eout').innerHTML='<h4>Output atteso</h4><div tabindex="0" role="region" aria-label="Codice" class="code">'+esc(JSON.stringify(o,null,2))+'</div><h4>Lo schema che lo estrae</h4><div tabindex="0" role="region" aria-label="Codice" class="code">'+esc(c.schema)+'</div><p>'+esc(c.post)+'</p>'}
  $('ef').onsubmit=function(ev){ev.preventDefault();if(a.closed){closedMsg();retry(c,'eacts');return}RSol.set('lab',c.id,{f:c.fields.map(function(f,i){return val(f,i)})});a.tries++;var all=true;
    c.fields.forEach(function(f,i){var r=document.getElementById('f'+c.id+'_'+i+'r'),ok=right(f,val(f,i));if(ok&&!a.ok[i]){a.ok[i]=true;a.score+=a.tries===1?10:5}
      if(!ok)all=false;r.className='res '+(ok?'ok':'ko');r.textContent=ok?'✓ '+f.why:'✗ Non ancora. Controlla il formato richiesto.'});
    paint();if(all){a.closed=true;retry(c,'eacts');var max=c.fields.length*10,sc=Math.max(0,a.score-a.hints*5);finish(c,sc,max);outp();$('eout').insertAdjacentHTML('afterbegin','<p class="win">Tutti i campi corretti: '+sc+' punti su '+max+'.</p>')}};
  $('ehint').onclick=function(){if(a.closed)return;var i=c.fields.findIndex(function(f,j){return !a.ok[j]});if(i<0)return;a.hints++;var f=c.fields[i],p=$('paper');
    p.querySelectorAll('.dv').forEach(function(s){s.classList.remove('hl-hint')});f.src.forEach(function(k){p.querySelectorAll('.dv[data-k="'+k+'"]').forEach(function(s){s.classList.add('hl-hint')})});
    toast('Campo '+(i+1)+': guarda le parti evidenziate in giallo (−5)')};
  $('esol').onclick=function(){retry(c,'eacts');if(!a.closed){a.closed=true;c.fields.forEach(function(f,i){var r=document.getElementById('f'+c.id+'_'+i+'r');if(!a.ok[i]){r.className='res ko';r.textContent='Risposta: '+f.ans+'. '+f.why}});paint(true);
    if(S.done[c.id]===undefined){S.done[c.id]=0;S.streak=0;save();hud();fillSel()}}outp()};
}
/* ---------- OTTIMIZZA */
function rOtt(c){
  var h='<div class="card">'+kick(c)+'<h3>'+esc(c.t)+'</h3><p>'+esc(c.ctx)+'</p><div tabindex="0" role="region" aria-label="Codice" class="code'+(c.bad.charAt(0)==='{'?'':' wrap')+'">'+esc(c.bad)+'</div>';
  h+='<fieldset style="border:0;padding:0;margin:1rem 0 0"><legend style="font-weight:700">Quali sono i problemi veri? Seleziona tutti quelli che trovi.</legend>'+c.issues.map(function(x,i){return '<label class="iss" id="is'+i+'"><input type="checkbox" value="'+i+'"><span>'+esc(x.x)+'<span class="why" id="isw'+i+'"></span></span></label>'}).join('')+'</fieldset>';
  h+='<div class="acts2" id="oacts"><button type="button" class="vbtn2" id="overif">Verifica</button></div><p class="fbk" id="ofb" role="status"></p><div class="out" id="oout"></div></div>';
  $('stage').innerHTML=h;var sv=NOREST?null:RSol.get('lab',c.id);if(sv&&sv.c){sv.c.forEach(function(i){var x=$('is'+i);if(x)x.querySelector('input').checked=true});$('oacts').insertAdjacentHTML('beforebegin',svNote(sv))}
  var odone=false;$('overif').onclick=function(){if(odone){closedMsg();return}odone=true;RSol.set('lab',c.id,{c:c.issues.map(function(x,i){return $('is'+i).querySelector('input').checked?i:-1}).filter(function(i){return i>=0})});var sc=0,max=0,miss=0;c.issues.forEach(function(x,i){var el=$('is'+i),ch=el.querySelector('input').checked;if(x.ok)max+=10;el.classList.remove('ok','ko','miss');
      if(ch&&x.ok){sc+=10;el.classList.add('ok')}else if(ch&&!x.ok){sc-=5;el.classList.add('ko')}else if(!ch&&x.ok){miss++;el.classList.add('miss')}
      $('isw'+i).textContent=(x.ok?(ch?'✓ Giusto: ':'Ti è sfuggito: '):(ch?'✗ Falso allarme: ':'Corretto non segnarlo: '))+x.why});
    sc=Math.max(0,sc);$('ofb').textContent='Punteggio: '+sc+' su '+max+(miss?' · problemi mancati: '+miss:'');
    $('oout').innerHTML='<h4>Versione ottimizzata</h4><div tabindex="0" role="region" aria-label="Codice" class="code'+(c.good.charAt(0)==='{'?'':' wrap')+'">'+esc(c.good)+'</div>';c.issues.forEach(function(x,i){$('is'+i).querySelector('input').disabled=true});retry(c,'oacts');finish(c,sc,max)};
}
/* ---------- COSTI */
function rCosti(c){
  var h='<div class="lgrid"><div class="card">'+kick(c)+'<h3>'+esc(c.t)+'</h3><p>'+esc(c.story)+'</p><p class="fmt" style="font-size:.88rem;color:var(--muted)">Listino del gioco, ipotetico. Obiettivo: scendere sotto '+fm(c.target)+' al mese.</p>';
  c.levers.forEach(function(lv,li){h+='<fieldset class="lever"><legend>'+esc(lv.lab)+'</legend>'+lv.opts.map(function(o,oi){return '<label><input type="radio" name="lv'+li+'" value="'+oi+'"'+(oi===0?' checked':'')+'><span>'+esc(o.x)+'</span></label>'}).join('')+'</fieldset>'});
  h+='</div><div><div class="card meter" aria-live="polite"><div class="k" style="font:700 .75rem var(--head);letter-spacing:.08em;text-transform:uppercase;color:var(--muted)">Costo mensile</div><div class="big" id="cbig"></div><div class="mbar" aria-hidden="true"><i id="cbar"></i><b id="ctgt"></b></div><div id="crows"></div><div id="cmsg"></div><div class="acts2" id="cacts"><button type="button" class="vbtn2" id="cok">Conferma la configurazione</button></div><p class="fbk" id="cfb" role="status"></p></div></div></div>';
  $('stage').innerHTML=h;
  function sel(){return c.levers.map(function(lv,li){return +document.querySelector('input[name="lv'+li+'"]:checked').value})}
  function calc(s){var p=Object.assign({},c.base);c.levers.forEach(function(lv,li){Object.assign(p,lv.opts[s[li]].set||{})});var P=p.pages,m=P*(p.share==null?1:p.share);
    var e=P*p.ext/1000,x=P*p.ctx/1000,ti=m*(p.tin*(p.conf||1)+(p.fig||0))*p.pin/1e6,to=m*p.tout*p.pout/1e6;return {e:e,x:x,ti:ti,to:to,t:e+x+ti+to}}
  function viol(s){return c.forbid.filter(function(f){var li=c.levers.findIndex(function(l){return l.k===f.k});return li>=0&&s[li]===f.o})}
  function upd(){var s=sel(),r=calc(s),v=viol(s);$('cbig').textContent=fm(r.t);var mx=c.start;$('cbar').style.width=Math.min(100,r.t/mx*100)+'%';$('ctgt').style.left=Math.min(100,c.target/mx*100)+'%';
    $('crows').innerHTML=[['Estrazione',r.e],['Contestualizzazione',r.x],['Token in ingresso',r.ti],['Token in uscita',r.to],['Obiettivo',c.target],['Partenza',c.start]].map(function(z){return '<div class="row"><span>'+z[0]+'</span><b>'+fm(z[1])+'</b></div>'}).join('');
    $('cmsg').innerHTML=v.map(function(f){return '<p class="warn">⚠ Requisito violato: '+esc(f.why)+'</p>'}).join('')+(!v.length&&r.t<=c.target?'<p class="win">Sotto l\'obiettivo e nei requisiti: puoi confermare.</p>':'')}
  var sv=NOREST?null:RSol.get('lab',c.id);if(sv&&sv.s){sv.s.forEach(function(oi,li){var r=document.querySelector('input[name="lv'+li+'"][value="'+oi+'"]');if(r)r.checked=true});$('cmsg').insertAdjacentHTML('beforebegin',svNote(sv))}
  document.querySelectorAll('.lever input').forEach(function(i){i.onchange=function(){upd();RSol.set('lab',c.id,{s:sel()})}});upd();
  $('cok').onclick=function(){var s=sel(),r=calc(s),v=viol(s);if(v.length){$('cfb').textContent='Prima risolvi i requisiti violati.';return}
    if(r.t>c.target){$('cfb').textContent='Sei a '+fm(r.t)+': manca ancora '+fm(r.t-c.target)+' per l\'obiettivo.';return}
    var sc=50+(r.t<=c.best*1.01?20:0);retry(c,'cacts');$('cfb').textContent='Obiettivo raggiunto: da '+fm(c.start)+' a '+fm(r.t)+' ('+Math.round((1-r.t/c.start)*100)+'% in meno). Ottimo possibile: '+fm(c.best)+'.';finish(c,sc,70)};
}
function fm(x){return x.toLocaleString('it-IT',{minimumFractionDigits:2,maximumFractionDigits:2})+' $'}
/* ---------- VULN */
function rVuln(c){
  var h='<div class="card">'+kick(c)+'<h3>'+esc(c.t)+'</h3><p>'+esc(c.intro)+'</p><div role="group" aria-label="Righe della configurazione">'+c.lines.map(function(l,i){return '<button type="button" class="vline" id="vl'+i+'" aria-pressed="false"><span class="n" aria-hidden="true">'+(i+1)+'</span><span>'+esc(l.x)+'<span class="why" id="vw'+i+'"></span></span></button>'}).join('')+'</div>';
  h+='<div class="acts2" id="vacts"><button type="button" class="vbtn2" id="vverif">Verifica</button></div><p class="fbk" id="vfb" role="status"></p></div>';$('stage').innerHTML=h;
  var vdone=false;var sv=NOREST?null:RSol.get('lab',c.id);if(sv&&sv.p){sv.p.forEach(function(i){var b=$('vl'+i);if(b)b.setAttribute('aria-pressed','true')});$('vacts').insertAdjacentHTML('beforebegin',svNote(sv))}c.lines.forEach(function(l,i){$('vl'+i).onclick=function(){if(vdone){closedMsg();return}this.setAttribute('aria-pressed',this.getAttribute('aria-pressed')==='true'?'false':'true')}});
  $('vverif').onclick=function(){if(vdone){closedMsg();return}vdone=true;RSol.set('lab',c.id,{p:c.lines.map(function(l,i){return $('vl'+i).getAttribute('aria-pressed')==='true'?i:-1}).filter(function(i){return i>=0})});var sc=0,max=0,miss=0;c.lines.forEach(function(l,i){var b=$('vl'+i),on=b.getAttribute('aria-pressed')==='true';if(l.bad)max+=10;
      if(on&&l.bad){sc+=10;b.classList.add('ok');$('vw'+i).textContent='✓ Vulnerabile: '+l.why}else if(on&&!l.bad){sc-=5;b.classList.add('ko');$('vw'+i).textContent='✗ Non è una vulnerabilità.'+(l.why?' '+l.why:'')}
      else if(!on&&l.bad){miss++;b.classList.add('miss');$('vw'+i).textContent='Ti è sfuggita: '+l.why}});
    sc=Math.max(0,sc);$('vfb').textContent='Punteggio: '+sc+' su '+max+(miss?' · righe mancate: '+miss:'');retry(c,'vacts');finish(c,sc,max)};
}
/* ---------- DEBUG */
function rDebug(c){
  var h='<div class="card">'+kick(c)+'<h3>'+esc(c.t)+'</h3><p>'+c.case+'</p><fieldset style="border:0;padding:0;margin:0"><legend style="font-weight:700;margin-bottom:.3rem">Qual è la causa?</legend>'+c.opts.map(function(o,i){return '<label class="dopt" id="do'+i+'"><input type="radio" name="dbg" value="'+i+'"><span>'+esc(o)+'</span></label>'}).join('')+'</fieldset>';
  h+='<div class="acts2" id="dacts"><button type="button" class="vbtn2" id="dverif">Verifica</button></div><p class="fbk" id="dfb" role="status"></p></div>';$('stage').innerHTML=h;var tries=0,closed=false;var sv=NOREST?null:RSol.get('lab',c.id);if(sv&&sv.o!=null){var rr=document.querySelector('input[name="dbg"][value="'+sv.o+'"]');if(rr)rr.checked=true;$('dacts').insertAdjacentHTML('beforebegin',svNote(sv))}
  $('dverif').onclick=function(){if(closed){closedMsg();return}var s=document.querySelector('input[name="dbg"]:checked');if(!s){$('dfb').textContent='Scegli una risposta.';return}tries++;var i=+s.value;RSol.set('lab',c.id,{o:i});
    document.querySelectorAll('.dopt').forEach(function(d){d.classList.remove('ok','ko')});
    if(i===c.c){closed=true;retry(c,'dacts');$('do'+i).classList.add('ok');$('dfb').textContent='✓ Esatto. '+c.why;finish(c,tries===1?30:10,30)}else{$('do'+i).classList.add('ko');$('dfb').textContent='✗ Non è questa: riprova.'}};
}
var CACHE={};function get(id){if(CACHE[id])return Promise.resolve(CACHE[id]);return fetch('lab/c'+id+'.json').then(function(r){if(!r.ok)throw new Error(r.status);return r.json()}).then(function(c){CACHE[id]=c;return c})}
var REND={estrai:rEstrai,ottimizza:rOtt,costi:rCosti,vuln:rVuln,debug:rDebug};
function show(m){$('stage').innerHTML='<p class="fbk" role="status">Carico la sfida…</p>';get(m.id).then(function(c){cur=c;REND[c.mode](c);fillSel();try{history.replaceState(null,'','#s'+c.id)}catch(e){}}).catch(function(){$('stage').innerHTML='<p class="warn">Non riesco a caricare la sfida: controlla la connessione e riprova.</p>'})}
function sandbox(){get(IDX.estrai[0]).then(function(first){$('stage').innerHTML='<div class="card"><h3>Prova libera</h3><p>Incolla il testo di un documento di esempio e scrivi lo schema dei campi nello stesso formato di Content Understanding. Il modello restituisce il JSON; tu confronti, correggi le descrizioni e riprovi. Non incollare documenti reali o aziendali.</p><div id="sbox"></div></div>';
  var sp=RSol.get('prova','libera')||{};RadarBench.mount($('sbox'),{open:true,docText:RadarBench.h2t(first.doc),schema:first.schema,savedDoc:sp.doc,savedSchema:sp.schema,savedSys:sp.sys,title:'Banco di prova libero',onSave:function(v){RSol.set('prova','libera',v)}})})}
function pos(){var L=byMode(mode);return L.findIndex(function(x){return cur&&x.id===cur.id})}
function step(d){var L=byMode(mode),i=pos();show(L[(i+d+L.length)%L.length]);$('stage').scrollIntoView({block:'start'})}
hud();
if(PAGE==='hub'){var lr=$('lreset');function lrInit(){lr.innerHTML='<button type="button" class="pbtn" id="lres1">Azzera i progressi del Laboratorio</button>';$('lres1').onclick=function(){lr.innerHTML='<span style="font-weight:700">Cancellare punti, serie e sfide completate?</span> <button type="button" class="vbtn2" id="lres2">Sì, azzera</button> <button type="button" class="pbtn" id="lres3">Annulla</button>';$('lres3').focus();$('lres3').onclick=function(){lrInit();$('lres1').focus()};$('lres2').onclick=function(){S={xp:0,done:{},streak:0,best:0};save();hud();lrInit();$('lres1').focus();toast('Progressi azzerati')}}}lrInit();
  var MN={estrai:'📄',ottimizza:'🛠',costi:'💶',vuln:'🛡',debug:'🔍'};function solList(){var all=RSol.all('lab'),ids=Object.keys(all).map(Number).sort(function(a,b){return (all[b].t||0)-(all[a].t||0)});$('lsolcount').textContent=ids.length?('Soluzioni salvate: '+ids.length+(RSol.get('prova','libera')?' · più la tua prova libera':'')+'. Le più recenti:'):'Non hai ancora soluzioni salvate: verifica una sfida per salvarla.';
    $('lsollist').innerHTML=ids.slice(0,40).map(function(id){var m=null;for(var k in IDX)if(IDX[k].indexOf(id)>=0)m=k;return m?'<li><a class="chip" href="'+PAGES[m]+'#s'+id+'">'+MN[m]+' sfida n. '+id+'</a></li>':''}).join('')}solList();
  $('lsolexp').onclick=function(){RSol.exportFile();$('lsolmsg').textContent='File scaricato: conservalo per ritrovare soluzioni e progressi.'};
  $('lsolimp').onchange=function(){var f=this.files&&this.files[0];if(!f)return;RSol.importFile(f,function(err,d){if(err){$('lsolmsg').textContent='⚠ '+err.message;return}var o=decS(RStore.load('radar_lab'));if(o)S=Object.assign({xp:0,done:{},streak:0,best:0},o);hud();solList();$('lsolmsg').textContent='Ripristinato il salvataggio del '+new Date(d.data).toLocaleDateString('it-IT')+'.'})};
  function bk(){$('lbk').value='LAB1:'+encS(S)}bk();var _h=hud;hud=function(){_h();if($('lbk'))bk()};
  $('lbc').onclick=function(){var t=$('lbk');t.select();try{navigator.clipboard.writeText(t.value).then(function(){$('lbm').textContent='Codice copiato.'},function(){document.execCommand('copy');$('lbm').textContent='Codice copiato.'})}catch(e){document.execCommand('copy');$('lbm').textContent='Codice copiato.'}};
  $('lbr').onclick=function(){var v=$('lbi').value.trim();if(v.indexOf('LAB1:')!==0){$('lbm').textContent='⚠ Questo non sembra un codice del Laboratorio (deve iniziare con LAB1:).';return}var o=decS(v.slice(5));if(!o){$('lbm').textContent='⚠ Codice non valido.';return}S=o;save();hud();$('lbi').value='';$('lbm').textContent='Progressi ripristinati: '+Object.keys(S.done).length+' sfide, '+S.xp+' punti.'};var hm=/^#s(\d+)$/.exec(location.hash);if(hm){var id=+hm[1];for(var k in IDX)if(IDX[k].indexOf(id)>=0){location.replace(PAGES[k]+'#s'+id);break}}else if(location.hash==='#prova')location.replace(PAGES.prova)}
else if(PAGE==='prova'){sandbox()}
else{mode=PAGE;
  $('gsel').onchange=function(){var id=+this.value;show(META.find(function(c){return c.id===id}))};
  $('gprev').onclick=function(){step(-1)};$('gnextc').onclick=function(){step(1)};
  $('gtodo').onclick=function(){var L=byMode(mode),i=pos();for(var k=1;k<=L.length;k++){var c=L[(i+k)%L.length];if(S.done[c.id]===undefined){show(c);$('stage').scrollIntoView({block:'start'});return}}toast('Hai completato tutte le sfide di questa modalità!')};
  $('grand').onclick=function(){var L=byMode(mode);show(L[Math.floor(Math.random()*L.length)]);$('stage').scrollIntoView({block:'start'})};
  var L0=byMode(mode),mm=/^#s(\d+)$/.exec(location.hash),st=mm&&META.find(function(c){return c.id===+mm[1]});show(st||L0.find(function(x){return S.done[x.id]===undefined})||L0[0])}
})();</script>'''

labdir = os.path.join(root, 'lab'); os.makedirs(labdir, exist_ok=True)
for c in CH:
    json.dump(c, open(os.path.join(labdir, 'c%d.json' % c['id']), 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
IDX = {m: [c['id'] for c in CH if c['mode'] == m] for m, _, _, _ in MODES if m != 'prova'}
HEAD = argomenti.head_from(root, 'Laboratorio Content Understanding') + CSS + bench.CSS + store.BACKUP_CSS + store.SOL_CSS + '<style>#stage{scroll-margin-top:7rem}a.mbtn{text-decoration:none}.mbtn[aria-current="page"]{border:2px solid var(--violet);background:var(--violet-soft)}</style></head>\n<body>\n'
def page(fname, pg, title, hero_html, body_html, meta):
    js = JS.replace('__CODEC__', store.LAB_CODEC).replace('__META__', json.dumps(meta, ensure_ascii=False, separators=(',', ':'))).replace('__IDX__', json.dumps(IDX)).replace('__PAGES__', json.dumps(PAGES)).replace('__PAGE__', json.dumps(pg)).replace('__MODES__', json.dumps(MODES, ensure_ascii=False))
    h = HEAD.replace('<title>Laboratorio Content Understanding · Radar AI</title>', '<title>%s · Radar AI</title>' % title) + argomenti.NAV('azure-laboratorio.html', eds) + hero_html + '<main class="wrap">' + body_html + '</main>' + argomenti.FOOT + argomenti.JS + store.JS + store.SOL_JS + bench.JS + js + '\n</body>\n</html>\n'
    open(os.path.join(root, fname), 'w', encoding='utf-8').write(h); return len(h)
sizes = {}
sizes['azure-laboratorio.html'] = page('azure-laboratorio.html', 'hub', 'Laboratorio Content Understanding', hero,
    '<section class="ch" id="gioco" style="padding-top:2.5rem"><div class="ch-head"><div class="kicker"><span class="chip guide">Partita</span></div><h2>La tua partita</h2><p class="lead">Scegli una modalità: ognuna ha la sua pagina, e punti e progressi valgono in tutte.</p></div>' + GBAR + NEWDAY + '<div class="acts2" id="lreset"></div>' + store.backup_html('l') + store.mysol_html('l') + modes_nav(None) + '</section>' + RULES + VERO + TOAST, [])
for m, ic, lab, d in MODES:
    meta = [{k: c[k] for k in ('id', 't', 'l', 'fmt', 'o') if k in c} for c in CH if c['mode'] == m]
    hh = ('<header class="hero"><div><div class="meta"><span class="chip guide">Laboratorio</span><span class="chip">%s</span></div><h1 style="margin-top:1.2rem">%s %s</h1><p class="sub">%s <a href="azure-laboratorio.html#regole">Regole e punti</a>.</p></div>%s</header>'
          % (('%d sfide' % cnt[m]) if cnt[m] else 'banco di prova', ic, lab, d, argomenti.MARK))
    body = '<section class="ch" id="gioco" style="padding-top:2rem">' + GBAR + modes_nav(m) + ('' if m == 'prova' else PICKER) + '<div class="stage" id="stage"></div></section>' + TOAST
    sizes[PAGES[m]] = page(PAGES[m], m, 'Laboratorio · ' + lab, hh, body, meta)
print('ok', len(CH), {k: round(v / 1024) for k, v in sizes.items()})
