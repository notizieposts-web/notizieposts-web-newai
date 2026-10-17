"""Sezione Argomenti: pagina indice + una pagina per ogni tema cardine della mappa + guide (es. Azure CU).
Tutte le pagine condividono lo stesso menu (NAV). Uso: python3 argomenti.py <repo>"""
import re, sys, os, html, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import graph

# Guide: pagine di approfondimento fatte a mano. 'eds' = edizioni collegate (per la mappa).
GUIDES = [
 {'id': 'cu', 'menu': 'Azure', 'c': 'Guida Content Understanding', 'u': 'azure.html',
  'title': 'Azure Content Understanding', 'eds': list(range(7, 24)),
  's': 'Tutte le puntate della rubrica fissa, ordinate per tema: costi, pipeline, qualità, sicurezza, produzione e casi reali.', 'n': '19 puntate'},
 {'id': 'cu-ex', 'menu': 'Esercizi', 'c': 'Palestra Content Understanding', 'u': 'azure-esercizi.html', 'map': False,
  'title': 'Palestra Content Understanding', 'eds': list(range(7, 24)),
  's': 'Oltre mille esercizi a tre livelli, media, alta ed estrema, con verifica immediata e soluzione spiegata.', 'n': '%s esercizi'},
 {'id': 'cu-lab', 'menu': 'Laboratorio', 'c': 'Laboratorio Content Understanding', 'u': 'azure-laboratorio.html', 'map': False,
  'title': 'Laboratorio Content Understanding', 'eds': list(range(7, 24)),
  's': 'Il gioco pratico: estrai e trasforma da documenti veri, ottimizza prompt e schemi, taglia i costi, trova vulnerabilità e guasti.', 'n': 'sfide'},
]
try:
    from lab_gen import CH as _CH
    GUIDES[2]['n'] = '%d sfide' % len(_CH)
except Exception:
    pass
try:
    from esercizi_gen import EX as _EX, it as _it
    GUIDES[1]['n'] = GUIDES[1]['n'] % _it(len(_EX))
except Exception:
    GUIDES[1]['n'] = 'esercizi'
# Temi cardine (i nodi evidenziati della mappa): slug, descrizione (<=160)
THEME_INFO = {
 'Sicurezza': ('sicurezza', 'Attacchi, difese e controlli su agenti e modelli: dalle istruzioni nascoste alle sandbox.'),
 'Grandi modelli': ('grandi-modelli', 'I lanci dei modelli di frontiera: cosa cambia davvero e come si confrontano tra loro.'),
 'Pesi aperti': ('pesi-aperti', 'Modelli scaricabili da usare in casa: licenze, hardware necessario e prestazioni.'),
 'Costi': ('costi', 'Prezzi, consumi e modi concreti di pagare meno a parità di risultato.'),
 'Ricerca': ('ricerca', 'Paper e risultati di laboratorio che spiegano dove sta andando la tecnologia.'),
 'Regole': ('regole', 'Leggi e autorità: AI Act, FTC e cosa chiedono concretamente alle aziende.'),
 'Decisionali': ('decisionali', 'Modelli che decidono senza scrivere testo, e quadri per scegliere quale modello usare.'),
 'Hardware': ('hardware', 'Chip, GPU e macchine: cosa serve per far girare i modelli e quanto costa.'),
 'Valutazione': ('valutazione', 'Benchmark e test: come si misura un modello e quanto fidarsi dei numeri.'),
}
for k, v in THEME_INFO.items():
    assert len(v[1]) <= 160, k

GENERIC = ['Costi','Benchmark','Confronto','Laboratori','Architetture','Settembre','Ricerca','Hardware','Open source','Guardrail','Audizione','Decisionali','Incidenti','Valutatori','Codice','Robot','Privacy','MoE','Piste']
def theme_url(t): return 'tema-%s.html' % THEME_INFO[t][0]

