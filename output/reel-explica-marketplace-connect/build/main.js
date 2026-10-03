// Linha do tempo determinística: window.__seek(t) posiciona tudo no instante t.
gsap.defaults({ lazy: false, overwrite: false });

const TL = window.TL;
const S = id => TL.scenes.find(s => s.id === id);
const cue = (id, ph) => S(id).cues[ph];
const $ = (q, r = document) => r.querySelector(q);
const $$ = (q, r = document) => [...r.querySelectorAll(q)];
const tl = gsap.timeline({ paused: true });
const hooks = [];
const ease = p => 1 - Math.pow(1 - p, 3);
const clamp01 = v => Math.max(0, Math.min(1, v));

function blurIn(t, tg, o = {}) {
  tl.fromTo(tg,
    { autoAlpha: 0, filter: `blur(${o.b ?? 16}px)`, x: o.x ?? 70, y: o.y ?? 0, scale: o.s ?? 1 },
    { autoAlpha: 1, filter: "blur(0px)", x: 0, y: 0, scale: 1, duration: o.d ?? 0.5, ease: o.e ?? "expo.out", stagger: o.st ?? 0.07 }, t);
}
function pop(t, tg, o = {}) {
  tl.fromTo(tg,
    { autoAlpha: 0, scale: o.s ?? 0.86, y: o.y ?? 60, filter: `blur(${o.b ?? 10}px)` },
    { autoAlpha: 1, scale: 1, y: 0, filter: "blur(0px)", duration: o.d ?? 0.6, ease: o.e ?? "back.out(1.4)", stagger: o.st ?? 0.08 }, t);
}
function blurOut(t, tg, o = {}) {
  tl.to(tg, { autoAlpha: 0, filter: `blur(${o.b ?? 14}px)`, x: o.x ?? -50, duration: o.d ?? 0.2, ease: "power2.in" }, t);
}

// ---------- medidas ----------
function textWidth(el) {
  const r = document.createRange(); r.selectNodeContents(el);
  return r.getBoundingClientRect().width;
}
function fitAll() {
  $$(".fit").forEach(el => {
    const w = textWidth(el), max = 950;
    if (w > max) el.style.fontSize = (parseFloat(getComputedStyle(el).fontSize) * max / w) + "px";
  });
  $$(".fith").forEach(el => {
    const w = Math.max(...$$(".ln", el).map(textWidth)), max = 930;
    if (w > max) el.style.fontSize = (parseFloat(getComputedStyle(el).fontSize) * max / w) + "px";
  });
  $$(".inter .big").forEach(el => {
    el.style.fontSize = "300px";
    const w = el.offsetWidth, fs = Math.min(300, 300 * 930 / w);
    el.style.fontSize = fs + "px";
    el.style.left = ((1080 - el.offsetWidth) / 2) + "px";
    el.style.top = ((1920 - el.offsetHeight) / 2 - 40) + "px";
  });
}

