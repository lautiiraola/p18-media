import React from 'react';
import {Composition} from 'remotion';
import {P18Story} from './compositions/P18Story';
import {CANVAS} from './tokens/tokens';
import {StoryProps} from './types';

// Una sola composición genérica. Cada video aporta sus datos con --props y sus assets con --public-dir.
export const Root: React.FC = () => (
  <Composition
    id="P18Story"
    component={P18Story}
    width={CANVAS.width}
    height={CANVAS.height}
    fps={CANVAS.fps}
    durationInFrames={60}
    defaultProps={{data: null} as StoryProps}
    calculateMetadata={({props}) => ({
      durationInFrames: props.data?.durationInFrames ?? 60,
      fps: props.data?.fps ?? CANVAS.fps,
    })}
  />
);
