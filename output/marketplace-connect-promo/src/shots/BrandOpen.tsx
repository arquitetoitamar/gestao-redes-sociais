// BrandOpen -- adapted from shots/opening/brand-ink-open.md (demo:
// demos/typography/brand-ink-open/BrandInkOpen.tsx). Re-skinned dark-navy /
// brand-blue instead of paper/amber; wordmark split across two lines
// ("Marketplace" / "Connect") to fit the 1080-wide portrait canvas; kicker
// wraps to two short lines to satisfy aesthetic-rules Q11's aux-text floor on
// this project's 1920-tall frame. Motion formula kept 1:1 from the card:
// crosshair pathLength draw-on -> per-glyph letterpress (scale 1.6->1 +
// blur->0 + amber/blue under-glint) -> mono kicker typewriter -> >=30f hold
// of the COMPLETE wordmark (R1) -> lift+shrink+fade handoff.
import { AbsoluteFill, interpolate, useCurrentFrame, Easing } from 'remotion';
import { NAVY, BLUE, OFFWHITE, FONT, MONO } from '../tokens';

export const BRAND_OPEN_DURATION = 96;

const LINES = ['Marketplace', 'Connect'];
const KICKER_LINES = ['SUA IA JÁ VENDE', 'NO MARKETPLACE'];

export const BrandOpen: React.FC = () => {
  const frame = useCurrentFrame();

  const vDraw = interpolate(frame, [0, 9], [100, 0], {
    extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.bezier(0.3, 0, 0.2, 1),
  });
  const hDraw = interpolate(frame, [8, 18], [100, 0], {
    extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.linear,
  });
  const crossFade = interpolate(frame, [24, 34], [1, 0], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });

  const kickStart = 30;
  const kickPerChar = 0.55;
  const line1Done = kickStart + KICKER_LINES[0].length * kickPerChar;
  const line2Start = line1Done;
  const line2Done = line2Start + KICKER_LINES[1].length * kickPerChar;
  const kickShown = [
    Math.max(0, Math.min(KICKER_LINES[0].length, Math.floor((frame - kickStart) / kickPerChar))),
    Math.max(0, Math.min(KICKER_LINES[1].length, Math.floor((frame - line2Start) / kickPerChar))),
  ];
  const cursorOn = (() => {
    if (frame < kickStart) return false;
    if (frame < line2Done) return true;
    if (frame > 86) return false;
    const b = frame - line2Done;
    return Math.floor(b / 2) % 2 === 0;
  })();

  // hold the complete wordmark >=30f (R1) before lifting off (88->96)
  const brandOut = interpolate(frame, [88, 96], [0, 1], {
    extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.bezier(0.4, 0, 0.5, 1),
  });
  const brandOpacity = 1 - brandOut;
  const groupY = -brandOut * 40;
  const groupScale = 1 - brandOut * 0.12;

  let renderIdx = 0;

  return (
    <AbsoluteFill style={{ backgroundColor: NAVY, justifyContent: 'center', alignItems: 'center' }}>
      <AbsoluteFill
        style={{ background: 'radial-gradient(900px 700px at 50% 40%, rgba(14,137,255,0.18), transparent 65%)' }}
      />
      <div
        style={{
          textAlign: 'center', opacity: brandOpacity,
          transform: `translateY(${groupY}px) scale(${groupScale})`,
        }}
      >
        <svg width={64} height={64} viewBox="0 0 64 64" style={{ display: 'block', margin: '0 auto 40px', opacity: crossFade }}>
          <line x1={32} y1={2} x2={32} y2={62} stroke={BLUE} strokeWidth={5} strokeLinecap="round" pathLength={100} strokeDasharray={100} strokeDashoffset={vDraw} />
          <line x1={2} y1={32} x2={62} y2={32} stroke={BLUE} strokeWidth={5} strokeLinecap="round" pathLength={100} strokeDasharray={100} strokeDashoffset={hDraw} />
        </svg>

        {LINES.map((line, li) => (
          <div
            key={li}
            style={{
              fontFamily: FONT, fontSize: 124, fontWeight: 700, color: OFFWHITE,
              letterSpacing: '-0.015em', lineHeight: 1.04, whiteSpace: 'pre',
              display: 'flex', justifyContent: 'center', alignItems: 'flex-end',
            }}
          >
            {line.split('').map((ch) => {
              const i = renderIdx++;
              const delay = 8 + i * 2;
              const t = interpolate(frame, [delay, delay + 12], [0, 1], {
                extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.bezier(0.2, 0.7, 0.25, 1),
              });
              const glintCenter = delay + 12;
              const glint = interpolate(frame, [glintCenter - 4, glintCenter, glintCenter + 4], [0, 1, 0], {
                extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
              });
              return (
                <span
                  key={i}
                  style={{
                    position: 'relative', display: 'inline-block', opacity: t,
                    transform: `scale(${1.6 - 0.6 * t})`, transformOrigin: 'center bottom',
                    filter: `blur(${(1 - t) * 6}px)`,
                  }}
                >
                  {ch}
                  <span
                    style={{
                      position: 'absolute', left: '50%', bottom: -6, transform: 'translateX(-50%)',
                      width: `${glint * 100}%`, height: 3, background: BLUE, opacity: glint, borderRadius: 2,
                    }}
                  />
                </span>
              );
            })}
          </div>
        ))}

        <div style={{ marginTop: 34, fontFamily: MONO, fontSize: 84, letterSpacing: '0.03em', color: 'rgba(245,243,240,0.78)', textTransform: 'uppercase' }}>
          {KICKER_LINES.map((line, li) => (
            <div key={li} style={{ display: 'flex', justifyContent: 'center', alignItems: 'baseline', height: 86 }}>
              <span style={{ whiteSpace: 'pre' }}>{line.slice(0, kickShown[li])}</span>
              {li === KICKER_LINES.length - 1 ? (
                <span
                  style={{
                    display: 'inline-block', width: 30, height: 58, marginLeft: 8,
                    background: BLUE, opacity: cursorOn ? 0.9 : 0,
                  }}
                />
              ) : null}
            </div>
          ))}
        </div>
      </div>
    </AbsoluteFill>
  );
};
