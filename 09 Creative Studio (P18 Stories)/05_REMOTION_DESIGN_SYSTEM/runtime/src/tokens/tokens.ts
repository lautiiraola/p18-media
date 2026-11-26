// Tokens P18 Stories — fuente: 05_REMOTION_DESIGN_SYSTEM/tokens.txt
export const COLOR = {
  deep: '#14251D',
  ink: '#172019',
  lime: '#C2F542',
  paper: '#F5F5EB',
  blue: '#8EC3E6',
  muted: '#CDD3C8',
  clay: '#C97955',
  white: '#FBFBF5',
};

export const CANVAS = {width: 1080, height: 1920, fps: 60};

export const SAFE = {side: 82, top: 94, bottom: 190};

export const FONT = "'P18 Manrope', 'Manrope', sans-serif";

// Sistema tipográfico rotativo P18 (regla del operador, 2026-11-24): variar familias, estilos y tamaños
// escena por escena, siempre dentro de la identidad P18, para que no se vea como plantilla de IA.
export const FONTS = {
  sans: FONT, // base: narración y subtítulos
  display: "'P18 Unbounded', 'P18 Manrope', sans-serif", // cifras, golpes, titulares cortos (geometría del logo P18)
  serif: "'P18 Serif', Georgia, serif", // citas y frases dichas por personas (itálica)
  mono: "'P18 Mono', 'Courier New', monospace", // créditos, fuentes, fechas, datos documentales
};

// Zona de subtítulos: arriba de las interfaces sociales y dentro del 80 % central
export const SUBTITLE_Y = 1390;
