"""Sapit: protezioni per il modello AI nel browser (WebLLM), condivise da Mappa viva e Laboratorio.

Fonti (novembre 2026):
- Llamas on the Web (UC Santa Cruz e Microsoft Research, arXiv 2605.20706, 20 maggio 2026): "on iOS devices Safari
  tab memory is limited to <500 MB"; sulle GPU di iPhone entrano solo i modelli piu' piccoli; Qwen su GPU Apple
  con accumulo f16 puo' dare testo incoerente -> su iOS usiamo la variante q4f32 del modello da 0,5B,
  con finestra di contesto e blocchi di prefill ridotti.
- WebKit, Updates to Storage Policy (10 agosto 2023): quota per origine, persistenza concessa con euristiche
  (per esempio app aggiunta alla schermata Home), dati "best-effort" cancellati dopo un periodo senza uso.
- WebKit bug 300782: iOS chiude la scheda per memoria senza errori visibili a JavaScript e la ricarica.
  Per questo salviamo un segnale "caricamento in corso": se la pagina si riapre con il segnale ancora li',
  il modello locale non si riprova da solo.

Espone window.RadarLLM: ios, models(list), pick(id,list), chatOpts(), limit(), load(webllm, id, progress),
generating(on), blocked(id), unblock(id), friendly(err).
"""

JS = r'''<script id="llm-guard">(function(){if(window.RadarLLM)return;
var ua=navigator.userAgent||'',ios=/iP(hone|od|ad)/.test(ua)||(navigator.platform==='MacIntel'&&navigator.maxTouchPoints>1);
var IOS=[['Qwen2.5-0.5B-Instruct-q4f32_1-MLC','Qwen2.5 0,5B · adatto a iPhone e iPad (circa 0,3 GB)']];
/* dimensione del download, in MB (stima prudente per il controllo dello spazio) */
var SIZE={'Qwen2.5-0.5B-Instruct-q4f16_1-MLC':330,'Qwen2.5-0.5B-Instruct-q4f32_1-MLC':360,'Qwen2.5-1.5B-Instruct-q4f16_1-MLC':950,'Qwen2.5-3B-Instruct-q4f16_1-MLC':1800,'Llama-3.2-3B-Instruct-q4f16_1-MLC':1800};
var K='radar-llm-run',KB='radar-llm-blocked',WEEK=7*864e5;
function rd(k){try{return JSON.parse(localStorage.getItem(k)||'null')}catch(e){return null}}
function wr(k,v){try{if(v==null)localStorage.removeItem(k);else localStorage.setItem(k,JSON.stringify(v))}catch(e){}}
/* all'apertura della pagina: un segnale rimasto vuol dire che la scheda e' stata chiusa a meta' */
(function(){var r=rd(K);if(r&&r.m&&Date.now()-(r.t||0)<30*6e4){var b=rd(KB)||{};b[r.m]={t:Date.now(),ph:r.ph||'load'};wr(KB,b)}wr(K,null)})();
function blocked(id){var b=rd(KB)||{},x=b[id];return x&&Date.now()-x.t<WEEK?x:null}
function unblock(id){var b=rd(KB)||{};delete b[id];wr(KB,b)}
function mark(id,ph){wr(K,{m:id,t:Date.now(),ph:ph})}
function clear(){wr(K,null)}
function models(list){return ios?IOS:list}
function pick(id,list){list=models(list);return list.some(function(m){return m[0]===id})?id:list[0][0]}
function chatOpts(){return ios?{context_window_size:3072,prefill_chunk_size:256}:undefined}
function limit(){return ios?{chars:3600,out:900}:{chars:7000,out:1400}}
function standalone(){try{return matchMedia('(display-mode: standalone)').matches||navigator.standalone===true}catch(e){return false}}
function E(msg,code){var e=new Error(msg);e.code=code;e.fallback=true;return e}
function friendly(e){var m=String(e&&e.message||e||'');if(e&&e.code)return m;
  if(/quota|QuotaExceeded|storage/i.test(m))return 'Non c’è abbastanza spazio per salvare il modello in questo browser. Libera spazio o usa Gemini.';
  if(/out of memory|OOM|device was lost|DeviceLost|GPUDevice|allocation/i.test(m))return 'Il dispositivo non ha abbastanza memoria per il modello. Usa Gemini o la mappa dell’edizione.';
  if(/Cannot fetch|Load failed|NetworkError|Failed to fetch/i.test(m))return 'Il download del modello si è interrotto (rete o spazio). Riprova con il Wi-Fi, oppure usa Gemini.';
  return m}
async function load(w,id,progress,note){
  if(blocked(id))throw E('L’ultima volta il modello ha fatto chiudere la pagina'+(ios?' (su iPhone la memoria per scheda è poca)':'')+': per sicurezza non lo riprovo da solo. Usa Gemini, oppure “Riprova il modello”.','blocked');
  var cached=false;try{if(w.hasModelInCache)cached=await w.hasModelInCache(id)}catch(e){}
  if(!cached&&navigator.storage){
    try{if(navigator.storage.estimate){var q=await navigator.storage.estimate(),free=(q.quota||0)-(q.usage||0),need=(SIZE[id]||1000)*1.15*1048576;
      if(q.quota&&free<need)throw E('Spazio insufficiente: servono circa '+Math.round(need/1048576)+' MB, ne restano '+Math.max(0,Math.round(free/1048576))+'. Libera spazio o usa Gemini.','quota')}}catch(e){if(e.code)throw e}
    try{if(navigator.storage.persist){var ok=await navigator.storage.persist();if(!ok&&ios&&!standalone()&&note)note('Consiglio: aggiungi Sapit alla schermata Home (Condividi → Aggiungi alla schermata Home), così iPhone non cancella il modello dopo qualche giorno.')}}catch(e){}}
  mark(id,'load');var eng;
  try{eng=await w.CreateMLCEngine(id,{initProgressCallback:progress},chatOpts())}
  catch(e){clear();var f=friendly(e);var x=new Error(f);x.fallback=/spazio|memoria|download/i.test(f);x.code=/spazio/.test(f)?'quota':'';throw x}
  clear();return eng}
addEventListener('pagehide',function(){var r=rd(K);if(r)clear()});
function generating(id,on){if(on)mark(id,'gen');else clear()}
window.RadarLLM={ios:ios,models:models,pick:pick,chatOpts:chatOpts,limit:limit,load:load,generating:generating,blocked:blocked,unblock:unblock,friendly:friendly};
})();</script>'''
