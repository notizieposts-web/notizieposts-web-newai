"""Glossario delle edizioni: termini cliccabili nelle pagine e pagina glossario.html con tutte le voci.

Nella pagina si scrive solo il segnaposto, alla PRIMA occorrenza del termine:
    <span class="gl" data-gl="mfu">MFU</span>
La chiave (data-gl) deve esistere in tools/glossario.json:
    "mfu": {"t": "MFU", "esteso": "Model FLOPs Utilization", "spiega": "...", "esempio": "...",
            "approfondisci": "...", "vedi": ["tpu"]}
("esteso", "approfondisci" e "vedi" sono facoltativi). Lo script:
  1. trasforma il segnaposto in un pulsante con scheda (spiegazione breve, esempio, link
     "Approfondisci nel glossario" che porta a glossario.html#g-<chiave> e ricorda il punto di partenza);
  2. aggiunge nell'intestazione di ogni edizione con termini il chip "Glossario: N termini";
  3. genera glossario.html (voci in ordine alfabetico, spiegazione estesa, voci collegate,
     "Dove compare" con i link a ogni occorrenza, termini raggruppati per edizione).
Comportamento (clic, Esc, aria-expanded, apertura al ritorno dal glossario) e stile delle schede
vengono da tools/inject.py. Idempotente: si può rilanciare.
Uso: python3 tools/glossario.py <repo>   (si ferma con errore se una chiave non esiste)
"""
import re, sys, os, json, html

HERE = os.path.dirname(os.path.abspath(__file__))
root = sys.argv[1] if len(sys.argv) > 1 else '.'
data = json.load(open(os.path.join(root, 'tools', 'glossario.json'), encoding='utf-8'))
for k, v in data.items():
    assert re.fullmatch(r'[a-z0-9-]+', k), 'chiave non valida: %s' % k
    assert v.get('t') and v.get('spiega') and v.get('esempio'), 'voce incompleta: %s' % k
    for r in v.get('vedi', []):
        assert r in data, 'voce %s: "vedi" punta a una chiave assente (%s)' % (k, r)

DONE = re.compile(r'<span class="gl" data-gl="([a-z0-9-]+)" data-gl-done><button[^>]*>(.*?)<span class="sr-only">.*?<!--/gl--></span>', re.S)
RAW = re.compile(r'<span class="gl" data-gl="([a-z0-9-]+)">([^<]+)</span>')
CHIP = re.compile(r'<!-- GLCHIP -->.*?<!-- /GLCHIP -->', re.S)
e = html.escape

def head_of(v):
    return '<b>%s</b>' % e(v['t']) + (' (%s)' % e(v['esteso']) if v.get('esteso') else '')

def build(n, i, key, text):
    v = data.get(key)
    if v is None:
        sys.exit('glossario: chiave "%s" assente in tools/glossario.json (edizione %s)' % (key, n))
    tid = 'gl-%s-%d' % (n, i)
    return ('<span class="gl" data-gl="%s" data-gl-done><button type="button" class="gl-btn" id="glb-%s-%d" aria-expanded="false" aria-controls="%s">%s'
            '<span class="sr-only">: che cos\'è</span><span class="gl-ico" aria-hidden="true">?</span></button>'
            '<span class="gl-tip" id="%s" role="note" hidden>%s. %s'
            '<span class="gl-ex"><b>Esempio:</b> %s</span>'
            '<span class="gl-act"><a class="gl-more" href="../glossario.html?da=%s-%d#g-%s">Approfondisci nel glossario<span class="sr-only">: %s</span></a>'
            '<button type="button" class="gl-close">Chiudi</button></span></span><!--/gl--></span>'
            % (key, n, i, tid, text, tid, head_of(v), e(v['spiega']), e(v['esempio']), n, i, key, e(v['t'])))

def chapters(s):
    """id capitolo -> voce del menu dell'edizione."""
    m = re.search(r'<div class="links" id="links">(.*?)</div>', s, re.S)
    return dict(re.findall(r'<a href="#([^"]+)">([^<]+)</a>', m.group(1))) if m else {}

