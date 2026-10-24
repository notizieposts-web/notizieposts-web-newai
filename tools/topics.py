"""Etichette del menu: una parola, il protagonista. Aggiunge anche il chip del protagonista in testa a ogni capitolo."""
import re, sys, os
STD = {'periodo':'Calendario','lab':'Prova tu','segnali':'Segnali','novita':'Novità','quiz':'Quiz','fonti':'Fonti','azure':'Azure','escluso':'Esclusi','piste':'Piste','correzioni':'Correzioni'}
MAP = {
 '02':{'mese':'Settembre','architetture':'Architetture','jev':'TypeSafe','paper':'CMU','ricerca':'Jev','clm':'Stanford','mercury':'Inception','atlas':'World Labs','nvidia':'NVIDIA','devday':'OpenAI','grandi':'Laboratori','costi':'Costi'},
 '03':{'argon':'Gemini','astra':'OpenAI','contesto':'Meta','grandi':'Laboratori','costi':'Costi'},
 '04':{'clef':'Cloudflare','bench':'Benchmark','scegli':'Confronto'},
 '05':{'strands':'Amazon','aperto':'Open source','gate':'Guardrail'},
 '06':{'sapien':'Sapien','proatt':'IBM','praxa':'Praxa'},
 '07':{'sun':'Google'},
 '08':{'kimi':'Moonshot'},
 '09':{'distill':'OpenAI'},
 '10':{'autopilot':'Microsoft'},
 '11':{'kolibri':'Aleph Alpha','moe':'MoE'},
 '12':{'pi':'Pi','tessera':'Cambridge'},
 '13':{'gemini':'Gemini','academy':'Anthropic'},
 '14':{'synopsys':'Synopsys'},
 '15':{'hearing':'Audizione','standards':'Laboratori'},
 '16':{'wm':'ChatGPT'},
 '17':{'chonk':'Mistral','beam':'Reflection'},
 '18':{'wiki':'Wikimedia','gpt6':'GPT-6','qualita':'Azure 12','cloud':'Azure 13','caso':'Azure 14'},
 '19':{'decisioni':'Decisionali','memento':'Memento','incidenti':'Incidenti','anthropic':'Anthropic'},
 '20':{'muse':'Meta','anthropic':'Anthropic','ferro':'Hardware','ricerca':'Ricerca'},
 '21':{'gemini':'Gemini','governance':'Valutatori','codice':'Codice','fisica':'Robot'},
 '22':{'agenti':'JPMorgan','gusto':'TasteVal','ritiri':'OpenAI','dati':'Privacy'},
 '23':{'recinto':'NVIDIA','lunghi':'Gemini','aperti':'Meta','regole':'FTC'},
 '24':{'sconfini':'OpenAI','semi':'Claude','lavoro':'Anthropic','flash':'DeepSeek','postgres':'PostgreSQL'},
 '25':{'fondo':'Anthropic','banche':'Schwab','nscale':'Nscale','cristalli':'MIT'},
 '26':{'cairn':'Cairn','microsoft':'Microsoft','openai':'OpenAI','hybrid':'HybridAgents'},
 '27':{'google':'Google','eka':'Eka','deepseek':'DeepSeek','guardrail':'Guardrail'},
 '28':{'php':'PHP','openai':'OpenAI','claude':'Claude','meta':'Meta'},
 '30':{'openai':'OpenAI','dxo':'Microsoft','rocq':'Anthropic','vercel':'Vercel'},
 '29':{'microsoft':'Microsoft','flint':'Flint','skills':'Anthropic','jolt':'Perplexity'},
}
def process(path, labels):
    s = open(path, encoding='utf-8').read()
    s = re.sub(r'<span class="chip topic"[^>]*>.*?</span>', '', s)
    nav = re.search(r'(<div class="links" id="links">)(.*?)(</div>)', s, re.S)
    if not nav: return
    def relabel(m):
        href = m.group(2); lab = labels.get(href) or STD.get(href)
        if not lab: return m.group(0)
        return '%s%s</a>' % (m.group(1), lab)
    inner = re.sub(r'(<a href="#([^"]+)"[^>]*>).*?</a>', relabel, nav.group(2))
    s = s[:nav.start()] + nav.group(1) + inner + nav.group(3) + s[nav.end():]
    for sec, lab in list(labels.items())+([('azure','Azure')] if 'id="azure"' in s else []):
        m = re.search(r'<section[^>]*id="%s"[^>]*>.*?<div class="kicker">' % re.escape(sec), s, re.S)
        if m: s = s[:m.end()] + '<span class="chip topic">%s</span>' % lab + s[m.end():]
    open(path, 'w', encoding='utf-8').write(s)
if __name__ == '__main__':
  root = sys.argv[1]
  for ed, labels in MAP.items():
    process(os.path.join(root, 'edizioni', ed + '.html'), labels)
  process(os.path.join(root, 'index.html'), {})
  print('ok')
