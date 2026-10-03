// HubConnect -- the centerpiece "quadros interagindo" beat the brief asked
// for. Adapted from shots/ui-entrance/integration-hub-map.md (demo:
// demos/ui-entrance/integration-hub-map/IntegrationHubMap.tsx). The original
// card's structure is "old page flips into a new hub page, THEN five
// satellite icons + pipes connect in a two-beat"; there is no "old page" in
// this product story, so the page-flip framing device is dropped (a
// structural simplification, noted in the delivery report) while the load-
// bearing motion law is kept verbatim: (1) icons appear in ONE beat, (2) a
// second beat later all pipes grow together, (3) a continuous flow pulse
// runs source->hub forever after -- "同时" is this card's identity, per its
// own documented pitfall history. Layout is re-composed for portrait: 3 AI
// tiles on top, 6 marketplace tiles on bottom, in two mirrored pillars
// converging on the Marketplace Connect hub badge in the middle.
//
// Logo policy (hard rule this session): every icon on screen must come from
// a real brand asset file, never an AI-redrawn mark. Claude / ChatGPT /
// Codex / Mercado Livre / Shopee / Amazon all have real source files and are
// rendered from them. Shein, TikTok Shop and Magalu have NO real logo asset
// available in this project -- rather than invent their marks, they are
// rendered as plain typographic name chips (our own brand font/color, no
// icon glyph at all), which cannot be mistaken for their real logos.
import { AbsoluteFill, Img, staticFile, interpolate, useCurrentFrame, Easing } from 'remotion';
import { NAVY, NAVY_DEEP, BLUE, OFFWHITE, FONT } from '../tokens';
import { BigCaption } from '../lib/BigCaption';
import { mulberry32 } from '../lib/rand';

export const HUB_CONNECT_DURATION = 150;

const W = 1080;
const H = 1920;
const HUB = { x: W / 2, y: 860 };

type Tile = { key: string; x: number; y: number; kind: 'img' | 'text'; src?: string; label: string; w: number; h: number };

const AI_TILES: Tile[] = [
  { key: 'claude', x: 230, y: 280, kind: 'img', src: 'logos/claude.png', label: 'Claude', w: 210, h: 210 },
  { key: 'chatgpt', x: 540, y: 250, kind: 'img', src: 'logos/chatgpt.png', label: 'ChatGPT', w: 260, h: 98 },
  { key: 'codex', x: 850, y: 280, kind: 'img', src: 'logos/codex.png', label: 'Codex', w: 220, h: 132 },
];

const MP_TILES: Tile[] = [
  { key: 'ml', x: 210, y: 1220, kind: 'img', src: 'logos/mercadolivre.png', label: 'Mercado Livre', w: 168, h: 136 },
  { key: 'shopee', x: 540, y: 1220, kind: 'img', src: 'logos/shopee.png', label: 'Shopee', w: 118, h: 148 },
  { key: 'amazon', x: 870, y: 1220, kind: 'img', src: 'logos/amazon.png', label: 'Amazon', w: 150, h: 112 },
  { key: 'shein', x: 210, y: 1460, kind: 'text', label: 'Shein', w: 190, h: 100 },
  { key: 'tiktokshop', x: 540, y: 1460, kind: 'text', label: 'TikTok Shop', w: 190, h: 100 },
  { key: 'magalu', x: 870, y: 1460, kind: 'text', label: 'Magalu', w: 190, h: 100 },
];

const ALL_TILES = [...AI_TILES, ...MP_TILES];

const rand = mulberry32(20260911);
const RECTS = Array.from({ length: 6 }, () => ({
  x: rand() * W,
  y: rand() * H,
  w: 70 + rand() * 130,
  h: 50 + rand() * 90,
  ph: rand() * Math.PI * 2,
}));

// quadratic bezier "S" path between a tile edge point and the hub edge
const pipePath = (x1: number, y1: number, x2: number, y2: number) => {
  const mx = (x1 + x2) / 2;
  const my = (y1 + y2) / 2;
  return `M ${x1} ${y1} Q ${mx} ${my} ${x2} ${y2}`;
};

