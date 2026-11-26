import React from 'react';
import {AbsoluteFill} from 'remotion';
import {loadFont as unb} from '@remotion/google-fonts/Unbounded';
import {loadFont as kro} from '@remotion/google-fonts/KronaOne';
import {loadFont as sg} from '@remotion/google-fonts/SpaceGrotesk';
import {loadFont as lex} from '@remotion/google-fonts/Lexend';
import {loadFont as sora} from '@remotion/google-fonts/Sora';
import {loadFont as man} from '@remotion/google-fonts/Manrope';
import {loadFont as exo} from '@remotion/google-fonts/Exo2';
import {loadFont as tom} from '@remotion/google-fonts/Tomorrow';
const fonts = [unb(), kro(), sg(), lex(), sora(), man(), exo(), tom()];
export const FontTest: React.FC = () => (
  <AbsoluteFill style={{background: '#14241c', padding: 40, display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 20}}>
    {fonts.map((f) => (
      <div key={f.fontFamily} style={{color: '#c2f443'}}>
        <div style={{fontFamily: f.fontFamily, fontWeight: 800, fontSize: 150, lineHeight: 1}}>P18</div>
        <div style={{color: '#fff', fontSize: 22, fontFamily: 'sans-serif'}}>{f.fontFamily}</div>
      </div>
    ))}
  </AbsoluteFill>
);
