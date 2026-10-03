// HeroCard -- adapted from shots/opening/spotlight-hero-card.md (demo:
// demos/opening/spotlight-hero-card/SpotlightHeroCard.tsx). The original rig
// is PageCam-driven (roving spotlight locks on a card cut from a real page
// screenshot). This project has no real dashboard page to replicate -- Q1
// explicitly allows hand-built UI outside "replicate an existing page"
// scenes, provided quality/clarity hold up -- so the "page" is replaced with
// a brand void (navy + soft blue vignette) and the card is an original
// composition built from the REAL Claude app-icon asset (never a redrawn
// logo). Motion kept 1:1: roving spotlight w/ waypoints -> lock -> card rise
// (overshoot) -> 54f sine-bob hover -> two-lap perimeter beam -> gentle
// reseat. Single hero, one complete >=3s arc (Q5/R3).
import { AbsoluteFill, Img, interpolate, staticFile, useCurrentFrame, Easing } from 'remotion';
import { NAVY, BLUE, OFFWHITE, FONT } from '../tokens';
import { BigCaption } from '../lib/BigCaption';

export const HERO_CARD_DURATION = 154;

const CARD_W = 460;
const CARD_H = 460;
const RADIUS = 40;

const POP_EASE = Easing.bezier(0.2, 1.25, 0.3, 1);
const RESEAT_EASE = Easing.bezier(0.4, 0, 0.3, 1.05);

