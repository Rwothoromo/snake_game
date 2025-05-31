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

1. **Clone the repository, enter the directory and remove orphan containers.**  
    This ensures a clean environment by deleting unused Docker resources that might interfere with the build process.
    ```bash
    docker-compose down --remove-orphans
    ```

2. **Build and start the Docker container:**
    Using the amazing buildozer for this. See [quickstart docs](https://buildozer.readthedocs.io/en/latest/quickstart.html).
    ```bash
    docker-compose build
    docker-compose run buildozer bash
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
    -v "$PWD/bin":${APP_DIR}/bin \
    kivy-buildozer bash
    ```
    
    **Tip:** To avoid cache, add `--no-cache`.

    **Tip:** To clean Buildozer state: `buildozer android clean`.

3. **Build your APK inside the container:**
    ```bash
    # First create all needed directories and fix permissions
    sudo mkdir -p ${APP_DIR}/.buildozer # For app-specific files
    sudo mkdir -p ${HOME}/.buildozer  # For global shared config
    sudo mkdir -p ${HOME}/.android
    sudo mkdir -p ${HOME}/.kivy
    sudo chown -R builduser:builduser ${APP_DIR}/.buildozer
    sudo chown -R builduser:builduser ${HOME}/.buildozer
    sudo chown -R builduser:builduser ${HOME}/.android
    sudo chown -R builduser:builduser ${HOME}/.kivy

    # Set Google DNS (needs sudo)
    echo "nameserver 8.8.8.8" | sudo tee /etc/resolv.conf > /dev/null

    # Install required Android API level and build-tools
    # mkdir -p ${ANDROID_SDK_ROOT}/cmdline-tools/latest/bin
    # ${ANDROID_SDK_ROOT}/cmdline-tools/latest/bin/sdkmanager --sdk_root=${ANDROID_SDK_ROOT} "platforms;android-33" "build-tools;33.0.2"
   
    # Clean previous build attempts
    buildozer android clean
    rm -rf ~/.gradle

    # First build attempt (will fail but creates directories)
    buildozer android debug || true
   
    # Apply patches
    chmod +x patch_py2to3.sh
    ./patch_py2to3.sh

    # Fix the ctypes module in the host Python
    chmod +x fix_ctypes.sh
    ./fix_ctypes.sh

    # Find and patch all the Python 2 to 3 long type compatibility issues
    chmod +x fix_py2to3.sh
    ./fix_py2to3.sh

    # Targeted fix for jnius_conversion.pxi
    chmod +x patch_jnius.sh
    ./patch_jnius.sh

    # Gradle shenanigans
    export GRADLE_OPTS="-Dorg.gradle.daemon=false -Dorg.gradle.jvmargs=-Xmx2048m"

    # Final build with logging. This captures all output (stdout and stderr use '2>&1'), shows it live (use '| tee' instead of '>'), and saves it to 'logs/buildozer.log'. With '--log-level' (0 - minimal, 1 - normal, 2 - verbose).
    buildozer -v android debug --log-level 2 --debug 2>&1 | tee logs/buildozer.log

    # In a separate terminal, periodically check the last 50 lines 
    tail -f -n 50 logs/buildozer.log | grep -E 'error|warning|compil|build|install|download'
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
    docker-compose build && docker-compose run buildozer bash -c "buildozer android clean && buildozer android debug || true && ./patch_py2to3.sh && buildozer -v android debug"
    ```

---

## Troubleshooting

### Common Desktop Issues
- **ModuleNotFoundError: No module named 'pygame'**: Make sure to install pygame explicitly with `pip install pygame`
- **Display issues**: Verify your Python environment has proper display support

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

- **In case you need to manually download the Android platform-tools:**
    ```bash
    # Manually download and install platform-tools instead of relying on sdkmanager. Create platform-tools directory
    mkdir -p ${ANDROID_SDK_ROOT}/platform-tools

    # Download and install platform-tools directly
    cd ${ANDROID_SDK_ROOT}
    wget -q https://dl.google.com/android/repository/platform-tools_r33.0.3-linux.zip -O platform-tools.zip
    unzip -q platform-tools.zip
    rm platform-tools.zip

    # Return to the app directory ${APP_DIR}$
    cd ~/app
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
