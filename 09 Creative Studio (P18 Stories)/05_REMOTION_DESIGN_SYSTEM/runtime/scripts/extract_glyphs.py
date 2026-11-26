"""Extrae los contornos de "P18" (y dígitos) en Manrope ExtraBold (wght 800) como paths SVG para extruirlos en 3D.
Uso: <python con fonttools> scripts/extract_glyphs.py <Manrope-Variable.ttf> src/assets/p18-glyphs.json
"""
import json, sys
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
from fontTools.pens.svgPathPen import SVGPathPen

src, out = sys.argv[1], sys.argv[2]
font = instantiateVariableFont(TTFont(src), {"wght": 800})
gs = font.getGlyphSet(); cmap = font.getBestCmap(); upm = font["head"].unitsPerEm
glyphs = {}
for ch in "P0123456789":
    name = cmap[ord(ch)]
    pen = SVGPathPen(gs)
    gs[name].draw(pen)  # unidades de fuente, y hacia arriba (three.js las usa tal cual)
    glyphs[ch] = {"d": pen.getCommands(), "advance": gs[name].width}
json.dump({"unitsPerEm": upm, "capHeight": getattr(font["OS/2"], "sCapHeight", 0), "glyphs": glyphs}, open(out, "w"))
print("ok", out, upm, {k: v["advance"] for k, v in glyphs.items() if k in "P18"})
