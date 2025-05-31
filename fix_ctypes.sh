#!/bin/bash

echo "Fixing ctypes module in host Python..."

# Specifically target the three most important ctypes files
CTYPES_FILES=(
    "${ANDROID_PLAT}/build-arm64-v8a_armeabi-v7a/build/other_builds/hostpython3/desktop/hostpython3/Lib/ctypes/__init__.py"
    "${ANDROID_PLAT}/build-arm64-v8a_armeabi-v7a/build/other_builds/python3/arm64-v8a__ndk_target_23/python3/Lib/ctypes/__init__.py"
    "${ANDROID_PLAT}/build-arm64-v8a_armeabi-v7a/build/other_builds/python3/armeabi-v7a__ndk_target_23/python3/Lib/ctypes/__init__.py"
)

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