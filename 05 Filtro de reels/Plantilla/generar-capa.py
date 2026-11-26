import sys,urllib.parse,pathlib
from playwright.sync_api import sync_playwright
title=sys.argv[1]; out=sys.argv[2]
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={'width':1080,'height':1920})
    pg.goto(pathlib.Path(__file__).with_name('plantilla.html').resolve().as_uri()+'?v='+sys.argv[3]+'&t='+urllib.parse.quote(title)); pg.wait_for_timeout(400)
    # cut the hole in background so video shows through
    pg.screenshot(path=out,omit_background=True); b.close()
