// Brand design tokens for Marketplace Connect (Tiops) — validated this
// session, reused verbatim across every shot. Do not invent new brand colors;
// extend this palette only with tints/shades derived from these three.
export const NAVY = '#1A1A2E';
export const NAVY_DEEP = '#111120';
export const BLUE = '#0E89FF';
export const BLUE_SOFT = 'rgba(14,137,255,0.55)';
export const OFFWHITE = '#F5F3F0';
export const FONT = 'SF Pro Rounded, -apple-system, BlinkMacSystemFont, sans-serif';
export const MONO = 'ui-monospace, SFMono-Regular, Menlo, monospace';

// energetic/tone axis per pipeline.md "brand -> motion params" table:
// this product reads as "ativo/startup" energy with a "profissional confiável"
// (B2B/fintech-adjacent) tone — a blend of the "专业信赖" and "活力大胆" presets,
// since the audience is marketplace sellers who want speed AND trust.
// -> main durations ~20-24f, bezier(0.2,0.9,0.25,1)-ish overshoot y1 1.05-1.12,
//    squash kept low (0.1-0.18), never zero (fully "冷" b2b would read cold for
//    a social/video ad).
