// Linha do tempo determinística: window.__seek(t) desenha o quadro do instante t.
const SC = [
  ["hook", 0.0, 2.5], ["b1", 2.5, 1.0], ["b2", 3.5, 0.7], ["b3", 4.2, 1.8], ["b4", 6.0, 1.0],
  ["b5", 7.0, 1.0], ["b6", 8.0, 1.5], ["c1", 9.5, 0.8], ["d", 10.3, 3.5], ["e", 13.8, 2.5],
];
window.TOTAL = 16.3;
const $ = (q, r = document) => r.querySelector(q);
const $$ = (q, r = document) => [...r.querySelectorAll(q)];
const clamp = (v, a = 0, b = 1) => Math.max(a, Math.min(b, v));
const ease = p => p < 0.5 ? 4 * p * p * p : 1 - Math.pow(-2 * p + 2, 3) / 2;
const hooks = [];

// ---------- pessoa (quadros pré-carregados, desenhados no canvas)
function seq(dir, n) { return Array.from({ length: n }, (_, i) => { const im = new Image(); im.src = `../assets/${dir}/f${String(i + 1).padStart(3, "0")}.jpg`; return im; }); }
const HOOK = seq("hook", 75), CTA = seq("cta", 75);
function person(cv, frames, start) {
  const ctx = $(cv).getContext("2d");
  hooks.push(t => {
    const i = Math.max(0, Math.min(frames.length - 1, Math.floor((t - start) * 30)));
    const k = 1 + 0.03 * clamp((t - start) / 2.5);           // leve zoom
    ctx.setTransform(k, 0, 0, k, -540 * (k - 1), -800 * (k - 1));
    ctx.drawImage(frames[i], 0, 0, 1080, 1920);
  });
}

// ---------- tela filmada: tremida de mão + leve inclinação + aproximação no foco
function noise(t, s) { return Math.sin(t * 1.7 + s) * 0.6 + Math.sin(t * 3.1 + s * 2) * 0.3 + Math.sin(t * 5.3 + s * 3) * 0.1; }
function screenCam(id, start, dur, o) {
  const scr = $(`#${id} .screen`);
  scr.style.transformOrigin = `${o.fx}px ${o.fy}px`;
  hooks.push(t => {
    const u = clamp((t - start) / dur);
    const s = o.s0 + (o.s1 - o.s0) * ease(u);
    const x = noise(t, o.seed) * 7, y = noise(t, o.seed + 9) * 6, rz = noise(t, o.seed + 4) * 0.45;
    scr.style.transform = `perspective(2400px) rotateX(${o.rx}deg) rotateY(${o.ry}deg) rotate(${o.rz + rz}deg) translate(${x}px, ${y}px) scale(${s})`;
  });
}

// ---------- cursor: keyframes [t, x, y] em coordenadas da tela, cliques com pulso
function cursor(id, start, keys, clicks = []) {
  const c = $(`#${id} .cursor`);
  hooks.push(t => {
    const u = t - start;
    let x = keys[0][1], y = keys[0][2];
    for (let i = 0; i < keys.length - 1; i++) {
      const [t0, x0, y0] = keys[i], [t1, x1, y1] = keys[i + 1];
      if (u >= t0 && u <= t1) { const p = ease((u - t0) / (t1 - t0)); x = x0 + (x1 - x0) * p; y = y0 + (y1 - y0) * p; break; }
      if (u > t1) { x = x1; y = y1; }
    }
    let sc = 1;
    for (const ck of clicks) { const d = u - ck; if (d >= 0 && d < 0.16) sc = 1 - 0.22 * Math.sin(Math.PI * d / 0.16); }
    c.style.transform = `translate(${x}px, ${y}px) scale(${sc})`;
  });
}
function at(start, rel, fn) { hooks.push(t => fn(t - start >= rel, t - start)); }
function typer(el, start, t0, t1, text) {
  hooks.push(t => {
    const u = t - start, p = clamp((u - t0) / (t1 - t0));
    const n = Math.round(p * text.length);
    el.textContent = text.slice(0, n);
    el.classList.toggle("typing", u >= t0 && n < text.length);
  });
}

