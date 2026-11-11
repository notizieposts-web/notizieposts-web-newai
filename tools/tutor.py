"""Rada, la guida degli esercizi: avatar che legge ad alta voce (voce del browser, testo sempre scritto)
e pannello "Lettura facilitata" (testo più grande, più spazio, carattere ad alta leggibilità, righello, numeri in evidenza).
Usata da esercizi_page.py (Palestra) e arena_page.py (Laboratorio). Niente server, niente chiavi: le preferenze restano nel browser.

API nel browser (window.RTutor):
  RTutor.say(titolo, [paragrafi di testo semplice], {open:false})  mostra il testo nel pannello e lo legge se richiesto
  RTutor.text(elementoOHtml)   testo semplice da un pezzo di pagina
  RTutor.nums(html)            mette i numeri in <span class="rt-n">, per l'opzione "Numeri in evidenza"
  RTutor.avatar(px)            l'SVG dell'avatar
"""

import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rada

CSS = '''<style id="tutor-css">
.rt-fab{position:fixed;right:max(.8rem,env(safe-area-inset-right));bottom:max(.8rem,env(safe-area-inset-bottom));z-index:9500;display:inline-flex;align-items:center;gap:.5rem;min-height:52px;padding:.3rem 1rem .3rem .4rem;border-radius:999px;border:2px solid var(--violet);background:var(--surface);color:var(--ink);font:700 .95rem var(--head,system-ui);cursor:pointer;box-shadow:0 8px 24px rgba(0,0,0,.18)}
.rt-fab[aria-expanded="true"]{background:var(--violet-soft)}
.rt-panel{position:fixed;right:max(.8rem,env(safe-area-inset-right));bottom:calc(max(.8rem,env(safe-area-inset-bottom)) + 62px);z-index:9500;width:min(27rem,calc(100vw - 1.6rem));max-height:min(74vh,40rem);overflow:auto;box-sizing:border-box;padding:1rem 1.1rem 1.1rem;border-radius:18px;border:2px solid var(--violet);background:var(--surface);color:var(--ink);box-shadow:0 18px 50px rgba(0,0,0,.28)}
.rt-panel[hidden]{display:none}
.rt-head{display:flex;gap:.8rem;align-items:flex-start}
.rt-head h2{font-size:1.15rem;margin:0}.rt-head p{margin:.15rem 0 0;font-size:.9rem;color:var(--muted)}
.rt-x{margin-left:auto;flex:none;min-width:44px;min-height:44px;border-radius:999px;border:1px solid var(--line);background:var(--surface);color:var(--ink);font-weight:700;cursor:pointer}
.rt-cap{margin:.8rem 0 .6rem;padding:.8rem .9rem;border-radius:12px;background:var(--soft);border-left:4px solid var(--violet);font-size:1.02rem;line-height:1.75;max-height:16rem;overflow:auto}
.rt-cap p{margin:0 0 .55rem}.rt-cap p:last-child{margin:0}
.rt-s.on{background:var(--violet-soft);box-shadow:0 0 0 2px var(--violet-soft);border-radius:4px;text-decoration:underline;text-decoration-thickness:2px;text-underline-offset:3px}
.rt-ctl{display:flex;flex-wrap:wrap;gap:.45rem;align-items:center}
.rt-b{min-height:44px;padding:.4rem .95rem;border-radius:999px;border:1px solid var(--line);background:var(--surface);color:var(--ink);font:700 .92rem var(--head,system-ui);cursor:pointer}
.rt-b.pri{background:var(--violet);color:var(--bg);border-color:var(--violet)}
.rt-b[disabled]{opacity:.5;cursor:default}
.rt-ctl label,.rt-read label{font-weight:600;font-size:.95rem}
.rt-ctl select,.rt-read select{font:inherit;min-height:40px;padding:.3rem .6rem;border-radius:10px;border:1px solid var(--line);background:var(--surface);color:var(--ink)}
.rt-msg{margin:.5rem 0 0;font-size:.9rem;font-weight:600}
.rt-read{margin-top:.9rem;border-top:1px solid var(--line);padding-top:.7rem}
.rt-read>summary{cursor:pointer;font-weight:700;min-height:40px;display:flex;align-items:center}
.rt-read fieldset{border:0;padding:0;margin:.3rem 0 0;display:grid;gap:.35rem}
.rt-read legend{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0)}
.rt-opt{display:flex;gap:.6rem;align-items:center;min-height:40px}
.rt-opt input[type=checkbox]{width:22px;height:22px;flex:none}
.rt-read .hint{font-size:.85rem;color:var(--muted);margin:.5rem 0 0}
.rt-face{display:inline-flex;flex:none}
.rt-eyes,.rt-mouth{transform-box:fill-box;transform-origin:center}
.rt-eyes{animation:rt-blink 5s infinite}
.rt-talk .rt-mouth{animation:rt-talk .26s infinite alternate ease-in-out}
@keyframes rt-blink{0%,94%,100%{transform:scaleY(1)}97%{transform:scaleY(.1)}}
@keyframes rt-talk{from{transform:scaleY(1)}to{transform:scaleY(2.8)}}
@media (prefers-reduced-motion:reduce){.rt-eyes,.rt-talk .rt-mouth{animation:none!important}}
@media (max-width:30rem){.rt-fab .rt-lab{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0)}.rt-fab{padding:.3rem .4rem}}
.rt-n{white-space:nowrap}
html.rt-num .rt-n{font-weight:700;background:var(--sun-soft);color:var(--ink);border-radius:5px;padding:.05em .25em;box-shadow:inset 0 -2px 0 var(--sun)}
html.rt-s1{font-size:112.5%}html.rt-s1 body{font-size:19px}
html.rt-s2{font-size:125%}html.rt-s2 body{font-size:21px}
html.rt-sp main p,html.rt-sp main li,html.rt-sp main label,html.rt-sp main td,html.rt-sp main th,html.rt-sp main summary,html.rt-sp .rt-cap{line-height:2!important;letter-spacing:.045em;word-spacing:.14em}
html.rt-sp main p,html.rt-sp main li{max-width:40rem}
html.rt-font body,html.rt-font main h1,html.rt-font main h2,html.rt-font main h3,html.rt-font main button,html.rt-font main input,html.rt-font main select,html.rt-font main textarea,html.rt-font .rt-panel,html.rt-font .rt-panel button{font-family:"Atkinson Hyperlegible",Verdana,Tahoma,sans-serif!important}
.rt-ruler{position:fixed;left:0;right:0;top:40%;height:3rem;z-index:9400;pointer-events:none;background:var(--violet);opacity:.13;border-top:2px solid var(--violet);border-bottom:2px solid var(--violet)}
.rt-ruler[hidden]{display:none}
.rt-say{display:inline-flex;align-items:center;gap:.4rem;min-height:40px;padding:.3rem .9rem .3rem .35rem;border-radius:999px;border:1px solid var(--violet);background:var(--surface);color:var(--ink);font:700 .92rem var(--head,system-ui);cursor:pointer}
</style>''' + rada.CSS

