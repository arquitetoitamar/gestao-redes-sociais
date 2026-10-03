// Main -- shot orchestrator. Single source-of-truth SHOTS table (frame
// offsets derived from each shot's own duration constant, never hard-coded
// twice) + a declarative SFX cue table whose `from` values are written as
// relative expressions off that table (S2/S3: time-line moves, cue table
// follows automatically; never a bare frame number).
//
// BGM: intentionally omitted in this delivery (scope simplification, see the
// hand-off report) -- this project ships SFX-only. All cuts share one navy
// brand ground so shot boundaries are plain hard cuts on a matched
// background ("hidden cut" via color continuity) rather than a transition
// effect; every shot's own foreground content fades in over its own first
// 6-12 frames.
import React from 'react';
import { AbsoluteFill, Audio, Sequence, staticFile } from 'remotion';
import { ensureFontLoaded } from './fonts';
import { BrandOpen, BRAND_OPEN_DURATION } from './shots/BrandOpen';
import { HeroCard, HERO_CARD_DURATION } from './shots/HeroCard';
import { HubConnect, HUB_CONNECT_DURATION } from './shots/HubConnect';
import { TitleCard, TITLE_CARD_DURATION } from './shots/TitleCard';
import { FeatureChips, FEATURE_CHIPS_DURATION } from './shots/FeatureChips';
import { Outro, OUTRO_DURATION } from './shots/Outro';

const brandOpen = { from: 0, duration: BRAND_OPEN_DURATION };
const heroCard = { from: brandOpen.from + brandOpen.duration, duration: HERO_CARD_DURATION };
const hubConnect = { from: heroCard.from + heroCard.duration, duration: HUB_CONNECT_DURATION };
const titleCard = { from: hubConnect.from + hubConnect.duration, duration: TITLE_CARD_DURATION };
const featureChips = { from: titleCard.from + titleCard.duration, duration: FEATURE_CHIPS_DURATION };
const outro = { from: featureChips.from + featureChips.duration, duration: OUTRO_DURATION };

export const SHOTS = { brandOpen, heroCard, hubConnect, titleCard, featureChips, outro };
export const TOTAL_DURATION = outro.from + outro.duration;

const SFX: { from: number; src: string; volume: number; note: string }[] = [
  { from: SHOTS.brandOpen.from + 12, src: 'transition-soft.mp3', volume: 0.45, note: 'crosshair draws in' },
  { from: SHOTS.brandOpen.from + SHOTS.brandOpen.duration - 8, src: 'whoosh-fast.mp3', volume: 0.4, note: 'brand -> hero handoff' },
  { from: SHOTS.heroCard.from + 48, src: 'whoosh-big.mp3', volume: 0.55, note: 'hero card rises' },
  { from: SHOTS.heroCard.from + 70, src: 'sparkle-touch.mp3', volume: 0.38, note: 'perimeter beam' },
  { from: SHOTS.heroCard.from + 146, src: 'transition-snap.mp3', volume: 0.32, note: 'card reseats' },
  { from: SHOTS.hubConnect.from + 6, src: 'transition-soft.mp3', volume: 0.4, note: 'hub badge materializes' },
  { from: SHOTS.hubConnect.from + 40, src: 'whoosh-big.mp3', volume: 0.5, note: 'nine tiles burst in (one beat)' },
  { from: SHOTS.hubConnect.from + 64, src: 'sparkle.mp3', volume: 0.45, note: 'pipes connect (second beat)' },
  { from: SHOTS.titleCard.from + 2, src: 'swoosh-quick.mp3', volume: 0.35, note: 'title card in' },
  { from: SHOTS.featureChips.from + 12, src: 'swoosh-quick.mp3', volume: 0.4, note: 'chip 1 lands' },
  { from: SHOTS.featureChips.from + 34, src: 'transition-snap.mp3', volume: 0.36, note: 'chip 2 lands' },
  { from: SHOTS.featureChips.from + 46, src: 'swoosh-quick.mp3', volume: 0.32, note: 'chip 3 lands' },
  { from: SHOTS.featureChips.from + 56, src: 'transition-snap.mp3', volume: 0.28, note: 'chip 4 lands' },
  { from: SHOTS.featureChips.from + 64, src: 'swoosh-quick.mp3', volume: 0.25, note: 'chip 5 lands' },
  { from: SHOTS.outro.from + 0, src: 'riser-cine.mp3', volume: 0.32, note: 'group-photo assembly riser' },
  { from: SHOTS.outro.from + 80, src: 'impact-deep-whoosh.mp3', volume: 0.55, note: 'wordmark stamp -- full-film volume peak' },
  { from: SHOTS.outro.from + 96, src: 'sparkle.mp3', volume: 0.38, note: 'rule + CTA' },
];

export const AIFL_TOTAL = TOTAL_DURATION;

export const MarketplaceConnectPromo: React.FC = () => {
  ensureFontLoaded();

  return (
    <AbsoluteFill style={{ backgroundColor: '#1A1A2E' }}>
      <Sequence from={brandOpen.from} durationInFrames={brandOpen.duration}>
        <BrandOpen />
      </Sequence>
      <Sequence from={heroCard.from} durationInFrames={heroCard.duration}>
        <HeroCard />
      </Sequence>
      <Sequence from={hubConnect.from} durationInFrames={hubConnect.duration}>
        <HubConnect />
      </Sequence>
      <Sequence from={titleCard.from} durationInFrames={titleCard.duration}>
        <TitleCard />
      </Sequence>
      <Sequence from={featureChips.from} durationInFrames={featureChips.duration}>
        <FeatureChips />
      </Sequence>
      <Sequence from={outro.from} durationInFrames={outro.duration}>
        <Outro />
      </Sequence>

      {SFX.map((s, i) => (
        <Sequence key={i} from={s.from}>
          <Audio src={staticFile(`audio/${s.src}`)} volume={s.volume} />
        </Sequence>
      ))}
    </AbsoluteFill>
  );
};
