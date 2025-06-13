#!/bin/bash

echo "Fixing ctypes module in host Python..."

# Ensure ANDROID_PLAT is set
if [ -z "$ANDROID_PLAT" ]; then
    echo "Error: ANDROID_PLAT environment variable is not set."
    exit 2
fi

# Find all ctypes __init__.py files under ANDROID_PLAT
mapfile -t CTYPES_FILES < <(find "$ANDROID_PLAT" -type f -path "*/ctypes/__init__.py")
echo "Found ctypes files:"
for f in "${CTYPES_FILES[@]}"; do
    echo "  $f"
done

PATCHED_COUNT=0

# Process each file
for INIT_FILE in "${CTYPES_FILES[@]}"; do
    if [ -f "$INIT_FILE" ]; then
        echo "Patching: $INIT_FILE"
        
        # Check if already patched
        if grep -q "_ctypes import c_long" "$INIT_FILE"; then
            echo "  ✓ Already patched, skipping"
            ((PATCHED_COUNT++))
            continue
        fi
        
        # Make a backup
        cp "$INIT_FILE" "${INIT_FILE}.bak"
        
        # Add the missing import at the beginning of the file
        sed -i '1s/^/from _ctypes import c_long, c_ulong\n/' "$INIT_FILE"
        
        # Verify patch was applied
        if grep -q "_ctypes import c_long" "$INIT_FILE"; then
            echo "  ✅ Successfully patched"
            ((PATCHED_COUNT++))
        else
            echo "  ❌ Failed to patch"
        fi
    else
        echo "File not found: $INIT_FILE"
    fi
done

if [ $PATCHED_COUNT -gt 0 ]; then
    echo "✅ Patched $PATCHED_COUNT ctypes module(s) successfully"
    exit 0
else
    echo "❌ No ctypes modules were patched"
    
    # Last resort - try to use sudo
    echo "Trying with elevated permissions..."
    for INIT_FILE in "${CTYPES_FILES[@]}"; do
        if [ -f "$INIT_FILE" ]; then
            echo "Attempting with sudo: $INIT_FILE"
            sudo cp "$INIT_FILE" "${INIT_FILE}.bak"
            echo 'from _ctypes import c_long, c_ulong' | sudo tee -a "$INIT_FILE.tmp" > /dev/null
            sudo cat "$INIT_FILE" >> "$INIT_FILE.tmp"
            sudo mv "$INIT_FILE.tmp" "$INIT_FILE"
        fi
    done
    
    exit 1
fi