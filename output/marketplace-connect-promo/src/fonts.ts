// Loads the real brand typeface (SF Pro Rounded, macOS system font) from a
// bundled TTF so render workers (which may run headless / without the font
// installed) still get the correct face. Uses the standard Remotion
// delayRender/continueRender font-loading pattern.
import { continueRender, delayRender, staticFile } from 'remotion';

export const FONT_FAMILY = 'SF Pro Rounded';

let loaded = false;

export const ensureFontLoaded = () => {
  if (loaded) return;
  loaded = true;
  const handle = delayRender('Loading SF Pro Rounded');
  const font = new FontFace(FONT_FAMILY, `url(${staticFile('fonts/SFNSRounded.ttf')})`);
  font
    .load()
    .then((loadedFont) => {
      (document.fonts as any).add(loadedFont);
      continueRender(handle);
    })
    .catch((err) => {
      console.error('Font failed to load', err);
      continueRender(handle);
    });
};
