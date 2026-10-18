# Radar AI — procedura per una nuova edizione

Questa cartella contiene tutto ciò che serve a una sessione nuova (anche pianificata) per produrre, pubblicare e inviare un'edizione di **Radar AI**, la newsletter italiana sull'AI di Alberto Cecinato.

- Sito pubblico (GitHub Pages): https://notizieposts-web.github.io/notizieposts-web-newai/
- Repository: `notizieposts-web/notizieposts-web-newai`, ramo `main` (ogni push pubblica in 1–2 minuti)
- Mittente email: il connettore Gmail collegato è l'account **notizieposts@gmail.com**
- Firma dei commit: `-c user.name="notizieposts-web" -c user.email="notizieposts@gmail.com"`

## Regole editoriali (non negoziabili)

1. **Solo notizie nuove**: nessuna notizia già data in un'edizione precedente. Prima di scrivere, leggi `index.html` (array `var ED=[...]`, che riassume ogni edizione) e i titoli dei capitoli di almeno le ultime 5 edizioni in `edizioni/NN.html`. Una notizia già coperta può tornare solo se c'è un fatto nuovo, dichiarato come tale.
2. **Date esatte** per ogni notizia (data dell'evento, non dell'edizione).
3. **Fonti etichettate**: ogni fonte con link e tipo: `paper`, `ufficiale`, `stampa`, `terze parti`. Cerca sempre: novità dei grandi laboratori **e** fuori dai grandi laboratori (paper, startup, open source, regolatori).
4. **Spiegazioni lunghe** con esempi concreti, una sezione domande e risposte per capitolo, esperimenti copia-e-incolla da provare ("Prova tu"), quiz finale (8 domande, risposta corretta in posizioni variate, non sempre la stessa lettera), segnali brevi, "cosa è cambiato".
5. **Rubrica fissa Azure Content Understanding**: una nuova puntata in ogni edizione, numerata di seguito (conta le puntate in `azure.html`: la prossima è l'ultima + 1). Tema nuovo, mai ripetuto, con consigli su tempi, costi ed elaborazioni massive, verificato su Microsoft Learn (connettore Microsoft Learn se disponibile).
6. **Trasparenza**: se una notizia riguarda Anthropic o Claude, aggiungi una nota che l'edizione è preparata da Claude (Anthropic).
7. **Tono**: italiano naturale, non robotico. Titoli ≤ 65 caratteri, descrizioni ≤ 160 caratteri con punto finale (linee guida GOV.UK).
8. **Accessibilità WCAG 2.2 AA** su tutto (vedi verifica sotto).

## Struttura di un'edizione

Copia la struttura di `edizioni/23.html` (stesso `<head>`, stessi stili, stesso JavaScript in fondo). Capitoli: `<section class="ch" id="...">`, ciascuno con `.ch-head` (kicker con chip della data, `h2`, `p.lead`) e `<div class="grid2"><div class="prose">…</div><div class="stick">…strumento interattivo…</div></div>`. Il capitolo Azure ha `id="azure"`. Capitoli standard: `periodo`, 3–5 capitoli di notizie, `azure`, `lab`, `segnali`, `novita`, `quiz`, `fonti`.

Nel menu (`<nav class="nav">`) ogni voce è **una parola** che indica il protagonista del capitolo (azienda, prodotto o persona: "NVIDIA", "Gemini", "Anthropic"…). Dopo aver scritto la pagina, applica gli script (sotto), che sistemano menu, chip, logo e accessibilità.

## Passi

```bash
cd <repo>
npm i --prefix tools axe-core@4.10.2   # una volta per sessione, serve agli audit
NN=24                                  # numero della nuova edizione (ultima + 1)
```

1. **Ricerca** (WebSearch/WebFetch): notizie dalle ultime 24–48 ore non ancora coperte. Annota data, fonte, tipo.
2. **Scrivi** `edizioni/$NN.html`.
   - **Testo audio** `tools/audio/$NN.txt`: la versione da ascoltare, che segue l'edizione **pari passo, capitolo per capitolo, nello stesso ordine della pagina**, così chi ascolta può seguirla tutta anche senza leggere. Lunghezza 10–13 minuti, **massimo 12.500 caratteri** (circa 1.800 parole): oltre, la quota gratuita Azure F0 di 500.000 caratteri al mese non basta per un'edizione al giorno. Per ogni capitolo: annuncio ("Capitolo due: ..."), la notizia con data e protagonisti, **almeno un esempio concreto** raccontato a voce (un caso pratico, un numero tradotto in qualcosa di quotidiano, un "immagina che..."), e **una domanda di riflessione** rivolta all'ascoltatore ("Prova a chiederti: ...") come paragrafo a sé, che termina con il punto interrogativo (il generatore lascia una pausa più lunga dopo le domande). Gli esperimenti "Prova tu" si raccontano in una frase ("nella pagina trovi un esperimento per...") senza codice. Poi: riassunto della puntata Azure con un esempio, la domanda del giorno con una pausa e poi la risposta, chiusura con il rimando alla pagina. Paragrafi separati da una riga vuota; frasi brevi, tono da conduttore; niente codice, URL, tabelle, simboli ($, %, →): scrivi "dollari", "per cento"; i numeri grandi in parole. Nota di trasparenza parlata se si parla di Anthropic o Claude. Durata annunciata in apertura stimata a circa 145 parole al minuto. Va nello stesso commit dell'edizione.
3. **Archivio**:
   - `index.html`: aggiungi in fondo all'array `var ED=[...]` la riga `['GG mese, fascia','Titolo','riassunto lungo dei contenuti…','edizioni/NN.html']` (stesso formato delle righe esistenti).
   - `tools/topics.py`: aggiungi in `MAP` la voce `'NN': {'idcapitolo':'Protagonista', ...}` per i capitoli di notizie.
   - `tools/edx.py`: aggiungi in `EDX` `'NN': (None, "Titolo ≤65", "Descrizione ≤160.")`.
   - `tools/graph.py`: aggiungi in `THEMES` `NN: ['Tema', ...]` scegliendo tra i temi esistenti (Sicurezza, Grandi modelli, Pesi aperti, Costi, Ricerca, Regole, Decisionali, Hardware, Valutazione).
   - `tools/guida.py`: aggiungi in `EP` la nuova puntata Azure `(N, 'NN', 'azure', 'gruppo', 'Titolo breve')` con gruppo tra costi, pipeline, qualita, sicurezza, produzione, casi.
4. **Applica gli script** (dalla radice del repo):
   ```bash
   python3 tools/topics.py .
   python3 tools/edx.py .
   python3 tools/graph.py .
   python3 tools/guida.py .
   python3 tools/argomenti.py .
   python3 tools/inject.py *.html edizioni/*.html
   ```
5. **Verifica**:
   ```bash
   python3 tools/audit3.py "$(pwd)"     # deve stampare nulla (0 violazioni axe, 4 temi)
   python3 tools/reflow.py "$(pwd)"     # deve stampare nulla (niente scorrimento orizzontale a 320px)
   ```
   Apri la pagina con Playwright e controlla a occhio uno screenshot. Correggi e ripeti finché è pulito.
6. **Pubblica**:
   ```bash
   git add -A && git -c user.name="notizieposts-web" -c user.email="notizieposts@gmail.com" commit -m "Edizione NN: <titolo>" && git push origin main
   ```
   Attendi il deploy: `gh api "repos/notizieposts-web/notizieposts-web-newai/actions/runs?per_page=1"` finché lo SHA del commit risulta `completed success`.
   Il push di `tools/audio/$NN.txt` avvia anche il workflow **Audio dell'edizione** (`.github/workflows/audio.yml`): crea l'MP3 e lo pubblica nella Release `audio-$NN` (file `radar-ai-$NN.mp3`). Gli audio stanno **solo nelle Release**, mai nel repository né sul sito: così non pesano sul limite di 1 GB di GitHub Pages. Controlla che il run finisca `success`; se fallisce, l'edizione resta valida e l'email parte senza il blocco audio.
7. **Stato per l'invio**: scrivi `tools/ultima.json` con `{"n": NN, "data": "AAAA-MM-GG", "titolo": "...", "descrizione": "...", "chips": [...], "statistiche": [[valore, etichetta], x3], "items": [[emoji, protagonista, titolo, testo], ...], "domanda": "..."}` e includilo nel commit. Serve all'operazione di invio delle 9:00 (preparazione alle 8:40).

## Email (invio)

Template: `tools/mail_template_teaser.html` (sfondo bianco, contrasti verificati anche con l'inversione della modalità scura di Gmail). Sostituisci: data, chip dei protagonisti, titolo, descrizione, tre statistiche, le voci "Dentro trovi" (pillola protagonista + titolo + testo), la domanda del giorno, i link all'edizione (`edizioni/NN.html`) e all'archivio (radice del sito), il numero totale di edizioni. L'email è un **invito alla lettura**, non il contenuto completo. Invia con il connettore Gmail (`send_message` con `htmlBody`), mittente notizieposts@gmail.com.

**Blocco audio.** Prima di inviare, verifica che esista `https://github.com/notizieposts-web/notizieposts-web-newai/releases/download/audio-NN/radar-ai-NN.mp3` (`gh api repos/notizieposts-web/notizieposts-web-newai/releases/tags/audio-NN --jq '.assets[].name'` deve elencare `radar-ai-NN.mp3`; in alternativa `curl -sI -o /dev/null -w '%{http_code}'` senza `-L` deve dare 302: con `-L` alcuni proxy rispondono 401 anche se il file c'è). Se il file non c'è ma il run di "Audio dell'edizione" per NN è ancora in corso (`gh api 'repos/notizieposts-web/notizieposts-web-newai/actions/workflows/audio.yml/runs?per_page=1'`), aspetta fino a 10 minuti controllando ogni minuto. Nel blocco scrivi la durata reale arrotondata ("circa N minuti"; con `ffprobe` sul file o stimando 145 parole al minuto dal testo). Se esiste, tieni il blocco tra `<!-- AUDIO -->` e `<!-- /AUDIO -->` con il link aggiornato; se non esiste ancora, toglilo e invia lo stesso. Non allegare l'MP3 all'email: il connettore Gmail non regge file di qualche MB.

## Altre pagine

- `azure.html` (guida per tema), `azure-esercizi.html` (palestra), `azure-laboratorio.html` + `lab-*.html` (gioco): si rigenerano con `guida.py`, `esercizi_page.py`, `lab_page.py`. Il Laboratorio e la Palestra non vanno toccati in un'edizione normale.

## Sfide quotidiane del Laboratorio (operazione delle 8:10)

Ogni giorno si aggiungono 50 sfide (10 per modalità) con complessità crescente: livello k = giorni dal 2026-10-17 + 1. Il generatore è `tools/lab_daily.py` (documenti Word con commenti, tabelle, grafici, note e testo nascosto; Excel con celle unite, righe e fogli nascosti e grafici; PowerPoint con grafici nativi e note del relatore; PDF con tabelle su più pagine; pacchetti ordine-bolla-fattura; schemi da correggere, conti da tagliare, audit e guasti multipli).

```bash
pip install --break-system-packages python-docx openpyxl python-pptx matplotlib >/dev/null
git pull --rebase origin main
python3 tools/lab_daily.py .                 # crea tools/lab_daily/packs/<oggi>.json e i file in lab/ (idempotente)
python3 tools/argomenti.py . && python3 tools/lab_page.py .
python3 tools/inject.py *.html edizioni/*.html
MINID=<primo id nuovo> python3 tools/labtest2.py .   # deve stampare "fails [] 0"
python3 tools/audit3.py "$(pwd)"            # 0 violazioni
git add -A && git -c user.name="notizieposts-web" -c user.email="notizieposts@gmail.com" commit -m "Laboratorio: sfide del giorno <data>" && git pull --rebase origin main && git push origin main
```

Se un test fallisce, correggi il generatore (non le singole sfide) e rigenera il pacchetto del giorno cancellando `tools/lab_daily/packs/<oggi>.json` e i file `lab/s<id>.*` che aveva creato.

## Audio (voce e chiave)

- **Dove vive l'audio**: solo nelle Release di GitHub (`audio-NN` → `radar-ai-NN.mp3`), mai nel repository né nel sito. Così non pesa sui limiti di GitHub Pages e non va allegato alle email: si linka.
- Generatore: `tools/audio_gen.py`. Con il secret `AZURE_SPEECH_KEY` usa Azure Speech, altrimenti la voce locale Kokoro (Sara).
- Configurazione attuale (variabili del repository, Settings → Secrets and variables → Actions → Variables):
  - `AZURE_SPEECH_REGION` = `northeurope` (la risorsa F0 è in North Europe: West Europe non accettava nuovi clienti). Se manca, il generatore usa `westeurope`.
  - `AZURE_SPEECH_VOICE` = `it-IT-IsabellaMultilingualNeural` (scelta il 18 ottobre 2026 tra Isabella, Diego e Isabella Multilingual).
  - `AZURE_SPEECH_RATE` = `-8%`. La Multilingual è più svelta delle altre (~135 parole/minuto a -8% contro ~115): se serve più calma, `-15%`.
  - `AZURE_SPEECH_ENDPOINT` esiste ma il generatore non la usa.
- **La chiave Azure non va mai scritta nel repository, nei file, nei commit, nei log o nelle email**: vive solo nel secret `AZURE_SPEECH_KEY`. Risorsa: Speech (Servizi voce) nel livello gratuito F0, 0,5 milioni di caratteri al mese; oltre la quota il servizio si ferma, non addebita. Un'edizione consuma circa 8.000 caratteri.
- Rigenerare un audio: Actions → "Audio dell'edizione" → Run workflow, con il numero e `rigenera = si`.
- Provare altre voci o velocità: Actions → "Campioni voce" → Run workflow (voci separate da virgola, velocità, paragrafi). I campioni finiscono nella pre-release `audio-campioni`. Senza chiave il workflow si ferma.
- Verifica: il commento nei metadati dell'MP3 riporta motore, area, voce e velocità usate (`ffprobe -show_entries format_tags=comment radar-ai-NN.mp3`). Gli errori Azure compaiono come annotazioni del run (codice, area, voce; mai la chiave).
- Nel testo `tools/audio/NN.txt` la durata annunciata va stimata a circa 145 parole al minuto con la voce attuale (l'edizione 24, 1.260 parole, dura 8 minuti e mezzo). Struttura e limite di caratteri: vedi il passo "Testo audio". Dopo un paragrafo che finisce con "?" il generatore lascia 2,5 secondi di silenzio.
