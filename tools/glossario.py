"""Glossario delle edizioni: trasforma i termini marcati nella pagina in un pulsante con scheda accessibile.

Nella pagina si scrive solo il segnaposto, alla PRIMA occorrenza del termine:
    <span class="gl" data-gl="mfu">MFU</span>
La chiave (data-gl) deve esistere in tools/glossario.json:
    "mfu": {"t": "MFU", "esteso": "Model FLOPs Utilization", "spiega": "...", "esempio": "..."}
("esteso" è facoltativo). Lo script genera il pulsante e la scheda; il comportamento (clic, Esc,
aria-expanded) e lo stile vengono da tools/inject.py. Idempotente: si può rilanciare.
Uso: python3 tools/glossario.py <repo>   (si ferma con errore se una chiave non esiste)
"""
import re, sys, os, json, html

root = sys.argv[1] if len(sys.argv) > 1 else '.'
data = json.load(open(os.path.join(root, 'tools', 'glossario.json'), encoding='utf-8'))
for k, v in data.items():
    assert re.fullmatch(r'[a-z0-9-]+', k), 'chiave non valida: %s' % k
    assert v.get('t') and v.get('spiega') and v.get('esempio'), 'voce incompleta: %s' % k

DONE = re.compile(r'<span class="gl" data-gl="([a-z0-9-]+)" data-gl-done><button[^>]*>(.*?)<span class="sr-only">.*?<!--/gl--></span>', re.S)
RAW = re.compile(r'<span class="gl" data-gl="([a-z0-9-]+)">([^<]+)</span>')
e = html.escape

def build(n, i, key, text):
    v = data.get(key)
    if v is None:
        sys.exit('glossario: chiave "%s" assente in tools/glossario.json (edizione %s)' % (key, n))
    tid = 'gl-%s-%d' % (n, i)
    head = '<b>%s</b>' % e(v['t']) + (' (%s)' % e(v['esteso']) if v.get('esteso') else '')
    return ('<span class="gl" data-gl="%s" data-gl-done><button type="button" class="gl-btn" aria-expanded="false" aria-controls="%s">%s'
            '<span class="sr-only">: che cos\'è</span></button><span class="gl-tip" id="%s" role="note" hidden>%s. %s'
            '<span class="gl-ex"><b>Esempio:</b> %s</span><button type="button" class="gl-close">Chiudi</button></span><!--/gl--></span>'
            % (key, tid, text, tid, head, e(v['spiega']), e(v['esempio'])))

tot = 0
for f in sorted(os.listdir(os.path.join(root, 'edizioni'))):
    if not f.endswith('.html'):
        continue
    n = f[:-5]
    p = os.path.join(root, 'edizioni', f)
    s = open(p, encoding='utf-8').read()
    s0 = s
    s = DONE.sub(lambda m: '<span class="gl" data-gl="%s">%s</span>' % (m.group(1), m.group(2)), s)
    c = [0]
    def rep(m):
        c[0] += 1
        return build(n, c[0], m.group(1), m.group(2))
    s = RAW.sub(rep, s)
    tot += c[0]
    if s != s0:
        open(p, 'w', encoding='utf-8').write(s)
print('glossario: %d termini, %d voci nel dizionario' % (tot, len(data)))
