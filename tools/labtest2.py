import asyncio,json,glob,subprocess,time
from playwright.async_api import async_playwright
import sys
R=sys.argv[1] if len(sys.argv)>1 else '.'
srv=subprocess.Popen(['python3','-m','http.server','8766'],cwd=R,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); time.sleep(1)
PAGES={'estrai':'lab-estrai.html','ottimizza':'lab-ottimizza.html','costi':'lab-costi.html','vuln':'lab-vulnerabilita.html','debug':'lab-debug.html'}
import os
CH=[json.load(open(f)) for f in glob.glob(R+'/lab/c*.json')]; CH.sort(key=lambda c:c['id'])
if os.environ.get('MINID'): CH=[c for c in CH if c['id']>=int(os.environ['MINID'])]
async def m():
  async with async_playwright() as p:
    b=await p.chromium.launch(); pg=await b.new_page(viewport={'width':1280,'height':1000}); err=[]; pg.on('pageerror',lambda e:err.append(str(e)))
    await pg.route('**/fonts.googleapis.com/**',lambda r:r.abort()); await pg.route('**/fonts.gstatic.com/**',lambda r:r.abort())
    fails=[]
    for c in CH:
        await pg.goto('http://localhost:8766/%s?x=%d#s%d'%(PAGES[c['mode']],c['id'],c['id']))
        sel={'estrai':'#ef','ottimizza':'#overif','costi':'#cok','vuln':'#vverif','debug':'#dverif'}[c['mode']]
        await pg.wait_for_selector(sel,timeout=8000)
        if c['mode']=='estrai':
            for i,f in enumerate(c['fields']):
                s='#f%d_%d'%(c['id'],i)
                if f['type']=='enum': await pg.select_option(s,f['ans'])
                else: await pg.fill(s,str(f['ans']))
            await pg.click('#ef .vbtn2'); ok=await pg.locator('#eout .win').count()
        elif c['mode']=='ottimizza':
            for i,x in enumerate(c['issues']):
                if x['ok']: await pg.check('#is%d input'%i)
            await pg.click('#overif'); ok='mancati' not in await pg.inner_text('#ofb')
        elif c['mode']=='costi':
            for li,oi in enumerate(c['bestsel']): await pg.check('input[name="lv%d"][value="%d"]'%(li,oi))
            await pg.click('#cok'); ok='raggiunto' in await pg.inner_text('#cfb')
        elif c['mode']=='vuln':
            for i,l in enumerate(c['lines']):
                if l['bad']: await pg.click('#vl%d'%i)
            await pg.click('#vverif'); ok='mancate' not in await pg.inner_text('#vfb')
        else:
            await pg.check('input[name="dbg"][value="%d"]'%c['c']); await pg.click('#dverif'); ok='Esatto' in await pg.inner_text('#dfb')
        if not ok: fails.append((c['id'],c['mode'],c['t']))
    await pg.goto('http://localhost:8766/azure-laboratorio.html'); await pg.wait_for_timeout(300)
    print('fails',fails[:10],len(fails)); print('hub', await pg.inner_text('#gxp'), await pg.inner_text('#gdone'), await pg.inner_text('#glv'), await pg.inner_text('#gbadges'))
    await pg.goto('http://localhost:8766/azure-laboratorio.html#s600'); await pg.wait_for_timeout(800); print('redirect ->', pg.url)
    await pg.goto('http://localhost:8766/lab-prova.html'); await pg.wait_for_timeout(800); print('prova textareas', await pg.locator('#stage textarea').count()); print('err',err[:3])
    await b.close()
asyncio.run(m()); srv.terminate()
