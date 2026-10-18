"""Genera l'MP3 di un'edizione da tools/audio/NN.txt.

Uso: python3 tools/audio_gen.py tools/audio/24.txt radar-ai-24.mp3 "18 ottobre 2026"

Voce: se esiste AZURE_SPEECH_KEY usa Azure Speech (AZURE_SPEECH_REGION, AZURE_SPEECH_VOICE,
AZURE_SPEECH_RATE); altrimenti la voce locale Kokoro (KOKORO_DIR, voce Sara).
La chiave NON va mai scritta nel repository: arriva solo dai secret di GitHub Actions.
"""
import os, sys, time, subprocess, tempfile, html, wave

def paragraphs(path):
    return [p.strip() for p in open(path, encoding='utf-8').read().split('\n\n') if p.strip()]

def azure(paras, wavdir):
    import urllib.request
    key = os.environ['AZURE_SPEECH_KEY']; region = (os.environ.get('AZURE_SPEECH_REGION') or 'northeurope').strip().lower()
    voice = os.environ.get('AZURE_SPEECH_VOICE') or 'it-IT-IsabellaNeural'
    rate = os.environ.get('AZURE_SPEECH_RATE') or '-8%'
    url = 'https://%s.tts.speech.microsoft.com/cognitiveservices/v1' % region
    files = []
    for i, p in enumerate(paras):
        pause = '2500ms' if p.rstrip().endswith('?') else ('900ms' if len(p) < 90 else '600ms')
        ssml = ('<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="it-IT">'
                '<voice name="%s"><prosody rate="%s">%s</prosody><break time="%s"/></voice></speak>'
                % (voice, rate, html.escape(p, quote=False), pause))
        req = urllib.request.Request(url, data=ssml.encode('utf-8'), method='POST', headers={
            'Ocp-Apim-Subscription-Key': key, 'Content-Type': 'application/ssml+xml',
            'X-Microsoft-OutputFormat': 'riff-24khz-16bit-mono-pcm', 'User-Agent': 'radar-ai-audio'})
        for attempt in range(6):
            try:
                data = urllib.request.urlopen(req, timeout=120).read(); break
            except Exception as e:
                code = getattr(e, 'code', None)
                if code in (429, 500, 502, 503, 504) and attempt < 5:
                    time.sleep(10 * (attempt + 1)); continue
                hint = {401: 'chiave rifiutata: controlla AZURE_SPEECH_KEY e che AZURE_SPEECH_REGION sia l\'area della risorsa',
                        400: 'richiesta rifiutata: controlla il nome della voce e la velocita',
                        403: 'accesso negato dalla risorsa'}.get(code, '')
                raise SystemExit('::error::Azure Speech errore %s sul paragrafo %d (area %s, voce %s) %s'
                                 % (code or type(e).__name__, i + 1, region, voice, hint))
        f = os.path.join(wavdir, '%03d.wav' % i); open(f, 'wb').write(data); files.append(f)
        time.sleep(3.2)  # livello gratuito F0: massimo 20 richieste al minuto
    return files

def kokoro(paras, wavdir):
    import numpy as np, sherpa_onnx
    K = os.environ.get('KOKORO_DIR', 'kokoro-multi-lang-v1_0')
    cfg = sherpa_onnx.OfflineTtsConfig(model=sherpa_onnx.OfflineTtsModelConfig(kokoro=sherpa_onnx.OfflineTtsKokoroModelConfig(
        model=K + '/model.onnx', voices=K + '/voices.bin', tokens=K + '/tokens.txt', data_dir=K + '/espeak-ng-data',
        dict_dir=K + '/dict', lexicon=K + '/lexicon-us-en.txt', lang='it'), num_threads=4), max_num_sentences=1)
    tts = sherpa_onnx.OfflineTts(cfg); files = []
    for i, p in enumerate(paras):
        a = tts.generate(p, sid=35, speed=0.92)  # 35 = if_sara
        pause = 2.5 if p.rstrip().endswith('?') else (0.9 if len(p) < 90 else 0.6)
        x = np.concatenate([np.array(a.samples, dtype=np.float32), np.zeros(int(a.sample_rate * pause), dtype=np.float32)])
        f = os.path.join(wavdir, '%03d.wav' % i); w = wave.open(f, 'wb'); w.setnchannels(1); w.setsampwidth(2)
        w.setframerate(a.sample_rate); w.writeframes((np.clip(x, -1, 1) * 32767).astype('int16').tobytes()); w.close(); files.append(f)
    return files

def main():
    src, out, label = sys.argv[1], sys.argv[2], sys.argv[3]
    paras = paragraphs(src)
    with tempfile.TemporaryDirectory() as d:
        files = azure(paras, d) if os.environ.get('AZURE_SPEECH_KEY') else kokoro(paras, d)
        if os.environ.get('AZURE_SPEECH_KEY'):
            info = 'Azure %s %s %s' % ((os.environ.get('AZURE_SPEECH_REGION') or 'northeurope').strip().lower(),
                                       os.environ.get('AZURE_SPEECH_VOICE') or 'it-IT-IsabellaNeural',
                                       os.environ.get('AZURE_SPEECH_RATE') or '-8%')
        else:
            info = 'Kokoro if_sara 0.92'
        lst = os.path.join(d, 'list.txt'); open(lst, 'w').write(''.join("file '%s'\n" % f for f in files))
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', lst,
                        '-af', 'loudnorm=I=-16:TP=-1.5', '-ac', '1', '-ar', '24000', '-b:a', '48k',
                        '-id3v2_version', '3', '-metadata', 'title=Radar AI · ' + label,
                        '-metadata', 'artist=Radar AI', '-metadata', 'comment=' + info, '-metadata', 'album=Radar AI', out], check=True)
    print('ok', out, 'azure' if os.environ.get('AZURE_SPEECH_KEY') else 'kokoro')

if __name__ == '__main__':
    main()
