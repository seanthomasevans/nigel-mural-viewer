#!/bin/bash
# Composite each mural onto a canvas matching the container panel aspect
# ratio, padded with the container's metal colour. This preserves the
# mural's native proportions and lets the container metal show on the
# remaining panel area, instead of stretching the mural to fill the panel.
#
# Front panel: 6.058 m × 2.591 m  → aspect 2.338
# End panel:   2.438 m × 2.591 m  → aspect 0.941
# Metal colour from build_container.py RGB(0.42, 0.47, 0.50) → #6b7880

set -euo pipefail

cd "$(dirname "$0")"

METAL="#6b7880"
mkdir -p textures/panels

# Front panels (mural placed at native height, padded horizontally)
# mural-1: 2400×1596 → canvas 3731×1596
magick -size 3731x1596 "xc:$METAL" \
  textures/mural-1-landscape.jpg -gravity center -composite \
  -quality 92 textures/panels/front-v1.jpg

# mural-2: 2400×1435 → canvas 3355×1435
magick -size 3355x1435 "xc:$METAL" \
  textures/mural-2-landscape.jpg -gravity center -composite \
  -quality 92 textures/panels/front-v2.jpg

# End panel (mural placed at native width, padded vertically)
# mural-3: 2400×2397 → canvas 2400×2551
magick -size 2400x2551 "xc:$METAL" \
  textures/mural-3-square.jpg -gravity center -composite \
  -quality 92 textures/panels/end.jpg

echo
echo "Wrote:"
for f in textures/panels/*.jpg; do
  echo "  $f $(sips -g pixelWidth -g pixelHeight "$f" | tail -2 | tr -d ' \n')"
done