const TILE_CUE = 40; // all 9 tiles pop within a couple frames of this (one beat)
const PIPE_CUE = 64; // second beat: all pipes grow together
const PIPE_GROW = 11;

const HubTile: React.FC<{ t: Tile; index: number; frame: number; breathe: number }> = ({ t, index, frame, breathe }) => {
  const cue = TILE_CUE + index * 1; // <=8f spread across 9 tiles -> reads as one beat, not a queue
  const t01 = interpolate(frame, [cue, cue + 12], [0, 1], {
    extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.bezier(0.2, 1.2, 0.3, 1),
  });
  if (t01 <= 0) return null;
  const on = interpolate(frame, [PIPE_CUE, PIPE_CUE + PIPE_GROW], [0.35, 1], {
    extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
  });
  const glow = 14 + on * (26 + breathe * 10);
  // text-only chips (Shein/TikTok Shop/Magalu -- no real logo asset, see
  // HubConnect header note) get a WIDER box than the square logo tiles so
  // their label can clear aesthetic-rules Q11's aux-text floor (>=3% of
  // this project's 1920px frame height, ~58px) without wrapping into an
  // illegibly cramped column -- text size was the QA-flagged failure here,
  // not layout, so the fix widens the box rather than shrinking the type.
  const boxW = t.kind === 'text' ? 300 : 220;
  const boxH = 220;
  return (
    <div
      style={{
        position: 'absolute', left: t.x - boxW / 2, top: t.y - boxH / 2, width: boxW, height: boxH,
        opacity: t01, transform: `translateY(${(1 - t01) * 26}px) scale(${0.82 + 0.18 * t01})`,
      }}
    >
      <div
        style={{
          width: '100%', height: '100%', borderRadius: 30, background: OFFWHITE,
          display: 'flex', alignItems: 'center', justifyContent: 'center', flexDirection: 'column', gap: 10,
          boxShadow: `0 0 ${glow}px rgba(14,137,255,${0.22 + on * 0.28}), 0 18px 40px rgba(0,0,0,0.35)`,
        }}
      >
        {t.kind === 'img' ? (
          <Img src={staticFile(t.src!)} style={{ width: t.w, height: t.h, maxWidth: 158, maxHeight: 120, objectFit: 'contain' }} />
        ) : (
          <div style={{ fontFamily: FONT, fontWeight: 700, fontSize: 80, lineHeight: 1.05, color: '#22222E', textAlign: 'center', padding: '0 14px' }}>{t.label}</div>
        )}
      </div>
    </div>
  );
};