def themes(eds):
    cnt = {}
    for e in eds:
        for t in e['m']: cnt[t] = cnt.get(t, 0) + 1
    return [t for t in sorted(cnt, key=lambda t: (-cnt[t], t)) if cnt[t] > 1 and t in THEME_INFO], cnt

def NAV(cur, eds):
    ts, _ = themes(eds)
    items = [('argomenti.html', 'Argomenti')] + [(g['u'], g['menu']) for g in GUIDES] + [(theme_url(t), t) for t in ts]
    a = ''.join('<a href="%s"%s>%s</a>' % (u, ' aria-current="page" class="on"' if u == cur else '', html.escape(l)) for u, l in items)
    return ('<nav class="nav" aria-label="Argomenti"><div class="nav-in"><a class="brand" href="./">Radar AI</a>'
            '<div class="links" id="links">%s</div></div><div class="progress" id="prog"></div></nav>') % a

CSS = '''<style id="arg-css">
.nav .links a[aria-current="page"]{background:var(--ink);color:var(--bg)}
.argrid{display:grid;grid-template-columns:repeat(auto-fill,minmax(min(100%,17rem),1fr));gap:1rem;margin-top:1.4rem}
.argcard{display:flex;flex-direction:column;gap:.45rem;padding:1.2rem 1.25rem!important;text-decoration:none;color:var(--ink)}
a.argcard:hover{border-color:var(--violet)}
.argcard h3{font-size:1.15rem;margin:.1rem 0}.argcard p{margin:0;font-size:.95rem;color:var(--muted)}
.argcard .meta2{font-size:.85rem;color:var(--muted);margin-top:auto;padding-top:.3rem}
.chips{list-style:none;padding:0;margin:.2rem 0 0;display:flex;flex-wrap:wrap;gap:.35rem}
.chips li{display:flex}
.chip.theme{background:var(--sun-soft)!important;color:var(--ink)!important;border:1px solid var(--sun)!important}
.chip.guide{background:var(--teal-soft)!important;color:var(--ink)!important;border:1px solid var(--teal)!important}
a.chip{text-decoration:none;min-height:24px;display:inline-flex;align-items:center}
a.chip:hover{outline:2px solid var(--violet);outline-offset:1px}
.edrow{margin-top:1rem;max-width:52rem}.edrow h3{font-size:1.2rem;margin:.5rem 0 .35rem}.edrow h3 a{color:var(--ink)}
.edrow p{margin:.2rem 0 .5rem}
.side2{display:grid;grid-template-columns:repeat(auto-fill,minmax(min(100%,18rem),1fr));gap:1rem;margin-top:1.4rem}
.side2 h3{font-size:.85rem;letter-spacing:.08em;text-transform:uppercase;color:var(--muted);margin:0 0 .5rem}
@media (max-width:860px){.hero .radar{display:none}}
</style>'''

def head_from(root, title):
    src = open(os.path.join(root, 'edizioni', '23.html'), encoding='utf-8').read()
    head = src[:src.index('<body')]
    head = re.sub(r'<title>.*?</title>', '<title>%s · Radar AI</title>' % html.escape(title), head)
    head = re.sub(r'<style id="(a11y|egraph-css|edx-css|arg-css)">.*?</style>', '', head, flags=re.S)
    head = re.sub(r'<script id="a11y-theme">.*?</script>', '', head, flags=re.S)
    head = re.sub(r'<link rel="icon"[^>]*>', '', head)
    return head + CSS

