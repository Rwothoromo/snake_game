echo "Patching SDL2_image download.sh to always remove libpng and jpeg directories before cloning..."

find .buildozer -path "*/SDL2_image/external/download.sh" | while read SH; do
  sed -i '/git clone.*libpng/i rm -rf libpng' "$SH"
  sed -i '/git clone.*jpeg/i rm -rf jpeg' "$SH"
done

echo "Patch complete."