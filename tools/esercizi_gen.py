"""Generatore degli esercizi su Azure Content Understanding.
Ogni esercizio: id, l (1 media, 2 alta, 3 estrema), g (gruppo), t (titolo), q (testo HTML), k (num|mcq),
 per num: a (valore), tol, u (unità), fa (risposta formattata); per mcq: o (opzioni), c (indice corretto);
 s (soluzione HTML), p (puntate di riferimento)."""
import random, math, json, re, os

def it(x, d=0):
    """Formato italiano: 1.234,56"""
    if d == 0:
        s = '{:,.0f}'.format(round(x))
    else:
        s = '{:,.{}f}'.format(x, d)
    return s.replace(',', 'X').replace('.', ',').replace('X', '.')

def money(x, d=2): return it(x, d) + ' $'

EX = []
SEEN = set()
def add(g, l, t, q, s, p, k='num', a=None, tol=None, u='', o=None, c=None, fa=None):
    key = re.sub(r'\s+', ' ', q)
    if key in SEEN: return
    SEEN.add(key)
    e = {'g': g, 'l': l, 't': t, 'q': q, 's': s, 'p': p, 'k': k}
    if k == 'num':
        e['a'] = a; e['tol'] = tol if tol is not None else (0.5 if float(a).is_integer() else max(abs(a) * 0.01, 0.01)); e['u'] = u
        e['fa'] = fa or (it(a, 0 if float(a).is_integer() else 2) + (' ' + u if u else ''))
    else:
        # mescola le opzioni in modo deterministico
        r = random.Random(key)
        idx = list(range(len(o)))
        if len(o) > 2: r.shuffle(idx)
        e['o'] = [o[i] for i in idx]; e['c'] = idx.index(c)
    EX.append(e)

