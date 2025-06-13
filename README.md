# Snake Game in Python

A classic Snake 🐍 Game 🎮 implemented in Python using Pygame and Kivy. Guide the snake to eat food, grow longer, and avoid collisions with walls or itself.

---

## Project Structure

```
snake_game
├── m4/                 # m4 macros for Android builds
├── logs/               # Build and runtime logs
├── bin/                # Output APKs (gitignored)
├── .buildozer/         # Android build artifacts (gitignored)
├── src/                # Core game logic
│   ├── snake.py        # Snake class
│   ├── food.py         # Food class
│   └── game.py         # Pygame-based Game class (optional)
├── main.py             # Kivy entry point
├── requirements.txt    # Python dependencies
├── buildozer.spec      # Buildozer config for APK builds
├── Dockerfile          # Dockerfile for Android APK builds
├── docker-compose.yml  # Docker Compose workflow
├── .gitignore          # Git ignore rules
├── best_score.txt      # Stores best score
└── README.md           # Project documentation
```

---

## Quick Start

### 1. Run on Desktop

#### Prerequisites

- Python 3.7+
- [Pip](https://pip.pypa.io/en/stable/)
- [Pygame](https://www.pygame.org/news)
- [Kivy](https://kivy.org/)

#### Steps

```bash
# Clone the repository
git clone https://github.com/Rwothoromo/snake_game.git
cd snake_game

# Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt pygame kivy

# (Optional) Reset best score
echo 0 > best_score.txt

# Run the game
python3 main.py
```

---

### 2. Build and Run on Android (with Docker)

#### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop)

#### Steps

```bash
# Clean up any previous containers and cache
docker-compose down --remove-orphans
docker volume rm snake_game_buildozer_cache || true

# Build and start the Docker container
docker-compose build
# Enter the Docker container
docker-compose run buildozer bash
```

Inside the container, run:

```bash
# Ensure scripts are executable
chmod +x *.sh

# Fix permissions for build directories
sudo chown -R $(whoami):$(whoami) $HOME/.buildozer $APP_DIR/.buildozer

# Prepare Android SDK and accept licenses
./fix_android_sdk.sh

# Set PATH for SDK tools
export PATH="${ANDROID_SDK_ROOT}/cmdline-tools/latest/bin:${ANDROID_SDK_ROOT}/platform-tools:${PATH}"

# Tell the linker where to find libffi
export LD_LIBRARY_PATH=/home/builduser/app/.buildozer/android/platform/build-arm64-v8a_armeabi-v7a/build/other_builds/libffi/armeabi-v7a__ndk_target_23/libffi/.libs:$LD_LIBRARY_PATH

./fix_sdl2_image_download.sh

# Clean previous builds
buildozer distclean
buildozer android clean

# First build attempt (downloads sources, builds libffi with custom recipe, 
# extracts Kivy/Pyjnius etc. May fail on other unpatched Cython or succeed through libffi)
buildozer -v android debug --log-level 2 --debug 2>&1 || true

# Apply Cython (Kivy/Pyjnius) and ctypes patches now that their sources are available
sudo ./patch_py2to3.sh
./fix_ctypes.sh

# Second build attempt. If the first attempt fully succeeded, this might not be strictly necessary but is safe.
buildozer -v android debug --log-level 2 --debug 2>&1 | tee -a logs/buildozer.log || true
cp logs/buildozer.log logs/buildozer_log.txt
```

**To deploy and run on a connected Android device:**

```bash
buildozer android debug deploy run logcat > logs/buildozer.log
cp logs/buildozer.log logs/buildozer_log.txt
```

#### Quick APK Build (One-Liner)

```bash
docker-compose down --remove-orphans
docker volume rm snake_game_buildozer_cache || true

docker-compose build && \
docker-compose run buildozer bash -c "\
chmod +x *.sh && \
sudo chown -R \$(whoami):\$(whoami) \$HOME/.buildozer \$APP_DIR/.buildozer && \
./fix_android_sdk.sh && \
export PATH=\"\${ANDROID_SDK_ROOT}/cmdline-tools/latest/bin:\${ANDROID_SDK_ROOT}/platform-tools:\$PATH\" && \
./fix_sdl2_image_download.sh && \
buildozer distclean && \
buildozer android clean && \
buildozer -v android debug --log-level 2 --debug 2>&1 || true && \
sudo ./patch_py2to3.sh && \
./fix_ctypes.sh && \
buildozer -v android debug --log-level 2 --debug 2>&1 | tee -a logs/buildozer.log || true && \
cp logs/buildozer.log logs/buildozer_log.txt"
```

---

## Troubleshooting

### Desktop

- **ModuleNotFoundError: No module named 'pygame'**  
    Run `pip install pygame`.
- **Display issues**  
    Ensure your Python environment supports GUI.

### Android

- **Android SDK/NDK issues**  
    Run `./fix_android_sdk.sh` and ensure all licenses are accepted.
- **API 30/33 not found**  
    Install with:
    ```bash
    yes | ${ANDROID_SDK_ROOT}/cmdline-tools/latest/bin/sdkmanager --licenses
    yes | ${ANDROID_SDK_ROOT}/cmdline-tools/latest/bin/sdkmanager \
            "platform-tools" "platforms;android-30" "build-tools;30.0.3" \
            "platforms;android-33" "build-tools;33.0.2"
    ```
- **Script fixes:**
    Visit [GitIngest](https://gitingest.com/) and upload the git repo, download its `*.txt` version, upload that to [ai.dev](aistudio.google.com) and seek answers!

---

## Features

- Touch controls (Android) and arrow keys (desktop)
- Eat food to grow the snake
- Game over on collision with walls or self
- Adjustable speed and boundary modes (wrap or bounded)
- Playable on desktop and Android
- Score and best score tracking (saved between sessions)

---

## Notes

- **No need to install Buildozer or Android SDK/NDK on your host.** Docker handles all dependencies.
- **Docker runs as a non-root user (`builduser`) to avoid permission issues.**
- **Customize builds by editing `buildozer.spec`.**
- **For advanced Android configuration, see Buildozer docs.**

---

Enjoy playing the classic Snake game!
