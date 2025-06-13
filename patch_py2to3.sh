#!/bin/bash
set -e

echo "==== PATCHING PYTHON 3 CONFIGURE SCRIPT FOR NDK 25+ ===="
# Find the python3 configure script in the build directory
mapfile -t CONFIGURE_FILES < <(find "${APP_DIR}/.buildozer" -path "*/other_builds/python3/*/python3/configure")

if [ ${#CONFIGURE_FILES[@]} -eq 0 ]; then
    echo "— Python 3 configure script not found. Skipping patch."
else
    for conf_file in "${CONFIGURE_FILES[@]}"; do
        if [ -f "$conf_file" ]; then
            echo "— Patching LDFLAGS in: $conf_file"
            # Use sed to insert the linker flag after the 'esac' block
            # This is more robust than a patch file.
            sed -i "/^esac$/a LDFLAGS=\"-L\$prefix/lib \$LDFLAGS -L\$UNIVERSE_BUILD_PREFIX/lib\"" "$conf_file"
        fi
    done
fi

echo "==== PATCHING 'noexcept' ISSUE IN CYTHON FILES ===="
# Find all .pyx and .pxi files in the build directory
find "${APP_DIR}/.buildozer" -name '*.pyx' -o -name '*.pxi' -print0 | while IFS= read -r -d '' file; do
    if grep -q "noexcept:" "$file"; then
        echo "— Patching noexcept in: $file"
        sed -i 's/) *noexcept:/):/g' "$file"
    fi
done

echo "==== PATCHES COMPLETE ===="