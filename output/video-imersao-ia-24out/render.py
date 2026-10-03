"""Renderiza build/index.html quadro a quadro (Chromium headless) em paralelo.
uso: python3 render.py [saida_frames] [--stills t1,t2,...]"""
import json, os, sys, math
from multiprocessing import Process
from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
URL = "file://" + os.path.join(HERE, "build", "index.html")
TL = json.load(open(os.path.join(HERE, "build", "timeline.json")))
FPS = TL["fps"]

def open_page(p):
    b = p.chromium.launch(args=["--disable-gpu-vsync", "--force-color-profile=srgb"])
    pg = b.new_page(viewport={"width": 1080, "height": 1920}, device_scale_factor=1)
    pg.goto(URL)
    pg.wait_for_function("window.__ready === true", timeout=30000)
    return b, pg

def worker(frames, outdir):
    with sync_playwright() as p:
        b, pg = open_page(p)
        for i in frames:
            pg.evaluate(f"window.__seek({i / FPS})")
            pg.screenshot(path=f"{outdir}/f{i:05d}.jpg", type="jpeg", quality=93)
        b.close()

if __name__ == "__main__":
    out = sys.argv[1]
    os.makedirs(out, exist_ok=True)
    if "--stills" in sys.argv:
        ts = [float(x) for x in sys.argv[sys.argv.index("--stills") + 1].split(",")]
        with sync_playwright() as p:
            b, pg = open_page(p)
            msgs = []
            pg.on("console", lambda m: msgs.append(m.text))
            for t in ts:
                pg.evaluate(f"window.__seek({t})")
                pg.screenshot(path=f"{out}/still_{t:06.2f}.jpg", type="jpeg", quality=85)
            b.close()
        sys.exit()
    n = int(math.ceil(TL["total"] * FPS))
    W = int(os.environ.get("WORKERS", 6))
    chunks = [list(range(n))[k::W] for k in range(W)]
    ps = [Process(target=worker, args=(c, out)) for c in chunks]
    [q.start() for q in ps]; [q.join() for q in ps]
    print("frames", n)
