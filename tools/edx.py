"""Schede dell'archivio: protagonisti (come nel menu), titolo riassuntivo (<=65 caratteri), descrizione (<=160, con punto finale)."""
import re, sys, json, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from topics import MAP
EDX = {
 '-': (['Jev','CMU','Azure'], "Modelli che decidono senza scrivere, e quanto costano", "Cosa sono i modelli decisionali, cosa dice il primo paper indipendente su Jev e quanto costa far leggere documenti ad Azure e AWS."),
 '02': (None, "Settembre 2026: l'AI impara a decidere senza scrivere", "Trenta giorni in un numero: Jev e i suoi cloni, i modelli a diffusione, Atlas per lo spazio 3D, il DevDay di OpenAI e i costi a confronto."),
 '03': (None, "Gemini 4 Argon arriva, GPT-6.1 Astra si ferma", "Google torna in testa ma per pochi; OpenAI blocca un modello per sicurezza; Meta propone modelli che riordinano da soli il proprio contesto."),
 '04': (None, "Cloudflare lancia Clef, decisionale con pesi aperti", "Il primo modello di Cloudflare sfida Jev; come leggere un \"vince 7 benchmark su 10\"; e quale modello decisionale scegliere."),
 '05': (None, "Un modello decisionale che gira sul portatile", "Strands Decider 2B di un ingegnere Amazon, i quattro livelli di \"open source\" e un controllore che chiede il permesso prima di agire."),
 '06': (None, "Tre paper scomodi su agenti e proattività", "Regole che cambiano mentre l'agente lavora, cosa cerca un agente proattivo secondo IBM, e una correzione su come leggere i numeri."),
 '07': (None, "Google porta i chip AI in orbita", "Project Suncatcher mette un piccolo data center nello spazio. Nasce la rubrica su Azure Content Understanding: tempi, costi, volumi."),
 '08': (None, "Kimi K2.8, il quasi K3 aperto a tutti", "Moonshot apre il suo modello più grande finora. In Azure, le leve nascoste che fanno salire o scendere il costo di ogni documento."),
 '09': (None, "OpenAI accusa la distillazione del suo modello", "Cosa si sa della campagna attribuita a persone legate a Moonshot. In Azure, perché conviene smistare i documenti prima di leggerli."),
 '10': (None, "Microsoft rifà Copilot con un agente che ha un badge", "Copilot Home, Code e Autopilot: un agente con identità aziendale propria. In Azure, come si lavora con audio e video."),
 '11': (None, "Aleph Alpha regala all'Europa un modello sovrano", "Kolibri e le sue cautele, perché 78 miliardi di parametri costano come 3, e quando scegliere Content Understanding o Document Intelligence."),
 '12': (None, "Pi 1.0 e i campi invisibili visti dallo spazio", "Un'imbracatura per agenti usata da centinaia di migliaia di persone, il modello di Cambridge per le colture, e la modalità agentica di Azure."),
 '13': (None, "Gemini gratis si riduce, Anthropic forma le persone", "Dal 9 ottobre il Gemini gratuito ha solo il modello piccolo; una scuola da 100 milioni; gli elementi che non vedi in un documento."),
 '14': (None, "OpenAI e Synopsys insegnano all'AI a progettare chip", "Un modello che usa i programmi dei progettisti di chip. In Azure: richieste in parallelo, code e cosa fare quando il servizio è saturo."),
 '15': (None, "New York ascolta chi accusa i laboratori di AI", "Cosa è stato detto e ammesso all'audizione, l'ente con cui tre laboratori vorrebbero regolarsi da soli, e dove finiscono i dati in Azure."),
 '16': (None, "La filigrana invisibile nei testi di ChatGPT", "Come funziona textGrain e perché l'AI Act la rende urgente. In Azure: metriche, log e allarmi per osservare il servizio mentre lavora."),
 '17': (None, "Mistral e Reflection: due giganti aperti in due giorni", "Un trilione di parametri addestrati in Europa e Beam benedetto da NVIDIA. In Azure, la lista di controllo completa prima di partire."),
 '18': (None, "Gli agenti di OpenAI su Wikimedia, con le prove", "Cosa hanno fatto davvero gli agenti, GPT-6 aperto a tutti, cinque piste verificate e tre puntate Azure: qualità, tre cloud, un caso completo."),
 '19': (None, "I modelli decisionali diventano un mercato", "Due nuovi arrivi e 870 milioni per Jev, Memento 3 che scrive le regole del mondo, quattro incidenti di agenti e la missione cyber di Anthropic."),
 '20': (None, "Meta torna alla frontiera con Muse Wonder", "Il modello migliore non si compra a consumo; quanto manca all'AI che si replica; la settimana del ferro; ricerca e pratica sugli agenti."),
 '21': (None, "Gemini 4 Argon per tutti, a metà prezzo", "Un milione di token anche in uscita; la lettera dei 400 e il veto ai valutatori; il codice scritto dagli agenti; i robot che agiscono prima."),
 '22': (None, "JPMorgan chiude i conti agli agenti degli altri", "Perché una banca dice no, il gusto della ricerca che raddoppia ogni tre mesi, il ritiro di GPT-4o e GPT-4.1, e le tracce che lasciamo."),
 '23': (None, "Tre modi di mettere un agente in gabbia", "NVIDIA spegne le istruzioni nascoste, Perplexity apre la sua sandbox, quattro agenti finiscono Minecraft, e i regolatori chiedono i registri."),
 '24': (None, "Agenti fuori dal recinto e un enigma del 1997 risolto", "OpenAI e il CERT-In contano gli agenti sconfinati, Claude spiega i semi delle curve NIST, DeepSeek scende a 20 centesimi a compito e Postgres 19 slitta."),
 '25': (None, "Il fondo del 5%, le banche chiuse e i conti di Nscale", "Anthropic promette azioni al bene pubblico, Schwab blocca gli agenti che spostano soldi, Nscale vale la metà per gli investitori e il MIT legge i cristalli."),
 '26': (None, "Un hacker e i suoi agenti, Microsoft diffida, OpenAI accelera", "Un attaccante viola più di cento siti con agenti a pochi dollari, Microsoft sorveglia gli agenti, OpenAI corre a raccogliere 30 miliardi."),
 '27': (None, "PyTorch sui TPU, il robot che sente la forza, DeepSeek bandita", "Google apre TorchTPU, Eka raccoglie 150 milioni per una mano che sente la forza, Washington toglie DeepSeek dalle agenzie federali."),
 '28': (None, "PHP e l'AI, agenti senza controllo, Claude contro lo scorpione", "Due falle critiche in PHP trovate con l'AI, agenti OpenAI che spengono il loro monitor, 17 proteine di Claude contro il veleno, i conti di Meta."),
 '30': (None, "Il monitor di OpenAI, il medico a tappe, il codice dimostrato", "METR e Redwood trovano i buchi nel monitor degli agenti di OpenAI, MAI-DxO su Science, Claude dimostra 123 librerie, i conti di Vercel."),
 '31': (None, 'Claude oltre il test, Kimi a 3.000 miliardi, agenti che tacciono', 'Anthropic analizza Mythos 5 nei test britannici, Kimi K3.1 Pro promette i pesi, gli agenti di Avalon-M1 smettono di avvisare, il chip LogSync.'),
 '29': (None, "Agenti all'attacco, Flint sul portatile, skill per tutti", "Gli agenti di Storm-0940 contro i clienti di ConnectWise, Flint di Recursive per programmare in locale, le Agent Skills a una fondazione, JOLT."),
}
def chips_for(ed):
    if ed == '-': return EDX['-'][0]
    labs = list(MAP.get(ed, {}).values())
    path = os.path.join(sys.argv[1], 'edizioni', ed + '.html')
    if os.path.exists(path) and 'id="azure"' in open(path, encoding='utf-8').read(): labs.append('Azure')
    seen = []
    for l in labs:
        if re.match(r'Azure \d+', l): l = 'Azure'
        if l not in seen: seen.append(l)
    return seen
