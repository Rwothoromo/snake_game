#!/bin/bash
set -e

# This Script:
#  A) Patches the missing LT_SYS_SYMBOL_USCORE macro into libffi and reruns autoreconf
#  B) Patches pyjnius & kivy Cython files (long → int, isinstance fixes, etc.)

echo "==== STEP A: FIXING libffi LT_SYS_SYMBOL_USCORE MACRO ===="

fix_libtool_uscore() {
  echo "Searching for libffi directories in /app/.buildozer"
  
  # Find all libffi directories
  local libffi_dirs=$(find /app/.buildozer -name "libffi" -type d 2>/dev/null)
  
  if [ -z "$libffi_dirs" ]; then
    echo "⚠️ No libffi directories found. Have you run buildozer android debug first?"
    return 1
  fi
  
  echo "Found libffi directories:"
  echo "$libffi_dirs"
  echo
  
  local patched=0
  
  # Process each libffi directory
  echo "$libffi_dirs" | while read -r LIBFFI_DIR; do
    if [ -f "$LIBFFI_DIR/configure.ac" ]; then
      echo "🔧 Found configure.ac at $LIBFFI_DIR/configure.ac"
      
      # Apply the patch to this directory
      M4="$LIBFFI_DIR/m4"
      echo "Creating directory $M4"
      mkdir -p "$M4"
      
      # Create the m4 macro file
      echo "Creating m4 macro file"
      cat > "$M4/libtool-symbol-uscore.m4" << 'EOF'
# missing LT_SYS_SYMBOL_USCORE
AC_DEFUN([LT_SYS_SYMBOL_USCORE],[
  AC_CACHE_CHECK([for underscore on global symbols],
    [lt_cv_sys_symbol_underscore],
    lt_cv_sys_symbol_underscore=no
    AC_COMPILE_IFELSE([AC_LANG_PROGRAM([[]],[[]])],
      [lt_cv_sys_symbol_underscore=no],[])
  )
  AC_SUBST([sys_symbol_underscore],[$lt_cv_sys_symbol_underscore])
])
EOF

      # Patch configure.ac
      echo "Patching configure.ac"
      awk 'NR==1{print;next}
           /^AC_INIT/{
             print
             print "m4_pattern_allow([LT_SYS_SYMBOL_USCORE])"
             print "AC_CONFIG_MACRO_DIRS([m4])"
             next
           }
           {print}' \
        "$LIBFFI_DIR/configure.ac" > "$LIBFFI_DIR/configure.ac.patched"
      mv "$LIBFFI_DIR/configure.ac.patched" "$LIBFFI_DIR/configure.ac"

      # Run autoreconf
      echo "Running autoreconf in $LIBFFI_DIR"
      (cd "$LIBFFI_DIR" && autoreconf -vfi)
      
      echo "✅ patched $LIBFFI_DIR/configure.ac"
      patched=$((patched + 1))
    fi
  done
  
  if [ $patched -eq 0 ]; then
    echo "⚠️ Found libffi directories but none had configure.ac to patch"
    return 1
  fi
  
  echo "✅ Successfully patched $patched libffi directories"
  return 0
}

# Temporarily disable exit-on-error for this function call
set +e
fix_libtool_uscore
libffi_result=$?
set -e

# If libffi patching failed, just show a warning but continue
if [ $libffi_result -ne 0 ]; then
  echo "⚠️ WARNING: libffi patching was skipped or failed, but continuing with Python 2-to-3 patching..."
fi

echo
echo "==== STEP B: PATCHING PYTHON-2 → PYTHON-3 ISSUES IN CYTHON FILES ===="

patch_cython_directory() {
  local DIR="$1"
  local FILES
  FILES=$(find "$DIR" -name '*.pyx' -o -name '*.pxi' 2>/dev/null)
  [ -n "$FILES" ] || { echo "⚠️  no Cython files in $DIR"; return; }
  echo "🔍 Patching Cython in $DIR"

  for F in $FILES; do
    echo "— $F"
    cp "$F" "$F.bak"
    local oldsum=$(md5sum "$F.bak" | cut -d' ' -f1)

    # 1) global long(...) → int(...)
    sed -i 's/\<long(/int(/g' "$F"
    # 2) isinstance(..., long) → isinstance(..., int)
    sed -i 's/isinstance(\([^,]*\), *long)/isinstance(\1, int)/g' "$F"
    sed -i 's/isinstance(\([^,]*\), *\(([^)]*), *long\))/isinstance(\1, (\2, int))/g' "$F"
    sed -i 's/isinstance(\([^,]*\), *\(long, *([^)]*)\))/isinstance(\1, (int, \2))/g' "$F"
    # 3) jnius_conversion.pxi dict key long:'J'
    [[ "$F" == *jnius_conversion.pxi ]] \
      && sed -i "s/long: 'J'/int: 'J'  # patched/g" "$F"

    local newsum=$(md5sum "$F" | cut -d' ' -f1)
    if [ "$oldsum" != "$newsum" ]; then
      echo "  ✅ patched"
      diff -u "$F.bak" "$F" | head -n20 \
        && echo "  ... ($(diff -u "$F.bak" "$F" | wc -l) lines changed)"
    else
      echo "  ℹ️  no changes"
    fi
    rm "$F.bak"
  done
}

echo "▶️  Patching pyjnius…"
find "${APP_DIR}/.buildozer" -path '*/build/other_builds/pyjnius-*' -type d \
  | while read D; do patch_cython_directory "$D"; done

echo "▶️  Patching kivy…"
find "${APP_DIR}/.buildozer" -path '*/build/other_builds/kivy-*' -type d \
  | while read D; do patch_cython_directory "$D"; done

echo
echo "==== ALL PATCHES COMPLETE ===="
echo "Now run: buildozer -v android debug --log-level 2 --debug 2>&1 | tee logs/buildozer.log"
echo