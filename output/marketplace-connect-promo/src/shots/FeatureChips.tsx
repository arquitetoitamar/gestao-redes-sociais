// FeatureChips -- simplified adaptation of shots/ui-entrance/deck-deal-flyin.md
// (demo: demos/ui-entrance/deck-deal-flyin/DeckDealFlyin.tsx). The full card
// choreographs a dark-metal pile-orbit preamble + 26-card scrolling grid
// against a REAL page; this project has no real list page to deal cards from
// and a 15-25s vertical short has no frame budget for a 2s orbit preamble,
// so the preamble is dropped (sequences/promo-energy-arc.md explicitly
// allows collapsing segments in short-form cuts). What is NOT downgraded --
// the card's actual "known pitfall" parameter -- is the hard-accelerating
// deal cadence (interval shrinks every card, never uniform) and the
// settle+press landing bounce (y1>1 bezier) plus the 0.5s full-stop rest
// after the last card lands (R2). Generic pictograms only (price tag / box /
// chat / megaphone / truck) -- no third-party logos belong on this shot.
import { AbsoluteFill, interpolate, useCurrentFrame, Easing } from 'remotion';
import { NAVY, BLUE, OFFWHITE, FONT } from '../tokens';
import { BigCaption } from '../lib/BigCaption';

export const FEATURE_CHIPS_DURATION = 112;

const DEAL_EASE = Easing.bezier(0.3, 0, 0.2, 1);
const SETTLE_EASE = Easing.bezier(0.3, 0, 0.25, 1.15);

type Feature = { label: string; icon: React.FC<{ color: string }> };

const IconTag: React.FC<{ color: string }> = ({ color }) => (
  <svg width={44} height={44} viewBox="0 0 24 24" fill="none">
    <path d="M12.6 2H4a2 2 0 0 0-2 2v8.6a2 2 0 0 0 .59 1.41l9 9a2 2 0 0 0 2.82 0l7.6-7.6a2 2 0 0 0 0-2.82l-9-9A2 2 0 0 0 12.6 2Z" stroke={color} strokeWidth={1.8} strokeLinejoin="round" />
    <circle cx={7.5} cy={7.5} r={1.6} fill={color} />
  </svg>
);
const IconBox: React.FC<{ color: string }> = ({ color }) => (
  <svg width={44} height={44} viewBox="0 0 24 24" fill="none">
    <path d="M3 8.5 12 4l9 4.5v7L12 20l-9-4.5v-7Z" stroke={color} strokeWidth={1.8} strokeLinejoin="round" />
    <path d="M3 8.5 12 13l9-4.5M12 13v7" stroke={color} strokeWidth={1.8} strokeLinejoin="round" />
  </svg>
);
const IconChat: React.FC<{ color: string }> = ({ color }) => (
  <svg width={44} height={44} viewBox="0 0 24 24" fill="none">
    <path d="M4 5h16v10H8l-4 4V5Z" stroke={color} strokeWidth={1.8} strokeLinejoin="round" />
    <path d="M8 9h8M8 12h5" stroke={color} strokeWidth={1.8} strokeLinecap="round" />
  </svg>
);
const IconMega: React.FC<{ color: string }> = ({ color }) => (
  <svg width={44} height={44} viewBox="0 0 24 24" fill="none">
    <path d="M3 10v4h3l6 4V6L6 10H3Z" stroke={color} strokeWidth={1.8} strokeLinejoin="round" />
    <path d="M15 9a4 4 0 0 1 0 6" stroke={color} strokeWidth={1.8} strokeLinecap="round" />
  </svg>
);
const IconTruck: React.FC<{ color: string }> = ({ color }) => (
  <svg width={44} height={44} viewBox="0 0 24 24" fill="none">
    <path d="M2 7h11v9H2z" stroke={color} strokeWidth={1.8} strokeLinejoin="round" />
    <path d="M13 10h4l4 3v3h-8v-6Z" stroke={color} strokeWidth={1.8} strokeLinejoin="round" />
    <circle cx={6} cy={18} r={1.7} fill={color} />
    <circle cx={17} cy={18} r={1.7} fill={color} />
  </svg>
);

const FEATURES: Feature[] = [
  { label: 'Atualiza preços', icon: IconTag },
  { label: 'Sincroniza estoque', icon: IconBox },
  { label: 'Responde perguntas', icon: IconChat },
  { label: 'Cria anúncios', icon: IconMega },
  { label: 'Acompanha pedidos', icon: IconTruck },
];

const CHIP_H = 150;
const CHIP_GAP = 38;
const LIST_TOP = 560;
const OFFSET = 12; // chips start shortly after the header caption begins

const cueFor = (k: number) => OFFSET + 14 * k - 1 * k * (k - 1); // hard-accelerating interval

export const FeatureChips: React.FC = () => {
  const frame = useCurrentFrame();
  const macroIn = interpolate(frame, [0, 8], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });

  return (
    <AbsoluteFill style={{ backgroundColor: NAVY, opacity: macroIn }}>
      <AbsoluteFill style={{ background: 'radial-gradient(900px 1100px at 50% 20%, rgba(14,137,255,0.14), transparent 60%)' }} />

      <BigCaption
        startFrame={0}
        fontSize={100}
        top={210}
        lines={[[{ text: 'O' }, { text: 'que' }, { text: 'sua' }, { text: 'IA', accent: true }, { text: 'passa' }, { text: 'a' }, { text: 'fazer:' }]]}
      />

      {FEATURES.map((f, k) => {
        const cue = cueFor(k);
        const dealT = interpolate(frame, [cue, cue + 10], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: DEAL_EASE });
        const settleT = interpolate(frame, [cue + 10, cue + 15], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: SETTLE_EASE });
        const press = interpolate(frame, [cue + 15, cue + 17], [0.97, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
        const finalX = dealT < 1 ? -700 * (1 - dealT) : -30 * (1 - settleT);
        const rot = dealT < 1 ? (1 - dealT) * -8 : 0;
        const scale = (0.9 + 0.1 * dealT) * press;
        const opacity = interpolate(frame, [cue, cue + 4], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
        const y = LIST_TOP + k * (CHIP_H + CHIP_GAP);
        const Icon = f.icon;
        const landGlow = interpolate(frame, [cue + 15, cue + 21], [0.4, 0], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });

        return (
          <div
            key={f.label}
            style={{
              position: 'absolute', left: 90, right: 90, top: y, height: CHIP_H,
              opacity, transform: `translateX(${finalX}px) rotate(${rot}deg) scale(${scale})`,
            }}
          >
            <div
              style={{
                width: '100%', height: '100%', borderRadius: 26, background: OFFWHITE,
                display: 'flex', alignItems: 'center', gap: 28, padding: '0 40px', boxSizing: 'border-box',
                boxShadow: `0 18px 40px rgba(0,0,0,0.32), 0 0 ${20 + landGlow * 60}px rgba(14,137,255,${0.25 + landGlow})`,
              }}
            >
              <div style={{ width: 76, height: 76, borderRadius: 20, background: 'rgba(14,137,255,0.12)', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
                <Icon color={BLUE} />
              </div>
              <div style={{ fontFamily: FONT, fontWeight: 700, fontSize: 62, color: '#22222E' }}>{f.label}</div>
            </div>
          </div>
        );
      })}
    </AbsoluteFill>
  );
};