MARK = '<svg class="radar" viewBox="0 0 400 400" aria-hidden="true"><g transform="translate(80 80) scale(7.5)"><rect width="32" height="32" rx="9" fill="var(--violet)"/><path d="M16 16 L16 5.5 A10.5 10.5 0 0 1 25.1 10.75 Z" fill="var(--bg)" opacity=".28"/><g fill="none" stroke="var(--bg)" stroke-linecap="round"><circle cx="16" cy="16" r="10.5" stroke-width="2" opacity=".6"/><circle cx="16" cy="16" r="5.6" stroke-width="2" opacity=".85"/><path d="M16 16 L25.1 10.75" stroke-width="2.4"/></g><circle cx="16" cy="16" r="2.3" fill="var(--bg)"/><circle cx="22.6" cy="21.4" r="2.2" fill="var(--bg)"/></g></svg>'
JS = '''<script id="arg-js">(function(){var p=document.getElementById('prog');function f(){var h=document.documentElement;if(p)p.style.width=(h.scrollTop/Math.max(1,h.scrollHeight-h.clientHeight)*100)+'%';}window.addEventListener('scroll',f,{passive:true});f();
var on=document.querySelector('.nav .links a[aria-current]');if(on)setTimeout(function(){var l=on.parentElement;l.scrollLeft=on.offsetLeft-l.clientWidth/2+on.offsetWidth/2},50);})();</script>'''
FOOT = '<footer>Radar AI · preparata da Claude (Anthropic). Quando una notizia riguarda Anthropic, lo trovi segnalato nella pagina.</footer>'

def page(head, nav, hero, body):
    return head + '</head>\n<body>\n' + nav + hero + '<main class="wrap">' + body + '</main>' + FOOT + JS + '\n</body>\n</html>\n'

def chips(items, label):
    return '<ul class="chips" aria-label="%s">%s</ul>' % (label, ''.join('<li>%s</li>' % i for i in items))

def edrow(e):
    title = html.escape(e['t'])
    h = '<a href="%s">%s</a>' % (e['u'], title) if e['u'] else title
    th = [('<a class="chip theme" href="%s">%s</a>' % (theme_url(t), html.escape(t))) if t in THEME_INFO else '<span class="chip theme">%s</span>' % html.escape(t) for t in e['m']]
    pr = ['<span class="chip topic">%s</span>' % html.escape(c) for c in e['c']]
    return ('<article class="card edrow"><div class="kicker"><span class="chip date">%s</span><span class="chip">Edizione %d</span></div>'
            '<h3>%s</h3><p>%s</p>%s%s%s</article>') % (html.escape(e['d']), e['n'], h, html.escape(e['s']),
            chips(pr, 'Protagonisti'), chips(th, 'Temi'), '' if e['u'] else '<p class="note">Solo email, senza pagina.</p>')

