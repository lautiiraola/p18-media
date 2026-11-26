// Carruseles P18 (1080x1350, 4:5). Cada frame de la composición es una lámina.
// Lenguaje tomado de los posts de @proyecto18.ar: portada con foto a sangre + chip lima + titular con palabra clave subrayada,
// lámina crema con foto arriba ("EL MITO"), lámina de cita sobre foto, y placa verde de marca.
import React from 'react';
import {AbsoluteFill, Img, staticFile, useCurrentFrame} from 'remotion';
import {COLOR, FONT} from '../brand/tokens';
import {BrandBackground, CategoryChip, DiagonalStripes, KeywordText, Logo, Outline18} from '../components/Brand';

export type Slide =
  | {tipo: 'portada'; foto: string; chip: string; titulo: string; bajada: string; focoY?: number}
  | {tipo: 'crema'; foto: string; etiqueta: string; titulo: string; texto: string; focoY?: number}
  | {tipo: 'cita'; foto: string; cita: string; firma: string; focoY?: number}
  | {tipo: 'marca'; etiqueta: string; titulo: string; texto?: string; lista?: {n: string; t: string; d?: string}[]}
  | {tipo: 'cierre'; frase: string; pregunta: string; accion: string};

export type CarruselData = {id: string; slides: Slide[]};

const PAD = 84;
const P18Mark: React.FC<{color?: string; style?: React.CSSProperties}> = ({color = COLOR.white, style}) => (
  <div style={{position: 'absolute', ...style}}>
    <Logo size={40} color={color} />
  </div>
);

const Foto: React.FC<{src: string; focoY?: number; style?: React.CSSProperties}> = ({src, focoY = 30, style}) => (
  <Img src={staticFile(src)} style={{width: '100%', height: '100%', objectFit: 'cover', objectPosition: `50% ${focoY}%`, ...style}} />
);

const Portada: React.FC<{s: Extract<Slide, {tipo: 'portada'}>}> = ({s}) => (
  <AbsoluteFill>
    <Foto src={s.foto} focoY={s.focoY} />
    <AbsoluteFill
      style={{
        background:
          'linear-gradient(180deg, rgba(10,20,15,0.45) 0%, rgba(10,20,15,0) 22%, rgba(10,20,15,0) 40%, rgba(10,20,15,0.78) 66%, rgba(10,20,15,0.95) 100%)',
      }}
    />
    <div style={{position: 'absolute', left: PAD, top: 76}}>
      <CategoryChip label={s.chip} scale={1.05} />
    </div>
    <P18Mark style={{right: PAD - 6, top: 72}} />
    <div style={{position: 'absolute', left: PAD, right: PAD, bottom: 96}}>
      <div
        style={{
          fontFamily: FONT.text, fontWeight: 800, fontSize: 104, lineHeight: 1.0, letterSpacing: '-0.035em',
          color: COLOR.white, textWrap: 'balance',
        }}
      >
        <KeywordText text={s.titulo} underline />
      </div>
      <div style={{marginTop: 30, fontFamily: FONT.text, fontWeight: 600, fontSize: 33, lineHeight: 1.3, color: 'rgba(255,255,255,0.9)', maxWidth: 860}}>
        {s.bajada}
      </div>
      <div
        style={{
          marginTop: 34, display: 'inline-block', fontFamily: FONT.text, fontWeight: 700, fontSize: 25, color: COLOR.white,
          border: '2px solid rgba(255,255,255,0.6)', borderRadius: 999, padding: '9px 22px',
        }}
      >
        Deslizá →
      </div>
    </div>
  </AbsoluteFill>
);

const Crema: React.FC<{s: Extract<Slide, {tipo: 'crema'}>}> = ({s}) => (
  <AbsoluteFill style={{background: COLOR.cream}}>
    <div style={{position: 'absolute', left: 0, right: 0, top: 0, height: 610, overflow: 'hidden'}}>
      <Foto src={s.foto} focoY={s.focoY ?? 26} />
      <div style={{position: 'absolute', inset: 0, background: 'linear-gradient(180deg, rgba(10,20,15,0.45) 0%, rgba(10,20,15,0) 30%)'}} />
    </div>
    <div style={{position: 'absolute', left: PAD, top: 76}}>
      <CategoryChip label={s.etiqueta} scale={1.05} />
    </div>
    <P18Mark style={{right: PAD - 6, top: 72}} />
    <div style={{position: 'absolute', left: PAD, right: PAD, top: 680}}>
      <div style={{width: 70, height: 7, background: COLOR.lime, borderRadius: 2, marginBottom: 34}} />
      <div
        style={{
          fontFamily: FONT.text, fontWeight: 800, fontSize: 84, lineHeight: 1.02, letterSpacing: '-0.035em',
          color: COLOR.greenDeep, textWrap: 'balance',
        }}
      >
        <KeywordText text={s.titulo} underline keyColor={COLOR.lime} />
      </div>
      <div style={{marginTop: 30, fontFamily: FONT.text, fontWeight: 600, fontSize: 35, lineHeight: 1.36, color: 'rgba(20,36,28,0.78)', textWrap: 'pretty'}}>
        {s.texto}
      </div>
    </div>
  </AbsoluteFill>
);

