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
7. **Stato per l'invio**: scrivi `tools/ultima.json` con `{"n": NN, "data": "AAAA-MM-GG", "titolo": "...", "descrizione": "...", "chips": [...], "statistiche": [[valore, etichetta], x3], "items": [[emoji, protagonista, titolo, testo], ...], "domanda": "..."}` e includilo nel commit. Serve all'operazione di invio delle 9:00 (preparazione alle 8:40).

## Email (invio)

Template: `tools/mail_template_teaser.html` (sfondo bianco, contrasti verificati anche con l'inversione della modalità scura di Gmail). Sostituisci: data, chip dei protagonisti, titolo, descrizione, tre statistiche, le voci "Dentro trovi" (pillola protagonista + titolo + testo), la domanda del giorno, i link all'edizione (`edizioni/NN.html`) e all'archivio (radice del sito), il numero totale di edizioni. L'email è un **invito alla lettura**, non il contenuto completo. Invia con il connettore Gmail (`send_message` con `htmlBody`), mittente notizieposts@gmail.com.

## Altre pagine

- `azure.html` (guida per tema), `azure-esercizi.html` (palestra), `azure-laboratorio.html` + `lab-*.html` (gioco): si rigenerano con `guida.py`, `esercizi_page.py`, `lab_page.py`. Il Laboratorio e la Palestra non vanno toccati in un'edizione normale.
