# Snake Game in Python

A classic Snake 🐍 Game 🎮 implemented in Python using Pygame and Kivy. GitHub Copilot assisted in development. Guide the snake to eat food, grow longer, and avoid collisions with walls or itself.

## Project Structure

```
snake_game
├── m4/                 # Contains m4 macros needed for Android builds
├── logs/               # Build and runtime logs
├── bin/                # Output directory for APKs (gitignored)
├── .buildozer/         # Generated during Android builds (gitignored)
├── src/                # Core game classes and logic
│   ├── snake.py        # Snake class
│   ├── food.py         # Food class
│   └── game.py         # Pygame-based Game class (optional)
├── main.py             # Entry point (Kivy-based)
├── requirements.txt    # Python dependencies
├── buildozer.spec      # Buildozer config for APK builds
├── Dockerfile          # Dockerfile for Android APK builds
├── docker-compose.yml  # Docker Compose workflow
├── .gitignore          # Git ignore rules
├── best_score.txt      # Stores best score
└── README.md           # Project documentation
```

---

## Running the Game on Desktop

1. **Clone the repository:**
    ```bash
    git clone <repo-url>
    cd snake_game
    ```

2. **Set up a virtual environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # Linux/macOS
    # venv\Scripts\activate   # Windows
    ```

3. **Install dependencies:**
    ```bash
    pip install --upgrade pip
    pip install -r requirements.txt
    pip install pygame appdirs
    pip install --upgrade python-for-android
    ```

4. **(Optional) Reset best score:**
    ```bash
    echo 0 > best_score.txt
    ```

5. **Run the game:**
    ```bash
    python3 main.py
    ```

---

## Building and Running on Android (with Docker)

### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop) installed

### Steps

1.  **Clone the repository, enter the directory, remove orphan containers, and clear the Buildozer cache volume.**
    This ensures a completely clean environment.
    ```bash
    docker-compose down --remove-orphans
    docker volume rm snake_game_buildozer_cache || true 
    # The volume name is typically <project_directory_name>_buildozer_cache
    # If 'snake_game_buildozer_cache' does not work, check 'docker volume ls'
    ```

2. **Build and start the Docker container:**
    Using the amazing buildozer for this. See [quickstart docs](https://buildozer.readthedocs.io/en/latest/quickstart.html).
    ```bash
    docker-compose build && docker-compose run buildozer bash
    ```

    Or, without Compose:
    ```bash
    docker build -t kivy-buildozer .
    docker run --dns 8.8.8.8 --memory=4g --cpus=2 --rm -it \
    -v "$PWD/src":${APP_DIR}/src \
    -v "$PWD/main.py":${APP_DIR}/main.py \
    -v "$PWD/requirements.txt":${APP_DIR}/requirements.txt \
    -v "$PWD/buildozer.spec":${APP_DIR}/buildozer.spec \
    -v "$PWD/patch_py2to3.sh":${APP_DIR}/patch_py2to3.sh \
    -v "$PWD/fix_ctypes.sh":${APP_DIR}/fix_ctypes.sh \
    -v "$PWD/fix_py2to3.sh":${APP_DIR}/fix_py2to3.sh \
    -v "$PWD/patch_jnius.sh":${APP_DIR}/patch_jnius.sh \
    -v "$PWD/bin":${APP_DIR}/bin \
    kivy-buildozer bash
    ```

    **Tip:** To avoid cache, add `--no-cache`.

    **Tip:** To clean Buildozer state: `buildozer android clean`.

3.  **Build your APK inside the container:**
    ```bash
    # Ensure all scripts are executable
    sudo chmod +x fix_android_sdk.sh patch_py2to3.sh fix_ctypes.sh fix_py2to3.sh patch_jnius.sh

    # STEP 1: Ensure builduser owns the .buildozer directory and its contents
    # This is crucial as Dockerfile might create some parts as root before user switch,
    # or volume mounts might have different ownership.
    sudo chown -R $(whoami):$(whoami) $HOME/.buildozer
    sudo chown -R $(whoami):$(whoami) $APP_DIR/.buildozer # Mounted volume

    # STEP 2: Run the SDK verification and finalization script
    # This ensures cmdline-tools are present, executable, licenses accepted, and API 30 tools installed.
    ./fix_android_sdk.sh

    # STEP 3: Explicitly set PATH for the current session to include SDK tools
    # This makes sure the current shell session can find sdkmanager and other tools.
    export PATH="${ANDROID_SDK_ROOT}/cmdline-tools/latest/bin:${ANDROID_SDK_ROOT}/platform-tools:${ANDROID_SDK_ROOT}/tools/bin:${HOME}/.local/bin:${PATH}"
    
    # STEP 4: Verify sdkmanager is found and executable IN THIS SHELL
    echo "Verifying sdkmanager in current shell:"
    which sdkmanager
    ls -l $(which sdkmanager || echo "${ANDROID_SDK_ROOT}/cmdline-tools/latest/bin/sdkmanager")
    sdkmanager --version || echo "SDK manager version check failed in current shell"

    # STEP 5: Clean any previous Buildozer distribution state
    # 'distclean' is more thorough than 'clean' for the distribution itself.
    buildozer distclean
    buildozer android clean

    # STEP 6: First Buildozer run (to download and extract recipes)
    # This command will attempt to create the distribution.
    # It should now find the SDK tools prepared by fix_android_sdk.sh.
    # It is still expected to FAIL at a later stage (e.g., Cython compilation) 
    # because Python patches have not been applied yet.
    echo "Attempting initial Buildozer distribution creation (may fail at compilation)..."
    nice -n -10 buildozer -v android debug --log-level 2 --debug || true

    # STEP 7: Apply Python-specific patches
    # These patches target files that should have been extracted by the previous Buildozer command.
    echo "Applying Python-specific patches..."
    ./patch_py2to3.sh && ./fix_ctypes.sh && ./fix_py2to3.sh && ./patch_jnius.sh

    # STEP 8: Final build attempt with logging
    echo "Attempting final build..."
    nice -n -10 buildozer -v android debug --log-level 2 --debug 2>&1 | tee logs/buildozer.log
    ```

    The APK will be generated in the `bin/` directory.

4. **(Optional) Deploy and run on a connected Android device:**
    ```bash
    buildozer android debug deploy run logcat > logs/buildozer.log
    cp logs/buildozer.log logs/buildozer_log.txt
    ```

### Quick APK Build (Docker One-Liner)
    For those who just want the APK without all the detailed steps:
    ```bash
    docker-compose build && docker-compose run buildozer bash -c "buildozer android clean && buildozer android debug || true && ./patch_py2to3.sh && ./fix_ctypes.sh && ./fix_py2to3.sh && ./patch_jnius.sh && buildozer -v android debug"
    ```

---

## Troubleshooting

### Common Desktop Issues
- **ModuleNotFoundError: No module named 'pygame'**: Make sure to install pygame explicitly with `pip install pygame`.
- **Display issues**: Verify your Python environment has proper display support.

### Common Android Build Issues
- **To directly edit and fix pyjnius bugs:**
    ```bash
    # Find the problem file and edit it with nano
    nano $(find ${APP_DIR}/.buildozer -path "*/pyjnius*" -name "jnius_conversion.pxi")

    # Directly fix "long type doesn't exist in Python 3" by replacing it with int:
    find ${APP_DIR}/.buildozer -path '*pyjnius*' -name 'jnius_conversion.pxi' \
    -exec sed -i 's/isinstance(py_arg, (int, long))/isinstance(py_arg, int)/g' {} \;

    # Find all Python files with 'long' references
    find ${APP_DIR}/.buildozer -name "*.py*" \
    -exec grep -l "long" {} \; 2>/dev/null
    ```

- **Fix mixing "include/" dir:**
    ```bash
    # First stop the build with Ctrl+C, then:
    cd ${ANDROID_PLAT}/build-arm64-v8a_armeabi-v7a/build/other_builds/kivy/arm64-v8a__ndk_target_23/kivy
    sudo mkdir -p include
    sudo touch include/config.pxi
    cd ${APP_DIR}
    ```

- **Install API 30 and 33 platfrom and tools:**
    ```bash
    # 1. Make sure you have the necessary directories
    mkdir -p ${ANDROID_SDK_ROOT}/cmdline-tools/latest/bin
    cd ${APP_DIR}

    # 2. Accept Android SDK licenses first
    yes | ${ANDROID_SDK_ROOT}/cmdline-tools/latest/bin/sdkmanager --licenses

    # 3. # Fix paths with symbolic links
    mkdir -p ${GLOBAL_ANDROID_PLAT}
    ln -sf ${ANDROID_SDK_ROOT} $GLOBAL_ANDROID_PLAT

    # 4. Then verify the symbolic links work:
    ls -la ${ANDROID_SDK_ROOT}/cmdline-tools/latest/bin/sdkmanager
    ls -la ${GLOBAL_ANDROID_SDK_ROOT}/cmdline-tools/latest/bin/sdkmanager

    # 5. Install Android API 30 and 33 platform and tools
    yes | ${ANDROID_SDK_ROOT}/cmdline-tools/latest/bin/sdkmanager \
        --sdk_root=${ANDROID_SDK_ROOT} \
            "platform-tools" \
            "platforms;android-30" \
            "build-tools;30.0.3" \
            "platforms;android-33" \
            "build-tools;33.0.2"

    # 6. Verify the installation (you should see 30 and 33)
    ls -la ${ANDROID_SDK_ROOT}/platforms
    ls -la ${ANDROID_SDK_ROOT}/build-tools
    ```

- **In case you need to manually download the Android platform-tools:**
    ```bash
    # Manually download and install platform-tools instead of relying on sdkmanager. Create platform-tools directory
    mkdir -p ${ANDROID_SDK_ROOT}/platform-tools

    # Download and install platform-tools directly
    cd ${ANDROID_SDK_ROOT}
    wget -q https://dl.google.com/android/repository/platform-tools_r30.0.3-linux.zip -O platform-tools.zip
    unzip -q platform-tools.zip
    rm platform-tools.zip

    # Return to the app directory ${APP_DIR}
    cd ${APP_DIR}
    ```

---

## Notes

- **No need to install Buildozer or Android SDK/NDK on your host.** Docker handles all dependencies.
- **Docker runs as a non-root user (`builduser`) to avoid permission issues.**
- **Customize builds by editing `buildozer.spec`.**
- **For advanced Android configuration, see Buildozer docs.**

---

## Features

- Touch controls (Android) and arrow keys (desktop)
- Eat food to grow the snake
- Game over on collision with walls or self
- Adjustable speed and boundary modes (wrap or bounded)
- Playable on desktop and Android
- Score and best score tracking (saved between sessions)

Enjoy playing the classic Snake game!
