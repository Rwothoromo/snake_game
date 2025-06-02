# prebuild.py
import shutil
import os

def prebuild():
    for d in [
        ".buildozer/android/platform/build-arm64-v8a_armeabi-v7a/build/bootstrap_builds/sdl2/jni/SDL2_image/external/jpeg",
        ".buildozer/android/platform/build-arm64-v8a_armeabi-v7a/build/bootstrap_builds/sdl2/jni/SDL2_image/external/libpng",
    ]:
        if os.path.exists(d):
            shutil.rmtree(d)

if __name__ == "__main__":
    prebuild()