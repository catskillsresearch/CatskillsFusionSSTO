#!/bin/bash
echo "--- CATSKILLS FUSION SSTO: VISUAL ASSETS ---"
printf "%-10s %-15s %-10s %-10s\n" "EXT" "TYPE" "COUNT" "SIZE"
echo "--------------------------------------------------------"

# PNG/JPG are for repainting, .ac are the 3D models for Blender
assets=( "png:Textures" "jpg:Thumbnails" "ac:3D Models" )

for a in "${assets[@]}"; do
    ext="${a%%:*}"
    desc="${a#*:}"
    count=$(find . -type f -name "*.$ext" | wc -l)
    size=$(find . -type f -name "*.$ext" -exec du -ch {} + | grep total$ | awk '{print $1}')
    printf "%-10s %-15s %-10s %-10s\n" ".$ext" "$desc" "$count" "${size:-0K}"
done

echo "--------------------------------------------------------"
echo "TOTAL REPAINT AREA: $(find . -type f \( -name "*.png" -o -name "*.jpg" \) -exec du -ch {} + | grep total$ | awk '{print $1}')"
