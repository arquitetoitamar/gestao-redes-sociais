// Shared narrative-caption component. aesthetic-rules.md Q11: text meant to be
// read must hit an effective height of >=5.2% of the frame height (narrative
// captions) computed on the ACTUAL rendered frame (1920 tall for this 9:16
// project, not the 1080 the rule's px examples assume) -- so sizes here are
// deliberately large. Word-by-word letterpress entrance (scale+blur->0), one
// accent word per line in BLUE italic, matching the brand-ink-open / paper
// title-card "入场三件套" formula used across every shot in this project.
import { interpolate, useCurrentFrame, Easing } from 'remotion';
import { BLUE, OFFWHITE, FONT } from '../tokens';

export type CaptionLine = { text: string; accent?: boolean }[];

export const BigCaption: React.FC<{
  lines: CaptionLine[];
  startFrame: number;
  fontSize?: number;
  color?: string;
  bottom?: number;
  top?: number;
}> = ({ lines, startFrame, fontSize = 88, color = OFFWHITE, bottom = 220, top }) => {
  const frame = useCurrentFrame() - startFrame;
  if (frame < 0) return null;
  let globalIdx = 0;
  return (
    <div
      style={{
        position: 'absolute',
        left: 90,
        right: 90,
        ...(top === undefined ? { bottom } : { top }),
        textAlign: 'center',
        fontFamily: FONT,
        fontWeight: 700,
        fontSize,
        lineHeight: 1.14,
        letterSpacing: '-0.01em',
      }}
    >
      {lines.map((words, li) => (
        <div key={li} style={{ display: 'flex', flexWrap: 'wrap', justifyContent: 'center', columnGap: '0.28em' }}>
          {words.map((w, wi) => {
            const i = globalIdx++;
            const delay = 3 + i * 3;
            const t = interpolate(frame, [delay, delay + 10], [0, 1], {
              extrapolateLeft: 'clamp',
              extrapolateRight: 'clamp',
              easing: Easing.bezier(0.2, 0.75, 0.3, 1),
            });
            return (
              <span
                key={wi}
                style={{
                  display: 'inline-block',
                  opacity: t,
                  transform: `scale(${1.22 - 0.22 * t})`,
                  filter: `blur(${(1 - t) * 6}px)`,
                  fontStyle: w.accent ? 'italic' : 'normal',
                  color: w.accent ? BLUE : color,
                }}
              >
                {w.text}
              </span>
            );
          })}
        </div>
      ))}
    </div>
  );
};
