#!/bin/bash
set -e  # Exit on error

echo "=== VERIFYING AND FINALIZING ANDROID SDK SETUP ==="

# Ensure APP_DIR, ANDROID_SDK_ROOT, and HOME are set
if [ -z "$APP_DIR" ] || [ -z "$ANDROID_SDK_ROOT" ] || [ -z "$HOME" ]; then
  echo "Error: APP_DIR, ANDROID_SDK_ROOT, or HOME environment variables are not set."
  exit 1
fi

# PRE-STEP: Ensure $HOME/.android directory exists for SDK manager
echo "Pre-Step: Ensuring $HOME/.android directory..."
mkdir -p "$HOME/.android"
# Ownership should be handled by Dockerfile or chown in README if this script is run with sudo

# 1. Ensure cmdline-tools 'latest' directory exists and binaries are executable
#    The Dockerfile should have created this. This is a verification and permission fix.
echo "Step 1: Verifying cmdline-tools and permissions..."
if [ ! -d "${ANDROID_SDK_ROOT}/cmdline-tools/latest/bin" ]; then
    echo "Error: ${ANDROID_SDK_ROOT}/cmdline-tools/latest/bin not found. SDK setup in Dockerfile might have failed."
    # Attempt to re-create it (similar to Dockerfile logic, but without sudo for user-owned dirs)
    echo "Attempting to re-create cmdline-tools..."
    mkdir -p "${ANDROID_SDK_ROOT}/cmdline-tools"
    cd "${ANDROID_SDK_ROOT}/cmdline-tools"
    if [ -f "tools.zip" ]; then rm tools.zip; fi # Clean up previous attempt
    if [ -d "cmdline-tools" ]; then rm -rf cmdline-tools; fi # Clean up previous attempt
    wget -q https://dl.google.com/android/repository/commandlinetools-linux-11076708_latest.zip -O tools.zip
    unzip -q tools.zip
    rm tools.zip
    mv cmdline-tools latest || true
    cd "$APP_DIR"
else
    echo "cmdline-tools/latest/bin found."
fi
find "${ANDROID_SDK_ROOT}/cmdline-tools/latest/bin" -type f -exec chmod +x {} \;

# 2. Ensure legacy tools/bin/sdkmanager symlink exists
#    The Dockerfile should have created this.
echo "Step 2: Verifying legacy sdkmanager symlink..."
mkdir -p "${ANDROID_SDK_ROOT}/tools/bin"
if [ ! -L "${ANDROID_SDK_ROOT}/tools/bin/sdkmanager" ]; then
    echo "Legacy symlink not found, creating..."
    ln -sf "${ANDROID_SDK_ROOT}/cmdline-tools/latest/bin/sdkmanager" "${ANDROID_SDK_ROOT}/tools/bin/sdkmanager"
else
    echo "Legacy symlink found."
fi

# 3. Accept licenses (crucial)
echo "Step 3: Accepting licenses..."
yes | "${ANDROID_SDK_ROOT}/cmdline-tools/latest/bin/sdkmanager" --sdk_root="${ANDROID_SDK_ROOT}" --licenses || echo "License acceptance failed, but continuing."

# 4. Ensure platform-tools and necessary build-tools for API 30 are present
#    Buildozer should handle this, but we can pre-install them here to be certain.
echo "Step 4: Ensuring platform-tools and build-tools for API 30..."
yes | "${ANDROID_SDK_ROOT}/cmdline-tools/latest/bin/sdkmanager" --sdk_root="${ANDROID_SDK_ROOT}" \
    "platform-tools" \
    "platforms;android-30" \
    "build-tools;30.0.3" # buildozer.spec uses API 30, ensure corresponding build-tools

# Ensure platform-tools binaries are executable
if [ -d "${ANDROID_SDK_ROOT}/platform-tools" ]; then
    find "${ANDROID_SDK_ROOT}/platform-tools" -type f -exec chmod +x {} \;
else
    echo "Warning: platform-tools directory not found after sdkmanager run."
fi

# 5. Verify sdkmanager is findable and executable
echo "Step 5: Verifying sdkmanager post-setup..."
echo "Expected sdkmanager at: ${ANDROID_SDK_ROOT}/cmdline-tools/latest/bin/sdkmanager"
ls -la "${ANDROID_SDK_ROOT}/cmdline-tools/latest/bin/sdkmanager" || echo "sdkmanager binary not found at direct path!"
echo "PATH: $PATH"
echo "Which sdkmanager: $(which sdkmanager || echo 'sdkmanager not in PATH via which')"
"${ANDROID_SDK_ROOT}/cmdline-tools/latest/bin/sdkmanager" --version || echo "sdkmanager direct execution failed"

echo "=== ANDROID SDK VERIFICATION/FINALIZATION COMPLETE ==="