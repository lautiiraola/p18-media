// Dispatcher de escenas: traduce cada escena de los props a componentes del sistema.
import React from 'react';
import {AbsoluteFill, Img, staticFile} from 'remotion';
import {COLOR, SAFE} from '../tokens/tokens';
import {Scene} from '../types';
import {prog} from '../utils/time';
import {ArchivePhoto, DocumentCard} from '../components/Archive';
import {Background, SourceCaption, Tag, Tone} from '../components/Brand';
import {DissolvingQuote, QuestionClose, SyncedQuote} from '../components/Typography';
import {
  Counter, Cyclone, DebtLine, EmptyField, FilterClog, Formulas, HouseGuarantee, Method, Metric, Microns,
  PrototypeGrid, Rejections, RouteJapan, TimelineTen, UprightVacuum, YearCard,
} from '../components/Graphics';
import {P18Outro} from '../components/Outro';
import {P18Outro3D} from '../components/Outro3D';
import {Enter, Gallery, GalleryItem} from '../components/Motion';
import {BigLine, BrowserMock, ChartReveal, FullBleedPhoto, LossYears, PeopleGrid, VideoCard, VoteBar} from '../components/Graphics2';

type W = {text: string; t0: number};
const num = (v: unknown, d = 0) => (typeof v === 'number' ? v : d);
const str = (v: unknown) => (typeof v === 'string' ? v : undefined);

const PatentImg: React.FC<{src: string}> = ({src}) => (
  <Img src={staticFile(src)} style={{width: '100%', height: '100%', objectFit: 'cover', objectPosition: '50% 18%', transform: 'scale(1.35)', transformOrigin: '50% 18%'}} />
);

export const toneOf = (s: Scene): Tone => (s.bg === 'paper' ? 'paper' : 'deep');

export const SceneView: React.FC<{s: Scene; t: number}> = ({s, t}) => {
  const gallery = s.gallery as GalleryItem[] | undefined;
  if (gallery && gallery.length) {
    return (
      <>
        <SceneBody s={s} t={t} />
        <Gallery items={gallery} t={t} sceneEnd={s.t[1]} />
      </>
    );
  }
  return <SceneBody s={s} t={t} />;
};

