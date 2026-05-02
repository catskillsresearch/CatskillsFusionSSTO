#!/bin/bash
echo "--- CATSKILLS FUSION SSTO: LOGIC INVENTORY ---"
printf "%-10s %-15s %-10s\n" "EXT" "LANGUAGE" "LINES"
echo "------------------------------------------"

# Define the file types
types=( "nas:Nasal (Scripting)" "xml:XML (Systems/Logic)" "eff:GLSL Effects" "js:JSBSim (Math)" )

for t in "${types[@]}"; do
    ext="${t%%:*}"
    lang="${t#*:}"
    lines=$(find . -type f -name "*.$ext" -exec cat {} + 2>/dev/null | wc -l)
    printf "%-10s %-15s %-10s\n" ".$ext" "$lang" "$lines"
done

echo "------------------------------------------"
echo "TOTAL LOGIC LINES: $(find . -type f \( -name "*.nas" -o -name "*.xml" -o -name "*.eff" -o -name "*.js" \) -exec cat {} + | wc -l)"
