#!/bin/bash
# Direct fix for jnius_conversion.pxi

echo "Looking for jnius_conversion.pxi files..."
CONVERSION_FILES=$(find ${APP_DIR}/.buildozer -path "*/pyjnius*" -name "jnius_conversion.pxi")

# Check if files were found
if [ -z "$CONVERSION_FILES" ]; then
  echo "❌ ERROR: Could not find any jnius_conversion.pxi files"
  exit 1
fi

# Process each file individually
echo "Found $(echo "$CONVERSION_FILES" | wc -l) conversion files"

# Loop through each file
while IFS= read -r file; do
  if [ -f "$file" ]; then
    echo "Processing: $file"
    
    # Make a backup
    cp "$file" "${file}.bak"
    
    # Replace the exact pattern causing the issue
    sed -i 's/            long: .*J.*,/            int: '\''J'\'',  # patched long->int/g' "$file"
    
    # More comprehensive fixes
    sed -i 's/\s*long:\s*'\''J'\''[,]*/            int: '\''J'\'',  # patched/g' "$file"
    
    # Check if the changes were applied
    if grep -q "patched" "$file"; then
      echo "✅ Successfully patched $file"
      diff -u "${file}.bak" "$file" | head -n 20
    else
      echo "⚠️ No patched marker in $file, checking if 'long' was removed"
      if ! grep -q "long: 'J'" "$file"; then
        echo "✅ Fix appears successful (no 'long: J' found)"
      else
        echo "❌ Failed to patch $file (still contains 'long: J')"
        echo "Contents of line with 'long: J':"
        grep "long: 'J'" "$file"
      fi
    fi
  else
    echo "❌ File not found: $file"
  fi
done <<< "$CONVERSION_FILES"

echo "Patching complete!"