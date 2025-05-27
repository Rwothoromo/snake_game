#!/bin/bash
set -e

# This Script:
#  A) Patches the missing LT_SYS_SYMBOL_USCORE macro into libffi and reruns autoreconf
#  B) Patches pyjnius & kivy Cython files (long → int, isinstance fixes, etc.)

echo "==== STEP A: FIXING libffi LT_SYS_SYMBOL_USCORE MACRO ===="

fix_libtool_uscore() {
  ANDROID_PLAT="${HOME}/.buildozer/android/platform"
  for ROOT in \
      "$ANDROID_PLAT"/build-arm64-v8a_armeabi-v7a \
      "$ANDROID_PLAT"/build-armeabi-v7a_arm64-v8a; do

    find "$ROOT" -path "*/other_builds/libffi/*/configure.ac" \
     | while read -r CFG; do
        [ -f "$CFG" ] || continue
        DIR=$(dirname "$CFG")
        M4="$DIR/m4"
        echo "🔧 Patching libffi in $DIR"
        mkdir -p "$M4"

        # 1) drop in the missing macro
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

        # 2) patch configure.ac: allow the macro & add m4 dir
        awk 'NR==1{print;next}
             /^AC_INIT/{
               print
               print "m4_pattern_allow([LT_SYS_SYMBOL_USCORE])"
               print "AC_CONFIG_MACRO_DIRS([m4])"
               next
             }
             {print}' \
          "$CFG" > "$CFG.patched"
        mv "$CFG.patched" "$CFG"

        # 3) rerun autoreconf so libffi picks it up
        pushd "$DIR" >/dev/null
          autoreconf -vfi
        popd >/dev/null

        echo "  ✅ patched $CFG"
    done
  done
}

fix_libtool_uscore


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
find ~/.buildozer -path '*/build/other_builds/pyjnius-*' -type d \
  | while read D; do patch_cython_directory "$D"; done

echo "▶️  Patching kivy…"
find ~/.buildozer -path '*/build/other_builds/kivy-*' -type d \
  | while read D; do patch_cython_directory "$D"; done

echo
echo "==== ALL PATCHES COMPLETE ===="
echo "Now run: buildozer -v android debug --log-level 2"