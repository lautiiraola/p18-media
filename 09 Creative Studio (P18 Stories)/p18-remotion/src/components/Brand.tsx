// Piezas de identidad P18 reutilizables (video principal, clips y carruseles)
import React from 'react';
import {AbsoluteFill} from 'remotion';
import {COLOR, FONT} from '../brand/tokens';

// Logotipo "P18" en lima
export const Logo: React.FC<{size?: number; color?: string; style?: React.CSSProperties}> = ({
  size = 64,
  color = COLOR.lime,
  style,
}) => (
  <div
    style={{
      fontFamily: FONT.logo,
      fontWeight: 800,
      fontSize: size,
      lineHeight: 1,
      color,
      letterSpacing: '-0.035em',
      transform: 'scaleX(0.9)',
      transformOrigin: 'left center',
      ...style,
    }}
  >
    P18
  </div>
);

// Pastilla "proyecto18.com" (borde fino blanco translúcido, como en los reels)
export const UrlPill: React.FC<{scale?: number; style?: React.CSSProperties}> = ({scale = 1, style}) => (
  <div
    style={{
      fontFamily: FONT.text,
      fontWeight: 700,
      fontSize: 26 * scale,
      color: COLOR.white,
      padding: `${10 * scale}px ${22 * scale}px`,
      borderRadius: 999,
      border: `${2 * scale}px solid rgba(255,255,255,0.35)`,
      background: 'rgba(14,25,19,0.35)',
      backdropFilter: 'blur(6px)',
      letterSpacing: '-0.01em',
      ...style,
    }}
  >
    proyecto18.com
  </div>
);

// Chip de categoría: fondo lima, texto verde oscuro en mayúsculas (como en los carruseles)
export const CategoryChip: React.FC<{label: string; scale?: number; style?: React.CSSProperties}> = ({
  label,
  scale = 1,
  style,
}) => (
  <div
    style={{
      display: 'inline-block',
      fontFamily: FONT.text,
      fontWeight: 800,
      fontSize: 22 * scale,
      letterSpacing: '0.08em',
      textTransform: 'uppercase',
      color: COLOR.greenDeep,
      background: COLOR.lime,
      padding: `${7 * scale}px ${14 * scale}px`,
      borderRadius: 4 * scale,
      ...style,
    }}
  >
    {label}
  </div>
);

// Texto con *palabras clave* en lima. "EL *AHORRO* VA PRIMERO" → AHORRO en lima.
export const KeywordText: React.FC<{text: string; keyColor?: string; underline?: boolean}> = ({
  text,
  keyColor = COLOR.lime,
  underline = false,
}) => {
  const parts = text.split(/(\*[^*]+\*)/g).filter(Boolean);
  return (
    <>
      {parts.map((p, i) =>
        p.startsWith('*') ? (
          <span
            key={i}
            style={
              underline
                ? {
                    textDecoration: 'underline',
                    textDecorationColor: keyColor,
                    textDecorationThickness: '0.09em',
                    textUnderlineOffset: '0.14em',
                  }
                : {color: keyColor}
            }
          >
            {p.slice(1, -1)}
          </span>
        ) : (
          <span key={i}>{p}</span>
        ),
      )}
    </>
  );
};

// Fondo de marca: verde oscuro, grilla fina con puntos, brillo frío arriba a la derecha, brillo verde abajo a la izquierda
export const BrandBackground: React.FC<{showGrid?: boolean}> = ({showGrid = true}) => (
  <AbsoluteFill style={{background: COLOR.greenDeep}}>
    <AbsoluteFill
      style={{
        background: `radial-gradient(circle at 92% 6%, rgba(62,102,112,0.75) 0%, rgba(62,102,112,0) 38%),
                     radial-gradient(circle at 8% 78%, rgba(120,170,40,0.28) 0%, rgba(120,170,40,0) 40%),
                     linear-gradient(180deg, ${COLOR.green} 0%, ${COLOR.greenDeep} 100%)`,
      }}
    />
    {showGrid ? (
      <AbsoluteFill
        style={{
          backgroundImage: `linear-gradient(${COLOR.grid} 1px, transparent 1px),
                            linear-gradient(90deg, ${COLOR.grid} 1px, transparent 1px),
                            radial-gradient(circle, rgba(194,244,67,0.16) 1.4px, transparent 1.6px)`,
          backgroundSize: '120px 120px, 120px 120px, 30px 30px',
          backgroundPosition: '-1px -1px, -1px -1px, 0 0',
        }}
      />
    ) : null}
  </AbsoluteFill>
);

// "18" gigante en contorno (marca de agua del fondo)
export const Outline18: React.FC<{size?: number; opacity?: number; style?: React.CSSProperties}> = ({
  size = 1100,
  opacity = 0.22,
  style,
}) => (
  <div
    style={{
      position: 'absolute',
      fontFamily: FONT.text,
      fontWeight: 800,
      fontSize: size,
      lineHeight: 0.8,
      color: 'transparent',
      WebkitTextStroke: `3px rgba(194,244,67,${opacity})`,
      letterSpacing: '-0.05em',
      ...style,
    }}
  >
    18
  </div>
);

// Franjas diagonales lima (firma gráfica de los reels)
export const DiagonalStripes: React.FC<{progress?: number; style?: React.CSSProperties; width?: number}> = ({
  progress = 1,
  style,
  width = 1080,
}) => (
  <svg width={width} height={260} viewBox="0 0 1080 260" style={{position: 'absolute', overflow: 'visible', ...style}}>
    <defs>
      <clipPath id="stripe-reveal">
        <rect x={0} y={-40} width={1080 * progress} height={340} />
      </clipPath>
    </defs>
    <g clipPath="url(#stripe-reveal)">
      <polygon points="120,260 1080,92 1080,150 400,260" fill={COLOR.lime} />
      <polygon points="430,260 1080,158 1080,178 540,260" fill={COLOR.limeDeep} opacity={0.85} />
    </g>
  </svg>
);
