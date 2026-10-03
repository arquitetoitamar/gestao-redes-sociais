import { Composition } from 'remotion';
import { MarketplaceConnectPromo, TOTAL_DURATION } from './Main';
import { Corte, CorteProps } from './Corte';

export const Root: React.FC = () => {
  return (
    <>
    <Composition
      id="MarketplaceConnectPromo"
      component={MarketplaceConnectPromo}
      durationInFrames={TOTAL_DURATION}
      fps={30}
      width={1080}
      height={1920}
    />
      <Composition
        id="Corte"
        component={Corte}
        durationInFrames={900}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{ clip: 'cuts/c1.mp4', durationSec: 30, headline: ['TESTE'], hl: [0], words: [], pages: [], callouts: [] } as CorteProps}
        calculateMetadata={({ props }) => ({ durationInFrames: Math.ceil((props as CorteProps).durationSec * 30) })}
      />
    </>
  );
};
