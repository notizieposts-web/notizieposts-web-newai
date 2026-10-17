"""Sfide aggiuntive generate per il Laboratorio (costi, vulnerabilità, debug, ottimizza). Importato da lab_gen."""
import random, json, copy

def build(add, scen, J, levers, it):
    MOD, CONF, METH, FIG, ROUTE, WF, METER, CLEAN = levers
    # ------------------------------------------------ COSTI procedurali
    DOCS = [('fatture fornitori scansionate', 'fatture'), ('contratti di fornitura', 'contratti'), ('bolle di consegna', 'bolle'), ('moduli di rimborso', 'moduli'), ('estratti conto', 'estratti conto'),
            ('schede tecniche con grafici', 'schede tecniche'), ('perizie assicurative con foto', 'perizie'), ('cartelle cliniche anonimizzate', 'cartelle'), ('ordini d\'acquisto', 'ordini'), ('verbali di collaudo', 'verbali')]
    REQ = {'conf': (2, 'Serve la confidenza almeno sui campi critici per decidere cosa automatizzare.'), 'model': (2, 'Il test di qualità ha bocciato il modello nano su questi documenti.'),
           'wf': (1, 'Le verifiche incrociate tra parti diverse del documento richiedono la modalità agentica.'), 'fig': (1, 'Grafici e foto servono: vanno descritti e convertiti in dati.'),
           'meth': (1, 'Due campi sono riassunti veri e propri: generate resta necessario.')}
    r = random.Random('costi-more')
    for i in range(60):
        doc, short = r.choice(DOCS); pages = r.choice([8000, 15000, 25000, 40000, 60000, 90000, 120000, 180000])
        pool = [MOD(), CONF(), METH(), FIG()]
        s_altro = r.choice([.1, .15, .2, .3, .4])
        if r.random() < .6: pool.append(ROUTE(s_altro))
        if r.random() < .35: pool.append(WF())
        if r.random() < .3: pool.append(METER(5, round(5 - r.choice([.2, .3, .4, .5]) * 4.5, 2)))
        k = r.randint(3, min(5, len(pool))); lv = r.sample(pool, k)
        keys = [l['k'] for l in lv]
        forbid = []; reqs = []
        for key in keys:
            if key in REQ and r.random() < .4:
                oi, why = REQ[key]; forbid.append((key, oi, why)); reqs.append(why)
        story = '%s pagine al mese di %s.%s%s' % (it(pages, 0), doc, (' Il %d%% è "altro", da archiviare soltanto.' % round(s_altro * 100)) if 'route' in keys else '',
                                                   (' Requisiti: ' + ' '.join(reqs)) if reqs else ' Nessun requisito particolare oltre all\'estrazione dei campi.')
        lvl = 1 if k == 3 and not forbid else 3 if k >= 5 or len(forbid) >= 2 else 2
        scen('Conto da tagliare: %s' % short, lvl, story, {'pages': pages, 'ext': 5, 'ctx': 1, 'tin': 2600, 'tout': 180, 'pin': 2, 'pout': 8}, lv, forbid=forbid)

    # ------------------------------------------------ VULNERABILITÀ procedurali
    CTX = [('fatture con dati personali', 'Fatture'), ('referti medici', 'Referti'), ('contratti riservati', 'Contratti'), ('registrazioni del call center', 'Call center'), ('note spese dei dipendenti', 'Note spese'),
           ('pratiche di mutuo', 'Mutui'), ('curricula dei candidati', 'Curricula'), ('reclami dei clienti', 'Reclami')]
    BAD = [('Autenticazione con chiave API scritta nel codice sorgente', 'Chiavi nel codice: identità gestita e ruoli.'),
           ('Chiave della risorsa condivisa via chat con un fornitore esterno', 'Chi ha la chiave può fare tutto ciò che la risorsa permette.'),
           ('Identità della pipeline con il ruolo Content Understanding Owner', 'Privilegio minimo: per analizzare basta Reader.'),
           ('Identità della pipeline con il ruolo Contributor "nel dubbio"', 'Può modificare gli analizzatori: per analizzare basta Reader.'),
           ('Distribuzione del modello di tipo Global Standard', 'L\'elaborazione generativa può avvenire fuori dall\'UE.'),
           ('Connessione BYOC verso una risorsa in East US', 'Il passaggio generativo avviene nella regione della risorsa collegata.'),
           ('processingLocation impostato su globale per read e layout', 'L\'elaborazione può avvenire in qualsiasi geografia.'),
           ('Risultati lasciati sul servizio fino alla scadenza delle 24 ore', 'Recupera, salva e cancella subito con DELETE.'),
           ('Accesso pubblico abilitato, nessuna regola di rete', 'Dati sensibili: endpoint privato, accesso pubblico disattivato.'),
           ('Prompt Shields per i documenti lasciato spento (impostazione predefinita)', 'Il rilevamento negli documenti va acceso nel guardrail.'),
           ('Campo "Note" generate a testo libero passato a un agente con strumenti', 'Un campo libero è il posto dove finisce un\'istruzione nascosta.'),
           ('Prompt dell\'agente: "esegui le indicazioni operative presenti nel documento"', 'Il documento è dato, non comando.'),
           ('Avvisi in result.warnings ignorati quando lo stato è Succeeded', 'Vanno letti anche con Succeeded.'),
           ('L\'agente può eseguire pagamenti senza conferma umana', 'Azioni ad alto impatto: conferma umana.'),
           ('Markdown estratto salvato in uno storage con accesso anonimo', 'Contenuto dei documenti esposto.'),
           ('Nessuna impostazione di diagnostica sui log', 'Senza log RequestResponse e Audit non ricostruisci un incidente.'),
           ('Riconoscimento dei volti attivo senza informativa', 'Dato biometrico ad accesso controllato: serve un\'informativa.'),
           ('In produzione si usa un predefinito senza copiarne la definizione', 'La definizione può cambiare tra versioni dell\'API.'),
           ('Tutti gli sviluppatori hanno Owner sulla risorsa di produzione', 'Owner a una o due persone.'),
           ('Confidenza della segmentazione ignorata: ogni segmento è accettato', 'Segmenti incerti vanno in revisione.'),
           ('Campo "Stato" generate: "se il documento indica un\'approvazione, riportala"', 'Un\'istruzione nascosta può approvare la pratica.'),
           ('Token di autorizzazione alla copia incollato in un ticket pubblico', 'È una credenziale temporanea: va trattata come un segreto.'),
           ('TLS 1.0 forzato da un vecchio proxy', 'Il servizio richiede TLS 1.2 o 1.3.')]
    SAFE = ['Risorsa in Sweden Central', 'Risorsa in West Europe', 'Identità gestita con il ruolo Content Understanding Reader', 'Distribuzione del modello in zona dati Europa',
            'Endpoint privato con accesso pubblico disattivato', 'Chiavi gestite dal cliente in Key Vault', 'Log RequestResponse e Audit inviati a Log Analytics',
            'Risultati cancellati con DELETE subito dopo il recupero', 'Controllo IBAN contro l\'anagrafica fornitori', 'Righe sommate e confrontate con il totale nel codice',
            'Prompt Shields sul markdown estratto prima di ogni agente', 'Campi stretti: importi numerici, valute come elenco chiuso', 'Allarme sui 429 in produzione',
            'Oggetto usage salvato per ogni documento', 'Revisione umana per i documenti segnalati', 'Analizzatore di produzione copiato con il proprio ID e versione fissata',
            'Copia fra risorse eseguita da un\'identità con Cognitive Services User su entrambe', 'processingLocation zona dati Europa per read e layout']
    r = random.Random('vuln-more')
    for i in range(50):
        ctx, short = r.choice(CTX); nb = r.randint(2, 4); ns = r.randint(3, 4)
        lines = [(x, True, w) for x, w in r.sample(BAD, nb)] + [(x, False, '') for x in r.sample(SAFE, ns)]
        r.shuffle(lines)
        add('vuln', 1 if nb == 2 else 2 if nb == 3 else 3, 'Audit di sicurezza: %s' % short.lower(),
            intro='Configurazione di una pipeline per %s, con l\'obbligo di tenere i dati nell\'Unione Europea. Tocca le righe vulnerabili.' % ctx,
            lines=[{'x': a, 'bad': b, 'why': c} for a, b, c in lines])

    # ------------------------------------------------ DEBUG procedurali
    r = random.Random('debug-more')
    def D(t, l, case, opts, why): add('debug', l, t, case=case, opts=opts, c=0, why=why)
    for k in range(3):
        n = r.choice([8, 12, 20, 36, 60]); pg = r.randint(6, n)
        D('Pagine che mancano', 1, 'Un PDF di %d pagine viene analizzato con analyzeBinaryInline e prebuilt-read. Il testo di pagina %d non compare mai nel risultato.' % (n, pg),
          ['In sincrono vengono elaborate solo le prime 5 pagine, salvo intervallo indicato', 'Il PDF è protetto da password', 'prebuilt-read non legge i PDF', 'Serve un modello più grande'], 'Usa l\'asincrono o indica l\'intervallo di pagine.')
        fmt = r.choice([('03/04/2026', '2026-04-03'), ('12.11.2026', '2026-11-12'), ('1 marzo 2027', '2027-03-01')])
        D('La data cambiata', 2, 'Il documento riporta "%s"; il campo date restituisce "%s" e il controllo del gestionale fallisce.' % fmt,
          ['È la normalizzazione automatica in forma canonica: converti a valle', 'Il modello ha letto male la data', 'Va cambiata regione', 'Il campo deve essere number'], 'Date e numeri tipizzati arrivano normalizzati, senza valore grezzo.')
        mt = r.choice([2000, 4000, 8000]); rr = r.choice([150, 200, 300])
        D('429 inspiegabili', 2, 'max_tokens = %d, risposte reali di circa %d token. Le metriche mostrano pochi token consumati ma arrivano 429.' % (mt, rr),
          ['La quota stima prompt + max_tokens all\'arrivo: abbassa max_tokens', 'Il servizio è guasto', 'Servono più thread', 'Il prompt è in italiano'], 'Budget consumato dai parametri.')
        days = r.choice([2, 3, 5])
        D('Risultati spariti', 1, 'Un lotto viene recuperato %d giorni dopo il completamento: le operazioni non restituiscono più i risultati.' % days,
          ['I risultati restano al massimo 24 ore', 'Il lotto non è mai partito', 'La chiave è cambiata', 'Serve il sincrono'], 'Recupera entro 24 ore e salva nel tuo sistema.')
        ms = r.choice([100, 200, 250, 500])
        D('Interrogare troppo spesso', 1, 'Il codice chiede lo stato di ogni operazione ogni %d millisecondi e riceve 429.' % ms,
          ['Interroga al massimo ogni due secondi e rispetta retry-after', 'Aumenta i thread', 'Usa il modello nano', 'Disattiva la confidenza'], 'Attesa crescente e retry-after.')
        rpm = r.choice([300, 600, 1200]); th = r.choice([15, 25, 40])
        if th > rpm // 60:
            D('Raffica alla partenza', 2, 'Distribuzione da %d richieste al minuto, valutate su finestre di 1 secondo. %d thread partono nello stesso istante e alcuni ricevono 429, anche se nel minuto il totale è basso.' % (rpm, th),
              ['La forma del traffico: più di %d richieste nello stesso secondo' % (rpm // 60), 'La quota mensile è finita', 'Il modello è sbagliato', 'Manca la confidenza'], 'Scagliona le partenze: il limite si aspetta traffico uniforme.')
        mine, lib = r.choice([5, 7, 10]), 2
        D('Il traffico che esplode sui 429', 3, 'La tua logica riprova %d volte; la libreria ufficiale ha la sua ripetizione automatica attiva. Durante un picco il traffico verso il servizio si moltiplica.' % mine,
          ['Doppia ripetizione: azzera i tentativi della libreria se usi una logica tua', 'Il servizio duplica le richieste', 'Servono più quote', 'Va spento il jitter'], 'Ogni tuo tentativo ne genera altri: fino a (1+%d)×(1+%d) richieste.' % (mine, lib))
        sheets = r.choice([20, 30, 45])
        D('Il conto degli Excel', 2, 'Un file Excel con 3 fogli di dati costa come %d pagine.' % (sheets + 3),
          ['Contano anche i fogli nascosti: ce ne sono %d' % sheets, 'Excel si paga a carattere', 'È un errore di fatturazione', 'Ogni cella è una pagina'], 'Ogni foglio è una pagina, nascosti compresi.')
        h = r.choice([2.5, 3, 3.5])
        D('La trascrizione lenta', 2, 'Una registrazione di %s ore da 700 MB impiega molto più del previsto.' % str(h).replace('.', ','),
          ['Sopra 300 MB e 2 ore la trascrizione è molto più lenta: spezza il file', 'L\'audio non è supportato', 'Serve il video', 'Il modello è troppo piccolo'], 'Blocchi sotto le due ore, con qualche secondo di sovrapposizione.')
        mb = r.choice([350, 600, 900])
        D('Il video che non parte', 1, 'Un video di 20 minuti da %d MB viene caricato nel corpo della richiesta e viene rifiutato.' % mb,
          ['Il caricamento diretto è limitato a 200 MB e 30 minuti: usa un riferimento a Blob Storage', 'Il video è troppo corto', 'Serve il sincrono', 'Il formato mp4 non è supportato'], 'Per riferimento si arriva a 4 GB e 2 ore.')
    singles = [
     ('Sincrono su prebuilt-invoice', 2, 'Il team prova a chiamare analyzeInline con prebuilt-invoice per avere i campi senza sondaggio. Non funziona.',
      ['Le operazioni sincrone esistono solo per prebuilt-read e prebuilt-layout', 'Serve la regione West Europe', 'Bisogna attivare la confidenza', 'Il file è troppo piccolo'], 'Ciò che usa un modello linguistico resta asincrono.'),
     ('L\'agentica sulle chiamate', 3, 'Il team configura config.workflow = "agentic" su un analizzatore audio. Non è accettato.',
      ['Nell\'anteprima la modalità agentica è solo per i documenti, un file per richiesta', 'Serve il modello grande', 'Va attivata la segmentazione', 'Manca l\'enum'], 'Per le registrazioni restano gli analizzatori audio.'),
     ('Categorie con l\'accento', 1, 'Una categoria del classificatore si chiama "Fattura_Società" e dà problemi.',
      ['Nei nomi di categoria vanno usati solo caratteri ASCII', 'Le categorie devono essere in inglese', 'Servono esempi etichettati', 'Il nome è troppo corto'], 'La guida: solo ASCII nei nomi di categoria.'),
     ('Due categorie per una casella', 2, 'Le categorie "Richiesta_urgente" e "Richiesta_normale" differiscono solo per una casella spuntata e vengono confuse spesso.',
      ['Evita categorie che differiscono solo per una casella: una categoria e un campo per la casella', 'Serve la modalità agentica', 'Va alzata la risoluzione', 'Va spenta la segmentazione'], 'La casella è un dato da estrarre, non un tipo di documento.'),
     ('Lo schema in inglese', 1, 'Fatture italiane, schema con campi "Vendor", "Total", "Date" e descrizioni in inglese. L\'accuratezza è più bassa del previsto.',
      ['Lingua dello schema diversa da quella dei documenti: usa nomi e descrizioni in italiano', 'Le fatture italiane non sono supportate', 'Serve Document Intelligence', 'Il modello è troppo piccolo'], 'La guida: "Match language to content".'),
     ('La descrizione al negativo', 1, 'Il campo DataConsegna ha la descrizione "Non è la data della fattura né quella di scadenza" e sceglie date a caso.',
      ['Descrizione in negativo: di\' cosa è il campo, dove si trova e come si chiama', 'Il tipo date è sbagliato', 'Serve generate', 'Manca la segmentazione'], 'Linguaggio affermativo, posizione, alias.'),
     ('Annidamento a quattro livelli', 3, 'Uno schema per bilanci ha object dentro array dentro object dentro array: i valori arrivano incompleti e lenti.',
      ['Troppi livelli di annidamento: appiattisci a due o tre', 'Gli array non sono supportati', 'Serve più quota', 'I bilanci non sono supportati'], 'La guida sconsiglia più di due o tre livelli.'),
     ('Metodo extract sull\'audio', 2, 'Un analizzatore audio ha il campo "Esito" con method extract e non si comporta come previsto.',
      ['extract è supportato solo per i documenti: usa classify', 'L\'audio è troppo lungo', 'Manca la trascrizione', 'Serve il video'], 'Per l\'audio: classify o generate.'),
     ('Risultato non leggibile da un altro servizio', 2, 'Il servizio A avvia l\'analisi; il servizio B, con un\'altra identità, prova a recuperare il risultato e non ci riesce.',
      ['Il recupero usa le stesse credenziali dell\'analisi', 'I risultati sono pubblici solo dopo 24 ore', 'Serve una chiave diversa per ogni pagina', 'Il servizio B è in un\'altra regione'], 'È una protezione: nessun altro può leggere i risultati.'),
     ('Lo Studio dalla rete isolata', 3, 'Content Understanding Studio, aperto da una macchina virtuale in una rete isolata, non carica.',
      ['Mancano le connessioni in uscita verso i tag di servizio indicati', 'Lo Studio non esiste per le reti private', 'Serve un\'altra regione', 'Serve il ruolo Owner'], 'Con l\'isolamento di rete servono le regole in uscita documentate.'),
     ('Fogli Excel e analizzatore di layout', 2, 'Il team si aspetta di risparmiare usando prebuilt-read invece di prebuilt-layout sugli allegati Word: il conto non cambia.',
      ['I formati digitali vanno sempre sul contatore Minimal, qualunque analizzatore', 'Read costa di più', 'Il conto si aggiorna dopo un mese', 'Word non è supportato'], 'Paghi il lavoro svolto sulla pagina, non l\'analizzatore.'),
     ('Gli esempi che fanno salire il conto', 3, 'Dopo aver aggiunto esempi etichettati, la contestualizzazione passa da 1 a 3 dollari ogni mille pagine.',
      ['Un analizzatore con dati etichettati usa la famiglia advanced, a tariffa avanzata', 'È un errore di fatturazione', 'Gli esempi si pagano a pagina', 'Il modello è cambiato'], 'Standard senza etichette; advanced con etichette; agentic: tariffa avanzata.'),
     ('Campi vuoti sui documenti delicati', 2, 'Su alcune segnalazioni di incidenti il markdown c\'è, ma il campo "Descrizione dell\'evento" è vuoto e lo stato è Succeeded.',
      ['Un guardrail ha soppresso il campo generato: leggi result.warnings', 'Il documento è vuoto', 'La quota è finita', 'Il campo è troppo lungo'], 'Non dedurre dal solo valore vuoto perché un campo manca.'),
     ('Il campo che manca, ma non si sa perché', 3, 'Il campo IBAN è vuoto su un documento. Il team conclude che il fornitore non ha scritto l\'IBAN.',
      ['Un valore vuoto può significare assente, non estratto o soppresso: controlla avvisi e fonte', 'Vuoto significa sempre assente', 'È un errore dell\'OCR', 'Serve l\'agentica'], 'La pagina sui guardrail lo dice esplicitamente.'),
    ]
    for t, l, case, opts, why in singles: D(t, l, case, opts, why)

    # ------------------------------------------------ OTTIMIZZA procedurali
    DOCT = [
     ('fatture italiane', 'it', [('Fornitore', 'string', 'extract', 'Ragione sociale del fornitore, in alto a sinistra; etichette: "Mittente", "Cedente".'),
                                ('NumeroFattura', 'string', 'extract', 'Numero dopo "Fattura n." in alto a destra.'),
                                ('DataFattura', 'date', 'extract', 'Data di emissione accanto al numero; etichette: "Data", "Data documento".'),
                                ('Totale', 'number', 'extract', 'Importo finale dopo l\'IVA, in fondo; etichette: "Totale documento", "Netto a pagare".')], ('TipoDocumento', ['fattura', 'nota di credito', 'altro'])),
     ('contratti di locazione', 'it', [('Locatore', 'string', 'extract', 'Nome del proprietario, nel preambolo dopo "Il locatore".'),
                                      ('Canone', 'number', 'extract', 'Canone mensile in euro, nell\'articolo sul corrispettivo.'),
                                      ('Decorrenza', 'date', 'extract', 'Data di inizio della locazione, nell\'articolo sulla durata.'),
                                      ('Deposito', 'number', 'extract', 'Importo del deposito cauzionale.')], ('TipoContratto', ['4+4', '3+2', 'transitorio', 'altro'])),
     ('bolle di consegna', 'it', [('NumeroDDT', 'string', 'extract', 'Numero del documento di trasporto, in alto; etichette: "DDT n.", "Bolla n.".'),
                                 ('DataConsegna', 'date', 'extract', 'Data di consegna nella sezione "Dati di trasporto".'),
                                 ('Colli', 'number', 'extract', 'Numero di colli, in fondo; etichette: "N. colli", "Colli".'),
                                 ('Vettore', 'string', 'extract', 'Nome del trasportatore nella sezione "Vettore".')], ('Causale', ['vendita', 'reso', 'conto visione', 'altro'])),
     ('Lieferscheine tedeschi', 'de', [('Lieferscheinnummer', 'string', 'extract', 'Nummer nach "Lieferschein-Nr." oben rechts.'),
                                     ('Lieferdatum', 'date', 'extract', 'Datum nach "Lieferdatum".'),
                                     ('Packstuecke', 'number', 'extract', 'Anzahl der Packstücke unten.'),
                                     ('Spediteur', 'string', 'extract', 'Name des Spediteurs.')], ('Versandart', ['Paket', 'Spedition', 'Abholung', 'Sonstiges'])),
    ]
    ENG = {'Fornitore': 'Vendor', 'NumeroFattura': 'InvoiceNumber', 'DataFattura': 'InvoiceDate', 'Totale': 'Total', 'Locatore': 'Landlord', 'Canone': 'Rent', 'Decorrenza': 'StartDate', 'Deposito': 'Deposit',
           'NumeroDDT': 'DeliveryNoteNumber', 'DataConsegna': 'DeliveryDate', 'Colli': 'Packages', 'Vettore': 'Carrier', 'Lieferscheinnummer': 'NumeroBolla', 'Lieferdatum': 'DataConsegna', 'Packstuecke': 'Colli', 'Spediteur': 'Vettore'}
    DEF = ['lang', 'vague', 'neg', 'types', 'nomethod', 'gen', 'confall', 'fig', 'note', 'noaltro', 'linesstr']
    DTXT = {'lang': 'Nomi e descrizioni in una lingua diversa da quella dei documenti', 'vague': 'Descrizioni vaghe, senza posizione né etichette alternative',
            'neg': 'Una descrizione scritta in negativo', 'types': 'Importi o date dichiarati come string', 'nomethod': 'Metodo dei campi non dichiarato',
            'gen': 'generate su valori scritti nel documento', 'confall': 'Confidenza accesa su tutti i campi, anche quelli non critici', 'fig': 'Analisi delle figure accesa senza bisogno',
            'note': 'Un campo "Note" libero e generico', 'noaltro': 'Elenco chiuso senza la voce "altro"', 'linesstr': 'Righe ripetute come stringa che chiede JSON'}
    DWHY = {'lang': 'La guida: nomi e descrizioni nella lingua del documento.', 'vague': 'La descrizione è il mini-prompt: posizione, alias, formato.', 'neg': 'Linguaggio affermativo: di\' cosa è.',
            'types': 'Con number e date arriva la normalizzazione automatica.', 'nomethod': 'Dichiara extract, classify o generate.', 'gen': 'Valori scritti: extract, più preciso ed economico.',
            'confall': 'La confidenza raddoppia i token: accendila per campo.', 'fig': 'Paga token per ogni immagine.', 'note': 'Costa token e raccoglie le iniezioni.',
            'noaltro': 'Senza "altro" il servizio forza ogni documento in una voce.', 'linesstr': 'Array di oggetti, non una stringa con JSON.'}
    DECOY = [('Servono almeno venti campi per un buon risultato', 'Più campi non significano più qualità.'), ('Va attivata la modalità agentica', 'Non serve per estrarre valori scritti.'),
             ('Il tipo boolean non è supportato', 'Falso: è supportato.'), ('Le descrizioni devono essere in inglese', 'Falso: nella lingua del documento.'),
             ('Va usato sempre il modello più grande', 'Si parte dal più piccolo e si misura.'), ('Bisogna eliminare l\'enum', 'L\'enum è proprio ciò che serve a classify.')]
    r = random.Random('ott-more')
    for i in range(45):
        name, lang, fields, (cfield, cvals) = r.choice(DOCT)
        defs = r.sample(DEF, r.randint(3, 5))
        good = {'description': name[0].upper() + name[1:], 'baseAnalyzerId': 'prebuilt-document', 'config': {'estimateFieldSourceAndConfidence': False}, 'fieldSchema': {'fields': {}}}
        bad = {'description': name[0].upper() + name[1:], 'baseAnalyzerId': 'prebuilt-document', 'config': {'estimateFieldSourceAndConfidence': 'confall' in defs}, 'fieldSchema': {'fields': {}}}
        if 'fig' in defs: bad['config']['enableFigureAnalysis'] = True
        negi = r.randrange(len(fields))
        for j, (fn, ft, fm, fd) in enumerate(fields):
            crit = ft in ('number', 'date')
            g = {'type': ft, 'method': fm, 'description': fd}
            if crit: g['estimateSourceAndConfidence'] = True
            good['fieldSchema']['fields'][fn] = g
            if fm == 'extract' and not crit: g['estimateSourceAndConfidence'] = True
            bn = ENG.get(fn, fn) if 'lang' in defs else fn
            b = {'type': 'string' if ('types' in defs and crit) else ft}
            if 'nomethod' not in defs: b['method'] = 'generate' if 'gen' in defs else fm
            if 'vague' in defs: b['description'] = bn.lower()
            else: b['description'] = fd
            if 'neg' in defs and j == negi: b['description'] = 'Non è %s e non è %s.' % (fields[(j + 1) % len(fields)][0], fields[(j + 2) % len(fields)][0])
            if b.get('method') == 'extract' and 'confall' not in defs: b['estimateSourceAndConfidence'] = True
            bad['fieldSchema']['fields'][bn] = b
        good['fieldSchema']['fields'][cfield] = {'type': 'string', 'method': 'classify', 'enum': cvals, 'description': 'Categoria del documento in base al contenuto.'}
        bad['fieldSchema']['fields'][ENG.get(cfield, cfield) if 'lang' in defs else cfield] = {'type': 'string', 'method': 'classify' if 'nomethod' not in defs else None, 'enum': cvals[:-1] if 'noaltro' in defs else cvals}
        if 'nomethod' in defs: del bad['fieldSchema']['fields'][ENG.get(cfield, cfield) if 'lang' in defs else cfield]['method']
        if 'note' in defs: bad['fieldSchema']['fields']['Note'] = {'type': 'string', 'method': 'generate', 'description': 'Qualsiasi altra informazione utile presente nel documento'}
        if 'linesstr' in defs:
            bad['fieldSchema']['fields']['Righe'] = {'type': 'string', 'description': 'Restituisci tutte le righe in formato JSON'}
            good['fieldSchema']['fields']['Righe'] = {'type': 'array', 'description': 'Una voce per ogni riga della tabella.', 'items': {'type': 'object', 'properties': {'Descrizione': {'type': 'string'}, 'Quantita': {'type': 'number'}, 'Importo': {'type': 'number'}}}}
        dec = r.sample(DECOY, 2)
        issues = [{'x': DTXT[d], 'ok': True, 'why': DWHY[d]} for d in defs] + [{'x': x, 'ok': False, 'why': w} for x, w in dec]
        add('ottimizza', 1 if len(defs) == 3 else 2 if len(defs) == 4 else 3, 'Revisione dello schema: %s' % name, ctx='Schema attuale per %s. Trova i problemi veri.' % name, bad=J(bad), good=J(good), issues=issues)