const SceneBody: React.FC<{s: Scene; t: number}> = ({s, t}) => {
  const [t0, t1] = s.t;
  const tone = toneOf(s);
  const fr = (sc: number, fx: number, fy: number) => ({scale: sc, fx, fy});

  switch (s.type) {
    case 'quote': {
      const words = s.words as W[];
      if (s.worn) {
        return (
          <>
            <Background tone="deep" />
            <SyncedQuote words={words} t={t} tone="deep" size={50} top={420} opacity={0.42} />
            <div style={{position: 'absolute', left: SAFE.side, right: SAFE.side, top: 1050, opacity: prog(t, num(s.captionT), num(s.captionT) + 0.3)}}>
              <div style={{fontFamily: "'P18 Manrope', sans-serif", fontWeight: 700, fontSize: 70, color: COLOR.white, letterSpacing: '-0.02em'}}>{str(s.caption)}</div>
            </div>
          </>
        );
      }
      const bd = s.backdrop as {opacity?: number} | undefined;
      return (
        <>
          <Background tone={tone} />
          {tone === 'deep' && bd ? (
            <UprightVacuum t={t} t0={t0} mode="bag" fill={0.75} opacity={num(bd.opacity, 0.2)} x={820} y={980} scale={1.05} />
          ) : null}
          <SyncedQuote words={words} t={t} tone={tone} underline={s.underline as string[]} attribution={str(s.attribution)} top={tone === 'paper' ? 520 : 470} />
        </>
      );
    }
    case 'portrait': {
      const mq = str(s.miniQuote);
      return (
        <>
          <Background tone="deep" />
          <div style={{position: 'absolute', left: 60, top: 400, width: 960, height: 992, opacity: prog(t, t0, t0 + 0.4),
            WebkitMaskImage: 'radial-gradient(ellipse 62% 60% at 50% 42%, #000 55%, transparent 100%)'}}>
            <Img src={staticFile(str(s.src)!)} style={{width: '100%', height: '100%', objectFit: 'cover',
              transform: `scale(${1 + prog(t, t0, t1) * 0.05})`, transformOrigin: '50% 40%'}} />
          </div>
          {mq ? (
            <div style={{position: 'absolute', left: SAFE.side, right: SAFE.side, top: 250, fontFamily: "'P18 Manrope', sans-serif", fontWeight: 600, fontSize: 34, lineHeight: 1.3, color: COLOR.white, opacity: 0.6}}>
              «{mq}»
            </div>
          ) : null}
          <Tag text={str(s.label) ?? ''} tone="deep" style={{position: 'absolute', left: SAFE.side, top: 1280, color: COLOR.lime, fontSize: 26}} />
          {s.credit ? <SourceCaption text={str(s.credit)!} tone="deep" style={{position: 'absolute', left: SAFE.side, top: 1320}} /> : null}
        </>
      );
    }
    case 'year':
      return (
        <>
          <Background tone="paper" />
          <YearCard t={t} t0={t0} year={str(s.year)!} caption={str(s.caption)} />
        </>
      );
    case 'document': {
      const fx = num(s.focusX, 0.5);
      const fy = num(s.focusY, 0.5);
      return (
        <>
          <Background tone="paper" />
          <DocumentCard src={str(s.src)!} t={t} t0={t0} t1={t1} from={fr(num(s.from, 1), fx, fy)} to={fr(num(s.to, 1.1), fx, fy)}
            credit={str(s.credit)} cardHeight={s.overlay === 'clog' ? 560 : 920} cardTop={s.overlay === 'clog' ? 300 : 280} />
          {s.overlay === 'clog' ? <FilterClog t={t} t0={t0} t1={t1} top={970} /> : null}
        </>
      );
    }
    case 'photo': {
      const fx = num(s.focusX, 0.5);
      const fy = num(s.focusY, 0.5);
      const panY = s.panY as [number, number] | undefined;
      const panX = s.panX as [number, number] | undefined;
      let from = fr(num(s.from, 1), panX ? panX[0] : fx, panY ? panY[0] : fy);
      let to = fr(num(s.to, 1.1), panX ? panX[1] : fx, panY ? panY[1] : fy);
      let tt0 = t0;
      let tt1 = t1;
      const zoomAt = num(s.zoomAt, 0);
      const zt = s.zoomTo as {scale: number; focusX: number; focusY: number} | undefined;
      if (zt && zoomAt && t >= zoomAt) {
        from = to;
        to = fr(zt.scale, zt.focusX, zt.focusY);
        tt0 = zoomAt;
        tt1 = zoomAt + 0.7;
      } else if (zt && zoomAt) {
        tt1 = zoomAt;
      }
      return (
        <>
          <Background tone="deep" />
          <ArchivePhoto src={str(s.src)!} t={t} t0={tt0} t1={tt1} from={from} to={to} credit={str(s.credit)} label={str(s.label)} mono={Boolean(s.mono)} enter={s.zoomTo ? undefined : (str(s.enter) as Enter | undefined)}
            cardTop={330} cardHeight={s.src === 'img/A14.jpg' || s.src === 'img/A21.jpg' ? 820 : 640} />
        </>
      );
    }
    case 'cyclone':
      return (
        <>
          <Background tone="deep" />
          <Cyclone t={t} t0={t0} growAt={num(s.grow)} hoursAt={num(s.hours)} label={str(s.label)} />
        </>
      );
    case 'bag':
      return (
        <>
          <Background tone="deep" />
          <UprightVacuum t={t} t0={t0} mode="bag" fill={prog(t, t0 + 0.2, t1)} />
          <Tag text={str(s.label) ?? ''} tone="deep" style={{position: 'absolute', left: SAFE.side, top: 1300}} />
        </>
      );
    case 'cardboard': {
      const freeze = num(s.freeze, t1);
      const spin = t < freeze ? 1 : Math.max(0.08, 1 - (t - freeze) * 1.4);
      return (
        <>
          <Background tone="deep" />
          <UprightVacuum t={t} t0={t0} mode="cone" fill={0.85} coneP={prog(t, t0 + 0.2, t0 + 1.6)} spin={spin} />
          <Tag text={str(s.label) ?? ''} tone="deep" style={{position: 'absolute', left: SAFE.side, top: 1300}} />
        </>
      );
    }
    case 'microns':
      return (
        <>
          <Background tone="deep" />
          <Microns t={t} t0={t0} label={str(s.label)} />
        </>
      );
    case 'formulas':
      return (
        <>
          <Background tone="deep" />
          <Formulas t={t} t0={t0} />
        </>
      );
    case 'method':
      return (
        <>
          <Background tone="deep" />
          <Method t={t} beats={s.beats as number[]} src={str(s.src)!} Img={PatentImg} />
        </>
      );
    case 'debt':
      return (
        <>
          <Background tone="deep" />
          <DebtLine t={t} t0={t0} t1={t1} />
        </>
      );
    case 'counter':
      return (
        <>
          <Background tone="deep" />
          <Counter t={t} t0={t0} hit={num(s.hit)} />
        </>
      );
    case 'field':
      return (
        <>
          <Background tone="paper" />
          <EmptyField t={t} t0={t0} />
        </>
      );
    case 'rejections':
      return (
        <>
          <Background tone="paper" />
          <Rejections t={t} t0={t0} label={str(s.label)} />
        </>
      );
    case 'japan': {
      const at = num(s.photoAt, t1);
      return (
        <>
          <Background tone="deep" />
          <RouteJapan t={t} t0={t0} />
          {t >= at - 0.2 ? (
            <AbsoluteFill style={{opacity: prog(t, at - 0.2, at + 0.2)}}>
              <ArchivePhoto src={str(s.src)!} t={t} t0={at} t1={t1} from={fr(1.0, 0.62, 0.5)} to={fr(1.12, 0.62, 0.55)} credit={str(s.credit)} label="G-Force · 1986"
                cardTop={640} cardHeight={600} />
            </AbsoluteFill>
          ) : null}
        </>
      );
    }
    case 'timeline':
      return (
        <>
          <Background tone="deep" />
          <TimelineTen t={t} t0={t0} />
        </>
      );
    case 'guarantee': {
      const cut = num(s.cut, t1);
      if (t < cut) {
        return (
          <>
            <Background tone="deep" />
            <HouseGuarantee t={t} t0={t0} />
          </>
        );
      }
      return (
        <>
          <Background tone="deep" />
          <ArchivePhoto src={str(s.src)!} t={t} t0={cut} t1={t1} from={fr(1.0, 0.5, 0.5)} to={fr(1.1, 0.42, 0.5)} credit={str(s.credit)} label="Su propia fábrica · 1993" />
        </>
      );
    }
    case 'metric':
      return (
        <>
          <Background tone="deep" />
          <Metric t={t} at={num(s.countAt)} value={num(s.value)} unit={str(s.unit) ?? ''} note={str(s.note)} />
        </>
      );
    case 'grid':
      return (
        <>
          <Background tone="deep" />
          <PrototypeGrid n={5126} highlight={5127} top={420} scale={1 - prog(t, t0, t1) * 0.12} />
        </>
      );
    case 'dissolve':
      return (
        <>
          <Background tone="deep" />
          <DissolvingQuote text={str(s.text)!} t={t} t0={t0} t1={t1} />
        </>
      );
    case 'question':
      return (
        <>
          <Background tone="paper" />
          <QuestionClose words={s.words as W[]} t={t} underline={s.underline as string[]} />
        </>
      );
    case 'people':
      return (
        <>
          <Background tone="deep" />
          <PeopleGrid t={t} appearAt={num(s.appearAt, t0)} verdictAt={num(s.verdictAt, t0)} focusYes={typeof s.focusYes === 'number' ? (s.focusYes as number) : undefined} top={num(s.gridTop, 560)} />
          {s.headline0 && t < num(s.headlineAt, t0) ? <BigLine t={t} at={t0} text={str(s.headline0)!} top={num(s.headlineTop, 300)} size={num(s.headlineSize, 96)} /> : null}
          {s.headline && t >= num(s.headlineAt, t0) ? <BigLine t={t} at={num(s.headlineAt, t0)} text={str(s.headline)!} top={num(s.headlineTop, 300)} size={num(s.headlineSize, 96)} /> : null}
        </>
      );
    case 'photoThenBrowser': {
      const sw = num(s.switchAt, t1);
      if (t < sw) {
        return (
          <>
            <Background tone="deep" />
            <ArchivePhoto src={str(s.src)!} t={t} t0={t0} t1={sw} from={fr(1.0, 0.5, 0.45)} to={fr(1.12, 0.5, 0.4)} credit={str(s.credit)} label={str(s.label)} cardTop={360} cardHeight={700} />
          </>
        );
      }
      return (
        <>
          <Background tone="deep" />
          <BrowserMock t={t} t0={sw} logo={str(s.logo)!} url={str(s.url)!} caption={str(s.browserCaption)} />
        </>
      );
    }
    case 'videoQuote':
      return (
        <>
          <Background tone="deep" />
          <VideoCard src={str(s.video)!} t={t} t0={t0} top={300} height={520} credit={str(s.credit)} label={str(s.label)} />
          <SyncedQuote words={s.words as W[]} t={t} tone="deep" underline={s.underline as string[]} size={56} top={960} />
        </>
      );
    case 'chart':
      return (
        <>
          <Background tone="paper" />
          <ChartReveal t={t} t0={t0} t1={t1} src={str(s.src)!} marks={s.marks as {x: number; label: string; at: number; color?: string}[]} credit={str(s.credit)} />
        </>
      );
    case 'vote':
      return (
        <>
          <Background tone="deep" />
          <VoteBar t={t} t0={t0} stopAt={num(s.stopAt, t1)} label={str(s.label)} />
        </>
      );
    case 'losses':
      return (
        <>
          <Background tone="deep" />
          <LossYears t={t} t0={t0} t1={t1} years={s.years as number[]} />
        </>
      );
    case 'photoThenSlide': {
      const sw = num(s.switchAt, t1);
      if (t < sw) {
        return (
          <>
            <Background tone="deep" />
            <ArchivePhoto src={str(s.src)!} t={t} t0={t0} t1={sw} from={fr(1.0, 0.45, 0.5)} to={fr(1.15, 0.4, 0.62)} credit={str(s.credit)} label={str(s.label)} cardTop={330} cardHeight={820} />
          </>
        );
      }
      return (
        <>
          <Background tone="deep" />
          <ArchivePhoto src={str(s.slide)!} t={t} t0={sw} t1={t1} from={fr(1.0, 0.5, 0.5)} to={fr(1.9, num(s.zoomX, 0.5), num(s.zoomY, 0.85))} credit={str(s.slideCredit)} label={str(s.slideLabel)} cardTop={380} cardHeight={700} />
        </>
      );
    }
    case 'fullbleed':
      return (
        <>
          <Background tone="deep" />
          <FullBleedPhoto src={str(s.src)!} t={t} t0={t0} t1={t1} fx={num(s.focusX, 0.5)} fy={num(s.focusY, 0.5)} credit={str(s.credit)} zoom={num(s.zoom, 1.04)} />
          {s.headline ? <BigLine t={t} at={num(s.headlineAt, t0)} text={str(s.headline)!} top={num(s.headlineTop, 300)} size={num(s.headlineSize, 96)} /> : null}
        </>
      );
    case 'outro':
      return <P18Outro t={t} t0={t0} fromNumber={str(s.fromNumber) ?? '0'} fromLabel={str(s.fromLabel) ?? ''} handle={str(s.handle) ?? '@proyecto18.ar'} web={str(s.web) ?? 'proyecto18.com'} tagline={str(s.tagline) ?? 'Talleres gratuitos para jóvenes'} />;
    case 'outro3d':
      return (
        <P18Outro3D t={t} t0={t0} fromNumber={str(s.fromNumber) ?? '0'} fromLabel={str(s.fromLabel) ?? ''}
          line={str(s.line) ?? 'Mentalidad emprendedora para los jóvenes.'} lineAccent={str(s.lineAccent) ?? 'los jóvenes'} handle={str(s.handle) ?? '@proyecto18.ar'} />
      );
    default:
      return <Background tone={tone} />;
  }
};
