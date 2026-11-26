// Carga local de las familias P18 (public/fonts). El render no depende de internet.
// Manrope (base) · Unbounded (display, geometría del logo) · Instrument Serif (editorial, citas) · JetBrains Mono (documental)
import {continueRender, delayRender, staticFile} from 'remotion';

const FACES: {family: string; file: string; weight: string; style?: string}[] = [
  {family: 'P18 Manrope', file: 'fonts/Manrope-Variable.ttf', weight: '200 800'},
  {family: 'P18 Unbounded', file: 'fonts/Unbounded-Variable.ttf', weight: '200 900'},
  {family: 'P18 Serif', file: 'fonts/InstrumentSerif-Regular.ttf', weight: '400'},
  {family: 'P18 Serif', file: 'fonts/InstrumentSerif-Italic.ttf', weight: '400', style: 'italic'},
  {family: 'P18 Mono', file: 'fonts/JetBrainsMono-Variable.ttf', weight: '100 800'},
];

let loaded = false;
export const loadFonts = () => {
  if (loaded || typeof window === 'undefined' || typeof FontFace === 'undefined') return;
  loaded = true;
  for (const f of FACES) {
    const handle = delayRender(`Cargando ${f.family} (${f.file})`);
    const face = new FontFace(f.family, `url(${staticFile(f.file)}) format('truetype')`, {weight: f.weight, style: f.style ?? 'normal'});
    face
      .load()
      .then((loadedFace) => {
        document.fonts.add(loadedFace);
        continueRender(handle);
      })
      .catch((err) => {
        // Si un video viejo no tiene la fuente, se sigue con el fallback
        console.error(err);
        continueRender(handle);
      });
  }
};
