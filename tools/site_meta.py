"""Radar AI: metadati e servizi del sito, secondo Google Search Central, W3C/WAI e GitHub Pages. Idempotente.

Uso (dalla radice del repository, dopo edx.py e audio_page.py, prima di inject.py):
  python3 tools/site_meta.py .

Fa:
- titolo descrittivo di ogni edizione ("Titolo · Radar AI, 19 ottobre 2026") e meta description (da tools/edx.py);
- canonical, link al feed, Open Graph e Twitter card, dati strutturati NewsArticle (JSON-LD);
- immagine di anteprima per ogni edizione (img/og/NN.png, 1200x630) e una generale (img/og/radar-ai.png);
- navigazione "edizione precedente / successiva" in fondo a ogni edizione;
- meta description, canonical e Open Graph anche sulle altre pagine;
- feed.xml (Atom, vale anche come sitemap per Google), sitemap.xml, 404.html.
Le date di pubblicazione stanno in tools/site_dates.json: una nuova edizione prende la data di tools/ultima.json.
"""
import datetime, glob, html, json, os, re, sys
from zoneinfo import ZoneInfo

SITE = 'https://notizieposts-web.github.io/notizieposts-web-newai/'
NAME = 'Radar AI'
TZ = ZoneInfo('Europe/Rome')
MESI = ['gennaio', 'febbraio', 'marzo', 'aprile', 'maggio', 'giugno', 'luglio', 'agosto',
        'settembre', 'ottobre', 'novembre', 'dicembre']

def esc(s):
    return html.escape(str(s), quote=True)

def short(s, n=160):
    s = re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', '', s))).strip()
    if len(s) <= n:
        return s
    cut = s[:n - 1].rsplit(' ', 1)[0].rstrip(',;:')
    return cut + '…'

def label(iso):
    y, m, d = iso.split('-')
    return '%d %s %s' % (int(d), MESI[int(m) - 1], y)

def stamp(iso, hour=9):
    dt = datetime.datetime(*map(int, iso.split('-')), hour, 0, tzinfo=TZ)
    return dt.isoformat()

# ---------------------------------------------------------------- immagini di anteprima
def og_image(root, path, kicker, title, chips):
    from PIL import Image, ImageDraw, ImageFont
    font = os.path.join(root, 'tools/fonts/Inter-Bold.otf')
    W, H, P = 1200, 630, 72
    im = Image.new('RGB', (W, H), '#3F3FD9')
    dr = ImageDraw.Draw(im)
    f_k = ImageFont.truetype(font, 28)
    dr.text((P, P), kicker.upper(), font=f_k, fill='#FFFFFF')
    size = 68
    while True:
        f_t = ImageFont.truetype(font, size)
        words, lines, cur = title.split(), [], ''
        for w in words:
            t = (cur + ' ' + w).strip()
            if dr.textlength(t, font=f_t) <= W - 2 * P:
                cur = t
            else:
                lines.append(cur); cur = w
        lines.append(cur)
        if len(lines) <= 4 or size <= 44:
            break
        size -= 4
    y = P + 70
    for ln in lines[:5]:
        dr.text((P, y), ln, font=f_t, fill='#FFFFFF')
        y += int(size * 1.18)
    f_c = ImageFont.truetype(font, 26)
    x, cy = P, H - P - 46
    for c in chips[:6]:
        w = dr.textlength(c, font=f_c) + 36
        if x + w > W - P:
            break
        dr.rounded_rectangle((x, cy, x + w, cy + 46), radius=23, outline='#FFFFFF', width=3)
        dr.text((x + 18, cy + 8), c, font=f_c, fill='#FFFFFF')
        x += w + 12
    os.makedirs(os.path.dirname(path), exist_ok=True)
    im.quantize(colors=32).save(path, optimize=True)