// ---------- montagem de elementos repetidos ----------
const TABS = [
  ["ML", "#ffe600", "#2d3277", "Mercado Livre", "Vendas de hoje"],
  ["S", "#ee4d2d", "#fff", "Shopee", "Pedidos a enviar"],
  ["TT", "#111", "#fff", "TikTok Shop", "Estoque"],
  ["a", "#232f3e", "#ff9900", "Amazon", "Preços"],
  ["M", "#0086ff", "#fff", "Magalu", "Perguntas"],
  ["SH", "#000", "#fff", "Shein", "Anúncios"],
  ["B", "#2bb24c", "#fff", "Bling", "Notas fiscais"],
  ["O", "#1d4ed8", "#fff", "Olist", "Pedidos"],
];
function buildDeck() {
  const deck = $("#deck");
  TABS.forEach((t, i) => {
    const d = document.createElement("div");
    d.className = "card tab";
    d.style.left = (i % 2 ? 50 : 10) + "px";
    d.style.top = (i * 80) + "px";
    d.style.width = "700px";
    d.innerHTML = `<div class="fav" style="background:${t[1]};color:${t[2]}">${t[0]}</div>
      <div class="tt"><b>${t[3]}</b><span>${t[4]}</span></div><div class="x"></div>`;
    deck.appendChild(d);
  });
}
const STORES = [
  ["ML", "#ffe600", "#2d3277", "Mercado Livre"],
  ["S", "#ee4d2d", "#fff", "Shopee"],
  ["TT", "#111", "#fff", "TikTok Shop"],
  ["a", "#232f3e", "#ff9900", "Amazon"],
  ["M", "#0086ff", "#fff", "Magalu"],
  ["B", "#2bb24c", "#fff", "Bling"],
];
const SVGNS = "http://www.w3.org/2000/svg";
function svgEl(tag, attrs) { const e = document.createElementNS(SVGNS, tag); for (const k in attrs) e.setAttribute(k, attrs[k]); return e; }
function buildStores() {
  const box = $("#stores"), svg = $("#s2svg");
  const paths = [], dots = [];
  const mk = d => {
    const p = svgEl("path", { d, fill: "none", stroke: "#e0a100", "stroke-width": 4, "stroke-linecap": "round", opacity: 0.9 });
    svg.appendChild(p); paths.push(p);
    const ds = [0, 1].map(() => { const c = svgEl("circle", { r: 8, fill: "#f5c400", stroke: "#fff", "stroke-width": 3, opacity: 0 }); svg.appendChild(c); return c; });
    dots.push(ds);
    return p;
  };
  mk("M380 780 C380 832 540 812 540 862");
  STORES.forEach((s, i) => {
    const cx = 120 + i * 168;
    mk(`M540 1012 C540 1070 ${cx} 1062 ${cx} 1120`);
    const d = document.createElement("div");
    d.className = "st";
    d.style.cssText = `position:absolute;left:${cx - 85}px;top:1120px;width:170px;text-align:center`;
    d.innerHTML = `<div class="card" style="position:relative;margin:0 auto;width:96px;height:96px;border-radius:26px;display:grid;place-items:center">
        <div class="fav" style="width:66px;height:66px;border-radius:18px;font-size:24px;background:${s[1]};color:${s[2]}">${s[0]}</div>
        <div class="stok" style="position:absolute;right:-10px;top:-10px;width:34px;height:34px;border-radius:50%;background:#16a34a;color:#fff;display:grid;place-items:center;font-size:19px;font-weight:900;border:3px solid #fff">✓</div>
      </div><div style="margin-top:12px;font-size:21px;font-weight:700;letter-spacing:-.02em;color:#3d3d38">${s[3]}</div>`;
    box.appendChild(d);
  });
  return { paths, dots };
}

// ---------- cena a cena ----------
function sceneFrames() {
  TL.scenes.forEach((s, i) => {
    const node = document.getElementById(s.id);
    if (i === 0) gsap.set(node, { visibility: "visible" });
    else tl.set(node, { visibility: "visible" }, s.start);
    if (i < TL.scenes.length - 1) tl.set(node, { visibility: "hidden" }, s.start + s.dur);
    const cam = $(".cam", node);
    if (cam) {
      tl.fromTo(cam, { scale: 1 }, { scale: 1.035, duration: s.dur, ease: "none" }, s.start);
      if (i < TL.scenes.length - 1) blurOut(s.start + s.dur - 0.2, cam, { x: -40, b: 18, d: 0.2 });
    }
    if (s.kind === "inter") {
      const big = $(".big", node);
      tl.fromTo(big, { autoAlpha: 0, scale: 1.25, filter: "blur(26px)" },
        { autoAlpha: 1, scale: 1, filter: "blur(0px)", duration: 0.22, ease: "expo.out" }, s.start);
      tl.to(big, { scale: 1.06, duration: s.dur - 0.22, ease: "none" }, s.start + 0.22);
      blurIn(s.start, $$(".hdr, .foot", node), { x: 0, b: 8, d: 0.3 });
    }
  });
  // grade de pontos andando devagar
  const grids = $$(".grid");
  hooks.push(t => { const x = (t * 9) % 36, y = (-t * 6) % 36; grids.forEach(g => g.style.transform = `translate(${x}px,${y}px)`); });
}

