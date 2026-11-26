// Video principal P18 (formato entrevista): video a pantalla completa + gráficos de marca integrados.
// Todo sale del JSON que genera _work/armar_montaje.py: tramos, subtítulos y marcas de gráficos/sonido.
import React from 'react';
import {AbsoluteFill, Audio, Sequence, interpolate, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import {VideoTrack, Segment} from '../components/VideoTrack';
import {Captions, Chunk} from '../components/Captions';
import {BrandWipe, EndCard, Header, HeadlineBlock, LowerThird, QuestionCard, Scrims} from '../components/Overlays';
import {SAFE} from '../brand/tokens';

export type Sfx = {at: number; file: string; vol: number; rate?: number};
export type Grafs = {
  titulo?: {from: number; dur: number; text: string; category?: string; source?: string};
  zocalos?: {from: number; dur: number; name: string; role: string}[];
  preguntas?: {from: number; dur: number; n: number; total: number; text: string}[];
  barridos?: number[];
  cierre?: {from: number; dur: number};
  ocultarSubs?: {from: number; to: number}[];
  musica?: {file: string; points: [number, number][]};
  sfx?: Sfx[];
};
export type EntrevistaData = {
  fps: number;
  durationInFrames: number;
  video: string;
  voz: string;
  segments: Segment[];
  captions: Chunk[];
  graficos: Grafs;
};

const TitleDim: React.FC<{dur: number}> = ({dur}) => {
  const f = useCurrentFrame();
  const d = interpolate(f, [0, 8, dur - 10, dur], [0, 1, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return <AbsoluteFill style={{background: `rgba(12,22,17,${0.5 * d})`, backdropFilter: `blur(${8 * d}px)`}} />;
};

const captionsVisible =(chunks: Chunk[], hide: {from: number; to: number}[], fps: number): Chunk[] =>
  // se oculta un subtítulo sólo si arranca dentro de una ventana (título o pregunta en pantalla)
  chunks.filter((c) => !hide.some((h) => c.start * fps + 2 >= h.from && c.start * fps < h.to));

export const Entrevista: React.FC<{data: EntrevistaData}> = ({data}) => {
  const {fps} = useVideoConfig();
  const g = data.graficos;
  const music = g.musica;
  const subs = captionsVisible(data.captions, g.ocultarSubs ?? [], fps);
  return (
    <AbsoluteFill style={{background: '#0E1913'}}>
      <VideoTrack segments={data.segments} video={data.video} fps={fps} />
      <Scrims />
      <Header delay={g.titulo ? g.titulo.from : 0} />
      <Captions chunks={subs} bottom={SAFE.bottom + 60} />

      {g.titulo ? (
        <Sequence from={g.titulo.from} durationInFrames={g.titulo.dur}>
          <TitleDim dur={g.titulo.dur} />
          <div style={{position: 'absolute', left: SAFE.side, right: SAFE.right - 40, top: 620}}>
            <HeadlineBlock
              title={g.titulo.text}
              category={g.titulo.category}
              source={g.titulo.source}
              size={92}
              exitAt={g.titulo.dur - 10}
            />
          </div>
        </Sequence>
      ) : null}

      {(g.zocalos ?? []).map((z, i) => (
        <Sequence key={`z${i}`} from={z.from} durationInFrames={z.dur}>
          <LowerThird name={z.name} role={z.role} dur={z.dur} />
        </Sequence>
      ))}

      {(g.preguntas ?? []).map((q, i) => (
        <Sequence key={`q${i}`} from={q.from} durationInFrames={q.dur}>
          <QuestionCard n={q.n} total={q.total} text={q.text} dur={q.dur} />
        </Sequence>
      ))}

      {(g.barridos ?? []).map((at, i) => (
        <Sequence key={`w${i}`} from={at - 8} durationInFrames={18}>
          <BrandWipe dur={18} />
        </Sequence>
      ))}

      {g.cierre ? (
        <Sequence from={g.cierre.from} durationInFrames={g.cierre.dur}>
          <EndCard dur={g.cierre.dur} />
        </Sequence>
      ) : null}

      {/* Audio: voz (protagonista), cama musical con automatización de volumen, efectos puntuales */}
      <Audio src={staticFile(data.voz)} />
      {music ? (
        <Audio
          src={staticFile(music.file)}
          volume={(f) =>
            interpolate(
              f,
              music.points.map((p) => p[0]),
              music.points.map((p) => p[1]),
              {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'},
            )
          }
        />
      ) : null}
      {(g.sfx ?? []).map((s, i) => (
        <Sequence key={`s${i}`} from={Math.max(0, s.at)}>
          <Audio src={staticFile(s.file)} volume={s.vol} playbackRate={s.rate ?? 1} />
        </Sequence>
      ))}
    </AbsoluteFill>
  );
};
