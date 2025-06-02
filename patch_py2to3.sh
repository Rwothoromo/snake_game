#!/bin/bash
set -e

echo
echo "==== PATCHING PYTHON-2 -> PYTHON-3 ISSUES IN CYTHON FILES (Kivy, Pyjnius, etc.) ===="

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

    # 1) global long(...) -> int(...)
    sed -i 's/\<long(/int(/g' "$F"

    # 2) isinstance(..., long) -> isinstance(..., int)
    sed -i 's/isinstance(\([^,]*\), *long)/isinstance(\1, int)/g' "$F"
    sed -i 's/isinstance(\([^,]*\), *\(([^)]*), *long\))/isinstance(\1, (\2, int))/g' "$F"
    sed -i 's/isinstance(\([^,]*\), *\(long, *([^)]*)\))/isinstance(\1, (int, \2))/g' "$F"
    # More generic isinstance(foo, (int, long)) -> isinstance(foo, int)
    sed -i 's/isinstance(\([^,]*\), *(int, *long))/isinstance(\1, int)/g' "$F"
    sed -i 's/isinstance(\([^,]*\), *(long, *int))/isinstance(\1, int)/g' "$F"

    # 3) Specifically target jnius_conversion.pxi for 'long: 'J''
    if [[ "$F" == *jnius_conversion.pxi ]]; then
      # Fix with comma - ensure comma stays OUTSIDE the comment
      sed -i "s/long: 'J',/int: 'J',  # patched/g" "$F"
      # Fix without comma - don't add a trailing comma in this case
      sed -i "s/long: 'J'$/int: 'J'  # patched/g" "$F"
      # Extra safety check - fix any incorrect patching that might have occurred
      sed -i "s/int: 'J'  # patched,/int: 'J',  # patched/g" "$F"
      echo "  Targeting jnius_conversion.pxi specific fix for 'long: 'J'' in $F"
      # This sed command replaces lines matching the pattern (typically 'long: 'J',')
      # with a standardized 'int: 'J',' line.
      # It looks for 'long' followed by ':', then 'J', with flexible spacing, an optional comma, and matches the whole line.
      if grep -q -E "[[:space:]]*long[[:space:]]*:[[:space:]]*'J'" "$F"; then
        sed -i -E "s/^[[:space:]]*(long)[[:space:]]*:[[:space:]]*('J')[[:space:]]*[,]?.*$/            int: 'J',  # patched by patch_py2to3.sh/" "$F"
        echo "    ✅ Successfully patched 'long: 'J'' to 'int: 'J',' in $F."
      else
        echo "    ℹ️  Pattern 'long: 'J'' not found in $F. Skipping this specific jnius_conversion.pxi patch."
      fi
    fi
    # 4. Find and fix Kivy weakproxy.pyx
    find ${APP_DIR}/.buildozer -name "weakproxy.pyx" -exec sed -i 's/def __long__(self):/def __index__(self):/' {} \;
    find ${APP_DIR}/.buildozer -name "weakproxy.pyx" -exec sed -i 's/return long(self.__ref__())/return int(self.__ref__())/' {} \;

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
echo "==== CYTHON PATCHES COMPLETE ===="
echo "Now run: buildozer -v android debug --log-level 0 --debug 2>&1 | tee logs/buildozer.log"
echo