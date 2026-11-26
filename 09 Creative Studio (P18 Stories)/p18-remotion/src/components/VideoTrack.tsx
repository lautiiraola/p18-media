// Pista de video a pantalla completa: une los tramos elegidos del crudo y cambia el encuadre en cada corte
// (plano general / medio / cerrado) para que los cortes de montaje no se vean como saltos.
import React from 'react';
import {AbsoluteFill, OffthreadVideo, Sequence, interpolate, staticFile, useCurrentFrame, Easing} from 'remotion';

export type Framing = {scale: number; x: number; y: number}; // x,y: punto de interés normalizado (0..1)
export type Segment = {
  id: string;
  src: number; // segundo de inicio en el proxy
  from: number; // frame de inicio en la línea de tiempo editada
  dur: number; // duración en frames
  framing: Framing;
  push?: number; // zoom lento dentro del tramo (0.02 = 2 %)
};

const FramedVideo: React.FC<{seg: Segment; video: string; fps: number}> = ({seg, video, fps}) => {
  const f = useCurrentFrame();
  const push = seg.push ?? 0.025;
  const drift = interpolate(f, [0, seg.dur], [0, push], {
    extrapolateRight: 'clamp',
    easing: Easing.inOut(Easing.sin),
  });
  const s = seg.framing.scale * (1 + drift);
  // Mantener el punto de interés cerca del centro sin mostrar bordes vacíos
  const maxShift = (s - 1) / (2 * s);
  const tx = Math.max(-maxShift, Math.min(maxShift, 0.5 - seg.framing.x));
  const ty = Math.max(-maxShift, Math.min(maxShift, 0.5 - seg.framing.y));
  return (
    <AbsoluteFill style={{overflow: 'hidden'}}>
      <AbsoluteFill
        style={{
          transform: `scale(${s}) translate(${tx * 100}%, ${ty * 100}%)`,
          transformOrigin: 'center center',
        }}
      >
        <OffthreadVideo
          src={staticFile(video)}
          startFrom={Math.round(seg.src * fps)}
          muted
          style={{width: '100%', height: '100%', objectFit: 'cover'}}
        />
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

export const VideoTrack: React.FC<{segments: Segment[]; video: string; fps: number}> = ({segments, video, fps}) => (
  <AbsoluteFill style={{background: '#000'}}>
    {segments.map((seg) => (
      <Sequence key={seg.id} from={seg.from} durationInFrames={seg.dur} premountFor={30}>
        <FramedVideo seg={seg} video={video} fps={fps} />
      </Sequence>
    ))}
  </AbsoluteFill>
);
