// Generado por _work/registrar.py: no editar a mano
import {EntrevistaData} from '../compositions/Entrevista';
import {ClipData} from '../compositions/Clip';
import {CarruselData} from '../compositions/Carrusel';
import argento from './argento.json';
import argento_clips from './argento_clips.json';
import argento_carr from './argento_carruseles.json';
import german from './german.json';
import german_clips from './german_clips.json';
import german_carr from './german_carruseles.json';
import leo from './leo.json';
import leo_clips from './leo_clips.json';
import leo_carr from './leo_carruseles.json';
import mariano from './mariano.json';
import mariano_clips from './mariano_clips.json';
import mariano_carr from './mariano_carruseles.json';
import moni from './moni.json';
import moni_clips from './moni_clips.json';
import moni_carr from './moni_carruseles.json';
import tom from './tom.json';
import tom_clips from './tom_clips.json';
import tom_carr from './tom_carruseles.json';
import victoria from './victoria.json';
import victoria_clips from './victoria_clips.json';
import victoria_carr from './victoria_carruseles.json';

export const PERSONAS: {slug: string; principal: EntrevistaData; clips?: ClipData[]; carruseles?: CarruselData[]}[] = [
  {slug: 'argento', principal: argento as unknown as EntrevistaData, clips: (argento_clips as unknown as {clips: ClipData[]}).clips, carruseles: (argento_carr as unknown as {carruseles: CarruselData[]}).carruseles},
  {slug: 'german', principal: german as unknown as EntrevistaData, clips: (german_clips as unknown as {clips: ClipData[]}).clips, carruseles: (german_carr as unknown as {carruseles: CarruselData[]}).carruseles},
  {slug: 'leo', principal: leo as unknown as EntrevistaData, clips: (leo_clips as unknown as {clips: ClipData[]}).clips, carruseles: (leo_carr as unknown as {carruseles: CarruselData[]}).carruseles},
  {slug: 'mariano', principal: mariano as unknown as EntrevistaData, clips: (mariano_clips as unknown as {clips: ClipData[]}).clips, carruseles: (mariano_carr as unknown as {carruseles: CarruselData[]}).carruseles},
  {slug: 'moni', principal: moni as unknown as EntrevistaData, clips: (moni_clips as unknown as {clips: ClipData[]}).clips, carruseles: (moni_carr as unknown as {carruseles: CarruselData[]}).carruseles},
  {slug: 'tom', principal: tom as unknown as EntrevistaData, clips: (tom_clips as unknown as {clips: ClipData[]}).clips, carruseles: (tom_carr as unknown as {carruseles: CarruselData[]}).carruseles},
  {slug: 'victoria', principal: victoria as unknown as EntrevistaData, clips: (victoria_clips as unknown as {clips: ClipData[]}).clips, carruseles: (victoria_carr as unknown as {carruseles: CarruselData[]}).carruseles},
];
