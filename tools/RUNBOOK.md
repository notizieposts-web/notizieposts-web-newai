# Sapit (prima Radar AI) — procedura per una nuova edizione

> Dal 12 novembre 2026 il sito si chiama **Sapit**: nel sito, nei titoli e nei piè di pagina delle nuove edizioni scrivi «Sapit». Marchio e regole: `docs/marchio.md`. L'email e i testi audio restano «Radar AI» finché non si decide diversamente.

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

**Come aprire le fonti senza richieste di consenso** (regola dal 1° novembre 2026; le operazioni pianificate girano senza nessuno che possa approvare): un link trovato **dentro** una pagina già letta (rassegne, newsletter, articoli) non si apre mai direttamente con WebFetch, perché fa scattare una richiesta di consenso che, senza risposta, scade e fa perdere la fonte. Si apre solo un link che arriva da un risultato di **WebSearch**: per ogni link interno, prima cerca con WebSearch il titolo della pagina o l'indirizzo esatto (eventualmente con `allowed_domains` sul dominio), poi apri con WebFetch l'indirizzo restituito dalla ricerca. Se la pagina non compare in nessuna ricerca, non aprirla: la fonte si segna come "non letta", e la notizia segue la regola qui sotto (segnale `non verificabile` o "Cosa ho escluso"). Se una pagina non si apre per un errore del sito, dillo nel riquadro Verifica.

**Notizie senza fonte primaria**: non diventano mai un capitolo. Possono comparire solo tra i segnali con l'etichetta `non verificabile`, scritte al condizionale e mai come fatto accertato. Se sono troppo deboli anche per questo, vanno in "Cosa ho escluso".

