// P18Outro3D — cierre fijo de P18 Stories, v2 (3D real).
// 1) El número clave de la historia gira como odómetro (2D) y cae en 18.
// 2) El 18 pasa a 3D: letras extruidas de Manrope ExtraBold con material físico (clearcoat), reflejos de entorno,
//    luz que barre la superficie y sombra en el piso. Entra la "P" y se forma P18. La cámara se mueve lento.
// 3) Debajo, una sola línea de identidad (sin llamados a la acción) y la firma @proyecto18.ar.
import React, {useMemo} from 'react';
import {AbsoluteFill, useCurrentFrame, useVideoConfig} from 'remotion';
import {ThreeCanvas} from '@remotion/three';
import {useThree} from '@react-three/fiber';
import * as THREE from 'three';
import {SVGLoader} from 'three/examples/jsm/loaders/SVGLoader.js';
import {RoomEnvironment} from 'three/examples/jsm/environments/RoomEnvironment.js';
import glyphData from '../assets/p18-glyphs.json';
import {COLOR, FONT, SAFE} from '../tokens/tokens';
import {easeInOut, easeOut, prog} from '../utils/time';
import {Underlined} from './Brand';
import {Wheel} from './Outro';

type GlyphJson = {unitsPerEm: number; capHeight: number; glyphs: Record<string, {d: string; advance: number}>};
const G = glyphData as GlyphJson;
const S = 0.001; // unidades de fuente → unidades de escena

const glyphGeometry = (ch: string) => {
  const svg = `<svg xmlns="http://www.w3.org/2000/svg"><path d="${G.glyphs[ch].d}"/></svg>`;
  const data = new SVGLoader().parse(svg);
  const shapes = data.paths.flatMap((p) => SVGLoader.createShapes(p));
  const geo = new THREE.ExtrudeGeometry(shapes, {
    depth: 260,
    bevelEnabled: true,
    bevelThickness: 34,
    bevelSize: 20,
    bevelSegments: 8,
    curveSegments: 24,
  });
  geo.scale(S, S, S);
  geo.computeVertexNormals();
  return geo;
};

const Environment: React.FC = () => {
  const {gl, scene} = useThree();
  useMemo(() => {
    const pmrem = new THREE.PMREMGenerator(gl);
    scene.environment = pmrem.fromScene(new RoomEnvironment(), 0.04).texture;
    scene.background = new THREE.Color(COLOR.deep);
    scene.fog = new THREE.Fog(new THREE.Color(COLOR.deep), 6.5, 13);
    gl.toneMapping = THREE.NeutralToneMapping; // respeta el tono del lima de marca
    gl.toneMappingExposure = 1.0;
    gl.shadowMap.enabled = true;
    gl.shadowMap.type = THREE.PCFSoftShadowMap;
  }, [gl, scene]);
  return null;
};

const Scene3D: React.FC<{t: number; t0: number}> = ({t, t0}) => {
  const {camera} = useThree();
  const geos = useMemo(() => ({P: glyphGeometry('P'), one: glyphGeometry('1'), eight: glyphGeometry('8')}), []);
  const material = useMemo(
    () =>
      new THREE.MeshPhysicalMaterial({
        color: new THREE.Color(COLOR.lime),
        metalness: 0.05,
        roughness: 0.34,
        clearcoat: 1,
        clearcoatRoughness: 0.06,
        envMapIntensity: 0.55,
      }),
    [],
  );

  const aP = G.glyphs.P.advance * S;
  const a1 = G.glyphs['1'].advance * S;
  const a8 = G.glyphs['8'].advance * S;
  const tracking = -0.04;
  const wFull = aP + a1 + a8 + tracking * 2;
  const w18 = a1 + a8 + tracking;

  const pIn = prog(t, t0 + 1.05, t0 + 1.6, easeOut); // entra la P
  const appear = prog(t, t0 + 0.8, t0 + 1.05);
  // posición del grupo "18": primero centrado, luego corrido a la derecha para hacer lugar a la P
  const x18 = -(w18 / 2) * (1 - pIn) + (-(wFull / 2) + aP + tracking) * pIn;
  const xP = -(wFull / 2) - (1 - pIn) * 1.6;

  // cámara: frontal al principio (coincide con el 18 plano), después orbita y se acerca
  const orbit = prog(t, t0 + 0.85, t0 + 3.0, easeInOut);
  const cam = new THREE.Vector3(Math.sin(-0.24 * orbit) * 7.4, 0.72 + 0.45 * orbit, Math.cos(-0.24 * orbit) * 7.4 - orbit * 0.25);
  camera.position.copy(cam);
  camera.lookAt(-0.12 * orbit, 0.02, 0);

  // luz que barre la superficie
  const sweep = prog(t, t0 + 1.2, t0 + 2.6, easeInOut);
  return (
    <>
      <Environment />
      <ambientLight intensity={0.15} />
      <directionalLight position={[-3, 6, 5]} intensity={1.5} castShadow shadow-mapSize-width={2048} shadow-mapSize-height={2048} shadow-camera-left={-5} shadow-camera-right={5} shadow-camera-top={5} shadow-camera-bottom={-5} />
      <spotLight position={[-4 + sweep * 8, 3, 4]} angle={0.35} penumbra={0.9} intensity={26 * appear} color={'#FFFFFF'} />
      <pointLight position={[0, 1.5, -3]} intensity={18} color={COLOR.blue} />
      <group position={[0, 0, 0]} scale={0.52 * (0.92 + 0.08 * appear)}>
        <group position={[x18, 0, -0.13]}>
          <mesh geometry={geos.one} material={material} castShadow receiveShadow />
          <mesh geometry={geos.eight} material={material} position={[a1 + tracking, 0, 0]} castShadow receiveShadow />
        </group>
        <mesh geometry={geos.P} material={material} position={[xP, 0, -0.13]} castShadow receiveShadow visible={pIn > 0.001} />
      </group>
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, -0.04, 0]} receiveShadow>
        <planeGeometry args={[40, 40]} />
        <shadowMaterial opacity={0.45} />
      </mesh>
    </>
  );
};

