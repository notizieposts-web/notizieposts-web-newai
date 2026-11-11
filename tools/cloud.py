"""Classifica online e progressi tra dispositivi (Supabase, progetto radar-ai, Francoforte).
Niente email e niente password: ogni persona ha un "codice personale" creato nel browser (resta in localStorage, chiave radar-me);
sul server se ne salva solo l'impronta. Il sito parla solo con quattro funzioni (tools/cloud/schema.sql):
radar_save, radar_load, radar_forget, radar_board. La tabella non è leggibile direttamente.
Si attiva solo se la persona lo chiede nella pagina squadre.html; da quel momento Palestra e Laboratorio inviano i punti da soli.
"""
import os, json
CFG = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cloud', 'config.json'), encoding='utf-8'))
JS = r'''<script id="cloud-js">(function(){
var URL0=__URL__,KEY=__KEY__,timer=null;
function rpc(fn,body){return fetch(URL0+'/rest/v1/rpc/'+fn,{method:'POST',headers:{'apikey':KEY,'Authorization':'Bearer '+KEY,'Content-Type':'application/json'},body:JSON.stringify(body||{})}).then(function(r){return r.text().then(function(t){var j=null;try{j=t?JSON.parse(t):null}catch(e){}if(!r.ok)throw new Error(j&&j.message?j.message:'Il servizio ha risposto con un errore ('+r.status+').');return j})})}
function rd(k){try{return JSON.parse(localStorage.getItem(k)||'{}')||{}}catch(e){return {}}}
function wr(k,o){try{localStorage.setItem(k,JSON.stringify(o))}catch(e){}}
function me(){return rd('radar-me')}
function setMe(o){wr('radar-me',o)}
function newSecret(){var b=new Uint8Array(24);(window.crypto||window.msCrypto).getRandomValues(b);var s='';for(var i=0;i<b.length;i++)s+=(b[i]<16?'0':'')+b[i].toString(16);return 'RA1-'+s}
function on(){var m=me();return !!(m.on&&m.s&&m.n)}
function setStats(p){var s=rd('radar-stats');for(var k in p)s[k]=p[k];wr('radar-stats',s)}
function pushNow(){var m=me(),s=rd('radar-stats');if(!on())return Promise.resolve(null);
  return rpc('radar_save',{p_secret:m.s,p_name:m.n,p_team:m.t||'',p_pp:+s.pp||0,p_lp:+s.lp||0,p_ps:+s.ps||0,p_ls:+s.ls||0,p_ex:window.RStore?RStore.load('radar_ex'):'',p_arena:window.RStore?RStore.load('radar_arena'):''})}
function push(){if(!on())return;clearTimeout(timer);timer=setTimeout(function(){pushNow().catch(function(){})},4000)}
window.RCloud={rpc:rpc,me:me,setMe:setMe,newSecret:newSecret,on:on,setStats:setStats,push:push,pushNow:pushNow};
})();</script>'''.replace('__URL__', json.dumps(CFG['url'])).replace('__KEY__', json.dumps(CFG['key']))
