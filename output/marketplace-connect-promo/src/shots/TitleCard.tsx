// TitleCard -- adapted from shots/typography/paper-title-card.md (demo:
// demos/typography/paper-title-card/PaperTitleCard.tsx), re-skinned as the
// card's own doc notes exists ("对照暗场版 TitleCard"): dark navy ground +
// blue accent instead of paper/amber. Same formula: per-word letterpress
// (scale 1.28->1 + blur->0), one accent word (C2: concrete claim, not a
// metaphor), underline scaleX collapse, digit-roll stat line. Breathing
// position between the hub-connect beat and the feature-chip beat (R1/rhythm
// bridge template "呼吸字卡").
import { AbsoluteFill, interpolate, useCurrentFrame, Easing } from 'remotion';
import { NAVY, BLUE, OFFWHITE, MONO, FONT } from '../tokens';
import { DigitRoll } from '../lib/DigitRoll';

export const TITLE_CARD_DURATION = 55;

const WORDS: { text: string; accent?: boolean }[] = [
  { text: 'Preço,' },
  { text: 'estoque' },
  { text: 'e' },
  { text: 'pedidos:' },
  { text: 'automáticos.', accent: true },
];

export const TitleCard: React.FC = () => {
  const frame = useCurrentFrame();
  const duration = TITLE_CARD_DURATION;
  const fadeOut = interpolate(frame, [duration - 8, duration], [1, 0], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
  const underline = interpolate(frame, [16, 34], [0, 1], {
    extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.bezier(0.3, 0, 0.2, 1),
  });
  const subT = interpolate(frame, [10, 22], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });

  return (
    <AbsoluteFill style={{ backgroundColor: NAVY, justifyContent: 'center', alignItems: 'center', opacity: fadeOut }}>
      <AbsoluteFill style={{ background: 'radial-gradient(1000px 700px at 50% 45%, rgba(14,137,255,0.16), transparent 65%)' }} />
      <div style={{ textAlign: 'center', maxWidth: 940, padding: '0 60px' }}>
        <div
          style={{
            fontFamily: FONT, fontSize: 100, fontWeight: 700, lineHeight: 1.14, color: OFFWHITE,
            letterSpacing: '-0.012em', display: 'flex', flexWrap: 'wrap', justifyContent: 'center', columnGap: '0.26em',
          }}
        >
          {WORDS.map((w, i) => {
            const delay = 4 + i * 4;
            const t = interpolate(frame, [delay, delay + 9], [0, 1], {
              extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.bezier(0.2, 0.75, 0.3, 1),
            });
            return (
              <span
                key={i}
                style={{
                  opacity: t, transform: `scale(${1.28 - 0.28 * t})`, filter: `blur(${(1 - t) * 7}px)`,
                  display: 'inline-block', fontStyle: w.accent ? 'italic' : 'normal',
                  color: w.accent ? BLUE : undefined,
                }}
              >
                {w.text}
              </span>
            );
          })}
        </div>
        <div style={{ height: 6, width: 200, margin: '38px auto 0', borderRadius: 3, background: BLUE, transform: `scaleX(${underline})` }} />
        <div
          style={{
            fontFamily: MONO, fontSize: 84, letterSpacing: '0.02em', color: 'rgba(245,243,240,0.8)',
            marginTop: 36, opacity: subT, textTransform: 'uppercase',
            display: 'flex', flexWrap: 'wrap', justifyContent: 'center', alignItems: 'baseline', gap: '0.35em',
          }}
        >
          <DigitRoll value="6" delay={12} fontSize={84} color={BLUE} />
          <span>MARKETPLACES</span>
        </div>
      </div>
    </AbsoluteFill>
  );
};
