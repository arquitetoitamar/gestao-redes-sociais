import sys, pathlib
from playwright.sync_api import sync_playwright
src = pathlib.Path(sys.argv[1]).resolve(); out = sys.argv[2]
w, h = int(sys.argv[3]), int(sys.argv[4])
with sync_playwright() as p:
    b = p.chromium.launch(channel="chrome")
    pg = b.new_page(viewport={"width": w, "height": h}, device_scale_factor=1)
    pg.goto(src.as_uri()); pg.wait_for_load_state("networkidle"); pg.wait_for_timeout(600)
    # report overflow of body content
    print(pg.evaluate("(()=>{const r=[...document.querySelectorAll('.wrap > *')].map(e=>e.getBoundingClientRect().bottom);return Math.max(...r)})()"))
    pg.screenshot(path=out, type="jpeg", quality=93)
    b.close()
