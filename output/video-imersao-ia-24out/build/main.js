// Linha do tempo determinística: window.__seek(t) posiciona tudo no instante t.
gsap.defaults({ lazy: false, overwrite: false });
const TL = window.TL;
const S = id => TL.scenes.find(s => s.id === id);
const cue = (id, ph) => S(id).cues[ph];
const $ = (q, r = document) => r.querySelector(q);
const $$ = (q, r = document) => [...r.querySelectorAll(q)];
const tl = gsap.timeline({ paused: true });
const hooks = [];
const clamp01 = v => Math.max(0, Math.min(1, v));

function blurIn(t, tg, o = {}) {
  tl.fromTo(tg, { autoAlpha: 0, filter: `blur(${o.b ?? 16}px)`, x: o.x ?? 0, y: o.y ?? 40, scale: o.s ?? 1 },
    { autoAlpha: 1, filter: "blur(0px)", x: 0, y: 0, scale: 1, duration: o.d ?? 0.5, ease: o.e ?? "expo.out", stagger: o.st ?? 0.07 }, t);
}
function pop(t, tg, o = {}) {
  tl.fromTo(tg, { autoAlpha: 0, scale: o.s ?? 0.85, y: o.y ?? 50, filter: `blur(${o.b ?? 10}px)` },
    { autoAlpha: 1, scale: 1, y: 0, filter: "blur(0px)", duration: o.d ?? 0.55, ease: o.e ?? "back.out(1.5)", stagger: o.st ?? 0.08 }, t);
}
function center(sel) { $$(sel).forEach(e => { e.style.transform = "none"; gsap.set(e, { xPercent: -50 }); }); }
function textWidth(el) { const r = document.createRange(); r.selectNodeContents(el); return r.getBoundingClientRect().width; }
function fitAll() {
  $$(".fit").forEach(el => { const w = textWidth(el), max = 960; if (w > max) el.style.fontSize = (parseFloat(getComputedStyle(el).fontSize) * max / w) + "px"; });
}

// pessoa (quadros pré-carregados)
const FR = Array.from({ length: 216 }, (_, i) => { const im = new Image(); im.src = `../assets/itamar/f${String(i + 1).padStart(3, "0")}.jpg`; return im; });
function person(start) {
  const ctx = $("#cvIt").getContext("2d");
  hooks.push(t => {
    const i = Math.max(0, Math.min(FR.length - 1, Math.floor((t - start) * 30)));
    const k = 1.04 + 0.05 * clamp01((t - start) / 7);
    ctx.setTransform(k, 0, 0, k, -540 * (k - 1), -700 * (k - 1) + 170);
    ctx.fillStyle = '#061a4d'; ctx.fillRect(0, 0, 1080, 1920);
    ctx.drawImage(FR[i], 0, 0, 1080, 1920);
    ctx.setTransform(1, 0, 0, 1, 0, 0);
  });
}

function frames() {
  TL.scenes.forEach((s, i) => {
    const node = document.getElementById(s.id);
    if (i === 0) gsap.set(node, { visibility: "visible" }); else tl.set(node, { visibility: "visible" }, s.start);
    if (i < TL.scenes.length - 1) tl.set(node, { visibility: "hidden" }, s.start + s.dur);
    const cam = $(".cam", node);
    if (cam) {
      tl.fromTo(cam, { scale: 1 }, { scale: 1.04, duration: s.dur, ease: "none" }, s.start);
      if (i < TL.scenes.length - 1) tl.to(cam, { autoAlpha: 0, filter: "blur(18px)", scale: 1.1, duration: 0.18, ease: "power2.in" }, s.start + s.dur - 0.18);
    }
  });
  const dots = $$(".dots");
  hooks.push(t => dots.forEach(d => d.style.transform = `translate(${(t * 10) % 38}px, ${(-t * 6) % 38}px)`));
}

