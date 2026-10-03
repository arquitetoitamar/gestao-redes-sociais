// Outro -- adapted from shots/outro/outro-group-photo-launch.md (demo:
// demos/outro/outro-group-photo-launch/OutroGroupPhotoLaunch.tsx). Every
// function shown earlier in the film gets a representative element flown
// back in for the "group photo" (Q8) -- here that is literally the 9 real
// logos from the hub-connect beat, converging on the Marketplace Connect
// wordmark. No PageCam background (there is no real page in this story);
// replaced with the same brand void used in HeroCard/HubConnect so the whole
// film reads as one continuous space. Kept verbatim: per-element cue+12f fly
// with a true overshoot bezier (y1>1), settle-then-recede treatment on the
// non-wordmark layer, crane rotateX(4->0)+scale camera, stage-light +
// particle-dust atmosphere (retinted brand blue, never the source's gold),
// letterpress wordmark sign-off held >=1s (R1), CTA is the product's
// standing rule: "Saiba mais", never "teste grátis" (see project MEMORY).
import { AbsoluteFill, Img, staticFile, interpolate, useCurrentFrame, Easing } from 'remotion';
import { NAVY, NAVY_DEEP, BLUE, OFFWHITE, FONT, MONO } from '../tokens';

export const OUTRO_DURATION = 160;

const FLY_EASE = Easing.bezier(0.34, 1.4, 0.44, 1);
const CRANE_EASE = Easing.bezier(0.3, 0, 0.2, 1);

type El = { key: string; kind: 'img' | 'text'; src?: string; label: string; cx: number; cy: number; w: number; h: number; scale: number; rot: number; dx: number; dy: number; cue: number };

const ELS: El[] = [
  { key: 'chatgpt', kind: 'img', src: 'logos/chatgpt.png', label: 'ChatGPT', cx: 540, cy: 260, w: 220, h: 84, scale: 1, rot: -2, dx: 0, dy: -420, cue: 4 },
  { key: 'claude', kind: 'img', src: 'logos/claude.png', label: 'Claude', cx: 200, cy: 400, w: 150, h: 150, scale: 1, rot: -5, dx: -420, dy: -300, cue: 7 },
  { key: 'codex', kind: 'img', src: 'logos/codex.png', label: 'Codex', cx: 880, cy: 400, w: 170, h: 102, scale: 1, rot: 4, dx: 420, dy: -300, cue: 10 },
  { key: 'ml', kind: 'img', src: 'logos/mercadolivre.png', label: 'Mercado Livre', cx: 120, cy: 800, w: 140, h: 114, scale: 1, rot: -3, dx: -480, dy: 0, cue: 13 },
  { key: 'amazon', kind: 'img', src: 'logos/amazon.png', label: 'Amazon', cx: 960, cy: 800, w: 132, h: 98, scale: 1, rot: 3, dx: 480, dy: 0, cue: 16 },
  { key: 'shopee', kind: 'img', src: 'logos/shopee.png', label: 'Shopee', cx: 150, cy: 1480, w: 96, h: 120, scale: 1, rot: 3, dx: -420, dy: 260, cue: 19 },
  // text-only chips (no real logo asset, see header note) get a wider box +
  // bigger type than the original card's tiny name-tags so the label clears
  // aesthetic-rules Q11's aux-text floor (>=3% of 1920px frame height)
  { key: 'tiktokshop', kind: 'text', label: 'TikTok Shop', cx: 900, cy: 1490, w: 280, h: 130, scale: 1, rot: -3, dx: 420, dy: 260, cue: 22 },
  { key: 'shein', kind: 'text', label: 'Shein', cx: 300, cy: 1710, w: 240, h: 130, scale: 1, rot: 2, dx: -200, dy: 420, cue: 25 },
  { key: 'magalu', kind: 'text', label: 'Magalu', cx: 780, cy: 1710, w: 260, h: 130, scale: 1, rot: -2, dx: 200, dy: 420, cue: 28 },
];

// 24 blue dust motes, deterministic (index-derived)
const DUST = Array.from({ length: 24 }, (_, i) => ({
  x: (i * 331 + 97) % 1080,
  y0: (i * 577 + 211) % 1920,
  rise: 0.28 + (i % 5) * 0.1,
  swayAmp: 8 + (i % 4) * 5,
  swayFreq: 0.02 + (i % 3) * 0.007,
  phase: (i * 0.83) % (Math.PI * 2),
  size: 2 + (i % 3) * 0.6,
  opacity: 0.14 + ((i * 7) % 5) * 0.045,
}));

