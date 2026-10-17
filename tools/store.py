"""Salvataggio dei progressi: cookie (a pezzi, 400 giorni) + localStorage, con il più recente che vince; codice di backup."""
JS = r'''<script id="rstore-js">(function(){
var MAXC=3600,DAYS=400;
function cookies(){var o={};document.cookie.split(';').forEach(function(p){var i=p.indexOf('=');if(i>0)o[p.slice(0,i).trim()]=p.slice(i+1).trim()});return o}
function readCookie(key){var c=cookies(),n=parseInt(c[key+'_n']||'0',10),s='';for(var i=0;i<n;i++){if(c[key+'_'+i]==null)return '';s+=c[key+'_'+i]}return s}
function writeCookie(key,val){var c=cookies(),old=parseInt(c[key+'_n']||'0',10),parts=[];for(var i=0;i<val.length;i+=MAXC)parts.push(val.slice(i,i+MAXC));
  var tail='; path=/; max-age='+(DAYS*86400)+'; SameSite=Lax'+(location.protocol==='https:'?'; Secure':'');
  parts.forEach(function(p,i){document.cookie=key+'_'+i+'='+p+tail});document.cookie=key+'_n='+parts.length+tail;
  for(var j=parts.length;j<old;j++)document.cookie=key+'_'+j+'=; path=/; max-age=0'}
function stamp(v){var m=/^t(\d+)\./.exec(v||'');return m?+m[1]:0}
window.RStore={
  load:function(key){var a='',b='';try{a=localStorage.getItem('rs_'+key)||''}catch(e){}try{b=readCookie(key)}catch(e){}var v=stamp(a)>=stamp(b)?a:b;return v?v.replace(/^t\d+\./,''):''},
  save:function(key,val){var v='t'+Date.now()+'.'+val;try{localStorage.setItem('rs_'+key,v)}catch(e){}try{writeCookie(key,v)}catch(e){}}
};
})();</script>'''

# Codifica compatta dei progressi del Laboratorio: x~s~b~id36-score_id36-score...
LAB_CODEC = r'''function encS(S){return [S.xp,S.streak,S.best].join('~')+'~'+Object.keys(S.done).map(function(k){return (+k).toString(36)+'-'+S.done[k]}).join('_')}
function decS(t){var p=String(t||'').split('~');if(p.length<4)return null;var o={xp:+p[0]||0,streak:+p[1]||0,best:+p[2]||0,done:{}};if(p[3])p[3].split('_').forEach(function(x){var q=x.split('-');if(q.length===2)o.done[parseInt(q[0],36)]=+q[1]||0});return o}'''

# Codifica degli esercizi fatti: bitset in base64url
EX_CODEC = r'''function encD(d,N){var b=new Uint8Array(Math.ceil((N+1)/8));Object.keys(d).forEach(function(k){k=+k;if(k>0&&k<=N)b[k>>3]|=1<<(k&7)});var s='';b.forEach(function(x){s+=String.fromCharCode(x)});return btoa(s).replace(/\+/g,'-').replace(/\//g,'_').replace(/=+$/,'')}
function decD(t){var o={};if(!t)return o;try{var s=atob(t.replace(/-/g,'+').replace(/_/g,'/'));for(var i=0;i<s.length;i++){var x=s.charCodeAt(i);for(var j=0;j<8;j++)if(x&(1<<j))o[i*8+j]=1}}catch(e){}return o}'''

BACKUP_CSS = '''<style id="backup-css">.backup{margin-top:1rem}.backup>summary{cursor:pointer;font-weight:700;min-height:32px;display:flex;align-items:center}
.backup textarea{width:100%;min-height:5rem;font:13px/1.5 ui-monospace,Menlo,monospace;padding:.6rem;border-radius:10px;border:1px solid var(--line);background:var(--soft);color:var(--ink);box-sizing:border-box;word-break:break-all}
.backup .brow{display:flex;flex-wrap:wrap;gap:.5rem;margin:.5rem 0}.backup .bmsg{font-weight:600;min-height:1.3em}</style>'''

