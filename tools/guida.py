"""Guida Azure Content Understanding: raccoglie tutte le puntate della rubrica in una pagina con menu per temi."""
import re, sys, os, html
root = sys.argv[1]
EP = [  # (puntata, edizione, sezione, gruppo, titolo breve)
 (1,'07','azure','costi','Tempi, costi e volumi'),
 (2,'08','azure','costi','Le leve nascoste del costo'),
 (3,'09','azure','pipeline','Smistare prima di leggere'),
 (4,'10','azure','pipeline','Audio e video'),
 (5,'11','azure','pipeline','Content Understanding o Document Intelligence'),
 (6,'12','azure','pipeline','La modalità agentica'),
 (7,'13','azure','qualita','Gli elementi invisibili di un documento'),
 (8,'14','azure','costi','Concorrenza, code e sovraccarico'),
 (9,'15','azure','sicurezza','Dove finiscono i documenti'),
 (10,'16','azure','produzione','Osservare il servizio mentre lavora'),
 (11,'17','azure','produzione','La lista di controllo completa'),
 (12,'18','qualita','qualita','Misurare la qualità dei campi'),
 (13,'18','cloud','casi','Azure, AWS e Google in un progetto misto'),
 (14,'18','caso','casi','Un caso completo: 50.000 documenti al mese'),
 (15,'19','azure','pipeline','Pronti all\'uso: prebuilt, toolkit e integrazioni'),
 (16,'20','azure','costi','Le tre corsie: sincrono, asincrono, capacità tua'),
 (17,'21','azure','produzione','Lingue e regioni'),
 (18,'22','azure','sicurezza','Chi può fare cosa: ruoli, rete, chiavi'),
 (19,'23','azure','sicurezza','I documenti avvelenati'),
 (20,'24','azure','qualita','Lo schema dei campi: descrizioni e metodi'),
 (21,'25','azure','produzione','La vita di un analizzatore: versioni'),
 (22,'26','azure','costi','I limiti del servizio: pagine, file, campi'),
 (23,'27','azure','qualita','Insegnare con gli esempi etichettati'),
]
GROUPS = [
 ('costi','Costi','Costi e prestazioni','Quanto costa, quanto ci mette, e come pagare meno a parità di risultato.'),
 ('pipeline','Pipeline','Progettare la pipeline','Quale servizio, quale modalità e quali componenti pronti usare per ogni tipo di contenuto.'),
 ('qualita','Qualità','Qualità dei dati','Cosa il servizio vede davvero in un documento, e come misurare se i campi estratti sono giusti.'),
 ('sicurezza','Sicurezza','Sicurezza e governance','Dove vanno i dati, chi può fare cosa, e come difendersi dai documenti malevoli.'),
 ('produzione','Produzione','Operare in produzione','Monitoraggio, lista di controllo prima di partire, lingue e regioni disponibili.'),
 ('casi','Casi','Architetture e casi reali','Progetti multi-cloud e un caso costruito dall\'avvio al cruscotto, con i numeri.'),
]
def strip_tags(x): return html.unescape(re.sub(r'<[^>]+>', '', x)).strip()
def extract(ed, sid):
    s = open(os.path.join(root, 'edizioni', ed + '.html'), encoding='utf-8').read()
    sec = re.search(r'<section class="ch" id="%s".*?</section>' % sid, s, re.S).group(0)
    h2 = strip_tags(re.search(r'<h2[^>]*>(.*?)</h2>', sec, re.S).group(1))
    lead = re.search(r'<p class="lead">(.*?)</p>', sec, re.S)
    lead = lead.group(1).strip() if lead else ''
    kick = re.search(r'<div class="kicker">(.*?)</div>', sec, re.S)
    dates = [strip_tags(c) for c in re.findall(r'<span class="chip date">(.*?)</span>', kick.group(1))] if kick else []
    prose = re.search(r'<div class="prose">(.*?)</div>\s*<div class="stick[^"]*">', sec, re.S)
    prose = prose.group(1) if prose else ''
    prose = re.sub(r'\sid="[^"]*"', '', prose)
    prose = re.sub(r'<h3>', '<h4>', prose); prose = re.sub(r'</h3>', '</h4>', prose)
    prose = prose.replace('qui accanto', 'nella pagina dell\'edizione').replace('selettore accanto', 'selettore nella pagina dell\'edizione')
    return h2, lead, prose