const WORD_LINES = ['Marketplace', 'Connect'];

export const Outro: React.FC = () => {
  const frame = useCurrentFrame();
  const duration = OUTRO_DURATION;

  const fadeOut = interpolate(frame, [duration - 12, duration], [1, 0], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
  const recede = interpolate(frame, [42, 50], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });

  const craneT = interpolate(frame, [0, 40], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: CRANE_EASE });
  const pushT = interpolate(frame, [40, duration], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
  const camScale = 1.05 - 0.05 * craneT + 0.03 * pushT;
  const camTilt = 4 * (1 - craneT);

  const stageLight = interpolate(frame, [42, 50, 58], [0, 0.55, 0.28], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
  const ruleT = interpolate(frame, [58, 70], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.bezier(0.3, 0, 0.2, 1) });
  const ruleExt = interpolate(frame, [58, 66], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.bezier(0.3, 0, 0.2, 1) });
  const ruleExtFade = interpolate(frame, [66, 74], [1, 0], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
  const iconIn = interpolate(frame, [40, 52], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.bezier(0.2, 1.1, 0.3, 1) });

  const ctaIn = interpolate(frame, [96, 108], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
  const urlIn = interpolate(frame, [104, 116], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });

  let glyphIdx = 0;

  return (
    <AbsoluteFill style={{ opacity: fadeOut, backgroundColor: NAVY }}>
      <AbsoluteFill style={{ transform: `perspective(1500px) rotateX(${camTilt}deg) scale(${camScale})`, transformOrigin: '50% 46%' }}>
        <AbsoluteFill style={{ background: `radial-gradient(1000px 1500px at 50% 50%, ${NAVY_DEEP}, ${NAVY} 72%)` }} />
        <AbsoluteFill style={{ opacity: 0.14, backgroundImage: 'radial-gradient(rgba(245,243,240,0.5) 1.5px, transparent 1.5px)', backgroundSize: '54px 54px' }} />

        {/* flying group-photo elements */}
        <AbsoluteFill style={{ pointerEvents: 'none' }}>
          {ELS.map((el) => {
            if (frame < el.cue) return null;
            const t = interpolate(frame, [el.cue, el.cue + 12], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: FLY_EASE });
            const opacity = interpolate(frame, [el.cue, el.cue + 3], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
            const x = el.dx * (1 - t);
            const y = el.dy * (1 - t);
            const rot = el.rot * (2 - t);
            const scale = el.scale * (1.12 - 0.12 * t);
            const air = Math.max(0, 1 - t);
            const shadow = `0 ${10 + 24 * air}px ${22 + 40 * air}px rgba(0,0,0,${0.3 + 0.15 * air})`;
            const settledOpacity = opacity * (1 - 0.12 * recede);
            const glow = interpolate(frame, [el.cue + 12, el.cue + 18], [0.4, 0], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
            const showGlow = frame >= el.cue + 12 && frame < el.cue + 18;
            const cardW = el.w + 60;
            const cardH = el.h + 60;
            return (
              <div key={el.key}>
                <div
                  style={{
                    position: 'absolute', left: el.cx - cardW / 2, top: el.cy - cardH / 2, width: cardW, height: cardH,
                    transform: `translate(${x}px, ${y}px) rotate(${rot}deg) scale(${scale})`,
                    transformOrigin: 'center center', borderRadius: 26, overflow: 'hidden',
                    background: OFFWHITE, boxShadow: shadow, opacity: settledOpacity,
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                  }}
                >
                  {el.kind === 'img' ? (
                    <Img src={staticFile(el.src!)} style={{ width: el.w, height: el.h, maxWidth: cardW - 40, maxHeight: cardH - 40, objectFit: 'contain' }} />
                  ) : (
                    <div style={{ fontFamily: FONT, fontWeight: 700, fontSize: 76, lineHeight: 1.02, color: '#22222E', textAlign: 'center', padding: '0 10px' }}>{el.label}</div>
                  )}
                </div>
                {showGlow ? (
                  <div
                    style={{
                      position: 'absolute', left: el.cx - cardW * 0.6, top: el.cy - cardW * 0.6, width: cardW * 1.2, height: cardW * 1.2,
                      borderRadius: '50%', background: `radial-gradient(circle, rgba(14,137,255,0.9), rgba(14,137,255,0) 70%)`,
                      opacity: glow, mixBlendMode: 'screen',
                    }}
                  />
                ) : null}
              </div>
            );
          })}
        </AbsoluteFill>

        {/* dust */}
        <AbsoluteFill style={{ pointerEvents: 'none' }}>
          {DUST.map((d, i) => {
            const y = (((d.y0 - frame * d.rise) % 1920) + 1920) % 1920;
            const x = d.x + Math.sin(frame * d.swayFreq + d.phase) * d.swayAmp;
            return (
              <div key={i} style={{ position: 'absolute', left: x, top: y, width: d.size, height: d.size, borderRadius: '50%', background: 'rgba(150,205,255,0.9)', opacity: d.opacity }} />
            );
          })}
        </AbsoluteFill>

        {/* stage light behind wordmark */}
        {stageLight > 0 ? (
          <AbsoluteFill style={{ pointerEvents: 'none', background: `radial-gradient(560px 480px at 540px 860px, rgba(150,205,255,0.55), rgba(14,137,255,0.18) 55%, rgba(14,137,255,0) 75%)`, opacity: stageLight }} />
        ) : null}

        {/* wordmark sign-off -- anchored from a fixed top offset (not pure
            vertical-center) so its extent is predictable and the flying
            logo ring can be laid out around it without collision */}
        <AbsoluteFill style={{ justifyContent: 'flex-start', alignItems: 'center', paddingTop: 560, pointerEvents: 'none' }}>
          <div style={{ textAlign: 'center' }}>
            <div style={{ opacity: iconIn, transform: `scale(${0.7 + 0.3 * iconIn}) translateY(${(1 - iconIn) * -14}px)`, marginBottom: 18 }}>
              <Img src={staticFile('logos/tiops-icon.png')} style={{ width: 84, height: 'auto', margin: '0 auto', display: 'block' }} />
            </div>
            {WORD_LINES.map((line, li) => (
              <div key={li} style={{ fontFamily: FONT, fontSize: 108, fontWeight: 700, color: OFFWHITE, letterSpacing: '-0.01em', lineHeight: 1.05, display: 'flex', justifyContent: 'center' }}>
                {line.split('').map((ch) => {
                  const i = glyphIdx++;
                  const delay = Math.round(42 + i * 2.0);
                  const t = interpolate(frame, [delay, delay + 8], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.bezier(0.2, 0.75, 0.3, 1) });
                  return (
                    <span key={i} style={{ opacity: t, transform: `translateY(${(1 - t) * 24}px) scale(${1.3 - 0.3 * t})`, filter: `blur(${(1 - t) * 7}px)`, display: 'inline-block', whiteSpace: 'pre' }}>
                      {ch}
                    </span>
                  );
                })}
              </div>
            ))}
            <div style={{ position: 'relative', height: 6, width: 220, margin: '30px auto 0' }}>
              <div style={{ position: 'absolute', inset: 0, borderRadius: 3, background: BLUE, transform: `scaleX(${ruleT})` }} />
              {ruleExt > 0 && ruleExtFade > 0 ? (
                <>
                  <div style={{ position: 'absolute', top: 2.5, height: 1, right: '100%', width: 150 * ruleExt, background: BLUE, opacity: ruleExtFade }} />
                  <div style={{ position: 'absolute', top: 2.5, height: 1, left: '100%', width: 150 * ruleExt, background: BLUE, opacity: ruleExtFade }} />
                </>
              ) : null}
            </div>

            <div style={{ marginTop: 36, opacity: ctaIn, transform: `translateY(${(1 - ctaIn) * 14}px)` }}>
              <div style={{ fontFamily: FONT, fontWeight: 700, fontSize: 100, color: BLUE }}>Saiba mais</div>
            </div>
            <div style={{ marginTop: 16, opacity: urlIn, fontFamily: MONO, fontSize: 60, letterSpacing: '-0.01em', color: 'rgba(245,243,240,0.85)' }}>
              marketplaces.tiops.com.br
            </div>
          </div>
        </AbsoluteFill>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
