import asyncio,glob,os,collections
from playwright.async_api import async_playwright
import sys
root=sys.argv[1] if len(sys.argv)>1 else '.'
files=sorted(os.path.basename(f) for f in glob.glob(root+'/*.html'))+sorted(os.path.relpath(f,root) for f in glob.glob(root+'/edizioni/*.html'))
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch();c=collections.Counter()
        for f in files:
            pg=await b.new_page(viewport={'width':320,'height':800})
            await pg.goto('file://'+root+'/'+f);await pg.wait_for_timeout(250)
            sw=await pg.evaluate("document.documentElement.scrollWidth")
            if sw<=322: await pg.close(); continue
            r=await pg.evaluate("""()=>{var out=[];document.querySelectorAll('body *').forEach(function(e){var r=e.getBoundingClientRect();if(r.right>322&&r.width>0){var p=e.parentElement;var pr=p?p.getBoundingClientRect().right:0;if(pr<=322&&!e.closest('.tl')&&!e.closest('.links')&&getComputedStyle(e).position!=='fixed'){out.push(e.tagName+'.'+(e.className&&e.className.baseVal===undefined?e.className:'')+'#'+e.id+' w='+Math.round(r.width)+' '+(e.textContent||'').trim().slice(0,30))}}});return out.slice(0,6)}""")
            print(f,sw,r)
            await pg.close()
        await b.close()
asyncio.run(main())