function s0() {
  const st = S("s0").start;
  blurIn(st + 0.12, "#s0a", { x: 0, y: 30, b: 24, s: 1.08 });
  blurIn(st + 0.45, "#s0b", { x: 0, y: 30, b: 24, s: 1.08 });
  tl.fromTo("#s0bar", { scaleX: 0, transformOrigin: "left center" }, { scaleX: 1, duration: 0.3, ease: "power3.inOut" }, cue("s0", "E se ela") - 0.2);
  tl.to(["#s0b", "#s0bar"], { autoAlpha: 0, filter: "blur(16px)", y: -30, duration: 0.22, ease: "power2.in" }, cue("s0", "E se ela") + 0.2);
  blurIn(cue("s0", "operasse") - 0.12, "#s0c", { x: 0, s: 1.3, b: 30, d: 0.45 });
  blurIn(cue("s0", "operasse") + 0.3, "#s0d", { x: 0, y: 30, b: 24 });
}

function s1() {
  const s = S("s1"), st = s.start;
  blurIn(st + 0.05, $$("#s1 .lbl"), { d: 0.4 });
  blurIn(st + 0.1, $$("#s1 .h1 .ln"), { st: 0.09 });
  tl.fromTo("#deck", { rotationY: -20, rotationX: 10, transformPerspective: 1600 }, { rotationY: -8, rotationX: 5, duration: s.dur, ease: "none" }, st);
  const names = ["Mercado Livre", "Shopee", "TikTok Shop", "Amazon"];
  $$("#deck .tab").forEach((el, i) => {
    const t = i < 4 ? cue("s1", names[i]) - 0.12 : cue("s1", "Amazon") + 0.28 + (i - 4) * 0.16;
    tl.fromTo(el, { autoAlpha: 0, x: 260, filter: "blur(14px)", rotation: 5 },
      { autoAlpha: 1, x: 0, filter: "blur(0px)", rotation: 0, duration: 0.45, ease: "expo.out" }, t);
  });
  const tc = cue("s1", "e quando vê") - 0.25;
  tl.to("#deck", { scale: 0.9, opacity: 0.35, filter: "blur(5px)", duration: 0.5, ease: "power2.out" }, tc);
  pop(tc + 0.05, "#clock");
  const t0 = tc + 0.2, t1 = cue("s1", "meio-dia") + 0.1;
  const num = $("#clockN");
  hooks.push(t => {
    const m = Math.round(480 + 240 * ease(clamp01((t - t0) / (t1 - t0))));
    num.textContent = String(Math.floor(m / 60)).padStart(2, "0") + ":" + String(m % 60).padStart(2, "0");
    num.style.color = t >= t1 ? "#dc2626" : "#0b0b0c";
  });
  tl.fromTo("#clockB", { scaleX: 0.03 }, { scaleX: 1, duration: t1 - t0, ease: "power3.out" }, t0);
}