// ---------- cenas
function build() {
  person("#cvHook", HOOK, 0);
  person("#cvCta", CTA, 13.8);

  // 1. Personalizar
  screenCam("b1", 2.5, 1.0, { fx: 420, fy: 1000, s0: 1.06, s1: 1.14, rx: 4, ry: -5, rz: -1.2, seed: 1 });
  cursor("b1", 2.5, [[0, 820, 1400], [0.6, 340, 1140]], [0.72]);
  at(2.5, 0.55, on => $("#itPers").classList.toggle("hl", on));

  // 2. Conectores
  screenCam("b2", 3.5, 0.7, { fx: 480, fy: 560, s0: 1.45, s1: 1.58, rx: 3, ry: 6, rz: 1.0, seed: 2 });
  cursor("b2", 3.5, [[0, 760, 1000], [0.42, 470, 750]], [0.52]);
  at(3.5, 0.38, on => $("#itConn").classList.toggle("hl", on));

  // 3. Adicionar +
  screenCam("b3", 4.2, 1.8, { fx: 1090, fy: 560, s0: 1.1, s1: 1.2, rx: 5, ry: -4, rz: -0.8, seed: 3 });
  cursor("b3", 4.2, [[0, 640, 1250], [0.5, 1080, 420], [0.75, 1080, 420], [1.3, 870, 720]], [0.6, 1.5]);
  at(4.2, 0.55, on => $("#plusBtn").style.background = on ? "#ebe9e1" : "transparent");
  at(4.2, 0.65, (on, u) => { const d = $("#dd"); d.style.opacity = on ? Math.min(1, (u - 0.65) / 0.1) : 0; });
  at(4.2, 1.25, on => $("#ddAdd").classList.toggle("hl", on));

  // 4. Nome
  screenCam("b4", 6.0, 1.0, { fx: 590, fy: 900, s0: 1.0, s1: 1.06, rx: 4, ry: 5, rz: 0.8, seed: 4 });
  cursor("b4", 6.0, [[0, 700, 1300], [0.25, 560, 920]], []);
  typer($("#nm4"), 6.0, 0.15, 0.85, "Marketplace Connect");
  at(6.0, 0, on => $("#b4 .fld").classList.add("focus"));

  // 5. Copie a URL (print real da landing)
  screenCam("b5", 7.0, 1.0, { fx: 600, fy: 780, s0: 1.06, s1: 1.12, rx: 3, ry: -6, rz: -1.0, seed: 5 });
  cursor("b5", 7.0, [[0, 600, 1350], [0.5, 990, 1010]], [0.6]);
  at(7.0, 0.65, (on, u) => { $("#copied").style.opacity = on ? Math.min(1, (u - 0.65) / 0.08) : 0; });

  // 6. Cole a URL e Adicionar
  screenCam("b6", 8.0, 1.5, { fx: 590, fy: 900, s0: 1.0, s1: 1.06, rx: 5, ry: 4, rz: 0.6, seed: 6 });
  cursor("b6", 8.0, [[0, 520, 900], [0.2, 520, 900], [0.95, 975, 1415]], [0.15, 1.2]);
  at(8.0, 0.3, (on, u) => {
    $("#urlFld").classList.toggle("focus", u >= 0.15);
    $("#urlPh").style.display = on ? "none" : "inline"; $("#urlVal").style.display = on ? "inline" : "none";
    $("#urlFld").style.background = on && u < 0.55 ? "#e8f0ff" : "#fff";
  });
  at(8.0, 1.25, on => { $("#addBtn").style.background = on ? "#3d3d3a" : "#1f1e1c"; });

  // autorização
  screenCam("c1", 9.5, 0.8, { fx: 590, fy: 900, s0: 1.06, s1: 1.12, rx: 4, ry: -4, rz: -0.6, seed: 7 });
  cursor("c1", 9.5, [[0, 900, 1600], [0.42, 640, 1340]], [0.52]);
  at(9.5, 0.58, on => { const b = $("#authBtn"); b.textContent = on ? "✓ Conectado" : "Autorizar"; b.style.background = on ? "#16a34a" : "#f5c400"; b.style.color = on ? "#fff" : "#111"; });

  // Claude trabalhando no Mercado Livre e no TikTok Shop
  screenCam("d", 10.3, 3.5, { fx: 590, fy: 760, s0: 1.0, s1: 1.04, rx: 3, ry: 3, rz: 0.5, seed: 8 });
  const P = "Confira minhas vendas no Mercado Livre e no TikTok Shop";
  typer($("#dPrompt"), 10.3, 0.1, 0.85, P);
  at(10.3, 0.95, on => { $("#dA").style.display = on ? "none" : "block"; $("#dB").style.display = on ? "block" : "none"; });
  cursor("d", 10.3, [[0, 900, 1500], [0.95, 900, 1500], [1.25, 905, 690]], [1.38]);
  at(10.3, 1.45, (on, u) => { const p = $("#perm"); p.style.opacity = on ? Math.max(0, 1 - (u - 1.45) / 0.12) : 1; });
  const rows = $$("#d .tr");
  rows.forEach((r, i) => at(10.3, 1.55 + i * 0.22, (on, u) => {
    r.style.opacity = on ? Math.min(1, (u - 1.55 - i * 0.22) / 0.1) : 0;
    const st = $(".st", r); const ok = u >= 1.75 + i * 0.22;
    st.classList.toggle("ok", ok); st.textContent = ok ? "✓" : "";
    st.style.transform = ok ? "none" : `rotate(${u * 600}deg)`;
  }));
  $$("#d .rc").forEach((c, i) => at(10.3, 2.3 + i * 0.12, (on, u) => {
    const p = on ? Math.min(1, (u - 2.3 - i * 0.12) / 0.2) : 0;
    c.style.opacity = p; c.style.transform = `translateY(${(1 - p) * 40}px)`;
  }));
  const cnt = (el, t0, to) => hooks.push(t => { const u = t - 10.3; el.textContent = Math.round(to * ease(clamp((u - t0) / 0.6))); });
  cnt($("#nML"), 2.35, 14); cnt($("#nTT"), 2.45, 6);
  at(10.3, 2.85, (on, u) => { const c = $("#cr"); c.style.opacity = on ? Math.min(1, (u - 2.85) / 0.15) : 0; });
  at(10.3, 1.75, on => { $("#capD1").style.display = on ? "none" : "block"; $("#capD2").style.display = on ? "block" : "none"; });
  at(10.3, 0, on => {});
}

// visibilidade das cenas
hooks.unshift(t => SC.forEach(([id, s, d]) => { document.getElementById(id).style.visibility = (t >= s && t < s + d) || (id === "e" && t >= s) ? "visible" : "hidden"; }));
// "dd", "copied" etc começam ocultos
$("#dd").style.opacity = 0; $("#copied").style.opacity = 0; $("#dB").style.display = "none";
$$("#d .tr, #d .rc, #cr").forEach(e => e.style.opacity = 0); $("#capD2").style.display = "none";

window.__seek = t => hooks.forEach(h => h(t));
Promise.all([document.fonts.ready, ...[...HOOK, ...CTA].map(im => im.decode().catch(() => {}))]).then(() => {
  build(); window.__seek(0); window.__ready = true;
});
