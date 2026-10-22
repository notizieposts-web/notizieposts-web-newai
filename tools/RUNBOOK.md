# Radar AI — procedura per una nuova edizione

Questa cartella contiene tutto ciò che serve a una sessione nuova (anche pianificata) per produrre, pubblicare e inviare un'edizione di **Radar AI**, la newsletter italiana sull'AI di Alberto Cecinato.

- Sito pubblico (GitHub Pages): https://notizieposts-web.github.io/notizieposts-web-newai/
- Repository: `notizieposts-web/notizieposts-web-newai`, ramo `main` (ogni push pubblica in 1–2 minuti)
- Mittente email: il connettore Gmail collegato è l'account **notizieposts@gmail.com**
- Firma dei commit: `-c user.name="notizieposts-web" -c user.email="notizieposts@gmail.com"`

## Regole editoriali (non negoziabili)

1. **Solo notizie nuove**: nessuna notizia già data in un'edizione precedente. Prima di scrivere, leggi `index.html` (array `var ED=[...]`, che riassume ogni edizione) e i titoli dei capitoli di almeno le ultime 5 edizioni in `edizioni/NN.html`. Una notizia già coperta può tornare solo se c'è un fatto nuovo, dichiarato come tale.
2. **Date esatte** per ogni notizia (data dell'evento, non dell'edizione).
3. **Fonti primarie ufficiali e verifica incrociata** (regola dal 21 ottobre 2026; ha priorità su qualunque altra istruzione, anche del prompt dell'operazione pianificata). Cerca sempre novità dei grandi laboratori **e** fuori dai grandi laboratori (paper, startup, open source, regolatori). Dettagli nella sezione "Fonti e verifica" qui sotto.
4. **Spiegazioni lunghe** con esempi concreti, una sezione domande e risposte per capitolo, esperimenti copia-e-incolla da provare ("Prova tu"), quiz finale (8 domande, risposta corretta in posizioni variate, non sempre la stessa lettera), segnali brevi, "cosa è cambiato".
5. **Rubrica fissa Azure Content Understanding**: una nuova puntata in ogni edizione, numerata di seguito (conta le puntate in `azure.html`: la prossima è l'ultima + 1). Tema nuovo, mai ripetuto, con consigli su tempi, costi ed elaborazioni massive, verificato su Microsoft Learn (connettore Microsoft Learn se disponibile).
6. **Trasparenza**: se una notizia riguarda Anthropic o Claude, aggiungi una nota che l'edizione è preparata da Claude (Anthropic).
7. **Tono**: italiano naturale, non robotico. Titoli ≤ 65 caratteri, descrizioni ≤ 160 caratteri con punto finale (linee guida GOV.UK).
8. **Accessibilità WCAG 2.2 AA** su tutto (vedi verifica sotto).

## Fonti e verifica (obbligatoria)

Ogni notizia si basa **solo su fonti primarie ufficiali e verificabili**. Etichette ammesse come prova, ciascuna con link e data di pubblicazione:

| Etichetta | Che cos'è | Classe CSS |
|---|---|---|
| `ufficiale` | comunicato, blog o documentazione dell'organizzazione coinvolta | `src u` |
| `istituzione` | università, enti di ricerca, autorità, governi, gazzette ufficiali (es. Federal Register) | `src u` |
| `repository` | repository e documentazione tecnica ufficiali (GitHub dell'organizzazione, model card) | `src u` |
| `paper revisionato` | articolo pubblicato dopo peer review (rivista, atti di conferenza) | `src p` |
| `preprint` | paper non revisionato (arXiv, bioRxiv…): sempre il link all'originale, mai ad aggregatori come Hugging Face Papers | `src p` |

`stampa` e `terze parti` (testate, rassegne, newsletter, aggregatori, blog di opinione) **non sono mai una prova**: si usano solo per scoprire le notizie o per il contesto, e se compaiono nella pagina sono etichettate come `contesto`.

Per ogni notizia, nel capitolo:

1. **Fonte primaria**: URL e data di pubblicazione dell'originale.
2. **Verifica incrociata**: cerca conferme, contestazioni o smentite da altre fonti primarie ufficiali indipendenti e riporta l'esito anche quando non trovi nulla (per esempio "nessuna conferma indipendente al 21 ottobre"). La mancanza di conferme non blocca la pubblicazione, ma va scritta.
3. **Dichiarato o dimostrato**: distingui ciò che l'organizzazione dichiara da ciò che è stato verificato da altri (benchmark ripetuti, dati pubblici, autorità).
4. **Limiti**: incertezze, contraddizioni, dati mancanti.
5. **Collegamenti**: se la notizia è collegata a capitoli di edizioni precedenti, metti i link diretti (es. `edizioni/26.html#deepseek`).
6. **Acronimi e termini tecnici**: spiegati in parole semplici con un esempio concreto.

Ogni capitolo di notizie ha un riquadro `<div class="example"><b>Verifica</b>…</div>` con: fonte primaria e data · dichiarato · verificato da altri · limiti · collegamenti.

**Notizie senza fonte primaria**: non diventano mai un capitolo. Possono comparire solo tra i segnali con l'etichetta `non verificabile`, scritte al condizionale e mai come fatto accertato. Se sono troppo deboli anche per questo, vanno in "Cosa ho escluso".

**Smentite**: se una fonte primaria ufficiale smentisce o contesta una notizia (anche una data in un'edizione precedente), la smentita si pubblica sempre: nel capitolo della notizia, oppure, se riguarda un'edizione passata, in "Cosa è cambiato" con l'etichetta `smentita` e il link al capitolo originale.

## Glossario (acronimi e termini tecnici)

Il componente è fisso: stile e comportamento (clic, Invio/Spazio, Esc che chiude e riporta il fuoco, `aria-expanded`, pulsante "Chiudi") stanno in `tools/inject.py` e sono già passati da audit3 e reflow. **Non va riscritto né modificato in un'edizione**: le sessioni aggiungono solo i termini.

1. Nella pagina marca la **prima** occorrenza di ogni acronimo o termine tecnico significativo (di norma 5–10 per edizione), dentro il testo dei capitoli, mai in titoli, menu, chip o nel codice: `<span class="gl" data-gl="mfu">MFU</span>`. Il testo visibile resta quello della frase.
2. Se la chiave non esiste, aggiungila a `tools/glossario.json` (chiave minuscola, lettere, cifre e trattini): `"mfu": {"t": "MFU", "esteso": "Model FLOPs Utilization", "spiega": "...", "esempio": "..."}`. `esteso` solo per gli acronimi; `spiega` in italiano semplice, due frasi al massimo; `esempio` concreto, una o due frasi. Le voci valgono per tutte le edizioni: riusale, non duplicarle; correggile solo se sbagliate, verificandole su fonti ufficiali.
3. `python3 tools/glossario.py .` genera pulsante e scheda (idempotente) e si ferma se manca una chiave.
4. **Audio**: niente schede; ogni sigla si scioglie a voce alla prima menzione ("il TPU, il chip di Google per l'AI"). **Email**: nessun glossario (è un invito alla lettura costruito da `mail_build.py`, il modello non si tocca).

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
   - **Testo audio** `tools/audio/$NN.txt`: la versione da ascoltare, che segue l'edizione **pari passo, capitolo per capitolo, nello stesso ordine della pagina**, così chi ascolta può seguirla tutta anche senza leggere. Lunghezza 8–11 minuti, **massimo 11.000 caratteri** (circa 1.600 parole): oltre, la quota gratuita Azure F0 di 500.000 caratteri al mese non basta per un'edizione al giorno. Per ogni capitolo: annuncio ("Capitolo due: ..."), la notizia con data e protagonisti, **senza esempi** (gli esempi stanno solo nella pagina: al massimo una frase tipo "nella pagina trovi un esempio su..."), e **una domanda di riflessione** rivolta all'ascoltatore ("Prova a chiederti: ...") come paragrafo a sé, che termina con il punto interrogativo (il generatore lascia una pausa più lunga dopo le domande). Gli esperimenti "Prova tu" si raccontano in una frase ("nella pagina trovi un esperimento per...") senza codice. Poi: riassunto della puntata Azure, la domanda del giorno con una pausa e poi la risposta, chiusura con il rimando alla pagina. Paragrafi separati da una riga vuota; frasi brevi, tono da conduttore; niente codice, URL, tabelle, simboli ($, %, →): scrivi "dollari", "per cento"; i numeri grandi in parole. Nota di trasparenza parlata se si parla di Anthropic o Claude. Durata annunciata in apertura stimata a circa 145 parole al minuto. Va nello stesso commit dell'edizione.
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
   python3 tools/audio_page.py .
   python3 tools/site_meta.py .
   python3 tools/graph.py .
   python3 tools/guida.py .
   python3 tools/argomenti.py .
   python3 tools/glossario.py .     # si ferma se un termine marcato non è in tools/glossario.json
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
7. **Stato per l'invio**: scrivi `tools/ultima.json` con `{"n": NN, "data": "AAAA-MM-GG", "titolo": "...", "descrizione": "...", "chips": [...], "statistiche": [[valore, etichetta], x3], "items": [[emoji, protagonista, titolo, testo], ...], "domanda": "..."}` e includilo nel commit. Serve all'invio automatico delle 9:00 (preparazione alle 7:30).

## Email (invio)

**L'HTML dell'email si costruisce SOLO con lo script**, che parte dal modello `tools/mail_template_teaser.html` e da `tools/ultima.json`:

```bash
python3 tools/mail_build.py /tmp/mail.html                 # destinatari quotidiani
python3 tools/mail_build.py /tmp/mail_prec.html --precedente   # destinatari a giorni alterni: aggiunge il link all'edizione precedente
```

**Invio: workflow "Invio email" di questo repository** (`.github/workflows/email.yml`), via SMTP di Gmail. Parte da solo quando l'operazione delle 8:40 pubblica `tools/ultima.json` con la data di oggi (evento push), con controlli di sicurezza alle :10 e :40 fino alle 10:40 (ora legale); se l'edizione del giorno non c'è, salta. Aspetta l'audio fino a 10 minuti, invia a `MAIL_DAILY` ogni giorno e a `MAIL_ALTERNATE` a giorni alterni da `MAIL_ALTERNATE_START` (predefinito 2026-10-19; giorno pari = invio), e mette il tag `mail-NN` per non inviare due volte. Secret di questo repository: `GMAIL_APP_PASSWORD` (password per le app di notizieposts@gmail.com), `MAIL_DAILY`, `MAIL_ALTERNATE`, `MAIL_TEST` (facoltativo). Senza `GMAIL_APP_PASSWORD` il workflow non invia e lascia fare alla riserva. I log sono pubblici: gli script non stampano indirizzi e i secret sono mascherati. Il connettore Gmail non si usa mai per la newsletter (riscrive i link in `google.com/url`). Nessuna operazione di Claude deve inviare.

**Riserva: repository privato `notizieposts-web/radar-ai-invio`** (`.github/workflows/invio.yml`, stessi secret): parte dalle 11:05 (ora legale) e invia solo se qui non c'è già il tag `mail-NN` dell'edizione di oggi.

A mano:

```bash
gh api -X POST repos/notizieposts-web/notizieposts-web-newai/actions/workflows/email.yml/dispatches -f ref=main -f 'inputs[modo]=prova'   # o tutti
gh api 'repos/notizieposts-web/notizieposts-web-newai/actions/workflows/email.yml/runs?per_page=1'
```

Lo script `tools/mail_build.py` inserisce il blocco audio solo se l'MP3 della Release esiste già (`curl -sI` senza `-L` deve dare 302) e **si ferma** se trova link non diretti. **Mai riusare l'HTML di un'email letta da Gmail.** Il modello è un invito alla lettura, non il contenuto completo. È un documento HTML completo con segnaposto `{{NOME}}` e blocchi ripetuti o facoltativi (`<!-- STAT -->`, `<!-- ITEM -->`, `<!-- AUDIO -->`, `<!-- PRECEDENTE -->`): lo script si ferma se resta un segnaposto vuoto. Regole del modello: testo di anteprima nascosto, una colonna mobile-first (statistiche che si impilano sotto 600 px anche senza `<style>`), pulsanti doppi: VML `v:roundrect` dentro `<!--[if mso]>` per Outlook desktop su Windows (motore Word, che ignora padding e bordi dei link) e HTML per gli altri client, area di almeno 44 px, titoli h1/h2/h3 veri, niente emoji (numerazione 01-05 per le notizie), nessun testo dentro immagini, contrasto di almeno 4,5:1 in chiaro e in scuro (`prefers-color-scheme` e `[data-ogsc]` per Outlook.com), colore mai unico portatore di significato. Se si cambia il modello: controllo automatico (axe WCAG 2.2, contrasto, 320 px, versione senza `<style>`) e prova con `modo=prova`.

## Metadati e servizi del sito (tools/site_meta.py)

Segue Google Search Central (titoli e descrizioni unici, sitemap, dati strutturati Article), W3C/WAI (regola 2.4.5, più modi per trovare una pagina) e GitHub Pages (pagina 404). Ogni edizione riceve: titolo "Titolo · Radar AI, data", meta description (da `tools/edx.py`), canonical, Open Graph con immagine `img/og/NN.png` (generata con `tools/fonts/Inter-Bold.otf`, licenza OFL), JSON-LD `NewsArticle`, e in fondo la navigazione "Edizione precedente / Tutte le edizioni / Edizione successiva". Le altre pagine ricevono descrizione, canonical e Open Graph. Vengono rigenerati `feed.xml` (Atom: vale anche come sitemap delle edizioni), `sitemap.xml` (lastmod solo sulle edizioni, dove la data è certa) e `404.html`. Le date di pubblicazione stanno in `tools/site_dates.json` (una nuova edizione prende la data di `tools/ultima.json`). Il menu "Argomenti" di ogni pagina (generato da `tools/argomenti.py`) parte con "Tutte le edizioni" e "Ultima edizione". Un `robots.txt` non serve: per un sito di progetto GitHub Pages andrebbe nella radice del dominio, che non è nostra; la sitemap si dichiara in Search Console.

## Altre pagine

- `azure.html` (guida per tema) e `azure-esercizi.html` (palestra) si rigenerano con `guida.py` ed `esercizi_page.py`. Il Laboratorio (`azure-laboratorio.html` + `lab-estrai.html`, `lab-trasforma.html`, `lab-confronta.html`, `lab-prova.html`) si rigenera con `arena_page.py`. Laboratorio e Palestra non vanno toccati in un'edizione normale.

## Sfide quotidiane del Laboratorio (operazione delle 8:10)

Standard dal 2026-10-20 (giorno 1), stile HackerRank: l'obiettivo è imparare a usare bene agenti e Content Understanding, non programmare. Ogni giorno 30 sfide, 10 per percorso, con difficoltà mista: 4 Facili (20 punti), 4 Medie (40), 2 Difficili (80). Livello del giorno k = giorni dal 2026-10-20 + 1: tutte e tre le difficoltà crescono con k (più righe, più aliquote, più test nascosti, trappole).

- 🔎 **Estrai**: fattura, scontrino, contratto, email. Per ogni campo valore (70%) e metodo (30%): extract, classify, oppure "estrai il dato grezzo e trasforma nel codice". Dopo la verifica: metodo e perché di ogni campo, schema CU con solo i campi da leggere.
- 🧮 **Trasforma** ("Crea la funzione"): l'utente fa scrivere all'agente (modello gratuito nel browser o Gemini) la funzione `trasforma(input)`; gira in un Worker isolato (niente rete, 3 secondi). Test visibili 2-3 e nascosti 5-13. Famiglie: F piva, importo, data, nome; M scorporo IVA, scadenza, somma righe, IBAN; D multi-aliquota, fine mese, valuta, nota di credito. Dopo: confronto di costo con un campo generate, soluzione JS e Python.
- 🔀 **Confronta**: F ordine + fattura; M three-way match ordine + DDT + fattura con tolleranza; D contratto (sconto, termini, penale) + DDT + fattura. Dopo: le regole in Python.

Ogni sfida ha linee guida ("📋 Linee guida", cosa notare senza dare la risposta). Il generatore è deterministico (seme = data, percorso, posizione) e scarta i casi sul mezzo centesimo. Pacchetti in `tools/arena/packs/<data>.json`, sfide in `lab/a<id>.json`, PDF in `lab/a<id>-<n>.pdf`. Progressi dell'utente nel browser (`RStore` chiave `radar_arena`, codice di backup `ARENA1:`).

```bash
git pull --rebase origin main
python3 tools/arena_gen.py .                 # crea tools/arena/packs/<oggi>.json e i PDF in lab/ (idempotente, fuso Europe/Rome)
python3 tools/argomenti.py . && python3 tools/arena_page.py . && python3 tools/site_meta.py .
python3 tools/inject.py *.html edizioni/*.html
python3 tools/arenatest.py .                 # deve stampare "fails [] 0"
python3 tools/audit3.py "$(pwd)"            # 0 violazioni
python3 tools/reflow.py .                    # nessuna pagina oltre 320 px
git add -A && git -c user.name="notizieposts-web" -c user.email="notizieposts@gmail.com" commit -m "Laboratorio: sfide del giorno <data>" && git pull --rebase origin main && git push origin main
```

Se un test fallisce, correggi il generatore (`tools/arena_gen.py`, mai le singole sfide), cancella `tools/arena/packs/<oggi>.json` e i file `lab/a<id>*` di quel giorno, e rigenera.

## Audio (voce e chiave)

- **Dove vive l'audio**: l'originale nelle Release di GitHub (`audio-NN` → `radar-ai-NN.mp3`), mai nel ramo main né nel sito. Le Release servono i file come `application/octet-stream` da scaricare, che Safari e iPhone non riproducono: per questo il workflow copia le **ultime 30** MP3 nel ramo orfano `audio` (un solo commit, sostituito con push forzato a ogni run, così la storia non cresce) e il lettore le prende da jsDelivr (`https://cdn.jsdelivr.net/gh/notizieposts-web/notizieposts-web-newai@audio/radar-ai-NN.mp3`, servite come `audio/mpeg`), con la Release come seconda sorgente. Il ramo `audio` non si tocca a mano e non si unisce mai a main; se manca o è incompleto, basta rilanciare il workflow "Audio dell'edizione" (lo ricostruisce scaricando dalle Release). Così non pesa sui limiti di GitHub Pages e non va allegato alle email: si linka.
- **Sul sito**: `tools/audio_page.py` mette in ogni edizione che ha `tools/audio/NN.txt` un blocco "Ascolta l'edizione" nell'intestazione (lettore con `preload="none"`, che non scarica nulla finché non si preme play, pulsante "Scarica l'MP3" e link a tutti gli audio), e `tools/edx.py` aggiunge il chip "🎧 Audio" nell'archivio. Il file resta nella Release. Il blocco è verificato con audit3 e reflow (WCAG 2.2 AA, 0 violazioni): non cambiarne colori o dimensioni senza rifare gli audit.
- Generatore: `tools/audio_gen.py`. Con il secret `AZURE_SPEECH_KEY` usa Azure Speech, altrimenti la voce locale Kokoro (Sara).
- Configurazione attuale (variabili del repository, Settings → Secrets and variables → Actions → Variables):
  - `AZURE_SPEECH_REGION` = `northeurope` (la risorsa F0 è in North Europe: West Europe non accettava nuovi clienti). Se manca o arriva vuota, il generatore usa comunque `northeurope`.
  - `AZURE_SPEECH_VOICE` = `it-IT-IsabellaMultilingualNeural` (scelta il 18 ottobre 2026 tra Isabella, Diego e Isabella Multilingual).
  - `AZURE_SPEECH_RATE` = `-8%`. La Multilingual è più svelta delle altre (~135 parole/minuto a -8% contro ~115): se serve più calma, `-15%`.
  - `AZURE_SPEECH_ENDPOINT` esiste ma il generatore non la usa.
- **La chiave Azure non va mai scritta nel repository, nei file, nei commit, nei log o nelle email**: vive solo nel secret `AZURE_SPEECH_KEY`. Risorsa: Speech (Servizi voce) nel livello gratuito F0, 0,5 milioni di caratteri al mese; oltre la quota il servizio si ferma, non addebita. Un'edizione consuma circa 8.000 caratteri.
- Rigenerare un audio: Actions → "Audio dell'edizione" → Run workflow, con il numero e `rigenera = si`.
- Provare altre voci o velocità: Actions → "Campioni voce" → Run workflow (voci separate da virgola, velocità, paragrafi). I campioni finiscono nella pre-release `audio-campioni`. Senza chiave il workflow si ferma.
- Verifica: il commento nei metadati dell'MP3 riporta motore, area, voce e velocità usate (`ffprobe -show_entries format_tags=comment radar-ai-NN.mp3`). Gli errori Azure compaiono come annotazioni del run (codice, area, voce; mai la chiave).
- Nel testo `tools/audio/NN.txt` la durata annunciata va stimata a circa 145 parole al minuto con la voce attuale (l'edizione 24, 1.260 parole, dura 8 minuti e mezzo). Struttura e limite di caratteri: vedi il passo "Testo audio". Dopo un paragrafo che finisce con "?" il generatore lascia 2,5 secondi di silenzio.
