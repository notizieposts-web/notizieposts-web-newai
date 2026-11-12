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
import sys, os
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
.kw-dim .prose>*:not(:has(mark.kw-m.on)),.kw-dim .lead:not(:has(mark.kw-m.on)){color:var(--muted)}
.kw-dim .prose>p:has(mark.kw-m.on),.kw-dim .prose>li:has(mark.kw-m.on),.kw-dim .lead:has(mark.kw-m.on){color:var(--ink);box-shadow:-10px 0 0 -6px var(--violet-ink)}
@media (prefers-reduced-motion:no-preference){mark.kw-m.on{transition:outline-color .2s}}
@media (forced-colors:active){mark.kw-m{forced-color-adjust:none;background:Mark;color:MarkText}.kw-chip[aria-pressed="true"],.kw-tool[aria-pressed="true"]{border:3px solid Highlight}}
</style>"""

JS_TMPL = r"""<script id="kw-js">
/* Sapio, trova le parole chiave (tools/chiavi.py) */
(function(){
  var STOP={}; '__STOP__'.split(' ').forEach(function(w){STOP[w]=1});
  var OWL_S='__OWL_S__', OWL_L='__OWL_L__';
  var SKIP='.gl-tip,.sr-only,code,pre,.prompt,button,.kw,script,style,.src,.chip';
  var L='A-Za-zÀ-ÖØ-öø-ÿ', LD=L+'0-9';
  function esc(s){return s.replace(/[&<>"]/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]})}
  function rx(s){return s.replace(/[.*+?^${}()|[\]\\]/g,'\\$&')}
  function textOf(el){var c=el.cloneNode(true);c.querySelectorAll(SKIP).forEach(function(x){
      if(x.classList.contains('gl-btn')){x.replaceWith(document.createTextNode(x.firstChild?x.firstChild.textContent:''));}else x.remove();});
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
  var uid=0;
  function build(sec){
    var head=sec.querySelector('.ch-head');if(!head||head.querySelector('.kw'))return;
    var id='kw-'+(++uid),h=head.querySelector('h2'),ht=h?h.textContent:'';
    var wrap=document.createElement('div');wrap.className='kw';
    wrap.innerHTML='<button type="button" class="kw-btn" aria-expanded="false" aria-controls="'+id+'">'+OWL_S+'<span>Sapio, trova le parole chiave</span></button>'+
      '<div class="kw-box" id="'+id+'" role="region" aria-label="Parole chiave del capitolo: '+esc(ht)+'" hidden></div>';
    head.appendChild(wrap);
    var btn=wrap.querySelector('.kw-btn'),box=wrap.querySelector('.kw-box'),data=null,sel=-1,showAll=false,focusMode=false;
    function render(){
      var L=data.list;if(!L.length){box.innerHTML='<div class="rd-row">'+OWL_L+'<p class="kw-say">In questo capitolo non ho trovato parole chiave chiare. Prova a leggere il titolo e l\'introduzione: sono il riassunto.</p></div>';return;}
      var top=L.slice(0,3).map(function(o){return '<b>'+esc(o.d)+'</b>'});
      box.innerHTML='<div class="rd-row">'+OWL_L+'<div><p class="kw-say">Questo capitolo parla soprattutto di '+joinIt(top)+'.</p><p class="kw-say" style="margin-top:.35rem">Ho trovato '+L.length+' parole chiave. Toccane una: la evidenzio nel testo e ti mostro la frase dove compare.</p></div></div>'+
        '<ul class="kw-list" aria-label="Parole chiave">'+L.map(function(o,i){return '<li><button type="button" class="kw-chip" data-i="'+i+'" aria-pressed="false">'+esc(o.d)+' <span class="kw-n" aria-hidden="true">×'+o.n+'</span><span class="sr-only">, '+o.n+(o.n===1?' volta':' volte')+'</span></button></li>'}).join('')+'</ul>'+
        '<div class="kw-ctx" aria-live="polite"></div>'+
        '<div class="kw-tools"><button type="button" class="kw-tool" data-t="all" aria-pressed="false">Evidenzia tutte nel testo</button>'+
        '<button type="button" class="kw-tool" data-t="focus" aria-pressed="false">Concentrati: attenua il resto</button>'+
        ('speechSynthesis' in window?'<button type="button" class="kw-tool" data-t="voice">Sapio, leggile ad alta voce</button>':'')+
        '<button type="button" class="kw-tool" data-t="close">Chiudi</button></div>';
    }
    function apply(){
      var L=data.list;if(showAll||sel>=0)markAll(sec,L);else unmark(sec);
      sec.querySelectorAll('mark.kw-m').forEach(function(m){var i=+m.getAttribute('data-kw');m.classList.toggle('on',i===sel);if(!showAll&&i!==sel){var p=m.parentNode;p.replaceChild(document.createTextNode(m.textContent),m);p.normalize();}});
      sec.classList.toggle('kw-dim',focusMode&&sel>=0);
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
      else{sel=-1;showAll=false;focusMode=false;apply();try{speechSynthesis.cancel()}catch(e){}}}
    btn.addEventListener('click',function(){open(box.hidden)});
    box.addEventListener('click',function(e){var c=e.target.closest('.kw-chip');
      if(c){var i=+c.getAttribute('data-i');sel=sel===i?-1:i;apply();return;}
      var t=e.target.closest('.kw-tool');if(!t)return;var k=t.getAttribute('data-t');
      if(k==='close'){open(false);btn.focus();return;}
      if(k==='all'){showAll=!showAll;t.setAttribute('aria-pressed',showAll?'true':'false');apply();return;}
      if(k==='focus'){focusMode=!focusMode;t.setAttribute('aria-pressed',focusMode?'true':'false');if(focusMode&&sel<0)sel=0;apply();return;}
      if(k==='go'){var m=sec.querySelector('mark.kw-m.on:not(.kw-card mark)');if(m){m.setAttribute('tabindex','-1');try{m.focus({preventScroll:true})}catch(x){m.focus()}m.scrollIntoView({block:'center',behavior:matchMedia('(prefers-reduced-motion: reduce)').matches?'auto':'smooth'});}return;}
      if(k==='voice'){try{speechSynthesis.cancel();var L=data.list,txt='Ciao, sono Sapio. Le parole chiave di questo capitolo sono: '+L.map(function(o){return o.d}).join(', ')+'.';
        if(sel>=0&&L[sel].ctx)txt='Sapio ti legge la frase su '+L[sel].d+'. '+L[sel].ctx;
        var u=new SpeechSynthesisUtterance(txt);u.lang='it-IT';u.rate=.95;var v=speechSynthesis.getVoices().filter(function(v){return /^it/i.test(v.lang)})[0];if(v)u.voice=v;speechSynthesis.speak(u);}catch(x){}}
    });
    box.addEventListener('keydown',function(e){if(e.key==='Escape'){open(false);btn.focus();e.stopPropagation();}});
  }
  function start(){document.querySelectorAll('section.ch').forEach(function(sec){
    if(!sec.querySelector('.prose')||!sec.querySelector('.ch-head h2'))return;
    var n=zones(sec).map(textOf).join(' ').split(' ').length;if(n<250)return;build(sec);});}
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',start);else start();
})();
</script>"""


def js():
    return (JS_TMPL.replace('__STOP__', ' '.join(STOP))
            .replace('__OWL_S__', rada.svg('curiosa', 30).replace("'", "\\'"))
            .replace('__OWL_L__', rada.svg('spiega', 60).replace("'", "\\'")))