occ = {}      # chiave -> [(n, i, capitolo)]
per_ed = {}   # n -> [chiavi in ordine]
tot = 0
for f in sorted(os.listdir(os.path.join(root, 'edizioni'))):
    if not f.endswith('.html'):
        continue
    n = f[:-5]
    p = os.path.join(root, 'edizioni', f)
    s = open(p, encoding='utf-8').read()
    s0 = s
    s = DONE.sub(lambda m: '<span class="gl" data-gl="%s">%s</span>' % (m.group(1), m.group(2)), s)
    caps = chapters(s)
    c = [0]
    def rep(m):
        c[0] += 1
        sec = [x for x in re.finditer(r'<section class="ch" id="([^"]+)"', s[:m.start()])]
        cid = sec[-1].group(1) if sec else ''
        occ.setdefault(m.group(1), []).append((n, c[0], caps.get(cid, '')))
        per_ed.setdefault(n, [])
        if m.group(1) not in per_ed[n]:
            per_ed[n].append(m.group(1))
        return build(n, c[0], m.group(1), m.group(2))
    s = RAW.sub(rep, s)
    tot += c[0]
    s = CHIP.sub('', s)
    if c[0]:
        chip = ('<!-- GLCHIP --><a class="chip gl-chip" href="../glossario.html#ed-%s">Glossario: %d %s</a><!-- /GLCHIP -->'
                % (n, len(per_ed[n]), 'termine' if len(per_ed[n]) == 1 else 'termini'))
        s = re.sub(r'(<header class="hero">\s*<div>\s*<div class="meta">.*?)(</div>)', lambda m: m.group(1) + chip + m.group(2), s, count=1, flags=re.S)
    if s != s0:
        open(p, 'w', encoding='utf-8').write(s)

# ---- pagina glossario.html ----
sys.path.insert(0, HERE)
import argomenti, graph

def sort_key(k):
    import unicodedata
    t = unicodedata.normalize('NFD', data[k]['t']).encode('ascii', 'ignore').decode().lower()
    return t

keys = sorted(data, key=sort_key)
letters = []
for k in keys:
    L = sort_key(k)[:1].upper()
    if L not in letters:
        letters.append(L)

CSS = '''<style id="glp-css">
.glidx{display:flex;flex-wrap:wrap;gap:.4rem;margin:1rem 0 0;padding:0;list-style:none}
.glidx a{display:inline-flex;align-items:center;justify-content:center;min-width:44px;min-height:44px;padding:0 .7rem;border-radius:12px;border:1px solid var(--line);background:var(--surface);color:var(--ink);font-weight:700;text-decoration:none}
.glidx a:hover{border-color:var(--violet);text-decoration:underline}
.glback{display:none;margin:1.2rem 0 0;padding:.9rem 1.1rem;border:2px solid var(--violet);border-radius:14px;background:var(--violet-soft);color:var(--ink)}
.glback.on{display:block}.glback a{font-weight:700;color:var(--ink)}
.glterm{scroll-margin-top:9rem;margin-top:1rem;max-width:52rem}
.glterm:target{outline:3px solid var(--violet);outline-offset:3px}
.glterm h3{font-size:1.35rem;margin:0}.glterm .esteso{margin:.2rem 0 .6rem;color:var(--muted);font-weight:600}
.glterm h4{font-size:.85rem;letter-spacing:.06em;text-transform:uppercase;color:var(--muted);margin:1rem 0 .3rem}
.glterm p{margin:.2rem 0}.glterm ul{margin:.2rem 0;padding-left:1.2rem}.glterm li{margin:.2rem 0}
.glterm .tback{margin-top:.8rem}
.gllet{font-size:1.6rem;margin:2rem 0 .2rem;scroll-margin-top:9rem}
.gled{margin-top:1rem;max-width:52rem}.gled h3{font-size:1.15rem;margin:0 0 .4rem;scroll-margin-top:9rem}
</style>'''

JS = '''<script id="glp-js">(function(){
var m=/[?&]da=(\\d{1,3})-(\\d{1,3})(?:&|$)/.exec(location.search);if(!m)return;
var href='edizioni/'+m[1]+'.html#glb-'+m[1]+'-'+m[2],txt='Torna all\\'edizione '+m[1]+', al punto in cui eri';
var b=document.getElementById('glback');if(b){b.querySelector('a').setAttribute('href',href);b.querySelector('a').textContent=txt;b.classList.add('on');}
var t=location.hash&&document.getElementById(location.hash.slice(1));
if(t&&t.classList.contains('glterm')){var p=document.createElement('p');p.className='tback';var a=document.createElement('a');a.href=href;a.textContent='\\u2190 '+txt;p.appendChild(a);t.appendChild(p);}
})();</script>'''