export const HubConnect: React.FC = () => {
  const frame = useCurrentFrame();

  const macroIn = interpolate(frame, [0, 10], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });

  // hub materializes first (0-30)
  const hubIn = interpolate(frame, [6, 30], [0, 1], {
    extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.bezier(0.2, 1.1, 0.3, 1),
  });
  const hubPulse = interpolate(frame, [26, 33, 40], [0, 0.14, 0], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });

  const allPipeOn = PIPE_CUE + 8 * 1 + PIPE_GROW; // last tile's pipe fully grown
  const breathe = frame > allPipeOn ? 0.5 + 0.5 * Math.sin((frame - allPipeOn) * 0.14) : 0;

  const mapIn = interpolate(frame, [18, 40], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });

  return (
    <AbsoluteFill style={{ backgroundColor: NAVY, opacity: macroIn }}>
      <AbsoluteFill style={{ background: `radial-gradient(900px 1400px at 50% 50%, ${NAVY_DEEP}, ${NAVY} 70%)` }} />

      {/* faint neon rectangle texture, brand-blue monochrome (not the rainbow
          of the source demo, which would read off-brand here) */}
      {RECTS.map((r, i) => {
        const on = interpolate(frame, [10 + i * 3, 24 + i * 3], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
        const flick = 0.6 + 0.4 * Math.sin(frame * 0.08 + r.ph);
        return (
          <div
            key={i}
            style={{
              position: 'absolute', left: r.x, top: r.y, width: r.w, height: r.h, borderRadius: 12,
              border: `2px solid rgba(14,137,255,${0.4 * on * flick})`,
              boxShadow: `0 0 16px rgba(14,137,255,${0.28 * on * flick})`,
            }}
          />
        );
      })}

      {/* pipes: quadratic curves from every tile to the hub, second beat */}
      <svg width={W} height={H} style={{ position: 'absolute', inset: 0, opacity: mapIn }}>
        <defs>
          <filter id="hubGlow" filterUnits="userSpaceOnUse" x={0} y={0} width={W} height={H}>
            <feGaussianBlur stdDeviation="6" result="b" />
            <feMerge>
              <feMergeNode in="b" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
        </defs>
        {ALL_TILES.map((t, i) => {
          const cue = PIPE_CUE + i * 1;
          const grow = interpolate(frame, [cue, cue + PIPE_GROW], [0, 1], {
            extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.out(Easing.quad),
          });
          if (grow <= 0) return null;
          const isAI = i < AI_TILES.length;
          const edgeY = isAI ? t.y + 100 : t.y - 100;
          const hubEdgeY = isAI ? HUB.y - 96 : HUB.y + 96;
          const d = pipePath(t.x, edgeY, HUB.x, hubEdgeY);
          const len = Math.hypot(t.x - HUB.x, edgeY - hubEdgeY) * 1.15;
          const pulse = frame > allPipeOn ? 0.75 + 0.25 * Math.sin((frame - allPipeOn) * 0.15 + i) : 1;
          const flowOffset = -((frame - cue) * 3.6 + i * 41);
          const flowIn = interpolate(frame, [cue + PIPE_GROW, cue + PIPE_GROW + 8], [0, 1], {
            extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
          });
          return (
            <g key={t.key} filter="url(#hubGlow)">
              <path d={d} fill="none" stroke={BLUE} strokeWidth={9} strokeLinecap="round" strokeDasharray={`${len * grow} ${len + 40}`} opacity={0.85 * pulse} />
              <path d={d} fill="none" stroke="rgba(255,255,255,0.85)" strokeWidth={2.6} strokeLinecap="round" strokeDasharray={`${len * grow} ${len + 40}`} opacity={0.8 * pulse} />
              {grow >= 1 && flowIn > 0 ? (
                <path
                  d={d} fill="none" stroke="#ffffff" strokeWidth={6} strokeLinecap="round"
                  strokeDasharray="14 44" strokeDashoffset={flowOffset} opacity={0.9 * flowIn}
                />
              ) : null}
            </g>
          );
        })}
      </svg>

      {/* tiles */}
      {ALL_TILES.map((t, i) => (
        <HubTile key={t.key} t={t} index={i} frame={frame} breathe={breathe} />
      ))}

      {/* hub badge: Marketplace Connect (real Tiops icon) */}
      <div
        style={{
          position: 'absolute', left: HUB.x - 96, top: HUB.y - 96, width: 192, height: 192,
          opacity: hubIn, transform: `scale(${0.7 + 0.3 * hubIn})`,
        }}
      >
        <div
          style={{
            width: '100%', height: '100%', borderRadius: '50%', background: OFFWHITE,
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            boxShadow: `0 0 ${50 + hubPulse * 180}px rgba(14,137,255,${0.45 + hubPulse}), 0 20px 50px rgba(0,0,0,0.4)`,
          }}
        >
          <Img src={staticFile('logos/tiops-icon.png')} style={{ width: 96, height: 'auto' }} />
        </div>
      </div>

      <BigCaption
        startFrame={92}
        fontSize={84}
        bottom={40}
        lines={[
          [{ text: 'Conecta' }, { text: 'qualquer', accent: true }, { text: 'IA' }],
          [{ text: 'a' }, { text: 'qualquer', accent: true }, { text: 'marketplace.' }],
        ]}
      />
    </AbsoluteFill>
  );
};