src23 = open(os.path.join(root, 'edizioni', '23.html'), encoding='utf-8').read()
head = src23[:src23.index('<body')]
head = re.sub(r'<title>.*?</title>', '<title>Guida Azure Content Understanding · Radar AI</title>', head)
head = re.sub(r'<style id="(a11y|egraph-css|edx-css)">.*?</style>', '', head, flags=re.S)
head = re.sub(r'<script id="a11y-theme">.*?</script>', '', head, flags=re.S)
head = re.sub(r'<link rel="icon"[^>]*>', '', head)
extra_css = '''<style id="guida-css">
.gsearch{display:flex;gap:.6rem;align-items:center;flex-wrap:wrap;margin-top:1.4rem}
.gsearch input{flex:1;min-width:14rem;font:inherit;padding:.65rem 1rem;border-radius:999px;border:1px solid var(--line);background:var(--surface);color:var(--ink)}
.gcount{font-size:.9rem;color:var(--muted)}
.gindex{display:grid;grid-template-columns:repeat(auto-fill,minmax(15rem,1fr));gap:.8rem;margin-top:1.4rem}
.gindex a{display:block;padding:1rem 1.1rem;border-radius:16px;border:1px solid var(--line);background:var(--surface);text-decoration:none;color:var(--ink)}
.gindex a:hover{border-color:var(--violet)}.gindex b{display:block;font-family:var(--head);font-size:1.05rem;margin:.35rem 0 .2rem}.gindex span.n{font-size:.85rem;color:var(--muted)}
.gsub{margin-top:1.4rem}.palcta{display:inline-flex;align-items:center;min-height:44px;padding:.5rem 1.2rem;border-radius:999px;background:var(--violet);color:var(--bg);font-weight:700;text-decoration:none}.palcta:hover{filter:brightness(1.08)}.gsub a.chip{min-height:32px;padding:.35rem .9rem;font-size:.95rem}.gsub a.chip.on{outline:2px solid var(--ink);outline-offset:2px}
.ep{margin-top:1rem;max-width:50rem}.ep .prose{max-width:none}@media (max-width:860px){.hero .radar{display:none}}
.gindex+*{}
.ep{margin-top:1rem}.ep h3{font-size:1.2rem;margin:.5rem 0 .35rem}.ep .lead{font-size:1rem;margin:0 0 .6rem}
.ep details>summary{cursor:pointer;font-weight:700;color:var(--violet);min-height:32px;display:flex;align-items:center}
.ep .prose{margin-top:.8rem}.ep .prose h4{font-size:1.05rem;margin:1.4rem 0 .4rem}
.ep .eplinks{display:flex;gap:.6rem;flex-wrap:wrap;margin-top:.8rem}
.ep .eplinks a{display:inline-flex;align-items:center;min-height:32px;padding:.35rem .9rem;border-radius:999px;border:1px solid var(--line);text-decoration:none;font-weight:600;color:var(--ink);background:var(--surface)}
.ep .eplinks a.pri{background:var(--violet);color:var(--bg);border-color:var(--violet)}
</style>'''
nav = '<nav class="nav" aria-label="Temi della guida"><div class="nav-in"><a class="brand" href="./">Radar AI</a><div class="links" id="links">' + \
      '<a href="#indice">Indice</a>' + ''.join('<a href="#%s">%s</a>' % (g[0], g[1]) for g in GROUPS) + '</div></div><div class="progress" id="prog"></div></nav>'
