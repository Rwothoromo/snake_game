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

def prebuild_hook(ctx):
    arch = ctx.arch
    if arch.startswith('arm'):
        os.environ['CC'] = os.path.join(ctx.ndk_dir, 'toolchains/llvm/prebuilt/linux-x86_64/bin/armv7a-linux-androideabi23-clang')
        os.environ['CXX'] = os.path.join(ctx.ndk_dir, 'toolchains/llvm/prebuilt/linux-x86_64/bin/armv7a-linux-androideabi23-clang++')
    elif arch == 'arm64':
        os.environ['CC'] = os.path.join(ctx.ndk_dir, 'toolchains/llvm/prebuilt/linux-x86_64/bin/aarch64-linux-android23-clang')
        os.environ['CXX'] = os.path.join(ctx.ndk_dir, 'toolchains/llvm/prebuilt/linux-x86_64/bin/aarch64-linux-android23-clang++')

if __name__ == "__main__":
    prebuild()