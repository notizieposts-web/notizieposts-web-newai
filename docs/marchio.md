# Il marchio Sapit

Dal 12 novembre 2026 il sito si chiama **Sapit** (prima «Radar AI»). Dal latino *sapio, sapere*: «egli sa, ha giudizio». Si pronuncia «sàpit».

## Il marchio e il personaggio

- **Sapit** è il nome del sito e del marchio (logo, favicon, anteprime).
- **Sapio** è il gufetto, il personaggio che guida, spiega e legge ad alta voce negli esercizi e negli aiuti. Il nome resta Sapio (deciso il 12 novembre 2026).
- Insieme: Sapio è il gufo di Sapit.

## La storia

Il sapere oggi passa dall'intelligenza artificiale e cambia ogni giorno. Sapit è il gufo che veglia di notte e la mattina ti porta quello che conta. Frase: **«Lui sa. Tu impari.»** Racconto completo, pubblico e confronto con le alternative: [`storia.md`](storia.md).

| Cosa sa fare | Segno nel logo |
|---|---|
| Sa guidarti | il becco che punta in avanti e lo sguardo dritto |
| Sa aggiornarti | le onde radar sopra l'orecchio e la lancetta verde nell'occhio |
| Sa aiutarti a farlo tuo | il puntino sulla «i», ambra con l'anello verde: mettere i puntini sulle i |

## File

- `tools/logo.py`: gufo, scritta (Fredoka Bold, licenza OFL, `tools/fonts/Fredoka-Bold.woff`, trasformata in tracciati) e favicon; lo inserisce `tools/inject.py` in ogni pagina.
- `img/brand/`: icona SVG e PNG (48, 96, 180 per la schermata Home, 192, 512, 512 ritagliabile con il gufo nel cerchio dell'80 per cento), gufo per le anteprime, logo completo chiaro e scuro in SVG e PNG.
- `tools/site_meta.py`: nome del sito (`NAME`), titoli, anteprime `img/og/` con il gufo, feed e 404.

## Regole d'uso

- Sempre «sapit» minuscolo e attaccato nel logo; nei testi «Sapit». Mai «SAPIT» o «SAP IT»: si confonde con il gestionale SAP.
- Il gufo sempre davanti al nome. Simbolo mai sotto i 16 pixel.
- Spazio libero intorno al logo: almeno quanto un occhio del gufo.
- Il gufo tiene i suoi colori su ogni fondo; la scritta è grafite sul chiaro e grigio chiarissimo sullo scuro.
- Niente gufo verde con occhi bianchi (ricorderebbe un'app di lingue molto nota).

## Regole ufficiali seguite

- Favicon quadrata, consigliata oltre 48×48, indirizzo stabile: [Google Search Central](https://developers.google.com/search/docs/appearance/favicon-in-search)
- Zona sicura: cerchio con raggio pari al 40 per cento del lato: [web.dev, maskable icons](https://web.dev/articles/maskable-icon) · [MDN, app icons](https://developer.mozilla.org/en-US/docs/Web/Progressive_web_apps/How_to/Define_app_icons)
- Il testo del logo non ha obblighi di contrasto; la parte grafica segue i 3:1: [W3C, WCAG 2.2, 1.4.3](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html)

## Da fare

- Verifiche prima di registrarlo: marchio (UIBM, EUIPO), dominio e profili social.
- Email della newsletter e testi audio dicono ancora «Radar AI»: il modello dell'email si cambia solo con approvazione.
