import asyncio, json, sys, glob, os
from playwright.async_api import async_playwright
AXE=open(os.path.join(os.path.dirname(__file__),'node_modules/axe-core/axe.min.js')).read()
root=sys.argv[1]
files=['index.html']+sorted(os.path.relpath(f,root) for f in glob.glob(root+'/edizioni/*.html'))
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(); tot={}
        for scheme in ['light','dark']:
          for f in files:
            pg=await b.new_page(viewport={'width':1280,'height':900},color_scheme=scheme)
            await pg.goto('file://'+root+'/'+f); await pg.wait_for_timeout(300)
            await pg.add_script_tag(content=AXE)
            r=await pg.evaluate("axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21a','wcag21aa','wcag22aa']}})")
            for v in r['violations']:
                k=(v['id'],v['impact'])
                tot.setdefault(k,{'n':0,'files':set(),'ex':v['nodes'][0]['target'],'sum':v['nodes'][0].get('failureSummary','')[:160]})
                tot[k]['n']+=len(v['nodes']); tot[k]['files'].add(f+':'+scheme)
            await pg.close()
        for k,v in sorted(tot.items(),key=lambda x:-x[1]['n']):
            print(k, v['n'], len(v['files']), v['ex'], '|', v['sum'].replace('\n',' '))
        await b.close()
asyncio.run(main())
