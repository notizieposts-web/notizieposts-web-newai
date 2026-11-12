# Palette di Radar AI: "Verde Deloitte"

Documento di riferimento per i colori del sito, scelto il 12 novembre 2026. Ogni modifica ai colori parte da qui.

Stato: **applicata a tutto il sito il 12 novembre 2026** (`tools/inject.py`). Resta escluso il modello dell'email, che ha ancora i suoi colori.

## Principi

1. **Base neutra grafite.** Fondi e testi sono grigi neutri, senza blu né viola.
2. **Un solo colore principale, il verde.** Prende il verde del sito di Deloitte (`#86BC24`) come riferimento di tono professionale. Usiamo solo il colore: niente logo, niente punto verde dopo il nome, niente caratteri tipografici di Deloitte, perché Radar AI non deve sembrare un loro sito.
3. **Nel tema scuro cambiano solo fondi e testi.** Pulsanti, etichette e colori di stato restano riconoscibili: il pulsante principale è identico nei due temi.
4. **Mai solo il colore.** Giusto, sbagliato e difficoltà hanno sempre anche un segno (✓, ✕) o una parola.
5. **Pubblico da 15 a 40 anni.** Vivace nei dettagli (serie di giorni, avanzamento), sobrio nella struttura.
6. **Accessibilità WCAG 2.2 AA** in entrambi i temi, verificata con `tools/audit3.py`.

## Colori

### Neutri

| Ruolo | Tema chiaro | Tema scuro |
|---|---|---|
| Fondo della pagina | `#F6F6F5` | `#121212` |
| Superficie (schede, pannelli) | `#FFFFFF` | `#1E1F21` |
| Testo | `#1C1D1F` | `#EDEDED` |
| Testo secondario | `#55575B` | `#A9AAAF` |
| Linee e bordi | `#D6D6D4` | `#3A3B3F` |

### Verde

| Ruolo | Colore | Testo sopra | Uso |
|---|---|---|---|
| Pulsante principale | `#3F7A12` | `#FFFFFF` | pulsanti, link d'azione; uguale in chiaro e in scuro, senza bordo |
| Verde chiaro (accento) | `#86BC24` | `#000000` | serie di giorni, barra di avanzamento, evidenziazioni; solo testi brevi in grassetto |

### Stati e difficoltà

| Ruolo | Tema chiaro (testo / fondo) | Tema scuro (testo / fondo) | Segno |
|---|---|---|---|
| Giusto, Facile | `#2E6B12` / `#E6F2D3` | `#9CD84A` / `#1C2A12` | ✓ |
| Attenzione, Media | `#9A4B00` / `#FCEFD9` | `#FFB86B` / `#3A2A12` | parola |
| Sbagliato, Difficile | `#B3261E` / `#FBE7E5` | `#FF8A80` / `#40201E` | ✕ |

Le guide Sapio (gufo) e Rada (fatina) tengono i loro colori naturali in entrambi i temi (`tools/rada.py`).

## Misure di contrasto

WCAG 2.2 è la norma in vigore (testo almeno 4,5:1, livello AA; 7:1 livello AAA; pulsanti e icone almeno 3:1). APCA è il metodo indicato nella bozza di WCAG 3, non ancora norma: le soglie usate (Lc 75 testo normale, Lc 60 testo in grassetto di almeno 16 px) sono quelle proposte dai suoi autori.

| Coppia | WCAG 2.2 | APCA | Esito |
|---|---|---|---|
| Testo bianco su `#3F7A12` (pulsante) | 5,24:1, AA | Lc 81 | ✓ |
| Pulsante `#3F7A12` sul fondo chiaro `#F6F6F5` | 4,85:1 | | ✓ (minimo 3:1) |
| Pulsante `#3F7A12` sul fondo scuro `#121212` | 3,57:1 | | ✓ (minimo 3:1) |
| Testo nero su `#86BC24` (accento) | 9,23:1, AAA | Lc 59 | ✓ solo testo breve in grassetto |
| Testo bianco su `#86BC24` | 2,27:1 | Lc 49 | ✕ non usare |
| Testo `#1C1D1F` sul fondo `#F6F6F5` | 15,6:1, AAA | | ✓ |
| Testo `#EDEDED` sul fondo `#121212` | 16,0:1, AAA | | ✓ |
| Testo secondario chiaro / scuro | 6,69:1 / 8,08:1 | | ✓ |
| Giusto, chiaro / scuro | 5,58:1 / 8,88:1 | | ✓ |
| Sbagliato, chiaro / scuro | 5,50:1 / 6,37:1 | | ✓ |
| Attenzione, chiaro / scuro | 5,47:1 / 8,11:1 | | ✓ |

## Regole ufficiali di riferimento

- Testo almeno 4,5:1, titoli grandi almeno 3:1, senza arrotondare: [W3C, WCAG 2.2, criterio 1.4.3](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html)
- Livello AAA, 7:1: [W3C, WCAG 2.2, criterio 1.4.6](https://www.w3.org/WAI/WCAG22/Understanding/contrast-enhanced.html)
- Pulsanti, icone e stati almeno 3:1 con ciò che hanno accanto: [W3C, WCAG 2.2, criterio 1.4.11](https://www.w3.org/WAI/WCAG22/Understanding/non-text-contrast)
- Contrasto percepito e APCA (bozza, non normativa): [W3C, WCAG 3, Visual contrast of text](https://www.w3.org/WAI/GL/WCAG3/2022/how-tos/visual-contrast-of-text)
- Mai affidarsi al solo colore: [Apple, Human Interface Guidelines, Color](https://developer.apple.com/design/human-interface-guidelines/color)
- Il tema scuro non è l'inverso del chiaro; almeno 4,5:1, meglio 7:1 per il testo piccolo: [Apple, Human Interface Guidelines, Dark Mode](https://developer.apple.com/design/human-interface-guidelines/dark-mode)
- Fondo scuro `#121212` invece del nero, testo non bianco puro, colori meno saturi: [Google, Material Design, laboratorio sul tema scuro](https://codelabs.developers.google.com/codelabs/design-material-darktheme/) · [Android Developers, Dark theme with MDC](https://medium.com/androiddevelopers/dark-theme-with-mdc-4c6fc357d956)
- Verde di riferimento `#86BC24`, come compare nel CSS del sito di Deloitte (Deloitte non pubblica una guida ufficiale ai colori): [delware.deloitte.com, landing.css](https://delware.deloitte.com/css/landing.css)

## Dove si applica

- `tools/inject.py`, righe `:root`: tutti i colori del sito, per i temi chiaro e scuro. Variabili: `--violet` = pulsante verde `#3F7A12` (il nome resta per compatibilità), `--on-violet` = testo bianco sopra il verde, `--violet-ink` = verde per i testi (`#3F7A12` in chiaro, `#9CD84A` in scuro), `--accent` / `--on-accent` = `#86BC24` con testo nero (badge «AI» del logo), `--teal`, `--sun`, `--red` con le loro tinte `-soft` per gli stati. Subito sotto, un blocco forza il testo bianco su tutti i componenti con fondo verde.
- `tools/logo.py` (logo e favicon) e `tools/site_meta.py` (immagini di anteprima e pagina 404).
- `tools/mail_template_teaser.html`: il modello dell'email ha ancora i suoi colori e si cambia solo con un'approvazione a parte.

Dopo ogni modifica: rigenera le pagine, poi `python3 tools/audit3.py "$(pwd)"` e `python3 tools/reflow.py "$(pwd)"`, che devono stampare nulla.
