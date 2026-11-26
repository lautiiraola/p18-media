// Identidad P18: valores tomados de los reels de @proyecto18.ar (muestreo de color sobre frames reales)
import {continueRender, delayRender, staticFile} from 'remotion';

// Tipografías locales (public/fonts): el render no depende de internet.
const LATIN = 'U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, U+02DC, U+0304, U+0308, U+0329, U+2000-206F, U+20AC, U+2122, U+2191, U+2193, U+2212, U+2215, U+FEFF, U+FFFD';
const LATIN_EXT = 'U+0100-02BA, U+02BD-02C5, U+02C7-02CC, U+02CE-02D7, U+02DD-02FF, U+0304, U+0308, U+0329, U+1D00-1DBF, U+1E00-1E9F, U+1EF2-1EFF, U+2020, U+20A0-20AB, U+20AD-20C0, U+2113, U+2C60-2C7F, U+A720-A7FF';

const loadLocal = (family: string, file: string, weight: string, unicodeRange: string) => {
  if (typeof window === 'undefined' || typeof FontFace === 'undefined') return;
  const handle = delayRender(`Cargando ${family} (${file})`);
  const face = new FontFace(family, `url(${staticFile(`fonts/${file}`)}) format('woff2')`, {weight, unicodeRange});
  face
    .load()
    .then((f) => {
      document.fonts.add(f);
      continueRender(handle);
    })
    .catch((err) => {
      console.error(err);
      continueRender(handle);
    });
};

loadLocal('P18 Manrope', 'manrope-latin.woff2', '200 800', LATIN);
loadLocal('P18 Manrope', 'manrope-latin-ext.woff2', '200 800', LATIN_EXT);
loadLocal('P18 Unbounded', 'unbounded-latin.woff2', '200 900', LATIN);
loadLocal('P18 Unbounded', 'unbounded-latin-ext.woff2', '200 900', LATIN_EXT);

export const FONT = {
  // Titulares, subtítulos y textos: Manrope (la familia de los reels y carruseles)
  text: "'P18 Manrope', sans-serif",
  // Logotipo "P18": Unbounded es la geometría más cercana al logo (P de panza cuadrada, 8 de contadores rectos)
  logo: "'P18 Unbounded', sans-serif",
};

export const COLOR = {
  lime: '#C2F443', // lima de marca (franja diagonal, logo, palabras clave)
  limeDeep: '#8DB82A', // franja secundaria (más oscura)
  green: '#1D2D25', // fondo verde oscuro
  greenDeep: '#14241C', // fondo más profundo (esquinas)
  ink: '#0E1913', // caja de subtítulos
  teal: '#3E6670', // brillo frío arriba a la derecha
  white: '#FFFFFF',
  cream: '#F2EFE6', // lámina clara de carruseles ("EL MITO")
  grid: 'rgba(194, 244, 67, 0.07)',
};

export const VIDEO = {
  width: 1080,
  height: 1920,
  fps: 30,
};

// Zonas seguras de Reels (1080x1920): arriba ~ 220 px, abajo ~ 420 px (caption + botones), derecha ~ 150 px (íconos)
export const SAFE = {
  top: 150,
  bottom: 430,
  side: 72,
  right: 150,
};
