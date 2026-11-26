// Banco de pruebas de gráficos sobre un cuadro del video (para revisar composición en stills)
import React from 'react';
import {AbsoluteFill, Img, Sequence, staticFile} from 'remotion';
import {Captions} from '../components/Captions';
import {EndCard, Header, HeadlineBlock, LowerThird, QuestionCard, Scrims} from '../components/Overlays';
import {SAFE} from '../brand/tokens';

const Frame: React.FC<{scale?: number; x?: number; y?: number}> = ({scale = 1, x = 0.5, y = 0.5}) => {
  const max = (scale - 1) / (2 * scale);
  const tx = Math.max(-max, Math.min(max, 0.5 - x));
  const ty = Math.max(-max, Math.min(max, 0.5 - y));
  return (
    <AbsoluteFill style={{transform: `scale(${scale}) translate(${tx * 100}%, ${ty * 100}%)`}}>
      <Img src={staticFile('test/frame.jpg')} style={{width: '100%', height: '100%', objectFit: 'cover'}} />
    </AbsoluteFill>
  );
};

const demoCaption = [
  {
    start: 0,
    end: 100,
    words: [
      {t0: 0, t1: 0.3, text: 'El'},
      {t0: 0, t1: 0.3, text: 'mundo'},
      {t0: 0, t1: 0.3, text: 'es'},
      {t0: 0, t1: 0.3, text: 'de'},
      {t0: 0, t1: 0.3, text: 'los'},
      {t0: 50, t1: 51, text: 'atrevidos.'},
    ],
  },
];

export const GraphicsTest: React.FC = () => (
  <AbsoluteFill>
    {/* 0: plano general + titular de apertura */}
    <Sequence from={0} durationInFrames={60}>
      <Frame />
      <Scrims />
      <Header />
      <AbsoluteFill style={{background: 'rgba(12,22,17,0.35)'}} />
      <div style={{position: 'absolute', left: SAFE.side, right: SAFE.right - 40, top: 620}}>
        <HeadlineBlock title={'SI HOY TUVIERAS\n*18 AÑOS*,\n¿QUÉ HARÍAS?'} category="Crecimiento personal" source="Con Moni · *Escalera Digital*" size={92} />
      </div>
    </Sequence>
    {/* 60: plano medio + zócalo + subtítulo */}
    <Sequence from={60} durationInFrames={60}>
      <Frame scale={1.35} x={0.22} y={0.36} />
      <Scrims />
      <Header />
      <LowerThird name="Moni" role="Escalera Digital" dur={60} />
      <Captions chunks={demoCaption} bottom={SAFE.bottom + 60} />
    </Sequence>
    {/* 120: tarjeta de pregunta */}
    <Sequence from={120} durationInFrames={60}>
      <Frame scale={1.3} x={0.76} y={0.33} />
      <Scrims />
      <Header />
      <QuestionCard n={3} total={6} dur={60} text={'Si un pibe de *18 años* está en una mesa llena de emprendedores, ¿qué tendría que hacer para no quedar como *espectador*?'} />
    </Sequence>
    {/* 180: cierre */}
    <Sequence from={180} durationInFrames={60}>
      <EndCard dur={200} />
    </Sequence>
  </AbsoluteFill>
);