JS = r'''<script id="tutor-js">(function(){
var AV=__AV__;
function av(px,ex){return (AV[ex]||AV.ciao).replace(/width="\d+" height="\d+"/,'width="'+px+'" height="'+Math.round(px*148/140)+'"')}
var face='';function setFace(ex){if(face===ex||!panel)return;face=ex;panel.querySelector('.rt-face').innerHTML=av(64,ex);fab.querySelector('.rt-face').innerHTML=av(44,ex)}
var P={size:0,sp:0,font:0,ruler:0,num:0,auto:0,rate:1};
try{var sv=JSON.parse(localStorage.getItem('radar-read')||'{}');for(var k in P)if(sv[k]!=null)P[k]=sv[k]}catch(e){}
function keep(){try{localStorage.setItem('radar-read',JSON.stringify(P))}catch(e){}}
var H=document.documentElement,ruler=null,fontLoaded=false;
function apply(){H.classList.toggle('rt-s1',+P.size===1);H.classList.toggle('rt-s2',+P.size===2);H.classList.toggle('rt-sp',!!P.sp);H.classList.toggle('rt-font',!!P.font);H.classList.toggle('rt-num',!!P.num);
  if(P.font&&!fontLoaded){fontLoaded=true;var l=document.createElement('link');l.rel='stylesheet';l.href='https://fonts.googleapis.com/css2?family=Atkinson+Hyperlegible:wght@400;700&display=swap';document.head.appendChild(l)}
  if(ruler)ruler.hidden=!P.ruler}
apply();
function text(x){var d;if(typeof x==='string'){d=document.createElement('div');d.innerHTML=x}else{d=x.cloneNode(true)}
  d.querySelectorAll('.sr-only,button,input,select,textarea,script,style').forEach(function(n){n.remove()});
  d.querySelectorAll('p,li,div,br,h1,h2,h3,h4,tr').forEach(function(n){n.insertAdjacentText('afterend',' ')});
  return d.textContent.replace(/\s+/g,' ').trim()}
var NRE;try{NRE=new RegExp('(<[^>]+>)|(?<![A-Za-zÀ-ú_\\-])(\\d[\\d.,]*\\d|\\d)(?![A-Za-z_\\-]*\\d)(\\s?(?:%|\\$|€))?','g')}catch(e){NRE=/(<[^>]+>)|(\d[\d.,]*\d|\d)(\s?(?:%|\$|€))?/g}
function nums(html){return String(html).replace(NRE,function(m,tag){return tag?tag:'<span class="rt-n">'+m+'</span>'})}
/* frasi: si taglia dopo . ! ? solo se segue uno spazio (17.646 e 3,5 restano interi) */
function sents(t){var out=[],s=0;for(var i=0;i<t.length;i++){var c=t.charAt(i);if((c==='.'||c==='!'||c==='?')&&(i+1>=t.length||/\s/.test(t.charAt(i+1)))){out.push(t.slice(s,i+1).trim());s=i+1}}
  var r=t.slice(s).trim();if(r)out.push(r);return out.filter(Boolean)}
function spoken(t){return t.replace(/÷/g,' diviso ').replace(/×/g,' per ').replace(/→/g,', quindi ').replace(/≤/g,' minore o uguale a ').replace(/≥/g,' maggiore o uguale a ').replace(/=\s*\?/g,' uguale a quanto?').replace(/=/g,' uguale ')
  .replace(/(\d)\s?%/g,'$1 per cento').replace(/(\d)\s?\$/g,'$1 dollari').replace(/\$\s?(\d[\d.,]*)/g,'$1 dollari').replace(/(\d)\s?€/g,'$1 euro').replace(/\/min\b/g,' al minuto').replace(/\/s\b/g,' al secondo').replace(/_/g,' ').replace(/▢/g,' da trovare ')}
function esc(s){return String(s).replace(/[&<>"]/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]})}
var syn=window.speechSynthesis||null,Q=[],qi=0,state='idle',voice=null,fab,panel,cap,lastFocus=null;
function pickVoice(){if(!syn)return;var v=syn.getVoices()||[];voice=v.filter(function(x){return /^it(-|_|$)/i.test(x.lang)})[0]||null}
if(syn){pickVoice();try{syn.addEventListener('voiceschanged',pickVoice)}catch(e){}}
function ui(){if(!panel)return;var b=panel.querySelector('#rt-play'),p=panel.querySelector('#rt-pause'),s=panel.querySelector('#rt-stop');
  b.disabled=!Q.length||!syn;b.textContent=state==='paused'?'▶ Riprendi':(state==='play'?'↺ Da capo':'▶ Ascolta');p.disabled=state!=='play';s.disabled=state==='idle';
  setFace(state==='play'?'parla':'ciao');
  panel.querySelector('#rt-msg').textContent=!syn?'Questo browser non ha una voce: il testo qui sopra dice le stesse cose.':(Q.length&&!voice&&syn.getVoices().length?'Non trovo una voce italiana in questo dispositivo: la lettura può avere un accento straniero. Il testo resta scritto qui sopra.':'')}
function mark(i){if(!cap)return;cap.querySelectorAll('.rt-s').forEach(function(n){n.classList.toggle('on',+n.dataset.i===i)});var on=cap.querySelector('.rt-s.on');if(on&&on.scrollIntoView)try{on.scrollIntoView({block:'nearest'})}catch(e){}}
function next(){if(state!=='play')return;if(qi>=Q.length){state='idle';mark(-1);ui();return}
  var u=new SpeechSynthesisUtterance(spoken(Q[qi]));u.lang='it-IT';if(voice)u.voice=voice;u.rate=+P.rate||1;var me=qi;
  u.onstart=function(){mark(me)};u.onend=function(){if(state==='play'&&qi===me){qi++;next()}};u.onerror=function(){if(state==='play'&&qi===me){qi++;next()}};
  mark(me);syn.speak(u)}
function stop(){if(syn)try{syn.cancel()}catch(e){}state='idle';qi=0;mark(-1);ui()}
function play(){if(!syn||!Q.length)return;try{syn.cancel()}catch(e){}qi=0;state='play';ui();setTimeout(next,60)}
function build(){
  fab=document.createElement('button');fab.type='button';fab.className='rt-fab';fab.id='rt-fab';fab.setAttribute('aria-expanded','false');fab.setAttribute('aria-controls','rt-panel');
  fab.innerHTML='<span class="rt-face"></span><span class="rt-lab">Rada ti aiuta</span><span class="sr-only">: apri la guida e la lettura facilitata</span>';
  panel=document.createElement('section');panel.className='rt-panel';panel.id='rt-panel';panel.hidden=true;panel.tabIndex=-1;panel.setAttribute('role','dialog');panel.setAttribute('aria-labelledby','rt-h');
  panel.innerHTML='<div class="rt-head"><span class="rt-face"></span><div><h2 id="rt-h">Rada, la tua guida</h2><p>Ti spiego gli esercizi un passo alla volta. Posso leggere ad alta voce: il testo resta sempre scritto.</p></div><button type="button" class="rt-x" id="rt-x" aria-label="Chiudi la guida">✕</button></div>'+
    '<div class="rt-cap" id="rt-cap" tabindex="0" role="region" aria-label="Quello che dice Rada" aria-live="polite"><p>Ciao! In ogni esercizio trovi i pulsanti di aiuto: un indizio, il metodo, la soluzione passo passo, un esempio già svolto. Premi «Ascolta» e te li leggo io.</p></div>'+
    '<div class="rt-ctl"><button type="button" class="rt-b pri" id="rt-play">▶ Ascolta</button><button type="button" class="rt-b" id="rt-pause">⏸ Pausa</button><button type="button" class="rt-b" id="rt-stop">⏹ Ferma</button>'+
    '<label for="rt-rate">Velocità</label><select id="rt-rate"><option value="0.75">Lenta</option><option value="1">Normale</option><option value="1.25">Veloce</option></select></div><p class="rt-msg" id="rt-msg" role="status"></p>'+
    '<details class="rt-read" id="rt-read"><summary>👓 Lettura facilitata</summary><fieldset><legend>Opzioni di lettura</legend>'+
    '<div class="rt-opt"><label for="rt-size">Grandezza del testo</label><select id="rt-size"><option value="0">Normale</option><option value="1">Grande</option><option value="2">Molto grande</option></select></div>'+
    '<label class="rt-opt"><input type="checkbox" id="rt-sp"> Più spazio tra righe, parole e lettere</label>'+
    '<label class="rt-opt"><input type="checkbox" id="rt-font"> Carattere ad alta leggibilità</label>'+
    '<label class="rt-opt"><input type="checkbox" id="rt-ruler"> Righello che segue la riga che leggi</label>'+
    '<label class="rt-opt"><input type="checkbox" id="rt-num"> Numeri in evidenza</label>'+
    '<label class="rt-opt"><input type="checkbox" id="rt-auto"> Leggi ad alta voce appena apro un aiuto</label>'+
    '</fieldset><p class="hint">Le scelte restano in questo browser. Negli esercizi non c\'è limite di tempo e gli aiuti non tolgono punti nella Palestra.</p></details>';
  ruler=document.createElement('div');ruler.className='rt-ruler';ruler.hidden=!P.ruler;ruler.setAttribute('aria-hidden','true');
  document.body.appendChild(ruler);document.body.appendChild(panel);document.body.appendChild(fab);cap=panel.querySelector('#rt-cap');
  Q=sents(text(cap));cap.innerHTML='<p>'+Q.map(function(s,i){return '<span class="rt-s" data-i="'+i+'">'+esc(s)+'</span>'}).join(' ')+'</p>';
  fab.onclick=function(){panel.hidden?show(true):hide()};panel.querySelector('#rt-x').onclick=function(){hide()};
  panel.querySelector('#rt-play').onclick=function(){if(state==='paused'){try{syn.resume()}catch(e){}state='play';ui()}else play()};
  panel.querySelector('#rt-pause').onclick=function(){if(state==='play'){try{syn.pause()}catch(e){}state='paused';ui()}};
  panel.querySelector('#rt-stop').onclick=stop;
  var r=panel.querySelector('#rt-rate');r.value=String(P.rate);if(!r.value)r.value='1';r.onchange=function(){P.rate=+r.value;keep();if(state==='play'){var at=qi;try{syn.cancel()}catch(e){}qi=at;state='play';setTimeout(next,60)}};
  var z=panel.querySelector('#rt-size');z.value=String(P.size);z.onchange=function(){P.size=+z.value;keep();apply()};
  [['sp','rt-sp'],['font','rt-font'],['ruler','rt-ruler'],['num','rt-num'],['auto','rt-auto']].forEach(function(o){var c=panel.querySelector('#'+o[1]);c.checked=!!P[o[0]];c.onchange=function(){P[o[0]]=c.checked?1:0;keep();apply()}});
  document.addEventListener('keydown',function(e){if(e.key==='Escape'&&!panel.hidden&&!e.defaultPrevented){hide()}});
  function mv(y){if(P.ruler)ruler.style.top=Math.max(0,y-ruler.offsetHeight/2)+'px'}
  document.addEventListener('mousemove',function(e){mv(e.clientY)},{passive:true});document.addEventListener('touchmove',function(e){if(e.touches[0])mv(e.touches[0].clientY)},{passive:true});
  document.addEventListener('focusin',function(e){if(P.ruler&&e.target.getBoundingClientRect){var b=e.target.getBoundingClientRect();mv(b.top+Math.min(b.height,40)/2)}});
  window.addEventListener('pagehide',function(){if(syn)try{syn.cancel()}catch(e){}});
  ui()}
function show(focus){lastFocus=document.activeElement;panel.hidden=false;fab.setAttribute('aria-expanded','true');if(focus)panel.focus()}
function hide(){var inside=panel.contains(document.activeElement);panel.hidden=true;fab.setAttribute('aria-expanded','false');stop();if(inside)fab.focus()}
function say(title,parts,opt){opt=opt||{};stop();var n=0,h=title?'<p><b>'+esc(title)+'</b></p>':'';Q=[];
  (parts||[]).forEach(function(p){var ss=sents(String(p));if(!ss.length)return;h+='<p>'+ss.map(function(s){Q.push(s);return '<span class="rt-s" data-i="'+(n++)+'">'+esc(s)+'</span>'}).join(' ')+'</p>'});
  cap.innerHTML=h;cap.scrollTop=0;if(opt.open!==false&&panel.hidden)show(false);ui();if(opt.play||P.auto)play()}
window.RTutor={say:say,text:text,nums:nums,avatar:av,stop:stop,prefs:P,sents:sents};
if(document.body)build();else document.addEventListener('DOMContentLoaded',build);
})();</script>'''.replace('__AV__', __import__('json').dumps(rada.ALL))


def say_btn(label='Ascolta da Rada', attrs=''):
    """Pulsante con l'avatar piccolo, da usare nelle pagine generate in Python."""
    return '<button type="button" class="rt-say" %s>%s<span>%s</span></button>' % (attrs, rada.svg('ciao', 28), label)
