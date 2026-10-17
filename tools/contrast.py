import asyncio, sys, glob, os, collections
from playwright.async_api import async_playwright
AXE=open('node_modules/axe-core/axe.min.js').read()
root=sys.argv[1]
files=['index.html']+sorted(os.path.relpath(f,root) for f in glob.glob(root+'/edizioni/*.html'))
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(); c=collections.Counter(); sel=collections.defaultdict(set)
        for scheme in ['light','dark']:
          for f in files:
            pg=await b.new_page(viewport={'width':1280,'height':900},color_scheme=scheme)
            await pg.goto('file://'+root+'/'+f); await pg.wait_for_timeout(300)
            await pg.add_script_tag(content=AXE)
            r=await pg.evaluate("axe.run(document,{runOnly:{type:'rule',values:['color-contrast']}})")
            for v in r['violations']:
                for n in v['nodes']:
                    d=n['any'][0]['data']; k=(scheme,d.get('fgColor'),d.get('bgColor'),d.get('contrastRatio'),d.get('fontSize'))
                    c[k]+=1; sel[k].add(n['target'][0][:50])
            await pg.close()
        for k,v in c.most_common(40): print(v,k,list(sel[k])[:3])
        await b.close()
asyncio.run(main())