# ---------------------------------------------------------------- blocchi HTML
def head_block(title, desc, url, image, kind, ld=None):
    b = ['<!-- META -->',
         '<meta name="description" content="%s">' % esc(desc),
         '<link rel="canonical" href="%s">' % esc(url),
         '<link rel="alternate" type="application/atom+xml" title="Radar AI, tutte le edizioni" href="%sfeed.xml">' % SITE,
         '<meta property="og:site_name" content="%s">' % NAME,
         '<meta property="og:locale" content="it_IT">',
         '<meta property="og:type" content="%s">' % kind,
         '<meta property="og:title" content="%s">' % esc(title),
         '<meta property="og:description" content="%s">' % esc(desc),
         '<meta property="og:url" content="%s">' % esc(url),
         '<meta property="og:image" content="%s">' % esc(image),
         '<meta property="og:image:width" content="1200">',
         '<meta property="og:image:height" content="630">',
         '<meta property="og:image:alt" content="%s">' % esc(title),
         '<meta name="twitter:card" content="summary_large_image">']
    if ld:
        b.append('<script type="application/ld+json">%s</script>' % json.dumps(ld, ensure_ascii=False).replace('</', '<\\/'))
    b.append('<!-- /META -->')
    return '\n'.join(b) + '\n'

def put_head(s, block, title=None):
    s = re.sub(r'<!-- META -->.*?<!-- /META -->\n?', '', s, flags=re.S)
    if title:
        s = re.sub(r'<title>.*?</title>', '<title>%s</title>' % esc(title), s, count=1, flags=re.S)
    m = re.search(r'<meta name="viewport"[^>]*>\n?', s)
    pos = m.end() if m else s.index('</head>')
    return s[:pos] + block + s[pos:]

PAGER_CSS = ('<style id="pager-css">'
             '.ed-pager{max-width:72rem;margin:3rem auto 0;padding:0 1.2rem;display:grid;grid-template-columns:repeat(auto-fit,minmax(16rem,1fr));gap:1rem}'
             '.ed-pager a{display:flex;flex-direction:column;gap:.3rem;min-height:44px;padding:1rem 1.2rem;border:1px solid var(--line);border-radius:16px;'
             'background:var(--surface);color:var(--ink);text-decoration:none}'
             '.ed-pager a:hover .tt{text-decoration:underline}'
             '.ed-pager .dir{font-size:.85rem;font-weight:700;letter-spacing:.04em;color:var(--muted)}'
             '.ed-pager .tt{font-weight:700;line-height:1.35}'
             '.ed-pager .next{text-align:right}'
             '</style>')

def pager(prev, nxt):
    parts = []
    if prev:
        parts.append('<a class="prev" href="%s" rel="prev"><span class="dir"><span aria-hidden="true">&larr;</span> Edizione precedente</span><span class="tt">%s</span></a>' % prev)
    parts.append('<a class="all" href="../"><span class="dir">Archivio</span><span class="tt">Tutte le edizioni</span></a>')
    if nxt:
        parts.append('<a class="next" href="%s" rel="next"><span class="dir">Edizione successiva <span aria-hidden="true">&rarr;</span></span><span class="tt">%s</span></a>' % nxt)
    return '<!-- PAGER --><nav class="ed-pager" aria-label="Altre edizioni">%s</nav><!-- /PAGER -->' % ''.join(parts)