hero = '''<header class="hero"><div>
<div class="meta"><span class="chip topic">Azure</span><span class="chip date">%d puntate</span><span class="chip">Aggiornata al 17 ottobre 2026</span></div>
<h1 style="margin-top:1.2rem">Azure Content Understanding: tutta la rubrica in una guida</h1>
<p class="sub">Le %d puntate della rubrica fissa di Radar AI, ordinate per tema invece che per data. Ogni puntata si apre qui sotto; per calcolatori, simulatori e liste di controllo interattive c'è il link alla sua edizione.</p>
<p style="margin:1.2rem 0 0;display:flex;flex-wrap:wrap;gap:.6rem"><a class="palcta" href="azure-laboratorio.html">🎮 Gioca nel laboratorio pratico →</a><a class="palcta" href="azure-esercizi.html">Allenati con oltre mille esercizi →</a></p>
%s</div><svg class="radar" viewBox="0 0 400 400" aria-hidden="true"><g transform="translate(80 80) scale(7.5)"><rect width="32" height="32" rx="9" fill="var(--violet)"/><path d="M16 16 L16 5.5 A10.5 10.5 0 0 1 25.1 10.75 Z" fill="var(--bg)" opacity=".28"/><g fill="none" stroke="var(--bg)" stroke-linecap="round"><circle cx="16" cy="16" r="10.5" stroke-width="2" opacity=".6"/><circle cx="16" cy="16" r="5.6" stroke-width="2" opacity=".85"/><path d="M16 16 L25.1 10.75" stroke-width="2.4"/></g><circle cx="16" cy="16" r="2.3" fill="var(--bg)"/><circle cx="22.6" cy="21.4" r="2.2" fill="var(--bg)"/></g></svg></header>''' % (len(EP), len(EP), '<nav class="gsub" id="gsub" aria-label="Temi della guida"><ul class="chips">' + ''.join('<li><a class="chip topic" href="#%s">%s</a></li>' % (g[0], g[1]) for g in GROUPS) + '</ul></nav>')
idx = '<section class="ch" id="indice" style="padding-top:2.5rem"><div class="ch-head"><div class="kicker"><span class="chip topic">Indice</span></div><h2>Sei temi, %d puntate</h2><p class="lead">Scegli un tema, oppure cerca una parola in tutte le puntate.</p></div>' % len(EP)
idx += '<div class="gsearch" role="search"><label class="sr-only" for="gq">Cerca nelle puntate</label><input id="gq" type="search" placeholder="Cerca: costi, 429, Private Link, prompt injection…" autocomplete="off"><span class="gcount" id="gcount" aria-live="polite"></span></div>'
idx += '<div class="gindex">' + ''.join('<a href="#%s"><span class="chip topic">%s</span><b>%s</b><span class="n">%d puntate · %s</span></a>' % (g[0], g[1], g[2], sum(1 for e in EP if e[3] == g[0]), g[3]) for g in GROUPS) + '</div></section>'
body = ''
for gid, glab, gtitle, gdesc in GROUPS:
    body += '<section class="ch" id="%s"><div class="ch-head"><div class="kicker"><span class="chip topic">%s</span></div><h2>%s</h2><p class="lead">%s</p></div>' % (gid, glab, gtitle, gdesc)
    for n, ed, sid, g, short in [e for e in EP if e[3] == gid]:
        h2, lead, prose = extract(ed, sid)
        url = 'edizioni/%s.html#%s' % (ed, sid)
        body += ('<article class="card ep" data-text="%s"><div class="kicker"><span class="chip date">Puntata %d</span><span class="chip">Edizione %d</span></div>'
                 '<h3>%s</h3><p class="lead">%s</p>'
                 '<details><summary>Leggi la puntata</summary><div class="prose">%s</div></details>'
                 '<div class="eplinks"><a class="pri" href="%s">Apri con gli strumenti interattivi</a></div></article>') % (
                 html.escape(strip_tags(h2 + ' ' + lead + ' ' + prose).lower(), quote=True), n, int(ed), short, lead or html.escape(h2), prose, url)
    body += '</section>'
js = '''<script id="guida-js">(function(){
var q=document.getElementById('gq'),c=document.getElementById('gcount'),eps=[].slice.call(document.querySelectorAll('.ep'));
function run(){var v=(q.value||'').trim().toLowerCase();var n=0;eps.forEach(function(e){var ok=!v||e.dataset.text.indexOf(v)>=0;e.hidden=!ok;if(ok)n++;});
document.querySelectorAll('section.ch[id]').forEach(function(s){if(s.id==='indice')return;var any=s.querySelector('.ep:not([hidden])');s.hidden=!!v&&!any;});
c.textContent=v?(n+(n===1?' puntata trovata':' puntate trovate')):'';}
q.addEventListener('input',run);
var links=[].slice.call(document.querySelectorAll('#gsub a')),secs=links.map(function(a){return document.querySelector(a.getAttribute('href'))});
function onScroll(){var h=document.documentElement;var p=document.getElementById('prog');if(p)p.style.width=(h.scrollTop/(h.scrollHeight-h.clientHeight)*100)+'%';var cur=0;secs.forEach(function(s,i){if(s&&!s.hidden&&s.getBoundingClientRect().top<140)cur=i});links.forEach(function(a,i){a.classList.toggle('on',i===cur&&window.scrollY>200)})}
window.addEventListener('scroll',onScroll,{passive:true});onScroll();
})();</script>'''
foot = '<footer>Radar AI · Guida Azure Content Understanding · preparata da Claude (Anthropic).<br>I contenuti vengono dalle puntate pubblicate nelle edizioni, con le fonti ufficiali di Microsoft Learn indicate in ciascuna; ricontrolla le impostazioni sulla documentazione della tua versione prima di usarle in produzione.</footer>'
page = head + extra_css + '</head>\n<body>\n' + nav + hero + '<main class="wrap">' + idx + body + '</main>' + foot + js + '\n</body>\n</html>\n'
open(os.path.join(root, 'azure.html'), 'w', encoding='utf-8').write(page)
print('ok', len(page))
