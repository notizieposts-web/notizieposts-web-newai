"""Radar AI: costruisce l'email dell'edizione dal modello tools/mail_template_teaser.html e da tools/ultima.json.

Uso:
  python3 tools/mail_build.py OUT.html                 # email standard
  python3 tools/mail_build.py OUT.html --precedente    # aggiunge il link all'edizione precedente (destinatari a giorni alterni)
  python3 tools/mail_build.py OUT.html --audio si|no   # forza il blocco audio (predefinito: si se la Release audio-NN ha l'MP3)

Regola: l'HTML dell'email si costruisce SOLO cosi'. Non riusare mai l'HTML di un'email letta da Gmail:
Gmail riscrive i link in https://www.google.com/url?q=... e toglie gli sfondi. Lo script si ferma se trova
link che non portano direttamente al sito o al repository.
"""
import html, json, os, re, subprocess, sys

SITE = 'https://notizieposts-web.github.io/notizieposts-web-newai/'
REPO = 'https://github.com/notizieposts-web/notizieposts-web-newai'
MESI = ['GENNAIO', 'FEBBRAIO', 'MARZO', 'APRILE', 'MAGGIO', 'GIUGNO', 'LUGLIO', 'AGOSTO',
        'SETTEMBRE', 'OTTOBRE', 'NOVEMBRE', 'DICEMBRE']
WPM = 145

def e(s):
    return html.escape(str(s), quote=False)

def ents(s):
    return ''.join(c if ord(c) < 128 else '&#%d;' % ord(c) for c in s if ord(c) != 0xFE0F)

def audio_exists(n):
    # 302 = il file esiste (GitHub rimanda al download), 404 = non ancora pubblicato
    url = '%s/releases/download/audio-%d/radar-ai-%d.mp3' % (REPO, n, n)
    try:
        out = subprocess.run(['curl', '-sI', '-o', '/dev/null', '-w', '%{http_code}', url],
                             capture_output=True, text=True, timeout=30)
        if out.stdout.strip() in ('200', '302'):
            return True
    except Exception:
        pass
    try:
        out = subprocess.run(['gh', 'api', 'repos/notizieposts-web/notizieposts-web-newai/releases/tags/audio-%d' % n,
                              '--jq', '.assets[].name'], capture_output=True, text=True, timeout=30)
        return ('radar-ai-%d.mp3' % n) in out.stdout.split()
    except Exception:
        return False

def previous_title(root, n):
    s = open(os.path.join(root, 'index.html'), encoding='utf-8').read()
    m = re.search(r'var ED=(\[\{.*?\}\]),GU=', s, flags=re.S)
    if not m:
        return None
    for ed in json.loads(m.group(1)):
        if ed.get('n') == n - 1:
            return ed.get('t')
    return None