# ---------------------------------------------------------------- principale
def main(root):
    sys.path.insert(0, os.path.join(root, 'tools'))
    sys.argv = [sys.argv[0], root]
    import edx
    dates_p = os.path.join(root, 'tools/site_dates.json')
    dates = json.load(open(dates_p)) if os.path.exists(dates_p) else {}
    ult = json.load(open(os.path.join(root, 'tools/ultima.json'), encoding='utf-8'))
    eds = sorted(os.path.basename(f)[:-5] for f in glob.glob(os.path.join(root, 'edizioni/*.html')))
    today = datetime.datetime.now(TZ).date().isoformat()
    for n in eds:
        if n not in dates:
            dates[n] = ult['data'] if int(ult['n']) == int(n) else today
    json.dump(dates, open(dates_p, 'w'), indent=1)

    info = {}
    for n in eds:
        t, d = edx.EDX[n][1], edx.EDX[n][2]
        chips = edx.chips_for(n)
        info[n] = {'t': t, 'd': d, 'c': chips, 'date': dates[n]}

    # immagini
    gen = os.path.join(root, 'img/og/radar-ai.png')
    if not os.path.exists(gen):
        og_image(root, gen, 'Radar AI · newsletter in italiano', 'Le novità sull\'intelligenza artificiale, spiegate con esempi ed esperimenti', ['Edizioni', 'Argomenti', 'Azure', 'Laboratorio'])
    for n in eds:
        p = os.path.join(root, 'img/og/%s.png' % n)
        if not os.path.exists(p):
            og_image(root, p, 'Radar AI · %s' % label(info[n]['date']), info[n]['t'], info[n]['c'])

    # edizioni
    for i, n in enumerate(eds):
        f = os.path.join(root, 'edizioni/%s.html' % n)
        s = open(f, encoding='utf-8').read()
        x = info[n]
        url = SITE + 'edizioni/%s.html' % n
        img = SITE + 'img/og/%s.png' % n
        title = '%s · %s, %s' % (x['t'], NAME, label(x['date']))
        ld = {'@context': 'https://schema.org', '@type': 'NewsArticle', 'headline': x['t'], 'description': x['d'],
              'datePublished': stamp(x['date']), 'inLanguage': 'it-IT', 'isAccessibleForFree': True,
              'image': [img], 'mainEntityOfPage': url, 'url': url,
              'author': {'@type': 'Organization', 'name': NAME, 'url': SITE},
              'publisher': {'@type': 'Organization', 'name': NAME, 'url': SITE},
              'about': x['c']}
        s = put_head(s, head_block(title, x['d'], url, img, 'article', ld), title)
        s = re.sub(r'<style id="pager-css">.*?</style>', '', s, flags=re.S)
        s = s.replace('</head>', PAGER_CSS + '</head>', 1)
        s = re.sub(r'<!-- PAGER -->.*?<!-- /PAGER -->', '', s, flags=re.S)
        prev = ('%s.html' % eds[i - 1], esc(info[eds[i - 1]]['t'])) if i > 0 else None
        nxt = ('%s.html' % eds[i + 1], esc(info[eds[i + 1]]['t'])) if i + 1 < len(eds) else None
        s = s.replace('</main>', pager(prev, nxt) + '</main>', 1)
        open(f, 'w', encoding='utf-8').write(s)

    # altre pagine
    gen_img = SITE + 'img/og/radar-ai.png'
    for f in sorted(glob.glob(os.path.join(root, '*.html'))):
        name = os.path.basename(f)
        if name == '404.html':
            continue
        s = open(f, encoding='utf-8').read()
        t = re.search(r'<title>(.*?)</title>', s, flags=re.S).group(1).strip()
        m = re.search(r'<p class="sub">(.*?)</p>', s, flags=re.S) or re.search(r'<p class="lead">(.*?)</p>', s, flags=re.S)
        desc = short(m.group(1)) if m else 'Radar AI, la newsletter in italiano sulle novità dell\'intelligenza artificiale.'
        if name == 'index.html':
            desc = 'Tutte le edizioni di Radar AI, la newsletter in italiano sull\'intelligenza artificiale: notizie verificate, esempi, esperimenti e la rubrica su Azure.'
        url = SITE if name == 'index.html' else SITE + name
        s = put_head(s, head_block(html.unescape(t), desc, url, gen_img, 'website'))
        open(f, 'w', encoding='utf-8').write(s)

    # feed Atom (vale anche come sitemap delle edizioni)
    entries = []
    for n in reversed(eds):
        x = info[n]
        url = SITE + 'edizioni/%s.html' % n
        entries.append('<entry><title>%s</title><link href="%s"/><id>%s</id><updated>%s</updated><published>%s</published>'
                       '<summary>%s</summary>%s</entry>' % (esc(x['t']), url, url, stamp(x['date']), stamp(x['date']), esc(x['d']),
                       ''.join('<category term="%s"/>' % esc(c) for c in x['c'])))
    last = stamp(info[eds[-1]]['date'])
    feed = ('<?xml version="1.0" encoding="utf-8"?>\n<feed xmlns="http://www.w3.org/2005/Atom" xml:lang="it">\n'
            '<title>Radar AI</title><subtitle>La newsletter in italiano sull\'intelligenza artificiale</subtitle>'
            '<link href="%s"/><link rel="self" href="%sfeed.xml"/><id>%s</id><updated>%s</updated>'
            '<author><name>Radar AI</name></author>\n%s\n</feed>\n') % (SITE, SITE, SITE, last, '\n'.join(entries))
    open(os.path.join(root, 'feed.xml'), 'w', encoding='utf-8').write(feed)

    # sitemap: lastmod solo dove la data e' certa (le edizioni)
    urls = []
    for f in sorted(glob.glob(os.path.join(root, '*.html'))):
        name = os.path.basename(f)
        if name == '404.html':
            continue
        urls.append('<url><loc>%s</loc></url>' % (SITE if name == 'index.html' else SITE + name))
    for n in eds:
        urls.append('<url><loc>%sedizioni/%s.html</loc><lastmod>%s</lastmod></url>' % (SITE, n, info[n]['date']))
    open(os.path.join(root, 'sitemap.xml'), 'w', encoding='utf-8').write(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n%s\n</urlset>\n' % '\n'.join(urls))

    # 404
    latest = eds[-1]
    open(os.path.join(root, '404.html'), 'w', encoding='utf-8').write(PAGE_404 % {
        'site': SITE, 'latest': latest, 'lt': esc(info[latest]['t'])})
    print('meta', len(eds), 'edizioni; feed, sitemap e 404 aggiornati')

PAGE_404 = '''<!doctype html>
<html lang="it">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex">
<title>Pagina non trovata · Radar AI</title>
<style>
:root{--bg:#FFFFFF;--ink:#121A2B;--muted:#3B455C;--line:#D3D9E6;--violet:#3F3FD9;--surface:#F5F6FB}
@media (prefers-color-scheme: dark){:root{--bg:#0E1322;--ink:#F2F4FA;--muted:#C3CADB;--line:#2C3550;--violet:#A5A5FF;--surface:#161D31}}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font:1.05rem/1.6 system-ui,-apple-system,"Segoe UI",Roboto,Helvetica,Arial,sans-serif}
main{max-width:40rem;margin:0 auto;padding:4rem 1.2rem}
h1{font-size:2rem;line-height:1.2;margin:.4rem 0 1rem}
.k{font-weight:700;letter-spacing:.12em;text-transform:uppercase;font-size:.85rem;color:var(--muted);margin:0}
ul{list-style:none;padding:0;margin:1.5rem 0 0;display:grid;gap:.6rem}
a{display:flex;align-items:center;min-height:44px;padding:.6rem 1rem;border:1px solid var(--line);border-radius:14px;background:var(--surface);color:var(--ink);font-weight:700;text-decoration:none}
a:hover{text-decoration:underline}
a:focus-visible{outline:3px solid var(--violet);outline-offset:2px}
</style>
</head>
<body>
<main>
<p class="k">Radar AI</p>
<h1>Pagina non trovata</h1>
<p>L'indirizzo che hai aperto non esiste, o è stato scritto in modo diverso. Puoi ripartire da qui:</p>
<nav aria-label="Pagine principali">
<ul>
<li><a href="%(site)sedizioni/%(latest)s.html">Ultima edizione: %(lt)s</a></li>
<li><a href="%(site)s">Tutte le edizioni</a></li>
<li><a href="%(site)sargomenti.html">Argomenti</a></li>
<li><a href="%(site)sazure.html">Guida Azure Content Understanding</a></li>
<li><a href="%(site)sazure-laboratorio.html">Laboratorio</a></li>
</ul>
</nav>
</main>
</body>
</html>
'''

if __name__ == '__main__':
    main(os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else '.'))