function s2(geo) {
  const s = S("s2"), st = s.start;
  blurIn(st + 0.05, $$("#s2 .lbl"), { d: 0.4 });
  blurIn(st + 0.1, $$("#s2 .h1 .ln"), { st: 0.09 });
  pop(cue("s2", "Marketplace Connect") + 0.05, "#nB");
  pop(cue("s2", "o Claude") - 0.1, "#nA");
  const draw = (p, t, d = 0.45) => {
    const L = p.getTotalLength();
    p.style.strokeDasharray = L;
    tl.fromTo(p, { strokeDashoffset: L }, { strokeDashoffset: 0, duration: d, ease: "power2.inOut" }, t);
  };
  const tAB = cue("s2", "ChatGPT") + 0.1;
  draw(geo.paths[0], tAB, 0.35);
  const tSt = cue("s2", "direto nas suas contas") - 0.1;
  pop(tSt, $$("#stores .st"), { st: 0.07, y: 40 });
  geo.paths.slice(1).forEach((p, i) => draw(p, tSt + 0.1 + i * 0.05, 0.45));
  geo.paths.forEach((p, i) => {
    const L = p.getTotalLength(), start = i === 0 ? tAB + 0.3 : tSt + 0.45, period = 1.1;
    hooks.push(t => geo.dots[i].forEach((c, k) => {
      if (t < start) { c.setAttribute("opacity", 0); return; }
      const ph = ((t - start) / period + k * 0.5) % 1, pt = p.getPointAtLength(ph * L);
      c.setAttribute("cx", pt.x); c.setAttribute("cy", pt.y);
      c.setAttribute("opacity", Math.min(1, (t - start) * 4) * Math.sin(Math.PI * ph));
    }));
  });
  const tc = cue("s2", "Um clique");
  const btn = $("#nBbtn");
  btn.style.transform = "none"; gsap.set(btn, { yPercent: -50 });
  tl.to(btn, { scale: 0.88, duration: 0.08, yoyo: true, repeat: 1, ease: "power1.inOut" }, tc - 0.05);
  hooks.push(t => { const on = t >= tc + 0.05; btn.textContent = on ? "✓ Autorizado" : "Autorizar"; btn.style.background = on ? "#16a34a" : "#0b0b0c"; });
  pop(tc + 0.15, $$("#stores .stok"), { st: 0.07, s: 0.3, y: 0, e: "back.out(2.4)", d: 0.4 });
  blurIn(tc - 0.1, "#s2sub", { d: 0.45 });
}

function s3() {
  const s = S("s3"), st = s.start;
  blurIn(st + 0.05, $$("#s3 .lbl"), { d: 0.4 });
  blurIn(st + 0.1, $$("#s3 .h1 .ln"), { st: 0.08 });
  pop(st + 0.12, "#chat", { y: 90 });
  tl.fromTo("#chat", { rotationX: 12, rotationY: -6, transformPerspective: 1800 }, { rotationX: 3, rotationY: -2, duration: s.dur, ease: "none" }, st);
  const bub = $("#bub"), txt = "Quais anúncios estão prestes a ficar sem estoque?", t0 = st + 0.4, cps = 42;
  hooks.push(t => {
    const n = Math.max(0, Math.min(txt.length, Math.floor((t - t0) * cps)));
    bub.textContent = txt.slice(0, n);
    bub.classList.toggle("typing", n < txt.length);
  });
  const tS = cue("s3", "e ele responde") - 0.15;
  blurIn(tS, "#stat", { x: 30, d: 0.35 });
  const spin = $("#spin"), tA = cue("s3", "dado real") - 0.3;
  hooks.push(t => { spin.style.transform = `rotate(${t * 520}deg)`; spin.style.opacity = t > tA + 0.3 ? 0.35 : 1; });
  blurIn(tA, "#ans", { x: 30, y: 10, d: 0.45 });
  blurIn(cue("s3", "sua conta") - 0.1, $$("#rows .row"), { x: 40, st: 0.13 });
  blurIn(cue("s3", "sua conta") + 0.3, "#s3note", { x: 0, d: 0.4 });
}

