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
  tl.fromTo(tg,
    { autoAlpha: 0, filter: `blur(${o.b ?? 16}px)`, x: o.x ?? 70, y: o.y ?? 0, scale: o.s ?? 1 },
    { autoAlpha: 1, filter: "blur(0px)", x: 0, y: 0, scale: 1, duration: o.d ?? 0.5, ease: o.e ?? "expo.out", stagger: o.st ?? 0.07 }, t);
}
function pop(t, tg, o = {}) {
  tl.fromTo(tg,
    { autoAlpha: 0, scale: o.s ?? 0.86, y: o.y ?? 60, filter: `blur(${o.b ?? 10}px)` },
    { autoAlpha: 1, scale: 1, y: 0, filter: "blur(0px)", duration: o.d ?? 0.6, ease: o.e ?? "back.out(1.4)", stagger: o.st ?? 0.08 }, t);
}
function out(t, tg, o = {}) {
  tl.to(tg, { autoAlpha: 0, filter: `blur(${o.b ?? 14}px)`, y: o.y ?? -30, x: o.x ?? 0, duration: o.d ?? 0.22, ease: "power2.in" }, t);
}
function typeText(el, text, a, b) {
  hooks.push(t => {
    const n = Math.round(clamp01((t - a) / (b - a)) * text.length);
    el.textContent = text.slice(0, n);
    el.parentElement.classList.toggle("typing", t > a - 0.4 && t < b + 0.3);
  });
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
  $$(".kwbig").forEach(el => gsap.set(el, { xPercent: -50 }));
}

function sceneFrames() {
  TL.scenes.forEach((s, i) => {
    const node = document.getElementById(s.id);
    if (i === 0) gsap.set(node, { visibility: "visible" });
    else tl.set(node, { visibility: "visible" }, s.start);
    if (i < TL.scenes.length - 1) tl.set(node, { visibility: "hidden" }, s.start + s.dur);
    const cam = $(".cam", node);
    if (cam) {
      tl.fromTo(cam, { scale: 1 }, { scale: 1.035, duration: s.dur, ease: "none" }, s.start);
      if (i < TL.scenes.length - 1) out(s.start + s.dur - 0.2, cam, { x: -40, y: 0, b: 18, d: 0.2 });
    }
    if (s.kind === "inter") {
      const big = $(".big", node);
      tl.fromTo(big, { autoAlpha: 0, scale: 1.25, filter: "blur(26px)" },
        { autoAlpha: 1, scale: 1, filter: "blur(0px)", duration: 0.22, ease: "expo.out" }, s.start);
      tl.to(big, { scale: 1.06, duration: s.dur - 0.22, ease: "none" }, s.start + 0.22);
      blurIn(s.start, $$(".hdr, .foot", node), { x: 0, b: 8, d: 0.3 });
    }
  });
  const grids = $$(".grid");
  hooks.push(t => { const x = (t * 9) % 36, y = (-t * 6) % 36; grids.forEach(g => g.style.transform = `translate(${x}px,${y}px)`); });
}

// cabeçalho, rótulo e título de cada cena clara
function intro(id) {
  const st = S(id).start;
  blurIn(st + 0.02, $$(`#${id} .hdr`), { x: 0, b: 8, d: 0.3 });
  blurIn(st + 0.05, $$(`#${id} .lbl`), { d: 0.4 });
  blurIn(st + 0.1, $$(`#${id} .h1 .ln`), { st: 0.09 });
}

function s0() {
  const st = S("s0").start;
  gsap.set("#s0 .hdr", { autoAlpha: 1 });
  blurIn(st + 0.05, "#s0a", { x: 0, y: 30, b: 24, s: 1.08, d: 0.4 });
  pop(st + 0.12, "#ord", { y: 80, d: 0.5 });
  pop(st + 0.2, "#frm", { y: 80, d: 0.5 });
  const tc = cue("s0", "copia");
  pop(tc - 0.1, "#k1", { s: 0.5, y: 0, d: 0.35, e: "back.out(2.2)" });
  tl.to("#k1", { y: 10, duration: 0.08, yoyo: true, repeat: 1 }, tc + 0.25);
  tl.fromTo("#ord .ln2:first-of-type", { backgroundColor: "rgba(250,204,21,0)" }, { backgroundColor: "rgba(250,204,21,.35)", duration: 0.2 }, tc + 0.25);
  blurIn(cue("s0", "pedido") - 0.08, "#s0b", { x: 0, y: 30, b: 24, s: 1.15, d: 0.35 });
  const tv = cue("s0", "marketplace");
  pop(tv - 0.1, "#k2", { s: 0.5, y: 0, d: 0.35, e: "back.out(2.2)" });
  tl.to("#k2", { y: 10, duration: 0.08, yoyo: true, repeat: 1 }, tv + 0.2);
  typeText($("#f1t"), "copiando do pedido #20000123", tv + 0.25, tv + 1.6);
  const te = cue("s0", "emitir");
  out(te - 0.15, ["#s0a", "#s0b"], { y: -30, b: 18 });
  blurIn(te - 0.02, "#s0c", { x: 0, y: 30, b: 24, s: 1.08, d: 0.35 });
  blurIn(cue("s0", "nota fiscal") - 0.05, "#s0d", { x: 0, y: 30, b: 24, s: 1.2, d: 0.4 });
  tl.to("#frm", { x: 8, duration: 0.05, yoyo: true, repeat: 5 }, cue("s0", "nota fiscal") + 0.3);
}

