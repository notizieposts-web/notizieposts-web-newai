"""Radar AI: aggiunge il lettore audio alle edizioni che hanno tools/audio/NN.txt. Idempotente.

Uso: python3 tools/audio_page.py .

Il file MP3 resta nella Release audio-NN di GitHub: la pagina contiene solo il lettore
(preload="none", non scarica nulla finche' non si preme play) e il link di download.
Il blocco va nell'intestazione, dopo il sommario (p.sub), tra <!-- AUDIO-PLAYER --> e <!-- /AUDIO-PLAYER -->.
"""
import glob, os, re, sys

REPO = 'https://github.com/notizieposts-web/notizieposts-web-newai'
WPM = 145  # parole al minuto della voce attuale (vedi RUNBOOK, sezione Audio)

CSS = ('<style id="audio-css">'
       '.audio-box{margin-top:1.4rem;padding:1rem 1.1rem;border:1px solid var(--line);border-radius:16px;background:var(--surface);max-width:34rem}'
       '.audio-box h2{font-size:1.05rem;margin:0 0 .3rem;color:var(--ink)}'
       '.audio-box p{margin:0;color:var(--muted);font-size:.95rem}'
       '.audio-box audio{display:block;width:100%;min-height:44px;margin:.75rem 0 .6rem}'
       '.audio-links{display:flex;flex-wrap:wrap;gap:.5rem 1rem;align-items:center}'
       '.audio-links a{display:inline-flex;align-items:center;min-height:44px;font-weight:700;color:var(--ink)}'
       '.audio-links a.audio-dl{padding:0 1rem;border-radius:999px;background:var(--ink);color:var(--bg);text-decoration:none}'
       '.audio-links a.audio-dl:hover{text-decoration:underline}'
       '</style>')

def minutes(txt):
    words = len(open(txt, encoding='utf-8').read().split())
    return max(1, round(words / WPM))

def block(n, mins):
    nn = '%02d' % n if n < 10 else str(n)
    url = '%s/releases/download/audio-%s/radar-ai-%s.mp3' % (REPO, nn, nn)
    return ('<!-- AUDIO-PLAYER --><section class="audio-box" aria-labelledby="audio-title">'
            '<h2 id="audio-title"><span aria-hidden="true">&#127911;</span> Ascolta l\'edizione</h2>'
            '<p>Versione audio, circa %d minuti, con voce sintetica. Segue la pagina capitolo per capitolo, '
            'con una domanda di riflessione alla fine di ognuno; il testo completo è questa pagina.</p>'
            '<audio controls preload="none" src="%s" aria-label="Versione audio dell\'edizione %d">'
            '<a href="%s">Scarica la versione audio (MP3)</a></audio>'
            '<p class="audio-links"><a class="audio-dl" href="%s" download>Scarica l\'MP3</a>'
            '<a href="%s/releases">Tutti gli audio</a></p>'
            '</section><!-- /AUDIO-PLAYER -->' % (mins, url, n, url, url, REPO))

def main(root):
    done = []
    for txt in sorted(glob.glob(os.path.join(root, 'tools/audio/*.txt'))):
        nn = os.path.splitext(os.path.basename(txt))[0]
        if not nn.isdigit():
            continue
        page = os.path.join(root, 'edizioni', '%s.html' % nn)
        if not os.path.exists(page):
            continue
        s = open(page, encoding='utf-8').read()
        s = re.sub(r'<!-- AUDIO-PLAYER -->.*?<!-- /AUDIO-PLAYER -->', '', s, flags=re.S)
        s = re.sub(r'<style id="audio-css">.*?</style>', '', s, flags=re.S)
        m = re.search(r'(<header class="hero">.*?<p class="sub">.*?</p>)', s, flags=re.S)
        if not m:
            print('sommario non trovato in', page); continue
        s = s[:m.end()] + block(int(nn), minutes(txt)) + s[m.end():]
        s = s.replace('</head>', CSS + '</head>', 1)
        open(page, 'w', encoding='utf-8').write(s)
        done.append(int(nn))
    print('audio', done)

if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else '.')