def mins_hm(m):
    h = int(m // 60); mm = int(round(m - h * 60))
    if mm == 60: h += 1; mm = 0
    return ('%d h %d min' % (h, mm)) if h else ('%d min' % mm)

# ---------------------------------------------------------------- COSTI E VOLUMI
def t_pagine():
    r = random.Random(1)
    for i in range(70):
        kind = i % 5
        if kind == 0:
            ch = r.randint(2, 400) * 250 + r.randint(1, 249)
            a = math.ceil(ch / 3000)
            add('costi', 1, 'Pagine di un file di testo', 'Un file <code>.txt</code> contiene %s caratteri. Quante pagine fatturabili conta Content Understanding?' % it(ch),
                'Per testo ed email 3.000 caratteri valgono una pagina, arrotondando per eccesso: %s ÷ 3.000 = %s → <b>%d pagine</b>.' % (it(ch), it(ch / 3000, 2), a), 'P1', a=a, u='pagine')
        elif kind == 1:
            v, h = r.randint(1, 12), r.randint(0, 40)
            add('costi', 1, 'Pagine di un foglio Excel', 'Una cartella <code>.xlsx</code> ha %d fogli visibili e %d fogli nascosti. Quante pagine fattura il servizio?' % (v, h),
                'Ogni foglio è una pagina, <b>compresi quelli nascosti</b>: %d + %d = <b>%d pagine</b>. Rimuovere i fogli inutili prima dell\'invio riduce il conto.' % (v, h, v + h), 'P1', a=v + h, u='pagine')
        elif kind == 2:
            n = r.randint(5, 120)
            add('costi', 1, 'Pagine di una presentazione', 'Un file <code>.pptx</code> ha %d diapositive. Quante pagine fatturabili conta il servizio?' % n,
                'Per le presentazioni ogni diapositiva è una pagina: <b>%d pagine</b>.' % n, 'P1', a=n, u='pagine')
        elif kind == 3:
            em = [r.randint(400, 20000) for _ in range(r.randint(3, 6))]
            a = sum(math.ceil(x / 3000) for x in em)
            add('costi', 2, 'Pagine di un lotto di email', 'Un lotto contiene %d email <code>.eml</code> di %s caratteri ciascuna. Quante pagine fatturabili in totale? (Ogni file si arrotonda per conto suo.)' % (len(em), ', '.join(it(x) for x in em)),
                'L\'arrotondamento per eccesso vale per file: ' + ' + '.join('⌈%s/3.000⌉=%d' % (it(x), math.ceil(x / 3000)) for x in em) + ' = <b>%d pagine</b>. Sommare prima i caratteri e poi dividere darebbe %d: è l\'errore tipico.' % (a, math.ceil(sum(em) / 3000)), 'P1', a=a, u='pagine')
        else:
            txt = r.randint(1000, 30000); xs, xh = r.randint(1, 6), r.randint(0, 20); sl = r.randint(5, 40); dp = r.randint(2, 30)
            a = math.ceil(txt / 3000) + xs + xh + sl + dp
            add('costi', 2, 'Pacchetto misto di file', 'Un fornitore manda: un file di testo da %s caratteri, un Excel con %d fogli visibili e %d nascosti, una presentazione da %d diapositive e un Word con paginazione nativa di %d pagine. Pagine fatturabili totali?' % (it(txt), xs, xh, sl, dp),
                'Testo ⌈%s/3.000⌉ = %d; Excel %d + %d = %d; PowerPoint %d; Word %d (paginazione nativa). Totale <b>%d pagine</b>.' % (it(txt), math.ceil(txt / 3000), xs, xh, xs + xh, sl, dp, a), 'P1', a=a, u='pagine')

def t_tempo_quota():
    r = random.Random(2)
    for i in range(45):
        n = r.choice([1, 2, 5]) * 10 ** r.randint(3, 5) + r.randint(0, 9) * 1000
        if i % 3 == 0:
            m = n / 1000
            add('costi', 1, 'Tempo minimo alla quota', 'Con la quota standard di 1.000 pagine al minuto, qual è il tempo minimo per elaborare %s pagine? Rispondi in minuti.' % it(n),
                '%s ÷ 1.000 = <b>%s minuti</b> (%s). La quota è una velocità, non una scorta: nessuna ottimizzazione scende sotto questo valore senza un aumento di quota.' % (it(n), it(m, 0 if m.is_integer() else 1), mins_hm(m)), 'P1', a=m, u='min', tol=0.6)
        else:
            pct = r.choice([80, 85, 90])
            rate = 1000 * pct / 100; m = n / rate
            add('costi', 2, 'Flusso regolare sotto il muro', 'Vuoi elaborare %s pagine restando al %d%% della quota di 1.000 pagine/minuto, per non ricevere 429. Quanti minuti servono (arrotonda per eccesso)?' % (it(n), pct),
                'Ritmo = 1.000 × %d%% = %s pagine/min. Tempo = %s ÷ %s = %s → <b>%d minuti</b> (%s).' % (pct, it(rate), it(n), it(rate), it(m, 2), math.ceil(m), mins_hm(math.ceil(m))), 'P1, P10', a=math.ceil(m), u='min')

def t_audio_quota():
    r = random.Random(3)
    for i in range(25):
        h = r.randint(10, 3000)
        m = h / 4
        add('costi', 1, 'Quota di audio e video', 'La quota standard è di 4 ore di audio o video al minuto. Quanti minuti servono, al minimo, per un archivio di %s ore di registrazioni?' % it(h),
            '%s ÷ 4 = <b>%s minuti</b> (%s).' % (it(h), it(m, 2 if not m.is_integer() else 0), mins_hm(m)), 'P4', a=m, u='min', tol=0.3)

def t_contest():
    r = random.Random(4)
    kinds = [('un analizzatore personalizzato senza esempi etichettati', 1), ('un analizzatore personalizzato addestrato con esempi etichettati', 3),
             ('un analizzatore in modalità agentica (<code>config.workflow = "agentic"</code>)', 3), ('<code>prebuilt-invoice</code>', 1), ('<code>prebuilt-contract</code>', 1),
             ('il modulo fiscale <code>prebuilt-tax.us.1040</code>', 3), ('<code>prebuilt-receipt.generic</code>', 1)]
    for i in range(56):
        name, rate = kinds[i % len(kinds)]
        p = r.randint(5, 900) * 100
        a = p / 1000 * rate
        add('costi', 2 if i % 2 else 1, 'Costo di contestualizzazione', 'Quanto costa la sola <b>contestualizzazione</b> di %s pagine con %s? (Tariffe: standard 1 $ ogni 1.000 pagine, avanzata 3 $.)' % (it(p), name),
            '%s usa la tariffa <b>%s</b>: %s ÷ 1.000 × %d $ = <b>%s</b>.' % (name[0].upper() + name[1:], 'standard' if rate == 1 else 'avanzata', it(p), rate, money(a)), 'P2, P6, P15', a=a, u='$', tol=0.01)

def t_costo_completo():
    r = random.Random(5)
    for i in range(80):
        p = r.choice([10, 100, 500, 1000, 2000, 5000, 10000, 25000, 50000, 110000]) * r.randint(1, 3)
        conf = r.random() < .5
        tin = 5200 if conf else 2600; tout = 180
        ex = r.choice([1.5, 5, 5, 10]); pin = r.choice([0.4, 1.25, 2, 4]); pout = pin * 4; ctx = 1
        c_ex = p / 1000 * ex; c_in = p * tin / 1e6 * pin; c_out = p * tout / 1e6 * pout; c_ctx = p / 1000 * ctx
        tot = c_ex + c_in + c_out + c_ctx
        lvl = 2 if i % 3 else 3
        add('costi', lvl, 'Conto completo di un lotto', ('Stima il costo totale di %s pagine con un analizzatore a contestualizzazione standard, %s. '
             'Usa questi valori ipotetici: estrazione %s ogni 1.000 pagine; %s token in ingresso e 180 in uscita per pagina; modello a %s per milione di token in ingresso e %s in uscita; contestualizzazione 1 $ ogni 1.000 pagine.')
             % (it(p), 'con stima di fonte e confidenza attiva' if conf else 'senza stima di confidenza', money(ex), it(tin), money(pin), money(pout)),
            ('Estrazione: %s/1.000 × %s = %s. Ingresso: %s × %s token = %s token → %s. Uscita: %s × 180 = %s token → %s. Contestualizzazione: %s. '
             'Totale <b>%s</b>. %s')
             % (it(p), money(ex), money(c_ex), it(p), it(tin), it(p * tin), money(c_in), it(p), it(p * tout), money(c_out), money(c_ctx), money(tot),
                'Con la confidenza accesa i token in ingresso sono circa il doppio: è la leva più grossa dopo il modello.' if conf else 'Accendendo la confidenza ovunque i token in ingresso raddoppierebbero: meglio attivarla solo sui campi critici.'),
            'P2, P15', a=round(tot, 2), u='$', tol=max(tot * 0.01, 0.01))

def t_ufficiale():
    # Esempio ufficiale: 10 pagine prebuilt-invoice = 0,0837 $
    r = random.Random(6)
    for i in range(20):
        p = r.randint(1, 500) * 1000
        a = p / 10 * 0.0837
        add('costi', 1, 'Scalare l\'esempio ufficiale', 'Nell\'esempio ufficiale, 10 pagine con <code>prebuilt-invoice</code>, confidenza attiva e GPT-5.2 globale costano 0,0837 $. A parità di condizioni, quanto costerebbero %s pagine?' % it(p),
            '0,0837 $ ÷ 10 = 0,00837 $ a pagina; × %s = <b>%s</b>. Senza confidenza i token in ingresso si dimezzano e il totale scende.' % (it(p), money(a)), 'P15', a=round(a, 2), u='$', tol=max(a * 0.005, 0.01))

def t_maxtokens():
    r = random.Random(7)
    for i in range(65):
        tpm = r.choice([30000, 50000, 100000, 150000, 240000, 300000, 450000, 1000000])
        pr = r.choice([800, 1500, 2000, 2600, 3000, 4000, 5200])
        mt = r.choice([100, 200, 300, 500, 800, 1000, 2000, 4000, 8000])
        rpm = tpm / (pr + mt)
        if i % 2 == 0:
            add('costi', 2, 'Richieste al minuto con max_tokens', 'Una distribuzione ha %s TPM. Ogni chiamata ha %s token di prompt e <code>max_tokens</code> = %s. Quante richieste al minuto regge, al massimo (arrotonda per difetto)?' % (it(tpm), it(pr), it(mt)),
                'La quota stima ogni richiesta su prompt + <code>max_tokens</code> al momento dell\'arrivo, non sui token effettivi: %s ÷ (%s + %s) = %s → <b>%d richieste/min</b>.' % (it(tpm), it(pr), it(mt), it(rpm, 1), int(rpm)), 'P8', a=int(rpm), u='rich./min')
        else:
            real = r.choice([150, 200, 250, 300])
            if real >= mt: continue
            rpm2 = tpm / (pr + real)
            add('costi', 3, 'Il prezzo di un max_tokens sovradimensionato', 'Con %s TPM e %s token di prompt, le risposte reali sono di circa %d token, ma <code>max_tokens</code> è impostato a %s. Quante richieste al minuto in più reggeresti impostando <code>max_tokens</code> = %d? (Arrotonda ciascun valore per difetto prima di sottrarre.)' % (it(tpm), it(pr), real, it(mt), real),
                'Ora: %s ÷ %s = %d rich./min. Con max_tokens %d: %s ÷ %s = %d rich./min. Differenza <b>%d</b>. La quota si consuma su ciò che "prenoti", non su ciò che usi.' % (it(tpm), it(pr + mt), int(rpm), real, it(tpm), it(pr + real), int(rpm2), int(rpm2) - int(rpm)), 'P8', a=int(rpm2) - int(rpm), u='rich./min')

def t_concorrenza():
    r = random.Random(8)
    for i in range(70):
        tpm = r.choice([100000, 150000, 200000, 300000, 450000, 600000])
        pr = r.choice([2000, 2600, 3000, 3500, 4000]); mt = r.choice([200, 300, 400, 500])
        lat = r.choice([2, 3, 4, 5, 6, 8]); n = r.choice([5000, 10000, 20000, 40000, 92400, 110000])
        rpm = tpm / (pr + mt); flight = rpm * lat / 60
        if i % 2 == 0:
            a = math.ceil(flight)
            add('costi', 2, 'Quante chiamate in volo', 'TPM %s, prompt %s token, <code>max_tokens</code> %s, latenza media misurata %d secondi. Quante chiamate devono essere in volo contemporaneamente per sfruttare la quota? (Arrotonda per eccesso.)' % (it(tpm), it(pr), it(mt), lat),
                'Richieste/min = %s ÷ %s = %s. In volo = richieste al secondo × latenza = %s ÷ 60 × %d = %s → <b>%d</b> chiamate. È il numero del semaforo, non 50 thread a caso.' % (it(tpm), it(pr + mt), it(rpm, 1), it(rpm, 1), lat, it(flight, 2), a), 'P8', a=a, u='chiamate')
        else:
            hrs = n / rpm / 60
            add('costi', 3, 'Durata di un lotto limitato dal modello', 'Devi mandare al modello %s pagine, una chiamata per pagina. TPM %s, prompt %s token, <code>max_tokens</code> %s. Quante ore dura il lotto, al minimo? (Una cifra decimale.)' % (it(n), it(tpm), it(pr), it(mt)),
                'Richieste/min = %s ÷ %s = %s. Tempo = %s ÷ %s = %s minuti = <b>%s ore</b>. Confrontalo con %s minuti alla quota di pagine: qui il collo di bottiglia è il modello.' % (it(tpm), it(pr + mt), it(rpm, 1), it(n), it(rpm, 1), it(n / rpm), it(hrs, 1), it(n / 1000)), 'P8, P14', a=round(hrs, 1), u='ore', tol=0.15)

def t_finestre():
    r = random.Random(9)
    for i in range(30):
        rpm = r.choice([60, 120, 300, 600, 900, 1200, 1800, 3000])
        if i % 2 == 0:
            add('costi', 2, 'La finestra di un secondo', 'Una distribuzione ha un limite di %s richieste al minuto, controllato su finestre di 1 secondo. Quante richieste al massimo puoi inviare nello stesso secondo senza 429?' % it(rpm),
                'Il limite si aspetta un traffico uniforme: %s ÷ 60 = <b>%s</b> richieste al secondo. Oltre, scatta il 429 anche se nel minuto saresti sotto la quota.' % (it(rpm), it(rpm / 60, 0 if (rpm / 60).is_integer() else 1)), 'P8', a=rpm / 60, u='rich./s', tol=0.05)
        else:
            th = r.choice([10, 20, 30, 50])
            ok = th <= rpm / 60
            add('costi', 2, 'Raffica alla partenza', 'Con un limite di %s richieste al minuto valutato su finestre di 1 secondo, %d thread partono insieme nello stesso secondo. Cosa succede?' % (it(rpm), th),
                'Il limite per secondo è %s. %s' % (it(rpm / 60, 1), 'Restano sotto: nessun 429 per la forma del traffico.' if ok else 'Alcune richieste superano la quota per secondo e ricevono 429, anche se nel minuto la quota non è finita: serve scaglionare le partenze.'),
                'P8', k='mcq', o=['Nessun 429: sono sotto il limite proporzionale al secondo', 'Alcune ricevono 429 per la forma del traffico, anche sotto la quota al minuto', 'Tutte ricevono 429 perché la quota al minuto è finita'], c=0 if ok else 1)

def t_backoff():
    seq = [2, 5, 13, 34]
    r = random.Random(10)
    for k in range(1, 5):
        add('costi', 1, 'Attesa crescente', 'Usi l\'attesa crescente suggerita dalla rubrica (2, 5, 13, 34 secondi). Dopo %d tentativi falliti consecutivi, quanti secondi hai atteso in totale?' % k,
            ' + '.join(str(x) for x in seq[:k]) + ' = <b>%d secondi</b>.' % sum(seq[:k]), 'P1', a=sum(seq[:k]), u='s')
    for i in range(14):
        lib = r.choice([2, 3]); mine = r.choice([3, 5, 7, 10])
        tot = (mine + 1) * (lib + 1)
        add('costi', 3, 'Tentativi che si moltiplicano', 'Hai una tua logica di ripetizione con %d nuovi tentativi, e la libreria ufficiale ne fa altri %d per ogni chiamata. Nel caso peggiore, quante richieste HTTP partono per un singolo documento?' % (mine, lib),
            'Ogni tua chiamata (1 + %d) genera 1 + %d richieste della libreria: (1 + %d) × (1 + %d) = <b>%d</b>. Per questo, con una logica tua, i tentativi della libreria vanno messi a zero.' % (mine, lib, mine, lib, tot), 'P8', a=tot, u='richieste')

def t_sync():
    r = random.Random(11)
    for i in range(55):
        mb = r.choice([0.4, 2, 6, 9.5, 12, 45, 150, 199, 230]); pg = r.choice([1, 3, 5, 6, 20, 120, 300, 320, 800])
        if mb <= 10 and pg <= 5: c = 0
        elif mb <= 10 and pg > 5 and pg <= 300: c = 1
        elif mb <= 200 and pg <= 300: c = 2
        else: c = 3
        exp = ['Va bene la chiamata sincrona: entro 10 MB e 5 pagine.',
               'In sincrono il servizio leggerebbe solo le prime 5 pagine, salvo indicare un intervallo: per il documento intero serve l\'asincrono (fino a 200 MB e 300 pagine).',
               'Supera i 10 MB del sincrono, ma rientra nell\'asincrono (≤ 200 MB, ≤ 300 pagine).',
               'Supera i limiti dell\'asincrono (200 MB o 300 pagine per file): va diviso in più file.'][c]
        add('costi', 1 if i % 2 else 2, 'Sincrono o asincrono', 'Un PDF scansionato pesa %s MB e ha %d pagine. Qual è la scelta corretta?' % (it(mb, 1 if mb % 1 else 0), pg), exp, 'P1, P16', k='mcq',
            o=['Operazione sincrona (analyzeInline / analyzeBinaryInline)', 'Asincrona: in sincrono verrebbero lette solo le prime 5 pagine', 'Asincrona, perché supera i 10 MB del sincrono', 'Dividere il file: supera i limiti dell\'asincrono'], c=c)

def t_av_limiti():
    r = random.Random(12)
    for i in range(45):
        typ = i % 3
        if typ == 0:
            mb = r.choice([50, 180, 199, 250, 900, 2500, 3900, 4200]); mn = r.choice([10, 25, 29, 40, 90, 119, 130])
            if mb <= 200 and mn <= 30: c = 0
            elif mb <= 4096 and mn <= 120: c = 1
            else: c = 2
            add('costi', 1, 'Come mandare un video', 'Un video pesa %s MB e dura %d minuti. Come lo invii?' % (it(mb), mn),
                ['Rientra nel caricamento diretto (≤ 200 MB e ≤ 30 minuti).', 'Supera il caricamento diretto: serve il riferimento a un file su Blob Storage (fino a 4 GB e 2 ore).', 'Supera anche il limite per riferimento (4 GB, 2 ore): va spezzato.'][c],
                'P4', k='mcq', o=['Nel corpo della richiesta (analyzeBinary)', 'Per riferimento a Blob Storage (analyze)', 'Va diviso in più file'], c=c)
        elif typ == 1:
            mb = r.choice([80, 250, 299, 320, 700, 990]); h = r.choice([0.5, 1.5, 1.9, 2.5, 3.5])
            fast = mb <= 300 or h <= 2
            add('costi', 2, 'Audio lento o veloce', 'Un file audio pesa %s MB e dura %s ore. La trascrizione sarà nella fascia "sostanzialmente più veloce" indicata dalla documentazione?' % (it(mb), it(h, 1)),
                'La documentazione indica tempi molto ridotti per file ≤ 300 MB <b>o</b> ≤ 2 ore (limite assoluto 1 GB e 4 ore). %s' % ('Questo file rientra.' if fast else 'Questo file no: conviene spezzarlo in blocchi con qualche secondo di sovrapposizione.'),
                'P4', k='mcq', o=['Sì', 'No, conviene spezzarlo'], c=0 if fast else 1)
        else:
            mn = r.choice([5, 12, 30, 45, 60, 90, 118])
            add('costi', 1, 'Fotogrammi analizzati', 'Il servizio analizza circa un fotogramma al secondo. Quanti fotogrammi analizza, circa, in un video di %d minuti?' % mn,
                '%d × 60 = <b>%s fotogrammi</b>, tutti ridotti a 512×512 pixel: caricare una risoluzione più alta non migliora l\'analisi (il massimo supportato è 1920×1080).' % (mn, it(mn * 60)), 'P4', a=mn * 60, u='fotogrammi', tol=mn)

def t_av_costi():
    r = random.Random(13)
    for i in range(30):
        h = r.randint(5, 2000)
        if i % 2 == 0:
            a = h * 0.10
            add('costi', 1, 'Contestualizzazione dell\'audio', 'La contestualizzazione costa 0,10 $ per ora di audio. Quanto costa per %s ore di chiamate?' % it(h), '%s × 0,10 $ = <b>%s</b>.' % (it(h), money(a)), 'P4', a=round(a, 2), u='$')
        else:
            a = h * (1 - 0.10)
            add('costi', 2, 'Audio invece di video', 'Hai %s ore di riunioni registrate in video, ma ti serve solo il parlato. Quanto risparmi di sola contestualizzazione mandando l\'audio (0,10 $/ora) invece del video (1 $/ora)?' % it(h),
                '%s × (1 − 0,10) $ = <b>%s</b>. Il video costa dieci volte tanto perché porta 3.600 fotogrammi per ora.' % (it(h), money(a)), 'P4', a=round(a, 2), u='$')

def t_contatore():
    cases = [('un file di testo .txt', 0), ('un allegato Word da email', 0), ('un foglio Excel', 0), ('una pagina HTML', 0), ('un\'email .msg', 0), ('una presentazione PowerPoint', 0),
             ('una scansione TIFF di cui serve solo il testo', 1), ('una foto di uno scontrino, solo OCR', 1), ('un PDF scansionato analizzato con prebuilt-read', 1),
             ('un PDF scansionato con tabelle da ricostruire', 2), ('una scansione analizzata con prebuilt-layout', 2), ('una fattura scansionata con prebuilt-invoice', 2)]
    for i, (d, c) in enumerate(cases):
        for ver in range(3):
            q = ['Su quale contatore di estrazione cade %s?', 'Quale contatore applica il servizio a %s, indipendentemente dall\'analizzatore scelto?', 'Il tuo lotto contiene %s. Che contatore paghi?'][ver] % d
            add('costi', 2, 'La regola del contatore', q, 'Il servizio "addebita in base al lavoro svolto su ogni pagina, non all\'analizzatore": i formati digitali (Word, Excel, PowerPoint, HTML, testo, email) vanno su Minimal; PDF e immagini su Basic se serve solo l\'OCR, su Standard se serve l\'impaginazione (tabelle comprese). Qui: <b>%s</b>.' % ['Minimal', 'Basic', 'Standard'][c],
                'P15', k='mcq', o=['Minimal', 'Basic', 'Standard'], c=c)
    r = random.Random(14)
    for i in range(20):
        tot = r.randint(20, 200) * 1000; dig = r.choice([0.2, 0.25, 0.33, 0.4, 0.5])
        a = tot * (1 - dig)
        add('costi', 2, 'Pagine digitali che escono dallo Standard', 'Su %s pagine al mese, il %d%% arriva in realtà come allegati Word, Excel o email (formati digitali). Quante pagine restano sul contatore Standard?' % (it(tot), round(dig * 100)),
            'Le pagine digitali vanno su Minimal: %s × (1 − %s) = <b>%s pagine</b> restano su Standard.' % (it(tot), it(dig, 2), it(a)), 'P15', a=a, u='pagine', tol=tot * 0.003)

# ---------------------------------------------------------------- PIPELINE
FIELDS = [
 ('l\'importo totale scritto in fondo alla fattura', 0), ('la data di scadenza indicata nel contratto', 0), ('il numero d\'ordine', 0), ('l\'IBAN del fornitore', 0), ('la partita IVA', 0),
 ('il nome del firmatario', 0), ('la valuta, scelta tra EUR, USD, GBP o "altro"', 1), ('il tipo di documento: fattura, nota di credito, sollecito, altro', 1), ('se il contratto ha il rinnovo automatico (sì/no)', 1),
 ('il motivo di una chiamata tra 6 categorie più "altro"', 1), ('l\'esito di una chiamata: risolto, da richiamare, escalation', 1), ('il sentimento del cliente: positivo, neutro, negativo', 1),
 ('la lingua del documento tra 5 lingue previste più "altro"', 1), ('un riassunto di tre righe della riunione', 2), ('un titolo descrittivo per un documento senza titolo', 2), ('le decisioni prese in riunione, riformulate', 2),
 ('una descrizione testuale di una foto di prodotto', 2), ('l\'indirizzo di consegna', 0), ('il codice cliente', 0), ('il numero di telefono del referente', 0),
 ('la priorità di un reclamo: alta, media, bassa', 1), ('il reparto destinatario tra 8 reparti', 1), ('una risposta di cortesia da proporre al cliente', 2), ('l\'elenco degli argomenti discussi, con parole tue', 2)]
def t_metodo():
    labels = ['extract', 'classify', 'generate']
    for d, c in FIELDS:
        for ver in range(2):
            q = ['Quale metodo del campo usi per estrarre %s?', 'Nello schema, il campo per %s va dichiarato con quale metodo?'][ver] % d
            sol = ['<b>extract</b>: il valore è scritto nel documento; è il metodo più preciso ed economico (solo per documenti).', '<b>classify</b>: le risposte sono un elenco chiuso, e conviene prevedere una categoria "altro".', '<b>generate</b>: serve creare testo nuovo; è il più flessibile e il più costoso in token di uscita.'][c]
            add('pipeline', 1, 'Extract, classify o generate', q, sol, 'P2', k='mcq', o=labels, c=c)

def t_smistare():
    r = random.Random(15)
    for i in range(45):
        cats = r.randint(3, 5)
        share = [r.randint(5, 60) for _ in range(cats)]; tot = sum(share); share = [s / tot for s in share]
        fields = [r.randint(3, 15) for _ in range(cats - 1)] + [0]
        univ = sum(fields[:-1]) + r.randint(0, 6)
        routed = sum(s * f for s, f in zip(share, fields))
        red = (1 - routed / univ) * 100
        names = ['fatture', 'contratti', 'conferme', 'bolle', 'solleciti'][:cats - 1] + ['altro']
        desc = ', '.join('%s %d%% (%d campi)' % (n, round(s * 100), f) for n, s, f in zip(names, share, fields))
        add('pipeline', 2 if i % 3 else 3, 'Quanto fa risparmiare lo smistamento', 'Lo schema universale ha %d campi e li applica a ogni documento. Con classificatore e instradamento, la composizione del lotto e i campi per categoria sono: %s. Di che percentuale si riducono i "campi per documento" medi? (Una cifra decimale; usa le percentuali arrotondate come mostrate.)' % (univ, desc),
            'Media con instradamento = ' + ' + '.join('%d%%×%d' % (round(s * 100), f) for s, f in zip(share, fields)) + ' = %s campi. Riduzione = 1 − %s/%d = <b>%s%%</b>. "Altro" non paga campi: va solo in archivio.' % (it(sum(round(s * 100) / 100 * f for s, f in zip(share, fields)), 2), it(sum(round(s * 100) / 100 * f for s, f in zip(share, fields)), 2), univ, it((1 - sum(round(s * 100) / 100 * f for s, f in zip(share, fields)) / univ) * 100, 1)),
            'P3', a=round((1 - sum(round(s * 100) / 100 * f for s, f in zip(share, fields)) / univ) * 100, 1), u='%', tol=0.3)

SCEN = [
 ('Solo OCR di scansioni per un archivio ricercabile', 0, 'Content Understanding con prebuilt-read o prebuilt-layout: costa meno e dà più dettagli di impaginazione.'),
 ('Fatture standard dei dieci fornitori principali, volumi alti, risultato sempre uguale', 1, 'Document Intelligence con il modello predefinito: deterministico, nessun token di modello, più prevedibile.'),
 ('Contratti e accordi di forma libera da cui dedurre condizioni', 0, 'Content Understanding con prebuilt-contract: servono ragionamento e campi dedotti.'),
 ('Lettere di referral non strutturate, senza esempi etichettati', 0, 'Content Understanding con un analizzatore personalizzato: parte senza etichette.'),
 ('Moduli di risarcimento molto strutturati, con 5 esempi etichettati disponibili', 1, 'Document Intelligence con un modello personalizzato, addestrabile con appena cinque esempi.'),
 ('Elaborazione in un ambiente isolato dalla rete, senza cloud', 1, 'Solo Document Intelligence nei contenitori: oggi è l\'unica opzione locale.'),
 ('Registrazioni di un call center da riassumere', 0, 'Content Understanding: tratta audio e video nello stesso servizio.'),
 ('Fatture di 400 fornitori con 400 impaginazioni diverse', 0, 'Content Understanding con analizzatore personalizzato: Microsoft lo raccomanda dove la varietà è alta.'),
 ('Documenti d\'identità standard da leggere con confidenza e posizione', 1, 'Document Intelligence con i modelli predefiniti, per l\'accuratezza sui modelli comuni.'),
 ('Descrivere i grafici di una relazione per un sistema RAG', 0, 'Content Understanding (prebuilt-documentSearch, analisi delle figure).'),
 ('Scontrini standard, volumi altissimi, costo prevedibile', 1, 'Document Intelligence: modelli predefiniti deterministici.'),
 ('Polizze assicurative di forma variabile da cui estrarre campi dedotti', 0, 'Content Understanding con analizzatore personalizzato senza etichette.'),
 ('Video di formazione da indicizzare per argomento', 0, 'Content Understanding: video e campi generativi.'),
 ('Moduli fiscali standard, risultato ripetibile', 1, 'Document Intelligence con i predefiniti per i moduli fiscali.'),
]
def t_cu_di():
    for d, c, sol in SCEN:
        for ver in range(3):
            q = ['Scenario: %s. Quale servizio indica la guida ufficiale "Choose the right Foundry Tool"?', 'Per questo caso, %s, quale servizio scegli?', 'Un cliente chiede: "%s". Cosa consigli?'][ver] % (d[0].lower() + d[1:] if ver else d)
            add('pipeline', 1 if ver == 0 else 2, 'Content Understanding o Document Intelligence', q, sol, 'P5', k='mcq', o=['Content Understanding', 'Document Intelligence'], c=c)

PREB = [
 ('smistare e leggere fatture, ordini, note di credito e scontrini in una sola chiamata', 'prebuilt-procurement'),
 ('trasformare PDF in markdown con descrizioni delle figure e blocchi pronti per un indice RAG', 'prebuilt-documentSearch'),
 ('solo OCR, senza modello linguistico, contatore Basic', 'prebuilt-read'),
 ('tabelle, sezioni e firme senza modello linguistico', 'prebuilt-layout'),
 ('leggere la struttura interna di file digitali senza OCR', 'prebuilt-digitalParse'),
 ('farsi proporre uno schema di campi da un documento di esempio', 'prebuilt-documentFieldSchema'),
 ('distinguere tra passaporti e patenti e leggerli', 'prebuilt-idDocument'),
 ('analizzare registrazioni di un call center', 'prebuilt-callCenter'),
 ('estrarre campi da contratti', 'prebuilt-contract'),
 ('estrarre coppie chiave-valore quando nessuno schema noto corrisponde', 'prebuilt-documentFields'),
]
def t_prebuilt():
    names = [p[1] for p in PREB]
    for i, (d, n) in enumerate(PREB):
        for ver in range(3):
            wrong = [x for x in names if x != n]
            r = random.Random(i * 10 + ver); r.shuffle(wrong)
            o = [n] + wrong[:3]
            q = ['Quale analizzatore predefinito serve per %s?', 'Devi %s. Da quale predefinito parti?', 'Nel catalogo dei predefiniti, chi si occupa di %s?'][ver] % d
            add('pipeline', 2, 'Scegliere il predefinito', q, '<b>%s</b>. In produzione conviene copiarne la definizione (GET, poi PUT con il tuo nome), perché i predefiniti possono cambiare tra versioni dell\'API.' % n, 'P15', k='mcq', o=o, c=0)

def t_agentica():
    r = random.Random(16)
    for i in range(25):
        p = r.randint(2, 200) * 500
        a = p / 1000 * 2
        add('pipeline', 2, 'Il triplo della contestualizzazione', 'Passi %s pagine da un analizzatore standard alla modalità agentica. Di quanto aumenta la sola contestualizzazione? (Standard 1 $, avanzata 3 $ ogni 1.000 pagine.)' % it(p),
            'Le famiglie diverse da "standard", agentic compresa, usano la tariffa avanzata: %s/1.000 × (3 − 1) $ = <b>%s</b> in più, prima dei token aggiuntivi del ragionamento.' % (it(p), money(a)), 'P6', a=a, u='$', tol=0.01)
    cases = [('estrarre dieci campi semplici da fatture standard', 1), ('verificare se un contratto e i suoi allegati soddisfano dieci condizioni', 0), ('riconciliare i valori di un bilancio', 0),
             ('controllare che la somma delle righe coincida con il totale dichiarato, collegando tabelle su più pagine', 0), ('copiare il numero di fattura', 1), ('trascrivere una registrazione audio', 2),
             ('capire come un contratto e le sue modifiche nello stesso file si rapportano', 0), ('leggere la data di emissione', 1)]
    for d, c in cases:
        for ver in range(2):
            add('pipeline', 2 if ver == 0 else 3, 'Quando la modalità agentica', ['Per %s, quale scelta è coerente con la documentazione?', 'Un team vuole usare la modalità agentica per %s. Cosa rispondi?'][ver] % d,
                ['<b>Modalità agentica</b>: ragionamento a più passi, calcoli o convalide su prove sparse; non sostituisce la revisione umana nei casi ad alto impatto.', '<b>Analizzatore standard</b>: per l\'estrazione semplice la documentazione dice di non usare l\'agentica.', '<b>Non disponibile</b>: nell\'anteprima l\'agentica è solo per documenti, un file per richiesta.'][c],
                'P6', k='mcq', o=['Modalità agentica', 'Analizzatore standard', 'Non si può: l\'agentica non supporta questo input'], c=c)

def t_id_analizzatore():
    ok = ['fatture_2026', 'contratti.v2', 'acq.fornitori_IT', 'a', 'Invoice.Custom.01']
    bad = [('fatture-2026', 'il trattino non è ammesso'), ('contratti v2', 'lo spazio non è ammesso'), ('analizzatore#1', 'il carattere # non è ammesso'), ('fatture/acquisti', 'la barra non è ammessa'), ('x' * 65, 'supera 64 caratteri'), ('àcquisti', 'le lettere accentate non sono nel pattern')]
    for s in ok:
        add('produzione', 1, 'ID di un analizzatore valido?', 'L\'ID di un analizzatore deve rispettare il pattern <code>[a-zA-Z0-9._]{1,64}</code>. <code>%s</code> è valido?' % s, '<b>Sì</b>: solo lettere, cifre, punto e trattino basso, lunghezza tra 1 e 64.', 'Limiti del servizio', k='mcq', o=['Sì', 'No'], c=0)
    for s, why in bad:
        add('produzione', 1, 'ID di un analizzatore valido?', 'L\'ID di un analizzatore deve rispettare il pattern <code>[a-zA-Z0-9._]{1,64}</code>. <code>%s</code> è valido?' % (s if len(s) < 30 else s[:12] + '…(65 caratteri)'), '<b>No</b>: %s.' % why, 'Limiti del servizio', k='mcq', o=['Sì', 'No'], c=1)

# ---------------------------------------------------------------- QUALITÀ
def t_wer_eer():
    r = random.Random(17)
    for i in range(45):
        if i % 3 == 0:
            w = r.randint(50, 5000); e = r.randint(1, w // 10)
            add('qualita', 1, 'Tasso di errore sulle parole', 'L\'OCR legge %s parole e ne sbaglia %s. Qual è il WER, in percentuale (due decimali)?' % (it(w), it(e)), 'WER = %s ÷ %s = <b>%s%%</b>.' % (it(e), it(w), it(e / w * 100, 2)), 'P12', a=round(e / w * 100, 2), u='%', tol=0.02)
        elif i % 3 == 1:
            n = r.randint(10, 500); e = r.randint(1, n // 5)
            add('qualita', 1, 'Tasso di errore sulle entità', 'Su %d importi estratti, %d sono sbagliati. Qual è l\'EER sugli importi, in percentuale (una cifra decimale)?' % (n, e), 'EER = %d ÷ %d = <b>%s%%</b>.' % (e, n, it(e / n * 100, 1)), 'P12', a=round(e / n * 100, 1), u='%', tol=0.1)
        else:
            ents = r.randint(5, 40); wpe = r.randint(2, 4); bad = r.randint(1, max(1, ents // 4))
            words = ents * wpe; wer = bad / words * 100; eer = bad / ents * 100
            add('qualita', 2, 'Lo stesso errore, due metriche', '%d nomi sono composti in tutto da %d parole. L\'OCR sbaglia %d parole, ciascuna in un nome diverso. Di quante volte l\'EER sui nomi supera il WER? (Una cifra decimale.)' % (ents, words, bad),
                'WER = %d/%d = %s%%; EER = %d/%d = %s%%. Rapporto = <b>%s</b>. Un OCR "quasi perfetto" può dare un\'estrazione di entità molto peggiore: per chi paga conta l\'EER.' % (bad, words, it(wer, 2), bad, ents, it(eer, 1), it(eer / wer, 1)), 'P12', a=round(eer / wer, 1), u='volte', tol=0.05)

def t_soglia():
    r = random.Random(18)
    for i in range(55):
        ths = [0.70, 0.75, 0.80, 0.85, 0.90, 0.95]
        auto = sorted([r.randint(50, 98) for _ in ths], reverse=True)
        err = sorted([round(r.uniform(0.1, 4.0), 1) for _ in ths], reverse=True)
        lim = r.choice([0.5, 1.0, 1.5, 2.0])
        okk = [j for j in range(len(ths)) if err[j] <= lim]
        if not okk: continue
        best = min(okk)
        rows = ''.join('<tr><td>%s</td><td>%d%%</td><td>%s%%</td></tr>' % (it(ths[j], 2), auto[j], it(err[j], 1)) for j in range(len(ths)))
        add('qualita', 2 if i % 2 else 3, 'Scegliere la soglia sulla curva', 'Sul campione, per il campo "totale" hai misurato:<div class="tw"><table><thead><tr><th scope="col">Soglia</th><th scope="col">Automatizzati</th><th scope="col">Errori che passano</th></tr></thead><tbody>%s</tbody></table></div>L\'ufficio accetta al massimo %s%% di errori che passano. Quale soglia massimizza l\'automazione?' % (rows, it(lim, 1)),
            'Le soglie ammesse sono quelle con errori ≤ %s%%: %s. Tra queste, la più bassa automatizza di più: <b>%s</b> (%d%% automatizzati). La soglia "giusta" è sperimentale, non quella di partenza della guida.' % (it(lim, 1), ', '.join(it(ths[j], 2) for j in okk), it(ths[best], 2), auto[best]),
            'P12', k='mcq', o=[it(t, 2) for t in ths], c=best)

def t_revisione():
    r = random.Random(19)
    for i in range(35):
        inv = r.choice([5000, 12000, 30000, 45000]); au = r.choice([60, 70, 75, 81, 90]); rate = r.choice([40, 60, 80])
        hrs = inv * au / 100 / rate
        if i % 2 == 0:
            add('casi', 2, 'Ore liberate dall\'automazione', 'Un impiegato contabilizza %d fatture l\'ora. Con %s fatture al mese e il %d%% contabilizzato in automatico, quante ore al mese si liberano?' % (rate, it(inv), au),
                '%s × %d%% = %s fatture automatiche; ÷ %d = <b>%s ore</b>.' % (it(inv), au, it(inv * au / 100), rate, it(hrs, 1)), 'P14', a=round(hrs, 1), u='ore', tol=0.2)
        else:
            dis = r.choice([1, 2, 3, 4, 5])
            add('qualita', 2, 'Il tetto della verità', 'Due persone trascrivono la verità del campione in modo indipendente e non concordano sul %d%% dei campi. Qual è, in pratica, l\'accuratezza massima che puoi misurare in modo affidabile per il servizio?' % dis,
                'Nessun sistema può essere misurato meglio dell\'accordo tra le persone che costruiscono la verità: il tetto pratico è <b>%d%%</b>.' % (100 - dis), 'P12', a=100 - dis, u='%')

HAND = ['inglese', 'cinese semplificato', 'francese', 'tedesco', 'italiano', 'thai', 'giapponese', 'coreano', 'portoghese', 'spagnolo', 'russo', 'arabo']
NOHAND = ['polacco', 'olandese', 'svedese', 'greco', 'turco', 'ceco', 'ungherese', 'rumeno', 'finlandese', 'danese', 'ebraico', 'hindi']
def t_lingue():
    for lang in HAND + NOHAND:
        ok = lang in HAND
        add('qualita', 1, 'Scrittura a mano: lingua supportata?', 'Il riconoscimento del testo scritto a mano include il <b>%s</b> nell\'elenco ufficiale?' % lang,
            '%s La lista della scrittura a mano ha dodici lingue: inglese, cinese semplificato, francese, tedesco, italiano, thai, giapponese, coreano, portoghese, spagnolo, russo, arabo. Fuori lista non significa "non funziona": significa "misuralo prima di prometterlo".' % ('<b>Sì.</b>' if ok else '<b>No.</b>'), 'P17', k='mcq', o=['Sì', 'No'], c=0 if ok else 1)

REG = [('West Europe', 0), ('Sweden Central', 0), ('UK South', 1), ('East US', 2), ('East US 2', 2), ('Japan East', 2), ('Australia East', 2), ('Canada Central', 2), ('South Central US', 2), ('Southeast Asia', 2), ('West US', 2), ('West US 3', 2)]
def t_regioni():
    for reg, c in REG:
        add('produzione', 1, 'Regioni e Unione Europea', 'La regione <b>%s</b>, tra quelle elencate per Content Understanding, si trova nell\'Unione Europea?' % reg,
            ['<b>Sì</b>: nell\'elenco attuale le regioni dell\'Unione sono due, West Europe (Paesi Bassi) e Sweden Central.', '<b>No</b>: UK South è vicina, ma fuori dall\'Unione.', '<b>No</b>: le uniche regioni dell\'Unione nell\'elenco sono West Europe e Sweden Central.'][c], 'P17', k='mcq', o=['Sì', 'No, ma è in Europa', 'No, è fuori dall\'Europa'], c=c)

def t_campione():
    r = random.Random(20)
    for i in range(20):
        tot = r.choice([300, 400, 500, 600]); k = r.choice([3, 4, 5, 6])
        if tot % k: continue
        add('qualita', 2, 'Campione stratificato', 'Vuoi un campione di %d documenti stratificato in parti uguali su %d lingue. Quanti documenti per lingua?' % (tot, k), '%d ÷ %d = <b>%d</b> per lingua, includendo le scansioni peggiori: un calo di qualità in una lingua non deve sparire nella media.' % (tot, k, tot // k), 'P12, P17', a=tot // k, u='documenti')

# ---------------------------------------------------------------- SICUREZZA
ROLES = [
 ('la pipeline di produzione che deve solo lanciare analisi', 0), ('un servizio che elenca gli analizzatori e classifica documenti', 0),
 ('il team che crea e prova nuovi analizzatori ma non deve cancellarne', 1), ('chi aggiorna i progetti di etichettatura', 1),
 ('chi deve poter cancellare analizzatori e classificatori', 2), ('l\'amministratore con accesso completo al servizio', 2)]
def t_ruoli():
    for d, c in ROLES:
        for ver in range(3):
            q = ['Qual è il ruolo integrato minimo per %s?', 'Applicando il privilegio minimo, che ruolo assegni a %s?', 'Ruoli di Content Understanding: cosa serve per %s?'][ver] % d
            add('sicurezza', 1 if ver == 0 else 2, 'Ruoli e privilegio minimo', q, ['<b>Reader</b>: legge, elenca e lancia analisi e classificazioni, ma non crea, modifica o cancella.', '<b>Contributor</b>: crea, aggiorna e prova, ma non cancella analizzatori o classificatori, non gestisce ruoli e non legge le chiavi.', '<b>Owner</b>: accesso completo, cancellazione compresa.'][c],
                'P18', k='mcq', o=['Content Understanding Reader', 'Content Understanding Contributor', 'Content Understanding Owner'], c=c)
    for ver in range(3):
        add('sicurezza', 2, 'Copiare un analizzatore fra tenant', ['Per copiare un analizzatore su una risorsa di un altro tenant, che ruolo deve avere l\'identità che esegue l\'operazione?', 'Promuovi un analizzatore da sviluppo a produzione con la copia fra risorse. Quale ruolo serve all\'identità di rilascio?', 'Quale combinazione di permessi richiede la copia di un analizzatore tra due risorse?'][ver],
            'L\'identità deve avere <b>Cognitive Services User su entrambe le risorse</b>. La copia ha due passi: autorizzazione sull\'origine (token con scadenza), poi copia sulla destinazione.', 'P18', k='mcq',
            o=['Cognitive Services User su entrambe le risorse', 'Owner solo sulla destinazione', 'Reader sull\'origine', 'Nessun ruolo: basta la chiave della destinazione'], c=0)

def t_residenza():
    cases = [('risorsa in West Europe, distribuzione del modello di tipo "globale", campi generativi', 1), ('risorsa in Sweden Central, distribuzione "zona dati Europa"', 0),
             ('prebuilt-read con processingLocation = zona dati Europa', 0), ('prebuilt-layout con processingLocation = globale', 1),
             ('capacità portata da una risorsa collegata in East US (BYOC), campi generativi', 1), ('risorsa in West Europe, solo prebuilt-read con processingLocation zona dati Europa e risultati cancellati subito', 0)]
    for d, c in cases:
        for ver in range(3):
            q = ['Configurazione: %s. L\'elaborazione può avvenire fuori dall\'Unione?', 'Un ufficio italiano usa: %s. I documenti possono essere elaborati fuori dall\'UE?', 'Con %s, la residenza dell\'elaborazione resta garantita in Europa?'][ver] % d
            yes_out = c == 1
            opts = ['Sì, può uscire', 'No, resta in Europa'] if ver < 2 else ['No, non è garantita', 'Sì, resta in Europa']
            add('sicurezza', 2 if ver else 1, 'Dove avviene l\'elaborazione', q,
                'I dati a riposo seguono la regione della risorsa; l\'elaborazione generativa segue la <b>distribuzione del modello</b> (geografia, zona dati, globale); per read e layout decide <code>processingLocation</code>. Qui: <b>%s</b>.' % ('l\'elaborazione può avvenire fuori dall\'UE' if yes_out else 'resta nel perimetro europeo'), 'P9, P16, P17', k='mcq', o=opts, c=0 if yes_out else 1)

def t_ritenzione():
    r = random.Random(21)
    for i in range(24):
        h = r.randint(0, 23); m = r.choice([0, 15, 30, 45])
        if i % 2 == 0:
            add('sicurezza', 1, 'Finestra dei risultati', 'Un\'analisi asincrona termina alle %02d:%02d. Senza cancellazione esplicita, fino a quando (al massimo) il risultato resta disponibile per il recupero? Rispondi con le ore trascorse.' % (h, m),
                'I risultati restano <b>fino a 24 ore</b>, poi vengono cancellati in automatico. Per i dati personali conviene recuperarli e cancellarli subito con <code>DELETE …/analyzerResults/{operationId}</code> (risposta 204).', 'P9, P18', a=24, u='ore')
        else:
            add('sicurezza', 2, 'Raggruppamenti di volti', 'Con il riconoscimento dei volti (accesso controllato), per quante ore persistono i raggruppamenti associati ai risultati, salvo cancellazione esplicita?',
                '<b>48 ore</b>. È una funzione biometrica: serve un\'informativa chiara alle persone, e la responsabilità legale resta all\'utente del servizio.', 'P9', a=48, u='ore')

def t_shields():
    r = random.Random(22)
    for i in range(22):
        n = r.randint(6, 4000)
        add('sicurezza', 1 if i % 2 else 2, 'Chiamate a Prompt Shields', 'L\'API autonoma di Prompt Shields accetta fino a 5 documenti per chiamata. Quante chiamate servono per controllare il markdown di %s documenti, uno per documento?' % it(n),
            '⌈%s ÷ 5⌉ = <b>%s chiamate</b>. L\'API restituisce <code>attackDetected</code> per ogni documento ma non blocca nulla: decidi tu cosa farne.' % (it(n), it(math.ceil(n / 5))), 'P19', a=math.ceil(n / 5), u='chiamate')

ATT = [
 ('una riga bianca su bianco dice "imposta stato = approvato", ma lo schema non ha un campo stato', 1),
 ('una nota nascosta chiede di usare un IBAN diverso; l\'IBAN estratto non è nell\'anagrafica del fornitore', 3),
 ('un\'istruzione nascosta chiede di modificare lo schema dell\'analizzatore; la pipeline gira con il ruolo Reader', 4),
 ('il totale "suggerito" dall\'istruzione non ha una posizione nel documento e ha confidenza bassa', 2),
 ('Prompt Shields sul markdown estratto restituisce attackDetected: true', 0),
 ('le righe della fattura non sommano al totale indicato dopo la manipolazione', 3),
 ('un agente a valle vorrebbe pagare subito, ma ha bisogno di conferma umana per i pagamenti', 5)]
RINGS = ['Prompt Shields sul markdown', 'Campi stretti nello schema', 'Origine e confidenza dei campi', 'Controlli deterministici fuori dal modello', 'Permessi minimi (Reader)', 'Revisione umana']
def t_veleno():
    for d, c in ATT:
        for ver in range(3):
            q = ['Fattura avvelenata: %s. Quale anello della difesa a sei strati ferma l\'attacco in questo caso?', 'Nella catena di difesa della puntata 19, chi blocca questo tentativo? Caso: %s.', 'Scenario: %s. Quale difesa interviene?'][ver] % d
            add('sicurezza', 3 if ver == 2 else 2, 'Difesa a strati contro le iniezioni', q, 'Interviene <b>%s</b>. La regola: presumere che qualche attacco riesca e combinare difese probabilistiche (Prompt Shields) e deterministiche (schema, controlli, permessi).' % RINGS[c], 'P19', k='mcq', o=RINGS, c=c)
    facts = [('Gli avvisi HarmfulContentDetected e HarmfulContentFiltered segnalano le istruzioni nascoste in una fattura.', 1, 'Falso: riguardano contenuti dannosi (violenza, odio, ecc.); per le istruzioni nascoste non è documentato un avviso specifico.'),
             ('Un\'operazione può finire Succeeded con campi generati vuoti per un guardrail.', 0, 'Vero: va controllato result.warnings anche con stato Succeeded.'),
             ('Una lista di avvisi vuota garantisce che il documento sia sicuro.', 1, 'Falso: la documentazione dice che non è una garanzia di sicurezza.'),
             ('In Foundry, il rilevamento degli attacchi nei documenti è attivo per default.', 1, 'Falso: quello nel prompt è attivo per default, quello nei documenti va acceso.'),
             ('Prompt Shields legge direttamente il PDF.', 1, 'Falso: legge testo; il PDF lo legge Content Understanding, che produce il markdown.'),
             ('Per il rilevamento, il contenuto dei documenti va racchiuso nei delimitatori &lt;documents&gt;.', 0, 'Vero, con il testo in JSON con escape.'),
             ('Lo Spotlighting codifica i documenti in base64 e costa token in più.', 0, 'Vero: è in anteprima e funziona solo con Chat Completions.'),
             ('I modelli di Prompt Shields sono valutati soprattutto in inglese: in italiano vanno provati.', 0, 'Vero: la documentazione raccomanda di valutarli in ogni lingua dell\'applicazione.')]
    for f, c, sol in facts:
        for ver in range(2):
            add('sicurezza', 2, 'Vero o falso sui guardrail', ['Vero o falso? %s', 'Affermazione da verificare: "%s"'][ver] % f, sol, 'P19', k='mcq', o=['Vero', 'Falso'], c=c)

def t_rete():
    cases = [('il servizio non deve essere raggiungibile da internet', 1), ('basta che risponda solo agli IP dell\'ufficio, anche se resta esposto', 0),
             ('il traffico deve passare sulla rete interna di Microsoft', 1), ('vuoi un filtro sulla porta d\'ingresso pubblica', 0)]
    for d, c in cases:
        for ver in range(2):
            add('sicurezza', 1 if ver == 0 else 2, 'Regole IP o endpoint privato', ['Requisito: %s. Cosa usi?', 'Un responsabile della sicurezza chiede che %s. Quale soluzione?'][ver] % d,
                ['Le <b>regole di rete</b>: filtrano chi entra, ma il servizio resta su internet.', 'Un <b>endpoint privato con Private Link</b>, con l\'accesso pubblico disattivato.'][c], 'P18', k='mcq', o=['Regole IP / reti virtuali', 'Endpoint privato (Private Link)'], c=c)

# ---------------------------------------------------------------- PRODUZIONE
T429 = [
 ('il messaggio dice che le richieste sono state limitate e l\'uso è vicino ai TPM assegnati', 0),
 ('il messaggio parla di alta domanda e il problema sparisce dopo l\'attesa indicata', 1),
 ('x-ratelimit-limit-tokens mostra un valore più basso del TPM configurato', 2),
 ('il limite scatta ma le metriche di token consumati sono basse e max_tokens è 4.000', 3)]
T429L = ['Limite superato', 'Capacità del sistema', 'Riduzione temporanea del pool condiviso', 'Budget consumato dai parametri (max_tokens)']
def t_429():
    for d, c in T429:
        for ver in range(4):
            q = ['Ricevi 429 e %s. Di che tipo di 429 si tratta?', 'Diagnosi: %s. Quale dei quattro tipi?', 'In produzione arrivano 429; %s. Causa più probabile?', 'Osservi questo: %s. Come classifichi il 429?'][ver] % d
            rem = ['aumentare o ribilanciare i TPM della distribuzione, o chiedere un aumento', 'riprovare dopo l\'attesa; se persiste valutare la capacità riservata', 'di solito si risolve in qualche ora: rallenta e monitora', 'ridurre max_tokens al minimo necessario, best_of = 1, prompt più corti'][c]
            add('produzione', 2 if ver < 2 else 3, 'I quattro tipi di 429', q, '<b>%s</b>. Rimedio: %s.' % (T429L[c], rem), 'P8, P10', k='mcq', o=T429L, c=c)

LOGS = [('una riga per ogni richiesta con codice di stato e latenza', 0), ('il dettaglio per il debug di una chiamata', 1), ('chi ha cambiato la configurazione della distribuzione', 2), ('distinguere i quattro tipi di 429 richiesta per richiesta', 0), ('gli eventi di controllo degli accessi', 2)]
def t_log():
    for d, c in LOGS:
        for ver in range(3):
            add('produzione', 1, 'Categorie di log', ['Quale categoria di log delle distribuzioni ti dà %s?', 'Devi recuperare %s. Quale log accendi?', 'Per avere %s, quale categoria di diagnostica serve?'][ver] % d,
                '<b>%s</b>. I log non si salvano da soli: serve un\'impostazione di diagnostica verso Log Analytics, storage o Event Hub, da creare il giorno in cui nasce la risorsa.' % ['RequestResponse', 'Trace', 'Audit'][c], 'P10', k='mcq', o=['RequestResponse', 'Trace', 'Audit'], c=c)

def t_allarmi():
    r = random.Random(23)
    for i in range(25):
        q = r.choice([1000, 1500, 2000, 3000, 5000]); pct = r.choice([80, 85, 90])
        add('produzione', 1, 'Soglia dell\'allarme sulle pagine', 'La quota approvata è di %s pagine al minuto. Imposti un allarme al %d%% della quota. A quante pagine al minuto scatta?' % (it(q), pct),
            '%s × %d%% = <b>%s pagine/min</b>: rallenti prima del muro, invece di aspettare i 429.' % (it(q), pct, it(q * pct / 100)), 'P10', a=q * pct / 100, u='pagine/min')
    for i in range(15):
        base = r.choice([1.2, 1.8, 2.5, 3, 4]); mul = 2
        add('produzione', 2, 'Allarme sul tempo alla risposta', 'Nel test hai misurato un tempo alla risposta medio di %s secondi. Con la regola "allarme oltre il doppio del valore di test", a quanti secondi imposti la soglia?' % it(base, 1),
            '%s × 2 = <b>%s s</b>. Spesso è il primo sintomo della riduzione temporanea del pool condiviso, prima dei 429.' % (it(base, 1), it(base * mul, 1)), 'P10', a=base * mul, u='s', tol=0.05)

def t_latenza():
    r = random.Random(24)
    for i in range(20):
        u = r.randint(4, 15); az = r.randint(1, u - 1)
        add('produzione', 2, 'Dove va il tempo', 'L\'utente aspetta %d secondi; il "tempo all\'ultimo byte" misurato da Azure è %d secondi. Quanti secondi sono fuori dalla misura di Azure (rete, code e codice tuo)?' % (u, az),
            '%d − %d = <b>%d s</b>. La metrica è misurata al gateway: serve un logging lato client con la stessa chiave di correlazione.' % (u, az, u - az), 'P10', a=u - az, u='s')

# ---------------------------------------------------------------- CASI E ARCHITETTURE
def t_caso_capacita():
    r = random.Random(25)
    for i in range(70):
        docs = r.choice([10000, 20000, 30000, 50000, 80000]); ppd = r.choice([1.5, 2, 2.2, 3]); altro = r.choice([0.1, 0.16, 0.2, 0.3])
        tpm = r.choice([150000, 300000, 600000]); pr = r.choice([2600, 3000]); mt = r.choice([300, 400])
        pages = docs * ppd; gen = pages * (1 - altro); rpm = tpm / (pr + mt)
        t_model = gen / rpm / 60; t_pages = pages / 1000 / 60
        if i % 2 == 0:
            add('casi', 3, 'Collo di bottiglia del lotto', ('%s documenti al mese, in media %s pagine ciascuno. Il %d%% è "altro" e va solo in archivio, senza modello. Distribuzione da %s TPM, prompt %s token, max_tokens %s, una chiamata per pagina. '
                 'Quante ore servono, al minimo, per la parte generativa? (Una cifra decimale.)') % (it(docs), it(ppd, 1), round(altro * 100), it(tpm), it(pr), it(mt)),
                ('Pagine = %s × %s = %s. Al modello: %s × %s = %s. Rich./min = %s ÷ %s = %s. Ore = %s ÷ %s ÷ 60 = <b>%s</b>. Alla quota di pagine basterebbero %s ore: il limite è il modello.')
                 % (it(docs), it(ppd, 1), it(pages), it(pages), it(1 - altro, 2), it(gen), it(tpm), it(pr + mt), it(rpm, 1), it(gen), it(rpm, 1), it(t_model, 1), it(t_pages, 1)), 'P14', a=round(t_model, 1), u='ore', tol=max(0.15, t_model * 0.01))
        else:
            need = gen / (10 * 60)  # richieste/min per finire in 10 ore
            tpm_need = need * (pr + mt)
            add('casi', 3, 'Quanta quota per una notte', ('Lo stesso tipo di lotto: %s pagine da mandare al modello, prompt %s token, max_tokens %s. Quanti TPM servono, al minimo, per finire in 10 ore? (Arrotonda alle migliaia per eccesso.)') % (it(gen), it(pr), it(mt)),
                'Rich./min necessarie = %s ÷ 600 = %s. TPM = %s × %s = %s → <b>%s</b>.' % (it(gen), it(need, 1), it(need, 1), it(pr + mt), it(tpm_need), it(math.ceil(tpm_need / 1000) * 1000)),
                'P8, P14', a=math.ceil(tpm_need / 1000) * 1000, u='TPM', tol=1000.5)

def t_multicloud():
    r = random.Random(26)
    for i in range(55):
        p = r.choice([10000, 50000, 100000, 110000, 250000]); fields = r.choice([12, 25, 30, 34, 40, 55])
        kind = i % 3
        if kind == 0:
            extra = max(0, fields - 30); per = 0.04 + 0.005 * extra
            add('casi', 2, 'Bedrock Data Automation, schema personalizzato', 'AWS Bedrock Data Automation con schema personalizzato costa 0,04 $ a pagina fino a 30 campi, più 0,005 $ per ogni campo oltre il trentesimo. Quanto costano %s pagine con uno schema da %d campi?' % (it(p), fields),
                'Prezzo a pagina = 0,04 + 0,005 × %d = %s $. × %s pagine = <b>%s</b>. Prezzo piatto: prevedibile, non necessariamente più economico.' % (extra, it(per, 3), it(p), money(p * per)), 'P13', a=round(p * per, 2), u='$', tol=max(1, p * per * 0.005))
        elif kind == 1:
            hrs = p / 120 / 60
            add('casi', 2, 'La quota di Google Document AI', 'Sugli estrattori personalizzati generativi online, Google indica 120 pagine al minuto. Quante ore servono per %s pagine? (Una cifra decimale.) E su Azure, alla quota di 1.000 pagine/min?' % it(p),
                'Google: %s ÷ 120 ÷ 60 = <b>%s ore</b>. Azure: %s minuti. Prima di confrontare i centesimi, confronta i minuti.' % (it(p), it(hrs, 1), it(p / 1000)), 'P13', a=round(hrs, 1), u='ore', tol=0.15)
        else:
            target = r.choice([300, 500, 800, 1000]); a = (target - 120) * 300
            add('casi', 3, 'Prenotare capacità su Google', 'Google vende la capacità extra a 300 $ al mese per ogni pagina al minuto oltre le 120 di base. Quanto costa al mese arrivare a %s pagine al minuto?' % it(target),
                '(%s − 120) × 300 $ = <b>%s</b> al mese. Ha senso per carichi costanti, non per lotti occasionali.' % (it(target), money(a, 0)), 'P13', a=a, u='$')

def t_roi():
    r = random.Random(27)
    for i in range(35):
        inv = r.choice([10000, 20000, 30000, 40000]); au = r.choice([0.7, 0.75, 0.81, 0.85]); rate = r.choice([50, 60]); cost_h = r.choice([25, 30, 35, 40]); svc = r.choice([600, 830, 1050, 1500])
        saved = inv * au / rate * cost_h; net = saved - svc
        add('casi', 3, 'Il bilancio del progetto', 'Fatture al mese: %s. Automazione misurata: %d%%. Un impiegato ne contabilizza %d l\'ora, al costo pieno di %d $ l\'ora. Il servizio costa %s $ al mese. Qual è il risparmio netto mensile, senza contare protocollo e controlli?' % (it(inv), round(au * 100), rate, cost_h, it(svc)),
            'Ore liberate = %s × %s ÷ %d = %s; valore = %s × %d $ = %s. Netto = %s − %s = <b>%s</b>. Il costo del servizio è la parte più visibile, non la più grande: la qualità ha i suoi costi.' % (it(inv), it(au, 2), rate, it(inv * au / rate, 1), it(inv * au / rate, 1), cost_h, money(saved), money(saved), money(svc, 0), money(net)),
            'P14', a=round(net, 2), u='$', tol=max(1, abs(net) * 0.005))

def t_caso_costi():
    r = random.Random(28)
    for i in range(40):
        pages = r.choice([50000, 92400, 110000, 200000]); ex = 5; ctx = r.choice([1, 3])
        tin = r.choice([300, 340, 500]) * 1e6 * pages / 110000; tout = 20e6 * pages / 110000
        pin, pout = 0.40, 1.60
        tot = pages / 1000 * ex + pages / 1000 * ctx + tin / 1e6 * pin + tout / 1e6 * pout
        add('casi', 3, 'Preventivo mensile completo', ('Preventivo per %s pagine al mese: estrazione Standard a 5 $ ogni 1.000 pagine (valore ipotetico), contestualizzazione %s (%d $ ogni 1.000), %s milioni di token in ingresso e %s milioni in uscita, a 0,40 $ e 1,60 $ per milione (modello di esempio). Totale mensile?')
             % (it(pages), 'standard' if ctx == 1 else 'avanzata', ctx, it(tin / 1e6, 1), it(tout / 1e6, 1)),
            'Estrazione %s; contestualizzazione %s; ingresso %s; uscita %s. Totale <b>%s</b>.' % (money(pages / 1000 * ex), money(pages / 1000 * ctx), money(tin / 1e6 * pin), money(tout / 1e6 * pout), money(tot)),
            'P14', a=round(tot, 2), u='$', tol=max(1, tot * 0.005))

# ---------------------------------------------------------------- CONCETTI (aperte, a scelta)
CONC = [
 ('pipeline', 2, 'Perché le operazioni sincrone esistono solo per prebuilt-read e prebuilt-layout?', ['Perché non usano un modello linguistico: tempo corto e prevedibile, elaborazione in memoria', 'Perché sono le uniche gratuite', 'Perché supportano solo immagini', 'Perché non hanno limiti di pagine'], 0, 'P16'),
 ('pipeline', 2, 'Default a livello di risorsa o modelDeployments per richiesta: quale regola?', ['I default descrivono la normalità, la sovrascrittura per richiesta le eccezioni', 'Sempre per richiesta, così è esplicito', 'Sempre default, la sovrascrittura non esiste', 'Indifferente: non cambia nulla'], 0, 'P16'),
 ('pipeline', 3, 'Con BYOC da un\'altra regione, dove avviene il passaggio generativo?', ['Nella regione della risorsa collegata', 'Sempre nella regione della risorsa Content Understanding', 'Nella regione del client', 'In una regione scelta a caso'], 0, 'P16'),
 ('pipeline', 2, 'Quale dei quattro analizzatori di base permette di derivare un analizzatore personalizzato?', ['prebuilt-document, -image, -audio, -video', 'prebuilt-invoice', 'prebuilt-read', 'prebuilt-documentSearch'], 0, 'P15'),
 ('pipeline', 2, 'A cosa serve enableSegment nel classificatore?', ['A dividere un file con più documenti in segmenti', 'A dividere una pagina in colonne', 'A ridurre la risoluzione', 'A spezzare l\'audio'], 0, 'P3'),
 ('pipeline', 3, 'A cosa serve allowInPageSegments?', ['A dividere una singola pagina che contiene più tipi di documento', 'A unire pagine diverse', 'A segmentare il video', 'A saltare le pagine vuote'], 0, 'P7'),
 ('pipeline', 2, 'Fino a quanti livelli si possono annidare i classificatori per i documenti?', ['Cinque', 'Due', 'Dieci', 'Uno'], 0, 'P7'),
 ('pipeline', 2, 'Fino a quanti livelli si possono annidare i classificatori per i video?', ['Due', 'Cinque', 'Tre', 'Nessuno'], 0, 'P7'),
 ('pipeline', 2, 'Cosa fa omitContent?', ['Non restituisce il contenuto originale, solo i risultati dei segmenti', 'Cancella il documento dallo storage', 'Disattiva l\'OCR', 'Nasconde i campi a bassa confidenza'], 0, 'P7'),
 ('qualita', 2, 'In che formati l\'analisi delle figure converte grafici e diagrammi?', ['Chart.js per i grafici, Mermaid per i diagrammi', 'CSV e PNG', 'SVG e HTML', 'Solo descrizioni testuali'], 0, 'P7'),
 ('qualita', 2, 'Gli esempi etichettati correggono un OCR che legge "l" come "1"?', ['No: è un problema di lettura (WER), non di comprensione', 'Sì, sempre', 'Sì, ma solo nella preview', 'Solo per i campi generate'], 0, 'P12'),
 ('qualita', 2, 'Qual è l\'ordine ufficiale per migliorare un campo?', ['Prima le descrizioni dei campi, poi gli esempi etichettati', 'Prima gli esempi, poi le descrizioni', 'Cambiare subito modello', 'Abbassare la soglia'], 0, 'P12'),
 ('qualita', 1, 'Le soglie 0,90 / 0,80 / 0,70 della guida sono…', ['Illustrative: vanno determinate sperimentalmente', 'Obbligatorie', 'Garantite da Microsoft', 'Valide solo per l\'inglese'], 0, 'P12'),
 ('qualita', 2, 'Una confidenza di 0,95 significa che il campo è giusto nel 95% dei casi?', ['No: è una stima, la calibrazione va misurata sul tuo campione', 'Sì, per definizione', 'Sì, ma solo con Standard', 'Solo per i campi classify'], 0, 'P2, P12'),
 ('qualita', 2, 'Le date normalizzate in ISO arrivano con il valore grezzo a fianco?', ['No: per tornare all\'originale serve il grounding (pagina e riquadro)', 'Sì, sempre', 'Solo per it-IT', 'Solo nella versione GA'], 0, 'P7, P17'),
 ('sicurezza', 1, 'Con quali algoritmi sono cifrati i dati salvati con chiavi gestite da Microsoft?', ['AES a 256 bit, conforme a FIPS 140-2', 'RSA a 1024 bit', 'DES', 'Non sono cifrati'], 0, 'P18'),
 ('sicurezza', 2, 'Cosa ottieni con le chiavi gestite dal cliente in Key Vault?', ['Un secondo strato di cifratura e il controllo del ciclo di vita, revoca compresa', 'Prezzi più bassi', 'Più quota', 'Nessuna differenza'], 0, 'P18'),
 ('sicurezza', 2, 'Con BYOC e la rete pubblica chiusa sulla risorsa collegata, quale autenticazione usi?', ['Identità gestita di sistema, con il ruolo Cognitive Services User', 'Chiave API', 'Nessuna', 'Token anonimo'], 0, 'P16, P18'),
 ('sicurezza', 1, 'Le richieste viaggiano cifrate con…', ['HTTPS con TLS 1.2 o 1.3', 'HTTP semplice', 'FTP', 'SSL 3.0'], 0, 'P9'),
 ('produzione', 2, 'Le metriche di uso di Azure Monitor dicono quale documento ha consumato più token?', ['No: sono aggregate; serve l\'oggetto usage salvato per documento', 'Sì, per nome del file', 'Sì, nella versione preview', 'Solo per l\'audio'], 0, 'P10'),
 ('produzione', 1, 'A che grana arrivano le metriche di uso?', ['Un minuto', 'Un\'ora', 'Un giorno', 'Un mese'], 0, 'P10'),
 ('produzione', 2, 'Perché le richieste fallite contano verso il limite al minuto?', ['Perché il servizio deve comunque riceverle e valutarle: insistere senza attesa peggiora il problema', 'È un errore della piattaforma', 'Non contano', 'Solo con la capacità riservata'], 0, 'P8'),
 ('produzione', 2, 'Il 429 della capacità riservata (PTU) è…', ['Un segnale di gestione del traffico: rifiuto immediato con attesa, per riprovare o dirottare', 'Un guasto', 'Un errore di autenticazione', 'Un limite di pagine'], 0, 'P8'),
 ('produzione', 3, 'Cosa fa la quota dinamica (anteprima)?', ['Permette a una distribuzione standard di usare più capacità quando c\'è, senza scendere sotto il valore configurato', 'Riduce i prezzi di notte', 'Accumula la quota non usata', 'Aumenta le pagine al minuto di Content Understanding'], 0, 'P8'),
 ('produzione', 1, 'La quota al minuto non usata di notte si accumula per il giorno dopo?', ['No: è una velocità, non una scorta', 'Sì, fino a 24 ore', 'Sì, fino a una settimana', 'Solo per l\'audio'], 0, 'P1'),
 ('produzione', 2, 'Ogni quanto, al massimo, conviene interrogare lo stato di un\'operazione?', ['Non più di una volta ogni due secondi, rispettando retry-after', 'Ogni 100 millisecondi', 'Ogni mezzo secondo', 'Mai: arriva una notifica'], 0, 'P1'),
 ('produzione', 1, 'Quante operazioni al minuto prevede la quota standard?', ['3.000', '1.000', '300', '10.000'], 0, 'P1'),
 ('produzione', 1, 'Quanti analizzatori al massimo per una risorsa S0?', ['100.000', '1.000', '500', '10'], 0, 'Limiti del servizio'),
 ('produzione', 1, 'Quanti caratteri al massimo per la descrizione di un campo o di un analizzatore?', ['1.024', '256', '64', '8.192'], 0, 'Limiti del servizio'),
 ('produzione', 1, 'Quanti caratteri al massimo per il nome di un campo?', ['64', '128', '256', '1.024'], 0, 'Limiti del servizio'),
 ('produzione', 1, 'Quanti tag al massimo su un analizzatore?', ['10', '5', '50', '100'], 0, 'Limiti del servizio'),
 ('costi', 2, 'Perché i token del modello non compaiono nella fattura di Content Understanding?', ['Perché il servizio usa la tua distribuzione Foundry: i token sono sulla fattura del modello', 'Perché sono gratuiti', 'Perché sono inclusi nella contestualizzazione', 'Perché si pagano a fine anno'], 0, 'P2'),
 ('costi', 2, 'Con l\'API 2026-06-01-preview, gli esempi etichettati aggiungono token a ogni analisi?', ['No: l\'addestramento li distilla nell\'analizzatore', 'Sì, sempre', 'Solo per i video', 'Solo con Standard'], 0, 'P2, P6'),
 ('costi', 2, 'Con l\'API 2025-11-01, gli esempi recuperati…', ['Si aggiungono ai token in ingresso a ogni analisi', 'Non costano nulla', 'Si pagano una volta sola', 'Riducono la contestualizzazione'], 0, 'P2'),
 ('costi', 1, 'Cosa paghi usando solo l\'estrazione del contenuto per un sistema RAG?', ['Solo l\'estrazione', 'Estrazione e token', 'Solo la contestualizzazione', 'Niente'], 0, 'P2'),
 ('costi', 2, 'L\'analisi delle figure su un catalogo di mille foto…', ['Paga token per ogni immagine e può diventare una voce enorme', 'È gratuita', 'Costa come una pagina di testo', 'Riduce i costi'], 0, 'P2'),
 ('costi', 2, 'Concatenare analizzatori diversi sui segmenti costa…', ['Come eseguirli separatamente', 'Meno della metà', 'Nulla in più', 'Solo la contestualizzazione'], 0, 'P2'),
 ('costi', 1, 'Su quale contatore cadono le operazioni sincrone Read e Layout, e consumano token di modello?', ['Read Basic, Layout Standard; nessun token di modello', 'Entrambe Minimal, con token', 'Entrambe Standard, con token', 'Gratuite'], 0, 'P16'),
]
def t_concetti():
    for g, l, q, o, c, p in CONC:
        add(g, l, 'Concetto chiave', q, 'Risposta: <b>%s</b>.' % o[c], p, k='mcq', o=o, c=c)

for f in [t_pagine, t_tempo_quota, t_audio_quota, t_contest, t_costo_completo, t_ufficiale, t_maxtokens, t_concorrenza, t_finestre, t_backoff, t_sync, t_av_limiti, t_av_costi, t_contatore,
          t_metodo, t_smistare, t_cu_di, t_prebuilt, t_agentica, t_id_analizzatore, t_wer_eer, t_soglia, t_revisione, t_lingue, t_regioni, t_campione,
          t_ruoli, t_residenza, t_ritenzione, t_shields, t_veleno, t_rete, t_429, t_log, t_allarmi, t_latenza, t_caso_capacita, t_multicloud, t_roi, t_caso_costi, t_concetti]:
    f()

for i, e in enumerate(EX, 1): e['id'] = i

if __name__ == '__main__':
    from collections import Counter
    print(len(EX), Counter(e['l'] for e in EX), Counter(e['g'] for e in EX))
    json.dump(EX, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'esercizi.json'), 'w'), ensure_ascii=False)
