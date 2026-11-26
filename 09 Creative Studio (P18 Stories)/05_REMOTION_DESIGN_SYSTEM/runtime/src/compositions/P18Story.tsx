// Composición P18 Stories: escenas + subtítulos + firma + audio, todo desde props.
import React from 'react';
import {AbsoluteFill, Audio, Sequence, interpolate, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import {COLOR, SAFE} from '../tokens/tokens';
import {StoryProps} from '../types';
import {loadFonts} from '../utils/fonts';
import {prog} from '../utils/time';
import {Kicker, P18BrandSignature} from '../components/Brand';
import {NarrativeSubtitles} from '../subtitles/NarrativeSubtitle';
import {SceneView, toneOf} from '../scenes/SceneView';

loadFonts();

export const P18Story: React.FC<StoryProps> = ({data}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  if (!data) return <AbsoluteFill style={{background: COLOR.deep}} />;
  const t = frame / fps;
  const scene = data.scenes.find((s) => t >= s.t[0] && t < s.t[1]) ?? data.scenes[data.scenes.length - 1];
  const tone = toneOf(scene);
  const enter = prog(t, scene.t[0], scene.t[0] + 0.1);
  const last = data.scenes[data.scenes.length - 1];
  const isClose = scene.id === last.id;
  const music = data.music;
  return (
    <AbsoluteFill style={{background: COLOR.deep}}>
      <AbsoluteFill style={{opacity: enter}}>
        <SceneView s={scene} t={t} />
      </AbsoluteFill>
      {scene.kicker && scene.type !== 'outro3d' ? <Kicker text={scene.kicker} tone={tone} t={t} t0={scene.t[0]} fps={fps} /> : null}
      <NarrativeSubtitles captions={data.captions} scenes={data.scenes} />
      {/* firma */}
      {scene.type === 'outro' || scene.type === 'outro3d' ? null : isClose ? (
        <P18BrandSignature tone="paper" tagline={data.footer} size={44}
          style={{position: 'absolute', left: SAFE.side, top: 1260, opacity: prog(t, last.t[1] - 1.6, last.t[1] - 1.0)}} />
      ) : (
        <P18BrandSignature tone={tone} tagline={data.footer} size={28} style={{position: 'absolute', left: SAFE.side, top: 1920 - SAFE.bottom - 60}} />
      )}

      {/* audio: voz maestra, cama con automatización, efectos puntuales */}
      <Audio src={staticFile(data.voice)} />
      {music ? (
        <Audio
          src={staticFile(music.file)}
          volume={(f) =>
            interpolate(
              f / fps,
              music.points.map((p) => p[0]),
              music.points.map((p) => p[1]),
              {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'},
            )
          }
        />
      ) : null}
      {data.sfx.map((s, i) => (
        <Sequence key={i} from={Math.max(0, Math.round(s.at * fps))} durationInFrames={Math.round(4 * fps)}>
          <Audio src={staticFile(s.file)} volume={s.vol} />
        </Sequence>
      ))}
    </AbsoluteFill>
  );
};