function s1() {
  intro("s1");
  pop(cue("s1", "Emissor") - 0.25, "#brand", { y: 70 });
  const td = cue("s1", "direto");
  pop(td - 0.35, "#nd1", { y: 50 });
  tl.fromTo("#ar1 i", { scaleX: 0 }, { scaleX: 1, duration: 0.3, ease: "power2.out" }, td - 0.05);
  tl.fromTo("#ar1", { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.1 }, td - 0.05);
  const ts = cue("s1", "SEFAZ");
  pop(ts - 0.15, "#nd2", { y: 50, s: 0.7 });
  tl.fromTo("#ar2 i", { scaleX: 0 }, { scaleX: 1, duration: 0.3, ease: "power2.out" }, ts + 0.35);
  tl.fromTo("#ar2", { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.1 }, ts + 0.35);
  pop(ts + 0.6, "#nd3", { y: 50, s: 0.7, e: "back.out(2)" });
  pop(cue("s1", "certificado") - 0.25, "#cert", { y: 70 });
  tl.fromTo("#certS .hl", { backgroundColor: "rgba(255,243,176,0)" }, { backgroundColor: "rgba(255,243,176,1)", duration: 0.25 }, cue("s1", "sua empresa") - 0.05);
  blurIn(cue("s1", "sua empresa") + 0.2, "#s1 .note", { x: 0, y: 16 });
}

function s2() {
  intro("s2");
  const st = S("s2").start;
  pop(st + 0.45, "#prev", { y: 90 });
  blurIn(st + 0.6, $$("#prev .prow"), { x: 30, st: 0.06, d: 0.4 });
  gsap.set("#prev .ck", { scale: 0 });
  tl.to("#r0 .ck", { scale: 1, duration: 0.3, ease: "back.out(2.5)" }, cue("s2", "prévia"));
  [["imposto", "#r1"], ["frete", "#r2"], ["desconto", "#r3"]].forEach(([ph, r]) => {
    const t = cue("s2", ph);
    tl.to(`${r} .glow`, { opacity: 1, duration: 0.15 }, t - 0.05);
    tl.to(`${r} .ck`, { scale: 1, duration: 0.3, ease: "back.out(2.5)" }, t);
    tl.to(`${r} .glow`, { opacity: 0, duration: 0.4 }, t + 0.5);
  });
  const tg = cue("s2", "sem gastar");
  tl.fromTo("#stamp", { autoAlpha: 0, scale: 1.8, rotate: -14 }, { autoAlpha: 1, scale: 1, rotate: -5, duration: 0.3, ease: "power4.in" }, tg - 0.1);
  tl.to("#prev", { y: 6, duration: 0.06, yoyo: true, repeat: 1 }, tg + 0.2);
  blurIn(tg + 0.35, "#s2 .note", { x: 0, y: 16 });
}

function s3() {
  intro("s3");
  const st = S("s3").start;
  pop(cue("s3", "intermediador") + 0.35, "#grp", { y: 80 });
  ["Mercado", "Shopee", "Amazon", "Magalu", "SHEIN", "TikTok"].forEach((ph, i) => {
    const t = cue("s3", ph);
    pop(t - 0.12, `#m${i}`, { y: 50, s: 0.75, d: 0.45, e: "back.out(1.8)" });
    tl.fromTo(`#m${i} .ck`, { scale: 0 }, { scale: 1, duration: 0.3, ease: "back.out(2.5)" }, t + 0.25);
  });
  tl.to("#grp .v span", { color: "#16a34a", duration: 0.2 }, cue("s3", "TikTok") + 0.4);
}

function s4() {
  intro("s4");
  const st = S("s4").start;
  pop(st + 0.3, "#nfe", { y: 70 });
  pop(cue("s4", "XML") - 0.15, "#xml", { y: 60 });
  pop(cue("s4", "DANFE") - 0.15, "#lab", { y: 80, s: 0.8 });
  const td = cue("s4", "dez");
  blurIn(td - 0.1, "#dim", { x: 0, y: 20 });
  pop(td + 0.1, "#box", { y: 120, s: 0.9 });
  const tc = cue("s4", "colar");
  out(tc - 0.1, "#dim", { y: 20 });
  tl.to("#lab", { x: -450, y: 270, scale: 0.6, rotate: -4, duration: 0.55, ease: "power3.inOut" }, tc - 0.1);
  tl.to("#box", { y: 8, duration: 0.07, yoyo: true, repeat: 1 }, tc + 0.45);
}

