import React from 'react';
import {Composition} from 'remotion';
import {GraphicsTest} from './compositions/GraphicsTest';
import {Entrevista} from './compositions/Entrevista';
import {Clip, clipDuration} from './compositions/Clip';
import {Carrusel} from './compositions/Carrusel';
import {PERSONAS} from './data/registro';

const cap = (s: string) => s.charAt(0).toUpperCase() + s.slice(1);

// Por cada persona: <Slug> (video principal), <Slug>Clip01..., <Slug>CARRUSEL01...
export const Root: React.FC = () => (
  <>
    {PERSONAS.map((p) => (
      <React.Fragment key={p.slug}>
        <Composition
          id={cap(p.slug)}
          component={Entrevista}
          durationInFrames={p.principal.durationInFrames}
          fps={30}
          width={1080}
          height={1920}
          defaultProps={{data: p.principal}}
        />
        {(p.clips ?? []).map((c) => (
          <Composition
            key={c.n}
            id={`${cap(p.slug)}Clip${String(c.n).padStart(2, '0')}`}
            component={Clip}
            durationInFrames={clipDuration(c, 30)}
            fps={30}
            width={1080}
            height={1920}
            defaultProps={{clip: c}}
          />
        ))}
        {(p.carruseles ?? []).map((c) => (
          <Composition
            key={c.id}
            id={`${cap(p.slug)}${c.id.replace('_', '')}`}
            component={Carrusel}
            durationInFrames={c.slides.length}
            fps={1}
            width={1080}
            height={1350}
            defaultProps={{data: c}}
          />
        ))}
      </React.Fragment>
    ))}
    <Composition id="GraphicsTest" component={GraphicsTest} durationInFrames={240} fps={30} width={1080} height={1920} />
  </>
);
