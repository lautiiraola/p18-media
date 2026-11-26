export type CaptionWord = {text: string; t0: number; active?: boolean};
export type Caption = {unit: number; start: number; end: number; words: CaptionWord[]};
export type Sfx = {file: string; at: number; vol: number};
export type Music = {file: string; points: [number, number][]};

// Cada escena trae sus propios campos según `type`; el dispatcher los interpreta.
export type Scene = {
  id: string;
  t: [number, number];
  type: string;
  kicker?: string;
  bg?: 'deep' | 'paper';
  [key: string]: unknown;
};

export type StoryData = {
  videoId: string;
  fps: number;
  durationInFrames: number;
  voice: string;
  music?: Music;
  sfx: Sfx[];
  captions: Caption[];
  scenes: Scene[];
  footer?: string;
};

export type StoryProps = {data: StoryData | null};
