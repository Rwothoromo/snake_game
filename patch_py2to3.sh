#!/bin/bash
set -e

echo "==== PATCHING 'noexcept' ISSUE IN CYTHON FILES ===="

# Find all .pyx and .pxi files in the build directory
# and remove the 'noexcept:' keyword which causes issues with some compilers.
find "${APP_DIR}/.buildozer" -name '*.pyx' -o -name '*.pxi' -print0 | while IFS= read -r -d '' file; do
    if grep -q "noexcept:" "$file"; then
        echo "— Patching noexcept in: $file"
        sed -i 's/) *noexcept:/):/g' "$file"
    fi
done

echo "==== CYTHON PATCHES COMPLETE ===="