function s5() {
  intro("s5");
  const st = S("s5").start;
  pop(st + 0.25, "#chat", { y: 90 });
  typeText($("#bubT"), "Emite a nota do pedido ML-2000012345678", st + 0.55, st + 1.55);
  gsap.set(["#bub"], { autoAlpha: 0 });
  tl.to("#bub", { autoAlpha: 1, duration: 0.1 }, st + 0.45);
  tl.to("#aiC", { backgroundColor: "#0b1640", color: "#ffffff", duration: 0.2 }, cue("s5", "Claude") - 0.05);
  tl.to("#aiG", { backgroundColor: "#0b1640", color: "#ffffff", duration: 0.2 }, cue("s5", "ChatGPT") - 0.05);
  blurIn(st + 1.75, "#tool", { x: 20, d: 0.3 });
  tl.fromTo("#spin", { rotate: 0 }, { rotate: 720, duration: 1.4, ease: "none" }, st + 1.75);
  tl.to("#spin", { autoAlpha: 0, duration: 0.1 }, st + 3.1);
  pop(st + 3.1, "#ans", { y: 30, s: 0.95 });
}

function s6() {
  const st = S("s6").start;
  blurIn(st + 0.02, $$("#s6 .hdr"), { x: 0, b: 8, d: 0.3 });
  blurIn(st + 0.05, $$("#s6 .lbl"), { d: 0.4 });
  blurIn(st + 0.1, $$("#s6 .h1 .ln"), { st: 0.12 });
  pop(st + 0.35, "#sw", { y: 60 });
  gsap.set("#opA", { color: "#0b1640" });
  blurIn(cue("s6", "homologação") - 0.1, "#envA", { x: 30 });
  const tl0 = cue("s6", "liberar");
  // cursor entra pela direita e clica em Produção
  gsap.set("#cursor", { x: 1000, y: 1250, autoAlpha: 0 });
  tl.to("#cursor", { autoAlpha: 1, duration: 0.2 }, tl0 - 0.9);
  tl.to("#cursor", { x: 110 + 640, y: 830 + 70, duration: 0.65, ease: "power3.inOut" }, tl0 - 0.9);
  tl.to("#cursor", { scale: 0.8, duration: 0.07, yoyo: true, repeat: 1 }, tl0 - 0.15);
  tl.to("#knob", { x: 416, backgroundColor: "#22c55e", duration: 0.35, ease: "power3.inOut" }, tl0 - 0.08);
  tl.to("#opA", { color: "rgba(255,255,255,.75)", duration: 0.2 }, tl0 - 0.05);
  tl.to("#opB", { color: "#0b1640", duration: 0.2 }, tl0 + 0.05);
  out(tl0 + 0.05, "#envA", { y: -10, d: 0.15 });
  blurIn(tl0 + 0.15, "#envB", { x: 30 });
  tl.to("#cursor", { autoAlpha: 0, duration: 0.25 }, tl0 + 0.6);
}

function s7() {
  const st = S("s7").start;
  gsap.set("#s7 .hdr", { autoAlpha: 1 });
  blurIn(st + 0.05, "#e1", { x: 0, s: 1.12, b: 26 });
  const tn = cue("s7", "NOTA");
  tl.fromTo("#e2", { autoAlpha: 0, scale: 0.6, y: 40, filter: "blur(16px)" },
    { autoAlpha: 1, scale: 1, y: 0, filter: "blur(0px)", duration: 0.45, ease: "back.out(1.8)" }, tn - 0.15);
  blurIn(tn + 0.35, "#e3", { x: 0, y: 16 });
  const tk = cue("s7", "link");
  pop(tk + 0.1, "#e4", { y: 40 });
  blurIn(tk + 0.4, "#e5", { x: 0, y: 16 });
  tl.to("#e2", { scale: 1.05, duration: 0.35, yoyo: true, repeat: 3, ease: "sine.inOut" }, tk + 0.6);
}

function cta() {
  const c = $("#cta"); c.style.transform = "none"; gsap.set(c, { xPercent: -50 });
  const a = S("s1").start + 0.6, b = S("s7").start - 0.15;
  tl.fromTo(c, { autoAlpha: 0, y: 40, filter: "blur(10px)" }, { autoAlpha: 1, y: 0, filter: "blur(0px)", duration: 0.5, ease: "expo.out" }, a);
  TL.scenes.filter(s => s.kind === "inter" && s.start > a).forEach(s => {
    tl.to(c, { autoAlpha: 0, duration: 0.08 }, s.start);
    tl.to(c, { autoAlpha: 1, duration: 0.15 }, s.start + s.dur);
  });
  tl.to(c, { autoAlpha: 0, y: 30, duration: 0.2 }, b);
}

async function build() {
  await document.fonts.ready;
  await Promise.all([...document.images].map(i => i.complete ? 0 : new Promise(r => { i.onload = r; i.onerror = r; })));
  fitAll();
  sceneFrames();
  s0(); s1(); s2(); s3(); s4(); s5(); s6(); s7(); cta();
  window.__seek(0);
  window.__ready = true;
}
window.__seek = t => { tl.seek(t, false); hooks.forEach(h => h(t)); };
build();