def build(root):
    eds = graph.data(root)
    ts, cnt = themes(eds)
    out = {}
    # indice
    hero = ('<header class="hero"><div><div class="meta"><span class="chip topic">Argomenti</span><span class="chip date">%d temi · %d guida</span></div>'
            '<h1 style="margin-top:1.2rem">Argomenti: le edizioni raccolte per tema</h1>'
            '<p class="sub">I temi cardine della mappa, ognuno con la sua pagina, e le guide di approfondimento. Il menu in alto resta lo stesso in tutte queste pagine.</p></div>%s</header>') % (len(ts), len(GUIDES), MARK)
    body = '<section class="ch" id="guide" style="padding-top:2.5rem"><div class="ch-head"><div class="kicker"><span class="chip guide">Guide</span></div><h2>Guide di approfondimento</h2><p class="lead">Una rubrica intera, riordinata per tema, in una pagina sola.</p></div><div class="argrid">'
    for g in GUIDES:
        body += '<a class="card argcard" href="%s"><span><span class="chip guide">%s</span></span><h3>%s</h3><p>%s</p><span class="meta2">%s · edizioni dalla %d alla %d</span></a>' % (g['u'], g['menu'], g['title'], g['s'], g.get('n', ''), g['eds'][0], g['eds'][-1])
    body += '</div></section><section class="ch" id="temi"><div class="ch-head"><div class="kicker"><span class="chip theme">Temi</span></div><h2>I temi cardine</h2><p class="lead">Sono i temi evidenziati nella mappa delle edizioni, dal più ricorrente.</p></div><div class="argrid">'
    for t in ts:
        last = max((e for e in eds if t in e['m']), key=lambda e: e['n'])
        body += '<a class="card argcard" href="%s"><span><span class="chip theme">%s</span></span><h3>%s</h3><p>%s</p><span class="meta2">%d edizioni · ultima: n. %d, %s</span></a>' % (theme_url(t), html.escape(t), html.escape(t), THEME_INFO[t][1], cnt[t], last['n'], html.escape(last['d']))
    body += '</div></section>'
    out['argomenti.html'] = page(head_from(root, 'Argomenti'), NAV('argomenti.html', eds), hero, body)
    # pagine tema
    for t in ts:
        url = theme_url(t)
        lst = sorted([e for e in eds if t in e['m']], key=lambda e: -e['n'])
        co, pr = {}, {}
        for e in lst:
            for x in e['m']:
                if x != t: co[x] = co.get(x, 0) + 1
            for c in e['c']: pr[c] = pr.get(c, 0) + 1
        co = sorted(co, key=lambda x: -co[x]); prl = [c for c in sorted(pr, key=lambda c: -pr[c]) if pr[c] > 1 and c not in GENERIC][:10]
        gl = [g for g in GUIDES if set(g['eds']) & {e['n'] for e in lst}]
        hero = ('<header class="hero"><div><div class="meta"><span class="chip theme">Tema</span><span class="chip date">%d edizioni</span></div>'
                '<h1 style="margin-top:1.2rem">%s</h1><p class="sub">%s</p></div>%s</header>') % (len(lst), html.escape(t), THEME_INFO[t][1], MARK)
        side = '<div class="side2">'
        side += '<div class="card"><h3>Temi vicini</h3>%s</div>' % chips([('<a class="chip theme" href="%s">%s</a>' % (theme_url(x), html.escape(x))) if x in ts else '<span class="chip theme">%s</span>' % html.escape(x) for x in co], 'Temi vicini')
        if prl: side += '<div class="card"><h3>Protagonisti ricorrenti</h3>%s</div>' % chips(['<span class="chip topic">%s</span>' % html.escape(c) for c in prl], 'Protagonisti ricorrenti')
        if gl: side += '<div class="card"><h3>Guide collegate</h3>%s</div>' % chips(['<a class="chip guide" href="%s">%s</a>' % (g['u'], g['title']) for g in gl], 'Guide collegate')
        side += '</div>'
        body = ('<section class="ch" id="edizioni" style="padding-top:2.5rem"><div class="ch-head"><div class="kicker"><span class="chip theme">%s</span></div><h2>Le edizioni su questo tema</h2>'
                '<p class="lead">Dalla più recente. Tocca il titolo per aprire l\'edizione.</p></div>%s%s</section>') % (html.escape(t), side, ''.join(edrow(e) for e in lst))
        out[url] = page(head_from(root, t), NAV(url, eds), hero, body)
    menu = [{'u': 'argomenti.html', 'l': 'Tutti gli argomenti', 'k': 'all'}] + \
           [{'u': g['u'], 'l': g['title'], 'k': 'guide', 'n': g.get('n', '')} for g in GUIDES] + \
           [{'u': theme_url(t), 'l': t, 'k': 'theme', 'n': '%d edizioni' % cnt[t]} for t in ts]
    json.dump(menu, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'topics_menu.json'), 'w', encoding='utf-8'), ensure_ascii=False)
    for f, s in out.items():
        open(os.path.join(root, f), 'w', encoding='utf-8').write(s)
    # guida Azure: menu argomenti in alto, menu interno come riga di chip
    p = os.path.join(root, 'azure.html'); s = open(p, encoding='utf-8').read()
    s = re.sub(r'<nav class="nav".*?</nav>', lambda m: NAV('azure.html', eds), s, count=1, flags=re.S)
    if 'arg-css' not in s: s = s.replace('</head>', CSS + '</head>', 1)
    open(p, 'w', encoding='utf-8').write(s)
    return list(out) + ['azure.html']

if __name__ == '__main__':
    print(build(sys.argv[1]))