export const P18Outro3D: React.FC<{t: number; t0: number; fromNumber: string; fromLabel: string; line: string; lineAccent: string; handle: string}> = ({
  t,
  t0,
  fromNumber,
  fromLabel,
  line,
  lineAccent,
  handle,
}) => {
  const {width, height} = useVideoConfig();
  useCurrentFrame();
  const enter = prog(t, t0, t0 + 0.2);
  const roll = prog(t, t0 + 0.1, t0 + 0.75, easeInOut);
  const flatOut = prog(t, t0 + 0.8, t0 + 1.0);
  const textIn = prog(t, t0 + 1.55, t0 + 1.95);
  const under = prog(t, t0 + 1.9, t0 + 2.3);
  const handleIn = prog(t, t0 + 2.0, t0 + 2.35);

  const src = fromNumber.replace(/\D/g, '');
  const n = Math.max(src.length, 2);
  const srcP = src.padStart(n, ' ');
  const tgtP = '18'.padStart(n, ' ');
  const [pre, post] = line.split(lineAccent);

  return (
    <AbsoluteFill style={{background: COLOR.deep, opacity: enter}}>
      {/* 3D */}
      <AbsoluteFill style={{opacity: prog(t, t0 + 0.78, t0 + 1.0)}}>
        <ThreeCanvas width={width} height={height} camera={{fov: 30, position: [0, 0.72, 7.4], near: 0.1, far: 60}} gl={{antialias: true}} shadows>
          <Scene3D t={t} t0={t0} />
        </ThreeCanvas>
      </AbsoluteFill>

      {/* odómetro 2D que se convierte en el 18 3D */}
      <div style={{position: 'absolute', left: 0, right: 0, top: 520, textAlign: 'center', opacity: 1 - flatOut, transform: `scale(${1 + flatOut * 0.15})`}}>
        <div style={{fontFamily: FONT, fontWeight: 800, fontSize: 30, letterSpacing: '0.18em', textTransform: 'uppercase', color: COLOR.clay, marginBottom: 10, opacity: 1 - prog(t, t0 + 0.55, t0 + 0.75)}}>
          {fromLabel}
        </div>
        <div style={{fontFamily: FONT, fontWeight: 800, fontSize: 400, lineHeight: 1, letterSpacing: '-0.04em', color: COLOR.lime, display: 'inline-block'}}>
          {Array.from({length: n}, (_, i) => {
            const a = srcP[i];
            const b = tgtP[i];
            if (b === ' ') {
              return (
                <span key={i} style={{display: 'inline-block', width: (1 - roll) * 0.62 + 'em', overflow: 'hidden', opacity: 1 - roll}}>
                  {a}
                </span>
              );
            }
            return <Wheel key={i} from={a === ' ' ? 0 : Number(a)} to={Number(b)} p={roll} spins={1 + ((n - i) % 2)} />;
          })}
        </div>
      </div>

      {/* identidad, sin llamados a la acción */}
      <div style={{position: 'absolute', left: SAFE.side, right: SAFE.side, top: 1180, textAlign: 'center', opacity: textIn, transform: `translateY(${(1 - textIn) * 16}px)`}}>
        <div style={{fontFamily: FONT, fontWeight: 800, fontSize: 28, letterSpacing: '0.32em', textTransform: 'uppercase', color: 'rgba(251,251,245,0.7)'}}>Proyecto 18</div>
        <div style={{marginTop: 22, fontFamily: FONT, fontWeight: 700, fontSize: 58, lineHeight: 1.15, letterSpacing: '-0.02em', color: COLOR.white}}>
          {pre}
          <Underlined p={under}>{lineAccent}</Underlined>
          {post}
        </div>
      </div>
      <div style={{position: 'absolute', left: 0, right: 0, top: 1450, textAlign: 'center', fontFamily: FONT, fontWeight: 700, fontSize: 30, letterSpacing: '0.04em', color: COLOR.blue, opacity: handleIn}}>
        {handle}
      </div>
      {/* viñeta para profundidad */}
      <AbsoluteFill style={{pointerEvents: 'none', background: 'radial-gradient(120% 70% at 50% 42%, rgba(0,0,0,0) 55%, rgba(5,12,9,0.55) 100%)'}} />
    </AbsoluteFill>
  );
};
