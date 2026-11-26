#!/usr/bin/env bash
set -euo pipefail

studio_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

required_dirs=(
  00_SISTEMA
  01_IDENTIDAD_P18
  02_REFERENCIAS
  03_SISTEMA_NARRATIVO
  04_SISTEMA_AUDIOVISUAL
  05_REMOTION_DESIGN_SYSTEM
  06_BIBLIOTECA_COMPARTIDA
  07_COLA_DE_HISTORIAS
  08_NUEVO_VIDEO_TEMPLATE
  09_VIDEOS_EN_PRODUCCION
  10_VIDEOS_TERMINADOS
)

required_files=(
  START_HERE.txt
  README.txt
  CLAUDE.txt
  ESTADO_DEL_ESTUDIO.txt
  00_SISTEMA/flujo-diario.txt
  01_IDENTIDAD_P18/story-format.txt
  02_REFERENCIAS/noticias-explicadas/reference-pack.txt
  03_SISTEMA_NARRATIVO/flujo-narrativo.txt
  04_SISTEMA_AUDIOVISUAL/direccion-de-edicion.txt
  05_REMOTION_DESIGN_SYSTEM/arquitectura.txt
  07_COLA_DE_HISTORIAS/story-scorecard.yaml
  08_NUEVO_VIDEO_TEMPLATE/manifest.yaml
  08_NUEVO_VIDEO_TEMPLATE/04_assets/asset-registry.csv
  08_NUEVO_VIDEO_TEMPLATE/05_storyboard/audiovisual-script.csv
  08_NUEVO_VIDEO_TEMPLATE/09_qa/qa-checklist.txt
  10_VIDEOS_TERMINADOS/INDEX.txt
)

for path in "${required_dirs[@]}"; do
  test -d "$studio_root/$path" || { echo "FALTA DIRECTORIO: $path"; exit 1; }
done

for path in "${required_files[@]}"; do
  test -s "$studio_root/$path" || { echo "FALTA ARCHIVO: $path"; exit 1; }
done

if find "$studio_root" -type f -name '*.md' | grep -q .; then
  echo "ERROR: se encontraron archivos .md"
  find "$studio_root" -type f -name '*.md'
  exit 1
fi

grep -q '1080 × 1920' "$studio_root/01_IDENTIDAD_P18/story-format.txt"
grep -q 'No usás Canva' "$studio_root/CLAUDE.txt"
grep -q 'Sin avatares' "$studio_root/00_SISTEMA/checklist-general.txt"
grep -q 'background' "$studio_root/02_REFERENCIAS/p18-stories/james-dyson-ejemplo/visual-reference/frame.html"
grep -q 'status: idea' "$studio_root/08_NUEVO_VIDEO_TEMPLATE/manifest.yaml"

echo "P18 CREATIVE STUDIO: VALIDACIÓN CORRECTA"
