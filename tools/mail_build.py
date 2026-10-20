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

MESI_L = [m.lower() for m in MESI]

def reading_minutes(root, n):
    """Minuti di lettura dell'edizione sul sito: parole del contenuto principale a 200 parole al minuto, arrotondati a 5."""
    try:
        h = open(os.path.join(root, 'edizioni', '%02d.html' % n), encoding='utf-8').read()
        h = re.sub(r'(?s)<(script|style|nav|footer|header)\b.*?</\1>', ' ', h)
        w = len(html.unescape(re.sub(r'<[^>]+>', ' ', h)).split())
        return max(5, int(round(w / 200 / 5.0)) * 5)
    except Exception:
        return 30

def block(t, name, fn):
    """Sostituisce ogni <!-- NAME -->...<!-- /NAME --> con fn(contenuto)."""
    return re.sub(r'(?s)<!-- %s -->(.*?)<!-- /%s -->' % (name, name), lambda m: fn(m.group(1)), t)

def fill(t, d):
    for k, v in d.items():
        t = t.replace('{{%s}}' % k, v)
    return t

def build(root, audio=None, precedente=False):
    t = open(os.path.join(root, 'tools/mail_template_teaser.html'), encoding='utf-8').read()
    u = json.load(open(os.path.join(root, 'tools/ultima.json'), encoding='utf-8'))
    n = int(u['n'])
    y, m, d = u['data'].split('-')
    url_ed = '%sedizioni/%02d.html' % (SITE, n)
    chips = [e(c) for c in u['chips']]
    chips_txt = (', '.join(chips[:-1]) + ' e ' + chips[-1]) if len(chips) > 1 else ''.join(chips)
    t = block(t, 'STAT', lambda b: ''.join(fill(b, {'STAT_V': e(v), 'STAT_L': e(l)}) for v, l in u['statistiche']))
    t = block(t, 'ITEM', lambda b: ''.join(fill(b, {'IT_NUM': '%02d' % (i + 1), 'IT_EMOJI': ents(em), 'IT_TEMA': e(prot), 'IT_TITOLO': e(tit), 'IT_TESTO': e(txt)}) for i, (em, prot, tit, txt) in enumerate(u['items'])))
    if audio is None:
        audio = audio_exists(n)
    if audio:
        txt = os.path.join(root, 'tools/audio/%d.txt' % n)
        mins = max(1, round(len(open(txt, encoding='utf-8').read().split()) / WPM)) if os.path.exists(txt) else None
        t = block(t, 'AUDIO', lambda b: fill(b, {'MINUTI_AUDIO': (', circa %d minuti' % mins) if mins else '',
                                                  'URL_AUDIO': '%s/releases/download/audio-%d/radar-ai-%d.mp3' % (REPO, n, n), 'URL_RELEASES': REPO + '/releases'}))
    else:
        t = block(t, 'AUDIO', lambda b: '')
    if precedente and n > 1:
        pt = previous_title(root, n) or ('Edizione %d' % (n - 1))
        t = block(t, 'PRECEDENTE', lambda b: fill(b, {'URL_PREC': '%sedizioni/%02d.html' % (SITE, n - 1), 'N_PREC': str(n - 1), 'TITOLO_PREC': e(pt)}))
    else:
        t = block(t, 'PRECEDENTE', lambda b: '')
    t = fill(t, {'TITOLO': e(u['titolo']), 'DESCRIZIONE': e(u['descrizione']), 'DOMANDA': e(u['domanda']), 'CHIPS': chips_txt,
                 'N': str(n), 'DATA_LUNGA': '%d %s %s' % (int(d), MESI_L[int(m) - 1], y), 'URL_ED': url_ed,
                 'URL_ED_TESTO': url_ed.replace('https://', ''), 'URL_SITO': SITE, 'MINUTI_LETTURA': str(reading_minutes(root, n))})
    check(t, n)
    return t, u

def check(t, n):
    bad = [h for h in re.findall(r'href="([^"]+)"', t) if not (h.startswith(SITE) or h.startswith(REPO + '/'))]
    if bad:
        raise SystemExit('Link non diretti nell\'email: %s' % bad[:3])
    left = re.findall(r'\{\{[A-Z_]+\}\}', t)
    if left:
        raise SystemExit('Segnaposto non riempiti nell\'email: %s' % sorted(set(left)))
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
