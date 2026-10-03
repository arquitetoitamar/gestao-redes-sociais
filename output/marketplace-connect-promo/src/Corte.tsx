import React from 'react';
import {
  AbsoluteFill, Audio, OffthreadVideo, Sequence, staticFile, useCurrentFrame, useVideoConfig,
  interpolate, spring, Easing,
} from 'remotion';

type Word = {t: string; s: number; e: number; p: string};
type Page = {s: number; e: number; w: number[]};
type Callout = {t: number; text: string; icon: string};
export type CorteProps = {
  clip: string; durationSec: number; headline: string[]; hl: number[];
  words: Word[]; pages: Page[]; callouts: Callout[];
};

const INK = '#042A31';
const DEEP = '#021d22';
const YELLOW = '#FFE94D';
const TEAL = '#16A092';
const FONT = '"Avenir Next", "Avenir", "Helvetica Neue", Arial, sans-serif';

const SLIDE = {x: 372, y: 240, w: 860, h: 400};
const SLIDE_BOX = {left: 24, top: 372, width: 1032, height: 480};
const FACE = {cx: 1665, cy: 555};
const FACE_BOX = {size: 640, left: 220, top: 1120};
const INTRO_END = 2.2;

const ring = (c: string, r: number) =>
  [[r, 0], [-r, 0], [0, r], [0, -r], [r * 0.7, r * 0.7], [-r * 0.7, r * 0.7], [r * 0.7, -r * 0.7], [-r * 0.7, -r * 0.7]]
    .map(([x, y]) => `${x}px ${y}px 0 ${c}`).join(', ');

const measure = (text: string): number => {
  const ctx = document.createElement('canvas').getContext('2d');
  if (!ctx) return text.length * 70;
  ctx.font = `800 100px ${FONT}`;
  return ctx.measureText(text.toUpperCase()).width;
};

const Icon: React.FC<{name: string; color: string}> = ({name, color}) => {
  const p = {stroke: color, strokeWidth: 2.4, fill: 'none', strokeLinecap: 'round' as const, strokeLinejoin: 'round' as const};
  return (
    <svg viewBox="0 0 24 24" width="100%" height="100%">
      {name === 'eye' && (<><path d="M1.5 12s4-7 10.5-7 10.5 7 10.5 7-4 7-10.5 7S1.5 12 1.5 12z" {...p} /><circle cx="12" cy="12" r="3.2" fill={color} /></>)}
      {name === 'plug' && (<path d="M9 2.5v5.5M15 2.5v5.5M6 8h12v3.5a6 6 0 0 1-12 0V8zM12 17.5v4" {...p} />)}
      {name === 'bolt' && (<path d="M13 2L4.5 13.5h6.5L10 22l9-12h-6.5L13 2z" fill={color} />)}
      {name === 'shield' && (<><path d="M12 2.5l8 3v6c0 4.8-3.4 8.6-8 10.5-4.6-1.9-8-5.7-8-10.5v-6l8-3z" {...p} /><path d="M8.5 12l2.5 2.5 4.5-5" {...p} /></>)}
      {name === 'moon' && (<path d="M20.5 13.8A8.6 8.6 0 1 1 10.2 3.5a7 7 0 0 0 10.3 10.3z" fill={color} />)}
      {name === 'check' && (<path d="M4 12.5l5 5L20 6.5" {...p} strokeWidth={3.2} />)}
      {name === 'clock' && (<><circle cx="12" cy="12" r="9" {...p} /><path d="M12 7v5.2l3.3 2" {...p} /></>)}
      {name === 'percent' && (<><path d="M19 5L5 19" {...p} /><circle cx="7" cy="7" r="2.6" {...p} /><circle cx="17" cy="17" r="2.6" {...p} /></>)}
      {name === 'stop' && (<rect x="5" y="5" width="14" height="14" rx="3.2" fill={color} />)}
      {name === 'list' && (<><path d="M9 6.5h12M9 12h12M9 17.5h12" {...p} /><circle cx="4.2" cy="6.5" r="1.3" fill={color} /><circle cx="4.2" cy="12" r="1.3" fill={color} /><circle cx="4.2" cy="17.5" r="1.3" fill={color} /></>)}
    </svg>
  );
};

const Logos: React.FC<{scale: number}> = ({scale}) => (
  <div style={{display: 'flex', alignItems: 'center', gap: 26, transform: `scale(${scale})`}}>
    <img src={staticFile('logos/claude.png')} style={{height: 104, width: 104, borderRadius: 24, boxShadow: '0 10px 30px rgba(0,0,0,.45)'}} />
    <div style={{fontFamily: FONT, fontWeight: 800, fontSize: 76, color: '#fff', lineHeight: 1, marginTop: -6}}>+</div>
    <img src={staticFile('logos/mercadolivre.png')} style={{height: 104, width: 130, borderRadius: 18, boxShadow: '0 10px 30px rgba(0,0,0,.45)'}} />
  </div>
);