function build() {
  fitAll();
  center(".chip, .tiopsc, .warn, .cta, .br");
  frames();
  // S0
  blurIn(0.08, "#h1", { s: 1.15, b: 24, y: 0 });
  blurIn(cue("s0", "ouvir falar") - 0.1, "#h2", { s: 1.15, b: 24, y: 0 });
  blurIn(cue("s0", "inteligência") - 0.05, "#h3", { s: 1.35, b: 30, y: 0, d: 0.45 });
  tl.fromTo("#hbr", { scaleX: 0, autoAlpha: 0 }, { scaleX: 1, autoAlpha: 1, duration: 0.5, ease: "expo.out" }, cue("s0", "inteligência") + 0.3);
  // S1
  const s1 = S("s1").start;
  pop(s1 + 0.05, "#e0", { y: 20, s: 0.8 });
  blurIn(s1 + 0.12, ["#e1", "#e2"], { s: 1.12, b: 22, y: 0, st: 0.12 });
  pop(cue("s1", "vinte e quatro") + 0.05, "#p1");
  pop(cue("s1", "São Paulo") - 0.1, "#p2");
  pop(cue("s1", "criar o seu") - 0.1, "#ag", { y: 90 });
  tl.fromTo("#ag", { rotationX: 12, transformPerspective: 1600 }, { rotationX: 2, duration: 4, ease: "none" }, cue("s1", "criar o seu"));
  pop(cue("s1", "agente de IA") + 0.15, "#t1", { y: 20, s: 0.95 });
  pop(cue("s1", "trabalhar") + 0.05, "#t2", { y: 20, s: 0.95 });
  pop(cue("s1", "marketplace") - 0.25, "#t3", { y: 20, s: 0.95 });
  tl.fromTo(".live", { opacity: 1 }, { opacity: 0.45, duration: 0.5, yoyo: true, repeat: 7, ease: "sine.inOut" }, cue("s1", "criar o seu"));
  // S2
  const s2 = S("s2").start;
  blurIn(s2 + 0.05, "#n0", { s: 1.2, b: 24, y: 0 });
  tl.fromTo("#nul", { scaleX: 0 }, { scaleX: 1, duration: 0.45, ease: "expo.out" }, s2 + 0.3);
  pop(cue("s2", "criar seus") - 0.1, "#c1", { y: 60 });
  pop(cue("s2", "ver aplicações") - 0.1, "#c2", { y: 60 });
  pop(cue("s2", "descobrir") - 0.1, "#c3", { y: 60 });
  pop(cue("s2", "automatizar") - 0.15, "#c4", { y: 60 });
  // S3
  const s3 = S("s3").start;
  person(s3);
  pop(s3 + 0.1, "#i0", { y: 20, s: 0.8 });
  blurIn(cue("s3", "Itamar Rocha") - 0.15, "#i1", { x: -60, y: 0 });
  blurIn(cue("s3", "professor") - 0.1, "#i2", { x: -40, y: 0 });
  blurIn(cue("s3", "fundador da Tiops") - 0.05, "#i3", { x: -40, y: 0 });
  tl.to("#i0", { autoAlpha: 0, y: -20, duration: 0.2 }, cue("s3", "plataforma") - 0.35);
  pop(cue("s3", "plataforma") - 0.2, "#i4", { y: 40, s: 0.8 });
  // S4
  const s4 = S("s4").start;
  pop(s4 + 0.05, "#v0", { y: 20, s: 0.7, e: "back.out(2.2)" });
  tl.to("#v0", { scale: 1.06, duration: 0.35, yoyo: true, repeat: 7, ease: "sine.inOut" }, s4 + 0.6);
  blurIn(s4 + 0.15, "#v1", { s: 1.4, b: 30, y: 0, d: 0.5 });
  blurIn(s4 + 0.35, "#v2", { s: 1.15, b: 22, y: 0 });
  blurIn(s4 + 0.6, ["#v3", "#v4"], { y: 20, st: 0.12 });
  pop(cue("s4", "Clique") - 0.1, "#v5", { y: 40, s: 0.8 });
  tl.fromTo("#v6", { autoAlpha: 0, y: -20 }, { autoAlpha: 1, y: 0, duration: 0.3 }, cue("s4", "Saiba mais"));
  tl.to("#v6", { y: 26, duration: 0.3, yoyo: true, repeat: 9, ease: "sine.inOut" }, cue("s4", "Saiba mais") + 0.3);
}

window.__seek = t => { tl.seek(t, false); hooks.forEach(h => h(t)); };
Promise.all([document.fonts.ready, ...FR.map(im => im.decode().catch(() => {}))]).then(() => { build(); window.__seek(0); window.__ready = true; });