def ed_label(n, cap):
    return 'Edizione %d%s' % (int(n), (', capitolo %s' % cap) if cap else '')

body = ('<section class="ch" id="voci" style="padding-top:2rem"><div class="ch-head"><div class="kicker"><span class="chip guide">Glossario</span></div>'
        '<h2>Le voci, dalla A alla Z</h2><p class="lead">Ogni voce ha la spiegazione breve che vedi nelle edizioni, una spiegazione più completa, un esempio e i link ai punti delle edizioni in cui compare.</p>'
        '<div class="glback" id="glback" role="region" aria-label="Ritorno all\'edizione"><a href="index.html">Torna all\'edizione</a></div>'
        '<nav aria-label="Lettere del glossario"><ul class="glidx">%s</ul></nav></div>') % ''.join('<li><a href="#lettera-%s">%s</a></li>' % (L.lower(), L) for L in letters)
cur = None
for k in keys:
    v = data[k]
    L = sort_key(k)[:1].upper()
    if L != cur:
        body += '<h2 class="gllet" id="lettera-%s">%s</h2>' % (L.lower(), L)
        cur = L
    body += '<article class="card glterm" id="g-%s" aria-labelledby="gt-%s"><h3 id="gt-%s">%s</h3>' % (k, k, k, e(v['t']))
    if v.get('esteso'):
        body += '<p class="esteso" lang="en">%s</p>' % e(v['esteso'])
    body += '<h4>In breve</h4><p>%s</p>' % e(v['spiega'])
    if v.get('approfondisci'):
        body += '<h4>Più nel dettaglio</h4><p>%s</p>' % e(v['approfondisci'])
    body += '<h4>Esempio</h4><p>%s</p>' % e(v['esempio'])
    if v.get('vedi'):
        body += '<h4>Voci collegate</h4><p>%s</p>' % ' · '.join('<a href="#g-%s">%s</a>' % (r, e(data[r]['t'])) for r in v['vedi'])
    oc = occ.get(k, [])
    if oc:
        body += '<h4>Dove compare</h4><ul>%s</ul>' % ''.join('<li><a href="edizioni/%s.html#glb-%s-%d">%s</a></li>' % (n, n, i, e(ed_label(n, cap))) for n, i, cap in oc)
    body += '</article>'
body += '</section>'
if per_ed:
    body += ('<section class="ch" id="per-edizione"><div class="ch-head"><div class="kicker"><span class="chip guide">Edizioni</span></div>'
             '<h2>I termini di ogni edizione</h2><p class="lead">Dalla più recente.</p></div>')
    for n in sorted(per_ed, key=int, reverse=True):
        body += '<div class="card gled"><h3 id="ed-%s"><a href="edizioni/%s.html">Edizione %d</a></h3><p>%s</p></div>' % (
            n, n, int(n), ' · '.join('<a href="#g-%s">%s</a>' % (k, e(data[k]['t'])) for k in per_ed[n]))
    body += '</section>'

desc = 'Gli acronimi e i termini tecnici delle edizioni di Radar AI, spiegati in parole semplici con un esempio concreto e i link ai punti in cui compaiono.'
hero = ('<header class="hero"><div><div class="meta"><span class="chip guide">Glossario</span><span class="chip date">%d voci</span></div>'
        '<h1 style="margin-top:1.2rem">Glossario: acronimi e termini tecnici</h1>'
        '<p class="sub">%s Nelle edizioni i termini sono sottolineati a puntini con un punto di domanda: toccali per la spiegazione breve, poi "Approfondisci nel glossario" per arrivare qui e tornare al punto in cui eri.</p></div>%s</header>') % (len(data), desc, argomenti.MARK)
eds = graph.data(root)
page = argomenti.page(argomenti.head_from(root, 'Glossario', 'glossario.html', desc) + CSS, argomenti.NAV('glossario.html', eds), hero, body)
page = page.replace('</body>', JS + '\n</body>', 1)
open(os.path.join(root, 'glossario.html'), 'w', encoding='utf-8').write(page)
print('glossario: %d termini, %d voci nel dizionario, glossario.html scritto' % (tot, len(data)))