export const Corte: React.FC<CorteProps> = ({clip, durationSec, headline, hl, words, pages, callouts}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const t = frame / fps;
  const progress = Math.min(1, t / durationSec);

  // ---- video crops ----
  const sS = SLIDE_BOX.width / SLIDE.w;
  const sF = 1.34 * (1 + 0.06 * progress);
  const half = FACE_BOX.size / 2;

  // ---- intro / header ----
  const introP = interpolate(t, [INTRO_END, INTRO_END + 0.8], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.out(Easing.cubic)});
  const logoY = interpolate(introP, [0, 1], [380, 300]);
  const logoScale = interpolate(introP, [0, 1], [1.5, 1]);
  const logoPop = spring({frame, fps, config: {damping: 11, stiffness: 140}});
  const scrimOpacity = interpolate(t, [INTRO_END, INTRO_END + 0.5], [0.84, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const headOut = interpolate(t, [INTRO_END, INTRO_END + 0.5], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});

  // ---- captions ----
  const page = t < INTRO_END + 0.3 ? undefined : pages.find((p) => t >= p.s && t < p.e);
  const pageStartF = page ? Math.round(page.s * fps) : 0;
  const pagePop = page ? spring({frame: frame - pageStartF, fps, config: {damping: 14, stiffness: 260}}) : 1;

  // ---- callout ----
  const callout = callouts.find((c) => t >= c.t && t < c.t + 2.5);
  const cf = callout ? frame - Math.round(callout.t * fps) : 0;
  const cPop = callout ? spring({frame: cf, fps, config: {damping: 9, stiffness: 170}}) : 0;
  const cOut = callout ? interpolate(t, [callout.t + 2.1, callout.t + 2.5], [1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'}) : 0;

  // ---- CTA ----
  const ctaStart = durationSec - 2.8;
  const ctaPop = spring({frame: frame - Math.round(ctaStart * fps), fps, config: {damping: 10, stiffness: 150}});
  const ctaBounce = Math.sin((t - ctaStart) * 6) * 6;

  return (
    <AbsoluteFill style={{background: `radial-gradient(1300px 1000px at 50% 28%, #0b4d4a 0%, ${INK} 58%, ${DEEP} 100%)`, fontFamily: FONT}}>
      {/* slide crop */}
      <div style={{position: 'absolute', ...SLIDE_BOX, overflow: 'hidden', borderRadius: 26, border: '3px solid rgba(255,255,255,.10)', boxShadow: '0 18px 50px rgba(0,0,0,.5)', background: '#0e1116'}}>
        <OffthreadVideo
          src={staticFile(clip)}
          style={{position: 'absolute', width: 1920, height: 1080, transformOrigin: '0 0', transform: `translate(${-SLIDE.x * sS}px, ${-SLIDE.y * sS}px) scale(${sS})`}}
        />
      </div>
      {/* progress */}
      <div style={{position: 'absolute', left: 24, top: 864, width: 1032, height: 7, borderRadius: 4, background: 'rgba(255,255,255,.14)'}}>
        <div style={{width: `${progress * 100}%`, height: '100%', borderRadius: 4, background: YELLOW}} />
      </div>

      {/* face */}
      <div style={{position: 'absolute', left: FACE_BOX.left, top: FACE_BOX.top, width: FACE_BOX.size, height: FACE_BOX.size, borderRadius: '50%', overflow: 'hidden',
        border: `9px solid ${YELLOW}`, boxShadow: `0 0 0 6px ${INK}, 0 24px 60px rgba(0,0,0,.55)`, boxSizing: 'border-box'}}>
        <OffthreadVideo
          src={staticFile(clip)} muted
          style={{position: 'absolute', width: 1920, height: 1080, transformOrigin: '0 0',
            transform: `translate(${half - 9 - FACE.cx * sF}px, ${half - 9 - FACE.cy * sF}px) scale(${sF})`}}
        />
      </div>

      {/* scrim (intro) */}
      <div style={{position: 'absolute', left: 0, top: 0, width: 1080, height: 1130, opacity: scrimOpacity,
        background: `linear-gradient(rgba(2,29,34,.9) 0%, rgba(2,29,34,.9) 90%, rgba(2,29,34,0) 100%)`}} />
      {/* header logos */}
      <div style={{position: 'absolute', left: 0, right: 0, top: logoY - 52, display: 'flex', justifyContent: 'center', opacity: Math.min(1, logoPop)}}>
        <Logos scale={logoScale * (0.85 + 0.15 * Math.min(1, logoPop))} />
      </div>

      {/* captions */}
      {page && (
        <div style={{position: 'absolute', left: 30, width: 1020, top: 890, height: 214, display: 'flex', flexWrap: 'wrap', alignItems: 'center', justifyContent: 'center',
          gap: '2px 34px', transform: `scale(${0.92 + 0.08 * pagePop})`, opacity: Math.min(1, pagePop * 1.4)}}>
          {page.w.map((wi, k) => {
            const w = words[wi];
            const next = words[wi + 1];
            const end = next ? Math.max(w.e, next.s - 0.01) : w.e + 0.4;
            const active = t >= w.s && t < end;
            const pop = active ? spring({frame: frame - Math.round(w.s * fps), fps, config: {damping: 12, stiffness: 300}}) : 1;
            return (
              <span key={k} style={{fontFamily: FONT, fontWeight: 800, fontSize: 78, lineHeight: 1.04, textTransform: 'uppercase',
                color: active ? YELLOW : '#fff', transform: `scale(${active ? 1 + 0.06 * Math.min(1, pop) : 1})`, display: 'inline-block',
                textShadow: `${ring(DEEP, 5)}, 0 8px 22px rgba(0,0,0,.55)`}}>
                {w.t.replace(/[.,?!]$/, '')}
              </span>
            );
          })}
        </div>
      )}

      {/* callout badge */}
      {callout && (
        <div style={{position: 'absolute', right: 44, top: 770, display: 'flex', alignItems: 'center', gap: 16, padding: '12px 30px 12px 14px', borderRadius: 60,
          background: YELLOW, boxShadow: '0 12px 34px rgba(0,0,0,.5)', opacity: cOut * Math.min(1, cPop * 1.5),
          transform: `translateY(${(1 - Math.min(1, cPop)) * -40}px) scale(${0.6 + 0.4 * cPop}) rotate(${(1 - Math.min(1, cPop)) * -6}deg)`}}>
          <div style={{width: 66, height: 66, borderRadius: '50%', background: INK, padding: 14, boxSizing: 'border-box'}}>
            <Icon name={callout.icon} color={YELLOW} />
          </div>
          <div style={{fontFamily: FONT, fontWeight: 800, fontSize: 44, color: INK, letterSpacing: 0.5}}>{callout.text}</div>
        </div>
      )}
      {callouts.map((c, i) => (
        <Sequence key={i} from={Math.round(c.t * fps)} durationInFrames={30}>
          <Audio src={staticFile('audio/sparkle-touch.mp3')} volume={0.22} />
        </Sequence>
      ))}

      {/* CTA */}
      {t >= ctaStart && (
        <div style={{position: 'absolute', left: 0, right: 0, top: 1742 + ctaBounce, display: 'flex', justifyContent: 'center', transform: `scale(${Math.min(1, ctaPop)})`}}>
          <div style={{display: 'flex', alignItems: 'center', gap: 16, padding: '18px 44px', borderRadius: 60, background: YELLOW, boxShadow: '0 14px 40px rgba(0,0,0,.55)'}}>
            <div style={{fontFamily: FONT, fontWeight: 800, fontSize: 52, color: INK}}>SAIBA MAIS</div>
            <svg width="44" height="44" viewBox="0 0 24 24"><path d="M12 4v13M6 12l6 6 6-6" stroke={INK} strokeWidth="3.4" fill="none" strokeLinecap="round" strokeLinejoin="round" /></svg>
          </div>
        </div>
      )}

      {/* intro overlay (also the cover) */}
      {t < INTRO_END + 0.6 && (
        <>
          <div style={{position: 'absolute', left: 0, right: 0, top: 470, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 10,
            opacity: 1 - headOut, transform: `translateY(${-70 * headOut}px)`}}>
            {headline.map((line, i) => {
              const size = Math.min(138, Math.floor((100 * 900) / measure(line)));
              const sp = spring({frame: frame - i * 4, fps, config: {damping: 11, stiffness: 190}});
              const hi = hl.includes(i);
              return (
                <div key={i} style={{fontFamily: FONT, fontWeight: 800, fontSize: size, lineHeight: 1.0, textTransform: 'uppercase', whiteSpace: 'nowrap',
                  color: hi ? INK : '#fff', background: hi ? YELLOW : 'transparent', padding: hi ? '8px 26px 2px' : '0 10px', borderRadius: 18,
                  transform: `scale(${0.7 + 0.3 * Math.min(1, sp)})`, opacity: Math.min(1, sp * 1.6),
                  textShadow: hi ? 'none' : `${ring(DEEP, 6)}, 0 10px 26px rgba(0,0,0,.6)`}}>
                  {line}
                </div>
              );
            })}
          </div>
        </>
      )}
      <Sequence from={0} durationInFrames={45}>
        <Audio src={staticFile('audio/whoosh-fast.mp3')} volume={0.28} />
      </Sequence>
      <OffthreadVideoAudioGuard />
    </AbsoluteFill>
  );
};

const OffthreadVideoAudioGuard: React.FC = () => null;