function s4() {
  const s = S("s4"), st = s.start;
  blurIn(st + 0.05, $$("#s4 .lbl"), { d: 0.4 });
  blurIn(st + 0.1, $$("#s4 .h1 .ln"), { st: 0.09 });
  pop(st + 0.4, $$("#mini span"), { st: 0.1, y: 20, s: 0.8 });
  pop(cue("s4", "ele prepara") - 0.45, "#appr", { y: 90 });
  tl.fromTo("#appr", { rotationX: 10, rotationY: 6, transformPerspective: 1800 }, { rotationX: 3, rotationY: 1, duration: s.dur, ease: "none" }, st);
  const tc = cue("s4", "você aprova");
  gsap.set("#bDone", { autoAlpha: 0 });
  gsap.set("#btOk", { autoAlpha: 0 });
  gsap.set("#cursor", { x: 840, y: 1330, autoAlpha: 0 });
  tl.to("#cursor", { autoAlpha: 1, duration: 0.2 }, tc - 0.95);
  tl.to("#cursor", { x: 60 + 266 + 150, y: 640 + 362 + 34, duration: 0.75, ease: "power3.inOut" }, tc - 0.9);
  tl.to("#cursor", { scale: 0.8, duration: 0.07, yoyo: true, repeat: 1 }, tc - 0.08);
  tl.to("#btYes", { scale: 0.94, duration: 0.07, yoyo: true, repeat: 1 }, tc - 0.08);
  tl.fromTo("#btOk", { autoAlpha: 0, scale: 0.8 }, { autoAlpha: 1, scale: 1, duration: 0.3, ease: "back.out(2)" }, tc + 0.02);
  tl.to("#bWait", { autoAlpha: 0, filter: "blur(8px)", duration: 0.15 }, tc + 0.1);
  tl.fromTo("#bDone", { autoAlpha: 0, x: 30, filter: "blur(8px)" }, { autoAlpha: 1, x: 0, filter: "blur(0px)", duration: 0.35, ease: "expo.out" }, tc + 0.2);
  tl.to("#cursor", { autoAlpha: 0, duration: 0.25 }, tc + 0.7);
  const te = cue("s4", "ele executa");
  pop(te - 0.35, "#log", { y: 70 });
  blurIn(te - 0.1, $$("#log .li"), { x: 40, st: 0.15 });
}

function s6() {
  const s = S("s6"), st = s.start;
  blurIn(st + 0.05, $$("#s6 .lbl"), { d: 0.4 });
  blurIn(st + 0.1, $$("#s6 .h1 .ln"), { st: 0.09 });
  pop(st + 0.3, $$("#s6 .step"), { st: 0.2, y: 70 });
  pop(cue("s6", "E no Claude") - 0.1, "#free", { y: 70 });
}

function s7() {
  const s = S("s7"), st = s.start;
  blurIn(st + 0.05, "#e1", { x: 0, s: 1.12, b: 26 });
  blurIn(st + 0.22, "#e2", { x: 0, s: 1.2, b: 30 });
  blurIn(st + 0.5, "#e3", { x: 0, y: 20 });
  const e4 = $("#e4"); e4.style.transform = "none"; gsap.set(e4, { xPercent: -50 });
  pop(cue("s7", "CONNECT") - 0.3, e4, { s: 0.7, y: 40 });
  blurIn(cue("s7", "o link") - 0.2, "#e5", { x: 0, y: 16 });
  blurIn(cue("s7", "o link") + 0.4, "#e6", { x: 0, y: 16 });
  tl.to(e4, { scale: 1.06, duration: 0.35, yoyo: true, repeat: 3, ease: "sine.inOut" }, cue("s7", "o link") + 0.6);
}

function cta() {
  const c = $("#cta"); c.style.transform = "none"; gsap.set(c, { xPercent: -50 });
  const a = S("s1").start + 0.6, b = S("s7").start - 0.15;
  tl.fromTo(c, { autoAlpha: 0, y: 40, filter: "blur(10px)" }, { autoAlpha: 1, y: 0, filter: "blur(0px)", duration: 0.5, ease: "expo.out" }, a);
  TL.scenes.filter(s => s.kind === "inter").forEach(s => tl.to(c, { scale: 1.07, duration: 0.12, yoyo: true, repeat: 1 }, s.start));
  tl.to(c, { autoAlpha: 0, y: 30, duration: 0.2 }, b);
}

async function build() {
  await document.fonts.ready;
  fitAll();
  buildDeck();
  const geo = buildStores();
  sceneFrames();
  s0(); s1(); s2(geo); s3(); s4(); s6(); s7(); cta();
  window.__seek(0);
  window.__ready = true;
}
window.__seek = t => { tl.seek(t, false); hooks.forEach(h => h(t)); };
build();