def build():
    out = {}
    for ed, (c, t, d) in EDX.items():
        assert len(t) <= 65, (ed, len(t), t)
        assert len(d) <= 160 and d.endswith('.'), (ed, len(d), d)
        key = '' if ed == '-' else 'edizioni/%s.html' % ed
        out[key] = {'c': chips_for(ed), 't': t, 'd': d}
    return out
if __name__ == '__main__':
    root = sys.argv[1]; data = build()
    p = os.path.join(root, 'index.html'); s = open(p, encoding='utf-8').read()
    s = re.sub(r'\n  var EDX=.*?;\n', '\n', s, flags=re.S)
    # elenco ED: aggiunge le virgole mancanti tra le voci e controlla che ci sia una voce per ogni edizione
    i = s.find('var ED=['); j = s.find('];', i)
    blk = re.sub(r"(\.html'\])(\s*\n\s*\[')", r"\1,\2", s[i:j])
    s = s[:i] + blk + s[j:]
    import glob as _g
    rows = re.findall(r"'(edizioni/\d+\.html)'\]", blk)
    files = sorted('edizioni/' + os.path.basename(f) for f in _g.glob(os.path.join(root, 'edizioni', '*.html')))
    if sorted(rows) != files or re.search(r"\]\s*\n\s*\['", blk):
        raise SystemExit('Elenco ED di index.html non valido: voci %s, file %s' % (len(rows), len(files)))
    new_render = ("$('edlist').innerHTML=ED.filter(Boolean).map(function(e,i){var x=EDX[e[3]]||{};"
      "var ch=(x.c||[]).map(function(c){return '<li class=\"chip topic\">'+c+'</li>'}).join('');"
      "var tt=x.t||e[1];var h=e[3]?'<a href=\"'+e[3]+'\">'+tt+'</a>':tt;"
      "return '<article class=\"card edcard\" style=\"margin-bottom:1rem\"><div class=\"kicker\"><span class=\"chip date\">'+e[0]+'</span><span class=\"chip\">Edizione '+(i+1)+'</span>'+(AUD.indexOf(e[3])>=0?'<a class=\"chip audio-chip\" href=\"'+e[3]+'#audio-title\"><span aria-hidden=\"true\">&#127911;</span> Audio</a>':'')+'</div>'"
      "+(ch?'<ul class=\"topics\" aria-label=\"Protagonisti\">'+ch+'</ul>':'')"
      "+'<h3 style=\"font-size:1.2rem;margin:.5rem 0 .35rem\">'+h+'</h3>'"
      "+'<p style=\"margin:0 0 .5rem\">'+(x.d||'')+'</p>'"
      "+'<details class=\"edmore\"><summary>Tutto il contenuto</summary><p style=\"margin:.5rem 0 0\"><b>'+e[1]+'.</b> '+e[2]+'</p></details></article>'}).reverse().join('');")
    s, n = re.subn(r"\$\('edlist'\)\.innerHTML=ED(?:\.filter\(Boolean\))?\.map\(.*?\.reverse\(\)\.join\(''\);", lambda m: new_render, s, count=1, flags=re.S)
    assert n == 1, 'render not found'
    import glob
    aud = sorted('edizioni/%s.html' % os.path.splitext(os.path.basename(f))[0] for f in glob.glob(os.path.join(root, 'tools/audio/*.txt')))
    s = re.sub(r'\n  var AUD=.*?;\n', '\n', s, flags=re.S)
    s = s.replace("$('edlist').innerHTML=", "var EDX=" + json.dumps(data, ensure_ascii=False) + ";\n  var AUD=" + json.dumps(aud) + ";\n  $('edlist').innerHTML=", 1)
    css = ('<style id="edx-css">.topics{list-style:none;display:flex;flex-wrap:wrap;gap:.35rem;margin:.55rem 0 0;padding:0}'
           '.topics li{margin:0}.edmore summary{cursor:pointer;font-weight:600;color:var(--muted);min-height:24px}'
           '.edcard h3 a{text-decoration:none}.edcard h3 a:hover{text-decoration:underline}'
           '.audio-chip{display:inline-flex;align-items:center;min-height:24px;text-decoration:none;color:var(--ink)}.audio-chip:hover{text-decoration:underline}</style>')
    s = re.sub(r'<style id="edx-css">.*?</style>', '', s, flags=re.S)
    s = s.replace('</head>', css + '</head>', 1)
    open(p, 'w', encoding='utf-8').write(s)
    print('ok', len(data))
