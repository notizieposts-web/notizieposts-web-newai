"""Sapit: «Sapio, trova le parole chiave». Per ogni capitolo di un'edizione, il gufo Sapio trova le parole chiave,
le evidenzia nel testo e mostra la frase in cui compaiono, per aiutare a concentrarsi e a capire il contesto.
Tutto avviene nel browser, senza servizi esterni: funziona su tutte le edizioni, passate e future, senza lavoro in più.
Inserito da tools/inject.py solo nelle pagine edizioni/NN.html. Idempotente (id kw-css, kw-js).

Come sceglie le parole (nessuna AI, regole trasparenti):
  1. i termini del glossario marcati nel capitolo (<span class="gl">);
  2. i nomi propri: gruppi di parole con l'iniziale maiuscola che non stanno solo a inizio frase (Gemini 4 Carbon, Google DeepMind);
  3. le parole di contenuto che tornano più volte (almeno 3), escluse le parole comuni dell'italiano;
  il punteggio sale se la parola è nel titolo o nell'introduzione; i doppioni (Carbon dentro Gemini 4 Carbon) si uniscono.
"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rada

STOP = ("abbiamo adesso affinché agli alla alle allo allora almeno alcuni alcune altra altre altri altro anche ancora "
        "anni anno attraverso aveva avere avevano bisogna bene caso cento certo che chi ciascun ciascuno come comunque "
        "con contro cosa cose così cui dalla dalle dallo degli della delle dello dentro deve devono dice dicono diventa "
        "dopo dove dunque durante ecco esempio essere esso fare fatto fino finora forse fra gennaio febbraio marzo aprile "
        "maggio giugno luglio agosto settembre ottobre novembre dicembre giorno giorni già grande grandi ieri invece "
        "lavoro loro lunedì martedì mercoledì giovedì venerdì sabato domenica mentre meno mese mesi metà migliaia miliardi "
        "milioni modo molto molti molte nella nelle nello nessun nessuno niente noi nostro nostra nuova nuove nuovi nuovo "
        "oggi ogni ognuno oltre oppure ora ossia parte perché però piccolo pochi poco poi poiché possono potrebbe potrebbero "
        "prima primo proprio può quale quali qualche qualcosa quando quanto quasi quella quelle quelli quello questa "
        "queste questi questo quindi rispetto sarà sarebbe secondo sembra semplice sempre senza serve servono settimana "
        "settimane sia siamo significa solo soltanto sono sopra sotto stata state stati stato stessa stesse stessi stesso "
        "sulla sulle sullo tanto tempo testo tra tranne troppo tutta tutte tutti tutto ultima ultime ultimi ultimo "
        "una uno vengono viene volta volte vuol vuole edizione capitolo verifica fonte fonti dichiarato verificato limiti "
        "collegamenti annunciato annuncio spiega scrive detto dollari euro domanda domande risposta risposte "
        "esempi persone cosa caso numero numeri punto punti tipo esattamente davvero infatti cioè anzi inoltre "
        "the and for with from that this into il lo la le gli un di da in su per con tra fra se ma ed non sui sul sulla dal dai del dei nel nei al ai ad né mai più tu io lui lei voi copia due tre quattro cinque sei sette otto nove dieci mille arriva arrivano usato usata usati usate fatta fatti").split()

CSS = r"""<style id="kw-css">
.kw{margin:.9rem 0 0}
.kw-btn{display:inline-flex;align-items:center;gap:.5rem;min-height:44px;padding:.3rem .95rem .3rem .4rem;border-radius:999px;border:2px solid var(--violet);background:var(--surface);color:var(--ink);font:inherit;font-weight:700;cursor:pointer}
.kw-btn:hover{background:var(--violet-soft)}
.kw-btn[aria-expanded="true"]{background:var(--violet-soft)}
.kw-box{margin-top:.7rem;padding:1rem 1.1rem;border:1px solid var(--line);border-radius:16px;background:var(--surface);color:var(--ink)}
.kw-say{margin:0;line-height:1.5}
.kw-say b{color:var(--violet-ink)}
.kw-list{list-style:none;display:flex;flex-wrap:wrap;gap:.45rem;margin:.85rem 0 0;padding:0}
.kw-chip{display:inline-flex;align-items:center;gap:.35rem;min-height:36px;padding:.25rem .8rem;border-radius:999px;border:1px solid var(--line);background:var(--soft);color:var(--ink);font:inherit;font-weight:600;cursor:pointer}
.kw-chip:hover{border-color:var(--violet)}
.kw-chip[aria-pressed="true"]{background:var(--violet);border-color:var(--violet);color:var(--on-violet)}
.kw-n{font-weight:400;font-size:.85em;opacity:.9}
.kw-ctx{margin-top:.85rem}
.kw-ctx:empty{display:none}
.kw-card{padding:.85rem 1rem;border-left:4px solid var(--violet);border-radius:0 12px 12px 0;background:var(--violet-soft);color:var(--ink)}
.kw-card h4{margin:0 0 .35rem;font-size:1rem}
.kw-card p{margin:.3rem 0 0;line-height:1.55}
.kw-lab{font-size:.8rem;font-weight:700;text-transform:uppercase;letter-spacing:.04em;color:var(--muted)}
.kw-tools{display:flex;flex-wrap:wrap;gap:.45rem;margin-top:.85rem}
.kw-tool{min-height:36px;padding:.25rem .85rem;border-radius:10px;border:1px solid var(--line);background:var(--surface);color:var(--ink);font:inherit;cursor:pointer}
.kw-tool:hover{border-color:var(--violet)}
.kw-tool[aria-pressed="true"]{background:var(--violet);border-color:var(--violet);color:var(--on-violet)}
mark.kw-m{background:var(--violet-soft);color:var(--ink);border-bottom:2px solid var(--violet-ink);border-radius:3px;padding:0 .1em}
mark.kw-m.on{outline:2px solid var(--violet-ink);outline-offset:1px}
.kw-card mark.kw-m{background:var(--surface)}
/* Guida di lettura (line focus): due veli coprono il testo sopra e sotto la finestra di 1, 3 o 5 righe; niente barre laterali */
.kw-mask{position:fixed;left:0;right:0;z-index:40;pointer-events:none;background:var(--bg);opacity:.86}
.kw-lf{position:fixed;left:50%;transform:translateX(-50%);bottom:max(12px,env(safe-area-inset-bottom));z-index:60;display:flex;flex-wrap:wrap;justify-content:center;gap:.4rem;width:max-content;max-width:calc(100vw - 32px);padding:.45rem;border:1px solid var(--line);border-radius:14px;background:var(--surface);color:var(--ink);box-shadow:0 6px 24px rgba(0,0,0,.18)}
.kw-lf .kw-tool{min-height:44px}
.kw-lf-hint{flex-basis:100%;text-align:center;font-size:.9rem;line-height:1.35;color:var(--ink)}
.kw-branch{position:fixed;z-index:41;pointer-events:none;line-height:0}
.kw-branch svg{display:block;overflow:visible}
@media print{.kw-mask,.kw-lf,.kw-branch{display:none}}
/* Riga di aiuti del capitolo: Sapio, Leggimi, Testo più comodo */
.kw-row{display:flex;flex-wrap:wrap;gap:.5rem}
.kw-row .kw-btn{flex:none}
.kw-say-btn,.kw-aa{padding:.3rem 1rem}
.kw-aa b{font-size:1.1em;letter-spacing:-.02em}
.kw-rd{margin-top:.7rem;padding:1rem 1.1rem;border:1px solid var(--line);border-radius:16px;background:var(--surface);color:var(--ink)}
.kw-rd fieldset{border:0;margin:0 0 .6rem;padding:0}
.kw-rd legend{font-weight:700;margin-bottom:.35rem;padding:0}
.kw-rd .kw-opts{display:flex;flex-wrap:wrap;gap:.45rem}
.kw-rd label{display:inline-flex;align-items:center;gap:.5rem;min-height:44px;padding:.2rem .85rem;border:1px solid var(--line);border-radius:12px;cursor:pointer;font-weight:600}
.kw-rd label:has(input:checked){border-color:var(--violet);background:var(--violet-soft)}
.kw-rd input{width:20px;height:20px;margin:0;accent-color:var(--violet)}
.kw-rd .kw-hint{margin:.2rem 0 0;font-size:.9rem;color:var(--muted)}
/* Lettura facilitata (stesse preferenze "radar-read" di Palestra e Laboratorio) */
html.rt-s1{font-size:112.5%}html.rt-s1 body{font-size:19px}
html.rt-s2{font-size:125%}html.rt-s2 body{font-size:21px}
html.rt-sp main p,html.rt-sp main li,html.rt-sp main summary,html.rt-sp main .lead{line-height:2!important;letter-spacing:.045em;word-spacing:.14em}
html.rt-sp main .prose>p,html.rt-sp main .prose li{max-width:40rem}
html.rt-font body,html.rt-font main h1,html.rt-font main h2,html.rt-font main h3,html.rt-font main button,html.rt-font main input,html.rt-font .kw-lf button,html.rt-font .kw-tts button{font-family:"Atkinson Hyperlegible",Verdana,Tahoma,sans-serif!important}
/* Leggimi: la frase letta si colora e la pagina la segue */
::highlight(kw-now){background-color:#FFE08A;color:#1C1D1F}
.kw-now-p{background:var(--sun-soft);border-radius:6px;box-shadow:0 0 0 4px var(--sun-soft)}
.kw-tts{position:fixed;left:50%;transform:translateX(-50%);bottom:max(12px,env(safe-area-inset-bottom));z-index:61;display:flex;flex-wrap:wrap;justify-content:center;align-items:center;gap:.4rem;width:max-content;max-width:calc(100vw - 32px);padding:.45rem;border:1px solid var(--line);border-radius:14px;background:var(--surface);color:var(--ink);box-shadow:0 6px 24px rgba(0,0,0,.18)}
.kw-tts .kw-tool{min-height:44px}
.kw-tts .kw-ic{min-width:48px;font-size:1.1rem}
.kw-tts .kw-tts-st{flex-basis:100%;text-align:center;font-size:.9rem;line-height:1.35}
/* Segnalibro: riprendi da dove eri rimasto */
.kw-mark{position:fixed;left:50%;transform:translateX(-50%);bottom:max(12px,env(safe-area-inset-bottom));z-index:62;display:flex;flex-wrap:wrap;align-items:center;justify-content:center;gap:.5rem;width:max-content;max-width:calc(100vw - 32px);padding:.55rem .7rem;border:2px solid var(--violet);border-radius:16px;background:var(--surface);color:var(--ink);box-shadow:0 8px 28px rgba(0,0,0,.22)}
.kw-mark p{margin:0;font-weight:600;line-height:1.35;flex:1 1 12rem}
.kw-mark .kw-tool{min-height:44px}
.kw-mark .kw-tool.pri{background:var(--violet);border-color:var(--violet);color:var(--on-violet);font-weight:700}
@media print{.kw-tts,.kw-mark,.kw-row{display:none}}
@media (forced-colors:active){::highlight(kw-now){background-color:Highlight;color:HighlightText}.kw-now-p{outline:3px solid Highlight}}
/* Sfondi a scelta (solo tema chiaro) */
@media (prefers-color-scheme: light){html.rt-bg1:not([data-theme="dark"]){--bg:#FBF4E4;--surface:#FFFBF2;--soft:#F3EAD6}html.rt-bg2:not([data-theme="dark"]){--bg:#EAF2F8;--surface:#F7FBFE;--soft:#DFEAF2}html.rt-bg3:not([data-theme="dark"]){--bg:#EDF5E6;--surface:#F8FCF5;--soft:#E1EDD7}}
html.rt-bg1[data-theme="light"]{--bg:#FBF4E4;--surface:#FFFBF2;--soft:#F3EAD6}html.rt-bg2[data-theme="light"]{--bg:#EAF2F8;--surface:#F7FBFE;--soft:#DFEAF2}html.rt-bg3[data-theme="light"]{--bg:#EDF5E6;--surface:#F8FCF5;--soft:#E1EDD7}
.kw-sw{display:inline-block;width:18px;height:18px;border-radius:50%;border:1px solid var(--line)}
/* Una frase per riga */
.kw-br{display:none}
html.rt-fr .kw-br{display:block;height:.55em}
/* Solo testo */
html.rt-pl .grid2{grid-template-columns:minmax(0,1fr)!important}
html.rt-pl .grid2>.stick,html.rt-pl svg.radar,html.rt-pl .tl,html.rt-pl .tl-card{display:none!important}
html.rt-pl *{animation:none!important;transition:none!important}
/* Parole difficili */
.kw-hd-b{font:inherit;color:inherit;background:none;border:0;padding:0;margin:0;cursor:pointer;text-decoration:underline dotted var(--muted);text-decoration-thickness:2px;text-underline-offset:4px;line-height:inherit;letter-spacing:inherit;word-spacing:inherit}
.kw-hd-b[aria-expanded="true"]{text-decoration-style:solid;text-decoration-color:var(--violet-ink)}
.kw-hd-tip{display:block;margin:.35rem 0 .5rem;padding:.55rem .8rem;border-radius:10px;background:var(--soft);color:var(--ink);font-size:.95em;line-height:1.5}
.kw-hd-tip[hidden]{display:none}
.kw-hd-tip b{color:var(--violet-ink)}
/* In breve e mappa */
.kw-sum{margin-top:.7rem;border:1px solid var(--line);border-radius:14px;background:var(--surface);color:var(--ink)}
.kw-sum>summary{min-height:44px;display:flex;align-items:center;gap:.4rem;padding:.3rem 1rem;font-weight:700;cursor:pointer}
.kw-sum>div{padding:0 1rem .9rem}
.kw-sum ul{margin:.2rem 0 0;padding-left:1.2rem}.kw-sum li{margin:.35rem 0;line-height:1.55}
.kw-map{list-style:none;padding:0!important;display:grid;gap:.45rem}
.kw-map a{display:block;padding:.55rem .8rem;border:1px solid var(--line);border-left:4px solid #5E9E4B;border-radius:10px;color:var(--ink);text-decoration:none}
.kw-map a:hover,.kw-map a:focus-visible{background:var(--soft)}
.kw-map a b{display:block;color:var(--violet-ink)}.kw-map a span{display:block;font-size:.92em;color:var(--muted);margin-top:.15rem}
/* Tempo */
.kw-time{font-variant-numeric:tabular-nums}
/* Tappe */
.kw-hide{display:none!important}
.kw-step{display:flex;flex-wrap:wrap;align-items:center;gap:.7rem;margin:1rem 0 1.2rem;padding:.7rem .9rem;border:1px dashed var(--violet);border-radius:14px;background:var(--surface)}
.kw-step .kw-tool{min-height:44px;background:var(--violet);border-color:var(--violet);color:var(--on-violet);font-weight:700}
.kw-leaves{display:inline-flex;gap:5px;align-items:center}
.kw-leaf{display:inline-block;width:13px;height:13px;border:1.2px solid #3A2618;border-radius:50% 0 50% 0;transform:rotate(-45deg);background:var(--surface)}
.kw-leaf.on{background:#5E9E4B}
/* Domanda lampo */
.kw-quick{margin:1.4rem 0 0;padding:1rem 1.1rem;border:2px solid var(--violet);border-radius:16px;background:var(--surface);color:var(--ink)}
.kw-quick h3{margin:0 0 .4rem;font-size:1.05rem}
.kw-quick blockquote{margin:.3rem 0 .7rem;padding:0;font-style:normal;line-height:1.6}
.kw-quick .kw-opts{display:flex;flex-wrap:wrap;gap:.45rem}
.kw-quick .kw-tool{min-height:44px;font-weight:600}
.kw-quick .kw-tool.ok{background:#5E9E4B;border-color:#3A2618;color:#fff}
.kw-quick .kw-tool.no{border-color:var(--red);text-decoration:line-through}
.kw-qres{margin:.6rem 0 0;display:flex;align-items:center;gap:.5rem;font-weight:600}
.kw-qres:empty{display:none}
/* Pausa gentile */
.kw-pause{position:fixed;inset:0;z-index:90;display:flex;align-items:center;justify-content:center;padding:16px;background:rgba(0,0,0,.45)}
.kw-pause>div{max-width:24rem;width:100%;padding:1.3rem;border-radius:20px;background:var(--surface);color:var(--ink);text-align:center;border:2px solid var(--violet)}
.kw-pause h2{font-size:1.25rem;margin:.3rem 0}
.kw-breath{width:110px;height:110px;margin:1rem auto;border-radius:50%;background:radial-gradient(circle,#BFE3A8,#5E9E4B);display:flex;align-items:center;justify-content:center;font-weight:800;font-size:1.4rem;color:#1C1D1F!important}
@media (prefers-reduced-motion:no-preference){.kw-breath{animation:kw-br 8s ease-in-out infinite}@keyframes kw-br{0%,100%{transform:scale(.75)}50%{transform:scale(1.05)}}}
.kw-pause .kw-tool{min-height:44px}
@media print{.kw-sum,.kw-step,.kw-quick,.kw-pause,.kw-hd-tip{display:none!important}.kw-hide{display:block!important}}
@media (prefers-reduced-motion:no-preference){mark.kw-m.on{transition:outline-color .2s}}
@media (forced-colors:active){.kw-mask{forced-color-adjust:none;background:Canvas}mark.kw-m{forced-color-adjust:none;background:Mark;color:MarkText}.kw-chip[aria-pressed="true"],.kw-tool[aria-pressed="true"]{border:3px solid Highlight}}
</style>"""

HARD = {'asincrono': 'Che non aspetta: le parti lavorano ognuna per conto suo, senza fermarsi ad attendere le altre.', 'asincrona': 'Che non aspetta: le parti lavorano ognuna per conto suo, senza fermarsi ad attendere le altre.', 'parametri': "I numeri interni di un modello AI, regolati durante l'addestramento. Più parametri vuol dire, di solito, un modello più grande.", 'addestramento': 'La fase in cui un modello impara da tantissimi esempi, prima di essere usato.', 'addestrato': 'Che ha imparato da tantissimi esempi, nella fase chiamata addestramento.', 'licenza': 'Le regole che dicono cosa si può fare con un software o un modello: usarlo, modificarlo, venderlo.', 'sandbox': 'Un ambiente chiuso e sicuro dove un programma può fare prove senza toccare il resto del computer.', 'GPU': 'Il processore grafico: un chip che fa moltissimi calcoli insieme, usato per addestrare e far girare i modelli AI.', 'NPU': "Un chip pensato apposta per l'intelligenza artificiale, presente in molti portatili e telefoni recenti.", 'CPU': 'Il processore principale del computer, quello che esegue i programmi di tutti i giorni.', 'token': 'Un pezzetto di testo (una parola o parte di parola) che il modello legge e scrive uno alla volta.', 'benchmark': 'Una prova standard che serve a confrontare modelli o programmi con gli stessi compiti.', 'inferenza': 'Il momento in cui un modello già addestrato viene usato per rispondere.', 'quantizzazione': 'Un modo per rendere un modello più leggero salvando i suoi numeri con meno precisione.', 'precisione': "Quante cifre si usano per salvare ogni numero: meno precisione, file più piccolo ma risultati un po' meno esatti.", 'open source': 'Software di cui chiunque può leggere, usare e modificare il codice.', 'API': 'Una porta di accesso che permette a un programma di usare un servizio, per esempio un modello AI.', 'cloud': "Computer potenti di un'azienda, usati via internet invece che sul proprio computer.", 'server': 'Un computer che lavora per altri, rispondendo alle loro richieste via rete.', 'regressione': 'Quando una modifica fa peggiorare qualcosa che prima funzionava bene.', 'configurazione': "L'insieme delle impostazioni con cui un programma viene fatto funzionare.", 'configurazioni': 'Gli insiemi di impostazioni con cui un programma viene fatto funzionare.', 'algoritmo': 'Una sequenza precisa di passi per risolvere un problema.', 'dataset': 'Una raccolta ordinata di dati, usata per addestrare o provare un modello.', 'prompt': 'Il testo o la domanda che si scrive a un modello AI per chiedergli qualcosa.', 'multimodale': 'Che capisce più tipi di contenuto insieme: testo, immagini, audio.', 'chatbot': 'Un programma con cui si parla scrivendo, che risponde come in una chat.', 'codificatore': "La parte di un modello che trasforma un contenuto (per esempio un'immagine) in numeri che il modello capisce.", 'latenza': 'Il tempo di attesa tra una richiesta e la risposta.', 'scalabile': 'Che funziona bene anche quando il lavoro o il numero di utenti cresce molto.', 'framework': 'Un insieme di strumenti già pronti su cui costruire un programma.', 'repository': 'Lo spazio online dove si conserva il codice di un progetto, con tutta la sua storia.', 'firmware': 'Il software di base dentro un dispositivo, che lo fa funzionare.', 'crittografia': 'Tecniche per rendere un messaggio leggibile solo da chi ha la chiave giusta.', 'tolleranza': 'Il margine di differenza accettato prima di considerare un valore sbagliato.', 'pipeline': "Una catena di passaggi automatici, in cui l'uscita di uno è l'ingresso del successivo.", 'telemetria': 'Dati raccolti in automatico da un programma su come sta funzionando.', 'profilazione': "L'analisi di dove un programma spende tempo e risorse, per capire cosa lo rallenta.", 'agentico': 'Detto di un sistema AI che non si limita a rispondere ma compie azioni da solo, passo dopo passo.', 'distillazione': 'Insegnare a un modello piccolo a imitare un modello grande, per averne uno più leggero.', 'ottimizzazione': 'Il lavoro per far andare qualcosa più veloce o con meno risorse.', 'interfaccia': 'La parte di un programma con cui si interagisce: schermate, pulsanti, comandi.', 'classificatore': 'Un programma che mette ogni elemento nella categoria giusta, per esempio "fattura" o "contratto".', 'estrazione': 'Il recupero automatico di dati precisi da un documento, come importi o date.', 'conformità': 'Il rispetto di leggi, regole e standard.', 'trasparenza': 'Il dovere di spiegare in modo chiaro come funziona qualcosa e quali dati usa.', 'semiconduttori': 'I materiali (come il silicio) con cui si fanno i chip.'}

JS_TMPL = r"""<script id="kw-js">
/* Sapio, trova le parole chiave (tools/chiavi.py) */
(function(){
  var STOP={}; '__STOP__'.split(' ').forEach(function(w){STOP[w]=1});
  var OWL_S='__OWL_S__', OWL_L='__OWL_L__', OWL_F='__OWL_F__', OWL_C='__OWL_C__', OWL_P='__OWL_P__';
  var SKIP='.gl-tip,.kw-hd-tip,.sr-only,code,pre,.prompt,button,.kw,.kw-sum,.kw-step,.kw-quick,script,style,.src,.chip';
  var L='A-Za-zÀ-ÖØ-öø-ÿ', LD=L+'0-9';
  function esc(s){return s.replace(/[&<>"]/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]})}
  function rx(s){return s.replace(/[.*+?^${}()|[\]\\]/g,'\\$&')}
  function textOf(el){var c=el.cloneNode(true);c.querySelectorAll(SKIP).forEach(function(x){
      if(x.classList.contains('gl-btn')||x.classList.contains('kw-hd-b')){x.replaceWith(document.createTextNode(x.firstChild?x.firstChild.textContent:''));}else x.remove();});
    return c.textContent.replace(/\s+/g,' ').trim();}
  function zones(sec){return [].slice.call(sec.querySelectorAll('.ch-head .lead, .prose'));}
  function sentences(t){return t.split(/(?<=[.!?…])\s+(?=[«"“A-ZÀ-Ý0-9])/);}
  function stem(w){return w.length>=6?w.replace(/(i|e|a|o)$/,''):w;}
  function analyze(sec){
    var h2=sec.querySelector('.ch-head h2'), title=h2?h2.textContent:'', leadEl=sec.querySelector('.ch-head .lead'), lead=leadEl?textOf(leadEl):'';
    var body=zones(sec).map(textOf).join(' '), all=title+'. '+body, C={};
    function add(k,disp,w,kind){var o=C[k]||(C[k]={k:k,d:disp,s:0,kind:kind,forms:{}});o.s+=w;o.forms[disp]=(o.forms[disp]||0)+1;if(kind==='gl'||kind==='np')o.kind=o.kind==='gl'?'gl':kind;return o;}
    /* 1. glossario */
    sec.querySelectorAll('.prose .gl, .ch-head .gl').forEach(function(g){var b=g.querySelector('.gl-btn'),t=b&&b.firstChild?b.firstChild.textContent.trim():'';
      if(t){var o=add(t.toLowerCase(),t,4,'gl');o.gl=g.getAttribute('data-gl');var tip=g.querySelector('.gl-tip');if(tip&&!o.def){var c=tip.cloneNode(true);c.querySelectorAll('.gl-ex,.gl-act,b').forEach(function(x){x.remove()});o.def=c.textContent.replace(/^\s*\.\s*/,'').trim();}}});
    /* 2. nomi propri */
    var np=new RegExp('(?:^|[^'+LD+'])((?:[A-ZÀ-Ý]['+LD+'\\-]*|[0-9][0-9.,]*)(?:\\s(?:[A-ZÀ-Ý]['+LD+'\\-]*|[0-9][0-9.,]*|AI|AI\\.))*)','g');
    sentences(all).forEach(function(s){var m;np.lastIndex=0;
      while((m=np.exec(s))){var p=m[1].replace(/[.,]+$/,''),start=m.index+(m[0].length-m[1].length);
        if(/^[0-9.,\s]+$/.test(p))continue;
        var ws=p.split(' ');while(ws.length&&STOP[ws[0].toLowerCase()])ws.shift();if(!ws.length)continue;
        if(start===0&&ws.length===p.split(' ').length&&ws.length===1&&!/[A-Z].*[A-Z]|[0-9]/.test(ws[0].slice(1)))continue;
        p=ws.join(' ');if(p.length<2||/^[0-9.,\s]+$/.test(p))continue;add(p.toLowerCase(),p,1.5,'np');}});
    /* 3. parole che tornano */
    var wr=new RegExp('['+L+']{6,}','g'),F={},m2;var low=body;
    while((m2=wr.exec(low))){var w=m2[0];if(/^[A-ZÀ-Ý]/.test(w))continue;var lw=w.toLowerCase();if(STOP[lw]||/(mente|are|ere|ire|ano|ono|ava|avano|eva|evano|iamo|ete)$/.test(lw))continue;var st=stem(lw);(F[st]||(F[st]={n:0,f:{}})).n++;F[st].f[lw]=(F[st].f[lw]||0)+1;}
    Object.keys(F).forEach(function(st){if(F[st].n<3)return;var best=Object.keys(F[st].f).sort(function(a,b){return F[st].f[b]-F[st].f[a]})[0];var o=add(best,best,F[st].n*0.8,'w');o.stem=st;});
    /* occorrenze reali, titolo e introduzione */
    var list=Object.keys(C).map(function(k){var o=C[k];o.d=Object.keys(o.forms).sort(function(a,b){return o.forms[b]-o.forms[a]})[0];
      var re=new RegExp('(?<!['+LD+'])'+rx(o.stem||o.d)+(o.stem?'['+L+']{0,3}':'')+'(?!['+LD+'])','gi');o.re=re;
      o.n=(all.match(re)||[]).length;if(o.kind==='np')o.s=o.n*1.5;if(o.kind==='gl')o.s=4+o.n;
      if(o.kind==='np'&&o.d.indexOf(' ')<0&&!/[A-Z].*[A-Z]|[0-9]/.test(o.d.slice(1))){var mid=new RegExp('[a-zà-ÿ0-9,;)]\\s'+rx(o.d)+'(?!['+LD+'])','g');if(!(all.match(mid)||[]).length)o.n=0;}
      re.lastIndex=0;if(re.test(title))o.s+=4;re.lastIndex=0;if(re.test(lead))o.s+=2;re.lastIndex=0;return o;})
      .filter(function(o){return o.n>0&&(o.kind!=='np'||o.n>=2||o.s>=4)});
    /* doppioni */
    list.sort(function(a,b){return b.d.length-a.d.length});
    var keep=[];list.forEach(function(o){var host=keep.filter(function(h){return h.d.length>o.d.length&&new RegExp('(?<!['+LD+'])'+rx(o.d)+'(?!['+LD+'])','i').test(h.d)})[0];
      if(host&&o.kind!=='gl'){host.s+=o.s*0.5;if(host.kind==='np'&&o.kind==='np'){(host.al||(host.al=[])).push(o.d);}}else keep.push(o);});
    keep.forEach(function(o){if(!o.al)return;o.re=new RegExp('(?<!['+LD+'])(?:'+[o.d].concat(o.al).map(rx).join('|')+')(?!['+LD+'])','gi');o.n=(all.match(o.re)||[]).length;o.re.lastIndex=0;});
    keep.sort(function(a,b){return b.s-a.s||b.n-a.n});
    var out=keep.slice(0,8);
    out.forEach(function(o){o.ctx='';sentences(body).some(function(s){o.re.lastIndex=0;if(o.re.test(s)){o.ctx=s;return true}});o.re.lastIndex=0;});
    return {title:title,list:out};
  }
  function unmark(sec){sec.querySelectorAll('mark.kw-m').forEach(function(m){var p=m.parentNode;p.replaceChild(document.createTextNode(m.textContent),m);p.normalize();});}
  function markAll(sec,list){unmark(sec);
    zones(sec).forEach(function(z){var w=document.createTreeWalker(z,NodeFilter.SHOW_TEXT,{acceptNode:function(n){return n.parentElement.closest(SKIP)?NodeFilter.FILTER_REJECT:NodeFilter.FILTER_ACCEPT}}),nodes=[],n;
      while((n=w.nextNode()))nodes.push(n);
      nodes.forEach(function(t){var s=t.nodeValue,hits=[];
        list.forEach(function(o,i){o.re.lastIndex=0;var m;while((m=o.re.exec(s))){hits.push([m.index,m.index+m[0].length,i]);}o.re.lastIndex=0;});
        if(!hits.length)return;hits.sort(function(a,b){return a[0]-b[0]||(b[1]-b[0])-(a[1]-a[0])});
        var f=document.createDocumentFragment(),pos=0;
        hits.forEach(function(h){if(h[0]<pos)return;f.appendChild(document.createTextNode(s.slice(pos,h[0])));var mk=document.createElement('mark');mk.className='kw-m';mk.setAttribute('data-kw',h[2]);mk.textContent=s.slice(h[0],h[1]);f.appendChild(mk);pos=h[1];});
        f.appendChild(document.createTextNode(s.slice(pos)));t.parentNode.replaceChild(f,t);});});}
  function joinIt(a){return a.length<2?a.join(''):a.slice(0,-1).join(', ')+' e '+a[a.length-1];}
  /* Guida di lettura riga per riga (come la "messa a fuoco della riga" dei lettori immersivi) */
  var LF=null;
  function lineRects(sec){var raw=[],sy=window.scrollY;
    zones(sec).forEach(function(z){var w=document.createTreeWalker(z,NodeFilter.SHOW_TEXT,{acceptNode:function(n){return (!n.nodeValue.trim()||n.parentElement.closest('.gl-tip,.kw-hd-tip,.sr-only,.kw,.kw-sum,.kw-step,.kw-quick,script,style'))?NodeFilter.FILTER_REJECT:NodeFilter.FILTER_ACCEPT}}),n;
      while((n=w.nextNode())){var r=document.createRange();r.selectNodeContents(n);[].forEach.call(r.getClientRects(),function(c){if(c.width>0&&c.height>0)raw.push({t:c.top+sy,b:c.bottom+sy,z:z});});}});
    raw.sort(function(a,b){return a.t-b.t});var out=[];
    raw.forEach(function(c){var l=out[out.length-1];if(l&&c.t<l.b-Math.min(l.b-l.t,c.b-c.t)/2){l.t=Math.min(l.t,c.t);l.b=Math.max(l.b,c.b);}else out.push({t:c.t,b:c.b,z:c.z});});
    return out;}
  function lfEnd(){var L=LF.lines,j=LF.i;while(j<Math.min(LF.i+LF.n-1,L.length-1)&&L[j+1].t-L[j].b<2*(L[j].b-L[j].t))j++;return L[j];}
  function lfBranch(w){var h=20,y=8,m=w/2;
    return '<svg width="'+w+'" height="'+h+'" viewBox="0 0 '+w+' '+h+'" focusable="false">'+
      '<path d="M6 '+y+' Q'+(w*.25)+' '+(y-3)+' '+m+' '+y+' T'+(w-6)+' '+(y-1)+'" fill="none" stroke="#3A2618" stroke-width="6" stroke-linecap="round"/>'+
      '<path d="M6 '+y+' Q'+(w*.25)+' '+(y-3)+' '+m+' '+y+' T'+(w-6)+' '+(y-1)+'" fill="none" stroke="#7A5230" stroke-width="3.6" stroke-linecap="round"/>'+
      '<path d="M'+(m+18)+' '+(y+1)+' q6 4 12 5" fill="none" stroke="#3A2618" stroke-width="2" stroke-linecap="round"/>'+
      '<path d="M'+(m+30)+' '+(y+6)+' q9 -5 15 2 q-8 5 -15 -2 z" fill="#5E9E4B" stroke="#3A2618" stroke-width="1"/>'+
      '<path d="M14 '+(y+1)+' q-8 9 -12 10 q0 -9 12 -10 z" fill="#5E9E4B" stroke="#3A2618" stroke-width="1"/>'+
      '<path d="M'+(w-14)+' '+(y-1)+' q4 -8 12 -7 q-3 8 -12 7 z" fill="#5E9E4B" stroke="#3A2618" stroke-width="1"/></svg>';}
  function lfDraw(){if(!LF)return;var L=LF.lines;if(!L.length)return;var a=L[LF.i],z=lfEnd(),pad=6,sy=window.scrollY;
    var top=a.t-pad-sy,bot=z.b+pad+8-sy;LF.up.style.top='0';LF.up.style.height=Math.max(0,top)+'px';LF.dn.style.top=Math.max(0,bot)+'px';LF.dn.style.bottom='0';
    var zr=a.z.getBoundingClientRect(),h=Math.max(0,bot-top)+'px';LF.lt.style.top=LF.rt.style.top=top+'px';LF.lt.style.height=LF.rt.style.height=h;LF.lt.style.left='0';LF.lt.style.right='auto';LF.lt.style.width=Math.max(0,zr.left-12)+'px';LF.rt.style.left=(zr.right+12)+'px';
    var bw=Math.round(zr.width+16);if(LF.bw!==bw){LF.bw=bw;LF.br.innerHTML=lfBranch(bw);}LF.br.style.left=(zr.left-8)+'px';LF.br.style.top=(bot-12)+'px';}
  function lfAnchor(){return window.innerHeight*.35;}
  function lfShow(){var L=LF.lines;if(!L.length)return;var a=L[LF.i],z=lfEnd(),vh=window.innerHeight,sy=window.scrollY;
    if(LF.sc){LF.lock=1;window.scrollTo({top:Math.max(0,a.t-lfAnchor()),behavior:matchMedia('(prefers-reduced-motion: reduce)').matches?'auto':'smooth'});clearTimeout(LF.lt0);LF.lt0=setTimeout(function(){if(LF)LF.lock=0},600);lfDraw();return;}
    if(a.t-sy<vh*.18||z.b-sy>vh*.68)window.scrollTo({top:Math.max(0,a.t-vh*.32),behavior:matchMedia('(prefers-reduced-motion: reduce)').matches?'auto':'smooth'});lfDraw();}
  function lfSay(){LF.live.textContent='Riga '+(LF.i+1)+' di '+LF.lines.length;}
  function lfMove(d){LF.i=Math.max(0,Math.min(LF.lines.length-1,LF.i+d));lfShow();lfSay();}
  function lfAt(y){var L=LF.lines,best=0;for(var k=0;k<L.length;k++){if(L[k].t<=y)best=k;else break;}return best;}
  function lfStop(back){if(!LF)return;var o=LF;LF=null;o.up.remove();o.dn.remove();o.lt.remove();o.rt.remove();o.br.remove();o.bar.remove();
    window.removeEventListener('scroll',o.onScroll);window.removeEventListener('resize',o.onResize);document.removeEventListener('keydown',o.onKey,true);document.removeEventListener('click',o.onClick,true);
    o.btn.setAttribute('aria-pressed','false');if(back)o.btn.focus();if(o.done)o.done();}
  function lfStart(sec,btn,startY,done){lfStop(false);
    var up=document.createElement('div'),dn=document.createElement('div'),lt=document.createElement('div'),rt=document.createElement('div'),br=document.createElement('div'),bar=document.createElement('div');
    [up,dn,lt,rt].forEach(function(m){m.className='kw-mask';m.setAttribute('aria-hidden','true');document.body.appendChild(m);});
    bar.className='kw-lf';bar.setAttribute('role','toolbar');bar.setAttribute('aria-label','Guida di lettura');
    bar.innerHTML='<button type="button" class="kw-tool" data-m="-1">↑ Riga su</button><button type="button" class="kw-tool" data-m="1">↓ Riga giù</button><button type="button" class="kw-tool" data-m="n">Righe visibili: 3</button><button type="button" class="kw-tool" data-m="x">Esci</button><span class="sr-only" aria-live="polite"></span>';
    br.className='kw-branch';br.setAttribute('aria-hidden','true');document.body.appendChild(br);document.body.appendChild(bar);
    LF={sc:matchMedia('(hover: none) and (pointer: coarse)').matches,lock:0,sec:sec,btn:btn,up:up,dn:dn,lt:lt,rt:rt,br:br,bar:bar,live:bar.querySelector('[aria-live]'),n:3,i:0,lines:lineRects(sec),done:done};
    var raf=0;LF.onScroll=function(){if(!raf)raf=requestAnimationFrame(function(){raf=0;if(!LF)return;if(LF.sc&&!LF.lock)LF.i=lfAt(window.scrollY+lfAnchor()+4);lfDraw()})};
    LF.onResize=function(){if(!LF)return;var y=LF.lines[LF.i]?LF.lines[LF.i].t:0,ratio=y/Math.max(1,document.documentElement.scrollHeight);LF.lines=lineRects(sec);LF.i=lfAt(ratio*document.documentElement.scrollHeight);lfDraw();};
    LF.onKey=function(e){if(!LF)return;var t=e.target,tag=t&&t.tagName;if(e.altKey||e.ctrlKey||e.metaKey||/INPUT|TEXTAREA|SELECT/.test(tag)||(t&&t.isContentEditable))return;
      if(e.key==='ArrowDown'){e.preventDefault();lfMove(1);}else if(e.key==='ArrowUp'){e.preventDefault();lfMove(-1);}else if(e.key==='Escape'){e.preventDefault();e.stopPropagation();lfStop(true);}};
    LF.onClick=function(e){if(!LF||bar.contains(e.target))return;var z=e.target.closest&&e.target.closest('.prose,.ch-head .lead');if(z&&sec.contains(z)&&!e.target.closest('a,button')){LF.i=lfAt(e.pageY+6);if(LF.sc){lfShow();}else lfDraw();lfSay();}};
    bar.addEventListener('click',function(e){var b=e.target.closest('button');if(!b)return;var m=b.getAttribute('data-m');
      if(m==='x'){lfStop(true);return;}
      if(m==='n'){LF.n=LF.n===1?3:LF.n===3?5:1;b.textContent='Righe visibili: '+LF.n;lfShow();return;}
      lfMove(+m);});
    window.addEventListener('scroll',LF.onScroll,{passive:true});window.addEventListener('resize',LF.onResize);document.addEventListener('keydown',LF.onKey,true);document.addEventListener('click',LF.onClick,true);
    LF.i=lfAt(startY);if(LF.sc){var hb=bar.querySelectorAll('[data-m="-1"],[data-m="1"]');[].forEach.call(hb,function(x){x.remove()});var hint=document.createElement('span');hint.className='kw-lf-hint';hint.textContent='Scorri con il dito: la finestra avanza da sola';bar.insertBefore(hint,bar.firstChild);}btn.setAttribute('aria-pressed','true');lfShow();lfSay();bar.querySelector('button').focus({preventScroll:true});}
  /* ---------- Testo più comodo (preferenze condivise "radar-read") ---------- */
  var RP={size:0,sp:0,font:0,bg:0,fr:0,tp:0,pl:0,pz:1},fontOn=false,RK=['size','sp','font','bg','fr','tp','pl','pz'];
  function rpLoad(){try{var o=JSON.parse(localStorage.getItem('radar-read')||'{}');RK.forEach(function(k){if(o[k]!=null)RP[k]=+o[k]||0})}catch(e){}}
  function rpSave(){try{var o=JSON.parse(localStorage.getItem('radar-read')||'{}');RK.forEach(function(k){o[k]=RP[k]});localStorage.setItem('radar-read',JSON.stringify(o))}catch(e){}}
  function rpApply(){var H=document.documentElement;H.classList.toggle('rt-s1',RP.size===1);H.classList.toggle('rt-s2',RP.size===2);H.classList.toggle('rt-sp',!!RP.sp);H.classList.toggle('rt-font',!!RP.font);[1,2,3].forEach(function(i){H.classList.toggle('rt-bg'+i,RP.bg===i)});H.classList.toggle('rt-pl',!!RP.pl);if(RP.fr)frOn();H.classList.toggle('rt-fr',!!RP.fr);if(started)stepsAll();
    if(RP.font&&!fontOn){fontOn=true;var l=document.createElement('link');l.rel='stylesheet';l.href='https://fonts.googleapis.com/css2?family=Atkinson+Hyperlegible:wght@400;700&display=swap';document.head.appendChild(l)}
    if(LF){LF.lines=lineRects(LF.sec);LF.i=Math.min(LF.i,LF.lines.length-1);lfDraw();}}
  var started=false;
  function rpBox(id,ht){return '<div class="kw-rd" id="'+id+'" role="region" aria-label="Testo più comodo: '+esc(ht)+'" hidden>'+
    '<fieldset><legend>Grandezza del testo</legend><div class="kw-opts">'+['Normale','Grande','Molto grande'].map(function(t,i){return '<label><input type="radio" name="'+id+'-s" value="'+i+'"> '+t+'</label>'}).join('')+'</div></fieldset>'+
    '<fieldset><legend>Colore dello sfondo (tema chiaro)</legend><div class="kw-opts">'+[['Normale','#F6F6F5'],['Crema','#FBF4E4'],['Azzurro','#EAF2F8'],['Verde chiaro','#EDF5E6']].map(function(t,i){return '<label><input type="radio" name="'+id+'-b" value="'+i+'"> <span class="kw-sw" style="background:'+t[1]+'" aria-hidden="true"></span>'+t[0]+'</label>'}).join('')+'</div></fieldset>'+
    '<fieldset><legend>Leggibilità</legend><div class="kw-opts"><label><input type="checkbox" data-k="sp"> Più spazio tra righe e lettere</label><label><input type="checkbox" data-k="font"> Carattere ad alta leggibilità</label><label><input type="checkbox" data-k="fr"> Una frase per riga</label></div></fieldset>'+
    '<fieldset><legend>Concentrazione</legend><div class="kw-opts"><label><input type="checkbox" data-k="tp"> Leggi a tappe</label><label><input type="checkbox" data-k="pl"> Solo testo: nascondi riquadri e animazioni</label><label><input type="checkbox" data-k="pz"> Ricordami una pausa ogni 15 minuti</label></div></fieldset>'+
    '<p class="kw-hint">Vale per tutte le pagine di Sapit e resta salvato in questo browser.</p></div>';}
  function rpSync(box){box.querySelectorAll('input[type=radio]').forEach(function(r){r.checked=+r.value===(/-b$/.test(r.name)?RP.bg:RP.size)});box.querySelectorAll('input[data-k]').forEach(function(c){c.checked=!!RP[c.getAttribute('data-k')]});}
  /* ---------- Leggimi: voce del browser, frase per frase, con la frase colorata ---------- */
  var TT=null,HL=!!(window.CSS&&CSS.highlights&&window.Highlight);
  function ttsUnits(sec){var out=[];
    zones(sec).forEach(function(z){var blocks=z.matches('.lead')?[z]:[].slice.call(z.querySelectorAll(':scope>p,:scope>h3,:scope>h4,:scope>blockquote,:scope>ul>li,:scope>ol>li'));
      blocks=blocks.filter(function(b){return b.getClientRects().length>0});
      blocks.forEach(function(b){var map=[],txt='',w=document.createTreeWalker(b,NodeFilter.SHOW_TEXT,{acceptNode:function(n){var p=n.parentElement;if(p.closest('.gl-tip,.kw-hd-tip,.sr-only,script,style,.kw,.kw-hide'))return NodeFilter.FILTER_REJECT;var bt=p.closest('button');if(bt&&!((bt.classList.contains('gl-btn')||bt.classList.contains('kw-hd-b'))&&bt.firstChild===n))return NodeFilter.FILTER_REJECT;return NodeFilter.FILTER_ACCEPT}}),n;
        while((n=w.nextNode())){map.push([txt.length,n]);txt+=n.nodeValue;}
        if(!txt.trim())return;
        function at(i){for(var k=map.length-1;k>=0;k--){if(map[k][0]<=i)return [map[k][1],Math.min(i-map[k][0],map[k][1].nodeValue.length)];}return [map[0][1],0];}
        var re=/[^.!?…]+(?:[.!?…]+["»”’)]*|$)/g,m;
        while((m=re.exec(txt))){var raw=m[0];if(!raw)break;var lead=raw.length-raw.replace(/^\s+/,'').length,t=raw.trim();if(!/[A-Za-zÀ-ÿ0-9]/.test(t))continue;
          /* non spezzare dopo numeri e sigle (1.200, ecc., p.es.) */
          if(out.length&&out[out.length-1].el===b&&(lead===0||/(?:\b(?:ecc|ad|es|cfr|pag|ca|vs|sig|dott|p)|\b[A-Z])[.]$/i.test(out[out.length-1].t))){var pv=out[out.length-1];pv.t=txt.slice(pv.si,m.index+raw.length).trim();pv.e=at(m.index+raw.length);continue;}
          out.push({el:b,t:t,si:m.index+lead,s:at(m.index+lead),e:at(m.index+raw.length)});}});});
    return out;}
  function ttsMark(u){if(HL){try{var r=document.createRange();r.setStart(u.s[0],u.s[1]);r.setEnd(u.e[0],u.e[1]);CSS.highlights.set('kw-now',new Highlight(r));}catch(e){}}
    document.querySelectorAll('.kw-now-p').forEach(function(x){x.classList.remove('kw-now-p')});if(!HL)u.el.classList.add('kw-now-p');
    var rc;try{var r2=document.createRange();r2.setStart(u.s[0],u.s[1]);r2.setEnd(u.s[0],u.s[1]);rc=r2.getBoundingClientRect();}catch(e){}if(!rc||!rc.height)rc=u.el.getBoundingClientRect();
    var vh=innerHeight;if(rc.top<vh*.18||rc.bottom>vh*.62)window.scrollTo({top:Math.max(0,rc.top+scrollY-vh*.3),behavior:matchMedia('(prefers-reduced-motion: reduce)').matches?'auto':'smooth'});
    if(LF&&LF.sec===TT.sec){LF.i=lfAt(rc.top+scrollY+2);lfDraw();}}
  function ttsClear(){if(HL)try{CSS.highlights.delete('kw-now')}catch(e){}document.querySelectorAll('.kw-now-p').forEach(function(x){x.classList.remove('kw-now-p')});}
  function ttsVoice(){var v=speechSynthesis.getVoices().filter(function(v){return /^it/i.test(v.lang)});return v.filter(function(x){return /natural|neural|premium|enhanced|alice|elsa|isabella/i.test(x.name)})[0]||v[0]||null;}
  function ttsSpeak(){if(!TT)return;var u=TT.U[TT.i];if(!u){ttsStop(false);return;}ttsMark(u);TT.st.textContent='Frase '+(TT.i+1)+' di '+TT.U.length;
    var my=++TT.tok,ut=new SpeechSynthesisUtterance(u.t);ut.lang='it-IT';ut.rate=TT.rate;var v=ttsVoice();if(v)ut.voice=v;
    ut.onend=function(){if(TT&&TT.tok===my&&TT.play){TT.i++;ttsSpeak();}};ut.onerror=function(){};speechSynthesis.speak(ut);}
  function ttsPlay(on){TT.play=on;TT.pb.textContent=on?'⏸ Pausa':'▶ Riprendi';TT.pb.setAttribute('aria-pressed',on?'false':'true');TT.tok++;try{speechSynthesis.cancel()}catch(e){}if(on)setTimeout(ttsSpeak,60);}
  function ttsStop(back){if(!TT)return;var o=TT;TT=null;o.tok++;try{speechSynthesis.cancel()}catch(e){}ttsClear();o.bar.remove();if(LF)LF.bar.style.bottom='';o.btn.setAttribute('aria-pressed','false');document.removeEventListener('keydown',o.onKey,true);if(back)o.btn.focus();}
  function ttsStart(sec,btn){ttsStop(false);var U=ttsUnits(sec);if(!U.length)return;
    var bar=document.createElement('div');bar.className='kw-tts';bar.setAttribute('role','toolbar');bar.setAttribute('aria-label','Leggimi il capitolo');
    bar.innerHTML='<span class="kw-tts-st" aria-hidden="true"></span><button type="button" class="kw-tool kw-ic" data-a="prev" aria-label="Frase prima" title="Frase prima">⏮</button><button type="button" class="kw-tool" data-a="play">⏸ Pausa</button><button type="button" class="kw-tool kw-ic" data-a="next" aria-label="Frase dopo" title="Frase dopo">⏭</button><button type="button" class="kw-tool" data-a="rate" aria-label="Velocità: normale">Normale</button><button type="button" class="kw-tool" data-a="stop">Stop</button>';
    if(LF)LF.bar.style.bottom='calc(max(12px,env(safe-area-inset-bottom)) + 7.5rem)';
    document.body.appendChild(bar);
    /* parte dalla frase in vista, se il capitolo è già sullo schermo */
    var i0=0,y=innerHeight*.15;for(var k=0;k<U.length;k++){var rc=U[k].el.getBoundingClientRect();if(rc.bottom>y){i0=k;break;}}
    TT={sec:sec,btn:btn,bar:bar,U:U,i:i0,rate:.95,play:true,tok:0,st:bar.querySelector('.kw-tts-st'),pb:bar.querySelector('[data-a=play]')};
    btn.setAttribute('aria-pressed','true');
    TT.onKey=function(e){if(TT&&e.key==='Escape'&&bar.contains(document.activeElement)){e.preventDefault();ttsStop(true);}};document.addEventListener('keydown',TT.onKey,true);
    bar.addEventListener('click',function(e){var b=e.target.closest('button');if(!b||!TT)return;var a=b.getAttribute('data-a');
      if(a==='stop'){ttsStop(true);return;}
      if(a==='play'){ttsPlay(!TT.play);return;}
      if(a==='prev'||a==='next'){TT.i=Math.max(0,Math.min(TT.U.length-1,TT.i+(a==='next'?1:-1)));if(TT.play)ttsPlay(true);else{ttsMark(TT.U[TT.i]);TT.st.textContent='Frase '+(TT.i+1)+' di '+TT.U.length;}return;}
      if(a==='rate'){var R=[[.95,'normale'],[.8,'lenta'],[1.1,'veloce']],j=0;for(var q=0;q<R.length;q++)if(R[q][0]===TT.rate)j=q;j=(j+1)%R.length;TT.rate=R[j][0];b.textContent=R[j][1].charAt(0).toUpperCase()+R[j][1].slice(1);b.setAttribute('aria-label','Velocità: '+R[j][1]);if(TT.play)ttsPlay(true);}});
    bar.querySelector('[data-a=play]').focus({preventScroll:true});ttsSpeak();}
  /* ---------- Segnalibro: ricorda il capitolo e il punto, e propone di riprendere ---------- */
  function markKey(){return 'radar-segno:'+location.pathname.replace(/.*\//,'');}
  function markSave(){var secs=document.querySelectorAll('section.ch[id]'),y=innerHeight*.3,cur=null;secs.forEach(function(s){var r=s.getBoundingClientRect();if(r.top<=y&&r.bottom>y)cur=s;});
    try{if(!cur||scrollY<innerHeight){return;}var r=cur.getBoundingClientRect();localStorage.setItem(markKey(),JSON.stringify({id:cur.id,f:Math.max(0,Math.min(1,(y-r.top)/Math.max(1,r.height))),t:Date.now()}));}catch(e){}}
  function markOffer(){var o=null;try{o=JSON.parse(localStorage.getItem(markKey())||'null')}catch(e){}
    if(!o||!o.id||location.hash||Date.now()-o.t>30*864e5)return;var sec=document.getElementById(o.id);if(!sec)return;
    var h=sec.querySelector('h2'),box=document.createElement('div');box.className='kw-mark';box.setAttribute('role','region');box.setAttribute('aria-label','Segnalibro');
    box.innerHTML=OWL_S+'<p>Riprendi da dove eri rimasto? <span style="font-weight:400">'+esc(function(t){t=t.split(':')[0];return t.length>48?t.slice(0,46)+'…':t}(h?h.textContent:''))+'</span></p><button type="button" class="kw-tool pri" data-g="1">Riprendi</button><button type="button" class="kw-tool" data-g="0">No, grazie</button>';
    document.body.appendChild(box);
    box.addEventListener('click',function(e){var b=e.target.closest('button');if(!b)return;box.remove();
      if(b.getAttribute('data-g')==='1'){if(sec._steps){sec._steps.n=sec._steps.g.length;stepsDraw(sec);}var r=sec.getBoundingClientRect();window.scrollTo({top:Math.max(0,r.top+scrollY+o.f*r.height-innerHeight*.3),behavior:'auto'});var t=h||sec;t.setAttribute('tabindex','-1');try{t.focus({preventScroll:true})}catch(x){}}
      else{try{localStorage.removeItem(markKey())}catch(x){}}});
    setTimeout(function(){if(box.isConnected&&!box.contains(document.activeElement))box.remove();},20000);}
  var mt=0;window.addEventListener('scroll',function(){clearTimeout(mt);mt=setTimeout(markSave,700)},{passive:true});
  /* ---------- Una frase per riga: piccoli a capo dopo ogni frase (e dopo ";") ---------- */
  var frDone=false;
  function frOn(){if(frDone)return;frDone=true;
    document.querySelectorAll('section.ch .prose>p, section.ch .ch-head .lead').forEach(function(b){var w=document.createTreeWalker(b,NodeFilter.SHOW_TEXT,{acceptNode:function(n){return n.parentElement.closest('button,.gl-tip,.kw-hd-tip,.sr-only,a')?NodeFilter.FILTER_REJECT:NodeFilter.FILTER_ACCEPT}}),nodes=[],n;
      while((n=w.nextNode()))nodes.push(n);
      nodes.forEach(function(t){var re=/([.!?…;]["»”’)]*)\s+(?=[«"“A-ZÀ-Ý0-9a-zà-ÿ])/g,m,cuts=[];var v=t.nodeValue;
        while((m=re.exec(v))){if(m[1]==='.'&&/(?:\b(?:ecc|es|cfr|pag|vs|dott|p)|\b[A-Z]|\d)$/i.test(v.slice(0,m.index)))continue;if(m[1]!==';'&&!/^\s*[«"“A-ZÀ-Ý0-9]/.test(v.slice(m.index+m[0].length-1)))continue;cuts.push(m.index+m[1].length);}
        for(var k=cuts.length-1;k>=0;k--){var r=t.splitText(cuts[k]);var sp=document.createElement('span');sp.className='kw-br';sp.setAttribute('aria-hidden','true');t.parentNode.insertBefore(sp,r);}});});}
  /* ---------- Parole difficili: prima comparsa nel capitolo, se non c'è già nel glossario ---------- */
  var HARD=__HARD__,hid=0;
  function hardWords(sec){var gl={};sec.querySelectorAll('.gl-btn').forEach(function(b){gl[(b.firstChild?b.firstChild.textContent:'').trim().toLowerCase()]=1});
    var keys=Object.keys(HARD).filter(function(k){return !gl[k.toLowerCase()]}).sort(function(a,b){return b.length-a.length});if(!keys.length)return;
    var re=new RegExp('(?<!['+LD+'])('+keys.map(rx).join('|')+')(?!['+LD+'])','i'),used={};
    zones(sec).forEach(function(z){var w=document.createTreeWalker(z,NodeFilter.SHOW_TEXT,{acceptNode:function(n){return n.parentElement.closest(SKIP+',a,mark,.gl,h3,h4,summary,label,details:not([open])')?NodeFilter.FILTER_REJECT:NodeFilter.FILTER_ACCEPT}}),nodes=[],n;
      while((n=w.nextNode()))nodes.push(n);
      nodes.forEach(function(t){var m=re.exec(t.nodeValue);if(!m)return;var key=Object.keys(HARD).filter(function(k){return k.toLowerCase()===m[1].toLowerCase()})[0];if(!key||used[HARD[key]])return;used[HARD[key]]=1;
        var mid=t.splitText(m.index);mid.splitText(m[1].length);var id='kwhd-'+(++hid);
        var span=document.createElement('span');span.className='kw-hd';
        span.innerHTML='<button type="button" class="kw-hd-b" aria-expanded="false" aria-controls="'+id+'">'+esc(mid.nodeValue)+'<span class="sr-only">: che cosa vuol dire</span></button><span class="kw-hd-tip" id="'+id+'" role="note" hidden><b>'+esc(mid.nodeValue)+'</b>: '+esc(HARD[key])+'</span>';
        mid.parentNode.replaceChild(span,mid);});});}
  document.addEventListener('click',function(e){var b=e.target.closest&&e.target.closest('.kw-hd-b');if(!b)return;var t=document.getElementById(b.getAttribute('aria-controls'));var o=t.hidden;if(o){var bl=b.closest('p,li,.lead,h3,h4')||b.parentNode;bl.after(t);}t.hidden=!o;b.setAttribute('aria-expanded',o?'true':'false');if(LF){LF.lines=lineRects(LF.sec);lfDraw();}});
  document.addEventListener('keydown',function(e){if(e.key!=='Escape')return;var b=e.target.closest&&e.target.closest('.kw-hd-b');if(b&&b.getAttribute('aria-expanded')==='true'){b.click();e.stopPropagation();}});
  /* ---------- In breve (3 frasi più ricche di parole chiave) e mappa del capitolo ---------- */
  function summary(sec,data,head){var body=sec.querySelectorAll('.prose>p');if(!body.length||!data.list.length)return;
    var S=[];[].forEach.call(body,function(p,pi){sentences(textOf(p)).forEach(function(t,si){if(t.length<40||t.length>280)return;var sc=0;data.list.forEach(function(o){o.re.lastIndex=0;if(o.re.test(t))sc+=o.s;o.re.lastIndex=0;});S.push({t:t,sc:sc/Math.sqrt(t.length/80),o:pi*100+si});});});
    var top=S.sort(function(a,b){return b.sc-a.sc}).slice(0,3).sort(function(a,b){return a.o-b.o});
    var h3=[].slice.call(sec.querySelectorAll('.prose>h3'));
    var html='';
    if(top.length>=2)html+='<details class="kw-sum"><summary><span aria-hidden="true">📌</span> In breve: '+top.length+' punti</summary><div><ul>'+top.map(function(x){return '<li>'+esc(x.t)+'</li>'}).join('')+'</ul></div></details>';
    if(h3.length>=2)html+='<details class="kw-sum"><summary><span aria-hidden="true">🗺</span> Mappa del capitolo: '+h3.length+' parti</summary><div><ol class="kw-map">'+h3.map(function(h,i){if(!h.id)h.id=sec.id+'-p'+(i+1);var p=h.nextElementSibling,f=p&&p.tagName==='P'?sentences(textOf(p))[0]||'':'';if(f.length>120)f=f.slice(0,118)+'…';return '<li><a href="#'+h.id+'"><b>'+(i+1)+'. '+esc(h.textContent)+'</b><span>'+esc(f)+'</span></a></li>'}).join('')+'</ol></div></details>';
    if(html){var d=document.createElement('div');d.innerHTML=html;while(d.firstChild)head.appendChild(d.firstChild);}
    head.querySelectorAll('.kw-map a').forEach(function(a){a.addEventListener('click',function(){var t=document.getElementById(a.getAttribute('href').slice(1));if(t&&t.classList.contains('kw-hide'))stepsReveal(sec,t);});});}
  /* ---------- Tempo per capitolo ---------- */
  var WPM=180;
  function timeChip(sec){var k=sec.querySelector('.ch-head .kicker');if(!k)return;var words=zones(sec).map(textOf).join(' ').split(/\s+/).length,min=Math.max(1,Math.round(words/WPM));
    var c=document.createElement('span');c.className='chip kw-time';c.textContent='⏱ circa '+min+' min';c.setAttribute('data-min',min);k.appendChild(c);sec._time=c;}
  function timeTick(){document.querySelectorAll('section.ch').forEach(function(sec){var c=sec._time;if(!c)return;var pr=sec.querySelector('.prose');if(!pr)return;var r=pr.getBoundingClientRect(),min=+c.getAttribute('data-min'),y=innerHeight*.5;
    var f=(y-r.top)/Math.max(1,r.height),txt;if(f<=0.02)txt='⏱ circa '+min+' min';else if(f>=0.98)txt='✓ letto';else txt='⏱ ancora '+Math.max(1,Math.round(min*(1-f)))+' min';if(c.textContent!==txt)c.textContent=txt;});}
  var tt0=0;window.addEventListener('scroll',function(){if(!tt0)tt0=requestAnimationFrame(function(){tt0=0;timeTick()})},{passive:true});
  /* ---------- Leggi a tappe: due parti per volta, poi "Continua" ---------- */
  function stepsBuild(sec){var pr=sec.querySelector('.prose');if(!pr||sec._steps)return;var kids=[].slice.call(pr.children).filter(function(x){return !x.classList.contains('kw-step')}),groups=[],cur=null,nh=0,tail=[],seenH=false;
    kids.forEach(function(x){var txt=/^(H3|H4|P|UL|OL|BLOCKQUOTE)$/.test(x.tagName);
      if(tail.length||(seenH&&!txt)){tail.push(x);return;}
      if(x.tagName==='H3'){seenH=true;if(!cur||nh>=2){cur=[];groups.push(cur);nh=0;}nh++;}else if(!cur){cur=[];groups.push(cur);}
      cur.push(x);});
    if(tail.length)groups.push(tail);if(groups.length<2)return;sec._steps={g:groups,n:1};}
  function stepsDraw(sec){var st=sec._steps;if(!st)return;var pr=sec.querySelector('.prose'),old=pr.querySelector('.kw-step');if(old)old.remove();
    st.g.forEach(function(g,i){g.forEach(function(x){x.classList.toggle('kw-hide',i>=st.n)})});
    if(st.n<st.g.length){var last=st.g[st.n-1],after=last[last.length-1],box=document.createElement('div');box.className='kw-step';
      box.innerHTML='<span class="kw-leaves" aria-hidden="true">'+st.g.map(function(_,i){return '<i class="kw-leaf'+(i<st.n?' on':'')+'"></i>'}).join('')+'</span><span>Tappa '+st.n+' di '+st.g.length+'</span><button type="button" class="kw-tool">Continua: tappa '+(st.n+1)+'</button>';
      after.after(box);box.querySelector('button').addEventListener('click',function(){st.n++;stepsDraw(sec);var f=st.g[st.n-1][0];if(f){f.setAttribute('tabindex','-1');try{f.focus({preventScroll:true})}catch(x){}f.scrollIntoView({block:'start',behavior:matchMedia('(prefers-reduced-motion: reduce)').matches?'auto':'smooth'});}});}
    if(LF&&LF.sec===sec){LF.lines=lineRects(sec);lfDraw();}}
  function stepsReveal(sec,el){var st=sec._steps;if(!st)return;st.g.forEach(function(g,i){if(g.indexOf(el)>=0)st.n=Math.max(st.n,i+1)});stepsDraw(sec);}
  function stepsAll(){document.querySelectorAll('section.ch').forEach(function(sec){if(RP.tp){stepsBuild(sec);stepsDraw(sec);}else if(sec._steps){sec._steps.g.forEach(function(g){g.forEach(function(x){x.classList.remove('kw-hide')})});var o=sec.querySelector('.kw-step');if(o)o.remove();sec._steps=null;}});}
  /* ---------- Domanda lampo: completa la frase con la parola chiave giusta ---------- */
  var ALLKW=[];
  function quick(sec,data){var pr=sec.querySelector('.prose');if(!pr)return;var c=data.list.filter(function(o){return o.ctx&&o.d.length>2&&o.kind!=='w'})[0]||data.list.filter(function(o){return o.ctx})[0];if(!c)return;
    var others=ALLKW.filter(function(d){return d.sec!==sec&&d.d.toLowerCase()!==c.d.toLowerCase()&&c.ctx.toLowerCase().indexOf(d.d.toLowerCase())<0});
    var seen={},wrong=[];others.forEach(function(d){var k=d.d.toLowerCase();if(!seen[k]&&wrong.length<2){seen[k]=1;wrong.push(d.d)}});if(wrong.length<2)return;
    c.re.lastIndex=0;var blank=esc(c.ctx).replace(new RegExp(c.re.source,'gi'),'<b>_____</b>');c.re.lastIndex=0;if(blank.indexOf('_____')<0)return;
    var opts=[c.d].concat(wrong),seed=sec.id.length;opts.sort(function(a,b){return ((a.length*7+seed)%5)-((b.length*7+seed)%5)||a.localeCompare(b)});
    var box=document.createElement('div');box.className='kw-quick';box.setAttribute('role','group');box.setAttribute('aria-label','Domanda lampo');
    box.innerHTML='<h3><span aria-hidden="true">⚡</span> Domanda lampo</h3><p style="margin:0">Quale parola completa la frase del capitolo?</p><blockquote>'+blank+'</blockquote><div class="kw-opts">'+opts.map(function(o){return '<button type="button" class="kw-tool">'+esc(o)+'</button>'}).join('')+'</div><p class="kw-qres" aria-live="polite"></p>';
    pr.appendChild(box);
    box.addEventListener('click',function(e){var b=e.target.closest('button');if(!b||box._done)return;box._done=1;var ok=b.textContent===c.d;
      box.querySelectorAll('button').forEach(function(x){x.setAttribute('aria-disabled','true');if(x.textContent===c.d)x.classList.add('ok');else if(x===b)x.classList.add('no');});
      box.querySelector('.kw-qres').innerHTML=(ok?OWL_F+'<span>Giusto! Hai seguito bene il capitolo.</span>':OWL_C+'<span>Quasi: la parola giusta è «'+esc(c.d)+'». La trovi nel testo con Sapio.</span>');});}
  /* ---------- Pausa gentile ---------- */
  var act=0,lastIn=Date.now();['scroll','keydown','pointerdown','touchstart'].forEach(function(ev){window.addEventListener(ev,function(){lastIn=Date.now()},{passive:true})});
  setInterval(function(){if(document.hidden||Date.now()-lastIn>90000||document.querySelector('.kw-pause'))return;act+=15;if(act>=900&&RP.pz){act=0;pauseOffer();}},15000);
  function pauseOffer(){if(document.querySelector('.kw-mark'))return;var box=document.createElement('div');box.className='kw-mark';box.setAttribute('role','region');box.setAttribute('aria-label','Pausa');
    box.innerHTML=OWL_S+'<p>Leggi da 15 minuti. Una pausa di un minuto?</p><button type="button" class="kw-tool pri" data-p="1">Pausa di 1 minuto</button><button type="button" class="kw-tool" data-p="0">Continuo a leggere</button>';
    document.body.appendChild(box);box.addEventListener('click',function(e){var b=e.target.closest('button');if(!b)return;box.remove();if(b.getAttribute('data-p')==='1')pauseRun();});
    setTimeout(function(){if(box.isConnected&&!box.contains(document.activeElement))box.remove();},30000);}
  function pauseRun(){var back=document.activeElement,ov=document.createElement('div');ov.className='kw-pause';
    ov.innerHTML='<div role="dialog" aria-modal="true" aria-labelledby="kwp-h">'+OWL_P+'<h2 id="kwp-h">Pausa con Sapio</h2><p style="margin:0">Guarda lontano dallo schermo e respira piano: dentro mentre il cerchio cresce, fuori mentre si stringe.</p><div class="kw-breath" aria-hidden="true">60</div><p class="sr-only" aria-live="polite"></p><button type="button" class="kw-tool">Riprendi a leggere</button></div>';
    document.body.appendChild(ov);try{speechSynthesis.cancel()}catch(e){}if(TT)ttsPlay(false);
    var n=60,c=ov.querySelector('.kw-breath'),sr=ov.querySelector('[aria-live]'),btn=ov.querySelector('button'),iv=setInterval(function(){n--;c.textContent=n;if(n===30)sr.textContent='Ancora 30 secondi.';if(n<=0){clearInterval(iv);c.textContent='✓';sr.textContent='Pausa finita: quando vuoi, riprendi a leggere.';}},1000);
    function close(){clearInterval(iv);ov.remove();act=0;if(back&&back.focus)try{back.focus({preventScroll:true})}catch(e){}}
    btn.addEventListener('click',close);ov.addEventListener('keydown',function(e){if(e.key==='Escape'){e.preventDefault();close();}if(e.key==='Tab'){e.preventDefault();btn.focus();}});btn.focus();}
  var uid=0;
  function build(sec){
    var head=sec.querySelector('.ch-head');if(!head||head.querySelector('.kw'))return;
    var id='kw-'+(++uid),h=head.querySelector('h2'),ht=h?h.textContent:'';
    var wrap=document.createElement('div');wrap.className='kw';
    var canSay='speechSynthesis' in window;
    wrap.innerHTML='<div class="kw-row"><button type="button" class="kw-btn" aria-expanded="false" aria-controls="'+id+'">'+OWL_S+'<span>Sapio, trova le parole chiave</span></button>'+
      (canSay?'<button type="button" class="kw-btn kw-say-btn" aria-pressed="false"><span aria-hidden="true">🔊</span> Leggimi il capitolo</button>':'')+
      '<button type="button" class="kw-btn kw-aa" aria-expanded="false" aria-controls="'+id+'-rd"><b aria-hidden="true">Aa</b> Testo più comodo</button></div>'+
      '<div class="kw-box" id="'+id+'" role="region" aria-label="Parole chiave del capitolo: '+esc(ht)+'" hidden></div>'+rpBox(id+'-rd',ht);
    head.appendChild(wrap);
    sec._head=head;
    var aa=wrap.querySelector('.kw-aa'),rd=wrap.querySelector('.kw-rd'),sb=wrap.querySelector('.kw-say-btn');
    aa.addEventListener('click',function(){var o=rd.hidden;rd.hidden=!o;aa.setAttribute('aria-expanded',o?'true':'false');if(o){rpSync(rd);var f=rd.querySelector('input:checked')||rd.querySelector('input');if(f)f.focus();}});
    rd.addEventListener('change',function(e){var t=e.target;if(t.type==='radio'){if(/-b$/.test(t.name))RP.bg=+t.value;else RP.size=+t.value;}else RP[t.getAttribute('data-k')]=t.checked?1:0;rpSave();rpApply();});
    rd.addEventListener('keydown',function(e){if(e.key==='Escape'){rd.hidden=true;aa.setAttribute('aria-expanded','false');aa.focus();e.stopPropagation();}});
    if(sb)sb.addEventListener('click',function(){if(TT&&TT.sec===sec){ttsStop(false);return;}ttsStart(sec,sb);});
    var btn=wrap.querySelector('.kw-btn'),box=wrap.querySelector('.kw-box'),data=sec._kw||null,sel=-1,showAll=false,focusMode=false;
    function render(){
      var L=data.list;if(!L.length){box.innerHTML='<div class="rd-row">'+OWL_L+'<p class="kw-say">In questo capitolo non ho trovato parole chiave chiare. Prova a leggere il titolo e l\'introduzione: sono il riassunto.</p></div>';return;}
      var top=L.slice(0,3).map(function(o){return '<b>'+esc(o.d)+'</b>'});
      box.innerHTML='<div class="rd-row">'+OWL_L+'<div><p class="kw-say">Questo capitolo parla soprattutto di '+joinIt(top)+'.</p><p class="kw-say" style="margin-top:.35rem">Ho trovato '+L.length+' parole chiave. Toccane una: la evidenzio nel testo e ti mostro la frase dove compare.</p></div></div>'+
        '<ul class="kw-list" aria-label="Parole chiave">'+L.map(function(o,i){return '<li><button type="button" class="kw-chip" data-i="'+i+'" aria-pressed="false">'+esc(o.d)+' <span class="kw-n" aria-hidden="true">×'+o.n+'</span><span class="sr-only">, '+o.n+(o.n===1?' volta':' volte')+'</span></button></li>'}).join('')+'</ul>'+
        '<div class="kw-ctx" aria-live="polite"></div>'+
        '<div class="kw-tools"><button type="button" class="kw-tool" data-t="all" aria-pressed="false">Evidenzia tutte nel testo</button>'+
        '<button type="button" class="kw-tool" data-t="focus" aria-pressed="false">Concentrati: leggi riga per riga</button>'+
        ('speechSynthesis' in window?'<button type="button" class="kw-tool" data-t="voice">Sapio, leggile ad alta voce</button>':'')+
        '<button type="button" class="kw-tool" data-t="close">Chiudi</button></div>';
    }
    function apply(){
      var L=data.list;if(showAll||sel>=0)markAll(sec,L);else unmark(sec);
      sec.querySelectorAll('mark.kw-m').forEach(function(m){var i=+m.getAttribute('data-kw');m.classList.toggle('on',i===sel);if(!showAll&&i!==sel){var p=m.parentNode;p.replaceChild(document.createTextNode(m.textContent),m);p.normalize();}});
      box.querySelectorAll('.kw-chip').forEach(function(c){c.setAttribute('aria-pressed',+c.getAttribute('data-i')===sel?'true':'false')});
      var ctx=box.querySelector('.kw-ctx');
      if(sel<0){ctx.innerHTML='';return;}
      var o=L[sel],s=esc(o.ctx);o.re.lastIndex=0;var hl=s.replace(new RegExp(o.re.source,'gi'),function(x){return '<mark class="kw-m on">'+x+'</mark>'});o.re.lastIndex=0;
      ctx.innerHTML='<div class="kw-card"><h4>'+esc(o.d)+'</h4>'+(o.def?'<p><span class="kw-lab">Che cos\'è</span><br>'+esc(o.def)+'</p>':'')+
        (o.ctx?'<p><span class="kw-lab">Nel testo</span><br>'+hl+'</p>':'')+
        '<p>Compare '+o.n+(o.n===1?' volta':' volte')+' in questo capitolo.'+(o.gl?' <a href="'+(document.querySelector('a.brand')?document.querySelector('a.brand').getAttribute('href'):'../')+'glossario.html#g-'+esc(o.gl)+'">Apri la voce del glossario</a>.':'')+'</p>'+
        '<div class="kw-tools" style="margin-top:.6rem"><button type="button" class="kw-tool" data-t="go">Portami al punto nel testo</button></div></div>';
    }
    function open(o){box.hidden=!o;btn.setAttribute('aria-expanded',o?'true':'false');
      if(o){if(!data){data=analyze(sec);render();}var f=box.querySelector('.kw-chip');if(f)f.focus();}
      else{if(LF&&LF.sec===sec)lfStop(false);sel=-1;showAll=false;focusMode=false;apply();try{speechSynthesis.cancel()}catch(e){}}}
    btn.addEventListener('click',function(){open(box.hidden)});
    box.addEventListener('click',function(e){var c=e.target.closest('.kw-chip');
      if(c){var i=+c.getAttribute('data-i');sel=sel===i?-1:i;apply();return;}
      var t=e.target.closest('.kw-tool');if(!t)return;var k=t.getAttribute('data-t');
      if(k==='close'){open(false);btn.focus();return;}
      if(k==='all'){showAll=!showAll;t.setAttribute('aria-pressed',showAll?'true':'false');apply();return;}
      if(k==='focus'){if(LF&&LF.sec===sec){lfStop(false);focusMode=false;return;}
        var mk=sel>=0?sec.querySelector('mark.kw-m.on:not(.kw-card mark)'):null,first=zones(sec)[0],y=mk?mk.getBoundingClientRect().top+window.scrollY+2:(first?Math.max(first.getBoundingClientRect().top,innerHeight*.15)+window.scrollY:0);
        focusMode=true;lfStart(sec,t,y,function(){focusMode=false});return;}
      if(k==='go'){var m=sec.querySelector('mark.kw-m.on:not(.kw-card mark)');if(m){m.setAttribute('tabindex','-1');try{m.focus({preventScroll:true})}catch(x){m.focus()}m.scrollIntoView({block:'center',behavior:matchMedia('(prefers-reduced-motion: reduce)').matches?'auto':'smooth'});}return;}
      if(k==='voice'){try{speechSynthesis.cancel();var L=data.list,txt='Ciao, sono Sapio. Le parole chiave di questo capitolo sono: '+L.map(function(o){return o.d}).join(', ')+'.';
        if(sel>=0&&L[sel].ctx)txt='Sapio ti legge la frase su '+L[sel].d+'. '+L[sel].ctx;
        var u=new SpeechSynthesisUtterance(txt);u.lang='it-IT';u.rate=.95;var v=speechSynthesis.getVoices().filter(function(v){return /^it/i.test(v.lang)})[0];if(v)u.voice=v;speechSynthesis.speak(u);}catch(x){}}
    });
    box.addEventListener('keydown',function(e){if(e.key==='Escape'){open(false);btn.focus();e.stopPropagation();}});
  }
  function start(){var secs=[];document.querySelectorAll('section.ch').forEach(function(sec){
    if(!sec.querySelector('.prose')||!sec.querySelector('.ch-head h2'))return;
    timeChip(sec);hardWords(sec);
    var n=zones(sec).map(textOf).join(' ').split(' ').length;if(n<250)return;build(sec);
    try{sec._kw=analyze(sec);sec._kw.list.forEach(function(o){if(o.kind!=='w')ALLKW.push({sec:sec,d:o.d})});secs.push(sec);}catch(e){}});
    secs.forEach(function(sec){try{summary(sec,sec._kw,sec._head);quick(sec,sec._kw);}catch(e){}});
    timeTick();}
  function boot(){rpLoad();rpApply();start();started=true;if(RP.tp)stepsAll();setTimeout(markOffer,600);}
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',boot);else boot();
})();
</script>"""


def js():
    return (JS_TMPL.replace('__STOP__', ' '.join(STOP))
            .replace('__OWL_S__', rada.svg('curiosa', 30).replace("'", "\\'"))
            .replace('__OWL_L__', rada.svg('spiega', 60).replace("'", "\\'"))
            .replace('__OWL_F__', rada.svg('felice', 34).replace("'", "\\'"))
            .replace('__OWL_C__', rada.svg('coraggio', 34).replace("'", "\\'"))
            .replace('__OWL_P__', rada.svg('ciao', 70).replace("'", "\\'"))
            .replace('__HARD__', json.dumps(HARD, ensure_ascii=False)))