def build(root, audio=None, precedente=False):
    t = open(os.path.join(root, 'tools/mail_template_teaser.html'), encoding='utf-8').read()
    u = json.load(open(os.path.join(root, 'tools/ultima.json'), encoding='utf-8'))
    n = int(u['n'])
    y, m, d = u['data'].split('-')
    # data in testa (qualunque data scritta nel modello)
    t = re.sub(r'(RADAR AI &middot; )\d{1,2} [A-Z]+ \d{4}', lambda mo: mo.group(1) + '%d %s %s' % (int(d), MESI[int(m) - 1], y), t, count=1)
    chip = ('<span style="display:inline-block;margin:0 6px 6px 0;padding:6px 12px;border-radius:999px;'
            'border:1.5px solid #FFFFFF;font-size:13px;font-weight:bold;color:#FFFFFF">%s</span>')
    t = re.sub(r'(<p style="margin:14px 0 0">).*?(</p><h1)', lambda mo: mo.group(1) + ''.join(chip % e(c) for c in u['chips']) + mo.group(2), t, count=1, flags=re.S)
    t = re.sub(r'(<h1[^>]*>).*?(</h1>)', lambda mo: mo.group(1) + e(u['titolo']) + mo.group(2), t, count=1, flags=re.S)
    t = re.sub(r'(</h1><p style="margin:12px 0 22px[^>]*>).*?(</p>)', lambda mo: mo.group(1) + e(u['descrizione']) + mo.group(2), t, count=1, flags=re.S)
    st = iter(u['statistiche'])
    def rs(mo):
        v, l = next(st)
        return mo.group(1) + e(v) + mo.group(2) + e(l) + mo.group(3)
    t = re.sub(r'(<p style="margin:0;font-size:26px;font-weight:bold;color:#121A2B">).*?(</p><p style="margin:4px 0 0;font-size:13px;line-height:1.4;color:#2E3850">).*?(</p>)', rs, t)
    blocks = re.findall(r'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="margin:0 0 (?:18|6)px">.*?</table>\n', t, flags=re.S)
    tpl = blocks[0].replace('margin:0 0 6px', 'margin:0 0 18px', 1)
    new = ''
    for i, (em, prot, tit, txt) in enumerate(u['items']):
        b = tpl if i < len(u['items']) - 1 else tpl.replace('margin:0 0 18px', 'margin:0 0 6px', 1)
        b = re.sub(r'(aria-hidden="true">).*?(</td>)', lambda mo: mo.group(1) + ents(em) + mo.group(2), b, count=1)
        b = re.sub(r'(letter-spacing:.04em;color:#121A2B">).*?(</span>)', lambda mo: mo.group(1) + e(prot) + mo.group(2), b, count=1)
        b = re.sub(r'(<h3[^>]*>).*?(</h3>)', lambda mo: mo.group(1) + e(tit) + mo.group(2), b, count=1)
        b = re.sub(r'(<p style="margin:0;font-size:15px;line-height:1.55;color:#2E3850">).*?(</p>)', lambda mo: mo.group(1) + e(txt) + mo.group(2), b, count=1)
        new += b
    t = t[:t.index(blocks[0])] + new + t[t.index(blocks[-1]) + len(blocks[-1]):]
    t = re.sub(r'(<p style="margin:0;font-size:17px;line-height:1.5;font-weight:bold;color:#121A2B">).*?(</p>)', lambda mo: mo.group(1) + e(u['domanda']) + mo.group(2), t, count=1, flags=re.S)
    # audio
    if audio is None:
        audio = audio_exists(n)
    if audio:
        txt = os.path.join(root, 'tools/audio/%d.txt' % n)
        mins = max(1, round(len(open(txt, encoding='utf-8').read().split()) / WPM)) if os.path.exists(txt) else None
        t = re.sub(r'audio-\d+/radar-ai-\d+\.mp3', 'audio-%d/radar-ai-%d.mp3' % (n, n), t)
        t = re.sub(r"La versione audio dell'edizione, circa [^.]*\.",
                   "La versione audio dell'edizione" + (', circa %d minuti.' % mins if mins else '.'), t)
        t = re.sub(r'<!-- AUDIO:[^>]*-->', '', t)
        t = t.replace('<!-- /AUDIO -->', '')
    else:
        t = re.sub(r'<!-- AUDIO:.*?<!-- /AUDIO -->\n?', '', t, flags=re.S)
    # link all'edizione e totale
    t = re.sub(r'edizioni/\d+\.html', 'edizioni/%02d.html' % n if n < 10 else 'edizioni/%d.html' % n, t)
    t = re.sub(r'Tutte le \d+ edizioni', 'Tutte le %d edizioni' % n, t)
    if precedente and n > 1:
        pt = previous_title(root, n) or ('Edizione %d' % (n - 1))
        prev = ('<p style="margin:0 0 18px;font-size:15px;line-height:1.5;color:#2E3850">Ti sei perso l\'edizione precedente? '
                '<a href="%sedizioni/%02d.html" target="_blank" rel="noopener" style="color:#121A2B;font-weight:bold;text-decoration:underline">%s</a></p>\n'
                % (SITE, n - 1, e(pt)))
        t = t.replace('<tr><td align="center" style="padding:28px 0 6px">\n', '<tr><td align="center" style="padding:28px 0 6px">\n' + prev, 1)
    check(t, n)
    return t, u

def check(t, n):
    bad = [h for h in re.findall(r'href="([^"]+)"', t) if not (h.startswith(SITE) or h.startswith(REPO + '/'))]
    if bad:
        raise SystemExit('Link non diretti nell\'email: %s' % bad[:3])
    if 'google.com/url' in t or 'safelinks' in t:
        raise SystemExit('Link riscritti trovati: costruisci l\'email solo dal modello.')
    if 'edizioni/%d.html' % n not in t and 'edizioni/%02d.html' % n not in t:
        raise SystemExit('Link all\'edizione %d mancante.' % n)

if __name__ == '__main__':
    args = sys.argv[1:]
    out = args[0]
    audio = None
    if '--audio' in args:
        audio = args[args.index('--audio') + 1] == 'si'
    t, u = build('.', audio=audio, precedente='--precedente' in args)
    open(out, 'w', encoding='utf-8').write(t)
    print('ok', out, 'edizione', u['n'], 'audio', 'si' if 'radar-ai-%d.mp3' % int(u['n']) in t else 'no',
          'oggetto:', '\U0001F4E1 Radar AI · ' + u['titolo'])
