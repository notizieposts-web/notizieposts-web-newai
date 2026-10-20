"""Test del Laboratorio: python3 tools/arenatest.py <repo> [AAAA-MM-GG]   (data predefinita: l'ultimo pacchetto)
Deve stampare "fails [] 0".
1. Trasforma: la soluzione di riferimento JavaScript (Node) e Python passa tutti i test, visibili e nascosti.
2. Estrai e Confronta: risposte coerenti (enum tra le opzioni, valori "come scritto" presenti nel documento).
3. Partita nel browser (Playwright): ogni sfida del giorno si risolve con il punteggio pieno, senza errori JavaScript.
"""
import sys, os, json, glob, subprocess, threading, functools, http.server, socketserver, asyncio, re, html as H
root = os.path.abspath(sys.argv[1]); TOOLS = os.path.join(root, 'tools')
packs = sorted(glob.glob(os.path.join(TOOLS, 'arena', 'packs', '*.json')))
path = os.path.join(TOOLS, 'arena', 'packs', sys.argv[2] + '.json') if len(sys.argv) > 2 else packs[-1]
P = json.load(open(path, encoding='utf-8')); fails = []

def eq(a, b):
    if isinstance(a, bool) or isinstance(b, bool): return a == b
    if isinstance(a, (int, float)) and isinstance(b, (int, float)): return abs(a - b) <= 0.005
    if isinstance(a, dict) and isinstance(b, dict): return a.keys() == b.keys() and all(eq(a[k], b[k]) for k in a)
    if isinstance(a, list) and isinstance(b, list): return len(a) == len(b) and all(eq(x, y) for x, y in zip(a, b))
    return a == b

# 1. Trasforma
JS = r'''const P=JSON.parse(require('fs').readFileSync(process.argv[1]));function eq(a,b){if(typeof a==='number'&&typeof b==='number')return Math.abs(a-b)<=0.005;if(a===null||b===null||typeof a!=='object'||typeof b!=='object')return a===b;
if(Array.isArray(a)!==Array.isArray(b))return false;const ka=Object.keys(a),kb=Object.keys(b);return ka.length===kb.length&&ka.every(k=>eq(a[k],b[k]))}const bad=[];
for(const c of P.sfide.filter(c=>c.track==='trasforma')){const fn=new Function(c.ref_js+';return trasforma;')();c.visible.concat(c.hidden).forEach((t,i)=>{let o;try{o=fn(JSON.parse(JSON.stringify(t.in)))}catch(e){o='errore '+e.message}if(!eq(o,t.out))bad.push(c.id+':'+i)})}
console.log(JSON.stringify(bad))'''
out = subprocess.run(['node', '-e', JS, path], capture_output=True, text=True)
fails += ['js ' + x for x in (json.loads(out.stdout) if out.returncode == 0 else ['node: ' + out.stderr[:200]])]
for c in P['sfide']:
    if c['track'] != 'trasforma': continue
    ns = {}; exec(c['ref_py'], ns)
    for i, t in enumerate(c['visible'] + c['hidden']):
        if not eq(ns['trasforma'](json.loads(json.dumps(t['in']))), t['out']): fails.append('py %d:%d' % (c['id'], i))

# 2. coerenza
for c in P['sfide']:
    if c['track'] == 'trasforma': continue
    txt = H.unescape(re.sub('<[^>]+>', ' ', ' '.join(d['html'] for d in c['docs'])))
    labs = [f['label'] for f in c['fields']]
    if len(set(labs)) != len(labs): fails.append('campi doppi %d' % c['id'])
    for f in c['fields']:
        if f['type'] == 'enum' and f['ans'] not in f['opts']: fails.append('enum %d %s' % (c['id'], f['label']))
        if c['track'] == 'estrai' and f['meth'] == 'extract' and f['type'] == 'text' and str(f['ans']) not in txt: fails.append('assente %d %s' % (c['id'], f['label']))
    for d in c['docs']:
        if not d.get('dl') or not os.path.exists(os.path.join(root, d['dl'])): fails.append('pdf mancante %d' % c['id'])
    if not os.path.exists(os.path.join(root, 'lab', 'a%d.json' % c['id'])): fails.append('json mancante %d' % c['id'])

# 3. partita nel browser
class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
srv = socketserver.TCPServer(('127.0.0.1', 0), functools.partial(Q, directory=root)); port = srv.server_address[1]
threading.Thread(target=srv.serve_forever, daemon=True).start()
async def play():
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await b.new_page(viewport={'width': 1280, 'height': 900}); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.route(re.compile(r'^https?://(?!127\.0\.0\.1)'), lambda r: r.abort())
        for c in P['sfide']:
            f = {'estrai': 'lab-estrai.html', 'trasforma': 'lab-trasforma.html', 'confronta': 'lab-confronta.html'}[c['track']]
            try:
                await pg.goto('http://127.0.0.1:%d/%s#a%d' % (port, f, c['id'])); await pg.wait_for_selector('#ctitle', timeout=8000)
                if c['track'] == 'trasforma':
                    await pg.fill('#ed', c['ref_js']); await pg.click('#runall')
                    await pg.wait_for_function("/Test superati/.test(document.getElementById('tsum').textContent)", timeout=8000)
                    ok = '✓' in await pg.text_content('#tsum')
                else:
                    for i, fl in enumerate(c['fields']):
                        sel = '#f%d_%d' % (c['id'], i); v = fl['ans']
                        if fl['type'] == 'enum': await pg.select_option(sel, str(v))
                        else: await pg.fill(sel, ('%.2f' % v).replace('.', ',') if fl['type'] == 'num' else str(v))
                        if c['track'] == 'estrai': await pg.check('input[name="m%d"][value="%s"]' % (i, fl['meth']))
                    await pg.click('#ff button[type=submit]'); ok = 'Tutto giusto' in await pg.text_content('#fsum')
                if not ok: fails.append('partita %d' % c['id'])
            except Exception as e:
                fails.append('partita %d %s' % (c['id'], str(e)[:80]))
        fails.extend('js-pagina ' + e[:100] for e in errs)
        await b.close()
asyncio.run(play()); srv.shutdown()
print('pacchetto', P['giorno'], 'sfide', len(P['sfide']))
print('fails', fails[:20], len(fails))