def backup_html(prefix):
    return ('<details class="backup"><summary>💾 Codice di backup dei progressi</summary>'
            '<p>I progressi si salvano da soli nei cookie e nella memoria di questo browser, per 400 giorni. Per non perderli se cancelli i dati del browser, o per portarli su un altro computer, copia questo codice e conservalo; poi incollalo qui e premi "Ripristina".</p>'
            '<label for="%sbk">Il tuo codice</label><textarea id="%sbk" readonly></textarea>'
            '<div class="brow"><button type="button" class="pbtn" id="%sbc">Copia il codice</button></div>'
            '<label for="%sbi">Incolla un codice salvato</label><textarea id="%sbi"></textarea>'
            '<div class="brow"><button type="button" class="pbtn" id="%sbr">Ripristina</button></div><p class="bmsg" id="%sbm" role="status" aria-live="polite"></p></details>') % ((prefix,) * 7)

# Soluzioni dell'utente: localStorage (molto più capiente dei cookie) + file da scaricare/caricare
SOL_JS = r'''<script id="rsol-js">(function(){
function rd(ns){try{return JSON.parse(localStorage.getItem('rsol_'+ns)||'{}')||{}}catch(e){return {}}}
function wr(ns,o){try{localStorage.setItem('rsol_'+ns,JSON.stringify(o));return true}catch(e){return false}}
window.RSol={
  get:function(ns,id){return rd(ns)[id]||null},
  set:function(ns,id,v){var o=rd(ns);o[id]=Object.assign({},o[id]||{},v,{t:Date.now()});return wr(ns,o)},
  all:function(ns){return rd(ns)},
  exportFile:function(){var d={tipo:'radar-ai-soluzioni',versione:1,data:new Date().toISOString(),progressi:{lab:RStore.load('radar_lab'),esercizi:RStore.load('radar_ex')},soluzioni:{lab:rd('lab'),esercizi:rd('ex'),prova:rd('prova')}};
    var b=new Blob([JSON.stringify(d,null,1)],{type:'application/json'}),a=document.createElement('a');a.href=URL.createObjectURL(b);a.download='radar-ai-le-mie-soluzioni-'+new Date().toISOString().slice(0,10)+'.json';document.body.appendChild(a);a.click();setTimeout(function(){URL.revokeObjectURL(a.href);a.remove()},500)},
  importFile:function(file,cb){var r=new FileReader();r.onload=function(){try{var d=JSON.parse(r.result);if(d.tipo!=='radar-ai-soluzioni')throw new Error('Il file non è un salvataggio di Radar AI.');
      ['lab','esercizi','prova'].forEach(function(k){var ns=k==='esercizi'?'ex':k;var cur=rd(ns),inc=(d.soluzioni||{})[k]||{};Object.keys(inc).forEach(function(id){if(!cur[id]||(inc[id].t||0)>=(cur[id].t||0))cur[id]=inc[id]});wr(ns,cur)});
      if(d.progressi){if(d.progressi.lab)RStore.save('radar_lab',d.progressi.lab);if(d.progressi.esercizi)RStore.save('radar_ex',d.progressi.esercizi)}cb(null,d)}catch(e){cb(e)}};r.readAsText(file)}
};})();</script>'''
SOL_CSS = '''<style id="rsol-css">.savednote{margin:.4rem 0 .8rem;padding:.55rem .8rem;border-radius:12px;background:var(--violet-soft);border:1px solid var(--violet);font-size:.92rem;font-weight:600}
.mysol ul{list-style:none;padding:0;margin:.6rem 0;display:flex;flex-wrap:wrap;gap:.4rem}.mysol li a{text-decoration:none}.mysol .brow{display:flex;flex-wrap:wrap;gap:.5rem;align-items:center;margin:.5rem 0}
.mysol input[type=file]{font:inherit;max-width:100%}</style>'''
def mysol_html(prefix):
    return ('<details class="backup mysol" id="%smysol"><summary>📒 Le mie soluzioni</summary>'
            '<p>Ogni volta che verifichi una sfida, le risposte che hai dato si salvano in questo browser; quando riapri la sfida le ritrovi già compilate. Nel banco di prova si salvano anche lo schema e il prompt che hai modificato. Scarica il file per conservarle o portarle su un altro computer: contiene anche punti e progressi.</p>'
            '<p id="%ssolcount"></p><ul id="%ssollist"></ul>'
            '<div class="brow"><button type="button" class="pbtn" id="%ssolexp">⬇ Scarica le mie soluzioni (.json)</button></div>'
            '<div class="brow"><label for="%ssolimp">Carica un file salvato</label><input type="file" id="%ssolimp" accept="application/json,.json"></div>'
            '<p class="bmsg" id="%ssolmsg" role="status" aria-live="polite"></p></details>') % ((prefix,) * 7)