**Smentite**: se una fonte primaria ufficiale smentisce o contesta una notizia (anche una data in un'edizione precedente), la smentita si pubblica sempre: nel capitolo della notizia, oppure, se riguarda un'edizione passata, in "Cosa è cambiato" con l'etichetta `smentita` e il link al capitolo originale.

## Glossario (acronimi e termini tecnici)

Il componente è fisso: stile e comportamento (clic, Invio/Spazio, Esc che chiude e riporta il fuoco, `aria-expanded`, pulsante "Chiudi") stanno in `tools/inject.py` e sono già passati da audit3 e reflow. **Non va riscritto né modificato in un'edizione**: le sessioni aggiungono solo i termini.

1. Nella pagina marca la **prima** occorrenza di ogni acronimo o termine tecnico significativo (di norma 5–10 per edizione), dentro il testo dei capitoli, mai in titoli, menu, chip o nel codice: `<span class="gl" data-gl="mfu">MFU</span>`. Il testo visibile resta quello della frase.
2. Se la chiave non esiste, aggiungila a `tools/glossario.json` (chiave minuscola, lettere, cifre e trattini): `"mfu": {"t": "MFU", "esteso": "Model FLOPs Utilization", "spiega": "...", "esempio": "..."}`. `esteso` solo per gli acronimi; `spiega` in italiano semplice, due frasi al massimo; `esempio` concreto, una o due frasi. Le voci valgono per tutte le edizioni: riusale, non duplicarle; correggile solo se sbagliate, verificandole su fonti ufficiali.
   Facoltativi ma consigliati per le voci nuove: `"approfondisci"` (spiegazione più completa, 3–5 frasi, mostrata solo nella pagina del glossario) e `"vedi"` (elenco di chiavi collegate, che devono esistere).
3. `python3 tools/glossario.py .` genera pulsante e scheda (idempotente) e si ferma se manca una chiave. Genera anche:
   - nella scheda di ogni termine il link "Approfondisci nel glossario" (`glossario.html?da=NN-i#g-chiave`): la pagina del glossario mostra "Torna all'edizione NN, al punto in cui eri", che riporta a `edizioni/NN.html#glb-NN-i` con la scheda già aperta e il fuoco sul termine;
   - il chip "Glossario: N termini" nell'intestazione di ogni edizione che ha termini;
   - la pagina `glossario.html` (voci dalla A alla Z, "Più nel dettaglio", voci collegate, "Dove compare", termini per edizione). È anche una guida nel menu Argomenti (`tools/argomenti.py`, GUIDES).
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
   - **Mappa viva** `tools/mappe/$NN.json`: per ogni capitolo di notizie e per la rubrica Azure, la mappa concettuale che cresce mentre si legge (vedi la sezione "Mappa viva"). 5-8 nodi per capitolo, ognuno con titolo breve (≤4 parole), spiegazione di una frase presa dal testo, paragrafo in cui compare (`at`, indice di `.prose > p` da 0), emoji, genitore e relazione che si legge come una frase ("Performance Factory" + "dà la caccia alle" + "Regressioni di prestazioni"). Solo fatti scritti nell'edizione; controlla che ogni `id` di capitolo esista. Senza file la pagina usa la mappa automatica.
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
7. **Stato per l'invio**: scrivi `tools/ultima.json` con `{"n": NN, "data": "AAAA-MM-GG", "titolo": "...", "descrizione": "...", "chips": [...], "items": [[emoji, protagonista, titolo, testo], ...], "domanda": "..."}` e includilo nel commit. Serve all'invio automatico delle 9:00 (preparazione alle 7:30).

## Email (invio)

**L'HTML dell'email si costruisce SOLO con lo script**, che parte dal modello `tools/mail_template_teaser.html` e da `tools/ultima.json`:

```bash
python3 tools/mail_build.py /tmp/mail.html                 # destinatari quotidiani
python3 tools/mail_build.py /tmp/mail_prec.html --precedente   # destinatari a giorni alterni: aggiunge il link all'edizione precedente
```

**Invio: workflow "Invio email" di questo repository** (`.github/workflows/email.yml`), via SMTP di Gmail. **L'email parte alle 9:00 in punto, ora italiana**: il workflow si avvia alle 8:30 (e alle 8:45 come riserva, perché gli orari di GitHub possono slittare) e aspetta le 9:00. Se a quell'ora `tools/ultima.json` non ha ancora la data di oggi, controlla ogni minuto e invia appena l'edizione esce, fino alle 10:00. All'ora dell'invio il blocco audio c'è se l'MP3 è già pubblicato. Invia a `MAIL_DAILY` ogni giorno e a `MAIL_ALTERNATE` a giorni alterni da `MAIL_ALTERNATE_START` (predefinito 2026-10-19; giorno pari = invio), e mette il tag `mail-NN` per non inviare due volte. Secret di questo repository: `GMAIL_APP_PASSWORD` (password per le app di notizieposts@gmail.com), `MAIL_DAILY`, `MAIL_ALTERNATE`, `MAIL_TEST` (facoltativo). Senza `GMAIL_APP_PASSWORD` il workflow non invia e lascia fare alla riserva. I log sono pubblici: gli script non stampano indirizzi e i secret sono mascherati. Il connettore Gmail non si usa mai per la newsletter (riscrive i link in `google.com/url`). Nessuna operazione di Claude deve inviare.

**Riserva: repository privato `notizieposts-web/radar-ai-invio`** (`.github/workflows/invio.yml`, stessi secret): parte dalle 11:05 (ora legale) e invia solo se qui non c'è già il tag `mail-NN` dell'edizione di oggi.

A mano:

```bash
gh api -X POST repos/notizieposts-web/notizieposts-web-newai/actions/workflows/email.yml/dispatches -f ref=main -f 'inputs[modo]=prova'   # o tutti
gh api 'repos/notizieposts-web/notizieposts-web-newai/actions/workflows/email.yml/runs?per_page=1'
```

Lo script `tools/mail_build.py` inserisce il blocco audio solo se l'MP3 della Release esiste già (`curl -sI` senza `-L` deve dare 302) e **si ferma** se trova link non diretti. **Mai riusare l'HTML di un'email letta da Gmail.** Il modello è un invito alla lettura, non il contenuto completo. È un documento HTML completo con segnaposto `{{NOME}}` e blocchi ripetuti o facoltativi (`<!-- ITEM -->`, `<!-- AUDIO -->`, `<!-- PRECEDENTE -->`): lo script si ferma se resta un segnaposto vuoto. Regole del modello: testo di anteprima nascosto, una colonna mobile-first; ordine fisso: argomenti del giorno, titolo e descrizione, "Dentro trovi", blocco audio ("La tua newsletter da ascoltare", pulsante "Scarica audio", link alle Release in piccolo), domanda del giorno, pulsante per leggere l'edizione; niente sezione "In tre numeri"; piede: "Radar AI è realizzata con l'aiuto dell'intelligenza artificiale.", pulsanti doppi: VML `v:roundrect` dentro `<!--[if mso]>` per Outlook desktop su Windows (motore Word, che ignora padding e bordi dei link) e HTML per gli altri client, area di almeno 44 px, titoli h1/h2/h3 veri, niente emoji (numerazione 01-05 per le notizie), nessun testo dentro immagini, contrasto di almeno 4,5:1 in chiaro e in scuro (`prefers-color-scheme` e `[data-ogsc]` per Outlook.com), colore mai unico portatore di significato. Se si cambia il modello: controllo automatico (axe WCAG 2.2, contrasto, 320 px, versione senza `<style>`) e prova con `modo=prova`.

## Metadati e servizi del sito (tools/site_meta.py)

Segue Google Search Central (titoli e descrizioni unici, sitemap, dati strutturati Article), W3C/WAI (regola 2.4.5, più modi per trovare una pagina) e GitHub Pages (pagina 404). Ogni edizione riceve: titolo "Titolo · Radar AI, data", meta description (da `tools/edx.py`), canonical, Open Graph con immagine `img/og/NN.png` (generata con `tools/fonts/Inter-Bold.otf`, licenza OFL), JSON-LD `NewsArticle`, e in fondo la navigazione "Edizione precedente / Tutte le edizioni / Edizione successiva". Le altre pagine ricevono descrizione, canonical e Open Graph. Vengono rigenerati `feed.xml` (Atom: vale anche come sitemap delle edizioni), `sitemap.xml` (lastmod solo sulle edizioni, dove la data è certa) e `404.html`. Le date di pubblicazione stanno in `tools/site_dates.json` (una nuova edizione prende la data di `tools/ultima.json`). Il menu "Argomenti" di ogni pagina (generato da `tools/argomenti.py`) parte con "Tutte le edizioni" e "Ultima edizione". Un `robots.txt` non serve: per un sito di progetto GitHub Pages andrebbe nella radice del dominio, che non è nostra; la sitemap si dichiara in Search Console.

## Altre pagine

- `azure.html` (guida per tema) e `azure-esercizi.html` (palestra) si rigenerano con `guida.py` ed `esercizi_page.py`. Il Laboratorio (`azure-laboratorio.html` + `lab-estrai.html`, `lab-trasforma.html`, `lab-confronta.html`, `lab-prova.html`) si rigenera con `arena_page.py`. Laboratorio e Palestra non vanno toccati in un'edizione normale.

## Colori (dal 12 novembre 2026)

**Palette "Verde Deloitte"**, applicata a tutto il sito e documentata in `docs/palette.md` (colori, contrasti, fonti ufficiali). Sta in un solo punto, `tools/inject.py` (righe `:root` e il blocco subito sotto). Neutri grafite; pulsante verde `#3F7A12` con testo bianco, identico in chiaro e in scuro; verde chiaro `#86BC24` con testo nero solo per dettagli; stati verde, ambra, rosso con le loro tinte. Logo e favicon in `tools/logo.py`, anteprime `img/og/` e 404 in `tools/site_meta.py`. Dopo un cambio: rigenera le pagine (per le anteprime, cancella prima `img/og/*.png`), poi `audit3.py` e `reflow.py`. Il modello dell'email non si tocca e ha ancora il suo blu-viola `#3F3FD9`: va deciso a parte.

## Rada, aiuti e lettura facilitata (dall'11 novembre 2026)

- `tools/tutor.py` contiene **Rada**, la guida degli esercizi: un avatar che legge ad alta voce con la voce del browser (nessun server, nessuna chiave), con il testo sempre scritto e la frase in lettura evidenziata, e il pannello **Lettura facilitata** (testo più grande, più spazio, carattere ad alta leggibilità, righello, numeri in evidenza, lettura automatica degli aiuti). Le preferenze stanno nel browser (`radar-read`). È incluso da `esercizi_page.py` e `arena_page.py`.
- **Le due guide** (`tools/rada.py`): **Sapio, il gufo saggio** (guida predefinita, al naturale: piumaggio bruno, disco facciale chiaro, occhi ambra, posato su un ramo, senza cappello né occhiali) e **Rada, la fatina** (capelli ramati, ali, bacchetta). Disegni originali: non devono richiamare personaggi famosi (gufi, alberi o maghi di cartoni, film e videogiochi). Nove espressioni animate per entrambi (ciao, parla, idea, pensa, spiega, felice, coraggio, curiosa, conta). La scelta si fa nel pannello della guida e resta nel browser (`radar-read`, campo `ch`); nomi e disegni nella pagina si aggiornano da soli (`.rt-nm`, `svg.rd[data-rd]`). `python3 tools/rada.py .` scrive `img/rada/sapio-*.svg` e `img/rada/rada-*.svg`. Decorativi (`aria-hidden`), fermi con "riduci movimento".
- **Palestra** (`esercizi_page.py`): elenco stile HackerRank con difficoltà Facile (20 punti), Media (40), Difficile (80), percorsi per tema, gradi a stelle; un esercizio alla volta (`#exN`). Gli aiuti non tolgono punti e si generano da soli da consegna e soluzione di `esercizi_gen.py`: indizio, metodo (passaggi senza risultati, o risposte da escludere), soluzione passo passo, esempio svolto (un esercizio dello stesso tipo con altri dati), "Spiegamelo facile" (schema, parole difficili da `WORDS`), calcolatrice.
- **Laboratorio**: in ogni sfida il pulsante "Rada, spiegami la sfida" e i passi "Come si affronta" (`HOW` in `arena_page.py`). Punteggi e regole non cambiano.
- Dopo ogni modifica: `esercizi_page.py`, `arena_page.py`, `site_meta.py`, `inject.py`, poi `arenatest.py`, `audit3.py`, `reflow.py`. Gli audit automatici vedono solo l'elenco: la vista di un esercizio con gli aiuti aperti va controllata a parte con axe.
- **Pacchetti e squadre** (`tools/squadre_page.py` → `squadre.html`, voce "Squadre" nel menu Argomenti): pacchetti Utente, Gruppo, Azienda, percorsi per ruolo (la Palestra accetta `?l=1..3&g=tema`), codice risultato `RS1:` creato da ogni persona e classifica di chi coordina, salvata nel suo browser (`radar-team`) ed esportabile in CSV. Nessun server e nessun controllo antifrode. Va rigenerata quando cambia il numero degli esercizi: `python3 tools/squadre_page.py .` prima di `site_meta.py` e `inject.py`.
- **Classifica online** (dall'11 novembre 2026, `tools/cloud.py`, `tools/cloud/config.json`): progetto Supabase `radar-ai` (organizzazione Newsletters, regione eu-central-1). Niente email: si entra con nome e password in `squadre.html` (un solo modulo per registrarsi e rientrare). Il browser trasforma nome e password in un codice `RA1-…` (PBKDF2, 150.000 iterazioni) e invia solo quello; nel database c'è la sua impronta. La password non si recupera. Nella pagina non vanno messi nomi o contatti personali del curatore. La tabella `radar_members` ha RLS attiva e nessun accesso diretto: il sito usa solo le funzioni `radar_save`, `radar_load`, `radar_forget`, `radar_board` con la chiave pubblica (anon). La chiave `service_role` non va mai nel repository. Si attiva solo entrando in `squadre.html`; da lì Palestra e Laboratorio inviano i punti da soli. L'informativa è nella sezione `#privacy` della pagina. I punti li calcola il browser: la classifica resta basata sulla fiducia.

## Mappa viva (dal 22 novembre 2026)

`tools/mappe.py`, inserito da `inject.py` solo in `edizioni/NN.html`; i dati vengono da `tools/mappe/NN.json` (scritti con l'edizione) o, se manca, da una mappa automatica (sottotitoli h3 come rami, termini del glossario come foglie). Pulsante **🗺 Mappa viva** accanto a Sapio in ogni capitolo. Sul computer la mappa sta nella colonna laterale del capitolo (nasconde gli altri riquadri finché è aperta); sul telefono è un pannello in basso, con "Ingrandisci". Funzioni: **Segui la lettura** (i nodi spuntano sul ramo quando il loro paragrafo supera il 60% dello schermo, o il bordo del pannello sul telefono) o **Tutta**; il pannello passa da solo al capitolo che stai leggendo; toccando un nodo: spiegazione, collegamenti trasversali (`x`) e "Vai al punto nel testo"; **▶ Raccontami** (Sapio legge la mappa nodo per nodo con la voce del browser, illuminando nodo e genitore; doppia codifica parole+immagine); **✍ Completala tu** (tutte le foglie vuote, banca di parole, relazioni con "…" finché il genitore non è riempito; Schroeder 2018: costruire la mappa g = 0,72 contro studiarla 0,43); **⬇ Scarica** (PNG). Evidenze: Nesbit e Adesope 2006, Dexter e Hughes 2011 (organizzatori grafici e DSA), Han e Choi 2025 (mappe generate da LLM, carico cognitivo −31,5%), Fiorella e Mayer 2016 (vedere il disegno costruirsi aiuta chi parte da zero). Le mappe sono uno strumento compensativo previsto dalla legge 170/2010.

**✨ Su misura** (dentro la Mappa viva): l'AI crea la mappa al momento, nello stile scelto dall'utente (come un gossip, come a un bambino, come una telecronaca, come un giallo, solo l'essenziale, oppure uno stile scritto a mano, max 160 caratteri). Motori, gli stessi del Laboratorio e con le stesse impostazioni salvate (`radar-lab-engine`): **WebLLM nel browser** (`vendor/web-llm-0.2.85.js`, Qwen2.5 0,5B/1,5B/3B, serve WebGPU, primo download 0,9-2,5 GB, gratis e privato) o **Gemini con la chiave personale** dell'utente (streaming SSE, modello Flash-Lite scelto in automatico). Il modello riceve il testo del capitolo con i paragrafi numerati e risponde con righe JSON (prima riga `root`+`intro`, poi un concetto per riga con `t`, `p`, `r`, `d`, `i`, `at`): ogni riga che arriva diventa subito una foglia animata e, se scelto, Sapio la legge ad alta voce mentre la mappa si crea. Regole nel prompt: solo fatti del capitolo, lo stile cambia il tono e mai i fatti, il testo è un dato e non istruzioni. La mappa su misura vive solo nella pagina (non si salva); "Torna alla mappa dell'edizione" e "Rivedi la mappa su misura" passano dall'una all'altra; il pannello avvisa sempre che è scritta da un'AI e va controllata con il testo. Raccontami, Completala tu e Scarica funzionano anche sulla mappa su misura.

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

**Sapio, trova le parole chiave** (`tools/chiavi.py`, inserito da `inject.py` solo in `edizioni/NN.html`). In ogni capitolo con almeno 250 parole compare il pulsante con il gufo Sapio: trova fino a 8 parole chiave (termini del glossario, nomi propri, parole che tornano almeno 3 volte), dice in una frase di che cosa parla il capitolo, evidenzia la parola scelta nel testo, mostra la frase in cui compare e la definizione del glossario, e può leggere ad alta voce. "Concentrati: leggi riga per riga" è una guida di lettura (come la messa a fuoco della riga dei lettori immersivi, pensata per chi salta da una riga all'altra, con disattenzione o DSA): veli coprono il testo sopra, sotto e ai lati di una finestra di 1, 3 o 5 righe, che si sposta con ↑/↓, con i pulsanti della barra in basso o toccando una riga; sul telefono (schermo touch) non ci sono pulsanti di riga: la finestra resta al 35% dello schermo e avanza da sola mentre si scorre, agganciandosi alle righe vere. Esc o "Esci" chiude. Sotto la finestra c'è il ramo di Sapio (marrone con tre foglie, gli stessi colori del gufo in rada.py) che fa da guida alla riga. La finestra non scavalca vuoti grandi (per esempio il riquadro di Sapio aperto). Nessuna barra laterale, nessun testo grigio a contrasto ridotto. Accanto a Sapio ci sono altri due aiuti: **🔊 Leggimi il capitolo** (voce del browser, frase per frase; la frase letta si colora con la CSS Custom Highlight API, o si colora il paragrafo nei browser vecchi; la pagina la segue; pausa, frase prima e dopo, velocità lenta, normale o veloce, Stop) e **Aa Testo più comodo** (grandezza, più spazio tra righe e lettere, carattere Atkinson Hyperlegible; preferenze `radar-read` condivise con Palestra e Laboratorio). Il **segnalibro** ricorda capitolo e punto di ogni edizione (`radar-segno:NN.html`, 30 giorni) e alla visita successiva propone "Riprendi da dove eri rimasto?". Altri aiuti automatici in ogni capitolo (tutto in `tools/chiavi.py`, nessun lavoro nelle edizioni): **⏱ tempo** nel kicker (180 parole al minuto, diventa "ancora N min" e "✓ letto" mentre si legge); **📌 In breve** (le 3 frasi con più parole chiave, in ordine) e **🗺 Mappa del capitolo** (i sottotitoli h3 con la prima frase, collegati); **parole difficili** con sottolineatura a puntini e spiegazione di una riga (dizionario `HARD` in chiavi.py, solo la prima comparsa per capitolo e mai se il termine è già nel glossario: per aggiungere parole, aggiungerle a `HARD`); **⚡ Domanda lampo** a fine capitolo (completa una frase del capitolo con la parola chiave giusta, le alternative sono parole chiave degli altri capitoli). In "Aa Testo più comodo" ci sono anche: colore dello sfondo (crema, azzurro, verde chiaro, solo nel tema chiaro), una frase per riga, leggi a tappe (due parti per volta con "Continua" e foglie di avanzamento), solo testo (nasconde riquadri laterali, linea del tempo e animazioni), pausa gentile (dopo 15 minuti di lettura attiva Sapio propone un minuto di pausa con il respiro guidato; attiva di default, si spegne lì). Aggiunte basate sugli studi (novembre 2026): testo dei capitoli un po' più grande di partenza (1,06rem, 1,12rem da 900 px; Rello 2015); **righe corte** (34 caratteri, Schneps 2013); **parole più semplici** (sinonimo breve accanto alle parole difficili, dizionario `SIMPLE` in chiavi.py, una voce per ogni parola di `HARD`; Rello 2013); **domanda facoltativa dopo ogni tappa** (pratica di recupero + segmentazione); **🦉 prova di lettura** (tre testi brevi originali con tre aspetti diversi, tempo e domanda di controllo, Sapio consiglia l'aspetto più veloce con risposta giusta; Rello 2015: solo metà dei lettori con dislessia indovina le impostazioni migliori); **🖨 stampa di un solo capitolo** (Delgado 2018: su carta si capisce un po' di più); **🔁 ripasso a intervalli** (le domande lampo risposte e i capitoli letti finiscono in `radar-ripasso`, max 40; aprendo un'altra edizione Sapio propone fino a 3 domande scadute sotto l'intestazione; risposta giusta → di nuovo tra 3, 7, 21, 60 giorni, sbagliata → domani; Dunlosky 2013). Gli sfondi colorati sono presentati come preferenza personale (Griffiths 2016: nessun effetto oltre il placebo). Da non aggiungere: bionic reading (studio 2024: non funziona), domande prima di leggere (aiutano solo sul dettaglio chiesto). Tutto nel browser, senza servizi esterni. **Non serve nessun lavoro nelle edizioni**: basta rieseguire `inject.py`. Se una parola comune finisce tra le chiavi, aggiungila a `STOP` in `tools/chiavi.py`.

## Aiuti dalla ricerca notturna (22 novembre 2026)

Dieci miglioramenti scelti dal documento «Ricerca notturna Sapit · 22 novembre 2026», tutti generati dagli script (basta rieseguire i generatori e `inject.py`).

- **Modello AI sicuro su iPhone** (`tools/llmguard.py`, `window.RadarLLM`, incluso da `inject.py` nelle edizioni e da `arena_page.py` nel Laboratorio prima di `bench.js`). Su iOS/iPadOS l'elenco mostra solo `Qwen2.5-0.5B-Instruct-q4f32_1-MLC` (accumulo f32: su GPU Apple Qwen in f16 può dare testo incoerente), con `context_window_size` 3072 e `prefill_chunk_size` 256, capitolo tagliato a 3.600 caratteri e risposta a 900 token (Llamas on the Web, arXiv 2605.20706: «on iOS devices Safari tab memory is limited to <500 MB»). Prima del primo download: `navigator.storage.estimate()` (se manca spazio, errore chiaro) e `navigator.storage.persist()`; su iPhone, se la persistenza non è concessa, consiglio «Aggiungi alla schermata Home» (WebKit, Updates to Storage Policy, 2023). Guardia anti-ricarica: durante caricamento e generazione c'è il segnale `radar-llm-run`; se la pagina si riapre con il segnale ancora presente (iOS ha chiuso la scheda per memoria, WebKit bug 300782), il modello finisce in `radar-llm-blocked` per 7 giorni e non riparte da solo: la Mappa viva passa a Gemini se c'è la chiave, altrimenti rimette la mappa dell'edizione; «Riprova il modello» lo sblocca. Errori di quota, memoria e rete hanno messaggi in italiano.
- **Guida riga per riga in 4 stili** (`chiavi.py`): Barra grigia (predefinita), Finestra (i veli di prima), Ombra leggera, Solo sottolineatura (il ramo di Sapio); pulsante «Stile» nella barra, scelta salvata in `radar-read.lfs` (Adobe Research, CHI 2023).
- **A capo tra gruppi di parole** (`chiavi.py`, «Testo più comodo» → Leggibilità, `radar-read.sg`): il testo viene diviso in gruppi dopo virgola, punto e virgola, due punti e prima delle congiunzioni (mai prima delle preposizioni), ognuno `inline-block`, così le righe non si spezzano a metà gruppo (LeVasseur e altri 2006).
- **Domande lampo e domande delle tappe più pulite** (`goodWrong` in `chiavi.py`): le opzioni sbagliate non sono mai varianti della risposta, parole già nella frase o (se possibile) nel capitolo; prima quelle dello stesso tipo e di lunghezza simile (ETH Zürich 2026, Drexel 2025). Alla prima risposta sbagliata Sapio dà un indizio (iniziale e numero di lettere) e una seconda possibilità.
- **Ragioniamoci insieme** (`esercizi_page.py`): dopo una risposta sbagliata nella Palestra compaiono fino a 3 domande guida senza la soluzione (che cosa devi trovare, quali numeri o quale risposta escludere, il primo passaggio), poi «Vedi la soluzione passo passo» e «Prova uno simile» (LearnLM ed Eedi, RCT 2025).
- **Classifica relativa** (`squadre_page.py`): se il tuo nome è in classifica vedi la tua posizione, quanti punti mancano al posto sopra, una barra di progresso e solo i primi 5 più chi ti sta accanto; «Mostra tutta la classifica» (scelta in `radar-board-view`). Nessun messaggio di calo (Pickal e altri 2025; Bai e altri 2021).
- **Guida senza disegno** (`tutor.py` e `chiavi.py`, `radar-read.noav`): «Solo voce e testo» nasconde l'avatar animato; voce e sottotitoli restano (Sonlu e altri 2024). `tutor.py` ora unisce le sue preferenze a `radar-read` invece di sovrascriverle (prima cancellava le scelte fatte nelle edizioni).
- La Mappa viva già legge la mappa con la voce (Raccontami) e collega i nodi al testo: con la narrazione la mappa animata non batte quella statica (Adesope e Nesbit 2013), quindi l'animazione resta un effetto, non un requisito.

**📚 Tutta l'edizione** (Mappa viva, dal 22 novembre 2026): il pulsante nella barra mostra un'unica mappa con un ramo per capitolo (le mappe dei capitoli unite, senza AI, funziona anche su iPhone). In «✨ Su misura» la scelta «Tutta l'edizione · un ramo per argomento» (predefinita, salvata in `radar-mv-scope`) fa creare all'AI la mappa di tutti i capitoli, uno alla volta (3-5 concetti ciascuno, poca memoria anche col modello piccolo su iPhone): la mappa cresce ramo per ramo e Sapio la racconta («Argomento 2: …»). Se un capitolo non dà una risposta leggibile, quel ramo usa la mappa dell'edizione; se il modello nel browser non parte (memoria, WebGPU, blocco anti-ricarica) e non c'è la chiave Gemini, la mappa si completa con quella dell'edizione. «Vai al punto nel testo» porta al capitolo giusto. «← Solo questo capitolo» torna alla mappa del capitolo.