export const HeroCard: React.FC = () => {
  const frame = useCurrentFrame();

  const macroIn = interpolate(frame, [0, 8], [0, 1], {
    extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.bezier(0.3, 0, 0.2, 1),
  });

  // roving spotlight (screen-space %), waypoints then locks on the card's
  // resting position (50%, 44%)
  const spotEase = Easing.bezier(0.4, 0, 0.3, 1);
  const spotX = interpolate(frame, [4, 8, 16, 22, 28, 48], [28, 28, 66, 40, 50, 50], {
    extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: spotEase,
  });
  const spotY = interpolate(frame, [4, 8, 16, 22, 28, 48], [24, 24, 36, 50, 44, 44], {
    extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: spotEase,
  });
  const spotOn = interpolate(frame, [2, 10], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });

  const poolBase = interpolate(frame, [22, 32, 48], [560, 400, 340], {
    extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.bezier(0.4, 0, 0.3, 1),
  });
  const poolPulse = interpolate(frame, [32, 36, 41], [0, 0.08, 0], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
  const poolR = poolBase * (1 + poolPulse);
  const vignette = interpolate(frame, [22, 32, 48], [0.2, 0.4, 0.5], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });

  // slow push-in on the whole void (subtle 3D depth, no real page to camera)
  const pushT = interpolate(frame, [32, 48], [0, 1], {
    extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.bezier(0.35, 0, 0.2, 1),
  });
  const worldScale = 1 + pushT * 0.14;
  const worldRotY = pushT * 6;

  // card rise (48->58 overshoot) -> hover (58->128, 70f sine bob) -> reseat
  // (128->146). Widened from the first pass's 54f hover (lock->touchdown was
  // running ~16% short of the shot card's own documented ~98f/3.3s recipe,
  // flagged by independent QA against R3's "always err slower" precedent) to
  // land lock->touchdown at ~98f, matching the card.
  const rise = interpolate(frame, [48, 58], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: POP_EASE });
  const reseat = interpolate(frame, [128, 146], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: RESEAT_EASE });
  const lift = rise * (1 - reseat);
  const bob = Math.sin(((frame - 58) / 40) * Math.PI * 2) * 6 * lift;
  const z = 60 * lift + bob;
  const landed = frame >= 146;
  const press = interpolate(frame, [142, 145, 146], [1, 0.997, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
  const shadow = `0 ${10 * lift}px ${16 + 14 * lift}px rgba(0,0,0,${0.28 * lift}), 0 ${50 * lift}px ${96 * lift}px rgba(0,0,0,${0.3 * lift})`;

  // perimeter beam: two laps (60-74 fast/bright, 80-100 slower/weaker)
  const beam1Prog = interpolate(frame, [60, 74], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.linear });
  const beam1On = frame >= 59 && frame <= 75;
  const beam2Prog = interpolate(frame, [80, 100], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.bezier(0.4, 0, 0.4, 1) });
  const beam2On = frame >= 79 && frame <= 101;
  const beamTrail = interpolate(frame, [100, 128], [0.35, 0], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
  const bw = CARD_W + 6;
  const bh = CARD_H + 6;

  const cardInScale = 0.86 + 0.14 * Math.min(1, rise * 1.4);

  return (
    <AbsoluteFill style={{ backgroundColor: NAVY }}>
      <AbsoluteFill style={{ background: 'radial-gradient(1000px 900px at 50% 30%, rgba(14,137,255,0.1), transparent 60%)' }} />

      {/* ambient dot grid -- brand texture, not fake UI */}
      <AbsoluteFill
        style={{
          opacity: 0.16,
          backgroundImage: 'radial-gradient(rgba(245,243,240,0.5) 1.5px, transparent 1.5px)',
          backgroundSize: '54px 54px',
        }}
      />

      <AbsoluteFill style={{ opacity: macroIn, perspective: 1400 }}>
        <div
          style={{
            position: 'absolute', inset: 0, transformStyle: 'preserve-3d',
            transform: `scale(${worldScale}) rotateY(${worldRotY}deg)`,
          }}
        >
          {/* the levitating hero card */}
          <div
            style={{
              position: 'absolute', left: '50%', top: '44%',
              transform: `translate(-50%,-50%) translateZ(${z}px) scale(${cardInScale * press})`,
              opacity: Math.min(1, rise * 1.6),
              transformOrigin: 'center center', transformStyle: 'preserve-3d',
            }}
          >
            <div style={{ position: 'relative', width: CARD_W, height: CARD_H }}>
              <div
                style={{
                  position: 'absolute', inset: 0, borderRadius: RADIUS, overflow: 'hidden',
                  background: OFFWHITE, boxShadow: landed ? '0 20px 60px rgba(0,0,0,0.35)' : shadow,
                  display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center',
                }}
              >
                <Img src={staticFile('logos/claude.png')} style={{ width: 220, height: 220, borderRadius: 28, display: 'block' }} />
                <div style={{ marginTop: 26, fontFamily: FONT, fontWeight: 700, fontSize: 64, color: '#22222E' }}>Claude</div>
                <div
                  style={{
                    position: 'absolute', inset: 0,
                    background: 'linear-gradient(160deg, rgba(255,255,255,0.35), transparent 40%)',
                    opacity: lift, pointerEvents: 'none',
                  }}
                />
              </div>

              {/* perimeter beam */}
              {(beam1On || beam2On) && lift > 0.4 ? (
                <svg
                  width={bw} height={bh} viewBox={`0 0 ${bw} ${bh}`}
                  style={{
                    position: 'absolute', left: -3, top: -3, overflow: 'visible', pointerEvents: 'none',
                    opacity: beam1On ? 1 : 0.62,
                    filter: `drop-shadow(0 0 8px ${BLUE}) drop-shadow(0 0 22px rgba(150,205,255,0.6))`,
                  }}
                >
                  <rect
                    x={2} y={2} width={bw - 4} height={bh - 4} rx={RADIUS} fill="none"
                    stroke={BLUE} strokeWidth={beam1On ? 6 : 4} strokeLinecap="round"
                    pathLength={1} strokeDasharray="0.14 1"
                    strokeDashoffset={-(beam1On ? beam1Prog : beam2Prog)}
                  />
                  <rect
                    x={2} y={2} width={bw - 4} height={bh - 4} rx={RADIUS} fill="none"
                    stroke="rgba(255,255,255,0.95)" strokeWidth={beam1On ? 2.5 : 1.75} strokeLinecap="round"
                    pathLength={1} strokeDasharray="0.14 1"
                    strokeDashoffset={-(beam1On ? beam1Prog : beam2Prog)}
                  />
                </svg>
              ) : null}

              {beamTrail > 0.01 ? (
                <div style={{ position: 'absolute', inset: -3, borderRadius: RADIUS + 3, border: `2px solid ${BLUE}`, opacity: beamTrail, pointerEvents: 'none' }} />
              ) : null}
            </div>
          </div>
        </div>

        {/* roving / locking spotlight */}
        <AbsoluteFill
          style={{
            background: `radial-gradient(${poolR}px ${poolR * 1.15}px at ${spotX}% ${spotY}%, rgba(180,215,255,0.28), rgba(180,215,255,0.08) 45%, rgba(4,4,10,${vignette * spotOn}) 100%)`,
            pointerEvents: 'none', opacity: spotOn,
          }}
        />
      </AbsoluteFill>

      <BigCaption
        startFrame={70}
        fontSize={98}
        lines={[
          [{ text: 'Um' }, { text: 'agente' }, { text: 'de' }, { text: 'IA,' }],
          [{ text: 'qualquer', accent: true }, { text: 'marketplace.', accent: true }],
        ]}
      />
    </AbsoluteFill>
  );
};
