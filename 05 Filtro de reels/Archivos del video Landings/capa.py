import sys,urllib.parse,pathlib
from playwright.sync_api import sync_playwright
h=pathlib.Path('plantilla-vertical.html').resolve().as_uri()
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={'width':1080,'height':1920})
    pg.goto(h+'?v=3&t='+urllib.parse.quote(sys.argv[1])); pg.wait_for_timeout(600)
    pg.screenshot(path='capa.png')
    pg.set_content('<body style="margin:0;background:#000"><div style="width:740px;height:1316px;border-radius:28px;background:#fff"></div>'); pg.screenshot(path='mascara.png',clip={'x':0,'y':0,'width':740,'height':1316})
    b.close()