const Cita: React.FC<{s: Extract<Slide, {tipo: 'cita'}>}> = ({s}) => {
  const len = s.cita.replace(/\*/g, '').length;
  const size = len > 150 ? 58 : len > 110 ? 66 : 76;
  return (
    <AbsoluteFill>
      <Foto src={s.foto} focoY={s.focoY} />
      <AbsoluteFill
        style={{background: 'linear-gradient(180deg, rgba(10,20,15,0.25) 0%, rgba(10,20,15,0.35) 35%, rgba(10,20,15,0.88) 68%, rgba(10,20,15,0.96) 100%)'}}
      />
      <div style={{position: 'absolute', left: PAD, right: PAD, bottom: 110}}>
        <div style={{fontFamily: FONT.text, fontWeight: 800, fontSize: size, lineHeight: 1.08, letterSpacing: '-0.03em', color: COLOR.white, textWrap: 'balance'}}>
          <KeywordText text={s.cita} />
        </div>
        <div style={{marginTop: 30, fontFamily: FONT.text, fontWeight: 800, fontSize: 24, letterSpacing: '0.1em', color: COLOR.lime, textTransform: 'uppercase'}}>
          {s.firma}
        </div>
      </div>
      <P18Mark style={{right: PAD - 6, bottom: 52}} />
    </AbsoluteFill>
  );
};

const Marca: React.FC<{s: Extract<Slide, {tipo: 'marca'}>}> = ({s}) => (
  <AbsoluteFill>
    <BrandBackground />
    <Outline18 size={1000} opacity={0.12} style={{right: -160, bottom: -140}} />
    <div style={{position: 'absolute', left: PAD, top: 76}}>
      <CategoryChip label={s.etiqueta} scale={1.05} />
    </div>
    <P18Mark color={COLOR.lime} style={{right: PAD - 6, top: 72}} />
    <div style={{position: 'absolute', left: PAD, right: PAD, top: 170, bottom: 250, display: 'flex', flexDirection: 'column', justifyContent: 'center'}}>
      <div style={{fontFamily: FONT.text, fontWeight: 800, fontSize: s.lista ? 80 : 92, lineHeight: 1.03, letterSpacing: '-0.035em', color: COLOR.white, textWrap: 'balance'}}>
        <KeywordText text={s.titulo} />
      </div>
      {s.texto ? (
        <div style={{marginTop: 44, fontFamily: FONT.text, fontWeight: 600, fontSize: 40, lineHeight: 1.36, color: 'rgba(255,255,255,0.84)', textWrap: 'pretty'}}>
          <KeywordText text={s.texto} />
        </div>
      ) : null}
      {s.lista ? (
        <div style={{marginTop: 60, display: 'flex', flexDirection: 'column', gap: 36}}>
          {s.lista.map((it) => (
            <div key={it.n} style={{display: 'flex', gap: 28, alignItems: 'baseline'}}>
              <div style={{fontFamily: FONT.text, fontWeight: 800, fontSize: 34, color: COLOR.lime, letterSpacing: '0.04em', width: 62}}>{it.n}</div>
              <div>
                <div style={{fontFamily: FONT.text, fontWeight: 800, fontSize: 54, color: COLOR.white, letterSpacing: '-0.025em', lineHeight: 1.08}}>{it.t}</div>
                {it.d ? <div style={{marginTop: 6, fontFamily: FONT.text, fontWeight: 600, fontSize: 31, color: 'rgba(255,255,255,0.72)', lineHeight: 1.3, textWrap: 'balance'}}>{it.d}</div> : null}
              </div>
            </div>
          ))}
        </div>
      ) : null}
    </div>
    <DiagonalStripes progress={1} style={{left: 0, bottom: -10}} />
  </AbsoluteFill>
);

const Cierre: React.FC<{s: Extract<Slide, {tipo: 'cierre'}>}> = ({s}) => (
  <AbsoluteFill>
    <BrandBackground />
    <Outline18 size={1100} opacity={0.16} style={{right: -140, top: 260}} />
    <div style={{position: 'absolute', left: PAD, top: 92}}>
      <Logo size={96} />
    </div>
    <div style={{position: 'absolute', left: PAD, right: PAD, top: 230, bottom: 290, display: 'flex', flexDirection: 'column', justifyContent: 'center'}}>
      <div style={{fontFamily: FONT.text, fontWeight: 800, fontSize: 80, lineHeight: 1.08, letterSpacing: '-0.03em', color: COLOR.white, textWrap: 'balance'}}>
        <KeywordText text={s.frase} underline />
      </div>
      <div style={{marginTop: 64, width: 70, height: 7, background: COLOR.lime, borderRadius: 2}} />
      <div style={{marginTop: 34, fontFamily: FONT.text, fontWeight: 700, fontSize: 48, lineHeight: 1.22, color: COLOR.lime, textWrap: 'balance'}}>
        {s.pregunta}
      </div>
      <div style={{marginTop: 28, fontFamily: FONT.text, fontWeight: 600, fontSize: 34, lineHeight: 1.35, color: 'rgba(255,255,255,0.78)'}}>
        {s.accion}
      </div>
    </div>
    <div style={{position: 'absolute', left: PAD, bottom: 210, fontFamily: FONT.text, fontWeight: 800, fontSize: 30, color: COLOR.white}}>
      @proyecto18.ar <span style={{color: 'rgba(255,255,255,0.5)', fontWeight: 600}}> · proyecto18.com</span>
    </div>
    <DiagonalStripes progress={1} style={{left: 0, bottom: -10}} />
  </AbsoluteFill>
);

export const Carrusel: React.FC<{data: CarruselData}> = ({data}) => {
  const f = useCurrentFrame();
  const s = data.slides[Math.min(f, data.slides.length - 1)];
  switch (s.tipo) {
    case 'portada':
      return <Portada s={s} />;
    case 'crema':
      return <Crema s={s} />;
    case 'cita':
      return <Cita s={s} />;
    case 'marca':
      return <Marca s={s} />;
    case 'cierre':
      return <Cierre s={s} />;
  }
};
